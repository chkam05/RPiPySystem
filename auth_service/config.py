import os
import uuid
from werkzeug.security import generate_password_hash
from auth_service.models.user import User

BIND = os.getenv('AUTH_BIND', '127.0.0.1')
PORT = int(os.getenv('AUTH_PORT', '5002'))
SECRET = os.getenv('AUTH_SECRET', 'dev-secret')
DB_PATH = os.getenv('AUTH_DB', './auth_service/db.json')

DEFAULT_ROOT_ID = str(uuid.uuid5(uuid.NAMESPACE_DNS, 'auth_service:root'))

DEFAULT_USERS = [
    {
        User.FIELD_ID: DEFAULT_ROOT_ID,
        User.FIELD_NAME: 'root',
        User.FIELD_PASSWORD_HASH: generate_password_hash('password'),
    }
]