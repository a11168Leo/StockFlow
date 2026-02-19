from backend.services.produto_service import ProdutoService
from backend.services.movimentacao_service import MovimentacaoService
from backend.models.movimentacao_model import Movimentacao

def processar_scan(codigo, tipo, quantidade, usuario_id):
    """
    Processa entrada ou saída via código de barras / QRCode.
    codigo: pode ser código de barras ou QRCode do produto
    tipo: 'entrada' ou 'saida'
    quantidade: int
    usuario_id: quem fez a operação
    """
    # Busca produto pelo código de barras
    produtos = ProdutoService.listar_produtos()
    produto = next((p for p in produtos if p.get("codigo_barra") == codigo), None)

    if not produto:
        raise ValueError(f"Produto com código {codigo} não encontrado.")

    novo_qtde = produto["quantidade"] + quantidade if tipo == "entrada" else produto["quantidade"] - quantidade
    if novo_qtde < 0:
        raise ValueError(f"Não é possível fazer saída. Estoque insuficiente ({produto['quantidade']}).")

    # Atualiza estoque
    ProdutoService.atualizar_estoque(produto["_id"], novo_qtde)

    # Registra movimentação
    mov = Movimentacao(
        produto_id=produto["_id"],
        tipo=tipo,
        quantidade=quantidade,
        preco_unitario=produto["preco_custo"],
        usuario_id=usuario_id,
        numero_lote=produto.get("numero_lote"),
        data_validade=produto.get("data_validade")
    )
    MovimentacaoService.registrar_movimentacao(mov)

    return {"produto": produto["nome"], "novo_estoque": novo_qtde}
