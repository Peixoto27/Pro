import requests
import pandas as pd
import time
from datetime import datetime

COINGECKO_API_KEY = "CG-SnFGo9ozwT62MLbBiuuzpxxh"
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

HEADERS = {
    "accept": "application/json",
    "x-cg-demo-api-key": COINGECKO_API_KEY
}

SYMBOL_TO_ID = {
    "BTCUSDT": "bitcoin",
    "ETHUSDT": "ethereum",
    "BNBUSDT": "binancecoin",
    "SOLUSDT": "solana",
    "XRPUSDT": "ripple",
    "ADAUSDT": "cardano",
    "AVAXUSDT": "avalanche-2",
    "DOTUSDT": "polkadot",
    "LINKUSDT": "chainlink",
    "TONUSDT": "the-open-network",
    "INJUSDT": "injective-protocol",
    "RNDRUSDT": "render-token",
    "ARBUSDT": "arbitrum",
    "LTCUSDT": "litecoin",
    "MATICUSDT": "matic-network",
    "OPUSDT": "optimism",
    "NEARUSDT": "near",
    "APTUSDT": "aptos",
    "PEPEUSDT": "pepe",
    "SEIUSDT": "sei-network"
}

def fetch_historical_data_coingecko(symbol, days=2):
    if symbol not in SYMBOL_TO_ID:
        print(f"❌ Moeda não reconhecida: {symbol}")
        return None

    coin_id = SYMBOL_TO_ID[symbol]
    url = f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": "hourly"
    }

    try:
        response = requests.get(url, params=params, headers=HEADERS)
        if response.status_code == 401:
            print(f"⚠️ Erro CoinGecko {symbol}: 401 (API key inválida ou ausente)")
            return None
        if response.status_code == 429:
            print(f"⚠️ Erro CoinGecko {symbol}: 429 (Limite atingido)")
            return None
        response.raise_for_status()
        data = response.json()

        if "prices" not in data or "total_volumes" not in data:
            print(f"⚠️ Dados incompletos para {symbol}")
            return None

        prices = data["prices"]
        volumes = data["total_volumes"]

        df = pd.DataFrame(prices, columns=["timestamp", "close"])
        df["volume"] = [v[1] for v in volumes]
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

        df["close"] = pd.to_numeric(df["close"], errors="coerce")
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")

        df = df.dropna().reset_index(drop=True)
        df = df.set_index("timestamp").resample("1h").mean().ffill().dropna().reset_index()

        return df

    except Exception as e:
        print(f"❌ Erro ao buscar dados de {symbol}: {e}")
        return None


def fetch_all_data(symbols):
    all_data = {}
    for symbol in symbols:
        print(f"🔁 Buscando dados de {symbol}...")
        df = fetch_historical_data_coingecko(symbol)
        if df is not None:
            all_data[symbol] = df
        else:
            print(f"⚠️ Dados indisponíveis para {symbol}. Pulando...")
        time.sleep(2.5)  # Delay entre chamadas
    return all_data
