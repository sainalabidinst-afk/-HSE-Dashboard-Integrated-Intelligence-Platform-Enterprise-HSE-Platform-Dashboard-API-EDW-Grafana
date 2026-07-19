# Enterprise HSE Dashboard Platform

**Version:** 2.1  
**Status:** In Progress  
**Audit Score:** 72/100  

Comprehensive Health, Safety, and Environment (HSE) management platform for mining, construction, and oil & gas operations.

---

## North Star

Build an HSE Dashboard Platform that helps HSE teams manage daily operations:
- Monitoring KPI HSE
- Incident Management
- Hazard Management
- PTW Management
- Inspection
- Audit
- Training
- Environmental Monitoring
- Reporting
- AI Assistant for HSE data

---

## What This Is

This is an **HSE application**, not:
- Enterprise Framework
- Low Code Platform
- AI Operating System
- Governance Platform
- ERP
- HRIS
- Project Management System

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI 0.104, Python 3.11 |
| Database | PostgreSQL 15 + pgvector |
| ORM | SQLAlchemy 2.0 |
| Cache/Broker | Redis 7 |
| Task Queue | Celery 5.3 |
| Auth | JWT (python-jose) + bcrypt |
| AI | OpenAI embeddings + RAG |
| Observability | OpenTelemetry, Prometheus, Grafana, Loki, Tempo |
| Container | Docker Compose |
| Frontend | HTML/CSS/JS, Chart.js |

---

## Quick Start

### Prerequisites

- Docker Desktop 24+ and Docker Compose 2.20+
- Git 2.30+
- Python 3.10+ (for ETL/development)

### Start Core Services

```powershell
cd backend
cp .env.example .env
# Edit .env with your values

docker compose up -d postgres redis
docker compose up -d api
```

### Verify

```powershell
curl http://localhost:8000/health
```

### Access Points

| Service | URL | Default Credentials |
|---------|-----|---------------------|
| API | http://localhost:8000 | JWT token required |
| Swagger Docs | http://localhost:8000/api/docs | JWT token required |
| Grafana | http://localhost:3000 | admin / admin123 |
| PgAdmin | http://localhost:5050 | admin@hse.local / admin123 |

### Test Users

| Email | Password | Role |
|-------|----------|------|
| super.admin@company.com | Welcome123! | Super Admin |
| hse.director@company.com | Welcome123! | HSE Director |
| site.manager.alpha@company.com | Welcome123! | Site Manager |
| hse.manager@company.com | Welcome123! | HSE Manager |
| hse.officer.alpha@company.com | Welcome123! | HSE Officer |
| auditor.external@company.com | Welcome123! | Auditor |
| contractor.alpha@company.com | Welcome123! | Contractor |

---

## Project Structure

```
├── backend/                        # FastAPI backend
│   ├── app/
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── config.py               # Pydantic settings
│   │   ├── database.py             # SQLAlchemy engine + session
│   │   ├── models/                 # ORM models (SQLAlchemy)
│   │   │   ├── hse_models.py       # Core EDW models (dim + fact + security)
│   │   │   ├── operational.py      # Operational transaction tables
│   │   │   ├── audit.py            # Audit, evidence, CAR models
│   │   │   ├── alert.py            # Alert rules, alerts, notifications
│   │   │   └── ai.py               # AI documents, chunks, conversations
│   │   ├── schemas/__init__.py     # Pydantic DTOs (70+ schemas)
│   │   ├── repositories/           # Data access layer
│   │   │   ├── __init__.py         # BaseRepository, DashboardRepository, AuthRepository
│   │   │   ├── operational.py      # Generic CRUD for operational modules
│   │   │   ├── audit.py            # AuditRepository, EvidenceRepository
│   │   │   ├── alert.py            # AlertRepository
│   │   │   └── ai.py               # AIRepository
│   │   ├── services/               # Business logic
│   │   │   ├── __init__.py         # DashboardService, AuthService, AuditService, AlertService, ReportingService, DataQualityService, AIService
│   │   │   └── operational.py      # IncidentService, PTWService, TrainingService, etc.
│   │   ├── controllers/__init__.py # All API routes (1366 lines)
│   │   ├── utils/                  # Helpers
│   │   │   ├── security.py         # Password hashing, JWT
│   │   │   ├── rbac.py             # RBAC, permissions, site filtering
│   │   │   ├── observability.py    # Prometheus metrics, OpenTelemetry
│   │   │   ├── celery_app.py       # Celery configuration
│   │   │   ├── grafana.py          # Grafana Live integration
│   │   │   ├── powerbi.py          # Power BI integration
│   │   │   └── websocket.py        # WebSocket manager
│   │   └── middleware/__init__.py   # Custom middleware (placeholder)
│   ├── sql/
│   │   └── hse_edw_setup.sql       # Full PostgreSQL schema (1800+ lines)
│   ├── alembic/                    # Database migrations
│   ├── tests/                      # Test suite (pytest)
│   │   ├── conftest.py             # Shared fixtures
│   │   └── unit/
│   │       └── test_security.py    # Security unit tests
│   ├── scripts/                    # Utilities
│   │   ├── init_db.py              # Database initialization
│   │   ├── seed_rbac.py            # RBAC seed data
│   │   ├── backup.ps1              # PostgreSQL backup (Windows)
│   │   ├── restore.ps1             # PostgreSQL restore (Windows)
│   │   ├── verify-backup.sh        # Backup verification
│   │   └── setup-secrets.ps1       # Secret generation
│   ├── observability/              # Configs
│   │   ├── prometheus.yml
│   │   ├── otel-collector-config.yaml
│   │   ├── loki-config.yaml
│   │   └── tempo-config.yaml
│   ├── docker-compose.yml          # Multi-service stack
│   ├── Dockerfile                  # Production image
│   ├── requirements.txt            # Python dependencies
│   ├── .env.example                # Environment template
│   ├── Makefile                    # Dev commands
│   ├── pytest.ini                  # Test config
│   └── README.md                   # Backend-specific docs
├── dashboard/                      # Static frontend
│   ├── index.html                  # Main dashboard page
│   ├── js/
│   │   ├── api.js                  # Centralized API client
│   │   ├── auth.js                 # Authentication module
│   │   ├── app.js                  # Main application
│   │   ├── store.js                # State management
│   │   └── modules/                # Feature modules
│   │       ├── dashboard.js
│   │       ├── incident.js
│   │       ├── ptw.js
│   │       ├── training.js
│   │       ├── environmental.js
│   │       ├── equipment.js
│   │       ├── contractor.js
│   │       ├── observation.js
│   │       ├── near-miss.js
│   │       └── hira.js
│   └── sites.geojson               # Site location data
├── sql/
│   └── hse_edw_setup.sql           # Full EDW schema
├── scripts/
│   ├── generate_dummy_hse.py       # Sample data generator
│   └── etl_pipeline.py             # ETL pipeline with validation
├── dummy_data/                     # Sample CSV datasets
├── HOW_TO_RUN.md                   # Deployment guide
├── STEP4_AUTH_RBAC.md              # RBAC implementation details
├── PRD_Technical_HSE_Dashboard.md  # Product requirements
├── HSE_Dashboard_Design_Specification.md  # UI/UX specifications
├── PowerBI_Template_Skeleton.md    # Power BI integration guide
├── Grafana_HSE_Realtime.json       # Grafana dashboard template
├── .github/workflows/ci.yml        # CI/CD pipeline
└── README.md                       # This file
```

---

## Key Features

### Operational Modules
- **Incident Management** — Reporting, investigation, workflow, CAPA
- **PTW (Permit to Work)** — Creation, approval, activation, closure
- **Training Management** — Records, certification, expiry tracking
- **Environmental Monitoring** — Readings, thresholds, exceedance alerts
- **Equipment Management** — Inspections, certification, compliance
- **Contractor Management** — Registration, evaluation, performance
- **Safety Observations (BBS)** — Safe/unsafe observations, near misses
- **HIRA/JSA** — Risk assessments, hazard identification

### Intelligence & Governance
- **AI Safety Assistant** — RAG-based Q&A with pgvector
- **RBAC** — Granular permissions with site/department scoping
- **Audit Trail** — Complete change tracking with evidence management
- **Alert Engine** — Rule-based alerts with email/SMS/Telegram
- **Reporting** — Executive, operational, compliance reports
- **Observability** — OpenTelemetry, Prometheus, Grafana, Loki, Tempo

### Enterprise Integration Ready
- SAP ERP (OData/REST)
- HRIS (LDAP/REST)
- SCADA/OPC-UA
- IoT Gateway (MQTT)
- Active Directory
- Email/SMS gateways
- Power BI

---

## Database Schema

The platform uses a star schema EDW with 40+ tables:

### Dimension Tables (11)
`dim_datetime`, `dim_site`, `dim_department`, `dim_employee`, `dim_contractor`, `dim_equipment`, `dim_incident`, `dim_ptw`, `dim_environmental`, `dim_training`, `dim_hazard`

### Fact Tables (1)
`fact_hse` — Central fact table with daily HSE metrics

### Security Tables (6)
`security_users`, `security_roles`, `security_permissions`, `security_role_permission`, `security_user_role`, `security_sessions`, `security_login_history`

### Audit Tables (5)
`audit_plans`, `audit_findings`, `evidence`, `audit_trail`, `corrective_actions`

### Alert Tables (3)
`alert_rules`, `alerts`, `notification_logs`

### AI Tables (4)
`ai_documents`, `ai_document_chunks`, `ai_conversations`, `ai_messages`

### Operational Tables
`operational_attachments`, `workflow_history`, `incident_reports`, `ptw_requests`, `training_records`, `safety_observations`, `equipment_inspections`, `hira_assessments`, `near_miss_reports`, `contractor_records`, `environmental_readings`, `workflow_statuses`

### Reference Tables (1)
`ref_env_threshold`

---

## API Endpoints

### Authentication
- `POST /api/auth/login` — Login with email/password
- `POST /api/auth/refresh` — Refresh access token
- `POST /api/auth/logout` — Logout current session
- `POST /api/auth/logout-all` — Logout all sessions
- `GET /api/auth/me` — Get current user info
- `GET /api/auth/permissions` — Get user permissions
- `GET /api/auth/menu` — Get dynamic menu

### Dashboard
- `GET /api/dashboard/summary` — Executive summary with KPI cards
- `GET /api/dashboard/incidents` — Incident analysis with trend
- `GET /api/dashboard/ptw` — PTW summary
- `GET /api/dashboard/training` — Training compliance summary
- `GET /api/dashboard/environmental` — Environmental monitoring summary
- `GET /api/dashboard/equipment` — Equipment compliance summary
- `GET /api/dashboard/contractor` — Contractor performance summary
- `GET /api/dashboard/alerts` — Active alerts

### Operational Modules
- `POST /api/operational/incidents` — Create incident
- `GET /api/operational/incidents` — List incidents
- `GET /api/operational/incidents/{id}` — Get incident detail
- `POST /api/operational/ptw` — Create PTW
- `GET /api/operational/ptw` — List PTW
- `POST /api/operational/training` — Create training record
- `GET /api/operational/training` — List training records
- `POST /api/operational/observations` — Create observation
- `GET /api/operational/observations` — List observations

### Audit & Compliance
- `GET /api/audit/plans` — List audit plans
- `POST /api/audit/plans` — Create audit plan
- `GET /api/audit/findings` — List audit findings
- `POST /api/audit/findings` — Create audit finding
- `POST /api/audit/evidence` — Upload evidence
- `GET /api/audit/trail` — Get audit trail

### Alerts
- `GET /api/alerts/rules` — List alert rules
- `POST /api/alerts/rules` — Create alert rule
- `GET /api/alerts/active` — List active alerts
- `POST /api/alerts/{id}/acknowledge` — Acknowledge alert

### AI Safety Assistant
- `POST /api/ai/chat` — Chat with AI assistant
- `POST /api/ai/documents` — Ingest document
- `GET /api/ai/documents` — List documents
- `GET /api/ai/knowledge/stats` — Knowledge base stats

### Administration
- `GET /health` — Health check
- `GET /ready` — Readiness check
- `GET /live` — Liveness check
- `POST /admin/refresh-materialized-views` — Refresh database views
- `GET /admin/data-quality` — Data quality report

---

## Authentication Flow

1. Client sends `POST /api/auth/login` with credentials
2. Server returns `access_token` (1 hour) + `refresh_token` (7 days)
3. Client includes `Authorization: Bearer {access_token}` header in subsequent requests
4. When access token expires, use `POST /api/auth/refresh` with refresh token
5. Server returns new access token

---

## Development

### Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### Run Tests

```bash
cd backend
pytest tests/ -v
```

### Code Quality

```bash
cd backend
ruff check .
black .
mypy .
```

### Make Commands

```bash
cd backend
make install    # Install dependencies
make test       # Run tests with coverage
make lint       # Run ruff linter
make typecheck  # Run mypy
make coverage   # Generate HTML coverage report
```

---

## Deployment

See `HOW_TO_RUN.md` for complete deployment guide including:
- Docker Compose setup
- Database initialization
- Secrets management (Docker secrets, Azure Key Vault)
- Backup & restore procedures
- Disaster recovery plan
- Production deployment checklist

### Quick Production Start

```powershell
cd backend
docker compose --profile monitoring --profile app up -d
```

---

## Governance

Governance artifacts (ADR, Decision Log, Traceability Matrix, etc.) are maintained in the `governance/` directory for teams that need them. They are not required for daily development.

| Package | Document | Audience |
|---------|----------|----------|
| Package 1 | Executive_Summary.md | Board, CIO, COO, HSE Director |
| Package 2 | Technical_Architecture_Audit.md | Solution Architect, Tech Lead |
| Package 2 | Architecture_Decision_Records.md | Solution Architect, Tech Lead |
| Package 3 | Security_Compliance_Assessment.md | Security, Compliance, Auditor |
| Package 4 | Delivery_Operations_Playbook.md | Project Manager, Operations |

---

## Audit Results

### Overall Scores

| Domain | Score | Status |
|--------|-------|--------|
| Technical Architecture | 85/100 | 🟡 Good |
| Security | 82/100 | 🟡 Good |
| Operations | 73/100 | 🟡 Good |
| Governance | 70/100 | 🟡 Good |
| Frontend/UX | 58/100 | 🔴 Needs Work |
| **Overall** | **72/100** | **🟡 Conditional Go** |

### Top Risks

| Risk | Score | Mitigation | Owner | Timeline |
|------|-------|------------|-------|----------|
| File upload path traversal | 9 | Sanitize paths | Backend Lead | Sprint 0 |
| JWT replay attacks | 9 | Add jti validation | Security Lead | Sprint 0 |
| Rate limiting not implemented | 8 | Redis-backed limiter | Backend Lead | Sprint 0 |
| Database single point of failure | 8 | PostgreSQL replication | DBA | Sprint 1 |
| No API versioning | 8 | Add `/v1/` prefix | Backend Lead | Sprint 0 |

---

## Roadmap

### Sprint 0 — Critical Security (Weeks 1-2)
- Sanitize file upload paths
- Add JWT jti validation
- Implement Redis rate limiting
- Add API versioning
- Runtime validation

### Sprint 1 — Core Stability (Weeks 3-5)
- Database partitioning
- Celery task implementation
- Repository cleanup
- Query optimization + caching
- Frontend build process
- PostgreSQL replication

### Sprint 2 — Enterprise Readiness (Weeks 6-8)
- CI/CD with SAST/DAST
- Blue-green deployment
- SLO/SLI implementation
- Secret rotation automation
- BCP/DR documentation

### Sprint 3 — AI & Advanced (Weeks 9-11)
- Prompt injection protection
- Remove mock embeddings
- Model/prompt registry
- SAP integration

### Sprint 4 — User Experience (Weeks 12-14)
- Accessibility audit
- Offline mode
- Dark mode
- Operator usability testing

---

## Compliance

| Standard | Coverage | Gap |
|----------|----------|-----|
| ISO 45001 | 91% | Incident investigation workflow |
| ISO 14001 | 88% | Environmental KPI automation |
| ISO 27001 | 84% | Security monitoring |
| SMKP Minerba | 86% | Contractor evaluation |
| OSHA | 82% | OSHA 300 recordkeeping |

---

## Contributing

See `backend/AGENTS.md` for development standards and conventions.

---

## License

Proprietary — PT Petrosea Tbk

---

## Support

- **Technical Issues:** Tech Lead
- **Security Issues:** Security Lead
- **Compliance Issues:** Compliance Officer
- **Governance:** Enterprise Architect

---

*Enterprise HSE Platform Governance Package v2.1 | Audit Score: 72/100 Conditional Go*
