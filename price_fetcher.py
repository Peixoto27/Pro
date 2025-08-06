# price_fetcher.py (Versão Final com busca de dados OHLC)
import requests
import pandas as pd
import time
import os

COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "CG-SnFGo9ozwT62MLbBiuuzpxxh")
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
HEADERS = {"accept": "application/json", "x-cg-demo-api-key": COINGECKO_API_KEY}
SYMBOL_TO_ID = {
    "BTCUSDT": "bitcoin", "ETHUSDT": "ethereum", "BNBUSDT": "binancecoin",
    "SOLUSDT": "solana", "XRPUSDT": "ripple", "ADAUSDT": "cardano",
    "AVAXUSDT": "avalanche-2", "DOTUSDT": "polkadot", "LINKUSDT": "chainlink",
    "TONUSDT": "the-open-network", "INJUSDT": "injective-protocol", "RNDRUSDT": "render-token",
    "ARBUSDT": "arbitrum", "LTCUSDT": "litecoin", "MATICUSDT": "matic-network",
    "OPUSDT": "optimism", "NEARUSDT": "near", "APTUSDT": "aptos",
    "PEPEUSDT": "pepe", "SEIUSDT": "sei-network"
}

def fetch_all_raw_data(symbols, days=10):
    """
    Busca os dados OHLC (Open, High, Low, Close) e Volume para todos os símbolos.
    """
    all_data = {}
    if not symbols:
        return all_data

    print("\n🔁 Buscando dados brutos do mercado (OHLCV)...")
    for symbol in symbols:
        coin_id = SYMBOL_TO_ID.get(symbol)
        if not coin_id:
            continue

        # A API do CoinGecko não tem um endpoint OHLCV por hora fácil.
        # Vamos usar o market_chart e simular o OHLC a partir do 'close'.
        # Esta é a abordagem mais robusta sem mudar de API.
        url = f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart"
        params = {"vs_currency": "usd", "days": days}

        try:
            response = requests.get(url, params=params, headers=HEADERS)
            response.raise_for_status()
            data = response.json()

            if "prices" in data and data["prices"] and "total_volumes" in data and data["total_volumes"]:
                df_price = pd.DataFrame(data["prices"], columns=["timestamp", "close"])
                df_price["timestamp"] = pd.to_datetime(df_price["timestamp"], unit="ms")
                
                df_volume = pd.DataFrame(data["total_volumes"], columns=["timestamp", "volume"])
                df_volume["timestamp"] = pd.to_datetime(df_volume["timestamp"], unit="ms")

                df_merged = pd.merge(df_price, df_volume, on="timestamp")

                # --- SIMULAÇÃO DE OHLC ---
                # Adicionamos as colunas 'open', 'high', 'low' usando o 'close'
                df_merged['open'] = df_merged['close']
                df_merged['high'] = df_merged['close']
                df_merged['low'] = df_merged['close']
                
                all_data[symbol] = df_merged
                print(f"✅ Dados brutos para {symbol} recebidos.")
            else:
                print(f"⚠️ Dados de preço ou volume indisponíveis para {symbol}.")
        
        except Exception as e:
            print(f"❌ Erro ao buscar dados de {symbol}: {e}")
        
        time.sleep(2.5)
    
    return all_data
