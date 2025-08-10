import joblib
import pandas as pd
import numpy as np

MODEL_FILE = "ai_model.pkl"

FEATURES = [
    "symbol",
    "rsi", "macd_diff", "sma_ratio", "volume_ratio",
    "volatility", "momentum", "sentiment_score",
    "hour_of_day", "day_of_week", "confidence_score",
]

_model = None

def load_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_FILE)
    return _model

def _ensure_row_schema(row: dict) -> pd.DataFrame:
    safe = {}
    for k in FEATURES:
        if k not in row:
            safe[k] = 0 if k != "symbol" else "BTCUSDT"
        else:
            safe[k] = row[k]
    for c in [f for f in FEATURES if f != "symbol"]:
        try:
            safe[c] = float(safe[c])
        except:
            safe[c] = 0.0
    safe["symbol"] = str(safe["symbol"])
    return pd.DataFrame([safe], columns=FEATURES)

def predict_success_proba(feature_row: dict) -> float:
    try:
        model = load_model()
        X = _ensure_row_schema(feature_row)
        proba = model.predict_proba(X)[0, 1]
        return float(np.clip(proba, 0.0, 1.0))
    except Exception as e:
        print(f"[AI] Falha na predição: {e}")
        return 0.5
