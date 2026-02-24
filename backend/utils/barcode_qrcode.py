from backend.models.movimentacao_model import Movimentacao
from backend.services.estoque_lote_service import EstoqueLoteService
from backend.services.movimentacao_service import MovimentacaoService
from backend.services.produto_service import ProdutoService
from backend.utils.alertas import verificar_estoque


def processar_scan(codigo, tipo, quantidade, usuario_id, numero_lote=None, data_validade=None):
    if tipo not in ["entrada", "saida"]:
        raise ValueError("Tipo invalido. Use 'entrada' ou 'saida'.")

    if quantidade <= 0:
        raise ValueError("Quantidade deve ser maior que zero.")

    produto = ProdutoService.buscar_por_codigo(codigo)
    if not produto:
        raise ValueError(f"Produto com codigo {codigo} nao encontrado.")

    novo_qtde = produto["quantidade"] + quantidade if tipo == "entrada" else produto["quantidade"] - quantidade
    if novo_qtde < 0:
        raise ValueError(f"Nao e possivel fazer saida. Estoque insuficiente ({produto['quantidade']}).")

    ProdutoService.atualizar_estoque(produto["_id"], novo_qtde)

    lote_movimentado = numero_lote or produto.get("numero_lote")
    validade_movimentada = data_validade or produto.get("data_validade")

    info_peps = None
    if tipo == "entrada":
        lote_movimentado = EstoqueLoteService.registrar_entrada(
            produto_id=produto["_id"],
            quantidade=quantidade,
            numero_lote=lote_movimentado,
            data_validade=validade_movimentada,
        )
    else:
        info_peps = EstoqueLoteService.consumir_saida(
            produto=produto,
            quantidade=quantidade,
            usuario_id=usuario_id,
            numero_lote_escolhido=lote_movimentado,
        )
        lote_movimentado = info_peps.get("numero_lote")
        validade_movimentada = info_peps.get("data_validade")

    mov = Movimentacao(
        produto_id=produto["_id"],
        tipo=tipo,
        quantidade=quantidade,
        preco_unitario=produto["preco_custo"],
        usuario_id=usuario_id,
        numero_lote=lote_movimentado,
        data_validade=validade_movimentada,
        origem="scan",
        lote_esperado_peps=info_peps.get("lote_esperado_peps") if info_peps else None,
        violacao_peps=info_peps.get("violacao_peps", False) if info_peps else False,
    )
    MovimentacaoService.registrar_movimentacao(mov)

    verificar_estoque()

    response = {"produto": produto["nome"], "novo_estoque": novo_qtde, "tipo": tipo}
    if info_peps:
        response["peps"] = info_peps
    return response
