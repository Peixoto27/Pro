# -*- coding: utf-8 -*-
import json
from scanner import main as collect_now
from apply_strategies import generate_signal
from publisher import publish_many
from config import MIN_CONFIDENCE
import train_ai_model

def load_raw():
    with open("data_raw.json","r") as f:
        return json.load(f)

def run_pipeline():
    # 1) coleta
    collect_now()

    # 2) geração de sinais
    raw = load_raw()
    approved = []
    for item in raw:
        symbol = item["symbol"]
        candles = item["ohlc"]
        sig = generate_signal(symbol, candles)
        if sig:
            approved.append(sig)
            print(f"✅ {symbol} aprovado ({int(sig['confidence']*100)}%)")
        else:
            print(f"⛔ {symbol} descartado (<{int(MIN_CONFIDENCE*100)}%)")

    # 3) persiste
    with open("signals.json","w") as f:
        json.dump(approved, f, indent=2)
    print(f"💾 {len(approved)} sinais salvos em signals.json")

    # 4) publica (Telegram)
    if approved:
        publish_many(approved)
        print("📨 Sinais enviados ao Telegram.")

    # 5) treino opcional
    train_ai_model.main()

if __name__ == "__main__":
    run_pipeline()
