# Telegram Bot — Worker no Render (PTB v21 + Pagar.me)

Pronto para rodar 24/7 como **Background Worker** no Render.
- `python-telegram-bot==21.6` (compatível com Python 3.13)
- Comando `/pix` cria cobrança PIX via **Pagar.me Core API v5**
- Sem porta HTTP (evita 'port scan timeout')

## Env vars
- `TELEGRAM_TOKEN` (obrigatório)
- `PAGARME_SECRET_KEY` (obrigatório)
- `ADMIN_ID` (opcional, para `/stop`)
- `PAGARME_API_BASE` (opcional; default `https://api.pagar.me/core/v5`)

## Deploy (manual)
1. Render → **New → Background Worker**
2. Build: `pip install -r requirements.txt`
3. Start: `python main.py`
4. Plan: Starter
5. Configure as env vars e Deploy.

> Importante: mantenha **apenas 1 serviço** usando este token para evitar `409 Conflict`.
