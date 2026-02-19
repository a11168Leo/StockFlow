import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class MongoDBConnection:
    def __init__(self):
        uri = os.getenv("MONGO_URI")
        if not uri:
            raise RuntimeError("❌ MONGO_URI não encontrada no .env")

        self.client = MongoClient(uri)
        # Define explicitamente o banco
        self.db = self.client.get_database("estoque_db")

    def get_collection(self, name: str):
        return self.db[name]

mongodb = MongoDBConnection()
