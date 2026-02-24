from datetime import datetime, timedelta, timezone

from bson import ObjectId

from backend.core.config import get_settings
from backend.database.connection import mongodb

refresh_tokens_collection = mongodb.get_collection("refresh_tokens")
password_reset_tokens_collection = mongodb.get_collection("password_reset_tokens")


class AuthService:
    @staticmethod
    def salvar_refresh_token(user_id: str, jti: str, expira_em: datetime) -> None:
        refresh_tokens_collection.insert_one(
            {
                "usuario_id": ObjectId(user_id),
                "jti": jti,
                "expira_em": expira_em,
                "revogado": False,
                "criado_em": datetime.now(timezone.utc),
            }
        )

    @staticmethod
    def validar_refresh_token(user_id: str, jti: str) -> bool:
        token = refresh_tokens_collection.find_one(
            {
                "usuario_id": ObjectId(user_id),
                "jti": jti,
                "revogado": False,
            }
        )
        if not token:
            return False
        expira_em = token.get("expira_em")
        if expira_em is None:
            return False
        if expira_em.tzinfo is None:
            expira_em = expira_em.replace(tzinfo=timezone.utc)
        return expira_em > datetime.now(timezone.utc)

    @staticmethod
    def revogar_refresh_token(user_id: str, jti: str) -> None:
        refresh_tokens_collection.update_one(
            {
                "usuario_id": ObjectId(user_id),
                "jti": jti,
            },
            {"$set": {"revogado": True, "revogado_em": datetime.now(timezone.utc)}},
        )

    @staticmethod
    def revogar_todos_refresh_tokens(user_id: str) -> None:
        refresh_tokens_collection.update_many(
            {
                "usuario_id": ObjectId(user_id),
                "revogado": False,
            },
            {"$set": {"revogado": True, "revogado_em": datetime.now(timezone.utc)}},
        )

    @staticmethod
    def criar_token_reset_senha(user_id: str, token: str) -> datetime:
        settings = get_settings()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.password_reset_minutes)
        password_reset_tokens_collection.insert_one(
            {
                "usuario_id": ObjectId(user_id),
                "token": token,
                "expira_em": expires_at,
                "usado": False,
                "criado_em": datetime.now(timezone.utc),
            }
        )
        return expires_at

    @staticmethod
    def validar_token_reset_senha(token: str) -> dict | None:
        found = password_reset_tokens_collection.find_one({"token": token, "usado": False})
        if not found:
            return None
        expira_em = found.get("expira_em")
        if expira_em is None:
            return None
        if expira_em.tzinfo is None:
            expira_em = expira_em.replace(tzinfo=timezone.utc)
        if expira_em <= datetime.now(timezone.utc):
            return None
        return found

    @staticmethod
    def marcar_token_reset_como_usado(token: str) -> None:
        password_reset_tokens_collection.update_one(
            {"token": token},
            {"$set": {"usado": True, "usado_em": datetime.now(timezone.utc)}},
        )
