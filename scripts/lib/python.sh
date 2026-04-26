# scripts/lib/python.sh
# Python helpers (POSIX). Safe to source multiple times.
# shellcheck shell=sh

# --- Guard against double sourcing. ---
if [ "x${_PYTHON_SH_LOADED:-}" != "x1" ]; then
    _PYTHON_SH_LOADED=1

    # --- Activates python virtual environment. ---
    activate_venv() {
        venv_dir="$1"

        if [ ! -f "$venv_dir/bin/activate" ]; then
            raise_err "Missing venv activate script at \"$venv_dir/bin/activate\"." 1
        fi

        # shellcheck disable=SC1090
        . "$venv_dir/bin/activate"

        # Return venv python path via stdout.
        printf '%s\n' "$venv_dir/bin/python"
    }

    # --- Creates a python virtual environment. ---
    create_venv() {
        py_exec="$1"
        venv_dir="$2"

        print_info "Creating Python virtual environment at $venv_dir ..."

        # Try stdlib venv first.
        if "$py_exec" -m venv "$venv_dir" >/dev/null 2>&1; then
            return 0
        fi

        # Fallback to virtualenv tool if available.
        if command -v virtualenv >/dev/null 2>&1; then
            if virtualenv -p "$py_exec" "$venv_dir" >/dev/null 2>&1; then
                return 0
            fi
        fi

        raise_err "Failed to create python virtual environment (.venv). Ensure Python's venv module or virtualenv is available."
    }

    # --- Detects a usable python version and return its executable (prefer python3). ---
    detect_python() {
        if command -v python3 >/dev/null 2>&1; then
            # Return python path via stdout.
            printf '%s\n' "python3"
            return 0
        fi

        if command -v python >/dev/null 2>&1; then
            # Return python path via stdout.
            printf '%s\n' "python"
            return 0
        fi

        return 1
    }

    # --- Upgrades pip toolchain (ignore ensurepip failure gracefully). ---
    upgrade_pip_toolchain() {
        py_exec="$1"

        print_info "Updating pip and installing its dependent packages ..."

        # ensurepip may be unavailable inside some distros; ignore failure
        "$py_exec" -m ensurepip --upgrade >/dev/null 2>&1 || true
        "$py_exec" -m pip install --upgrade pip setuptools wheel
    }

    # --- Install python requirements (libraries) from file (if present). ---
    install_requirements() {
        py_exec="$1"
        req_file="$2"

        if [ -f "$req_file" ]; then
            print_info "Installing dependencies from \"$req_file\" ..."
            "$py_exec" -m pip install -r "$req_file"
        else
            print_warn "$req_file file not found; Skipping dependencies installation."
        fi
    }
fi