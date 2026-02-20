"""
Test script for Excel import functionality with equity data
"""

import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_layer.collectors.excel_importer import EXCEL_IMPORTER
from ai_engine.anomaly_detector import ENGINE
from ai_engine.feature_engineering import build_features


def create_test_dataset():
    """
    Create test dataset based on the provided equity data
    """
    data = {
        'Company': [
            '005930 KS Equity', '6758 JT Equity', 'AAPL US Equity', 'ACKB BB Equity',
            'CAP FP Equity', 'CPHN SW Equity', 'GOOGL US Equity', 'IBM US Equity',
            'NOVOB DC Equity', 'NVDA US Equity', 'RELIANCE IN Equity', 'WPP LN Equity'
        ],
        'bs_cash_cash_equivalents_and_sti': [
            125847000000000, 2086500000000, 66907000000, 0,
            3032000000, 27042000, 126843000000, 14417000000,
            26962000000, 60608000000, 223871000000, 1437000000
        ],
        'eqy_float': [
            4865424384, 5954229248, 14433337344, 21135574,
            168198784, 37045450, 5785339392, 933439488,
            3364180992, 23372908544, 5980084224, 1078711296
        ],
        'eqy_sh_out': [
            5919637922, 6149810645, 14681140000, 33157750,
            169928671, 60000000, 5822000000, 934735206,
            3390128000, 24300000000, 13532472634, 1078802358
        ],
        'px_last': [
            190300, 3336, 260.58, 287.4,
            103.95, 85, 302.85, 256.28,
            307.4, 187.9, 1425.699951, 275.4
        ]
    }
    
    df = pd.DataFrame(data)
    return df


def test_excel_import():
    """Test the Excel import functionality"""
    print("=" * 70)
    print("EXCEL IMPORT TEST FOR STABLECOIN RISK MONITOR")
    print("=" * 70)
    print()
    
    # Create test dataset
    print("1. Creating test dataset...")
    df = create_test_dataset()
    print(f"   ✓ Created dataset with {len(df)} companies")
    print(f"   Columns: {list(df.columns)}")
    print()
    
    # Validate data
    print("2. Validating dataset...")
    required_columns = [
        'Company',
        'bs_cash_cash_equivalents_and_sti',
        'eqy_float',
        'eqy_sh_out',
        'px_last'
    ]
    is_valid, missing = EXCEL_IMPORTER.validate_data(df, required_columns)
    
    if is_valid:
        print("   ✓ All required columns present")
    else:
        print(f"   ✗ Missing columns: {missing}")
        return False
    print()
    
    # Get summary statistics
    print("3. Generating data summary...")
    summary = EXCEL_IMPORTER.get_data_summary(df)
    print(f"   Rows: {summary['row_count']}")
    print(f"   Columns: {summary['column_count']}")
    print(f"   Numeric columns: {len(summary['numeric_columns'])}")
    print()
    
    # Transform to snapshots
    print("4. Transforming to risk snapshots...")
    snapshots = EXCEL_IMPORTER.transform_equity_to_snapshots(df)
    print(f"   ✓ Created {len(snapshots)} snapshots")
    print()
    
    # Display first snapshot details
    if snapshots:
        print("5. Sample snapshot (first company):")
        first = snapshots[0]
        print(f"   Company: {first['company']}")
        print(f"   Reserves (Cash): ${first['reserves']:,.0f}")
        print(f"   Supply (Shares): {first['supply']:,.0f}")
        print(f"   Price: ${first['price']:.2f}")
        print(f"   Market Cap: ${first['market_cap']:,.0f}")
        print(f"   Cash/Market Cap Ratio: {first['cash_to_market_cap']:.4f}")
        print(f"   Float Ratio: {first['float_ratio']:.4f}")
        print()
    
    # Test feature engineering
    print("6. Testing feature engineering...")
    try:
        features = build_features(snapshots[0])
        print(f"   ✓ Generated {len(features.columns)} features")
        print(f"   Feature columns: {list(features.columns)}")
        print()
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        return False
    
    # Test risk analysis
    print("7. Analyzing risk for all companies...")
    print()
    print("-" * 70)
    print(f"{'Company':<25} {'Risk Score':<12} {'Label':<12} {'Cash/MCap':<12}")
    print("-" * 70)
    
    for i, snapshot in enumerate(snapshots):
        try:
            prev_snapshot = snapshots[i-1] if i > 0 else None
            result = ENGINE.analyze_snapshot(snapshot, prev_snapshot)
            
            company = snapshot['company'][:24]
            risk_score = result['risk_score']
            label = result['label']
            cash_ratio = snapshot['cash_to_market_cap']
            
            print(f"{company:<25} {risk_score:<12.4f} {label:<12} {cash_ratio:<12.4f}")
            
        except Exception as e:
            print(f"{snapshot['company']:<25} ERROR: {str(e)}")
    
    print("-" * 70)
    print()
    
    # Summary statistics
    print("8. Risk Analysis Summary:")
    risk_labels = [ENGINE.analyze_snapshot(s)['label'] for s in snapshots]
    label_counts = pd.Series(risk_labels).value_counts().to_dict()
    
    for label, count in label_counts.items():
        print(f"   {label}: {count} companies ({count/len(snapshots)*100:.1f}%)")
    print()
    
    # Identify highest risk
    print("9. Highest Risk Companies:")
    risks = [(s['company'], ENGINE.analyze_snapshot(s)['risk_score']) 
             for s in snapshots]
    risks.sort(key=lambda x: x[1], reverse=True)
    
    for i, (company, score) in enumerate(risks[:3], 1):
        print(f"   {i}. {company}: {score:.4f}")
    print()
    
    print("=" * 70)
    print("TEST COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    
    return True


def test_feature_coverage():
    """Test that all features work correctly with equity data"""
    print("\n" + "=" * 70)
    print("FEATURE COVERAGE TEST")
    print("=" * 70)
    print()
    
    df = create_test_dataset()
    snapshots = EXCEL_IMPORTER.transform_equity_to_snapshots(df)
    
    print("Testing feature engineering on all companies...")
    print()
    
    all_features = []
    for i, snapshot in enumerate(snapshots):
        prev_snapshot = snapshots[i-1] if i > 0 else None
        features = build_features(snapshot, prev_snapshot)
        all_features.append(features)
    
    # Combine all features
    combined_features = pd.concat(all_features, ignore_index=True)
    
    print(f"Total samples: {len(combined_features)}")
    print(f"Total features: {len(combined_features.columns)}")
    print()
    
    print("Feature Statistics:")
    print("-" * 70)
    for col in combined_features.columns:
        stats = combined_features[col].describe()
        print(f"{col}:")
        print(f"  Mean: {stats['mean']:.4e}, Std: {stats['std']:.4e}")
        print(f"  Min: {stats['min']:.4e}, Max: {stats['max']:.4e}")
        print()
    
    # Check for missing or infinite values
    print("Data Quality Check:")
    null_counts = combined_features.isnull().sum()
    inf_counts = combined_features.isin([float('inf'), float('-inf')]).sum()
    
    if null_counts.sum() == 0 and inf_counts.sum() == 0:
        print("  ✓ No missing or infinite values")
    else:
        print(f"  ✗ Null values: {null_counts.sum()}")
        print(f"  ✗ Infinite values: {inf_counts.sum()}")
    
    print()
    
    return True


if __name__ == "__main__":
    print("\n")
    
    # Run main test
    success = test_excel_import()
    
    if success:
        # Run feature coverage test
        test_feature_coverage()
        
        print("\n" + "=" * 70)
        print("ALL TESTS PASSED!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Save your equity data as 'equity_data.xlsx' in the data/ folder")
        print("2. Run: python tests/test_excel_import.py")
        print("3. Use the API endpoints:")
        print("   - POST /api/data/upload-excel (upload and view data)")
        print("   - POST /api/data/analyze-excel (upload and analyze)")
        print()
    else:
        print("\n✗ Tests failed!")
        sys.exit(1)
