#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# Stop Nginx service (with fallback methods)
# ------------------------------------------------------------------------------

set -euo pipefail

# Resolve project root and work from there.
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd -P)"
APP_NAME="$(basename -- "${PROJECT_ROOT%/}")"

CLEAR_SCRIPT="$PROJECT_ROOT/scripts/clear.sh"
NGINX_INIT_SCRIPT="$PROJECT_ROOT/scripts/nginx_init.sh"

cd "$PROJECT_ROOT"

echo "[$APP_NAME] Attempting to stop Nginx..."

# systemctl (prefered)
# ------------------------------------------------------------------------------
if command -v systemctl >/dev/null 2>&1; then
    if systemctl list-units --type=service | grep -q nginx; then
        echo "[$APP_NAME] Shutting down nginx via systemctl ..."
        systemctl stop nginx && exit 0
    fi
fi
# ------------------------------------------------------------------------------

# service (SysV-init)
# ------------------------------------------------------------------------------
if command -v service >/dev/null 2>&1; then
    echo "[$APP_NAME] Shutting down nginx via service command ..."
    service nginx stop && exit 0
fi
# ------------------------------------------------------------------------------

# Direct init scripts (fallback)
# ------------------------------------------------------------------------------
if [ -x /usr/sbin/service ]; then
    echo "[$APP_NAME] Shutting down nginx via /usr/sbin/service ..."
    /usr/sbin/service nginx stop && exit 0
fi

if [ -x /sbin/service ]; then
    echo "[$APP_NAME] Shutting down nginx via /sbin/service ..."
    /sbin/service nginx stop && exit 0
fi
# ------------------------------------------------------------------------------

echo "[$APP_NAME] ERROR: Failed to shutdown Nginx service." >&2
exit 1