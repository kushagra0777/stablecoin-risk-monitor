# governance_routes.py
# API endpoints to fetch contract state for dashboard integration

from flask import Blueprint, jsonify
from web3 import Web3
import os
import json

gov_bp = Blueprint('governance', __name__)

# Load environment variables
RPC_URL = os.getenv('RPC_URL', 'http://127.0.0.1:8545')
DAO_CONTRACT_ADDRESS = os.getenv('DAO_CONTRACT_ADDRESS')
CONTRACT_ABI_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../blockchain_layer/contracts/GovernanceDAO.json'))

# Load contract ABI
with open(CONTRACT_ABI_PATH) as f:
    contract_abi = json.load(f)["abi"]

w3 = Web3(Web3.HTTPProvider(RPC_URL))
dao_contract = w3.eth.contract(address=DAO_CONTRACT_ADDRESS, abi=contract_abi)

@gov_bp.route('/governance/proposals', methods=['GET'])
def get_proposals():
    # Example: fetch all proposals (assumes contract has getProposals or similar)
    try:
        proposals = dao_contract.functions.getProposals().call()
        return jsonify({"proposals": proposals})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@gov_bp.route('/governance/votes/<int:proposal_id>', methods=['GET'])
def get_votes(proposal_id):
    # Example: fetch votes for a proposal (assumes contract has getVotes or similar)
    try:
        votes = dao_contract.functions.getVotes(proposal_id).call()
        return jsonify({"votes": votes})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
