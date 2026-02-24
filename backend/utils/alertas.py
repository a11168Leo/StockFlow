from backend.models.alerta_model import AlertaEstoque
from backend.services.alerta_service import AlertaService
from backend.services.configuracao_service import ConfiguracaoService
from backend.services.produto_service import ProdutoService
from backend.services.tarefa_service import TarefaService
from backend.services.usuario_service import UsuarioService


def _usuarios_para_alerta():
    usuarios = UsuarioService.listar_por_perfis(["admin", "lider"])
    return [u["_id"] for u in usuarios]


def _lideres_ativos():
    return UsuarioService.listar_por_perfis(["lider"])


def verificar_estoque(margin=None):
    margem = ConfiguracaoService.get_margem_alerta_estoque() if margin is None else float(margin)
    produtos = ProdutoService.listar_produtos()
    alertas_criados = []

    notificados = _usuarios_para_alerta()
    lideres = _lideres_ativos()

    for p in produtos:
        limite = p["estoque_minimo"] * (1 + margem / 100)
        if p["quantidade"] <= limite:
            alerta = AlertaEstoque(
                produto_id=p["_id"],
                quantidade_atual=p["quantidade"],
                quantidade_minima=limite,
                margem_percentual=margem,
                usuario_notificado_ids=notificados,
            )
            inserted = AlertaService.criar_alerta_estoque_se_nao_existir(alerta)
            if inserted:
                alertas_criados.append(alerta.to_dict())

            for lider in lideres:
                TarefaService.criar_tarefa_sistema_se_nao_existir(
                    titulo=f"Verificar estoque: {p['nome']}",
                    descricao=(
                        f"Produto abaixo do limite ({p['quantidade']} <= {limite:.2f}). "
                        "Revisar estoque fisico e planejar reposicao."
                    ),
                    responsavel_id=lider["_id"],
                    tipo="auditoria_estoque",
                    prioridade="alta",
                )

    return alertas_criados
