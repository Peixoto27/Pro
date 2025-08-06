# signal_generator.py (Versão Final com Stop Dinâmico ATR)
import pandas as pd
import datetime
from sentiment_analyzer import get_sentiment_score

# --- CHAVES DE ATIVAÇÃO ---
USAR_MTA = True
USAR_SENTIMENTO = True
USAR_STOP_DINAMICO_ATR = True # <<< NOSSA NOVA CHAVE!

def generate_signal(df_with_indicators, symbol, tendencia_macro="NEUTRA"):
    if df_with_indicators is None or len(df_with_indicators) < 2:
        return None

    if USAR_SENTIMENTO:
        sentiment_score = get_sentiment_score(symbol)
    else:
        sentiment_score = 0

    latest_data = df_with_indicators.iloc[-1]
    
    # Extrai todos os valores necessários, incluindo o novo ATR
    current_price = latest_data.get('close')
    atr_value = latest_data.get('ATR_14') # Pega o valor do ATR
    # ... (outros indicadores)
    sma_short = latest_data.get('SMA_20')
    sma_long = latest_data.get('SMA_50')
    rsi = latest_data.get('RSI')
    macd_line = latest_data.get('MACD')
    macd_signal_line = latest_data.get('MACD_signal')
    current_volume = latest_data.get('volume')
    volume_sma = latest_data.get('Volume_SMA_20')

    # Verifica se todos os dados necessários existem
    if any(v is None for v in [current_price, atr_value, sma_short, sma_long, rsi, macd_line, macd_signal_line, current_volume, volume_sma]):
        return None

    signal_type = None
    
    condicao_compra = (
        sma_short > sma_long and
        (tendencia_macro == "ALTA" or tendencia_macro == "NEUTRA") and
        macd_line > macd_signal_line and
        current_volume > volume_sma and
        sentiment_score >= -0.05
    )

    condicao_venda = (
        sma_short < sma_long and
        (tendencia_macro == "BAIXA" or tendencia_macro == "NEUTRA") and
        macd_line < macd_signal_line and
        sentiment_score <= 0.1
    )

    if condicao_compra:
        signal_type = "COMPRA"
    elif condicao_venda:
        signal_type = "VENDA"

    if signal_type:
        # --- LÓGICA DE GESTÃO DE RISCO (FIXA vs. DINÂMICA) ---
        risk_reward_ratio = 2.0
        
        if USAR_STOP_DINAMICO_ATR and atr_value > 0:
            # --- GESTÃO DE RISCO DINÂMICA COM ATR ---
            multiplicador_atr_stop = 2.0 # Fator de multiplicação para o stop (ajustável)
            
            if signal_type == "COMPRA":
                stop_loss = current_price - (atr_value * multiplicador_atr_stop)
                target_price = current_price + (current_price - stop_loss) * risk_reward_ratio
            else: # VENDA
                stop_loss = current_price + (atr_value * multiplicador_atr_stop)
                target_price = current_price - (stop_loss - current_price) * risk_reward_ratio
            
            strategy_name = "Confluência Total + ATR Stop"
        else:
            # --- GESTÃO DE RISCO FIXA (Nosso método antigo como fallback) ---
            if signal_type == "COMPRA":
                stop_loss = current_price * 0.98
                target_price = current_price + (current_price - stop_loss) * risk_reward_ratio
            else: # VENDA
                stop_loss = current_price * 1.02
                target_price = current_price - (stop_loss - current_price) * risk_reward_ratio
            
            strategy_name = "Confluência Total (Stop Fixo)"

        # --- CÁLCULO DE CONFIANÇA E CRIAÇÃO DO SINAL ---
        # (O resto do código continua o mesmo)
        confianca_rsi = (70 - rsi) if signal_type == "COMPRA" else (rsi - 30)
        confianca_macd = abs(macd_line - macd_signal_line) * 10
        score_rsi = min(max(confianca_rsi * 2.5, 0), 100)
        score_macd = min(max(confianca_macd, 0), 100)
        score_sentimento = (sentiment_score + 1) * 50
        confidence_score = (score_rsi + score_macd + score_sentimento) / 3

        if confidence_score > 65:
            expected_profit_percent = abs((target_price - current_price) / current_price) * 100
            signal_dict = {
                "symbol": symbol, "signal_type": signal_type, "entry_price": f"{current_price:.4f}",
                "target_price": f"{target_price:.4f}", "stop_loss": f"{stop_loss:.4f}",
                "risk_reward": f"1:{risk_reward_ratio}", "confidence_score": f"{confidence_score:.1f}",
                "expected_profit_percent": f"{expected_profit_percent:.2f}",
                "expected_profit_usdt": f"{(expected_profit_percent/100 * 1000):.2f} (em lote de 1000 USDT)",
                "news_summary": f"Sentimento: {sentiment_score:.2f} | ATR: {atr_value:.4f}",
                "strategy": strategy_name, "timeframe": "1 Hora",
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return signal_dict

    return None
