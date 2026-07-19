# ADR-011: Compliance Automation

**Version:** 2.1  
**Date:** 2026-07-18  
**Status:** Draft  
**Deciders:** Compliance Officer, Security Lead, Enterprise Architect  
**Related:** ADR-008, ADR-009, ADR-010

---

## Context

The Enterprise HSE Platform must comply with multiple regulations and standards:
- **ISO 45001:** Occupational Health and Safety
- **ISO 14001:** Environmental Management
- **ISO 27001:** Information Security Management
- **SMKP Minerba:** Mining Safety Management System (Indonesia)
- **OSHA:** Occupational Safety and Health Administration (US)
- **SMK3:** Sistem Manajemen K3 (Indonesia)

Currently, compliance is verified through:
- Manual audits
- Periodic assessments
- Checklist-based reviews

This approach has limitations:
- **Time-consuming:** Manual audits require significant effort
- **Inconsistent:** Different auditors may find different issues
- **Delayed:** Issues found only during periodic audits
- **Difficult to prove:** Hard to demonstrate continuous compliance

We need automated compliance checks that:
- Run continuously (not just during audits)
- Provide immediate feedback
- Generate audit evidence automatically
- Reduce manual audit effort

---

## Decision

Implement **Compliance Automation** — a set of automated checks and reports that verify compliance with regulatory requirements continuously.

### Compliance Automation Components

#### 1. Automated Compliance Checks

**Data Integrity Checks:**
```python
# Verify referential integrity
def check_referential_integrity():
    """Verify all foreign keys are valid."""
    # Check fact_hse references valid dimension records
    # Check no orphaned records
    
# Verify data completeness
def check_data_completeness():
    """Verify required fields are populated."""
    # Check man_hours_worked is not null
    # Check date_key is not null
    # Check site_key is not null
```

**Security Compliance Checks:**
```python
# Verify RBAC is enforced
def check_rbac_compliance():
    """Verify all endpoints have RBAC."""
    # Check all endpoints have require_permission
    
# Verify audit trail
def check_audit_trail():
    """Verify all mutations are logged."""
    # Check audit_trail table has entries for all changes
    
# Verify password policy
def check_password_policy():
    """Verify password requirements are enforced."""
    # Check minimum length, complexity, expiry
```

**Environmental Compliance Checks:**
```python
# Verify threshold monitoring
def check_threshold_monitoring():
    """Verify environmental thresholds are monitored."""
    # Check alerts generated for exceedances
    # Check threshold values are within regulatory limits
    
# Verify data retention
def check_data_retention():
    """Verify data retention policies are enforced."""
    # Check old data is archived/deleted per policy
```

#### 2. Compliance Dashboard

Create a compliance dashboard that shows:
- Overall compliance score
- Compliance by standard (ISO 45001, ISO 14001, etc.)
- Compliance by category (data, security, environmental)
- Trend over time
- Open compliance issues

**Implementation:**
```python
# backend/app/services/compliance_service.py
class ComplianceService:
    def get_compliance_score(self, standard: str) -> float:
        """Calculate compliance score for a standard."""
        
    def get_compliance_issues(self) -> List[Dict]:
        """Get list of open compliance issues."""
        
    def get_compliance_trend(self, days: int) -> List[Dict]:
        """Get compliance trend over time."""
```

#### 3. Automated Evidence Generation

**Audit Evidence Package:**
- Automatically generate evidence packages for audits
- Include: compliance scores, test results, audit trails, data samples
- Format: PDF report with supporting data
- Retention: 7 years (per corporate policy)

**Implementation:**
```python
# backend/app/services/compliance_service.py
def generate_audit_evidence(self, standard: str, period: str) -> Dict:
    """Generate evidence package for audit."""
    evidence = {
        "compliance_score": self.get_compliance_score(standard),
        "test_results": self.get_test_results(),
        "audit_trail": self.get_audit_trail(period),
        "data_samples": self.get_data_samples(period),
        "issues": self.get_compliance_issues()
    }
    return evidence
```

#### 4. Continuous Monitoring

**Real-time Compliance Monitoring:**
- Monitor compliance metrics continuously
- Alert on compliance degradation
- Track remediation progress

**Implementation:**
```python
# backend/app/services/compliance_service.py
def monitor_compliance(self):
    """Continuous compliance monitoring."""
    while True:
        score = self.get_compliance_score("ISO45001")
        if score < 0.9:
            self.create_alert("Compliance degradation", score)
        time.sleep(3600)  # Check every hour
```

#### 5. Compliance Reporting

**Automated Reports:**
- Daily compliance summary
- Weekly compliance trend
- Monthly compliance report
- Quarterly audit preparation report

**Implementation:**
```python
# backend/scripts/compliance_report.py
def generate_daily_report():
    """Generate daily compliance report."""
    # Run compliance checks
    # Generate report
    # Send to stakeholders
    
def generate_monthly_report():
    """Generate monthly compliance report."""
    # Run comprehensive compliance checks
    # Generate detailed report
    # Include evidence for auditors
```

---

## Implementation Plan

### Phase 1: Core Compliance Checks (Week 1-2)
1. Implement data integrity checks
2. Implement security compliance checks
3. Create compliance dashboard
4. Add to CI pipeline

### Phase 2: Evidence Generation (Week 3-4)
1. Implement automated evidence generation
2. Create PDF report template
3. Implement retention policy
4. Test with sample audit

### Phase 3: Continuous Monitoring (Week 5-6)
1. Implement real-time compliance monitoring
2. Create compliance alerts
3. Implement automated reporting
4. Train team on compliance automation

### Phase 4: Integration (Week 7-8)
1. Integrate with governance automation (ADR-010)
2. Create compliance API endpoints
3. Integrate with audit workflow
4. Document compliance process

---

## Compliance Standards Mapping

| Standard | Coverage | Automated Checks | Manual Checks | Evidence |
|----------|----------|------------------|---------------|----------|
| ISO 45001 | 91% | 85% | 15% | Automated |
| ISO 14001 | 88% | 80% | 20% | Automated |
| ISO 27001 | 84% | 75% | 25% | Automated |
| SMKP Minerba | 86% | 82% | 18% | Automated |
| OSHA | 82% | 78% | 22% | Automated |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Compliance score | > 90% | Automated checks |
| Audit preparation time | < 1 day | Time tracking |
| Compliance issues detected | 100% | CI pass rate |
| False positive rate | < 5% | Team feedback |
| Audit findings | 0 | Audit results |

---

## Alternatives Considered

### 1. Manual Compliance (Current State)

**Rejected:**
- Time-consuming
- Inconsistent
- Delayed detection
- Hard to prove compliance

### 2. Third-party Compliance Tools (e.g., OneTrust, Compliance.ai)

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
- Continuous verification

---

## Consequences

### Positive

- **Continuous compliance:** Issues detected immediately
- **Reduced audit effort:** Evidence generated automatically
- **Improved compliance score:** Continuous monitoring and alerting
- **Faster audit preparation:** Evidence packages ready instantly
- **Reduced risk:** Compliance gaps detected early

### Negative

- **Initial investment:** Time to build automation
- **Maintenance:** Checks must be updated as regulations change
- **False positives:** May flag legitimate exceptions
- **Complexity:** More moving parts

### Risks

- **Incomplete coverage:** Not all requirements automated (mitigation: regular review)
- **Regulatory changes:** Checks become outdated (mitigation: quarterly review)
- **Over-reliance:** Manual checks neglected (mitigation: hybrid approach)

---

## Governance

This ADR is governed by:
- `Governance_Rules_Catalog.md` — Compliance rules
- `ADR_Index.md` — ADR tracking
- `Decision_Log.md` — Implementation decisions
- Compliance Officer — Regulatory requirements

### Compliance Rule Changes

To add or modify compliance rules:
1. Update `Governance_Rules_Catalog.md`
2. Update compliance check scripts
3. Update this ADR if scope changes
4. Get approval from Compliance Officer

---

## Related Documents

- `ADR-008_Architecture_Validation_Framework.md` — Architecture gates
- `ADR-009_Release_Quality_Gates.md` — Release gates
- `ADR-010_Governance_Automation.md` — Governance automation
- `Governance_Rules_Catalog.md` — Governance rules
- `Security_Compliance_Assessment.md` — Security and compliance assessment
- `ADR_Index.md` — ADR tracking
- `Decision_Log.md` — Implementation decisions

---

*Document End*
