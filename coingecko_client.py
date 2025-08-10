import requests
import time
import random

API_BASE = "https://api.coingecko.com/api/v3"
MAX_RETRIES = 4

# Configurações de delay
API_DELAY_BULK = 2.5   # para coletar preços em lote
API_DELAY_OHLC = 8.0   # delay maior para OHLC, evita 429

def fetch_bulk_prices(symbols):
    """Coleta preços em lote (simple/price)"""
    ids = ",".join(symbols)
    url = f"{API_BASE}/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true"
    
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            time.sleep(API_DELAY_BULK)  # delay rápido
            return resp.json()
        except Exception as e:
            print(f"⚠️ Erro bulk: {e} (tentativa {attempt+1}/{MAX_RETRIES})")
            time.sleep(API_DELAY_BULK + random.uniform(0.5, 1.5))
    return {}

def fetch_ohlc(symbol_id, days=1, interval="30m"):
    """Coleta OHLC para um ativo"""
    url = f"{API_BASE}/coins/{symbol_id}/ohlc?vs_currency=usd&days={days}"
    
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            time.sleep(API_DELAY_OHLC + random.uniform(0.5, 1.5))  # delay maior + jitter
            return resp.json()
        except Exception as e:
            print(f"⚠️ Erro OHLC {symbol_id}: {e} (tentativa {attempt+1}/{MAX_RETRIES})")
            time.sleep(API_DELAY_OHLC + random.uniform(1.0, 2.5))
    return []

if __name__ == "__main__":
    # Teste rápido
    test_symbols = ["bitcoin", "ethereum", "binancecoin"]
    print(fetch_bulk_prices(test_symbols))
    print(fetch_ohlc("bitcoin"))
