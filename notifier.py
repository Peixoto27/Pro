import requests
import time
import json

BOT_TOKEN = "7360602779:AAFIpncv7fkXaEX5PdWdEAUBb7NQ9SeA-F0"
CHAT_ID = "@botsinaistop"  # Envia diretamente para o canal público

def escape_markdown_v2(text):
    """Escapa apenas os caracteres essenciais para MarkdownV2 que podem conflitar com o conteúdo.
    Mantém a formatação mais limpa para melhor visualização.
    """
    # Caracteres que precisam ser escapados em MarkdownV2 para texto simples
    # A barra invertida deve ser escapada primeiro
    text = text.replace("\\", "\\\\")
    # Escapar apenas os caracteres que são usados para formatação e que podem aparecer no texto
    # Removendo o escape de alguns caracteres que não são estritamente necessários para a formatação básica
    text = text.replace("_", "\\_")
    text = text.replace("*", "\\*")
    text = text.replace("[", "\\[")
    text = text.replace("]", "\\]")
    text = text.replace("(", "\\(")
    text = text.replace(")", "\\)")
    text = text.replace("~", "\\~")
    text = text.replace("`", "\\`")
    text = text.replace(">", "\\>")
    text = text.replace("#", "\\#")
    text = text.replace("+", "\\+")
    text = text.replace("-", "\\-")
    text = text.replace("=", "\\=")
    text = text.replace("|", "\\|")
    text = text.replace("{", "\\{")
    text = text.replace("}", "\\}")
    text = text.replace("!", "\\!")
    text = text.replace(".", "\\.") # Ponto final pode ser um problema em alguns contextos
    return text

def send_signal_notification(content, max_retries=3, retry_delay=2):
    """
    Envia notificação para o Telegram com mecanismo de retry robusto.
    
    Args:
        content: Conteúdo da mensagem (dict para sinal ou str para mensagem)
        max_retries: Número máximo de tentativas (padrão: 3)
        retry_delay: Delay entre tentativas em segundos (padrão: 2)
    """
    try:
        if isinstance(content, dict): # É um sinal de entrada
            symbol = content["symbol"]
            entry_price = content["entry_price"]
            target_price = content["target_price"]
            stop_loss = content["stop_loss"]
            risk_reward = content["risk_reward"]
            confidence_score = content["confidence_score"]
            strategy = content["strategy"]
            created_at = content["created_at"]
            signal_id = content["id"]

            # Aplicar escape apenas onde necessário para MarkdownV2
            text = (
                f'📢 Novo sinal detectado para *{escape_markdown_v2(symbol)}*\n'
                f'🎯 Entrada: `{escape_markdown_v2(str(entry_price))}` | Alvo: `{escape_markdown_v2(str(target_price))}` | Stop: `{escape_markdown_v2(str(stop_loss))}`\n'
                f'📊 R:R: `{escape_markdown_v2(str(risk_reward))}` | Confiança: `{escape_markdown_v2(str(confidence_score))}`%\n'
                f'⏱️ Estratégia: `{escape_markdown_v2(strategy)}`\n'
                f'📅 Criado em: `{escape_markdown_v2(created_at)}`\n'
                f'🆔 ID do Sinal: `{escape_markdown_v2(signal_id)}`'
            )
            print(f"[NOTIFIER] Preparando para enviar sinal: {content['symbol']}")
        elif isinstance(content, str): # É uma mensagem de alvo/stop loss
            text = escape_markdown_v2(content)
            print(f"[NOTIFIER] Preparando para enviar mensagem de status: {content[:50]}...")
        else:
            print("❌ Tipo de conteúdo de notificação não suportado.")
            return False

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "MarkdownV2"  # Mantendo MarkdownV2
        }
        
        # Implementação do mecanismo de retry
        for attempt in range(max_retries):
            try:
                print(f"[NOTIFIER] Tentativa {attempt + 1}/{max_retries} - Enviando para: {url}")
                response = requests.post(url, json=payload, timeout=10)
                
                print(f"[NOTIFIER] Resposta da API: Status {response.status_code}")
                print(f"[NOTIFIER] Conteúdo da resposta: {response.text}")
                
                if response.status_code == 200:
                    response_data = response.json()
                    if response_data.get("ok"):
                        print("✅ Notificação enviada para o canal com sucesso.")
                        return True
                    else:
                        print(f"❌ API retornou erro: {response_data.get('description', 'Erro desconhecido')}")
                elif response.status_code == 429:  # Rate limit
                    retry_after = response.json().get("parameters", {}).get("retry_after", retry_delay)
                    print(f"⚠️ Rate limit atingido. Aguardando {retry_after} segundos...")
                    time.sleep(retry_after)
                    continue
                else:
                    print(f"❌ Erro HTTP {response.status_code}: {response.text}")
                
                # Se não foi sucesso e não é a última tentativa, aguarda antes de tentar novamente
                if attempt < max_retries - 1:
                    print(f"⏳ Aguardando {retry_delay} segundos antes da próxima tentativa...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Backoff exponencial
                    
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



