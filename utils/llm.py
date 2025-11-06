"""
llm.py — Wrapper de comunicação com o modelo Gemini (Google Generative AI)
para o projeto CALIA V2.0.

Responsável por:
 - Inicializar o cliente da API Gemini usando a chave armazenada em .env
 - Enviar prompts de texto e retornar as respostas geradas
 - Fazer tratamento de erros e manter um fallback de segurança

Autor: Carlos
Projeto: CALIA V2.0
"""

import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Configuração do logger local
logger = logging.getLogger(__name__)


# =====================================
# ⚙️ Inicialização da API Gemini
# =====================================
class LLMWrapper:
    """
    Classe de alto nível para interação com o modelo Gemini da Google.

    Essa classe centraliza toda a comunicação com o modelo de linguagem,
    permitindo fácil substituição ou troca de modelo no futuro (por ex: GPT, Claude, Mistral, etc.).

    Uso:
        llm = LLMWrapper()
        resposta = llm.send("Explique o conceito de RAG.")
    """

    def __init__(self, api_key_env: str = "API_KEY_CALIA", model_name: str = "gemini-2.5-flash"):
        """
        Inicializa a classe, configurando o cliente da API Gemini.

        Args:
            api_key_env (str): Nome da variável de ambiente onde a API key está armazenada.
                               Por padrão: 'API_KEY_CALIA'
            model_name (str): Nome do modelo Gemini a ser usado.
                              (ex: 'gemini-1.5-flash', 'gemini-1.5-pro', etc.)
        """
        load_dotenv()

        self.api_key = os.getenv(api_key_env)
        self.model_name = model_name
        self.model = None

        if not self.api_key:
            logger.warning(f"⚠️ Chave de API '{api_key_env}' não encontrada no .env.")
        else:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                logger.info(f"🤖 Modelo Gemini configurado: {self.model_name}")
            except Exception as e:
                logger.exception(f"❌ Erro ao inicializar o modelo Gemini: {e}")

    # =====================================
    # 🧠 Envio de prompt e geração de texto
    # =====================================
    def send(self, prompt: str) -> str:
        """
        Envia um prompt de texto ao modelo Gemini e retorna a resposta.

        Args:
            prompt (str): Texto ou comando a ser processado pelo modelo.

        Returns:
            str: Resposta textual gerada pelo modelo.
        """
        if not self.model:
            logger.warning("⚠️ Modelo LLM não configurado corretamente.")
            return "[ERRO] Modelo não configurado. Verifique a API_KEY_CALIA no .env."

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip() if hasattr(response, "text") else str(response)
            logger.info("💬 Resposta recebida do Gemini com sucesso.")
            return text
        except Exception as e:
            logger.error(f"❌ Erro ao enviar prompt para o Gemini: {e}")
            return "[ERRO] Falha ao gerar resposta com o modelo Gemini."


# =====================================
# 🧪 Teste rápido
# =====================================
if __name__ == "__main__":
    """
    Teste direto do módulo LLMWrapper.
    Permite verificar se a API Gemini está funcionando corretamente.
    """
    llm = LLMWrapper()
    resposta = llm.send("Olá! Você está funcionando?")
    print("Resposta:", resposta)
