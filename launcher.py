import os
import time
import subprocess

def iniciar_calia():
    print("""
╔══════════════════════════════════════════════════╗
║          💜 BEM-VINDO À CALIA v1.0 💜            ║
╠══════════════════════════════════════════════════╣
║ Iniciando servidor Streamlit...                  ║
║ Isso pode levar alguns segundos.                 ║
╚══════════════════════════════════════════════════╝
""")

    # Executa o Streamlit em segundo plano
    process = subprocess.Popen(["streamlit", "run", "main.py"])

    # Espera o servidor iniciar
    time.sleep(3)

    # Abre no navegador
    print("🌐 Acesse a CALIA no seu navegador: http://localhost:8501")
    print("💡 Para encerrar, pressione CTRL + C")
    try:
        process.wait()  # Mantém o Streamlit ativo
    except KeyboardInterrupt:
        print("\n🛑 Encerrando a CALIA...")
        process.terminate()

iniciar_calia()
