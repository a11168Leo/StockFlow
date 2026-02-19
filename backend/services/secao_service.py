from backend.database.connection import mongodb
from backend.models.secao_model import Secao
from bson import ObjectId

secoes_collection = mongodb.get_collection("secoes")

class SecaoService:

    @staticmethod
    def criar_secao(secao: Secao):
        # Evita duplicação de seção com mesmo nome
        if secoes_collection.find_one({"nome": secao.nome}):
            raise ValueError(f"Seção '{secao.nome}' já existe.")
        return secoes_collection.insert_one(secao.to_dict())

    @staticmethod
    def listar_secoes():
        return list(secoes_collection.find())

    @staticmethod
    def buscar_secao_por_id(secao_id):
        return secoes_collection.find_one({"_id": ObjectId(secao_id)})
