import joblib
import pandas as pd

MODEL_FILE = "ai_model.pkl"

_model = None
FEATURES = [
    "symbol",
    "rsi","macd_diff","sma_ratio","volume_ratio",
    "volatility","momentum","sentiment_score",
    "hour_of_day","day_of_week","confidence_score"
]

def load_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_FILE)
    return _model

def predict_success_proba(feature_row: dict) -> float:
    """
    feature_row deve conter todas as chaves de FEATURES.
    retorna probabilidade (0..1) de o sinal ser 'bom'.
    """
    model = load_model()
    X = pd.DataFrame([feature_row], columns=FEATURES)
    return float(model.predict_proba(X)[0,1])
