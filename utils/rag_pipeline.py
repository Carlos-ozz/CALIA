"""
rag_pipeline.py — Pipeline de Recuperação e Geração (RAG) da CALIA V2.0

Responsável por:
 - Buscar documentos relevantes no índice vetorial (FAISS) usando LangChain.
 - Montar um prompt contextualizado combinando os documentos e a pergunta do usuário.
 - Enviar o prompt ao modelo Gemini (através do LLMWrapper).
 - Retornar uma resposta textual processada.

Fluxo resumido:
Usuário → pergunta → retriever (FAISS) → contexto → prompt → Gemini → resposta

Autor: Carlos
Projeto: CALIA V2.0
"""

from utils.memoria import carregar_retriever
from utils.llm import LLMWrapper
import logging
from typing import List, Any

# Logger do módulo
logger = logging.getLogger(__name__)

# Instâncias únicas (singleton simples) para evitar recarregamento
_llm_singleton: LLMWrapper | None = None
_retriever_singleton: Any | None = None


# =====================================
# 🔧 Funções internas de inicialização
# =====================================
def _get_llm() -> LLMWrapper:
    """
    Retorna uma instância única do LLMWrapper configurado (Gemini).
    Evita inicializar o modelo a cada requisição, otimizando desempenho.
    """
    global _llm_singleton
    if _llm_singleton is None:
        logger.info("Inicializando modelo LLM (Gemini)...")
        _llm_singleton = LLMWrapper()
    return _llm_singleton


def _get_retriever():
    """
    Retorna uma instância única do retriever FAISS, caso exista.
    Se o índice FAISS não for encontrado, retorna um retriever vazio.
    """
    global _retriever_singleton
    if _retriever_singleton is None:
        logger.info("Carregando retriever FAISS (se disponível)...")
        _retriever_singleton = carregar_retriever()
    return _retriever_singleton


# =====================================
# 🧠 Função principal do pipeline
# =====================================
def gerar_resposta(pergunta: str) -> str:
    """
    Executa o pipeline RAG (Retrieval-Augmented Generation).

    Args:
        pergunta (str): Texto da pergunta feita pelo usuário.

    Returns:
        str: Resposta gerada pelo modelo Gemini, com ou sem contexto FAISS.
    """
    try:
        # Recupera instâncias principais
        retriever = _get_retriever()
        llm = _get_llm()

        # Busca documentos relevantes (caso FAISS esteja ativo)
        try:
            docs = retriever.get_relevant_documents(pergunta) or []
            logger.info(f"{len(docs)} documentos relevantes recuperados.")
        except Exception as e:
            logger.warning("Falha ao recuperar documentos: %s", e)
            docs = []

        # Monta o contexto textual com os documentos
        contexto = _montar_contexto(docs)

        # Constrói o prompt final que será enviado ao modelo Gemini
        prompt = _montar_prompt(pergunta, contexto)

        # Gera a resposta via modelo
        resposta = llm.send(prompt)
        return resposta

    except Exception as e:
        logger.exception("Erro inesperado no pipeline RAG: %s", e)
        return f"[Erro interno no pipeline RAG] {str(e)}"


# =====================================
# 🧩 Funções auxiliares
# =====================================
def _montar_contexto(docs: List[Any]) -> str:
    """
    Monta o contexto concatenando o conteúdo dos documentos retornados pelo retriever.

    Args:
        docs (List[Any]): Lista de documentos retornados pelo FAISS retriever.

    Returns:
        str: Texto consolidado dos documentos (ou string vazia se não houver docs).
    """
    if not docs:
        return ""

    partes = []
    for doc in docs:
        try:
            # Compatível com diferentes formatos de documentos LangChain
            texto = getattr(doc, "page_content", None) or getattr(doc, "content", None) or str(doc)
            partes.append(texto)
        except Exception as e:
            logger.warning("Erro ao processar documento: %s", e)

    contexto = "\n\n".join(partes)
    return contexto.strip()


def _montar_prompt(pergunta: str, contexto: str) -> str:
    """
    Monta o prompt final que será enviado ao modelo Gemini.

    Args:
        pergunta (str): Texto da pergunta feita pelo usuário.
        contexto (str): Texto contextual (extraído de documentos, se houver).

    Returns:
        str: Prompt completo formatado.
    """
    prompt_base = (
        "Você é CALIA, uma assistente de IA útil e contextual.\n"
        "Use o contexto abaixo (se disponível) para responder de forma objetiva e natural.\n\n"
    )

    if contexto:
        prompt_base += f"Contexto:\n{contexto}\n\n"

    prompt_base += f"Pergunta: {pergunta}\n\nResposta:"
    return prompt_base
