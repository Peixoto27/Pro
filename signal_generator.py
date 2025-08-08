# signal_generator.py (Versão Final e CORRETA)
import pandas as pd
import datetime

# --- PARÂMETROS DA ESTRATÉGIA COM PESOS DA IA ---
PONTUACAO_MINIMA_PARA_SINAL = 85

PESO_SMA = 35
PESO_VOLUME = 30
PESO_MACD = 25
PESO_RSI = 10

# A função volta a receber o df com indicadores e o symbol
def generate_signal(df_with_indicators, symbol):
    """
    Gera um sinal de compra usando um sistema de pontuação.
    Assume que o DataFrame já contém os indicadores calculados.
    """
    if df_with_indicators.empty:
        return None

    # Pega os dados mais recentes
    latest = df_with_indicators.iloc[-1]
    
    # --- INICIA O CÁLCULO DA PONTUAÇÃO ---
    confidence_score = 0
    
    if latest['close'] > latest['sma_50']:
        confidence_score += PESO_SMA
        
    if latest['volume'] > latest['volume_sma_20']:
        confidence_score += PESO_VOLUME
        
    if latest['macd_diff'] > 0:
        confidence_score += PESO_MACD
        
    if latest['rsi'] < 70:
        confidence_score += PESO_RSI

    # --- DECISÃO FINAL ---
    if confidence_score >= PONTUACAO_MINIMA_PARA_SINAL:
        entry_price = latest['close']
        stop_loss = entry_price - (2 * latest['atr'])
        target_price = entry_price + (4 * latest['atr'])
        
        signal_dict = {
            'signal_type': 'BUY',
            'symbol': symbol,
            'entry_price': f"{entry_price:.4f}",
            'target_price': f"{target_price:.4f}",
            'stop_loss': f"{stop_loss:.4f}",
            'risk_reward': "1:2.0",
            'confidence_score': f"{confidence_score}",
            'strategy': f"IA-Weighted (ATR Stop)",
            'created_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return signal_dict

    return None
