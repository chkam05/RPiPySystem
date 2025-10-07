import os
from utils.security import load_auth_secret

BIND = os.getenv('INFO_BIND', '127.0.0.1')
PORT = int(os.getenv('INFO_PORT', '5004'))

# Secret for signing tokens (must exist)
SECRET = load_auth_secret()
