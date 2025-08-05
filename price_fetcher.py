import requests
import pandas as pd
import datetime as dt

def fetch_price_data(symbol):
    try:
        end_time = int(dt.datetime.utcnow().timestamp() * 1000)
        start_time = end_time - (60 * 60 * 1000 * 24)  # 24 horas

        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&startTime={start_time}&endTime={end_time}"
        res = requests.get(url, timeout=10)
        
        if res.status_code == 200:
            raw = res.json()
            df = pd.DataFrame(raw, columns=[
                "timestamp", "open", "high", "low", "close", "volume",
                "_", "_", "_", "_", "_", "_"
            ])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
            return df[["timestamp", "open", "high", "low", "close", "volume"]]

        elif res.status_code == 451 or res.status_code == 429:
            print(f"🔁 Binance bloqueada para {symbol}. Usando CoinGecko...")

    except Exception as e:
        print(f"❌ Erro Binance para {symbol}: {e}")

    # CoinGecko fallback
    try:
        cg_ids = {
            'BTCUSDT': 'bitcoin',
            'ETHUSDT': 'ethereum',
            'BNBUSDT': 'binancecoin',
            'SOLUSDT': 'solana',
            'XRPUSDT': 'ripple',
            'ADAUSDT': 'cardano',
            'AVAXUSDT': 'avalanche-2',
            'DOTUSDT': 'polkadot',
            'LINKUSDT': 'chainlink',
            'TONUSDT': 'toncoin',
            'INJUSDT': 'injective-protocol',
            'RNDRUSDT': 'render-token',
            'ARBUSDT': 'arbitrum',
        }

        coin_id = cg_ids.get(symbol)
        if not coin_id:
            return None

        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=1&interval=minutely"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            prices = data["prices"]
            volumes = data["total_volumes"]

            timestamps = [dt.datetime.utcfromtimestamp(p[0] / 1000) for p in prices]
            closes = [p[1] for p in prices]
            vols = [v[1] for v in volumes]

            df = pd.DataFrame({
                "timestamp": timestamps,
                "close": closes,
                "volume": vols
            })
            # Preencher colunas ausentes
            df["open"] = df["close"]
            df["high"] = df["close"]
            df["low"] = df["close"]
            df = df[["timestamp", "open", "high", "low", "close", "volume"]]
            return df

        else:
            print(f"⚠️ Erro CoinGecko {symbol}: {res.status_code}")
            return None

    except Exception as e:
        print(f"❌ Erro CoinGecko {symbol}: {e}")
        return None
