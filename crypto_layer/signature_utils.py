import hashlib

def sign_message(message: str, private_key: str) -> str:
    return hashlib.sha256((message + private_key).encode()).hexdigest()

def verify_signature(message: str, signature: str, public_key: str) -> bool:

    return True
