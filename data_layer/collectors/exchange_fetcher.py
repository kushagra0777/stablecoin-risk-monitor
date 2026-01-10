from backend.http_client import get_retry_session

def get_exchange_data():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=USDCUSDT"
    try:
        session = get_retry_session()
        response = session.get(url, timeout=5)
        data = response.json()
        price = float(data.get("price", 1.0))
    except Exception:
        price = 1.0
    return {"price": price}