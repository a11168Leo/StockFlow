import json
import logging
import secrets
import time
from pathlib import Path
from urllib.parse import urlencode

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from backend.api.deps import get_current_user, get_optional_current_user, require_roles
from backend.api.schemas import (
    AuthMeResponse,
    ForgotPasswordRequest,
    FornecedorCreate,
    HealthResponse,
    LoginRequest,
    LogoutRequest,
    MovimentacaoCreate,
    ReadinessResponse,
    RefreshRequest,
    ResetPasswordRequest,
    SecaoCreate,
    StatusResponse,
    TokenPairResponse,
    UsuarioCreate,
)
from backend.core.config import get_settings
from backend.core.security import (
    assert_token_type,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from backend.database.bootstrap import ensure_default_settings, ensure_indexes
from backend.database.connection import mongodb
from backend.models.fornecedor_model import Fornecedor
from backend.models.movimentacao_model import Movimentacao
from backend.models.produto_model import Produto
from backend.models.secao_model import Secao
from backend.models.tarefa_model import Tarefa
from backend.models.usuario_model import Usuario
from backend.services.auth_service import AuthService
from backend.services.configuracao_service import ConfiguracaoService
from backend.services.fornecedor_service import FornecedorService
from backend.services.movimentacao_service import MovimentacaoService
from backend.services.produto_service import ProdutoService
from backend.services.secao_service import SecaoService
from backend.services.tarefa_service import TarefaService
from backend.services.usuario_service import UsuarioService
from backend.utils.alertas import verificar_estoque
from backend.utils.barcode_qrcode import processar_scan
from backend.utils.csv_import import importar_produtos_csv
from backend.utils.email_service import send_password_reset_email
from backend.utils.serializer import serialize_document, serialize_many

settings = get_settings()
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit_default])
app = FastAPI(title="StockFlow API", version="1.1.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

REQUEST_COUNT = Counter(
    "stockflow_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "stockflow_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)

logger = logging.getLogger("stockflow.api")


def configure_logging() -> None:
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.handlers = [handler]


@app.middleware("http")
async def metrics_and_logging_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start

    path = request.url.path
    method = request.method
    status = str(response.status_code)

    REQUEST_COUNT.labels(method=method, path=path, status=status).inc()
    REQUEST_LATENCY.labels(method=method, path=path).observe(elapsed)

    logger.info(
        json.dumps(
            {
                "event": "http_request",
                "method": method,
                "path": path,
                "status": response.status_code,
                "duration_ms": round(elapsed * 1000, 2),
                "client_ip": request.client.host if request.client else None,
            }
        )
    )
    return response


@app.on_event("startup")
def bootstrap_database():
    configure_logging()
    ensure_indexes()
    ensure_default_settings()


def _emit_tokens(usuario: dict) -> TokenPairResponse:
    user_id = str(usuario["_id"])
    access = create_access_token(user_id=user_id, perfil=usuario["perfil"])
    refresh, jti, refresh_exp = create_refresh_token(user_id=user_id)
    AuthService.salvar_refresh_token(user_id=user_id, jti=jti, expira_em=refresh_exp)
    return TokenPairResponse(
        access_token=access,
        refresh_token=refresh,
        token_type="bearer",
        expires_in_seconds=settings.access_token_minutes * 60,
    )


@app.get("/health/live", response_model=HealthResponse, tags=["infra"])
def liveness():
    return {"status": "ok"}


@app.get("/health/ready", response_model=ReadinessResponse, tags=["infra"])
def readiness():
    try:
        mongodb.client.admin.command("ping")
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Mongo indisponivel: {exc}") from exc
    return {"status": "ok", "mongo": "up"}


@app.get("/metrics", tags=["infra"])
def metrics():
    return PlainTextResponse(generate_latest().decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


@app.post("/usuarios/", tags=["usuarios"])
@limiter.limit("30/minute")
def criar_usuario(
    request: Request,
    usuario: UsuarioCreate,
    current_user: dict | None = Depends(get_optional_current_user),
):
    try:
        total_usuarios = UsuarioService.contar_usuarios()

        if total_usuarios == 0:
            if usuario.perfil != "admin":
                raise HTTPException(status_code=400, detail="Primeiro usuario deve ser admin.")
        else:
            if not current_user:
                raise HTTPException(status_code=401, detail="Token Bearer obrigatorio.")
            require_roles(current_user, ["admin", "lider"])
            if current_user["perfil"] == "lider" and usuario.perfil != "funcionario":
                raise HTTPException(status_code=403, detail="Lider pode criar apenas funcionarios.")

        novo_usuario = Usuario(**usuario.model_dump())
        criado = UsuarioService.criar_usuario(novo_usuario)
        return {"status": "ok", "usuario": serialize_document(criado)}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/auth/login", response_model=TokenPairResponse, tags=["auth"])
@limiter.limit("30/minute")
def auth_login(request: Request, payload: LoginRequest):
    usuario = UsuarioService.autenticar(payload.email, payload.senha)
    if not usuario:
        raise HTTPException(status_code=401, detail="Email ou senha invalidos")
    return _emit_tokens(usuario)


@app.post("/login/", tags=["auth"], deprecated=True)
def login_legacy(payload: LoginRequest):
    usuario = UsuarioService.autenticar(payload.email, payload.senha)
    if not usuario:
        raise HTTPException(status_code=401, detail="Email ou senha invalidos")
    tokens = _emit_tokens(usuario)
    return {
        "status": "ok",
        "usuario": serialize_document(usuario),
        "tokens": tokens.model_dump(),
    }


@app.post("/auth/refresh", response_model=TokenPairResponse, tags=["auth"])
@limiter.limit("60/minute")
def refresh_token(request: Request, payload: RefreshRequest):
    decoded = decode_token(payload.refresh_token)
    assert_token_type(decoded, "refresh")

    user_id = decoded.get("sub")
    jti = decoded.get("jti")
    if not user_id or not jti:
        raise HTTPException(status_code=401, detail="Refresh token invalido.")

    if not AuthService.validar_refresh_token(user_id=user_id, jti=jti):
        raise HTTPException(status_code=401, detail="Refresh token revogado ou expirado.")

    usuario = UsuarioService.buscar_usuario_por_id(user_id)
    if not usuario or not usuario.get("ativo", True):
        raise HTTPException(status_code=401, detail="Usuario nao autenticado.")

    AuthService.revogar_refresh_token(user_id=user_id, jti=jti)
    return _emit_tokens(usuario)


@app.post("/auth/logout", tags=["auth"])
@limiter.limit("60/minute")
def logout(request: Request, payload: LogoutRequest):
    decoded = decode_token(payload.refresh_token)
    assert_token_type(decoded, "refresh")

    user_id = decoded.get("sub")
    jti = decoded.get("jti")
    if not user_id or not jti:
        raise HTTPException(status_code=401, detail="Refresh token invalido.")

    AuthService.revogar_refresh_token(user_id=user_id, jti=jti)
    return {"status": "ok"}


@app.post("/auth/forgot-password", response_model=StatusResponse, tags=["auth"])
@limiter.limit("20/minute")
def forgot_password(request: Request, payload: ForgotPasswordRequest):
    # Resposta fixa evita enumeração de emails válidos.
    default_response = {
        "status": "ok",
        "detail": "Se o email existir, enviaremos instrucoes para redefinir a senha.",
    }

    usuario = UsuarioService.buscar_usuario_por_email(payload.email)
    if not usuario or not usuario.get("ativo", True):
        return default_response

    token = secrets.token_urlsafe(32)
    AuthService.criar_token_reset_senha(user_id=str(usuario["_id"]), token=token)

    query = urlencode({"token": token})
    reset_link = f"{settings.frontend_reset_url}?{query}"
    try:
        send_password_reset_email(to_email=payload.email, reset_link=reset_link)
    except Exception:
        logger.exception("Falha ao enviar email de reset para %s", payload.email)
    return default_response


@app.post("/auth/reset-password", response_model=StatusResponse, tags=["auth"])
@limiter.limit("20/minute")
def reset_password(request: Request, payload: ResetPasswordRequest):
    token_doc = AuthService.validar_token_reset_senha(payload.token)
    if not token_doc:
        raise HTTPException(status_code=400, detail="Token de redefinicao invalido ou expirado.")

    usuario_id = token_doc.get("usuario_id")
    updated = UsuarioService.atualizar_senha_por_id(usuario_id=usuario_id, nova_senha=payload.nova_senha)
    if not updated:
        raise HTTPException(status_code=400, detail="Nao foi possivel atualizar a senha.")

    AuthService.marcar_token_reset_como_usado(payload.token)
    AuthService.revogar_todos_refresh_tokens(str(usuario_id))
    return {"status": "ok", "detail": "Senha redefinida com sucesso."}


@app.get("/auth/me", response_model=AuthMeResponse, tags=["auth"])
def auth_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": str(current_user["_id"]),
        "nome": current_user.get("nome", ""),
        "email": current_user.get("email", ""),
        "perfil": current_user.get("perfil", ""),
    }


@app.get("/produtos/", tags=["produtos"])
def listar_produtos(current_user: dict = Depends(get_current_user)):
    require_roles(current_user, ["admin", "lider", "funcionario"])
    return serialize_many(ProdutoService.listar_produtos())


@app.post("/produtos/", tags=["produtos"])
def criar_produto(produto: dict, current_user: dict = Depends(get_current_user)):
    require_roles(current_user, ["admin", "lider"])
    try:
        p = Produto(**produto)
        criado = ProdutoService.criar_produto(p)
        return {"status": "ok", "produto": serialize_document(criado)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/produtos/scan/", tags=["produtos"])
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


@app.post("/produtos/csv/", tags=["produtos"])
def importar_csv(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    require_roles(current_user, ["admin", "lider"])
    caminho = f"temp_{Path(file.filename).name}"
    with open(caminho, "wb") as file_buffer:
        file_buffer.write(file.file.read())
    resultado = importar_produtos_csv(caminho)
    return resultado


@app.get("/alertas/", tags=["alertas"])
def listar_alertas(current_user: dict = Depends(get_current_user)):
    require_roles(current_user, ["admin", "lider"])
    from backend.services.alerta_service import AlertaService

    return serialize_many(AlertaService.listar_alertas())


@app.post("/alertas/gerar/", tags=["alertas"])
def gerar_alertas(current_user: dict = Depends(get_current_user)):
    require_roles(current_user, ["admin", "lider"])
    return serialize_many(verificar_estoque())


@app.get("/configuracoes/margem-alerta", tags=["configuracoes"])
def obter_margem_alerta(current_user: dict = Depends(get_current_user)):
    require_roles(current_user, ["admin", "lider"])
    return {"margem_alerta_estoque": ConfiguracaoService.get_margem_alerta_estoque()}


@app.put("/configuracoes/margem-alerta", tags=["configuracoes"])
def atualizar_margem_alerta(valor: float, current_user: dict = Depends(get_current_user)):
    require_roles(current_user, ["admin", "lider"])
    try:
        ConfiguracaoService.set_margem_alerta_estoque(valor)
        return {"status": "ok", "margem_alerta_estoque": valor}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/tarefas/", tags=["tarefas"])
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


@app.get("/tarefas/minhas", tags=["tarefas"])
def listar_minhas_tarefas(current_user: dict = Depends(get_current_user)):
    tarefas = TarefaService.listar_por_responsavel(current_user["_id"])
    return serialize_many(tarefas)


@app.post("/tarefas/{tarefa_id}/concluir", tags=["tarefas"])
def concluir_tarefa(tarefa_id: str, current_user: dict = Depends(get_current_user)):
    tarefa = TarefaService.buscar_tarefa_por_id(tarefa_id)
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa nao encontrada.")

    if current_user["perfil"] == "funcionario" and tarefa.get("responsavel_id") != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Funcionario so pode concluir tarefas proprias.")

    TarefaService.concluir_tarefa(tarefa_id)
    return {"status": "ok"}


@app.get("/fornecedores/", tags=["fornecedores"])
def listar_fornecedores(current_user: dict = Depends(get_current_user)):
    require_roles(current_user, ["admin", "lider", "funcionario"])
    return serialize_many(FornecedorService.listar_fornecedores())


@app.post("/fornecedores/", tags=["fornecedores"])
def criar_fornecedor(payload: FornecedorCreate, current_user: dict = Depends(get_current_user)):
    require_roles(current_user, ["admin", "lider"])
    try:
        fornecedor = Fornecedor(**payload.model_dump())
        result = FornecedorService.criar_fornecedor(fornecedor)
        criado = FornecedorService.buscar_fornecedor_por_id(result.inserted_id)
        return {"status": "ok", "fornecedor": serialize_document(criado)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/secoes/", tags=["secoes"])
def listar_secoes(current_user: dict = Depends(get_current_user)):
    require_roles(current_user, ["admin", "lider", "funcionario"])
    return serialize_many(SecaoService.listar_secoes())


@app.post("/secoes/", tags=["secoes"])
def criar_secao(payload: SecaoCreate, current_user: dict = Depends(get_current_user)):
    require_roles(current_user, ["admin", "lider"])
    try:
        secao = Secao(**payload.model_dump())
        result = SecaoService.criar_secao(secao)
        criada = SecaoService.buscar_secao_por_id(result.inserted_id)
        return {"status": "ok", "secao": serialize_document(criada)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/movimentacoes/", tags=["movimentacoes"])
def listar_movimentacoes(current_user: dict = Depends(get_current_user)):
    require_roles(current_user, ["admin", "lider"])
    return serialize_many(MovimentacaoService.listar_movimentacoes())


@app.post("/movimentacoes/", tags=["movimentacoes"])
def criar_movimentacao(payload: MovimentacaoCreate, current_user: dict = Depends(get_current_user)):
    require_roles(current_user, ["admin", "lider"])
    try:
        mov = Movimentacao(**payload.model_dump())
        result = MovimentacaoService.registrar_movimentacao(mov)
        criado = mongodb.get_collection("movimentacoes").find_one({"_id": result.inserted_id})
        return {"status": "ok", "movimentacao": serialize_document(criado)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
