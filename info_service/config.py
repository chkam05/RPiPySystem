import os


# --- SERVICE CONFIGURATION ---

API_ENDPOINT = os.getenv('INFO_SERVICE_API')
HOST = os.getenv('INFO_SERVICE_HOST')
PORT = int(os.getenv('INFO_SERVICE_PORT'))
SERVICE_NAME = 'info_service'
SWAGGER_DESCRIPTION = 'Service providing system & network diagnostics, OS info, and weather.\n'
SWAGGER_TITLE = 'Info Service API'

# --- AUTHENTICATION CONFIGURATION ---

AUTH_URL = os.getenv('GLOBAL_AUTH_URL')