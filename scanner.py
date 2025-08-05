# scanner.py (Versão Otimizada e Final)
import pandas as pd
import ta
from price_fetcher import fetch_all_raw_data
from technical_indicators import calculate_indicators
from signal_generator import generate_signal
from state_manager import ler_trades_abertos, salvar_trades_abertos
from notifier import send_signal_notification, send_take_profit_notification, send_stop_loss_notification

SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT", "TONUSDT",
    "INJUSDT", "RNDRUSDT", "ARBUSDT", "LTCUSDT", "MATICUSDT",
    "OPUSDT", "NEARUSDT", "APTUSDT", "PEPEUSDT", "SEIUSDT"
]

# --- CHAVE DE ATIVAÇÃO PARA MTA ---
USAR_MTA = True

def get_macro_trend(df_raw):
    """Calcula a tendência macro a partir dos dados brutos, reamostrando para 4h."""
    if df_raw is None or df_raw.empty:
        return "NEUTRA"
    
    df_4h = df_raw.set_index('timestamp').resample('4h').last().dropna().reset_index()
    
    if len(df_4h) < 50:
        return "NEUTRA"
        
    df_4h['SMA_50'] = ta.trend.SMAIndicator(close=df_4h['close'], window=50).sma_indicator()
    
    ultimo_preco = df_4h['close'].iloc[-1]
    ultima_sma = df_4h['SMA_50'].iloc[-1]

    if ultimo_preco > ultima_sma:
        return "ALTA"
    elif ultimo_preco < ultima_sma:
        return "BAIXA"
    return "NEUTRA"

def main():
    print("🤖 Iniciando ciclo do robô de sinais...")
    trades_abertos = ler_trades_abertos()
    print(f"🔍 Trades em monitoramento: {list(trades_abertos.keys())}")

    # 1. Busca os dados brutos UMA ÚNICA VEZ
    dados_brutos_mercado = fetch_all_raw_data(SYMBOLS)
    if not dados_brutos_mercado:
        print("🔴 Não foi possível buscar dados de mercado. Encerrando ciclo.")
        return

    # --- FASE 1: Monitorar Trades Abertos ---
    print("\n📊 Fase 1: Monitorando trades existentes...")
    trades_fechados = []
    for symbol, trade_info in trades_abertos.items():
        if symbol not in dados_brutos_mercado:
            continue
        
        preco_atual = dados_brutos_mercado[symbol]['close'].iloc[-1]
        alvo = float(trade_info['target_price'])
        stop = float(trade_info['stop_loss'])

        # ... (lógica de verificação de alvo/stop continua a mesma)
        if (trade_info['signal_type'] == 'COMPRA' and preco_atual >= alvo) or \
           (trade_info['signal_type'] == 'VENDA' and preco_atual <= alvo):
            print(f"✅ ALVO ATINGIDO para {symbol}!")
            send_take_profit_notification(trade_info, preco_atual)
            trades_fechados.append(symbol)
        elif (trade_info['signal_type'] == 'COMPRA' and preco_atual <= stop) or \
             (trade_info['signal_type'] == 'VENDA' and preco_atual >= stop):
            print(f"❌ STOP ATINGIDO para {symbol}!")
            send_stop_loss_notification(trade_info, preco_atual)
            trades_fechados.append(symbol)
            
    for symbol in trades_fechados:
        del trades_abertos[symbol]

    # --- FASE 2: Buscar Novos Sinais ---
    print("\n🔎 Fase 2: Buscando por novos sinais...")
    for symbol, df_raw in dados_brutos_mercado.items():
        if symbol in trades_abertos:
            print(f"⚪ {symbol} já tem um trade em andamento.")
            continue

        # Define a tendência macro usando os dados brutos
        tendencia_macro = get_macro_trend(df_raw) if USAR_MTA else "NEUTRA"
        print(f"🔮 Tendência MACRO para {symbol} é: {tendencia_macro}")

        # Cria o dataframe de 1h para os indicadores
        df_1h = df_raw.set_index('timestamp').resample('1h').last().ffill().dropna().reset_index()
        
        df_com_indicadores = calculate_indicators(df_1h)
        
        if df_com_indicadores is not None and not df_com_indicadores.empty:
            novo_sinal = generate_signal(df_com_indicadores, symbol, tendencia_macro) # Passa a tendência como argumento
            if novo_sinal:
                print(f"📢 Novo sinal encontrado para {symbol}! Adicionando ao monitoramento.")
                trades_abertos[symbol] = novo_sinal
                send_signal_notification(novo_sinal)

    salvar_trades_abertos(trades_abertos)
    print("\n💾 Estado atualizado salvo. Ciclo concluído.")

if __name__ == "__main__":
    main()
