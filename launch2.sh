#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# RPiSystem multi-service application startup and management script.
# ------------------------------------------------------------------------------

set -eu


# --- CONSTANT ---
CONST_DEPLOYMENT_DEV="dev"
CONST_DEPLOYMENT_PROD="prod"
CONST_DEPLOYMENT_TEST="test"
CONST_MODE_CLEANUP="cleanup"
CONST_MODE_FULL="full"
CONST_MODE_MIGRATE="migrate"
CONST_MODE_STOP="stop"
DEFAULT_IP_ADDRESS="192.168.1.101"


# --- Resolve project directories. ---
SCRIPT_DIR=$(dirname "$0")
SCRIPT_NAME=$(basename "$0")
PROJECT_ROOT=$(cd "$SCRIPT_DIR" && pwd -P)

# --- Resolve scripts directories. ---
SCRIPTS_DIR="$PROJECT_ROOT/scripts"
LIB_DIR="$SCRIPTS_DIR/lib"

CLEAR_SCRIPT="$SCRIPTS_DIR/cleanup.sh"
INIT_NGINX_SCRIPT="$SCRIPTS_DIR/init_nginx.sh"
SETUP_SCRIPT="$SCRIPTS_DIR/setup.sh"
STOP_NGINX_SCRIPT="$SCRIPTS_DIR/stop_nginx.sh"
STOP_SUPERVISORD_SCRIPT="$SCRIPTS_DIR/stop_supervisord.sh"

# --- Common files and directories. ---
DJANGO_SERVICE_PATH="$PROJECT_ROOT/control_service"
DJANGO_APP_PATH="$DJANGO_SERVICE_PATH/manage.py"
LOGS_DIR="$PROJECT_ROOT/logs"
REQ_FILE="$PROJECT_ROOT/requirements.txt"
VENV_DIR="$PROJECT_ROOT/.venv"

# --- VARIABLES & PARAMETERS ---
APP_NAME=$(basename "$PROJECT_ROOT")
DEPLOYMENT="$CONST_DEPLOYMENT_DEV"
IP_ADDRESS="$DEFAULT_IP_ADDRESS"
LOGO_FILE="$PROJECT_ROOT/scripts/logo.txt"
MODE="$CONST_MODE_FULL"
NO_CLEANUP=0
NO_MIGRATION=0
NO_NGINX_INIT=0

# Work from the project root.
cd "$PROJECT_ROOT"

# Source common libs.
. "$LIB_DIR/common.sh"
. "$LIB_DIR/python.sh"


# ------------------------------------------------------------------------------
# --- PRINT HELP METHODS ---
# ------------------------------------------------------------------------------

# --- Prints help text on the screen console. ---
print_help() {
    # region HELP CONTENT
    HELP_TEXT=$(cat <<EOF
RPiSystem multi-service application startup and management script.

Usage: $SCRIPT_NAME [OPTIONS]

Options:
    -h, --help                  Show this help message and exit.
    -c, --cleanup               Clears supervisor and service logs, along with python build files.
    -m, --migrate               Performs Django service migrations.
    -s, --stop                  Stops the application by stopping the supervisord service.
    -d, --deployment <value>    Sets the .env environment configuration (file path can be specified).
        --ip <ipv4_address>     The IP address on which the service is to be hosted by nginx.
        --nocleanup             Skip clearing logs on startup.
        --nomigration           Skip Django service migrations on startup.
        --nonginx-init          Skip nginx service reinitialization on startup.

Development modes:
    -dev        .env.dev file
    -prod       .env file
    -test       .env.test file

Examples:
    $SCRIPT_NAME --cleanup
    $SCRIPT_NAME --stop
    $SCRIPT_NAME -d test --ip 192.168.1.101
    $SCRIPT_NAME -d prod --ip 192.168.1.101 --nocleanup --nomigration
EOF
)
    # endregion

    print_line
    printf "%s\n" "$HELP_TEXT"
    print_line
}

# ------------------------------------------------------------------------------
# --- PARAMS HANDLING METHODS ---
# ------------------------------------------------------------------------------

# --- Reads and validates the IPv4 address from param; fallback to: ENV, default value. ---
read_ipv4_address() {
    ip_addr=${1-}

    # Check whether a value has been provided.
    if [ -z "$ip_addr" ]; then
        raise_err "Missing IP address value after --ip." 2
    fi

    # Remove whitespace (spaces, tabs, CR/LF) from input. 
    ip_addr=$(printf '%s' "$ip_addr" | tr -d ' \t\r\n')

    # Temporarily set IFS to dot, disable globbing, split into octets.
    set -f
    old_ifs=$IFS
    IFS=.
    set -- $ip_addr
    IFS=$old_ifs
    set +f

    # Check the number of octets (have to be 4).
    if [ "$#" -ne 4 ]; then
        raise_err "Invalid IPv4 address: $ip_addr." 2
        return 2
    fi

    # Validation of each octet.
    for oct in "$@"; do
        # Only numbers
        case $oct in
            ''|*[!0-9]*)
                raise_err "Invalid IPv4 address: $ip_addr." 2
                return 2
                ;;
        esac

        # Range 0..255
        if [ "$oct" -lt 0 ] || [ "$oct" -gt 255 ]; then
            raise_err "Invalid IPv4 address: $ip_addr." 2
            return 2
        fi
    done

    printf '%s\n' "$ip_addr"
}

# ------------------------------------------------------------------------------
# --- MAIN EXECUTION METHODS ---
# ------------------------------------------------------------------------------

# --- Runs a script that cleanup logs and python build files from __pycache__. ---
cleanup() {
    if [ -f "$CLEAR_SCRIPT" ]; then
        sudo -k bash "$CLEAR_SCRIPT" --no-logo --app-name "$APP_NAME"
    fi
}

# --- Loads environment variables dependent on deployment or from a file. ---
load_deployment_env() {
    env_file=""

    case "$DEPLOYMENT" in
        "$CONST_DEPLOYMENT_DEV")
            env_file="$PROJECT_ROOT/.env.dev"
            ;;
        "$CONST_DEPLOYMENT_PROD")
            env_file="$PROJECT_ROOT/.env"
            ;;
        "$CONST_DEPLOYMENT_TEST")
            env_file="$PROJECT_ROOT/.env.test"
            ;;
        *)
            # If file path is given, trye to load from file.
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

# --- Initializes nginx service config and starts it up. ---
nginx_init() {
    if [ -f "$INIT_NGINX_SCRIPT" ]; then
        sudo -k bash "$INIT_NGINX_SCRIPT" --no-logo --app-name "$APP_NAME" --ip "$IP_ADDRESS"
    fi
}

# --- Runs Django migrations if a Django app is present. ---
run_django_migrations() {
    py_exec="$1"

    if [ -d "$DJANGO_SERVICE_PATH" ] && [ -f "$DJANGO_APP_PATH" ]; then
        print_info "Running Django migrations ..."
        prev_pwd=$(pwd)
        cd "$DJANGO_SERVICE_PATH"
        "$py_exec" "$DJANGO_APP_PATH" migrate --noinput
        cd "$prev_pwd"
    fi
}

# --- Detect (if doesn't exist, create) and activate the Python virtual environment. ---
setup_venv() {
    py_exec="$1"
    venv_dir="$2"
    req_file="$3"

    if [ ! -d "$venv_dir" ]; then
        # Create Python virtual environment.
        create_venv "$py_exec" "$venv_dir"

        # Activate the virtual environment.
        py_exec=$(activate_venv "$venv_dir")

        # Upgrade pip toolchain and install requirements.
        upgrade_pip_toolchain "$py_exec"
        install_requirements "$py_exec" "$req_file"
    else
        # Activate existing virtual environment.
        py_exec=$(activate_venv "$venv_dir")
    fi

    # Return python path via stdout.
    printf '%s\n' "$py_exec"
}

# --- Start supervisord service (start application). ---
start_supervisord() {
    export VIRTUAL_ENV="$VENV_DIR"

    # Disable annoying pkg_resources deprecation warning (Python 3.13+)
    PYTHONWARNINGS="ignore:pkg_resources is deprecated as an API:UserWarning"
    export PYTHONWARNINGS

    # Supervisor Configuration (used in supervisord.conf)
    RUN_AS_USER="${USER:-$(id -un)}"
    export RUN_AS_USER

    SUPERVISOR_SOCK="/tmp/supervisor-rpi.sock"
    export SUPERVISOR_SOCK

    printf '\n'
    print_info "Starting application ..."

    SUPERVISOR_BIN="$VENV_DIR/bin/supervisord"

    if [ ! -x "$SUPERVISOR_BIN" ]; then
        raise_err "$SUPERVISOR_BIN not found or not executable.\nMake sure Supervisor is installed inside the venv." 3
    fi

    # Run as root, with -E (keep VIRTUAL_ENV, PATH, RUN_AS_USER, SUPERVISOR_SOCK)
    exec sudo -E "$SUPERVISOR_BIN" -n -c supervisord.conf
}

# --- Stops the application by stopping supervisord. ---
stop_supervisord() {
    if [ -f "$STOP_SUPERVISORD_SCRIPT" ]; then
        sudo -k bash "$STOP_SUPERVISORD_SCRIPT" --no-logo --app-name "$APP_NAME"
    fi
}


# --- Handle provided script parameters. ----
handle_script_parameters() {
    exclusive_count=0

    while [ "$#" -gt 0 ]; do
        case "$1" in
            -h|--help)
                print_help
                exit 0
                ;;
            -c|--cleanup)
                exclusive_count=$((exclusive_count + 1))
                MODE="$CONST_MODE_CLEANUP"
                shift 1
                ;;
            -m|--migrate)
                exclusive_count=$((exclusive_count + 1))
                MODE="$CONST_MODE_MIGRATE"
                shift 1
                ;;
            -s|--stop)
                exclusive_count=$((exclusive_count + 1))
                MODE="$CONST_MODE_STOP"
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
            --nonginx-init)
                NO_NGINX_INIT=1
                shift 1
                ;;
            *)
                raise_err "Unknown parameter: $1." 1
                ;;
        esac
    done

    # Guard against multiple exclusive modes at once.
    if [ "$exclusive_count" -gt 1 ]; then
        raise_err "Conflicting options: choose only one of --cleanup, --migrate, --stop." 2
    fi
}

# --- Handle exclusive modes. ---
handle_exclusive_modes() {
    py_exec="$1"

    case "$MODE" in
        "$CONST_MODE_CLEANUP")
            cleanup
            exit 0
            ;;
        "$CONST_MODE_MIGRATE")
            py_exec=$(setup_venv "$py_exec" "$VENV_DIR" "$REQ_FILE")
            load_deployment_env
            run_django_migrations "$py_exec"
            exit 0
            ;;
        "$CONST_MODE_STOP")
            stop_supervisord
            exit 0
            ;;
    esac
}

# --- The main execution function that handles script parameters. ---
main() {
    print_logo

    # Handle provided script parameters.
    handle_script_parameters "$@"

    # Check if python interpreter is available in system.
    PY_EXEC=$(detect_python || true)

    # Handle exclusive modes.
    handle_exclusive_modes "$PY_EXEC"

    # Detect (if doesn't exist, create) and activate the Python virtual environment.
    PY_EXEC=$(setup_venv "$PY_EXEC" "$VENV_DIR" "$REQ_FILE")

    # Cleanup logs and python build files from __pycache__.
    if [ "$NO_CLEANUP" -eq 0 ]; then
        cleanup
    fi

    # Load environment variables from file.
    load_deployment_env

    # Run Django migrations if a Django app is present.
    if [ "$NO_MIGRATION" -eq 0 ]; then
        run_django_migrations "$PY_EXEC"
    fi

    # Initialize nginx service configuration and start it up.
    if [ "$NO_NGINX_INIT" -eq 0 ]; then
        nginx_init
    fi

    # Start supervisor service (start application).
    start_supervisord
}


main "$@"