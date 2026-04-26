from werkzeug.security import generate_password_hash
import os
import uuid


# SERVICE CONFIGURATION

HOST = os.getenv('API_SERVICE_HOST')
PORT = int(os.getenv('API_SERVICE_PORT'))
ROUTE = os.getenv('API_SERVICE_ROUTE')
SERVICE_NAME = 'api_service'
SWAGGER_DESCRIPTION = 'RaspberryPi Service API.\n'
SWAGGER_TITLE = 'RaspberryPi Service API'

# AUTHENTICATION CONFIGURATION

ACCESS_TOKEN_SECONDS = int(os.getenv('API_SERVICE_ACCESS_TOKEN_SECONDS'))
REFRESH_TOKEN_SECONDS = int(os.getenv('API_SERVICE_REFRESH_TOKEN_SECONDS'))
SECRET = os.getenv('API_SERVICE_SECRET')

# STORAGE CONFIGURATION

SESSION_STORAGE_PATH = os.getenv('SESSION_STORAGE')
USER_STORAGE_PATH = os.getenv('USER_STORAGE')

# DEFAULT DATA

DEFAULT_ROOT_ID = str(uuid.uuid5(uuid.NAMESPACE_DNS, 'api_service:root'))
DEFAULT_USERS = [
#    {
#        User.FIELD_ID: DEFAULT_ROOT_ID,
#        User.FIELD_NAME: 'root',
#        User.FIELD_PASSWORD_HASH: generate_password_hash('password'),
#        User.FIELD_LEVEL: AccessLevel.ROOT.value
#    }
]