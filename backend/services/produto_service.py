from backend.database.connection import mongodb
from backend.models.produto_model import Produto
from bson import ObjectId

produtos_collection = mongodb.get_collection("produtos")

class ProdutoService:

    @staticmethod
    def criar_produto(produto: Produto):
        return produtos_collection.insert_one(produto.to_dict())

    @staticmethod
    def listar_produtos():
        return list(produtos_collection.find({"ativo": True}))

    @staticmethod
    def buscar_produto_por_id(produto_id):
        return produtos_collection.find_one({"_id": ObjectId(produto_id)})

    @staticmethod
    def atualizar_estoque(produto_id, nova_quantidade):
        return produtos_collection.update_one(
            {"_id": ObjectId(produto_id)},
            {"$set": {"quantidade": nova_quantidade}}
        )

    @staticmethod
    def desativar_produto(produto_id):
        return produtos_collection.update_one(
            {"_id": ObjectId(produto_id)},
            {"$set": {"ativo": False}}
        )
