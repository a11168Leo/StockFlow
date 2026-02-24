# StockFlow

Status atual do projeto para orientar integracoes e continuidade do desenvolvimento.

## Visao Geral

StockFlow hoje esta implementado como backend em FastAPI com MongoDB para controle de estoque, alertas e tarefas operacionais.

## O que ja foi feito

- Estrutura principal do backend organizada em:
  - `backend/api`
  - `backend/models`
  - `backend/services`
  - `backend/utils`
  - `backend/database`
- Conexao com MongoDB via `MONGO_URI` e selecao de banco.
- Bootstrap de indices e configuracao padrao (`margem_alerta_estoque`).
- Modelos de dominio:
  - Usuario
  - Produto
  - Movimentacao
  - Alerta
  - Tarefa
  - Fornecedor
  - Secao
- Servicos implementados para:
  - usuarios
  - produtos
  - movimentacoes
  - alertas
  - tarefas
  - configuracoes
  - estoque por lote (PEPS/FIFO)
  - fornecedores
  - secoes
- Endpoints principais ja disponiveis:
  - `POST /usuarios/`
  - `POST /login/`
  - `GET /produtos/`
  - `POST /produtos/`
  - `POST /produtos/scan/`
  - `POST /produtos/csv/`
  - `GET /alertas/`
  - `POST /alertas/gerar/`
  - `GET /configuracoes/margem-alerta`
  - `PUT /configuracoes/margem-alerta`
  - `POST /tarefas/`
  - `GET /tarefas/minhas`
  - `POST /tarefas/{tarefa_id}/concluir`
- Regras de negocio ja aplicadas:
  - perfis de acesso (`admin`, `lider`, `funcionario`)
  - controle de permissoes por rota
  - validacoes de duplicidade de produto
  - movimentacao por scan (entrada e saida)
  - controle de lote e validacao PEPS
  - criacao automatica de alertas e tarefas em cenarios operacionais
  - importacao de produtos por CSV
  - serializacao de `ObjectId` e `datetime` para JSON

## O que esta em progresso

- Existem alteracoes locais nao commitadas no backend (arquivos modificados e novos arquivos).
- Existem arquivos de cache Python (`__pycache__`, `.pyc`) no workspace que precisam de limpeza.

## O que ainda nao foi feito

- Autenticacao robusta (JWT com expiracao/refresh). Hoje usa `X-User-Id`.
- Suite de testes automatizados (unitarios e integracao).
- CI/CD com lint e testes em push.
- Observabilidade completa (logs estruturados, metricas e alertas tecnicos).
- Endpoints publicos para todos os servicos auxiliares (ex.: fornecedores/secoes/movimentacoes).
- Documentacao detalhada de payloads/request-response de cada endpoint.
- Estrategia formal de deploy (Docker, health checks, ambiente staging/producao).
- Hardening de seguranca para producao (gestao de segredos, CORS restritivo, rate limit).

## Proximas Integracoes Recomendadas

1. Implementar JWT e remover dependencia de `X-User-Id`.
2. Criar testes para fluxos criticos (`/login`, `/produtos/scan`, `/alertas`).
3. Expor endpoints faltantes para fornecedores, secoes e movimentacoes.
4. Padronizar erros e adicionar endpoints de health check.
5. Limpar arquivos de cache e ajustar `.gitignore`.

## Como executar (baseline)

1. Criar e ativar ambiente virtual Python.
2. Instalar dependencias:
   - `pip install -r backend/requirements.txt`
3. Configurar `.env` na raiz com:
   - `MONGO_URI=...`
   - `MONGO_DB_NAME=estoque_db` (opcional)
4. Iniciar API:
   - `uvicorn backend.api.main:app --reload`

## Observacao

Este README representa o estado observado no workspace em 23/02/2026 e deve ser atualizado a cada ciclo de entrega.
