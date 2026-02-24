from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile

from backend.api.deps import get_current_user, require_roles
from backend.database.bootstrap import ensure_default_settings, ensure_indexes
from backend.models.produto_model import Produto
from backend.models.tarefa_model import Tarefa
from backend.models.usuario_model import Usuario
from backend.services.configuracao_service import ConfiguracaoService
from backend.services.produto_service import ProdutoService
from backend.services.tarefa_service import TarefaService
from backend.services.usuario_service import UsuarioService
from backend.utils.alertas import verificar_estoque
from backend.utils.barcode_qrcode import processar_scan
from backend.utils.csv_import import importar_produtos_csv
from backend.utils.serializer import serialize_document, serialize_many

app = FastAPI(title="StockFlow API")


@app.on_event("startup")
def bootstrap_database():
    ensure_indexes()
    ensure_default_settings()


@app.post("/usuarios/")
def criar_usuario(usuario: dict, x_user_id: str | None = Header(None, alias="X-User-Id")):
    try:
        total_usuarios = UsuarioService.contar_usuarios()

        if total_usuarios == 0:
            if usuario.get("perfil") != "admin":
                raise HTTPException(status_code=400, detail="Primeiro usuario deve ser admin.")
        else:
            if not x_user_id:
                raise HTTPException(status_code=401, detail="X-User-Id obrigatorio.")
            atual = UsuarioService.buscar_usuario_por_id(x_user_id)
            if not atual:
                raise HTTPException(status_code=401, detail="Usuario autenticado invalido.")
            require_roles(atual, ["admin", "lider"])

            if atual["perfil"] == "lider" and usuario.get("perfil") != "funcionario":
                raise HTTPException(status_code=403, detail="Lider pode criar apenas funcionarios.")

        novo_usuario = Usuario(**usuario)
        criado = UsuarioService.criar_usuario(novo_usuario)
        return {"status": "ok", "usuario": serialize_document(criado)}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/login/")
def login(email: str, senha: str):
    usuario = UsuarioService.autenticar(email, senha)
    if not usuario:
        raise HTTPException(status_code=401, detail="Email ou senha invalidos")
    return {"status": "ok", "usuario": serialize_document(usuario)}


@app.get("/produtos/")
def listar_produtos(current_user: dict = Depends(get_current_user)):
    require_roles(current_user, ["admin", "lider", "funcionario"])
    return serialize_many(ProdutoService.listar_produtos())


@app.post("/produtos/")
def criar_produto(produto: dict, current_user: dict = Depends(get_current_user)):
    require_roles(current_user, ["admin", "lider"])
    try:
        p = Produto(**produto)
        criado = ProdutoService.criar_produto(p)
        return {"status": "ok", "produto": serialize_document(criado)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/produtos/scan/")
def scan_produto(
    codigo: str,
    tipo: str,
    quantidade: int,
    numero_lote: str | None = None,
    data_validade: str | None = None,
    current_user: dict = Depends(get_current_user),
):
    require_roles(current_user, ["admin", "lider", "funcionario"])
    try:
        res = processar_scan(
            codigo=codigo,
            tipo=tipo,
            quantidade=quantidade,
            usuario_id=current_user["_id"],
            numero_lote=numero_lote,
            data_validade=data_validade,
        )
        return res
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/produtos/csv/")
def importar_csv(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    require_roles(current_user, ["admin", "lider"])
    caminho = f"temp_{file.filename}"
    with open(caminho, "wb") as file_buffer:
        file_buffer.write(file.file.read())
    resultado = importar_produtos_csv(caminho)
    return resultado


@app.get("/alertas/")
def listar_alertas(current_user: dict = Depends(get_current_user)):
    require_roles(current_user, ["admin", "lider"])
    from backend.services.alerta_service import AlertaService

    return serialize_many(AlertaService.listar_alertas())


@app.post("/alertas/gerar/")
def gerar_alertas(current_user: dict = Depends(get_current_user)):
    require_roles(current_user, ["admin", "lider"])
    return serialize_many(verificar_estoque())


@app.get("/configuracoes/margem-alerta")
def obter_margem_alerta(current_user: dict = Depends(get_current_user)):
    require_roles(current_user, ["admin", "lider"])
    return {"margem_alerta_estoque": ConfiguracaoService.get_margem_alerta_estoque()}


@app.put("/configuracoes/margem-alerta")
def atualizar_margem_alerta(valor: float, current_user: dict = Depends(get_current_user)):
    require_roles(current_user, ["admin", "lider"])
    try:
        ConfiguracaoService.set_margem_alerta_estoque(valor)
        return {"status": "ok", "margem_alerta_estoque": valor}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/tarefas/")
def criar_tarefa(tarefa: dict, current_user: dict = Depends(get_current_user)):
    require_roles(current_user, ["admin", "lider"])

    responsavel = UsuarioService.buscar_usuario_por_id(tarefa["responsavel_id"])
    if not responsavel:
        raise HTTPException(status_code=404, detail="Responsavel nao encontrado.")

    if current_user["perfil"] == "lider" and responsavel["perfil"] != "funcionario":
        raise HTTPException(status_code=403, detail="Lider pode atribuir tarefas apenas a funcionarios.")

    tarefa["responsavel_id"] = responsavel["_id"]
    nova_tarefa = Tarefa(**tarefa)
    TarefaService.criar_tarefa(nova_tarefa)
    return {"status": "ok"}


@app.get("/tarefas/minhas")
def listar_minhas_tarefas(current_user: dict = Depends(get_current_user)):
    tarefas = TarefaService.listar_por_responsavel(current_user["_id"])
    return serialize_many(tarefas)


@app.post("/tarefas/{tarefa_id}/concluir")
def concluir_tarefa(tarefa_id: str, current_user: dict = Depends(get_current_user)):
    tarefa = TarefaService.buscar_tarefa_por_id(tarefa_id)
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa nao encontrada.")

    if current_user["perfil"] == "funcionario" and tarefa.get("responsavel_id") != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Funcionario so pode concluir tarefas proprias.")

    TarefaService.concluir_tarefa(tarefa_id)
    return {"status": "ok"}
