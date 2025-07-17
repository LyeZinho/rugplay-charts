import os
import sys
import json
import pickle
import numpy as np
from sklearn.linear_model import LinearRegression

dataset_dir = os.path.join(os.path.dirname(__file__), "dataset")
model_dir = os.path.join(os.path.dirname(__file__), "models")
if not os.path.exists(model_dir):
    os.makedirs(model_dir)

def load_dataset(symbol):
    file_path = os.path.join(dataset_dir, f"{symbol}.json")
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def train_model_for_symbol(symbol, ignore_check=False):
    data = load_dataset(symbol)
    if not data or (len(data) < 2 and not ignore_check):
        print(f"Dataset insuficiente para {symbol}")
        return None
    closes = []
    for entry in data:
        closes.extend([c.get("close") for c in entry.get("candlestickData", []) if c.get("close") is not None])
    if len(closes) < 2 and not ignore_check:
        print(f"Dados de candles insuficientes para {symbol}")
        return None
    if len(closes) < 2 and ignore_check:
        # Treina com o que tem, mesmo que seja só um valor
        X = np.arange(len(closes)).reshape(-1, 1)
        y = np.array(closes)
        model = LinearRegression()
        model.fit(X, y)
        with open(os.path.join(model_dir, f"{symbol}_model.pkl"), "wb") as f:
            pickle.dump(model, f)
        print(f"Modelo treinado para {symbol} com {len(closes)} candles (ignorado check).")
        return model
    X = np.arange(len(closes)).reshape(-1, 1)
    y = np.array(closes)
    model = LinearRegression()
    model.fit(X, y)
    # Salva modelo
    with open(os.path.join(model_dir, f"{symbol}_model.pkl"), "wb") as f:
        pickle.dump(model, f)
    print(f"Modelo treinado para {symbol} com {len(closes)} candles.")
    return model

def train_all(ignore_check=False):
    for fname in os.listdir(dataset_dir):
        if fname.endswith(".json"):
            symbol = fname.replace(".json", "")
            train_model_for_symbol(symbol, ignore_check=ignore_check)

def predict_next(symbol):
    # Carrega modelo
    model_path = os.path.join(model_dir, f"{symbol}_model.pkl")
    if not os.path.exists(model_path):
        print(f"Modelo não encontrado para {symbol}. Treine primeiro.")
        return
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    # Carrega dataset
    data = load_dataset(symbol)
    closes = []
    for entry in data:
        closes.extend([c.get("close") for c in entry.get("candlestickData", []) if c.get("close") is not None])
    if not closes:
        print(f"Dados insuficientes para predição de {symbol}")
        return
    next_time = np.array([[len(closes)]])
    pred = model.predict(next_time)[0]
    print(f"Predição do próximo preço de fechamento para {symbol}: {pred:.6f}")
    return pred

def main():
    if len(sys.argv) < 2:
        print("Uso: python train_predictor.py [train|predict SYMBOL] [--ignore-check]")
        return
    cmd = sys.argv[1]
    ignore_check = '--ignore-check' in sys.argv
    if cmd == "train":
        train_all(ignore_check=ignore_check)
    elif cmd == "predict" and len(sys.argv) >= 3:
        symbol = sys.argv[2].strip().upper()
        predict_next(symbol)
    else:
        print("Comando inválido. Use 'train' ou 'predict SYMBOL'.")

if __name__ == "__main__":
    main()
