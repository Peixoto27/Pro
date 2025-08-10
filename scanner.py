# -*- coding: utf-8 -*-
import json
import time
from coingecko_client import get_price_change, get_ohlc
from config import API_DELAY_SEC

SYMBOLS = [
    "BTCUSDT","ETHUSDT","BNBUSDT","XRPUSDT","ADAUSDT",
    "SOLUSDT","DOGEUSDT","MATICUSDT","DOTUSDT","LTCUSDT"
]

def collect_symbol(symbol):
    price = get_price_change(symbol)
    ohlc  = get_ohlc(symbol, days=1, vs_currency="usd")
    return {"symbol": symbol, "price": price, "ohlc": ohlc}

def main():
    all_data = []
    for s in SYMBOLS:
        print(f"📊 Coletando {s}...")
        try:
            d = collect_symbol(s)
            if d["price"] and d["ohlc"]:
                all_data.append(d)
                print(f"✅ {s} OK | candles={len(d['ohlc'])}")
            else:
                print(f"❌ Dados insuficientes para {s}")
        except Exception as e:
            print(f"⚠️ Erro {s}: {e}")
        time.sleep(API_DELAY_SEC)

    with open("data_raw.json","w") as f:
        json.dump(all_data, f, indent=2)
    print(f"💾 Salvo data_raw.json ({len(all_data)} ativos)")

if __name__ == "__main__":
    main()
