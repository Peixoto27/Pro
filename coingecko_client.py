import requests
import time
import random
from config import API_DELAY_BULK, API_DELAY_OHLC, MAX_RETRIES, BACKOFF_BASE

# IDs no CoinGecko para cada par
SYMBOL_TO_ID = {
    "BTCUSDT": "bitcoin",
    "ETHUSDT": "ethereum",
    "BNBUSDT": "binancecoin",
    "XRPUSDT": "ripple",
    "ADAUSDT": "cardano",
    "SOLUSDT": "solana",
    "DOGEUSDT": "dogecoin",
    "MATICUSDT": "matic-network",
    "DOTUSDT": "polkadot",
    "LTCUSDT": "litecoin",
    "LINKUSDT": "chainlink",
    "BCHUSDT": "bitcoin-cash",
    "ATOMUSDT": "cosmos",
    "AVAXUSDT": "avalanche-2",
    "XLMUSDT": "stellar",
    "FILUSDT": "filecoin",
    "TRXUSDT": "tron",
    "APTUSDT": "aptos",
    "INJUSDT": "injective-protocol",
    "ARBUSDT": "arbitrum"
}

def fetch_bulk_prices(symbol_ids):
    """Busca preços atuais em lote"""
    ids = ",".join(symbol_ids)
    url = f"https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": ids, "vs_currencies": "usd"}
    time.sleep(API_DELAY_BULK)
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()

def fetch_ohlc(symbol_id, days=1):
    """Busca OHLC com retry e tratamento de rate limit"""
    url = f"https://api.coingecko.com/api/v3/coins/{symbol_id}/ohlc"
    params = {"vs_currency": "usd", "days": days}
    delay = API_DELAY_OHLC

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, params=params, timeout=20)
            if resp.status_code == 200:
                time.sleep(API_DELAY_OHLC + random.uniform(0.5, 1.5))
                return resp.json()

            if resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                wait = float(retry_after) if retry_after else delay
                wait += random.uniform(0.5, 2.0)
                print(f"⚠️ 429 {symbol_id}: aguardando {round(wait, 1)}s (tentativa {attempt}/{MAX_RETRIES})")
                time.sleep(wait)
                delay = min(delay * BACKOFF_BASE, 60)
                continue

            if 500 <= resp.status_code < 600:
                wait = delay + random.uniform(0.5, 2.0)
                print(f"⚠️ {resp.status_code} {symbol_id}: aguardando {round(wait, 1)}s")
                time.sleep(wait)
                delay = min(delay * BACKOFF_BASE, 60)
                continue

            resp.raise_for_status()

        except requests.RequestException as e:
            wait = delay + random.uniform(0.5, 2.0)
            print(f"⚠️ Erro {symbol_id}: {e} (tentativa {attempt}/{MAX_RETRIES}). Aguardando {round(wait, 1)}s")
            time.sleep(wait)
            delay = min(delay * BACKOFF_BASE, 60)

    return []
