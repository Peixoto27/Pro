import time
from price_fetcher import fetch_price_data
from technical_indicators import calculate_indicators
from signal_model import generate_signal
from notifier import send_signal_notification

symbols = [
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 'ADAUSDT',
    'AVAXUSDT', 'DOTUSDT', 'LINKUSDT', 'TONUSDT', 'INJUSDT', 'RNDRUSDT', 'ARBUSDT'
]

print("🔍 Iniciando varredura de sinais...\n")

for symbol in symbols:
    try:
        price_data = fetch_price_data(symbol)
        if not price_data:
            print(f"⚠️ Dados indisponíveis para {symbol}. Pulando...\n")
            continue

        # Simulando DataFrame fictício apenas com preço
        import pandas as pd
        df = pd.DataFrame({
            "close": [price_data["price"]] * 100,
            "timestamp": pd.date_range(end=pd.Timestamp.utcnow(), periods=100, freq="H")
        })

        indicators = calculate_indicators(df)
        signal = generate_signal(symbol, df, indicators)

        if signal:
            send_signal_notification(signal)
            print(f"✅ Sinal enviado para {symbol} (Confiança: {signal['confidence_score']}%)\n")
        else:
            print(f"ℹ️ Nenhum sinal válido para {symbol}.\n")

        time.sleep(1.5)  # Delay entre chamadas

    except Exception as e:
        print(f"❌ Erro ao processar {symbol}: {e}\n")
