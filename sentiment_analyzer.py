# sentiment_analyzer.py (Versão Final com Gerenciador de Cota)
from textblob import TextBlob
from news_fetcher import get_recent_news
import time
from collections import deque

# --- NOSSO GERENCIADOR DE COTA INTELIGENTE ---
# Máximo de chamadas que queremos fazer em uma hora
HOURLY_API_CALL_LIMIT = 10  # Muito seguro para o plano gratuito
# Fila para armazenar os timestamps das nossas chamadas de API
api_call_timestamps = deque()
# -----------------------------------------

# Cache para guardar os resultados das notícias (isso continua sendo útil!)
sentiment_cache = {}
CACHE_DURATION = 6 * 60 * 60  # Cache de 2 horas

def can_make_api_call():
    """Verifica se podemos fazer uma nova chamada à API sem exceder o limite por hora."""
    current_time = time.time()
    
    # Remove timestamps da fila que são mais antigos que 1 hora
    while api_call_timestamps and api_call_timestamps[0] < current_time - 3600:
        api_call_timestamps.popleft()
        
    # Se o número de chamadas na última hora for menor que o nosso limite, podemos prosseguir
    if len(api_call_timestamps) < HOURLY_API_CALL_LIMIT:
        return True
    else:
        # Se atingimos o limite, não podemos fazer a chamada
        print("🚦 Limite de chamadas da API por hora atingido. Usando sentimento neutro.")
        return False

def get_sentiment_score(symbol):
    """
    Calcula uma pontuação de sentimento, usando cache e gerenciando a cota da API.
    """
    current_time = time.time()

    # 1. Verifica o cache primeiro (a forma mais rápida e barata)
    if symbol in sentiment_cache:
        cached_data = sentiment_cache[symbol]
        if current_time - cached_data['timestamp'] < CACHE_DURATION:
            print(f"🧠 Sentimento para {symbol} (do cache): {cached_data['score']:.2f}")
            return cached_data['score']

    # 2. Se não há cache, verifica se temos "crédito" para chamar a API
    if not can_make_api_call():
        # Se não podemos chamar a API, retornamos 0.0 e NÃO atualizamos o cache
        # para que ele possa tentar de novo no próximo ciclo.
        return 0.0

    # 3. Se podemos chamar a API, fazemos o trabalho pesado
    print(f"🌐 Buscando notícias frescas para {symbol} (crédito de API usado)...")
    # Registra que fizemos uma chamada
    api_call_timestamps.append(current_time)
    
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

    # 4. Guarda o novo resultado no cache
    sentiment_cache[symbol] = {
        'score': average_polarity,
        'timestamp': current_time
    }
    
    return average_polarity
