import time
from datetime import datetime
from price_fetcher import fetch_all_data
from technical_indicators import calculate_indicators
from signal_generator import generate_signal
from notifier import send_signal_notification
from state_manager import load_open_trades, save_open_trades, check_and_notify_closed_trades
from ai_predictor import predict_success_proba

# --- CONFIGURAÇÕES ---
SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT", "TONUSDT",
    "INJUSDT", "RNDRUSDT", "ARBUSDT", "LTCUSDT", "MATICUSDT",
    "OPUSDT", "NEARUSDT", "APTUSDT", "PEPEUSDT", "SEIUSDT",
    "TRXUSDT", "DOGEUSDT", "SHIBUSDT", "FILUSDT", "SUIUSDT"
]
USAR_SENTIMENTO = True

def get_macro_trend(df, symbol):
    return "ALTA"

def run_scanner():
    print("\n--- Iniciando novo ciclo do scanner ---")
    
    try:
        open_trades = load_open_trades()
    except Exception as e:
        print(f"⚠️ Erro ao carregar trades abertos: {e}")
        open_trades = {}

    try:
        market_data_for_monitoring = fetch_all_data(list(open_trades.keys()))
        check_and_notify_closed_trades(open_trades, market_data_for_monitoring, send_signal_notification)
    except Exception as e:
        print(f"⚠️ Erro ao verificar trades fechados: {e}")

    print("\n🔍 Fase 2: Buscando por novos sinais...")
    all_symbols_to_fetch = list(set(SYMBOLS) - set(open_trades.keys()))
    if not all_symbols_to_fetch:
        print("⚪ Não há novas moedas para analisar, todos os trades estão abertos.")
        return

    print("🚚 Buscando dados brutos do mercado (OHLCV)...")
    try:
        market_data = fetch_all_data(all_symbols_to_fetch)
    except Exception as e:
        print(f"🚨 Erro ao buscar dados de mercado: {e}")
        return

    for symbol, df in market_data.items():
        try:
            if df is None or df.empty:
                print(f"⚪ Sem dados para {symbol}, pulando...")
                continue

            print("-" * 20)
            print(f"🔬 Analisando {symbol}...")

            df_with_indicators = calculate_indicators(df)
            if df_with_indicators.empty:
                print(f"⚠️ Não foi possível calcular indicadores para {symbol}. Pulando...")
                continue
            print("✅ Indicadores calculados com sucesso.")

            tendencia_macro = get_macro_trend(df, symbol)
            if tendencia_macro != "ALTA":
                print(f"⚪ Tendência macro não é de ALTA para {symbol}. Pulando...")
                continue

            sentiment_score = 0.0
            if USAR_SENTIMENTO:
                from sentiment import get_sentiment_score
                sentiment_score = get_sentiment_score(symbol)
                print(f"🧠 Sentimento para {symbol}: {sentiment_score:.2f}")
                if sentiment_score < 0:
                    print(f"⚪ Sentimento negativo ({sentiment_score:.2f}) para {symbol}. Pulando...")
                    continue

            # === IA: monta features para predição ===
            row = df_with_indicators.iloc[-1]
            def _safe(v, default=0.0):
                try:
                    return float(v) if v is not None else float(default)
                except Exception:
                    return float(default)
            close = _safe(row.get("close"), 0)
            sma50 = _safe(row.get("sma_50", row.get("sma50", 0)), 0)
            vol = _safe(row.get("volume"), 1)
            v_sma20 = _safe(row.get("volume_sma_20", row.get("v_sma20", 1)), 1)
            feats = {
                "rsi": _safe(row.get("rsi"), 0),
                "macd_diff": _safe(row.get("macd_diff"), 0),
                "sma_ratio": (close / sma50) if sma50 > 0 else 1.0,
                "volume_ratio": (vol / v_sma20) if v_sma20 > 0 else 1.0,
                "volatility": _safe(row.get("volatility"), 0),
                "momentum": _safe(row.get("momentum"), 0),
            }
            created_dt = datetime.utcnow()
            proba = predict_success_proba({
                "symbol": symbol,
                "rsi": feats["rsi"],
                "macd_diff": feats["macd_diff"],
                "sma_ratio": feats["sma_ratio"],
                "volume_ratio": feats["volume_ratio"],
                "volatility": feats["volatility"],
                "momentum": feats["momentum"],
                "sentiment_score": sentiment_score,
                "hour_of_day": created_dt.hour,
                "day_of_week": created_dt.weekday(),
                "confidence_score": 70.0,
            })
            print(f"🤖 Probabilidade IA para {symbol}: {proba:.2f}")
            if proba < 0.60:
                print(f"⚪ IA recomendou PULAR ({proba:.2f}). Pulando {symbol}…")
                continue

            signal = generate_signal(df_with_indicators, symbol)
            
            if signal:
                print(f"🔥 SINAL ENCONTRADO PARA {symbol}!")
                caution = "⚠️ *Cautela:* prob. intermediária.\n" if 0.60 <= proba < 0.75 else ""
                signal_text = (
                    f"🚀 *NOVA OPORTUNIDADE DE TRADE*\n\n"
                    f"📌 *Par:* {signal['symbol']}\n"
                    f"🎯 *Entrada:* `{signal['entry_price']}`\n"
                    f"🎯 *Alvo:* `{signal['target_price']}`\n"
                    f"🛑 *Stop Loss:* `{signal['stop_loss']}`\n\n"
                    f"📊 *Risco/Retorno:* `{signal['risk_reward']}`\n"
                    f"📈 *Confiança (técnico):* `{signal['confidence_score']}%`\n"
                    f"🤖 *Prob. IA:* `{proba:.2f}`\n"
                    f"{caution}"
                    f"🧠 Estratégia: `{signal['strategy']}`\n"
                    f"📅 Criado em: `{signal['created_at']}`\n"
                    f"🆔 ID: `{signal['id']}`"
                )
                if send_signal_notification(signal_text):
                    open_trades[symbol] = signal
                    save_open_trades(open_trades)
                else:
                    print(f"⚠️ Falha ao enviar sinal para {symbol}")
            else:
                print(f"⚪ Sem sinal para {symbol} após análise final.")

        except Exception as e:
            print(f"🚨 Erro inesperado ao processar {symbol}: {e}")

if __name__ == "__main__":
    run_scanner()
