# mta_analyzer.py
from price_fetcher import get_coingecko_data
import ta

# Usamos uma média móvel de 50 períodos no gráfico de 4h para definir a tendência
MACRO_TREND_SMA = 50

def get_macro_trend(symbol):
    """
    Analisa o timeframe de 4 horas para determinar a tendência principal.
    Retorna 'ALTA', 'BAIXA' ou 'NEUTRA'.
    """
    # Para calcular uma SMA de 50, precisamos de 50 períodos de 4h. 50 * 4h = 200h = ~9 dias.
    # Buscamos 10 dias para ter uma margem de segurança.
    df_4h = get_coingecko_data(symbol, days=10, interval='4h')

    if df_4h is None or len(df_4h) < MACRO_TREND_SMA:
        print(f"⚠️ Dados insuficientes no timeframe de 4h para {symbol}. Tendência considerada NEUTRA.")
        return "NEUTRA"

    # Calcula a Média Móvel Simples de 50 períodos
    df_4h['SMA_50'] = ta.trend.SMAIndicator(close=df_4h['close'], window=MACRO_TREND_SMA).sma_indicator()
    
    # Pega o último preço e a última média móvel
    ultimo_preco = df_4h['close'].iloc[-1]
    ultima_sma = df_4h['SMA_50'].iloc[-1]

    if ultimo_preco > ultima_sma:
        print(f"📈 Tendência MACRO para {symbol} é de ALTA.")
        return "ALTA"
    elif ultimo_preco < ultima_sma:
        print(f"📉 Tendência MACRO para {symbol} é de BAIXA.")
        return "BAIXA"
    else:
        return "NEUTRA"
