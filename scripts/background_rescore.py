import os
import pandas as pd

from ai_engine.anomaly_detector import ENGINE
from ai_engine.feature_engineering import build_features

DATA_PATH = "data/historical_snapshots.csv"


def rescore_history():

    if not os.path.exists(DATA_PATH):
        print("[WARN] No historical snapshots found at:", DATA_PATH)
        return

    print("[INFO] Loading historical dataset...")
    df = pd.read_csv(DATA_PATH)

    rescored_rows = []

    print(f"[INFO] Found {len(df)} snapshots. Rescoring...")

    for i in range(len(df)):
        snap = df.iloc[i].to_dict()
        prev = df.iloc[i - 1].to_dict() if i > 0 else None

        result = ENGINE.analyze_snapshot(snap, prev)

        snap["risk_score"] = result["risk_score"]
        snap["risk_label"] = result["label"]

        rescored_rows.append(snap)

    pd.DataFrame(rescored_rows).to_csv(DATA_PATH, index=False)
    print("[INFO] Rescoring complete. Saved back to:", DATA_PATH)


if __name__ == "__main__":
    rescore_history()
