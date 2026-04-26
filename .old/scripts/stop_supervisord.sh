#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# RPiSystem multi-service application shutdown/kill script.
# ------------------------------------------------------------------------------

# Fail on unset vars and non-zero exit codes.
set -eu

# --- Resolve project directories. ---
SCRIPT_DIR=$(dirname "$0")
SCRIPT_NAME=$(basename "$0")
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd -P)
LIB_DIR="$PROJECT_ROOT/scripts/lib"

# --- VARIABLES ---
APP_NAME=$(basename "$PROJECT_ROOT")
LOGO_FILE="$PROJECT_ROOT/scripts/logo.txt"
SUPERVISOR_SOCK_URI=${SUPERVISOR_SOCK_URI:-unix:///tmp/supervisor.sock}

if [ -x "$PROJECT_ROOT/.venv/bin/supervisorctl" ]; then
    SUPERVISORCTL="$PROJECT_ROOT/.venv/bin/supervisorctl"
else
    SUPERVISORCTL="supervisorctl"
fi

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
Script for forcing the application to close by stopping the supervisor.

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
# --- SUPERVISOR MANAGEMENT METHODS ---
# ------------------------------------------------------------------------------

# --- Runs supervisord command. ---
run_supervisorctl() {
    # Usage: run_supervisorctl <args...>
    "$SUPERVISORCTL" -s "$SUPERVISOR_SOCK_URI" "$@"
}

# --- Checks if supervisord is still running (if so, returns 0, otherwise 1). ---
is_supervisord_running() {
    if pgrep -x supervisord >/dev/null 2>&1; then
        return 0
    fi

    return 1
}

# --- Waits N seconds for supervisord to close. ---
wait_until_stopped() {
    # Usage: wait_until_stopped <N seconds>
    seconds="$1"

    # Check if the seconds value was provided via parameter; fallback to 5.
    if [ -z "$seconds" ]; then
        seconds=5
    fi

    # Ensure seconds is positive integer; fallback to 5.
    if ! expr "$seconds" : '^[0-9][0-9]*$' >/dev/null 2>&1; then
        seconds=5
    fi

    # Countdown waiting for supervisord to close.
    i=0
    while [ "$i" -lt "$seconds" ]; do
        if ! is_supervisord_running; then
            return 0
        fi
        sleep 1
        i=$((i + 1))
    done

    # Final check if supervisord is still running.
    if is_supervisord_running; then
        return 1
    fi

    return 0
}

# --- Graceful shutdown supervisord via supervisorctl. ---
try_graceful_shutdown() {
    print_info "Attempting graceful shutdown via supervisorctl ..."

    if run_supervisorctl status >/dev/null 2>&1; then

        # Stop all programs first (best effort)
        if ! run_supervisorctl stop all >/dev/null 2>&1; then
            print_warn "Failed to stop services by supervisordctl."
        fi

        # Ask supervisord to shut down
        if run_supervisorctl shutdown >/dev/null 2>&1; then
            return 0
        fi

        print_warn "supervisorctl shutdown cmd failed."
        return 1
    fi

    print_warn "supervisorctl not responding."
    return 1
}

# --- Sends SIGTERM to supervisord. ---
try_term_supervisord() {
    print_info "Attempting to SIGTERM shutdown supervisord ..."

    if pkill -TERM -x supervisord >/dev/null 2>&1; then
        return 0
    fi

    print_warn "Failed to SIGTERM shutdown supervisord."
    return 1
}

# --- Sends SIGKILL to supervisord. ---
try_kill_supervisord() {
    print_error "Sending SIGKILL (-9) to supervisord ..."

    if pkill -KILL -x supervisord >/dev/null 2>&1; then
        return 0
    fi

    print_warn "Failed to SIGKILL supervisord."
    return 1
}


# ------------------------------------------------------------------------------
# --- MAIN EXECUTION METHODS ---
# ------------------------------------------------------------------------------

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

    # Shutting down application...
    if is_supervisord_running; then
        print_info "Detected running supervisord service."

        # Graceful shutdown via supervisorctl.
        if try_graceful_shutdown; then
            wait_until_stopped 5
        else
            print_warn "Failed to gracefully shutdown supervisord service."
        fi

        # Shutdown via SIGTERM.
        if is_supervisord_running; then
            if try_term_supervisord; then
                wait_until_stopped 5
            else
                print_warn "Failed to shutdown supervisord via SIGTERM."
            fi
        fi

        # Shutdown via SIGKILL.
        if is_supervisord_running; then
            if try_kill_supervisord; then
                wait_until_stopped 3
            else
                print_warn "Failed to shutdown supervisord via SIGKILL."
            fi
        fi

        # Final status
        if is_supervisord_running; then
            raise_err "Failed to shutdown supervisord." 1
        else
            print_info "Supervisord has been shut down."
            exit 0
        fi
    else
        print_info "No supervisord process found."
        exit 0
    fi
}


main "$@"