from fastapi import HTTPException

from backend.core.config import get_settings
from backend.core.security import (
    assert_token_type,
    create_access_token,
    create_refresh_token,
    decode_token,
)


def test_access_token_roundtrip(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "unit-secret")
    get_settings.cache_clear()

    token = create_access_token(user_id="507f1f77bcf86cd799439011", perfil="admin")
    payload = decode_token(token)

    assert payload["sub"] == "507f1f77bcf86cd799439011"
    assert payload["perfil"] == "admin"
    assert payload["type"] == "access"


def test_refresh_token_contains_jti(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "unit-secret")
    get_settings.cache_clear()

    token, jti, _ = create_refresh_token(user_id="507f1f77bcf86cd799439011")
    payload = decode_token(token)

    assert payload["sub"] == "507f1f77bcf86cd799439011"
    assert payload["jti"] == jti
    assert payload["type"] == "refresh"


def test_assert_token_type_rejects_wrong_type(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "unit-secret")
    get_settings.cache_clear()

    token = create_access_token(user_id="507f1f77bcf86cd799439011", perfil="admin")
    payload = decode_token(token)

    try:
        assert_token_type(payload, "refresh")
        raise AssertionError("expected type validation to fail")
    except HTTPException as exc:
        assert exc.status_code == 401
