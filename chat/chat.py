from flask import Flask, render_template, Response, request
import requests
import json

import secrets

URL_ROBO = "http://localhost:5000"
URL_ROBO_ALIVE = f"{URL_ROBO}/alive"
URL_ROBO_RESPONDER = f"{URL_ROBO}/sintomas"
URL_ROBO_PESQUISAR_SINTOMAS = f"{URL_ROBO}/sintomas"

CONFIANCA_MINIMA = 0.7

chat = Flask(__name__)
chat.secret_key = secrets.token_hex(16)

def acessar_robo(url, para_enviar = None):
    sucesso, resposta = False, None

    try:
        if para_enviar:
            resposta = requests.post(url, json=para_enviar)
        else:
            resposta = requests.get(url)
        resposta = resposta.json()

        sucesso = True
    except Exception as e:
        print(f"erro ao fazer requisição: {str(e)}")    

    return sucesso, resposta

def robo_alive():
    sucesso, resposta = acessar_robo(URL_ROBO_ALIVE)

    return sucesso and resposta["alive"] == "sim"

def perguntar_robo(pergunta):
    mensagem = "Não sei se entendi bem o que disse, pode me explicar melhor?"

    sucesso, resposta = acessar_robo(URL_ROBO_RESPONDER, {"pergunta": pergunta})
    if sucesso and resposta["confianca"] >= CONFIANCA_MINIMA:
        mensagem = resposta["resposta"]
    return sucesso, mensagem

def pesquisar_profissionais(pergunta):
    sucesso, resposta = acessar_robo(URL_ROBO_PESQUISAR_SINTOMAS, {"pergunta": pergunta})
    profissionais_selecionados = []
    if sucesso:
        profissionais = resposta["resposta"]
        for prof in profissionais:
            profissionais_selecionados.append({
                "id": prof["id"],
                "Especialidade": prof["especialidade"],
                "Descrição": prof["descricao"]
            })
    return profissionais_selecionados

@chat.get("/")
def index():
    return render_template("index.html")

@chat.post("/responder")
def get_resposta():
    conteudo = request.json
    pergunta = conteudo['pergunta']

    profissionais = pesquisar_profissionais(pergunta)
    if profissionais:
        resposta_formatada = "Com base nos sintomas informados, você pode estar relacionado às seguintes doenças:<br><ul>"
        for prof in profissionais:
            resposta_formatada += f"<li><b>{prof['Descrição']}</b> — Especialista indicado: <b>{prof['Especialidade']}</b></li>"
        resposta_formatada += "</ul>"
    else:
        resposta_formatada = "Desculpe, não consegui encontrar um especialista para esses sintomas. Tente talvez me descrever melhor os sintomas ou adicionar outros possíveis sintomas que esteja sentindo."


    return Response(
        json.dumps({"resposta": resposta_formatada}),
        status=200,
        mimetype='application/json'
    )

if __name__ == "__main__":
    chat.run(
        host = "0.0.0.0",
        port = 5001,
        debug=True
    )
