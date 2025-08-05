# signal_generator.py (VERSÃO DE TESTE)
import pandas as pd
import datetime

def generate_signal(df_with_indicators, symbol):
    """
    Gera um SINAL DE TESTE para a primeira moeda (BTCUSDT) 
    para garantir que a notificação do Telegram está funcionando.
    """
    # Vamos gerar um sinal apenas para o BTC para não lotar o canal.
    if symbol != "BTCUSDT":
        return None # Ignora as outras moedas

    print(f"👉 FORÇANDO SINAL DE TESTE para {symbol}...")

    # Pega o preço atual para o sinal parecer real
    current_price = df_with_indicators.iloc[-1].get('close', 50000)

    # Cria um dicionário de sinal falso
    signal_dict = {
        "symbol": symbol,
        "entry_price": f"{current_price:.2f}",
        "target_price": f"{current_price * 1.05:.2f}",
        "stop_loss": f"{current_price * 0.98:.2f}",
        "risk_reward": "1:2.5",
        "confidence_score": "99.9",
        "expected_profit_percent": "5.00",
        "expected_profit_usdt": "2500 (em lote de 50000 USDT)",
        "news_summary": "Este é um sinal de teste para verificar a conexão com o Telegram.",
        "strategy": "Teste de Notificação",
        "timeframe": "1 Hora",
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return signal_dict
