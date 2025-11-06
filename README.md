🧭 CALIA V2.0 — Documentação Completa
🌐 Visão Geral:
    CALIA é uma aplicação de IA local desenvolvida em Python + Flask, que integra o modelo Gemini da Google (via API) com uma interface web moderna e responsiva.

⚙️ Estrutura do Projeto
    IA/
    │
    ├── main.py                     # Inicializa o Flask e carrega as rotas
    ├── rotas.py                    # Define endpoints e lógica web
    │
    ├── templates/
    │   └── homepage.html           # Interface principal (HTML)
    │
    ├── static/
    │   ├── css/
    │   │   └── style.css           # Estilos visuais do site
    │   └── img/
    │       └── bg_calia.png        # Fundo visual da aplicação
    │
    ├── utils/
    │   ├── __init__.py
    │   ├── llm.py                  # Carrega e comunica com o modelo Gemini
    │   ├── memoria.py              # (Opcional) Gerencia índices FAISS
    │   └── rag_pipeline.py         # Pipeline de recuperação e geração (RAG)
    │
    ├── .env                        # Chaves de API e configs sensíveis
    ├── requirements.txt            # Dependências Python
    └── readme.md                   # (este arquivo)


🚀 Instalação e Execução
    1. Clone o projeto
        git clone https://github.com/seuusuario/calia-v2.git
        cd calia-v2/IA
    2. Crie o ambiente virtual
        python -m venv venv
        venv\Scripts\activate    # (Windows)
        # ou
        source venv/bin/activate # (Linux/Mac)
    3. Instale as dependências
        pip install -r requirements.txt
    4. Configure sua chave do Gemini
        Edite o arquivo .env e adicione:
            API_KEY_CALIA=sua_chave_gemini_aqui
            FLASK_HOST=127.0.0.1
            FLASK_PORT=5000
            FLASK_DEBUG=true
    5. Execute o servidor
        python main.py


📦 Dependências Principais

    Biblioteca	                     Função
    
    Flask	                         Framework web para o servidor e rotas
    google-generativeai	             Acesso ao modelo Gemini
    langchain	                    Base para pipeline RAG (integração FAISS)
    faiss-cpu	                    Armazenamento e busca vetorial de embeddings
    python-dotenv	                Carrega variáveis do .env
    pymupdf	                        Manipulação de PDFs (para ingestão futura)

🔐 Variáveis de Ambiente
    Arquivo: .env

    Variável	        Descrição

    API_KEY_CALIA	    Chave de API do modelo Gemini
    FLASK_HOST
    FLASK_PORT
    FLASK_DEBUG