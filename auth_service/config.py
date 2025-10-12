import os
import uuid
from werkzeug.security import generate_password_hash

from .models.access_level import AccessLevel
from .models.user import User


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

# --- DEFAULT DATA ---

DEFAULT_ROOT_ID = str(uuid.uuid5(uuid.NAMESPACE_DNS, 'auth_service:root'))
DEFAULT_USERS = [
    {
        User.FIELD_ID: DEFAULT_ROOT_ID,
        User.FIELD_NAME: 'root',
        User.FIELD_PASSWORD_HASH: generate_password_hash('password'),
        User.FIELD_LEVEL: AccessLevel.ROOT.value
    }
]