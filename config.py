import os

# === Configurações Gerais ===
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
DEBUG_SCORE = os.getenv("DEBUG_SCORE", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# === API Keys ===
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

# === Configurações de Sinais ===
MIN_CONFIDENCE = float(os.getenv("MIN_CONFIDENCE", 75))  # publicar sinais acima de 75%
MAX_SYMBOLS = int(os.getenv("MAX_SYMBOLS", 20))          # máximo de moedas analisadas
TOP_SYMBOLS = int(os.getenv("TOP_SYMBOLS", 20))          # quantas moedas rankear p/ OHLC

# === Configurações de Delay e Tentativas para CoinGecko ===
API_DELAY_BULK = float(os.getenv("API_DELAY_BULK", 2.5))  # segundos entre chamadas de preço em lote
API_DELAY_OHLC = float(os.getenv("API_DELAY_OHLC", 12.0)) # segundos entre chamadas OHLC
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 6))            # número máximo de tentativas
BACKOFF_BASE = float(os.getenv("BACKOFF_BASE", 2.5))      # tempo base para backoff exponencial

# === Configuração de Batching ===
BATCH_OHLC = int(os.getenv("BATCH_OHLC", 8))              # quantos OHLC por bloco
BATCH_PAUSE_SEC = int(os.getenv("BATCH_PAUSE_SEC", 60))   # pausa entre blocos (segundos)

# === Configuração do Telegram ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# === Pastas e Arquivos ===
DATA_RAW_FILE = "data_raw.json"
SIGNALS_FILE = "signals.json"
MODEL_FILE = "model.pkl"
