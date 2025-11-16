import os


# --- SERVICE CONFIGURATION ---

API_ENDPOINT = os.getenv('BT_SERVICE_API')
HOST = os.getenv('BT_SERVICE_HOST')
PORT = int(os.getenv('BT_SERVICE_PORT'))
SERVICE_NAME = 'bluetooth_service'
SWAGGER_DESCRIPTION = 'Service for handling communication with Bluetooth devices and their management.\n'
SWAGGER_TITLE = 'Bluetooth Service API'

# --- AUTHENTICATION CONFIGURATION ---

AUTH_URL = os.getenv('GLOBAL_AUTH_URL')