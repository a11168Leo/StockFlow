# StockFlow

Backend FastAPI para controle de estoque com MongoDB.

## Entregas desta iteracao

- Autenticacao JWT com access token e refresh token rotativo.
- Revogacao de refresh token em `logout` e no processo de `refresh`.
- Dependencias de autorizacao por perfil migradas para Bearer token.
- Observabilidade com logs estruturados em JSON e metricas Prometheus em `/metrics`.
- Health checks em `/health/live` e `/health/ready`.
- Hardening inicial com CORS restritivo por ambiente e rate limit global.
- Endpoints publicos para servicos auxiliares:
  - fornecedores
  - secoes
  - movimentacoes
- Suite de testes (unitarios + integracao com `mongomock`).
- Pipeline CI em GitHub Actions com lint e testes em push/PR.
- Baseline de deploy com `Dockerfile` e `docker-compose.yml`.

## Endpoints principais

### Autenticacao

- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `POST /login/` (legado, marcado como deprecated)

#### `POST /auth/login`
Request:
```json
{
  "email": "admin@stockflow.com",
  "senha": "Senha123!"
}
```
Response:
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in_seconds": 1800
}
```

#### `POST /auth/refresh`
Request:
```json
{
  "refresh_token": "..."
}
```
Response:
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in_seconds": 1800
}
```

#### `POST /auth/logout`
Request:
```json
{
  "refresh_token": "..."
}
```
Response:
```json
{
  "status": "ok"
}
```

### Infra

- `GET /health/live`
- `GET /health/ready`
- `GET /metrics`

### Auxiliares (novos)

- `GET /fornecedores/`
- `POST /fornecedores/`
- `GET /secoes/`
- `POST /secoes/`
- `GET /movimentacoes/`
- `POST /movimentacoes/`

## Como executar localmente

1. Criar e ativar ambiente virtual.
2. Instalar dependencias:
   - `pip install -r backend/requirements-dev.txt`
3. Criar `.env` a partir de `.env.example`.
4. Iniciar API:
   - `uvicorn backend.api.main:app --reload`
5. Acessar documentacao OpenAPI:
   - `http://localhost:8000/docs`

## Seed inicial de usuarios

Executar:

- `python -m backend.scripts.seed_users`

Usuarios criados/atualizados:

- admin: `a11168@csmiguel.pt` / `admin1234`
- funcionario: `a11077@csmiguel.pt` / `123456`

## Testes e qualidade

- Rodar lint:
  - `ruff check backend/api backend/core backend/services/auth_service.py tests`
- Rodar testes:
  - `pytest -q`

## CI/CD

Arquivo: `.github/workflows/ci.yml`

- Executa em `push` e `pull_request`.
- Etapas:
  1. install dependencies
  2. lint com `ruff`
  3. testes com `pytest`

## Deploy (staging/producao)

### Docker

- Build:
  - `docker build -t stockflow-api .`
- Run:
  - `docker compose up -d`

### Estrategia sugerida

1. `staging`: branch `develop`, base de dados isolada, smoke tests pos deploy.
2. `producao`: branch `main`, deploy com aprovacao manual, monitoramento de `/health/ready` e `/metrics`.

### Acesso externo gratuito (Cloudflare Tunnel)

1. Criar conta Cloudflare e abrir `Zero Trust`.
2. Criar um Tunnel e copiar o token.
3. Colocar no `.env`:
   - `CLOUDFLARE_TUNNEL_TOKEN=seu_token`
4. No Cloudflare Tunnel, criar rotas publicas para:
   - `stockflow.seudominio.com` -> `http://frontend:3000`
   - `api-stockflow.seudominio.com` -> `http://api:8000`
5. Atualizar `.env`:
   - `VITE_API_BASE_URL=https://api-stockflow.seudominio.com`
   - `CORS_ALLOW_ORIGINS=http://localhost:3000,http://172.16.31.139:3000,https://stockflow.seudominio.com`
   - `FRONTEND_RESET_URL=https://stockflow.seudominio.com/login/`
6. Subir tudo com tunnel:
   - `docker compose --profile tunnel up -d --build`

Observacao:
- Sempre que mudar `VITE_API_BASE_URL`, recrie o frontend com `--build`.

## Variaveis de ambiente

Ver `.env.example`.

Campos criticos para producao:

- `JWT_SECRET` forte e rotacionavel.
- `CORS_ALLOW_ORIGINS` restrito ao dominio frontend oficial.
- `RATE_LIMIT_DEFAULT` ajustado por perfil de carga.
- `MONGO_URI` apontando para cluster com autenticacao e TLS.
