#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# Emergency stop:
# Try shutdown supervisord gracefully (supervisorctl) if possible,
# Then force kill it.
# ------------------------------------------------------------------------------

set -euo pipefail

# Work from project root (parent of ./scripts)
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
APP_NAME="$(basename -- "${PROJECT_ROOT%/}")"

# Prefer project venv supervisorctl, fallback to system one.
# ------------------------------------------------------------------------------
SUPERVISOR_SOCK_URI="${SUPERVISOR_SOCK_URI:-unix:///tmp/supervisor.sock}"

if [ -x "$PROJECT_ROOT/.venv/bin/supervisorctl" ]; then
    CTL="$PROJECT_ROOT/.venv/bin/supervisorctl -s $SUPERVISOR_SOCK_URI"
else
    CTL="supervisorctl -s $SUPERVISOR_SOCK_URI"
fi
# ------------------------------------------------------------------------------

# Supervisord shutdown process
# ------------------------------------------------------------------------------
if pgrep -x supervisord > /dev/null; then
    echo "[$APP_NAME] Supervisord detected."

    if $SUPERVISORCTL status >/dev/null 2>&1; then
        # Shutting down supervisord process gracefully ...
        echo "[$APP_NAME] Attempting to shutdown supervisorctl ..."
        $SUPERVISORCTL stop all || true
        $SUPERVISORCTL shutdown || true
    else
        # Killing supervisord process ...
        echo "[$APP_NAME] WARN: supervisorctl is not responding, forcing kill ..."
        pkill -9 -x supervisord
    fi

    # Final check if supervisord service is still running.
    if pgrep -x supervisord > /dev/null; then
        echo "[$APP_NAME] Supervisorctl has been shut down."
    fi
else
    echo "[$APP_NAME] No supervisord process found."
fi
# ------------------------------------------------------------------------------