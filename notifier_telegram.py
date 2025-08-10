# -*- coding: utf-8 -*-
import requests
import time

# 🔹 DADOS DO SEU BOT / CANAL
BOT_TOKEN = "7360602779:AAFIpncv7fkXaEX5PdWdEAUBb7NQ9SeA-F0"
CHAT_ID = "-1002897426078"  # ID numérico do canal @botsinaistop

def escape_markdown_v2(text):
    """Escapa caracteres especiais para MarkdownV2"""
    text = str(text)
    escape_chars = [
        "\\", "_", "*", "[", "]", "(", ")", "~", "`", ">", "#",
        "+", "-", "=", "|", "{", "}", ".", "!"
    ]
    for char in escape_chars:
        text = text.replace(char, "\\" + char)
    return text

def send_signal_notification(content, max_retries=3, retry_delay=2):
    """
    Envia sinal ou mensagem simples para o canal do Telegram.
    """
    try:
        if isinstance(content, dict):  # É um sinal estruturado
            text = (
                f"📢 Novo sinal detectado para *{escape_markdown_v2(content['symbol'])}*\n"
                f"🎯 Entrada: `{escape_markdown_v2(content['entry_price'])}` | "
                f"Alvo: `{escape_markdown_v2(content['target_price'])}` | "
                f"Stop: `{escape_markdown_v2(content['stop_loss'])}`\n"
                f"📊 R:R: `{escape_markdown_v2(content['risk_reward'])}` | "
                f"Confiança: `{escape_markdown_v2(content['confidence_score'])}`%\n"
                f"⏱️ Estratégia: `{escape_markdown_v2(content['strategy'])}`\n"
                f"📅 Criado em: `{escape_markdown_v2(content['created_at'])}`\n"
                f"🆔 ID do Sinal: `{escape_markdown_v2(content['id'])}`"
            )
        else:  # Mensagem simples
            text = escape_markdown_v2(str(content))

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "MarkdownV2"}

        for attempt in range(max_retries):
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200 and response.json().get("ok"):
                print("✅ Notificação enviada com sucesso!")
                return True
            elif response.status_code == 429:  # Rate limit
                retry_after = response.json().get("parameters", {}).get("retry_after", retry_delay)
                print(f"⚠️ Rate limit, aguardando {retry_after}s...")
                time.sleep(retry_after)
            else:
                print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            time.sleep(retry_delay)
        return False
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        return False

# 🔹 TESTE RÁPIDO
if __name__ == "__main__":
    send_signal_notification("🚀 Teste de envio — Bot conectado ao canal!")
