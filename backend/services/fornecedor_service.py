from backend.database.connection import mongodb
from backend.models.fornecedor_model import Fornecedor
from bson import ObjectId

fornecedores_collection = mongodb.get_collection("fornecedores")

class FornecedorService:

    @staticmethod
    def criar_fornecedor(fornecedor: Fornecedor):
        if fornecedores_collection.find_one({"nome": fornecedor.nome}):
            raise ValueError(f"Fornecedor '{fornecedor.nome}' já existe.")
        return fornecedores_collection.insert_one(fornecedor.to_dict())

    @staticmethod
    def listar_fornecedores():
        return list(fornecedores_collection.find())

    @staticmethod
    def buscar_fornecedor_por_id(fornecedor_id):
        return fornecedores_collection.find_one({"_id": ObjectId(fornecedor_id)})
