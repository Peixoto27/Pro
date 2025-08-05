def generate_signal(symbol: str, indicators: dict, price: float) -> dict:
    if not indicators or price is None:
        raise ValueError("Indicadores ou preço inválido.")

    rsi = indicators.get("rsi")
    macd = indicators.get("macd")
    macd_signal = indicators.get("macd_signal")
    ma20 = indicators.get("ma20")
    ma50 = indicators.get("ma50")

    signal = "neutro"
    score = 0

    # RSI
    if rsi < 30:
        signal = "compra"
        score += 30
    elif rsi > 70:
        signal = "venda"
        score += 30
    else:
        score += 10

    # MACD
    if macd > macd_signal:
        signal = "compra"
        score += 30
    elif macd < macd_signal:
        signal = "venda"
        score += 30
    else:
        score += 10

    # Médias móveis
    if ma20 > ma50:
        signal = "compra"
        score += 25
    elif ma20 < ma50:
        signal = "venda"
        score += 25
    else:
        score += 10

    # Ajuste para o caso em que os sinais são mistos
    if score < 60:
        signal = "neutro"

    # Definição de alvo e stop (ajustável)
    take_profit = round(price * 1.015, 4)  # 1.5%
    stop_loss = round(price * 0.985, 4)    # -1.5%

    return {
        "symbol": symbol,
        "signal": signal,
        "confidence": score,
        "price": round(price, 4),
        "take_profit": take_profit,
        "stop_loss": stop_loss
    }
