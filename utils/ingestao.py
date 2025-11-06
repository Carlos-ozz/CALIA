"""
ingestao.py — Script de ingestão de documentos para o CALIA V2.0

Este módulo realiza:
 - Leitura automática de arquivos (PDF, TXT e DOCX) da pasta /uploads/
 - Divisão do texto em partes (chunks)
 - Criação de embeddings com HuggingFace
 - Geração e salvamento do índice vetorial FAISS

Resultado:
Cria (ou atualiza) a pasta /faiss_index/ com o índice usado pelo RAG da CALIA.

Autor: Carlos
Projeto: CALIA V2.0
"""

import os
import logging
from pathlib import Path
from typing import List

# Bibliotecas LangChain
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")

# ============================
# ⚙️ CONFIGURAÇÕES DO SCRIPT
# ============================

UPLOADS_DIR = Path("uploads")
INDEX_DIR = Path("faiss_index")

# Modelo de embeddings (rápido e leve)
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Tamanho dos pedaços de texto
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


# ============================
# 🧩 FUNÇÕES DE SUPORTE
# ============================

def carregar_arquivos() -> List:
    """
    Carrega todos os arquivos suportados da pasta /uploads/
    e retorna uma lista de Documentos LangChain.
    """
    documentos = []

    if not UPLOADS_DIR.exists():
        logging.warning(f"Pasta '{UPLOADS_DIR}' não encontrada. Criando automaticamente...")
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        logging.info("Adicione arquivos PDF, TXT ou DOCX em '/uploads/' e execute novamente.")
        return []

    arquivos = [f for f in UPLOADS_DIR.iterdir() if f.suffix.lower() in [".pdf", ".txt", ".docx"]]

    if not arquivos:
        logging.warning("Nenhum arquivo encontrado em /uploads/.")
        return []

    for arquivo in arquivos:
        try:
            logging.info(f"Lendo arquivo: {arquivo.name}")

            if arquivo.suffix.lower() == ".pdf":
                loader = PyMuPDFLoader(str(arquivo))
            elif arquivo.suffix.lower() == ".txt":
                loader = TextLoader(str(arquivo), encoding="utf-8")
            elif arquivo.suffix.lower() == ".docx":
                loader = UnstructuredWordDocumentLoader(str(arquivo))
            else:
                logging.warning(f"Formato não suportado: {arquivo.suffix}")
                continue

            documentos.extend(loader.load())
        except Exception as e:
            logging.error(f"Erro ao carregar {arquivo.name}: {e}")

    return documentos


def dividir_documentos(documentos: List) -> List:
    """
    Divide os documentos em pedaços menores (chunks)
    para melhor processamento e busca semântica.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    texts = splitter.split_documents(documentos)
    logging.info(f"Divididos {len(documentos)} documentos em {len(texts)} partes menores.")
    return texts


def criar_faiss_index(textos: List):
    """
    Cria o índice FAISS local com embeddings dos textos divididos.
    """
    logging.info("Gerando embeddings e criando índice FAISS...")

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    index = FAISS.from_documents(textos, embeddings)

    INDEX_DIR.mkdir(exist_ok=True)
    index.save_local(str(INDEX_DIR))

    logging.info(f"✅ Índice FAISS salvo em: {INDEX_DIR.resolve()}")


# ============================
# 🚀 EXECUÇÃO PRINCIPAL
# ============================

def main():
    """
    Função principal de ingestão.
    Executa o pipeline completo de leitura, chunking e indexação.
    """
    logging.info("🚀 Iniciando ingestão de documentos para o CALIA V2.0...")

    # 1️⃣ Carregar arquivos
    docs = carregar_arquivos()
    if not docs:
        logging.info("Nenhum documento processado. Encerrando ingestão.")
        return

    # 2️⃣ Dividir em partes menores
    textos = dividir_documentos(docs)

    # 3️⃣ Criar e salvar o índice FAISS
    criar_faiss_index(textos)

    logging.info("🎉 Ingestão concluída com sucesso! O CALIA agora pode responder com base nos seus arquivos.")


if __name__ == "__main__":
    main()
