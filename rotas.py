"""
rotas.py — Define as rotas e endpoints principais da aplicação CALIA V2.0.

Este módulo contém as rotas Flask responsáveis por:
 - Renderizar a interface principal (homepage.html)
 - Receber perguntas do usuário via requisições POST (/ask)
 - Encaminhar a pergunta para o pipeline de RAG (Retriever + LLM Gemini)
 - Retornar a resposta em formato JSON para o front-end

Autor: Carlos
Projeto: CALIA V2.0
"""

from flask import Blueprint, render_template, request, jsonify
from utils.rag_pipeline import gerar_resposta
import logging

# Criação do blueprint principal (modularização do Flask)
# Isso permite importar e registrar as rotas em main.py
site_routes = Blueprint("site_routes", __name__)

# Configura o logger local para este módulo
logger = logging.getLogger(__name__)


@site_routes.route("/")
def homepage():
    """
    Rota principal (GET /)

    Renderiza o template principal da CALIA (homepage.html),
    que contém a interface do chat e integração JavaScript com a rota /ask.
    """
    logger.info("Página inicial acessada.")
    return render_template("homepage.html")


@site_routes.route("/ask", methods=["POST"])
def ask():
    """
    Endpoint de interação com a IA (POST /ask)

    Espera receber um JSON no formato:
    {
        "message": "texto da pergunta"
    }

    Envia a mensagem para o pipeline RAG (gerar_resposta),
    que se comunica com o modelo Gemini e retorna a resposta.

    Retorna:
        JSON no formato:
        {
            "ok": True/False,
            "resposta": "texto da resposta" | "mensagem de erro"
        }
    """
    try:
        # Extrai dados do corpo da requisição JSON
        data = request.get_json(force=True)
        pergunta = (data.get("message") or "").strip()

        if not pergunta:
            logger.warning("Requisição recebida sem mensagem válida.")
            return jsonify({
                "ok": False,
                "error": "Mensagem vazia. Envie um texto válido."
            }), 400

        # Gera a resposta via pipeline da CALIA
        resposta = gerar_resposta(pergunta)
        logger.info(f"Pergunta recebida: {pergunta[:60]}...")

        return jsonify({
            "ok": True,
            "resposta": resposta
        }), 200

    except Exception as e:
        # Captura qualquer erro inesperado (ex: LLM, retriever, etc.)
        logger.exception("Erro ao processar a pergunta: %s", e)
        return jsonify({
            "ok": False,
            "error": f"Erro interno: {str(e)}"
        }), 500
