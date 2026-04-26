# scripts/lib/common.sh
# Common helpers (POSIX). Safe to source multiple times.
# shellcheck shell=sh

# --- Guard against double sourcing. ---
if [ "x${_COMMON_SH_LOADED:-}" != "x1" ]; then
    _COMMON_SH_LOADED=1

    # Expect PROJECT_ROOT & APP_NAME defined by caller; derive when missing.
    if [ -z "${PROJECT_ROOT:-}" ]; then
        SCRIPT_DIR=$(dirname "$0")
        PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd -P)
    fi

    if [ -z "${APP_NAME:-}" ]; then
        APP_NAME=$(basename "$PROJECT_ROOT")
    fi

    # --------------------------------------------------------------------------
    # --- PRINT UTILITY METHODS ---
    # --------------------------------------------------------------------------

    # --- Prints an error message on the screen console. ---
    print_error() {
        printf '[%s] ERROR: %s\n' "$APP_NAME" "$*" 1>&2
    }

    # --- Prints a warning message on the screen console. ---
    print_warn() {
        printf '[%s] WARN: %s\n' "$APP_NAME" "$*"
    }

    # --- Prints a message on the screen console. ---
    print_info() {
        printf '[%s] %s\n' "$APP_NAME" "$*"
    }

    # --- Prints logo on the screen console. ---
    print_logo() {
        lf="${LOGO_FILE:-$PROJECT_ROOT/scripts/logo.txt}"

        if [ -f "$lf" ]; then
            printf '\n'
            cat "$lf"
            printf '\n\n'
        fi
    }

    # --- Prints the horizotnal screen split line on the screen console. ---
    print_line() {
        cols=""

        # Try to get terminal width, fallback to 80 if not available.
        if command -v tput >/dev/null 2>&1; then
            c=$(tput cols 2>/dev/null || printf ''); [ -n "$c" ] && cols="$c"
        fi

        if [ -z "$cols" ] && command -v stty >/dev/null 2>&1; then
            s=$(stty size 2>/dev/null || printf ''); [ -n "$s" ] && set -- $s && [ $# -ge 2 ] && cols="$2"
        fi

        # Fallback if cols is empty or invalid.
        if [ -z "$cols" ] || ! expr "$cols" : '^[0-9][0-9]*$' >/dev/null 2>&1 || [ "$cols" -le 0 ] 2>/dev/null; then
            cols=80
        fi

        # Print line of '-' characters using printf and tr for safely character repeatition.
        printf '%*s\n' "$cols" '' | tr ' ' '-'
    }

    # --------------------------------------------------------------------------
    # --- SCRIPTS UTILITY METHODS ---
    # --------------------------------------------------------------------------

    # --- Prints an error message on the screen console and exit with an error code. ---
    raise_err() {
        error_msg="$1"
        error_code="$2"

        if [ -z "$error_code" ]; then
            error_code="1"
        fi

        print_error "$error_msg"
        exit "$error_code"
    }

    # --- Checks if the script was run with root privileges (returns 0 if so, 1 otherwise). ---
    is_root() {
        if [ "$(id -u)" -eq 0 ]; then   # 0 means root
            return 0
        else
            return 1
        fi
    }

    # --- Ensure the script is run as root; otherwise raise an error. ---
    check_root() {
        if ! is_root; then
            raise_err "To perform this operation the ROOT privileges are required." 1
        fi
    }

    # --------------------------------------------------------------------------
    # --- FILE SYSTEM UTILITY METHODS ---
    # --------------------------------------------------------------------------

    # --- Makes sure the directory exists, if not creates it. ---
    ensure_directory_exists() {
        dir_path="$1"

        if [ ! -d "$dir_path" ]; then
            mkdir -p "$dir_path"
        fi
    }

    # --- Copies the file if it exists. ---
    copy_file_if_exists() {
        # Usage: copy_file_if_exists <src> <dst>
        src="$1"
        dst="$2"

        if [ -f "$src" ]; then
            cp -f "$src" "$dst"
            return 0
        fi

        return 1
    }
fi