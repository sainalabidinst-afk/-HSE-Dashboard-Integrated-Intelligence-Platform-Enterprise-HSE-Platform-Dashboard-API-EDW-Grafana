# Decision Log

**Version:** 2.1  
**Date:** 2026-07-18  
**Owner:** Enterprise Architect  
**Review Cycle:** Monthly  
**Status:** Active

---

## Purpose

This Decision Log captures day-to-day project decisions that are significant but do not require a full Architecture Decision Record (ADR). While ADRs document permanent architecture decisions, this log tracks tactical and operational decisions that impact the project.

---

## Decision Format

Each decision entry includes:
- **Date:** When the decision was made
- **Decision:** What was decided
- **Reason:** Why the decision was made
- **Impact:** What is affected
- **Owner:** Who is responsible for the decision
- **Status:** Current status of the decision

---

## Decisions

### 2026-07-18: Resolve duplicate `security_user_role` table definition

**Decision:** Remove duplicate `CREATE TABLE hse.security_user_role` from `sql/hse_edw_setup.sql` line 301-314. The table is already defined correctly at line 450+ with proper schema.

**Reason:** Duplicate table definition causes schema conflict during database initialization. The first definition used `user_email` as PK, while the correct definition uses `user_role_id` as PK with proper foreign keys.

**Impact:** 
- Database initialization now succeeds without errors
- SQLAlchemy models align with actual database schema
- No migration required

**Owner:** Backend Lead

**Status:** Implemented

---

### 2026-07-18: Fix missing foreign key on `FactHSE.hazard_key`

**Decision:** Add `ForeignKey("hse.dim_hazard.hazard_id")` to `FactHSE.hazard_key` column in `backend/app/models/hse_models.py`.

**Reason:** The foreign key was missing, causing:
- ORM relationship not working
- Referential integrity not enforced at database level
- Query optimizer cannot use joins efficiently

**Impact:**
- Database referential integrity now enforced
- ORM relationships work correctly
- Query performance improved

**Owner:** Backend Lead

**Status:** Implemented

---

### 2026-07-18: Fix duplicate `__table_args__` in `SecurityUserRole` model

**Decision:** Remove duplicate `__table_args__` definition in `SecurityUserRole` class. Keep only the tuple version with `UniqueConstraint`.

**Reason:** SQLAlchemy does not allow duplicate `__table_args__` definitions. The class had both a dict and a tuple definition, causing the second to be ignored.

**Impact:**
- SQLAlchemy model now works correctly
- Unique constraint on `(user_id, role_id)` is properly enforced
- No migration required

**Owner:** Backend Lead

**Status:** Implemented

---

### 2026-07-18: Enforce fail-hard policy for AI embeddings

**Decision:** Update `AIService._generate_embedding()` to raise `RuntimeError` when OpenAI API is unavailable and `ENABLE_MOCK_EMBEDDINGS=false` (production default).

**Reason:** ADR-004 specifies production must fail-fast rather than silently using mock embeddings. Previous implementation silently fell back to mock embeddings on any error.

**Impact:**
- Production AI features fail clearly with error message
- Mock embeddings only used in development/testing
- Prevents false confidence in AI search quality

**Owner:** AI Lead, Security Lead

**Status:** Implemented

---

### 2026-07-18: Add `ENABLE_MOCK_EMBEDDINGS` environment variable

**Decision:** Add `ENABLE_MOCK_EMBEDDINGS` environment variable (default: `false`) to control mock embedding usage.

**Reason:** Provides explicit control over mock embedding behavior. Prevents accidental use of mock embeddings in production.

**Impact:**
- Clear configuration for development vs production
- CI can verify production uses real embeddings
- Documentation updated

**Owner:** AI Lead, DevOps Lead

**Status:** Implemented

---

### 2026-07-18: Update root README to reflect actual project state

**Decision:** Rewrite root `README.md` to accurately reflect:
- Current project structure and components
- Actual tech stack and versions
- Real audit scores and maturity level
- Complete feature list
- Governance package structure

**Reason:** Previous README was outdated and did not reflect the current state of the project. Caused confusion for new team members and stakeholders.

**Impact:**
- Single source of truth for project overview
- Reduces onboarding time
- Aligns documentation with implementation

**Owner:** Technical Writer, Enterprise Architect

**Status:** Implemented

---

### 2026-07-18: Create Architecture Principles Catalog

**Decision:** Create `Architecture_Principles_Catalog.md` with 15 governing principles for the platform.

**Reason:** Project needed explicit architecture principles to guide decision-making and ensure consistency across the codebase.

**Impact:**
- Clear guidelines for architecture decisions
- Reference for code reviews
- Foundation for architecture validation gates (future)

**Owner:** Enterprise Architect

**Status:** Implemented

---

### 2026-07-18: Create Technology Radar

**Decision:** Create `Technology_Radar.md` with Adopt/Trial/Assess/Hold quadrants for all technologies used in the platform.

**Reason:** Team needed a single reference for technology choices and their lifecycle status.

**Impact:**
- Consistent technology decisions across teams
- Clear roadmap for technology adoption
- Visibility into technology risks

**Owner:** Enterprise Architect, Tech Lead

**Status:** Implemented

---

### 2026-07-18: Create ADR Index

**Decision:** Create `ADR_Index.md` as a quick reference to all ADRs with status tracking.

**Reason:** ADRs were scattered in a single file without quick reference. Difficult to track which ADRs are accepted, proposed, or draft.

**Impact:**
- Quick reference for ADR status
- Easier governance review
- Better decision traceability

**Owner:** Enterprise Architect

**Status:** Implemented

---

## Decision Categories

| Category | Count | Examples |
|----------|-------|---------|
| **Database** | 3 | Schema fixes, foreign keys, partitioning |
| **Security** | 2 | Embedding policy, RBAC |
| **Documentation** | 3 | README updates, ADR index, principles |
| **Architecture** | 2 | Principles catalog, technology radar |
| **AI/ML** | 2 | Embedding strategy, mock policy |
| **Operations** | 1 | Configuration management |

---

## Decision Trends

- **2026-07-18:** 11 decisions (project stabilization and governance foundation)
- Most decisions are **implementation fixes** (schema, models, configuration)
- Increasing trend toward **governance artifacts** (ADR, principles, radar)

---

## Decision Velocity

| Week | Decisions | Theme |
|------|-----------|-------|
| Week 1 | 11 | Foundation & Stabilization |
| Week 2 | TBD | TBD |
| Week 3 | TBD | TBD |
| Week 4 | TBD | TBD |

---

## Pending Decisions

| Decision | Owner | Due Date | Status |
|----------|-------|----------|--------|
| ADR-008: Architecture Validation Framework | Enterprise Architect | 2026-07-25 | Draft |
| ADR-009: Release Quality Gates | Enterprise Architect | 2026-07-25 | Draft |
| ADR-010: Governance Automation | Enterprise Architect | 2026-08-01 | Draft |
| ADR-011: Compliance Automation | Compliance Officer | 2026-08-01 | Draft |
| Security Headers Implementation (ADR-006) | Security Lead | 2026-07-31 | Proposed |
| Database Connection Pooling (ADR-007) | DBA | 2026-07-31 | Proposed |

---

## Decision Review Checklist

When reviewing decisions:
- [ ] Is the decision still valid?
- [ ] Have circumstances changed?
- [ ] Is the decision still being followed?
- [ ] Are there unintended consequences?
- [ ] Should this be promoted to an ADR?

---

## Related Documents

- `ADR_Index.md` — Architecture Decision Records index
- `Architecture_Decision_Records.md` — Full ADR details
- `Architecture_Principles_Catalog.md` — Architecture principles
- `Technology_Radar.md` — Technology choices

---

*Document End*
