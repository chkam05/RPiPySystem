#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# RPiSystem multiservice application one-time setup:
#
# - create .venv, bootstrap pip,
# - install requirements.
#
# FIRST RUN ONLY !
# ------------------------------------------------------------------------------

set -Eeuo pipefail
clear

# Resolve project root and work from there.
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
APP_NAME="$(basename -- "${PROJECT_ROOT%/}")"

cd "$PROJECT_ROOT"

# Create & activate Python Virtual Environment
# ------------------------------------------------------------------------------
VENV_DIR="$PROJECT_ROOT/.venv"

echo "[$APP_NAME] Checking Python virtual environment (.venv) ..."

if [ ! -d "$VENV_DIR" ]; then
  echo "[$APP_NAME] Creating python virtual environment at $VENV_DIR ..."
  python -m venv "$VENV_DIR"
fi
# ------------------------------------------------------------------------------

# Activate Python Virtual Environment and finish one-time setup
# ------------------------------------------------------------------------------
# shellcheck disable=SC1091
. "$VENV_DIR/bin/activate"
# ------------------------------------------------------------------------------

# Upgrade pip and install pip-dependent packages
# ------------------------------------------------------------------------------
echo "[$APP_NAME] Updating pip and installing its dependent packages ..."
python -m ensurepip --upgrade >/dev/null 2>&1 || true
python -m pip install --upgrade pip setuptools wheel
# ------------------------------------------------------------------------------

# Install python requirements from file.
# ------------------------------------------------------------------------------
REQ_FILE="$PROJECT_ROOT/requirements.txt"

if [ -f "$REQ_FILE" ]; then
    echo "[$APP_NAME] Installing dependencies from $REQ_FILE ..."
    python -m pip install -r "$REQ_FILE"
else
    echo "[start] NOTE: $REQ_FILE file not found; Skipping dependencies installation."
fi
# ------------------------------------------------------------------------------

# Finish
echo "[$APP_NAME] Install complete."
echo "[$APP_NAME] Activate python virtual environment with: source ./.venv/bin/activate"