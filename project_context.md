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
    📄 context_generator.sh  (2 KB)
  📁 auth_service/
    📁 controllers/
      📄 health_controller.py  (1 KB)
      📄 sessions_controller.py  (9 KB)
      📄 users_controller.py  (10 KB)
    📁 db/
      📄 sessions.json  (0 KB)
      📄 users.json  (0 KB)
    📁 models/
      📄 access_level.py  (1 KB)
      📄 access_token.py  (3 KB)
      📄 refresh_token.py  (1 KB)
      📄 refresh_token_record.py  (1 KB)
      📄 token_pair.py  (2 KB)
      📄 user.py  (3 KB)
    📁 storage/
      📄 sessions_storage.py  (3 KB)
      📄 users_storage.py  (3 KB)
    📁 utils/
      📄 auth_guard.py  (3 KB)
    📄 app.py  (0 KB)
    📄 config.py  (1 KB)
    📄 service.py  (2 KB)
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
      📄 health_controller.py  (1 KB)
      📄 processes_controller.py  (8 KB)
    📁 listeners/
      📄 event_listener.py  (0 KB)
      📄 event_logger.py  (1 KB)
      📄 event_service.py  (5 KB)
      📄 rules.py  (4 KB)
    📁 models/
      📄 event_handler.py  (1 KB)
    📁 utils/
      📄 processes_manager.py  (2 KB)
      📄 supervisor_proxy_factory.py  (1 KB)
      📄 timeout_transport.py  (0 KB)
    📄 app.py  (0 KB)
    📄 config.py  (1 KB)
    📄 service.py  (1 KB)
    📄 swagger.py  (2 KB)
  📁 supervisor_service_old/
    📁 controllers/
      📄 processes.py  (7 KB)
    📁 listeners/
    📁 models/
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
    📄 base_json_storage.py  (4 KB)
    📄 flask_api_service.py  (3 KB)
    📄 key_generator.py  (1 KB)
    📄 security.py  (1 KB)
  📄 .env.dev  (1 KB)
  📄 .gitignore  (5 KB)
  📄 launch.sh  (5 KB)
  📄 LICENSE  (1 KB)
  📄 main.py  (0 KB)
  📄 project_context.md  (35 KB)
  📄 README.md  (0 KB)
  📄 requirements.txt  (1 KB)
  📄 supervisord.conf  (6 KB)
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

- `auth_service` → unknown
- `control_service` → django
- `email_service` → flask
- `info_service` → flask
- `io_service` → flask
- `supervisor_service` → unknown



## Klucze konfiguracyjne (tylko nazwy)

- `auth_service/config.py`: ACCESS_TOKEN_SECONDS, API_ENDPOINT, DEFAULT_ROOT_ID, DEFAULT_USERS, HOST, PORT, REFRESH_TOKEN_SECONDS, SECRET, SERVICE_NAME, SESSIONS_STORAGE_PATH, SWAGGER_DESCRIPTION, SWAGGER_TITLE, USERS_STORAGE_PATH


- `email_service/config.py`: BIND, PORT, SECRET, SMTP_FROM, SMTP_HOST, SMTP_PORT


- `info_service/config.py`: BIND, PORT, SECRET


- `io_service/config.py`: BIND, PORT, SECRET


- `supervisor_service/config.py`: API_ENDPOINT, AUTH_URL, HOST, PORT, SERVICE_NAME, SOC_PASS, SOC_TIMEOUT, SOC_URL, SOC_USER, SWAGGER_DESCRIPTION, SWAGGER_TITLE



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

# Parse arguments
# ------------------------------------------------------------------------------
DEPLOYMENT="dev"

while [[ "${1-}" != "" ]]; do
    case "$1" in
        -d|--deployment)
            if [[ "${2-}" == "" ]]; then
                echo "[$APP_NAME] Missing value for --deployment (use: dev|test|prod)."
                exit 2
            fi
            DEPLOYMENT="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--deployment dev|test|prod]"
            exit 0
            ;;
        *)
            echo "[$APP_NAME] Unknown parameter: $1"
            echo "Usage: $0 [--deployment dev|test|prod]"
            exit 1
            ;;
    esac
done
# ------------------------------------------------------------------------------

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
        echo "[$APP_NAME] NOTE: $REQ_FILE file not found; Skipping dependencies installation."
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
# Map deployment to .env filename
case "$DEPLOYMENT" in
    dev)   ENV_FILE=".env.dev"  ;;
    test)  ENV_FILE=".env.test" ;;
    prod)  ENV_FILE=".env"      ;;
    *)     ENV_FILE=".env.dev"  ;;
esac

if [ -f "$ENV_FILE" ]; then
    echo "[$APP_NAME] Loading environment from $ENV_FILE ..."
    set -a              # Automatically exports all variables.
    # shellcheck disable=SC1090
    source "$ENV_FILE"  # Loads variables into the environment.
    set +a              # Disables auto-export.
else
    echo "[$APP_NAME] NOTE: Environment file $ENV_FILE not found! Skipping ..."
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
autorestart=unexpected      ; Not True
exitcodes=0                 ; Only 0 is the "expected" output
startsecs=10                ; Process must survive 10 seconds to be considered a successful start
startretries=3              ; After 3 failed attempts -> FATAL
stdout_logfile=./logs/auth_service.out
stdout_logfile_maxbytes=0
stderr_logfile=./logs/auth_service.err
stderr_logfile_maxbytes=0
environment=PYTHONUNBUFFERED="1"

;[program:email_service]
;command=%(ENV_VIRTUAL_ENV)s/bin/python -u -m email_service.app
;autostart=true
;autorestart=unexpected      ; Not True
;exitcodes=0                 ; Only 0 is the "expected" output
;startsecs=10                ; Process must survive 10 seconds to be considered a successful start
;startretries=3              ; After 3 failed attempts -> FATAL
;stdout_logfile=./logs/email_service.out
;stdout_logfile_maxbytes=0
;stderr_logfile=./logs/email_service.err
;stderr_logfile_maxbytes=0
;environment=PYTHONUNBUFFERED="1"

;[program:info_service]
;command=%(ENV_VIRTUAL_ENV)s/bin/python -u -m info_service.app
;autostart=true
;autorestart=unexpected      ; Not True
;exitcodes=0                 ; Only 0 is the "expected" output
;startsecs=10                ; Process must survive 10 seconds to be considered a successful start
;startretries=3              ; After 3 failed attempts -> FATAL
;stdout_logfile=./logs/info_service.out
;stdout_logfile_maxbytes=0
;stderr_logfile=./logs/info_service.err
;stderr_logfile_maxbytes=0
;environment=PYTHONUNBUFFERED="1"

;[program:io_service]
;command=%(ENV_VIRTUAL_ENV)s/bin/python -u -m io_service.app
;autostart=true
;autorestart=unexpected      ; Not True
;exitcodes=0                 ; Only 0 is the "expected" output
;startsecs=10                ; Process must survive 10 seconds to be considered a successful start
;startretries=3              ; After 3 failed attempts -> FATAL
;stdout_logfile=./logs/io_service.out
;stdout_logfile_maxbytes=0
;stderr_logfile=./logs/io_service.err
;stderr_logfile_maxbytes=0
;environment=PYTHONUNBUFFERED="1"

;[program:control_service]
;command=%(ENV_VIRTUAL_ENV)s/bin/gunicorn control_site.wsgi:application --chdir %(here)s/control_service --workers 2 --bind 127.0.0.1:8080
;autostart=true
;autorestart=unexpected      ; Not True
;exitcodes=0                 ; Only 0 is the "expected" output
;startsecs=10                ; Process must survive 10 seconds to be considered a successful start
;startretries=3              ; After 3 failed attempts -> FATAL
;stdout_logfile=./logs/control_service.out
;stdout_logfile_maxbytes=0
;stderr_logfile=./logs/control_service.err
;stderr_logfile_maxbytes=0
;environment=PYTHONUNBUFFERED="1",GUNICORN_CMD_ARGS="--access-logfile - --error-logfile - --capture-output --enable-stdio-inheritance"

;[group:RaspberryPiSystem]
;programs=supervisor_service,auth_service;,email_service,info_service,io_service,control_service

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

### `supervisor_service/controllers/processes_controller.py`

```text
from flask import jsonify, request
from typing import ClassVar
import requests

from auth_service.models.access_level import AccessLevel
from supervisor_service.utils.processes_manager import ProcessesManager
from utils.auto_swag import auto_swag, ok, unauthorized
from utils.base_controller import BaseController
from utils.security import SecurityUtils


class ProcessesController(BaseController):
    _CONTROLLER_NAME: ClassVar[str] = 'supervisor_processes'
    _CONTROLLER_PATH: ClassVar[str] = 'processes'

    def __init__(self, url_prefix_base: str, auth_url: str, processes_manager: ProcessesManager) -> None:
        # Fields validation:
        if not isinstance(url_prefix_base, str) or not url_prefix_base.strip():
            raise ValueError('url_prefix_base is required')
        if not isinstance(auth_url, str) or not auth_url.strip():
            raise ValueError('auth_url is required')
        if not processes_manager:
            raise ValueError('processes_manager is required')
        
        url_prefix = self.join_prefix(url_prefix_base, self._CONTROLLER_PATH)

        self._auth_url = auth_url
        self._processes_manager = processes_manager
        super().__init__(self._CONTROLLER_NAME, __name__, url_prefix)
    
    def register_routes(self) -> 'ProcessesController':
        self.add_url_rule('/list', view_func=self.list_processes, methods=['GET'])
        # self.add_url_rule('/<name>/start', view_func=self.start_process, methods=['POST'])
        # self.add_url_rule('/<name>/stop', view_func=self.stop_process, methods=['POST'])
        # self.add_url_rule('/<name>/restart', view_func=self.restart_process, methods=['POST'])
        # self.add_url_rule('/stop_all', view_func=self.stop_all, methods=['POST'])
        return self
    
    # --- Authentication helper methods ---

    def _require_root(self):
        headers = SecurityUtils.bearer_headers_from_request()
        
        if not headers:
            return False, {'message': 'missing bearer token'}, 401

        try:
            r = self.http.post(self._auth_url, headers=headers, timeout=3.0)
        except requests.RequestException:
            return False, {'message': 'auth service unreachable'}, 503

        if r.status_code != 200:
            return False, {'message': 'invalid or expired token'}, 401

        try:
            payload = r.json()
            level = (payload.get('user') or {}).get('level')
        except Exception:
            return False, {'message': 'auth response malformed'}, 503

        if level != AccessLevel.ROOT.value:
            return False, {'message': 'forbidden: requires Root'}, 403

        return True, None, 200
    
    # --- Utilities ---

    def _exec(self, fn, *args, **kwargs):
        try:
            return jsonify(fn(*args, **kwargs)), 200
        except RuntimeError as e:
            return jsonify({'message': str(e)}), 503

    # --- ENDPOINTS ---

    @auto_swag(
        tags=['processes'],
        summary='List Supervisord Processes — Root Only',
        description='Returns the status and basic metadata for all Supervisord-managed services in the microservice suite (Root required).',
        responses={
            200: ok(
                {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string'},
                            'state': {'type': 'string'},
                            'pid': {'type': 'integer', 'nullable': True},
                        }
                    }
                }
            ),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def list_processes(self):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code
        return self._exec(self.pm.list_processes)
    
    @auto_swag(
        tags=['processes'],
        summary='Start Supervisord Process — Root Only',
        description='Starts the specified Supervisord-managed service if it is not already running (Root required).',
        parameters=[{
            'in': 'path',
            'name': 'name',
            'schema': {'type': 'string', 'example': 'service_name'},
            'required': True,
            'description': 'Service name'
        }],
        responses={
            200: ok(
                {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'started': {'type': 'boolean'},
                        'message': {'type': 'string'},
                    },
                }
            ),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def start_process(self, name: str):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code
        return self._exec(self.pm.start, name)

    @auto_swag(
        tags=['processes'],
        summary='Stop Supervisord Process — Root Only',
        description='Stops the specified Supervisord-managed service gracefully (Root required).',
        parameters=[{
            'in': 'path',
            'name': 'name',
            'schema': {'type': 'string', 'example': 'service_name'},
            'required': True,
            'description': 'Service name'
        }],
        responses={
            200: ok(
                {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'stopped': {'type': 'boolean'},
                        'message': {'type': 'string'},
                    },
                }
            ),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def stop_process(self, name: str):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code
        return self._exec(self.pm.stop, name)

    @auto_swag(
        tags=['processes'],
        summary='Restart Supervisord Process — Root Only',
        description='Restarts the specified Supervisord-managed service, stopping it if running and then starting it again (Root required).',
        parameters=[{
            'in': 'path',
            'name': 'name',
            'schema': {'type': 'string', 'example': 'service_name'},
            'required': True,
            'description': 'Service name'
        }],
        responses={
            200: ok(
                {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'restarted': {'type': 'boolean'},
                        'message': {'type': 'string'},
                    },
                }
            ),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def restart_process(self, name: str):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code
        return self._exec(self.pm.restart, name)

    @auto_swag(
        tags=['processes'],
        summary='Stop All Supervisord Processes — Root Only',
        description='Stops all Supervisord-managed services in the microservice suite gracefully (Root required).',
        responses={
            200: ok(
                {
                    'type': 'object',
                    'properties': {
                        'stopped': {'type': 'integer', 'description': 'How many were stopped'}
                    },
                }
            ),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def stop_all(self):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code
        return self._exec(self.pm.stop_all)
```

### `utils/base_controller.py`

```text
from abc import ABC, abstractmethod
from flask import Blueprint

class BaseController(Blueprint):
    
    def __init__(self, name: str, import_name: str, url_prefix: str) -> None:
        # Prefix normalization
        if not url_prefix.startswith('/'):
            url_prefix = '/' + url_prefix

        super().__init__(name, import_name, url_prefix=url_prefix)
        # Auto-register routes defined by subclasses
        # Subclass should override register_routes() and call add_url_rule(...)
        self.register_routes()
    
    @staticmethod
    def join_prefix(base: str, *parts: str) -> str:
        base = '/' + base.strip('/')
        rest = '/'.join(p.strip('/') for p in parts if p is not None)
        return base if not rest else f'{base}/{rest}'

    @abstractmethod
    def register_routes(self) -> 'BaseController':
        # Subclasses must override and return self
        raise NotImplementedError(f'{self.__class__.__name__}.register_routes() must be overridden')

```
