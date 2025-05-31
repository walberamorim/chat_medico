from flask import Flask, Response, request
from robo import *

import json

from processar_dados import word_tokenize, eliminar_palavras_de_parada, eliminar_pontuacao, eliminar_classes_gramaticais_indesejadas, eliminar_frequencias_baixas, inicializar_palavras
from processar_dados import get_doencas as get_doencas_bd
sucesso, robo, doencas = inicializar()
servico = Flask(NOME_ROBO)

INFO = {
    'descricao': 'Robô Médico. Atendimento a pacientes em busca de um especialista.',
    'versao': '1.0',
}

@servico.get('/')
def get_info():
    return Response(json.dumps(INFO), status=200, mimetype='application/json')

@servico.get('/alive')
def is_alive():
    return Response(json.dumps({'alive': 'sim' if sucesso else 'não'}), status=200, mimetype='application/json')

@servico.post('/responder')
def get_resposta():
    if sucesso:
        conteudo = request.json
        resposta = robo.get_response(conteudo['pergunta'])

        return Response(json.dumps({'resposta': resposta.text, 'confianca': resposta.confidence}), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({'resposta': 'Robô não inicializado', 'confianca': 0}), status=503, mimetype='application/json')

@servico.post('/sintomas')
def pesquisar_por_sintomas():
    conteudo = request.json
    sintomas = conteudo.get('pergunta', '')
    palavras_de_parada, classificacoes = inicializar_palavras()

    # Processa os sintomas para extrair as chaves
    tokens = word_tokenize(sintomas, language='portuguese')
    tokens = eliminar_palavras_de_parada(tokens, palavras_de_parada)
    tokens = eliminar_pontuacao(tokens)
    tokens = eliminar_classes_gramaticais_indesejadas(tokens, classificacoes)
    tokens = eliminar_frequencias_baixas(tokens)
    chaves = (tokens + [""] * 7)[:7]

    # Pesquisa no banco de dados
    doencas = get_doencas_bd(como_linhas=True)
    especialistas = []
    for doenca in doencas:
        chaves_doenca = [doenca['chave1'], doenca['chave2'], doenca['chave3'], doenca['chave4'], doenca['chave5'], doenca['chave6'], doenca['chave7']]
        if any(chave in chaves_doenca for chave in chaves if chave):
            especialistas.append({
                "id": doenca['id_doenca'],
                "especialidade": doenca['especialista'],
                "descricao": doenca['doenca']
            })

    return Response(json.dumps({"resposta": especialistas}), status=200, mimetype='application/json')



if __name__ == "__main__":
    servico.run(host='0.0.0.0', port=5000, debug=True)

