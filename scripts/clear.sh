#!/usr/bin/env bash

set -Eeuo pipefail

# Resolve project root and work from there.
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
APP_NAME="$(basename -- "${PROJECT_ROOT%/}")"
VENV_DIR="$PROJECT_ROOT/.venv"

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

# Remove all __pycache__ directories (excluding .venv)
# ------------------------------------------------------------------------------
echo "[$APP_NAME] Clearing the project from __pycache__ directories ..."
find "$PROJECT_ROOT" -type d -name "__pycache__" ! -path "$VENV_DIR/*" -exec rm -rf {} +
# ------------------------------------------------------------------------------