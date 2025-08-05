# signal_generator.py
import pandas as pd
import datetime

def generate_signal(df_with_indicators, symbol): # Adicionado 'symbol' como parâmetro
    """Gera um dicionário de sinal de compra ou venda com base nos indicadores."""
    if df_with_indicators is None or df_with_indicators.empty:
        return None

    latest_data = df_with_indicators.iloc[-1]
    
    sma_short = latest_data.get('SMA_20')
    sma_long = latest_data.get('SMA_50')
    rsi = latest_data.get('RSI')
    current_price = latest_data.get('close')

    if sma_short is None or sma_long is None or rsi is None or current_price is None:
        return None

    signal_type = None
    if sma_short > sma_long and rsi < 70:
        signal_type = "COMPRA"
    elif sma_short < sma_long and rsi > 30:
        signal_type = "VENDA"

    if signal_type:
        # --- CRIAÇÃO DO DICIONÁRIO DE SINAL ---
        # Esta é uma lógica de exemplo. Você deve substituir os cálculos
        # pelos da sua estratégia real.
        entry_price = current_price
        risk_reward_ratio = 2.0  # Exemplo: Risco/Retorno de 2:1

        if signal_type == "COMPRA":
            stop_loss = entry_price * 0.98  # Stop loss 2% abaixo da entrada
            target_price = entry_price + (entry_price - stop_loss) * risk_reward_ratio
        else: # VENDA
            stop_loss = entry_price * 1.02  # Stop loss 2% acima da entrada
            target_price = entry_price - (stop_loss - entry_price) * risk_reward_ratio

        expected_profit_percent = abs((target_price - entry_price) / entry_price) * 100
        
        signal_dict = {
            "symbol": symbol,
            "entry_price": f"{entry_price:.4f}",
            "target_price": f"{target_price:.4f}",
            "stop_loss": f"{stop_loss:.4f}",
            "risk_reward": f"1:{risk_reward_ratio}",
            "confidence_score": f"{75 + rsi/10:.1f}", # Lógica de exemplo para confiança
            "expected_profit_percent": f"{expected_profit_percent:.2f}",
            "expected_profit_usdt": f"{(expected_profit_percent/100 * 1000):.2f} (em lote de 1000 USDT)", # Exemplo
            "news_summary": "N/A", # Você integraria a busca de notícias aqui
            "strategy": "Cruzamento de Médias Móveis com RSI",
            "timeframe": "1 Hora",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return signal_dict

    return None
