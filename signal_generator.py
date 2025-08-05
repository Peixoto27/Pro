# signal_generator.py (com Análise de Múltiplos Timeframes)
import pandas as pd
import datetime
from mta_analyzer import get_macro_trend # Importa nossa nova função

# --- CHAVE DE ATIVAÇÃO ---
# Mude para False para desligar a análise de múltiplos timeframes e voltar ao comportamento original
USAR_MTA = True

def generate_signal(df_with_indicators, symbol):
    if df_with_indicators is None or df_with_indicators.empty:
        return None

    # --- Filtro de Análise de Múltiplos Timeframes (MTA) ---
    if USAR_MTA:
        tendencia_macro = get_macro_trend(symbol)
    else:
        tendencia_macro = "NEUTRA" # Se desligado, permite qualquer trade

    latest_data = df_with_indicators.iloc[-1]
    sma_short = latest_data.get('SMA_20')
    sma_long = latest_data.get('SMA_50')
    rsi = latest_data.get('RSI')
    current_price = latest_data.get('close')

    if any(v is None for v in [sma_short, sma_long, rsi, current_price]):
        return None

    signal_type = None
    confidence_score = 0

    # Condição de COMPRA: só gera sinal se a tendência macro for de ALTA ou NEUTRA
    if sma_short > sma_long and rsi < 70 and (tendencia_macro == "ALTA" or tendencia_macro == "NEUTRA"):
        signal_type = "COMPRA"
        confidence_score = 50 + (70 - rsi)
    
    # Condição de VENDA: só gera sinal se a tendência macro for de BAIXA ou NEUTRA
    elif sma_short < sma_long and rsi > 30 and (tendencia_macro == "BAIXA" or tendencia_macro == "NEUTRA"):
        signal_type = "VENDA"
        confidence_score = 50 + (rsi - 30)

    if signal_type and confidence_score > 60:
        # ... (o resto do código para criar o dicionário do sinal continua exatamente o mesmo)
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
            "strategy": "Cruzamento de Médias Móveis com RSI + Filtro MTA", "timeframe": "1 Hora",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return signal_dict

    return None
