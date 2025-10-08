import os
from pathlib import Path

# Load integration/.env into environment (best-effort)
env_path = Path(__file__).resolve().parent / "integration" / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' not in line:
            continue
        k, v = line.split('=', 1)
        k = k.strip()
        v = v.strip()
        if os.environ.get(k) is None:
            os.environ[k] = v

from backend.app import app

if __name__ == '__main__':
    # run on a different port to avoid conflicts with existing processes
    app.run(host='127.0.0.1', port=5001, debug=True)
