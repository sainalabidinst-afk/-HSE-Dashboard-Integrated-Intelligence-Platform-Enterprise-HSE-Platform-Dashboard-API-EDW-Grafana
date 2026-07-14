# HSE Enterprise Backend API

FastAPI-based REST API for the HSE Dashboard Platform.

## Features

- **Clean Architecture**: Controller → Service → Repository → Database
- **JWT Authentication**: Access + Refresh tokens with Role-Based Access Control
- **PostgreSQL EDW**: Direct connection to HSE Enterprise Data Warehouse
- **CORS Enabled**: Ready for web dashboard consumption
- **Rate Limiting**: Built-in request throttling
- **Health Checks**: `/health`, `/ready`, `/live` endpoints
- **Auto Documentation**: Swagger UI at `/api/docs`, ReDoc at `/api/redoc`
- **Structured Logging**: JSON-formatted logs with process time tracking
- **Docker Ready**: Production-ready containerization

## Quick Start

### Using Docker Compose (Recommended)

```bash
cd backend
cp .env.example .env
docker-compose up -d postgres redis
docker-compose up -d api
```

The API will be available at: `http://localhost:8000`

### Manual Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database credentials
uvicorn app.main:app --reload
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login with email/password
- `POST /api/auth/refresh` - Refresh access token

### Dashboard
- `GET /api/dashboard/summary` - Executive summary with KPI cards
- `GET /api/dashboard/incidents` - Incident analysis with trend
- `GET /api/dashboard/ptw` - PTW summary
- `GET /api/dashboard/training` - Training compliance summary
- `GET /api/dashboard/environmental` - Environmental monitoring summary
- `GET /api/dashboard/equipment` - Equipment compliance summary
- `GET /api/dashboard/contractor` - Contractor performance summary
- `GET /api/dashboard/alerts` - Active alerts

### Administration
- `GET /health` - Health check
- `GET /ready` - Readiness check
- `GET /live` - Liveness check
- `POST /admin/refresh-materialized-views` - Refresh database views
- `GET /admin/data-quality` - Data quality report

## Request Examples

### Get Executive Summary

```bash
curl "http://localhost:8000/api/dashboard/summary?site_id=SITE-A&period_days=30"
```

Response:
```json
{
  "kpis": [
    {
      "label": "LTIFR",
      "value": 0.42,
      "status": "green",
      "subtext": "Target: < 1.0"
    },
    {
      "label": "TRIR",
      "value": 1.08,
      "status": "green",
      "subtext": "Target: < 2.0"
    }
  ],
  "generated_at": "2025-07-13T10:00:00",
  "period_days": 30,
  "site_id": "SITE-A"
}
```

### Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=hse.manager@company.com&password=password"
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user_role": "HSEManager",
  "site_access": ["SITE-A", "SITE-B", "SITE-C"]
}
```

## Authentication Flow

1. Client sends `POST /api/auth/login` with credentials
2. Server returns `access_token` (1 hour) + `refresh_token` (7 days)
3. Client includes `Authorization: Bearer {access_token}` header in subsequent requests
4. When access token expires, use `POST /api/auth/refresh` with refresh token
5. Server returns new access token

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing key (CHANGE IN PRODUCTION!)
- `REDIS_URL` - Redis for caching and Celery
- `CORS_ORIGINS` - Allowed origins for CORS
- `ALERT_EMAIL_ENABLED` - Enable email notifications

## Architecture

```
backend/
├── app/
│   ├── main.py                   # FastAPI app entry point
│   ├── config.py                 # Configuration management
│   ├── database.py               # Database connection
│   ├── models/                   # SQLAlchemy ORM models
│   ├── schemas/                  # Pydantic request/response schemas
│   ├── repositories/             # Data access layer (queries)
│   ├── services/                 # Business logic layer
│   ├── controllers/              # API route handlers
│   ├── middleware/               # Custom middleware
│   └── utils/                    # Helpers: security, KPI, alerts
├── alembic/                      # Database migrations
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Integration

This API is consumed by:
- **Dashboard HTML** (`dashboard/index.html` via fetch)
- **Grafana** (via PostgreSQL data source or API)
- **Power BI** (via DirectQuery or import)
- **Mobile App** (REST API calls)
- **Custom Integrations** (any HTTP client)

## Next Steps

1. ✅ Backend API created
2. 🔄 Update dashboard to call `/api/dashboard/*` endpoints
3. 🔄 Implement proper password hashing in auth
4. 🔄 Add more detailed error handling
5. 🔄 Add API versioning (v1, v2)

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | FastAPI |
| Database | PostgreSQL 15 |
| ORM | SQLAlchemy 2.0 |
| Auth | JWT (python-jose) |
| Cache | Redis |
| Task Queue | Celery |
| Container | Docker |
