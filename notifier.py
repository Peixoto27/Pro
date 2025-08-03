import requests

WEBHOOK_URL = "https://your-webhook-url.com"  # Coloque seu Webhook real aqui

def send_signal_notification(signal):
    try:
        text = (
            f"📢 Novo sinal detectado para {signal['symbol']}\n"
            f"🎯 Entrada: {signal['entry_price']} | Alvo: {signal['target_price']} | Stop: {signal['stop_loss']}\n"
            f"📊 R:R: {signal['risk_reward']} | Confiança: {signal['confidence_score']}%\n"
            f"📰 Notícia: {signal['news_summary']}\n"
            f"⏱️ Estratégia: {signal['strategy']} | {signal['timeframe']}\n"
        )
        payload = {"content": text}
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code in [200, 204]:
            print("🔔 Notificação enviada com sucesso.")
        else:
            print(f"Erro ao notificar: {response.status_code}")
    except Exception as e:
        print(f"Erro no envio da notificação: {e}")
