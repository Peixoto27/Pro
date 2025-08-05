import requests
import pandas as pd
from datetime import datetime

def fetch_price_data(symbol):
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
        print(f"❌ CoinGecko ID não encontrado para {symbol}")
        return None

    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc?vs_currency=usd&days=1"
        res = requests.get(url, timeout=5)

        if res.status_code == 200:
            data = res.json()

            if not data or len(data) < 20:
                print(f"⚠️ Dados insuficientes para {symbol}")
                return None

            df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

            # Volume separado
            volume_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=1"
            vol_res = requests.get(volume_url, timeout=5)
            if vol_res.status_code == 200:
                vol_data = vol_res.json().get("total_volumes", [])
                if vol_data:
                    volume_df = pd.DataFrame(vol_data, columns=["timestamp", "volume"])
                    volume_df["timestamp"] = pd.to_datetime(volume_df["timestamp"], unit="ms")
                    volume_df = volume_df.set_index("timestamp").resample("1H").mean().fillna(method='ffill').reset_index()
                    df = pd.merge_asof(df.sort_values("timestamp"), volume_df.sort_values("timestamp"), on="timestamp")
                else:
                    df["volume"] = 0
            else:
                df["volume"] = 0

            return df

        elif res.status_code == 429:
            print(f"⚠️ Limite atingido na CoinGecko para {symbol}.")
        else:
            print(f"⚠️ Erro CoinGecko {symbol}: {res.status_code}")

    except Exception as e:
        print(f"❌ Erro ao buscar dados de {symbol}: {e}")

    return None
