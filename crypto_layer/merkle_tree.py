import hashlib

def sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

def build_merkle_tree(leaves):
    tree = [leaves]
    while len(tree[-1]) > 1:
        level = []
        for i in range(0, len(tree[-1]), 2):
            left = tree[-1][i]
            right = tree[-1][i+1] if i+1 < len(tree[-1]) else left
            level.append(sha256(left + right))
        tree.append(level)
    return tree

def get_merkle_root(leaves):
    return build_merkle_tree(leaves)[-1][0]
