# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime

from coingecko_client import fetch_bulk_prices, fetch_ohlc
from apply_strategies import generate_signal
from publisher import publish_many

# ===== CONFIG =====
MIN_CONFIDENCE = float(os.getenv("MIN_CONFIDENCE", "0.75"))
TOP_SYMBOLS = int(os.getenv("TOP_SYMBOLS", "20"))  # Usando todas as 20 moedas
DEBUG_SCORE = os.getenv("DEBUG_SCORE", "false").lower() == "true"

# Lista de 20 pares
SYMBOL_TO_ID = {
    "BTCUSDT":  "bitcoin",
    "ETHUSDT":  "ethereum",
    "BNBUSDT":  "binancecoin",
    "XRPUSDT":  "ripple",
    "ADAUSDT":  "cardano",
    "SOLUSDT":  "solana",
    "DOGEUSDT": "dogecoin",
    "MATICUSDT":"matic-network",
    "DOTUSDT":  "polkadot",
    "LTCUSDT":  "litecoin",
    "TRXUSDT":  "tron",
    "LINKUSDT": "chainlink",
    "AVAXUSDT": "avalanche-2",
    "BCHUSDT":  "bitcoin-cash",
    "ATOMUSDT": "cosmos",
    "XLMUSDT":  "stellar",
    "FILUSDT":  "filecoin",
    "APTUSDT":  "aptos",
    "INJUSDT":  "injective-protocol",
    "ARBUSDT":  "arbitrum",
}
SYMBOLS = list(SYMBOL_TO_ID.keys())

def log(msg):
    print(msg, flush=True)

def run_pipeline():
    # 1) Preços/variação em BULK (1 chamada)
    ids = [SYMBOL_TO_ID[s] for s in SYMBOLS]
    log("🧩 Coletando PREÇOS em lote (bulk)…")
    bulk = fetch_bulk_prices(ids)  # dict por ID do CG

    # 2) Ranking por volatilidade 24h e seleção TOP N
    ranked = []
    for s in SYMBOLS:
        cid = SYMBOL_TO_ID[s]
        info = bulk.get(cid)
        if not info: 
            continue
        change = float(info.get("usd_24h_change", 0.0))
        ranked.append((s, abs(change)))

    ranked.sort(key=lambda t: t[1], reverse=True)
    selected = [sym for sym, _ in ranked[:max(1, TOP_SYMBOLS))]
    log(f"✅ Selecionados para OHLC: {', '.join(selected)}")

    # 3) Coleta OHLC só dos selecionados
    all_data = []
    for s in selected:
        cid = SYMBOL_TO_ID[s]
        log(f"📊 Coletando OHLC {s}…")
        data = fetch_ohlc(cid, days=1)
        if data:
            candles = []
            for row in data:
                ts, o, h, l, c = row
                candles.append({
                    "timestamp": int(ts/1000),
                    "open": float(o),
                    "high": float(h),
                    "low": float(l),
                    "close": float(c),
                })
            all_data.append({"symbol": s, "ohlc": candles})
            log(f"   → OK | candles={len(candles)}")
        else:
            log(f"   → ❌ Dados insuficientes para {s}")

    # 4) Salva bruto para auditoria
    with open("data_raw.json", "w") as f:
        json.dump(all_data, f, indent=2)
    log(f"💾 Salvo data_raw.json ({len(all_data)} ativos)")

    # 5) Gera e filtra sinais
    approved = []
    for item in all_data:
        s = item["symbol"]
        sig = generate_signal(s, item["ohlc"])
        if sig:
            approved.append(sig)
            log(f"✅ {s} aprovado ({int(sig['confidence']*100)}%)")
        else:
            if DEBUG_SCORE:
                # Log opcional para diagnóstico do score
                from statistics import fmean
                closes = [c["close"] for c in item["ohlc"]]
                sc = score_signal(closes)
                log(f"⛔ {s} descartado (score={None if sc is None else round(sc*100,1)}% < {int(MIN_CONFIDENCE*100)}%)")
            else:
                log(f"⛔ {s} descartado (<{int(MIN_CONFIDENCE*100)}%)")

    # 6) Persistência dos sinais aprovados
    with open("signals.json", "w") as f:
        json.dump(approved, f, indent=2)
    log(f"💾 {len(approved)} sinais salvos em signals.json")

    # 7) Publicação
    if approved:
        publish_many(approved)
        log("📨 Sinais enviados ao Telegram.")

    # 8) (Opcional) Registrar execução
    log(f"🕒 Fim: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")

if __name__ == "__main__":
    run_pipeline()
