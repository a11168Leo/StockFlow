class Secao:
    def __init__(self, nome, pos_x, pos_y, largura, altura, cor_padrao="green"):
        """
        Representa uma seção ou prateleira no mapa 2D.
        """
        self.nome = nome
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.largura = largura
        self.altura = altura
        self.cor_padrao = cor_padrao

    def to_dict(self):
        return self.__dict__
