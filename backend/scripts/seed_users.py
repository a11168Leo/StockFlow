from datetime import datetime, timezone

from backend.database.bootstrap import ensure_default_settings, ensure_indexes
from backend.database.connection import mongodb
from backend.models.usuario_model import PERFIS_VALIDOS, Usuario


USERS_TO_SEED = [
    {
        "nome": "Administrador Inicial",
        "email": "a11168@csmiguel.pt",
        "senha": "admin1234",
        "perfil": "admin",
        "caixa_id": 11168,
    },
    {
        "nome": "Funcionario Inicial",
        "email": "a11077@csmiguel.pt",
        "senha": "123456",
        "perfil": "funcionario",
        "caixa_id": 11077,
    },
]


def upsert_user(user: dict) -> str:
    perfil = user["perfil"]
    if perfil not in PERFIS_VALIDOS:
        raise ValueError(f"Perfil invalido para seed: {perfil}")

    usuarios = mongodb.get_collection("usuarios")
    now = datetime.now(timezone.utc)

    result = usuarios.update_one(
        {"email": user["email"]},
        {
            "$set": {
                "nome": user["nome"],
                "email": user["email"],
                "perfil": perfil,
                "caixa_id": user["caixa_id"],
                "ativo": True,
                "senha_hash": Usuario.hash_senha(user["senha"]),
                "data_atualizacao": now,
            },
            "$setOnInsert": {
                "data_criacao": now,
            },
        },
        upsert=True,
    )

    if result.upserted_id is not None:
        return "created"
    return "updated"


def run() -> None:
    ensure_indexes()
    ensure_default_settings()

    print("[seed] iniciado")
    for user in USERS_TO_SEED:
        status = upsert_user(user)
        print(f"[seed] {status}: {user['email']} ({user['perfil']})")
    print("[seed] concluido")


if __name__ == "__main__":
    run()
