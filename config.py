# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

# Carrega .env da raiz
load_dotenv()

# ===== Qualidade / Debug =====
# Use 0.75 (fração). Se quiser 75 (percentual), adapte no apply_strategies.
MIN_CONFIDENCE = float(os.getenv("MIN_CONFIDENCE", "0.75"))
DEBUG_SCORE    = os.getenv("DEBUG_SCORE", "false").lower() == "true"
LOG_LEVEL      = os.getenv("LOG_LEVEL", "INFO").upper()

# ===== Seleção de pares =====
# Ex.: "BTCUSDT,ETHUSDT,BNBUSDT"
SYMBOLS = [s.strip() for s in os.getenv(
    "SYMBOLS",
    "BTCUSDT,ETHUSDT,BNBUSDT,XRPUSDT,ADAUSDT,DOGEUSDT,SOLUSDT,MATICUSDT,DOTUSDT,LTCUSDT,LINKUSDT"
).split(",") if s.strip()]

# ===== Delays / Retry (CoinGecko) =====
API_DELAY_BULK  = float(os.getenv("API_DELAY_BULK", 2.5))   # /simple/price
API_DELAY_OHLC  = float(os.getenv("API_DELAY_OHLC", 12.0))  # /ohlc
MAX_RETRIES     = int(os.getenv("MAX_RETRIES", 6))
BACKOFF_BASE    = float(os.getenv("BACKOFF_BASE", 2.5))

# Batching para OHLC (se seu main usar blocos)
BATCH_OHLC       = int(os.getenv("BATCH_OHLC", 8))
BATCH_PAUSE_SEC  = int(os.getenv("BATCH_PAUSE_SEC", 60))

# ===== Telegram (se usar no notifier) =====
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", os.getenv("BOT_TOKEN", ""))
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", os.getenv("CHAT_ID", ""))

# ===== Arquivos =====
DATA_RAW_FILE = os.getenv("DATA_RAW_FILE", "data_raw.json")
SIGNALS_FILE  = os.getenv("SIGNALS_FILE",  "signals.json")
HISTORY_FILE  = os.getenv("HISTORY_FILE",  "history.json")
