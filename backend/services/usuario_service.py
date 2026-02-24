from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from backend.database.connection import mongodb
from backend.models.usuario_model import PERFIS_VALIDOS, Usuario


usuarios_collection = mongodb.get_collection("usuarios")


class UsuarioService:
    @staticmethod
    def contar_usuarios():
        return usuarios_collection.count_documents({})

    @staticmethod
    def _gerar_caixa_id_unico():
        for _ in range(30):
            caixa_id = Usuario.gerar_caixa_id()
            if not usuarios_collection.find_one({"caixa_id": caixa_id}):
                return caixa_id
        raise ValueError("Nao foi possivel gerar caixa_id unico.")

    @staticmethod
    def criar_usuario(usuario: Usuario):
        if usuario.perfil not in PERFIS_VALIDOS:
            raise ValueError("Perfil invalido.")

        if usuarios_collection.find_one({"email": usuario.email}):
            raise ValueError(f"Email '{usuario.email}' ja cadastrado.")

        if not usuario.caixa_id:
            usuario.caixa_id = UsuarioService._gerar_caixa_id_unico()
        elif usuarios_collection.find_one({"caixa_id": usuario.caixa_id}):
            raise ValueError(f"Caixa ID '{usuario.caixa_id}' ja cadastrado.")

        try:
            result = usuarios_collection.insert_one(usuario.to_dict())
        except DuplicateKeyError as exc:
            raise ValueError("Email ou caixa_id ja cadastrado.") from exc

        return usuarios_collection.find_one({"_id": result.inserted_id})

    @staticmethod
    def autenticar(email, senha):
        usuario = usuarios_collection.find_one({"email": email, "ativo": True})
        if usuario and Usuario.verificar_senha_static(senha, usuario["senha_hash"]):
            return usuario
        return None

    @staticmethod
    def listar_usuarios(ativos_only=True):
        filtro = {"ativo": True} if ativos_only else {}
        return list(usuarios_collection.find(filtro))

    @staticmethod
    def listar_por_perfis(perfis):
        return list(usuarios_collection.find({"perfil": {"$in": list(perfis)}, "ativo": True}))

    @staticmethod
    def buscar_usuario_por_id(usuario_id):
        if isinstance(usuario_id, str):
            usuario_id = ObjectId(usuario_id)
        return usuarios_collection.find_one({"_id": usuario_id})


def verificar_senha_static(senha, hash_armazenado):
    from passlib.hash import bcrypt

    return bcrypt.verify(senha, hash_armazenado)


Usuario.verificar_senha_static = staticmethod(verificar_senha_static)
