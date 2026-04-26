import os
from utils.security import load_auth_secret

BIND = os.getenv('IO_BIND', '127.0.0.1')
PORT = int(os.getenv('IO_PORT', '5005'))

# Secret for signing tokens (must exist)
SECRET = load_auth_secret()
