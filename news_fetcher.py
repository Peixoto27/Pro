# news_fetcher.py
import requests
import os

# A API do CryptoPanic não requer chave para o endpoint público
CRYPTOPANIC_API_URL = "https://cryptopanic.com/api/v1/posts/"

def get_recent_news(symbol):
    """Busca as notícias mais recentes para um símbolo de moeda específico."""
    # Remove 'USDT' do símbolo para buscar (ex: 'BTCUSDT' -> 'BTC')
    currency_code = symbol.replace("USDT", "")
    
    params = {
        "auth_token": os.getenv("CRYPTOPANIC_API_KEY", ""), # Chave opcional para planos pagos
        "currencies": currency_code,
        "public": "true"
    }
    
    try:
        response = requests.get(CRYPTOPANIC_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get('results'):
            # Retorna uma lista dos títulos das notícias
            return [post['title'] for post in data['results']]
        return []
        
    except Exception as e:
        print(f"⚠️ Erro ao buscar notícias para {symbol}: {e}")
        return []
