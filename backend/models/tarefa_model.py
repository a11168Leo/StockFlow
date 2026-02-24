from datetime import datetime


class Tarefa:
    def __init__(
        self,
        titulo,
        descricao,
        responsavel_id,
        status="pendente",
        prioridade="normal",
        origem="manual",
        tipo="operacional",
        prazo=None,
    ):
        self.titulo = titulo
        self.descricao = descricao
        self.responsavel_id = responsavel_id
        self.status = status  # 'pendente', 'em andamento', 'concluida'
        self.prioridade = prioridade  # 'baixa', 'normal', 'alta'
        self.origem = origem  # 'manual', 'sistema'
        self.tipo = tipo
        self.prazo = prazo
        self.data_criacao = datetime.now()
        self.data_conclusao = None

    def concluir(self):
        self.status = "concluida"
        self.data_conclusao = datetime.now()

    def to_dict(self):
        return self.__dict__
