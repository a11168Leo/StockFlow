from backend.database.connection import mongodb
from backend.models.tarefa_model import Tarefa
from bson import ObjectId

tarefas_collection = mongodb.get_collection("tarefas")

class TarefaService:

    @staticmethod
    def criar_tarefa(tarefa: Tarefa):
        return tarefas_collection.insert_one(tarefa.to_dict())

    @staticmethod
    def listar_tarefas():
        return list(tarefas_collection.find())

    @staticmethod
    def concluir_tarefa(tarefa_id):
        return tarefas_collection.update_one(
            {"_id": ObjectId(tarefa_id)},
            {"$set": {"status": "concluida", "data_conclusao": datetime.now()}}
        )
