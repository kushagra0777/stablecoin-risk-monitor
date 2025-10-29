import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from xgboost import XGBClassifier
from data_layer.collectors.blockchain_fetcher import get_blockchain_data
from data_layer.collectors.mock_custodian import get_custodian_data
from data_layer.collectors.exchange_fetcher import get_exchange_data
from ai_engine.feature_engineering import build_features

# Dummy training (for now)
np.random.seed(42)
reserves = np.random.normal(1000, 50, 500)
supply = reserves + np.random.normal(0, 20, 500)
labels = (supply > reserves + 50).astype(int)

df = pd.DataFrame({
    "reserves": reserves,
    "supply": supply,
    "diff": supply - reserves,
    "label": labels
})

iso = IsolationForest(contamination=0.05, random_state=42)
iso.fit(df[["reserves", "supply"]])

xgb = XGBClassifier(use_label_encoder=False, eval_metric="logloss")
xgb.fit(df[["reserves", "supply", "diff"]], df["label"])

def analyze_snapshot(reserves, supply, whales=0.0, price=1.0, prev_reserves=None, prev_supply=None):
    snap = {
        "reserves": reserves,
        "supply": supply,
        "whale_supply": whales,
        "price": price,
        "prev_reserves": prev_reserves or reserves,
        "prev_supply": prev_supply or supply
    }
    feats = build_features(snap)
    diff = feats["diff"].iloc[0]

    anomaly_flag = 1 if iso.predict(feats[["reserves", "supply"]])[0] == -1 else 0
    risk_class = int(xgb.predict(feats[["reserves", "supply", "diff"]])[0])
    risk_prob = float(xgb.predict_proba(feats[["reserves", "supply", "diff"]])[0][1])

    risk_score = int(100 * risk_prob + 20 * anomaly_flag)
    label = "SAFE"
    if risk_score > 70:
        label = "RISKY"
    elif risk_score > 40:
        label = "WARNING"

    return {
        "risk_score": risk_score,
        "label": label,
        "explanation": {
            "diff": float(diff),
            "reserves": float(reserves),
            "supply": float(supply),
            "price": float(price)
        }
    }

def analyze_from_live_data():
    chain = get_blockchain_data()
    cust = get_custodian_data()
    exch = get_exchange_data()

    return analyze_snapshot(
        reserves=cust["totalReserves"],
        supply=chain["circulatingSupply"],
        price=exch["price"]
    )