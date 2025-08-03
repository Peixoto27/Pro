import requests

RSS_FEEDS = {
    "BTC": "https://cryptopanic.com/api/v1/posts/?auth_token=demo&currencies=BTC",
    "ETH": "https://cryptopanic.com/api/v1/posts/?auth_token=demo&currencies=ETH",
    "SOL": "https://cryptopanic.com/api/v1/posts/?auth_token=demo&currencies=SOL"
}

def fetch_news_summary(symbol):
    symbol_key = symbol.split("/")[0]
    feed_url = RSS_FEEDS.get(symbol_key)
    if not feed_url:
        return "Sem fonte de notícia para esse ativo."
    try:
        response = requests.get(feed_url)
        if response.status_code == 200:
            data = response.json()
            if data.get("results"):
                latest = data["results"][0]
                return f"{latest['title']} ({latest['published_at'][:10]})"
        return "Notícia não encontrada."
    except Exception as e:
        return f"Erro ao buscar notícia: {e}"
