# -*- coding: utf-8 -*-
import requests, time

# ✅ seu bot + canal (ID numérico)
BOT_TOKEN = "7360602779:AAFIpncv7fkXaEX5PdWdEAUBb7NQ9SeA-F0"
CHAT_ID   = "-1002705937565"

def escape_markdown_v2(text):
    text = str(text)
    # sem escapar o ponto (.)
    for ch in ["\\","_","*","[","]","(",")","~","`",">","#","+","-","=","|","{","}","!"]:
        text = text.replace(ch, "\\"+ch)
    return text

def _post(url, payload, max_retries=3, retry_delay=2):
    for attempt in range(max_retries):
        try:
            r = requests.post(url, json=payload, timeout=12)
            print(f"[TG] tentativa {attempt+1}, status={r.status_code}, resp={r.text[:200]}")
            if r.status_code == 200 and r.json().get("ok"):
                return True
            if r.status_code == 429:
                ra = r.json().get("parameters", {}).get("retry_after", retry_delay)
                time.sleep(float(ra))
            else:
                time.sleep(retry_delay); retry_delay *= 2
        except requests.RequestException as e:
            print(f"[TG] erro req: {e}")
            time.sleep(retry_delay); retry_delay *= 2
    return False

def _build_text(content: dict) -> str:
    symbol = content.get("symbol","N/A")
    entry  = content.get("entry_price", content.get("entry"))
    tp     = content.get("target_price", content.get("tp"))
    sl     = content.get("stop_loss", content.get("sl"))
    rr     = content.get("risk_reward")
    conf   = content.get("confidence_score", content.get("confidence"))
    if isinstance(conf, float) and conf <= 1: conf = round(conf*100,2)
    strat  = content.get("strategy","RSI+MACD+EMA+BB")
    created= content.get("created_at", content.get("timestamp"))
    sig_id = content.get("id","")

    lines = [
        f"📢 Novo sinal para *{escape_markdown_v2(symbol)}*",
        f"🎯 Entrada: `{escape_markdown_v2(entry)}` | Alvo: `{escape_markdown_v2(tp)}` | Stop: `{escape_markdown_v2(sl)}`",
    ]
    if rr is not None: lines.append(f"📊 R:R: `{escape_markdown_v2(rr)}`")
    if conf is not None: lines.append(f"📈 Confiança: `{escape_markdown_v2(conf)}`%")
    lines.append(f"🧠 Estratégia: `{escape_markdown_v2(strat)}`")
    if created is not None: lines.append(f"📅 Criado em: `{escape_markdown_v2(created)}`")
    if sig_id: lines.append(f"🆔 ID: `{escape_markdown_v2(sig_id)}`")
    return "\n".join(lines)

def send_signal_notification(content, max_retries=3, retry_delay=2):
    try:
        text = _build_text(content) if isinstance(content, dict) else escape_markdown_v2(str(content))
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "MarkdownV2"}

        ok = _post(url, payload, max_retries=max_retries, retry_delay=retry_delay)
        if ok:
            print("✅ Notificação enviada.")
            return True

        # Fallback para HTML (remove escapes básicos)
        html_text = text.replace("\\","").replace("`","").replace("*","")
        html_payload = {"chat_id": CHAT_ID, "text": html_text, "parse_mode": "HTML", "disable_web_page_preview": True}
        ok = _post(url, html_payload, max_retries=max_retries, retry_delay=retry_delay)
        print("✅ Enviado no fallback HTML." if ok else "❌ Falha no envio após retries.")
        return ok
    except Exception as e:
        print(f"❌ Erro crítico notifier: {e}")
        return False
