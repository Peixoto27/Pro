import requests

BOT_TOKEN = "7360602779:AAFIpncv7fkXaEX5PdWdEAUBb7NQ9SeA-F0"
CHAT_ID = "@botsinaistop"

def send_telegram_message(text: str) -> bool:
    if not BOT_TOKEN or not CHAT_ID:
        print("[TG] Bot token/Chat ID ausentes. Pulei envio.")
        return False
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        if r.status_code == 200 and r.json().get("ok"):
            print("[TG] Mensagem enviada com sucesso.")
            return True
        print(f"[TG] Falha ({r.status_code}): {r.text}")
    except Exception as e:
        print(f"[TG] Erro envio: {e}")
    return False
