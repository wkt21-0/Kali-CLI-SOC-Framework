Certbot & HTTPS setup for SOC ingest server

This document explains how to obtain a Let's Encrypt certificate with Certbot and configure Nginx
as a reverse proxy that terminates TLS for the SOC ingest FastAPI server.

Prerequisites
- A registered domain (e.g. soc.example.com) pointing to this server's public IP
- Root or sudo access

High-level steps
1. Install Nginx and Certbot
2. Place the nginx site configuration and enable it
3. Obtain certificates with Certbot
4. Run uvicorn on 127.0.0.1:8000 managed by systemd

Commands (Debian/Ubuntu example)

# Install packages
sudo apt update
sudo apt install -y nginx python3-certbot-nginx

# Copy the provided nginx site file to /etc/nginx/sites-available/soc_ingest
# then enable it:
sudo cp deployment/nginx/soc_ingest.conf /etc/nginx/sites-available/soc_ingest
sudo ln -s /etc/nginx/sites-available/soc_ingest /etc/nginx/sites-enabled/soc_ingest

# Test and reload nginx
sudo nginx -t && sudo systemctl reload nginx

# Obtain certificates (interactive)
# Replace soc.example.com with your domain and provide a valid email for renewal notices
sudo certbot --nginx -d soc.example.com --agree-tos --email you@example.com --non-interactive

# Certbot will update the nginx config and create the certificate files under /etc/letsencrypt

# Ensure automatic renewal is working (certbot installs a cron/systemd timer)
sudo systemctl status certbot.timer

# Start the uvicorn service via systemd (unit file: system/systemd/soc-ingest.prod.service)
# Copy the unit to /etc/systemd/system and the env file to /etc/default/soc-ingest (set INGEST_API_KEY)
sudo cp system/systemd/soc-ingest.prod.service /etc/systemd/system/soc-ingest.service
sudo cp system/systemd/soc-ingest.env /etc/default/soc-ingest
sudo systemctl daemon-reload
sudo systemctl enable --now soc-ingest.service

Notes & security
- Make sure /etc/default/soc-ingest is owned by root and permissions are 600.
- Do not place API keys in the repository. Use the env file only on the host.
- Nginx handles TLS and should be kept updated. Certbot will automatically renew certs by default.
- Consider enabling UFW and opening only necessary ports (80, 443) to the world; keep port 8000 local-only.

Troubleshooting
- If certbot fails due to existing nginx config, check /var/log/letsencrypt/letsencrypt.log
- To manually renew: sudo certbot renew --dry-run
