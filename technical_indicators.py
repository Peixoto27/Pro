def analyze_indicators(df):
    close = df['close']
    rsi = compute_rsi(close)
    macd_signal = compute_macd(close)
    bollinger = compute_bollinger_bands(close)

    return {
        "RSI": rsi,
        "MACD": macd_signal,
        "BOLL": bollinger
    }

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi.iloc[-1], 2)

def compute_macd(series, short=12, long=26, signal=9):
    ema_short = series.ewm(span=short, adjust=False).mean()
    ema_long = series.ewm(span=long, adjust=False).mean()
    macd = ema_short - ema_long
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return "bullish" if macd.iloc[-1] > signal_line.iloc[-1] else "bearish"

def compute_bollinger_bands(series, period=20):
    sma = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper = sma + 2 * std
    lower = sma - 2 * std
    if series.iloc[-1] < lower.iloc[-1]:
        return "lower breakout"
    elif series.iloc[-1] > upper.iloc[-1]:
        return "upper breakout"
    else:
        return "inside bands"
