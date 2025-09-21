from data_layer.collectors.exchange_fetcher import fetch_supply
from data_layer.collectors.mock_custodian import get_mock_reserves
from crypto_layer.merkle_tree import get_merkle_root
from ai_engine.anomaly_detector import AnomalyDetector
import numpy as np

def run():
    supply = fetch_supply()
    reserves = sum([r["balance"] for r in get_mock_reserves()])
    leaves = [str(reserves), str(supply)]
    root = get_merkle_root(leaves)

    print("Merkle Root:", root)

    model = AnomalyDetector()
    training_data = np.array([[1000000, 1100000], [1050000, 1060000]])
    model.train(training_data)

    result = model.predict([supply, reserves])
    if result == -1:
        print("🚨 Anomaly detected!")
    else:
        print("✅ All Good")

if __name__ == "__main__":
    run()
