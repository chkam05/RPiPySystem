#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# RPiSystem multiservice application one-time setup script.
# ------------------------------------------------------------------------------

# Fail on unset vars and non-zero exit codes.
set -eu

# --- Resolve project directories. ---
SCRIPT_DIR=$(dirname "$0")
SCRIPT_NAME=$(basename "$0")
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd -P)
LIB_DIR="$PROJECT_ROOT/scripts/lib"
REQ_FILE="$PROJECT_ROOT/requirements.txt"
VENV_DIR="$PROJECT_ROOT/.venv"

# --- VARIABLES ---
APP_NAME=$(basename "$PROJECT_ROOT")
LOGO_FILE="$PROJECT_ROOT/scripts/logo.txt"

# Work from the project root.
cd "$PROJECT_ROOT"

# Source common libs.
. "$LIB_DIR/common.sh"
. "$LIB_DIR/python.sh"


# ------------------------------------------------------------------------------
# --- MAIN EXECUTION METHODS ---
# ------------------------------------------------------------------------------

# --- The main execution function that handles script parameters. ---
main() {
    print_logo

    # Check if python interpreter is available in system.
    PY_EXEC=$(detect_python || true)

    if [ -z "${PY_EXEC:-}" ]; then
        raise_err "No python interpreter found (python3/python)." 1
    fi

    # Ensure existence of python virtual environment.
    if [ ! -d "$VENV_DIR" ]; then
        create_venv "$PY_EXEC" "$VENV_DIR"
    else
        print_info "Python virtual environment already exists at $VENV_DIR."
    fi

    # Activate python virtual environment.
    PY_EXEC=$(activate_venv "$VENV_DIR")

    # Upgrade python packages manager and install requirements.
    upgrade_pip_toolchain "$PY_EXEC"
    install_requirements "$PY_EXEC" "$REQ_FILE"

    print_info "Installation complete."
    print_info "Activate python virtual environment with: source ./.venv/bin/activate"
}


main "$@"