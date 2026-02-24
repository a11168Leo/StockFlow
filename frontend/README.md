# Frontend (Vite + JS)

Frontend inicial organizado por perfil:

- `login/`
- `admin/`
- `gerente/`
- `funcionario/`

## Estrutura

- `index.html`: redireciona para `/login/`
- `login/index.html`: login
- `admin/index.html`: area admin
- `gerente/index.html`: area gerente
- `funcionario/index.html`: area funcionario
- `src/shared/auth.js`: sessao, decode JWT e regras de acesso

## Regras de redirecionamento

Depois do login:
- `admin` -> `/admin/`
- `lider` (backend) -> `/gerente/`
- `funcionario` -> `/funcionario/`

## Setup

1. Suba o backend em `http://localhost:8000`.
2. No `frontend`:
   - `npm install`
   - `npm run dev`
3. Abra `http://localhost:3000/login/`.

## Config

Crie `frontend/.env` baseado em `.env.example`.

- `VITE_API_BASE_URL=http://localhost:8000`
- `VITE_RAIN_MODE=mixed` (`stars`, `icons`, `mixed`)
- `VITE_ICON_FILES=cart.svg,box.svg,tag.svg`

## Icones para chuva

Coloque seus arquivos em `frontend/public/icons/`.
Exemplos iniciais ja incluidos:

- `cart.svg`
- `box.svg`
- `tag.svg`

## Build

- `npm run build`
- `npm run preview`
