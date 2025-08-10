import subprocess
import os
import json
from datetime import datetime, timezone

LAST_TRAIN_FILE = "last_train.json"

def run_script(script_name):
    print(f"[MAIN] Executando: {script_name}")
    result = subprocess.call(["python", script_name])
    print(f"[MAIN] Finalizado: {script_name} (código {result})")
    return result

def should_train():
    if not os.path.exists(LAST_TRAIN_FILE):
        return True
    try:
        with open(LAST_TRAIN_FILE, "r") as f:
            data = json.load(f)
        last_run = datetime.fromisoformat(data.get("last_train"))
        diff_minutes = (datetime.now(timezone.utc) - last_run).total_seconds() / 60
        return diff_minutes >= 60
    except Exception:
        return True

def update_last_train():
    with open(LAST_TRAIN_FILE, "w") as f:
        json.dump({"last_train": datetime.now(timezone.utc).isoformat()}, f)

if __name__ == "__main__":
    print("\n========== NOVA EXECUÇÃO ==========")
    run_script("scanner.py")

    if should_train():
        print("[MAIN] Hora de treinar a IA...")
        run_script("train_ai_model.py")
        update_last_train()
    else:
        print("[MAIN] Treino pulado, menos de 1h desde o último.")

    print("========== EXECUÇÃO FINALIZADA ==========\n")
