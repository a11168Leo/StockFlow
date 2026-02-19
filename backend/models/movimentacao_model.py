from datetime import datetime

class Movimentacao:
    def __init__(self, produto_id, tipo, quantidade, preco_unitario, usuario_id,
                 numero_lote=None, data_validade=None):
        """
        Movimentação de estoque (entrada, saída, ajuste).
        """
        self.produto_id = produto_id
        self.tipo = tipo  # 'entrada', 'saida', 'ajuste'
        self.quantidade = quantidade
        self.preco_unitario = preco_unitario
        self.usuario_id = usuario_id
        self.numero_lote = numero_lote
        self.data_validade = data_validade
        self.data = datetime.now()

    def to_dict(self):
        return self.__dict__
