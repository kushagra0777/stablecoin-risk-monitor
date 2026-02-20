"""
Retrain AI models with updated feature engineering (19 features)
This script generates synthetic training data and retrains the models
"""

import sys
import os
import numpy as np
import pandas as pd

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_engine.anomaly_detector import ENGINE
from ai_engine.feature_engineering import build_features


def generate_training_data(n_samples=500):
    """
    Generate synthetic training data with proper labels
    """
    print(f"Generating {n_samples} training samples...")
    
    training_snapshots = []
    labels = []
    
    for i in range(n_samples):
        # Generate varied scenarios
        if i < n_samples * 0.7:  # 70% SAFE
            reserves = np.random.uniform(1_000_000, 10_000_000)
            supply = np.random.uniform(0.8 * reserves, 1.2 * reserves)
            price = np.random.uniform(0.98, 1.02)
            whale_supply = np.random.uniform(0, 0.1 * supply)
            equity_float = supply - whale_supply
            label = 0  # SAFE
            
        elif i < n_samples * 0.9:  # 20% WARNING
            reserves = np.random.uniform(500_000, 5_000_000)
            supply = np.random.uniform(1.2 * reserves, 1.5 * reserves)
            price = np.random.uniform(0.95, 1.05)
            whale_supply = np.random.uniform(0.1 * supply, 0.3 * supply)
            equity_float = supply - whale_supply
            label = 1  # WARNING
            
        else:  # 10% RISKY
            reserves = np.random.uniform(100_000, 1_000_000)
            supply = np.random.uniform(1.5 * reserves, 3 * reserves)
            price = np.random.uniform(0.90, 1.10)
            whale_supply = np.random.uniform(0.3 * supply, 0.5 * supply)
            equity_float = supply - whale_supply
            label = 2  # RISKY
        
        # Calculate market cap and ratios
        market_cap = supply * price
        float_ratio = equity_float / supply
        cash_to_market_cap = reserves / market_cap
        
        snapshot = {
            'reserves': reserves,
            'supply': supply,
            'price': price,
            'whale_supply': whale_supply,
            'custodians': [],
            'equity_float': equity_float,
            'market_cap': market_cap,
            'float_ratio': float_ratio,
            'cash_to_market_cap': cash_to_market_cap
        }
        
        # Add some previous values for delta calculations
        if i > 0:
            prev = training_snapshots[-1]
            snapshot['prev_reserves'] = prev['reserves']
            snapshot['prev_supply'] = prev['supply']
            snapshot['prev_price'] = prev['price']
        
        training_snapshots.append(snapshot)
        labels.append(label)
    
    # Build features for all snapshots
    feature_dfs = []
    for i, snapshot in enumerate(training_snapshots):
        prev_snapshot = training_snapshots[i-1] if i > 0 else None
        features = build_features(snapshot, prev_snapshot)
        feature_dfs.append(features)
    
    df_features = pd.concat(feature_dfs, ignore_index=True)
    
    print(f"✓ Generated {len(df_features)} feature vectors with {len(df_features.columns)} features")
    print(f"  Features: {list(df_features.columns)}")
    print(f"  Label distribution: SAFE={labels.count(0)}, WARNING={labels.count(1)}, RISKY={labels.count(2)}")
    
    return df_features, labels


def retrain_models():
    """
    Retrain the AI models with updated feature engineering
    """
    print("=" * 70)
    print("RETRAINING AI MODELS WITH UPDATED FEATURES")
    print("=" * 70)
    print()
    
    # Generate training data
    df_features, labels = generate_training_data(n_samples=500)
    
    print()
    print("Training models...")
    
    # Train the models
    ENGINE.train(df_features, labels)
    
    print("✓ Models trained and saved successfully!")
    print()
    
    # Test the models
    print("Testing models with sample data...")
    
    test_cases = [
        {
            'name': 'SAFE scenario',
            'snapshot': {
                'reserves': 5_000_000,
                'supply': 5_000_000,
                'price': 1.0,
                'whale_supply': 100_000,
                'equity_float': 4_900_000,
                'market_cap': 5_000_000,
                'float_ratio': 0.98,
                'cash_to_market_cap': 1.0
            }
        },
        {
            'name': 'WARNING scenario',
            'snapshot': {
                'reserves': 1_000_000,
                'supply': 1_500_000,
                'price': 0.98,
                'whale_supply': 300_000,
                'equity_float': 1_200_000,
                'market_cap': 1_470_000,
                'float_ratio': 0.80,
                'cash_to_market_cap': 0.68
            }
        },
        {
            'name': 'RISKY scenario',
            'snapshot': {
                'reserves': 500_000,
                'supply': 1_500_000,
                'price': 0.90,
                'whale_supply': 600_000,
                'equity_float': 900_000,
                'market_cap': 1_350_000,
                'float_ratio': 0.60,
                'cash_to_market_cap': 0.37
            }
        }
    ]
    
    print()
    print("-" * 70)
    print(f"{'Scenario':<20} {'Risk Score':<12} {'Label':<12} {'Details'}")
    print("-" * 70)
    
    for case in test_cases:
        result = ENGINE.analyze_snapshot(case['snapshot'])
        print(f"{case['name']:<20} {result['risk_score']:<12} {result['label']:<12} "
              f"R/S ratio: {result['explanation']['reserve_supply_ratio']:.2f}")
    
    print("-" * 70)
    print()
    
    print("=" * 70)
    print("RETRAINING COMPLETE!")
    print("=" * 70)
    print()
    print("The models are now updated to work with 19 features including:")
    print("- Core metrics (reserves, supply, price)")
    print("- Ratios (reserve/supply, whale, float)")
    print("- Delta features (changes in reserves, supply, price)")
    print("- Equity-specific features (market cap, cash/market cap ratio)")
    print()
    print("You can now run: python tests/test_excel_import.py")
    print()


if __name__ == "__main__":
    retrain_models()
