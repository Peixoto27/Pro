# notifier.py (Versão Final e Completa)
import requests
import os

# Pega as credenciais das variáveis de ambiente para segurança
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_signal_notification(signal):
    """Envia a notificação de um NOVO sinal para o Telegram."""
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Credenciais do Telegram não configuradas. Não é possível enviar o sinal.")
        return

    try:
        # Mensagem formatada para um novo sinal
        text = (
            f"📢 **Novo Sinal: {signal['symbol']}**\n\n"
            f"📈 **Tipo:** {signal['signal_type']}\n"
            f"💰 **Entrada:** `{signal['entry_price']}`\n\n"
            f"🎯 **Alvo:** `{signal['target_price']}` (+{signal['expected_profit_percent']}%)\n"
            f"🛑 **Stop:** `{signal['stop_loss']}`\n\n"
            f"📊 **Risco/Retorno:** {signal['risk_reward']}\n"
            f"🧠 **Confiança:** {signal['confidence_score']}%\n"
            f"📰 **Info:** {signal['news_summary']}\n"
            f"⚙️ **Estratégia:** {signal['strategy']}"
        )

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "Markdown" # Habilita o uso de negrito, itálico, etc.
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"✅ Notificação de novo sinal para {signal['symbol']} enviada ao Telegram.")
        else:
            print(f"❌ Erro ao enviar sinal para o Telegram: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro crítico no envio para o Telegram: {e}")

# --- FUNÇÃO QUE ESTAVA FALTANDO ---
def send_trade_update_notification(symbol, status, trade_info):
    """Envia a notificação de ATUALIZAÇÃO de um trade (lucro/perda)."""
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Credenciais do Telegram não configuradas. Não é possível enviar a atualização.")
        return

    status_emoji = "✅" if "LUCRO" in status else "❌"
    
    try:
        # Mensagem formatada para a atualização do trade
        text = (
            f"{status_emoji} **Atualização de Trade: {symbol}**\n\n"
            f"**Status:** {status}\n\n"
            f"**Sinal Original:**\n"
            f"  - Tipo: {trade_info['signal_type']}\n"
            f"  - Entrada: `{trade_info['entry_price']}`\n"
            f"  - Alvo: `{trade_info['target_price']}`\n"
            f"  - Stop: `{trade_info['stop_loss']}`"
        )

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"✅ Notificação de atualização para {symbol} enviada ao Telegram.")
        else:
            print(f"❌ Erro ao enviar atualização para o Telegram: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro crítico no envio da atualização para o Telegram: {e}")
