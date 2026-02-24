import os
from pathlib import Path

from pymongo import MongoClient
from pymongo.errors import PyMongoError

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover
    load_dotenv = None


ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT_DIR / ".env"
if load_dotenv:
    load_dotenv(dotenv_path=ENV_PATH, override=False)


class MongoDBConnection:
    def __init__(self):
        uri = os.getenv("MONGO_URI")
        if not uri:
            raise RuntimeError("MONGO_URI nao encontrada no .env")

        db_name = os.getenv("MONGO_DB_NAME", "estoque_db")

        try:
            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command("ping")
        except PyMongoError as exc:
            raise RuntimeError(f"Falha ao conectar ao MongoDB: {exc}") from exc

        self.db = self.client[db_name]

    def get_collection(self, name: str):
        return self.db[name]


mongodb = MongoDBConnection()
