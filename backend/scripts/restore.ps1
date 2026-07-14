# PostgreSQL Restore Script for HSE Enterprise Platform
# Restores database from a backup file

param(
    [string]$BackupFile = "",
    [string]$PostgresHost = "localhost",
    [int]$PostgresPort = 5432,
    [string]$PostgresDb = "hse_edw",
    [string]$PostgresUser = "postgres"
)

if (-not $BackupFile) {
    $BackupFile = Join-Path $PSScriptRoot "..\backups\latest.sql.gz"
}

if (-not (Test-Path $BackupFile)) {
    Write-Host "ERROR: Backup file not found: $BackupFile" -ForegroundColor Red
    Write-Host "Usage: .\restore.ps1 -BackupFile <path_to_backup.sql.gz>" -ForegroundColor Yellow
    exit 1
}

# Read password from secrets file if available
$secretPath = Join-Path $PSScriptRoot "secrets\postgres_password.txt"
if (Test-Path $secretPath) {
    $postgresPassword = Get-Content $secretPath -Raw
} else {
    $postgresPassword = Read-Host "Enter PostgreSQL password" -AsSecureString
    $postgresPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($postgresPassword))
}

$env:PGPASSWORD = $postgresPassword

Write-Host "WARNING: This will drop and recreate the database!" -ForegroundColor Red
$confirm = Read-Host "Are you sure you want to continue? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "Restore cancelled"
    exit 0
}

Write-Host "Starting restore from $BackupFile..." -ForegroundColor Cyan

# Drop existing connections
Write-Host "Terminating existing connections..."
psql -h $PostgresHost -p $PostgresPort -U $PostgresUser -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$PostgresDb' AND pid <> pg_backend_pid();" 2>&1 | Out-Null

# Drop and recreate database
Write-Host "Dropping and recreating database..."
psql -h $PostgresHost -p $PostgresPort -U $PostgresUser -d postgres -c "DROP DATABASE IF EXISTS $PostgresDb;" 2>&1 | Out-Null
psql -h $PostgresHost -p $PostgresPort -U $PostgresUser -d postgres -c "CREATE DATABASE $PostgresDb OWNER $PostgresUser;" 2>&1 | Out-Null

# Restore from backup
Write-Host "Restoring data..."
$stream = [System.IO.File]::OpenRead($BackupFile)
$gzipStream = New-Object System.IO.Compression.GZipStream($stream, [System.IO.Compression.CompressionMode]::Decompress)
$reader = New-Object System.IO.StreamReader($gzipStream)
$sqlContent = $reader.ReadToEnd()
$reader.Close()
$gzipStream.Close()
$stream.Close()

$sqlContent | psql -h $PostgresHost -p $PostgresPort -U $PostgresUser -d $PostgresDb

# Clear password
$env:PGPASSWORD = $null

Write-Host "Restore completed successfully from $BackupFile" -ForegroundColor Green
