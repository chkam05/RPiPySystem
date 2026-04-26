import os
from utils.security import load_auth_secret

BIND = os.getenv('EMAIL_BIND', '127.0.0.1')
PORT = int(os.getenv('EMAIL_PORT', '5003'))

# Secret for signing tokens (must exist)
SECRET = load_auth_secret()

# Email configuration
SMTP_HOST = os.getenv('SMTP_HOST', 'localhost')
SMTP_PORT = int(os.getenv('SMTP_PORT', '25'))
SMTP_FROM = os.getenv('SMTP_FROM', 'pi@example.local')
