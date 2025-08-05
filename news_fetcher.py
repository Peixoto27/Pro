# news_fetcher.py (Versão Final com Construção Manual de URL)
import requests
import os
from urllib.parse import urlencode

# URL base, limpa, sem '?' ou parâmetros
CRYPTOPANIC_API_URL_BASE = "https://cryptopanic.com/api/v1/posts/"

def get_recent_news(symbol):
    """Busca as notícias mais recentes para um símbolo de moeda específico."""
    currency_code = symbol.replace("USDT", "")
    
    # --- CORREÇÃO APLICADA AQUI: Construção Manual e Explícita ---
    
    # 1. Cria um dicionário com os parâmetros obrigatórios.
    params_dict = {
        "currencies": currency_code,
        "public": "true"
    }
    
    # 2. Busca a chave da API.
    api_key = os.getenv("CRYPTOPANIC_API_KEY")
    
    # 3. Adiciona o 'auth_token' ao dicionário SOMENTE se a chave existir.
    if api_key:
        params_dict['auth_token'] = api_key
        
    # 4. Constrói a string de parâmetros (ex: 'currencies=BTC&public=true')
    # A função urlencode lida com caracteres especiais de forma segura.
    query_string = urlencode(params_dict)
    
    # 5. Monta a URL final completa.
    final_url = f"{CRYPTOPANIC_API_URL_BASE}?{query_string}"
    
    try:
        # A requisição agora usa a URL final, sem passar 'params' para a biblioteca.
        response = requests.get(final_url)
        response.raise_for_status()
        data = response.json()
        
        if data.get('results'):
            return [post['title'] for post in data['results']]
        return []
        
    except Exception as e:
        print(f"⚠️ Erro ao buscar notícias para {symbol}: {e}")
        return []
