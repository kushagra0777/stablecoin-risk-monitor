import requests

def fetch_supply():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=USDTUSDT"
    try:
        response = requests.get(url, timeout=5)
        return float(response.json().get("price", 0))
    except:
        return 1000000  # mock fallback
