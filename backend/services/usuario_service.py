from backend.database.connection import mongodb
from backend.models.usuario_model import Usuario

usuarios_collection = mongodb.get_collection("usuarios")

class UsuarioService:

    @staticmethod
    def criar_usuario(usuario: Usuario):
        # Evita duplicação de email
        if usuarios_collection.find_one({"email": usuario.email}):
            raise ValueError(f"Email '{usuario.email}' já cadastrado.")
        return usuarios_collection.insert_one(usuario.to_dict())

    @staticmethod
    def autenticar(email, senha):
        usuario = usuarios_collection.find_one({"email": email})
        if usuario and Usuario.verificar_senha_static(senha, usuario["senha_hash"]):
            return usuario
        return None

    @staticmethod
    def listar_usuarios():
        return list(usuarios_collection.find())

    @staticmethod
    def buscar_usuario_por_id(usuario_id):
        from bson import ObjectId
        return usuarios_collection.find_one({"_id": ObjectId(usuario_id)})

# Método estático auxiliar para verificar senha de hash
def verificar_senha_static(senha, hash_armazenado):
    from passlib.hash import bcrypt
    return bcrypt.verify(senha, hash_armazenado)

Usuario.verificar_senha_static = staticmethod(verificar_senha_static)
