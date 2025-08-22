# ai_model/predict.py
import joblib
import numpy as np

# Carregar modelo treinado
model = joblib.load("ai_model/model.pkl")

def predict_signal(rsi, macd, ema20, ema50, adx):
    X_input = np.array([[rsi, macd, ema20, ema50, adx]])
    pred = model.predict(X_input)[0]
    prob = model.predict_proba(X_input)[0]
    return {
        "prediction": int(pred),  # 1=alta, 0=baixa
        "confidence": float(max(prob))
    }

# Exemplo rápido
if __name__ == "__main__":
    print(predict_signal(45, -0.01, 2.5, 2.6, 18))
