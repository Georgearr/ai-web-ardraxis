#!/bin/bash
set -e

echo "=== DRAX Deployment Script ==="

PROJECT_DIR="/var/www/draxis"
REPO_URL="git@github.com:your-org/draxis.git"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "Cloning repository..."
    git clone "$REPO_URL" "$PROJECT_DIR"
fi

echo "Pulling latest changes..."
cd "$PROJECT_DIR"
git pull origin main

echo "--- Backend ---"
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate

echo "--- Frontend ---"
cd ../frontend
npm ci
npm run build

echo "--- Restarting Services ---"
sudo systemctl daemon-reload
sudo systemctl restart drax-backend
sudo systemctl restart drax-frontend

echo "--- Reloading Nginx ---"
sudo nginx -t && sudo systemctl reload nginx

echo "=== Deployment Complete ==="
