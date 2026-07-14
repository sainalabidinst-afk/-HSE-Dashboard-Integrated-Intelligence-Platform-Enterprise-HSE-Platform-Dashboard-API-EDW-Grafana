# HSE Backend — Agent Instructions

## Project Overview

Enterprise HSE (Health, Safety, Environment) Platform backend.  
FastAPI + SQLAlchemy + PostgreSQL EDW.  
Standards: SMKP Minerba · ISO 45001 · ISO 14001 · SMK3

---

## Architecture

```
backend/
├── app/
│   ├── main.py              ← FastAPI app entry point
│   ├── config.py            ← Pydantic Settings (loads from .env)
│   ├── database.py          ← SQLAlchemy engine + session
│   ├── models/
│   │   ├── hse_models.py    ← Core EDW models (dim + fact tables)
│   │   ├── audit.py         ← Audit, evidence, CAR, audit_trail models
│   │   └── alert.py         ← Alert rules, alerts, notification_logs models
│   ├── schemas/
│   │   └── __init__.py      ← Pydantic schemas (request/response DTOs)
│   ├── repositories/
│   │   ├── __init__.py      ← BaseRepository, DashboardRepository, AuthRepository, AlertRepository
│   │   └── audit.py         ← AuditRepository, EvidenceRepository
│   ├── services/
│   │   └── __init__.py      ← Business logic: DashboardService, AuthService, AuditService, AlertService, ReportingService, DataQualityService
│   ├── controllers/
│   │   └── __init__.py      ← FastAPI routers (all routes registered here)
│   ├── utils/
│   │   ├── security.py      ← Password hashing, JWT create/decode
│   │   ├── rbac.py          ← RBAC helpers: authenticate_user, get_current_user, require_permission
│   │   └── grafana.py       ← Grafana Live + Provisioning helpers
│   └── middleware/           ← Custom middleware
├── sql/
│   └── hse_edw_setup.sql    ← Full PostgreSQL schema (dim + fact + security + audit + alert tables)
├── alembic/                 ← DB migration history
├── requirements.txt         ← Python dependencies
├── Dockerfile               ← Production Docker image
├── docker-compose.yml       ← Multi-service stack
├── .env.example             ← Environment template
└── AGENTS.md                ← THIS FILE
```

---

## Code Conventions

### Python Style

- **PEP 8** compliance, 4-space indentation
- Type hints on all function signatures
- Docstrings on all public methods (Google style)
- No comments unless explaining non-obvious logic
- Use `from __future__ import annotations` where needed

### Naming

| Element | Convention | Example |
|---|---|---|
| Python files | `snake_case` | `audit_service.py` |
| Classes | `PascalCase` | `AuditService` |
| Functions/methods | `snake_case` | `get_audit_plans()` |
| Database tables | `snake_case` with `hse.` schema | `hse.audit_plans` |
| SQL columns | `snake_case` | `audit_status` |
| API routes | kebab-case in path | `/api/audit/plans` |
| Enums | `PascalCase` values | `AuditStatus.PLANNED` |

### Model Conventions

- All models inherit from `Base` (from `app.database`)
- Use `__tablename__` and `__table_args__ = {"schema": "hse"}`
- Primary keys: snake_case with `_id` suffix
- Foreign keys: `{table_singular}_id` pattern
- Timestamps: `created_at`, `updated_at` on all tables
- Soft deletes: use `is_active` boolean, never `DELETE`

### Repository Pattern

```python
class AuditRepository(BaseRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_audit_plans(self, site_id: str = None) -> List[Dict]:
        query = self.db.query(AuditPlan)
        if site_id and site_id != "all":
            query = query.filter(AuditPlan.site_id == site_id)
        results = query.all()
        return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in results]
```

- Return `List[Dict]` from repository (serialize SQLAlchemy models to dicts)
- Use `self.db` (Session) for all queries
- Use `__table__.columns` for dict serialization

### Service Layer

- Orchestrates repositories and business rules
- Returns Pydantic models or plain dicts
- No SQL queries — delegates to repositories

### Controller (Routes)

- All routes in `app/controllers/__init__.py`
- Use `APIRouter` per domain: `auth_router`, `dashboard_router`, `audit_router`, `alert_router`, `report_router`, `data_router`
- Register routers: `router.include_router(auth_router)`
- Always use `Depends(get_current_user)` for protected routes
- Use `Depends(require_permission("module:action"))` for permission checks
- Use `Query()` for optional filter parameters
- Use `ResponseModel` in route signature for auto-documentation

### RBAC Decorators

```python
from app.utils.rbac import get_current_user, require_permission

# Public (auth) route
@auth_router.post("/login")

# Any authenticated user
async def get_my_info(current_user: Dict = Depends(get_current_user)):

# Specific permission required
async def create_audit(current_user: Dict = Depends(require_permission("audit:create"))):
```

### Schemas (Pydantic)

- All schemas in `app/schemas/__init__.py`
- Use `model_config = ConfigDict(from_attributes=True)` for ORM models
- Create* schemas for request bodies
- *Response schemas for responses
- Use `Field(..., description="...")` for API docs

---

## Database

### Running Migrations

```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Manual SQL Changes

Add new tables to `sql/hse_edw_setup.sql` and also add models to `app/models/`.

### Adding New Models

1. Add model class in `app/models/<domain>.py`
2. Add SQL to `sql/hse_edw_setup.sql`
3. Import in repositories that need it
4. Create schemas in `app/schemas/__init__.py`
5. Add repository methods in `app/repositories/<domain>.py`
6. Add service methods in `app/services/__init__.py`
7. Add controller routes in `app/controllers/__init__.py`
8. Register router

---

## API Design

### URL Pattern

```
/api/auth/...          Authentication & RBAC
/api/dashboard/...     Dashboard aggregations
/api/audit/...         Audit management
/api/alerts/...        Alert rules & alerts
/api/reports/...       Report generation & export
/api/data/...          Data quality & validation
/api/admin/...         System administration
```

### Response Format

Success:
```json
{
  "key": "value",
  "items": [...]
}
```

Error:
```json
{
  "error": "Error Type",
  "detail": "Human readable message"
}
```

### Status Codes

| Code | Use |
|---|---|
| 200 | Success (GET, PUT) |
| 201 | Created (POST) |
| 400 | Bad request / validation error |
| 401 | Unauthenticated |
| 403 | Forbidden (insufficient permissions) |
| 404 | Resource not found |
| 422 | Validation error |
| 429 | Rate limited |
| 500 | Server error |

---

## Testing

```bash
# Run tests
cd backend
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Test Users (seeded in DB)

| Email | Password | Role |
|---|---|---|
| super.admin@company.com | Welcome123! | Super Admin |
| hse.director@company.com | Welcome123! | HSE Director |
| site.manager.alpha@company.com | Welcome123! | Site Manager |
| hse.manager@company.com | Welcome123! | HSE Manager |
| auditor.external@company.com | Welcome123! | Auditor |

---

## Docker

### Build

```bash
cd backend
docker compose build
```

### Start

```bash
# All services
docker compose up -d

# With profiles
docker compose --profile monitoring --profile tools up -d
```

### Logs

```bash
docker compose logs -f api
docker compose logs -f postgres
```

---

## Key Files Reference

| File | Purpose |
|---|---|
| `backend/app/main.py` | FastAPI app, middleware, routes |
| `backend/app/config.py` | Environment settings |
| `backend/app/database.py` | DB connection, session |
| `backend/app/models/` | SQLAlchemy ORM models |
| `backend/app/schemas/__init__.py` | Pydantic DTOs |
| `backend/app/repositories/` | Data access layer |
| `backend/app/services/__init__.py` | Business logic |
| `backend/app/controllers/__init__.py` | API routes |
| `backend/app/utils/rbac.py` | Authentication & RBAC |
| `backend/app/utils/security.py` | Password hashing, JWT |
| `sql/hse_edw_setup.sql` | Full PostgreSQL schema |
| `backend/docker-compose.yml` | Container stack |
| `backend/.env` | Environment variables (gitignored) |

---

## Adding a New Module (Example: Incident)

1. **Model**: Add `class Incident(Base)` in `app/models/hse_models.py`
2. **SQL**: Add `CREATE TABLE hse.incidents (...)` in `sql/hse_edw_setup.sql`
3. **Schema**: Add `class IncidentCreate(BaseModel)` in `app/schemas/__init__.py`
4. **Repository**: Add `get_incidents()` in `app/repositories/__init__.py` or new file
5. **Service**: Add `get_incidents()` in `app/services/__init__.py`
6. **Controller**: Add routes in `app/controllers/__init__.py`
7. **Register**: `router.include_router(incident_router)`
8. **Test**: Run `pytest` and test via `/api/docs`

---

*End of AGENTS.md*
