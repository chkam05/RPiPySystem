import os
import uuid
from werkzeug.security import generate_password_hash
from auth_service.models.user import User
from utils.security import load_auth_secret


# --- Database files ---
DB_DIR = './auth_service/db'
SESSIONS_STORAGE_NAME = 'sessions'
USERS_STORAGE_NAME = 'users'


# --- Configuration ---
HOST = os.getenv('AUTH_SERVICE_HOST')
PORT = int(os.getenv('AUTH_SERVICE_PORT'))
ACCESS_TOKEN_SECONDS = int(os.getenv('AUTH_SERVICE_ACCESS_TOKEN_SECONDS'))
REFRESH_TOKEN_SECONDS = int(os.getenv('AUTH_SERVICE_REFRESH_TOKEN_SECONDS'))
SECRET = os.getenv('AUTH_SERVICE_SECRET')


# --- Default Users ---
DEFAULT_ROOT_ID = str(uuid.uuid5(uuid.NAMESPACE_DNS, 'auth_service:root'))
DEFAULT_USERS = [
    {
        User.FIELD_ID: DEFAULT_ROOT_ID,
        User.FIELD_NAME: 'root',
        User.FIELD_PASSWORD_HASH: generate_password_hash('password'),
        User.FIELD_LEVEL: 'Root'
    }
]


# def db_path(storage_name: str) -> str:
#     os.makedirs(DB_DIR, exist_ok=True)
#     return os.path.join(DB_DIR, f"{storage_name}.json")