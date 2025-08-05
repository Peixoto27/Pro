# sentiment_analyzer.py
from textblob import TextBlob
from news_fetcher import get_recent_news

def get_sentiment_score(symbol):
    """
    Calcula uma pontuação de sentimento média para um símbolo com base nas últimas notícias.
    A pontuação varia de -1.0 (muito negativo) a +1.0 (muito positivo).
    """
    news_titles = get_recent_news(symbol)
    
    if not news_titles:
        # Se não houver notícias, o sentimento é neutro
        return 0.0

    total_polarity = 0
    analyzed_count = 0

    for title in news_titles:
        # Cria um objeto TextBlob para análise
        analysis = TextBlob(title)
        
        # A propriedade 'sentiment.polarity' dá a pontuação de sentimento
        total_polarity += analysis.sentiment.polarity
        analyzed_count += 1
    
    # Calcula a média da polaridade
    average_polarity = total_polarity / analyzed_count
    print(f"🧠 Sentimento para {symbol}: {average_polarity:.2f} (baseado em {analyzed_count} notícias)")
    
    return average_polarity
