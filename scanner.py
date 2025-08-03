import ccxt
import pandas as pd
from technical_indicators import analyze_indicators
from signal_model import generate_signal

PAIRS = [
    'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT',
    'ADA/USDT', 'AVAX/USDT', 'DOT/USDT', 'LINK/USDT', 'TON/USDT',
    'INJ/USDT', 'RNDR/USDT', 'ARB/USDT', 'OP/USDT', 'APT/USDT',
    'LDO/USDT', 'GALA/USDT', 'FET/USDT', 'MATIC/USDT', 'NEAR/USDT'
]

TIMEFRAME = '1h'
exchange = ccxt.binance({ 'enableRateLimit': True })

def fetch_ohlcv(pair):
    try:
        data = exchange.fetch_ohlcv(pair, timeframe=TIMEFRAME, limit=100)
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f"Erro ao buscar dados de {pair}: {e}")
        return None

def scan_market():
    signals = []
    for pair in PAIRS:
        df = fetch_ohlcv(pair)
        if df is None or df.empty:
            continue
        indicators = analyze_indicators(df)
        signal = generate_signal(pair, df, indicators)
        if signal:
            signals.append(signal)
    return signals

if __name__ == "__main__":
    print("Iniciando varredura de sinais...")
    generated_signals = scan_market()
    for s in generated_signals:
        print(s)
