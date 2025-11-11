import os


# --- SERVICE CONFIGURATION ---

API_ENDPOINT = os.getenv('SYSTEM_SERVICE_API')
HOST = os.getenv('SYSTEM_SERVICE_HOST')
PORT = int(os.getenv('SYSTEM_SERVICE_PORT'))
SERVICE_NAME = 'system_service'
SWAGGER_DESCRIPTION = 'Service providing system & network diagnostics, OS info, and weather.\n'
SWAGGER_TITLE = 'System Service API'

# --- AUTHENTICATION CONFIGURATION ---

AUTH_URL = os.getenv('GLOBAL_AUTH_URL')