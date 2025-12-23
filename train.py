import os
import pandas as pd
import numpy as np
from ai_engine.anomaly_detector import AnomalyEngine
from ai_engine.feature_engineering import build_features

DATA_PATH = "data/historical_snapshots.csv"
MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

def load_training_data():

    if os.path.exists(DATA_PATH):
        print(f"Loading dataset from {DATA_PATH}")
        df = pd.read_csv(DATA_PATH)
    else:
        print("No historical dataset found. Generating synthetic training data.")
        np.random.seed(42)
        reserves = np.random.normal(1000, 50, 800)
        supply = reserves + np.random.normal(0, 20, 800)
        whales = np.abs(np.random.normal(5, 2, 800))
        price = 1 + np.random.normal(0, 0.01, 800)
        labels = (supply > reserves + 40).astype(int)

        df = pd.DataFrame({
            "reserves": reserves,
            "supply": supply,
            "whale_supply": whales,
            "price": price,
            "label": labels
        })
    return df

def build_feature_matrix(df: pd.DataFrame):
    rows = []

    for i in range(len(df)):
        snap = df.iloc[i].to_dict()
        if "label" not in snap or pd.isna(snap["label"]):
            snap["label"] = int(snap["supply"] > snap["reserves"] + 40)

        prev = df.iloc[i - 1].to_dict() if i > 0 else None
        feats = build_features(snap, prev)
        feats["label"] = snap["label"]
        rows.append(feats)
    final_df = pd.concat(rows, ignore_index=True)
    return final_df


def train_model(feature_df: pd.DataFrame):
    print("Training ML models...")

    labels = feature_df["label"].values
    X = feature_df.drop(columns=["label"])

    engine = AnomalyEngine()

    if len(set(labels)) < 2:
        print("Only one label class detected. Training unsupervised IsolationForest only.")
        engine.train(X, labels=None)
        print("Model training (unsupervised) complete.")
        return engine

    engine.train(X, labels)
    print(" Full model training (IsolationForest + XGBoost) complete.")
    return engine

def evaluate_model(engine: AnomalyEngine, feature_df: pd.DataFrame):
    print("\n Evaluating model...")

    labels = feature_df["label"].values
    X = feature_df.drop(columns=["label"])

    preds = []
    for i in range(len(X)):
        snap = X.iloc[i].to_dict()
        out = engine.analyze_snapshot(snap)
        preds.append(out["label"])

    preds = np.array(preds)
    numeric_preds = (preds != "SAFE").astype(int)

    accuracy = (numeric_preds == labels).mean()
    print(f"Accuracy: {accuracy:.4f}")

    print("Example prediction:", preds[0])


if __name__ == "__main__":
    print("\nSTABLECOIN RISK MODEL TRAINING")

    df = load_training_data()
    feature_df = build_feature_matrix(df)

    engine = train_model(feature_df)
    evaluate_model(engine, feature_df)

    print("\nTraining pipeline completed")