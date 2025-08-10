# -*- coding: utf-8 -*-
import time
from statistics import fmean
from indicators import rsi, macd, ema, bollinger
from config import MIN_CONFIDENCE

def score_signal(closes):
    # precisa de histórico mínimo para EMAs/BB e cruzamentos
    if closes is None or len(closes) < 60:
        return None

    r = rsi(closes, 14)
    macd_line, signal_line, hist = macd(closes, 12, 26, 9)
    ema20 = ema(closes, 20)
    ema50 = ema(closes, 50)
    bb_up, bb_mid, bb_low = bollinger(closes, 20, 2.0)

    i = len(closes) - 1
    # guarda pra cruzamento não estourar índice
    if i < 1 or r[i] is None or ema20[i] is None or ema50[i] is None or bb_low[i] is None:
        return None

    c = closes[i]

    is_rsi_bull   = 45 <= r[i] <= 65
    is_macd_cross = (macd_line[i] > signal_line[i] and macd_line[i-1] <= signal_line[i-1])
    is_trend_up   = ema20[i] > ema50[i]
    near_bb_low   = c <= bb_low[i] * 1.01

    s_rsi   = 1.0 if is_rsi_bull else (0.6 if 40 <= r[i] <= 70 else 0.0)
    s_macd  = 1.0 if is_macd_cross else (0.7 if hist[i] > 0 else 0.2)
    s_trend = 1.0 if is_trend_up else 0.3
    s_bb    = 1.0 if near_bb_low else 0.5

    score = fmean([s_rsi, s_macd, s_trend, s_bb])

    # normalização leve por volatilidade recente
    recent = [abs(h) for h in hist[-20:] if h is not None]
    if recent and hist[i] is not None:
        vol_boost = min(max(abs(hist[i]) / (max(recent) + 1e-9), 0.0), 1.0)
        score = 0.85 * score + 0.15 * vol_boost

    return max(0.0, min(1.0, score))

def build_trade_plan(closes, risk_ratio_tp=2.0, risk_ratio_sl=1.0):
    if closes is None or len(closes) < 30:
        return None
    diffs = [abs(closes[j] - closes[j-1]) for j in range(-15, 0)]
    if not diffs:
        return None
    import statistics
    last = float(closes[-1])
    atr_like = float(statistics.fmean(diffs))
    sl = last - (atr_like * risk_ratio_sl)
    tp = last + (atr_like * risk_ratio_tp)
    return {"entry": last, "tp": tp, "sl": sl, "rr": (tp - last) / (last - sl) if (last - sl) != 0 else None}

def generate_signal(symbol, candles):
    if not candles:
        return None
    closes = [c["close"] for c in candles if "close" in c]
    score = score_signal(closes)
    if score is None:
        return None

    plan = build_trade_plan(closes)
    if plan is None:
        return None

    sig = {
        "symbol": symbol,
        "timestamp": int(time.time()),
        "confidence": round(score, 4),
        "entry": float(plan["entry"]),
        "tp": float(plan["tp"]),
        "sl": float(plan["sl"]),
        "strategy": "RSI+MACD+EMA+BB",
        "source": "coingecko"
    }
    # opcional para seu notifier (se não usar, ele ignora)
    if plan.get("rr") is not None:
        sig["risk_reward"] = round(plan["rr"], 2)

    if sig["confidence"] < MIN_CONFIDENCE:
        return None
    return sig
