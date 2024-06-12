from flask import Flask,render_template, request, Response
from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import *
from assistente import *

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = os.getenv("MODELO_GERAL")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_KEY")


thread = criar_thread()

entrevistador =  "asst_w4HdCa3Sm7RyeZw8Uh2L5ays" #Asistente Entrevistador 2 (OpenaAI Bicalho):  "asst_mLwagdf01yBC0BGbEd71FscF"
analista = "asst_FOWRenT4EeWjO6vCTJsclGKS" #Analista IART


assistente = analista #Cosntruir função para selecionar o assistente de acordo com o prompt de saída Entrevistador IART mantendo a thread com o Briefing.


def bot(prompt):
    maximo_tentativas = 1
    repeticao = 0
    #assistente = seleciona_persona(prompt)
    while True:
        try:
            cliente.beta.threads.messages.create(
                thread_id = thread.id,
                role = "user",
                content = prompt
            )
            run = cliente.beta.threads.runs.create(
                thread_id = thread.id,
                assistant_id = assistente
            )

            while run.status != "completed":
                run = cliente.beta.threads.runs.retrieve(
                    thread_id = thread.id,
                    run_id = run.id
            )
            
            historico = list(cliente.beta.threads.messages.list(thread_id=thread.id).data)
            resposta = historico[0]
            return resposta



        except Exception as erro:
            repeticao += 1
            if repeticao >= maximo_tentativas:
                return "Erro no GPT: %s" % erro
            print('Erro de comunicação com OpenAI: ', erro)
            sleep(1)


@app.route("/chat", methods=["POST"])
def chat():##
    prompt = request.json["msg"]
    resposta = bot(prompt)
    print(resposta)
    texto_resposta = resposta.content[0].text.value
    return texto_resposta

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug = True)
