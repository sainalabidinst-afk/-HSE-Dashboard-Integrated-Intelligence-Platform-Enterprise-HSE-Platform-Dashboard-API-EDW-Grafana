# Power BI Template Skeleton — HSE Dashboard
## Developer Implementation Guide

**Platform:** Power BI Desktop (.pbit template)  
**Target:** Power BI Service (cloud), Mobile, Paginated Reports  
**Standards:** SMKP Minerba, ISO 45001, ISO 14001, SMK3  
**Audience:** Data Engineer / BI Developer

---

## 1. TEMPLATE OVERVIEW

Create a `.pbit` template file that serves as the master skeleton. Every new site/year deployment starts from this template.

### File Structure

```
HSE_Dashboard_Skeleton/
├── HSE_Dashboard.pbit                      ← Master template file
├── Documentation/
│   ├── README.md                           ← Template usage guide
│   ├── DAX_Measures.md                     ← KPI formulas + business rules
│   ├── Page_Layout_Spec.md                 ← Wireframe per page
│   └── RLS_Configuration.md                ← Role setup guide
├── Data/
│   ├── Sample_Data.xlsx                    ← Sample 100 rows per table for dev
│   └── Schema/
│       ├── star_schema_create.sql          ← EDW schema script
│       ├── etl_sample.dtsx                 ← SSIS sample package (optional)
│       └── powerquery_m.md                 ← Power Query M function examples
├── Theme/
│   ├── HSE_Theme.json                      ← Custom theme file (colors, fonts)
│   └── Bookmark_Templates/                 ← Export-print-ready PNGs
└── Deployment/
    ├── deployment_checklist.md
    └── parameter_config.json               ← Site parameter (site_id, site_name)
```

---

## 2. THEME CONFIGURATION

### 2.1 Importable Theme File (`HSE_Theme.json`)

```json
{
  "name": "HSE Corporate Theme",
  "dataColors": [
    "#2196F3", "#9C27B0", "#009688", "#FF9800", "#F44336",
    "#2E7D32", "#F57C00", "#C62828", "#455A64", "#1976D2"
  ],
  "background": "#FFFFFF",
  "foreground": "#212121",
  "tableAccent": "#2E7D32",
  "visualStyles": {
    "*": {
      "*": {
        "nulls": [ { "show": false } ],
        "responsive": true
      }
    },
    "page": {
      "*": {
        "*": [
          { "fontFamily": "Segoe UI", "fontSize": 12 },
          { "background": { "color": "#F5F5F5" } },
          { "padding": 16 }
        ]
      }
    },
    "card": {
      "*": {
        "*": [
          { "background": { "color": "#FFFFFF" }, "border": { "radius": 4 } },
          { "dataLabel": { "color": "#212121", "fontSize": 24 }},
          { "categoryLabel": { "color": "#616161", "fontSize": 11 }},
          { "title": { "color": "#616161", "fontSize": 12 }},
          { "outline": { "color": "#B0BEC5", "visible": true }}
        ]
      }
    },
    "gauge": {
      "*": {
        "*": [
          { "background": { "color": "#FFFFFF" }},
          { "dataLimit": { "show": false }},
          { "target": { "color": "#455A64", "displayUnits": true }}
        ]
      }
    },
    "timeseries": {
      "*": {
        "*": [
          { "lineWidth": 2 },
          { "showLegend": true },
          { "legend": { "position": "bottom", "showTitle": true }}
        ]
      }
    },
    "barChart": {
      "*": {
        "*": [
          { "innerRadius": 0 }
        ]
      }
    }
  }
}
```

**Import Method:** View → Customize theme → Import theme → Select JSON file

---

## 3. SEMANTIC MODEL (Datasets)

### 3.1 Table Names (MUST match EDW exactly)

| Table Name | Type | Source | Grain |
|---|---|---|---|
| `dim_datetime` | Dimension | EDW | 1 row per date |
| `dim_site` | Dimension | EDW | 1 row per site |
| `dim_department` | Dimension | EDW | 1 row per department |
| `dim_employee` | Dimension | EDW | 1 row per employee |
| `dim_equipment` | Dimension | EDW | 1 row per equipment |
| `dim_contractor` | Dimension | EDW | 1 row per contractor |
| `dim_incident` | Dimension | EDW | 1 row per incident type |
| `dim_ptw` | Dimension | EDW | 1 row per PTW |
| `dim_environmental` | Dimension | EDW | 1 row per parameter |
| `dim_training` | Dimension | EDW | 1 row per training program |
| `dim_hazard` | Dimension | EDW | 1 row per hazard type |
| `fact_hse` | Fact | EDW | Transactional daily metric |
| `ref_env_threshold` | Reference | EDW | Environmental limits per site |

### 3.2 Relationships (Star Schema)

```
dim_datetime[date_key]             → 1:* → fact_hse[date_key]
dim_site[site_id]                  → 1:* → fact_hse[site_key]
dim_department[dept_id]            → 1:* → fact_hse[dept_key]
dim_employee[employee_id]          → 1:* → fact_hse[emp_key]
dim_equipment[equipment_id]        → 1:* → fact_hse[equip_key]
dim_contractor[contractor_id]      → 1:* → fact_hse[contractor_key]
dim_incident[incident_id]          → 1:* → fact_hse[incident_key]
dim_ptw[ptw_id]                    → 1:* → fact_hse[ptw_key]
dim_hazard[hazard_id]              → 1:* → fact_hse[hazard_key]
dim_training[training_id]          → 1:* → fact_hse[train_key]

dim_site[site_id]                  → 1:* → ref_env_threshold[site_id]
dim_environmental[param_id]        → 1:* → ref_env_threshold[param_id]
```

**Cardinality:** All relationships: One-to-Many (1:*), Cross-filter: Single  
**Relationship enforce:** Off (to preserve historical data with SCD Type 2 slowly changing dims if used)

---

## 4. MEASURES LIBRARY (DAX)

Create a **separate Measures table** (not a physical table, use calculated table or dedicated measure table):

```dax
-- Measures Table (named "HSE Measures" or use dedicated display folder)

-- =============================================
-- WORKFORCE
-- =============================================
TotalManHours = SUM(fact_hse[man_hours_worked])
TotalWorkers = DISTINCTCOUNT(fact_hse[emp_key])
ManHoursThisMonth = CALCULATE([TotalManHours], DATESMTD(dim_datetime[date_key]))
ManHoursLastMonth = CALCULATE([TotalManHours], PREVIOUSMONTH(dim_datetime[date_key]))

-- =============================================
-- SAFETY KPIs
-- =============================================
LTIFR = 
VAR lti_cases = SUM(fact_hse[lti_count])
VAR man_hours = SUM(fact_hse[man_hours_worked])
RETURN
DIVIDE(lti_cases * 1000000, man_hours, BLANK())

TRIR = 
VAR incident_cases = SUM(fact_hse[lti_count]) + SUM(fact_hse[mti_count]) + SUM(fact_hse[fai_count])
VAR man_hours = SUM(fact_hse[man_hours_worked])
RETURN
DIVIDE(incident_cases * 200000, man_hours, BLANK())

SeverityRate = 
VAR days_lost = SUM(fact_hse[days_lost])
VAR man_hours = SUM(fact_hse[man_hours_worked])
RETURN
DIVIDE(days_lost * 200000, man_hours, BLANK())

DIFR = 
VAR dif_cases = SUM(fact_hse[lti_count]) + SUM(fact_hse[mti_count])
VAR man_hours = SUM(fact_hse[man_hours_worked])
RETURN
DIVIDE(dif_cases * 1000000, man_hours, BLANK())

NearMissRate = 
VAR near_miss = SUM(fact_hse[near_miss_count])
VAR workers = [TotalWorkers]
RETURN
DIVIDE(near_miss * 1000, workers, BLANK())

FAIR = DIVIDE(SUM(fact_hse[fai_count]) * 200000, [TotalManHours], BLANK())
MTIR = DIVIDE(SUM(fact_hse[mti_count]) * 200000, [TotalManHours], BLANK())

-- Cumulative (MTD / YTD)
FatalityYTD = CALCULATE(SUM(fact_hse[fatality_count]), DATESYTD(dim_datetime[date_key]), fact_hse[is_recordable] = TRUE())
LTIYTD = CALCULATE(SUM(fact_hse[lti_count]), DATESYTD(dim_datetime[date_key]), fact_hse[is_recordable] = TRUE())
TotalIncidentsMTD = CALCULATE(
  SUM(fact_hse[lti_count]) + SUM(fact_hse[mti_count]) + SUM(fact_hse[fai_count]) + SUM(fact_hse[near_miss_count]),
  DATESMTD(dim_datetime[date_key])
)

-- =============================================
-- LEADING INDICATORS
-- =============================================
ToolboxCompletionRate = DIVIDE([TotalToolboxDone], [TotalToolboxScheduled], BLANK())
JSACompletionRate = DIVIDE([TotalJSADone], [TotalJSARequired], BLANK())
ObservationCompletionRate = DIVIDE([TotalObservationsDone], [TotalObservationTarget], BLANK())
PTWComplianceRate = DIVIDE([PTWClosedValid], [PTWTotalIssued], BLANK())

TotalToolboxDone = CALCULATE(COUNTROWS(dim_ptw), dim_ptw[toolbox_completed] = TRUE())
TotalToolboxScheduled = COUNTROWS(dim_ptw)

TotalJSADone = CALCULATE(COUNTROWS(fact_hse), fact_hse[jsa_completed_before_work] = TRUE())
TotalJSARequired = DISTINCTCOUNT(fact_hse[jsa_required_flag])

TotalObservationsDone = SUM(fact_hse[observation_count])
TotalObservationTarget = 150

PTWClosedValid = CALCULATE(COUNTROWS(dim_ptw), dim_ptw[ptw_status] = "CLOSED", dim_ptw[violation_count] = 0)
PTWTotalIssued = COUNTROWS(dim_ptw)

-- =============================================
-- COMPLIANCE KPIs
-- =============================================
AuditComplianceScore = DIVIDE([TotalAuditScore], [MaxAuditScore], BLANK())
TrainingComplianceRate = DIVIDE([TrainingCompleted], [TrainingTotal], BLANK())
EquipmentCertValidRate = DIVIDE([EquipmentCertValid], [TotalEquipment], BLANK())

TotalAuditScore = SUM(fact_hse[audit_score])
MaxAuditScore = CALCULATE(MAX(dim_environmental[regulatory_limit]), fact_hse[audit_score] > 0)

TrainingCompleted = SUM(fact_hse[training_passed_count])
TrainingTotal = CALCULATE([TrainingCompleted] + SUM(fact_hse[training_failed_count]) + SUM(fact_hse[training_pending_count]))

EquipmentCertValid = CALCULATE(COUNTROWS(dim_equipment), dim_equipment[certification_expiry] > TODAY())
TotalEquipment = COUNTROWS(dim_equipment)

-- =============================================
-- ENVIRONMENTAL KPIs
-- =============================================
EnvExceedanceRate = DIVIDE(COUNTROWS(FILTER(fact_hse, fact_hse[env_exceeded] = TRUE())), COUNTROWS(fact_hse[env_reading_value]), BLANK())
CurrentEnvReading = LASTNONBLANKVALUE(fact_hse[env_reading_value], 1)

-- Dynamic threshold per site
PM25ThresholdForSite = 
CALCULATE(
  MAX(ref_env_threshold[threshold_value]),
  ref_env_threshold[site_id] = SELECTEDVALUE(dim_site[site_id]),
  ref_env_threshold[parameter_name] = "PM2.5"
)

PM25Status = 
VAR reading = [CurrentEnvReading]
VAR threshold = [PM25ThresholdForSite]
RETURN
IF(ISBLANK(reading), "NO DATA",
IF(reading > threshold * 1.5, "🔴 CRITICAL",
IF(reading > threshold, "🟠 WARNING", "🟢 NORMAL")))

-- =============================================
-- HELPER MEASURES
-- =============================================
TotalWorkersHeadcount = CALCULATE(DISTINCTCOUNT(dim_employee[employee_id]), dim_employee[employment_type] <> "CONTRACTOR")
TotalContractorHeadcount = CALCULATE(DISTINCTCOUNT(dim_employee[employee_id]), dim_employee[employment_type] = "CONTRACTOR")

HSE_RAG_Status = 
VAR kpi = [LTIFR]
RETURN
IF(kpi < 1.0, "🟢 GREEN", IF(kpi < 2.0, "🟡 AMBER", "🔴 RED"))

LastDataUpdate = MAX(fact_hse[updated_at])
```

---

## 5. PAGE SPECIFICATION

### 5.1 Page Setup (Standard for all pages)

| Property | Value |
|---|---|
| Page size | 16:9 (1920 x 1080) for desktop, custom for mobile |
| Background | White (#FFFFFF), padding 16px |
| Default font | Segoe UI, 12pt |
| Card title font | Semibold, 11pt, #616161 |
| KPI value font | Semibold, 24pt, #212121 |
| Color mode | RAG (Red/Amber/Green) consistent across all pages |
| Navigation | Page navigation tabs top center |
| Filter pane | Collapsible, saved in bookmarks |

### 5.2 Page 01: Executive Summary

**Purpose:** 30-second scan for top management  
**Users:** Top Management, Site Manager  
**Refresh:** Daily

```
┌──────────────────────────────────────────────────────────────────────┐
│  [FILTERS] Site ▼ | Month ▼ | Year ▼                        ⚙      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐              │
│  │LTIFR     │ │TRIR      │ │SEVERITY  │ │FATAL     │              │
│  │0.42 🟢   │ │1.08 🟢   │ │12.5 🟡   │ │0 YTD 🟢 │              │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐              │
│  │NEAR MISS │ │AUDIT     │ │TRAINING  │ │PTW       │              │
│  │89 🟢     │ │96% 🟢    │ │93% 🟢    │ │98% 🟢    │              │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘              │
├────────────────────────────────┬─────────────────────────────────────┤
│  📈 SAFETY TREND (TRIR 12M)   │ 🥧 INCIDENT MIX                     │
│  Line chart with benchmark     │ Donut: LTI/MTI/FAI/NearMiss/Env      │
├────────────────────────────────┴─────────────────────────────────────┤
|  🗺️ SITE COMPARISON MAP   | 📊 NEAR MISS TREND   | 🏆 TRAINING MATRIX |
|  Map with site pins        | Bar chart            | Heatmap            |
├────────────────────────────────┴─────────────────────────────────────┤
|  🚨 OPEN ACTION STATUS     | ⚠️ TOP 5 RISKS       | 🌿 ENV STATUS      |
|  Table: CAPA open + overdue | HIRA heatmap values  | Green/Amber/Red    |
└──────────────────────────────────────────────────────────────────────
```

**Components:**
- 8 KPI Cards (2 rows x 4) — use Card visual with measure
- Line chart: `TRIR` with forecast/projection
- Trend line: `NearMissRate` month-over-month
- Slicers: Site, Month, Department
- Bookmarks: `Print_ExecutiveSummary`

### 5.3 Page 02: Incident Analysis

**Purpose:** Deep-dive incident analysis for HSE Manager  
**Users:** HSE Manager, HSE Officer  
**Refresh:** Daily + Event-driven

```
┌──────────────────────────────────────────────────────────────────────┐
│  FILTERS: Date Range | Site | Severity | Cause | Agency           │
├──────────────────────────────────────────────────────────────────────┤
│  📊 PARETO CHART: Root Cause            📈 INCIDENT TREND: 12 Month │
│  Bar: Unsafe Act (40%), Unsafe Cond (25%), Equipment (20%), etc.  │
├────────────────────────────────┬─────────────────────────────────────┤
│  📋 INCIDENT REGISTER          | 🗺️ GIS LOCATION MAP               │
│  Table with drill-through      | Map pins by severity              │
├────────────────────────────────┴─────────────────────────────────────┤
|  🔍 FISHBONE / 5-WHY            | 📉 COST / LOST DAYS ANALYSIS       |
|  Visual cause analysis          | Financial impact visualization      |
└──────────────────────────────────────────────────────────────────────
```

**Drill-through:** Page 02 → Drill to Incident Detail (single incident view with photos, RCA, CAPA)  
**Bookmarks:** `Print_IncidentAnalysis`, `Filter_Critical`, `Filter_Contractor`

### 5.4 Page 03: Leading Indicators

**Purpose:** Proactive safety monitoring  
**Users:** Supervisor, HSE Officer

```
┌──────────────────────────────────────────────────────────────────────┐
│  FILTERS: Site | Shift | Month                                      │
├──────────────────────────────────────────────────────────────────────┤
|  🎯 OBSERVATION TARGET vs ACTUAL   | 🗣️ TOOLBOX COMPLETION           │
|  Gauge: Target 150, Actual 173      | Bar chart by department         │
├────────────────────────────────┬─────────────────────────────────────┤
|  📋 JSA / HIRA COMPLETION       | ✅ PRE-USE INSPECTION              │
|  Stacked bar: completed vs       | Compliance % by equipment type   |
|  required                        |                                    |
├────────────────────────────────┴─────────────────────────────────────┤
|  📈 WEEKLY SAFETY PATROL TREND | 🚶 BBS OBSERVATION HEATMAP         |
|  Line chart                     | Calendar heatmap (day x supervisor) |
└──────────────────────────────────────────────────────────────────────
```

### 5.5 Page 04: Compliance Dashboard

**Purpose:** Multi-standard compliance tracking  
**Users:** HSE Manager, Auditor

```
┌──────────────────────────────────────────────────────────────────────┐
│  FILTERS: Standard | Audit Cycle | Site                             │
├──────────────────────────────────────────────────────────────────────┤
|  📊 COMPLIANCE SCORE GAUGE (SMKP/ISO/SMK3)                          |
|  Combined gauge with per-standard breakdown                         |
├────────────────────────────────┬─────────────────────────────────────┤
|  📋 AUDIT FINDINGS TREND       | 🔴 OPEN FINDINGS                    |
|  Stacked bar: Major/Minor/Obs/  | Table with owner, due date, status │
|  Opportunity                    |                                    |
├────────────────────────────────┴─────────────────────────────────────┤
|  📈 CAPA CLOSURE RATE          | 📋 COMPLIANCE EVIDENCE LIST         |
|  Line chart with target 100%   | Links to document by clause         |
└──────────────────────────────────────────────────────────────────────
```

### 5.6 Page 05: Environmental Dashboard

**Purpose:** Environmental monitoring and trend analysis  
**Users:** Environmental Officer, HSE Officer

```
┌──────────────────────────────────────────────────────────────────────┐
│  FILTERS: Site | Parameter | Date Range                             │
├──────────────────────────────────────────────────────────────────────┤
|  🌬️ AIR QUALITY STACK                    | 💧 WATER QUALITY TABLE     |
|  Multi-line: PM2.5, PM10, SO2, NO2, CO  | Table + conditional format  |
├────────────────────────────────┬─────────────────────────────────────┤
|  🗑️ WASTE COMPOSITION            | 🌡️ GHG EMISSION TREND         |
|  Donut: Hazardous/Non-Haz/Recycle | Area chart (Scope 1 + 2 + 3)  │
├────────────────────────────────┴─────────────────────────────────────┤
|  🔊 NOISE LEVEL HEATMAP (hour x day)  | 🟢 ENV ALERT LOG              |
|  Heatmap of recorded noise levels     | Recent exceedances            |
└──────────────────────────────────────────────────────────────────────
```

---

## 6. ADVANCED FEATURES

### 6.1 Bookmarks (Print-Ready Export)

| Bookmark Name | Page | Purpose |
|---|---|---|
| `Print_ExecutiveSummary` | 01 | Print-friendly hide slicers |
| `Print_IncidentAnalysis` | 02 | Print incident register |
| `Print_Compliance` | 04 | Export audit page |
| `Print_Environment` | 05 | Environmental monitoring printout |
| `Filter_Critical` | 02,04 | Filter to show only red/amber |
| `Filter_Contractor` | 02 | Filter to contractor incidents only |

**Bookmark technique:**
1. Apply slicer selections + hide filter pane
2. View → Bookmarks → Add → name it
3. In Selection pane: hide everything except visuals for print

### 6.2 Drill-Through Configuration

| From Page | Drill-To Page | Passed Field |
|---|---|---|
| Executive Summary | Incident Detail | IncidentID |
| Incident Analysis | Incident Detail | IncidentID |
| Compliance | Audit Finding Detail | AuditID |
| Environmental | Env Reading Detail | SampleID |
| Equipment | Equipment History | EquipmentID |
| Site Comparison | Site Detail | SiteID |

### 6.3 Tooltip Pages (Custom Report Tooltips)

| Tooltip Page | Trigger Visual | Content |
|---|---|---|
| Tooltip_KPI_Detail | Any KPI card | Previous period, YoY change, benchmark |
| Tooltip_Incident | Incident bar/line | Count breakdown by type, sparkline |
| Tooltip_Employee | Any employee-related | Competency matrix, incident history |

**Setup:**
1. Create new blank page, set size: 200x150 (tiny)
2. Enable: Type: Page, Data volume: Full data
3. Add relevant visuals
4. In main visual: set Tooltip → Report type: Report page → Page name

---

## 7. POWER QUERY (M) EXAMPLES

### 7.1 Load fact_hse with Date Table Expansion

```powerquery
let
    Source = Sql.Database("edw-server.database.windows.net", "HSE_EDW"),
    fact_hse = Source{[Schema="dbo",Item="fact_hse"]}[Data],
    dim_date = Source{[Schema="dbo",Item="dim_datetime"]}[Data],
    dim_site = Source{[Schema="dbo",Item="dim_site"]}[Data],
    
    -- Join to enrich with site name
    enriched = Table.NestedJoin(fact_hse, {"site_key"}, dim_site, {"site_id"}, "Site", JoinKind.LeftOuter),
    expanded_site = Table.ExpandTableColumn(enriched, "Site", {"site_name", "site_type"}, {"site_name", "site_type"}),
    
    -- Join to enrich with date attributes
    enriched2 = Table.NestedJoin(expanded_site, {"date_key"}, dim_date, {"date_key"}, "Date", JoinKind.LeftOuter),
    final = Table.ExpandTableColumn(enriched2, "Date", {"calendar_month", "calendar_year", "month_name"}, {"calendar_month", "calendar_year", "month_name"}),
    
    -- Filter out future dates
    filtered = Table.SelectRows(final, each [date_key] <= Date.Today()),
    
    -- Remove unnecessary columns
    clean = Table.SelectColumns(filtered, {"date_key", "site_name", "site_type", "calendar_month", "calendar_year", "man_hours_worked", "lti_count", "mti_count", "fai_count", "near_miss_count", "fatality_count", "ptw_issued_count", "inspection_count", "observation_count", "training_passed_count", "equipment_down_count", "audit_score", "env_reading_value", "env_exceeded"})
in
    clean
```

### 7.2 Dynamic Threshold Lookup

```powerquery
let
    Source = Sql.Database("edw-server.database.windows.net", "HSE_EDW"),
    ref_env_threshold = Source{[Schema="dbo",Item="ref_env_threshold"]}[Data],
    
    -- Pivot to get one row per site with threshold columns
    pivoted = Table.Pivot(ref_env_threshold, List.Distinct(ref_env_threshold[parameter_name]), "parameter_name", "threshold_value", List.Sum),
    
    -- Replace null with default
    replaced = Table.ReplaceValue(pivoted, null, 999, Replacer.ReplaceValue, {"PM2.5", "PM10", "SO2", "NO2", "CO", "Noise"})
in
    replaced
```

---

## 8. ROW-LEVEL SECURITY (RLS) SETUP

### 8.1 Security Tables

Create `security_user_role` in EDW:

```sql
CREATE TABLE security_user_role (
    user_email      VARCHAR(200) PRIMARY KEY,
    user_name       VARCHAR(200),
    role_name       VARCHAR(50),  -- TopManagement / SiteManager / HSEOfficer / ICT / Auditor
    site_access     VARCHAR(500), -- comma-separated site_id, or 'ALL'
    page_access     VARCHAR(1000),-- comma-separated page list, or 'ALL'
    can_export      BOOLEAN DEFAULT FALSE,
    can_edit        BOOLEAN DEFAULT FALSE,
    can_configure_alerts BOOLEAN DEFAULT FALSE,
    is_active       BOOLEAN DEFAULT TRUE,
    expires_at      DATE           -- for auditor temporary access
);
```

### 8.2 DAX RLS Filter Expressions

Connect Power BI to `security_user_role` with `UserPrincipalName()`:

```dax
-- Site filter (for Site Manager / HSE Officer)
SiteFilter = 
VAR CurrentUser = USERPRINCIPALNAME()
VAR UserRole = LOOKUPVALUE(security_user_role[role_name], security_user_role[user_email], CurrentUser)
VAR CanAccessAll = LOOKUPVALUE(security_user_role[site_access], security_user_role[user_email], CurrentUser) = "ALL"
RETURN
IF(CanAccessAll || UserRole = "ICT", TRUE(), dim_site[site_id] IN SELECTEDVALUE(security_user_role[site_access]))

-- Page access filter (optional: used in slicer or page navigation)
PageAccessFilter = 
VAR CurrentUser = USERPRINCIPALNAME()
VAR PageAccess = LOOKUPVALUE(security_user_role[page_access], security_user_role[user_email], CurrentUser)
RETURN
CONTAINSSTRING(PageAccess, "ALL") || CONTAINSSTRING(PageAccess, "Executive Summary")

-- Export restriction via Button action (not RLS):
-- Use Power Automate to log export activity, or restrict to Premium capacity workspace with export disabled
```

**RLS Application:**  
Model → Security → Add role `[HSE - Site Filter]` → Apply `SiteFilter` on `dim_site`  
Power BI Service: Workspace → Dataset → Security → Add/Remove users to role

---

## 9. SCHEDULED REFRESH CONFIGURATION

### 9.1 Power BI Service — Data Source Credentials

| Data Source | Authentication Method | IP Allowlist |
|---|---|---|
| PostgreSQL EDW | Service Principal (OAuth) | Yes |
| InfluxDB | Token-based auth | Yes (if self-hosted) |
| REST API (CSV) | Managed Identity | N/A |

### 9.2 Refresh Schedule

| Dataset | Frequency | Time | Notes |
|---|---|---|---|
| fact_hse (historical) | Daily | 05:00 AM (after ETL) | Incremental refresh: last 90 days full, older partitions monthly |
| dim_* (master data) | Daily | 04:45 AM (before fact) | Full refresh |
| ref_env_threshold | Weekly | Sunday 01:00 AM | Change only when updated |
| Real-time (DirectQuery) | Live | Live | No refresh needed |

---

## 10. MOBILE OPTIMIZATION

### 10.1 Mobile Layout (Power BI App)

- Use **Phone layout** (View → Phone layout)
- Priority panels for Executive Summary:
  - LTIFR, TRIR, Severity, Fatality (top)
  - Incident Trend (compact)
  - Near Miss counter
  - Action status (compact table)
- Hide detailed tables, drill-throughs on desktop only

### 10.2 Grafana Mobile

- Use Grafana app (iOS/Android)
- Dashboard optimized for 375px width
- Stat panels preferred, avoid dense tables
- Alert notifications: push notification on mobile

---

## 11. DEPLOYMENT CHECKLIST

### Pre-Deployment

- [ ] Semantic model validated: all relationships active, no circular dependencies
- [ ] All measures tested against SQL manual calculation (verify LTIFR, TRIR formula)
- [ ] RLS tested: 3 different users (Top Management, Site Manager, HSE Officer)
- [ ] Page load time < 5 seconds on average dataset size
- [ ] Bookmarks tested for print (PDF export quality)
- [ ] Theme applied consistently across all pages
- [ ] Tooltips tested for all visuals
- [ ] Drill-through tested with valid/invalid IncidentID
- [ ] Time intelligence tested: YTD, MTD, rolling 12M, YoY%
- [ ] Mock data removed or replaced with placeholder before go-live
- [ ] All hardcoded site names replaced with parameters

### Go-Live

- [ ] PBI workspace created with appropriate sensitivity labels
- [ ] Data source gateway configured (if on-premises)
- [ ] Scheduled refresh enabled
- [ ] Dataset certified (if organization uses content certification)
- [ ] App workspace published: "HSE Dashboard — Production"
- [ ] Users added to workspace with appropriate roles
- [ ] Mobile app notifications testing completed

---

## 12. MAINTENANCE GUIDE

### Monthly Review

- [ ] Check measure definitions against latest KPI formula sheet
- [ ] Verify RLS membership changes (new hires, role changes)
- [ ] Validate threshold table for site-specific overrides
- [ ] Check refresh failures in Power BI Admin Portal

### Quarterly Review

- [ ] Add new page for emerging risk (if needed)
- [ ] Review page performance (slow visual optimization)
- [ ] Update sample data for UAT purposes
- [ ] Refresh power query if source schema changed

---

*End of Power BI Template Skeleton*
