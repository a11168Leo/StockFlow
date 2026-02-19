from backend.database.connection import mongodb
from backend.models.movimentacao_model import Movimentacao

movimentacoes_collection = mongodb.get_collection("movimentacoes")

class MovimentacaoService:

    @staticmethod
    def registrar_movimentacao(mov: Movimentacao):
        return movimentacoes_collection.insert_one(mov.to_dict())

    @staticmethod
    def listar_movimentacoes():
        return list(movimentacoes_collection.find())
