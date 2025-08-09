import time
from price_fetcher import fetch_all_data
from technical_indicators import calculate_indicators
from signal_generator_working import generate_signal
from notifier_working import send_signal_notification
from state_manager import load_open_trades, save_open_trades, check_and_notify_closed_trades

def get_sentiment_score(symbol):
    return 0.5 # Retorna um valor neutro para teste

# --- CONFIGURAÇÕES --- 
SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT", "TONUSDT",
    "INJUSDT", "RNDRUSDT", "ARBUSDT", "LTCUSDT", "MATICUSDT",
    "OPUSDT", "NEARUSDT", "APTUSDT", "PEPEUSDT", "SEIUSDT"
]
USAR_SENTIMENTO = False

def get_macro_trend(df, symbol):
    return "ALTA"

def run_scanner():
    print("\n--- Iniciando novo ciclo do scanner ---")
    
    # Fase 1: Monitoramento de trades abertos
    print("🔍 Fase 1: Monitorando trades abertos...")
    open_trades = load_open_trades()
    if open_trades:
        print(f"📊 Monitorando {len(open_trades)} trades abertos...")
        market_data_for_monitoring = fetch_all_data(list(open_trades.keys()))
        check_and_notify_closed_trades(open_trades, market_data_for_monitoring, send_signal_notification)
    else:
        print("📊 Nenhum trade aberto para monitorar.")
    
    print("\n🔍 Fase 2: Buscando por novos sinais...")
    all_symbols_to_fetch = list(set(SYMBOLS) - set(open_trades.keys()))
    if not all_symbols_to_fetch:
        print("⚪ Não há novas moedas para analisar, todos os trades estão abertos.")
        return

    print("🚚 Buscando dados brutos do mercado (OHLCV)...")
    market_data = fetch_all_data(all_symbols_to_fetch)

    for symbol, df in market_data.items():
        if df is None or df.empty:
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
            print(f"✅ Pré-condição técnica encontrada para {symbol}. Buscando sentimento...")
            sentiment_score = get_sentiment_score(symbol)
            if sentiment_score < 0:
                print(f"⚪ Sentimento negativo ({sentiment_score:.2f}) para {symbol}. Pulando...")
                continue
        
        signal = generate_signal(df_with_indicators, symbol)
        
        if signal:
            print(f"🔥 SINAL ENCONTRADO PARA {symbol}!")
            send_signal_notification(signal)
            open_trades[symbol] = {
                'entry_price': float(signal['entry_price']),
                'target_price': float(signal['target_price']),
                'stop_loss': float(signal['stop_loss']),
                'created_at': signal['created_at']
            }
            save_open_trades(open_trades)
        else:
            print(f"⚪ Sem sinal para {symbol} após análise final.")

if __name__ == "__main__":
    while True:
        try:
            run_scanner()
        except Exception as e:
            print(f"🚨 ERRO CRÍTICO NO LOOP PRINCIPAL: {e}")
        print("\n--- Ciclo concluído. Aguardando 15 minutos... ---")
        time.sleep(900)

