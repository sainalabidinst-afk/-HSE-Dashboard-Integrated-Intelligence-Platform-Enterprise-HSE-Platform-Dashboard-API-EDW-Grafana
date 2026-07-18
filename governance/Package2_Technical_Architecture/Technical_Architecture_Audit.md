# Enterprise HSE Platform — Technical Architecture Audit

**Document:** Technical Architecture Audit (Domains 1-20 + 28)  
**Version:** 2.1  
**Date:** 2026-07-18  
**Audience:** Solution Architect, Tech Lead, Backend, Frontend, DevOps  
**Classification:** Internal Use — Technical

---

## TABLE OF CONTENTS

1. [Domain 1: Database Architecture](#domain-1-database-architecture)
2. [Domain 2: API Design](#domain-2-api-design)
3. [Domain 3: Code Quality](#domain-3-code-quality)
4. [Domain 4: Repository Layer](#domain-4-repository-layer)
5. [Domain 5: Dependency Direction](#domain-5-dependency-direction)
6. [Domain 6: AI Assistant](#domain-6-ai-assistant)
7. [Domain 7: RBAC](#domain-7-rbac)
8. [Domain 8: Background Worker](#domain-8-background-worker)
9. [Domain 9: Docker](#domain-9-docker)
10. [Domain 10: Logging](#domain-10-logging)
11. [Domain 11: Configuration](#domain-11-configuration)
12. [Domain 12: Secret Rotation](#domain-12-secret-rotation)
13. [Domain 13: Performance](#domain-13-performance)
14. [Domain 14: Scalability](#domain-14-scalability)
15. [Domain 15: Availability](#domain-15-availability)
16. [Domain 16: Security (OWASP)](#domain-16-security-owasp)
17. [Domain 17: Frontend](#domain-17-frontend)
18. [Domain 18: UX](#domain-18-ux)
19. [Domain 19: Observability](#domain-19-observability)
20. [Domain 20: Production Readiness](#domain-20-production-readiness)
21. [Domain 28: Enterprise Architecture Governance & Standards](#domain-28-enterprise-architecture-governance--standards)
22. [Architecture Decision Records](#architecture-decision-records)
23. [Architecture Views](#architecture-views)

---

## DOMAIN 1: DATABASE ARCHITECTURE

**Score: 87/100**

### Schema Design
- **Star Schema EDW:** 9 dimension tables + 1 fact table (`fact_hse`)
- **Operational Tables:** 13 transaction tables with soft-delete pattern
- **Security Tables:** 7 RBAC tables with hierarchical roles
- **AI Layer:** 5 tables for knowledge base (documents, chunks, conversations)
- **Alert System:** 3 tables (rules, alerts, notification logs)
- **Audit Trail:** 3 tables (audit_plans, audit_findings, evidence, audit_trail, corrective_actions)

### Normalization
- ✅ Dimension tables: 3NF
- ✅ Fact table: Star schema
- ✅ Operational tables: 3NF with soft-delete pattern (`is_deleted`, `deleted_at`, `deleted_by`)
- ✅ Timestamp consistency: `created_at`, `updated_at` on all tables

### Indexing Strategy
- 38 indexes defined across all tables
- Composite indexes on high-frequency filters: `(date_key, site_key)`, `(site_id, ptw_status)`
- Partial indexes for filtered queries: `WHERE env_exceeded = TRUE`
- IVFFlat index for vector embeddings: `USING ivfflat (embedding vector_cosine_ops)`

### Constraints
- ✅ CHECK constraints on enum-like columns
- ✅ UNIQUE constraints: `uq_daily_metric(date_key, site_key, dept_key, metric_type)`
- ✅ NOT NULL constraints on critical columns
- ✅ Foreign keys with referential integrity

### Critical Findings
1. **Missing FK:** `fact_hse.hazard_key` → `dim_hazard.hazard_id` not defined
2. **No partitioning:** `fact_hse` will grow unbounded
3. **Mixed PK strategies:** SERIAL, VARCHAR, UUID across tables
4. **No cascade on dimension FKs:** Deleting from dimension tables orphanes fact records

### Recommendations
1. Add FK constraint on `hazard_key`
2. Implement range partitioning by `date_key` (monthly)
3. Standardize PK strategy to UUID
4. Add `ON DELETE SET NULL` on dimension FKs
5. Implement data retention policy (archive after 2 years)

---

## DOMAIN 2: API DESIGN

**Score: 78/100**

### REST Consistency
- Base path: `/api/*`
- Domain routers: `/auth`, `/dashboard`, `/audit`, `/alerts`, `/reports`, `/data`, `/admin`, `/ai`, `/operational`
- HTTP methods used correctly

### Issues
1. **No API versioning:** Missing `/v1/` prefix
2. **Inconsistent pluralization:** `/audit/plans` vs `/alerts/{id}/acknowledge`
3. **No response envelope:** No `{"data": ..., "meta": {...}}` wrapper
4. **No cursor-based pagination:** Offset pagination causes performance issues
5. **Verb-based actions:** `/acknowledge`, `/resolve` in paths

### HTTP Status Codes
- 200, 201, 400, 401, 403, 404, 422, 429, 500 used appropriately
- Generic 500 handler returns details in DEBUG mode

### Recommendations
1. Add `/v1/` prefix to all routes
2. Standardize response envelope
3. Implement cursor pagination
4. Replace verb paths with action endpoints

---

## DOMAIN 3: CODE QUALITY

**Score: 82/100**

### Strengths
- PEP 8 compliant with 4-space indentation
- Type hints on all public functions
- Clear layer separation (controllers → services → repositories)
- Docstrings present on major components

### Issues
1. **Large files:** `controllers/__init__.py` (1332+ lines), `services/__init__.py` (749+ lines), `schemas/__init__.py` (1088 lines)
2. **Duplicate enum handling:** `hasattr(x, 'value')` pattern repeated 20+ times
3. **Magic strings:** Permission strings scattered throughout
4. **Inline imports:** Inside route handlers
5. **No CI linting:** No evidence of ruff/flake8/mypy in CI pipeline

### Recommendations
1. Split large files by domain
2. Create `enum_value()` helper utility
3. Centralize permissions in `app/constants/permissions.py`
4. Move all imports to module top
5. Add ruff, mypy, black to CI pipeline

---

## DOMAIN 4: REPOSITORY LAYER

**Score: 90/100**

### Architecture Compliance
- Repositories return `List[Dict]` or domain models ✓
- No SQL queries in service layer ✓
- BaseRepository pattern with common operations ✓
- Session management via FastAPI dependency injection ✓

### Issues
1. Raw SQL in controllers (`db.execute("SELECT COUNT(*) FROM hse.fact_hse")`)
2. No query logging for debugging
3. No repository unit tests

### Recommendations
1. Move raw SQL to repository methods
2. Add SQL query logging in development
3. Add repository test coverage

---

## DOMAIN 5: DEPENDENCY DIRECTION

**Score: 95/100**

### Layer Dependencies
```
Controllers → Services → Repositories → Database
   ↓             ↓            ↓
Schemas       Models      Utils (leaf)
```

- No circular imports ✓
- Utils are leaf dependencies ✓
- Clean separation of concerns ✓

### Minor Issue
- Services import models directly (acceptable but could be tighter)

---

## DOMAIN 6: AI ASSISTANT

**Score: 74/100**

### Architecture
- RAG-based Q&A with pgvector ✓
- Document chunking with embeddings ✓
- Conversation memory ✓
- IVFFlat index for vector search ✓

### Security & Governance Gaps
1. No prompt injection detection
2. No confidence threshold enforcement
3. Mock embeddings fallback (returns meaningless vectors)
4. No token budget or context window management
5. No cost tracking for API calls
6. No AI audit trail for safety review
7. RBAC too permissive (`system:config` for document management)

### Recommendations
1. Add prompt injection filtering
2. Enforce minimum confidence threshold (70%)
3. Remove mock embeddings — fail hard on API unavailability
4. Implement token counting and limits
5. Add AI usage logging per user/role

---

## DOMAIN 7: RBAC

**Score: 92/100**

### Permission Model
- Granular module:action permissions (`incident:create`, `audit:view`) ✓
- Role hierarchy with `parent_role_id` ✓
- Site/department scoping ✓
- Session management with expiry ✓
- Login history with IP/user-agent ✓
- Account lockout after failed attempts ✓
- Password expiry and forced change ✓

### Gaps
1. AI endpoints use `get_current_user` instead of `require_permission`
2. No automated scan for unprotected routes
3. Site filtering must be enforced in repositories, not just controllers
4. No prevention of role escalation by users

### Recommendations
1. Add RBAC to all AI endpoints
2. Implement permission audit scanner
3. Enforce site filtering at repository level
4. Add role assignment validation

---

## DOMAIN 8: BACKGROUND WORKER

**Score: 65/100**

### Current State
- Celery configured with Redis broker ✓
- Basic task definitions exist ✓
- Time limits configured (5min hard, 4min soft)

### Critical Gaps
1. No retry policy
2. No dead letter queue
3. No queue routing/priority separation
4. No task idempotency design
5. No concurrency limits configured
6. Placeholder tasks (`pass` statements)

### Recommendations
1. Configure retry: `autoretry_for=(Exception,), max_retries=3, retry_backoff=True`
2. Add DLQ: `hse-dead-letter` queue
3. Route tasks: `alerts`, `reports`, `ai` queues
4. Implement idempotency keys
5. Set worker concurrency: `--concurrency=4`

---

## DOMAIN 9: DOCKER

**Score: 88/100**

### Image Security
- `python:3.11-slim` base image ✓
- Non-root user (`hseuser`) ✓
- Layer caching (requirements before source) ✓
- Healthcheck on API ✓

### Issues
1. Single-stage build (no multi-stage)
2. No read-only root filesystem
3. No security options (`no-new-privileges`, `cap-drop`)
4. No resource limits (CPU/memory)
5. No volume encryption

### Recommendations
1. Add multi-stage build
2. Add `security_opt: [no-new-privileges: true]`
3. Set `read_only: true` with tmpfs mounts
4. Add `deploy.resources.limits`
5. Encrypt sensitive volumes

---

## DOMAIN 10: LOGGING

**Score: 75/100**

### Current State
- `python-json-logger` for structured logs ✓
- Request timing middleware ✓
- Health check endpoints ✓

### Gaps
1. No security event logger
2. No separate audit log channel
3. No log aggregation (Fluentd/Logstash)
4. No log rotation configuration
5. Risk of PII in debug logs

### Recommendations
1. Add `SecurityLogger` for auth events
2. Add `AuditLogger` for data access
3. Configure Loki agent for log aggregation
4. Set Docker log max-size/max-file
5. Add PII redaction middleware

---

## DOMAIN 11: CONFIGURATION

**Score: 85/100**

### Strengths
- Pydantic Settings with type safety ✓
- `.env.example` comprehensive ✓
- Secrets precedence (Docker > Azure > env) ✓

### Gaps
1. No environment-specific configs
2. No startup validation for critical config
3. Feature flags defined but no management UI

### Recommendations
1. Add environment-specific config files
2. Add startup validation with explicit error messages
3. Add feature flag service with UI

---

## DOMAIN 12: SECRET ROTATION

**Score: 70/100**

### Current State
- Multiple secret sources supported ✓
- Secrets masked in logs ✓
- `setup-secrets.ps1` script exists ✓

### Gaps
1. No automated rotation schedule
2. No expiry tracking or alerts
3. No revocation runbook
4. No key versioning

### Recommendations
1. Implement 90-day rotation schedule
2. Add expiry alerts (30 days before)
3. Document revocation procedure
4. Track secret versions in Azure Key Vault

---

## DOMAIN 13: PERFORMANCE

**Score: 60/100**

### Current State
- SQLAlchemy connection pooling configured ✓
- GZip compression middleware ✓
- In-memory rate limiting (development only) ✓

### Gaps
1. No query profiling or slow query logging
2. No caching strategy (Redis configured but unused)
3. N+1 query risk in list endpoints
4. Synchronous large report generation
5. No CDN for static assets

### Recommendations
1. Enable `log_min_duration_statement` in PostgreSQL
2. Implement Redis caching for dashboard summaries (TTL 60s)
3. Optimize queries with `joinedload`/`selectinload`
4. Stream large exports (CSV/JSON) instead of buffering
5. Add CDN for dashboard static assets

---

## DOMAIN 14: SCALABILITY

**Score: 68/100**

### Current State
- Stateless API design ✓
- Worker separation (Celery) ✓
- Docker Compose profiles for scaling ✓

### Gaps
1. PostgreSQL single instance (no replication)
2. Redis single instance (no Sentinel/cluster)
3. No read replicas for reporting queries
4. Hardcoded worker count (`--workers 4`)

### Recommendations
1. Add PostgreSQL streaming replication
2. Add Redis Sentinel for HA
3. Route read queries to replicas
4. Make worker count configurable via env var

---

## DOMAIN 15: AVAILABILITY

**Score: 72/100**

### Current State
- Health checks: `/health`, `/ready`, `/live` ✓
- Container restart policy (`unless-stopped`) ✓
- Daily automated backups ✓
- RTO/RPO defined (4h/24h) ✓

### Gaps
1. No automatic failover for PostgreSQL/Redis
2. No load balancer for API
3. No blue-green deployment
4. No chaos testing

### Recommendations
1. Add Patroni for PostgreSQL HA
2. Add Redis Sentinel
3. Add Nginx/cloud load balancer
4. Implement blue-green deployment

---

## DOMAIN 16: SECURITY (OWASP TOP 10)

**Score: 80/100**

| OWASP Category | Status | Notes |
|----------------|--------|-------|
| A01: Broken Access Control | 🟡 | RBAC exists but needs enforcement in repositories |
| A02: Cryptographic Failures | 🟢 | JWT with HS256, secrets properly managed |
| A03: Injection | 🟢 | SQLAlchemy ORM prevents SQL injection |
| A04: Insecure Design | 🟡 | No rate limiting implementation, no API versioning |
| A05: Security Misconfiguration | 🟡 | CORS wildcard in dev, debug mode risk |
| A06: Vulnerable Components | 🟡 | No dependency scanning in CI |
| A07: Auth Failures | 🟢 | JWT, refresh tokens, account lockout implemented |
| A08: Data Integrity | 🟡 | No JWT jti validation, no code signing |
| A09: Logging Failures | 🟡 | Security events not logged separately |
| A10: SSRF | 🟡 | No SSRF protection on outbound requests |

### Critical Findings
1. File upload path traversal risk (`file_path` parameter not sanitized)
2. JWT replay attacks possible (no jti/nonce)
3. Rate limiting defined but not implemented (in-memory only)
4. CORS wildcard in development

### Recommendations
1. Sanitize file paths (whitelist directories)
2. Add jti to JWT and validate against blacklist
3. Implement Redis-backed rate limiting
4. Tighten CORS origins for production

---

## DOMAIN 17: FRONTEND

**Score: 65/100**

### Current State
- Static HTML/CSS/JS dashboard ✓
- Responsive design with CSS Grid ✓
- Chart.js for visualizations ✓

### Gaps
1. No build tool (no bundling/minification)
2. No accessibility (ARIA, keyboard nav)
3. No dark mode
4. Vanilla JS state management (no framework)
5. No error boundary handling
6. No loading skeletons

### Recommendations
1. Add Vite for build process
2. Implement WCAG 2.1 AA accessibility
3. Add dark mode toggle
4. Consider React/Vue for complex state
5. Add error boundaries and loading states

---

## DOMAIN 18: UX

**Score: 55/100**

### Current State
- Mobile responsive ✓
- Indonesian language localization ✓
- Tab-based navigation ✓

### Gaps
1. No offline mode (service worker)
2. No confirmation dialogs for destructive actions
3. No color-blind safety verification
4. No 3-click rule validation
5. No touch target size verification

### Recommendations
1. Add service worker for offline caching
2. Add confirmation modals for delete/cancel
3. Test and adjust for color-blind users
4. Conduct field operator usability testing

---

## DOMAIN 19: OBSERVABILITY

**Score: 85/100**

### Current State
- OpenTelemetry instrumentation (FastAPI, Celery, SQLAlchemy) ✓
- Prometheus metrics endpoint ✓
- Grafana dashboards auto-provisioned ✓
- Loki + Tempo for logs/traces ✓

### Gaps
1. No SLO/SLI definitions
2. No Prometheus alert rules
3. No incident integration (PagerDuty/OpsGenie)

### Recommendations
1. Define SLOs: API latency P95 < 200ms, availability > 99.9%
2. Configure AlertManager rules
3. Add PagerDuty integration for on-call

---

## DOMAIN 20: PRODUCTION READINESS

**Score: 72/100**

### Current State
- Automated daily backups ✓
- Backup verification script ✓
- Disaster recovery procedures documented ✓
- RTO/RPO defined ✓

### Gaps
1. No blue-green deployment
2. No zero-downtime migrations
3. No detailed runbooks
4. No chaos testing

### Recommendations
1. Implement blue-green deployment with Docker Compose
2. Use `CONCURRENTLY` for index creation
3. Create incident response runbooks
4. Add chaos testing (kill containers, simulate failures)

---

## DOMAIN 28: ENTERPRISE ARCHITECTURE GOVERNANCE & STANDARDS

**Score: 70/100**

### 28.1 Architecture Principles

| Principle | Description | Rationale | Applies To |
|-----------|-------------|-----------|------------|
| API First | All capabilities exposed as APIs | Enables integration, scalability | All services |
| Security by Design | Security requirements in every phase | Reduces vulnerability surface | All components |
| Event Driven | Async communication via events | Loose coupling, resilience | Integration layer |
| Immutable Infrastructure | Containers are immutable | Reproducibility, reliability | Deployment |
| Least Privilege | Minimal permissions by default | Reduces blast radius | RBAC, infrastructure |
| Domain Driven Design | Bounded contexts per domain | Maintains modularity | Code organization |
| Observability by Default | Metrics, logs, traces built-in | Fast troubleshooting | All services |
| Data as a Product | Data owned by domain teams | Quality, accountability | Data architecture |

### 28.2 Technology Radar

| Technology | Status | Domain | Adoption Target | Notes |
|------------|--------|--------|----------------|-------|
| FastAPI | **Adopt** | Backend | Current | Core API framework |
| PostgreSQL | **Adopt** | Database | Current | Primary data store |
| SQLAlchemy | **Adopt** | ORM | Current | Database abstraction |
| Redis | **Adopt** | Cache/Broker | Current | Caching + Celery broker |
| Celery | **Trial** | Background Jobs | 6 months | Alert/report processing |
| Docker Compose | **Adopt** | Deployment | Current | Container orchestration |
| OpenTelemetry | **Adopt** | Observability | Current | Tracing + metrics |
| Grafana | **Adopt** | Monitoring | Current | Dashboard + alerting |
| pgvector | **Trial** | AI/Vector | 6 months | Embedding storage |
| Kafka | **Assess** | Event Streaming | 12 months | High-volume event ingestion |
| Kubernetes | **Assess** | Orchestration | 12 months | Multi-service scaling |
| Elasticsearch | **Hold** | Search | Future | Full-text search needs evaluation |
| MongoDB | **Hold** | Database | Future | No current use case |

### 28.3 Architecture Decision Governance

**Decision Ownership:**
- **Solution Architect:** Final authority on architecture decisions
- **Tech Lead:** Implementation-level decisions
- **Security Lead:** Security-related decisions
- **Enterprise Architect:** Cross-domain decisions

**Review Cadence:**
- Monthly Architecture Review Board (ARB)
- Quarterly technology refresh
- Ad-hoc for security incidents

**Decision Template:**
- Title, Date, Status (Proposed/Accepted/Rejected/Superseded)
- Context, Decision, Rationale
- Alternatives considered
- Consequences
- Related ADRs

### 28.4 Reference Architecture

**Enterprise HSE Reference Model:**
```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
│  Dashboard (Chart.js) + Mobile App + Power BI + Grafana     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     API GATEWAY LAYER                       │
│  Nginx / Cloud LB + Rate Limiting + Auth + Routing         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                         │
│  FastAPI (Auth, Dashboard, Audit, Alerts, Reports, AI)     │
│  Celery Workers (Alerts, Reports, AI Tasks)                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    INTEGRATION LAYER                        │
│  REST API + MQTT + OPC-UA + LDAP + SMTP + Webhooks         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     DATA LAYER                              │
│  PostgreSQL EDW (hse schema) + Redis Cache + Vector DB     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 INFRASTRUCTURE LAYER                        │
│  Docker / Kubernetes + Monitoring + Backup + DR             │
└─────────────────────────────────────────────────────────────┘
```

### 28.5 Technical Debt Register

| Debt ID | Description | Impact | Effort | Owner | Target Sprint | Score |
|---------|-------------|--------|--------|-------|---------------|-------|
| TD-001 | Large controller files (1332 lines) | Maintainability | 5 days | Backend Lead | Sprint 1 | 8 |
| TD-002 | No API versioning | Breaking changes | 1 day | Backend Lead | Sprint 0 | 9 |
| TD-003 | Mock embeddings in code | Production risk | 1 day | AI Lead | Sprint 3 | 9 |
| TD-004 | No database partitioning | Performance | 5 days | DBA | Sprint 1 | 8 |
| TD-005 | No CI/CD pipeline | Delivery speed | 5 days | DevOps | Sprint 2 | 8 |
| TD-006 | Frontend no build process | Performance | 3 days | Frontend Lead | Sprint 1 | 7 |
| TD-007 | No Redis caching | Performance | 3 days | Backend Lead | Sprint 1 | 7 |
| TD-008 | Missing FK on hazard_key | Data integrity | 1 day | DBA | Sprint 0 | 9 |

**Debt Scoring:** Impact (1-5) × Effort (1-5) = Priority (higher = address first)

### 28.6 Architecture Review Process

**Review Triggers:**
- New module or domain added
- Major technology change
- Security-impacting change
- Performance-critical path modification
- Cross-domain integration

**Review Checklist:**
- [ ] Aligns with architecture principles
- [ ] Follows approved technology stack (Technology Radar)
- [ ] Includes observability (metrics, logs, traces)
- [ ] Includes security review (OWASP, threat model)
- [ ] Includes data governance (classification, lineage)
- [ ] Includes performance implications
- [ ] Includes cost implications
- [ ] Includes documentation plan

**Approval Workflow:**
1. Author submits ADR + design doc
2. Peer review (2 reviewers)
3. Security review (if applicable)
4. ARB approval (monthly meeting)
5. Implementation + documentation

### 28.7 Lifecycle Management

**Technology Lifecycle Stages:**
- **Emerging:** Under evaluation (e.g., Kafka)
- **Growing:** Approved for new projects (e.g., Celery)
- **Mature:** Standard for production (e.g., FastAPI, PostgreSQL)
- **Sunset:** Deprecated, migration planned

**Sunset Policy:**
- 12-month notice before deprecation
- Migration guide provided
- Support window: 6 months after deprecation
- Technical debt ticket created for migration

---

## ARCHITECTURE DECISION RECORDS

### ADR-001: API Versioning Strategy
**Decision:** Add `/v1/` prefix to all API routes  
**Rationale:** Enables backward compatibility for future breaking changes  
**Alternatives:** Header-based versioning, URL parameter versioning  
**Consequences:** Requires client updates, but provides clean migration path

### ADR-002: Database Partitioning Strategy
**Decision:** Range partition `fact_hse` by `date_key` (monthly partitions)  
**Rationale:** Time-series data naturally partitions by date, improves query performance  
**Alternatives:** No partitioning, hash partitioning by site  
**Consequences:** Requires partition management logic, but enables data archival

### ADR-003: Caching Strategy
**Decision:** Redis caching for dashboard summaries with 60s TTL  
**Rationale:** Dashboard reads are frequent and data changes infrequently  
**Alternatives:** No caching, CDN caching, application-level caching  
**Consequences:** Stale data up to 60s, but 10x performance improvement

### ADR-004: AI Embedding Strategy
**Decision:** Use OpenAI `text-embedding-3-small` with development-only deterministic mock fallback  
**Rationale:** Production-quality embeddings with safe development fallback  
**Alternatives:** Open-source models (Llama, BERT), no fallback  
**Consequences:** OpenAI API cost, but best-in-class search quality  

**Production Policy:** Mock embeddings (`_mock_embedding`) **MUST be disabled** in production environments. The application **must fail** with a clear error message if the OpenAI API is unavailable. Mock embeddings are strictly for development and testing environments only, controlled by the `ENABLE_MOCK_EMBEDDINGS` feature flag (default: `false`).

### ADR-005: Background Task Processing
**Decision:** Celery with Redis broker, separate queues per domain  
**Rationale:** Proven reliability, supports retries, monitoring, and scaling  
**Alternatives:** Dramatiq, RQ, in-process async  
**Consequences:** Additional infrastructure (Redis), but robust task processing

---

## ARCHITECTURE VIEWS

See `11_Architecture/` folder for detailed specifications:
- **Executive:** Context diagram, business capability map, value stream
- **Solution:** C4 model (Context, Container, Component, Code)
- **Infrastructure:** Deployment diagram, network zones, trust boundaries
- **Security:** STRIDE threat model, attack surface map
- **Data:** ERD, data flow diagram, lineage diagram
- **Integration:** Integration landscape, event flow, sequence diagrams
- **Operations:** Backup/recovery flow, incident response flow

---

## DOCUMENT REFERENCES

- [Package 1: Executive Governance](../Package1_Executive_Governance/Executive_Summary.md)
- [Package 3: Security & Compliance](../Package3_Security_Compliance/)
- [Package 4: Delivery & Operations](../Package4_Delivery_Operations/)
- [Architecture Views](../Package2_Technical_Architecture/11_Architecture/)

---

*Document End*
