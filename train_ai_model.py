import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score, accuracy_score, precision_recall_fscore_support
from sklearn.ensemble import RandomForestClassifier

try:
    from xgboost import XGBClassifier
    USE_XGB = True
except Exception:
    USE_XGB = False

DATA_FILE = "ai_training_data.json"
MODEL_FILE = "ai_model.pkl"
META_FILE = MODEL_FILE + ".meta.json"

MIN_SAMPLES_TO_TRAIN = 200
RETRAIN_DELTA = 50

NUMERIC_FEATURES = [
    "rsi", "macd_diff", "sma_ratio", "volume_ratio",
    "volatility", "momentum", "sentiment_score",
    "hour_of_day", "day_of_week", "confidence_score",
]
CATEGORICAL_FEATURES = ["symbol"]

def ensure_data_file():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)
        print("[AI] Arquivo de dados inicializado vazio. Aguardando coleta de sinais.")
        return False
    return True

def load_training_df():
    if not ensure_data_file():
        return pd.DataFrame()
    with open(DATA_FILE, "r") as f:
        raw = json.load(f)
    if not raw:
        return pd.DataFrame()
    df = pd.DataFrame(raw)
    if "target" not in df.columns and "result" in df.columns:
        df["target"] = (df["result"] == "success").astype(int)
    for c in NUMERIC_FEATURES:
        if c not in df.columns:
            df[c] = 0.0
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    else:
        df["created_at"] = pd.Timestamp.utcnow()
    return df.dropna(subset=["target"])

def build_pipeline():
    pre = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )
    if USE_XGB:
        model = XGBClassifier(
            n_estimators=500,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            reg_lambda=1.0,
            tree_method="hist",
            eval_metric="logloss",
            random_state=42,
        )
    else:
        model = RandomForestClassifier(
            n_estimators=700,
            max_depth=None,
            min_samples_leaf=2,
            class_weight="balanced",
            n_jobs=-1,
            random_state=42,
        )
    return Pipeline(steps=[("pre", pre), ("clf", model)])

def should_retrain(current_count):
    if not os.path.exists(META_FILE):
        return current_count >= MIN_SAMPLES_TO_TRAIN
    try:
        with open(META_FILE, "r") as f:
            meta = json.load(f)
        last = int(meta.get("trained_on_samples", 0))
        return (current_count - last) >= RETRAIN_DELTA
    except:
        return True

def main():
    df = load_training_df()
    if df.empty:
        print("[AI] Sem dados suficientes para treinar.")
        return
    if not should_retrain(len(df)):
        print("[AI] Modelo ainda válido. Nenhum retreinamento necessário.")
        return
    df = df.sort_values("created_at")
    split_idx = int(len(df) * 0.8)
    train_df, test_df = df.iloc[:split_idx], df.iloc[split_idx:]
    X_train, y_train = train_df[CATEGORICAL_FEATURES + NUMERIC_FEATURES], train_df["target"]
    X_test, y_test = test_df[CATEGORICAL_FEATURES + NUMERIC_FEATURES], test_df["target"]
    pipe = build_pipeline()
    pipe.fit(X_train, y_train)
    y_proba = pipe.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= 0.5).astype(int)
    acc = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba) if len(set(y_test)) > 1 else float("nan")
    pr, rc, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="binary", zero_division=0)
    joblib.dump(pipe, MODEL_FILE)
    version = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    meta = {
        "trained_on_samples": len(df),
        "version": version,
        "metrics": {"acc": acc, "auc": auc, "precision": pr, "recall": rc, "f1": f1},
        "timestamp_utc": datetime.utcnow().isoformat(),
    }
    with open(META_FILE, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"[AI] Treino concluído | Samples={len(df)} | ACC={acc:.4f} | AUC={auc:.4f} | F1={f1:.4f}")

if __name__ == "__main__":
    main()
