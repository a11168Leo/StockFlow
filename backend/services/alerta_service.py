from backend.database.connection import mongodb
from backend.models.alerta_model import AlertaEstoque
from bson import ObjectId
from datetime import datetime

alertas_collection = mongodb.get_collection("alertas")

class AlertaService:

    @staticmethod
    def criar_alerta(alerta: AlertaEstoque):
        return alertas_collection.insert_one(alerta.to_dict())

    @staticmethod
    def listar_alertas():
        return list(alertas_collection.find())

    @staticmethod
    def marcar_visualizado(alerta_id):
        return alertas_collection.update_one(
            {"_id": ObjectId(alerta_id)},
            {"$set": {"status": "visualizado"}}
        )
