"""Formulário de visita às Ovitrampas: Flask + MongoDB (pymongo)."""
import json
import os
from pathlib import Path

from bson import ObjectId
from bson.errors import InvalidId
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_file
from pymongo import MongoClient
from pymongo.errors import PyMongoError

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "ovitrampas")
COLLECTION = os.getenv("COLLECTION", "visitas")
# Quem pode chamar a API. "*" permite abrir o index.html direto do computador.
CORS_ORIGIN = os.getenv("CORS_ORIGIN", "*")

# DS -> lista de bairros do Recife (arquivo editável em data/recife_bairros.json)
ARQUIVO_BAIRROS = Path(__file__).parent / "data" / "recife_bairros.json"
BAIRROS_RECIFE = json.loads(ARQUIVO_BAIRROS.read_text(encoding="utf-8"))

# ---------------------------------------------------------------
# CAMPOS DO FORMULÁRIO: edite esta lista para mudar o formulário.
# tipos aceitos: text, email, date, number, textarea, select, radio, ano
# "depende_de" + "opcoes_por": lista que muda conforme outro campo.
# ---------------------------------------------------------------
CAMPOS = [
    {"nome": "analista_responsavel", "rotulo": "Analista responsável pelo preenchimento",
     "curto": "Analista", "tipo": "text", "obrigatorio": True},
    {"nome": "ano", "rotulo": "Ano", "tipo": "ano", "obrigatorio": True},
    {"nome": "ciclo", "rotulo": "Ciclo", "tipo": "select",
     "opcoes": [f"Ciclo {n}" for n in range(1, 6)], "obrigatorio": True},
    {"nome": "ds", "rotulo": "DS (Distrito Sanitário)", "curto": "DS", "tipo": "select",
     "opcoes": list(BAIRROS_RECIFE), "obrigatorio": True},
    {"nome": "bairro", "rotulo": "Bairro", "tipo": "select", "depende_de": "ds",
     "opcoes_por": BAIRROS_RECIFE, "obrigatorio": True},
    {"nome": "area_bairro", "rotulo": "Área do bairro", "tipo": "text", "obrigatorio": True},
    {"nome": "nome_agente", "rotulo": "Nome do agente", "tipo": "text", "obrigatorio": True},
    {"nome": "matricula_agente", "rotulo": "Matrícula do agente", "tipo": "text", "obrigatorio": True},
    {"nome": "quantidade_palhetas", "rotulo": "Quantidade de palhetas/armadilhas",
     "tipo": "number", "passo": "1", "obrigatorio": True},
    {"nome": "id_ovitrampa", "rotulo": "Id da Ovitrampa", "tipo": "text", "obrigatorio": True},
    {"nome": "data_coleta", "rotulo": "Data de Coleta", "tipo": "date", "obrigatorio": True},
    {"nome": "data_entrega_palhetas", "rotulo": "Data de entrega das palhetas",
     "tipo": "date", "obrigatorio": True},
    {"nome": "observacao", "curto": "Observação", "tipo": "radio",
     "opcoes": ["F", "E", "R", "D", "Rec"], "obrigatorio": True,
     "rotulo": "OBSERVAÇÃO: F (Fechado), E (Extraviado), R (Recusado), D (Desocupado) ou Rec (Recuperada)"},
]

app = Flask(__name__)
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
colecao = client[DB_NAME][COLLECTION]


def limpar(dados):
    """Valida os dados e mantém só os campos definidos em CAMPOS."""
    doc = {}
    for c in CAMPOS:
        nome = c.get("curto", c["rotulo"])
        valor = dados.get(c["nome"])
        valor = valor.strip() if isinstance(valor, str) else valor
        if valor in ("", None):
            if c.get("obrigatorio"):
                raise ValueError(f"O campo '{nome}' é obrigatório.")
            doc[c["nome"]] = None
        elif c["tipo"] in ("number", "ano"):
            try:
                n = float(str(valor).replace(",", "."))
            except ValueError:
                raise ValueError(f"O campo '{nome}' precisa ser um número.")
            if c["tipo"] == "ano" and not (n.is_integer() and 2000 <= n <= 2100):
                raise ValueError("Escolha um ano válido.")
            doc[c["nome"]] = int(n) if n.is_integer() else n
        elif c["tipo"] in ("select", "radio"):
            if c.get("depende_de"):
                permitidas = c["opcoes_por"].get(doc.get(c["depende_de"]), [])
            else:
                permitidas = c["opcoes"]
            if valor not in permitidas:
                raise ValueError(f"Escolha uma opção válida em '{nome}'.")
            doc[c["nome"]] = valor
        else:
            doc[c["nome"]] = valor
    return doc


def para_json(doc):
    doc["_id"] = str(doc["_id"])
    return doc


def oid(valor):
    try:
        return ObjectId(valor)
    except InvalidId:
        raise ValueError("ID inválido.")


@app.errorhandler(ValueError)
def erro_validacao(e):
    return jsonify(erro=str(e)), 400


@app.errorhandler(PyMongoError)
def erro_mongo(e):
    return jsonify(erro="Não foi possível acessar o MongoDB. Confira o MONGO_URI no arquivo .env."), 503


@app.after_request
def liberar_cors(resp):
    """Permite que o index.html aberto como arquivo (file://) converse com este servidor."""
    resp.headers["Access-Control-Allow-Origin"] = CORS_ORIGIN
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return resp


@app.get("/")
def index():
    return send_file(Path(__file__).parent / "index.html")


@app.get("/api/campos")
def campos():
    return jsonify(CAMPOS)


@app.get("/api/status")
def status():
    client.admin.command("ping")  # se o banco não responder, cai no erro 503 acima
    return jsonify(ok=True, banco=DB_NAME, colecao=COLLECTION)


@app.get("/api/registros")
def listar():
    return jsonify([para_json(d) for d in colecao.find().sort("_id", -1)])


@app.post("/api/registros")
def criar():
    doc = limpar(request.get_json(force=True))
    doc["_id"] = colecao.insert_one(doc).inserted_id
    return jsonify(para_json(doc)), 201


@app.put("/api/registros/<id>")
def atualizar(id):
    doc = limpar(request.get_json(force=True))
    r = colecao.update_one({"_id": oid(id)}, {"$set": doc})
    if r.matched_count == 0:
        return jsonify(erro="Registro não encontrado."), 404
    return jsonify(ok=True)


@app.delete("/api/registros/<id>")
def excluir(id):
    colecao.delete_one({"_id": oid(id)})
    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
