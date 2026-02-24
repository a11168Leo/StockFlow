from typing import Iterable

from bson import ObjectId
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.core.security import assert_token_type, decode_token
from backend.services.usuario_service import UsuarioService

bearer_scheme = HTTPBearer(auto_error=False)


def _resolve_user_from_credentials(credentials: HTTPAuthorizationCredentials | None):
    if not credentials:
        return None

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Token Bearer obrigatorio.")

    payload = decode_token(credentials.credentials)
    assert_token_type(payload, "access")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token sem usuario.")

    try:
        oid = ObjectId(user_id)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Token com usuario invalido.") from exc

    usuario = UsuarioService.buscar_usuario_por_id(oid)
    if not usuario or not usuario.get("ativo", True):
        raise HTTPException(status_code=401, detail="Usuario nao autenticado.")
    return usuario


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    usuario = _resolve_user_from_credentials(credentials)
    if not usuario:
        raise HTTPException(status_code=401, detail="Token Bearer obrigatorio.")
    return usuario


def get_optional_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)):
    return _resolve_user_from_credentials(credentials)


def require_roles(usuario: dict, allowed_roles: Iterable[str]):
    role = usuario.get("perfil")
    allowed = set(allowed_roles)
    if role not in allowed:
        raise HTTPException(status_code=403, detail="Sem permissao para esta operacao.")
