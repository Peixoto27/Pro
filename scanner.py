import time
from price_fetcher import fetch_price_data
from technical_indicators import calculate_indicators
from signal_model import generate_signal
from notifier import send_signal_notification

symbols = [
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT',
    'ADAUSDT', 'AVAXUSDT', 'DOTUSDT', 'LINKUSDT', 'TONUSDT',
    'INJUSDT', 'RNDRUSDT', 'ARBUSDT', 'OPUSDT', 'MATICUSDT',
    'LTCUSDT', 'TRXUSDT', 'NEARUSDT', 'ATOMUSDT', 'HBARUSDT',
    'APEUSDT', 'FTMUSDT', 'SUIUSDT', 'PEPEUSDT', 'DOGEUSDT',
    'CHZUSDT', 'AAVEUSDT', 'DYDXUSDT', 'BLURUSDT', 'UNIUSDT'
]

print("🔍 Iniciando varredura de sinais...\n")

for symbol in symbols:
    try:
        df = fetch_price_data(symbol)
        if df is None or df.empty:
            print(f"⚠️ Dados indisponíveis para {symbol}. Pulando...\n")
            continue

        indicators = calculate_indicators(df)
        signal = generate_signal(symbol, df, indicators)

        if signal:
            send_signal_notification(signal)
        else:
            print(f"ℹ️ Nenhum sinal válido para {symbol}.\n")

        time.sleep(2.5)

    except Exception as e:
        print(f"❌ Erro ao processar {symbol}: {e}\n")
