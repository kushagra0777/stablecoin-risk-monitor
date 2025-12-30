import random
import time

def get_custodian_data():

    total_reserves = random.uniform(950_000, 1_050_000)

    custodian_breakdown = [
        total_reserves * 0.6,
        total_reserves * 0.4
    ]
    return {
        "totalReserves": float(total_reserves),
        "custodians": [float(x) for x in custodian_breakdown],
        "timestamp": time.time()
    }