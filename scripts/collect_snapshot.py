import os
import sys
import csv
import json
import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_layer.collectors.blockchain_fetcher import get_blockchain_data
from data_layer.collectors.mock_custodian import get_custodian_data
from data_layer.collectors.exchange_fetcher import get_exchange_data

SNAPSHOT_DIR = "data_layer/snapshots"
CSV_PATH = "data/historical_snapshots.csv"

os.makedirs(SNAPSHOT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)


def collect_snapshot():
    chain = get_blockchain_data()
    cust = get_custodian_data()
    exch = get_exchange_data()


    snapshot = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "reserves": float(cust.get("totalReserves", 0)),
        "custodians": cust.get("custodians", []),
        "supply": float(chain.get("circulatingSupply", 0)),
        "whale_supply": float(chain.get("whale_supply", 0)),
        "price": float(exch.get("price", 1.0))
    }

    file_safe_ts = snapshot["timestamp"].replace(":", "-")
    json_path = os.path.join(SNAPSHOT_DIR, f"snapshot_{file_safe_ts}.json")

    with open(json_path, "w") as f:
        json.dump(snapshot, f, indent=4)

    write_header = not os.path.exists(CSV_PATH)

    with open(CSV_PATH, "a", newline="") as f:
        writer = csv.writer(f)

        if write_header:
            writer.writerow([
                "timestamp",
                "reserves",
                "supply",
                "whale_supply",
                "price",
                "custodians"
            ])

        writer.writerow([
            snapshot["timestamp"],
            snapshot["reserves"],
            snapshot["supply"],
            snapshot["whale_supply"],
            snapshot["price"],
            json.dumps(snapshot["custodians"])
        ])

    print(f"[INFO] Snapshot saved → {json_path}")
    print(f"[INFO] CSV updated → {CSV_PATH}")

    return snapshot


if __name__ == "__main__":
    collect_snapshot()