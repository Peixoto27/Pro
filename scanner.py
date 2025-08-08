# scanner.py (Versão CORRETA e COMPLETA)
import time
from price_fetcher import fetch_all_data
from technical_indicators import calculate_indicators # Importa a função de volta
from signal_generator import generate_signal
from state_manager import load_open_trades, save_open_trades, check_and_notify_closed_trades
from notifier import send_signal_notification
from sentiment_analyzer import get_sentiment_score

# --- CONFIGURAÇÕES ---
SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT", "TONUSDT",
    "INJUSDT", "RNDRUSDT", "ARBUSDT", "LTCUSDT", "MATICUSDT",
    "OPUSDT", "NEARUSDT", "APTUSDT", "PEPEUSDT", "SEIUSDT"
]
USAR_SENTIMENTO = True # Chave para ligar/desligar a análise de sentimento

def get_macro_trend(df, symbol):
    """Analisa a tendência macro (4h) para uma moeda específica."""
    try:
        df_4h = df.set_index('timestamp').resample('4h').agg({
            'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'
        }).dropna()
        
        if len(df_4h) < 50: return "NEUTRA"
        
        sma_50_4h = ta.trend.sma_indicator(df_4h['close'], window=50)
        last_close = df_4h['close'].iloc[-1]
        last_sma = sma_50_4h.iloc[-1]

        if last_close > last_sma:
            print(f"🔮 Tendência MACRO para {symbol} é: ALTA")
            return "ALTA"
        else:
            print(f"🔮 Tendência MACRO para {symbol} é: BAIXA")
            return "BAIXA"
    except Exception as e:
        print(f"⚠️ Erro ao calcular tendência macro para {symbol}: {e}")
        return "NEUTRA"

def run_scanner():
    """
    Executa o ciclo principal do scanner.
    """
    print("\n--- Iniciando novo ciclo do scanner ---")
    
    # Fase 1: Monitorar trades existentes
    print("\n📊 Fase 1: Monitorando trades existentes...")
    open_trades = load_open_trades()
    market_data_for_monitoring = fetch_all_data(list(open_trades.keys()))
    check_and_notify_closed_trades(open_trades, market_data_for_monitoring)

    # Fase 2: Buscar por novos sinais
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

        # --- FLUXO DE DADOS CORRETO ---
        # 1. Calcula os indicadores
        df_with_indicators = calculate_indicators(df)
        if df_with_indicators.empty:
            print(f"⚠️ Não foi possível calcular indicadores para {symbol}. Pulando...")
            continue
        print("✅ Indicadores calculados com sucesso.")

        # 2. Pega a tendência macro
        tendencia_macro = get_macro_trend(df, symbol)
        if tendencia_macro != "ALTA":
            print(f"⚪ Tendência macro não é de ALTA para {symbol}. Pulando...")
            continue

        # 3. Pega o sentimento (se ativado)
        sentiment_score = 0.0
        if USAR_SENTIMENTO:
            print(f"✅ Pré-condição técnica encontrada para {symbol}. Buscando sentimento...")
            sentiment_score = get_sentiment_score(symbol)
            if sentiment_score < 0:
                print(f"⚪ Sentimento negativo ({sentiment_score:.2f}) para {symbol}. Pulando...")
                continue
        
        # 4. Gera o sinal, passando o DataFrame COM indicadores
        signal = generate_signal(df_with_indicators, symbol) # Passa o DF correto!
        
        if signal:
            print(f"🔥 SINAL ENCONTRADO PARA {symbol}!")
            send_signal_notification(signal)
            open_trades[symbol] = signal
            save_open_trades(open_trades)
        else:
            print(f"⚪ Sem sinal para {symbol} após análise final.")

# --- Loop Principal ---
if __name__ == "__main__":
    while True:
        try:
            run_scanner()
        except Exception as e:
            print(f"🚨 ERRO CRÍTICO NO LOOP PRINCIPAL: {e}")
        print("\n--- Ciclo concluído. Aguardando 15 minutos... ---")
        time.sleep(900)
