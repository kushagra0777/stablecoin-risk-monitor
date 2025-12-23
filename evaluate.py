import os
import pandas as pd
import numpy as np

from ai_engine.anomaly_detector import AnomalyEngine
from ai_engine.feature_engineering import build_features

DATA_PATH = "data/historical_snapshots.csv"

def load_eval_data():
    if os.path.exists(DATA_PATH):
        print(f" Loading evaluation dataset from {DATA_PATH}")
        return pd.read_csv(DATA_PATH)
    else:
        raise FileNotFoundError("Not found. Run train.py or generate real snapshots.")

def build_eval_matrix(df):
    rows = []
    for i in range(len(df)):
        snap = df.iloc[i].to_dict()
        prev = df.iloc[i-1].to_dict() if i > 0 else None
        feats = build_features(snap, prev)
        feats["label"] = snap.get("label", 0)
        rows.append(feats)
    return pd.concat(rows, ignore_index=True)

def evaluate(engine, df):
    X = df.drop(columns=["label"])
    y = df["label"].values

    preds = []
    for i in range(len(X)):
        out = engine.analyze_snapshot(X.iloc[i].to_dict())
        preds.append(out["label"])

    preds_numeric = (np.array(preds) != "SAFE").astype(int)

    accuracy = (preds_numeric == y).mean()
    print(f"\nML Evaluation Accuracy = {accuracy:.4f}")
    return accuracy

if __name__ == "__main__":
    print("\nMODEL EVALUATION")

    df = load_eval_data()
    eval_df = build_eval_matrix(df)

    engine = AnomalyEngine()
    evaluate(engine, eval_df)

    print("Evaluation done.")
