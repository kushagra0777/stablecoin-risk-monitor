from flask import Blueprint, jsonify, request
from ai_engine.anomaly_detector import ENGINE

bp = Blueprint("risk_routes", __name__, url_prefix="/api/risk")

@bp.route("/debug/alert", methods=["GET"])
def debug_alert():
    test_snapshot = {
        "reserves": 1_000_000,
        "supply": 1_200_000,
        "whale_supply": 0,
        "price": 1.0
    }

    result = ENGINE.analyze_snapshot(test_snapshot)

    alert_msg = "Anomaly Detected!" if result["label"] in ["RISKY", "WARNING"] else "All Good"

    return jsonify({
        "alert": alert_msg,
        "risk_score": result["risk_score"],
        "label": result["label"],
        "details": result["explanation"]
    })



@bp.route("/analyze", methods=["POST"])
def analyze_snapshot_api():
    data = request.get_json(force=True)

    snapshot = {
        "reserves": data.get("reserves", 0),
        "supply": data.get("supply", 0),
        "whale_supply": data.get("whales", 0.0),
        "price": data.get("price", 1.0),
        "prev_reserves": data.get("prev_reserves"),
        "prev_supply": data.get("prev_supply"),
        "custodians": data.get("custodians", [])
    }

    result = ENGINE.analyze_snapshot(snapshot)
    return jsonify(result)


@bp.route("/analyze/live", methods=["GET"])
def analyze_live():
    result = ENGINE.analyze_live()
    return jsonify(result)

@bp.route("/rescore/history", methods=["GET"])
def rescore_history_api():
    import pandas as pd
    import os
    from ai_engine.anomaly_detector import ENGINE

    path = "data/historical_snapshots.csv"
    if not os.path.exists(path):
        return jsonify({"error": "No historical data found"}), 404

    df = pd.read_csv(path)
    rescored = []

    for i in range(len(df)):
        snap = df.iloc[i].to_dict()
        prev = df.iloc[i - 1].to_dict() if i > 0 else None

        out = ENGINE.analyze_snapshot(snap, prev)
        snap["risk_score"] = out["risk_score"]
        snap["risk_label"] = out["label"]

        rescored.append(snap)

    return jsonify(rescored)