from datetime import datetime

from bson import ObjectId

from backend.database.connection import mongodb
from backend.models.tarefa_model import Tarefa


tarefas_collection = mongodb.get_collection("tarefas")


class TarefaService:
    @staticmethod
    def criar_tarefa(tarefa: Tarefa):
        return tarefas_collection.insert_one(tarefa.to_dict())

    @staticmethod
    def criar_tarefa_sistema_se_nao_existir(titulo, descricao, responsavel_id, tipo, prioridade="alta"):
        filtro = {
            "titulo": titulo,
            "responsavel_id": responsavel_id,
            "status": {"$in": ["pendente", "em andamento"]},
            "tipo": tipo,
            "origem": "sistema",
        }
        if tarefas_collection.find_one(filtro):
            return None

        tarefa = Tarefa(
            titulo=titulo,
            descricao=descricao,
            responsavel_id=responsavel_id,
            prioridade=prioridade,
            origem="sistema",
            tipo=tipo,
        )
        return tarefas_collection.insert_one(tarefa.to_dict())

    @staticmethod
    def listar_tarefas():
        return list(tarefas_collection.find())

    @staticmethod
    def listar_por_responsavel(responsavel_id):
        return list(tarefas_collection.find({"responsavel_id": responsavel_id}))

    @staticmethod
    def buscar_tarefa_por_id(tarefa_id):
        if isinstance(tarefa_id, str):
            tarefa_id = ObjectId(tarefa_id)
        return tarefas_collection.find_one({"_id": tarefa_id})

    @staticmethod
    def concluir_tarefa(tarefa_id):
        if isinstance(tarefa_id, str):
            tarefa_id = ObjectId(tarefa_id)
        return tarefas_collection.update_one(
            {"_id": tarefa_id},
            {"$set": {"status": "concluida", "data_conclusao": datetime.now()}},
        )
