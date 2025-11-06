"""
main.py — Ponto de entrada principal do projeto CALIA V2.0

Responsável por:
 - Inicializar o aplicativo Flask
 - Carregar variáveis de ambiente (.env)
 - Configurar logging
 - Registrar o blueprint de rotas (rotas.py)
 - Iniciar o servidor local de desenvolvimento

Autor: Carlos
Projeto: CALIA V2.0
"""

from flask import Flask
from dotenv import load_dotenv
from rotas import site_routes
import logging
import os

# -------------------------------
# 🔧 Configuração Inicial
# -------------------------------

def create_app() -> Flask:
    """
    Cria e configura a instância principal do Flask.

    Returns:
        Flask: objeto da aplicação Flask configurado e pronto para uso.
    """
    # Carrega variáveis de ambiente (ex: API_KEY_CALIA)
    load_dotenv()

    # Cria instância do Flask (define templates e static folders)
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    # Registra as rotas definidas em rotas.py
    app.register_blueprint(site_routes)

    # Configuração do logger
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    logging.info("Aplicação Flask inicializada com sucesso.")
    return app


# -------------------------------
# 🚀 Execução direta do servidor
# -------------------------------
if __name__ == "__main__":
    """
    Execução direta do servidor Flask.
    Este bloco é acionado quando o arquivo é executado manualmente.
    """

    app = create_app()

    # Obtém configuração de host e porta (permite customização via ambiente)
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug_mode = os.getenv("FLASK_DEBUG", "true").lower() == "True"

    logging.info(f"Iniciando CALIA V2.0 em http://{host}:{port} (debug={debug_mode})")

    # Inicia o servidor Flask
    app.run(
        host=host,
        port=port,
        debug=debug_mode
    )
