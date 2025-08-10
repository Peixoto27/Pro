import os

def getenv_float(key, default):
    try:
        return float(os.getenv(key, str(default)))
    except:
        return default

TRAINING_ENABLED = os.getenv("TRAINING_ENABLED", "false").lower() == "true"
MIN_CONFIDENCE   = getenv_float("MIN_CONFIDENCE", 0.75)
INTERVAL_MINUTES = int(getenv_float("INTERVAL_MINUTES", 20))
API_DELAY_SEC    = getenv_float("API_DELAY_SEC", 2.5)
LOG_LEVEL        = os.getenv("LOG_LEVEL", "INFO").upper()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")
