import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

def build_features(snapshot: Dict[str, Any],
                   prev_snapshot: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Build feature set from snapshot data.
    
    Supports both stablecoin and equity data structures:
    - Stablecoin: reserves, supply, price, whale_supply
    - Equity: cash reserves, shares outstanding, price, float
    
    Args:
        snapshot: Current snapshot dictionary
        prev_snapshot: Previous snapshot for delta calculations
        
    Returns:
        DataFrame with engineered features
    """
    reserves = float(snapshot.get("reserves", 0))
    supply = float(snapshot.get("supply", 0))
    price = float(snapshot.get("price", 1.0))
    whales = float(snapshot.get("whale_supply", 0.0))

    if prev_snapshot:
        prev_reserves = float(prev_snapshot.get("reserves", reserves))
        prev_supply = float(prev_snapshot.get("supply", supply))
        prev_price = float(prev_snapshot.get("price", price))
    else:
        prev_reserves = float(snapshot.get("prev_reserves", reserves))
        prev_supply = float(snapshot.get("prev_supply", supply))
        prev_price = float(snapshot.get("prev_price", price))

    # Core metrics
    diff = supply - reserves
    reserve_supply_ratio = reserves / (supply + 1e-9)
    whale_ratio = whales / (supply + 1e-9)

    # Delta calculations
    delta_reserves = reserves - prev_reserves
    delta_supply = supply - prev_supply
    delta_price = price - prev_price

    # Percentage changes
    pct_reserve_change = (reserves - prev_reserves) / (abs(prev_reserves) + 1e-9)
    pct_supply_change = (supply - prev_supply) / (abs(prev_supply) + 1e-9)
    pct_price_change = (price - prev_price) / (abs(prev_price) + 1e-9)

    # Custodian variance (if available)
    custodian_balances = snapshot.get("custodians", None)
    custodian_variance = 0.0
    if isinstance(custodian_balances, list) and len(custodian_balances) > 0:
        custodian_variance = float(np.var(custodian_balances))

    # Equity-specific features (optional, will be 0 if not present)
    equity_float = float(snapshot.get("equity_float", 0))
    market_cap = float(snapshot.get("market_cap", 0))
    float_ratio = float(snapshot.get("float_ratio", 0))
    cash_to_market_cap = float(snapshot.get("cash_to_market_cap", 0))
    
    # Calculate liquidity score
    liquidity_score = reserve_supply_ratio * price
    
    # Volatility indicator (if we have price history)
    price_volatility = abs(pct_price_change)

    features = {
        # Core features
        "reserves": reserves,
        "supply": supply,
        "diff": diff,
        "price": price,
        "reserve_supply_ratio": reserve_supply_ratio,
        "whale_ratio": whale_ratio,
        
        # Delta features
        "delta_reserves": delta_reserves,
        "delta_supply": delta_supply,
        "delta_price": delta_price,
        
        # Percentage change features
        "pct_reserve_change": pct_reserve_change,
        "pct_supply_change": pct_supply_change,
        "pct_price_change": pct_price_change,
        
        # Custodian features
        "custodian_variance": custodian_variance,
        
        # Equity-specific features
        "equity_float": equity_float,
        "market_cap": market_cap,
        "float_ratio": float_ratio,
        "cash_to_market_cap": cash_to_market_cap,
        
        # Derived features
        "liquidity_score": liquidity_score,
        "price_volatility": price_volatility
    }

    df = pd.DataFrame([features])
    df = df.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    return df
