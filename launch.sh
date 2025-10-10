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