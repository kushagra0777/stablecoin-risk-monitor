"""
merkle_proof_generator.py
Generates Merkle proofs from mock custodian balances for off-chain integration.
"""

from data_layer.collectors.mock_custodian import get_mock_reserves
from crypto_layer.merkle_tree import build_merkle_tree, sha256

class MerkleProofGenerator:
    def __init__(self):
        self.reserves = get_mock_reserves()
        self.leaves = [self._leaf_hash(r) for r in self.reserves]
        self.tree = build_merkle_tree(self.leaves)

    def _leaf_hash(self, reserve):
        # Hash account and balance as a string
        return sha256(f"{reserve['account']}:{reserve['balance']}")

    def get_merkle_root(self):
        return self.tree[-1][0] if self.tree else None

    def get_proof(self, index):
        # Returns the Merkle proof for the leaf at the given index
        proof = []
        num_levels = len(self.tree)
        for level in range(num_levels - 1):
            level_nodes = self.tree[level]
            sibling_index = index ^ 1
            if sibling_index < len(level_nodes):
                proof.append(level_nodes[sibling_index])
            index //= 2
        return proof

if __name__ == "__main__":
    mpg = MerkleProofGenerator()
    print("Merkle Root:", mpg.get_merkle_root())
    for i, reserve in enumerate(mpg.reserves):
        print(f"Proof for {reserve['account']}: {mpg.get_proof(i)}")
