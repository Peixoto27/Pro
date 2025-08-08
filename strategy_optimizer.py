# strategy_optimizer.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import ta

def prepare_data(filename):
    """Lê o CSV e calcula os indicadores e o 'alvo' para o treinamento."""
    print("Preparando dados para treinamento...")
    df = pd.read_csv(filename, parse_dates=['timestamp'])
    
    # Calcula todos os indicadores que usamos na nossa estratégia
    df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
    df['rsi'] = ta.momentum.rsi(df['close'], window=14)
    df['macd_diff'] = ta.trend.macd_diff(df['close'], window_slow=26, window_fast=12, window_sign=9)
    df['volume_sma_20'] = ta.trend.sma_indicator(df['volume'], window=20)
    
    # --- A MÁGICA DO MACHINE LEARNING: DEFININDO O ALVO ---
    # Nosso objetivo é prever se o preço vai subir nos próximos X períodos.
    # Vamos definir um "alvo": o preço subiu 5% nas próximas 24 horas? (1 = Sim, 0 = Não)
    future_periods = 24
    price_increase_threshold = 1.05 # 5% de aumento
    
    # Calcula o preço futuro
    df['future_price'] = df['close'].shift(-future_periods)
    
    # Cria a nossa variável alvo (target)
    df['target'] = (df['future_price'] / df['close']) > price_increase_threshold
    df['target'] = df['target'].astype(int)
    
    # Remove linhas com dados NaN (gerados pelos indicadores e pelo shift)
    df.dropna(inplace=True)
    
    print("Dados preparados com sucesso.")
    return df

def train_model(df):
    """Treina um modelo de IA para encontrar a importância de cada indicador."""
    print("Iniciando o treinamento do modelo de IA...")
    
    # Define quais colunas são os "recursos" (features) que o modelo usará para aprender
    features = ['sma_50', 'rsi', 'macd_diff', 'volume_sma_20', 'open', 'high', 'low', 'close', 'volume']
    # Define qual coluna é o "alvo" (target) que queremos prever
    target = 'target'
    
    X = df[features]
    y = df[target]
    
    # Divide os dados em um conjunto de treino e um conjunto de teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Usa um dos modelos mais eficazes para este tipo de problema: RandomForest
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    
    # Treina o modelo com os dados de treino
    model.fit(X_train, y_train)
    
    # Avalia o modelo com os dados de teste (que ele nunca viu antes)
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"🎯 Acurácia do modelo nos dados de teste: {accuracy * 100:.2f}%")
    
    # --- A RESPOSTA QUE QUEREMOS: A IMPORTÂNCIA DE CADA FATOR ---
    print("\n--- Importância de cada indicador (segundo a IA) ---")
    feature_importances = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)
    print(feature_importances)
    
    print("\nTreinamento concluído.")
    return model, feature_importances

# --- Para executar este script ---
if __name__ == "__main__":
    # Nome do arquivo gerado pelo data_collector.py
    data_file = "historical_data_BTC_USDT_1h.csv"
    
    prepared_df = prepare_data(data_file)
    trained_model, importances = train_model(prepared_df)

