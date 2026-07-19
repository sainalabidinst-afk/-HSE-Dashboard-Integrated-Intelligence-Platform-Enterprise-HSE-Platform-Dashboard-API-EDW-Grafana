# Traceability Matrix

**Version:** 2.1  
**Date:** 2026-07-18  
**Owner:** Enterprise Architect  
**Review Cycle:** Monthly  
**Status:** Active

---

## Purpose

This Traceability Matrix provides end-to-end traceability from business requirements through technical implementation to testing and risk management. It ensures that every business requirement is implemented, tested, and governed.

---

## Structure

| Field | Description |
|-------|-------------|
| **BR** | Business Requirement ID |
| **Business Requirement** | Description of the business need |
| **Module** | Application module responsible |
| **API Endpoint** | REST API endpoint(s) |
| **Database Table** | Primary database table(s) |
| **Schema/Model** | SQLAlchemy model file |
| **Test Case** | Test file and test function |
| **Risk** | Associated risk ID |
| **ADR** | Related Architecture Decision |
| **Status** | Implementation status |

---

## Traceability Matrix

### Executive & Governance

| BR | Business Requirement | Module | API Endpoint | Database Table | Schema/Model | Test Case | Risk | ADR | Status |
|----|---------------------|--------|--------------|----------------|--------------|-----------|------|-----|--------|
| BR-001 | View executive KPI dashboard | Dashboard | `GET /api/v1/dashboard/summary` | `fact_hse`, `dim_*` | `DashboardService` | `tests/unit/test_dashboard.py` | SEC-001 | ADR-003 | ✅ Implemented |
| BR-002 | View incident trends | Dashboard | `GET /api/v1/dashboard/incidents` | `fact_hse`, `dim_incident` | `DashboardService` | `tests/unit/test_dashboard.py` | SEC-002 | ADR-003 | ✅ Implemented |
| BR-003 | View PTW status | Dashboard | `GET /api/v1/dashboard/ptw` | `fact_hse`, `dim_ptw` | `DashboardService` | `tests/unit/test_dashboard.py` | SEC-003 | ADR-003 | ✅ Implemented |
| BR-004 | View training compliance | Dashboard | `GET /api/v1/dashboard/training` | `fact_hse`, `dim_training` | `DashboardService` | `tests/unit/test_dashboard.py` | SEC-004 | ADR-003 | ✅ Implemented |
| BR-005 | View environmental metrics | Dashboard | `GET /api/v1/dashboard/environmental` | `fact_hse`, `dim_environmental` | `DashboardService` | `tests/unit/test_dashboard.py` | SEC-005 | ADR-003 | ✅ Implemented |
| BR-006 | View equipment status | Dashboard | `GET /api/v1/dashboard/equipment` | `fact_hse`, `dim_equipment` | `DashboardService` | `tests/unit/test_dashboard.py` | SEC-006 | ADR-003 | ✅ Implemented |
| BR-007 | View contractor performance | Dashboard | `GET /api/v1/dashboard/contractor` | `fact_hse`, `dim_contractor` | `DashboardService` | `tests/unit/test_dashboard.py` | SEC-007 | ADR-003 | ✅ Implemented |
| BR-008 | View active alerts | Dashboard | `GET /api/v1/dashboard/alerts` | `alerts`, `alert_rules` | `AlertService` | `tests/unit/test_alerts.py` | SEC-008 | ADR-003 | ✅ Implemented |

### Incident Management

| BR | Business Requirement | Module | API Endpoint | Database Table | Schema/Model | Test Case | Risk | ADR | Status |
|----|---------------------|--------|--------------|----------------|--------------|-----------|------|-----|--------|
| BR-009 | Report new incident | Incident | `POST /api/v1/operational/incidents` | `incident_reports` | `IncidentService` | `tests/unit/test_incidents.py` | OPS-001 | ADR-001 | ✅ Implemented |
| BR-010 | View incident list | Incident | `GET /api/v1/operational/incidents` | `incident_reports` | `IncidentService` | `tests/unit/test_incidents.py` | OPS-001 | ADR-001 | ✅ Implemented |
| BR-011 | View incident detail | Incident | `GET /api/v1/operational/incidents/{id}` | `incident_reports` | `IncidentService` | `tests/unit/test_incidents.py` | OPS-001 | ADR-001 | ✅ Implemented |
| BR-012 | Update incident status | Incident | `PATCH /api/v1/operational/incidents/{id}` | `incident_reports` | `IncidentService` | `tests/unit/test_incidents.py` | OPS-001 | ADR-001 | ✅ Implemented |
| BR-013 | Close incident with CAPA | Incident | `POST /api/v1/operational/incidents/{id}/close` | `incident_reports`, `corrective_actions` | `IncidentService` | `tests/unit/test_incidents.py` | OPS-001 | ADR-001 | 🔄 Planned |
| BR-014 | Export incident register | Incident | `GET /api/v1/operational/incidents/export` | `incident_reports` | `IncidentService` | `tests/unit/test_incidents.py` | OPS-002 | ADR-001 | 🔄 Planned |

### PTW (Permit to Work)

| BR | Business Requirement | Module | API Endpoint | Database Table | Schema/Model | Test Case | Risk | ADR | Status |
|----|---------------------|--------|--------------|----------------|--------------|-----------|------|-----|--------|
| BR-015 | Create PTW request | PTW | `POST /api/v1/operational/ptw` | `ptw_requests` | `PTWService` | `tests/unit/test_ptw.py` | OPS-003 | ADR-001 | ✅ Implemented |
| BR-016 | View PTW list | PTW | `GET /api/v1/operational/ptw` | `ptw_requests` | `PTWService` | `tests/unit/test_ptw.py` | OPS-003 | ADR-001 | ✅ Implemented |
| BR-017 | Approve PTW | PTW | `POST /api/v1/operational/ptw/{id}/approve` | `ptw_requests` | `PTWService` | `tests/unit/test_ptw.py` | OPS-003 | ADR-001 | 🔄 Planned |
| BR-018 | Activate PTW | PTW | `POST /api/v1/operational/ptw/{id}/activate` | `ptw_requests` | `PTWService` | `tests/unit/test_ptw.py` | OPS-003 | ADR-001 | 🔄 Planned |
| BR-019 | Close PTW | PTW | `POST /api/v1/operational/ptw/{id}/close` | `ptw_requests` | `PTWService` | `tests/unit/test_ptw.py` | OPS-003 | ADR-001 | 🔄 Planned |
| BR-020 | Track PTW violations | PTW | `POST /api/v1/operational/ptw/{id}/violations` | `ptw_requests` | `PTWService` | `tests/unit/test_ptw.py` | OPS-003 | ADR-001 | 🔄 Planned |

### Training Management

| BR | Business Requirement | Module | API Endpoint | Database Table | Schema/Model | Test Case | Risk | ADR | Status |
|----|---------------------|--------|--------------|----------------|--------------|-----------|------|-----|--------|
| BR-021 | Create training record | Training | `POST /api/v1/operational/training` | `training_records` | `TrainingService` | `tests/unit/test_training.py` | OPS-004 | ADR-001 | ✅ Implemented |
| BR-022 | View training list | Training | `GET /api/v1/operational/training` | `training_records` | `TrainingService` | `tests/unit/test_training.py` | OPS-004 | ADR-001 | ✅ Implemented |
| BR-023 | Track certification expiry | Training | `GET /api/v1/operational/training/expiring` | `training_records` | `TrainingService` | `tests/unit/test_training.py` | OPS-004 | ADR-001 | 🔄 Planned |
| BR-024 | Generate training compliance report | Training | `GET /api/v1/operational/training/compliance` | `training_records` | `TrainingService` | `tests/unit/test_training.py` | OPS-004 | ADR-001 | 🔄 Planned |

### Environmental Monitoring

| BR | Business Requirement | Module | API Endpoint | Database Table | Schema/Model | Test Case | Risk | ADR | Status |
|----|---------------------|--------|--------------|----------------|--------------|-----------|------|-----|--------|
| BR-025 | Record environmental reading | Environmental | `POST /api/v1/operational/environmental` | `environmental_readings` | `EnvironmentalService` | `tests/unit/test_environmental.py` | OPS-005 | ADR-001 | ✅ Implemented |
| BR-026 | View environmental trends | Environmental | `GET /api/v1/operational/environmental/trends` | `environmental_readings` | `EnvironmentalService` | `tests/unit/test_environmental.py` | OPS-005 | ADR-001 | 🔄 Planned |
| BR-027 | Check threshold exceedance | Environmental | `GET /api/v1/operational/environmental/exceedances` | `environmental_readings`, `ref_env_threshold` | `EnvironmentalService` | `tests/unit/test_environmental.py` | OPS-005 | ADR-005 | 🔄 Planned |
| BR-028 | Generate environmental report | Environmental | `GET /api/v1/operational/environmental/report` | `environmental_readings` | `EnvironmentalService` | `tests/unit/test_environmental.py` | OPS-005 | ADR-001 | 🔄 Planned |

### Equipment Management

| BR | Business Requirement | Module | API Endpoint | Database Table | Schema/Model | Test Case | Risk | ADR | Status |
|----|---------------------|--------|--------------|----------------|--------------|-----------|------|-----|--------|
| BR-029 | Create equipment inspection | Equipment | `POST /api/v1/operational/equipment/inspections` | `equipment_inspections` | `EquipmentInspectionService` | `tests/unit/test_equipment.py` | OPS-006 | ADR-001 | ✅ Implemented |
| BR-030 | View equipment status | Equipment | `GET /api/v1/operational/equipment` | `equipment_inspections` | `EquipmentInspectionService` | `tests/unit/test_equipment.py` | OPS-006 | ADR-001 | ✅ Implemented |
| BR-031 | Track certification expiry | Equipment | `GET /api/v1/operational/equipment/expiring` | `equipment_inspections` | `EquipmentInspectionService` | `tests/unit/test_equipment.py` | OPS-006 | ADR-001 | 🔄 Planned |

### Contractor Management

| BR | Business Requirement | Module | API Endpoint | Database Table | Schema/Model | Test Case | Risk | ADR | Status |
|----|---------------------|--------|--------------|----------------|--------------|-----------|------|-----|--------|
| BR-032 | Register contractor | Contractor | `POST /api/v1/operational/contractor` | `contractor_records` | `ContractorService` | `tests/unit/test_contractor.py` | OPS-007 | ADR-001 | ✅ Implemented |
| BR-033 | View contractor list | Contractor | `GET /api/v1/operational/contractor` | `contractor_records` | `ContractorService` | `tests/unit/test_contractor.py` | OPS-007 | ADR-001 | ✅ Implemented |
| BR-034 | Evaluate contractor performance | Contractor | `POST /api/v1/operational/contractor/{id}/evaluate` | `contractor_records` | `ContractorService` | `tests/unit/test_contractor.py` | OPS-007 | ADR-001 | 🔄 Planned |

### Audit & Compliance

| BR | Business Requirement | Module | API Endpoint | Database Table | Schema/Model | Test Case | Risk | ADR | Status |
|----|---------------------|--------|--------------|----------------|--------------|-----------|------|-----|--------|
| BR-035 | Create audit plan | Audit | `POST /api/v1/audit/plans` | `audit_plans` | `AuditService` | `tests/unit/test_audit.py` | GOV-001 | ADR-001 | ✅ Implemented |
| BR-036 | View audit plans | Audit | `GET /api/v1/audit/plans` | `audit_plans` | `AuditService` | `tests/unit/test_audit.py` | GOV-001 | ADR-001 | ✅ Implemented |
| BR-037 | Record audit findings | Audit | `POST /api/v1/audit/findings` | `audit_findings` | `AuditService` | `tests/unit/test_audit.py` | GOV-001 | ADR-001 | ✅ Implemented |
| BR-038 | Upload evidence | Audit | `POST /api/v1/audit/evidence` | `evidence` | `AuditService` | `tests/unit/test_audit.py` | GOV-001 | ADR-001 | ✅ Implemented |
| BR-039 | Create corrective action | Audit | `POST /api/v1/audit/corrective-actions` | `corrective_actions` | `AuditService` | `tests/unit/test_audit.py` | GOV-001 | ADR-001 | ✅ Implemented |
| BR-040 | View audit trail | Audit | `GET /api/v1/audit/trail` | `audit_trail` | `AuditService` | `tests/unit/test_audit.py` | GOV-001 | ADR-001 | ✅ Implemented |

### Alert Engine

| BR | Business Requirement | Module | API Endpoint | Database Table | Schema/Model | Test Case | Risk | ADR | Status |
|----|---------------------|--------|--------------|----------------|--------------|-----------|------|-----|--------|
| BR-041 | Create alert rule | Alert | `POST /api/v1/alerts/rules` | `alert_rules` | `AlertService` | `tests/unit/test_alerts.py` | OPS-008 | ADR-005 | ✅ Implemented |
| BR-042 | View alert rules | Alert | `GET /api/v1/alerts/rules` | `alert_rules` | `AlertService` | `tests/unit/test_alerts.py` | OPS-008 | ADR-005 | ✅ Implemented |
| BR-043 | View active alerts | Alert | `GET /api/v1/alerts/active` | `alerts` | `AlertService` | `tests/unit/test_alerts.py` | OPS-008 | ADR-005 | ✅ Implemented |
| BR-044 | Acknowledge alert | Alert | `POST /api/v1/alerts/{id}/acknowledge` | `alerts` | `AlertService` | `tests/unit/test_alerts.py` | OPS-008 | ADR-005 | 🔄 Planned |
| BR-045 | Send alert notification | Alert | Background task | `notification_logs` | `AlertService` | `tests/unit/test_alerts.py` | OPS-008 | ADR-005 | 🔄 Planned |

### AI Safety Assistant

| BR | Business Requirement | Module | API Endpoint | Database Table | Schema/Model | Test Case | Risk | ADR | Status |
|----|---------------------|--------|--------------|----------------|--------------|-----------|------|-----|--------|
| BR-046 | Chat with AI assistant | AI | `POST /api/v1/ai/chat` | `ai_conversations`, `ai_messages` | `AIService` | `tests/unit/test_ai.py` | AI-001 | ADR-004 | ✅ Implemented |
| BR-047 | Ingest document into knowledge base | AI | `POST /api/v1/ai/documents` | `ai_documents`, `ai_document_chunks` | `AIService` | `tests/unit/test_ai.py` | AI-001 | ADR-004 | ✅ Implemented |
| BR-048 | View knowledge base stats | AI | `GET /api/v1/ai/knowledge/stats` | `ai_documents` | `AIService` | `tests/unit/test_ai.py` | AI-001 | ADR-004 | ✅ Implemented |
| BR-049 | Generate RAG embeddings | AI | Internal | `ai_document_chunks` | `AIService` | `tests/unit/test_ai.py` | AI-001 | ADR-004 | ✅ Implemented |

### Authentication & Authorization

| BR | Business Requirement | Module | API Endpoint | Database Table | Schema/Model | Test Case | Risk | ADR | Status |
|----|---------------------|--------|--------------|----------------|--------------|-----------|------|-----|--------|
| BR-050 | User login | Auth | `POST /api/v1/auth/login` | `security_users` | `AuthService` | `tests/unit/test_security.py` | SEC-009 | ADR-001 | ✅ Implemented |
| BR-051 | Refresh access token | Auth | `POST /api/v1/auth/refresh` | `security_sessions` | `AuthService` | `tests/unit/test_security.py` | SEC-009 | ADR-001 | ✅ Implemented |
| BR-052 | User logout | Auth | `POST /api/v1/auth/logout` | `security_sessions` | `AuthService` | `tests/unit/test_security.py` | SEC-009 | ADR-001 | ✅ Implemented |
| BR-053 | Get current user | Auth | `GET /api/v1/auth/me` | `security_users` | `AuthService` | `tests/unit/test_security.py` | SEC-009 | ADR-001 | ✅ Implemented |
| BR-054 | Get user permissions | Auth | `GET /api/v1/auth/permissions` | `security_permissions` | `AuthService` | `tests/unit/test_security.py` | SEC-009 | ADR-001 | ✅ Implemented |
| BR-055 | Get dynamic menu | Auth | `GET /api/v1/auth/menu` | `security_permissions` | `AuthService` | `tests/unit/test_security.py` | SEC-009 | ADR-001 | ✅ Implemented |
| BR-056 | Enforce RBAC on endpoints | Auth | Middleware | `security_user_role` | `RBACMiddleware` | `tests/unit/test_rbac.py` | SEC-010 | ADR-001 | ✅ Implemented |

### Reporting

| BR | Business Requirement | Module | API Endpoint | Database Table | Schema/Model | Test Case | Risk | ADR | Status |
|----|---------------------|--------|--------------|----------------|--------------|-----------|------|-----|--------|
| BR-057 | Generate executive report | Reporting | `POST /api/v1/reports/generate` | `fact_hse` | `ReportingService` | `tests/unit/test_reporting.py` | OPS-009 | ADR-001 | 🔄 Planned |
| BR-058 | Export to PDF | Reporting | `GET /api/v1/reports/{id}/pdf` | `fact_hse` | `ReportingService` | `tests/unit/test_reporting.py` | OPS-009 | ADR-001 | 🔄 Planned |
| BR-059 | Export to Excel | Reporting | `GET /api/v1/reports/{id}/excel` | `fact_hse` | `ReportingService` | `tests/unit/test_reporting.py` | OPS-009 | ADR-001 | 🔄 Planned |

### Data Quality

| BR | Business Requirement | Module | API Endpoint | Database Table | Schema/Model | Test Case | Risk | ADR | Status |
|----|---------------------|--------|--------------|----------------|--------------|-----------|------|-----|--------|
| BR-060 | Run data quality checks | Data Quality | `GET /api/v1/data/quality` | `fact_hse` | `DataQualityService` | `tests/unit/test_data_quality.py` | OPS-010 | ADR-002 | ✅ Implemented |
| BR-061 | Validate data freshness | Data Quality | `GET /api/v1/data/quality/freshness` | `fact_hse` | `DataQualityService` | `tests/unit/test_data_quality.py` | OPS-010 | ADR-002 | ✅ Implemented |

---

## Coverage Summary

| Module | Total Requirements | Implemented | Planned | Coverage |
|--------|-------------------|-------------|---------|----------|
| Executive & Governance | 8 | 8 | 0 | 100% |
| Incident Management | 6 | 3 | 3 | 50% |
| PTW | 6 | 1 | 5 | 17% |
| Training | 4 | 1 | 3 | 25% |
| Environmental | 4 | 1 | 3 | 25% |
| Equipment | 3 | 1 | 2 | 33% |
| Contractor | 3 | 1 | 2 | 33% |
| Audit & Compliance | 6 | 6 | 0 | 100% |
| Alert Engine | 5 | 3 | 2 | 60% |
| AI Safety Assistant | 4 | 4 | 0 | 100% |
| Authentication & Authorization | 7 | 7 | 0 | 100% |
| Reporting | 3 | 0 | 3 | 0% |
| Data Quality | 2 | 2 | 0 | 100% |
| **Total** | **61** | **38** | **23** | **62%** |

---

## Traceability by ADR

| ADR | Business Requirements | Implementation Status |
|-----|----------------------|----------------------|
| ADR-001 | BR-001 through BR-059 (API design) | 38 implemented, 23 planned |
| ADR-002 | BR-060, BR-061 (partitioning, data quality) | 2 implemented |
| ADR-003 | BR-001 through BR-008 (caching) | 8 implemented |
| ADR-004 | BR-046 through BR-049 (AI embeddings) | 4 implemented |
| ADR-005 | BR-027, BR-041 through BR-045 (background tasks) | 3 implemented, 3 planned |

---

## Risk Coverage

| Risk ID | Risk Description | Business Requirements | Mitigation |
|---------|-----------------|----------------------|------------|
| SEC-001 | File upload path traversal | BR-009 through BR-014 | Path sanitization (Sprint 0) |
| SEC-002 | JWT replay attacks | BR-050 through BR-056 | jti validation (Sprint 0) |
| SEC-003 | Rate limiting not implemented | BR-001 through BR-059 | Redis rate limiter (Sprint 0) |
| SEC-004 | Database single point of failure | All | PostgreSQL replication (Sprint 1) |
| SEC-005 | No API versioning | BR-001 through BR-059 | ADR-001 implementation |
| SEC-006 | Missing foreign keys | All | Fixed 2026-07-18 |
| SEC-007 | Duplicate schema definitions | All | Fixed 2026-07-18 |
| SEC-008 | Alert notification failures | BR-041 through BR-045 | ADR-005 (Celery) |
| SEC-009 | Authentication bypass | BR-050 through BR-056 | JWT + RBAC |
| SEC-010 | Authorization bypass | BR-050 through BR-056 | RBAC middleware |
| OPS-001 | Incident data loss | BR-009 through BR-014 | Database constraints, audit trail |
| OPS-002 | Export performance | BR-014 | Async report generation (ADR-005) |
| OPS-003 | PTW workflow errors | BR-015 through BR-020 | State machine validation |
| OPS-004 | Training data gaps | BR-021 through BR-024 | Data quality checks |
| OPS-005 | Environmental threshold errors | BR-025 through BR-028 | `ref_env_threshold` table |
| OPS-006 | Equipment certification lapses | BR-029 through BR-031 | Alert rules |
| OPS-007 | Contractor performance gaps | BR-032 through BR-034 | Evaluation workflow |
| OPS-008 | Alert storm | BR-041 through BR-045 | Rate limiting, deduplication |
| OPS-009 | Report generation failures | BR-057 through BR-059 | Celery retry (ADR-005) |
| OPS-010 | Data quality degradation | BR-060 through BR-061 | Automated quality checks |
| AI-001 | AI hallucination | BR-046 through BR-049 | RAG with source citation |

---

## Test Coverage Matrix

| Module | Unit Tests | Integration Tests | E2E Tests | Coverage |
|--------|-----------|-------------------|-----------|----------|
| Dashboard | ✅ | 🔄 | ❌ | 60% |
| Incident | ✅ | 🔄 | ❌ | 50% |
| PTW | ✅ | 🔄 | ❌ | 40% |
| Training | ✅ | 🔄 | ❌ | 40% |
| Environmental | ✅ | 🔄 | ❌ | 40% |
| Equipment | ✅ | 🔄 | ❌ | 40% |
| Contractor | ✅ | 🔄 | ❌ | 40% |
| Audit | ✅ | 🔄 | ❌ | 70% |
| Alert | ✅ | 🔄 | ❌ | 60% |
| AI | ✅ | 🔄 | ❌ | 70% |
| Auth | ✅ | ✅ | ❌ | 80% |

---

## Maintenance

This matrix should be updated:
- When new business requirements are added
- When new modules are created
- When ADRs are accepted or superseded
- When risks are identified or mitigated
- When test coverage changes

---

## Related Documents

- `ADR_Index.md` — Architecture Decision Records index
- `Architecture_Decision_Records.md` — Full ADR details
- `Decision_Log.md` — Day-to-day project decisions
- `Governance_Rules_Catalog.md` — Governance rules
- `Technical_Architecture_Audit.md` — Technical architecture assessment

---

*Document End*
