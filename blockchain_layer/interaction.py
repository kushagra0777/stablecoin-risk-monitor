from web3 import Web3

# connect to local Hardhat or Sepolia
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# load contract ABI + address
import json
with open("blockchain_layer/contracts/ProofOfReserves.json") as f:
    abi = json.load(f)["abi"]

contract_address = "0xYourDeployedContract"
contract = w3.eth.contract(address=contract_address, abi=abi)

def update_supply(supply):
    # TODO: Add tx signing
    tx = contract.functions.setSupply(supply).build_transaction()
    return tx

def verify(total_reserves):
    return contract.functions.verifyProof(total_reserves).call()
