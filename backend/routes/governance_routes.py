# governance_routes.py
# API endpoints to fetch contract state for dashboard integration

from flask import Blueprint, jsonify
from web3 import Web3
import os
import json
from pathlib import Path

def _load_integration_env():
    # If environment variables are missing, try to read integration/.env
    env_path = Path(__file__).resolve().parents[2] / "integration" / ".env"
    if not env_path.exists():
        return
    try:
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            k, v = line.split('=', 1)
            k = k.strip()
            v = v.strip()
            # don't override already set env vars
            if os.getenv(k) is None:
                os.environ[k] = v
    except Exception:
        # best-effort only
        pass

gov_bp = Blueprint('governance', __name__)

# Load environment variables
_load_integration_env()
RPC_URL = os.getenv('RPC_URL', 'http://127.0.0.1:8545')
DAO_CONTRACT_ADDRESS = os.getenv('DAO_CONTRACT_ADDRESS')
CONTRACT_ABI_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../blockchain_layer/contracts/GovernanceDAO.json'))

# Load contract ABI (if available)
contract_abi = None
if os.path.exists(CONTRACT_ABI_PATH):
    with open(CONTRACT_ABI_PATH) as f:
        try:
            contract_abi = json.load(f).get("abi")
        except Exception:
            contract_abi = None

w3 = Web3(Web3.HTTPProvider(RPC_URL))

def _get_dao_contract():
    if not DAO_CONTRACT_ADDRESS:
        return None, "DAO_CONTRACT_ADDRESS not set in environment (tried env and integration/.env)"
    if contract_abi is None:
        return None, "GovernanceDAO ABI not found"
    try:
        dao = w3.eth.contract(address=DAO_CONTRACT_ADDRESS, abi=contract_abi)
        return dao, None
    except Exception as e:
        return None, str(e)


@gov_bp.route('/governance/proposals', methods=['GET'])
def get_proposals():
    dao, err = _get_dao_contract()
    if err:
        return jsonify({"error": err}), 500
    try:
        # GovernanceDAO exposes getAllProposals()
        proposal_ids = dao.functions.getAllProposals().call()
        return jsonify({"proposals": list(proposal_ids)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@gov_bp.route('/governance/votes/<int:proposal_id>', methods=['GET'])
def get_votes(proposal_id):
    dao, err = _get_dao_contract()
    if err:
        return jsonify({"error": err}), 500
    try:
        # getProposal returns the proposal tuple; map the fields we care about
        p = dao.functions.getProposal(proposal_id).call()
        # p ordering matches the Proposal struct in the contract
        # id, proposer, title, description, startTime, endTime, forVotes, againstVotes, abstainVotes, executed, state, target, data, value
        result = {
            "id": p[0],
            "proposer": p[1],
            "title": p[2],
            "description": p[3],
            "startTime": p[4],
            "endTime": p[5],
            "forVotes": int(p[6]),
            "againstVotes": int(p[7]),
            "abstainVotes": int(p[8]),
            "executed": bool(p[9])
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
