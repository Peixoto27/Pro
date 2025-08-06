# technical_indicators.py (Versão com ATR)
import pandas as pd
import ta

def calculate_indicators(df):
    """Calcula todos os indicadores técnicos necessários para a estratégia."""
    try:
        # --- APROXIMAÇÃO PARA DADOS OHLC ---
        # Como a API do CoinGecko não fornece OHLC por hora facilmente,
        # usamos o 'close' para os cálculos que precisam de high/low.
        # Esta é uma simplificação funcional.
        if 'high' not in df.columns:
            df['high'] = df['close']
        if 'low' not in df.columns:
            df['low'] = df['close']

        # --- CÁLCULOS EXISTENTES ---
        df['SMA_20'] = ta.trend.sma_indicator(df['close'], window=20)
        df['SMA_50'] = ta.trend.sma_indicator(df['close'], window=50)
        df['RSI'] = ta.momentum.rsi(df['close'], window=14)
        
        macd = ta.trend.MACD(df['close'], window_slow=26, window_fast=12, window_sign=9)
        df['MACD'] = macd.macd()
        df['MACD_signal'] = macd.macd_signal()
        
        df['Volume_SMA_20'] = ta.volume.sma_volume(df['volume'], window=20)

        # --- NOVO CÁLCULO DE ATR ---
        # Adicionamos o cálculo do Average True Range (ATR) para volatilidade
        df['ATR_14'] = ta.volatility.AverageTrueRange(
            high=df['high'], 
            low=df['low'], 
            close=df['close'], 
            window=14
        ).average_true_range()

        # Remove linhas com valores NaN gerados pelos cálculos iniciais
        df = df.dropna().reset_index(drop=True)
        
        print(f"✅ Indicadores para {df.iloc[-1]['symbol']} calculados com sucesso.")
        return df

    except Exception as e:
        print(f"⚠️ Não foi possível calcular indicadores: {e}")
        return None
