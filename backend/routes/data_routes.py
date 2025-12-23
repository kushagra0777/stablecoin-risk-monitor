from flask import Blueprint, jsonify
from data_layer.collectors.exchange_fetcher import get_exchange_data
from data_layer.collectors.mock_custodian import get_custodian_data
from data_layer.collectors.blockchain_fetcher import get_blockchain_data

bp = Blueprint("data", __name__, url_prefix="/api/data")

@bp.route("/snapshot", methods=["GET"])
def snapshot():

    exch = get_exchange_data()
    cust = get_custodian_data()
    chain = get_blockchain_data()

    return jsonify({
        "price": exch["price"],
        "reserves": cust["totalReserves"],
        "custodians": cust["custodians"],
        "supply": chain["circulatingSupply"],
        "whale_supply": chain["whale_supply"]
    })