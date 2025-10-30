#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# Nginx service shutdown script (with fallback methods).
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
SET_AUTO=1  # default: enabled

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
Nginx service shutdown script (with fallback methods).

Usage: $SCRIPT_NAME [OPTIONS]

Options:
    -h, --help                  Show this help message and exit.
        --no-autostart          Disable nginx service autostart.
        --no-logo               Skip printing the logo.
        --app-name <value>      Override the application name.

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
# --- NGINX MANAGEMENT METHODS ---
# ------------------------------------------------------------------------------

# --- Checks if any nginx master/worker running (if so, returns 0, otherwise 1). ---
is_nginx_running() {
    if pgrep -x nginx >/dev/null 2>&1; then
        return 0
    fi

    return 1
}

# --- Waits N seconds for nginx to stop. ---
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

    # Countdown waiting for nginx to stop.
    i=0
    while [ "$i" -lt "$seconds" ]; do
        if ! is_nginx_running; then
            return 0
        fi
        sleep 1
        i=$((i + 1))
    done

    # Final check if nginx is still running.
    if is_nginx_running; then
        return 1
    fi

    return 0
}

# --- Disables the nginx service from autostart. ---
disable_nginx_autostart() {
    # Skipping the autostart disable setting if flag is not set.
    if [ "${SET_AUTO:-1}" -ne 0 ]; then
        return 0
    fi

    print_info "Disabling Nginx autostart ..."

    if command -v systemctl >/dev/null 2>&1; then
        if systemctl disable nginx >/dev/null 2>&1; then
            print_info "systemctl: Disabled nginx service autostart."
            return 0
        fi
        print_warn "Failed to disable nginx from autostart via systemctl."
    fi

    if command -v update-rc.d >/dev/null 2>&1; then
        if update-rc.d nginx disable >/dev/null 2>&1; then
            print_info "update-rc.d: Disabled nginx service autostart."
            return 0
        fi
        print_warn "Failed to disable nginx from autostart via update-rc.d."
    fi

    if command -v chkconfig >/dev/null 2>&1; then
        if chkconfig nginx off >/dev/null 2>&1; then
            print_info "chkconfig: Disabled nginx service autostart."
            return 0
        fi
        print_warn "Failed to disable nginx from autostart via chkconfig."
    fi

    print_warn "Could not disable nginx service autostart (no supported tool found)."
    return 1
}

# --- Stop nginx service via systemctl. ---
try_stop_nginx_systemctl() {
    if command -v systemctl >/dev/null 2>&1; then
        print_info "Shutting down nginx service via systemctl ..."

        if systemctl stop nginx >/dev/null 2>&1; then
            return 0
        fi

        print_warn "Failed to stop nginx service via via systemctl."
        return 1
    fi

    print_warn "systemctl not available."
    return 1
}

# --- Stop nginx service via SysV-init. ---
try_stop_nginx_service() {
    if command -v service >/dev/null 2>&1; then
        print_info "Shutting down nginx service via service (SysV-init) ..."

        if service nginx stop >/dev/null 2>&1; then
            return 0
        fi

        print_warn "Failed to stop nginx service via service (SysV-init)."
        return 1
    fi

    print_warn "service (SysV-init) command not available."
    return 1
}

# --- Stop nginx service by referencing binaries directly. ---
try_stop_nginx_service_paths() {
    if [ -x /usr/sbin/service ]; then
        print_info "Shutting down nginx service via /usr/sbin/service ..."

        if /usr/sbin/service nginx stop >/dev/null 2>&1; then
            return 0
        fi

        print_warn "Failed to stop nginx service via /usr/sbin/service."
    fi

    if [ -x /sbin/service ]; then
        print_info "Shutting down nginx service via /sbin/service ..."

        if /sbin/service nginx stop >/dev/null 2>&1; then
            return 0
        fi

        print_warn "Failed to stop nginx service via /sbin/service."
    fi

    return 1
}

# --- Stop nginx service via SIGTERM. ---
try_term_nginx() {
    print_info "Sending SIGTERM to nginx service ..."

    if pkill -TERM -x nginx >/dev/null 2>&1; then
        return 0
    fi

    print_warn "Failed to stop nginx service via SIGTERM."
    return 1
}

# --- Force nginx service to stop via SIGKILL. ---
try_kill_nginx() {
    print_info "Sending SIGKILL (-9) to nginx service ..."

    if pkill -KILL -x nginx >/dev/null 2>&1; then
        return 0
    fi

    print_warn "Failed to force stop nginx service via SIGKILL."
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
            --no-autostart)
                SET_AUTO=0
                shitf 1
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

    print_info "Attempting to stop nginx service ..."

    ATTEMPTS="
        try_stop_nginx_systemctl
        try_stop_nginx_service
        try_stop_nginx_service_paths
        try_term_nginx
        try_kill_nginx
    "

    # Stopping nginx service...
    for fn in $ATTEMPTS; do

        # Check if the nginx service is already stopped.
        if ! is_nginx_running; then
            print_info "Nginx has been shut down."
            disable_nginx_autostart
            return 0
        fi

        if "$fn"; then
            if wait_until_nginx_stopped 5; then
                if ! is_nginx_running; then
                    print_info "Nginx service has been stopped."
                    disable_nginx_autostart
                    return 0
                fi
            fi
        fi
    done
}


main "$@"