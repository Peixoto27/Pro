import requests
import time
import json

BOT_TOKEN = "7360602779:AAFIpncv7fkXaEX5PdWdEAUBb7NQ9SeA-F0"
CHAT_ID = "@botsinaistop"  # Envia diretamente para o canal público

def escape_markdown_v2(text):
    """
    Escapa todos os caracteres especiais do MarkdownV2 para evitar erros no Telegram.
    """
    if not isinstance(text, str):
        text = str(text)

    # Ordem é importante: a barra invertida primeiro
    escape_chars = [
        "\\", "_", "*", "[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|",
        "{", "}", ".", "!", 
    ]
    for char in escape_chars:
        text = text.replace(char, "\\" + char)
    return text

def send_signal_notification(content, max_retries=3, retry_delay=2):
    """
    Envia notificação para o Telegram com mecanismo de retry robusto.
    Agora todos os caracteres reservados do MarkdownV2 são escapados de forma global.
    """
    try:
        if isinstance(content, dict):  # É um sinal de entrada
            symbol = str(content["symbol"])
            entry_price = str(content["entry_price"])
            target_price = str(content["target_price"])
            stop_loss = str(content["stop_loss"])
            risk_reward = str(content["risk_reward"])
            confidence_score = str(content["confidence_score"])
            strategy = str(content["strategy"])
            created_at = str(content["created_at"])
            signal_id = str(content["id"])

            # Monta tudo cru, sem escapes
            raw_text = (
                f"📢 Novo sinal detectado para *{symbol}*\n"
                f"🎯 Entrada: `{entry_price}` | Alvo: `{target_price}` | Stop: `{stop_loss}`\n"
                f"📊 R:R: `{risk_reward}` | Confiança: `{confidence_score}`%\n"
                f"⏱️ Estratégia: `{strategy}`\n"
                f"📅 Criado em: `{created_at}`\n"
                f"🆔 ID do Sinal: `{signal_id}`"
            )

        elif isinstance(content, str):  # Mensagem simples
            raw_text = content

        else:
            print("❌ Tipo de conteúdo de notificação não suportado.")
            return False

        # Escapa tudo de uma vez no final
        text = escape_markdown_v2(raw_text)

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "MarkdownV2"
        }

        for attempt in range(max_retries):
            try:
                print(f"[NOTIFIER] Tentativa {attempt + 1}/{max_retries} - Enviando para: {url}")
                response = requests.post(url, json=payload, timeout=10)

                print(f"[NOTIFIER] Resposta da API: Status {response.status_code}")
                print(f"[NOTIFIER] Conteúdo da resposta: {response.text}")

                if response.status_code == 200 and response.json().get("ok"):
                    print("✅ Notificação enviada para o canal com sucesso.")
                    return True
                elif response.status_code == 429:
                    retry_after = response.json().get("parameters", {}).get("retry_after", retry_delay)
                    print(f"⚠️ Rate limit atingido. Aguardando {retry_after} segundos...")
                    time.sleep(retry_after)
                else:
                    print(f"❌ Erro HTTP {response.status_code}: {response.text}")

                if attempt < max_retries - 1:
                    print(f"⏳ Aguardando {retry_delay} segundos antes da próxima tentativa...")
                    time.sleep(retry_delay)
                    retry_delay *= 2

            except requests.exceptions.Timeout:
                print(f"⏰ Timeout na tentativa {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
            except requests.exceptions.RequestException as e:
                print(f"🌐 Erro de conexão na tentativa {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2

        print(f"❌ Falha ao enviar notificação após {max_retries} tentativas.")
        return False

    except Exception as e:
        print(f"❌ Erro crítico no envio para o Telegram: {e}")
        return False
