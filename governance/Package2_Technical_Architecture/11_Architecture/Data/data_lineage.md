# Enterprise HSE Platform — Data Lineage Diagram

**Document:** Data Lineage Diagram  
**Version:** 2.1  
**Date:** 2026-07-18  
**Audience:** Data Architect, Compliance Officer, Auditor

---

## LEVEL 0: HIGH-LEVEL LINEAGE

```
┌─────────────────────────────────────────────────────────────┐
│                    SOURCE SYSTEMS                            │
│  SAP ERP | HRIS | SCADA | IoT Gateway | Manual Entry       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    INTEGRATION LAYER                         │
│  REST API | MQTT | OPC-UA | LDAP | Webhooks                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    STAGING / VALIDATION                      │
│  Input validation, deduplication, transformation            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    ENTERPRISE DATA WAREHOUSE                 │
│                                                              │
│  Dimension Tables (hse.dim_*)                               │
│  Fact Table (hse.fact_hse)                                  │
│  Audit Tables (hse.audit_*)                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    CONSUMPTION LAYER                         │
│  API Endpoints | Dashboard Views | Reports | AI | Grafana   │
└─────────────────────────────────────────────────────────────┘
```

---

## LEVEL 1: DETAILED LINEAGE BY DATA DOMAIN

### 1.1 Incident Data Lineage

```
SOURCE: HSE Officer (Web UI) / Mobile App
    │
    ▼
INTEGRATION: FastAPI POST /api/v1/operational/incidents
    │
    ▼
VALIDATION: Pydantic schema (IncidentReportCreate)
    │
    ▼
BUSINESS LOGIC: IncidentService.create_incident()
    │
    ▼
DATA ACCESS: IncidentRepository.insert()
    │
    ▼
STORAGE: hse.incident_reports (transaction table)
    │
    ▼
AGGREGATION: Trigger → hse.fact_hse (daily aggregation)
    │
    ▼
VIEW: hse.v_daily_hse_summary (dashboard view)
    │
    ▼
CONSUMPTION: Dashboard / API / Reports
```

### 1.2 Environmental Data Lineage

```
SOURCE: SCADA / IoT Gateway / Manual Entry
    │
    ▼
INTEGRATION: MQTT broker → FastAPI webhook
    │
    ▼
VALIDATION: Range check, threshold check
    │
    ▼
BUSINESS LOGIC: EnvironmentalService.create_reading()
    │
    ▼
DATA ACCESS: EnvironmentalRepository.insert()
    │
    ▼
STORAGE: hse.environmental_readings (transaction table)
    │
    ▼
AGGREGATION: Celery task → hse.fact_hse (hourly/daily)
    │
    ▼
THRESHOLD CHECK: hse.get_env_threshold() function
    │
    ▼
ALERT: hse.alerts (if threshold exceeded)
    │
    ▼
VIEW: hse.v_env_realtime (Grafana dashboard)
    │
    ▼
CONSUMPTION: Grafana / Email alert / SMS alert
```

### 1.3 AI Document Lineage

```
SOURCE: User upload / System import
    │
    ▼
INTEGRATION: FastAPI POST /api/v1/ai/documents
    │
    ▼
VALIDATION: File type, size, content check
    │
    ▼
BUSINESS LOGIC: AIService.ingest_document()
    │
    ▼
CHUNKING: Text splitter (chunk_size=1000, overlap=200)
    │
    ▼
EMBEDDING: OpenAI text-embedding-3-small
    │
    ▼
STORAGE: 
    hse.ai_documents (metadata)
    hse.ai_document_chunks (chunks + embeddings)
    │
    ▼
INDEXING: IVFFlat index on embedding vector
    │
    ▼
CONSUMPTION: RAG search → AI chat responses
```

---

## LEVEL 2: DATA LINEAGE TABLE

| Source System | Source Table/Entity | Integration Method | Target Table | Transformation | Refresh Frequency | Owner |
|---------------|---------------------|--------------------|--------------|----------------|-------------------|-------|
| SAP ERP | Employee master | REST/OData | hse.dim_employee | Map fields, validate | Daily | ICT Admin |
| HRIS | Employee org | LDAP | hse.dim_employee | Sync changes | Real-time | HR Manager |
| SCADA | Sensor readings | OPC-UA/MQTT | hse.environmental_readings | Validate, aggregate | Real-time | Engineering |
| IoT Gateway | Device data | MQTT | hse.environmental_readings | Filter, transform | Real-time | Engineering |
| Manual Entry | User input | Web UI | hse.incident_reports | Validate, enrich | On-demand | HSE Officer |
| Power BI | Reports | REST/ODBC | Read-only | Query | On-demand | HSE Director |
| Email Gateway | Notifications | SMTP/Webhook | hse.notification_logs | Log | On-demand | ICT Admin |
| SMS Gateway | Alerts | REST API | hse.notification_logs | Log | On-demand | ICT Admin |

---

## LINEAGE TRACKING IMPLEMENTATION

### ETL Metadata Table

```sql
CREATE TABLE hse.etl_metadata (
    load_id VARCHAR(50) PRIMARY KEY,
    source_system VARCHAR(100) NOT NULL,
    source_table VARCHAR(100) NOT NULL,
    source_record_id VARCHAR(100) NOT NULL,
    target_table VARCHAR(100) NOT NULL,
    target_record_id VARCHAR(100) NOT NULL,
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    load_status VARCHAR(20) CHECK (load_status IN ('pending', 'success', 'failed', 'partial')),
    transformation_logic TEXT,
    error_message TEXT,
    retry_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_etl_metadata_source ON hse.etl_metadata(source_system, source_table);
CREATE INDEX idx_etl_metadata_target ON hse.etl_metadata(target_table, target_record_id);
CREATE INDEX idx_etl_metadata_timestamp ON hse.etl_metadata(load_timestamp);
CREATE INDEX idx_etl_metadata_status ON hse.etl_metadata(load_status);
```

### Lineage Query Examples

**Trace data from source to target:**
```sql
SELECT 
    source_system,
    source_table,
    source_record_id,
    target_table,
    target_record_id,
    load_timestamp,
    load_status
FROM hse.etl_metadata
WHERE source_system = 'SCADA'
  AND source_record_id = 'SENSOR-001'
ORDER BY load_timestamp DESC;
```

**Find all downstream dependencies:**
```sql
SELECT 
    target_table,
    target_record_id,
    COUNT(*) as downstream_refs
FROM hse.etl_metadata
WHERE source_table = 'dim_site'
  AND source_record_id = 'SITE-A'
GROUP BY target_table, target_record_id;
```

**Audit data freshness:**
```sql
SELECT 
    source_system,
    MAX(load_timestamp) as last_load,
    COUNT(*) as records_loaded_today
FROM hse.etl_metadata
WHERE load_timestamp >= CURRENT_DATE
GROUP BY source_system;
```

---

## DATA QUALITY MONITORING

| Check | Description | Method | Frequency | Owner |
|-------|-------------|--------|-----------|-------|
| Completeness | All required fields populated | DB constraints | Real-time | Data Engineer |
| Validity | Values within allowed ranges | CHECK constraints | Real-time | Data Engineer |
| Consistency | Related records synchronized | Application logic | Daily | Data Engineer |
| Timeliness | Data entered within SLA | Timestamp validation | Hourly | Data Steward |
| Uniqueness | No duplicate records | UNIQUE constraints | Real-time | Data Engineer |
| Lineage completeness | All loads tracked | ETL metadata | Daily | Data Engineer |

---

*Document End*
