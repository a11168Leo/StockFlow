from typing import Iterable

from bson import ObjectId
from fastapi import Header, HTTPException

from backend.services.usuario_service import UsuarioService


def get_current_user(x_user_id: str = Header(..., alias="X-User-Id")):
    try:
        user_id = ObjectId(x_user_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="X-User-Id invalido.") from exc

    usuario = UsuarioService.buscar_usuario_por_id(user_id)
    if not usuario or not usuario.get("ativo", True):
        raise HTTPException(status_code=401, detail="Usuario nao autenticado.")
    return usuario


def require_roles(usuario: dict, allowed_roles: Iterable[str]):
    role = usuario.get("perfil")
    allowed = set(allowed_roles)
    if role not in allowed:
        raise HTTPException(status_code=403, detail="Sem permissao para esta operacao.")
