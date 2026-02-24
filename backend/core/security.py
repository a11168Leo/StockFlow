import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException

from backend.core.config import get_settings


class TokenError(ValueError):
    pass


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(user_id: str, perfil: str) -> str:
    settings = get_settings()
    expire = _now_utc() + timedelta(minutes=settings.access_token_minutes)
    payload = {
        "sub": user_id,
        "perfil": perfil,
        "type": "access",
        "exp": expire,
        "iat": _now_utc(),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: str) -> tuple[str, str, datetime]:
    settings = get_settings()
    jti = str(uuid.uuid4())
    expire = _now_utc() + timedelta(days=settings.refresh_token_days)
    payload = {
        "sub": user_id,
        "type": "refresh",
        "jti": jti,
        "exp": expire,
        "iat": _now_utc(),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, jti, expire


def decode_token(token: str) -> dict:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Token expirado.") from exc
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Token invalido.") from exc


def assert_token_type(payload: dict, expected: str) -> None:
    token_type = payload.get("type")
    if token_type != expected:
        raise HTTPException(status_code=401, detail="Tipo de token invalido.")
