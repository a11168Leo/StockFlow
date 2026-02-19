from datetime import datetime

class AlertaEstoque:
    def __init__(self, produto_id, quantidade_atual, quantidade_minima, usuario_notificado_ids):
        """
        Alerta de baixo estoque.
        usuario_notificado_ids: lista de IDs (admin e gerente) que recebem o alerta
        """
        self.produto_id = produto_id
        self.quantidade_atual = quantidade_atual
        self.quantidade_minima = quantidade_minima
        self.usuario_notificado_ids = usuario_notificado_ids
        self.data_alerta = datetime.now()
        self.status = "pendente"  # 'pendente', 'visualizado'

    def to_dict(self):
        return self.__dict__
