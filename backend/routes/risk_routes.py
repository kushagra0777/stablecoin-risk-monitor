from flask import Blueprint, jsonify
from ai_engine.anomaly_detector import AnomalyDetector
from ai_engine.feature_engineering import prepare_features
import numpy as np

bp = Blueprint("risk", __name__, url_prefix="/api/risk")

@bp.route("/alert", methods=["GET"])
def alert():
    model = AnomalyDetector()
    training_data = np.array([[1000000, 1200000], [1100000, 1150000]])
    model.train(training_data)

    test_point = [1500000, 900000]
    result = model.predict(test_point)

    if result == -1:
        return jsonify({"alert": "🚨 Anomaly Detected!"})
    return jsonify({"alert": "✅ All Good"})
