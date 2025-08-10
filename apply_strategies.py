# -*- coding: utf-8 -*-
import time
from statistics import fmean
from indicators import rsi, macd, ema, bollinger
from config import MIN_CONFIDENCE
from history_manager import append_to_history

def score_signal(closes):
    if len(closes) < 60:
        return None
    r = rsi(closes, 14)
    macd_line, signal_line, hist = macd(closes, 12, 26, 9)
    ema20 = ema(closes, 20)
    ema50 = ema(closes, 50)
    bb_up, bb_mid, bb_low = bollinger(closes, 20, 2.0)

    i = len(closes) - 1
    c = closes[i]

    is_rsi_bull   = 45 <= r[i] <= 65 if r[i] is not None else False
    is_macd_cross = (macd_line[i] > signal_line[i] and macd_line[i-1] <= signal_line[i-1])
    is_trend_up   = ema20[i] > ema50[i]
    near_bb_low   = (bb_low[i] is not None) and (c <= bb_low[i]*1.01)

    s_rsi   = 1.0 if is_rsi_bull else (0.6 if (r[i] is not None and 40 <= r[i] <= 70) else 0.0)
    s_macd  = 1.0 if is_macd_cross else (0.7 if hist[i] > 0 else 0.2)
    s_trend = 1.0 if is_trend_up else 0.3
    s_bb    = 1.0 if near_bb_low else 0.5

    score = fmean([s_rsi, s_macd, s_trend, s_bb])

    # normalização leve por volatilidade recente
    recent = [abs(h) for h in hist[-20:] if h is not None]
    if recent:
        vol_boost = min(max(abs(hist[i]) / (max(recent) + 1e-9), 0.0), 1.0)
        score = 0.85*score + 0.15*vol_boost
    return max(0.0, min(1.0, score)), {
        "RSI": r[i],
        "MACD_line": macd_line[i],
        "Signal_line": signal_line[i],
        "Hist": hist[i],
        "EMA20": ema20[i],
        "EMA50": ema50[i],
        "BB_up": bb_up[i],
        "BB_mid": bb_mid[i],
        "BB_low": bb_low[i]
    }

def build_trade_plan(closes, risk_ratio_tp=2.0, risk_ratio_sl=1.0):
    if len(closes) < 30:
        return None
    import statistics
    last = closes[-1]
    diffs = [abs(closes[j] - closes[j-1]) for j in range(-15, 0)]
    atr_like = statistics.fmean(diffs)
    sl = last - (atr_like * risk_ratio_sl)
    tp = last + (atr_like * risk_ratio_tp)
    return {"entry": last, "tp": tp, "sl": sl}

def generate_signal(symbol, candles):
    closes = [c["close"] for c in candles]
    scored = score_signal(closes)
    if scored is None:
        return None
    score, indicators_data = scored

    plan = build_trade_plan(closes)
    if plan is None:
        return None

    confidence = round(score, 4)
    signal_data = {
        "symbol": symbol,
        "timestamp": int(time.time()),
        "confidence": confidence,
        "entry": plan["entry"],
        "tp": plan["tp"],
        "sl": plan["sl"],
        "strategy": "RSI+MACD+EMA+BB",
        "source": "coingecko",
        "indicators": indicators_data
    }

    # Salva no histórico (mesmo se não atingir confiança mínima)
    append_to_history({
        "symbol": symbol,
        "timestamp": signal_data["timestamp"],
        "score": confidence,
        "decision": "aprovado" if confidence >= MIN_CONFIDENCE else "reprovado",
        "indicators": indicators_data
    })

    if confidence < MIN_CONFIDENCE:
        return None

    return signal_data
