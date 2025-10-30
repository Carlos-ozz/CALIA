"""
===========================================
   CALIA - Sistema RAG (Retrieval System)
   Autor: Arkino
   Data: 2025
===========================================

Este módulo é responsável por:
- Carregar e dividir documentos em chunks;
- Criar e gerenciar o índice vetorial FAISS;
- Recuperar informações relevantes (RAG);
- Armazenar e registrar conversas como arquivos .txt
  para uso futuro como dados de contexto.

Todos os caminhos e chaves são controlados via .env
===========================================
"""

# ==== IMPORTAÇÕES ====
from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import datetime
import os


# ==== CARREGAR VARIÁVEIS DO ARQUIVO .ENV ====
load_dotenv()
EMBEDDING_KEY = os.getenv("API_KEY_EMBEDDING")            # Chave da API do Gemini
RAG_PATH = os.getenv("RAG_PATH")                  # Caminho da pasta com os documentos da CALIA

# Converter caminho em objeto Path (mais seguro e multiplataforma)
pasta_docs = Path(RAG_PATH)

# Caminho do índice FAISS local
INDEX_PATH = "faiss_index"

# Cria a pasta caso ela ainda não exista
if not pasta_docs.exists():
    os.makedirs(pasta_docs)
    print(f"[INFO] Pasta RAG criada automaticamente em: {pasta_docs}")


# ==== FUNÇÃO: Carregar documentos ====
def carregar_documentos(pasta_docs):
    """
    Lê todos os arquivos (.pdf, .txt, .md) dentro da pasta especificada
    e retorna uma lista de documentos para uso no RAG.
    """
    docs = []
    for ndocs in Path(pasta_docs).glob("*"):
        if ndocs.suffix.lower() in [".pdf", ".txt", ".md"]:
            try:
                loader = PyMuPDFLoader(str(ndocs))
                docs.extend(loader.load())
                print(f"[OK] Documento carregado: {ndocs.name}")
            except Exception as e:
                print(f"[ERRO] Falha ao carregar {ndocs.name}: {e}")
    print(f"[INFO] Total de documentos carregados: {len(docs)}")
    return docs


# ==== FUNÇÃO: Criar ou carregar retriever FAISS ====
def criar_retriever(pasta_docs, rebuild=False):
    """
    Cria ou carrega o índice vetorial FAISS responsável por armazenar embeddings.

    Parâmetros:
        pasta_docs (Path): Pasta com os documentos do RAG.
        rebuild (bool): Se True, força a recriação completa do índice FAISS.
    
    Retorna:
        retriever (FAISS.as_retriever): Objeto usado para busca contextual.
    """
    # Criar modelo de embeddings do Gemini
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=EMBEDDING_KEY
    )

    # Carregar índice existente, ou criar do zero se não houver
    if os.path.exists(INDEX_PATH) and not rebuild:
        print("[INFO] Carregando índice FAISS existente...")
        vectorstore = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    else:
        print("[INFO] Criando novo índice FAISS a partir dos documentos...")
        docs = carregar_documentos(pasta_docs)

        # Dividir documentos em chunks menores (para melhor precisão sem perder contexto)
        splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
        chunks = splitter.split_documents(docs)

        # Converter chunks em vetores (embeddings) e criar índice FAISS
        vectorstore = FAISS.from_documents(chunks, embeddings)
        vectorstore.save_local(INDEX_PATH)
        print("[OK] Novo índice FAISS salvo localmente.")

    # Criar retriever (buscador) com configuração de similaridade
    retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"score_threshold": 0.3, "k": 4}
    )

    print("[READY] RAG inicializado e pronto para consultas.")
    return retriever


# ==== FUNÇÃO: Salvar histórico da sessão como .txt ====
def salvar_historico_como_txt(historico, pasta_docs):
    """
    Salva todas as mensagens trocadas (usuário e CALIA) em um arquivo .txt
    dentro da pasta de documentos RAG. O arquivo pode ser usado
    posteriormente para atualizar o índice vetorial.

    Parâmetros:
        historico (list[dict]): Lista de mensagens no formato:
            {"remetente": "user" ou "calia", "texto": "mensagem"}
        pasta_docs (Path): Pasta onde os arquivos .txt serão salvos.
    
    Retorna:
        Path: Caminho completo do arquivo salvo.
    """
    if not historico:
        print("[WARN] Nenhuma mensagem para salvar.")
        return None

    # Nome do arquivo único com base em data e hora
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"sessao_{timestamp}.txt"
    caminho_arquivo = Path(pasta_docs) / nome_arquivo

    # Montar conteúdo do arquivo
    conteudo = ""
    for msg in historico:
        remetente = "USER" if msg["remetente"] == "user" else "CALIA"
        conteudo += f"{remetente}: {msg['texto']}\n"

    # Salvar conteúdo no arquivo
    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo)

    print(f"[SAVE] Histórico salvo com sucesso em: {caminho_arquivo}")
    return caminho_arquivo


# ==== FUNÇÃO (Opcional): Atualizar FAISS com novo arquivo salvo ====
def atualizar_faiss_com_novo_arquivo(caminho_arquivo):
    """
    Atualiza o índice FAISS existente com um novo documento, sem precisar recriar tudo.
    Ideal para adicionar conversas recentes automaticamente.

    Parâmetros:
        caminho_arquivo (Path): Caminho do arquivo recém-salvo.
    """
    if not os.path.exists(INDEX_PATH):
        print("[WARN] Nenhum índice FAISS encontrado. Execute criar_retriever() primeiro.")
        return

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=EMBEDDING_KEY
    )

    # Carrega o índice atual
    vectorstore = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)

    # Carrega e processa o novo arquivo
    loader = PyMuPDFLoader(str(caminho_arquivo))
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    chunks = splitter.split_documents(docs)

    # Adiciona os novos embeddings ao índice
    vectorstore.add_documents(chunks)
    vectorstore.save_local(INDEX_PATH)
    print(f"[UPDATE] FAISS atualizado com novo arquivo: {caminho_arquivo.name}")
