from datetime import datetime


class Produto:
    REQUIRED_FIELDS = [
        "nome",
        "preco_custo",
        "preco_venda",
        "quantidade",
        "estoque_minimo",
    ]

    OPTIONAL_FIELDS = [
        "sku",
        "codigo_barra",
        "ean",
        "categoria",
        "subcategoria",
        "marca",
        "descricao",
        "foto_produto",
        "margem_lucro",
        "preco_promocional",
        "estoque_maximo",
        "localizacao_estoque",
        "fornecedor",
        "fornecedor_id",
        "data_entrada",
        "data_validade",
        "ncm",
        "unidade_medida",
        "cfop",
        "lote",
        "numero_serie",
        "variacoes",
        "observacoes",
        "status",
        "secao_id",
        "historico_movimentacao",
    ]

    def __init__(
        self,
        nome,
        preco_custo,
        preco_venda,
        quantidade,
        estoque_minimo,
        categoria=None,
        subcategoria=None,
        marca=None,
        descricao=None,
        foto_produto=None,
        sku=None,
        codigo_barra=None,
        ean=None,
        margem_lucro=None,
        preco_promocional=None,
        estoque_maximo=None,
        localizacao_estoque=None,
        fornecedor=None,
        fornecedor_id=None,
        data_entrada=None,
        data_validade=None,
        ncm=None,
        unidade_medida="un",
        cfop=None,
        lote=None,
        numero_lote=None,
        numero_serie=None,
        variacoes=None,
        observacoes=None,
        ativo=True,
        status=None,
        secao_id=None,
        historico_movimentacao=None,
        controlar_lote=True,
        controlar_validade=True,
        aplicar_peps=True,
        estoque_por_lote=None,
    ):
        self.nome = nome
        self.sku = sku
        self.codigo_barra = codigo_barra
        self.ean = ean
        self.categoria = categoria
        self.subcategoria = subcategoria
        self.marca = marca
        self.descricao = descricao
        self.foto_produto = foto_produto

        self.preco_custo = float(preco_custo)
        self.preco_venda = float(preco_venda)
        self.margem_lucro = self._calcular_margem(margem_lucro)
        self.preco_promocional = float(preco_promocional) if preco_promocional not in (None, "") else None

        self.quantidade = int(quantidade)
        self.estoque_minimo = int(estoque_minimo)
        self.estoque_maximo = int(estoque_maximo) if estoque_maximo not in (None, "") else None
        self.localizacao_estoque = localizacao_estoque
        self.fornecedor = fornecedor
        self.fornecedor_id = fornecedor_id
        self.data_entrada = self._parse_date(data_entrada) or datetime.now()
        self.data_validade = self._parse_date(data_validade)

        self.ncm = ncm
        self.unidade_medida = unidade_medida
        self.cfop = cfop

        self.lote = lote if lote is not None else numero_lote
        self.numero_lote = self.lote
        self.numero_serie = numero_serie
        self.variacoes = variacoes if variacoes is not None else {}

        self.ativo = bool(ativo)
        self.status = status if status else ("ativo" if self.ativo else "inativo")
        if self.status == "inativo":
            self.ativo = False

        self.observacoes = observacoes
        self.secao_id = secao_id
        self.historico_movimentacao = historico_movimentacao if historico_movimentacao is not None else []
        self.controlar_lote = bool(controlar_lote)
        self.controlar_validade = bool(controlar_validade)
        self.aplicar_peps = bool(aplicar_peps)
        self.estoque_por_lote = estoque_por_lote if estoque_por_lote is not None else []

        self.data_criacao = datetime.now()
        self.data_atualizacao = datetime.now()

    @staticmethod
    def _parse_date(value):
        if value in (None, ""):
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            value = value.strip()
            for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y"):
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                raise ValueError(f"Data invalida: {value}")
        raise ValueError("Formato de data invalido.")

    def _calcular_margem(self, margem_lucro):
        if margem_lucro not in (None, ""):
            return float(margem_lucro)
        if self.preco_custo <= 0:
            return 0.0
        return round(((self.preco_venda - self.preco_custo) / self.preco_custo) * 100, 2)

    def to_dict(self):
        return self.__dict__
