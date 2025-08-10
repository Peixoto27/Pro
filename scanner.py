import os
import time
import requests
from textblob import TextBlob
from price_fetcher import fetch_all_data
from technical_indicators import calculate_indicators
from signal_generator import generate_signal
from notifier import send_signal_notification
from state_manager import load_open_trades, save_open_trades, check_and_notify_closed_trades

# --- CONFIGURAÇÕES ---
SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT", "TONUSDT",
    "INJUSDT", "RNDRUSDT", "ARBUSDT", "LTCUSDT", "MATICUSDT",
    "OPUSDT", "NEARUSDT", "APTUSDT", "PEPEUSDT", "SEIUSDT",
    "TRXUSDT", "DOGEUSDT", "SHIBUSDT", "FILUSDT", "SUIUSDT"
]

USAR_SENTIMENTO = True
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_API_URL = "https://newsapi.org/v2/everything"

# Cache para evitar chamadas repetidas
_sentiment_cache = {}

# Mapeamento de símbolos para nomes legíveis
symbol_map = {
    "BTCUSDT": "Bitcoin",
    "ETHUSDT": "Ethereum",
    "BNBUSDT": "Binance Coin",
    "SOLUSDT": "Solana",
    "XRPUSDT": "XRP",
    "ADAUSDT": "Cardano",
    "AVAXUSDT": "Avalanche",
    "DOTUSDT": "Polkadot",
    "LINKUSDT": "Chainlink",
    "TONUSDT": "Toncoin",
    "INJUSDT": "Injective",
    "RNDRUSDT": "Render Token",
    "ARBUSDT": "Arbitrum",
    "LTCUSDT": "Litecoin",
    "MATICUSDT": "Polygon",
    "OPUSDT": "Optimism",
    "NEARUSDT": "Near Protocol",
    "APTUSDT": "Aptos",
    "PEPEUSDT": "Pepe",
    "SEIUSDT": "Sei Network",
    "TRXUSDT": "Tron",
    "DOGEUSDT": "Dogecoin",
    "SHIBUSDT": "Shiba Inu",
    "FILUSDT": "Filecoin",
    "SUIUSDT": "Sui"
}

def get_sentiment_score(symbol):
    # Se já buscamos nessa execução, retorna do cache
    if symbol in _sentiment_cache:
        return _sentiment_cache[symbol]

    query = symbol_map.get(symbol, symbol)
    try:
        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 5,
            "apiKey": NEWS_API_KEY
        }
        resp = requests.get(NEWS_API_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

        if not data.get("articles"):
            _sentiment_cache[symbol] = 0
            return 0

        sentiment_sum = 0
        for article in data["articles"]:
            text = (article.get("title") or "") + " " + (article.get("description") or "")
            analysis = TextBlob(text)
            sentiment_sum += analysis.sentiment.polarity

        score = sentiment_sum / len(data["articles"])
        _sentiment_cache[symbol] = score
        return score

    except Exception as e:
        print(f"⚠️ Erro ao buscar sentimento para {symbol}: {e}")
        _sentiment_cache[symbol] = 0
        return 0

def get_macro_trend(df, symbol):
    return "ALTA"

def run_scanner():
    print("\n--- Iniciando novo ciclo do scanner ---")
    
    try:
        open_trades = load_open_trades()
    except Exception as e:
        print(f"⚠️ Erro ao carregar trades abertos: {e}")
        open_trades = {}

    try:
        market_data_for_monitoring = fetch_all_data(list(open_trades.keys()))
        check_and_notify_closed_trades(open_trades, market_data_for_monitoring, send_signal_notification)
    except Exception as e:
        print(f"⚠️ Erro ao verificar trades fechados: {e}")

    print("\n🔍 Fase 2: Buscando por novos sinais...")
    all_symbols_to_fetch = list(set(SYMBOLS) - set(open_trades.keys()))
    if not all_symbols_to_fetch:
        print("⚪ Não há novas moedas para analisar, todos os trades estão abertos.")
        return

    print("🚚 Buscando dados brutos do mercado (OHLCV)...")
    try:
        market_data = fetch_all_data(all_symbols_to_fetch)
    except Exception as e:
        print(f"🚨 Erro ao buscar dados de mercado: {e}")
        return

    for symbol, df in market_data.items():
        try:
            if df is None or df.empty:
                print(f"⚪ Sem dados para {symbol}, pulando...")
                continue

            print("-" * 20)
            print(f"🔬 Analisando {symbol}...")

            df_with_indicators = calculate_indicators(df)
            if df_with_indicators.empty:
                print(f"⚠️ Não foi possível calcular indicadores para {symbol}. Pulando...")
                continue
            print("✅ Indicadores calculados com sucesso.")

            tendencia_macro = get_macro_trend(df, symbol)
            if tendencia_macro != "ALTA":
                print(f"⚪ Tendência macro não é de ALTA para {symbol}. Pulando...")
                continue

            sentiment_score = 0.0
            if USAR_SENTIMENTO:
                sentiment_score = get_sentiment_score(symbol)
                print(f"🧠 Sentimento para {symbol}: {sentiment_score:.2f}")
                if sentiment_score < 0:
                    print(f"⚪ Sentimento negativo ({sentiment_score:.2f}) para {symbol}. Pulando...")
                    continue
            
            signal = generate_signal(df_with_indicators, symbol)
            
            if signal:
                print(f"🔥 SINAL ENCONTRADO PARA {symbol}!")
                try:
                    signal_text = (
                        f"🚀 *NOVA OPORTUNIDADE DE TRADE*\n\n"
                        f"📌 *Par:* {signal['symbol']}\n"
                        f"🎯 *Entrada:* `{signal['entry_price']}`\n"
                        f"🎯 *Alvo:* `{signal['target_price']}`\n"
                        f"🛑 *Stop Loss:* `{signal['stop_loss']}`\n\n"
                        f"📊 *Risco/Retorno:* `{signal['risk_reward']}`\n"
                        f"📈 *Confiança:* `{signal['confidence_score']}%`\n\n"
                        f"🧠 Estratégia: `{signal['strategy']}`\n"
                        f"📅 Criado em: `{signal['created_at']}`\n"
                        f"🆔 ID: `{signal['id']}`"
                    )
                    if send_signal_notification(signal_text):
                        open_trades[symbol] = signal
                        save_open_trades(open_trades)
                    else:
                        print(f"⚠️ Falha ao enviar sinal para {symbol}")
                except Exception as e:
                    print(f"🚨 Erro ao enviar notificação para {symbol}: {e}")
            else:
                print(f"⚪ Sem sinal para {symbol} após análise final.")

        except Exception as e:
            print(f"🚨 Erro inesperado ao processar {symbol}: {e}")

if __name__ == "__main__":
    while True:
        try:
            run_scanner()
        except Exception as e:
            print(f"🚨 ERRO CRÍTICO NO LOOP PRINCIPAL: {e}")
        print("\n--- Ciclo concluído. Aguardando 15 minutos... ---")
        time.sleep(900)
