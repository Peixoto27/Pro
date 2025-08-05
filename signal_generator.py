# signal_generator.py
import pandas as pd
import datetime

def generate_signal(df_with_indicators, symbol):
    """
    Gera um dicionário de sinal de compra ou venda com base na estratégia real.
    O sinal só é retornado se a pontuação de confiança for alta.
    """
    if df_with_indicators is None or df_with_indicators.empty:
        return None

    latest_data = df_with_indicators.iloc[-1]
    
    sma_short = latest_data.get('SMA_20')
    sma_long = latest_data.get('SMA_50')
    rsi = latest_data.get('RSI')
    current_price = latest_data.get('close')

    if sma_short is None or sma_long is None or rsi is None or current_price is None:
        return None

    signal_type = None
    confidence_score = 0

    if sma_short > sma_long and rsi < 70:
        signal_type = "COMPRA"
        confidence_score = 50 + (70 - rsi) 
    elif sma_short < sma_long and rsi > 30:
        signal_type = "VENDA"
        confidence_score = 50 + (rsi - 30)

    if signal_type and confidence_score > 60:
        
        risk_reward_ratio = 2.0

        if signal_type == "COMPRA":
            stop_loss = current_price * 0.98
            target_price = current_price + (current_price - stop_loss) * risk_reward_ratio
        else: # VENDA
            stop_loss = current_price * 1.02
            target_price = current_price - (stop_loss - current_price) * risk_reward_ratio

        expected_profit_percent = abs((target_price - current_price) / current_price) * 100
        
        signal_dict = {
            "symbol": symbol,
            "signal_type": signal_type, # <-- ESTA É A LINHA QUE FALTAVA
            "entry_price": f"{current_price:.4f}",
            "target_price": f"{target_price:.4f}",
            "stop_loss": f"{stop_loss:.4f}",
            "risk_reward": f"1:{risk_reward_ratio}",
            "confidence_score": f"{confidence_score:.1f}",
            "expected_profit_percent": f"{expected_profit_percent:.2f}",
            "expected_profit_usdt": f"{(expected_profit_percent/100 * 1000):.2f} (em lote de 1000 USDT)",
            "news_summary": "Análise técnica baseada em indicadores.",
            "strategy": "Cruzamento de Médias Móveis com RSI",
            "timeframe": "1 Hora",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return signal_dict

    return None
