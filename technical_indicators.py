import pandas as pd
import ta

def calculate_indicators(df):
    if df.empty or len(df) < 50:
        print("⚠️ DataFrame insuficiente para calcular todos os indicadores.")
        return pd.DataFrame() # Retorna um DataFrame vazio se não houver dados suficientes

    try:
        # Faz uma cópia para evitar avisos de SettingWithCopyWarning
        df_indicators = df.copy()

        # Calcula todos os indicadores que nossa estratégia precisa
        df_indicators["sma_50"] = ta.trend.sma_indicator(df_indicators["close"], window=50)
        df_indicators["rsi"] = ta.momentum.rsi(df_indicators["close"], window=14)
        df_indicators["macd_diff"] = ta.trend.macd_diff(df_indicators["close"], window_slow=26, window_fast=12, window_sign=9)
        df_indicators["volume_sma_20"] = ta.trend.sma_indicator(df_indicators["volume"], window=20)
        
        # ATR removido pois a API não fornece high/low
        
        # Remove linhas com valores NaN que são criados no início do cálculo dos indicadores
        return df_indicators.dropna()

    except Exception as e:
        print(f"❌ Erro ao calcular indicadores: {e}")
        return pd.DataFrame()

