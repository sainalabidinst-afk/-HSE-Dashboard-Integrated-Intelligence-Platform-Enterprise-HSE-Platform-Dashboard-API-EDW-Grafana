#!/bin/bash
set -euo pipefail

# PostgreSQL Backup Script for HSE Enterprise Platform
# Performs full database backup with compression and retention

BACKUP_DIR="${BACKUP_DIR:-/backups}"
POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_DB="${POSTGRES_DB:-hse_edw}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/hse_edw_$TIMESTAMP.sql.gz"

# Read password from file if available (Docker secrets)
if [ -f "/run/secrets/postgres_password" ]; then
    POSTGRES_PASSWORD=$(cat /run/secrets/postgres_password)
elif [ -n "${POSTGRES_PASSWORD:-}" ]; then
    POSTGRES_PASSWORD="$POSTGRES_PASSWORD"
else
    echo "ERROR: PostgreSQL password not provided" >&2
    exit 1
fi

export PGPASSWORD="$POSTGRES_PASSWORD"

echo "Starting backup of $POSTGRES_DB..."

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Perform backup
pg_dump -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
    --format=plain \
    --no-owner \
    --no-acl \
    --verbose \
    --schema=hse \
    | gzip > "$BACKUP_FILE"

# Unset password
unset PGPASSWORD

# Verify backup
if [ -f "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "Backup completed successfully: $BACKUP_FILE ($BACKUP_SIZE)"
else
    echo "ERROR: Backup file not created" >&2
    exit 1
fi

# Create latest symlink
ln -sf "$(basename "$BACKUP_FILE")" "$BACKUP_DIR/latest.sql.gz"

# Apply retention policy
echo "Applying retention policy: keeping last $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "hse_edw_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
echo "Retention policy applied"

# List backups
echo ""
echo "Current backups:"
ls -lah "$BACKUP_DIR"/hse_edw_*.sql.gz 2>/dev/null || echo "No backups found"
