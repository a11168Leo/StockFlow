class Fornecedor:
    def __init__(self, nome, contato, email, produtos_fornecidos=None):
        """
        Fornecedor e os produtos que ele fornece.
        """
        self.nome = nome
        self.contato = contato
        self.email = email
        self.produtos_fornecidos = produtos_fornecidos if produtos_fornecidos else []

    def to_dict(self):
        return self.__dict__
