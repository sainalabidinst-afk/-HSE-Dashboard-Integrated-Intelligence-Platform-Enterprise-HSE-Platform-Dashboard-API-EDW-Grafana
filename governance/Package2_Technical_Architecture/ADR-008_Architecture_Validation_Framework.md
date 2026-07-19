# ADR-008: Architecture Validation Framework

**Version:** 2.1  
**Date:** 2026-07-18  
**Status:** Draft  
**Deciders:** Enterprise Architect, Tech Lead, Security Lead  
**Related:** ADR-001 through ADR-007, Governance_Rules_Catalog.md

---

## Context

The Enterprise HSE Platform has grown to include:
- 40+ database tables
- 70+ API endpoints
- Multiple architectural layers (controllers, services, repositories, models)
- Complex security requirements (RBAC, JWT, file uploads, rate limiting)
- AI/ML components (RAG with embeddings)

As the codebase grows, maintaining architectural consistency becomes increasingly difficult. Current code review process relies on manual inspection, which:
- Is inconsistent across reviewers
- Cannot catch all violations
- Does not scale with team growth
- Allows technical debt to accumulate

We need an automated way to enforce architecture rules and maintain code quality standards.

---

## Decision

Implement an **Architecture Validation Framework** that enforces governance rules automatically in CI/CD. The framework consists of:

### 1. CI/CD Integration

Add architecture validation as a mandatory CI job that runs on every pull request:

```yaml
architecture-validation:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: "3.11"
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install ruff mypy bandit
    - name: Run architecture checks
      run: |
        cd backend
        python scripts/architecture_validation.py
```

### 2. Validation Script

Create `backend/scripts/architecture_validation.py` that checks:

#### Layer Separation (GOV-001, GOV-002, GOV-003)
```python
# Controllers must not import database directly
# Repositories must not import FastAPI
# Services must not import controllers
```

#### Import Rules
```python
# Enforce:
# - controllers/ → services/ (OK)
# - controllers/ → repositories/ (FORBIDDEN)
# - services/ → repositories/ (OK)
# - repositories/ → models/ (OK)
# - models/ → (nothing above) (FORBIDDEN)
```

#### Circular Dependency Detection
```python
# Detect circular imports between modules
```

#### RBAC Enforcement (GOV-004)
```python
# All endpoints (except /health, /docs, /redoc) must have:
# @router.get/post/... + Depends(require_permission(...))
```

#### Foreign Key Validation (GOV-005)
```python
# All relationship columns in models must have ForeignKey
```

#### Mock Embedding Check (GOV-016)
```python
# _mock_embedding must not be called in production code paths
# ENABLE_MOCK_EMBEDDINGS must be false in production
```

#### Secret Scanning (GOV-017)
```python
# No hardcoded secrets, passwords, API keys
# Use truffleHog or git-secrets
```

### 3. Pre-commit Hooks

Add pre-commit hooks to catch violations before they reach CI:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: architecture-check
        name: Architecture Validation
        entry: python scripts/architecture_validation.py
        language: python
        types: [python]
```

### 4. IDE Integration

Provide IDE configuration (VS Code, PyCharm) to run architecture checks on save:

```json
// .vscode/settings.json
{
  "python.linting.ruffEnabled": true,
  "python.linting.mypyEnabled": true,
  "python.testing.pytestEnabled": true
}
```

### 5. Documentation

Update `CONTRIBUTING.md` with:
- How to run architecture checks locally
- Common violations and how to fix them
- Exception request process

---

## Alternatives Considered

### 1. Manual Code Review Only

**Rejected:**
- Inconsistent enforcement
- Does not scale
- Human error
- No immediate feedback

### 2. Third-party Architecture Tools (e.g., SonarQube, CodeClimate)

**Rejected:**
- Additional cost
- Less flexible for custom rules
- External dependency
- Overkill for current team size

### 3. No Automation (Current State)

**Rejected:**
- Technical debt accumulates
- Inconsistent code quality
- Difficult to maintain as team grows

---

## Consequences

### Positive

- **Consistent enforcement:** Rules are applied uniformly to all code
- **Immediate feedback:** Developers know about violations immediately
- **Scalable:** Works regardless of team size
- **Maintainable:** Easy to add new rules as governance evolves
- **Transparent:** All rules are documented and visible

### Negative

- **Initial setup effort:** Requires writing validation scripts
- **False positives:** May flag legitimate code patterns
- **Maintenance overhead:** Rules must be updated as architecture evolves
- **Learning curve:** Team must learn new tools and processes

### Risks

- **Overly strict rules:** May slow down development (mitigation: exception process, regular rule review)
- **CI performance:** Additional validation time (mitigation: parallel execution, caching)
- **Rule bypass:** Developers may disable checks (mitigation: CI enforcement, code review)

---

## Implementation Plan

### Phase 1: Core Validation (Week 1)
1. Create `architecture_validation.py` script
2. Implement layer separation checks
3. Implement import rule checks
4. Add CI job
5. Test on sample PRs

### Phase 2: Advanced Validation (Week 2)
1. Implement RBAC enforcement check
2. Implement foreign key validation
3. Implement mock embedding check
4. Add pre-commit hooks
5. Update documentation

### Phase 3: Monitoring & Improvement (Week 3-4)
1. Add validation metrics to CI
2. Create dashboard for architecture compliance
3. Gather feedback from team
4. Refine rules based on feedback
5. Train team on architecture validation

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Architecture violations per PR | < 2 | CI metrics |
| False positive rate | < 5% | Team feedback |
| CI validation time | < 2 minutes | CI pipeline |
| Rule compliance rate | 100% | CI pass rate |
| Developer satisfaction | > 4/5 | Survey |

---

## Governance

This ADR is governed by:
- `Governance_Rules_Catalog.md` — Rules being enforced
- `ADR_Index.md` — ADR tracking
- `Decision_Log.md` — Implementation decisions

### Rule Changes

To add or modify architecture rules:
1. Update `Governance_Rules_Catalog.md`
2. Update `architecture_validation.py`
3. Update this ADR if scope changes
4. Communicate changes to team

---

## Related Documents

- `Governance_Rules_Catalog.md` — Rules being enforced
- `ADR_Index.md` — ADR tracking
- `Decision_Log.md` — Implementation decisions
- `Architecture_Principles_Catalog.md` — Governing principles
- `.github/workflows/ci.yml` — CI/CD pipeline

---

*Document End*
