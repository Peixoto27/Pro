import requests

BOT_TOKEN = "7360602779:AAFIpncv7fkXaEX5PdWdEAUBb7NQ9SeA-F0"
CHAT_ID = "@botsinaistop"  # Envia diretamente para o canal público

def send_signal_notification(signal):
    try:
        text = (
            f"📢 Novo sinal detectado para {signal['symbol']}\n"
            f"🎯 Entrada: {signal['entry_price']} | Alvo: {signal['target_price']} | Stop: {signal['stop_loss']}\n"
            f"📊 R:R: {signal['risk_reward']} | Confiança: {signal['confidence_score']}%\n"
            f"💰 Lucro estimado: {signal['expected_profit_percent']}% ≈ {signal['expected_profit_usdt']} USDT\n"
            f"📰 Notícia: {signal['news_summary']}\n"
            f"⏱️ Estratégia: {signal['strategy']} | {signal['timeframe']}\n"
            f"📅 Criado em: {signal['created_at']}"
        )

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": text
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("✅ Sinal enviado para o canal com sucesso.")
        else:
            print(f"❌ Erro ao enviar para o canal: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro no envio para o Telegram: {e}")
