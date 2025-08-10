# -*- coding: utf-8 -*-
import os
import json
import time
from datetime import datetime

from config import (
    MIN_CONFIDENCE, DEBUG_SCORE, TOP_SYMBOLS,
    BATCH_OHLC, BATCH_PAUSE_SEC,
    SYMBOLS, DATA_RAW_FILE, SIGNALS_FILE
)
from coingecko_client import fetch_bulk_prices, fetch_ohlc, SYMBOL_TO_ID
from apply_strategies import generate_signal, score_signal
from notifier_telegram import send_signal_notification

def log(msg: str):
    print(msg, flush=True)

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def run_pipeline():
    # 1) preços/variação em BULK (1 chamada)
    log("🧩 Coletando PREÇOS em lote (bulk)…")
    bulk = fetch_bulk_prices(SYMBOLS)  # dict por TICKER ex.: {"BTCUSDT": {"usd":..., "usd_24h_change":...}}

    # 2) ranking por volatilidade 24h e seleção TOP N
    ranked = []
    for s in SYMBOLS:
        info = bulk.get(s)
        if not info:
            continue
        change = float(info.get("usd_24h_change", 0.0))
        ranked.append((s, abs(change)))
    ranked.sort(key=lambda t: t[1], reverse=True)
    selected = [sym for sym, _ in ranked[:max(1, int(TOP_SYMBOLS))]]
    log(f"✅ Selecionados para OHLC: {', '.join(selected)}")

    # 3) coleta OHLC em blocos com pausa
    all_data = []
    for idx, block in enumerate(chunks(selected, max(1, int(BATCH_OHLC)))):
        if idx > 0:
            log(f"⏸️ Pausa de {BATCH_PAUSE_SEC}s entre blocos para respeitar limites…")
            time.sleep(BATCH_PAUSE_SEC)
        for s in block:
            cid = SYMBOL_TO_ID.get(s, s.replace("USDT","").lower())
            log(f"📊 Coletando OHLC {s}…")
            data = fetch_ohlc(cid, days=7)
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

    # 4) salva bruto
    with open(DATA_RAW_FILE, "w") as f:
        json.dump(all_data, f, indent=2)
    log(f"💾 Salvo {DATA_RAW_FILE} ({len(all_data)} ativos)")

    # 5) gera, filtra e publica
    threshold = MIN_CONFIDENCE if MIN_CONFIDENCE <= 1 else MIN_CONFIDENCE / 100.0
    approved = []
    for item in all_data:
        s = item["symbol"]
        sig = generate_signal(s, item["ohlc"])  # retorna entry/tp/sl/confidence (0..1)
        if sig:
            approved.append(sig)
            log(f"✅ {s} aprovado ({int(sig['confidence']*100)}%)")

            # 🔔 formata pro notifier (campos no seu padrão)
            wire = {
                "symbol": s,
                "entry_price": sig["entry"],
                "target_price": sig["tp"],
                "stop_loss": sig["sl"],
                "risk_reward": sig.get("risk_reward") or sig.get("rr"),  # se existir
                "confidence_score": round(sig["confidence"]*100, 2),
                "strategy": sig.get("strategy","RSI+MACD+EMA+BB"),
                "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "id": f"{s}-{int(time.time())}"
            }
            send_signal_notification(wire)

        else:
            if DEBUG_SCORE:
                closes = [c["close"] for c in item["ohlc"]]
                sc = score_signal(closes)
                shown = "None" if sc is None else f"{round(sc*100,1)}%"
                log(f"ℹ️ Score {s}: {shown} (min {int(threshold*100)}%)")
            else:
                log(f"⛔ {s} descartado (<{int(threshold*100)}%)")

    # 6) persiste sinais aprovados
    with open(SIGNALS_FILE, "w") as f:
        json.dump(approved, f, indent=2)
    log(f"💾 {len(approved)} sinais salvos em {SIGNALS_FILE}")

    log(f"🕒 Fim: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")

if __name__ == "__main__":
    run_pipeline()
