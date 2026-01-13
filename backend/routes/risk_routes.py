from flask import Blueprint, jsonify, request
from ai_engine.anomaly_detector import ENGINE
from backend.schemas import RiskAnalysisRequest

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
    try:
        # Pydantic validation
        data = request.get_json(force=True)
        validated_data = RiskAnalysisRequest(**data)
        
        snapshot = {
            "reserves": validated_data.reserves,
            "supply": validated_data.supply,
            "whale_supply": validated_data.whales,
            "price": validated_data.price,
            "prev_reserves": validated_data.prev_reserves if validated_data.prev_reserves is not None else validated_data.reserves,
            "prev_supply": validated_data.prev_supply if validated_data.prev_supply is not None else validated_data.supply,
            "custodians": validated_data.custodians
        }

        result = ENGINE.analyze_snapshot(snapshot)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


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