# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime

POSITIONS_FILE = os.getenv("POSITIONS_FILE", "positions.json")


def _load_positions():
    if not os.path.exists(POSITIONS_FILE):
        return {"open": [], "closed": []}
    try:
        with open(POSITIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"open": [], "closed": []}


def _save_positions(data):
    with open(POSITIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def should_send_and_register(symbol):
    """
    Verifica se um sinal para 'symbol' já está aberto.
    Se não estiver, registra e retorna True.
    Se já estiver aberto, retorna False.
    """
    data = _load_positions()

    # Já existe posição aberta para esse símbolo?
    for pos in data["open"]:
        if pos["symbol"] == symbol:
            return False

    # Registra nova posição
    data["open"].append({
        "symbol": symbol,
        "opened_at": datetime.utcnow().timestamp()
    })
    _save_positions(data)
    return True


def close_position(symbol, result):
    """
    Move uma posição de 'open' para 'closed', registrando o resultado.
    """
    data = _load_positions()
    closed_at = datetime.utcnow().timestamp()
    to_close = None

    for pos in data["open"]:
        if pos["symbol"] == symbol:
            to_close = pos
            break

    if to_close:
        data["open"].remove(to_close)
        to_close["closed_at"] = closed_at
        to_close["result"] = result
        data["closed"].append(to_close)
        _save_positions(data)
        return True

    return False
