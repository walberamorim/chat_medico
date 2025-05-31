from chatterbot import ChatBot
from processar_dados import get_doencas

NOME_ROBO = "Robô Médico"
BD_ROBO = "chat.sqlite3"
CAMINHO_BD = "C:\\Users\\WAA-HP\\Documents\\posweb\\chat_medico"
BD_DADOS = f"{CAMINHO_BD}\\dados.sqlite3"

CONFIANCA_MINIMA = 0.6

def inicializar():
    sucesso, robo, doencas = False, None, None

    try:
        robo = ChatBot(NOME_ROBO,
            read_only = True, 
            storage_adapter='chatterbot.storage.SQLStorageAdapter', 
            database_uri=f'sqlite:///{BD_ROBO}')
        
        doencas = get_doencas(True)
        
        sucesso = True
    except Exception as e:
        print(f"Erro inicializando o robô: {NOME_ROBO}: {str(e)}")

    return sucesso, robo, doencas

def executar(robo):
    while True:
        mensagem = input("👤: ")
        resposta = robo.get_response(mensagem.lower())

        if(resposta.confidence >= CONFIANCA_MINIMA):
            print(f"🤖: {resposta.text}. Confianca = {resposta.confidence}")
        else:
            print(f"🤖: Infelizmente, ainda não sei responder essa pergunta. Confiança = {resposta.confidence}")
            # registrar a pergunta em um log

def pesquisar_doencas_por_chaves(chaves, doencas):
    encontrou, doencas_selecionadas = False, []
    ordem = 1
    for d in doencas:
        for chave in chaves:
            chave = chave.strip()
            if chave and any(chave in c for c in [d['chave1'], d['chave2'], d['chave3'], d['chave4'], d['chave5'], d['chave6'], d['chave7']]):
                doencas_selecionadas.append({'ordem': ordem, 'titulo': d['doenca'], 'sintomas': d['sintomas']})
                encontrou = True
                ordem += 1

    return encontrou, doencas_selecionadas        

if __name__ == "__main__":
    sucesso, robo, doencas = inicializar()

    if sucesso:
        executar(robo)