import time
from price_fetcher import fetch_all_data
from technical_indicators import calculate_indicators
from signal_generator import generate_signal
from notifier import send_signal_notification
from state_manager import load_open_trades, save_open_trades, check_and_notify_closed_trades

# --- Módulos placeholder para evitar erros de importação --- 
# Estes módulos precisarão ser implementados ou substituídos por versões reais
# se o usuário quiser a funcionalidade completa de gerenciamento de estado, notificação e sentimento.

def get_sentiment_score(symbol):
    return 0.5  # Retorna um valor neutro para teste

# --- CONFIGURAÇÕES --- 
SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT", "TONUSDT",
    "INJUSDT", "RNDRUSDT", "ARBUSDT", "LTCUSDT", "MATICUSDT",
    "OPUSDT", "NEARUSDT", "APTUSDT", "PEPEUSDT", "SEIUSDT"
]
USAR_SENTIMENTO = False  # Desativado por padrão para simplificar o teste inicial

def get_macro_trend(df, symbol):
    # Esta função precisa de 'ta' e um DataFrame com dados suficientes
    # Para simplificar o teste inicial, vamos retornar sempre 'ALTA'
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
                print(f"✅ Pré-condição técnica encontrada para {symbol}. Buscando sentimento...")
                sentiment_score = get_sentiment_score(symbol)
                if sentiment_score < 0:
                    print(f"⚪ Sentimento negativo ({sentiment_score:.2f}) para {symbol}. Pulando...")
                    continue
            
            signal = generate_signal(df_with_indicators, symbol)
            
            if signal:
                print(f"🔥 SINAL ENCONTRADO PARA {symbol}!")
                try:
                    if send_signal_notification(signal):
                        open_trades[symbol] = signal
                        save_open_trades(open_trades)
                    else:
                        print(f"⚠️ Falha ao enviar sinal para {symbol}, não será salvo como trade aberto.")
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
