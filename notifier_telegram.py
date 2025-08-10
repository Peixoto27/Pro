# -*- coding: utf-8 -*-
import requests, time
from config import TELEGRAM_BOT_TOKEN as BOT_TOKEN, TELEGRAM_CHAT_ID as CHAT_ID

def escape_markdown_v2(text):
    text = str(text)
    escape = ["\\","_","*","[","]","(",")","~","`",">","#","+","-","=","|","{","}","!","."]
    for ch in escape:
        text = text.replace(ch, "\\"+ch)
    return text

def _post(url, payload, max_retries=3, retry_delay=2):
    for attempt in range(max_retries):
        try:
            r = requests.post(url, json=payload, timeout=12)
            if r.status_code == 200 and r.json().get("ok"):
                return True
            if r.status_code == 429:
                ra = r.json().get("parameters", {}).get("retry_after", retry_delay)
                time.sleep(float(ra))
            else:
                time.sleep(retry_delay); retry_delay *= 2
        except requests.RequestException:
            time.sleep(retry_delay); retry_delay *= 2
    return False

def send_signal_notification(content, max_retries=3, retry_delay=2):
    if not BOT_TOKEN or not CHAT_ID:
        print("[TG] BOT_TOKEN/CHAT_ID ausentes.")
        return False

    if isinstance(content, dict):
        symbol = content.get("symbol","N/A")
        entry  = content.get("entry_price", content.get("entry"))
        tp     = content.get("target_price", content.get("tp"))
        sl     = content.get("stop_loss", content.get("sl"))
        rr     = content.get("risk_reward")
        conf   = content.get("confidence_score", content.get("confidence"))
        if isinstance(conf, float) and conf <= 1: conf = round(conf*100,2)
        strategy = content.get("strategy","RSI+MACD+EMA+BB")
        created  = content.get("created_at", content.get("timestamp"))
        sig_id   = content.get("id","")

        lines = [
            f"📢 Novo sinal para *{escape_markdown_v2(symbol)}*",
            f"🎯 Entrada: `{escape_markdown_v2(entry)}` | Alvo: `{escape_markdown_v2(tp)}` | Stop: `{escape_markdown_v2(sl)}`",
        ]
        if rr is not None:
            lines.append(f"📊 R:R: `{escape_markdown_v2(rr)}`")
        if conf is not None:
            lines.append(f"📈 Confiança: `{escape_markdown_v2(conf)}`%")
        lines.append(f"🧠 Estratégia: `{escape_markdown_v2(strategy)}`")
        if created is not None:
            lines.append(f"📅 Criado em: `{escape_markdown_v2(created)}`")
        if sig_id:
            lines.append(f"🆔 ID: `{escape_markdown_v2(sig_id)}`")
        text = "\n".join(lines)
    else:
        text = escape_markdown_v2(str(content))

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "MarkdownV2"}
    ok = _post(url, payload, max_retries=max_retries, retry_delay=retry_delay)
    print("✅ Enviado ao Telegram." if ok else "❌ Falha no envio.")
    return ok
