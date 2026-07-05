#!/usr/bin/env bash
set -euo pipefail

# Simple setup script to install nginx + certbot and enable the provided site.
# Usage: sudo DOMAIN=your.domain EMAIL=you@example.com ./scripts/setup_nginx_certbot.sh

DOMAIN=${DOMAIN:-}
EMAIL=${EMAIL:-}

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
  echo "Usage: DOMAIN=your.domain EMAIL=you@example.com $0"
  exit 1
fi

echo "Installing nginx and certbot..."
apt update
apt install -y nginx python3-certbot-nginx

echo "Copying nginx site configuration..."
sudo cp deployment/nginx/soc_ingest.conf /etc/nginx/sites-available/soc_ingest
sudo sed -i "s/soc.example.com/$DOMAIN/g" /etc/nginx/sites-available/soc_ingest

if [ ! -e /etc/nginx/sites-enabled/soc_ingest ]; then
  sudo ln -s /etc/nginx/sites-available/soc_ingest /etc/nginx/sites-enabled/soc_ingest
fi

echo "Testing nginx configuration..."
sudo nginx -t
sudo systemctl reload nginx

echo "Requesting Let's Encrypt certificate for $DOMAIN..."
sudo certbot --nginx -d "$DOMAIN" --agree-tos --email "$EMAIL" --non-interactive

echo "Done. Certificates obtained and nginx reloaded."

# Reminder to copy systemd unit and env file
cat <<'EOF'
Next steps:
 - Copy system/systemd/soc-ingest.prod.service to /etc/systemd/system/soc-ingest.service
 - Copy system/systemd/soc-ingest.env to /etc/default/soc-ingest and edit INGEST_API_KEY
 - sudo systemctl daemon-reload
 - sudo systemctl enable --now soc-ingest.service
EOF
