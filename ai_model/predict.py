# ai_model/predict.py
import joblib
import numpy as np
import sys, os

# 🔧 Corrige caminho para acessar raiz do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from indicators import rsi, macd, ema, bollinger
from apply_strategies import score_signal

MODEL_PATH = "ai_model/model.pkl"

# Carregar modelo salvo
model = joblib.load(MODEL_PATH)

def predict_signal(closes):
    """Recebe lista de preços de fechamento e retorna previsão"""
    if len(closes) < 60:
        return None

    R = rsi(closes, 14)
    M, S, H = macd(closes, 12, 26, 9)
    E20 = ema(closes, 20)
    E50 = ema(closes, 50)
    Bup, Bmid, Blow = bollinger(closes, 20, 2.0)

    i = len(closes) - 1
    feats = [R[i], M[i], S[i], H[i], E20[i], E50[i], Bup[i], Bmid[i], Blow[i]]
    sc = score_signal(closes)
    sc_val = sc[0] if isinstance(sc, tuple) else sc
    feats.append(sc_val)

    X_input = np.array([feats])
    pred = model.predict(X_input)[0]
    proba = model.predict_proba(X_input)[0]

    return {
        "prediction": int(pred),       # 1 = alta, 0 = baixa
        "confidence_up": float(proba[1]),
        "confidence_down": float(proba[0])
    }

# 🔎 Exemplo rápido
if __name__ == "__main__":
    closes = [i for i in range(100, 160)]  # sequência fictícia
    result = predict_signal(closes)
    print("Teste de previsão:", result)
