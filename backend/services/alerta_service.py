from bson import ObjectId

from backend.database.connection import mongodb
from backend.models.alerta_model import AlertaEstoque


alertas_collection = mongodb.get_collection("alertas")


class AlertaService:
    @staticmethod
    def criar_alerta(alerta: AlertaEstoque):
        return alertas_collection.insert_one(alerta.to_dict())

    @staticmethod
    def criar_alerta_estoque_se_nao_existir(alerta: AlertaEstoque):
        filtro = {
            "produto_id": alerta.produto_id,
            "status": "pendente",
        }
        if alertas_collection.find_one(filtro):
            return None
        return alertas_collection.insert_one(alerta.to_dict())

    @staticmethod
    def criar_alerta_operacional_se_nao_existir(
        tipo,
        mensagem,
        usuario_notificado_ids,
        produto_id=None,
        chave_deduplicacao=None,
    ):
        filtro = {"status": "pendente", "tipo": tipo}
        if chave_deduplicacao:
            filtro["chave_deduplicacao"] = chave_deduplicacao
        elif produto_id is not None:
            filtro["produto_id"] = produto_id
            filtro["mensagem"] = mensagem
        else:
            filtro["mensagem"] = mensagem

        if alertas_collection.find_one(filtro):
            return None

        doc = {
            "tipo": tipo,
            "mensagem": mensagem,
            "produto_id": produto_id,
            "usuario_notificado_ids": usuario_notificado_ids,
            "status": "pendente",
            "chave_deduplicacao": chave_deduplicacao,
        }
        return alertas_collection.insert_one(doc)

    @staticmethod
    def listar_alertas():
        return list(alertas_collection.find())

    @staticmethod
    def marcar_visualizado(alerta_id):
        if isinstance(alerta_id, str):
            alerta_id = ObjectId(alerta_id)
        return alertas_collection.update_one(
            {"_id": alerta_id},
            {"$set": {"status": "visualizado"}},
        )
