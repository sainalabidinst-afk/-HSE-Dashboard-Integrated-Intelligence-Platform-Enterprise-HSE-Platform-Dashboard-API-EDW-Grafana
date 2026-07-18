# Enterprise HSE Platform

**Version:** 2.1  
**Status:** Conditional Go — Sprint 0 Pending  
**Audit:** Enterprise Governance & Production Readiness Assessment v2.1  
**Last Updated:** 2026-07-18

Comprehensive Health, Safety, and Environment (HSE) management platform for mining, construction, and oil & gas operations. Built with FastAPI, PostgreSQL, and Docker, with enterprise-grade governance, compliance, and observability.

---

## Current Status

| Aspect | Status |
|--------|--------|
| Architecture | ✅ Complete — Enterprise HSE Reference Model |
| Backend API | ✅ Functional — FastAPI + SQLAlchemy |
| Database | ✅ Complete — PostgreSQL EDW with 40+ tables |
| Security | 🟡 Partial — RBAC complete, hardening pending |
| Frontend | 🟡 Functional — Static dashboard, build pending |
| AI Assistant | 🟡 Functional — RAG with pgvector |
| Observability | ✅ Configured — OpenTelemetry, Prometheus, Grafana |
| Governance | ✅ Complete — 27-domain audit v2.1 |
| Production Readiness | 🟡 Conditional Go — Sprint 0-2 required |

**Overall Readiness:** 72/100 — Conditional Go  
**Maturity Level:** CMMI Level 2 — Repeatable  
**Next Milestone:** Complete Sprint 0 (Critical Security) for Go-Live readiness

---

## Documentation

### Governance Package (v2.1)

The platform includes a comprehensive enterprise governance package organized by stakeholder:

```
governance/
├── README.md                                           # Governance package index
├── Package1_Executive_Governance/
│   └── Executive_Summary.md                            # Board/C-Level overview
├── Package2_Technical_Architecture/
│   ├── Technical_Architecture_Audit.md                 # 20 technical domains + Domain 28
│   ├── Architecture_Decision_Records.md                # ADRs 001-007
│   └── 11_Architecture/
│       ├── README.md                                   # Diagram rendering guide
│       ├── Executive/
│       │   └── context_diagram.puml                    # C4 Level 1
│       ├── Solution/
│       │   ├── container_diagram.puml                  # C4 Level 2
│       │   └── component_diagram.puml                  # C4 Level 3
│       ├── Infrastructure/
│       │   ├── deployment_diagram.puml                 # C4 Level 4
│       │   └── network_zones.puml                      # Trust boundaries
│       ├── Security/
│       │   ├── threat_model.puml                       # STRIDE analysis
│       │   └── trust_boundary.puml                     # Security zones
│       ├── Data/
│       │   ├── erd_diagram.puml                        # Entity relationships
│       │   ├── data_flow_diagram.md                    # Data flow diagrams
│       │   └── data_lineage.md                         # Lineage tracking
│       ├── Integration/
│       │   ├── integration_landscape.puml              # Integration matrix
│       │   └── sequence_diagram.puml                   # Integration flows
│       └── Operations/
│           └── operations_architecture.md              # BCP, DR, runbooks
├── Package3_Security_Compliance/
│   └── Security_Compliance_Assessment.md               # OWASP, ISO, SMKP, STRIDE
└── Package4_Delivery_Operations/
    └── Delivery_Operations_Playbook.md                 # Roadmap, BCP, cost, debt
```

### Core Documentation

| Document | Audience | Purpose |
|----------|----------|---------|
| `README.md` | All stakeholders | Project overview and quick start |
| `HOW_TO_RUN.md` | Engineering | Deployment and operations guide |
| `backend/README.md` | Backend developers | API documentation and examples |
| `HSE_Dashboard_Design_Specification.md` | Designers, Frontend | UI/UX specifications |
| `PRD_Technical_HSE_Dashboard.md` | Product, Business | Product requirements |
| `STEP4_AUTH_RBAC.md` | Security, Backend | RBAC implementation details |
| `PowerBI_Template_Skeleton.md` | Analytics, Reporting | Power BI integration guide |
| `backend/AGENTS.md` | AI Agents | Development standards and patterns |

---

## Project Structure

```
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py             # FastAPI app entry point
│   │   ├── config.py           # Pydantic settings
│   │   ├── database.py         # SQLAlchemy engine + session
│   │   ├── models/             # ORM models (SQLAlchemy)
│   │   ├── schemas/            # Pydantic DTOs
│   │   ├── repositories/       # Data access layer
│   │   ├── services/           # Business logic
│   │   ├── controllers/        # API routes
│   │   ├── utils/              # Security, RBAC, observability
│   │   └── middleware/         # Custom middleware
│   ├── sql/
│   │   └── hse_edw_setup.sql   # Full PostgreSQL schema
│   ├── alembic/                # Database migrations
│   ├── tests/                  # Test suite
│   ├── scripts/                # Backup, restore, seeding
│   ├── observability/          # Prometheus, Grafana, Loki, Tempo
│   ├── Dockerfile              # Production image
│   ├── docker-compose.yml      # Multi-service stack
│   ├── requirements.txt        # Python dependencies
│   └── .env.example            # Environment template
├── dashboard/                  # Static frontend dashboard
│   ├── index.html              # Main dashboard page
│   ├── js/                     # JavaScript modules
│   └── sites.geojson           # Site location data
├── dummy_data/                 # Sample data for testing
├── scripts/                    # ETL and data generation
├── sql/                        # Database schema
│   └── hse_edw_setup.sql       # Full EDW schema
├── governance/                 # Enterprise governance package
│   └── [4 packages]            # Executive, Technical, Security, Delivery
└── [root docs]                 # Project-level documentation
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

## Technology Stack

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
- Python 3.10+ (for development)
- Node.js 18+ (for frontend development)

### Start with Docker Compose

```bash
# Clone repository
git clone <repository-url>
cd HSE-Dashboard-Integrated-Intelligence-Platform

# Start core services
cd backend
cp .env.example .env
docker compose up -d postgres redis
docker compose up -d api

# Verify
curl http://localhost:8000/health
```

### Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| API | http://localhost:8000 | JWT token |
| Swagger Docs | http://localhost:8000/api/docs | JWT token |
| Grafana | http://localhost:3000 | admin / admin123 |
| PgAdmin | http://localhost:5050 | admin@hse.local / admin123 |

### Test Users

| Email | Password | Role |
|-------|----------|------|
| super.admin@company.com | Welcome123! | Super Admin |
| hse.director@company.com | Welcome123! | HSE Director |
| site.manager.alpha@company.com | Welcome123! | Site Manager |
| hse.manager@company.com | Welcome123! | HSE Manager |
| auditor.external@company.com | Welcome123! | Auditor |

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

## Governance & Compliance

### Compliance Coverage

| Standard | Coverage | Gap |
|----------|----------|-----|
| ISO 45001 | 91% | Incident investigation workflow |
| ISO 14001 | 88% | Environmental KPI automation |
| ISO 27001 | 84% | Security monitoring |
| SMKP Minerba | 86% | Contractor evaluation |
| OSHA | 82% | OSHA 300 recordkeeping |

### Maturity Assessment

**Current:** CMMI Level 2 — Repeatable  
**Target:** CMMI Level 3 — Defined (within 6 months)

---

## Contributing

See `backend/AGENTS.md` for development standards and conventions.

### Development Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### Running Tests

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
