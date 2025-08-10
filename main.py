# -*- coding: utf-8 -*-
import os
import json
import time
from datetime import datetime

from config import (
    MIN_CONFIDENCE, TOP_SYMBOLS, DEBUG_SCORE,
    BATCH_OHLC, BATCH_PAUSE_SEC,
    DATA_RAW_FILE, SIGNALS_FILE
)
from coingecko_client import fetch_bulk_prices, fetch_ohlc, SYMBOL_TO_ID
from apply_strategies import generate_signal, score_signal
from publisher import publish_many

def log(msg: str):
    print(msg, flush=True)

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def run_pipeline():
        # 0) prepara lista de símbolos (20 pares do mapping)
    SYMBOLS = list(SYMBOL_TO_ID.keys())

    # 1) preços/variação em BULK (1 chamada)
    ids = [SYMBOL_TO_ID[s] for s in SYMBOLS]
    log("🧩 Coletando PREÇOS em lote (bulk)…")
    bulk = fetch_bulk_prices(ids)  # dict por ID do CG (ex.: {"bitcoin": {...}})

    # 2) ranking por volatilidade 24h e seleção TOP N
    ranked = []
    for s in SYMBOLS:
        cid = SYMBOL_TO_ID[s]
        info = bulk.get(cid)
        if not info:
            continue
        change = float(info.get("usd_24h_change", 0.0))
        ranked.append((s, abs(change)))

    ranked.sort(key=lambda t: t[1], reverse=True)
    selected = [sym for sym, _ in ranked[:max(1, int(TOP_SYMBOLS))]]
    log(f"✅ Selecionados para OHLC: {', '.join(selected)}")

    # 3) coleta OHLC em blocos com pausa entre blocos
    all_data = []
    blocks = list(chunks(selected, max(1, int(BATCH_OHLC))))
    for b_index, block in enumerate(blocks):
        if b_index > 0:
            log(f"⏸️ Pausa de {BATCH_PAUSE_SEC}s para respeitar limites…")
            time.sleep(BATCH_PAUSE_SEC)

        for s in block:
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

    # 4) salva bruto para auditoria
    with open(DATA_RAW_FILE, "w") as f:
        json.dump(all_data, f, indent=2)
    log(f"💾 Salvo {DATA_RAW_FILE} ({len(all_data)} ativos)")

    # 5) gera e filtra sinais
    threshold_pct = MIN_CONFIDENCE if MIN_CONFIDENCE <= 1 else MIN_CONFIDENCE / 100.0
    approved = []
    for item in all_data:
        s = item["symbol"]
        sig = generate_signal(s, item["ohlc"])
        if sig:
            approved.append(sig)
            log(f"✅ {s} aprovado ({int(sig['confidence']*100)}%)")
        else:
            if DEBUG_SCORE:
                closes = [c["close"] for c in item["ohlc"]]
                sc = score_signal(closes)
                shown = "None" if sc is None else f"{round(sc*100,1)}%"
                log(f"ℹ️ Score {s}: {shown} (min {int(threshold_pct*100)}%)")
            else:
                log(f"⛔ {s} descartado (<{int(threshold_pct*100)}%)")

    # 6) persistência dos sinais aprovados
    with open(SIGNALS_FILE, "w") as f:
        json.dump(approved, f, indent=2)
    log(f"💾 {len(approved)} sinais salvos em {SIGNALS_FILE}")

    # 7) publicação
    if approved:
        publish_many(approved)
        log("📨 Sinais enviados ao Telegram.")

    # 8) log final
    log(f"🕒 Fim: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")

if __name__ == "__main__":
    run_pipeline()
