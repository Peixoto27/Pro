# scanner.py
from price_fetcher import fetch_all_data
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

def monitorar_trades_abertos(trades_abertos, df_mercado_atual):
    """Verifica se algum trade aberto atingiu o alvo ou o stop."""
    trades_fechados = []
    for symbol, trade_info in trades_abertos.items():
        if symbol not in df_mercado_atual:
            continue

        df_ativo = df_mercado_atual[symbol]
        preco_atual = df_ativo['close'].iloc[-1]
        
        alvo = float(trade_info['target_price'])
        stop = float(trade_info['stop_loss'])
        
        # Lógica para trade de COMPRA
        if trade_info['signal_type'] == 'COMPRA':
            if preco_atual >= alvo:
                print(f"✅ ALVO ATINGIDO para {symbol}!")
                send_take_profit_notification(trade_info, preco_atual)
                trades_fechados.append(symbol)
            elif preco_atual <= stop:
                print(f"❌ STOP ATINGIDO para {symbol}!")
                send_stop_loss_notification(trade_info, preco_atual)
                trades_fechados.append(symbol)

        # Lógica para trade de VENDA
        elif trade_info['signal_type'] == 'VENDA':
            if preco_atual <= alvo:
                print(f"✅ ALVO ATINGIDO para {symbol}!")
                send_take_profit_notification(trade_info, preco_atual)
                trades_fechados.append(symbol)
            elif preco_atual >= stop:
                print(f"❌ STOP ATINGIDO para {symbol}!")
                send_stop_loss_notification(trade_info, preco_atual)
                trades_fechados.append(symbol)

    # Remove os trades que foram fechados do dicionário principal
    for symbol in trades_fechados:
        del trades_abertos[symbol]

def buscar_novos_sinais(trades_abertos, df_mercado_atual):
    """Busca por novos sinais apenas para os ativos que não têm trade aberto."""
    for symbol, df in df_mercado_atual.items():
        if symbol in trades_abertos:
            print(f"⚪ {symbol} já tem um trade em andamento. Ignorando busca por novo sinal.")
            continue

        try:
            df_com_indicadores = calculate_indicators(df)
            if df_com_indicadores is not None and not df_com_indicadores.empty:
                novo_sinal = generate_signal(df_com_indicadores, symbol)
                if novo_sinal:
                    print(f"📢 Novo sinal encontrado para {symbol}! Adicionando ao monitoramento.")
                    trades_abertos[symbol] = novo_sinal
                    send_signal_notification(novo_sinal)
        except Exception as e:
            print(f"❌ Erro crítico ao processar {symbol} para novo sinal: {e}")

def main():
    """Função principal que orquestra o scanner."""
    print("🤖 Iniciando ciclo do robô de sinais...")

    # 1. Carrega o estado atual (trades que já estão abertos)
    trades_abertos = ler_trades_abertos()
    print(f"🔍 Trades em monitoramento: {list(trades_abertos.keys())}")

    # 2. Busca os dados de mercado mais recentes para todos os ativos
    df_mercado_atual = fetch_all_data(SYMBOLS)
    if not df_mercado_atual:
        print("🔴 Não foi possível buscar dados de mercado. Encerrando ciclo.")
        return

    # 3. Monitora os trades que já estavam abertos
    print("\n📊 Fase 1: Monitorando trades existentes...")
    monitorar_trades_abertos(trades_abertos, df_mercado_atual)

    # 4. Busca por novos sinais nos ativos que não estão em operação
    print("\n🔎 Fase 2: Buscando por novos sinais...")
    buscar_novos_sinais(trades_abertos, df_mercado_atual)

    # 5. Salva o estado final (com novos trades adicionados ou antigos removidos)
    salvar_trades_abertos(trades_abertos)
    print("\n💾 Estado atualizado salvo. Ciclo concluído.")

if __name__ == "__main__":
    main()
