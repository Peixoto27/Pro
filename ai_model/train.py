# ai_model/train.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# Exemplo: carregar CSV ou DataFrame de candles + indicadores
# Aqui você vai adaptar para os dados do seu projeto
def load_data(csv_path="data.csv"):
    df = pd.read_csv(csv_path)
    # Features: indicadores técnicos
    X = df[["rsi", "macd", "ema20", "ema50", "adx"]]
    # Target: direção futura (1=alta, 0=baixa)
    y = df["future_direction"]
    return X, y

def train_model():
    X, y = load_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    acc = model.score(X_test, y_test)
    print(f"✅ Modelo treinado! Acurácia: {acc:.2f}")

    joblib.dump(model, "ai_model/model.pkl")
    print("📁 Modelo salvo em ai_model/model.pkl")

if __name__ == "__main__":
    train_model()
