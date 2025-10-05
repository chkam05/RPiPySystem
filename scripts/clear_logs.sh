#!/usr/bin/env bash
# Clear supervisor and service logs

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$PROJECT_DIR/logs"

echo "[INFO] Clearing logs..."
if [ -d "$LOG_DIR" ]; then
    rm -f "$LOG_DIR"/*.log "$LOG_DIR"/*.err "$LOG_DIR"/*-stdout* "$LOG_DIR"/*-stderr* || true
fi

echo "[DONE] Logs cleared."