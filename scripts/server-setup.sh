#!/usr/bin/env bash
# One-time setup for Oh Hell on the existing cartergrove-me droplet.
# Run as root: bash /opt/oh-hell/scripts/server-setup.sh
set -euo pipefail

DOMAIN="ohhell.cartergrove.me"
APP_DIR="/opt/oh-hell"
DEPLOY_USER="deploy"

echo "==> Installing Python 3.12"
apt-get update
apt-get install -y python3.12 python3.12-venv python3.12-dev || echo "  (Python 3.12 may already be installed)"

echo "==> Installing uv (Python package manager)"
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

echo "==> Creating app directory"
mkdir -p "$APP_DIR"
chown $DEPLOY_USER:$DEPLOY_USER "$APP_DIR"

echo "==> Copying nginx config"
cp "$APP_DIR/nginx/ohhell.cartergrove.me.conf" /etc/nginx/sites-available/ohhell.cartergrove.me.conf
ln -sf /etc/nginx/sites-available/ohhell.cartergrove.me.conf /etc/nginx/sites-enabled/

echo "==> Obtaining SSL certificate"
certbot certonly --nginx -d "$DOMAIN" --non-interactive --agree-tos --email "carter@cartergrove.me" || echo "  (SSL will be configured after DNS propagates)"

echo "==> Testing and reloading nginx"
nginx -t && systemctl reload nginx

echo "==> Done! Next steps:"
echo "  1. Add the deploy public key to /home/$DEPLOY_USER/.ssh/authorized_keys"
echo "  2. Push to main to trigger the first GitHub Actions deploy"
echo "  3. Verify https://$DOMAIN loads correctly"
