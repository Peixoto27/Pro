# signal_generator.py (Versão Final com Pontuação da IA)
import pandas as pd
import datetime

# --- PARÂMETROS DA ESTRATÉGIA COM PESOS DA IA ---
PONTUACAO_MINIMA_PARA_SINAL = 85  # Aumentamos a exigência. Queremos sinais A+

# Pesos baseados na importância que a IA nos deu
PESO_SMA = 35
PESO_VOLUME = 30
PESO_MACD = 25
PESO_RSI = 10  # Ainda vale alguma coisa, mas menos

def generate_signal(df, indicators):
    """
    Gera um sinal de compra usando um sistema de pontuação ponderado pela IA.
    """
    if df.empty or len(df) < 50:
        return None

    # Pega os dados mais recentes
    latest = df.iloc[-1]
    
    # --- INICIA O CÁLCULO DA PONTUAÇÃO ---
    confidence_score = 0
    
    # 1. Condição da SMA 50 (O mais importante - vale até 35 pontos)
    # O preço precisa estar acima da média de 50 períodos
    if latest['close'] > latest['sma_50']:
        confidence_score += PESO_SMA
        
    # 2. Condição do Volume (O segundo mais importante - vale até 30 pontos)
    # O volume atual precisa ser maior que a média de volume
    if latest['volume'] > latest['volume_sma_20']:
        confidence_score += PESO_VOLUME
        
    # 3. Condição do MACD (O terceiro mais importante - vale até 25 pontos)
    # A linha do MACD precisa estar acima da linha de sinal (cruzamento de alta)
    if latest['macd_diff'] > 0:
        confidence_score += PESO_MACD
        
    # 4. Condição do RSI (Menos importante, mas ajuda - vale até 10 pontos)
    # RSI não pode estar sobrecomprado (menor que 70)
    if latest['rsi'] < 70:
        confidence_score += PESO_RSI

    # --- DECISÃO FINAL ---
    # Verifica se a pontuação total atingiu nosso mínimo de alta confiança
    if confidence_score >= PONTUACAO_MINIMA_PARA_SINAL:
        # Se sim, calcula os alvos usando a volatilidade (ATR)
        entry_price = latest['close']
        stop_loss = entry_price - (2 * latest['atr'])  # Stop dinâmico com ATR
        target_price = entry_price + (4 * latest['atr']) # Alvo com R:R de 1:2
        
        # Monta o dicionário completo do sinal
        signal_dict = {
            'signal_type': 'BUY',
            'symbol': indicators['symbol'],
            'entry_price': f"{entry_price:.4f}",
            'target_price': f"{target_price:.4f}",
            'stop_loss': f"{stop_loss:.4f}",
            'risk_reward': "1:2.0",
            'confidence_score': f"{confidence_score}",
            'strategy': f"IA-Weighted (ATR Stop)",
            'created_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return signal_dict

    return None
