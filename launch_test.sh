#!/usr/bin/env bash

set -eu

# --- CONST ---
CONST_CMD_CLEAR_ROOT="--internal-clear-root"
CONST_CMD_INIT_NGINX_ROOT="--internal-init-nginx-root"
CONST_CMD_STOP_SUPERVISR_ROOT="--internal-stop-supervisor-root"
CONST_DEV_DEV="dev"
CONST_DEV_PROD="prod"
CONST_DEV_TEST="test"
CONST_MODE_CLEANUP="cleanup"
CONST_MODE_FULL="full"
CONST_MODE_MIGRATE="migrate"
CONST_MODE_STOP="stop"

# --- Directories Setup. ---
SCRIPT_PATH="$0"
PROJECT_ROOT=$(CDPATH=; cd -- "$(dirname "$SCRIPT_PATH")" && pwd -P)
DJANGO_SERVICE_PATH="$PROJECT_ROOT/control_service"
DJANGO_APP_PATH="$DJANGO_SERVICE_PATH/manage.py"
LOGS_DIR="$PROJECT_ROOT/logs"
VENV_DIR="$PROJECT_ROOT/.venv"

APP_NAME=$(basename "${PROJECT_ROOT%/}")
DEVELOPMENT="$CONST_DEV_DEV"
DIR_PERM=700
EXCLUSIVE_COUNT=0
IP_ADDRESS="192.168.1.101"
MODE="$CONST_MODE_FULL"
NO_CLEANUP=0
NO_MIGRATION=0

cd "$PROJECT_ROOT"

# region LOGO CONTENT
LOGO=$(cat << 'EOF'
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

# ------------------------------------------------------------------------------
# --- DISPLAY UTILITIES ---
# ------------------------------------------------------------------------------

# --- Displays an error message in the console. ---
print_error() {
    printf '[%s] ERROR: %s\n' "$APP_NAME" "$*" 1>&2
}

# --- Displays an informational message in the console. ---
print_info() {
    printf '[%s] %s\n' "$APP_NAME" "$*"
}

# --- Display script logo in the console. ---
print_logo() {
    printf '%s\n\n' "$LOGO"
}

# ------------------------------------------------------------------------------
# --- SCRIPT UTILITIES ---
# ------------------------------------------------------------------------------

# --- Displays an error message in the console and terminates the script with an error code. ---
raise_err() {
    error_msg="$1"
    error_code="$2"

    if [ -z "$error_code" ]; then
        error_code="1"
    fi

    print_error "$error_msg"
    exit "$error_code"
}

# --- Check whether the script was run with ROOT privileges. ---
check_root() {
    if [ "$(id -u)" -ne 0 ]; then
        raise_err "To perform this operation the ROOT privileges are required." 1
    fi
}

# --- Creates a directory if it does not exist. ---
ensure_directory_exists() {
    dir_path=${1-}

    # Returning an error if the directory path is invalid.
    if [ -z "$dir_path" ]; then
        raise_err "ensure_directory_exists: Directory path is empty" 1
    fi

    if [ ! -d "$dir_path" ]; then
        if ! mkdir -p -m "$DIR_PERM" -- "$dir_path"; then
            raise_err "Failed to create directory: \"$dir_path\"." 1
        fi
    fi
}

# ------------------------------------------------------------------------------
# --- SCRIPT PARAMETER UTILITIES ---
# ------------------------------------------------------------------------------

# --- Reads IPv4 address value from the script parameter. ---
read_ipv4_address() {
    ip_addr=${1-}

    # Check whether a value has been provided.
    if [ -z "$ip_addr" ]; then
        raise_err "Missing IP address value after --ip." 2
    fi

    IFS=. set -- $ip_addr
    if [ "$#" -ne 4 ]; then
        raise_err "Invalid IPv4 address: $ip_addr." 2
    fi

    for oct in "$@"; do
        case "$oct" in
            ''|*[!0-9]*) raise_err "Invalid IPv4 address: $ip_addr." 2 ;;
        esac

        if [ "$oct" -lt 0 ] || [ "$oct" -gt 255 ]; then
            raise_err "Invalid IPv4 address: $ip_addr" 2
        fi
    done

    printf '%s\n' "$ip_addr"
}

# ------------------------------------------------------------------------------
# --- MAIN EXECUTIVE FUNCTIONS ---
# ------------------------------------------------------------------------------

# --- Clear logs and python build directories. ---
clear_logs() {
    print_info "Clearing supervisor and services logs ..."
    ensure_directory_exists "$LOGS_DIR"
    rm -rf -- "$LOG_DIR"/*

    print_info "Cleaning __pycache__ build file directories ..."
    find "$PROJECT_ROOT" -type d -name "__pycache__" ! -path "$VENV_DIR/*" -exec rm -rf -- {} +
}

# --- Runs logs and python build directories cleanup as root. ---
clear_logs_as_root() {
    sudo -k -- "$SCRIPT_PATH" "$CONST_CMD_CLEAR_ROOT"
}

# --- Initializes the nginx server. ---
init_nginx() {
    ip="${NGINX_IP:-${IP_ADDRESS:-192.168.1.101}}"

    
}

# --- Runs nginx server initialization as root. ---
init_nginx_as_root() {
    sudo -k -- "$SCRIPT_PATH" "$CONST_CMD_INIT_NGINX_ROOT"
}

# --- Loads environment variables from a file. ---
load_env() {
    env_file=""

    case "$DEPLOYMENT" in
        "$CONST_DEV_DEV")   env_file="$PROJECT_ROOT/.env.dev"   ;;
        "$CONST_DEV_PROD")  env_file="$PROJECT_ROOT/.env"       ;;
        "$CONST_DEV_TEST")  env_file="$PROJECT_ROOT/.env.test"  ;;
        *)
            # Use the given path to the .env file.
            if [ -n "$DEPLOYMENT" ] && [ -f "$DEPLOYMENT" ]; then
                env_file="$DEPLOYMENT"
            fi
            ;;
    esac

    if [ -f "$env_file" ]; then
        print_info "Loading environment from $env_file ..."
        set -a          # Automatically exports all variables.
        # shellcheck disable=SC1090
        . "$env_file"   # Loads variables into the environment.
        set +a          # Disables auto-export.
    else
        print_info "NOTE: Environment file $env_file not found! Skipping ..."
    fi
}

# --- Runs Django migrations if a Django app is present. ---
run_django_migrations() {
    if [ -d "$DJANGO_SERVICE_PATH" ] && [ -f "$DJANGO_APP_PATH" ]; then
        print_info "Running Django migrations ..."
        prev_pwd=$(pwd)
        cd "$DJANGO_SERVICE_PATH"
        python "$DJANGO_APP_PATH" migrate --noinput
        cd "$prev_pwd"
    fi
}

# --- Creates & activates Python Virtual Environment. ---
setup_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        print_info "NOTE: Python virtual environment not found."
        print_info "Creating python virtual environment at $VENV_DIR ..."

        python -m venv "$VENV_DIR"

        # Activate Python Virtual Environment and finish one-time setup.
        # shellcheck disable=SC1091
        print_info "Activating python virtual environment ..."
        . "$VENV_DIR/bin/activate"

        # Upgrade pip and install pip-dependent packages.
        print_info "Updating pip and installing its dependent packages ..."
        python -m ensurepip --upgrade >/dev/null 2>&1 || true
        python -m pip install --upgrade pip setuptools wheel

        # Install python requirements from file.
        if [ -f "$REQ_FILE" ]; then
            print_info "Installing dependencies from $REQ_FILE ..."
            python -m pip install -r "$REQ_FILE"
        else
            print_info "NOTE: $REQ_FILE file not found; Skipping dependencies installation."
        fi
    else
        # Activate Python Virtual Environment
        # shellcheck disable=SC1091
        print_info "Activating python virtual environment ..."
        . "$VENV_DIR/bin/activate"
    fi
}

# --- Starts supervisor service. ---
start_supervisor() {
    # Disable annoying pkg_resources deprecation warning (Python 3.13+)
    PYTHONWARNINGS="ignore:pkg_resources is deprecated as an API:UserWarning"
    export PYTHONWARNINGS

    # Supervisor Configuration (used in supervisord.conf)
    RUN_AS_USER="${USER:-$(id -un)}"
    export RUN_AS_USER

    SUPERVISOR_SOCK="/tmp/supervisor-${RUN_AS_USER}.sock"
    export SUPERVISOR_SOCK

    print_info "\nStarting application ..."

    if [ ! -x "$SUPERVISOR_BIN" ]; then
        raise_err "$SUPERVISOR_BIN not found or not executable.\nMake sure Supervisor is installed inside the venv." 3
    fi

    # Run as root, with -E (keep VIRTUAL_ENV, PATH, RUN_AS_USER, SUPERVISOR_SOCK)
    exec sudo -E "$SUPERVISOR_BIN" -n -c supervisord.conf
}

# --- Stops supervisor service. ---
stop_supervisor() {
    # ChatGPT: TODO
}

# --- Runs stop supervisor as root. ---
stop_supervisor_as_root() {
    sudo -k -- "$SCRIPT_PATH" "$CONST_CMD_STOP_SUPERVISR_ROOT"
}

# ------------------------------------------------------------------------------
# --- MAIN FUNCTIONS THAT HANDLES SCRIPT PARAMETERS ---
# ------------------------------------------------------------------------------

# --- Handle internal commands for root only functions execution. ---
handle_internal_command() {
    cmd=${1-}

    check_root

    case "$cmd" in
        "$CONST_CMD_CLEAR_ROOT")
            clear_logs
            ;;
        "$CONST_CMD_INIT_NGINX_ROOT")
            init_nginx
            ;;
        "$CONST_CMD_STOP_SUPERVISR_ROOT")
            stop_supervisor
            ;;
    esac

    exit 0
}

# --- Main method that executes the function corresponding to the given command. ---
main() {
    handle_internal_command "${1-}"

    print_logo

    # Handle parameters.
    while [ "$#" -gt 0 ]; do
        case "$1" in
            -h|--help)
                exit 0
                ;;
            -c|--cleanup)
                EXCLUSIVE_COUNT=$((exclusive_count + 1))
                MODE="$CONST_MODE_CLEANUP"
                shift 1
                ;;
            -m|--migrate)
                EXCLUSIVE_COUNT=$((exclusive_count + 1))
                MODE="$CONST_MODE_MIGRATE"
                shift 1
                ;;
            -s|--stop)
                EXCLUSIVE_COUNT=$((exclusive_count + 1))
                MODE="stop"
                  shift 1
                ;;
            -d|--deployment)
                if [ "$#" -lt 2 ] || [ -z "${2:-}" ]; then
                    raise_err "Missing value for --deployment (use: dev|test|prod|file_path)." 2
                fi
                DEPLOYMENT="$2"
                shift 2
                ;;
            --ip)
                IP_ADDRESS=$(read_ipv4_address "${2-}")
                shift 2
                ;;
            --nocleanup)
                NO_CLEANUP=1
                shift 1
                ;;
            --nomigration)
                NO_MIGRATION=1
                shift 1
                ;;
            *)
                raise_err "Unknown parameter: $1." 1
                ;;
        esac
    done

    # Guard against multiple exclusive modes at once.
    if [ "$EXCLUSIVE_COUNT" -gt 1 ]; then
        raise_err "Conflicting options: choose only one of --cleanup, --migrate, or --stop." 2
    fi

    # Handle exclusive modes.
    case "$MODE" in
        "$CONST_MODE_CLEANUP")
            clear_logs_as_root
            exit 0
            ;;
        "$CONST_MODE_MIGRATE")
            setup_venv
            load_env
            run_django_migrations
            exit 0
            ;;
        "$CONST_MODE_STOP")
            stop_supervisor_as_root
            exit 0
            ;;
    esac

    setup_venv

    if [ "$NO_CLEANUP" -eq 0 ]; then
        clear_logs_as_root
    fi

    load_env

    if [ "$NO_MIGRATION" -eq 0 ]; then
        run_django_migrations
    fi

    init_nginx_as_root
    start_supervisor
}

main "$@"