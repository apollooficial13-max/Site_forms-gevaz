"""Testa a conexão com o MongoDB usando o MONGO_URI do arquivo .env."""
import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"), serverSelectionTimeoutMS=5000)

try:
    client.admin.command("ping")
    print("Conexão com o MongoDB funcionando!")
except Exception as erro:
    print("Falha na conexão:", erro)
