# Setup Secrets for HSE Enterprise Platform
# This script generates secure random passwords and writes them to the secrets directory.
# Run this script once during initial setup.

param(
    [switch]$Force
)

$secretsDir = Join-Path $PSScriptRoot "secrets"

# Create secrets directory if it doesn't exist
if (-not (Test-Path $secretsDir)) {
    New-Item -ItemType Directory -Path $secretsDir -Force | Out-Null
    Write-Host "Created secrets directory: $secretsDir" -ForegroundColor Green
}

# Function to generate a random password
function New-Secret {
    param(
        [int]$Length = 32,
        [switch]$UrlSafe = $false
    )
    
    if ($UrlSafe) {
        $bytes = New-Object byte[] $Length
        [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
        return [System.Convert]::ToBase64String($bytes).TrimEnd('=').Replace('+', '-').Replace('/', '_')
    } else {
        $chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?"
        $password = -join ((1..$Length) | ForEach-Object { $chars[(Get-Random -Maximum $chars.Length)] })
        return $password
    }
}

# Define secrets to generate
$secrets = @{
    "postgres_password.txt" = { New-Secret -Length 32 }
    "secret_key.txt" = { New-Secret -Length 32 -UrlSafe }
    "smtp_password.txt" = { New-Secret -Length 24 }
    "grafana_password.txt" = { New-Secret -Length 16 }
    "pgadmin_password.txt" = { New-Secret -Length 16 }
    "influxdb_password.txt" = { New-Secret -Length 32 }
}

foreach ($secretFile in $secrets.Keys) {
    $secretPath = Join-Path $secretsDir $secretFile
    
    if ((Test-Path $secretPath) -and -not $Force) {
        Write-Host "Skipping $secretFile (already exists, use -Force to overwrite)" -ForegroundColor Yellow
        continue
    }
    
    $secretValue = & $secrets[$secretFile]
    Set-Content -Path $secretPath -Value $secretValue -NoNewline
    Write-Host "Generated $secretFile" -ForegroundColor Green
}

Write-Host ""
Write-Host "Secrets setup complete!" -ForegroundColor Cyan
Write-Host "Secrets directory: $secretsDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Update SMTP credentials in secrets/smtp_password.txt with your actual SMTP password"
Write-Host "2. Start the stack with: docker compose --profile monitoring --profile app up -d"
Write-Host "3. The application will automatically read secrets from /run/secrets/ in containers"
Write-Host ""
Write-Host "Security reminders:" -ForegroundColor Red
Write-Host "- Never commit the secrets/ directory to version control"
Write-Host "- Rotate secrets regularly (at least every 90 days)"
Write-Host "- Use Azure Key Vault for production deployments"
Write-Host "- Backup secrets securely (outside of version control)"
