# Governance Rules Catalog

**Version:** 2.1  
**Date:** 2026-07-18  
**Owner:** Enterprise Architect  
**Review Cycle:** Monthly  
**Status:** Active

---

## Purpose

This catalog defines the governance rules that must be followed by all contributors to the Enterprise HSE Platform. These rules ensure code quality, architectural consistency, security, and maintainability. They are enforced through code review, CI/CD automation, and runtime checks.

---

## Rule Format

Each rule includes:
- **Rule ID:** Unique identifier (GOV-XXX)
- **Rule:** The governance rule statement
- **Rationale:** Why this rule exists
- **Enforcement:** How the rule is enforced
- **Exception Process:** How to request an exception

---

## Governance Rules

### Architecture Rules

| Rule ID | Rule | Rationale | Enforcement | Exception Process |
|---------|------|-----------|-------------|-------------------|
| GOV-001 | Controllers MUST NOT access the database directly. All data access must go through repositories. | Ensures separation of concerns, enables testing, prevents SQL injection | CI + Code Review | ADR required |
| GOV-002 | Repositories MUST NOT import FastAPI or any API layer dependencies. | Maintains clean architecture layers | CI + Code Review | ADR required |
| GOV-003 | Services MUST NOT import controller or API layer code. | Maintains clean architecture layers | CI + Code Review | ADR required |
| GOV-004 | All API endpoints MUST have RBAC protection (except public endpoints like `/health`, `/docs`). | Prevents unauthorized access | CI + Code Review | Security Lead approval |
| GOV-005 | All database models MUST define foreign keys for all relationship columns. | Ensures referential integrity and query performance | CI + Migration Review | DBA approval |
| GOV-006 | All database schema changes MUST be managed via Alembic migrations. | Enables version control and rollback | CI + Migration Review | DBA approval |
| GOV-007 | All migrations MUST include a rollback strategy. | Enables safe deployment and rollback | CI + Migration Review | DBA approval |
| GOV-008 | No circular dependencies between modules (controllers → services → repositories → models). | Prevents tight coupling and testing difficulties | CI (architecture check) | ADR required |
| GOV-009 | All configuration MUST be loaded from environment variables or secrets, never hardcoded. | Enables 12-factor app, secure secret management | CI + Code Review | DevOps Lead approval |
| GOV-010 | All environment-specific values MUST be in `.env.example` with comments. | Ensures consistent configuration across environments | Code Review | Tech Lead approval |

### Security Rules

| Rule ID | Rule | Rationale | Enforcement | Exception Process |
|---------|------|-----------|-------------|-------------------|
| GOV-011 | All passwords MUST be hashed using bcrypt before storage. | Prevents credential theft | CI + Code Review | Security Lead approval |
| GOV-012 | JWT tokens MUST include `jti` claim for replay attack prevention. | Prevents token replay attacks | CI + Code Review | Security Lead approval |
| GOV-013 | All file uploads MUST be validated for path traversal and file type. | Prevents arbitrary file write and malware upload | CI + SAST | Security Lead approval |
| GOV-014 | Rate limiting MUST be implemented on all public endpoints. | Prevents DoS and brute-force attacks | CI + Integration Test | Security Lead approval |
| GOV-015 | All API responses MUST not expose sensitive data (passwords, secrets, internal errors). | Prevents information disclosure | CI + SAST | Security Lead approval |
| GOV-016 | Mock embeddings MUST NOT be used in production. | Prevents false confidence in AI search quality | CI + Runtime check | AI Lead + Security Lead approval |
| GOV-017 | All secrets MUST be managed via Docker secrets or Azure Key Vault. | Prevents secret leakage in version control | CI + Code Review | DevOps Lead approval |
| GOV-018 | CORS origins MUST be explicitly configured, not wildcard (`*`). | Prevents unauthorized cross-origin access | CI + Code Review | Security Lead approval |
| GOV-019 | All user input MUST be validated using Pydantic schemas. | Prevents injection attacks and data corruption | CI + Code Review | Tech Lead approval |
| GOV-020 | SQL queries MUST use parameterized queries or ORM; no string concatenation. | Prevents SQL injection | CI + SAST | Security Lead approval |

### Testing Rules

| Rule ID | Rule | Rationale | Enforcement | Exception Process |
|---------|------|-----------|-------------|-------------------|
| GOV-021 | All new code MUST have unit tests with ≥70% coverage. | Ensures code quality and prevents regressions | CI (coverage check) | Tech Lead approval |
| GOV-022 | All bug fixes MUST include a regression test. | Prevents bug recurrence | Code Review | Tech Lead approval |
| GOV-023 | All security-related code MUST have security tests. | Ensures security controls work | CI + Security Review | Security Lead approval |
| GOV-024 | All API endpoints MUST have integration tests. | Ensures end-to-end functionality | CI (integration tests) | Tech Lead approval |
| GOV-025 | Test data MUST be isolated from production data. | Prevents data corruption | Code Review | DBA approval |

### Code Quality Rules

| Rule ID | Rule | Rationale | Enforcement | Exception Process |
|---------|------|-----------|-------------|-------------------|
| GOV-026 | All code MUST pass linting (ruff) with no errors. | Ensures code style consistency | CI (ruff) | Tech Lead approval |
| GOV-027 | All code MUST pass type checking (mypy) with no errors. | Prevents type-related bugs | CI (mypy) | Tech Lead approval |
| GOV-028 | All functions MUST have type hints. | Improves code readability and catches bugs | CI (mypy) | Tech Lead approval |
| GOV-029 | All public functions MUST have docstrings. | Improves maintainability | Code Review | Tech Lead approval |
| GOV-030 | No `print()` statements in production code; use logging. | Ensures proper logging and monitoring | CI + Code Review | Tech Lead approval |

### Documentation Rules

| Rule ID | Rule | Rationale | Enforcement | Exception Process |
|---------|------|-----------|-------------|-------------------|
| GOV-031 | All ADRs MUST have status (Draft/Proposed/Accepted/Superseded/Deprecated/Rejected). | Enables decision tracking | Code Review | Enterprise Architect approval |
| GOV-032 | All ADRs MUST be indexed in `ADR_Index.md`. | Enables quick reference | CI + Code Review | Enterprise Architect approval |
| GOV-033 | All significant decisions MUST be logged in `Decision_Log.md`. | Enables decision history | Code Review | Enterprise Architect approval |
| GOV-034 | All business requirements MUST be traceable in `Traceability_Matrix.md`. | Ensures requirements coverage | Code Review | Enterprise Architect approval |
| GOV-035 | README MUST be updated when project structure changes. | Prevents documentation drift | Code Review | Tech Lead approval |

### Database Rules

| Rule ID | Rule | Rationale | Enforcement | Exception Process |
|---------|------|-----------|-------------|-------------------|
| GOV-036 | All database changes MUST be reviewed by DBA. | Prevents performance and data integrity issues | Code Review | DBA approval |
| GOV-037 | All tables MUST have appropriate indexes for query patterns. | Ensures query performance | CI (query plan review) | DBA approval |
| GOV-038 | All foreign keys MUST have appropriate indexes. | Ensures join performance | CI (migration review) | DBA approval |
| GOV-039 | No nullable columns without explicit justification. | Ensures data quality | Code Review | DBA approval |
| GOV-040 | All tables MUST have `created_at` and `updated_at` timestamps. | Enables audit trail and debugging | CI + Code Review | DBA approval |

### API Rules

| Rule ID | Rule | Rationale | Enforcement | Exception Process |
|---------|------|-----------|-------------|-------------------|
| GOV-041 | All API endpoints MUST be versioned (`/api/v1/`, `/api/v2/`, etc.). | Enables backward compatibility | CI + Code Review | Tech Lead approval |
| GOV-042 | All API responses MUST use consistent response format. | Improves client integration | CI + Integration Test | Tech Lead approval |
| GOV-043 | All API errors MUST return appropriate HTTP status codes. | Enables proper error handling | CI + Integration Test | Tech Lead approval |
| GOV-044 | All API endpoints MUST have OpenAPI documentation. | Enables API discoverability | CI (Swagger check) | Tech Lead approval |
| GOV-045 | All API endpoints MUST have request/response schemas defined. | Enables validation and documentation | CI + Code Review | Tech Lead approval |

---

## Rule Enforcement Mechanisms

### CI/CD Enforcement

| Mechanism | Rules Enforced | Tool |
|-----------|---------------|------|
| Linting | GOV-026 | ruff |
| Type Checking | GOV-027, GOV-028 | mypy |
| Coverage | GOV-021 | pytest-cov |
| Architecture Check | GOV-001, GOV-002, GOV-003, GOV-008 | Custom script |
| Migration Review | GOV-006, GOV-007, GOV-038 | Custom script |
| Security Scan | GOV-011, GOV-013, GOV-015, GOV-019, GOV-020 | bandit, semgrep |
| Mock Embedding Check | GOV-016 | Custom script |
| Secret Scan | GOV-017 | truffleHog, git-secrets |

### Code Review Enforcement

| Check | Rules Enforced |
|-------|---------------|
| Architecture compliance | GOV-001, GOV-002, GOV-003, GOV-008 |
| Security review | GOV-004, GOV-011 through GOV-020 |
| Database review | GOV-005, GOV-036 through GOV-040 |
| API review | GOV-041 through GOV-045 |
| Documentation review | GOV-031 through GOV-035 |
| Test review | GOV-021 through GOV-025 |

### Runtime Enforcement

| Check | Rules Enforced |
|-------|---------------|
| Mock embedding disabled | GOV-016 |
| CORS configuration | GOV-018 |
| Rate limiting | GOV-014 |

---

## Exception Process

### When to Request an Exception

Request an exception when:
- The rule cannot be followed due to technical constraints
- The rule conflicts with a higher-priority requirement
- The exception is temporary and has a clear timeline

### How to Request an Exception

1. Create an ADR documenting the exception
2. Specify the rule being excepted
3. Provide justification and impact analysis
4. Specify the exception duration (max 6 months)
5. Include a mitigation plan
6. Get approval from relevant stakeholders:
   - Architecture exceptions → Enterprise Architect
   - Security exceptions → Security Lead
   - Database exceptions → DBA
   - Code quality exceptions → Tech Lead

### Exception Tracking

All exceptions are tracked in the `Decision_Log.md` with:
- Exception ID
- Rule ID
- Justification
- Expiration date
- Owner

---

## Compliance Dashboard

| Category | Total Rules | Enforced by CI | Enforced by Review | Enforced at Runtime |
|----------|-------------|----------------|-------------------|---------------------|
| Architecture | 10 | 4 | 10 | 0 |
| Security | 10 | 5 | 10 | 2 |
| Testing | 5 | 2 | 5 | 0 |
| Code Quality | 5 | 2 | 5 | 0 |
| Documentation | 5 | 0 | 5 | 0 |
| Database | 5 | 1 | 5 | 0 |
| API | 5 | 2 | 5 | 0 |
| **Total** | **45** | **16** | **45** | **2** |

---

## Rule Lifecycle

```
Proposed → Active → Deprecated → Retired
```

### Proposed
- Under discussion
- Not yet enforced
- Feedback welcome

### Active
- Approved and enforced
- Must be followed by all contributors
- Monitored for compliance

### Deprecated
- No longer recommended
- Still enforced for backward compatibility
- Migration path provided

### Retired
- No longer enforced
- Removed from catalog

---

## Related Documents

- `ADR_Index.md` — Architecture Decision Records index
- `Architecture_Decision_Records.md` — Full ADR details
- `Decision_Log.md` — Day-to-day project decisions
- `Architecture_Principles_Catalog.md` — Architecture principles
- `Technology_Radar.md` — Technology choices

---

*Document End*
