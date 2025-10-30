import streamlit as st
from pathlib import Path
import time
import os
from dotenv import load_dotenv
from utils import salvar_memoria
from langchain_google_genai import ChatGoogleGenerativeAI
from rag import criar_retriever, salvar_historico_como_txt, atualizar_faiss_com_novo_arquivo

# ==============================================
#    CONFIGURAÇÃO INICIAL
# ==============================================
load_dotenv()
CALIA_KEY = os.getenv("API_KEY_CALIA")
RAG_PATH = os.getenv("RAG_PATH")

st.set_page_config(page_title="CALIA", page_icon="💜", layout="centered")

# ==============================================
#    ESTILO PERSONALIZADO
# ==============================================
st.markdown("""
    <style>
        body { background-color: #faf6ff; color: #3c2a4d; }
        .main { background-color: #faf6ff; }
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
    </style>
""", unsafe_allow_html=True)

# ==============================================
#    INICIALIZAÇÃO DO MODELO E RETRIEVER
# ==============================================
calia_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.6,
    api_key=CALIA_KEY
)

# Inicializa o RAG (carrega FAISS e documentos)
retriever = criar_retriever(RAG_PATH)

# ==============================================
#    ESTADO DE SESSÃO
# ==============================================
if "historico" not in st.session_state:
    st.session_state.historico = []

# ==============================================
#   INTERFACE DO CHAT
# ==============================================
st.title("💜 CALIA")

# Exibir histórico de conversa
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
for msg in st.session_state.historico:
    if msg["remetente"] == "user":
        st.markdown(f"<div class='user-bubble'>{msg['texto']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='calia-bubble'>{msg['texto']}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ==============================================
#    ENTRADA DO USUÁRIO
# ==============================================
prompt = st.chat_input("Escreva algo para CALIA...")

if prompt:
    st.session_state.historico.append({"remetente": "user", "texto": prompt})

    with st.spinner("CALIA está pensando... 💭"):
        # Busca contexto no RAG
        docs = retriever.invoke(prompt)
        contexto = "\n\n".join([d.page_content for d in docs]) if docs else "Nenhum contexto relevante encontrado."

        # Monta o prompt com contexto
        prompt_final = f"""
        Use o seguinte contexto para responder de forma útil e natural:
        {contexto}

        Pergunta do usuário: {prompt}
        """

        # Gera a resposta com o modelo LLM
        time.sleep(0.6)
        resposta = calia_llm.invoke(prompt_final).content

    # Armazena a resposta no histórico
    st.session_state.historico.append({"remetente": "calia", "texto": resposta})

    st.rerun()

# ==============================================
#    BOTÕES DE AÇÃO
# ==============================================
if len(st.session_state.historico) > 0:
    ultima = st.session_state.historico[-1]

    # Salvar resposta como memória (antigo)
    if ultima["remetente"] == "calia":
        if st.button("Salvar essa resposta como memória"):
            salvar_memoria(ultima["texto"])
            st.success("Memória salva ✅")

    # Salvar conversa completa como .txt e atualizar FAISS
    if st.button(" Salvar conversa no RAG"):
        arquivo = salvar_historico_como_txt(st.session_state.historico, RAG_PATH)
        if arquivo:
            atualizar_faiss_com_novo_arquivo(arquivo)
            st.success("Conversa salva e adicionada ao RAG com sucesso ")

pasta_docs = Path(RAG_PATH)

if not pasta_docs.exists():
    os.makedirs(pasta_docs)
    print(f"[INFO] Pasta RAG criada automaticamente em: {pasta_docs}")
