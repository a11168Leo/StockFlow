from backend.database.connection import mongodb
from backend.models.secao_model import Secao
from bson import ObjectId

secoes_collection = mongodb.get_collection("secoes")

class SecaoService:

    @staticmethod
    def criar_secao(secao: Secao):
        return secoes_collection.insert_one(secao.to_dict())

    @staticmethod
    def listar_secoes():
        return list(secoes_collection.find())
