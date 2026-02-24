import csv
import json

from backend.models.produto_model import Produto
from backend.services.produto_service import ProdutoService


REQUIRED_COLUMNS = ["nome", "preco_custo", "preco_venda", "quantidade", "estoque_minimo"]


def _parse_variacoes(raw):
    if raw in (None, ""):
        return {}
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw)
    except Exception:
        return {"valor": raw}


def _parse_bool(raw, default):
    if raw in (None, ""):
        return default
    return str(raw).strip().lower() in ("true", "1", "sim", "yes")


def importar_produtos_csv(caminho_arquivo):
    adicionados = 0
    com_erro = []

    with open(caminho_arquivo, newline="", encoding="utf-8") as csvfile:
        leitor = csv.DictReader(csvfile)
        for row in leitor:
            try:
                faltantes = [col for col in REQUIRED_COLUMNS if not row.get(col)]
                if faltantes:
                    raise ValueError(f"Campos obrigatorios ausentes: {', '.join(faltantes)}")

                produto = Produto(
                    nome=row.get("nome"),
                    sku=row.get("sku"),
                    codigo_barra=row.get("codigo_barra"),
                    ean=row.get("ean"),
                    categoria=row.get("categoria"),
                    subcategoria=row.get("subcategoria"),
                    marca=row.get("marca"),
                    descricao=row.get("descricao"),
                    foto_produto=row.get("foto_produto"),
                    preco_custo=row.get("preco_custo"),
                    preco_venda=row.get("preco_venda"),
                    margem_lucro=row.get("margem_lucro"),
                    preco_promocional=row.get("preco_promocional"),
                    quantidade=row.get("quantidade"),
                    estoque_minimo=row.get("estoque_minimo"),
                    estoque_maximo=row.get("estoque_maximo"),
                    localizacao_estoque=row.get("localizacao_estoque"),
                    fornecedor=row.get("fornecedor"),
                    fornecedor_id=row.get("fornecedor_id"),
                    data_entrada=row.get("data_entrada"),
                    data_validade=row.get("data_validade"),
                    ncm=row.get("ncm"),
                    unidade_medida=row.get("unidade_medida") or "un",
                    cfop=row.get("cfop"),
                    lote=row.get("lote") or row.get("numero_lote"),
                    numero_serie=row.get("numero_serie"),
                    variacoes=_parse_variacoes(row.get("variacoes")),
                    observacoes=row.get("observacoes"),
                    status=row.get("status"),
                    ativo=(row.get("ativo", "true").strip().lower() != "false"),
                    secao_id=row.get("secao_id"),
                    controlar_lote=_parse_bool(row.get("controlar_lote"), True),
                    controlar_validade=_parse_bool(row.get("controlar_validade"), True),
                    aplicar_peps=_parse_bool(row.get("aplicar_peps"), True),
                    estoque_por_lote=_parse_variacoes(row.get("estoque_por_lote")),
                )
                ProdutoService.criar_produto(produto)
                adicionados += 1
            except Exception as exc:
                com_erro.append({"linha": row, "erro": str(exc)})

    return {"adicionados": adicionados, "com_erro": com_erro}
