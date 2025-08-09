import pandas as pd
import datetime
import uuid

PONTUACAO_MINIMA_PARA_SINAL = 90

PESO_SMA = 35
PESO_VOLUME = 30
PESO_MACD = 25
PESO_RSI = 10

def generate_signal(df_with_indicators, symbol):
    if df_with_indicators.empty:
        return None

    latest = df_with_indicators.iloc[-1]
    
    confidence_score = 0
    
    # Condições para sinais de compra
    # SMA: Preço acima da média móvel de 50 períodos
    if latest["close"] > latest["sma_50"]:
        confidence_score += PESO_SMA
        
    # Volume: Volume atual maior que a média móvel de 20 períodos do volume
    if latest["volume"] > latest["volume_sma_20"]:
        confidence_score += PESO_VOLUME
        
    # MACD: Linha MACD acima da linha de sinal (MACD Diff > 0)
    if latest["macd_diff"] > 0:
        confidence_score += PESO_MACD
        
    # RSI: RSI abaixo de 70 (não sobrecomprado)
    if latest["rsi"] < 70:
        confidence_score += PESO_RSI

    if confidence_score >= PONTUACAO_MINIMA_PARA_SINAL:
        entry_price = latest["close"]
        # Stop e alvo fixos, pois ATR não está disponível
        stop_loss = entry_price * 0.98 # Exemplo: 2% abaixo
        target_price = entry_price * 1.04 # Exemplo: 4% acima
        
        signal_dict = {
            "id": str(uuid.uuid4()),
            "signal_type": "BUY",
            "symbol": symbol,
            "entry_price": f"{entry_price:.4f}",
            "target_price": f"{target_price:.4f}",
            "stop_loss": f"{stop_loss:.4f}",
            "risk_reward": "1:2.0",
            "confidence_score": f"{confidence_score}",
            "strategy": "IA-Weighted (Fixed Stop)",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return signal_dict

    return None

