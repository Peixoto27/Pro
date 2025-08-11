# -*- coding: utf-8 -*-
import os, json, time
from datetime import datetime

from config import (
    MIN_CONFIDENCE, DEBUG_SCORE, TOP_SYMBOLS,
    BATCH_OHLC, BATCH_PAUSE_SEC, SYMBOLS,
    DATA_RAW_FILE, SIGNALS_FILE, OHLC_DAYS
)
from coingecko_client import fetch_bulk_prices, fetch_ohlc, SYMBOL_TO_ID
from apply_strategies import generate_signal, score_signal
from notifier_telegram import send_signal_notification

def log(msg): print(msg, flush=True)
def chunks(lst, n): 
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def run_pipeline():
    log("🧩 Coletando PREÇOS em lote (bulk)…")
    bulk = fetch_bulk_prices(SYMBOLS)

    ranked = []
    for s in SYMBOLS:
        info = bulk.get(s)
        if not info: 
            continue
        ranked.append((s, abs(float(info.get("usd_24h_change", 0.0)))))
    ranked.sort(key=lambda t: t[1], reverse=True)
    selected = [sym for sym, _ in ranked[:max(1, int(TOP_SYMBOLS))]]
    log(f"✅ Selecionados para OHLC: {', '.join(selected)}")

    all_data = []
    for idx, block in enumerate(chunks(selected, max(1, int(BATCH_OHLC)))):
        if idx > 0:
            log(f"⏸️ Pausa de {BATCH_PAUSE_SEC}s entre blocos…")
            time.sleep(BATCH_PAUSE_SEC)
        for s in block:
            cid = SYMBOL_TO_ID.get(s, s.replace("USDT","").lower())
            log(f"📊 Coletando OHLC {s} (days={OHLC_DAYS})…")
            data = fetch_ohlc(cid, days=OHLC_DAYS)
            if data:
                candles = [{"timestamp": int(ts/1000), "open": float(o), "high": float(h),
                            "low": float(l), "close": float(c)} for ts,o,h,l,c in data]
                all_data.append({"symbol": s, "ohlc": candles})
                log(f"   → OK | candles={len(candles)}")
            else:
                log(f"   → ❌ Dados insuficientes para {s}")

    with open(DATA_RAW_FILE, "w") as f:
        json.dump(all_data, f, indent=2)
    log(f"💾 Salvo {DATA_RAW_FILE} ({len(all_data)} ativos)")

    thr = MIN_CONFIDENCE if MIN_CONFIDENCE <= 1 else MIN_CONFIDENCE / 100.0
    approved = []
    for item in all_data:
        s = item["symbol"]
        sig = generate_signal(s, item["ohlc"])
        if sig:
            approved.append(sig)
            log(f"✅ {s} aprovado ({int(sig['confidence']*100)}%)")

            wire = {
                "symbol": s,
                "entry_price": sig["entry"],
                "target_price": sig["tp"],
                "stop_loss": sig["sl"],
                "risk_reward": sig.get("risk_reward"),
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
                if sc is None:
                    shown = "None"
                else:
                    sc_val = sc[0] if isinstance(sc, tuple) else sc
                    shown = f"{round(sc_val*100,1)}%"
                log(f"ℹ️ Score {s}: {shown} (min {int(thr*100)}%)")
            else:
                log(f"⛔ {s} descartado (<{int(thr*100)}%)")

    with open(SIGNALS_FILE, "w") as f:
        json.dump(approved, f, indent=2)
    log(f"💾 {len(approved)} sinais salvos em {SIGNALS_FILE}")
    log(f"🕒 Fim: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")

if __name__ == "__main__":
    run_pipeline()
