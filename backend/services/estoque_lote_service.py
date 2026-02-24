from datetime import datetime, timezone

from bson import ObjectId

from backend.database.connection import mongodb
from backend.services.alerta_service import AlertaService
from backend.services.tarefa_service import TarefaService
from backend.services.usuario_service import UsuarioService


estoque_lotes_collection = mongodb.get_collection("estoque_lotes")


def _normalize_datetime(value):
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
        return datetime.fromisoformat(value)
    raise ValueError("Data invalida para lote.")


def _default_lote():
    return f"SEM-LOTE-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"


class EstoqueLoteService:
    @staticmethod
    def registrar_entrada(produto_id, quantidade, numero_lote=None, data_validade=None, data_entrada=None):
        if isinstance(produto_id, str):
            produto_id = ObjectId(produto_id)
        if quantidade <= 0:
            raise ValueError("Quantidade de entrada deve ser maior que zero.")

        numero_lote = numero_lote or _default_lote()
        validade = _normalize_datetime(data_validade)
        entrada = _normalize_datetime(data_entrada) or datetime.now()

        estoque_lotes_collection.update_one(
            {"produto_id": produto_id, "numero_lote": numero_lote},
            {
                "$inc": {"quantidade_disponivel": int(quantidade)},
                "$set": {
                    "data_validade": validade,
                    "data_entrada": entrada,
                    "atualizado_em": datetime.now(),
                },
                "$setOnInsert": {"criado_em": datetime.now()},
            },
            upsert=True,
        )
        return numero_lote

    @staticmethod
    def listar_lotes_disponiveis(produto_id):
        if isinstance(produto_id, str):
            produto_id = ObjectId(produto_id)
        lotes = list(
            estoque_lotes_collection.find(
                {"produto_id": produto_id, "quantidade_disponivel": {"$gt": 0}}
            )
        )
        lotes.sort(
            key=lambda lote: (
                lote.get("data_validade") or datetime.max,
                lote.get("data_entrada") or datetime.min,
                lote.get("numero_lote") or "",
            )
        )
        return lotes

    @staticmethod
    def _notificar_violacao_peps(produto, lote_correto, lote_escolhido, usuario_id):
        usuarios = UsuarioService.listar_por_perfis(["lider", "funcionario"])
        ids_notificados = [u["_id"] for u in usuarios]

        mensagem = (
            f"Saida fora de PEPS no produto '{produto.get('nome')}'. "
            f"Lote esperado: {lote_correto.get('numero_lote')}. "
            f"Lote utilizado: {lote_escolhido.get('numero_lote')}."
        )
        chave = (
            f"peps:{produto.get('_id')}:{lote_correto.get('numero_lote')}:"
            f"{lote_escolhido.get('numero_lote')}"
        )
        AlertaService.criar_alerta_operacional_se_nao_existir(
            tipo="violacao_peps",
            mensagem=mensagem,
            usuario_notificado_ids=ids_notificados,
            produto_id=produto.get("_id"),
            chave_deduplicacao=chave,
        )

        lideres = [u for u in usuarios if u.get("perfil") == "lider"]
        for lider in lideres:
            TarefaService.criar_tarefa_sistema_se_nao_existir(
                titulo=f"Ajustar PEPS: {produto.get('nome')}",
                descricao=mensagem + " Ajustar exposicao e orientar equipe.",
                responsavel_id=lider["_id"],
                tipo="ajuste_peps",
                prioridade="alta",
            )

        if usuario_id:
            usuario = UsuarioService.buscar_usuario_por_id(usuario_id)
            if usuario and usuario.get("perfil") == "funcionario":
                TarefaService.criar_tarefa_sistema_se_nao_existir(
                    titulo=f"Reorganizar lote: {produto.get('nome')}",
                    descricao=mensagem + " Reorganizar produto para saida correta.",
                    responsavel_id=usuario["_id"],
                    tipo="ajuste_peps",
                    prioridade="normal",
                )

    @staticmethod
    def consumir_saida(produto, quantidade, usuario_id=None, numero_lote_escolhido=None):
        produto_id = produto.get("_id")
        lotes = EstoqueLoteService.listar_lotes_disponiveis(produto_id)
        if not lotes:
            if not produto.get("controlar_lote", True):
                return {
                    "numero_lote": None,
                    "data_validade": produto.get("data_validade"),
                    "lote_esperado_peps": None,
                    "violacao_peps": False,
                }

            quantidade_legacy = int(produto.get("quantidade") or 0)
            if quantidade_legacy > 0:
                EstoqueLoteService.registrar_entrada(
                    produto_id=produto_id,
                    quantidade=quantidade_legacy,
                    numero_lote=produto.get("numero_lote"),
                    data_validade=produto.get("data_validade"),
                    data_entrada=produto.get("data_entrada"),
                )
                lotes = EstoqueLoteService.listar_lotes_disponiveis(produto_id)

        if not lotes:
            raise ValueError("Nao ha lotes disponiveis para este produto.")
        if quantidade <= 0:
            raise ValueError("Quantidade de saida deve ser maior que zero.")

        lote_correto = lotes[0]
        lote_alvo = lote_correto

        if numero_lote_escolhido:
            lote_manual = next(
                (l for l in lotes if l.get("numero_lote") == numero_lote_escolhido),
                None,
            )
            if not lote_manual:
                raise ValueError("Lote informado nao encontrado ou sem saldo.")
            lote_alvo = lote_manual

            if lote_manual.get("numero_lote") != lote_correto.get("numero_lote"):
                EstoqueLoteService._notificar_violacao_peps(
                    produto=produto,
                    lote_correto=lote_correto,
                    lote_escolhido=lote_manual,
                    usuario_id=usuario_id,
                )

        if lote_alvo.get("quantidade_disponivel", 0) < quantidade:
            raise ValueError("Quantidade de saida maior que saldo do lote selecionado.")

        estoque_lotes_collection.update_one(
            {"_id": lote_alvo["_id"]},
            {
                "$inc": {"quantidade_disponivel": -int(quantidade)},
                "$set": {"atualizado_em": datetime.now()},
            },
        )

        return {
            "numero_lote": lote_alvo.get("numero_lote"),
            "data_validade": lote_alvo.get("data_validade"),
            "lote_esperado_peps": lote_correto.get("numero_lote"),
            "violacao_peps": lote_alvo.get("numero_lote") != lote_correto.get("numero_lote"),
        }
