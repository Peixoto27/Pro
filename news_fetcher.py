# news_fetcher.py (Versão Final Simplificada e Correta)
import requests
import os

# URL base, limpa, sem '?' ou parâmetros
CRYPTOPANIC_API_URL = "https://cryptopanic.com/api/v1/posts/"

def get_recent_news(symbol):
    """Busca as notícias mais recentes para um símbolo de moeda específico."""
    currency_code = symbol.replace("USDT", "")
    
    # --- CORREÇÃO FINAL APLICADA AQUI ---
    
    # 1. Busca a chave da API. Se não existir, api_key será None.
    api_key = os.getenv("CRYPTOPANIC_API_KEY")
    
    # 2. Monta o dicionário de parâmetros.
    #    Se a chave NÃO existir, o dicionário fica VAZIO, acessando o endpoint público.
    #    Se a chave EXISTIR, ela é adicionada, acessando o endpoint privado.
    params = {
        "auth_token": api_key,
        "currencies": currency_code
    } if api_key else {
        "currencies": currency_code
    }
    
    try:
        # A biblioteca 'requests' vai montar a URL corretamente a partir daqui.
        response = requests.get(CRYPTOPANIC_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get('results'):
            return [post['title'] for post in data['results']]
        return []
        
    except Exception as e:
        # Imprime a URL exata que falhou para depuração final.
        print(f"❌ Erro ao buscar notícias para {symbol}. URL: {response.url}. Erro: {e}")
        return []
