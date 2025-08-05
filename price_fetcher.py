# price_fetcher.py
import requests
import pandas as pd
import time
import os

# A chave "CG-..." é para o plano DEMO.
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "CG-SnFGo9ozwT62MLbBiuuzpxxh")

# --- CORREÇÃO ---
# 1. Usar a URL base da API DEMO (gratuita).
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

# 2. Usar o nome de cabeçalho correto para a API DEMO.
HEADERS = {
    "accept": "application/json",
    "x-cg-demo-api-key": COINGECKO_API_KEY
}

# Dicionário para mapear símbolos para IDs do CoinGecko
SYMBOL_TO_ID = {
    "BTCUSDT": "bitcoin", "ETHUSDT": "ethereum", "BNBUSDT": "binancecoin",
    "SOLUSDT": "solana", "XRPUSDT": "ripple", "ADAUSDT": "cardano",
    "AVAXUSDT": "avalanche-2", "DOTUSDT": "polkadot", "LINKUSDT": "chainlink",
    "TONUSDT": "the-open-network", "INJUSDT": "injective-protocol", "RNDRUSDT": "render-token",
    "ARBUSDT": "arbitrum", "LTCUSDT": "litecoin", "MATICUSDT": "matic-network",
    "OPUSDT": "optimism", "NEARUSDT": "near", "APTUSDT": "aptos",
    "PEPEUSDT": "pepe", "SEIUSDT": "sei-network"
}

def fetch_historical_data_coingecko(symbol, days=2):
    """Busca dados históricos de uma moeda específica no CoinGecko."""
    coin_id = SYMBOL_TO_ID.get(symbol)
    if not coin_id:
        print(f"❌ Moeda não reconhecida no mapeamento: {symbol}")
        return None

    url = f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days, "interval": "hourly"}

    try:
        response = requests.get(url, params=params, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

        if "prices" not in data or not data["prices"]:
            print(f"⚠️ Dados de preço indisponíveis para {symbol} na resposta da API.")
            return None

        df = pd.DataFrame(data["prices"], columns=["timestamp", "close"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        
        if "total_volumes" in data and data["total_volumes"]:
            volumes_df = pd.DataFrame(data["total_volumes"], columns=["timestamp", "volume"])
            volumes_df["timestamp"] = pd.to_datetime(volumes_df["timestamp"], unit="ms")
            volumes_df.set_index("timestamp", inplace=True)
            df = df.join(volumes_df, how="inner")

        df = df.apply(pd.to_numeric, errors="coerce").dropna()
        df = df.resample('1h').last().ffill().reset_index()

        return df

    except requests.exceptions.HTTPError as http_err:
        # Imprime a mensagem de erro da API, que é mais informativa
        print(f"⚠️ Erro HTTP para {symbol}: {http_err.response.status_code} - {http_err.response.text}")
        return None
    except Exception as e:
        print(f"❌ Erro inesperado ao buscar dados de {symbol}: {e}")
        return None

def fetch_all_data(symbols):
    """Busca dados para uma lista de símbolos com um delay entre as chamadas."""
    all_data = {}
    for symbol in symbols:
        print(f"🔁 Buscando dados de {symbol}...")
        df = fetch_historical_data_coingecko(symbol)
        if df is not None and not df.empty:
            all_data[symbol] = df
        else:
            print(f"⚠️ Dados indisponíveis para {symbol}. Pulando...")
        # O plano Demo tem um limite de requisições mais baixo, então um delay maior é mais seguro.
        time.sleep(2.5) 
    return all_data
