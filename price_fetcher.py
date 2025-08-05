# price_fetcher.py (Versão com suporte a múltiplos timeframes)
import requests
import pandas as pd
import time
import os

COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "CG-SnFGo9ozwT62MLbBiuuzpxxh")
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
HEADERS = {"accept": "application/json", "x-cg-demo-api-key": COINGECKO_API_KEY}
SYMBOL_TO_ID = {
    "BTCUSDT": "bitcoin", "ETHUSDT": "ethereum", "BNBUSDT": "binancecoin",
    "SOLUSDT": "solana", "XRPUSDT": "ripple", "ADAUSDT": "cardano",
    "AVAXUSDT": "avalanche-2", "DOTUSDT": "polkadot", "LINKUSDT": "chainlink",
    "TONUSDT": "the-open-network", "INJUSDT": "injective-protocol", "RNDRUSDT": "render-token",
    "ARBUSDT": "arbitrum", "LTCUSDT": "litecoin", "MATICUSDT": "matic-network",
    "OPUSDT": "optimism", "NEARUSDT": "near", "APTUSDT": "aptos",
    "PEPEUSDT": "pepe", "SEIUSDT": "sei-network"
}

def get_coingecko_data(symbol, days, interval='hourly'):
    """Função genérica para buscar dados do CoinGecko."""
    coin_id = SYMBOL_TO_ID.get(symbol)
    if not coin_id:
        print(f"❌ Moeda não reconhecida: {symbol}")
        return None

    # A API do CoinGecko infere o intervalo pelo número de dias.
    # Para dados de 4h, precisamos de um período maior que 90 dias para ter granularidade.
    # No entanto, a API gratuita nos dá dados diários para > 90 dias.
    # A melhor abordagem é pegar os dados horários e reamostrá-los.
    url = f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days}

    try:
        response = requests.get(url, params=params, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

        if "prices" not in data or not data["prices"]:
            return None

        df = pd.DataFrame(data["prices"], columns=["timestamp", "close"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        
        # Reamostragem para o intervalo desejado
        if interval == '4h':
            df = df.resample('4h').last()
        else: # Padrão é 1h
            df = df.resample('1h').last()

        df = df.apply(pd.to_numeric, errors="coerce").ffill().dropna().reset_index()
        return df

    except Exception as e:
        print(f"❌ Erro ao buscar dados de {symbol}: {e}")
        return None

def fetch_all_data(symbols, days=4):
    """Busca dados para o timeframe principal (1h)."""
    all_data = {}
    print("\n🔁 Buscando dados de 1 Hora para sinais...")
    for symbol in symbols:
        df = get_coingecko_data(symbol, days, interval='1h')
        if df is not None and not df.empty:
            all_data[symbol] = df
        time.sleep(1.5) # Delay para não exceder o limite da API
    return all_data
