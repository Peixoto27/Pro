# technical_indicators.py (Versão com a correção do Volume SMA)
import pandas as pd
import ta

def calculate_indicators(df):
    """Calcula todos os indicadores técnicos necessários para a estratégia."""
    try:
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
        
        # --- CORREÇÃO APLICADA AQUI ---
        # O nome da função estava incorreto. A forma correta é usar o sma_indicator
        # diretamente na coluna de volume.
        df['Volume_SMA_20'] = ta.trend.sma_indicator(df['volume'], window=20)

        # --- NOVO CÁLCULO DE ATR ---
        df['ATR_14'] = ta.volatility.AverageTrueRange(
            high=df['high'], 
            low=df['low'], 
            close=df['close'], 
            window=14
        ).average_true_range()

        df = df.dropna().reset_index(drop=True)
        
        # Adicionei o 'symbol' ao DataFrame para a mensagem de sucesso ser mais clara
        # Esta parte é opcional, mas ajuda na depuração.
        # Se o seu df já tiver o símbolo, pode ignorar.
        # df['symbol'] = symbol 
        
        print(f"✅ Indicadores calculados com sucesso.")
        return df

    except Exception as e:
        print(f"⚠️ Não foi possível calcular indicadores: {e}")
        return None
