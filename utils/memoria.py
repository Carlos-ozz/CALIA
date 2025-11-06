"""
memoria.py — Gerenciamento de memória vetorial (FAISS) da CALIA V2.0

Este módulo é responsável por:
 - Carregar o índice FAISS salvo localmente (gerado pelo script ingestao.py)
 - Retornar um retriever LangChain compatível com o pipeline RAG
 - Fornecer um retriever “vazio” quando o índice não existe (modo fallback)

Autor: Carlos
Projeto: CALIA V2.0
"""
from langchain_huggingface import HuggingFaceEmbeddings
import os
import logging

logger = logging.getLogger(__name__)


# =============================================
# 🧠 Função principal: carregar o retriever FAISS
# =============================================
def carregar_retriever(index_folder: str = "faiss_index"):
    """
    Carrega o índice FAISS local e retorna um retriever LangChain.

    Args:
        index_folder (str): Caminho da pasta onde o índice FAISS foi salvo.
                            (Por padrão, "faiss_index")

    Returns:
        retriever (langchain.retrievers.base.BaseRetriever):
            Objeto retriever pronto para busca semântica.
            Caso o índice não exista, retorna um retriever vazio (_EmptyRetriever).
    """
    try:
        from langchain_community.vectorstores import FAISS
        from langchain_community.embeddings import HuggingFaceEmbeddings
    except ImportError as e:
        logger.warning(f"⚠️ LangChain ou FAISS não instalado corretamente: {e}")
        return _EmptyRetriever()

    if os.path.isdir(index_folder):
        try:
            logger.info(f"📂 Carregando índice FAISS de: {index_folder}")

            # Recria o modelo de embeddings para garantir compatibilidade
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

            # Carrega o índice FAISS salvo localmente
            faiss_store = FAISS.load_local(index_folder, embeddings)

            # Converte o vetorstore em um retriever (para busca semântica)
            retriever = faiss_store.as_retriever(search_kwargs={"k": 4})

            logger.info("✅ Índice FAISS carregado com sucesso.")
            return retriever

        except Exception as e:
            logger.exception(f"❌ Erro ao carregar o índice FAISS: {e}")
            return _EmptyRetriever()
    else:
        logger.warning("⚠️ Nenhum índice FAISS encontrado. Usando retriever vazio.")
        return _EmptyRetriever()


# =============================================
# 🔄 Classe fallback: retriever vazio
# =============================================
class _EmptyRetriever:
    """
    Classe retriever “vazio” — usada quando o índice FAISS não existe
    ou não pôde ser carregado.

    Retorna sempre uma lista vazia de documentos.
    Permite que o sistema continue funcionando sem falhas.
    """

    def get_relevant_documents(self, query, *args, **kwargs):
        logger.info("ℹ️ Retriever vazio utilizado — nenhum contexto disponível.")
        return []
