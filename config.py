# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
load_dotenv()

def getenv_float(k, d):
    try:
        return float(os.getenv(k, str(d)))
    except:
        return d

TRAINING_ENABLED = os.getenv("TRAINING_ENABLED","false").lower() == "true"
MIN_CONFIDENCE   = getenv_float("MIN_CONFIDENCE", 0.75)

API_DELAY_SEC    = getenv_float("API_DELAY_SEC", 5.0)  # delay padrão mais alto
MAX_RETRIES      = int(getenv_float("MAX_RETRIES", 4))
BACKOFF_BASE     = getenv_float("BACKOFF_BASE", 2.0)
BATCH_SIZE       = int(getenv_float("BATCH_SIZE", 10))

TOP_SYMBOLS      = int(os.getenv("TOP_SYMBOLS", "8"))   # <- novo

LOG_LEVEL        = os.getenv("LOG_LEVEL", "INFO").upper()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")
# Delay entre chamadas à API CoinGecko (segundos)
API_DELAY_BULK = 2.5    # para /simple/price
API_DELAY_OHLC = 2.5    # para /ohlc

# Quantidade máxima de tentativas por chamada
MAX_RETRIES = 4

# Tempo base de espera no backoff exponencial
BACKOFF_BASE = 2
