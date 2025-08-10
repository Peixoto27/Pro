# -*- coding: utf-8 -*-
import json
from coingecko_client import get_prices_change_bulk, get_ohlc
from config import API_DELAY_SEC

SYMBOLS = [
    "BTCUSDT","ETHUSDT","BNBUSDT","XRPUSDT","ADAUSDT",
    "SOLUSDT","DOGEUSDT","MATICUSDT","DOTUSDT","LTCUSDT"
]

def main():
    print("🧩 Coletando PREÇOS em lote (bulk)…")
    prices = get_prices_change_bulk(SYMBOLS)  # 1..N chamadas (lotes)

    all_data = []
    for s in SYMBOLS:
        print(f"📊 Coletando OHLC {s}…")
        try:
            ohlc = get_ohlc(s, days=1, vs_currency="usd")
            price = prices.get(s)
            if price and ohlc:
                all_data.append({"symbol": s, "price": price, "ohlc": ohlc})
                print(f"✅ {s} OK | candles={len(ohlc)}")
            else:
                print(f"❌ Dados insuficientes para {s}")
        except Exception as e:
            print(f"⚠️ Erro {s}: {e}")

    with open("data_raw.json","w") as f:
        json.dump(all_data, f, indent=2)
    print(f"💾 Salvo data_raw.json ({len(all_data)} ativos)")

if __name__ == "__main__":
    main()
