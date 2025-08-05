import pandas as pd

def calculate_indicators(df):
    # RSI
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    # MACD
    ema_12 = df["close"].ewm(span=12, adjust=False).mean()
    ema_26 = df["close"].ewm(span=26, adjust=False).mean()
    macd_line = ema_12 - ema_26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    macd_trend = "bullish" if macd_line.iloc[-1] > signal_line.iloc[-1] else "bearish"

    # Bollinger Bands
    sma = df["close"].rolling(window=20).mean()
    std = df["close"].rolling(window=20).std()
    lower_band = sma - 2 * std
    bollinger_position = "lower breakout" if df["close"].iloc[-1] < lower_band.iloc[-1] else "inside bands"

    return {
        "RSI": round(rsi.iloc[-1], 2),
        "MACD": macd_trend,
        "BOLL": bollinger_position
    }
