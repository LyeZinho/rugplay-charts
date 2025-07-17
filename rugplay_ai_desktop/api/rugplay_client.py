
import os
import requests
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("KEY")
BASE_URL = "https://rugplay.com/api/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def get_coin_info(symbol: str, timeframe="1m"):
    url = f"{BASE_URL}/coin/{symbol}?timeframe={timeframe}"
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    return res.json()

def get_holders(symbol: str, limit=50):
    url = f"{BASE_URL}/holders/{symbol}?limit={limit}"
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    return res.json()

def get_market_top():
    url = f"{BASE_URL}/top"
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    return res.json()
