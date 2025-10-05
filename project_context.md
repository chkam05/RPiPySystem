# Projekt aplikacji wieloserwisowej na Raspberry Pi — Pakiet kontekstu
_Ten plik gromadzi minimalny kontekst potrzebny do kontynuacji pracy nad projektem._


## Metadane projektu

- Katalog główny: `/opt/RPiPySystem`

- Python: `Python 3.13.5`


## Struktura projektu (skrócona)

```
Katalog główny: /opt/RPiPySystem
  📁 auth_service/
    📁 controllers/
      📄 health.py  (0 KB)
      📄 sessions.py  (1 KB)
      📄 users.py  (1 KB)
    📄 app.py  (1 KB)
    📄 config.py  (0 KB)
    📄 db.json  (0 KB)
    📄 swagger.py  (1 KB)
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
      📄 health.py  (0 KB)
      📄 send.py  (1 KB)
    📄 app.py  (1 KB)
    📄 config.py  (0 KB)
    📄 swagger.py  (1 KB)
  📁 info_service/
    📁 controllers/
      📄 health.py  (0 KB)
      📄 network.py  (1 KB)
      📄 weather.py  (1 KB)
    📄 app.py  (1 KB)
    📄 config.py  (0 KB)
    📄 swagger.py  (1 KB)
  📁 io_service/
    📁 controllers/
      📄 gpio.py  (1 KB)
      📄 health.py  (0 KB)
    📄 app.py  (1 KB)
    📄 config.py  (0 KB)
    📄 swagger.py  (1 KB)
  📁 nginx/
    📄 pi_stack.conf  (2 KB)
  📁 scripts/
    📄 clear_logs.sh  (0 KB)
    📄 gpt_context_generator.sh  (1 KB)
    📄 init_nginx.sh  (1 KB)
    📄 kill_supervisord.sh  (1 KB)
  📁 supervisor/
    📄 nginx_stop.py  (2 KB)
    📄 reaper.py  (3 KB)
    📄 requirements_solver.py  (9 KB)
  📁 supervisor_service/
    📄 app.py  (1 KB)
    📄 config.py  (0 KB)
    📄 process_manager.py  (1 KB)
    📄 swagger.py  (1 KB)
  📁 utils/
    📄 __init__.py  (0 KB)
    📄 gpt_context_generator.py  (16 KB)
    📄 utils.py  (1 KB)
  📄 .env.example  (0 KB)
  📄 .gitignore  (5 KB)
  📄 LICENSE  (1 KB)
  📄 main.py  (0 KB)
  📄 project_context.md  (6 KB)
  📄 README.md  (0 KB)
  📄 requirements.txt  (1 KB)
  📄 start.sh  (2 KB)
  📄 supervisord.conf  (5 KB)
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

- `supervisor_service` → `%(ENV_VIRTUAL_ENV)s/bin/python -m supervisor_service.app`
  
  logi: stdout=`/dev/null`, stderr=`./logs/supervisor_service.err`
- `auth_service` → `%(ENV_VIRTUAL_ENV)s/bin/python -m auth_service.app`
  
  logi: stdout=`/dev/null`, stderr=`./logs/auth_service.err`
- `email_service` → `%(ENV_VIRTUAL_ENV)s/bin/python -m email_service.app`
  
  logi: stdout=`/dev/null`, stderr=`./logs/email_service.err`
- `info_service` → `%(ENV_VIRTUAL_ENV)s/bin/python -m info_service.app`
  
  logi: stdout=`/dev/null`, stderr=`./logs/info_service.err`
- `io_service` → `%(ENV_VIRTUAL_ENV)s/bin/python -m io_service.app`
  
  logi: stdout=`/dev/null`, stderr=`./logs/io_service.err`
- `control_service` → `%(ENV_VIRTUAL_ENV)s/bin/gunicorn control_site.wsgi:application --chdir %(here)s/control_service --workers 2 --bind 127.0.0.1:8080`
  
  logi: stdout=`/dev/null`, stderr=`./logs/control_service.err`


**Nasłuchiwacze zdarzeń**:

- `reaper` → `/opt/RPiPySystem/.venv/bin/python /opt/RPiPySystem/supervisor/reaper.py`
  
  logi: stdout=`/dev/null`, stderr=`/dev/stderr`
  
  env: PYTHONPATH=%(here)s
- `nginx_stop` → `%(ENV_VIRTUAL_ENV)s/bin/python /opt/RPiPySystem/supervisor/nginx_stop.py`
  
  logi: stdout=`/dev/null`, stderr=`/dev/stderr`
  
  env: PYTHONPATH=%(here)s


## Reverse proxy Nginx

- Plik: `nginx/pi_stack.conf`

**Serwery**:

- listen: `80`; server_name: `192.168.1.101`

- listen: `443 ssl`; server_name: `192.168.1.101`


**Lokalizacje (mapowanie proxy)**:

- `/` → `http://127.0.0.1:8080/`

- `/control/` → `http://127.0.0.1:8080/`

- `/api/supervisor/` → `http://127.0.0.1:5001/`

- `/api/auth/` → `http://127.0.0.1:5002/`

- `/api/email/` → `http://127.0.0.1:5003/`

- `/api/info/` → `http://127.0.0.1:5004/`

- `/api/io/` → `http://127.0.0.1:5005/`



## Wykryte serwisy

- `auth_service` → flask
- `control_service` → django
- `email_service` → flask
- `info_service` → flask
- `io_service` → flask
- `supervisor_service` → flask



## Klucze konfiguracyjne (tylko nazwy)

- `auth_service/config.py`: BIND, DB_PATH, PORT, SECRET


- `email_service/config.py`: BIND, PORT, SMTP_FROM, SMTP_HOST, SMTP_PORT


- `info_service/config.py`: BIND, PORT, WEATHER_API


- `io_service/config.py`: BIND, PORT


- `supervisor_service/config.py`: BIND, PORT, SUPERVISOR_URL

