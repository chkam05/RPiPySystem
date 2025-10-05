#!/usr/bin/env bash
clear

# e: terminate the script if any step returns an error.
# u: treat the use of an undefined variable as an error.
# o pipefail: if a command in the pipeline fails, the entire pipeline returns an error.
set -euo pipefail

# Environment configuration
# Go to the project directory
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# Clear supervisor and service logs
./scripts/clear_logs.sh

# Python virtual environment
if [ ! -d .venv ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

# Loading environment variables
if [ -f .env ]; then
    set -a          # Automatically exports all variables.
    source .env     # Loads variables into the environment.
    set +a          # Disables auto-export.
fi

# Django Migrations
pushd control_service > /dev/null   # Enters the control_service directory (where the Django project is located).
python manage.py migrate --noinput  # Starts database migration (creates/updates tables).
popd > /dev/null                    # Returns to the previous directory.

# Reverse proxy (Nginx): config + cert
./scripts/init_nginx.sh 192.168.1.101

# Disable annoying pkg_resources deprecation warning (Python 3.13+)
export PYTHONWARNINGS="ignore:pkg_resources is deprecated as an API:UserWarning"

# Launching the supervisor – the supervisor service takes care of the rest
exec supervisord -n -c supervisord.conf