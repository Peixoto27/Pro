# state_manager.py
import json
import os

# O nome do nosso arquivo de "memória"
STATE_FILE = "trades_abertos.json"

def ler_trades_abertos():
    """
    Lê o arquivo JSON e retorna um dicionário de trades abertos.
    Se o arquivo não existir ou estiver vazio, retorna um dicionário vazio.
    """
    # Garante que o arquivo exista, mesmo que vazio
    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'w') as f:
            json.dump({}, f)
        return {}

    try:
        with open(STATE_FILE, 'r') as f:
            # Se o arquivo estiver vazio, o json.load falha, então tratamos isso
            if os.path.getsize(STATE_FILE) == 0:
                return {}
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # Em caso de erro de leitura ou arquivo corrompido, retorna um estado seguro (vazio)
        return {}

def salvar_trades_abertos(trades):
    """
    Recebe um dicionário de trades e o salva no arquivo JSON.
    """
    with open(STATE_FILE, 'w') as f:
        # 'indent=4' torna o arquivo JSON legível para humanos, o que é ótimo para depuração
        json.dump(trades, f, indent=4)

