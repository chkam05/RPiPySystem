import os


# --- SERVICE CONFIGURATION ---

API_ENDPOINT = os.getenv('AUTH_SERVICE_API')
HOST = os.getenv('AUTH_SERVICE_HOST')
PORT = int(os.getenv('AUTH_SERVICE_PORT'))
SERVICE_NAME = 'auth_service'
SWAGGER_DESCRIPTION = 'Authentication and user management service.\n'
SWAGGER_TITLE = 'Auth Service API'

# --- AUTHENTICATION CONFIGURATION ---

ACCESS_TOKEN_SECONDS = int(os.getenv('AUTH_SERVICE_ACCESS_TOKEN_SECONDS'))
REFRESH_TOKEN_SECONDS = int(os.getenv('AUTH_SERVICE_REFRESH_TOKEN_SECONDS'))
SECRET = os.getenv('AUTH_SERVICE_SECRET')

# --- STORAGE CONFIGURATION ---

SESSIONS_STORAGE_PATH = './auth_service/db/sessions.json'
USERS_STORAGE_PATH = './auth_service/db/users.json'
