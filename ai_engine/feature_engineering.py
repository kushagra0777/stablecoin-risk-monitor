import pandas as pd

def build_features(snapshot: dict) -> pd.DataFrame:
    reserves = snapshot.get("reserves", 0)
    supply = snapshot.get("supply", 0)
    whales = snapshot.get("whale_supply", 0)
    price = snapshot.get("price", 1.0)
    prev_reserves = snapshot.get("prev_reserves", reserves)
    prev_supply = snapshot.get("prev_supply", supply)

    diff = supply - reserves
    pct_reserve_change = (reserves - prev_reserves) / (prev_reserves + 1e-9)
    pct_supply_change = (supply - prev_supply) / (prev_supply + 1e-9)
    whale_ratio = whales / (supply + 1e-9)

    return pd.DataFrame([{
        "reserves": reserves,
        "supply": supply,
        "diff": diff,
        "price": price,
        "pct_reserve_change": pct_reserve_change,
        "pct_supply_change": pct_supply_change,
        "whale_ratio": whale_ratio
    }])