# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime, timedelta

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


def should_send_and_register(symbol, cooldown_hours=0):
    """
    Verifica se um sinal para 'symbol' pode ser enviado.
    - Se já existir e ainda estiver no cooldown, retorna (False, motivo)
    - Se não existir ou cooldown expirou, registra e retorna (True, 'ok')
    """
    data = _load_positions()
    now = datetime.utcnow()

    for pos in data["open"]:
        if pos["symbol"] == symbol:
            opened_at = datetime.utcfromtimestamp(pos["opened_at"])
            if cooldown_hours > 0 and now - opened_at < timedelta(hours=cooldown_hours):
                return False, f"Aguardando cooldown ({cooldown_hours}h)"
            else:
                # Cooldown expirou, atualiza o horário
                pos["opened_at"] = now.timestamp()
                _save_positions(data)
                return True, "Cooldown expirado, reenviando"

    # Não encontrado, registrar novo
    data["open"].append({
        "symbol": symbol,
        "opened_at": now.timestamp()
    })
    _save_positions(data)
    return True, "Novo sinal"


def close_position(symbol, result):
    """
    Fecha uma posição aberta e move para 'closed'.
    """
    data = _load_positions()
    now = datetime.utcnow().timestamp()

    for pos in data["open"]:
        if pos["symbol"] == symbol:
            data["open"].remove(pos)
            pos["closed_at"] = now
            pos["result"] = result
            data["closed"].append(pos)
            _save_positions(data)
            return True

    return False
