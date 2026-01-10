
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-dev-key')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    PORT = int(os.getenv('PORT', 5000))

    # Blockchain / Governance
    RPC_URL = os.getenv('RPC_URL', 'http://127.0.0.1:8545')
    DAO_CONTRACT_ADDRESS = os.getenv('DAO_CONTRACT_ADDRESS')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
