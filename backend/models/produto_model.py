from datetime import datetime

class Produto:
    def __init__(self, nome, categoria, preco_custo, preco_venda, quantidade,
                 estoque_minimo, secao_id, ativo=True, codigo_barra=None,
                 numero_lote=None, data_validade=None):
        """
        Produto completo com lote, validade e código de barras.
        """
        self.nome = nome
        self.categoria = categoria
        self.preco_custo = preco_custo
        self.preco_venda = preco_venda
        self.quantidade = quantidade
        self.estoque_minimo = estoque_minimo
        self.secao_id = secao_id
        self.ativo = ativo
        self.codigo_barra = codigo_barra
        self.numero_lote = numero_lote
        self.data_validade = data_validade
        self.data_criacao = datetime.now()

    def to_dict(self):
        return self.__dict__
