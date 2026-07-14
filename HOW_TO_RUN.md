# HSE Dashboard — How to Run
## Complete Deployment Guide

**Version:** 1.0  
**Date:** 2026-07-14

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (All Services)](#quick-start-all-services)
3. [Step-by-Step Deployment](#step-by-step-deployment)
4. [Service URLs](#service-urls)
5. [Configuration](#configuration)
6. [Testing the Installation](#testing-the-installation)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Docker Desktop | 24+ | Container runtime |
| Docker Compose | 2.20+ | Multi-container orchestration |
| Git | 2.30+ | Source control |
| Python | 3.10+ | ETL scripts (optional) |
| Node.js | 18+ | Frontend development (optional) |

---

## Quick Start (All Services)

### 1. Clone and navigate

```powershell
cd "C:\Users\SAbidin\HSE Dashboard"
```

### 2. Create `.env` file

```powershell
# backend/.env
SECRET_KEY=your-super-secret-jwt-key-change-in-production
POSTGRES_PASSWORD=secure-postgres-password
GRAFANA_PASSWORD=admin123
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_FROM_EMAIL=hse-alerts@company.com
```

### 3. Start all services

```powershell
cd backend
docker compose --profile monitoring --profile tools up -d
```

### 4. Verify services are running

```powershell
docker compose ps
```

Expected output: all containers with `State: Running`.

---

## Step-by-Step Deployment

### Step 1: Start PostgreSQL

```powershell
cd backend
docker compose up -d postgres
```

Verify PostgreSQL is ready:
```powershell
docker exec -it hse-postgres pg_isready -U postgres
```

### Step 2: Initialize Database Schema

The schema is auto-initialized from `sql/hse_edw_setup.sql` on first startup.

Verify tables were created:
```powershell
docker exec -it hse-postgres psql -U postgres -d hse_edw -c "\dt hse.*"
```

Expected tables: `dim_site`, `dim_department`, `dim_employee`, `dim_equipment`, `dim_contractor`, `dim_incident`, `dim_ptw`, `dim_environmental`, `dim_training`, `fact_hse`, `security_users`, `security_roles`, `audit_plans`, `audit_findings`, `evidence`, `alerts`, `alert_rules`, `notification_logs`, `corrective_actions`, `audit_trail`.

### Step 3: Start Redis

```powershell
docker compose up -d redis
```

### Step 4: Start the FastAPI Backend

```powershell
docker compose up -d api
```

Check API health:
```powershell
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "timestamp": "2026-07-14T..."
}
```

### Step 5: Start Grafana (Real-time Monitoring)

```powershell
docker compose --profile monitoring up -d grafana
```

Access Grafana: http://localhost:3000  
Default login: `admin` / `admin123` (change on first login)

Import the dashboard:  
`Grafana_HSE_Realtime.json` is auto-provisioned at startup.

### Step 6: Start Optional Services

```powershell
# PgAdmin (Database management UI)
docker compose --profile tools up -d pgadmin

# InfluxDB (for environmental IoT data)
docker compose --profile iot up -d influxdb

# Celery worker (for background tasks: alert sending, report generation)
docker compose --profile worker up -d celery-worker celery-beat
```

---

## Service URLs

| Service | URL | Credentials |
|---|---|---|
| **FastAPI Backend** | http://localhost:8000 | JWT token required |
| **API Docs (Swagger)** | http://localhost:8000/api/docs | JWT token required |
| **Grafana** | http://localhost:3000 | admin / admin123 |
| **Prometheus** | http://localhost:9090 | No auth |
| **OTEL Collector** | http://localhost:4317 (gRPC) | No auth |
| **Loki** | http://localhost:3100 | No auth |
| **Tempo** | http://localhost:3200 | No auth |
| **PgAdmin** | http://localhost:5050 | admin@hse.local / admin123 |
| **PostgreSQL** | localhost:5432 | postgres / (from .env) |
| **Redis** | localhost:6379 | No auth (dev only) |
| **InfluxDB** | http://localhost:8086 | admin / (from .env) |

### Platform Health Dashboard

Access the Platform Health dashboard at: http://localhost:3000/d/hse-platform-health

Default dashboard: **HSE Platform Health**
- API Request Rate
- API Latency (P95, P99)
- API Error Rate
- Active Users
- Celery Task Duration
- Database Query Duration
- Alerts Generated
- ETL Job Duration
- JWT Issued Rate
- Failed Login Attempts
- API Availability SLI

### Running the Observability Stack

```powershell
# Start all services including observability
cd backend
docker compose --profile monitoring --profile app up -d

# Or start only observability stack
docker compose --profile monitoring up -d otel-collector prometheus grafana loki tempo
```

---

## Configuration

### Environment Variables

Create `backend/.env`:

```env
# Application
APP_NAME=HSE Enterprise Platform
APP_VERSION=1.0.0
DEBUG=false
SECRET_KEY=your-super-secret-jwt-key-min-32-chars-change-in-production

# Database
DATABASE_URL=postgresql://postgres:secure-postgres-password@postgres:5432/hse_edw
DATABASE_ECHO=false

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_ENABLED=true

# JWT
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]

# Alert Engine
ALERT_EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_FROM_EMAIL=hse-alerts@company.com

# Monitoring
GRAFANA_PASSWORD=admin123
INFLUXDB_PASSWORD=admin123
POSTGRES_PASSWORD=secure-postgres-password
PGADMIN_EMAIL=admin@hse.local
PGADMIN_PASSWORD=admin123
```

---

## Testing the Installation

### 1. Test Authentication

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=super.admin@company.com&password=Welcome123!"
```

### 2. Test Dashboard Summary

```bash
TOKEN="your-jwt-token-from-login"
curl "http://localhost:8000/api/dashboard/summary" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Test Dynamic Menu

```bash
curl "http://localhost:8000/api/auth/menu" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Test Audit Routes

```bash
curl "http://localhost:8000/api/audit/plans" \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Test Alerts

```bash
curl "http://localhost:8000/api/alerts/active" \
  -H "Authorization: Bearer $TOKEN"
```

### 6. Test Data Quality

```bash
curl "http://localhost:8000/api/data/quality" \
  -H "Authorization: Bearer $TOKEN"
```

### 7. Test Report Generation

```bash
curl -X POST "http://localhost:8000/api/reports/generate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"report_type":"executive","start_date":"2026-01-01","end_date":"2026-07-14","format":"csv"}'
```

### 8. Test Health Check

```bash
curl http://localhost:8000/health
```

---

## Secrets Management

### Overview

The platform supports three methods for managing secrets, in order of precedence:

1. **Docker Secrets** (recommended for production containers)
2. **Azure Key Vault** (recommended for Azure production deployments)
3. **Environment Variables** (development only)

### Method 1: Docker Secrets (Recommended for Production)

Docker secrets securely pass sensitive data to containers without exposing them in environment variables.

#### Setup

```powershell
cd backend

# Generate secure random secrets
python -c "import secrets; print(secrets.token_urlsafe(32))" > secrets/postgres_password.txt
python -c "import secrets; print(secrets.token_urlsafe(32))" > secrets/secret_key.txt
python -c "import secrets; print(secrets.token_urlsafe(16))" > secrets/grafana_password.txt
python -c "import secrets; print(secrets.token_urlsafe(16))" > secrets/pgadmin_password.txt

# Or use the setup script
.\scripts\setup-secrets.ps1

# Start services
docker compose --profile monitoring --profile app up -d
```

The application automatically reads secrets from `/run/secrets/<secret_name>` in containers.

**Important:** The `secrets/` directory is in `.gitignore`. Never commit secrets to version control.

### Method 2: Azure Key Vault (Azure Production)

For Azure deployments, secrets are fetched from Azure Key Vault at runtime.

```powershell
# Set the Key Vault URL
$env:AZURE_KEY_VAULT_URL = "https://your-vault.vault.azure.net/"

# The application will automatically fetch:
# - SECRET_KEY
# - DATABASE_URL
# - SMTP_PASSWORD
# - TELEGRAM_BOT_TOKEN
```

**Prerequisites:**
- Azure Key Vault created with secrets
- Managed Identity or Service Principal with `get` permission on secrets
- `azure-identity` and `azure-keyvault-secrets` packages installed

### Method 3: Environment Variables (Development)

For local development, use `.env` file:

```powershell
cd backend
copy .env.example .env
# Edit .env with your values
```

**Warning:** Never use `.env` in production. Use Docker secrets or Azure Key Vault instead.

### Secrets Reference

| Secret | Docker Secret File | Environment Variable | Purpose |
|---|---|---|---|
| PostgreSQL Password | `postgres_password.txt` | `POSTGRES_PASSWORD` | Database authentication |
| JWT Secret Key | `secret_key.txt` | `SECRET_KEY` | JWT token signing |
| SMTP Password | `smtp_password.txt` | `SMTP_PASSWORD` | Email alert sending |
| Grafana Password | `grafana_password.txt` | `GRAFANA_PASSWORD` | Grafana admin access |
| PgAdmin Password | `pgadmin_password.txt` | `PGADMIN_PASSWORD` | PgAdmin access |
| InfluxDB Password | `influxdb_password.txt` | `INFLUXDB_PASSWORD` | InfluxDB authentication |

### Secret Rotation

Rotate secrets regularly (recommended: every 90 days):

```powershell
# 1. Generate new secrets
.\scripts\setup-secrets.ps1 -Force

# 2. Restart services to pick up new secrets
docker compose restart api celery-worker celery-beat

# 3. Verify services are healthy
docker compose ps
```

---

## Backup & Disaster Recovery

### Automated Backups

The platform includes automated PostgreSQL backups with compression and retention.

#### Enable Automated Backups

```powershell
cd backend
docker compose --profile backup up -d postgres-backup
```

The backup service runs daily at 2:00 AM and stores compressed backups in the `./backups` directory.

#### Backup Configuration

| Setting | Default | Description |
|---|---|---|
| `BACKUP_DIR` | `./backups` | Backup storage directory |
| `BACKUP_RETENTION_DAYS` | `30` | Number of days to keep backups |
| `BACKUP_SCHEDULE` | `0 2 * * *` | Cron schedule (daily at 2 AM) |

#### Manual Backup

```powershell
# Using PowerShell script
cd backend
.\scripts\backup.ps1

# Using Docker
docker exec hse-postgres-backup /scripts/backup.sh

# Using pg_dump directly
docker exec hse-postgres pg_dump -U postgres hse_edw | gzip > backups/manual_backup.sql.gz
```

### Restore from Backup

#### Using PowerShell Script

```powershell
cd backend
.\scripts\restore.ps1 -BackupFile ./backups/hse_edw_20260101_020000.sql.gz
```

#### Using Bash Script

```bash
cd backend
bash scripts/restore.sh ./backups/hse_edw_20260101_020000.sql.gz
```

#### Using Docker

```powershell
# Restore from latest backup
docker exec -i hse-postgres-backup gunzip < /backups/latest.sql.gz | docker exec -i hse-postgres psql -U postgres -d hse_edw
```

### Backup Verification

Verify backup integrity before relying on it:

```powershell
cd backend
bash scripts/verify-backup.sh
```

The verification script:
1. Checks backup file integrity (gzip validation)
2. Counts tables in the backup
3. Tests restore to a temporary database
4. Verifies restored data
5. Cleans up test database

### Disaster Recovery Plan

#### RTO (Recovery Time Objective): 4 hours
#### RPO (Recovery Point Objective): 24 hours

#### Recovery Procedures

1. **Complete System Failure**
   ```powershell
   # 1. Restore database from latest backup
   cd backend
   .\scripts\restore.ps1 -BackupFile ./backups/latest.sql.gz

   # 2. Start services
   docker compose --profile monitoring --profile app up -d

   # 3. Verify health
   curl http://localhost:8000/health
   ```

2. **Database Corruption**
   ```powershell
   # 1. Stop API services
   docker compose stop api celery-worker celery-beat

   # 2. Restore database
   .\scripts\restore.ps1 -BackupFile ./backups/latest.sql.gz

   # 3. Start services
   docker compose start api celery-worker celery-beat
   ```

3. **Accidental Data Deletion**
   ```powershell
   # 1. Find backup before deletion
   ls ./backups/ | Sort-Object Descending | Select-Object -First 5

   # 2. Restore to temporary database
   .\scripts\restore.ps1 -BackupFile ./backups/hse_edw_20260101_020000.sql.gz

   # 3. Export and import specific data
   ```

### Backup Best Practices

1. **Test restores regularly** — Run `verify-backup.sh` weekly
2. **Store backups offsite** — Copy backups to Azure Blob Storage or S3
3. **Encrypt backups** — Use GPG or Azure Storage encryption
4. **Monitor backup jobs** — Check `/var/log/backup.log` in backup container
5. **Document retention policy** — Keep 30 days local, 1 year offsite

### Offsite Backup (Azure Blob Storage)

```powershell
# Upload latest backup to Azure Blob Storage
az storage blob upload `
  --account-name <storage-account> `
  --container-name hse-backups `
  --file ./backups/latest.sql.gz `
  --name "hse_edw_$(Get-Date -Format 'yyyyMMdd').sql.gz"
```

---

## Production Deployment

### Security Checklist

- [ ] Change `SECRET_KEY` to a strong random value (min 32 chars)
- [ ] Change `POSTGRES_PASSWORD` to a strong password
- [ ] Change `GRAFANA_PASSWORD` to a strong password
- [ ] Set `DEBUG=false` in production
- [ ] Configure `CORS_ORIGINS` to only allow trusted domains
- [ ] Enable HTTPS with valid SSL certificates (update `nginx.conf`)
- [ ] Configure SMTP for alert notifications
- [ ] Set up database backups (cron job)
- [ ] Enable PostgreSQL SSL connections
- [ ] Use Docker secrets for sensitive environment variables

### Production Docker Compose Override

Create `backend/docker-compose.prod.yml`:

```yaml
services:
  api:
    environment:
      - DEBUG=false
      - DATABASE_ECHO=false
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1'
          memory: 512M
  postgres:
    command: >
      postgres
      -c ssl=on
      -c ssl_cert_file=/etc/ssl/certs/server.crt
      -c ssl_key_file=/etc/ssl/private/server.key
```

Start production stack:
```powershell
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Troubleshooting

### Database connection refused

```powershell
# Check PostgreSQL is running
docker compose ps postgres

# Check PostgreSQL logs
docker logs hse-postgres

# Restart PostgreSQL
docker compose restart postgres
```

### Grafana dashboard not loading

```powershell
# Verify dashboard JSON is mounted
docker exec hse-grafana ls /etc/grafana/provisioning/dashboards/

# Restart Grafana
docker compose restart grafana

# Check Grafana logs
docker logs hse-grafana
```

### API returning 500 errors

```powershell
# Check API logs
docker logs hse-api

# Verify database is accessible from API container
docker exec hse-api curl -f http://localhost:8000/health

# Check environment variables
docker exec hse-api env | grep DATABASE_URL
```

### Celery worker not processing tasks

```powershell
# Check Celery logs
docker logs hse-celery

# Verify Redis connection
docker exec hse-celery redis-cli -h redis ping

# Restart worker
docker compose restart celery-worker
```

### Port already in use

```powershell
# Check what's using the port
netstat -ano | findstr "8000"

# Or use PowerShell
Get-NetTCPConnection -LocalPort 8000

# Stop conflicting service or change port in docker-compose.yml
```

---

## Volume Backups

### Backup PostgreSQL

```powershell
docker exec hse-postgres pg_dump -U postgres hse_edw > backup_$(Get-Date -Format "yyyyMMdd").sql
```

### Backup Grafana

```powershell
docker exec hse-grafana tar czf /tmp/grafana-backup.tar.gz /var/lib/grafana
docker cp hse-grafana:/tmp/grafana-backup.tar.gz ./backups/
```

---

## Stopping Services

```powershell
# Stop all services
docker compose down

# Stop and remove volumes (WARNING: deletes data)
docker compose down -v

# Stop specific service
docker compose stop api
```

---

## Support

- API Docs: http://localhost:8000/api/docs
- Grafana: http://localhost:3000
- PgAdmin: http://localhost:5050
- Review: `PRD_Technical_HSE_Dashboard.md`
- Database schema: `sql/hse_edw_setup.sql`

*Generated: 2026-07-14 | Version: 1.0*
