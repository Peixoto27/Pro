import requests
import pandas as pd
import time

def fetch_price_data(symbol):
    try:
        # Tenta Binance primeiro
        binance_url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        res = requests.get(binance_url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            return pd.DataFrame([{
                "timestamp": pd.Timestamp.utcnow(),
                "price": float(data["lastPrice"]),
                "volume": float(data["quoteVolume"]),
                "price_change_percent": float(data["priceChangePercent"])
            }])
        elif res.status_code == 451:
            print(f"🔁 Binance bloqueada para {symbol}. Usando CoinGecko...")
        else:
            print(f"⚠️ Erro Binance para {symbol}: {res.status_code}")

    except Exception as e:
        print(f"❌ Erro Binance para {symbol}: {e}")

    # Fallback CoinGecko
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
            'ARBUSDT': 'arbitrum'
        }

        coin_id = cg_ids.get(symbol)
        if not coin_id:
            return None

        cg_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&market_data=true"
        res = requests.get(cg_url, timeout=5)
        if res.status_code == 200:
            coin = res.json()["market_data"]
            df = pd.DataFrame([{
                "timestamp": pd.Timestamp.utcnow(),
                "price": coin["current_price"]["usd"],
                "volume": coin["total_volume"]["usd"],
                "price_change_percent": coin["price_change_percentage_24h"]
            }])

            # Simulando histórico com uma linha, mas aplicando o mesmo tratamento
            df = (
                df.set_index("timestamp")
                .resample("1h")
                .mean()
                .ffill()
                .reset_index()
            )

            time.sleep(2)  # para evitar bloqueio da CoinGecko
            return df

        else:
            print(f"⚠️ Erro CoinGecko {symbol}: {res.status_code}")
            return None

    except Exception as e:
        print(f"❌ Erro CoinGecko {symbol}: {e}")
        return None
