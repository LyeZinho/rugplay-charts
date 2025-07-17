import os
import sys
import json
from datetime import datetime
from api.rugplay_client import get_coin_info, get_holders

def main():
    if len(sys.argv) < 2:
        print("Uso: python dataset_collector.py SYMBOL")
        return
    symbol = sys.argv[1].strip().upper()
    # Busca dados da API
    try:
        coin_data = get_coin_info(symbol, timeframe="1d")
        holders_data = get_holders(symbol, limit=200)
    except Exception as e:
        print(f"Erro ao buscar dados da API: {e}")
        return
    # Monta registro do dia
    today = datetime.now().strftime("%Y-%m-%d")
    entry = {
        "date": today,
        "coin": coin_data.get("coin", {}),
        "candlestickData": coin_data.get("candlestickData", []),
        "volumeData": coin_data.get("volumeData", []),
        "holders": holders_data.get("holders", []),
        "poolInfo": holders_data.get("poolInfo", {})
    }
    # Pasta dataset
    dataset_dir = os.path.join(os.path.dirname(__file__), "dataset")
    if not os.path.exists(dataset_dir):
        os.makedirs(dataset_dir)
    # Caminho do arquivo
    file_path = os.path.join(dataset_dir, f"{symbol}.json")
    # Carrega histórico existente
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []
    # Adiciona registro do dia
    data.append(entry)
    # Salva
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Dados salvos em {file_path}")

if __name__ == "__main__":
    main()
