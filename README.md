# Telegram Bot Unificado — Worker no Render (com Pagar.me)

Projeto **unificado** (um único entrypoint) para rodar 24/7 no **Render** como **Background Worker**.
- Bot do Telegram com `python-telegram-bot v20`
- Comando `/pix` para criar cobrança **PIX** na **Pagar.me Core API v5**
- Evita conflitos de polling (`409 Conflict`) e erro de porta (não abre HTTP).

## Variáveis de ambiente
- `TELEGRAM_TOKEN` — token do BotFather (**obrigatório**)
- `ADMIN_ID` — seu user_id (opcional; autoriza `/stop`)
- `PAGARME_SECRET_KEY` — chave secreta da Pagar.me (**obrigatório**)
- `PAGARME_API_BASE` — default: `https://api.pagar.me/core/v5`

## Comandos
- `/start` — status
- `/help` — ajuda
- `/id` — retorna seu `user_id`
- `/stop` — encerra o bot (somente `ADMIN_ID`)
- `/pix <valor> <descrição...>` — cria cobrança PIX na Pagar.me (ex.: `/pix 19.90 Plano`)

## Deploy no Render
### A) Blueprint
- Render → **New → Blueprint** (aponta para o repo com `render.yaml`).

### B) Manual (Background Worker)
- Render → **New → Background Worker**
- Build: `pip install -r requirements.txt`
- Start: `python main.py`
- Plan: Starter
- Defina as env vars e faça deploy.

> Mantenha **apenas 1 serviço** usando este token para evitar `409 Conflict`.
