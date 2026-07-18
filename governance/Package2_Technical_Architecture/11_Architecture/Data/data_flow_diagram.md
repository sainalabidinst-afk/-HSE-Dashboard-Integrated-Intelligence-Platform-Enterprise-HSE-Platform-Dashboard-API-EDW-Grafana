# Enterprise HSE Platform — Data Flow Diagram

**Document:** Data Flow Diagram (DFD)  
**Version:** 2.1  
**Date:** 2026-07-18  
**Audience:** Data Architect, Security Team, Compliance Officer

---

## LEVEL 0: CONTEXT DIAGRAM

```
┌─────────────────────────────────────────────────────────────┐
│                     EXTERNAL ENTITIES                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Users   │  │   SAP    │  │  SCADA   │  │   IoT    │  │
│  │ (HSE)    │  │   ERP    │  │   OPC    │  │ Gateway  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │             │             │             │         │
└───────┼─────────────┼─────────────┼─────────────┼─────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│              ENTERPRISE HSE PLATFORM                        │
│                                                             │
│    ┌─────────────────────────────────────────────────┐    │
│    │  API Gateway (Nginx)                            │    │
│    │  - Authentication                                │    │
│    │  - Rate Limiting                                 │    │
│    │  - Routing                                       │    │
│    └──────────────────┬──────────────────────────────┘    │
│                       │                                     │
│    ┌──────────────────▼──────────────────────────────┐    │
│    │  FastAPI Backend                                │    │
│    │  - Business Logic                               │    │
│    │  - RBAC                                         │    │
│    │  - Validation                                   │    │
│    └──────────────────┬──────────────────────────────┘    │
│                       │                                     │
│    ┌──────────────────▼──────────────────────────────┐    │
│    │  PostgreSQL EDW                                 │    │
│    │  - Dimension Tables                             │    │
│    │  - Fact Tables                                  │    │
│    │  - Security Tables                              │    │
│    │  - Audit Tables                                 │    │
│    └─────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## LEVEL 1: DATA FLOW BY MODULE

### 1.1 Incident Management Data Flow

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  HSE    │────▶│  FastAPI│────▶│PostgreSQL│────▶│ Dashboard│
│ Officer │     │ Backend │     │  EDW    │     │  View   │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
     │                │                │                │
     │ 1. Create      │ 2. Validate    │ 3. Insert      │ 4. Query
     │    Incident    │    RBAC        │    record      │    & Display
     │                │                │                │
     ▼                ▼                ▼                ▼
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  Mobile │     │ Celery  │     │  Audit  │     │ Grafana │
│  App    │     │ Worker  │     │  Trail  │     │Dashboard │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
     │                │                │                │
     │ 5. Offline     │ 6. Send        │ 7. Log          │ 8. Metrics
     │    sync        │    alerts      │    changes      │
     │                │                │                │
```

### 1.2 AI Knowledge Base Data Flow

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  User   │────▶│  FastAPI│────▶│  AI     │────▶│ pgvector│
│  Query  │     │ Backend │     │ Service │     │  Index  │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
     │                │                │                │
     │ 1. Submit      │ 2. Authenticate│ 3. Embed       │ 4. Vector
     │    question    │    & Authorize │    query       │    search
     │                │                │                │
     ▼                ▼                ▼                ▼
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ OpenAI  │     │PostgreSQL│     │  Audit  │     │Response │
│  API    │     │  (meta) │     │  Trail  │     │  Cache  │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
     │                │                │                │
     │ 5. Generate     │ 6. Store        │ 7. Log          │ 8. Cache
     │    embedding    │    metadata     │    AI query     │    result
     │                │                │                │
     ▼                ▼                ▼                ▼
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│Response │     │ Redis   │     │ Metrics │     │ Frontend│
│ to User │     │  Cache  │     │  (OTEL) │     │ Display │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
```

### 1.3 Environmental Monitoring Data Flow

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ SCADA / │────▶│  MQTT   │────▶│ FastAPI │────▶│PostgreSQL│
│   IoT   │     │ Broker  │     │ Backend │     │  EDW    │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
     │                │                │                │
     │ 1. Sensor      │ 2. Publish     │ 3. Ingest      │ 4. Store
     │    data        │    message     │    & validate  │    reading
     │                │                │                │
     ▼                ▼                ▼                ▼
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Sensor  │     │  MQTT   │     │ Celery  │     │  Alert  │
│Network  │     │ Broker  │     │ Worker  │     │ Engine  │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
     │                │                │                │
     │ 5. Continuous  │ 6. Route to    │ 7. Evaluate     │ 8. Trigger
     │    streaming   │    handlers    │    thresholds   │    alerts
     │                │                │                │
     ▼                ▼                ▼                ▼
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Grafana │     │  Email  │     │Dashboard│     │  Audit  │
│Dashboard│     │ Gateway │     │  View   │     │  Trail  │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
```

---

## LEVEL 2: DATA LINEAGE

```
┌─────────────────────────────────────────────────────────────┐
│                    SOURCE SYSTEMS                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │   SAP    │  │   HRIS   │  │  SCADA   │  │   IoT    │  │
│  │   ERP    │  │          │  │   OPC    │  │ Gateway  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
└───────┼─────────────┼─────────────┼─────────────┼─────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                    STAGING LAYER                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ETL/Integration Layer                               │  │
│  │  - Data validation                                   │  │
│  │  - Transformation                                    │  │
│  │  - Deduplication                                     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│              ENTERPRISE DATA WAREHOUSE                       │
│                                                              │
│  DIMENSION TABLES                   FACT TABLE               │
│  ┌──────────────┐                  ┌──────────────┐         │
│  │ dim_site     │                  │              │         │
│  │ dim_employee │                  │   fact_hse   │         │
│  │ dim_department│◄─────────────────│              │         │
│  │ dim_equipment│                  │              │         │
│  │ dim_contractor│                 │              │         │
│  │ dim_incident │                  │              │         │
│  │ dim_ptw      │                  │              │         │
│  │ dim_training │                  │              │         │
│  │ dim_environmental│             │              │         │
│  └──────────────┘                  └──────────────┘         │
│                                                              │
│  LINEAGE TRACKING TABLE                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  etl_metadata                                         │  │
│  │  - source_system, source_table, source_record_id      │  │
│  │  - target_table, target_record_id                     │  │
│  │  - load_timestamp, load_status                        │  │
│  │  - transformation_logic                               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                    CONSUMPTION LAYER                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │Dashboard │  │   API    │  │   AI     │  │ Reports  │  │
│  │ Views    │  │  Endpoints│  │ Service  │  │  Export  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                              │
│  AGGREGATION VIEWS                                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  v_daily_hse_summary                                  │  │
│  │  v_ptw_current_status                                 │  │
│  │  v_env_realtime                                       │  │
│  │  v_equipment_compliance                               │  │
│  │  v_active_alerts                                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## DATA RETENTION MATRIX

| Data Category | Retention Period | Archive After | Delete After | Legal Basis |
|---------------|-----------------|---------------|--------------|-------------|
| Incident Reports | 10 years | 7 years | 10 years | ISO 45001, OSHA |
| PTW Records | 7 years | 5 years | 7 years | SMKP Minerba |
| Environmental Readings | 5 years | 3 years | 5 years | ISO 14001 |
| Training Records | 5 years | 3 years | 5 years | ISO 45001 |
| Equipment Records | Equipment lifecycle | N/A | Decommission + 5 years | SMKP Minerba |
| Audit Plans | 10 years | 7 years | 10 years | ISO 45001 |
| AI Documents | 3 years | 2 years | 3 years | Internal policy |
| Audit Trail | 10 years | 7 years | 10 years | ISO 27001 |
| Login History | 2 years | 1 year | 2 years | ISO 27001 |

---

## DATA QUALITY RULES

| Rule ID | Rule Description | Validation Method | Action on Failure |
|---------|------------------|-------------------|-------------------|
| DQ-001 | All required fields populated | DB NOT NULL constraints | Reject insert/update |
| DQ-002 | Foreign key references valid | DB FK constraints | Reject insert/update |
| DQ-003 | Date ranges valid (start < end) | Application validation | Reject with error |
| DQ-004 | Numeric values within range | CHECK constraints | Reject with error |
| DQ-005 | No duplicate records | UNIQUE constraints | Reject insert |
| DQ-006 | Enum values valid | CHECK constraints | Reject with error |
| DQ-007 | Timestamps within SLA | Application validation | Alert data steward |
| DQ-008 | Audit trail complete | Application logic | Alert compliance |

---

*Document End*
