# scanner.py (Versão Final Polida)
import pandas as pd
import time
from price_fetcher import fetch_all_raw_data
from technical_indicators import calculate_indicators
from signal_generator import generate_signal
from notifier import send_signal_notification, send_trade_update_notification
from state_manager import load_open_trades, save_open_trades
from sentiment_analyzer import get_sentiment_score

SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", 
    "AVAXUSDT", "DOTUSDT", "LINKUSDT", "TONUSDT", "INJUSDT", "RNDRUSDT", 
    "ARBUSDT", "LTCUSDT", "MATICUSDT", "OPUSDT", "NEARUSDT", "APTUSDT", 
    "PEPEUSDT", "SEIUSDT"
]

def run_scanner():
    print("\n--- Iniciando novo ciclo de varredura ---")
    
    # FASE 1: Monitorar Trades Existentes
    print("\n📊 Fase 1: Monitorando trades existentes...")
    open_trades = load_open_trades()
    trades_to_remove = []
    
    # --- CORREÇÃO 1: VERIFICA SE HÁ TRADES ABERTOS ANTES DE BUSCAR DADOS ---
    if open_trades:
        raw_data_trades = fetch_all_raw_data(list(open_trades.keys()))
        
        for symbol, trade_info in open_trades.items():
            df_raw = raw_data_trades.get(symbol)
            if df_raw is None or df_raw.empty:
                continue
            
            # --- CORREÇÃO 2: USA 'h' MINÚSCULO PARA RESAMPLE ---
            df_1h = df_raw.set_index('timestamp').resample('1h').agg({
                'close': 'last', 'high': 'max', 'low': 'min', 'volume': 'sum'
            }).dropna().reset_index()
            
            if df_1h.empty:
                continue

            current_price = df_1h.iloc[-1]['close']
            
            if trade_info['signal_type'] == 'COMPRA':
                if current_price >= float(trade_info['target_price']):
                    send_trade_update_notification(symbol, 'ALVO ATINGIDO (LUCRO)', trade_info)
                    trades_to_remove.append(symbol)
                elif current_price <= float(trade_info['stop_loss']):
                    send_trade_update_notification(symbol, 'STOP ATINGIDO (PERDA)', trade_info)
                    trades_to_remove.append(symbol)
            elif trade_info['signal_type'] == 'VENDA':
                if current_price <= float(trade_info['target_price']):
                    send_trade_update_notification(symbol, 'ALVO ATINGIDO (LUCRO)', trade_info)
                    trades_to_remove.append(symbol)
                elif current_price >= float(trade_info['stop_loss']):
                    send_trade_update_notification(symbol, 'STOP ATINGIDO (PERDA)', trade_info)
                    trades_to_remove.append(symbol)

    for symbol in trades_to_remove:
        del open_trades[symbol]

    # FASE 2: Buscar Novos Sinais
    print("\n🔍 Fase 2: Buscando por novos sinais...")
    symbols_to_scan = [s for s in SYMBOLS if s not in open_trades]
    all_market_data = fetch_all_raw_data(symbols_to_scan)

    for symbol, df_raw in all_market_data.items():
        # --- CORREÇÃO 2: USA 'h' MINÚSCULO PARA RESAMPLE ---
        df_4h = df_raw.set_index('timestamp').resample('4h').agg({
            'close': 'last', 'high': 'max', 'low': 'min', 'volume': 'sum'
        }).dropna().reset_index()
        
        df_1h = df_raw.set_index('timestamp').resample('1h').agg({
            'close': 'last', 'high': 'max', 'low': 'min', 'volume': 'sum'
        }).dropna().reset_index()

        if df_4h.empty or df_1h.empty:
            continue

        sma_20_4h = df_4h['close'].rolling(window=20).mean().iloc[-1]
        sma_50_4h = df_4h['close'].rolling(window=50).mean().iloc[-1]
        
        tendencia_macro = "NEUTRA"
        if sma_20_4h > sma_50_4h:
            tendencia_macro = "ALTA"
        elif sma_20_4h < sma_50_4h:
            tendencia_macro = "BAIXA"
        print(f"🔮 Tendência MACRO para {symbol} é: {tendencia_macro}")

        df_with_indicators = calculate_indicators(df_1h.copy())
        if df_with_indicators is None or df_with_indicators.empty:
            continue

        latest_indicators = df_with_indicators.iloc[-1]
        sma_short = latest_indicators.get('SMA_20')
        sma_long = latest_indicators.get('SMA_50')
        
        pre_condicao_compra = sma_short > sma_long
        pre_condicao_venda = sma_short < sma_long

        sentiment_score = 0.0
        if pre_condicao_compra or pre_condicao_venda:
            print(f"📈 Pré-condição técnica encontrada para {symbol}. Buscando sentimento...")
            sentiment_score = get_sentiment_score(symbol)
        
        signal = generate_signal(df_with_indicators, symbol, tendencia_macro, sentiment_score)
        
        if signal:
            print(f"📢 Novo sinal encontrado para {symbol}!")
            send_signal_notification(signal)
            open_trades[symbol] = signal

    save_open_trades(open_trades)
    print("\n💾 Estado atualizado salvo. Ciclo concluído.")

if __name__ == "__main__":
    while True:
        run_scanner()
        print("\n--- Aguardando 15 minutos para o próximo ciclo ---")
        time.sleep(900)
