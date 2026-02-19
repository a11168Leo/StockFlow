from backend.database.connection import mongodb
from backend.models.produto_model import Produto
from bson import ObjectId

produtos_collection = mongodb.get_collection("produtos")

class ProdutoService:

    @staticmethod
    def criar_produto(produto: Produto):
        # Evita duplicação de produto com mesmo nome e lote
        filtro = {"nome": produto.nome, "numero_lote": produto.numero_lote}
        if produtos_collection.find_one(filtro):
            raise ValueError(f"Produto '{produto.nome}' com lote '{produto.numero_lote}' já existe.")
        return produtos_collection.insert_one(produto.to_dict())

    @staticmethod
    def listar_produtos(ativos=True):
        filtro = {"ativo": True} if ativos else {}
        return list(produtos_collection.find(filtro))

    @staticmethod
    def buscar_produto_por_id(produto_id):
        return produtos_collection.find_one({"_id": ObjectId(produto_id)})

    @staticmethod
    def atualizar_estoque(produto_id, nova_quantidade):
        if nova_quantidade < 0:
            raise ValueError("Quantidade não pode ser negativa.")
        return produtos_collection.update_one(
            {"_id": ObjectId(produto_id)},
            {"$set": {"quantidade": nova_quantidade}}
        )

    @staticmethod
    def atualizar_produto(produto_id, dados: dict):
        # Permite atualizar qualquer campo de produto
        return produtos_collection.update_one(
            {"_id": ObjectId(produto_id)},
            {"$set": dados}
        )

    @staticmethod
    def desativar_produto(produto_id):
        return produtos_collection.update_one(
            {"_id": ObjectId(produto_id)},
            {"$set": {"ativo": False}}
        )
