from nltk import word_tokenize
from nltk.corpus import floresta, stopwords

from string import punctuation
from collections import Counter

import sqlite3
import os

CAMINHO_DADOS = "C:\\Users\\WAA-HP\\Documents\\posweb\\chat_medico\\dados"
CAMINHO_BD = "C:\\Users\\WAA-HP\\Documents\\posweb\\chat_medico"
BD_DADOS = f"{CAMINHO_BD}\\dados.sqlite3"

CLASSES_GRAMATICAIS_INDESEJADAS = [
    "num",
    "adv",
    "v-inf",
    "v-fin",
    "v-pcp",
    "v-ger",
]

FREQUENCIA_MINIMA = 1
PALAVRAS_CHAVE_POR_DADOS = 7

def inicializar_palavras():
    palavras_de_parada = set(stopwords.words('portuguese'))

    classificacoes = {}
    for (palavra, classificacao) in floresta.tagged_words():
        classificacoes[palavra.lower()] = classificacao

    return palavras_de_parada, classificacoes

def ler_conteudo(dado):
    sucesso, conteudo = False, None

    try:
        with open(dado, "r", encoding="utf-8") as arquivo:
            conteudo = arquivo.read()

        sucesso = True
    except Exception as e:
        print(f"Erro ao ler os dados: {dado}: {str(e)}")
    return sucesso, conteudo

def extrair_doenca(conteudo):
    marcador = "Doença: "
    marcador = conteudo.index(marcador) + len(marcador)

    doenca = conteudo[marcador:]
    doenca = doenca[:doenca.index(";")]

    return doenca


def extrair_sintomas(conteudo):
    marcador_inicio = "Sintomas:"
    marcador_fim = ";"
    inicio = conteudo.index(marcador_inicio) + len(marcador_inicio)
    fim = conteudo.index(marcador_fim, inicio)
    sintomas = conteudo[inicio:fim].strip()
    return sintomas

def extrair_especialidade(conteudo):
    marcador_inicio = "Especialista:"
    marcador_fim = ";"
    inicio = conteudo.index(marcador_inicio) + len(marcador_inicio)
    fim = conteudo.index(marcador_fim, inicio)
    especialidade = conteudo[inicio:fim].strip()
    return especialidade

def eliminar_palavras_de_parada(tokens, palavras_de_parada):
    tokens_filtrados = []
    for token in tokens:
        if token.lower() not in palavras_de_parada:
            tokens_filtrados.append(token)
    return tokens_filtrados

def eliminar_pontuacao(tokens):
    tokens_filtrados = []
    for token in tokens:
        if token not in punctuation:
            tokens_filtrados.append(token)
    return tokens_filtrados

def eliminar_classes_gramaticais_indesejadas(tokens, classificacoes):
    tokens_filtrados = []
    for token in tokens:
        if token in classificacoes.keys():
            classificacao = classificacoes[token]
            if not any (s in classificacao for s in CLASSES_GRAMATICAIS_INDESEJADAS):
                tokens_filtrados.append(token)
        else:
            tokens_filtrados.append(token)
    return tokens_filtrados

def eliminar_frequencias_baixas(tokens):
    frequencias = Counter(tokens)
    tokens_filtrados = []
    for token, frequencia in frequencias.most_common():
        if frequencia >= FREQUENCIA_MINIMA:
            tokens_filtrados.append(token)
    return tokens_filtrados

def iniciar_banco_doencas():
    if os.path.exists(BD_DADOS):
        os.remove(BD_DADOS)    

    conexao = sqlite3.connect(BD_DADOS)
    cursor = conexao.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS doenca (id INTEGER PRIMARY KEY AUTOINCREMENT, doenca TEXT, sintomas TEXT, especialista TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS chaves (id INTEGER PRIMARY KEY AUTOINCREMENT, id_doenca INTEGER, chave1 TEXT, chave2 TEXT, chave3 TEXT, chave4 TEXT, chave5 TEXT, chave6 TEXT, chave7 TEXT, FOREIGN KEY(id_doenca) REFERENCES doenca(id))")
    conexao.commit()
    conexao.close()

def gravar_doenca(id, doenca, chaves, sintomas, especialista):
    conexao = sqlite3.connect(BD_DADOS)
    cursor = conexao.cursor()

    cursor.execute("INSERT INTO doenca (id, doenca, sintomas, especialista) VALUES (?, ?, ?, ?)", (id, doenca, sintomas, especialista))

    # Garante que chaves tenha exatamente 7 elementos
    chaves = (chaves + [""] * PALAVRAS_CHAVE_POR_DADOS)[:PALAVRAS_CHAVE_POR_DADOS]

    cursor.execute("INSERT INTO chaves (id_doenca, chave1, chave2, chave3, chave4, chave5, chave6, chave7) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (id, *chaves))

    conexao.commit()
    conexao.close()

def get_doencas(como_linhas = False):
    conexao = sqlite3.connect(BD_DADOS)
    if (como_linhas):
        conexao.row_factory = sqlite3.Row
    cursor = conexao.cursor()

    cursor.execute("SELECT id_doenca, doenca, sintomas, especialista, chave1, chave2, chave3, chave4, chave5, chave6, chave7 FROM doenca, chaves WHERE chaves.id_doenca = doenca.id")
    doencas = cursor.fetchall()

    for d in doencas:
        print(f"ID: {d[0]}, Doença: {d[1]}")
        cursor.execute("SELECT * FROM chaves WHERE id_doenca = ?", (d[0],))
        chaves = cursor.fetchone()
        print(f"Chaves: {chaves[2:] if chaves else None}")

    conexao.close()
    return doencas

if __name__ == "__main__":
    palavras_de_parada, classificacoes = inicializar_palavras()
    iniciar_banco_doencas()
    for contador in range(1, 200):
        caminho_doenca = f"{CAMINHO_DADOS}\\{contador}.txt"
        if os.path.exists(caminho_doenca):
            sucesso, conteudo = ler_conteudo(caminho_doenca)

            if sucesso:
                nome = extrair_doenca(conteudo)
                print(f"doença: {caminho_doenca}")
                sintomas = extrair_sintomas(conteudo)
                print(f"sintomas: {sintomas}")
                especialidade = extrair_especialidade(conteudo)
                print(f"especialidade: {especialidade}")
                tokens = word_tokenize(sintomas, language='portuguese')
                tokens = eliminar_palavras_de_parada(tokens, palavras_de_parada)
                tokens = eliminar_pontuacao(tokens)
                tokens = eliminar_classes_gramaticais_indesejadas(tokens, classificacoes)
                tokens = eliminar_frequencias_baixas(tokens)
                print(f"tokens: {tokens}")
                gravar_doenca(contador, nome, tokens, sintomas, especialidade)
        else:
            print(f"doença: {caminho_doenca} não encontrado")
            break
    print("Doenças gravadas no banco: ")
    get_doencas()