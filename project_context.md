# Projekt aplikacji wieloserwisowej na Raspberry Pi — Pakiet kontekstu
_Ten plik gromadzi minimalny kontekst potrzebny do kontynuacji pracy nad projektem._


## Metadane projektu

- Katalog główny: `/opt/RPiPySystem`

- Python: `Python 3.13.5`


## Struktura projektu (skrócona)

```
Katalog główny: /opt/RPiPySystem
  📁 .gpt/
    📄 context_generator.py  (16 KB)
    📄 context_generator.sh  (3 KB)
  📁 auth_service/
    📁 controllers/
      📄 health.py  (1 KB)
      📄 sessions.py  (11 KB)
      📄 users.py  (9 KB)
    📁 db/
      📄 sessions.json  (3 KB)
      📄 users.json  (0 KB)
    📁 models/
      📄 access_token_payload.py  (2 KB)
      📄 refresh_token_payload.py  (1 KB)
      📄 refresh_token_record.py  (1 KB)
      📄 user.py  (3 KB)
    📁 storage/
      📄 sessions_storage.py  (4 KB)
      📄 users_storage.py  (4 KB)
    📁 utils/
      📄 auth_guard.py  (3 KB)
    📄 app.py  (1 KB)
    📄 config.py  (1 KB)
    📄 swagger.py  (2 KB)
  📁 control_service/
    📁 control_site/
      📄 __init__.py  (0 KB)
      📄 settings.py  (1 KB)
      📄 urls.py  (0 KB)
      📄 wsgi.py  (0 KB)
    📁 dashboard/
      📁 templates/
      📁 views/
      📄 __init__.py  (0 KB)
      📄 urls.py  (0 KB)
    📄 db.sqlite3  (24 KB)
    📄 manage.py  (0 KB)
  📁 email_service/
    📁 controllers/
      📄 health.py  (1 KB)
    📄 app.py  (1 KB)
    📄 config.py  (0 KB)
    📄 swagger.py  (2 KB)
  📁 info_service/
    📁 controllers/
      📄 health.py  (1 KB)
      📄 network.py  (1 KB)
      📄 weather.py  (1 KB)
    📄 app.py  (1 KB)
    📄 config.py  (0 KB)
    📄 swagger.py  (2 KB)
  📁 io_service/
    📁 controllers/
      📄 gpio.py  (1 KB)
      📄 health.py  (1 KB)
    📄 app.py  (1 KB)
    📄 config.py  (0 KB)
    📄 swagger.py  (2 KB)
  📁 nginx/
    📄 pi_stack.conf  (2 KB)
  📁 scripts/
    📄 init_nginx.sh  (2 KB)
    📄 install.sh  (2 KB)
    📄 kill_supervisord.sh  (2 KB)
  📁 secrets/
    📄 auth_secret.key  (0 KB)
  📁 supervisor_service/
    📁 controllers/
      📄 processes.py  (7 KB)
    📁 listeners/
      📄 event_listener.py  (0 KB)
      📄 event_logger.py  (1 KB)
      📄 event_service.py  (5 KB)
      📄 rules.py  (4 KB)
    📁 models/
      📄 event_handler.py  (1 KB)
    📁 utils/
      📄 process_manager.py  (2 KB)
      📄 supervisor_proxy_factory.py  (2 KB)
      📄 timeout_transport.py  (0 KB)
    📄 app.py  (1 KB)
    📄 config.py  (0 KB)
    📄 swagger.py  (2 KB)
  📁 utils/
    📄 __init__.py  (0 KB)
    📄 auto_swag.py  (7 KB)
    📄 base_controller.py  (1 KB)
    📄 security.py  (2 KB)
  📄 .env.example  (0 KB)
  📄 .gitignore  (5 KB)
  📄 launch.sh  (4 KB)
  📄 LICENSE  (1 KB)
  📄 main.py  (0 KB)
  📄 project_context.md  (30 KB)
  📄 README.md  (0 KB)
  📄 requirements.txt  (1 KB)
  📄 supervisord.conf  (5 KB)
  📄 TODO.txt  (0 KB)
```

## Wymagania Pythona

`requirements.txt` (wybrane linie):

```text
# Developer tools:
debugpy==1.8.17         # Python debugger (e.g. VS Code, remote debugging)
setuptools<81           # Pin older Setuptools to avoid deprecation warning for pkg_resources (required by Supervisor)

# Flask microservice:
Flask==3.0.3            # Lightweight web framework
Werkzeug==3.0.3         # HTTP engine and routing, the basis of Flask
flasgger==0.9.7.1       # Automatic Swagger/OpenAPI documentation
requests==2.32.3        # HTTP client for communicating with other services
python-dotenv==1.0.1    # Loading configuration from .env file

# Process management
supervisor==4.2.5       # Process manager, service startup and monitoring

# IoT microservice (Raspberry Pi)
RPi.GPIO==0.7.1         # Low-level GPIO pin support on Raspberry Pi
gpiozero==2.0           # Higher level API for hardware support (e.g. LED, buttons)

# Django microservice
Django==5.0.7           # Full web framework (ORM, admin panel, routing, migrations)
whitenoise==6.7.0       # Serving static files in Django without an additional server

# HTTP application server (for Django behind Nginx)
gunicorn==22.0.0        # WSGI server to run Django in production
```

Zainstalowane wersje (wykryte przez `pip freeze`):

```text
Django==5.0.7
Flask==3.0.3
RPi.GPIO==0.7.1
Werkzeug==3.0.3
debugpy==1.8.17
flasgger==0.9.7.1
gpiozero==2.0
gunicorn==22.0.0
python-dotenv==1.0.1
requests==2.32.3
supervisor==4.2.5
whitenoise==6.7.0
```

## Podsumowanie Supervisor

- Plik: `supervisord.conf`


**Programy**:

- `supervisor_service` → `%(ENV_VIRTUAL_ENV)s/bin/python -u -m supervisor_service.app`
  
  logi: stdout=`./logs/supervisor_service.out`, stderr=`./logs/supervisor_service.err`
  
  env: PYTHONUNBUFFERED="1"
- `auth_service` → `%(ENV_VIRTUAL_ENV)s/bin/python -u -m auth_service.app`
  
  logi: stdout=`./logs/auth_service.out`, stderr=`./logs/auth_service.err`
  
  env: PYTHONUNBUFFERED="1"
- `email_service` → `%(ENV_VIRTUAL_ENV)s/bin/python -u -m email_service.app`
  
  logi: stdout=`./logs/email_service.out`, stderr=`./logs/email_service.err`
  
  env: PYTHONUNBUFFERED="1"
- `info_service` → `%(ENV_VIRTUAL_ENV)s/bin/python -u -m info_service.app`
  
  logi: stdout=`./logs/info_service.out`, stderr=`./logs/info_service.err`
  
  env: PYTHONUNBUFFERED="1"
- `io_service` → `%(ENV_VIRTUAL_ENV)s/bin/python -u -m io_service.app`
  
  logi: stdout=`./logs/io_service.out`, stderr=`./logs/io_service.err`
  
  env: PYTHONUNBUFFERED="1"
- `control_service` → `%(ENV_VIRTUAL_ENV)s/bin/gunicorn control_site.wsgi:application --chdir %(here)s/control_service --workers 2 --bind 127.0.0.1:8080`
  
  logi: stdout=`./logs/control_service.out`, stderr=`./logs/control_service.err`
  
  env: PYTHONUNBUFFERED="1", GUNICORN_CMD_ARGS="--access-logfile - --error-logfile - --capture-output --enable-stdio-inheritance"


**Nasłuchiwacze zdarzeń**:

- `event_listener` → `%(ENV_VIRTUAL_ENV)s/bin/python ./supervisor_service/listeners/event_listener.py`
  
  logi: stdout=`/dev/null`, stderr=`/dev/stderr`
  
  env: PYTHONPATH=%(here)s, PYTHONUNBUFFERED="1"


## Reverse proxy Nginx

- Plik: `nginx/pi_stack.conf`

**Serwery**:

- listen: `80`; server_name: `192.168.1.101`

- listen: `443 ssl`; server_name: `192.168.1.101`


**Lokalizacje (mapowanie proxy)**:

- `/` → `http://127.0.0.1:8080/`

- `/control/` → `http://127.0.0.1:8080/`

- `/api/supervisor/` → `http://127.0.0.1:5001`

- `/api/auth/` → `http://127.0.0.1:5002`

- `/api/email/` → `http://127.0.0.1:5003`

- `/api/info/` → `http://127.0.0.1:5004`

- `/api/io/` → `http://127.0.0.1:5005`



## Wykryte serwisy

- `auth_service` → flask
- `control_service` → django
- `email_service` → flask
- `info_service` → flask
- `io_service` → flask
- `supervisor_service` → flask



## Klucze konfiguracyjne (tylko nazwy)

- `auth_service/config.py`: ACCESS_TOKEN_SECONDS, BIND, DB_DIR, DEFAULT_ROOT_ID, DEFAULT_USERS, PORT, REFRESH_TOKEN_SECONDS, SECRET, SESSIONS_STORAGE_NAME, USERS_STORAGE_NAME


- `email_service/config.py`: BIND, PORT, SECRET, SMTP_FROM, SMTP_HOST, SMTP_PORT


- `info_service/config.py`: BIND, PORT, SECRET


- `io_service/config.py`: BIND, PORT, SECRET


- `supervisor_service/config.py`: AUTH_BASE_URL, AUTH_VALIDATION_ENDPOINT, BIND, PORT, SUPERVISOR_PASS, SUPERVISOR_TIMEOUT, SUPERVISOR_URL, SUPERVISOR_USER



## Fragmenty plików

### `launch.sh`

```text
#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# RPiSystem multiservice application startup script.
# ------------------------------------------------------------------------------

set -Eeuo pipefail
clear

# Resolve project root and work from there.
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd -P)"
APP_NAME="$(basename -- "${PROJECT_ROOT%/}")"

cd "$PROJECT_ROOT"

# Clear supervisor and service logs
# ------------------------------------------------------------------------------
echo "[$APP_NAME] Clearing supervisor and services logs ..."
LOG_DIR="${PROJECT_ROOT}/logs"

if [ ! -d "$LOG_DIR" ]; then
    mkdir -- "$LOG_DIR"
fi

rm -rf -- "$LOG_DIR"/*
# ------------------------------------------------------------------------------

# Create & activate Python Virtual Environment
# ------------------------------------------------------------------------------
VENV_DIR="$PROJECT_ROOT/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "[$APP_NAME] Python virtual environment not found."
    echo "[$APP_NAME] Creating python virtual environment at $VENV_DIR ..."

    python -m venv "$VENV_DIR"

    # Activate Python Virtual Environment and finish one-time setup
    # shellcheck disable=SC1091
    echo "[$APP_NAME] Activating python virtual environment ..."
    . "$VENV_DIR/bin/activate"

    # Upgrade pip and install pip-dependent packages
    echo "[$APP_NAME] Updating pip and installing its dependent packages ..."
    python -m ensurepip --upgrade >/dev/null 2>&1 || true
    python -m pip install --upgrade pip setuptools wheel

    # Install python requirements from file.
    REQ_FILE="$PROJECT_ROOT/requirements.txt"

    if [ -f "$REQ_FILE" ]; then
        echo "[$APP_NAME] Installing dependencies from $REQ_FILE ..."
        python -m pip install -r "$REQ_FILE"
    else
        echo "[start] NOTE: $REQ_FILE file not found; Skipping dependencies installation."
    fi
else
    # Activate Python Virtual Environment
    # shellcheck disable=SC1091
    echo "[$APP_NAME] Activating python virtual environment ..."
    . "$VENV_DIR/bin/activate"
fi
# ------------------------------------------------------------------------------

# Remove all __pycache__ directories (excluding .venv)
# ------------------------------------------------------------------------------
echo "[$APP_NAME] Clearing the project from __pycache__ directories ..."
find "$PROJECT_ROOT" -type d -name "__pycache__" ! -path "$VENV_DIR/*" -exec rm -rf {} +
# ------------------------------------------------------------------------------

# Loading environment variables
# ------------------------------------------------------------------------------
if [ -f .env ]; then
    set -a          # Automatically exports all variables.
    source .env     # Loads variables into the environment.
    set +a          # Disables auto-export.
fi
# ------------------------------------------------------------------------------

# Optional: Run Django migrations if a Django app is present.
# ------------------------------------------------------------------------------
if [ -d control_service ] && [ -f control_service/manage.py ]; then
    echo "[$APP_NAME] Running Django migrations ..."
    pushd control_service > /dev/null       # Enters the control_service directory (where the Django project is located).
    python manage.py migrate --noinput      # Starts database migration (creates/updates tables).
    popd > /dev/null                        # Returns to the previous directory.
fi
# ------------------------------------------------------------------------------

# Initialize Nginx configuration from script.
# ------------------------------------------------------------------------------
NGINX_IP="${NGINX_IP:-192.168.1.101}"

if [ -f "$PROJECT_ROOT/scripts/init_nginx.sh" ]; then
    echo "[$APP_NAME] Initializing nginx (IP: $NGINX_IP) ..."
    bash "$PROJECT_ROOT/scripts/init_nginx.sh" "$NGINX_IP"
fi
# ------------------------------------------------------------------------------

# Disable annoying pkg_resources deprecation warning (Python 3.13+)
export PYTHONWARNINGS="ignore:pkg_resources is deprecated as an API:UserWarning"

# Launching the supervisor – the supervisor service takes care of the rest
echo
echo "[$APP_NAME] Starting application ..."
exec supervisord -n -c supervisord.conf
```

### `supervisord.conf`

```text
; Establishes a Unix socket for communication between supervisord and the supervisorctl tool (CLI client).
; This allows you to control services (supervisorctl status, supervisorctl restart, etc.)
[unix_http_server]
file=/tmp/supervisor.sock

[supervisord]
loglevel=info                   ; debug|info|warn|error|critical
logfile=./logs/supervisord.log  ; the main Supervisor log,
logfile_maxbytes=50MB           ; Automatic rotation
;logfile_backups=5              ; How many copies to keep
pidfile=./logs/supervisord.pid  ; The PID record of the supervisord process,
childlogdir=./logs              ; The directory containing the logs of individual programs.

; Allows remote control of the Supervisor via RPC (e.g. supervisorctl).
[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

; Configure the supervisorctl client to use the same socket as supervisord.
[supervisorctl]
serverurl=unix:///tmp/supervisor.sock

; === APPLICATIONS (MODULES) ===
; [program:name]    ; Service name.
; command           ; Determines what to run (usually Python in venv).
; autostart         ; Specifies whether to start automatically when supervisord starts.
; autorestart       ; Determines whether to restart the service if it crashes.
; stopasgroup       ; This option causes all processes in the group to be stopped when the program is stopped (stop or autorestart).
; killasgroup       ; If a process (and its children) do not gracefully terminate on the TERM signal, the Supervisor will force the entire group to terminate with the KILL signal.
; priority          ; Determines the order in which services are started and stopped. By default, all are 999. Lower value, higher priority.
; Logs into files:
; stdout_logfile                ; Specifies the log files that the service prints to standard output (print, logging.info).
; stderr_logfile                ; Specifies the log files that hit standard errors (logging.error, stacktrace).
; stderr_logfile_maxbytes=10MB  ; Automatic rotation
; stderr_logfile_backups=2      ; How many copies to keep
; Output in console
; stdout_logfile=/dev/stdout
; stdout_logfile_maxbytes=0
; environment=PYTHONUNBUFFERED="1"

[program:supervisor_service]
command=%(ENV_VIRTUAL_ENV)s/bin/python -u -m supervisor_service.app
directory=%(here)s
autostart=true
autorestart=unexpected      ; Not True
exitcodes=0                 ; Only 0 is the "expected" output
startsecs=10                ; Process must survive 10 seconds to be considered a successful start
startretries=3              ; After 3 failed attempts -> FATAL
stopasgroup=true
killasgroup=true
priority=100
stdout_logfile=./logs/supervisor_service.out
stdout_logfile_maxbytes=0
stderr_logfile=./logs/supervisor_service.err
stderr_logfile_maxbytes=0
environment=PYTHONUNBUFFERED="1"

[program:auth_service]
command=%(ENV_VIRTUAL_ENV)s/bin/python -u -m auth_service.app
autostart=true
autorestart=true
stdout_logfile=./logs/auth_service.out
stdout_logfile_maxbytes=0
stderr_logfile=./logs/auth_service.err
stderr_logfile_maxbytes=0
environment=PYTHONUNBUFFERED="1"

[program:email_service]
command=%(ENV_VIRTUAL_ENV)s/bin/python -u -m email_service.app
autostart=true
autorestart=true
stdout_logfile=./logs/email_service.out
stdout_logfile_maxbytes=0
stderr_logfile=./logs/email_service.err
stderr_logfile_maxbytes=0
environment=PYTHONUNBUFFERED="1"

[program:info_service]
command=%(ENV_VIRTUAL_ENV)s/bin/python -u -m info_service.app
autostart=true
autorestart=true
stdout_logfile=./logs/info_service.out
stdout_logfile_maxbytes=0
stderr_logfile=./logs/info_service.err
stderr_logfile_maxbytes=0
environment=PYTHONUNBUFFERED="1"

[program:io_service]
command=%(ENV_VIRTUAL_ENV)s/bin/python -u -m io_service.app
autostart=true
autorestart=true
stdout_logfile=./logs/io_service.out
stdout_logfile_maxbytes=0
stderr_logfile=./logs/io_service.err
stderr_logfile_maxbytes=0
environment=PYTHONUNBUFFERED="1"

[program:control_service]
command=%(ENV_VIRTUAL_ENV)s/bin/gunicorn control_site.wsgi:application --chdir %(here)s/control_service --workers 2 --bind 127.0.0.1:8080
autostart=true
autorestart=true
stdout_logfile=./logs/control_service.out
stdout_logfile_maxbytes=0
stderr_logfile=./logs/control_service.err
stderr_logfile_maxbytes=0
environment=PYTHONUNBUFFERED="1",GUNICORN_CMD_ARGS="--access-logfile - --error-logfile - --capture-output --enable-stdio-inheritance"

[group:RaspberryPiSystem]
programs=supervisor_service,auth_service,email_service,info_service,io_service,control_service

; Event listeners (event response logic)
; The eventlistener is a process that listens for Supervisor events.

[eventlistener:event_listener]
command=%(ENV_VIRTUAL_ENV)s/bin/python ./supervisor_service/listeners/event_listener.py
events=PROCESS_STATE, SUPERVISOR_STATE_CHANGE
environment=PYTHONPATH=%(here)s,PYTHONUNBUFFERED="1"
autorestart=true
; Specifies the maximum buffer size (in bytes) in which Supervisor keeps communication data between supervisord and the listener. 
; The default is 64 KB (65536).
buffer_size=1024
stdout_logfile=/dev/null
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0   ; important: turn off rotation, otherwise "Illegal seek"
```

### `.env.example`

```text
AUTH_SECRET=0vZ_Ms5UDZKq18dyz8v4Jeuhd_A1gM9Yq8-ShmbqU0CxmriG1nTCzvXcQuB3VoRkG9j1-2LtOI8GxvSTm0I3NA
DJANGO_SECRET=0vZ_Ms5UDZKq18dyz8v4Jeuhd_A1gM9Yq8-ShmbqU0CxmriG1nTCzvXcQuB3VoRkG9j1-2LtOI8GxvSTm0I3NA
SMTP_HOST=localhost
SMTP_PORT=25
SMTP_FROM=pi@example.local
```

### `auth_service/app.py`

```text
from flask import Flask
from flasgger import Swagger
import logging

from .config import BIND, PORT, SECRET
from .controllers.health import HealthController
from .controllers.sessions import SessionsController
from .controllers.users import UsersController
from .swagger import SWAGGER_TEMPLATE, SWAGGER_CONFIG

# Initialize Flask app
app = Flask(__name__)

# Configure Logger
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] %(levelname)s: %(message)s'
)
logging.getLogger('werkzeug').setLevel(logging.INFO)

app.config['SECRET_KEY'] = SECRET

# Register blueprints
app.register_blueprint(HealthController())
app.register_blueprint(UsersController())
app.register_blueprint(SessionsController())

# Initialize Swagger using the external configuration
swagger = Swagger(app, template=SWAGGER_TEMPLATE, config=SWAGGER_CONFIG)

# Run the service
if __name__ == '__main__':
    app.run(host=BIND, port=PORT)

```

### `auth_service/config.py`

```text
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
```

### `auth_service/swagger.py`

```text
SERVICE_NAME = 'auth'
SWAGGER_TITLE = 'Auth Service API'

SWAGGER_TEMPLATE = {
    'openapi': '3.0.3',
    'info': {
        'title': SWAGGER_TITLE,
        'version': '1.0.0',
        'description': (
            'Authentication and user management service.\n'
        )
    },
    'components': {
        'securitySchemes': {
            # Bearer token definition for Authorization header
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',  # UI shows a token input field
                'description': 'Enter your access token without the \'Bearer \' prefix.'
            }
        }
    },
    # Global rule — all endpoints require BearerAuth,
    # individual endpoints (e.g., /login) can override it with `security: []`
    'security': [{'BearerAuth': []}],
}

SWAGGER_CONFIG = {
    'openapi': '3.0.3',
    'swagger_ui': True,
    'headers': [],

    # Define where the JSON spec will be served
    'specs': [
        {
            'endpoint': 'apispec',
            'route': f'/api/{SERVICE_NAME}/apispec.json',   # Full path (must include the prefix)
            'rule_filter': lambda rule: rule.rule.startswith(f'/api/{SERVICE_NAME}/'),
            'model_filter': lambda tag: True,
        }
    ],

    # Define where Swagger UI will be served
    'specs_route': f'/api/{SERVICE_NAME}/apidocs/',
    'static_url_path': f'/api/{SERVICE_NAME}/flasgger_static',

    # UI meta
    'title': SWAGGER_TITLE,
    'uiversion': 3,

    'config': {
        # Remember entered authorization across refreshes
        'persistAuthorization': True,
        # Optional: collapse models for clarity
        'docExpansion': 'none'
    },
}
```

### `auth_service/controllers/sessions.py`

```text
import time
import uuid
from typing import Any, Dict, Optional
from flask import request, jsonify
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from utils.auto_swag import auto_swag, ok, bad_request, unauthorized, request_body_json
from utils.base_controller import BaseController

from auth_service.models.user import User
from auth_service.models.access_token_payload import AccessTokenPayload
from auth_service.models.refresh_token_payload import RefreshTokenPayload
from auth_service.storage.users_storage import UsersStorage
from auth_service.storage.sessions_storage import SessionsStorage
from auth_service.utils.auth_guard import AuthGuard
from auth_service import config


class SessionsController(BaseController):
    def __init__(
            self,
            *,
            url_prefix: str = "/api/auth/session",
            users: Optional[UsersStorage] = None,
            sessions: Optional[SessionsStorage] = None) -> None:
        self.users = users or UsersStorage()
        self.sessions = sessions or SessionsStorage()
        self.auth = AuthGuard(self.users)  # <— wspólna obsługa access tokenów
        self.serializer = URLSafeTimedSerializer(config.SECRET, salt="auth-tokens")
        self.ACCESS_TTL = getattr(config, "ACCESS_TOKEN_SECONDS", 15 * 60)
        self.REFRESH_TTL = getattr(config, "REFRESH_TOKEN_SECONDS", 30 * 24 * 60 * 60)
        super().__init__("auth_sessions", __name__, url_prefix=url_prefix)

    # region --- Helper methods ---

    def _issue_tokens(self, user: User, *, prev_refresh_jti: Optional[str] = None) -> Dict[str, Any]:
        # Generates a new access and refresh token (refresh rotated and stored in SessionsStorage).
        # Returns a payload ready to be sent to the client.
        now = int(time.time())

        access_payload = AccessTokenPayload(
            typ="access",
            jti=str(uuid.uuid4()),
            sub=user.id,
            nam=user.name,
            lvl=user.level,
            iat=now,
            exp=now + self.ACCESS_TTL,
        ).to_dict()

        refresh_payload = RefreshTokenPayload(
            typ="refresh",
            jti=str(uuid.uuid4()),
            sub=user.id,
            iat=now,
            exp=now + self.REFRESH_TTL,
        ).to_dict()

        access_token = self.serializer.dumps(access_payload)
        refresh_token = self.serializer.dumps(refresh_payload)

        # Rejestr/rotacja refresh tokenów
        self.sessions.rotate_refresh(prev_refresh_jti, refresh_payload["jti"], user.id, refresh_payload["exp"])

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": self.ACCESS_TTL,
            "user": user.to_public(),
        }

    def _load_token(self, token: str, *, max_age: Optional[int] = None) -> Dict[str, Any]:
        # Reads and verifies the token signature. Throws ValueError('expired'|'invalid') on errors.
        try:
            payload = self.serializer.loads(token, max_age=max_age)
            return payload
        except SignatureExpired:
            raise ValueError("expired")
        except BadSignature:
            raise ValueError("invalid")
    
    def _read_bearer(self) -> Optional[str]:
        # Gets the token from the Authorization: Bearer <token> header.
        auth = request.headers.get("Authorization", "")
        if not auth:
            return None

        # Normalize URL-encoded variant (some proxies/clients)
        raw = auth.strip()
        raw = raw.replace("Bearer%20", "Bearer ")

        # Peel off any number of leading "Bearer " (handles 'Bearer Bearer <token>')
        while raw.lower().startswith("bearer "):
            raw = raw[7:].lstrip()

        # Drop surrounding quotes if present
        if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
            raw = raw[1:-1].strip()

        if not raw:
            return None

        return raw

    # endregion --- Helper methods ---

    @auto_swag(
        tags=["auth"],
        summary="Login — issue access & refresh tokens (Bearer)",
        security=[],    # Public
        request_body=request_body_json(
            {
                "type": "object",
                "properties": {"name": {"type": "string"}, "password": {"type": "string"}},
                "required": ["name", "password"]
            }
        ),
        responses={
            200: ok(
                {
                    "type": "object",
                    "properties": {
                        "access_token": {"type": "string"},
                        "refresh_token": {"type": "string"},
                        "token_type": {"type": "string", "example": "Bearer"},
                        "expires_in": {"type": "integer", "example": 900},
                        "user": User.schema_public()
                    }
                }
            ),
            401: unauthorized("Invalid credentials"),
            400: bad_request("Invalid payload")
        }
    )
    def login(self):
        data = request.get_json(silent=True) or {}
        name = data.get("name")
        password = data.get("password")

        if not isinstance(name, str) or not isinstance(password, str):
            return jsonify({"message": "invalid payload"}), 400

        user = self.users.verify_credentials(name, password)
        if not user:
            return jsonify({"message": "invalid credentials"}), 401

        return jsonify(self._issue_tokens(user)), 200
    
    @auto_swag(
        tags=["auth"],
        summary="Refresh — rotate refresh token and issue new access token",
        security=[],    # Public
        request_body=request_body_json(
            {
                "type": "object",
                "properties": {"refresh_token": {"type": "string"}},
                "required": ["refresh_token"]
            }
        ),
        responses={
            200: ok(
                {
                    "type": "object",
                    "properties": {
                        "access_token": {"type": "string"},
                        "refresh_token": {"type": "string"},
                        "token_type": {"type": "string"},
                        "expires_in": {"type": "integer"},
                        "user": User.schema_public(),
                    }
                }
            ),
            401: unauthorized("Invalid or expired refresh token"),
        }
    )
    def refresh(self):
        data = request.get_json(silent=True) or {}
        rtok = data.get("refresh_token")
        if not isinstance(rtok, str) or not rtok:
            return jsonify({"message": "invalid payload"}), 400

        # Decode and verify refresh payload
        try:
            raw = self._load_token(rtok, max_age=self.REFRESH_TTL)
            payload = RefreshTokenPayload.from_dict(raw)
        except ValueError:
            return jsonify({"message": "invalid or expired refresh token"}), 401

        uid, jti = payload.sub, payload.jti

        # Checking SessionsStorage (revoked/expired)
        if not self.sessions.is_valid(jti, uid):
            return jsonify({"message": "refresh token revoked or unknown"}), 401

        user = self.users.get_by_id(uid)
        if not user:
            return jsonify({"message": "user not found"}), 401

        out = self._issue_tokens(user, prev_refresh_jti=jti)
        return jsonify(out), 200
    
    @auto_swag(
        tags=["auth"],
        summary="Validate access token (Authorization: Bearer)",
        responses={
            200: ok(
                {
                    "type": "object",
                    "properties": {
                        "valid": {"type": "boolean"},
                        "user": User.schema_public(),
                        "token": {"type": "object"}
                    }
                }
            ),
            401: unauthorized("Invalid or expired token"),
        },
    )
    def validate(self):
        try:
            user, payload_model = self.auth.require_auth()
        except PermissionError as e:
            return jsonify({"message": "invalid or expired token"}), 401

        return jsonify({"valid": True, "user": user.to_public(), "token": payload_model.to_dict()}), 200
    
    @auto_swag(
        tags=["auth"],
        summary="Logout — revoke provided refresh token (body or Authorization header)",
        security=[],    # Public
        request_body=request_body_json(
            {
                "type": "object",
                "properties": {
                    "refresh_token": {"type": "string"}
                }
            },
            required=False
        ),
        responses={
            200: ok(
                {
                    "type": "object",
                    "properties": {
                        "revoked": {"type": "boolean"}
                    }
                }
            ),
            401: unauthorized("Invalid refresh token")}
    )
    def logout(self):
        # Prefer refresh_token from body and also allow Bearer (e.g. CLI clients)
        data = request.get_json(silent=True) or {}
        rtok = data.get("refresh_token") or self._read_bearer()
        if not isinstance(rtok, str) or not rtok:
            return jsonify({"message": "missing refresh token"}), 400

        try:
            raw = self._load_token(rtok, max_age=self.REFRESH_TTL)
            payload = RefreshTokenPayload.from_dict(raw)
        except ValueError:
            return jsonify({"message": "invalid or expired refresh token"}), 401

        # Idempotentnie — jeśli już nieważny, zwracamy sukces
        if not self.sessions.is_valid(payload.jti, payload.sub):
            return jsonify({"revoked": True}), 200

        self.sessions.revoke(payload.jti)
        return jsonify({"revoked": True}), 200
    
    @auto_swag(
        tags=["auth"],
        summary="Who am I — return current user from access token",
        responses={
            200: ok(User.schema_public()),
            401: unauthorized("Invalid or missing token")
        },
    )
    def me(self):
        try:
            user, _ = self.auth.require_auth()
        except PermissionError as e:
            return jsonify({"message": "invalid or expired token"}), 401

        return jsonify(user.to_public()), 200
    
    # region --- Endpoint registration ---

    def register_routes(self) -> "SessionsController":
        self.add_url_rule("/login", view_func=self.login, methods=["POST"])
        self.add_url_rule("/refresh", view_func=self.refresh, methods=["POST"])
        self.add_url_rule("/validate", view_func=self.validate, methods=["POST"])
        self.add_url_rule("/logout", view_func=self.logout, methods=["POST"])
        self.add_url_rule("/me", view_func=self.me, methods=["GET"])
        return self

    # endregion --- Endpoint registration ---

```

### `auth_service/utils/auth_guard.py`

```text
from typing import Optional, Tuple, Dict, Any
from flask import request
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from auth_service.models.user import User
from auth_service.models.access_token_payload import AccessTokenPayload
from auth_service.storage.users_storage import UsersStorage
from auth_service import config


class AuthGuard:
    def __init__(self, users: Optional[UsersStorage] = None) -> None:
        self.users = users or UsersStorage()
        self.serializer = URLSafeTimedSerializer(config.SECRET, salt="auth-tokens")
        self.ACCESS_TTL = getattr(config, "ACCESS_TOKEN_SECONDS", 15 * 60)
    
    # region --- Token helper methods ---

    @staticmethod
    def read_bearer() -> Optional[str]:
        # Gets the token from the Authorization: Bearer <token> header.
        auth = request.headers.get("Authorization", "")
        if not auth:
            return None

        # Normalize URL-encoded variant (some proxies/clients)
        raw = auth.strip()
        raw = raw.replace("Bearer%20", "Bearer ")

        # Peel off any number of leading "Bearer " (handles 'Bearer Bearer <token>')
        while raw.lower().startswith("bearer "):
            raw = raw[7:].lstrip()

        # Drop surrounding quotes if present
        if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
            raw = raw[1:-1].strip()

        return raw or None
    
    def load_access(self, token: str) -> Dict[str, Any]:
        # Decodes and validates an access token, returning a payload (dict).
        # Throws ValueError('expired'|'invalid') on error.
        try:
            return self.serializer.loads(token, max_age=self.ACCESS_TTL)
        except SignatureExpired:
            raise ValueError("expired")
        except BadSignature:
            raise ValueError("invalid")
    
    def require_auth(self) -> Tuple[User, AccessTokenPayload]:
        # Requires a valid access token.
        # Returns: (User, AccessTokenPayload)
        # Throws PermissionError if unauthorized.
        atok = self.read_bearer()
        if not atok:
            raise PermissionError("missing bearer")

        try:
            raw = self.load_access(atok)
            payload = AccessTokenPayload.from_dict(raw)
        except Exception as e:
            raise PermissionError("invalid token")

        actor = self.users.get_user_by_id(payload.sub)
        if not actor:
            raise PermissionError("user not found")

        return actor, payload

    # endregion --- Token helper methods ---

    # region --- Role Helpers ---

    @staticmethod
    def is_root(user: User) -> bool:
        return user.level == User.LEVEL_ROOT

    @staticmethod
    def is_admin(user: User) -> bool:
        return user.level == User.LEVEL_ADMIN

    @staticmethod
    def is_user(user: User) -> bool:
        return user.level == User.LEVEL_USER

    # endregion --- Role Helpers ---
    
```
