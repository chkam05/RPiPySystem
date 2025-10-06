import os
import uuid
from werkzeug.security import generate_password_hash
from auth_service.models.user import User
from utils.security import load_auth_secret

BIND = os.getenv('AUTH_BIND', '127.0.0.1')
PORT = int(os.getenv('AUTH_PORT', '5002'))

# Directory for "db" files (created automatically)
DB_DIR = os.getenv("AUTH_DB_DIR", "./auth_service/db")

# Storage names - JSON file names
USERS_STORAGE_NAME = "users"
SESSIONS_STORAGE_NAME = "sessions"

def db_path(storage_name: str) -> str:
    os.makedirs(DB_DIR, exist_ok=True)
    return os.path.join(DB_DIR, f"{storage_name}.json")

# Secret for signing tokens (must exist)
SECRET = load_auth_secret()

# Token TTLs
ACCESS_TOKEN_SECONDS = int(os.getenv("ACCESS_TOKEN_SECONDS", str(15 * 60)))
REFRESH_TOKEN_SECONDS = int(os.getenv("REFRESH_TOKEN_SECONDS", str(30 * 24 * 3600)))

# Default Users
DEFAULT_ROOT_ID = str(uuid.uuid5(uuid.NAMESPACE_DNS, 'auth_service:root'))

DEFAULT_USERS = [
    {
        User.FIELD_ID: DEFAULT_ROOT_ID,
        User.FIELD_NAME: 'root',
        User.FIELD_PASSWORD_HASH: generate_password_hash('password'),
        User.FIELD_LEVEL: 'Root'
    }
]