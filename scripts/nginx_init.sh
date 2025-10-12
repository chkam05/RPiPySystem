#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# Init nginx site:
# 
# - copy config from repo,
# - ensure self-signed cert,
# - reload nginx.
# ------------------------------------------------------------------------------
set -euo pipefail

# Work from project root (parent of ./scripts)
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
APP_NAME="$(basename -- "${PROJECT_ROOT%/}")"

cd "$PROJECT_ROOT"

# IP comes from arg, then env, then default.
IP="${1:-${NGINX_IP:-192.168.1.101}}"

# Configuration
# ------------------------------------------------------------------------------
SITE="pi_stack"
CONF_SRC="$PROJECT_ROOT/nginx/${SITE}.conf"
CONF_DST="/etc/nginx/sites-available/${SITE}.conf"
LINK_DST="/etc/nginx/sites-enabled/${SITE}.conf"
SSL_DIR="/etc/ssl/${SITE}"
CHAIN="$SSL_DIR/fullchain.pem"
KEY="$SSL_DIR/privkey.pem"
# ------------------------------------------------------------------------------

# Create required directories
mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled "$SSL_DIR"

# Copy nginx configuration
# ------------------------------------------------------------------------------
if [ -f "$CONF_SRC" ]; then
    cp -f "$CONF_SRC" "$CONF_DST"
    ln -sf "$CONF_DST" "$LINK_DST"
else
    echo "[$APP_NAME] ERR: Missing ngingx configuration file $CONF_SRC" >&2
    exit 1
fi
# ------------------------------------------------------------------------------

# Create a simple self-signed cert if missing
# ------------------------------------------------------------------------------
if [ ! -f "$CHAIN" ] || [ ! -f "$KEY" ]; then
    echo "[$APP_NAME] Generating self-signed cert for CN=$IP ..."

    openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
        -subj "/CN=$IP" \
        -keyout "$KEY" \
        -out "$CHAIN"
fi
# ------------------------------------------------------------------------------

# Test and restart nginx (if installed)
# ------------------------------------------------------------------------------
if command -v nginx >/dev/null 2>&1; then
    echo "[$APP_NAME] Restarting Nginx server on $IP ..."
    nginx -t
    systemctl restart nginx
    systemctl enable nginx >/dev/null 2>&1 || true
    echo "[$APP_NAME] Nginx server ready on $IP"
else
    echo "[$APP_NAME] ERR: Nginx server is not installed"
fi
# ------------------------------------------------------------------------------