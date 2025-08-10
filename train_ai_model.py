import os, json, joblib
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score, accuracy_score
from sklearn.ensemble import RandomForestClassifier

# tenta usar XGBoost; se não tiver, cai para RandomForest
try:
    from xgboost import XGBClassifier
    USE_XGB = True
except Exception:
    USE_XGB = False

DATA_FILE = os.getenv("AI_TRAIN_DATA_FILE", "ai_training_data.json")
MODEL_FILE = os.getenv("AI_MODEL_FILE", "ai_model.pkl")
MIN_SAMPLES_TO_TRAIN = int(os.getenv("AI_MIN_SAMPLES", "200"))     # mínimo p/ primeiro treino
RETRAIN_DELTA = int(os.getenv("AI_RETRAIN_DELTA", "50"))           # só retreina se houver +N amostras novas

BASE_FEATURES = [
    "rsi","macd_diff","sma_ratio","volume_ratio",
    "volatility","momentum","sentiment_score",
    "hour_of_day","day_of_week","confidence_score"
]

def load_training_df() -> pd.DataFrame:
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"{DATA_FILE} não encontrado.")
    with open(DATA_FILE, "r") as f:
        raw = json.load(f)
    if not raw:
        raise ValueError("Arquivo de dados está vazio.")

    df = pd.DataFrame(raw)

    # cria 'target' se necessário
    if "result" in df.columns and "target" not in df.columns:
        df["target"] = (df["result"] == "success").astype(int)

    keep_cols = ["symbol","created_at"] + BASE_FEATURES + ["target"]
    for c in keep_cols:
        if c not in df.columns:
            # cria coluna ausente com 0
            df[c] = 0

    df = df[keep_cols].copy()
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df = df.dropna(subset=["created_at"])
    df = df.replace([np.inf, -np.inf], np.nan).dropna()

    # ordena por tempo (anti-leak)
    df = df.sort_values("created_at")
    return df

def build_pipeline(symbols_fit: np.ndarray) -> Pipeline:
    numeric = BASE_FEATURES
    categorical = ["symbol"]

    pre = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric),
            ("cat", OneHotEncoder(handle_unknown="ignore",
                                  categories=[sorted(np.unique(symbols_fit))]), categorical),
        ],
        remainder="drop"
    )

    if USE_XGB:
        model = XGBClassifier(
            n_estimators=400,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            reg_lambda=1.0,
            eval_metric="logloss",
            tree_method="hist",
            random_state=42
        )
    else:
        model = RandomForestClassifier(
            n_estimators=600,
            max_depth=None,
            min_samples_leaf=2,
            class_weight="balanced",
            n_jobs=-1,
            random_state=42
        )

    return Pipeline(steps=[("pre", pre), ("clf", model)])

def should_retrain(current_count: int) -> bool:
    meta_path = MODEL_FILE + ".meta.json"
    if not os.path.exists(MODEL_FILE):   # nunca treinou
        return current_count >= MIN_SAMPLES_TO_TRAIN
    last = 0
    if os.path.exists(meta_path):
        try:
            with open(meta_path,"r") as f:
                last = int(json.load(f).get("trained_on_samples", 0))
        except Exception:
            pass
    return (current_count - last) >= RETRAIN_DELTA

def save_meta(samples: int, acc: float, auc: float, ver: str):
    meta_path = MODEL_FILE + ".meta.json"
    with open(meta_path,"w") as f:
        json.dump({
            "trained_on_samples": int(samples),
            "version": ver,
            "acc": float(acc),
            "auc": float(auc)
        }, f, indent=2)

def main():
    df = load_training_df()
    total = len(df)
    if not should_retrain(total):
        print(f"[AI] Sem retreinamento: amostras={total}. Aguardando novos dados.")
        return

    X = df.drop(columns=["target","created_at"])
    y = df["target"].values

    # split temporal simples 80/20 (já está ordenado por data)
    split_idx = int(len(df)*0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    pipe = build_pipeline(symbols_fit=X_train["symbol"].values)
    pipe.fit(X_train, y_train)

    # métricas
    proba = pipe.predict_proba(X_test)[:,1] if len(X_test) else np.array([])
    pred  = (proba >= 0.5).astype(int) if len(proba) else np.array([])
    acc = accuracy_score(y_test, pred) if len(pred) else float("nan")
    auc = roc_auc_score(y_test, proba) if len(np.unique(y_test))>1 and len(proba) else float("nan")

    # salva
    joblib.dump(pipe, MODEL_FILE)
    ver = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    joblib.dump(pipe, f"ai_model_v{ver}.pkl")
    save_meta(total, acc, auc, ver)

    print(f"[AI] Treino concluído | samples={total} | ACC={acc:.4f} | AUC={auc:.4f} | ver={ver}")

if __name__ == "__main__":
    main()
