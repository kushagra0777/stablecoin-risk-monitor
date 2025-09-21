from flask import Blueprint, jsonify
from data_layer.collectors.exchange_fetcher import fetch_supply
from data_layer.collectors.mock_custodian import get_mock_reserves

bp = Blueprint("data", __name__, url_prefix="/api/data")

@bp.route("/snapshot", methods=["GET"])
def snapshot():
    supply = fetch_supply()
    reserves = sum([r["balance"] for r in get_mock_reserves()])
    return jsonify({"supply": supply, "reserves": reserves})
