#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# RPiSystem multi-service application cleanup script.
# ------------------------------------------------------------------------------

# Fail on unset vars and non-zero exit codes.
set -eu


# --- Resolve project directories. ---
SCRIPT_DIR=$(dirname "$0")
SCRIPT_NAME=$(basename "$0")
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd -P)
LIB_DIR="$PROJECT_ROOT/scripts/lib"
LOG_DIR="$PROJECT_ROOT/logs"
VENV_DIR="$PROJECT_ROOT/.venv"

# --- VARIABLES ---
APP_NAME=$(basename "$PROJECT_ROOT")
LOGO_FILE="$PROJECT_ROOT/scripts/logo.txt"

# Work from the project root.
cd "$PROJECT_ROOT"

# Source common libs.
. "$LIB_DIR/common.sh"


# ------------------------------------------------------------------------------
# --- PRINT HELP METHODS ---
# ------------------------------------------------------------------------------

# --- Prints help text on the screen console. ---
print_help() {
    # region HELP CONTENT
    HELP_TEXT=$(cat <<EOF
Script for cleaning supervisor logs, services, and build files from __pycache__ directories.

Usage: $SCRIPT_NAME [OPTIONS]

Options:
    -h, --help              Show this help message and exit.
        --no-logo           Skip printing the logo.
        --app-name <value>  Override the application name.

Examples:
    $SCRIPT_NAME --no-logo
    $SCRIPT_NAME --app-name myproject
EOF
)
    # endregion

    print_line
    printf "%s\n" "$HELP_TEXT"
    print_line
}


# ------------------------------------------------------------------------------
# --- MAIN EXECUTION METHODS ---
# ------------------------------------------------------------------------------

# --- Cleans supervisor and services logs. ---
clean_logs() {
    print_info "Cleaning supervisor and services logs ..."
    
    # Ensure the log directory exists
    ensure_directory_exists "$LOG_DIR"

    # Remove all files and directories inside LOG_DIR, including dotfiles.
    # The pattern may not match; suppress errors to remain portable under 'set -e'.
    rm -rf -- "$LOG_DIR"/* "$LOG_DIR"/.[!.]* "$LOG_DIR"/..?* 2>/dev/null || :
}

# --- Cleans up python build files from __pycache__ directories. ---
clean_pycache() {
    print_info "Cleaning the project from __pycache__ directories ..."
    
    find "$PROJECT_ROOT" \
        -path "$VENV_DIR" -prune -o \
        -type d -name "__pycache__" -exec rm -rf -- {} + 2>/dev/null
}

# --- The main execution function that handles script parameters. ---
main() {
    SHOW_LOGO=1     # default: show logo.

    # Handle script parameters.
    while [ $# -gt 0 ]; do
        case "$1" in
            -h|--help)
                print_logo
                print_help
                exit 0
                ;;
            --app-name)
                # Override APP_NAME if provided.
                if [ $# -lt 2 ]; then
                    raise_err "Missing value for --app-name" 1
                fi
                APP_NAME="$2"
                shift 2
                ;;
            --no-logo)
                SHOW_LOGO=0
                shift
                ;;
            *)
                raise_err "Unknown option: \"$1\" (Use -h/--help)." 1
                ;;
        esac
    done

    if [ "$SHOW_LOGO" -eq 1 ]; then
        print_logo
    fi

    # Require ROOT privilages to cleanup logs.
    check_root

    # Cleaning ...
    clean_logs
    clean_pycache

    print_info "Cleaning complete."
}


main "$@"