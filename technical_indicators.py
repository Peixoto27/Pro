# technical_indicators.py (Versão com MACD e Volume)
import pandas as pd
import ta

def calculate_indicators(df):
    """Calcula os indicadores técnicos necessários, incluindo MACD e Volume."""
    if df.empty or 'close' not in df.columns or 'volume' not in df.columns:
        print("⚠️ DataFrame vazio ou sem colunas 'close'/'volume'.")
        return None
    
    try:
        # Indicadores existentes
        df['RSI'] = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
        df['SMA_20'] = ta.trend.SMAIndicator(close=df['close'], window=20).sma_indicator()
        df['SMA_50'] = ta.trend.SMAIndicator(close=df['close'], window=50).sma_indicator()

        # --- NOVOS INDICADORES ---
        # 1. MACD (Moving Average Convergence Divergence)
        macd = ta.trend.MACD(close=df['close'], window_slow=26, window_fast=12, window_sign=9)
        df['MACD'] = macd.macd()
        df['MACD_signal'] = macd.macd_signal() # A linha de sinal do MACD

        # 2. Média Móvel do Volume
        df['Volume_SMA_20'] = ta.trend.SMAIndicator(close=df['volume'], window=20).sma_indicator()

        return df.dropna()
    
    except Exception as e:
        print(f"❌ Erro ao calcular indicadores: {e}")
        return None
