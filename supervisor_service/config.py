import os

SUPERVISOR_URL = os.getenv('SUPERVISOR_URL', 'http://127.0.0.1:9001/RPC2')
BIND = os.getenv('SUPERVISOR_SERVICE_BIND', '0.0.0.0')
PORT = int(os.getenv('SUPERVISOR_SERVICE_PORT', '5001'))
