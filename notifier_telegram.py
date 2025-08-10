# -*- coding: utf-8 -*-
import requests
import time
import random

# ⚠️ Se preferir ler do .env, troque por import do config e pegue TELEGRAM_BOT_TOKEN/CHAT_ID de lá.
BOT_TOKEN = "7360602779:AAFIpncv7fkXaEX5PdWdEAUBb7NQ9SeA-F0"
CHAT_ID = "@botsinaistop"  # canal ou chat id numérico

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

def _post(url, payload, max_retries=4, base_delay=2.0):
    delay = base_delay
    for attempt in range(1, max_retries+1):
        try:
            r = requests.post(url, json=payload, timeout=15)
            if r.status_code == 200 and r.json().get("ok"):
                return True, r.json()
            if r.status_code == 429:
                ra = r.json().get("parameters", {}).get("retry_after", None)
                wait = float(ra) if ra else delay + random.uniform(0.5, 1.5)
                print(f"⚠️ Rate limit TG: aguardando {round(wait,1)}s (tentativa {attempt}/{max_retries})")
                time.sleep(wait)
                delay = min(delay * 2.0, 60)
                continue
            # outros erros HTTP: tenta backoff leve
            print(f"[TG] Falha ({r.status_code}): {r.text}")
            time.sleep(delay + random.uniform(0.5, 1.5))
            delay = min(delay * 2.0, 60)
        except requests.exceptions.RequestException as e:
            print(f"[TG] Erro envio: {e}")
            time.sleep(delay + random.uniform(0.5, 1.5))
            delay = min(delay * 2.0, 60)
    return False, None

def send_text(text: str) -> bool:
    if not BOT_TOKEN or not CHAT_ID:
        print("[TG] BOT_TOKEN/CHAT_ID ausentes.")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    # 1) Tenta MarkdownV2 com escape
    md_payload = {
        "chat_id": CHAT_ID,
        "text": escape_markdown_v2(text),
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True
    }
    ok, _ = _post(url, md_payload)
    if ok:
        return True

    # 2) Fallback pra HTML sem escapes
    html_payload = {
        "chat_id": CHAT_ID,
        "text": text.replace("`", ""),
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    ok, _ = _post(url, html_payload)
    return ok

def _format_signal_message(content: dict) -> str:
    # Normaliza chaves: aceita dois formatos
    symbol = content.get("symbol", "N/A")

    entry = content.get("entry_price", content.get("entry"))
    tp    = content.get("target_price", content.get("tp"))
    sl    = content.get("stop_loss", content.get("sl"))

    rr    = content.get("risk_reward")
    conf  = content.get("confidence_score", content.get("confidence"))
    # se vier 0..1, converte pra %
    if isinstance(conf, float) and conf <= 1.0:
        conf = int(round(conf * 100))

    strategy = content.get("strategy", "RSI+MACD+EMA+BB")
    created  = content.get("created_at", content.get("timestamp"))
    sig_id   = content.get("id", "")

    # Monta texto (HTML simples – o send_text dá fallback se precisar)
    lines = [
        "📢 <b>Alerta Sinais</b>",
        "",
        f"💱 Par: <b>{symbol}</b>",
    ]
    if entry is not None: lines.append(f"🎯 Entrada: <b>{entry}</b>")
    if tp    is not None: lines.append(f"🥅 Alvo (TP): <b>{tp}</b>")
    if sl    is not None: lines.append(f"🛡️ Stop (SL): <b>{sl}</b>")
    if rr    is not None: lines.append(f"📊 R:R: <b>{rr}</b>")
    if conf  is not None: lines.append(f"📈 Confiança: <b>{conf}%</b>")
    lines.append(f"🧠 Estratégia: <i>{strategy}</i>")
    if created is not None: lines.append(f"📅 Criado: <code>{created}</code>")
    if sig_id: lines.append(f"🆔 ID: <code>{sig_id}</code>")

    return "\n".join(lines)

def send_signal_notification(content) -> bool:
    """Aceita dict no formato local ou string simples."""
    if isinstance(content, str):
        return send_text(content)
    if isinstance(content, dict):
        text = _format_signal_message(content)
        return send_text(text)
    print("❌ Conteúdo não suportado pelo notifier.")
    return False
