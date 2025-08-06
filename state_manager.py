# state_manager.py (Versão Final e Correta)
import json
import os

# Define o nome do arquivo que guardará nosso "estado" ou "memória"
STATE_FILE = 'trades_abertos.json'

def save_open_trades(trades_dict):
    """
    Salva o dicionário de trades abertos em um arquivo JSON.
    Esta função se chama 'save_open_trades', como o scanner espera.
    """
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(trades_dict, f, indent=4)
    except Exception as e:
        print(f"❌ Erro ao salvar o estado dos trades: {e}")

def load_open_trades():
    """
    Carrega o dicionário de trades abertos do arquivo JSON.
    Esta função se chama 'load_open_trades', como o scanner espera.
    """
    # Verifica se o arquivo de estado existe
    if not os.path.exists(STATE_FILE):
        return {}  # Retorna um dicionário vazio se for a primeira execução

    try:
        with open(STATE_FILE, 'r') as f:
            # Se o arquivo estiver vazio, retorna um dicionário vazio para evitar erros
            content = f.read()
            if not content:
                return {}
            return json.loads(content)
    except json.JSONDecodeError:
        print("⚠️ Arquivo de estado corrompido ou vazio. Começando com um novo estado.")
        return {} # Retorna um dicionário vazio se o arquivo estiver malformado
    except Exception as e:
        print(f"❌ Erro ao carregar o estado dos trades: {e}")
        return {}
