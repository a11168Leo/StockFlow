import random
from datetime import datetime

from passlib.hash import bcrypt

PERFIS_VALIDOS = {"admin", "lider", "funcionario"}


class Usuario:
    def __init__(self, nome, email, senha, perfil, caixa_id=None, ativo=True):
        self.nome = nome
        self.email = email
        if perfil not in PERFIS_VALIDOS:
            raise ValueError("Perfil invalido. Use: admin, lider ou funcionario.")
        self.senha_hash = self.hash_senha(senha)
        self.perfil = perfil
        self.caixa_id = caixa_id if caixa_id else self.gerar_caixa_id()
        self.ativo = ativo
        self.data_criacao = datetime.now()

    @staticmethod
    def gerar_caixa_id():
        return random.randint(10000, 99999)

    @staticmethod
    def hash_senha(senha):
        return bcrypt.hash(senha)

    def verificar_senha(self, senha):
        return bcrypt.verify(senha, self.senha_hash)

    def to_dict(self):
        return self.__dict__
