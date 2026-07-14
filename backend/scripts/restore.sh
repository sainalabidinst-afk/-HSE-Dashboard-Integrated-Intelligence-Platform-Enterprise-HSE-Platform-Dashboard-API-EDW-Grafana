#!/bin/bash
set -euo pipefail

# PostgreSQL Restore Script for HSE Enterprise Platform
# Restores database from a backup file

BACKUP_DIR="${BACKUP_DIR:-./backups}"
POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_DB="${POSTGRES_DB:-hse_edw}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
BACKUP_FILE="${1:-$BACKUP_DIR/latest.sql.gz}"

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

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "ERROR: Backup file not found: $BACKUP_FILE" >&2
    echo "Usage: $0 <backup_file.sql.gz>" >&2
    exit 1
fi

echo "WARNING: This will drop and recreate the database!" >&2
read -p "Are you sure you want to continue? (yes/no): " -r
if [ "$REPLY" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

echo "Starting restore from $BACKUP_FILE..."

# Drop existing connections
psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$POSTGRES_DB' AND pid <> pg_backend_pid();"

# Drop and recreate database
psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d postgres -c "DROP DATABASE IF EXISTS $POSTGRES_DB;"
psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE $POSTGRES_DB OWNER $POSTGRES_USER;"

# Restore from backup
gunzip < "$BACKUP_FILE" | psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB"

# Unset password
unset PGPASSWORD

echo "Restore completed successfully from $BACKUP_FILE"
