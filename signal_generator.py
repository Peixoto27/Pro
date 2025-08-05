# signal_generator.py (Versão com Análise de Sentimento)
import pandas as pd
import datetime
from sentiment_analyzer import get_sentiment_score # Importa nossa nova função

# --- CHAVES DE ATIVAÇÃO ---
USAR_MTA = True
USAR_SENTIMENTO = False # Nosso novo interruptor!

def generate_signal(df_with_indicators, symbol, tendencia_macro="NEUTRA"):
    if df_with_indicators is None or len(df_with_indicators) < 2:
        return None

    # --- Filtro de Análise de Sentimento ---
    if USAR_SENTIMENTO:
        sentiment_score = get_sentiment_score(symbol)
    else:
        sentiment_score = 0 # Valor neutro se a análise estiver desligada

    latest_data = df_with_indicators.iloc[-1]
    # ... (extração de dados dos indicadores continua a mesma)
    sma_short = latest_data.get('SMA_20')
    sma_long = latest_data.get('SMA_50')
    rsi = latest_data.get('RSI')
    current_price = latest_data.get('close')
    macd_line = latest_data.get('MACD')
    macd_signal_line = latest_data.get('MACD_signal')
    current_volume = latest_data.get('volume')
    volume_sma = latest_data.get('Volume_SMA_20')

    if any(v is None for v in [sma_short, sma_long, rsi, current_price, macd_line, macd_signal_line, current_volume, volume_sma]):
        return None

    signal_type = None
    
    # --- CONDIÇÕES DE SINAL COM FILTRO DE SENTIMENTO ---
    condicao_compra = (
        sma_short > sma_long and
        (tendencia_macro == "ALTA" or tendencia_macro == "NEUTRA") and
        macd_line > macd_signal_line and
        current_volume > volume_sma and
        sentiment_score >= -0.05 # Permite um sentimento levemente negativo, mas bloqueia notícias ruins
    )

    condicao_venda = (
        sma_short < sma_long and
        (tendencia_macro == "BAIXA" or tendencia_macro == "NEUTRA") and
        macd_line < macd_signal_line and
        sentiment_score <= 0.1 # Permite um sentimento levemente positivo, mas bloqueia euforia
    )

    if condicao_compra:
        signal_type = "COMPRA"
    elif condicao_venda:
        signal_type = "VENDA"

    if signal_type:
        # ... (cálculo de confiança e criação do dicionário continuam os mesmos)
        confianca_rsi = (70 - rsi) if signal_type == "COMPRA" else (rsi - 30)
        confianca_macd = abs(macd_line - macd_signal_line) * 10
        score_rsi = min(max(confianca_rsi * 2.5, 0), 100)
        score_macd = min(max(confianca_macd, 0), 100)
        # Adicionamos o sentimento ao cálculo de confiança!
        score_sentimento = (sentiment_score + 1) * 50 # Mapeia -1 a 1 para 0 a 100
        confidence_score = (score_rsi + score_macd + score_sentimento) / 3 # Média de 3 fatores

        if confidence_score > 65:
            # ... (código para criar o dicionário do sinal)
            risk_reward_ratio = 2.0
            if signal_type == "COMPRA":
                stop_loss = current_price * 0.98
                target_price = current_price + (current_price - stop_loss) * risk_reward_ratio
            else: # VENDA
                stop_loss = current_price * 1.02
                target_price = current_price - (stop_loss - current_price) * risk_reward_ratio
            expected_profit_percent = abs((target_price - current_price) / current_price) * 100
            signal_dict = {
                "symbol": symbol, "signal_type": signal_type, "entry_price": f"{current_price:.4f}",
                "target_price": f"{target_price:.4f}", "stop_loss": f"{stop_loss:.4f}",
                "risk_reward": f"1:{risk_reward_ratio}", "confidence_score": f"{confidence_score:.1f}",
                "expected_profit_percent": f"{expected_profit_percent:.2f}",
                "expected_profit_usdt": f"{(expected_profit_percent/100 * 1000):.2f} (em lote de 1000 USDT)",
                "news_summary": f"Sentimento do Mercado: {sentiment_score:.2f}",
                "strategy": "Confluência Total (MTA+SMA+MACD+Vol+Sent.)", "timeframe": "1 Hora",
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return signal_dict

    return None
