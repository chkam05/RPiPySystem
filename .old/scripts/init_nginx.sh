#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# Nginx service configuration script for RPiSystem multi-service application.
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
SET_AUTO=0  # default: disabled

SITE="pi_stack"
NGINX_CONF_DIR="/etc/nginx/sites-available"
NGINX_LINK_DIR="/etc/nginx/sites-enabled"
SSL_DIR="/etc/ssl/${SITE}"

CONF_SRC="$PROJECT_ROOT/nginx/${SITE}.conf"
CHAIN="$SSL_DIR/fullchain.pem"
KEY="$SSL_DIR/privkey.pem"
NGINX_CONF="${NGINX_CONF_DIR}/${SITE}.conf"
NGINX_LINK="${NGINX_LINK_DIR}/${SITE}.conf"

DEFAULT_IP="192.168.1.101"

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
Nginx service configuration script for RPiSystem multi-service application.

Usage: $SCRIPT_NAME [OPTIONS]

Options:
    -h, --help                  Show this help message and exit.
    -a, --autostart             Enable nginx service autostart.
        --ip <value>            Override IP used in generated self-signed cert CN.
        --config <file>         Path to nginx site configuration to install.
        --config-name <value>   Target site configuration name.
        --key <file>            Path to 'privkey.pem' to copy into \"$KEY\".
        --chain <file>          Path to 'fullchain.pem' to copy into \"$CHAIN\".
        --no-logo               Skip printing the logo.
        --app-name <value>      Override the application name.

Rules:
    - If both --key or --chain is omitted, a self-signed pair will be generated.

Environment:
    NGINX_IP    Default IP if --ip not provided (fallback: $DEFAULT_IP)

Examples:
    $SCRIPT_NAME --ip 192.168.1.101 --config $PROJECT_ROOT/nginx/$SITE.conf --config-name $SITE
    $SCRIPT_NAME --ip 192.168.1.101 --no-logo --app-name myproject
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

# --- Returns the ip for the nginx service; fallback: ENV, default. ---
resolve_ip() {
    ip="$1"

    if [ -n "$ip" ]; then
        printf '%s\n' "$ip"
        return 0
    fi

    if [ -n "${NGINX_IP-}" ]; then
        printf '%s\n' "$NGINX_IP"
        return 0
    fi

    printf '%s\n' "$DEFAULT_IP"
}

# --- Overwrites the target configuration name and updates dependent paths. ---
overwrite_site_name() {
    site_name="$1"

    if [ -n "$site_name" ] && expr "$site_name" : '^[A-Za-z0-9._-]\+$' >/dev/null 2>&1; then
        SITE="$site_name"
        SSL_DIR="/etc/ssl/${site_name}"
        NGINX_CONF="${NGINX_CONF_DIR}/${site_name}.conf"
        NGINX_LINK="${NGINX_LINK_DIR}/${site_name}.conf"
    else
        raise_err "Incorrect value \"$site_name\" for --config-name" 1
    fi
}


# ------------------------------------------------------------------------------
# --- NGINX MANAGEMENT METHODS ---
# ------------------------------------------------------------------------------

# --- Installs the nginx service configuration. ---
install_nginx_conf() {
    # Usage: install_nginx_conf <conf_src>
    conf_src="$1"

    if [ ! -f "$conf_src" ]; then
        raise_err "Missing nginx configuration file: \"$conf_src\"." 1
    fi

    ensure_directory_exists "$NGINX_CONF_DIR"
    ensure_directory_exists "$NGINX_LINK_DIR"

    cp -f "$conf_src" "$NGINX_CONF"
    ln -sf "$NGINX_CONF" "$NGINX_LINK"

    print_info "Installed nginx config: \"$NGINX_CONF\" -> \"$NGINX_LINK\"."
}

# --- Generates nginx server key and certificate. ---
generate_self_signed_if_missing() {
    ip="$1"

    if [ -f "$KEY" ] && [ -f "$CHAIN" ]; then
        print_info "SSL files already present; Generation skipped."
        return 0
    fi

    if ! command -v openssl >/dev/null 2>&1; then
        raise_err "OpenSSL not found; Cannot generate self-signed certificate."
    fi

    # Ensure existence of SSL directory.
    ensure_directory_exists "$SSL_DIR"

    print_info "Generating self-signed key + certificate for CN=$ip ..."
    openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
        -subj "/CN=$ip" \
        -keyout "$KEY" \
        -out "$CHAIN"
}

# --- Enables the nginx service to autostart. ---
enable_nginx_autostart() {
    # Skipping the autostart enable setting if flag is not set.
    if [ "${SET_AUTO:-0}" -ne 1 ]; then
        return 0
    fi

    print_info "Enabling nginx service autostart ..."

    if command -v systemctl >/dev/null 2>&1; then
        if systemctl enable nginx >/dev/null 2>&1; then
            print_info "systemctl: Enabled nginx service autostart."
            return 0
        fi
        print_warn "Failed to enable nginx autostart via systemctl."
    fi

    if command -v update-rc.d >/dev/null 2>&1; then
        if update-rc.d nginx enable >/dev/null 2>&1; then
            print_info "update-rc.d: Enabled nginx service autostart."
            return 0
        fi
        print_warn "Failed to enable nginx autostart via update-rc.d."
    fi

    if command -v chkconfig >/dev/null 2>&1; then
        if chkconfig nginx on >/dev/null 2>&1; then
            print_info "chkconfig: Enabled nginx service autostart."
            return 0
        fi
        print_warn "Failed to enable nginx autostart via chkconfig."
    fi

    print_warn "Could not enable nginx service autostart (no supported tool found)."
    return 1
}

# --- Restarts the nginx service. ---
reload_nginx() {
    if command -v nginx >/dev/null 2>&1; then
        print_info "Restarting Nginx server ..."
        nginx -t

        if command -v systemctl >/dev/null 2>&1; then
            if ! systemctl restart nginx >/dev/null 2>&1; then
                print_warn "Failed to restart nginx service via systemctl."
            fi

            enable_nginx_autostart
        else
            if command -v service >/dev/null 2>&1; then
                if ! service nginx restart >/dev/null 2>&1; then
                    print_warn "Failed to restart nginx service via service (SysV-init)."
                fi

                enable_nginx_autostart
            else
                print_warn "No systemctl/service found; Please restart nginx manually."
            fi
        fi

        print_info "Nginx server ready on $IP."
    else
        raise_err "Nginx server is not installed." 1
    fi
}


# ------------------------------------------------------------------------------
# --- MAIN EXECUTION METHODS ---
# ------------------------------------------------------------------------------

# --- The main execution function that handles script parameters. ---
main() {
    ARG_CONF=""
    ARG_CHAIN=""
    ARG_KEY=""
    IP=""
    IP_PROVIDED=0   # default: ip not provied via param.
    SHOW_LOGO=1     # default: show logo.

    # Handle script parameters.
    while [ $# -gt 0 ]; do
        case "$1" in
            -h|--help)
                print_logo
                print_help
                exit 0
                ;;
            -a|--autostart)
                SET_AUTO=1
                shift 1
                ;;
            --app-name)
                # Override APP_NAME if provided.
                if [ $# -lt 2 ]; then
                    raise_err "Missing value for --app-name" 1
                fi
                APP_NAME="$2"
                shift 2
                ;;
            --ip)
                if [ $# -lt 2 ]; then
                    raise_err "Missing value for --ip"
                fi
                IP=$(resolve_ip "$2")
                IP_PROVIDED=1
                shift 2
                ;;
            --config)
                if [ $# -lt 2 ]; then
                    raise_err "Missing value for --config"
                fi
                ARG_CONF="$2"
                shift 2
                ;;
            --config-name)
                if [ $# -lt 2 ]; then
                    raise_err "Missing value for --config-name"
                fi
                overwrite_site_name "$2"
                shift 2
                ;;
            --key)
                if [ $# -lt 2 ]; then
                    raise_err "Missing value for --key"
                fi
                ARG_KEY="$2"
                shift 2
                ;;
            --chain)
                if [ $# -lt 2 ]; then
                    raise_err "Missing value for --chain"
                fi
                ARG_CHAIN="$2"
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

    # Compute final IP if not set by --ip (CLI had highest priority).
    if [ "$IP_PROVIDED" -eq 0 ]; then
        IP=$(resolve_ip "")
    fi

    # Resolve CONF (CLI override).
    if [ -n "$ARG_CONF" ]; then
        CONF_SRC="$ARG_CONF"
    fi

    # Copy Nginx configuration file.
    ensure_directory_exists "$SSL_DIR"
    install_nginx_conf "$CONF_SRC"

    if [ -n "$ARG_KEY" ] && [ -n "$ARG_CHAIN" ]; then
        # Copy key & chain file.
        if copy_file_if_exists "$ARG_KEY" "$KEY"; then
            print_info "Installed key \"$ARG_KEY\" -> \"$KEY\"."
        else
            raise_err "Key file not found at \"$ARG_KEY\"." 1
        fi

        if copy_file_if_exists "$ARG_CHAIN" "$CHAIN"; then
            print_info "Installed chain \"$ARG_CHAIN\" -> \"$CHAIN\"."
        else
            raise_err "Chain file not found at \"$ARG_CHAIN\"." 1
        fi
    else
        # Generate self-signed key + certificate.
        generate_self_signed_if_missing "$IP"
    fi

    # Test & reload nginx
    reload_nginx
}


main "$@"