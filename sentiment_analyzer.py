# sentiment_analyzer.py (Versão Final com Cache)
from textblob import TextBlob
from news_fetcher import get_recent_news
import time

# Nosso "cache" em memória. Um dicionário para guardar os resultados.
sentiment_cache = {}
# Tempo de vida do cache em segundos (ex: 2 horas)
CACHE_DURATION = 2 * 60 * 60 

def get_sentiment_score(symbol):
    """
    Calcula uma pontuação de sentimento, usando um cache para evitar chamadas repetidas.
    """
    current_time = time.time()

    # 1. Verifica se temos um resultado válido no cache
    if symbol in sentiment_cache:
        cached_data = sentiment_cache[symbol]
        # Se o cache não expirou, retorna o valor guardado
        if current_time - cached_data['timestamp'] < CACHE_DURATION:
            print(f"🧠 Sentimento para {symbol} (do cache): {cached_data['score']:.2f}")
            return cached_data['score']

    # 2. Se não há cache válido, busca as notícias (trabalho pesado)
    print(f"🌐 Buscando notícias frescas para {symbol}...")
    news_titles = get_recent_news(symbol)
    
    if not news_titles:
        average_polarity = 0.0
    else:
        total_polarity = 0
        for title in news_titles:
            analysis = TextBlob(title)
            total_polarity += analysis.sentiment.polarity
        average_polarity = total_polarity / len(news_titles)
    
    print(f"🧠 Sentimento calculado para {symbol}: {average_polarity:.2f}")

    # 3. Guarda o novo resultado no cache com o horário atual
    sentiment_cache[symbol] = {
        'score': average_polarity,
        'timestamp': current_time
    }
    
    return average_polarity
