#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# RPiSystem multi-service application cleanup script.
# ------------------------------------------------------------------------------

# Fail on unset vars and non-zero exit codes.
set -eu


# --- Resolve project directories and work from root directory. ---
SCRIPT_DIR=$(dirname "$0")
SCRIPT_NAME=$(basename "$0")
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd -P)
LOG_DIR="$PROJECT_ROOT/logs"
VENV_DIR="$PROJECT_ROOT/.venv"

# --- VARIABLES ---
APP_NAME=$(basename "$PROJECT_ROOT")

# region LOGO CONTENT
LOGO_CONTENT=$(cat << 'EOF'
 ______   ______   __    _____                       __                            
/      \ /      \ /  |  /     \                     /  |                           
$$$$$$  |$$$$$$  |$$/  /$$$$$  | __   __   ______  _$$ |_     _____   _____  ____  
$$ |_$$ |$$ |_$$ |/  | $$ \_$$/ /  | /  | /      |/ $$   |   /     \ /     \/    \ 
$$   $$< $$   $$/ $$ | $$     \ $$ | $$ |/$$$$$$/ $$$$$$/   /$$$$$  |$$$$$$ $$$$  |
$$$$$$  |$$$$$$/  $$ |  $$$$$  |$$ | $$ |$$     \   $$ | __ $$   $$ |$$ | $$ | $$ |
$$ | $$ |$$ |     $$ | /  \_$$ |$$ \_$$ | $$$$$  |  $$ |/  |$$$$$$$/ $$ | $$ | $$ |
$$ | $$ |$$ |     $$ | $$   $$/ $$   $$ |/    $$/   $$  $$/ $$      |$$ | $$ | $$ |
$$/  $$/ $$/      $$/   $$$$$/   $$$$$$ |$$$$$$/     $$$$/   $$$$$$/ $$/  $$/  $$/ 
                                /  \_$$ |                                          
                                $$   $$/                                           
                                 $$$$$/                                            
EOF
)
# endregion


# Work from the project root.
cd "$PROJECT_ROOT"


# ------------------------------------------------------------------------------
# --- PRINT UTILITY METHODS ---
# ------------------------------------------------------------------------------

# --- Prints an error message on the screen console. ---
print_error() {
    printf '[%s] ERROR: %s\n' "$APP_NAME" "$*" 1>&2
}

# --- Prints a message on the screen console. ---
print_info() {
    printf '[%s] %s\n' "$APP_NAME" "$*"
}

# --- Prints logo on the screen console. ---
print_logo() {
    printf '\n%s\n\n' "$LOGO_CONTENT"
}

# --- Prints the horizotnal screen split line on the screen console. ---
print_line() {
    # Try to get terminal width, fallback to 80 if not available.
    cols=$(tput cols 2>/dev/null || stty size 2>/dev/null | awk '{print $2}' || printf '80')

    # Fallback if cols is empty or invalid.
    case "$cols" in
        ''|*[!0-9]*) cols=80 ;;
    esac

    # Print line of '-' characters using printf and tr for safely character repeatition.
    printf '%*s\n' "$cols" '' | tr ' ' '-'
}


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
    --no-logo           Skip printing the logo.
    --app-name <value>  Override the application name.
    -h, --help          Show this help message and exit.

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
# --- SCRIPT UTILITY METHODS ---
# ------------------------------------------------------------------------------

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

# --- Makes sure the directory exists, if not creates it. ---
ensure_directory_exists() {
    dir_path="$1"

    if [ ! -d "$dir_path" ]; then
        mkdir -p "$dir_path"
    fi
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
        -type d -name "__pycache__" -exec rm -rf -- {} \;
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