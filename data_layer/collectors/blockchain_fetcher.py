
def get_blockchain_data():

    supply = 1_200_000  # mock supply from smart contract
    whale_supply = 25_000  # mock top-wallet concentration (replace later)
    return {
        "circulatingSupply": float(supply),
        "whale_supply": float(whale_supply)
    }