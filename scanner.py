# scanner.py (versão corrigida com integração de sentimento e fallback)

import ccxt
import pandas as pd
import time
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
from ta.volatility import BollingerBands

# --- Import do analisador de sentimento com fallback ---
try:
    from sentiment_analyzer import get_sentiment_score
except Exception as e:
    print(f"[SENTIMENT] Falha ao importar sentiment_analyzer ({e}). Usando sentimento neutro.")
    def get_sentiment_score(symbol: str) -> float:
        return 0.0

# --- Configurações ---
EXCHANGE = ccxt.binance()
SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT",
    "DOGEUSDT", "SOLUSDT", "MATICUSDT", "LTCUSDT", "TRXUSDT",
    "SHIBUSDT", "AVAXUSDT", "NEARUSDT", "APTUSDT", "PEPEUSDT",
    "SUIUSDT", "OPUSDT", "INJUSDT", "SEIUSDT", "TONUSDT"
]
TIMEFRAME = "1h"
LIMIT = 100

def fetch_data(symbol):
    """Baixa dados OHLCV da Binance e retorna DataFrame formatado."""
    try:
        ohlcv = EXCHANGE.fetch_ohlcv(symbol, TIMEFRAME, limit=LIMIT)
        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df
    except Exception as e:
        print(f"⚠️ Erro ao buscar dados para {symbol}: {e}")
        return None

def analyze_indicators(df):
    """Calcula indicadores técnicos e retorna sinais."""
    try:
        df["rsi"] = RSIIndicator(df["close"], window=14).rsi()
        macd = MACD(df["close"])
        df["macd"] = macd.macd()
        df["macd_signal"] = macd.macd_signal()
        ema = EMAIndicator(df["close"], window=50)
        df["ema50"] = ema.ema_indicator()
        bb = BollingerBands(df["close"], window=20, window_dev=2)
        df["bb_high"] = bb.bollinger_hband()
        df["bb_low"] = bb.bollinger_lband()
        return df
    except Exception as e:
        print(f"⚠️ Erro ao calcular indicadores: {e}")
        return df

def generate_signal(df, symbol):
    """Gera sinal de trade baseado nos indicadores e sentimento."""
    try:
        last_row = df.iloc[-1]
        rsi = last_row["rsi"]
        macd_val = last_row["macd"]
        macd_signal = last_row["macd_signal"]
        price = last_row["close"]
        ema50 = last_row["ema50"]

        # Calcula sentimento
        sentiment_score = get_sentiment_score(symbol)
        
        # Lógica simples de exemplo (pode ser evoluída com IA)
        if rsi < 30 and macd_val > macd_signal and price > ema50:
            decision = "BUY"
        elif rsi > 70 and macd_val < macd_signal and price < ema50:
            decision = "SELL"
        else:
            decision = "HOLD"

        return {
            "symbol": symbol,
            "price": price,
            "rsi": rsi,
            "macd": macd_val,
            "macd_signal": macd_signal,
            "ema50": ema50,
            "sentiment": sentiment_score,
            "signal": decision
        }
    except Exception as e:
        print(f"⚠️ Erro ao gerar sinal para {symbol}: {e}")
        return None

def main():
    print("[MAIN] Iniciando scanner...")
    all_signals = []
    
    for symbol in SYMBOLS:
        print(f"\n🪙 Analisando {symbol}...")
        df = fetch_data(symbol)
        if df is None:
            continue
        df = analyze_indicators(df)
        signal_data = generate_signal(df, symbol)
        if signal_data:
            print(f"✅ Indicadores calculados com sucesso. Sinal: {signal_data['signal']} | Sentimento: {signal_data['sentiment']:.2f}")
            all_signals.append(signal_data)
        time.sleep(1.5)  # Delay para evitar limite da API
    
    print("\n📊 Sinais gerados:")
    for sig in all_signals:
        print(sig)

if __name__ == "__main__":
    main()
