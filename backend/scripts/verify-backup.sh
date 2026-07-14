#!/bin/bash
set -euo pipefail

# Backup Verification Script
# Verifies backup integrity and tests restore process

BACKUP_DIR="${BACKUP_DIR:-./backups}"
POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_DB="${POSTGRES_DB:-hse_edw}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
TEST_DB="${POSTGRES_DB}_restore_test"

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

echo "=== Backup Verification ==="
echo ""

# Check if backups exist
if [ -z "$(ls -A $BACKUP_DIR/hse_edw_*.sql.gz 2>/dev/null)" ]; then
    echo "ERROR: No backups found in $BACKUP_DIR" >&2
    exit 1
fi

# Get latest backup
LATEST_BACKUP=$(ls -t $BACKUP_DIR/hse_edw_*.sql.gz | head -1)
echo "Testing latest backup: $LATEST_BACKUP"
echo ""

# Verify backup file
echo "1. Checking backup file integrity..."
if gunzip -t "$LATEST_BACKUP" 2>/dev/null; then
    echo "   ✓ Backup file is valid"
else
    echo "   ✗ Backup file is corrupted!" >&2
    exit 1
fi

# Count tables in backup
echo "2. Checking backup contents..."
TABLE_COUNT=$(gunzip < "$LATEST_BACKUP" | grep -c "^CREATE TABLE" || true)
echo "   ✓ Found $TABLE_COUNT tables in backup"

# Test restore to temporary database
echo "3. Testing restore to temporary database..."
psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d postgres -c "DROP DATABASE IF EXISTS $TEST_DB;" >/dev/null 2>&1
psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE $TEST_DB OWNER $POSTGRES_USER;" >/dev/null 2>&1

if gunzip < "$LATEST_BACKUP" | psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$TEST_DB" >/dev/null 2>&1; then
    echo "   ✓ Restore test successful"
else
    echo "   ✗ Restore test failed!" >&2
    exit 1
fi

# Verify restored data
echo "4. Verifying restored data..."
RESTORED_TABLES=$(psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$TEST_DB" -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'hse';")
echo "   ✓ Restored $RESTORED_TABLES tables"

# Cleanup test database
psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d postgres -c "DROP DATABASE $TEST_DB;" >/dev/null 2>&1

# Unset password
unset PGPASSWORD

echo ""
echo "=== Backup Verification Complete ==="
echo "✓ All checks passed"
echo ""
echo "Backup details:"
echo "  File: $LATEST_BACKUP"
echo "  Size: $(du -h "$LATEST_BACKUP" | cut -f1)"
echo "  Tables: $TABLE_COUNT"
echo "  Date: $(stat -c %y "$LATEST_BACKUP" 2>/dev/null || stat -f "%Sm" "$LATEST_BACKUP")"
