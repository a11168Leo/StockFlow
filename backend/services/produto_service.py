from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from backend.database.connection import mongodb
from backend.models.produto_model import Produto


produtos_collection = mongodb.get_collection("produtos")


class ProdutoService:
    @staticmethod
    def criar_produto(produto: Produto):
        if produto.sku and produtos_collection.find_one({"sku": produto.sku}):
            raise ValueError(f"SKU '{produto.sku}' ja cadastrado.")

        if produto.numero_lote:
            filtro = {"nome": produto.nome, "numero_lote": produto.numero_lote}
            if produtos_collection.find_one(filtro):
                raise ValueError(f"Produto '{produto.nome}' com lote '{produto.numero_lote}' ja existe.")
        try:
            result = produtos_collection.insert_one(produto.to_dict())
        except DuplicateKeyError as exc:
            raise ValueError("Produto duplicado (sku, nome+lote, codigo_barra ou ean).") from exc
        return produtos_collection.find_one({"_id": result.inserted_id})

    @staticmethod
    def listar_produtos(ativos=True):
        filtro = {"ativo": True} if ativos else {}
        return list(produtos_collection.find(filtro))

    @staticmethod
    def buscar_produto_por_id(produto_id):
        if isinstance(produto_id, str):
            produto_id = ObjectId(produto_id)
        return produtos_collection.find_one({"_id": produto_id})

    @staticmethod
    def buscar_por_codigo(codigo):
        return produtos_collection.find_one(
            {
                "$or": [{"codigo_barra": codigo}, {"ean": codigo}],
                "ativo": True,
            }
        )

    @staticmethod
    def atualizar_estoque(produto_id, nova_quantidade):
        if nova_quantidade < 0:
            raise ValueError("Quantidade nao pode ser negativa.")
        if isinstance(produto_id, str):
            produto_id = ObjectId(produto_id)
        result = produtos_collection.update_one(
            {"_id": produto_id},
            {"$set": {"quantidade": nova_quantidade}},
        )
        if result.matched_count == 0:
            raise ValueError("Produto nao encontrado.")
        return produtos_collection.find_one({"_id": produto_id})

    @staticmethod
    def atualizar_produto(produto_id, dados: dict):
        if isinstance(produto_id, str):
            produto_id = ObjectId(produto_id)
        result = produtos_collection.update_one({"_id": produto_id}, {"$set": dados})
        if result.matched_count == 0:
            raise ValueError("Produto nao encontrado.")
        return produtos_collection.find_one({"_id": produto_id})

    @staticmethod
    def desativar_produto(produto_id):
        if isinstance(produto_id, str):
            produto_id = ObjectId(produto_id)
        return produtos_collection.update_one(
            {"_id": produto_id},
            {"$set": {"ativo": False}},
        )
