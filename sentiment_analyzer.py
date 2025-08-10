# sentiment_analyzer.py — otimizado p/ produção
import os
import time
from collections import deque
from typing import List, Optional

from textblob import TextBlob
from news_fetcher import get_recent_news  # deve existir no projeto

# ========================
# Configs (ajustáveis via env)
# ========================
HOURLY_API_CALL_LIMIT = int(os.getenv("SENTI_HOURLY_LIMIT", "10"))          # chamadas/hora
CACHE_DURATION        = int(os.getenv("SENTI_CACHE_SECONDS", str(2*60*60))) # 2h por padrão
STALE_GRACE_SECONDS   = int(os.getenv("SENTI_STALE_GRACE", str(24*60*60)))  # usar cache vencido até 24h se API falhar
NEWS_LIMIT_PER_QUERY  = int(os.getenv("SENTI_NEWS_LIMIT", "8"))             # qtde de notícias buscadas
MIN_NEWS_FOR_SIGNAL   = int(os.getenv("SENTI_MIN_NEWS", "2"))               # mínimo p/ média; senão neutro

# ========================
# Estado
# ========================
api_call_timestamps: deque[float] = deque()
sentiment_cache = {}  # { symbol: {"score": float, "timestamp": float } }

# Nome legível para consulta de notícias
_SYMBOL_MAP = {
    "BTCUSDT": "Bitcoin",      "ETHUSDT": "Ethereum",     "BNBUSDT": "Binance Coin",
    "SOLUSDT": "Solana",       "XRPUSDT": "XRP",          "ADAUSDT": "Cardano",
    "AVAXUSDT": "Avalanche",   "DOTUSDT": "Polkadot",     "LINKUSDT": "Chainlink",
    "TONUSDT": "Toncoin",      "INJUSDT": "Injective",    "RNDRUSDT": "Render Token",
    "ARBUSDT": "Arbitrum",     "LTCUSDT": "Litecoin",     "MATICUSDT": "Polygon",
    "OPUSDT": "Optimism",      "NEARUSDT": "NEAR",        "APTUSDT": "Aptos",
    "PEPEUSDT": "Pepe",        "SEIUSDT": "Sei",          "TRXUSDT": "TRON",
    "DOGEUSDT": "Dogecoin",    "SHIBUSDT": "Shiba Inu",   "FILUSDT": "Filecoin",
    "SUIUSDT": "Sui",
}

def _normalize_query(symbol: str) -> str:
    # tenta mapear; se não tiver, usa símbolo bruto sem sufixo comum
    if symbol in _SYMBOL_MAP:
        return _SYMBOL_MAP[symbol]
    # fallback simples: tira "USDT"/"USD"/"USDC"
    for suf in ("USDT", "USD", "USDC"):
        if symbol.endswith(suf):
            return symbol[:-len(suf)]
    return symbol

def _now() -> float:
    return time.time()

def can_make_api_call() -> bool:
    """Verifica janela de 1h para respeitar limite de chamadas."""
    now = _now()
    while api_call_timestamps and api_call_timestamps[0] < now - 3600:
        api_call_timestamps.popleft()
    if len(api_call_timestamps) < HOURLY_API_CALL_LIMIT:
        return True
    print("🚦 Limite/hora atingido. Usando fallback/cache.")
    return False

def _dedupe_titles(titles: List[str]) -> List[str]:
    seen = set()
    unique = []
    for t in titles:
        t = (t or "").strip()
        if not t:
            continue
        key = t.lower()
        if key not in seen:
            seen.add(key)
            unique.append(t)
    return unique

def _compute_polarity(titles: List[str]) -> float:
    if not titles:
        return 0.0
    total = 0.0
    n = 0
    for t in titles:
        try:
            total += TextBlob(t).sentiment.polarity  # [-1, 1]
            n += 1
        except Exception:
            continue
    if n == 0:
        return 0.0
    score = total / n
    # pequenas oscilações ~ruído → aproxima de zero
    if abs(score) < 0.05:
        score = 0.0
    # clamp/round
    return round(max(-1.0, min(1.0, score)), 2)

def _get_cache(symbol: str, now: float) -> Optional[float]:
    item = sentiment_cache.get(symbol)
    if not item:
        return None
    age = now - item["timestamp"]
    if age < CACHE_DURATION:
        print(f"🧠 Sentimento (cache válido) {symbol}: {item['score']:.2f}")
        return item["score"]
    return None  # cache vencido; pode servir como stale se API falhar

def _get_stale_if_allowed(symbol: str, now: float) -> Optional[float]:
    item = sentiment_cache.get(symbol)
    if not item:
        return None
    age = now - item["timestamp"]
    if age < CACHE_DURATION + STALE_GRACE_SECONDS:
        print(f"🧠 Sentimento (cache *stale* usado) {symbol}: {item['score']:.2f}")
        return item["score"]
    return None

def get_sentiment_score(symbol: str) -> float:
    """
    Retorna o sentimento médio [-1..1] para o símbolo.
    - Usa cache fresco quando disponível
    - Respeita cota/hora
    - Em caso de erro/limite, tenta cache 'stale'; se não houver, retorna 0.0
    """
    now = _now()

    # 1) tenta cache fresco
    cached = _get_cache(symbol, now)
    if cached is not None:
        return cached

    # 2) se não há cache fresco, verifica cota
    if not can_make_api_call():
        stale = _get_stale_if_allowed(symbol, now)
        return stale if stale is not None else 0.0

    # 3) fará chamada — registra consumo de cota
    api_call_timestamps.append(now)
    query = _normalize_query(symbol)
    print(f"🌐 Buscando notícias para {symbol} (query='{query}', limit={NEWS_LIMIT_PER_QUERY})…")

    try:
        # Ajuste a assinatura conforme seu news_fetcher
        titles = get_recent_news(query=query, limit=NEWS_LIMIT_PER_QUERY)
        titles = _dedupe_titles(titles or [])

        if len(titles) < MIN_NEWS_FOR_SIGNAL:
            score = 0.0
        else:
            score = _compute_polarity(titles)

        print(f"🧠 Sentimento calculado {symbol}: {score:.2f}")
        sentiment_cache[symbol] = {"score": score, "timestamp": now}
        return score

    except Exception as e:
        print(f"⚠️ Falha ao buscar notícias para {symbol}: {e}")
        # tenta usar cache stale
        stale = _get_stale_if_allowed(symbol, now)
        if stale is not None:
            return stale
        return 0.0
