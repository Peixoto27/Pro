# signal_generator.py
import pandas as pd

def generate_signal(df_with_indicators):
    """Gera um sinal de compra ou venda com base nos indicadores."""
    if df_with_indicators is None or df_with_indicators.empty:
        return None

    # Pega a última linha de dados, que contém os valores mais recentes dos indicadores
    latest_data = df_with_indicators.iloc[-1]
    
    # --- LÓGICA DE SINAL DE EXEMPLO ---
    # Adapte esta lógica para a sua estratégia de trading.
    # Exemplo: Sinal de compra quando a média móvel curta (SMA_20) cruza para cima da longa (SMA_50)
    # e o RSI está abaixo de 70 (não sobrecomprado).
    
    sma_short = latest_data.get('SMA_20')
    sma_long = latest_data.get('SMA_50')
    rsi = latest_data.get('RSI')

    if sma_short is None or sma_long is None or rsi is None:
        print("⚠️ Colunas de indicadores necessárias (SMA_20, SMA_50, RSI) não encontradas.")
        return None

    # Lógica de Compra
    if sma_short > sma_long and rsi < 70:
        return "COMPRA (Cruzamento de Média Móvel)"

    # Lógica de Venda
    if sma_short < sma_long and rsi > 30:
        return "VENDA (Cruzamento de Média Móvel)"

    # Se nenhuma condição for atendida
    return None
