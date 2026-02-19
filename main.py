from backend.models.produto_model import Produto
from backend.services.produto_service import ProdutoService

# Criar produto teste
produto = Produto(
    nome="Arroz 5kg",
    categoria="Alimentos",
    preco_custo=15.0,
    preco_venda=22.0,
    quantidade=100,
    estoque_minimo=10,
    secao_id="A1"
)

ProdutoService.criar_produto(produto)

# Listar produtos
for p in ProdutoService.listar_produtos():
    print(p)
