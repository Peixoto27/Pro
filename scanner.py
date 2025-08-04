import time
from price_fetcher import fetch_price_data
from signal_model import analisar_sinal
from notifier import send_signal_notification

symbols = [
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 'ADAUSDT',
    'AVAXUSDT', 'DOTUSDT', 'LINKUSDT', 'TONUSDT', 'INJUSDT', 'RNDRUSDT', 'ARBUSDT'
]

print("🔍 Iniciando varredura de sinais...\n")

for symbol in symbols:
    try:
        dados = fetch_price_data(symbol)
        if not dados:
            print(f"⚠️ Dados indisponíveis para {symbol}. Pulando...\n")
            continue

        sinal = analisar_sinal(symbol, dados)
        if sinal:
            send_signal_notification(sinal)
        else:
            print(f"ℹ️ Nenhum sinal válido para {symbol}.\n")

        time.sleep(1.5)  # Delay entre chamadas

    except Exception as e:
        print(f"❌ Erro ao processar {symbol}: {e}\n")
