# ai_predictor.py
import joblib
import os

MODEL_PATH = "ai_model/model.pkl"

def load_model():
    if os.path.exists(MODEL_PATH):
        try:
            return joblib.load(MODEL_PATH)
        except Exception as e:
            print(f"❌ Erro ao carregar modelo: {e}")
            return None
    else:
        print("⚠️ Nenhum modelo IA encontrado. Execute train.py primeiro.")
        return None

def predict_proba(model, features):
    try:
        proba = model.predict_proba([features])[0][1]  # probabilidade de "alta"
        return float(proba)
    except Exception as e:
        print(f"❌ Erro na predição: {e}")
        return None

def log_if_active(threshold):
    print(f"🤖 IA ativa | Threshold={int(threshold*100)}%")
