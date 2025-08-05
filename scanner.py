# scanner.py
import datetime
from price_fetcher import fetch_all_data
from technical_indicators import calculate_indicators
from signal_generator import generate_signal
from notifier import send_signal_notification # <-- 1. IMPORTAÇÃO ADICIONADA

# Lista de moedas a serem analisadas
SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT", "TONUSDT",
    "INJUSDT", "RNDRUSDT", "ARBUSDT", "LTCUSDT", "MATICUSDT",
    "OPUSDT", "NEARUSDT", "APTUSDT", "PEPEUSDT", "SEIUSDT"
]

def main():
    """Função principal para executar o scanner de criptomoedas."""
    print("🔍 Iniciando varredura de sinais...\n")

    market_data = fetch_all_data(SYMBOLS)

    if not market_data:
        print("🔴 Não foi possível buscar dados de mercado. Encerrando.")
        return

    print("\n📊 Processando dados e gerando sinais...\n")
    for symbol, df in market_data.items():
        try:
            df_with_indicators = calculate_indicators(df)
            
            if df_with_indicators is not None and not df_with_indicators.empty:
                # A função generate_signal precisa retornar um dicionário como o esperado pelo notifier
                signal_data = generate_signal(df_with_indicators, symbol) # Passando o símbolo para a função

                if signal_data:
                    # --- 2. INTEGRAÇÃO COM O TELEGRAM ---
                    # Imprime no log que o sinal foi encontrado
                    print(f"✅ Sinal encontrado para {symbol}. Enviando para o Telegram...")
                    # Chama a função do notifier para enviar a notificação
                    send_signal_notification(signal_data)
                else:
                    print(f"⚪ Sem sinal relevante para {symbol}")
            else:
                print(f"⚠️ Não foi possível calcular indicadores para {symbol}.")

        except Exception as e:
            print(f"❌ Erro crítico ao processar {symbol}: {e}")

if __name__ == "__main__":
    main()
