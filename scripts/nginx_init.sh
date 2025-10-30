#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# Nginx service configuration script for RPiSystem multi-service application.
# ------------------------------------------------------------------------------

# Fail on unset vars and non-zero exit codes.
set -eu

# --- Resolve project directories and work from root directory. ---
SCRIPT_DIR=$(dirname "$0")
SCRIPT_NAME=$(basename "$0")
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd -P)

# --- VARIABLES ---
APP_NAME=$(basename "$PROJECT_ROOT")

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
Nginx service configuration script for RPiSystem multi-service application.

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

# --- Restarts the nginx service. ---
reload_nginx() {
    if command -v nginx >/dev/null 2>&1; then
        print_info "Restarting Nginx server ..."
        nginx -t

        if command -v systemctl >/dev/null 2>&1; then
            systemctl restart nginx

            if ! systemctl enable nginx >/dev/null 2>&1; then
                print_info "Skipping \"systemctl enable nginx\" (may be unsupported)."
            fi
        else
            if command -v service >/dev/null 2>&1; then
                service nginx restart
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
        if copy_if_exists "$ARG_KEY" "$KEY"; then
            print_info "Installed key \"$ARG_KEY\" -> \"$KEY\"."
        else
            raise_err "Key file not found at \"$ARG_KEY\"." 1
        fi

        if copy_if_exists "$ARG_CHAIN" "$CHAIN"; then
            print_info "Installed key \"$ARG_CHAIN\" -> \"$CHAIN\"."
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