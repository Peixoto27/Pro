import requests
import time
import random
from config import API_DELAY_BULK, API_DELAY_OHLC, MAX_RETRIES, BACKOFF_BASE

API_BASE = "https://api.coingecko.com/api/v3"

# Função para buscar preços em lote (bulk)
def fetch_bulk_prices(symbols):
    ids = ",".join(symbols)
    url = f"{API_BASE}/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true"
    
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            time.sleep(API_DELAY_BULK)
            return resp.json()
        except Exception as e:
            print(f"⚠️ Erro bulk: {e} (tentativa {attempt+1}/{MAX_RETRIES})")
            time.sleep(API_DELAY_BULK + random.uniform(0.5, 1.5))  # Atraso aleatório
    return {}

# Função para buscar OHLC de um ativo
def fetch_ohlc(symbol_id, days=1, interval="30m"):
    url = f"{API_BASE}/coins/{symbol_id}/ohlc?vs_currency=usd&days={days}"
    
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            time.sleep(API_DELAY_OHLC + random.uniform(0.5, 1.5))  # Atraso maior + jitter
            return resp.json()
        except Exception as e:
            print(f"⚠️ Erro OHLC {symbol_id}: {e} (tentativa {attempt+1}/{MAX_RETRIES})")
            time.sleep(API_DELAY_OHLC + random.uniform(1.0, 2.5))  # Backoff exponencial
    return []
