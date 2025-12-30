import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

def build_features(snapshot: Dict[str, Any],
                   prev_snapshot: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    reserves = float(snapshot.get("reserves", 0))
    supply = float(snapshot.get("supply", 0))
    price = float(snapshot.get("price", 1.0))
    whales = float(snapshot.get("whale_supply", 0.0))

    if prev_snapshot:
        prev_reserves = float(prev_snapshot.get("reserves", reserves))
        prev_supply = float(prev_snapshot.get("supply", supply))
    else:
        prev_reserves = float(snapshot.get("prev_reserves", reserves))
        prev_supply = float(snapshot.get("prev_supply", supply))

    diff = supply - reserves
    reserve_supply_ratio = reserves / (supply + 1e-9)
    whale_ratio = whales / (supply + 1e-9)

    delta_reserves = reserves - prev_reserves
    delta_supply = supply - prev_supply

    pct_reserve_change = (reserves - prev_reserves) / (abs(prev_reserves) + 1e-9)
    pct_supply_change = (supply - prev_supply) / (abs(prev_supply) + 1e-9)

    custodian_balances = snapshot.get("custodians", None)
    custodian_variance = 0.0
    if isinstance(custodian_balances, list) and len(custodian_balances) > 0:
        custodian_variance = float(np.var(custodian_balances))

    features = {
        "reserves": reserves,
        "supply": supply,
        "diff": diff,
        "price": price,
        "reserve_supply_ratio": reserve_supply_ratio,
        "whale_ratio": whale_ratio,
        "delta_reserves": delta_reserves,
        "delta_supply": delta_supply,
        "pct_reserve_change": pct_reserve_change,
        "pct_supply_change": pct_supply_change,
        "custodian_variance": custodian_variance
    }

    df = pd.DataFrame([features])
    df = df.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    return df
