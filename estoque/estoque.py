
from datetime import datetime, timedelta

estoque = []


def adicionar_item(codigo, nome, quantidade, local, preco_custo, preco_venda):
    # Verificar se código já existe
    for item in estoque:
        if item["codigo"] == codigo:
            raise ValueError("Código já cadastrado no estoque.")

    # Perguntar ao usuário sobre validade
    resposta = input("O produto tem validade? (y/n): ").strip().lower()
    if resposta == "y":
        while True:
            data_input = input("Digite a data de validade (dd/mm/aaaa): ").strip()
            try:
                validade = datetime.strptime(data_input, "%d/%m/%Y")
                break
            except ValueError:
                print("Data inválida. Use o formato dd/mm/aaaa.")
    else:
        validade = None

    novo_item = {
        "codigo": codigo,
        "nome": nome,
        "quantidade": quantidade,
        "local": local,
        "preco_custo": preco_custo,
        "preco_venda": preco_venda,
        "validade": validade
    }

    estoque.append(novo_item)
    return novo_item

# ------------------------------------
# 🔹 Função para verificar produtos próximos da validade
# ------------------------------------
def alertar_validade(dias_aviso=7):
    """Retorna produtos que vencem em até dias_aviso dias"""
    hoje = datetime.now()
    alertas = []
    for item in estoque:
        if item["validade"] is not None:
            if 0 <= (item["validade"] - hoje).days <= dias_aviso:
                alertas.append({
                    "codigo": item["codigo"],
                    "nome": item["nome"],
                    "validade": item["validade"].strftime("%d/%m/%Y"),
                    "dias_restantes": (item["validade"] - hoje).days
                })
    return alertas

# ------------------------------------
# 🔹 Atualizar item
# ------------------------------------
def atualizar_item(codigo, nome=None, quantidade=None, local=None, preco_custo=None, preco_venda=None, validade=None):
    for item in estoque:
        if item["codigo"] == codigo:
            if nome is not None:
                item["nome"] = nome
            if quantidade is not None:
                item["quantidade"] = quantidade
            if local is not None:
                item["local"] = local
            if preco_custo is not None:
                item["preco_custo"] = preco_custo
            if preco_venda is not None:
                item["preco_venda"] = preco_venda
            if validade is not None:
                item["validade"] = validade
            return item
    raise ValueError("Item não encontrado.")

# ------------------------------------
# 🔹 Remover item
# ------------------------------------
def remover_item(codigo):
    global estoque
    for item in estoque:
        if item["codigo"] == codigo:
            estoque.remove(item)
            return item
    raise ValueError("Item não encontrado.")

# ------------------------------------
# 🔹 Buscar item
# ------------------------------------
def buscar_item(codigo=None, nome=None):
    resultados = []
    for item in estoque:
        if codigo and item["codigo"] == codigo:
            resultados.append(item)
        elif nome and nome.lower() in item["nome"].lower():
            resultados.append(item)
    return resultados

# ------------------------------------
# 🔹 Listar todos os itens
# ------------------------------------
def listar_estoque():
    return estoque


# Entrar e sair quantidade
def entrada_estoque(codigo, quantidade):
    for item in estoque:
        if item["codigo"] == codigo:
            item["quantidade"] += quantidade
            return item
    raise ValueError("Item não encontrado.")

def saida_estoque(codigo, quantidade):
    for item in estoque:
        if item["codigo"] == codigo:
            if item["quantidade"] < quantidade:
                raise ValueError("Quantidade insuficiente em estoque.")
            item["quantidade"] -= quantidade
            return item
    raise ValueError("Item não encontrado.")


# Cálculo de valor total do estoque
def calcular_valor_total():
    total = 0
    for item in estoque:
        total += item["quantidade"] * item["preco_custo"]
    return total
