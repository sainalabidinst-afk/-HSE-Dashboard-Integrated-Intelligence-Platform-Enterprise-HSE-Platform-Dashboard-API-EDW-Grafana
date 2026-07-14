# HSE DASHBOARD DESIGN SPECIFICATION
## Professional Health, Safety & Environment Analytics Platform
### Standards: SMKP Minerba · ISO 45001 · ISO 14001 · SMK3 Indonesia

---

## 1. STRUKTUR DASHBOARD

### 1.1 Daftar Halaman Dashboard

| No | Halaman | Tujuan Utama | Target User | Refresh Rate |
|---|---|---|---|---|
| 01 | Executive Summary | High-level overview untuk decision-maker | Top Management, Site Manager | Real-time (daily) |
| 02 | Operational Daily Monitor | Monitoring siklus HSE harian (PTW, patroli, patroli, inspection) | HSE Officer, Site Supervisor | Real-time / Live |
| 03 | Incident Analysis | Analisis mendalam semua kategori insiden dan near miss | HSE Manager, HSE Officer | Event-driven + Daily |
| 04 | Risk & HIRA/JSA | Manajemen risiko proaktif berbasis HIRA dan JSA | HSE Officer, Site Manager | Real-time + Weekly |
| 05 | Compliance & Audit | Skor kepatuhan multi-standar dan temuan audit | HSE Manager, Auditor | Real-time + Audit cycle |
| 06 | Environmental Performance | Monitoring dampak lingkungan dan emisi | HSE Officer, Environmental Specialist | Hourly + Daily |
| 07 | Training & Competency | Manajemen kompetensi dan K3 workforce | Site Manager, HR, HSE Officer | Weekly + Monthly |
| 08 | Equipment & PTW | Status keselamatan alat dan izin kerja | Site Supervisor, HSE Officer | Real-time |
| 09 | Predictive Safety AI | Early warning dan prediksi insiden (Advanced) | HSE Manager, Data Engineer | Real-time |
| 10 | Export & Audit Report | Laporan siap cetak untuk compliance audit | Auditor, Top Management, HSE Officer | On-demand |

### 1.2 Layout Information Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│  [EXECUTIVE SUMMARY]           <- Strategic Layer (Top Mgmt)         │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐        │
│  │ OPERATIONAL│ │ INCIDENT   │ │ RISK &     │ │COMPLIANCE │        │
│  │ DAILY      │ │ ANALYSIS   │ │ HIRA/JSA   │ │ & AUDIT   │        │
│  │ MONITOR    │ │            │ │            │ │           │        │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘        │
│                                                                      │
│  [ENVIRONMENTAL]  [TRAINING]  [EQUIPMENT/PTW]  [PREDICTIVE]          │
│                    <- Tactical Layer (HSE + Operations Teams)        │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  [PREDICTIVE SAFETY AI] <- Advanced Layer (Data Engineering)        │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 2. KPI & METRICS

### 2.1 Safety Performance Indicators

| KPI | Formula | Target | Industry Benchmark | Reporting Frequency |
|---|---|---|---|---|
| **LTIFR** (Lost Time Injury Frequency Rate) | (LTI cases × 1,000,000) / Total Man-hours | < 1.0 | Mining: 1.5–3.0, Oil & Gas: 0.5–1.5 | Monthly |
| **TRIR** (Total Recordable Incident Rate) | (Total Recordable × 200,000) / Total Man-hours | < 2.0 | Global: 1.0–2.5 | Monthly |
| **Severity Rate** | (Total Lost Days × 200,000) / Total Man-hours | < 15 | Mining: 20–50, O&G: 10–25 | Monthly |
| **DIFR** (Disabling Injury Frequency Rate) | (DIF × 1,000,000) / Total Man-hours | < 0.5 | Global: 0.3–1.0 | Quarterly |
| **Near Miss Reporting Rate** | (Near Miss × 1,000) / Total Workforce | > 15 | World-class: 20–30 | Weekly |
| **First Aid Incident Rate** | (FAI × 200,000) / Total Man-hours | < 5.0 | Mining: 5–10 | Monthly |
| **MTI Rate** (Medical Treatment Injury) | (MTI × 200,000) / Total Man-hours | < 3.0 | O&G: 2–5 | Monthly |

### 2.2 Leading / Lagging Indicators

| Tipe | Indicator | Icon | Threshold |
|---|---|---|---|
| **Leading** | Safety Observation Completed | 👁 | Target: 80% completion |
| **Leading** | PTW Issued/Closed (no violation) | 📋 | Target: 100% |
| **Leading** | JSA Completed before work | 📝 | Target: 95%+ |
| **Leading** | Toolbox Talk held | 🗣 | Target: 100% daily |
| **Leading** | Pre-use Inspection passed | ✅ | Target: 90%+ |
| **Lagging** | Fatalities | ☠ | Target: 0 |
| **Lagging** | LTI (> 1 day) | 🩺 | Target: 0 |
| **Lagging** | Environmental Incident | 🌿 | Target: 0 |
| **Lagging** | Property Damage | 🏗 | Target: minimized |

### 2.3 Compliance KPIs

| KPI | Target | Data Source |
|---|---|---|
| Audit Compliance Score | > 90% | Audit checklist items |
| PTW Compliance | 100% valid PTW | PTW system log |
| Training Compliance | > 95% scheduled | LMS data |
| Equipment Certification Valid | 100% | Asset management system |
| Calibration/Inspection Due Rate | < 5% overdue | CMMS / Inspection log |
| ISO 45001 Clause Coverage | 100% | Audit findings |
| SMK3 Kepatuhan | > 85% | Internal audit + EHS audit |
| Incident Investigation TAT | < 24 jam (critical), < 72 jam (major) | Incident management |

### 2.4 Environmental KPIs

| KPI | Unit | Target | Standard |
|---|---|---|---|
| Air Emission (CO, NOx, SOx) | mg/Nm³ | < Threshold | UNDP / Local Regulation |
| Water Discharge Quality | mg/L | < Threshold | SNI / IFC Performance Standard |
| Waste Segregation Compliance | % | 100% | ISO 14001 + PermenLHK |
| GHG Intensity | kg CO₂e / ton material | Annual reduction 3% | GHG Protocol |
| Oil Spill Incident | count | 0 | SPIDER |
| Reforestation/Mineral Acreage | ha | % of CPoW | AMDAL commitment |
| Hazardous Waste Manifest | % | 100% | B3 Waste Regulation |
| Water Consumption per Ton | m³/ton | < Baseline | ISO 14001 |

---

## 3. DESAIN VISUAL

### 3.1 Halaman Executive Summary (Power BI)

```
┌────────────────────────────────────────────────────────────────────┐
│  🔴 KPI TILES (Hero Section - 4 columns)                            │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐           │
│  │ LTIFR: 0.8│ │ TRIR: 1.9 │ │ SEVERITY: │ │ 0 FATAL   │           │
│  │ 🟢 On Targ│ │ 🟡 Watch  │ │ 12.5 🟡  │ │   ✅ YTD  │           │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘           │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐     │
│  │ EMPLOYEE HOURS   │ │ OBSERVATION RATE │ │ COMPLIANCE SCHD │     │
│  │ 2.5M hrs         │ │ 18.2 / 1k 🟢    │ │ 94% 🟢         │     │
│  └──────────────────┘ └──────────────────┘ └──────────────────┘     │
├──────────────────────────────────────────────────────────────────────
│  📈 TREND AREA (2:1 width) - Safety TRIR 12-Month Trend             │
│  Line chart with trend line, shaded green/red threshold zones       │
│  [Benchmark line: Industry average = 2.5]                           │
├───────────────────────────┬──────────────────────────────────────────┤
│  🥧 DONUT CHART           │ 📊 BAR CHART                              │
│  Incident Category Mix    │ Incidents by Department/Contractor        │
│  - LTI: 15%               │ ▓▓▓▓▓▓▓▓▓ Mining                        │
│  - MTI: 25%               │ ▓▓▓▓▓▓ Construction                      │
│  - FAI: 40%               │ ▓▓▓▓▓▓▓ ICT                             │
│  - Near Miss: 20%          │ ▓▓▓▓ O&G Support                         │
├───────────────────────────┴──────────────────────────────────────────┤
│  🗺️ MAP - Incident Hotspots (Geospatial Map)                        │
│  Red/Orange/Green pins by incident severity in last 90 days        │
└──────────────────────────────────────────────────────────────────────
```

### 3.2 Safety Color Palette (ISO 7010 Compliant)

```css
/* HSE Dashboard Color System */
:root {
  /* Status Colors */
  --hse-green: #2E7D32;     /* Safe / On Target / Compliant */
  --hse-amber: #F57C00;     /* Caution / Watch / Pending */
  --hse-red: #C62828;       /* Danger / Critical / Non-compliant */

  /* Semantic Extensions */
  --hse-green-light: #E8F5E9;
  --hse-amber-light: #FFF3E0;
  --hse-red-light: #FFEBEE;
  --hse-gray: #455A64;      /* Secondary information */
  --hse-dark: #1a1a2e;      /* Background dark mode */
  --hse-white: #FFFFFF;
  --hse-border: #B0BEC5;

  /* Chart Series */
  --series-1: #2196F3;      /* Blue - Primary series */
  --series-2: #9C27B0;      /* Purple - Secondary */
  --series-3: #009688;      /* Teal - Tertiary */
  --series-4: #FF9800;      /* Orange - Warning */
  --series-5: #F44336;      /* Red - Critical */

  /* Accessibility */
  --text-primary: #212121;
  --text-secondary: #616161;
  --text-on-green: #FFFFFF;
  --text-on-red: #FFFFFF;
}
```

### 3.3 Layout Wireframe — Halaman Operational Daily Monitor

```
┌──────────────────────────────────────────────────────────────────── Project: Site Alpha ─ Top Bar ──┐
│  Filter: [Date Range ▼] [Site ▼] [Shift ▼] [Department ▼]                              ⚙ Settings   │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│  🟢 STATUS OVERVIEW - PTW                              👷 MANPOWER                          │
│  +-----------+ +-----------+                             On-Site       On-Leave      Contractor  │
│  │ OPEN    32│ │ CLOSED 145│                             247            23            45          │
│  │ 🟡 Pending│ │ ✅ Done   │                             ████████████████████████████████████  │
│  +-----------+ +-----------+                             84% Attendance                        │
│  Fueling   3   Welding    8   Excavation 5   Electrical   2                                      │
├───────────────────────────┬───────────────────────────────────────────────────────────────────┤
│  🕔 LIVE SHIFT BOARD      │ 🚨 NEAR MISS / INCIDENT FEED (Real-time)                       │
│  08:00 - 16:00 | 245 men  │ ┌────────────────────────────────────────────────────────────┐   │
│  ├─ Mining      107       │ │ 🟡 [08:15] NM-001 | Slip near pump station | Opened     │   │
│  ├─ Construction 83      │ │     Reporter: A. Rahman | Contractor: PT. Karya        │   │
│  ├─ ICT          32      │ │ 🟠 [07:45] MTI-003 | Hand cut | Under investigation  │   │
│  └─ Support      23      │ │     Status: Dr. Siti consulted | RTH: 2 days         │   │
│  ⚠ Active Safe: 18        │ │ 🔴 [07:30] NM-002 | Fall protection unsecured       │   │
│                           │ │     Assigned: Safety Sup. Budi | Due: Aug 2, 2025     │   │
│                           │ └────────────────────────────────────────────────────────────┘   │
├───────────────────────────┴───────────────────────────────────────────────────────────────────┤
│  📋 INSPECTION QUEUE               🔧 EQUIPMENT STATUS               📑 TRAINING ALERTS            │
│  +------------------+     +------------------+          +------------------+                     │
│  │ 🟡 Dump Truck-03 │     │ Excavator CAT-01  ✅ | 🟢         │ 🟠 Defensive     │ 5 NOT STARTED │
│  │ Due: Today 14:00 │     │ Excavator CAT-02  ❌ | 🔴         │ Harness training 8 days overdue  │ │
│  | Inspector: Budi  │     │   - Brake overdue  │             │ 2 Refresher due  │                 │
│  +------------------+     +------------------+          +------------------+                     │
│  +------------------+     | Drilling RIG-05   ✅ | 🟢         | 🟡 Permit renew  │ 3 EXPIRED     │
│  | Hauling Road A   │     | Pump Station PS-03 🟡 | ⏰           | Confined Space   7 days overdue │ │
│  | 12 open issues   │     |   - Annual cert due│             | training          │                 │
│  +------------------+     +------------------+          +------------------+                     │
└───────────────────────────┴───────────────────────────────────────────────────────────────────┘
```

### 3.4 Recommendation Charts Per Page

| Halaman | Jenis Chart | Alasan Pemilihan |
|---|---|---|
| Executive Summary | Cards + Trend Line + Donut + Map | Quick digest untuk executive, visual impacto tinggi |
| Operational Daily | Live Table + Gauge + Card | Live data, actionable, direct assignment |
| Incident Analysis | Pareto Chart + Fishbone Trigger + Sankey | Root cause identification, FTA-style |
| Risk & HIRA | Heatmap (Likelihood × Severity) + Spider Chart | Risk prioritization, visual standar HIRA |
| Compliance | Stacked Bar + Heatmap + Bullet Chart | Gap analysis, audit trail clear |
| Environmental | Time Series + Stacked Area + Scatter | Trend monitoring, multi-parameter tracking |
| Training | Stacked Bar + Calendar Heatmap | Competency planning, compliance tracking |
| Equipment | Gauge + Card + P-I Chart (Pareto-Index) | Maintenance prioritization |
| Predictive AI | Scatter + Anomaly Detection + Alert Panel | Statistical anomaly, early detection |
| Export | Custom Layout + Structured Table | Audit-ready, standardized format |

---

## 4. DATA MODEL

### 4.1 Star Schema Overview

```
┌───────────────┐       ┌──────────────┐
│ dim_datetime  │        │ dim_site     │
│ (PK date)     │────┐    │ (PK site_id) │
└───────────────┘    │    └──────────────┘
                     │
┌──────────────┐     │    ┌──────────────┐      ┌────────────────┐
│ dim_employee │     │    │dim_department│      │ dim_contractor │
│   (PK emp_id)│────┤    │ (PK dept_id) │────┤ │  (PK ctr_id)   │
└──────────────┘     │    └──────────────┘      └────────────────┘
                     │
┌───────────────┐    │    ┌──────────────┐      ┌────────────────┐
│ dim_equipment │    │    │dim_incident  │      │ dim_ptw        │
│ (PK equip_id) │────┤    │  (PK inc_id) │────┤ │  (PK ptw_id)   │
└───────────────┘    │    └──────────────┘      └────────────────┘
                     │
                     │    ┌──────────────┐      ┌────────────────┐
                     │    │dim_hazard    │      │ dim_training    │
                     │────┤ (PK haz_id)  │────┤ │  (PK train_id) │
                          └──────────────┘      └────────────────┘
                                    │
                                    │
                          ┌────────▼─────────┐
                          │    fact_hse        │  <-- CENTRAL FACT TABLE
                          │   (Transaction)   │
                          │ ───────────────── │
                          │ date_key  (FK)    │
                          │ site_key  (FK)    │
                          │ dept_key  (FK)    │
                          │ emp_key   (FK)    │
                          │ equip_key (FK)    │
                          │ incident_key (FK) │
                          │ ptw_key   (FK)    │
                          │ hazard_key (FK)   │
                          │ train_key (FK)    │
                          │ man_hours (NUM)   │
                          │ metric_type       │
                          │ metric_value      │
                          │ severity_level    │
                          │ is_recordable     │
                          │ investigation_status│
                          │ created_at        │
                          │ updated_at        │
                          └───────────────────┘
```

### 4.2 Detailed Table Structures

```sql
-- =============================================
-- DIMENSION TABLES
-- =============================================

CREATE TABLE dim_datetime (
    date_key          DATE PRIMARY KEY,
    date_id           INT UNIQUE,
    full_date         DATE,
    day_of_week       INT,          -- 1-7
    day_name          VARCHAR(20),
    is_weekend        BOOLEAN,
    is_holiday        BOOLEAN,
    fiscal_year       INT,
    fiscal_quarter    INT,
    fiscal_month      INT,
    calendar_year     INT,
    calendar_quarter  INT,
    calendar_month    INT,
    week_of_year      INT,
    shift_name        VARCHAR(20),   -- Morning/Afternoon/Night/Custom
    production_period VARCHAR(20)
);

CREATE TABLE dim_site (
    site_id           VARCHAR(20) PRIMARY KEY,
    site_name         VARCHAR(200),
    site_type         VARCHAR(50),  -- Mine / Construction / ICT / O&G Support
    location_lat      DECIMAL(10, 8),
    location_long     DECIMAL(11, 8),
    zone              VARCHAR(50),  -- North Pit / Workshop / Office
    area_type         VARCHAR(50),  -- Open Pit / Underground / Surface
    site_status       VARCHAR(20),  -- Active / Inactive / Suspended
    permit_no         VARCHAR(100),
    managing_director VARCHAR(100)
);

CREATE TABLE dim_employee (
    employee_id       VARCHAR(20) PRIMARY KEY,
    employment_type   VARCHAR(50),  -- Employee / Contractor / Visitor
    nationality       VARCHAR(50),
    job_title         VARCHAR(100),
    job_grade         VARCHAR(20),
    department_id     VARCHAR(20),
    site_id           VARCHAR(20),
    certification_lvl VARCHAR(50),  -- SMKP Level 1/2/3, ISO Certified
    hse_training_due  DATE,
    medical_clearance DATE,
    drug_test_status  VARCHAR(20),
    blood_group        VARCHAR(5)
);

CREATE TABLE dim_department (
    dept_id           VARCHAR(20) PRIMARY KEY,
    dept_name         VARCHAR(100),
    dept_type         VARCHAR(50),  -- Mining / Construction / ICT / Environmental / HSE
    parent_dept_id    VARCHAR(20),
    site_id           VARCHAR(20),
    head_of_dept      VARCHAR(100),
    budget_code       VARCHAR(50)
);

CREATE TABLE dim_contractor (
    contractor_id     VARCHAR(20) PRIMARY KEY,
    contractor_name   VARCHAR(200),
    contractor_type   VARCHAR(100), -- Drilling / Hauling / Civil / MEP / Security
    risk_rating       VARCHAR(20),  -- Low / Medium / High / Critical
    hse_cert_expiry   DATE,
    insurance_valid   DATE,
    site_access_until DATE,
    hse_audit_result  VARCHAR(20),  -- Pass / Fail / Conditional
    lat_audit_date    DATE
);

CREATE TABLE dim_equipment (
    equipment_id      VARCHAR(50) PRIMARY KEY,
    equipment_type    VARCHAR(100), -- Dump Truck / Excavator / Drill / Compressor / WELDER
    category          VARCHAR(50),  -- Heavy Equipment / Lifting / Electrical / PPE
    manufacturer      VARCHAR(100),
    model             VARCHAR(50),
    serial_no         VARCHAR(100),
    installed_at      DATE,
    ownership         VARCHAR(20),  -- Owned / Leased / Rental
    current_site_id   VARCHAR(20),
    current_owner     VARCHAR(50),
    inspection_type   VARCHAR(100),
    certification_type VARCHAR(100),
    next_inspection   DATE,
    certification_expiry DATE,
    operational_hours DECIMAL(10, 2),
    days_since_last_insp INT
);

CREATE TABLE dim_incident (
    incident_id       VARCHAR(30) PRIMARY KEY,
    incident_type     VARCHAR(50),  -- LTI / MTI / FAI / Near Miss / Property Damage / Environmental
    incident_category VARCHAR(100), -- Slip / Fall / Struck / Caught / Fire / Explosion / Spill
    severity_class    VARCHAR(20),  -- Fatal / Serious / Moderate / Minor
    body_part         VARCHAR(50),  -- Head / Hand / Foot / Back / Chest (for LTI/MTI)
    agency_type       VARCHAR(20),  -- Employee / Contractor / 3rd Party / Public
    incident_cause    VARCHAR(100), -- Unsafe Act / Unsafe Condition / Equipment Failure
    preliminary_cause VARCHAR(200),
    incident_location VARCHAR(200),
    ptw_required      BOOLEAN,
    ptw_used          BOOLEAN,
    ptw_approved      BOOLEAN,
    investigation_required BOOLEAN,
    case_status       VARCHAR(20),  -- Reported / Under Investigation / Root Cause Found / Closed
    investigation_lead VARCHAR(100),
    investigation_due DATE,
    root_cause        TEXT,
    corrective_action TEXT,
    preventive_action TEXT,
    insurance_claim   BOOLEAN,
    claim_amt_usd     DECIMAL(15, 2),
    lost_days         INT,
    restricted_days   INT
);

CREATE TABLE dim_ptw (
    ptw_id            VARCHAR(30) PRIMARY KEY,
    ptw_type          VARCHAR(100), -- Hot Work / Confined Space / Electrical / Excavation / Crane
    ptw_category      VARCHAR(50),  -- Routine / Critical / Excavation / Break-in
    issued_by         VARCHAR(100),
    approved_by       VARCHAR(100),
    site_id           VARCHAR(20),
    workstation        VARCHAR(200),
    start_at          TIMESTAMP,
    end_at            TIMESTAMP,
    hazard_identified VARCHAR(200),
    mitigation_list   TEXT,
    isolation_list    TEXT,
    cna_required      BOOLEAN,
    gas_test_done     BOOLEAN,
    gas_test_result   VARCHAR(20),
    sign_in           TIMESTAMP,
    sign_out          TIMESTAMP,
    is_cancelled      BOOLEAN,
    cancellation_reason TEXT,
    violation_count   INT DEFAULT 0
);

CREATE TABLE dim_environmental (
    env_id            VARCHAR(30) PRIMARY KEY,
    parameter_type    VARCHAR(100), -- Air Quality / Water / Waste / Emission / Noise / Soil
    parameter_name    VARCHAR(100), -- PM2.5 / SO2 / NOx / BOD / CDB / Oil Content
    monitoring_point  VARCHAR(200),
    site_id           VARCHAR(20),
    lab_method        VARCHAR(100),
    regulatory_limit  DECIMAL(15, 4),
    unit_of_measure   VARCHAR(20),
    frequency         VARCHAR(20),  -- Hourly / Daily / Weekly / Monthly / Quarterly
    data_quality_flag VARCHAR(20)   -- Valid / Estimated / Outliers
);

-- =============================================
-- FACT TABLE
-- =============================================

CREATE TABLE fact_hse (
    fact_id           BIGSERIAL PRIMARY KEY,
    date_key          DATE REFERENCES dim_datetime(date_key),
    site_key          VARCHAR(20) REFERENCES dim_site(site_id),
    dept_key          VARCHAR(20) REFERENCES dim_department(dept_id),
    emp_key           VARCHAR(20) REFERENCES dim_employee(employee_id),
    equip_key         VARCHAR(50) REFERENCES dim_equipment(equipment_id),
    contractor_key    VARCHAR(20) REFERENCES dim_contractor(contractor_id),
    incident_key      VARCHAR(30) REFERENCES dim_incident(incident_id),
    ptw_key           VARCHAR(30) REFERENCES dim_ptw(ptw_id),
    hazard_key        VARCHAR(20),

    -- Workforce Metrics
    man_hours_worked  DECIMAL(12, 2),
    man_hours_allowed DECIMAL(12, 2),
    headcount_present INT,

    -- Incident Counts (zero-fill on daily)
    lti_count         INT DEFAULT 0,
    mti_count         INT DEFAULT 0,
    fai_count         INT DEFAULT 0,
    near_miss_count   INT DEFAULT 0,
    fatality_count    INT DEFAULT 0,
    first_aid_count   INT DEFAULT 0,
    property_dmg_count INT DEFAULT 0,
    env_incident_count INT DEFAULT 0,

    -- Environmental Readings
    env_reading_value DECIMAL(15, 4),
    env_limit_value   DECIMAL(15, 4),
    env_exceeded      BOOLEAN,
    env_sample_id     VARCHAR(50),

    -- PTW Metrics
    ptw_issued_count  INT DEFAULT 0,
    ptw_closed_count  INT DEFAULT 0,
    ptw_open_count    INT DEFAULT 0,
    ptw_violation_count INT DEFAULT 0,
    gas_clearance_count INT DEFAULT 0,

    -- Inspection & Observation
    inspection_count  INT DEFAULT 0,
    observation_count INT DEFAULT 0,
    observation_safe  INT DEFAULT 0,
    observation_unsafe INT DEFAULT 0,

    -- Training Metrics
    training_passed_count INT DEFAULT 0,
    training_failed_count INT DEFAULT 0,
    training_pending_count INT DEFAULT 0,

    -- Equipment
    equipment_insp_pass_count INT DEFAULT 0,
    equipment_insp_fail_count INT DEFAULT 0,
    equipment_down_count      INT DEFAULT 0,

    -- Calculated Metric (pre-computed or on-the-fly)
    metric_value      DECIMAL(15, 4),
    metric_type       VARCHAR(50),  -- LTIFR / TRIR / SEVERITY / NEAR_MISS_RATE

    -- Audit & Compliance
    audit_score       DECIMAL(5, 2),
    audit_findings    INT,
    audit_critical    INT,
    audit_major       INT,
    audit_minor       INT,

    -- Risk (HIRA)
    risk_score        DECIMAL(5, 2),
    risk_level        VARCHAR(20),  -- Very High / High / Medium / Low

    created_at        TIMESTAMP DEFAULT NOW(),
    updated_at        TIMESTAMP DEFAULT NOW(),

    -- Unique daily constraint
    CONSTRAINT uq_daily_metric UNIQUE (date_key, site_key, dept_key, metric_type)
);
```

### 4.3 Key Field Definitions

| Field | Definition | Source System | Used In |
|---|---|---|---|
| `man_hours_worked` | Total productive person-hours worked that day | HR / Timekeeping | LTIFR, TRIR calculation |
| `recordable_case_flag` | Boolean: True if meets local regulatory recordable threshold | Incident Register | TRIR |
| `root_cause` | 4M1E (Man, Machine, Material, Method, Environment) structured | Investigation report | Incident Analysis, RCA |
| `gas_clearance` | Confined Space gas test results | Gas detector log | PTW compliance |
| `env_exceeded` | Boolean flag: value > regulatory limit | Lab LIMS / IoT sensor | Environmental alert |
| `hira_risk_score` | Likelihood × Severity score | HIRA register | Risk Heatmap |
| `training_current_flag` | Is certification or refresher current | LMS = Learning Management System | Compliance score |

---

## 5. USE CASE OUTPUT

### 5.1 USE CASE 1: Power BI (Management Reporting — Weekly/Monthly)

**Scenario:** Site Manager and HSE Manager perlu membuat Weekly HSE Performance Report

**Flow:**
1. **Data Refresh:** DimRefresh (PolyBase) dari Data Warehouse → Power BI DirectQuery atau Import mode
2. **Drill-Through:** Executive Summary → Site-level Detail → Incident-level Detail → RCA
3. **Key Outputs:**
   - PDF laporan dengan template terformat (header perusahaan, logo, penandatanganan)
   - Export Excel untuk detail HIRA undangan audit
   - Power BI App untuk distribusi internal (bukan email file)

**Pages Delivered:**
- Cover Page: Executive kpi + trend Bulan Berjalan (MTD)
- Page 1: Safety KPI Bulanan (LTIFR, TRIR, Severity, Near Miss Rate)
- Page 2: Incident Register (Pivot: Severity × Cause × Location)
- Page 3: HIRA / Risk Register Summary
- Page 4: Audit / Compliance Tracker
- Page 5: Environmental Monitoring Trend
- Page 6: Training Pipeline / Gap Analysis

**Integration Points:**
- Power BI Dataflows → snowflake Primary Data Source
- Row-Level Security (RLS) → HSE Officer (Site only), Site Manager (Full site), Top Management (All sites)
- Data Alert → Email notification if LTIFR threshold breached (Power BI native alerts)

### 5.2 USE CASE 2: Grafana (Real-Time Operational Monitoring)

**Scenario:** HSE Officer di site memantau status PTW dan incident live 24/7

**Flow:**
1. **Data Source:** PostgreSQL (oltp_hse) atau InfluxDB (IoT environmental sensor)
2. **Real-time Ingestion:** MQTT / Kafka untuk IoT sensor (gas, noise, water quality), REST API untuk PTW/incident API
3. **Dashboard:** Refresh 10-15 detik

**Key Panels (Grafana):**

| Panel | Query | Visualization |
|---|---|---|
| PTW Live Status | `SELECT count(*) FROM fact_hse WHERE date_key = today() AND ptw_open_count > 0` | Stat Panel |
| Incident Stream | `SELECT * FROM fact_hse WHERE date_key = today() ORDER BY created_at DESC LIMIT 20` | Table Panel |
| Environmental Gauge | `SELECT env_reading_value FROM dim_environmental WHERE parameter_name='PM2.5' AND date_key=today()` | Gauge (red/amber/green threshold) |
| Manpower Count | `SELECT headcount_present FROM fact_hse WHERE date_key=today()` | Stat |
| Equipment Down Time | `SELECT count(*) FROM fact_hse WHERE equipment_down_count > 0` | Stat + Trend |
| Daily Near Miss Rate | `SELECT near_miss_count / NULLIF(headcount_present,0) FROM fact_hse WHERE date_key=today()` | Bar |

**Alerting Rules (Grafana Alert):**
```yaml
- alert: HighPM25Reading
  condition: query(A) > 35  # µg/m³ (WHO threshold)
  for: 5m
  annotations:
    summary: "PM2.5 levels at {{ $labels.site }} exceed safe limit"
  
- alert: NearMissRateSpike
  condition: query(A) > 3.0  # per 1000 workers
  for: 1h
```

### 5.3 USE CASE 3: Export PDF (Audit Report)

**Scenario:** Auditor eksternal datang untuk ISO 45001 / SMKP / SMK3 audit

**Flow:**
1. **Trigger:** Auditor meminta dokumen via kalender audit (Email → HSE Officer)
2. **Automation:** Power BI → Export to PDF (Scheduled) atau Paginated Report (Power BI Report Builder)
3. **Content Structure:**
   - Cover sheet: Audit period, Auditor name, Site name, sign-off
   - Policy statement acknowledgment (HSE Policy)
   - Organization chart (HSE responsibilities)
   - Scope and boundary of certification
   - KPIs Dashboard snapshot (MTD screenshot)
   - Incident Register summary (formal register format)
   - HIRA / Risk Register
   - Training Records (competency matrix printout)
   - Corrective Action Log (CAR log / NC log)
   - Environmental Monitoring Log book
   - PTW compliance log
   - Internal Audit schedule & findings
   - Management review minutes
4. **Output:** ZIP file (PDF + supporting Excel) → Audit portal upload → Auditor review

### 5.4 USE CASE 4: Excel (Detailed Analysis)

**Scenario:** Analisis tren insiden 36 bulan untuk HSE Committee presentation

**Flow:**
1. **Export Method:** Power BI → Analyze in Excel (OLAP) atau Export Raw Data from Power Query
2. **Excel Template:** HSE Analysis Template.xlsx
   - Sheet 1: Executive Summary (Pivot KPI)
   - Sheet 2: Incident Register (Power Query data pull)
   - Sheet 3: HIRA Summary (Risk matrix dynamic chart)
   - Sheet 4: Pareto Analysis (Pareto of incident causes)
   - Sheet 5: Scatter Plot (Frequency vs. Severity by department)
   - Sheet 6: Benchmarking (Company vs. Industry average)
3. **Advanced:** Microsoft Excel Online (Office 356) dengan Power BI tiles embedded
4. **Sharing:** SharePoint / Teams folder (versioned, role-based access)

---

## 6. BEST PRACTICE INTERNASIONAL

### 6.1 Industry Benchmarking

| Perusahaan | HSE Dashboard Maturity | Key Practice |
|---|---|---|
| **BHP Billiton** | Advanced | Real-time leading indicator dashboard with AI anomaly detection across global sites |
| **Rio Tinto** | Advanced | Integrated OHS + Environmental + Social (ESG) unified dashboard with automated reporting |
| **Shell** | Advanced | Trifecta: Live Ops Monitor + Compliance Tracker + Predictive analytics (digital twin concept) |
| **Caterpillar** | Intermediate | Equipment OEE (Overall Equipment Effectiveness) fused with HSE stop-work events |
| **Vale (Mining)** | Intermediate | SPICE framework (Safety Performance Indicator for Companies & Enterprises) - 5-tier indicator |
| **Woodside Energy** | Advanced | "One Site" dashboard: all operations (HSE, production, reliability) single pane of glass |
| **Anglo American** | Advanced | Zero-harm mindset: predictive models based on climate survey + behavioral observation data |
| **DAngelo International** | Developing | Focus on simplified incident-free metrics with contractor management |
| **Worley** | Intermediate | Project HSE dashboard: KPIs mapped to ISO 45001/14001 clause coverage |

### 6.2 HSE Dashboard Best Practices (World-Class)

#### 6.2.1 Information Hierarchy

```
Level 1 (Executive - 3-second grab):
└── Red/Amber/Green KPI Cards (RAG Status)
    ├── LTIFR YTD
    ├── Total fatalities YTD
    └── Major environmental incidents YTD

Level 2 (Management - 30-second scan):
├── Trend lines (12-month) with benchmark overlay
├── Pareto chart: top incident categories
├── Leading indicator completion rate
└── Audit compliance %

Level 3 (Operational - 5-minute drill):
├── Incident register with filters
├── Open investigation status
├── PTW violation trends
└── Equipment down list

Level 4 (Analytical - 30-minute analysis):
├── Root Cause Analysis (5-Why / Fishbone)
├── Hypothesis testing (correlation: training vs. incident)
├── Statistical significance testing
└── Drill-through to evidence/findings
```

#### 6.2.2 Design Principles

| Principle | Implementation |
|---|---|
| **1-Red Flag Rule** | Maximum 1 critical/red KPI per screen for executive view; rest in amber/green |
| **Traffic-Light Consistency** | RAG (Red/Amber/Green) must be consistent: Red = > 100% metric, Amber = 80-100%, Green < 80% |
| **Trend First, Detail Second** | Always show trend in detail views; detail tables are sub-views |
| **Benchmark Everywhere** | Every metric must have: company target, previous period, industry benchmark |
| **Evidence Links** | Every KPI number hyperlinks back to source (incident ID, inspection log, PTW #) |
| **Zero-Recordable First** | Design for BBS (Behavioral-Based Safety): leading indicators > lagging |
| **Data Freshness Indicator** | Show "Last updated: [timestamp]" on every page |
| ** Drill-To-Print** | Every view has 1-click Print/PDF export button |
| **Role-Based Views** | Executive View (10 KPIs) → HSE Officer (50 KPIs) → Auditor (100+ items) |

#### 6.2.3 Leading Indicator Focus

⚠️ **CRITICAL DESIGN PRINCIPLE:** Leading indicators must have 70%+ dashboard real estate; lagging indicators are summary only.

**Leading Indicators to Prioritize:**
1. Safety Observation / BBS completion rate (MOST PREDICTIVE OF FUTURE INJURY)
2. Near Miss Reporting rate (Proxy for safety culture maturity)
3. PTW compliance rate (Proxy for permit discipline)
4. Toolbox Talk completion (Frequency of safety communication)
5. Pre-start inspection compliance (Equipment safety culture)
6. Job Hazard Analysis completion before work
7. Safety suggestion submission rate
8. Training hours per employee
9. Behavioral safety observation warm/cold counts
10. Permit to Work violation rate (repeat PTW violations predict LTI)

---

## 7. BONUS (ADVANCED FEATURES)

### 7.1 Recommended Alert System (Early Warning System - EWS)

```
┌──────────────────────────────────────────────────────────────────────┐
│                    HSE EARLY WARNING SYSTEM (EWS)                     │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  LEVEL 1: DAILY AUTOMATED SCANNING (Every 06:00 AM)                 │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ Rule Engine Checks:                                            │ │
│  │ 1. LTIFR > 3 × rolling baseline  → 🟠 WARNING                 │ │
│  │ 2. LTIFR > 5 × rolling baseline  → 🔴 CRITICAL                │ │
│  │ 3. Near miss rate > 3× average    → 🟠 WARNING                 │ │
│  │ 4. 3+ near misses same shift       → 🔴 CRITICAL               │ │
│  │ 5. PTW violation rate > 20%        → 🟠 WARNING                 │ │
│  │ 6. Equipment overdue inspection + overdue = 3+ → 🔴 CRITICAL     │ │
│  │ 7. Training compliance < 90%       → 🟡 WATCH                   │ │
│  │ 8. Environmental exceedance (air) → 🔴 CRITICAL                 │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  LEVEL 2: ESCALATION PROTOCOL (3-Stage)                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐ │
│  │ Stage 1: 🟠 │  │ Stage 2: 🟡 │  │ Stage 3: 🔴                  │ │
│  │ HSE Officer │  │ HSE Manager │  │ Site Manager + Top Mgmt     │ │
│  │ SMS + Email │  │   SMS       │  │   Call Tree + War Room       │ │
│  │ Action: 4h  │  │ Action: 2h  │  │  Action: Immediate           │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────────┘ │
│                                                                      │
│  LEVEL 3: REAL-TIME TRIGGERED (Event-driven)                         │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ Event → Automatic Alert                                        │ │
│  │ • Fatality confirmed → 🔴 ALL hands (phone + email + dashboard) │ │
│  │ • Environmental spill (> dry limit) → 🟠 Environmental team     │ │
│  │ • Equipment critical failure → 🟠 Maintenance + Ops Lead       │ │
│  │ • Radiation/HAZMAT level exceed → 🔴 Immediate evacuation       │ │
│  └────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────
```

### 7.2 Automated Risk Heatmap

```
IMPLEMENTATION: Dynamic HIRA Heatmap Matrix

                    SEVERITY (z-axis) →
            │         │         │         │         │
     ┌──────┼─────────┼─────────┼─────────┼─────────┤
     │      │  Minor   │ Moderate│ Serious │ Fatal   │
HIGH ├────  │   (1)    │   (2)   │   (3)   │   (4)   │
LIKELIHOOD    ├─────────┼─────────┼─────────┤─────────┤
  ─ ► Rare (R)│   LOW   │  MEDIUM │  HIGH   │ VERY HG │
      ┌───────┼─────────┼─────────┼─────────┤─────────┤
      │Unlikly│  LOW    │  MEDIUM │  HIGH   │ EXTREME │
  M   ├───────┼─────────┼─────────┼─────────┤─────────┤
  E   │Possib │  MEDIUM │  HIGH   │ VERY HG │ CRITICAL│
  D   ├───────┼─────────┼─────────┼─────────┤─────────┤
  I   │Likely │  HIGH   │ VERY HG │ CRITICAL│ CRITICAL│
  U   ├───────┼─────────┼─────────┼─────────┤─────────┤
  M │Almost  │ VERY HG │ CRITICAL│ CRITICAL│ CRITICAL│
     └───────┴─────────┴─────────┴─────────┴─────────┘
     
ACTION LEVEL:
🟢 Low Score → Monitor (annual review)
🟡 Medium Score → Control action required (quarterly review)
🟠 High Score → Immediate action (monthly review)
🔴 Very High → STOP WORK / Emergency response

DASHBOARD INTERACTION:
• Hover: Shows specific HIRA IDs, site, work activity
• Click: Drill-down to JSA detail, incident history
• Filter: By site, work type, contractor, date
• Color coding: Matches site safety board (physical board in field office)
```

### 7.3 Predictive Safety Analytics (AI/ML Integration)

#### 7.3.1 Problem Forecasting Models

| Model | Input Features | Output |Use Case |
|---|---|---|---|
| **Incident Prediction (XGBoost / Random Forest)** | Historical incident, near miss, man-hours, weather, shift time, contractor rating, equipment age | Probability of incident in next 30 days | Trigger pre-work briefing |
| **Time-Series Anomaly (Prophet / LSTM)** | Daily incident count, man-hours, seasonal | Detects anomalous spikes | Auto-alerting during abnormal period |
| **Root Cause Mining (Association Rules / Apriori)** | Incident attributes: location, activity, weather, equipment type | "If excavation + rain + 3 days without inspection → 80% chance of incident" | Preventive action assignment |
| **Behavioral Score Prediction** | BBS observation counts, near miss patterns, training compliance | Safety culture score | Targeted intervention plan |
| **Equipment Failure Prediction** | Maintenance history, operational hours, sensor data | Risk score per equipment | Predictive maintenance scheduling |

#### 7.3.2 AI Integration Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         DATA PIPELINE                                │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Data Sources → ETL/ELT → Data Warehouse → Feature Store            │
│                           ↓                                       │
│              ┌───────────────┐    ┌─────────────────┐               │
│              │   Python       │    │   Grafana        │               │
│              │  (FastAPI +   │    │  (Real-time      │               │
│              │  Scikit-learn) │    │   Dashboard)     │               │
│              │ ──────────────│◄───│  ──────────────   │               │
│              │  Model Serving │    │  Panel: Predictions│             │
│              │  REST API: /predict │ (Score, Category,    │          │
│              └───────────────┘    │  Suggested Action)  │            │
│                                   └─────────────────┘               │
│                                                                      │
│  Power BI → Power BI Dataflow (Daily Batch) → Model Input            │
│                                                                      │
│  Alert Cross-System:                                                 │
│  ⚡ High Risk Prediction → Slack/Teams + Dashboard + SMS Manager    │
│  ⚡ Low Safety Culture → Q4 Calibration Training Plan               │
│  ⚡ Contractor Spike Risk → Re-tender / Suspension Review           │
└──────────────────────────────────────────────────────────────────────
```

#### 7.3.3 Model Monitoring & Governance

```python
# Example: Prediction Drift Detection (Seldon / Evidently AI)
Model Monitoring Checklist:
□ Weekly: Prediction distribution vs. Training distribution drift
□ Monthly: Performance metrics (Precision, Recall, F1) on labeled holdout set
□ Quarterly: Retrain model with fresh data
□ Governance: Model versioning, explainability (SHAP values), bias audit
```

### 7.4 Advanced Use Case: Digital HSE Twin (Site Simulation)

```
CONCEPT: Digital shadow of site HSE performance using:
• Time-series sensor data (dust, noise, gas)
• Video analytics (PPE compliance, dangerous acts detection)
• Mobile app BBS observations (real-time geo-tagging)
• IoT devices (personnel tracking, proximity alert)

OUTPUT PANELS:
• Live Map: Workers position (geo-fencing), equipment movement, excluded zone monitoring
• PPE Compliance Camera: Camera analytics with snippet of non-compliant footage
• Confined Space Tracker: Real-time gas readings + worker count inside
• Lifting Zone Monitor: Critical lifting op: real-time tracked load + weather overlay
• Behavioral Heatmap: Site area colored by near miss / unsafe act density

RISK: Data privacy (GDPR / local law compliance)
MITIGATION: Anonymized aggregation, no facial recognition, consent-based
```

---

## 8. IMPLEMENTATION ROADMAP

```
PHASE 1 (Weeks 1-4): Data Foundation
├─ Data Inventory & Assessment (existing ETL? data quality?)
├─ Data Dictionary Finalization
├─ Dimensional Model design & approval
├─ ETL Development (extract from HR, Incident Register, Inspection log, Lab LIMS)
└─ Dimensional Load (staging, SCD handling)

PHASE 2 (Weeks 5-8): Dashboard - Power BI & Grafana
├─ Core KPI Development (LTIFR, TRIR, Severity) in Power BI
├─ Executive Summary Page
├─ Operational Dashboard in Grafana
├─ Row-Level Security Configuration
└─ Calibration & Threshold Setting with HSE Committee

PHASE 3 (Weeks 9-12): Deep-Dive & Compliance Pages
├─ Incident Analysis Pages (root cause, Pareto)
├─ HIRA / Risk Heatmap
├─ Environmental Monitoring
├─ Training & Competency
├─ Equipment & PTW
└─ PDF Export for Audit

PHASE 4 (Weeks 13-16): Advanced Features
├─ Power BI Dataflows & Scheduled Refresh
├─ Model Training (incident prediction)
├─ Alert System Setup (Power BI native + Grafana)
├─ Model Deployment Loop (Python API)
└─ Governance & Documentation (user manual, data lineage)

PHASE 5 (Weeks 17-20): Deployment & Training
├─ UAT (User Acceptance Testing) with 3 distinct user groups
├─ Executive Presentation (demo for Top Management)
├─ HSE Officer Training (workshop)
├─ Site Manager Training (dashboard navigation)
├─ ICT Handover (maintenance runbook)
└─ Go-Live Support (hotline for 2 weeks)

MAINTENANCE CYCLE (Ongoing):
├─ Monthly Dashboard Review Meeting (KPI tuning)
├─ Quarterly Data Quality Audit (missing data, outlier check)
├─ Quarterly Model Retrain (AI model)
└─ Annual Dashboard Refresh (new KPIs, UX improvement)
```

## 9. DOCUMENTATION & GOVERNANCE

### 9.1 Required Documentation

| Doc | Owner | Purpose |
|---|---|---|
| Data Dictionary | Data Engineer | Definisi setiap field, contoh value, SCD rules |
| Dashboard User Manual | HSE + ICT | Navigasi, filter, export, alert configuration |
| KPI Formula Sheet | HSE Manager | Definisi resmi tiap KPI (sudah didiskusikan dengan HSE committee) |
| Alert Runbook | HSE + Ops | Threshold logic, escalation protocol, owner |
| Data Refresh Calendar | Data Engineer | Schedule + SLA per data source |
| Audit Report Template | HSE + Auditor | Template LM (Lista Material) untuk audit printout |

---

## 10. SUMMARY CHECKLIST (Siap Implementasi)

### 10.1 KPIs Confirmed

- [ ] LTIFR (Lost Time Injury Frequency Rate)
- [ ] TRIR (Total Recordable Incident Rate)
- [ ] Severity Rate
- [ ] DIFR (Disabling Injury Frequency Rate)
- [ ] Near Miss Reporting Rate
- [ ] First Aid Injury Rate (FAIR)
- [ ] MTI Rate (Medical Treatment Injury Rate)
- [ ] Fatality Count (cumulative MTD / YTD)
- [ ] PTW Completion Rate
- [ ] Audit Compliance Score
- [ ] Training Compliance %
- [ ] Environmental Performance Index (EPI)
- [ ] Equipment Certification Valid %
- [ ] Observation Completion Rate
- [ ] Inspection Overdue %
- [ ] Corrective Action Closure Rate

### 10.2 Data Source Confirmed

- [ ] ERP / HR: Man-hours, headcount, employee master, department
- [ ] Incident Register: All incident categories (LTI, MTI, FAI, NM, Property Damage)
- [ ] Safety Observation System: Gemba walk, BBS observations
- [ ] Inspection Management System: 5S, JSA, equipment inspection
- [ ] PTW System: Issuance, closure, violation log
- [ ] Training Management System: Schedule, completion, certification
- [ ] CMMS / Asset Management: Equipment certification, inspection, downtime
- [ ] Environmental Lab / IoT Sensor: Real-time air, water, waste, emission data
- [ ] HIRA/JSA Register: Hazard identification and risk assessment
- [ ] Audit Management: Internal, external, management review findings

### 10.3 Platform Confirmed

- [ ] Power BI (management reporting, PDF export, audit documentation)
- [ ] Grafana (real-time monitoring, live dashboard at site)
- [ ] PostgreSQL/MySQL (transactional data source)
- [ ] Python/ FastAPI (data wrangling, AI models)
- [ ] MQTT (IoT sensor real-time ingestion)
- [ ] SharePoint (Excel, document repository)

---

*Document Version: 1.0*
*Author: Senior HSE Data Analyst*
*Standards Reference: SMKP Minerba 2024, ISO 45001:2018, ISO 14001:2015, SMK3 PP No. 50/2012*
