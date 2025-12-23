import requests

def get_exchange_data():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=USDCUSDT"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        price = float(data.get("price", 1.0))
    except Exception:
        price = 1.0
    return {"price": price}