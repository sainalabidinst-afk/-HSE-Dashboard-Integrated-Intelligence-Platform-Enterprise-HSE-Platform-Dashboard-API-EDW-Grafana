# PostgreSQL Backup Script for HSE Enterprise Platform
# Performs full database backup with compression and retention

param(
    [string]$BackupDir = "./backups",
    [string]$PostgresHost = "localhost",
    [int]$PostgresPort = 5432,
    [string]$PostgresDb = "hse_edw",
    [string]$PostgresUser = "postgres",
    [int]$RetentionDays = 30
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = Join-Path $BackupDir "hse_edw_$timestamp.sql.gz"

# Read password from secrets file if available
$secretPath = Join-Path $PSScriptRoot "secrets\postgres_password.txt"
if (Test-Path $secretPath) {
    $postgresPassword = Get-Content $secretPath -Raw
} else {
    $postgresPassword = Read-Host "Enter PostgreSQL password" -AsSecureString
    $postgresPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($postgresPassword))
}

# Create backup directory if it doesn't exist
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

# Set PGPASSWORD environment variable
$env:PGPASSWORD = $postgresPassword

Write-Host "Starting backup of $PostgresDb..." -ForegroundColor Cyan

# Perform backup using pg_dump
$dumpCmd = "pg_dump -h $PostgresHost -p $PostgresPort -U $PostgresUser -d $PostgresDb --format=plain --no-owner --no-acl --schema=hse"
$dumpOutput = & cmd /c $dumpCmd 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: pg_dump failed" -ForegroundColor Red
    Write-Host $dumpOutput
    exit 1
}

# Compress and save
$dumpOutput | gzip > $backupFile

# Clear password from environment
$env:PGPASSWORD = $null

# Verify backup
if (Test-Path $backupFile) {
    $backupSize = (Get-Item $backupFile).Length / 1MB
    Write-Host "Backup completed successfully: $backupFile ($([math]::Round($backupSize, 2)) MB)" -ForegroundColor Green
} else {
    Write-Host "ERROR: Backup file not created" -ForegroundColor Red
    exit 1
}

# Create latest symlink (copy since Windows doesn't have symlinks by default)
$latestFile = Join-Path $BackupDir "latest.sql.gz"
Copy-Item $backupFile $latestFile -Force

# Apply retention policy
Write-Host "Applying retention policy: keeping last $RetentionDays days..."
$cutoffDate = (Get-Date).AddDays(-$RetentionDays)
Get-ChildItem $BackupDir -Filter "hse_edw_*.sql.gz" | Where-Object { $_.LastWriteTime -lt $cutoffDate } | Remove-Item -Force
Write-Host "Retention policy applied"

# List backups
Write-Host ""
Write-Host "Current backups:"
Get-ChildItem $BackupDir -Filter "hse_edw_*.sql.gz" | Format-Table Name, Length, LastWriteTime
