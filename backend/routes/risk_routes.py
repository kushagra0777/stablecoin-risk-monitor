from flask import Blueprint, jsonify, request
from ai_engine.anomaly_detector import analyze_snapshot, analyze_from_live_data

bp = Blueprint("risk_routes", __name__, url_prefix="/api/risk")

@bp.route("/debug/alert", methods=["GET"])
def alert():
    result = analyze_snapshot(reserves=1_000_000, supply=1_200_000)

    if result["label"] in ["RISKY", "WARNING"]:
        return jsonify({
            "alert": "Anomaly Detected!",
            "risk_score": result["risk_score"],
            "label": result["label"],
            "details": result["explanation"]
        })
    else:
        return jsonify({
            "alert": "All Good",
            "risk_score": result["risk_score"],
            "label": result["label"],
            "details": result["explanation"]
        })


@bp.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(force=True)
    reserves = data.get("reserves", 0)
    supply = data.get("supply", 0)
    whales = data.get("whales", 0.0)
    price = data.get("price", 1.0)
    prev_reserves = data.get("prev_reserves")
    prev_supply = data.get("prev_supply")

    result = analyze_snapshot(
        reserves=reserves,
        supply=supply,
        whales=whales,
        price=price,
        prev_reserves=prev_reserves,
        prev_supply=prev_supply,
    )
    return jsonify(result)


@bp.route("/analyze/live", methods=["GET"])
def analyze_live():
    result = analyze_from_live_data()
    return jsonify(result)
