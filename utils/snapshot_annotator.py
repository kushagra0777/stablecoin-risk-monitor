import json
import os
from ai_engine.anomaly_detector import ENGINE


def annotate_snapshot(input_path: str, output_path: str):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Snapshot not found: {input_path}")

    with open(input_path, "r") as f:
        snapshot = json.load(f)

    result = ENGINE.analyze_snapshot(snapshot)

    snapshot["risk"] = {
        "risk_score": result["risk_score"],
        "label": result["label"],
        "features": result["raw_features"],
        "explanation": result["explanation"],
    }
    with open(output_path, "w") as f:
        json.dump(snapshot, f, indent=4)

    print(f"[INFO] Snapshot annotated → {output_path}")
