from datetime import datetime

from pydantic import BaseModel, Field


class UsuarioCreate(BaseModel):
    nome: str = Field(..., examples=["Admin Principal"])
    email: str = Field(..., examples=["admin@stockflow.com"])
    senha: str = Field(..., min_length=6, examples=["Senha123!"])
    perfil: str = Field(..., examples=["admin"])
    caixa_id: int | None = Field(default=None, examples=[10001])
    ativo: bool = True


class LoginRequest(BaseModel):
    email: str
    senha: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    nova_senha: str = Field(..., min_length=6)


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_seconds: int


class AuthMeResponse(BaseModel):
    id: str
    nome: str
    email: str
    perfil: str


class FornecedorCreate(BaseModel):
    nome: str
    contato: str
    email: str
    produtos_fornecidos: list[str] = []


class SecaoCreate(BaseModel):
    nome: str
    pos_x: int
    pos_y: int
    largura: int
    altura: int
    cor_padrao: str = "green"


class MovimentacaoCreate(BaseModel):
    produto_id: str
    tipo: str
    quantidade: int
    preco_unitario: float
    usuario_id: str
    numero_lote: str | None = None
    data_validade: datetime | None = None
    origem: str = "manual"
    lote_esperado_peps: str | None = None
    violacao_peps: bool = False


class HealthResponse(BaseModel):
    status: str


class ReadinessResponse(BaseModel):
    status: str
    mongo: str


class StatusResponse(BaseModel):
    status: str
    detail: str
