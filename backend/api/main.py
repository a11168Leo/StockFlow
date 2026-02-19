from fastapi import FastAPI, HTTPException, UploadFile, File
from backend.services.usuario_service import UsuarioService
from backend.services.produto_service import ProdutoService
from backend.utils.csv_import import importar_produtos_csv
from backend.utils.alertas import verificar_estoque
from backend.utils.barcode_qrcode import processar_scan

app = FastAPI(title="StockFlow API")

# -------------------------------
# Usuários
@app.post("/usuarios/")
def criar_usuario(usuario: dict):
    try:
        u = UsuarioService.criar_usuario(**usuario)
        return {"status": "ok", "usuario": usuario}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login/")
def login(email: str, senha: str):
    usuario = UsuarioService.autenticar(email, senha)
    if not usuario:
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")
    return {"status": "ok", "usuario": usuario}

# -------------------------------
# Produtos
@app.get("/produtos/")
def listar_produtos():
    return ProdutoService.listar_produtos()

@app.post("/produtos/")
def criar_produto(produto: dict):
    from backend.models.produto_model import Produto
    try:
        p = Produto(**produto)
        ProdutoService.criar_produto(p)
        return {"status": "ok", "produto": produto}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/produtos/scan/")
def scan_produto(codigo: str, tipo: str, quantidade: int, usuario_id: int):
    try:
        res = processar_scan(codigo, tipo, quantidade, usuario_id)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/produtos/csv/")
def importar_csv(file: UploadFile = File(...)):
    # Salvar temporariamente
    caminho = f"temp_{file.filename}"
    with open(caminho, "wb") as f:
        f.write(file.file.read())
    resultado = importar_produtos_csv(caminho)
    return resultado

# -------------------------------
# Alertas
@app.get("/alertas/")
def gerar_alertas(margin: int = 0):
    return verificar_estoque(margin=margin)
