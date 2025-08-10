import time
import requests
import json
import os

# Lista de pares para analisar
SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT",
    "SOLUSDT", "DOGEUSDT", "MATICUSDT", "DOTUSDT", "LTCUSDT"
]

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
BINANCE_URL = "https://api.binance.com/api/v3/ticker/24hr"

OUTPUT_FILE = "signals.json"

def get_from_coingecko(symbol):
    """Busca preço no CoinGecko."""
    try:
        coin_id = symbol.replace("USDT", "").lower()
        params = {
            "ids": coin_id,
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }
        r = requests.get(COINGECKO_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        if coin_id in data:
            return {
                "price": data[coin_id]["usd"],
                "change24h": data[coin_id]["usd_24h_change"]
            }
    except Exception as e:
        print(f"⚠️ Erro CoinGecko {symbol}: {e}")
    return None

def get_from_binance(symbol):
    """Busca preço na Binance."""
    try:
        params = {"symbol": symbol}
        r = requests.get(BINANCE_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        return {
            "price": float(data["lastPrice"]),
            "change24h": float(data["priceChangePercent"])
        }
    except Exception as e:
        print(f"⚠️ Erro Binance {symbol}: {e}")
    return None

def main():
    signals = []
    
    for symbol in SYMBOLS:
        print(f"📊 Analisando {symbol}...")
        
        # 1. CoinGecko primeiro
        result = get_from_coingecko(symbol)
        
        # 2. Fallback Binance se CoinGecko falhar
        if not result:
            print(f"🔁 CoinGecko indisponível para {symbol}. Tentando Binance...")
            result = get_from_binance(symbol)
        
        if result:
            signals.append({
                "symbol": symbol,
                "price": result["price"],
                "change24h": result["change24h"],
                "timestamp": time.time()
            })
            print(f"✅ {symbol} -> Preço: {result['price']}, Variação 24h: {result['change24h']}%")
        else:
            print(f"❌ Não foi possível obter dados para {symbol}")
        
        # Delay para evitar bloqueios
        time.sleep(2.5)

    # Salva sinais
    with open(OUTPUT_FILE, "w") as f:
        json.dump(signals, f, indent=4)

    print(f"\n💾 {len(signals)} sinais salvos em {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
