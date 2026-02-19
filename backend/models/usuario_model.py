import random
from datetime import datetime
from passlib.hash import bcrypt  # Para hash seguro de senhas

class Usuario:
    def __init__(self, nome, email, senha, perfil, caixa_id=None, ativo=True):
        """
        Usuario do sistema com email e senha segura.
        perfil: 'admin', 'gerente', 'funcionario'
        caixa_id: número aleatório de 5 dígitos para funcionário
        """
        self.nome = nome
        self.email = email
        self.senha_hash = self.hash_senha(senha)  # senha criptografada
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
