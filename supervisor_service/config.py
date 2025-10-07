import os

BIND = os.getenv('SUPERVISOR_SERVICE_BIND', '0.0.0.0')
PORT = int(os.getenv('SUPERVISOR_SERVICE_PORT', '5001'))

AUTH_BASE_URL = os.getenv("AUTH_BASE_URL", "http://127.0.0.1:5002")
AUTH_VALIDATION_ENDPOINT = '/api/auth/session/validate'
SUPERVISOR_URL = os.getenv('SUPERVISOR_URL', 'http://127.0.0.1:9001/RPC2')