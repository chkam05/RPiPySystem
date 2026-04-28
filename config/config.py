from werkzeug.security import generate_password_hash
import uuid

from core.authorization.enums.access_level import AccessLevel
from auth_service.models.user import User


DEFAULT_ROOT_ID = str(uuid.uuid5(uuid.NAMESPACE_DNS, 'auth_service:root'))
DEFAULT_USERS = [
    {
        User.FIELD_ID: DEFAULT_ROOT_ID,
        User.FIELD_NAME: 'root',
        User.FIELD_PASSWORD_HASH: generate_password_hash('password'),
        User.FIELD_LEVEL: AccessLevel.ROOT.value
    }
]