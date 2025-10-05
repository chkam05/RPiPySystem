#!/usr/bin/env bash
# Kill supervisord gracefully if possible, otherwise force kill.

set -euo pipefail

SUPERVISORCTL="/opt/RPiPySystem/.venv/bin/supervisorctl -s unix:///tmp/supervisor.sock"

if pgrep -x supervisord > /dev/null; then
    echo "[INFO] supervisord detected."
    if $SUPERVISORCTL status >/dev/null 2>&1; then
        echo "[INFO] Shutting down via supervisorctl..."
        $SUPERVISORCTL stop all || true
        $SUPERVISORCTL shutdown || true
    else
        echo "[WARN] supervisorctl not responding, forcing kill..."
        pkill -9 -x supervisord
    fi
else
    echo "[INFO] No supervisord process found."
fi