# -*- coding: utf-8 -*-
import json, os, time
from datetime import datetime, timedelta

POSITIONS_FILE = "positions.json"

def _now_utc():
    return datetime.utcnow()

def _load_positions():
    if os.path.exists(POSITIONS_FILE):
        try:
            with open(POSITIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"open": []}  # { "open": [ {symbol, entry, tp, sl, created_at, last_sent_at} ] }

def _save_positions(obj):
    with open(POSITIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def _pct_diff(a, b):
    if a is None or b is None: return 999.0
    a, b = float(a), float(b)
    if a == 0: return 999.0
    return abs(a - b) / abs(a) * 100.0

def should_send_and_register(sig: dict, cooldown_hours: float = 6.0, change_threshold_pct: float = 1.0):
    """
    Decide se envia entrada nova:
      - Se não houver posição aberta desse símbolo → envia e registra.
      - Se houver, só envia se mudou forte (entry/tp/sl mudou > threshold) OU se cooldown expirou.
    Retorna (True/False, reason)
    """
    sym = sig.get("symbol")
    entry, tp, sl = sig.get("entry"), sig.get("tp"), sig.get("sl")
    if sym is None: return (False, "sem_symbol")

    book = _load_positions()
    open_list = book.get("open", [])

    # procura posição aberta do mesmo símbolo
    found = None
    for pos in open_list:
        if pos.get("symbol") == sym:
            found = pos
            break

    now = _now_utc()
    if found is None:
        # registra nova
        open_list.append({
            "symbol": sym,
            "entry": float(entry),
            "tp": float(tp),
            "sl": float(sl),
            "created_at": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "last_sent_at": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "status": "open"
        })
        book["open"] = open_list
        _save_positions(book)
        return (True, "novo")

    # já existe posição aberta — checar cooldown e mudança
    last_sent = found.get("last_sent_at")
    last_dt = None
    try:
        if last_sent:
            last_dt = datetime.strptime(last_sent, "%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        last_dt = None

    cooldown_ok = True
    if last_dt:
        cooldown_ok = (now - last_dt) >= timedelta(hours=cooldown_hours)

    changed = (
        _pct_diff(found.get("entry"), entry) > change_threshold_pct or
        _pct_diff(found.get("tp"), tp) > change_threshold_pct or
        _pct_diff(found.get("sl"), sl) > change_threshold_pct
    )

    if changed or cooldown_ok:
        # atualiza plano e last_sent_at, e permite enviar
        found["entry"] = float(entry)
        found["tp"] = float(tp)
        found["sl"] = float(sl)
        found["last_sent_at"] = now.strftime("%Y-%m-%d %H:%M:%S UTC")
        _save_positions(book)
        return (True, "mudou" if changed else "cooldown")

    # não envia duplicado
    return (False, "duplicado")

def close_position(symbol: str, reason: str):
    """
    Fecha a posição (hit_tp / hit_sl / expirado).
    """
    book = _load_positions()
    open_list = book.get("open", [])
    new_open = []
    closed = False
    for pos in open_list:
        if pos.get("symbol") == symbol and pos.get("status") == "open":
            pos["status"] = reason
            pos["closed_at"] = _now_utc().strftime("%Y-%m-%d %H:%M:%S UTC")
            # move para um array 'closed'
            closed_list = book.get("closed", [])
            closed_list.append(pos)
            book["closed"] = closed_list
            closed = True
        else:
            new_open.append(pos)
    book["open"] = new_open
    _save_positions(book)
    return closed
