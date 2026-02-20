
# 🛡️ Stablecoin Risk Monitor

AI-powered risk monitoring system for stablecoins and financial assets with **Desktop GUI**, Excel import, and machine learning analysis.

## ✨ Key Features

- **🖥️ Desktop GUI**: Beautiful tkinter interface - no web server needed!
- **📊 Excel Import**: Analyze .xlsx, .xls, CSV files instantly
- **🤖 AI Analysis**: 19-feature ML models (Isolation Forest + XGBoost)
- **🌐 Web API**: RESTful API for integration
- **⚛️ React Frontend**: Modern web interface
- **🔗 Blockchain**: Smart contracts for governance & proof of reserves

## 🚀 Quick Start - Desktop GUI ⭐

```bash
# Windows - Just double-click!
run_gui.bat

# Or run manually
python gui.py
```

**Then:** Browse → Select Excel → Analyze → Export! 

📖 [Full GUI Guide](docs/GUI_USER_GUIDE.md) | [Quick Start](QUICK_START.md)

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
