from datetime import datetime


class AlertaEstoque:
    def __init__(
        self,
        produto_id,
        quantidade_atual,
        quantidade_minima,
        usuario_notificado_ids,
        margem_percentual=0,
        status="pendente",
    ):
        self.produto_id = produto_id
        self.quantidade_atual = quantidade_atual
        self.quantidade_minima = quantidade_minima
        self.margem_percentual = margem_percentual
        self.usuario_notificado_ids = usuario_notificado_ids
        self.data_alerta = datetime.now()
        self.status = status

    def to_dict(self):
        return self.__dict__
