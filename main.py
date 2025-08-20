import os
import logging
import base64
from typing import Optional

import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
PAGARME_SECRET_KEY = os.getenv("PAGARME_SECRET_KEY")
PAGARME_API_BASE = os.getenv("PAGARME_API_BASE", "https://api.pagar.me/core/v5")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("telegram-bot")

def _pagarme_auth_header(secret_key: str) -> str:
    token = base64.b64encode((secret_key + ":").encode()).decode()
    return f"Basic {token}"

def criar_cobranca_pix(valor_centavos: int, descricao: str, customer_email: Optional[str] = None) -> dict:
    if not PAGARME_SECRET_KEY:
        raise RuntimeError("PAGARME_SECRET_KEY não definida.")
    url = f"{PAGARME_API_BASE}/orders"
    payload = {
        "items": [{"amount": valor_centavos, "description": descricao[:255], "quantity": 1}],
        "payments": [{"payment_method": "pix"}],
    }
    if customer_email:
        payload["customer"] = {"name": "Cliente", "email": customer_email}
    headers = {"Authorization": _pagarme_auth_header(PAGARME_SECRET_KEY), "Content-Type": "application/json"}
    r = requests.post(url, json=payload, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()

def _parse_valor_to_centavos(txt: str) -> Optional[int]:
    txt = txt.strip().replace("R$", "").replace(",", ".")
    try:
        valor = float(txt)
        return max(int(round(valor * 100)), 0)
    except Exception:
        return None

HELP_TEXT = (
    "🤖 *Bot do Telegram online!*\n"
    "Comandos:\n"
    "• `/start` – status\n"
    "• `/help` – ajuda\n"
    "• `/id` – mostra seu user_id\n"
    "• `/pix <valor> <descrição...>` – cria cobrança PIX (ex.: `/pix 19.90 Plano`)\n"
    "• `/stop` – parar o bot (somente ADMIN)\n"
)

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot rodando 24/7 como Worker no Render.\nEnvie /help para ver os comandos.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_markdown_v2(HELP_TEXT)

async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id if update.effective_user else None
    await update.message.reply_text(f"Seu user_id: {uid}")

async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user and update.effective_user.id == ADMIN_ID:
        await update.message.reply_text("⛔ Bot desligando...")
        await context.application.stop()
    else:
        await update.message.reply_text("🚫 Você não tem permissão para parar o bot.")

async def pix_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not PAGARME_SECRET_KEY:
        await update.message.reply_text("❗ Configure a variável PAGARME_SECRET_KEY antes de usar /pix.")
        return
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Uso: /pix <valor> <descrição...>\nEx.: /pix 19.90 Plano mensal")
        return

    valor_txt = context.args[0]
    descricao = " ".join(context.args[1:])
    centavos = _parse_valor_to_centavos(valor_txt)
    if centavos is None or centavos <= 0:
        await update.message.reply_text("Valor inválido. Ex.: 19.90 ou 12,34")
        return

    try:
        resp = criar_cobranca_pix(centavos, descricao)
        charges = resp.get("charges") or resp.get("payments") or []
        resumo = [f"✅ PIX criado com sucesso!", f"Descrição: {descricao[:80]}", f"Valor: R$ {centavos/100:.2f}"]
        info = {}
        def dig(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    lk = k.lower()
                    if isinstance(v, str):
                        if lk in ("qr_code_url", "qr_code_link", "payment_link", "link"):
                            info.setdefault("link", v)
                        if lk in ("qr_code", "qrcode", "qr", "qr_code_base64"):
                            info.setdefault("qr", v)
                    dig(v)
            elif isinstance(obj, list):
                for el in obj: dig(el)
        dig(charges)
        if info.get("link"): resumo.append(f"🔗 Link: {info['link']}")
        if info.get("qr") and len(info["qr"]) < 1500:
            resumo.append("\n🔑 Chave PIX (QR):\n" + info["qr"])
        await update.message.reply_text("\n".join(resumo))
    except requests.HTTPError as e:
        body = e.response.text if e.response is not None else str(e)
        await update.message.reply_text(f"❌ Erro HTTP na Pagar.me: {e.response.status_code if e.response else ''} {body[:600]}")
    except Exception as e:
        await update.message.reply_text(f"❌ Falha ao criar cobrança PIX: {e}")

def main():
    if not TELEGRAM_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN não definido.")
    if not PAGARME_SECRET_KEY:
        raise RuntimeError("PAGARME_SECRET_KEY não definido.")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("id", id_cmd))
    app.add_handler(CommandHandler("stop", stop_cmd))
    app.add_handler(CommandHandler("pix", pix_cmd))

    # PTB v21: run_polling síncrono; descarta updates antigos
    app.run_polling(drop_pending_updates=True, allowed_updates=None)

if __name__ == "__main__":
    main()
