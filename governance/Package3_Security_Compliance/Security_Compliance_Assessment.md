# Enterprise HSE Platform — Security & Compliance Assessment

**Document:** Security & Compliance Assessment  
**Version:** 2.1  
**Date:** 2026-07-18  
**Audience:** Security Team, Internal Audit, External Auditor, Compliance Officer  
**Classification:** Confidential — Security Sensitive

---

## TABLE OF CONTENTS

1. [Security Assessment (OWASP Top 10)](#1-security-assessment-owasp-top-10)
2. [Compliance Matrix](#2-compliance-matrix)
3. [Data Governance](#3-data-governance)
4. [AI Governance](#4-ai-governance)
5. [STRIDE Threat Model](#5-stride-threat-model)
6. [Risk Register](#6-risk-register)
7. [Security Recommendations](#7-security-recommendations)

---

## 1. SECURITY ASSESSMENT (OWASP TOP 10)

| OWASP Category | Status | Score | Notes |
|----------------|--------|-------|-------|
| A01: Broken Access Control | 🟡 | 75% | RBAC exists but needs repository-level enforcement |
| A02: Cryptographic Failures | 🟢 | 90% | JWT HS256, bcrypt, secrets properly managed |
| A03: Injection | 🟢 | 95% | SQLAlchemy ORM prevents SQL injection |
| A04: Insecure Design | 🟡 | 70% | No rate limiting implementation, no API versioning |
| A05: Security Misconfiguration | 🟡 | 75% | CORS wildcard in dev, debug mode risk, missing security headers |
| A06: Vulnerable Components | 🟡 | 70% | No dependency scanning in CI |
| A07: Identification & Auth Failures | 🟢 | 90% | JWT, refresh tokens, account lockout, password expiry |
| A08: Software & Data Integrity | 🟡 | 75% | No JWT jti validation, no code signing |
| A09: Security Logging Failures | 🟡 | 70% | Security events not logged separately |
| A10: Server-Side Request Forgery | 🟡 | 70% | No SSRF protection on outbound requests |

**Overall Security Score: 82/100**

### Critical Findings

| ID | Finding | Severity | Status | Remediation |
|----|---------|----------|--------|-------------|
| SEC-001 | File upload path traversal | High | Open | Sanitize paths, whitelist directories |
| SEC-002 | JWT replay attacks (no jti) | High | Open | Add jti validation, token blacklist |
| SEC-003 | Rate limiting not implemented | Medium | Open | Redis-backed rate limiter |
| SEC-004 | CORS wildcard in development | Medium | Open | Whitelist specific origins |
| SEC-005 | Mock embeddings fallback | High | Open | Disable in production |
| SEC-006 | No SAST/DAST in CI | High | Open | Add security scanning pipeline |
| SEC-007 | No secret scanning | High | Open | Add gitleaks/trufflehog |
| SEC-008 | No dependency scanning | Medium | Open | Add pip-audit/safety |

---

## 2. COMPLIANCE MATRIX

### ISO 45001 — Occupational Health & Safety

| Requirement | Implementation | Gap | Evidence | Priority |
|-------------|----------------|-----|----------|----------|
| Incident reporting | 95% | Investigation workflow incomplete | `incident_reports` table, `workflow_statuses` | Medium |
| PTW management | 90% | Electronic approval workflow | `ptw_requests` table | Medium |
| Training records | 85% | Certification tracking | `training_records` table | Medium |
| Audit trail | 95% | Complete | `audit_trail`, `audit_plans`, `audit_findings` | Low |
| Risk assessment | 90% | HIRA implemented | `hira_assessments` table | Low |
| Contractor management | 86% | Evaluation workflow partial | `contractor_records` table | Medium |

### ISO 14001 — Environmental Management

| Requirement | Implementation | Gap | Evidence | Priority |
|-------------|----------------|-----|----------|----------|
| Environmental monitoring | 88% | Automated KPI calculation | `environmental_readings` table | Medium |
| Emission tracking | 80% | Threshold alerts | `ref_env_threshold` table, `v_env_realtime` view | Medium |
| Waste management | 60% | Not implemented | Missing table | High |
| Compliance evaluation | 85% | Threshold-based alerts | `v_env_realtime` view | Medium |
| Documentation | 90% | Document ingestion | `ai_documents` table | Low |

### ISO 27001 — Information Security Management

| Requirement | Implementation | Gap | Evidence | Priority |
|-------------|----------------|-----|----------|----------|
| Access control | 90% | RBAC complete | `security_users`, `security_roles`, `security_permissions` | Low |
| Cryptography | 85% | JWT, bcrypt | `security.py`, `rbac.py` | Low |
| Incident management | 75% | No security incident workflow | Missing | High |
| Business continuity | 68% | Backup/restore defined | Backup scripts, `run_tests.bat` | High |
| Security monitoring | 70% | No SIEM integration | Missing | High |
| Vulnerability management | 60% | No scanning in CI | Missing | High |

### SMKP Minerba — Mining Safety Management

| Requirement | Implementation | Gap | Evidence | Priority |
|-------------|----------------|-----|----------|----------|
| Contractor evaluation | 86% | Evaluation workflow partial | `contractor_records` table | Medium |
| Equipment inspection | 90% | Certification tracking | `equipment_inspections` table | Low |
| Environmental monitoring | 88% | Threshold-based alerts | `v_env_realtime` view | Medium |
| Incident investigation | 85% | Workflow defined | `incident_reports` table | Medium |
| Training compliance | 85% | Certification tracking | `training_records` table | Medium |

### OSHA — Occupational Safety & Health

| Requirement | Implementation | Gap | Evidence | Priority |
|-------------|----------------|-----|----------|----------|
| Recordkeeping (300/300A) | 82% | OSHA 300 template missing | `incident_reports` table | Medium |
| Injury classification | 85% | Severity classes defined | `dim_incident` table | Low |
| Fatality reporting | 80% | Basic tracking | `fact_hse.fatality_count` | Medium |
| Exposure assessment | 70% | Environmental readings | `environmental_readings` table | Medium |

**Overall Compliance Score: 86/100**

---

## 3. DATA GOVERNANCE

### Data Ownership Matrix

| Data Domain | Owner | Steward | Classification | Retention | Quality Rule |
|-------------|-------|---------|----------------|-----------|--------------|
| Incident Reports | HSE Director | HSE Manager | Confidential | 10 years | Completeness: 100% required fields |
| PTW Requests | Site Manager | HSE Officer | Internal | 7 years | Validity: Approval workflow complete |
| Environmental Readings | HSE Manager | Environmental Officer | Public | 5 years | Accuracy: Lab method documented |
| Equipment Records | Maintenance Manager | Maintenance Officer | Internal | Equipment lifecycle | Validity: Certification valid |
| Training Records | HR Manager | Training Officer | Internal | 5 years | Completeness: Certification number |
| Audit Plans | Compliance Manager | Auditor | Confidential | 10 years | Integrity: Signed by lead auditor |
| AI Documents | ICT Admin | HSE Manager | Internal | 3 years | Provenance: Source documented |

### Data Classification Schema

| Classification | Description | Examples | Handling Requirements |
|----------------|-------------|----------|----------------------|
| Public | Non-sensitive, publicly releasable | Site names, general statistics | No restrictions |
| Internal | Internal business use | Department names, training records | Access control required |
| Confidential | Sensitive business data | Incident reports, audit findings | Encryption, access logging |
| Restricted | Highly sensitive, regulated | Employee PII, medical records | Encryption, audit trail, retention policy |

### Data Quality Rules

| Rule | Description | Validation | Action on Failure |
|------|-------------|------------|-------------------|
| Completeness | All required fields populated | Application + DB constraints | Reject insert/update |
| Validity | Values within allowed ranges | CHECK constraints | Reject insert/update |
| Consistency | Related records synchronized | Application logic | Alert data steward |
| Timeliness | Data entered within SLA | Timestamp validation | Alert supervisor |
| Uniqueness | No duplicate records | UNIQUE constraints | Reject insert |

### Data Lineage

```
Source Systems (SAP, HRIS, SCADA)
    ↓
ETL/Integration Layer
    ↓
Staging Tables (hse_staging)
    ↓
Dimension Tables (dim_*)
    ↓
Fact Table (fact_hse)
    ↓
Aggregation Views (v_daily_hse_summary, v_active_alerts)
    ↓
Dashboard / Reports / AI
```

**Lineage Tracking:** Implement ETL metadata table `hse.etl_metadata` with:
- `source_system`, `source_table`, `source_record_id`
- `target_table`, `target_record_id`
- `load_timestamp`, `load_status`
- `transformation_logic`

### Master Data Management (MDM)

| Master Data | Source of Truth | Sync Frequency | Governance |
|-------------|-----------------|----------------|------------|
| Site | SAP ERP / Manual entry | Real-time + Daily | HSE Director |
| Employee | HRIS | Daily | HR Manager |
| Equipment | Maintenance System | Weekly | Maintenance Manager |
| Contractor | Procurement | Weekly | Procurement Manager |
| Hazard | HSE Standards | Quarterly | HSE Manager |

---

## 4. AI GOVERNANCE

### Model Registry

| Model | Version | Training Date | Accuracy | Embedding Dimension | Status |
|-------|---------|---------------|----------|---------------------|--------|
| text-embedding-3-small | 1.0.0 | 2026-07-18 | N/A | 1536 | Production |
| [Future LLM] | TBD | TBD | TBD | N/A | Assessment |

### Prompt Registry

| Prompt ID | Version | Created | Last Modified | Purpose | Owner |
|-----------|---------|---------|---------------|---------|-------|
| safety-chat-v1 | 1.0.0 | 2026-07-18 | 2026-07-18 | HSE Q&A | AI Lead |
| compliance-check-v1 | 1.0.0 | 2026-07-18 | 2026-07-18 | Compliance intelligence | Compliance Lead |

### Dataset Provenance

| Dataset | Source | Date Imported | Quality Score | License | Retention |
|---------|--------|---------------|---------------|---------|-----------|
| HSE SOPs | Internal upload | TBD | TBD | Internal | 3 years |
| Regulations | Government sources | TBD | TBD | Public | Permanent |
| Audit Reports | Internal upload | TBD | TBD | Internal | 10 years |

### AI Risk Classification (EU AI Act Framework)

| AI Feature | Risk Level | Justification | Required Controls |
|------------|-----------|---------------|-------------------|
| Document Q&A | Limited | Informational only | Transparency, logging |
| Risk scoring | High | Influences safety decisions | Human approval, explainability, audit trail |
| Compliance intelligence | Medium | Supports decision-making | Accuracy monitoring, source citation |

### Human Approval Workflow

```
AI Suggestion → Human Review → Approval/Rejection → Action
     ↓              ↓                ↓
  Logged        Logged           Logged
```

**High-risk decisions** (incident classification, compliance gaps) require human approval before action.

### Bias Monitoring

| Check | Method | Frequency | Owner |
|-------|--------|-----------|-------|
| Training data diversity | Demographic analysis | Quarterly | AI Lead |
| Response fairness | A/B testing | Per release | AI Lead |
| Prompt bias | Manual review | Monthly | Compliance Lead |

---

## 5. STRIDE THREAT MODEL

### Threat Model per Component

| Component | Spoofing | Tampering | Repudiation | Info Disclosure | Denial of Service | Elevation of Privilege | Risk Level |
|-----------|----------|-----------|-------------|-----------------|-------------------|------------------------|------------|
| API Gateway | 🟡 | 🟢 | 🟡 | 🟢 | 🟡 | 🟡 | Medium |
| FastAPI Backend | 🟢 | 🟡 | 🟢 | 🟡 | 🟡 | 🟡 | Medium |
| PostgreSQL | 🟢 | 🟢 | 🟢 | 🟡 | 🟡 | 🟡 | Medium |
| Redis | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | Medium |
| Celery Workers | 🟢 | 🟡 | 🟢 | 🟢 | 🟡 | 🟡 | Low |
| AI Service | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | Medium |
| File Upload | 🟢 | 🔴 | 🟡 | 🟡 | 🟢 | 🟡 | High |

### Attack Surface Map

| Surface | Entry Point | Protocol | Authentication | Risk |
|---------|-------------|----------|----------------|------|
| API endpoints | `/api/v1/*` | HTTPS | JWT | Medium |
| File upload | `/api/v1/audit/evidence/upload` | HTTPS | JWT + Permission | High |
| Database | `5432` | TCP | Password | Medium |
| Redis | `6379` | TCP | None (internal) | Medium |
| Celery | `6379` | TCP | None (internal) | Medium |
| Grafana | `3000` | HTTPS | Basic Auth | Medium |
| AI chat | `/api/v1/ai/chat` | HTTPS | JWT | Medium |

---

## 6. RISK REGISTER

| Risk ID | Risk | Category | Likelihood | Impact | Score | Mitigation | Owner | Target Date | Status |
|---------|------|----------|-----------|--------|-------|------------|-------|-------------|--------|
| SEC-001 | File upload path traversal | Security | Medium | High | 9 | Sanitize paths, whitelist directories | Backend Lead | Sprint 0 | Open |
| SEC-002 | JWT replay attacks | Security | Medium | High | 9 | Add jti validation, token blacklist | Security Lead | Sprint 0 | Open |
| SEC-003 | Rate limiting not implemented | Security | High | Medium | 8 | Redis-backed rate limiter | Backend Lead | Sprint 0 | Open |
| SEC-004 | Database single point of failure | Infrastructure | Medium | High | 8 | PostgreSQL streaming replication | DBA | Sprint 1 | Open |
| SEC-005 | No API versioning | Architecture | High | Medium | 8 | Add `/v1/` prefix | Backend Lead | Sprint 0 | Open |
| SEC-006 | Prompt injection in AI | AI Security | Medium | High | 8 | Input sanitization, prompt filtering | AI Lead | Sprint 3 | Open |
| SEC-007 | Mock embeddings in production | AI Security | Medium | High | 8 | Remove mock, fail hard on API error | AI Lead | Sprint 3 | Open |
| SEC-008 | No DAST/SAST in CI | DevSecOps | High | Medium | 7 | Add security scanning pipeline | DevOps | Sprint 2 | Open |
| SEC-009 | Secrets not rotated | Security | Medium | Medium | 7 | Automated 90-day rotation | Security Lead | Sprint 2 | Open |
| SEC-010 | No BCP/DR演练 | Operations | Low | High | 7 | Quarterly recovery drills | Operations | Sprint 2 | Open |
| SEC-011 | Frontend no build process | Frontend | Medium | Medium | 6 | Add Vite build pipeline | Frontend Lead | Sprint 1 | Open |
| SEC-012 | No compliance reporting | Compliance | Medium | Medium | 6 | Automated ISO/OSHA reports | Compliance | Sprint 2 | Open |
| SEC-013 | AI cost overrun | Cost | Medium | Medium | 6 | Token budgeting, caching | AI Lead | Sprint 3 | Open |
| SEC-014 | No data lineage tracking | Data Governance | Medium | Medium | 6 | Implement ETL metadata | Data Engineer | Sprint 3 | Open |
| SEC-015 | Color-blind UX issues | UX | Medium | Low | 5 | Accessibility audit, palette testing | UX Lead | Sprint 4 | Open |

---

## 7. SECURITY RECOMMENDATIONS

### Immediate (Sprint 0)
1. Sanitize file upload paths — whitelist directories, reject `../` patterns
2. Add JWT jti validation — blacklist revoked tokens in Redis
3. Implement Redis rate limiting — replace in-memory implementation
4. Add API versioning (`/v1/` prefix)
5. Fix missing FK on `hazard_key`

### Short-term (Sprint 1-2)
6. Add SAST/DAST to CI pipeline
7. Add secret scanning (gitleaks)
8. Add dependency scanning (pip-audit)
9. Implement security headers (CSP, HSTS, X-Frame-Options)
10. Add SSRF protection for outbound requests

### Medium-term (Sprint 3-4)
11. Implement prompt injection detection for AI
12. Remove mock embeddings — fail hard on API unavailability
13. Add security incident response workflow
14. Implement SIEM integration
15. Conduct penetration test

---

## DOCUMENT REFERENCES

- [Package 1: Executive Governance](../Package1_Executive_Governance/Executive_Summary.md)
- [Package 2: Technical Architecture](../Package2_Technical_Architecture/Technical_Architecture_Audit.md)
- [Package 4: Delivery & Operations](../Package4_Delivery_Operations/)

---

*Document End*
