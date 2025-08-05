# technical_indicators.py
import pandas as pd
import ta

def calculate_indicators(df):
    """Calcula os indicadores técnicos necessários a partir de um DataFrame."""
    if df.empty or 'close' not in df.columns:
        print("⚠️ DataFrame vazio ou sem coluna 'close'. Não é possível calcular indicadores.")
        return None
    
    try:
        # Adiciona todos os indicadores técnicos que você precisa
        df['RSI'] = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
        
        # Exemplo: Adicionando Médias Móveis
        df['SMA_20'] = ta.trend.SMAIndicator(close=df['close'], window=20).sma_indicator()
        df['SMA_50'] = ta.trend.SMAIndicator(close=df['close'], window=50).sma_indicator()

        # Exemplo: Adicionando Bandas de Bollinger
        bollinger = ta.volatility.BollingerBands(close=df['close'], window=20, window_dev=2)
        df['BB_high'] = bollinger.bollinger_hband()
        df['BB_low'] = bollinger.bollinger_lband()

        # Retorna o DataFrame com os novos indicadores
        return df.dropna() # Remove linhas com NaN após o cálculo dos indicadores
    
    except Exception as e:
        print(f"❌ Erro ao calcular indicadores: {e}")
        return None
