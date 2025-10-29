import streamlit as st
import time
from utils import carregar_memorias, salvar_memoria
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

# CARREGAR API KEY NO ARQUIVO .ENV
load_dotenv()
CALIA_KEY = os.getenv("API_KEY_CALIA")

# CONFIGURAÇÕES INICIAIS 
st.set_page_config(page_title=" CALIA", page_icon="💜", layout="centered")

# ESTILO PERSONALIZADO 
st.markdown("""
    <style>
        body {
            background-color: #faf6ff;
            color: #3c2a4d;
        }
        .main {
            background-color: #faf6ff;
        }
        .stTextInput input {
            border-radius: 12px;
            border: 2px solid #c8a2ff;
            padding: 8px;
        }
        .user-bubble {
            background-color: rgba(128, 128, 128, 0.2);
            border-radius: 18px;
            padding: 10px 16px;
            margin: 4px 0;
            text-align: right;
            max-width: 80%;
            align-self: flex-end;
        }
        .calia-bubble {
            background-color: rgba(157, 0, 255, 0.2);
            border-radius: 18px;
            padding: 10px 16px;
            margin: 4px 0;
            text-align: left;
            max-width: 80%;
            align-self: flex-start;
            font-style: italic;
        }
        .chat-container {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        .memory-button {
            background-color: #cdb4ff;
            color: #fff;
            border-radius: 10px;
            padding: 6px 12px;
            border: none;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# INICIALIZAÇÃO DO MODELO

calia_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.6,
    api_key=CALIA_KEY
)

# ESTADO DE SESSÃO
if "historico" not in st.session_state:
    st.session_state.historico = []

# CABEÇALHO
st.title("💜 CALIA")

# EXIBIR CONVERSA
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
for msg in st.session_state.historico:
    if msg["remetente"] == "user":
        st.markdown(f"<div class='user-bubble'>{msg['texto']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='calia-bubble'>{msg['texto']}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ENTRADA DO USUÁRIO
prompt = st.chat_input("Escreva algo para CALIA...")

if prompt:
    # Adiciona mensagem do usuário
    st.session_state.historico.append({"remetente": "user", "texto": prompt})

    # Mostra animação "digitando..."
    with st.spinner("CALIA está pensando... 💭"):
        time.sleep(0.6)
        resposta = calia_llm.invoke(prompt).content

    # Adiciona resposta da CALIA
    st.session_state.historico.append({"remetente": "calia", "texto": resposta})

    # Atualiza visual
    st.rerun()

# BOTÃO DE MEMÓRIA 
if len(st.session_state.historico) > 0:
    ultima = st.session_state.historico[-1]
    if ultima["remetente"] == "calia":
        if st.button("Salvar essa resposta como memória"):
            salvar_memoria(ultima["texto"])
            st.success("Memória salva ✅")