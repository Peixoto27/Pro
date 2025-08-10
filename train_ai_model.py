# -*- coding: utf-8 -*-
import json
import os
from config import TRAINING_ENABLED

def load_dataset():
    if not os.path.exists("signals_history.json"):
        return []
    with open("signals_history.json","r") as f:
        return json.load(f)

def train(dataset):
    # placeholder simples
    return {"version": 1, "note": "bootstrap-weights"}

def save_model(model):
    with open("model.json","w") as f:
        json.dump(model, f, indent=2)

def main():
    if not TRAINING_ENABLED:
        print("[AI] Treino desabilitado por configuração. Pulando.")
        return
    data = load_dataset()
    if len(data) < 200:
        print("[AI] Dados insuficientes (<200). Pulando treino.")
        return
    model = train(data)
    save_model(model)
    print("[AI] Modelo treinado e salvo com sucesso.")

if __name__ == "__main__":
    main()
