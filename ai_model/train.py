# ai_model/train.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import os, json, sys

# 🔧 Corrige caminho para acessar arquivos da raiz do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from indicators import rsi, macd, ema, bollinger
from apply_strategies import score_signal
from config import DATA_RAW_FILE

SAVE_PATH = "ai_model/model.pkl"

def build_features_from_closes(closes):
    if not closes or len(closes) < 60:
        return None, None
    R = rsi(closes, 14)
    M, S, H = macd(closes, 12, 26, 9)
    E20 = ema(closes, 20)
    E50 = ema(closes, 50)
    Bup, Bmid, Blow = bollinger(closes, 20, 2.0)
    i = len(closes) - 1
    vals = [R[i], M[i], S[i], H[i], E20[i], E50[i], Bup[i], Bmid[i], Blow[i]]
    if any(v is None for v in vals): return None, None
    sc = score_signal(closes)
    sc_val = sc[0] if isinstance(sc, tuple) else sc
    if sc_val is None: return None, None
    feats = [float(v) for v in vals] + [float(sc_val)]
    return feats, sc_val

def load_training_data():
    if not os.path.exists(DATA_RAW_FILE):
        raise FileNotFoundError(f"{DATA_RAW_FILE} não encontrado. Rode o pipeline primeiro.")

    with open(DATA_RAW_FILE) as f:
        raw = json.load(f)

    X, y = [], []
    for item in raw:
        closes = [c["close"] for c in item["ohlc"]]
        feats, sc_val = build_features_from_closes(closes)
        if feats is not None:
            X.append(feats)
            # regra simples: se último fechamento maior que penúltimo → alvo=1 (alta), senão=0
            y.append(1 if closes[-1] > closes[-2] else 0)

    return np.array(X), np.array(y)

def train_model():
    X, y = load_training_data()
    if len(X) < 50:
        print("⚠️ Poucos dados para treinar IA.")
        return

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    acc = model.score(X_test, y_test)
    print(f"✅ Modelo treinado com acurácia={acc:.2f}")

    joblib.dump(model, SAVE_PATH)
    print(f"📁 Modelo salvo em {SAVE_PATH}")

if __name__ == "__main__":
    train_model()
