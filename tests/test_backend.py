
import sys
import os
import unittest
import json
from unittest.mock import patch, MagicMock

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app

class TestBackend(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.testing = True

    # --- System & Health Checks ---
    def test_health(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "healthy"})

    # --- Data Routes ---
    @patch('backend.routes.data_routes.get_exchange_data')
    @patch('backend.routes.data_routes.get_custodian_data')
    @patch('backend.routes.data_routes.get_blockchain_data')
    def test_data_snapshot(self, mock_chain, mock_cust, mock_exch):
        mock_exch.return_value = {"price": 1.05}
        mock_cust.return_value = {"totalReserves": 1000, "custodians": [600, 400]}
        mock_chain.return_value = {"circulatingSupply": 950, "whale_supply": 100}

        response = self.client.get('/api/data/snapshot')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data['price'], 1.05)
        self.assertEqual(data['reserves'], 1000)
        self.assertEqual(data['supply'], 950)

    # --- Risk Routes ---
    def test_analyze_validation_success(self):
        payload = {
            "reserves": 1000000,
            "supply": 1000000,
            "price": 1.0,
            "whales": 0
        }
        response = self.client.post('/api/risk/analyze', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("risk_score", response.json)

    def test_analyze_validation_fail(self):
        payload = {
            "reserves": -100, # Invalid
            "supply": 1000000,
            "price": 1.0
        }
        response = self.client.post('/api/risk/analyze', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    def test_debug_alert(self):
        response = self.client.get('/api/risk/debug/alert')
        self.assertEqual(response.status_code, 200)
        self.assertIn("alert", response.json)
        self.assertIn("risk_score", response.json)

    @patch('backend.routes.risk_routes.ENGINE.analyze_live')
    def test_analyze_live(self, mock_analyze):
        mock_analyze.return_value = {"risk_score": 50, "label": "WARNING", "explanation": {}}
        response = self.client.get('/api/risk/analyze/live')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['risk_score'], 50)

    def test_rescore_history_no_file(self):
        # Ensure we don't accidentally rely on a file existing on the user's disk
        with patch('os.path.exists', return_value=False):
            response = self.client.get('/api/risk/rescore/history')
            self.assertEqual(response.status_code, 404)

    # --- Governance Routes ---
    @patch('backend.routes.governance_routes._get_dao_contract')
    def test_get_proposals(self, mock_get_dao):
        # Mock DAO contract
        mock_dao = MagicMock()
        mock_dao.functions.getAllProposals.return_value.call.return_value = [1, 2, 3]
        mock_get_dao.return_value = (mock_dao, None)

        response = self.client.get('/governance/proposals')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['proposals'], [1, 2, 3])

    @patch('backend.routes.governance_routes._get_dao_contract')
    def test_get_proposals_error(self, mock_get_dao):
        # Mock error from contract getter
        mock_get_dao.return_value = (None, "Contract not found")
        
        response = self.client.get('/governance/proposals')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json['error'], "Contract not found")

    @patch('backend.routes.governance_routes._get_dao_contract')
    def test_get_votes(self, mock_get_dao):
        mock_dao = MagicMock()
        # id, proposer, title, description, startTime, endTime, forVotes, againstVotes, abstainVotes, executed
        proposal_tuple = (1, "0x123", "Test Prop", "Desc", 100, 200, 10, 5, 2, True)
        mock_dao.functions.getProposal.return_value.call.return_value = proposal_tuple
        mock_get_dao.return_value = (mock_dao, None)

        response = self.client.get('/governance/votes/1')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['title'], "Test Prop")
        self.assertEqual(data['forVotes'], 10)
        self.assertEqual(data['executed'], True)

if __name__ == '__main__':
    unittest.main()
