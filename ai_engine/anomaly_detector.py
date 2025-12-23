import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from xgboost import XGBClassifier
from ai_engine.feature_engineering import build_features
from data_layer.collectors.blockchain_fetcher import get_blockchain_data
from data_layer.collectors.mock_custodian import get_custodian_data
from data_layer.collectors.exchange_fetcher import get_exchange_data


MODEL_DIR = "models"
ISO_PATH = os.path.join(MODEL_DIR, "iso_model.pkl")
XGB_PATH = os.path.join(MODEL_DIR, "xgb_model.pkl")

os.makedirs(MODEL_DIR, exist_ok=True)



class AnomalyEngine:
    def __init__(self):
        self.iso = None
        self.xgb = None
        self._load_models()

    def _load_models(self):
        if os.path.exists(ISO_PATH):
            self.iso = joblib.load(ISO_PATH)

        if os.path.exists(XGB_PATH):
            self.xgb = joblib.load(XGB_PATH)



    def _save_models(self):
        if self.iso is not None:
            joblib.dump(self.iso, ISO_PATH)

        if self.xgb is not None:
            joblib.dump(self.xgb, XGB_PATH)

    def train(self, df_features: pd.DataFrame, labels=None):
        self.iso = IsolationForest(
            contamination=0.05,
            random_state=42
        )
        self.iso.fit(df_features.values)

        if labels is not None:
            self.xgb = XGBClassifier(
                eval_metric="logloss",
                use_label_encoder=False
            )
            self.xgb.fit(df_features.values, labels)

        self._save_models()

    def analyze_snapshot(self, snapshot: dict, prev_snapshot=None):
        feats = build_features(snapshot, prev_snapshot)
        X = feats.values
        anomaly_flag = 0
        if self.iso is not None:
            iso_pred = self.iso.predict(X)[0]    
            anomaly_flag = 1 if iso_pred == -1 else 0


        risk_prob = 0.0
        risk_class = 0

        if self.xgb is not None:
            risk_class = int(self.xgb.predict(X)[0])

            if hasattr(self.xgb, "predict_proba"):
                risk_prob = float(self.xgb.predict_proba(X)[0][1])
        else:
            diff = feats["diff"].iloc[0]
            ratio = feats["reserve_supply_ratio"].iloc[0]

            if diff > 50 or ratio < 1.0:
                risk_prob = 0.8
                risk_class = 1
            else:
                risk_prob = 0.2
                risk_class = 0


        risk_score = int(risk_prob * 100 + anomaly_flag * 20)

        label = "SAFE"
        if risk_score > 70:
            label = "RISKY"
        elif risk_score > 40:
            label = "WARNING"

        return {
            "risk_score": risk_score,
            "label": label,
            "explanation": {
                "anomaly_flag": anomaly_flag,
                "risk_class": risk_class,
                "risk_probability": risk_prob,
                "diff": float(feats["diff"].iloc[0]),
                "reserve_supply_ratio": float(feats["reserve_supply_ratio"].iloc[0]),
                "delta_reserves": float(feats["delta_reserves"].iloc[0]),
                "delta_supply": float(feats["delta_supply"].iloc[0]),
            },
            "raw_features": feats.to_dict(orient="records")[0]
        }


    def analyze_live(self):
        chain = get_blockchain_data()
        cust = get_custodian_data()
        exch = get_exchange_data()

        snapshot = {
            "reserves": cust.get("totalReserves", 0),
            "supply": chain.get("circulatingSupply", 0),
            "whale_supply": chain.get("whale_supply", 0),
            "price": exch.get("price", 1.0)
        }

        return self.analyze_snapshot(snapshot)

ENGINE = AnomalyEngine()
