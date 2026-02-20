# Excel Data Import Feature

## Overview
This feature allows you to import and analyze equity/financial data from Excel files (.xlsx, .xls, .csv) in the Stablecoin Risk Monitor system.

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

Or specifically:
```bash
pip install openpyxl pandas numpy scikit-learn xgboost
```

## Data Format

The Excel file should contain the following columns:

| Column Name | Description | Type |
|------------|-------------|------|
| Company | Company name or identifier | Text |
| bs_cash_cash_equivalents_and_sti | Cash and cash equivalents (reserves) | Number |
| eqy_float | Equity float (freely traded shares) | Number |
| eqy_sh_out | Equity shares outstanding (total supply) | Number |
| px_last | Last traded price | Number |

### Example Data Structure:
```
Company                 | bs_cash_... | eqy_float   | eqy_sh_out  | px_last
------------------------|-------------|-------------|-------------|--------
AAPL US Equity         | 66907000000 | 14433337344 | 14681140000 | 260.58
GOOGL US Equity        | 126843000000| 5785339392  | 5822000000  | 302.85
```

## Usage

### 1. Command Line Testing

Test with built-in dataset:
```bash
python tests/test_excel_import.py
```

This will:
- Create a test dataset with 12 companies
- Validate the data format
- Transform to risk snapshots
- Analyze risk for each company
- Display summary statistics

### 2. API Endpoints

#### Upload and View Data
```http
POST /api/data/upload-excel
Content-Type: multipart/form-data

file: <your_excel_file.xlsx>
```

Response:
```json
{
  "success": true,
  "filename": "equity_data.xlsx",
  "snapshots": [...],
  "summary": {
    "row_count": 12,
    "column_count": 5,
    "basic_stats": {...}
  },
  "count": 12
}
```

#### Upload and Analyze
```http
POST /api/data/analyze-excel
Content-Type: multipart/form-data

file: <your_excel_file.xlsx>
```

Response:
```json
{
  "success": true,
  "filename": "equity_data.xlsx",
  "results": [
    {
      "company": "AAPL US Equity",
      "risk_score": 20.0,
      "risk_label": "SAFE",
      "explanation": {...},
      "metrics": {
        "reserves": 66907000000,
        "supply": 14681140000,
        "price": 260.58,
        "market_cap": 3824970000000,
        "cash_to_market_cap": 0.0175
      }
    },
    ...
  ],
  "total_analyzed": 12
}
```

### 3. Python Script

```python
from data_layer.collectors.excel_importer import import_excel_data
from ai_engine.anomaly_detector import ENGINE

# Import data
snapshots = import_excel_data('data/equity_data.xlsx')

# Analyze each company
for snapshot in snapshots:
    result = ENGINE.analyze_snapshot(snapshot)
    print(f"{snapshot['company']}: {result['label']} (Score: {result['risk_score']})")
```

## Data Transformation

The system automatically transforms equity data into a risk analysis format:

| Equity Metric | Risk Analysis Mapping |
|--------------|---------------------|
| Cash & Equivalents | Reserves |
| Shares Outstanding | Supply |
| Price | Price |
| Non-Float Shares | Whale Supply |
| Market Cap | Calculated: shares × price |
| Cash/Market Cap | Risk indicator |
| Float Ratio | Liquidity indicator |

## Features Generated

The system generates 19 features for analysis:

### Core Metrics
- `reserves`: Cash and equivalents
- `supply`: Total shares outstanding
- `price`: Last traded price
- `diff`: Supply - Reserves imbalance

### Ratios
- `reserve_supply_ratio`: Reserves / Supply
- `whale_ratio`: Non-float shares / Supply
- `float_ratio`: Float / Supply
- `cash_to_market_cap`: Cash / Market Cap

### Delta Features (Changes)
- `delta_reserves`: Change in reserves
- `delta_supply`: Change in supply
- `delta_price`: Change in price
- `pct_reserve_change`: % change in reserves
- `pct_supply_change`: % change in supply
- `pct_price_change`: % change in price

### Derived Features
- `market_cap`: Market capitalization
- `equity_float`: Freely traded shares
- `liquidity_score`: Overall liquidity metric
- `price_volatility`: Price change volatility
- `custodian_variance`: Variance in custodian holdings

## Risk Scoring

### Risk Labels
- **SAFE** (0-40): Low risk, good reserves/supply ratio
- **WARNING** (41-70): Moderate risk, monitor closely
- **RISKY** (71-100): High risk, immediate attention needed

### Risk Score Components
1. **Anomaly Detection**: Isolation Forest identifies unusual patterns
2. **Risk Classification**: XGBoost predicts risk probability
3. **Reserve Ratio**: Cash-to-market-cap and reserve-supply ratios
4. **Whale Concentration**: Large holder concentration
5. **Price Volatility**: Price stability indicators

## Example Output

```
======================================================================
RISK ANALYSIS RESULTS
======================================================================

Company                   Risk Score   Label        Cash/MCap
----------------------------------------------------------------------
AAPL US Equity            20.0000      SAFE         0.0175      
GOOGL US Equity           20.0000      SAFE         0.0719      
NVDA US Equity            20.0000      SAFE         0.0133      
----------------------------------------------------------------------

Risk Distribution:
- SAFE: 10 companies (83.3%)
- WARNING: 2 companies (16.7%)
- RISKY: 0 companies (0.0%)
```

## Retraining Models

If you need to retrain the AI models with new data:

```bash
python scripts/retrain_models.py
```

This will:
1. Generate synthetic training data (500 samples)
2. Train Isolation Forest for anomaly detection
3. Train XGBoost classifier for risk prediction
4. Save models to `models/` directory
5. Validate with test scenarios

## Troubleshooting

### Error: "Missing required columns"
- Ensure your Excel file has all 5 required columns
- Check column names match exactly (case-sensitive)
- Remove any extra header rows

### Error: "X has N features, but model expects M"
- Run `python scripts/retrain_models.py` to retrain models
- This updates models to work with current feature set

### Error: "No module named 'openpyxl'"
- Install: `pip install openpyxl`
- Or install all: `pip install -r requirements.txt`

## Files Modified/Created

1. **requirements.txt** - Added `openpyxl==3.1.2`
2. **data_layer/collectors/excel_importer.py** - Excel import module
3. **backend/routes/data_routes.py** - Added `/upload-excel` and `/analyze-excel` endpoints
4. **ai_engine/feature_engineering.py** - Extended to 19 features including equity metrics
5. **tests/test_excel_import.py** - Comprehensive test suite
6. **scripts/retrain_models.py** - Model retraining script

## Next Steps

1. Save your equity data as Excel file
2. Test locally: `python tests/test_excel_import.py`
3. Start the API server: `python backend/app.py`
4. Upload data via API or frontend
5. Review risk analysis results
6. Set up alerts for WARNING/RISKY companies

## API Integration Example (curl)

```bash
# Upload and analyze Excel file
curl -X POST http://localhost:5000/api/data/analyze-excel \
  -F "file=@equity_data.xlsx" \
  -H "Content-Type: multipart/form-data"
```

## Frontend Integration Example (JavaScript)

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('/api/data/analyze-excel', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('Analysis results:', data.results);
  displayResults(data.results);
})
.catch(error => console.error('Error:', error));
```
