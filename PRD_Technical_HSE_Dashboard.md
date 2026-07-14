# HSE Dashboard — Technical PRD (Product Requirements Document)
## For Developer / Data Engineer / ICT Team

**Document Owner:** HSE Manager + ICT Lead  
**Version:** 1.0  
**Date:** 2026-07-13  
**Standards:** SMKP Minerba, ISO 45001, ISO 14001, SMK3 Indonesia  
**Platform:** Power BI (management) + Grafana (real-time ops)

---

## 1. OBJECTIVE

Build an integrated HSE intelligence platform that provides:
- **Strategic visibility** for top management (daily/weekly/monthly)
- **Operational monitoring** for site teams (real-time)
- **Compliance evidence** for auditors (ISO/SMKP/SMK3)
- **Predictive risk** signals via leading indicators + AI

---

## 2. SCOPE

| In Scope | Out of Scope (v1) |
|---|---|
| All HSE KPIs listed in Blueprint | Mobile native app (web responsive only) |
| Power BI + Grafana | Custom ERP module development |
| PDF/Excel export | Blockchain audit trail |
| Real-time IoT integration | IoT hardware procurement |
| Rule-based EWS | Advanced AI model (model skeleton only) |

---

## 3. DATA SOURCES

| System | Data | Integration Method | Owner |
|---|---|---|---|
| ERP / HRIS | Man-hours, headcount, org structure | API / DB View | ICT |
| Incident Register | Incident master, investigation | API / CSV drop | HSE Officer |
| Safety Observation | BBS observation, patrol log | API / CSV drop | HSE Officer |
| Audit System | Audit checklist, findings, CAPA | API / CSV drop | Auditor |
| LIMS / IoT Sensor | Air quality, noise, water, emission | MQTT / REST API | ICT |
| CMMS / Asset Mgmt | Equipment cert, inspection, downtime | API / DB View | Maintenance |
| LMS | Training schedule, completion, cert | API / CSV drop | HR |
| PTW System | PTW issuance, closure, violation | API / CSV drop | Ops Supervisor |
| HIRA/JSA Register | Hazard ID, risk score, mitigation | API / CSV drop | HSE Officer |
| Contractor Management | Contractor rating, audit, training | API / CSV drop | Procurement |

### 3.1 Current System Integration Assessment
> **Catatan:** Bagian ini diisi berdasarkan sistem yang aktif di organisasi. Jika belum ada sistem tertentu, gunakan kolom "Interim Solution".

| No | Sistem yang Dibutuhkan | Sistem yang Sudah Ada | Metode Integrasi (v1) | Interim Solution (jika belum ada) | PIC |
|---|---|---|---|---|---|
| 1 | Man-hours & headcount | ERP/HRIS (misal: SAP, Oracle,local ERP) | API via middleware / DB view | Spreadsheet harian (upload CSV) | ICT + HR |
| 2 | Incident Register | Excel / Google Sheets / Sistem HSE terpisah | API / CSV drop folder | Google Form → Sheets → CSV drop | HSE Officer |
| 3 | Safety Observation | Apps HSE (misal: SiteAware, SafetyCulture) | REST API | Google Form / Microsoft Form | HSE Officer |
| 4 | Audit & CAPA | Sistem internal / Excel | CSV drop / manual import | Audit checklist Excel → CSV | Auditor + HSE |
| 5 | LIMS / Environmental | Excel LIMS / IoT sensor lokal | MQTT broker → InfluxDB | Manual input Excel → CSV drop | Environmental Officer |
| 6 | CMMS / Asset Mgmt | Sistem maintenance (misal: SAP PM, eMaint, excel) | API / DB view | Excel export → CSV drop | Maintenance |
| 7 | LMS | Sistem training internal / Excel | API / CSV drop | Training Excel → CSV drop | HR + HSE |
| 8 | PTW System | Sistem PTW digital / Excel | API / CSV drop | PTW Excel → CSV drop | Ops Supervisor |
| 9 | HIRA/JSA Register | Excel / Apps digital | CSV drop | Excel template → CSV | HSE Officer |
| 10 | Contractor Management | Excel / Portal procurement | CSV drop | Contractor Excel → CSV | Procurement + HSE |

**Golden Rule:** Semua data source harus mendarat di **Enterprise Data Warehouse (EDW)** sebelum masuk dashboard. Tidak ada koneksi langsung dashboard-to-source.

---

## 4. TECHNICAL ARCHITECTURE

```
┌────────────────────────────────────────────────────────────────────┐
│                        SOURCE SYSTEMS                              │
│  ERP | Incident | Observation | Audit | LIMS | CMMS | LMS | PTW   │
└──────────────────────────────┬─────────────────────────────────────┘
                               │ ETL (PolyBase / ADF / Airflow)
                               ▼
┌────────────────────────────────────────────────────────────────────┐
│              LANDING ZONE / DATA LAKE (Bronze)                     │
│  Raw files (Parquet/CSV) with audit trail & ingestion timestamp    │
└──────────────────────────────┬─────────────────────────────────────┘
                               │ Transformation (dbt / T-SQL)
                               ▼
┌────────────────────────────────────────────────────────────────────┐
│         STAGING / CLEAN ROOM (Silver)                              │
│  Validated, deduplicated, standardized data                        │
└──────────────────────────────┬─────────────────────────────────────┘
                               │ Star Schema load (SCD Type 1/2)
                               ▼
┌────────────────────────────────────────────────────────────────────┐
│           ENTERPRISE DATA WAREHOUSE (Gold)                         │
│  dim_* + fact_hse (see Data Model section in spec)                │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                 │
              ▼                                 ▼
     ┌─────────────────┐             ┌──────────────────┐
     │   Power BI       │             │   Grafana         │
     │ - Import Mode    │             │ - PostgreSQL DS   │
     │ - DirectQuery    │             │ - InfluxDB (IoT)  │
     │ - Dataflows      │             │ - Alertmanager    │
     └─────────────────┘             └──────────────────┘
```

---

## 5. DATA MODEL (RECAP)

### 5.1 Fact Table

```sql
fact_hse (transactional grain: 1 row per metric per day per site/department)
  - date_key (FK to dim_datetime)
  - site_key (FK to dim_site)
  - dept_key (FK to dim_department)
  - emp_key (FK to dim_employee)
  - equip_key (FK to dim_equipment)
  - contractor_key (FK to dim_contractor)
  - incident_key (FK to dim_incident)
  - ptw_key (FK to dim_ptw)
  - hazard_key (FK to dim_hazard)
  - man_hours_worked
  - lti_count, mti_count, fai_count, near_miss_count, fatality_count
  - env_reading_value, env_exceeded
  - ptw_issued_count, ptw_violation_count
  - inspection_count, observation_count
  - training_passed_count
  - equipment_down_count
  - audit_score
  - metric_value, metric_type (LTIFR, TRIR, etc.)
```

### 5.2 Dimension Tables

```
dim_datetime
dim_site
dim_employee
dim_department
dim_contractor
dim_equipment
dim_incident
dim_ptw
dim_environmental
dim_training
dim_hazard
```

---

## 6. POWER BI CONFIGURATION

### 6.1 Data Source Configuration

| Item | Specification |
|---|---|
| Dataset Mode | Import (for historical) + DirectQuery (for real-time) |
| Dataflows | Yes — separate from semantic model, for staging |
| Scheduled Refresh | Daily at 05:00 AM (after ETL completes) |
| Incremental Refresh | Enabled on fact_hse (partition by date) |
| Connection | Service Principal (no user credential) |
| Data Source IP Allowlist | Restrict to Power BI service IP range |

### 6.2 Security

| Feature | Implementation |
|---|---|
| RLS (Row-Level Security) | Site-level filter: HSE Officer sees own site only; HSE Manager sees all sites; Top Management sees all |
| Data masking | Sensitive fields (employee medical, insurance) masked via DAX |
| Export restriction | Top Management can export PDF; HSE Officer can export CSV; Viewer read-only |
| Audit log | Power BI audit log enabled in Admin Portal |

### 6.3 Report Structure

```
HSE_Dashboard.pbit (template)
├── Page 01: Executive Summary
├── Page 02: Incident Analysis
├── Page 03:Leading Indicators
├── Page 04: Compliance Dashboard
├── Page 05: Environmental Dashboard
├── Page 06: PTW Dashboard
├── Page 07: HIRA / Risk Dashboard
├── Page 08: Equipment Safety
├── Page 09: Training Dashboard
├── Page 10: Contractor Dashboard
├── Page 11: Real-Time Operations
├── Page 12: Predictive Analytics
└── Page 13: Audit Export (print-ready)
```

### 6.4 Calculated Columns & Measures (DAX)

```dax
-- LTIFR
LTIFR = DIVIDE(SUM(fact_hse[lti_count]) * 1000000, SUM(fact_hse[man_hours_worked]), 0)

-- TRIR
TRIR = DIVIDE(
  (SUM(fact_hse[lti_count]) + SUM(fact_hse[mti_count]) + SUM(fact_hse[fai_count])) * 200000,
  SUM(fact_hse[man_hours_worked]), 0)

-- Severity Rate
SeverityRate = DIVIDE(SUM(fact_hse[days_lost]) * 200000, SUM(fact_hse[man_hours_worked]), 0)

-- Near Miss Rate
NearMissRate = DIVIDE(SUM(fact_hse[near_miss_count]) * 1000, [TotalWorkers], 0)

-- Audit Compliance %
AuditCompliance = DIVIDE([TotalScore], [MaxScore], 0)

-- Training Compliance %
TrainingCompliance = DIVIDE([TrainingCompleted], [TrainingTotal], 0)

-- PTW Compliance %
PTWCompliance = DIVIDE([PTWClosedValid], [PTWTotalIssued], 0)

-- Environmental Exceedance %
EnvExceedanceRate = DIVIDE([EnvExceedances], [EnvTotalReadings], 0)
```

### 6.5 Bookmarks for Print-Ready Export

- Each page has a bookmark named `Print_[PageName]`
- Filter pane hidden, navigation hidden via bookmark
- Page size: A4 landscape for audit reports
- Page width: 1900px, Height: 1080px (Power BI view)

---

## 7. GRAFANA CONFIGURATION

### 7.1 Data Sources

| Source | Type | Purpose |
|---|---|---|
| PostgreSQL | SQL | Fact HSE summary, master data |
| InfluxDB | Time-series | IoT sensor (air quality, noise, gas) |
| MySQL (optional) | SQL | Legacy systems |

### 7.2 Panel Types Per Metric

| Metric | Panel Type | Refresh |
|---|---|---|
| PTW Open/Closed Count | Stat | 15s |
| Incident Stream (last 20) | Table | 30s |
| Manpower Present | Stat | 60s |
| Environmental Gauge (PM2.5) | Gauge | 10s |
| Environmental Trend (24h) | Time Series | 10s |
| Near Miss Rate (daily) | Bar | 5m |
| Equipment Down | Stat + Alert | 60s |
| Audit Score Trend | Stat | Daily |
| Training Expiry Alert | Alert List | Daily |

### 7.3 Alerting Rules (Grafana)

```yaml
groups:
  - name: HSE_Alerts
    rules:
      - alert: HighPM25
        expr: pm25_reading > 35
        for: 5m
        labels:
          severity: critical
          site: "{{ $labels.site }}"
        annotations:
          summary: "PM2.5 di {{ $labels.site }} melebihi ambang batas WHO"

      - alert: NearMissSpike
        expr: near_miss_rate_hourly > 5
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Near miss rate tinggi pada shift ini"

      - alert: PTWExpiring
        expr: ptw_expires_in_hours < 2
        for: 0m
        labels:
          severity: critical
        annotations:
          summary: "PTW {{ $labels.ptw_id }} akan berakhir dalam 2 jam"

      - alert: EquipmentCritical
        expr: equipment_overdue_inspection_count > 0
        for: 0m
        labels:
          severity: warning
        annotations:
          summary: "{{ $labels.equipment_id }} melebihi jadwal inspeksi"
```

### 7.4 Grafana Dashboard Structure

```json
{
  "dashboard": {
    "title": "HSE Real-Time Operations",
    "tags": ["hse", "operations"],
    "timezone": "Asia/Jakarta",
    "panels": [
      {
        "title": "PTW Status",
        "type": "stat",
        "datasource": "PostgreSQL-HSE",
        "targets": [{ "expr": "SELECT ... FROM fact_hse WHERE date = CURRENT_DATE" }],
        "fieldConfig": {
          "defaults": { "color": { "mode": "thresholds" }, "thresholds": {
            "steps": [
              { "value": 0, "color": "green" },
              { "value": 5, "color": "yellow" },
              { "value": 10, "color": "red" }
            ]
          }}
        }
      }
    ]
  }
}
```

---

## 8. USER ROLE MATRIX

### 8.1 High-Level Access Summary

| Role | Power BI Access | Grafana Access | Actions |
|---|---|---|---|
| **Top Management** | All sites, all pages | Viewer (all) | View, Export PDF |
| **Site Manager** | Assigned site(s) only | Editor (assigned site) | View, Export, Drill-through, Schedule refresh |
| **HSE Manager** | All sites, all pages | Editor | View, Edit, Export, Configure Alerts |
| **HSE Officer** | Assigned site only | Editor | View, Edit (own site), Export |
| **ICT / Data Engineer** | Admin | Admin | Full access, manage data sources, ETL |
| **Auditor (external)** | Read-only (specific pages) | No access | View (audit pages only), Export PDF |
| **Ops Supervisor** | Assigned site, ops pages only | Editor (real-time ops) | View, Export |

### 8.2 Page-Level Permission Matrix (Power BI + Grafana)
> **Kunci:** V = View, E = Edit/Input, X = Export, D = Drill-through, A = Admin/Configure Alert, - = No Access

| Halaman | Top Mgmt | Site Manager | HSE Manager | HSE Officer | ICT | Auditor | Ops Supervisor |
|---|---|---|---|---|---|---|---|
| **01. Executive Summary** | V, X | V, X | V, X | V, X | V, A | V, X | V, X |
| **02. Incident Analysis** | V, D, X | V, D, X | V, E, D, X | V, E, D, X | V, A | V, D, X | V, D, X |
| **03. Leading Indicators** | V, X | V, X | V, E, X | V, E, X | V, A | V, X | V, X |
| **04. Compliance Dashboard** | V, D, X | V, D, X | V, E, D, A, X | V, D, X | V, A | V, D, X | V, D |
| **05. Environmental** | V, X | V, D, X | V, D, A, X | V, D, X | V, A | V, D | V, D |
| **06. PTW Dashboard** | V, X | V, D, X | V, E, A, X | V, E, D, X | V, A | V, D | V, E, D, X |
| **07. HIRA / JSA** | V, D, X | V, D, X | V, E, D, X | V, E, D, X | V, A | V, D, X | V, D, X |
| **08. Equipment Safety** | V, X | V, D, X | V, E, A, X | V, E, D, X | V, A | V, D, X | V, E, D, X |
| **09. Training Dashboard** | V, D, X | V, D, X | V, E, D, X | V, D, X | V, A | V, D, X | V, D |
| **10. Contractor Dashboard** | V, X | V, X | V, E, X | V, E, X | V, A | V, X | V, X |
| **11. Real-Time Operations** | V, X | V, X | V, A, X | V, A, X | V, A | - | V, E, A, X |
| **12. Predictive Analytics** | V, D, X | V, D, X | V, A, X | V, X | V, A | V, X | V, X |
| **13. Audit Export** | V, X | V, X | V, X | V, X | V, X | V, X | V, X |

**Catatan Penting:**
- **Export PDF**: Hanya untuk halaman yang dibutuhkan untuk audit/reporting. Audit Export page dilindungi password/token.
- **Drill-through**: Akses ke level individu (employee) hanya untuk HSE Manager, HSE Officer (own site), dan Site Manager.
- **Edit/Input**: Input data langsung ke dashboard hanya di Grafana operational pages. Entry data medan (field) selalu melalui sistem source (bukan edit di dashboard).
- **Auditor**: Akses baca saja, timed access (expire setelah audit selesai).

---

## 9. THRESHOLD & REGULATORY LIMITS

### 9.1 Environmental Thresholds (Indonesia Standard + WHO)

| Parameter | Unit | Threshold | Source | Alert Level |
|---|---|---|---|---|
| PM2.5 | µg/m³ | 35 (24h avg) | PermenLHK No. 13/2023 | > 35 = 🟠, > 55 = 🔴 |
| PM10 | µg/m³ | 150 (24h avg) | PermenLHK | > 150 = 🟠, > 250 = 🔴 |
| SO2 | µg/m³ | 365 (24h avg) | PermenLHK | > 365 = 🟠 |
| NO2 | µg/m³ | 200 (24h avg) | PermenLHK | > 200 = 🟠 |
| CO | mg/m³ | 10 (8h avg) | PermenLHK | > 10 = 🟠 |
| Noise (Leq) | dB(A) | 85 (8h) | PermenLHK | > 85 = 🟠, > 90 = 🔴 |
| Vibration | mm/s | 5 (8h) | SNI 03-6391 | > 5 = 🟠 |

### 9.2 HSE Performance Thresholds

| KPI | Green | Amber | Red | Action on Red |
|---|---|---|---|---|
| LTIFR | < 1.0 | 1.0–2.0 | > 2.0 | Immediate investigation |
| TRIR | < 2.0 | 2.0–3.5 | > 3.5 | War room + root cause |
| Near Miss Rate | > 15/1k | 10–15/1k | < 10/1k | Culture investigation |
| Audit Compliance | > 95% | 85–95% | < 85% | Management review |
| Training Compliance | > 95% | 85–95% | < 85% | Immediate schedule |
| PTW Compliance | 100% | 95–99% | < 95% | Supervisor briefing |
| Equipment Cert Valid | 100% | 95–99% | < 95% | Maintenance escalation |

### 9.3 Location-Specific Environmental Thresholds
> **Catatan:** Baku mutu lingkungan dapat berbeda antar lokasi operasi (kabupaten/kota). Threshold di bawah adalah default WHO + PermenLHK, tetapi **harus dioverride** berdasarkan AMDAL/IPP lokasi.

| Parameter | Unit | Default Threshold (WHO/PermenLHK) | Lokasi | Override Value | Sumber Peraturan | Alert Level |
|---|---|---|---|---|---|---|
| PM2.5 | µg/m³ | 35 (24h avg) | Site Alpha (Kab. Kutai) | 50 | AMDAL 2023 | > 50 = 🟠, > 80 = 🔴 |
| PM10 | µg/m³ | 150 (24h avg) | Site Alpha (Kab. Kutai) | 200 | AMDAL 2023 | > 200 = 🟠, > 300 = 🔴 |
| PM2.5 | µg/m³ | 35 (24h avg) | Site Beta (Kota Balikpapan) | 35 | PermenLHK No.13/2023 | > 35 = 🟠, > 55 = 🔴 |
| Noise (Leq) | dB(A) | 85 (8h) | Site Alpha (area industri) | 90 | Perda Kab. Kutai | > 90 = 🟠, > 100 = 🔴 |
| Noise (Leq) | dB(A) | 85 (8h) | Site Beta (camp/kantor) | 85 | PermenLHK | > 85 = 🟠, > 90 = 🔴 |
| SO2 | µg/m³ | 365 (24h avg) | Semua site | 365 | PermenLHK | > 365 = 🟠 |
| NO2 | µg/m³ | 200 (24h avg) | Semua site | 200 | PermenLHK | > 200 = 🟠 |
| CO | mg/m³ | 10 (8h avg) | Semua site | 10 | PermenLHK | > 10 = 🟠 |
| Vibration | mm/s | 5 (8h) | Semua site | 5 | SNI 03-6391 | > 5 = 🟠 |
| Water Discharge (BOD) | mg/L | 30 | Site Alpha | 30 | AMDAL | > 30 = 🟠 |
| Water Discharge (pH) | pH unit | 6-9 | Site Alpha | 6-9 | AMDAL | Outside 6-9 = 🟠 |

**Implementasi di Dashboard:**
- Tambah field `location_override` di tabel `dim_site` atau tabel lookup `ref_env_threshold`
- Grafana/alert engine membaca threshold berdasarkan `site_id`, bukan hardcoded
- Power BI: gunakan SWITCH/IF DAX untuk threshold dinamis berdasarkan site
- Admin dapat update threshold tanpa deploy ulang (dim_env_threshold table controlled by HSE Manager)

---

## 10. IMPLEMENTATION ROADMAP

| Phase | Duration | Deliverable |
|---|---|---|
| 1. Data Foundation | Week 1-4 | Data Inventory, Data Dictionary, ETL pipeline, EDW star schema |
| 2. Core Dashboard | Week 5-8 | Power BI Executive + Operational + Grafana live dashboard |
| 3. Deep-Dive Pages | Week 9-12 | All remaining Power BI pages, PDF export, Excel template |
| 4. Advanced | Week 13-16 | EWS, Risk Heatmap, AI model skeleton, feature store |
| 5. Deployment | Week 17-20 | UAT, Training, Documentation, Go-live |

---

## 11. DELIVERABLES CHECKLIST

### Developer / ICT Deliverables

- [ ] Data Warehouse schema (DBScript folder with CREATE TABLE scripts)
- [ ] ETL pipeline (ADF pipeline or Airflow DAG or dbt project)
- [ ] Power BI semantic model (.pbix) with DAX measures
- [ ] Grafana dashboard JSON (exportable)
- [ ] Alertmanager / Grafana Alert rules YAML
- [ ] API endpoint for incident/PTW/fact ingestion (optional)
- [ ] Data quality validation job (null check, range check, referential integrity)

### HSE Deliverables

- [ ] KPI Formula Sheet (signed by HSE Committee)
- [ ] Threshold matrix per parameter
- [ ] User role matrix (signed by management)
- [ ] Data dictionary (business terms)
- [ ] Audit documentation template (PDF structure)

### Project Management Deliverables

- [ ] UAT Test Script
- [ ] Training materials (slide + video)
- [ ] Maintenance runbook
- [ ] Go-live checklist

---

## 12. SUCCESS METRICS (POST-IMPLEMENTATION)

| Metric | Target | Measurement |
|---|---|---|
| Dashboard adoption | > 80% weekly active users (HSE team) | Power BI usage metrics |
| Data latency | < 24 hours for management reports | ETL SLA monitor |
| Real-time dashboard latency | < 30 seconds | Grafana panel refresh |
| Audit report generation | < 5 minutes (automated) | Manual test |
| Incident investigation TAT | < 72 hours (major), < 24h (critical) | Incident register |
| Near Miss reporting rate | +50% within 6 months | Before/after comparison |
| PTW compliance | > 98% | PTW register |
| User satisfaction | > 4.0/5.0 | Survey |

---

*End of Technical PRD — For questions, contact ICT Lead + HSE Manager*
