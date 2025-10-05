#!/usr/bin/env bash
set -euo pipefail

IP="${1:-192.168.1.101}"  # Allows to overwrite IP: ./init_nginx.sh 10.0.0.5

# Create required directories
mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled /etc/ssl/pi_stack

# Copy nginx configuration
cp -f nginx/pi_stack.conf /etc/nginx/sites-available/pi_stack.conf
ln -sf /etc/nginx/sites-available/pi_stack.conf /etc/nginx/sites-enabled/pi_stack.conf

# Self-signed cert (there will be warnings in the browser for the IP - this is normal)
if [ ! -f /etc/ssl/pi_stack/fullchain.pem ]; then
  openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
    -subj "/CN=${IP}" \
    -keyout /etc/ssl/pi_stack/privkey.pem \
    -out /etc/ssl/pi_stack/fullchain.pem
fi

# Test and restart nginx (if installed)
if command -v nginx >/dev/null 2>&1; then
  nginx -t && systemctl restart nginx
  systemctl enable nginx >/dev/null 2>&1 || true
else
  echo "[!] Nginx is not installed."
fi