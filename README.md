
# Stablecoin Risk Monitor

A risk monitoring system for stablecoins, integrating on-chain data, exchange data, and AI-based anomaly detection.

## Features

- **Data Collection**: Fetches data from exchanges (mock/real) and blockchain.
- **Risk Analysis**: AI engine to detect anomalies in supply, reserves, and price.
- **Governance Integration**: Monitors DAO proposals and votes.
- **API**: REST API for frontend integration.

## Setup

### Prerequisites

- Python 3.9+
- Docker (optional)

### Local Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   Create a `.env` file in the root directory (optional, defaults provided):
   ```env
   FLASK_DEBUG=True
   PORT=5000
   RPC_URL=http://127.0.0.1:8545
   DAO_CONTRACT_ADDRESS=0x...
   LOG_LEVEL=INFO
   ```

3. **Run Backend**
   ```bash
   # From the root directory
   python -m backend.app
   ```
   The API will be available at `http://localhost:5000`.

### Docker Setup

1. **Build and Run**
   ```bash
   docker-compose up --build
   ```

## API Documentation

### Health Check
- `GET /health`
  - Returns: `{"status": "healthy"}`

### Data Endpoints
- `GET /api/data/snapshot`
  - Returns current market and chain data.

### Risk Endpoints
- `POST /api/risk/analyze`
  - Body:
    ```json
    {
      "reserves": 1000000,
      "supply": 1000000,
      "price": 0.99,
      "whales": 50000
    }
    ```
  - Returns: Risk score and analysis.

### Governance Endpoints
- `GET /api/governance/proposals`
- `GET /api/governance/votes/<proposal_id>`
