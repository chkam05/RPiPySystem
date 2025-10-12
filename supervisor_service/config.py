import os
from typing import Set


# --- SERVICE CONFIGURATION ---

API_ENDPOINT = os.getenv('SUPERVISOR_SERVICE_API')
HOST = os.getenv('SUPERVISOR_SERVICE_HOST')
PORT = int(os.getenv('SUPERVISOR_SERVICE_PORT'))
SERVICE_NAME = 'supervisor_service'
SWAGGER_DESCRIPTION = 'Application components management service.\n'
SWAGGER_TITLE = 'Supervisor Service API'

# --- AUTHENTICATION CONFIGURATION ---

AUTH_URL = os.getenv('GLOBAL_AUTH_URL')

# --- SUPERVISOR CONFIGURATION ---

EXCLUDED_FROM_STOP_ALL: Set[str] = {'event_listener'} # [eventlistener:event_listener]
SOC_TIMEOUT = float(os.getenv('SUPERVISOR_SERVICE_SOC_TIMEOUT', '3.0'))
SOC_URL = os.getenv('SUPERVISOR_SERVICE_SOC_URL')
SOC_USER = os.getenv('SUPERVISOR_SERVICE_SOC_USER', None)
SOC_PASS = os.getenv('SUPERVISOR_SERVICE_SOC_PASS', None)