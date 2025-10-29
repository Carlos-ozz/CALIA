import os
import json
from datetime import datetime


def conversar_llm(llm):
    pergunta=str(input("Digite sua pergunta: "))
    resposta=llm.invoke(pergunta)
    return resposta.content

def carregar_memorias():
    if os.path.exists("memories.json"):
        with open("memories.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_memoria(texto):
    mems = carregar_memorias()
    nova = {
        "texto": texto,
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    mems.append(nova)
    with open("memories.json", "w", encoding="utf-8") as f:
        json.dump(mems, f, ensure_ascii=False, indent=2)
