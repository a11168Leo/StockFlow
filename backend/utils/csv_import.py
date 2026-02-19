import csv
from backend.services.produto_service import ProdutoService
from backend.models.produto_model import Produto

def importar_produtos_csv(caminho_arquivo):
    """
    Lê arquivo CSV e adiciona produtos ao estoque.
    Se o produto com mesmo nome + lote já existir, não adiciona.
    CSV esperado: nome,categoria,preco_custo,preco_venda,quantidade,estoque_minimo,secao_id,codigo_barra,numero_lote,data_validade
    """
    adicionados = 0
    com_erro = []

    with open(caminho_arquivo, newline='', encoding='utf-8') as csvfile:
        leitor = csv.DictReader(csvfile)
        for row in leitor:
            try:
                produto = Produto(
                    nome=row["nome"],
                    categoria=row["categoria"],
                    preco_custo=float(row["preco_custo"]),
                    preco_venda=float(row["preco_venda"]),
                    quantidade=int(row["quantidade"]),
                    estoque_minimo=int(row["estoque_minimo"]),
                    secao_id=row["secao_id"],
                    codigo_barra=row.get("codigo_barra"),
                    numero_lote=row.get("numero_lote"),
                    data_validade=row.get("data_validade")
                )
                ProdutoService.criar_produto(produto)
                adicionados += 1
            except Exception as e:
                com_erro.append({"linha": row, "erro": str(e)})

    return {"adicionados": adicionados, "com_erro": com_erro}
