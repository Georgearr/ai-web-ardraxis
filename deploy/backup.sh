#!/bin/bash
set -e

BACKUP_DIR="/var/backups/draxis"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_PATH="$BACKUP_DIR/draxis-backup-$TIMESTAMP.tar.gz"

mkdir -p "$BACKUP_DIR"

echo "Creating backup at $BACKUP_PATH..."

tar -czf "$BACKUP_PATH" \
    -C /var/www/draxis \
    --exclude="node_modules" \
    --exclude=".venv" \
    --exclude=".next" \
    --exclude="__pycache__" \
    .

echo "Removing backups older than 7 days..."
find "$BACKUP_DIR" -name "draxis-backup-*.tar.gz" -mtime +7 -delete

echo "Backup complete: $BACKUP_PATH"
