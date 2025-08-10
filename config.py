# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
load_dotenv()

def getenv_float(k, d): 
    try: return float(os.getenv(k, str(d)))
    except: return d

TRAINING_ENABLED = os.getenv("TRAINING_ENABLED","false").lower() == "true"
MIN_CONFIDENCE   = getenv_float("MIN_CONFIDENCE", 0.75)

# ▶️ aumentei o delay padrão para 5s
API_DELAY_SEC    = getenv_float("API_DELAY_SEC", 5.0)

# ▶️ novos parâmetros para lidar com 429
MAX_RETRIES      = int(getenv_float("MAX_RETRIES", 4))
BACKOFF_BASE     = getenv_float("BACKOFF_BASE", 2.0)
BATCH_SIZE       = int(getenv_float("BATCH_SIZE", 10))   # ids por chamada bulk

LOG_LEVEL        = os.getenv("LOG_LEVEL", "INFO").upper()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")
