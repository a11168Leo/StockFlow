from datetime import datetime, timezone

from bson import ObjectId

from backend.database.connection import mongodb

refresh_tokens_collection = mongodb.get_collection("refresh_tokens")


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
