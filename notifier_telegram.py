# -*- coding: utf-8 -*-
import requests
import time

# ⚠️ Você pediu token/id fixos no arquivo:
BOT_TOKEN = "7360602779:AAFIpncv7fkXaEX5PdWdEAUBb7NQ9SeA-F0"
CHAT_ID = "@botsinaistop"  # canal público ou chat id numérico

def escape_markdown_v2(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    escape_chars = [
        "\\", "_", "*", "[", "]", "(", ")", "~", "`", ">", "#",
        "+", "-", "=", "|", "{", "}", ".", "!"
    ]
    for ch in escape_chars:
        text = text.replace(ch, "\\" + ch)
    return text

def _post(url, payload, max_retries=3, retry_delay=2):
    for attempt in range(max_retries):
        try:
            r = requests.post(url, json=payload, timeout=12)
            if r.status_code == 200 and r.json().get("ok"):
                return True, r.json()
            if r.status_code == 429:
                retry_after = r.json().get("parameters", {}).get("retry_after", retry_delay)
                time.sleep(retry_after)
            else:
                # tenta backoff exponencial
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
        except requests.exceptions.RequestException:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
    return False, None

def send_text(text: str) -> bool:
    """Tenta MarkdownV2 (com escape) e cai pra HTML se der erro de parse."""
    if not BOT_TOKEN or not CHAT_ID:
        print("[TG] Faltou BOT_TOKEN/CHAT_ID.")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    # 1) MarkdownV2 com escape total
    md_payload = {
        "chat_id": CHAT_ID,
        "text": escape_markdown_v2(text),
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True
    }
    ok, resp = _post(url, md_payload)
    if ok:
        return True

    # 2) Fallback pra HTML simples (sem escapes)
    html_payload = {
        "chat_id": CHAT_ID,
        "text": text.replace("`", ""),  # remove crases que quebram HTML
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    ok, resp = _post(url, html_payload)
    return ok

def send_photo(image_url_or_fileid: str, caption: str = "") -> bool:
    """Envio opcional de imagem com legenda (MarkdownV2 escapado)."""
    if not BOT_TOKEN or not CHAT_ID:
        print("[TG] Faltou BOT_TOKEN/CHAT_ID.")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": CHAT_ID,
        "photo": image_url_or_fileid,
        "caption": escape_markdown_v2(caption) if caption else "",
        "parse_mode": "MarkdownV2" if caption else None
    }
    ok, resp = _post(url, payload)
    if not ok and caption:
        # fallback sem parse_mode
        payload.pop("parse_mode", None)
        ok, resp = _post(url, payload)
    return ok

def send_signal_notification(content) -> bool:
    """
    Aceita:
      - dict no SEU formato:
         symbol, entry_price, target_price, stop_loss, risk_reward, confidence_score, strategy, created_at, id
      - dict no formato deste projeto:
         symbol, entry, tp, sl, confidence, strategy, timestamp, source
      - ou string simples
    """
    if isinstance(content, str):
        return send_text(content)

    if isinstance(content, dict):
        # Normaliza chaves
        symbol = content.get("symbol", "N/A")

        entry = content.get("entry_price", content.get("entry"))
        tp    = content.get("target_price", content.get("tp"))
        sl    = content.get("stop_loss", content.get("sl"))

        rr    = content.get("risk_reward")
        conf  = content.get("confidence_score", content.get("confidence"))
        if isinstance(conf, float):
            conf = int(round(conf * 100))  # se veio 0..1 -> %
        strategy = content.get("strategy", "RSI+MACD+EMA+BB")
        created  = content.get("created_at", content.get("timestamp"))
        sig_id   = content.get("id", "")

        raw = (
            f"📢 <b>Alerta Sinais</b>\n\n"
            f"💱 Par: <b>{symbol}</b>\n"
            f"🎯 Entrada: <b>{entry}</b>\n"
            f"🥅 Alvo (TP): <b>{tp}</b>\n"
            f"🛡️ Stop (SL): <b>{sl}</b>\n"
            f"📊 R:R: <b>{rr}</b>\n" if rr else
            f"📊 Confiança: <b>{conf}%</b>\n"
        )

        # completa garantido
        extra = (
            ("" if rr else f"📊 Confiança: <b>{conf}%</b>\n") +
            f"🧠 Estratégia: <i>{strategy}</i>\n" +
            (f"📅 Criado: <code>{created}</code>\n" if created else "") +
            (f"🆔 ID: <code>{sig_id}</code>\n" if sig_id else "")
        )
        text = raw + extra
        return send_text(text)

    print("❌ Conteúdo de notificação não suportado.")
    return False
