import time
import requests
from config import API_DELAY_SEC

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

def _sleep():
    time.sleep(API_DELAY_SEC)

def get_price_change(symbol: str):
    coin_id = SYMBOL_TO_ID.get(symbol, symbol.replace("USDT","").lower())
    url = f"{COINGECKO_BASE}/simple/price"
    params = {
        "ids": coin_id,
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    _sleep()
    if coin_id in data:
        return {
            "source": "coingecko",
            "price": float(data[coin_id]["usd"]),
            "change24h": float(data[coin_id]["usd_24h_change"])
        }
    return None

def get_ohlc(symbol: str, days: int = 1, vs_currency: str = "usd"):
    coin_id = SYMBOL_TO_ID.get(symbol, symbol.replace("USDT","").lower())
    url = f"{COINGECKO_BASE}/coins/{coin_id}/ohlc"
    params = {"vs_currency": vs_currency, "days": days}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    _sleep()
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
