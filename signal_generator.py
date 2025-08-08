# signal_generator.py (Versão Final com Cálculo Interno - CORRIGIDO)
import pandas as pd
import datetime
import ta

def calculate_indicators(df):
    """Função auxiliar para calcular todos os indicadores necessários."""
    df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
    df['rsi'] = ta.momentum.rsi(df['close'], window=14)
    df['macd_diff'] = ta.trend.macd_diff(df['close'], window_slow=26, window_fast=12, window_sign=9)
    df['volume_sma_20'] = ta.trend.sma_indicator(df['volume'], window=20)
    df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=14)
    return df.dropna()

# --- PARÂMETROS DA ESTRATÉGIA COM PESOS DA IA ---
PONTUACAO_MINIMA_PARA_SINAL = 85

PESO_SMA = 35
PESO_VOLUME = 30
PESO_MACD = 25
PESO_RSI = 10

# A função agora só precisa do df bruto e do symbol
def generate_signal(df, symbol):
    """
    Calcula indicadores e gera um sinal de compra usando um sistema de pontuação.
    """
    if df.empty or len(df) < 50:
        return None

    # PASSO 1: Calcular os indicadores necessários
    df_with_indicators = calculate_indicators(df.copy())

    if df_with_indicators.empty:
        return None

    # Pega os dados mais recentes já com os indicadores
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
