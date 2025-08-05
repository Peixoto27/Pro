# notifier.py
import requests
import os

# Carregando as credenciais de variáveis de ambiente para mais segurança
BOT_TOKEN = os.getenv("BOT_TOKEN", "7360602779:AAFIpncv7fkXaEX5PdWdEAUBb7NQ9SeA-F0")
CHAT_ID = os.getenv("CHAT_ID", "@botsinaistop")

def send_signal_notification(signal):
    """Envia a notificação de um NOVO SINAL encontrado."""
    try:
        text = (
            f"📢 **Novo Sinal Detectado**\n\n"
            f"🪙 **Ativo:** {signal['symbol']}\n"
            f"📈 **Tipo:** {signal['signal_type']}\n\n"
            f"🎯 **Entrada:** `{signal['entry_price']}`\n"
            f"✅ **Alvo (Lucro):** `{signal['target_price']}`\n"
            f"❌ **Stop (Perda):** `{signal['stop_loss']}`\n\n"
            f"📊 **Risco/Retorno:** {signal['risk_reward']}\n"
            f"💡 **Confiança:** {signal['confidence_score']}%\n"
            f"💰 **Lucro Estimado:** {signal['expected_profit_percent']}%\n\n"
            f"🔍 **Estratégia:** {signal['strategy']} ({signal['timeframe']})"
        )
        _send_message(text)
        print(f"✅ Notificação de novo sinal para {signal['symbol']} enviada ao Telegram.")
    except Exception as e:
        print(f"❌ Erro no envio da notificação de novo sinal: {e}")

def send_take_profit_notification(trade, current_price):
    """Envia a notificação de que o ALVO (Take Profit) foi atingido."""
    try:
        profit_percent = abs((float(trade['target_price']) - float(trade['entry_price'])) / float(trade['entry_price'])) * 100
        text = (
            f"✅ **ALVO ATINGIDO! (LUCRO)** ✅\n\n"
            f"🪙 **Ativo:** {trade['symbol']}\n"
            f"📈 **Tipo:** {trade['signal_type']}\n\n"
            f"🔹 **Preço de Entrada:** `{trade['entry_price']}`\n"
            f"🎯 **Preço do Alvo:** `{trade['target_price']}`\n"
            f"📈 **Preço Atual:** `{current_price:.4f}`\n\n"
            f"💰 **Lucro Realizado:** +{profit_percent:.2f}%"
        )
        _send_message(text)
        print(f"✅ Notificação de ALVO ATINGIDO para {trade['symbol']} enviada ao Telegram.")
    except Exception as e:
        print(f"❌ Erro no envio da notificação de alvo atingido: {e}")

def send_stop_loss_notification(trade, current_price):
    """Envia a notificação de que o STOP (Stop Loss) foi atingido."""
    try:
        loss_percent = abs((float(trade['stop_loss']) - float(trade['entry_price'])) / float(trade['entry_price'])) * 100
        text = (
            f"❌ **STOP ATINGIDO! (PERDA)** ❌\n\n"
            f"🪙 **Ativo:** {trade['symbol']}\n"
            f"📉 **Tipo:** {trade['signal_type']}\n\n"
            f"🔹 **Preço de Entrada:** `{trade['entry_price']}`\n"
            f"🚫 **Preço do Stop:** `{trade['stop_loss']}`\n"
            f"📉 **Preço Atual:** `{current_price:.4f}`\n\n"
            f"💸 **Perda Realizada:** -{loss_percent:.2f}%"
        )
        _send_message(text)
        print(f"✅ Notificação de STOP ATINGIDO para {trade['symbol']} enviada ao Telegram.")
    except Exception as e:
        print(f"❌ Erro no envio da notificação de stop atingido: {e}")

def _send_message(text):
    """Função interna para enviar a mensagem para a API do Telegram."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"  # Habilita o uso de negrito, itálico, etc.
    }
    response = requests.post(url, json=payload)
    response.raise_for_status() # Lança um erro se a requisição falhar
