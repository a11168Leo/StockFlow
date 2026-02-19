from backend.services.produto_service import ProdutoService
from backend.services.alerta_service import AlertaService
from backend.models.alerta_model import AlertaEstoque

def verificar_estoque(margin=0):
    """
    Verifica produtos abaixo do estoque mínimo ajustado pela margem
    e cria alertas para admin e gerentes.
    margin: percentual de tolerância (ex: 10 para 10%)
    """
    produtos = ProdutoService.listar_produtos()
    alertas_criados = []

    for p in produtos:
        limite = p["estoque_minimo"] * (1 + margin/100)
        if p["quantidade"] <= limite:
            # Pegamos ids de admin e gerente para notificação
            from backend.services.usuario_service import UsuarioService
            usuarios = UsuarioService.listar_usuarios()
            notificados = [u["_id"] for u in usuarios if u["perfil"] in ["admin", "gerente"]]
            alerta = AlertaEstoque(
                produto_id=p["_id"],
                quantidade_atual=p["quantidade"],
                quantidade_minima=limite,
                usuario_notificado_ids=notificados
            )
            AlertaService.criar_alerta(alerta)
            alertas_criados.append(alerta.to_dict())

    return alertas_criados
