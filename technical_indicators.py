import pandas as pd
import ta

def calculate_indicators(df: pd.DataFrame) -> dict:
    if df.empty or "close" not in df.columns:
        raise ValueError("DataFrame inválido ou sem coluna 'close'.")

    indicators = {}

    # RSI
    df["rsi"] = ta.momentum.RSIIndicator(close=df["close"], window=14).rsi()
    indicators["rsi"] = df["rsi"].iloc[-1]

    # MACD
    macd = ta.trend.MACD(close=df["close"])
    indicators["macd"] = macd.macd().iloc[-1]
    indicators["macd_signal"] = macd.macd_signal().iloc[-1]

    # Médias Móveis
    df["ma20"] = ta.trend.SMAIndicator(close=df["close"], window=20).sma_indicator()
    df["ma50"] = ta.trend.SMAIndicator(close=df["close"], window=50).sma_indicator()
    indicators["ma20"] = df["ma20"].iloc[-1]
    indicators["ma50"] = df["ma50"].iloc[-1]

    # Volume Médio (caso disponível)
    if "volume" in df.columns:
        indicators["volume_avg"] = df["volume"].rolling(window=20).mean().iloc[-1]
    else:
        indicators["volume_avg"] = None

    return indicators
