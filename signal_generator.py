# signal_generator.py (Versão com Confluência de Sinais)
import pandas as pd
import datetime

def generate_signal(df_with_indicators, symbol, tendencia_macro="NEUTRA"):
    if df_with_indicators is None or len(df_with_indicators) < 2:
        return None

    latest_data = df_with_indicators.iloc[-1]
    
    # --- Extrai todos os dados necessários ---
    sma_short = latest_data.get('SMA_20')
    sma_long = latest_data.get('SMA_50')
    rsi = latest_data.get('RSI')
    current_price = latest_data.get('close')
    # Novos dados
    macd_line = latest_data.get('MACD')
    macd_signal_line = latest_data.get('MACD_signal')
    current_volume = latest_data.get('volume')
    volume_sma = latest_data.get('Volume_SMA_20')

    if any(v is None for v in [sma_short, sma_long, rsi, current_price, macd_line, macd_signal_line, current_volume, volume_sma]):
        return None

    signal_type = None
    
    # --- NOVAS CONDIÇÕES DE SINAL (CONFLUÊNCIA) ---
    # Condição de COMPRA:
    # 1. Cruzamento de médias (SMA20 > SMA50)
    # 2. Alinhado com a tendência macro (MTA)
    # 3. MACD está acima da sua linha de sinal (confirmação de momentum de alta)
    # 4. Volume atual é maior que a média (confirmação de força)
    condicao_compra = (
        sma_short > sma_long and
        (tendencia_macro == "ALTA" or tendencia_macro == "NEUTRA") and
        macd_line > macd_signal_line and
        current_volume > volume_sma
    )

    # Condição de VENDA:
    # 1. Cruzamento de médias (SMA20 < SMA50)
    # 2. Alinhado com a tendência macro (MTA)
    # 3. MACD está abaixo da sua linha de sinal (confirmação de momentum de baixa)
    condicao_venda = (
        sma_short < sma_long and
        (tendencia_macro == "BAIXA" or tendencia_macro == "NEUTRA") and
        macd_line < macd_signal_line
    )

    if condicao_compra:
        signal_type = "COMPRA"
    elif condicao_venda:
        signal_type = "VENDA"

    if signal_type:
        # --- CÁLCULO DE CONFIANÇA REFINADO ---
        # A confiança agora é uma média de múltiplas "sub-pontuações"
        confianca_rsi = (70 - rsi) if signal_type == "COMPRA" else (rsi - 30)
        confianca_macd = abs(macd_line - macd_signal_line) * 10 # Distância do MACD
        
        # Normaliza as pontuações para uma escala de 0 a 100
        score_rsi = min(max(confianca_rsi * 2.5, 0), 100) # Mapeia 0-40 para 0-100
        score_macd = min(max(confianca_macd, 0), 100)
        
        confidence_score = (score_rsi + score_macd) / 2 # Média das confianças

        if confidence_score > 65: # Aumentamos um pouco o limiar devido à maior precisão
            # ... (o resto do código para criar o dicionário do sinal continua o mesmo)
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
                "news_summary": "Análise técnica baseada em indicadores.",
                "strategy": "Confluência (MTA + SMA + MACD + Volume)", "timeframe": "1 Hora",
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return signal_dict

    return None
