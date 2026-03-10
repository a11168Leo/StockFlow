# StockFlow

> Sistema completo de controle de estoque com backend FastAPI, banco de dados MongoDB e frontend multi-página em Vanilla JS + Vite.

---

## Índice

- [Visão Geral](#visão-geral)
- [Arquitetura do Sistema](#arquitetura-do-sistema)
- [Estrutura de Pastas](#estrutura-de-pastas)
- [Backend](#backend)
  - [Tecnologias e Dependências](#tecnologias-e-dependências)
  - [Configuração Settings](#configuração-settings)
  - [Segurança e Autenticação JWT](#segurança-e-autenticação-jwt)
  - [Modelos de Dados](#modelos-de-dados)
  - [Serviços](#serviços)
  - [Utilitários](#utilitários)
  - [Banco de Dados](#banco-de-dados)
  - [API Endpoints Completos](#api-endpoints-completos)
  - [Observabilidade](#observabilidade)
  - [Rate Limiting](#rate-limiting)
- [Frontend](#frontend)
  - [Tecnologias Frontend](#tecnologias-frontend)
  - [Páginas e Rotas](#páginas-e-rotas)
  - [Autenticação no Frontend](#autenticação-no-frontend)
  - [Painel Admin Mapa do Armazém](#painel-admin-mapa-do-armazém)
  - [Painel Gerente e Lider](#painel-gerente-e-lider)
  - [Painel Funcionário](#painel-funcionário)
  - [Estilos e Design System](#estilos-e-design-system)
- [Testes](#testes)
- [CI/CD](#cicd)
- [Deploy com Docker](#deploy-com-docker)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Seed Inicial de Usuários](#seed-inicial-de-usuários)
- [Acesso Externo com Cloudflare Tunnel](#acesso-externo-com-cloudflare-tunnel)
- [Perfis e Permissões](#perfis-e-permissões)
- [Fluxo PEPS FIFO](#fluxo-peps-fifo)
- [Sistema de Alertas e Tarefas](#sistema-de-alertas-e-tarefas)

---

## Visão Geral

O **StockFlow** é uma aplicação web de gestão de estoque desenvolvida como projeto de Programação Orientada a Objetos (POO). O sistema oferece:

- Autenticação segura com JWT (access token + refresh token rotativo)
- Controle de estoque por lote com política **PEPS (FIFO)**
- Importação de produtos via **CSV**
- Leitura de **código de barras / QR Code**
- Sistema de **alertas automáticos** de estoque baixo
- Sistema de **tarefas** atribuídas por perfil
- **Mapa visual 2D** do armazém (canvas interativo)
- Envio de **email** para redefinição de senha
- Métricas **Prometheus** e health checks
- Deploy containerizado com **Docker Compose**

---

## Arquitetura do Sistema

```
+----------------------------------------------------------+
|                      Docker Compose                      |
|                                                          |
|  +--------------+   +--------------+   +-------------+  |
|  |   Frontend   |   |   Backend    |   |   MongoDB   |  |
|  |  Vite / JS   +-->+  FastAPI     +-->+   Mongo 7   |  |
|  |  Port: 3000  |   |  Port: 8000  |   |  Port:27017 |  |
|  +--------------+   +--------------+   +-------------+  |
|                            |                             |
|                   +----------------+                     |
|                   |  Cloudflared   |  (perfil: tunnel)   |
|                   |   (opcional)   |                     |
|                   +----------------+                     |
+----------------------------------------------------------+
```

**Fluxo de autenticação:**

```
Cliente --> POST /auth/login --> access_token (30 min) + refresh_token (7 dias)
        --> GET /rota-protegida (Bearer access_token)
        --> POST /auth/refresh (refresh_token) --> novo par de tokens
        --> POST /auth/logout  (refresh_token) --> revoga token
```

---

## Estrutura de Pastas

```
StockFlow/
├── backend/
│   ├── api/
│   │   ├── main.py            # Aplicação FastAPI, todos os endpoints
│   │   ├── deps.py            # Dependências de autenticação (Bearer)
│   │   └── schemas.py         # Schemas Pydantic (request/response)
│   ├── core/
│   │   ├── config.py          # Settings via variáveis de ambiente
│   │   └── security.py        # Criação/decodificação de tokens JWT
│   ├── database/
│   │   ├── connection.py      # Singleton de conexão MongoDB
│   │   └── bootstrap.py       # Criação de índices e configurações padrão
│   ├── models/
│   │   ├── usuario_model.py
│   │   ├── produto_model.py
│   │   ├── movimentacao_model.py
│   │   ├── fornecedor_model.py
│   │   ├── secao_model.py
│   │   ├── tarefa_model.py
│   │   └── alerta_model.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── usuario_service.py
│   │   ├── produto_service.py
│   │   ├── movimentacao_service.py
│   │   ├── fornecedor_service.py
│   │   ├── secao_service.py
│   │   ├── tarefa_service.py
│   │   ├── alerta_service.py
│   │   ├── estoque_lote_service.py
│   │   └── configuracao_service.py
│   ├── utils/
│   │   ├── alertas.py          # Verificação automática de estoque
│   │   ├── barcode_qrcode.py   # Processamento de scan de código
│   │   ├── csv_import.py       # Importação de produtos via CSV
│   │   ├── email_service.py    # Envio de email SMTP
│   │   └── serializer.py       # Serialização de ObjectId/datetime
│   ├── scripts/
│   │   └── seed_users.py       # Seed inicial de usuários
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/
│   ├── index.html              # Página raiz (redireciona ao login)
│   ├── login/index.html        # Tela de login
│   ├── admin/index.html        # Painel do administrador
│   ├── gerente/index.html      # Painel do gerente/líder
│   ├── funcionario/index.html  # Painel do funcionário
│   ├── src/
│   │   ├── login/main.js
│   │   ├── admin/main.js
│   │   ├── gerente/main.js
│   │   ├── funcionario/main.js
│   │   ├── shared/
│   │   │   └── auth.js         # Módulo compartilhado de autenticação
│   │   └── styles/
│   │       ├── login.css
│   │       ├── role.css
│   │       └── admin.css
│   ├── public/
│   │   ├── logo/Logo.png
│   │   └── icons/              # SVGs usados na animação de chuva de ícones
│   ├── package.json
│   └── vite.config.js
├── tests/
│   ├── conftest.py             # Fixtures com mongomock
│   ├── unit/
│   │   └── test_security.py
│   └── integration/
│       └── test_auth_flow.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .gitignore
```

---

## Backend

### Tecnologias e Dependências

**Produção (`backend/requirements.txt`):**

| Pacote | Versão | Uso |
|---|---|---|
| `fastapi` | 0.116.1 | Framework web assíncrono |
| `uvicorn` | 0.35.0 | Servidor ASGI |
| `pymongo` | 4.10.1 | Driver MongoDB |
| `python-dotenv` | 1.0.1 | Carregamento de `.env` |
| `passlib[bcrypt]` | 1.7.4 | Hash de senhas |
| `bcrypt` | 4.1.3 | Backend de hash bcrypt |
| `PyJWT` | 2.10.1 | Geração e validação de tokens JWT |
| `prometheus-client` | 0.23.1 | Métricas Prometheus |
| `slowapi` | 0.1.9 | Rate limiting por IP |
| `python-multipart` | 0.0.20 | Upload de arquivos (CSV) |

**Desenvolvimento (`backend/requirements-dev.txt`):**

| Pacote | Versão | Uso |
|---|---|---|
| `pytest` | 8.4.2 | Framework de testes |
| `pytest-cov` | 6.3.0 | Cobertura de testes |
| `mongomock` | 4.3.0 | Mock do MongoDB para testes |
| `ruff` | 0.13.2 | Linter e formatador de código |
| `httpx` | 0.28.1 | Cliente HTTP para testes de integração |

---

### Configuração Settings

**Arquivo:** `backend/core/config.py`

A classe `Settings` carrega todas as configurações via variáveis de ambiente com fallback para valores padrão. Usa `@lru_cache` para instanciar apenas uma vez durante o ciclo de vida da aplicação.

| Variável de Ambiente | Padrão | Descrição |
|---|---|---|
| `JWT_SECRET` | `change-me-in-production` | Chave secreta para assinar tokens JWT |
| `JWT_ALGORITHM` | `HS256` | Algoritmo de assinatura JWT |
| `JWT_ACCESS_MINUTES` | `30` | Duração do access token em minutos |
| `JWT_REFRESH_DAYS` | `7` | Duração do refresh token em dias |
| `CORS_ALLOW_ORIGINS` | `http://localhost:3000` | Origens CORS permitidas (separadas por vírgula) |
| `APP_ENV` | `development` | Ambiente: `development`, `staging` ou `production` |
| `RATE_LIMIT_DEFAULT` | `120/minute` | Limite global de requisições por IP |
| `FRONTEND_RESET_URL` | `http://localhost:3000/login/` | URL base para link de reset de senha no email |
| `PASSWORD_RESET_MINUTES` | `30` | Validade do token de reset de senha em minutos |
| `SMTP_HOST` | _(vazio)_ | Host SMTP para envio de emails |
| `SMTP_PORT` | `587` | Porta SMTP |
| `SMTP_USER` | _(vazio)_ | Usuário SMTP |
| `SMTP_PASSWORD` | _(vazio)_ | Senha SMTP |
| `SMTP_FROM` | `no-reply@stockflow.local` | Endereço remetente dos emails |
| `SMTP_USE_TLS` | `true` | Usar STARTTLS na conexão SMTP |

---

### Segurança e Autenticação JWT

**Arquivo:** `backend/core/security.py`

#### Estrutura dos Tokens

**Access Token** — payload:
```json
{
  "sub": "<user_id>",
  "perfil": "admin|lider|funcionario",
  "type": "access",
  "exp": "<timestamp>",
  "iat": "<timestamp>"
}
```

**Refresh Token** — payload:
```json
{
  "sub": "<user_id>",
  "type": "refresh",
  "jti": "<uuid4>",
  "exp": "<timestamp>",
  "iat": "<timestamp>"
}
```

O campo `jti` (JWT ID) é um UUID único que permite revogar tokens individualmente no banco de dados.

#### Funções de Segurança

| Função | Retorno | Descrição |
|---|---|---|
| `create_access_token(user_id, perfil)` | `str` | Cria access token assinado com HS256 |
| `create_refresh_token(user_id)` | `(token, jti, expira_em)` | Cria refresh token com JTI único |
| `decode_token(token)` | `dict` | Decodifica e valida; HTTP 401 se expirado/inválido |
| `assert_token_type(payload, expected)` | `None` | Valida campo `type`; HTTP 401 se incorreto |

#### Dependências de Autorização

**Arquivo:** `backend/api/deps.py`

| Função | Descrição |
|---|---|
| `get_current_user` | Extrai Bearer token, valida e retorna usuário; HTTP 401 se inválido |
| `get_optional_current_user` | Igual ao anterior, mas retorna `None` se sem token (rotas opcionais) |
| `require_roles(usuario, allowed_roles)` | Verifica perfil do usuário; HTTP 403 se não autorizado |

**Fluxo interno de `get_current_user`:**
1. Extrai token do header `Authorization: Bearer <token>`
2. Decodifica e valida assinatura JWT
3. Verifica que `type == "access"`
4. Extrai `sub` (user_id) e converte para `ObjectId`
5. Busca usuário no banco e verifica se está ativo
6. Retorna documento do usuário

---

### Modelos de Dados

Todos os modelos são **classes Python puras** (sem ORM) com método `to_dict()` para serialização ao MongoDB. A validação de negócio ocorre nos construtores.

#### `Usuario` — `backend/models/usuario_model.py`

| Campo | Tipo | Descrição |
|---|---|---|
| `nome` | `str` | Nome completo do usuário |
| `email` | `str` | Email único (índice único no MongoDB) |
| `senha_hash` | `str` | Hash bcrypt da senha (nunca armazenada em texto plano) |
| `perfil` | `str` | `admin`, `lider` ou `funcionario` |
| `caixa_id` | `int` | ID numérico de 5 dígitos, gerado aleatoriamente se não informado |
| `ativo` | `bool` | Se o usuário está ativo (padrão: `True`) |
| `data_criacao` | `datetime` | Timestamp de criação |

- Perfis válidos: `{"admin", "lider", "funcionario"}` — lança `ValueError` se inválido
- Senha é hasheada com `bcrypt` automaticamente no construtor
- `caixa_id` gerado aleatoriamente entre 10000–99999 se não fornecido

#### `Produto` — `backend/models/produto_model.py`

Modelo rico com suporte a controle fiscal, por lote e PEPS.

**Campos obrigatórios:**

| Campo | Tipo | Descrição |
|---|---|---|
| `nome` | `str` | Nome do produto |
| `preco_custo` | `float` | Preço de custo |
| `preco_venda` | `float` | Preço de venda |
| `quantidade` | `int` | Quantidade em estoque |
| `estoque_minimo` | `int` | Quantidade mínima para alertas |

**Campos opcionais (seleção):**

| Campo | Tipo | Descrição |
|---|---|---|
| `sku` | `str` | Código SKU único |
| `codigo_barra` | `str` | Código de barras único |
| `ean` | `str` | Código EAN único |
| `categoria` | `str` | Categoria do produto |
| `subcategoria` | `str` | Subcategoria |
| `marca` | `str` | Marca |
| `descricao` | `str` | Descrição detalhada |
| `foto_produto` | `str` | URL ou path da foto |
| `localizacao_estoque` | `str` | Localização física no armazém |
| `fornecedor` | `str` | Nome do fornecedor |
| `fornecedor_id` | `ObjectId` | Referência ao fornecedor |
| `data_entrada` | `datetime` | Data de entrada no estoque |
| `data_validade` | `datetime` | Data de validade |
| `ncm` | `str` | Código NCM (fiscal) |
| `unidade_medida` | `str` | Unidade de medida (ex: `un`, `kg`) |
| `cfop` | `str` | Código CFOP (fiscal) |
| `numero_lote` | `str` | Número do lote |
| `numero_serie` | `str` | Número de série |
| `variacoes` | `dict` | Variações do produto (ex: tamanho, cor) |
| `estoque_maximo` | `int` | Quantidade máxima desejada |
| `preco_promocional` | `float` | Preço promocional |
| `margem_lucro` | `float` | Calculada automaticamente se não informada |
| `secao_id` | `ObjectId` | Referência à seção do armazém |
| `controlar_lote` | `bool` | Habilita controle por lote |
| `controlar_validade` | `bool` | Habilita controle de validade |
| `aplicar_peps` | `bool` | Habilita política PEPS/FIFO |
| `estoque_por_lote` | `list` | Lista de lotes com quantidades |
| `ativo` | `bool` | Soft delete (padrão: `True`) |

> A `margem_lucro` é calculada automaticamente: `((preco_venda - preco_custo) / preco_custo) * 100`

#### `Movimentacao` — `backend/models/movimentacao_model.py`

| Campo | Tipo | Descrição |
|---|---|---|
| `produto_id` | `ObjectId` | Referência ao produto |
| `tipo` | `str` | `entrada`, `saida` ou `ajuste` |
| `quantidade` | `int` | Quantidade movimentada |
| `preco_unitario` | `float` | Preço unitário no momento da movimentação |
| `usuario_id` | `ObjectId` | Usuário que realizou a movimentação |
| `numero_lote` | `str?` | Lote envolvido na movimentação |
| `data_validade` | `datetime?` | Validade do lote |
| `origem` | `str` | Origem: `manual`, `scan`, `csv`, etc. |
| `lote_esperado_peps` | `str?` | Lote correto segundo a política PEPS |
| `violacao_peps` | `bool` | Se houve violação da política PEPS |
| `data` | `datetime` | Timestamp da movimentação |

#### `Fornecedor` — `backend/models/fornecedor_model.py`

| Campo | Tipo | Descrição |
|---|---|---|
| `nome` | `str` | Nome único do fornecedor |
| `contato` | `str` | Contato (telefone ou pessoa responsável) |
| `email` | `str` | Email do fornecedor |
| `produtos_fornecidos` | `list[str]` | Lista de produtos fornecidos |

#### `Secao` — `backend/models/secao_model.py`

Representa uma seção/prateleira no mapa 2D do armazém.

| Campo | Tipo | Descrição |
|---|---|---|
| `nome` | `str` | Nome único da seção |
| `pos_x` | `int` | Posição X no canvas (pixels) |
| `pos_y` | `int` | Posição Y no canvas (pixels) |
| `largura` | `int` | Largura em pixels |
| `altura` | `int` | Altura em pixels |
| `cor_padrao` | `str` | Cor de exibição no mapa (padrão: `"green"`) |

#### `Tarefa` — `backend/models/tarefa_model.py`

| Campo | Tipo | Descrição |
|---|---|---|
| `titulo` | `str` | Título da tarefa |
| `descricao` | `str` | Descrição detalhada |
| `responsavel_id` | `ObjectId` | Usuário responsável pela tarefa |
| `status` | `str` | `pendente`, `em andamento` ou `concluida` |
| `prioridade` | `str` | `baixa`, `normal` ou `alta` |
| `origem` | `str` | `manual` (criada por usuário) ou `sistema` (criada automaticamente) |
| `tipo` | `str` | Tipo: `auditoria_estoque`, `ajuste_peps`, etc. |
| `prazo` | `datetime?` | Prazo de conclusão |
| `data_criacao` | `datetime` | Timestamp de criação |
| `data_conclusao` | `datetime?` | Timestamp de conclusão |

#### `AlertaEstoque` — `backend/models/alerta_model.py`

| Campo | Tipo | Descrição |
|---|---|---|
| `produto_id` | `ObjectId` | Produto em situação de alerta |
| `quantidade_atual` | `int` | Quantidade atual em estoque |
| `quantidade_minima` | `float` | Limite calculado com margem aplicada |
| `margem_percentual` | `float` | Margem percentual aplicada sobre estoque mínimo |
| `usuario_notificado_ids` | `list` | IDs dos usuários notificados |
| `data_alerta` | `datetime` | Quando o alerta foi gerado |
| `status` | `str` | `pendente` ou `visualizado` |

---

### Serviços

#### `AuthService` — `backend/services/auth_service.py`

Gerencia tokens de sessão persistidos no MongoDB.

| Método | Descrição |
|---|---|
| `salvar_refresh_token(user_id, jti, expira_em)` | Persiste refresh token na coleção `refresh_tokens` |
| `validar_refresh_token(user_id, jti)` | Verifica se token existe, não foi revogado e não expirou |
| `revogar_refresh_token(user_id, jti)` | Marca token como revogado (`revogado: true`) |
| `revogar_todos_refresh_tokens(user_id)` | Revoga todos os tokens ativos do usuário |
| `criar_token_reset_senha(user_id, token)` | Cria token de reset com expiração configurável |
| `validar_token_reset_senha(token)` | Valida token de reset (não usado e não expirado) |
| `marcar_token_reset_como_usado(token)` | Marca token de reset como usado |

#### `UsuarioService` — `backend/services/usuario_service.py`

| Método | Descrição |
|---|---|
| `contar_usuarios()` | Conta total de usuários (usado para lógica do primeiro admin) |
| `criar_usuario(usuario)` | Cria usuário com validação de email e caixa_id únicos |
| `autenticar(email, senha)` | Busca usuário ativo e verifica senha com bcrypt |
| `listar_usuarios(ativos_only)` | Lista usuários (padrão: apenas ativos) |
| `listar_por_perfis(perfis)` | Lista usuários filtrados por lista de perfis |
| `buscar_usuario_por_email(email)` | Busca por email |
| `buscar_usuario_por_id(usuario_id)` | Busca por ObjectId |
| `atualizar_senha_por_id(usuario_id, nova_senha)` | Atualiza hash da senha |

#### `ProdutoService` — `backend/services/produto_service.py`

| Método | Descrição |
|---|---|
| `criar_produto(produto)` | Cria produto com validação de SKU e nome+lote únicos |
| `listar_produtos(ativos)` | Lista produtos (padrão: apenas ativos) |
| `buscar_produto_por_id(produto_id)` | Busca por ObjectId |
| `buscar_por_codigo(codigo)` | Busca por `codigo_barra` ou `ean` |
| `atualizar_estoque(produto_id, nova_quantidade)` | Atualiza quantidade (não permite negativo) |
| `atualizar_produto(produto_id, dados)` | Atualiza campos arbitrários do produto |
| `desativar_produto(produto_id)` | Soft delete: seta `ativo: false` |

#### `EstoqueLoteService` — `backend/services/estoque_lote_service.py`

Serviço central para controle de estoque por lote com política PEPS.

| Método | Descrição |
|---|---|
| `registrar_entrada(produto_id, quantidade, numero_lote, data_validade, data_entrada)` | Registra entrada de lote (upsert por produto+lote) |
| `listar_lotes_disponiveis(produto_id)` | Lista lotes com saldo > 0, ordenados por PEPS |
| `consumir_saida(produto, quantidade, usuario_id, numero_lote_escolhido)` | Consome saída respeitando PEPS; detecta e registra violações |
| `_notificar_violacao_peps(...)` | Cria alerta e tarefas automáticas quando PEPS é violado |

**Lógica PEPS detalhada:**
1. Lotes são ordenados por `data_validade ASC` → `data_entrada ASC` → `numero_lote ASC`
2. O primeiro lote da lista é o "lote correto" segundo PEPS
3. Se o operador escolher outro lote, é registrada uma violação (`violacao_peps: true`)
4. Violações geram alertas operacionais e tarefas automáticas para todos os líderes ativos

#### `AlertaService` — `backend/services/alerta_service.py`

| Método | Descrição |
|---|---|
| `criar_alerta(alerta)` | Insere alerta diretamente |
| `criar_alerta_estoque_se_nao_existir(alerta)` | Cria alerta de estoque apenas se não houver pendente para o produto |
| `criar_alerta_operacional_se_nao_existir(tipo, mensagem, ...)` | Cria alerta operacional com deduplicação por chave |
| `listar_alertas()` | Lista todos os alertas |
| `marcar_visualizado(alerta_id)` | Atualiza status para `visualizado` |

#### `TarefaService` — `backend/services/tarefa_service.py`

| Método | Descrição |
|---|---|
| `criar_tarefa(tarefa)` | Insere tarefa |
| `criar_tarefa_sistema_se_nao_existir(titulo, descricao, responsavel_id, tipo, prioridade)` | Cria tarefa do sistema com deduplicação (evita duplicatas pendentes) |
| `listar_tarefas()` | Lista todas as tarefas |
| `listar_por_responsavel(responsavel_id)` | Lista tarefas de um usuário específico |
| `buscar_tarefa_por_id(tarefa_id)` | Busca por ObjectId |
| `concluir_tarefa(tarefa_id)` | Seta `status: "concluida"` e `data_conclusao` |

#### `FornecedorService` — `backend/services/fornecedor_service.py`

| Método | Descrição |
|---|---|
| `criar_fornecedor(fornecedor)` | Cria fornecedor com validação de nome único |
| `listar_fornecedores()` | Lista todos os fornecedores |
| `buscar_fornecedor_por_id(fornecedor_id)` | Busca por ObjectId |

#### `SecaoService` — `backend/services/secao_service.py`

| Método | Descrição |
|---|---|
| `criar_secao(secao)` | Cria seção com validação de nome único |
| `listar_secoes()` | Lista todas as seções |
| `buscar_secao_por_id(secao_id)` | Busca por ObjectId |

#### `MovimentacaoService` — `backend/services/movimentacao_service.py`

| Método | Descrição |
|---|---|
| `registrar_movimentacao(mov)` | Insere movimentação na coleção `movimentacoes` |
| `listar_movimentacoes()` | Lista todas as movimentações |

#### `ConfiguracaoService` — `backend/services/configuracao_service.py`

Gerencia configurações globais do sistema armazenadas no MongoDB (chave-valor).

| Método | Descrição |
|---|---|
| `get_margem_alerta_estoque()` | Retorna margem percentual para alertas (padrão: `0`) |
| `set_margem_alerta_estoque(valor)` | Atualiza margem (não permite valor negativo) |

---

### Utilitários

#### `alertas.py` — Verificação Automática de Estoque

Função `verificar_estoque(margin=None)`:

1. Obtém a margem configurada via `ConfiguracaoService` (ou usa a passada como parâmetro)
2. Lista todos os produtos ativos
3. Para cada produto onde `quantidade <= estoque_minimo * (1 + margem/100)`:
   - Cria alerta de estoque (com deduplicação — não cria se já houver pendente)
   - Cria tarefa de auditoria para cada líder ativo (com deduplicação)

#### `barcode_qrcode.py` — Processamento de Scan

Função `processar_scan(codigo, tipo, quantidade, usuario_id, numero_lote, data_validade)`:

1. Valida tipo (`entrada` ou `saida`) e quantidade positiva
2. Busca produto por `codigo_barra` ou `ean`
3. Calcula nova quantidade e valida estoque sufic
