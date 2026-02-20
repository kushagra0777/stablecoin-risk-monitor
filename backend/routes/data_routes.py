from flask import Blueprint, jsonify, request
from data_layer.collectors.exchange_fetcher import get_exchange_data
from data_layer.collectors.mock_custodian import get_custodian_data
from data_layer.collectors.blockchain_fetcher import get_blockchain_data
from data_layer.collectors.excel_importer import EXCEL_IMPORTER
from werkzeug.utils import secure_filename
import os
import tempfile

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


@bp.route("/upload-excel", methods=["POST"])
def upload_excel():
    """
    Upload and process Excel file with equity/financial data
    
    Expected file formats: .xlsx, .xls, .csv
    Expected columns:
    - Company
    - bs_cash_cash_equivalents_and_sti
    - eqy_float
    - eqy_sh_out
    - px_last
    
    Returns JSON with:
    - snapshots: List of processed data snapshots
    - summary: Data statistics
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Validate file extension
        allowed_extensions = {'.xlsx', '.xls', '.csv'}
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({
                "error": f"Unsupported file format. Allowed: {', '.join(allowed_extensions)}"
            }), 400
        
        # Read file bytes
        file_bytes = file.read()
        
        # Import and transform data
        df = EXCEL_IMPORTER.import_from_bytes(file_bytes, filename)
        
        # Validate required columns
        required_columns = [
            'Company',
            'bs_cash_cash_equivalents_and_sti',
            'eqy_float',
            'eqy_sh_out',
            'px_last'
        ]
        
        is_valid, missing_cols = EXCEL_IMPORTER.validate_data(df, required_columns)
        
        if not is_valid:
            return jsonify({
                "error": "Missing required columns",
                "missing_columns": missing_cols,
                "found_columns": list(df.columns)
            }), 400
        
        # Transform to snapshots
        snapshots = EXCEL_IMPORTER.transform_equity_to_snapshots(df)
        
        # Get summary statistics
        summary = EXCEL_IMPORTER.get_data_summary(df)
        
        return jsonify({
            "success": True,
            "filename": filename,
            "snapshots": snapshots,
            "summary": summary,
            "count": len(snapshots)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/analyze-excel", methods=["POST"])
def analyze_excel():
    """
    Upload Excel file and immediately analyze for risks
    
    Returns risk analysis for each company in the dataset
    """
    try:
        from ai_engine.anomaly_detector import ENGINE
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        filename = secure_filename(file.filename)
        file_bytes = file.read()
        
        # Import and transform data
        df = EXCEL_IMPORTER.import_from_bytes(file_bytes, filename)
        snapshots = EXCEL_IMPORTER.transform_equity_to_snapshots(df)
        
        # Analyze each snapshot
        results = []
        for i, snapshot in enumerate(snapshots):
            prev_snapshot = snapshots[i-1] if i > 0 else None
            
            analysis = ENGINE.analyze_snapshot(snapshot, prev_snapshot)
            
            results.append({
                "company": snapshot.get("company", f"Company_{i}"),
                "risk_score": analysis["risk_score"],
                "risk_label": analysis["label"],
                "explanation": analysis["explanation"],
                "metrics": {
                    "reserves": snapshot["reserves"],
                    "supply": snapshot["supply"],
                    "price": snapshot["price"],
                    "market_cap": snapshot.get("market_cap", 0),
                    "cash_to_market_cap": snapshot.get("cash_to_market_cap", 0)
                }
            })
        
        return jsonify({
            "success": True,
            "filename": filename,
            "results": results,
            "total_analyzed": len(results)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
