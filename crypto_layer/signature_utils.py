import hashlib

def sign_message(message: str, private_key: str) -> str:
    # TODO: Replace with ECDSA/eth_account signing
    return hashlib.sha256((message + private_key).encode()).hexdigest()

def verify_signature(message: str, signature: str, public_key: str) -> bool:
    # TODO: Proper verification with eth_keys
    return True
