# ADR-010: Governance Automation

**Version:** 2.1  
**Date:** 2026-07-18  
**Status:** Draft  
**Deciders:** Enterprise Architect, DevOps Lead, Tech Lead  
**Related:** ADR-008, ADR-009

---

## Context

The Enterprise HSE Platform has established:
- Architecture Principles Catalog (15 principles)
- Technology Radar (Adopt/Trial/Assess/Hold)
- ADR Index (7 accepted, 3 proposed, 4 draft)
- Governance Rules Catalog (45 rules)
- Decision Log (11 decisions)
- Traceability Matrix (61 business requirements)

However, these governance artifacts are currently **documents only**. They are not integrated into the development workflow. This creates a gap:

- Governance decisions are made but not enforced
- Rules are documented but not automatically checked
- Compliance is manual and error-prone
- Documentation drifts from implementation

We need to automate governance enforcement to ensure that:
- Architecture rules are checked automatically
- ADRs are created for significant decisions
- Documentation stays in sync with code
- Compliance is continuously verified

---

## Decision

Implement **Governance Automation** — a set of automated checks and workflows that enforce governance artifacts throughout the development lifecycle.

### Automation Components

#### 1. ADR Automation

**ADR Creation Workflow:**
- PR template includes ADR checklist
- CI checks if PR requires ADR (based on criteria)
- ADR index automatically updated when ADR is created
- ADR status tracked in Decision Log

**ADR Criteria (automatic detection):**
- Changes to `app/models/` → ADR required
- Changes to `app/controllers/` → ADR required
- Changes to `app/config.py` → ADR required
- Changes to `sql/` → ADR required
- New dependencies in `requirements.txt` → ADR required

**Implementation:**
```yaml
# .github/workflows/adr-check.yml
name: ADR Check
on: pull_request
jobs:
  check-adr:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check if ADR required
        run: |
          if git diff --name-only ${{ github.event.pull_request.base.sha }} ${{ github.event.pull_request.head.sha }} | grep -E "(models|controllers|config|sql)"; then
            echo "ADR_REQUIRED=true" >> $GITHUB_ENV
          fi
      - name: Verify ADR exists
        if: env.ADR_REQUIRED == 'true'
        run: |
          # Check if ADR was added in PR
          git diff --name-only ${{ github.event.pull_request.base.sha }} ${{ github.event.pull_request.head.sha }} | grep -E "ADR_.*\.md" || (echo "ADR required but not found" && exit 1)
```

#### 2. Documentation Sync Automation

**Automatic Checks:**
- README matches project structure (check file existence)
- API documentation matches actual endpoints (check OpenAPI spec)
- Database schema matches SQLAlchemy models (check migration files)
- ADR Index includes all ADRs (check file listing)
- Traceability Matrix includes all endpoints (check API routes)

**Implementation:**
```python
# backend/scripts/documentation_sync.py
def check_readme_sync():
    """Verify README matches actual project structure."""
    # Check if all documented directories exist
    # Check if all documented files exist
    # Check if API endpoints match documentation
    
def check_adr_index_sync():
    """Verify ADR Index includes all ADRs."""
    # List all ADR files
    # Check if all are in ADR_Index.md
    
def check_traceability_sync():
    """Verify Traceability Matrix includes all endpoints."""
    # List all API routes
    # Check if all are in Traceability_Matrix.md
```

#### 3. Compliance Automation

**Automatic Checks:**
- All endpoints have RBAC (check for `require_permission`)
- All passwords are hashed (check for `hash_password`)
- No secrets in code (check with `truffleHog`)
- Mock embeddings disabled in production (check environment)
- CORS configured (check for wildcard)

**Implementation:**
```python
# backend/scripts/compliance_check.py
def check_rbac_compliance():
    """Verify all endpoints have RBAC."""
    # Parse all route definitions
    # Check if all have Depends(require_permission)
    
def check_secret_scanning():
    """Scan for secrets in code."""
    # Use truffleHog or git-secrets
    # Fail if secrets found
```

#### 4. Decision Log Automation

**Automatic Updates:**
- When ADR is merged → add entry to Decision Log
- When schema changes → add entry to Decision Log
- When dependencies change → add entry to Decision Log

**Implementation:**
```yaml
# .github/workflows/decision-log.yml
name: Update Decision Log
on:
  pull_request:
    types: [closed]
    branches: [main]
jobs:
  update-decision-log:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Extract ADR info
        run: |
          # Extract ADR title, date, status from PR
      - name: Update Decision Log
        run: |
          # Append new entry to Decision_Log.md
```

#### 5. Technology Radar Automation

**Automatic Updates:**
- Scan `requirements.txt` for dependencies
- Update Technology Radar status based on usage
- Alert when dependencies are outdated

**Implementation:**
```python
# backend/scripts/tech_radar_update.py
def scan_dependencies():
    """Scan requirements.txt and update Technology Radar."""
    # Read requirements.txt
    # Check each dependency against Technology Radar
    # Update status if needed
```

---

## Implementation Plan

### Phase 1: Basic Automation (Week 1-2)
1. Implement ADR check in CI
2. Implement documentation sync checks
3. Implement compliance checks
4. Add to CI pipeline

### Phase 2: Advanced Automation (Week 3-4)
1. Implement Decision Log automation
2. Implement Technology Radar automation
3. Create governance dashboard
4. Train team on automation

### Phase 3: Monitoring & Improvement (Week 5-8)
1. Monitor automation effectiveness
2. Gather team feedback
3. Refine automation rules
4. Add new automation as needed

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| ADR compliance | 100% | CI pass rate |
| Documentation sync | 100% | CI pass rate |
| Compliance violations | 0 | CI pass rate |
| Manual governance tasks | < 1 hour/week | Time tracking |
| Governance automation coverage | > 80% | Rule count |

---

## Alternatives Considered

### 1. Manual Governance (Current State)

**Rejected:**
- Inconsistent enforcement
- Documentation drift
- Compliance gaps
- Time-consuming

### 2. Third-party Governance Tools (e.g., Jira, Confluence)

**Rejected:**
- Additional cost
- External dependency
- Less flexible
- Overkill for current needs

### 3. Lightweight Automation (Selected)

**Selected:**
- Custom scripts for specific checks
- Integrated into existing CI/CD
- Low overhead
- High flexibility

---

## Consequences

### Positive

- **Consistent enforcement:** Rules applied uniformly
- **Reduced manual work:** Automation handles repetitive checks
- **Improved compliance:** Continuous verification
- **Better documentation:** Automated sync checks
- **Faster development:** Immediate feedback on violations

### Negative

- **Initial investment:** Time to build automation
- **Maintenance:** Scripts must be maintained
- **False positives:** May flag legitimate code
- **Complexity:** More moving parts

### Risks

- **Automation gaps:** Some rules not automated (mitigation: regular review)
- **Bypass:** Developers may disable checks (mitigation: CI enforcement)
- **Performance:** CI time increases (mitigation: parallel execution)

---

## Governance

This ADR is governed by:
- `Governance_Rules_Catalog.md` — Rules being automated
- `ADR_Index.md` — ADR tracking
- `Decision_Log.md` — Implementation decisions

---

## Related Documents

- `ADR-008_Architecture_Validation_Framework.md` — Architecture gates
- `ADR-009_Release_Quality_Gates.md` — Release gates
- `Governance_Rules_Catalog.md` — Governance rules
- `ADR_Index.md` — ADR tracking
- `Decision_Log.md` — Implementation decisions
- `.github/workflows/ci.yml` — CI/CD pipeline

---

*Document End*
