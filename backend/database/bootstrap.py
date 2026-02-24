from pymongo import ASCENDING

from backend.database.connection import mongodb


def ensure_indexes():
    usuarios = mongodb.get_collection("usuarios")
    produtos = mongodb.get_collection("produtos")
    tarefas = mongodb.get_collection("tarefas")
    alertas = mongodb.get_collection("alertas")
    movimentacoes = mongodb.get_collection("movimentacoes")
    fornecedores = mongodb.get_collection("fornecedores")
    estoque_lotes = mongodb.get_collection("estoque_lotes")

    usuarios.create_index([("email", ASCENDING)], unique=True, name="uniq_email")
    usuarios.create_index([("caixa_id", ASCENDING)], unique=True, name="uniq_caixa_id")
    usuarios.create_index([("perfil", ASCENDING)], name="idx_usuario_perfil")

    produtos.create_index(
        [("nome", ASCENDING), ("numero_lote", ASCENDING)],
        unique=True,
        name="uniq_nome_lote",
    )
    produtos.create_index(
        [("codigo_barra", ASCENDING)],
        unique=True,
        sparse=True,
        name="uniq_codigo_barra",
    )
    produtos.create_index(
        [("ean", ASCENDING)],
        unique=True,
        sparse=True,
        name="uniq_ean",
    )
    produtos.create_index(
        [("sku", ASCENDING)],
        unique=True,
        sparse=True,
        name="uniq_sku",
    )
    produtos.create_index([("ativo", ASCENDING)], name="idx_produto_ativo")
    produtos.create_index([("categoria", ASCENDING)], name="idx_produto_categoria")

    tarefas.create_index([("status", ASCENDING)], name="idx_tarefa_status")
    tarefas.create_index([("responsavel_id", ASCENDING)], name="idx_tarefa_responsavel")
    tarefas.create_index([("origem", ASCENDING)], name="idx_tarefa_origem")

    alertas.create_index([("status", ASCENDING)], name="idx_alerta_status")
    alertas.create_index([("produto_id", ASCENDING)], name="idx_alerta_produto")

    movimentacoes.create_index([("produto_id", ASCENDING)], name="idx_mov_produto")
    movimentacoes.create_index([("data", ASCENDING)], name="idx_mov_data")

    fornecedores.create_index([("nome", ASCENDING)], unique=True, name="uniq_fornecedor_nome")

    estoque_lotes.create_index(
        [("produto_id", ASCENDING), ("numero_lote", ASCENDING)],
        unique=True,
        name="uniq_produto_lote",
    )
    estoque_lotes.create_index(
        [("produto_id", ASCENDING), ("data_validade", ASCENDING), ("data_entrada", ASCENDING)],
        name="idx_peps_ordem",
    )


def ensure_default_settings():
    configuracoes = mongodb.get_collection("configuracoes")
    existing = configuracoes.find_one({"chave": "margem_alerta_estoque"})
    if not existing:
        configuracoes.insert_one(
            {
                "chave": "margem_alerta_estoque",
                "valor": 0,
                "descricao": "Percentual de margem aplicado sobre estoque minimo para gerar alertas.",
            }
        )
