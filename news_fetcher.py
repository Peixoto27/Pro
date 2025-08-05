# news_fetcher.py (Versão Corrigida)
import requests
import os

CRYPTOPANIC_API_URL = "https://cryptopanic.com/api/v1/posts/"

def get_recent_news(symbol):
    """Busca as notícias mais recentes para um símbolo de moeda específico."""
    currency_code = symbol.replace("USDT", "")
    
    # --- CORREÇÃO APLICADA AQUI ---
    # 1. Começamos com os parâmetros que sempre estarão presentes.
    params = {
        "currencies": currency_code,
        "public": "true"
    }
    
    # 2. Buscamos a chave da API.
    api_key = os.getenv("CRYPTOPANIC_API_KEY")
    
    # 3. Adicionamos o 'auth_token' ao dicionário SOMENTE se a chave existir.
    if api_key:
        params['auth_token'] = api_key
    
    try:
        # A requisição agora envia um dicionário de parâmetros limpo.
        response = requests.get(CRYPTOPANIC_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get('results'):
            return [post['title'] for post in data['results']]
        return []
        
    except Exception as e:
        print(f"⚠️ Erro ao buscar notícias para {symbol}: {e}")
        return []
