# -*- coding: utf-8 -*-
import time
import requests
from config import API_DELAY_SEC, MAX_RETRIES, BACKOFF_BASE, BATCH_SIZE

COINGECKO_BASE = "https://api.coingecko.com/api/v3"

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
}

session = requests.Session()
session.headers.update({"User-Agent": "CryptonSignals/1.0 (+railway)"})


def _request(url, params, sleep_after=True):
    """Request com retry/backoff para 429 e 5xx."""
    delay = 1.0
    for attempt in range(MAX_RETRIES):
        try:
            r = session.get(url, params=params, timeout=30)
            if r.status_code == 200:
                if sleep_after:
                    time.sleep(API_DELAY_SEC)
                return r.json()
            if r.status_code == 429 or 500 <= r.status_code < 600:
                # backoff exponencial
                time.sleep(delay)
                delay *= BACKOFF_BASE
                continue
            r.raise_for_status()
        except requests.RequestException:
            time.sleep(delay)
            delay *= BACKOFF_BASE
    raise requests.HTTPError(f"Falha após {MAX_RETRIES} tentativas: {url}")


def get_prices_change_bulk(symbols):
    """
    Retorna dict {symbol: {price, change24h, source}} usando 1..N chamadas (em lotes).
    """
    # 1) converte symbols -> ids
    ids = [SYMBOL_TO_ID.get(s, s.replace("USDT","").lower()) for s in symbols]

    results = {}
    for i in range(0, len(ids), BATCH_SIZE):
        chunk_ids = ids[i:i+BATCH_SIZE]
        url = f"{COINGECKO_BASE}/simple/price"
        params = {
            "ids": ",".join(chunk_ids),
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }
        data = _request(url, params, sleep_after=False)  # sem sleep aqui
        # pequeno espaçamento entre lotes
        time.sleep(API_DELAY_SEC)

        # volta para symbols na mesma posição
        for j, coin_id in enumerate(chunk_ids, start=i):
            sym = symbols[j]
            if coin_id in data:
                results[sym] = {
                    "source": "coingecko",
                    "price": float(data[coin_id]["usd"]),
                    "change24h": float(data[coin_id].get("usd_24h_change", 0.0))
                }
    return results


def get_ohlc(symbol: str, days: int = 1, vs_currency: str = "usd"):
    """OHLC com retry/backoff (chamada individual – mantém delay)."""
    coin_id = SYMBOL_TO_ID.get(symbol, symbol.replace("USDT","").lower())
    url = f"{COINGECKO_BASE}/coins/{coin_id}/ohlc"
    params = {"vs_currency": vs_currency, "days": days}
    data = _request(url, params, sleep_after=True)
    candles = []
    for row in data:
        ts, o, h, l, c = row
        candles.append({
            "timestamp": int(ts/1000),
            "open": float(o),
            "high": float(h),
            "low": float(l),
            "close": float(c),
        })
    return candles
