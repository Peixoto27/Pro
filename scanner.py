from price_fetcher import fetch_all_data
from technical_indicators import calculate_indicators
from signal_generator import generate_signal

SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT", "TONUSDT",
    "INJUSDT", "RNDRUSDT", "ARBUSDT", "LTCUSDT", "MATICUSDT",
    "OPUSDT", "NEARUSDT", "APTUSDT", "PEPEUSDT", "SEIUSDT"
]  # 20 moedas

print("🔍 Iniciando varredura de sinais...\n")

market_data = fetch_all_data(SYMBOLS)

for symbol, df in market_data.items():
    try:
        indicators = calculate_indicators(df)
        signal = generate_signal(df, indicators)

        if signal:
            print(f"✅ Sinal encontrado para {symbol}: {signal}")
        else:
            print(f"⚪ Sem sinal relevante para {symbol}")

    except Exception as e:
        print(f"❌ Erro ao processar {symbol}: {e}")
