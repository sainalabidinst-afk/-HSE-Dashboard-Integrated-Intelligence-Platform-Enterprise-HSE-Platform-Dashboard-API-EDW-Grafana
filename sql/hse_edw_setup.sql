-- =============================================
-- HSE ENTERPRISE DATA WAREHOUSE
-- Standards: SMKP Minerba · ISO 45001 · ISO 14001 · SMK3
-- Created: 2026-07-13
-- =============================================

-- =============================================
-- EXTENSION & SETUP
-- =============================================
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE SCHEMA IF NOT EXISTS hse;

-- =============================================
-- DIMENSION TABLES
-- =============================================

CREATE TABLE hse.dim_datetime (
    date_key          DATE PRIMARY KEY,
    day_of_week       INT NOT NULL,
    day_name          VARCHAR(20) NOT NULL,
    is_weekend        BOOLEAN NOT NULL,
    is_holiday        BOOLEAN DEFAULT FALSE,
    calendar_year     INT NOT NULL,
    calendar_quarter  INT NOT NULL,
    calendar_month    INT NOT NULL,
    fiscal_year       INT,
    fiscal_quarter    INT,
    week_of_year      INT,
    shift_name        VARCHAR(20),
    production_period VARCHAR(20)
);

CREATE TABLE hse.dim_site (
    site_id           VARCHAR(20) PRIMARY KEY,
    site_name         VARCHAR(200) NOT NULL,
    site_type         VARCHAR(50),
    location_lat      DECIMAL(10, 8),
    location_long     DECIMAL(11, 8),
    zone              VARCHAR(100),
    area_type         VARCHAR(50),
    site_status       VARCHAR(20) DEFAULT 'Active',
    permit_no         VARCHAR(100),
    managing_director VARCHAR(100),
    timezone          VARCHAR(50) DEFAULT 'Asia/Jakarta',
    active_from       DATE DEFAULT CURRENT_DATE,
    active_to         DATE DEFAULT '9999-12-31'
);

CREATE TABLE hse.dim_employee (
    employee_id       VARCHAR(20) PRIMARY KEY,
    employment_type   VARCHAR(50),
    nationality       VARCHAR(50),
    job_title         VARCHAR(100),
    job_grade         VARCHAR(20),
    department_id     VARCHAR(20),
    site_id           VARCHAR(20),
    certification_lvl VARCHAR(100),
    hse_training_due  DATE,
    medical_clearance DATE,
    drug_test_status  VARCHAR(20),
    blood_group       VARCHAR(5),
    active_from       DATE DEFAULT CURRENT_DATE,
    active_to         DATE DEFAULT '9999-12-31'
);

CREATE TABLE hse.dim_department (
    dept_id           VARCHAR(20) PRIMARY KEY,
    dept_name         VARCHAR(100) NOT NULL,
    dept_type         VARCHAR(50),
    parent_dept_id    VARCHAR(20),
    site_id           VARCHAR(20),
    head_of_dept      VARCHAR(100),
    budget_code       VARCHAR(50),
    active_from       DATE DEFAULT CURRENT_DATE,
    active_to         DATE DEFAULT '9999-12-31'
);

CREATE TABLE hse.dim_contractor (
    contractor_id     VARCHAR(20) PRIMARY KEY,
    contractor_name   VARCHAR(200) NOT NULL,
    contractor_type   VARCHAR(100),
    risk_rating       VARCHAR(20),
    hse_cert_expiry   DATE,
    insurance_valid   DATE,
    site_access_until DATE,
    hse_audit_result  VARCHAR(20),
    lat_audit_date    DATE,
    active_from       DATE DEFAULT CURRENT_DATE,
    active_to         DATE DEFAULT '9999-12-31'
);

CREATE TABLE hse.dim_equipment (
    equipment_id      VARCHAR(50) PRIMARY KEY,
    equipment_type    VARCHAR(100),
    category          VARCHAR(50),
    manufacturer      VARCHAR(100),
    model             VARCHAR(50),
    serial_no         VARCHAR(100),
    installed_at      DATE,
    ownership         VARCHAR(20),
    current_site_id   VARCHAR(20),
    current_owner     VARCHAR(50),
    inspection_type   VARCHAR(100),
    certification_type VARCHAR(100),
    next_inspection   DATE,
    certification_expiry DATE,
    operational_hours DECIMAL(10, 2) DEFAULT 0,
    days_since_last_insp INT,
    active_from       DATE DEFAULT CURRENT_DATE,
    active_to         DATE DEFAULT '9999-12-31'
);

CREATE TABLE hse.dim_incident (
    incident_id       VARCHAR(30) PRIMARY KEY,
    incident_type     VARCHAR(50),
    incident_category VARCHAR(100),
    severity_class    VARCHAR(20),
    body_part         VARCHAR(50),
    agency_type       VARCHAR(20),
    incident_cause    VARCHAR(100),
    preliminary_cause VARCHAR(200),
    incident_location VARCHAR(200),
    ptw_required      BOOLEAN DEFAULT FALSE,
    ptw_used          BOOLEAN DEFAULT FALSE,
    ptw_approved      BOOLEAN DEFAULT FALSE,
    investigation_required BOOLEAN DEFAULT FALSE,
    case_status       VARCHAR(20) DEFAULT 'Reported',
    investigation_lead VARCHAR(100),
    investigation_due DATE,
    root_cause        TEXT,
    corrective_action TEXT,
    preventive_action TEXT,
    insurance_claim   BOOLEAN DEFAULT FALSE,
    claim_amt_usd     DECIMAL(15, 2) DEFAULT 0,
    lost_days         INT DEFAULT 0,
    restricted_days   INT DEFAULT 0
);

CREATE TABLE hse.dim_ptw (
    ptw_id            VARCHAR(30) PRIMARY KEY,
    ptw_type          VARCHAR(100),
    ptw_category      VARCHAR(50),
    issued_by         VARCHAR(100),
    approved_by       VARCHAR(100),
    site_id           VARCHAR(20),
    workstation       VARCHAR(200),
    start_at          TIMESTAMP,
    end_at            TIMESTAMP,
    hazard_identified VARCHAR(200),
    mitigation_list   TEXT,
    isolation_list    TEXT,
    cna_required      BOOLEAN DEFAULT FALSE,
    gas_test_done     BOOLEAN DEFAULT FALSE,
    gas_test_result   VARCHAR(20),
    sign_in           TIMESTAMP,
    sign_out          TIMESTAMP,
    is_cancelled      BOOLEAN DEFAULT FALSE,
    cancellation_reason TEXT,
    violation_count   INT DEFAULT 0,
    ptw_status        VARCHAR(20) DEFAULT 'OPEN'
);

CREATE TABLE hse.dim_environmental (
    env_id            VARCHAR(30) PRIMARY KEY,
    parameter_type    VARCHAR(100),
    parameter_name    VARCHAR(100),
    monitoring_point  VARCHAR(200),
    site_id           VARCHAR(20),
    lab_method        VARCHAR(100),
    regulatory_limit  DECIMAL(15, 4),
    unit_of_measure   VARCHAR(20),
    frequency         VARCHAR(20),
    data_quality_flag VARCHAR(20) DEFAULT 'Valid'
);

CREATE TABLE hse.dim_training (
    training_id              VARCHAR(30) PRIMARY KEY,
    training_program         VARCHAR(200),
    training_type            VARCHAR(50),
    certification_name       VARCHAR(200),
    cert_validity_months     INT,
    competency_area          VARCHAR(100),
    mandatory_frequency      VARCHAR(50)
);

CREATE TABLE hse.dim_hazard (
    hazard_id          VARCHAR(20) PRIMARY KEY,
    hazard_type        VARCHAR(100),
    hazard_category    VARCHAR(100),
    control_measure    TEXT,
    risk_rating        VARCHAR(20),
    regulatory_ref     VARCHAR(200)
);

CREATE TABLE hse.ref_env_threshold (
    threshold_id       VARCHAR(30) PRIMARY KEY,
    site_id            VARCHAR(20) NOT NULL,
    parameter_name     VARCHAR(100) NOT NULL,
    threshold_value    DECIMAL(15, 4) NOT NULL,
    threshold_unit     VARCHAR(20),
    alert_amber        DECIMAL(15, 4),
    alert_red          DECIMAL(15, 4),
    regulatory_source  VARCHAR(200),
    active_from        DATE DEFAULT CURRENT_DATE,
    active_to          DATE DEFAULT '9999-12-31',
    notes              TEXT
);

-- =============================================
-- FACT TABLE
-- =============================================

CREATE TABLE hse.fact_hse (
    fact_id                BIGSERIAL PRIMARY KEY,
    date_key               DATE NOT NULL REFERENCES hse.dim_datetime(date_key),
    site_key               VARCHAR(20) NOT NULL REFERENCES hse.dim_site(site_id),
    dept_key               VARCHAR(20) REFERENCES hse.dim_department(dept_id),
    emp_key                VARCHAR(20) REFERENCES hse.dim_employee(employee_id),
    equip_key              VARCHAR(50) REFERENCES hse.dim_equipment(equipment_id),
    contractor_key         VARCHAR(20) REFERENCES hse.dim_contractor(contractor_id),
    incident_key           VARCHAR(30) REFERENCES hse.dim_incident(incident_id),
    ptw_key                VARCHAR(30) REFERENCES hse.dim_ptw(ptw_id),
    hazard_key             VARCHAR(20) REFERENCES hse.dim_hazard(hazard_id),
    train_key              VARCHAR(30) REFERENCES hse.dim_training(training_id),

    -- Workforce
    man_hours_worked       DECIMAL(12, 2) DEFAULT 0,
    headcount_present      INT DEFAULT 0,
    headcount_leave        INT DEFAULT 0,
    headcount_contractor   INT DEFAULT 0,

    -- Incident Counts
    lti_count              INT DEFAULT 0,
    mti_count              INT DEFAULT 0,
    fai_count              INT DEFAULT 0,
    near_miss_count        INT DEFAULT 0,
    fatality_count         INT DEFAULT 0,
    first_aid_count        INT DEFAULT 0,
    property_dmg_count     INT DEFAULT 0,
    env_incident_count     INT DEFAULT 0,

    -- Environmental
    env_reading_value      DECIMAL(15, 4),
    env_limit_value        DECIMAL(15, 4) DEFAULT 9999,
    env_exceeded           BOOLEAN DEFAULT FALSE,
    env_sample_id          VARCHAR(50),

    -- PTW
    ptw_issued_count       INT DEFAULT 0,
    ptw_closed_count       INT DEFAULT 0,
    ptw_open_count         INT DEFAULT 0,
    ptw_violation_count    INT DEFAULT 0,
    gas_clearance_count    INT DEFAULT 0,

    -- Observation & Inspection
    inspection_count       INT DEFAULT 0,
    observation_count      INT DEFAULT 0,
    observation_safe       INT DEFAULT 0,
    observation_unsafe     INT DEFAULT 0,

    -- Training
    training_passed_count  INT DEFAULT 0,
    training_failed_count  INT DEFAULT 0,
    training_pending_count INT DEFAULT 0,

    -- Equipment
    equipment_insp_pass_count INT DEFAULT 0,
    equipment_insp_fail_count INT DEFAULT 0,
    equipment_down_count   INT DEFAULT 0,

    -- Audit & Compliance
    audit_score            DECIMAL(5, 2),
    audit_findings         INT DEFAULT 0,
    audit_critical         INT DEFAULT 0,
    audit_major            INT DEFAULT 0,
    audit_minor            INT DEFAULT 0,

    -- Calculated / Derived
    metric_value           DECIMAL(15, 4),
    metric_type            VARCHAR(50),

    -- Risk
    risk_score             DECIMAL(5, 2),
    risk_level             VARCHAR(20),

    -- Context
    weather_condition      VARCHAR(50),
    shift_name             VARCHAR(20),

    created_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_daily_metric UNIQUE (date_key, site_key, dept_key, metric_type)
);

-- =============================================
-- SECURITY TABLES
-- =============================================

-- Note: security_user_role is defined later with correct schema (line 450+)
-- This section intentionally left blank to avoid duplicate table definition

-- =============================================
-- INDEXES
-- =============================================

CREATE INDEX idx_fact_hse_date_site ON hse.fact_hse(date_key, site_key);
CREATE INDEX idx_fact_hse_dept ON hse.fact_hse(dept_key);
CREATE INDEX idx_fact_hse_emp ON hse.fact_hse(emp_key);
CREATE INDEX idx_fact_hse_ptw ON hse.fact_hse(ptw_key);
CREATE INDEX idx_fact_hse_incident ON hse.fact_hse(incident_key);
CREATE INDEX idx_fact_hse_equip ON hse.fact_hse(equip_key);
CREATE INDEX idx_fact_hse_env_exceeded ON hse.fact_hse(env_exceeded) WHERE env_exceeded = TRUE;
CREATE INDEX idx_fact_hse_metric ON hse.fact_hse(metric_type, date_key);
CREATE INDEX idx_fact_hse_updated ON hse.fact_hse(updated_at);

CREATE INDEX idx_dim_site_type ON hse.dim_site(site_type);
CREATE INDEX idx_dim_employee_site ON hse.dim_employee(site_id);
CREATE INDEX idx_dim_equipment_site ON hse.dim_equipment(current_site_id);
CREATE INDEX idx_dim_equipment_cert ON hse.dim_equipment(certification_expiry);
CREATE INDEX idx_dim_ptw_site_status ON hse.dim_ptw(site_id, ptw_status);
CREATE INDEX idx_ref_env_threshold_site ON hse.ref_env_threshold(site_id, parameter_name);

-- =============================================
-- SAMPLE DATA
-- =============================================

-- Insert sample sites
INSERT INTO hse.dim_site (site_id, site_name, site_type, location_lat, location_long, zone, area_type, permit_no, managing_director) VALUES
('SITE-A', 'Site Alpha Kutai', 'Mining', -0.4240, 116.9830, 'North Pit', 'Open Pit', 'IUP-2024-001', 'Budi Santoso'),
('SITE-A-C', 'Site Alpha Workshop', 'Construction', -0.4245, 116.9835, 'Workshop', 'Surface', 'IUP-2024-001', 'Budi Santoso'),
('SITE-A-O', 'Site Alpha Office', 'ICT Support', -0.4248, 116.9840, 'Admin Area', 'Surface', 'IUP-2024-001', 'Budi Santoso'),
('SITE-B', 'Site Beta Balikpapan', 'Oil & Gas Support', -1.2653, 116.8312, 'Processing Plant', 'Surface', 'IUP-2024-002', 'Siti Rahayu'),
('SITE-B-C', 'Site Beta Contractor Yard', 'Construction', -1.2658, 116.8318, 'Yard', 'Surface', 'IUP-2024-002', 'Siti Rahayu'),
('SITE-C', 'Site Gamma Samarinda', 'Mining', -0.4966, 117.1438, 'South Pit', 'Open Pit', 'IUP-2024-003', 'Andi Wijaya'),
('SITE-C-U', 'Site Gamma Underground', 'Mining', -0.4970, 117.1440, 'Underground', 'Underground', 'IUP-2024-003', 'Andi Wijaya');

-- Insert sample departments
INSERT INTO hse.dim_department (dept_id, dept_name, dept_type, site_id, head_of_dept) VALUES
('DEPT-MIN', 'Mining Operations', 'Mining', 'SITE-A', 'Joko Susilo'),
('DEPT-CON', 'Construction & Civil', 'Construction', 'SITE-A-C', 'Ahmad Fauzi'),
('DEPT-ICT', 'ICT & Data Management', 'ICT', 'SITE-A-O', 'Rina Wulandari'),
('DEPT-MNT', 'Mining Maintenance', 'Maintenance', 'SITE-A', 'Bambang Sutrisno'),
('DEPT-ENV', 'Environmental Management', 'Environmental', 'SITE-A-C', 'Dr. Siti Aminah'),
('DEPT-EHS', 'Environmental Health & Safety', 'HSE', 'SITE-A', 'Maya Indira'),
('DEPT-PROC', 'Process Plant Operations', 'Oil & Gas Support', 'SITE-B', 'Hendra Gunawan'),
('DEPT-MNT-B', 'Maintenance & Reliability', 'Maintenance', 'SITE-B', 'Dedi Prasetyo'),
('DEPT-HSE', 'HSE Operations', 'HSE', 'SITE-B', 'Sari Dewi'),
('DEPT-SUB', 'Site Support', 'Site Support', 'SITE-B-C', 'Yusuf Hidayat'),
('DEPT-MIN-C', 'Contractor Mining', 'Mining', 'SITE-C', 'M. Rizki'),
('DEPT-HSE-C', 'HSE Compliance', 'HSE', 'SITE-C', 'Dewi Lestari'),
('DEPT-SAF', 'Safety & Emergency', 'Safety', 'SITE-C-U', 'Agus Salim');

-- Insert sample datetime (first 10 days of 2025)
INSERT INTO hse.dim_datetime (date_key, day_of_week, day_name, is_weekend, calendar_year, calendar_quarter, calendar_month, week_of_year, shift_name)
VALUES
('2025-01-01', 4, 'Wednesday', FALSE, 2025, 1, 1, 1, 'Morning'),
('2025-01-02', 5, 'Thursday', FALSE, 2025, 1, 1, 1, 'Morning'),
('2025-01-03', 6, 'Friday', FALSE, 2025, 1, 1, 1, 'Morning'),
('2025-01-06', 2, 'Monday', FALSE, 2025, 1, 1, 2, 'Morning'),
('2025-01-07', 3, 'Tuesday', FALSE, 2025, 1, 1, 2, 'Afternoon'),
('2025-01-08', 4, 'Wednesday', FALSE, 2025, 1, 1, 2, 'Morning'),
('2025-01-13', 2, 'Monday', FALSE, 2025, 1, 1, 3, 'Morning');

-- Insert sample environmental thresholds (location-specific)
INSERT INTO hse.ref_env_threshold (threshold_id, site_id, parameter_name, threshold_value, threshold_unit, alert_amber, alert_red, regulatory_source, notes) VALUES
('THR-001', 'SITE-A', 'PM2.5', 50, 'µg/m³', 50, 80, 'AMDAL 2023', 'Kab. Kutai override'),
('THR-002', 'SITE-A', 'PM10', 200, 'µg/m³', 200, 300, 'AMDAL 2023', 'Kab. Kutai override'),
('THR-003', 'SITE-A', 'Noise', 90, 'dB(A)', 90, 100, 'Perda Kab. Kutai', 'Area industri'),
('THR-004', 'SITE-A-C', 'Noise', 85, 'dB(A)', 85, 90, 'PermenLHK', 'Camp/kantor'),
('THR-005', 'SITE-A-C', 'PM2.5', 35, 'µg/m³', 35, 55, 'PermenLHK No.13/2023', 'Default WHO'),
('THR-006', 'SITE-B', 'PM2.5', 35, 'µg/m³', 35, 55, 'PermenLHK No.13/2023', 'Kota Balikpapan'),
('THR-007', 'SITE-B', 'Noise', 85, 'dB(A)', 85, 90, 'PermenLHK', 'Default'),
('THR-008', 'SITE-C', 'PM2.5', 35, 'µg/m³', 35, 55, 'PermenLHK No.13/2023', 'Default'),
('THR-009', 'SITE-C', 'Noise', 85, 'dB(A)', 85, 90, 'PermenLHK', 'Default');

-- =============================================
-- ENTERPRISE RBAC SECURITY TABLES
-- =============================================

-- Users table with credentials
CREATE TABLE hse.security_users (
    user_id           SERIAL PRIMARY KEY,
    email             VARCHAR(200) UNIQUE NOT NULL,
    username          VARCHAR(100) UNIQUE,
    full_name         VARCHAR(200) NOT NULL,
    password_hash     VARCHAR(255) NOT NULL,
    is_active         BOOLEAN DEFAULT TRUE,
    is_locked         BOOLEAN DEFAULT FALSE,
    failed_login_attempts INT DEFAULT 0,
    locked_until      TIMESTAMP,
    last_login_at     TIMESTAMP,
    last_login_ip     VARCHAR(45),
    last_login_user_agent TEXT,
    password_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    password_expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '90 days'),
    must_change_password BOOLEAN DEFAULT FALSE,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by        VARCHAR(200),
    updated_by        VARCHAR(200)
);

-- Roles table with hierarchy
CREATE TABLE hse.security_roles (
    role_id           SERIAL PRIMARY KEY,
    role_name         VARCHAR(50) UNIQUE NOT NULL,
    role_display_name VARCHAR(100) NOT NULL,
    role_description  TEXT,
    parent_role_id    INT REFERENCES hse.security_roles(role_id),
    is_system_role    BOOLEAN DEFAULT FALSE,
    is_active         BOOLEAN DEFAULT TRUE,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Permissions table (granular per modul/aksi)
CREATE TABLE hse.security_permissions (
    permission_id     SERIAL PRIMARY KEY,
    permission_name   VARCHAR(100) UNIQUE NOT NULL,
    permission_display_name VARCHAR(100) NOT NULL,
    module           VARCHAR(50) NOT NULL,
    action           VARCHAR(50) NOT NULL,
    description      TEXT,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Role-Permission mapping (many-to-many)
CREATE TABLE hse.security_role_permission (
    role_id           INT REFERENCES hse.security_roles(role_id) ON DELETE CASCADE,
    permission_id     INT REFERENCES hse.security_permissions(permission_id) ON DELETE CASCADE,
    granted_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    granted_by       VARCHAR(200),
    PRIMARY KEY (role_id, permission_id)
);

-- User-Role mapping (many-to-many, with site/department scope)
CREATE TABLE hse.security_user_role (
    user_role_id      SERIAL PRIMARY KEY,
    user_id           INT REFERENCES hse.security_users(user_id) ON DELETE CASCADE,
    role_id           INT REFERENCES hse.security_roles(role_id) ON DELETE CASCADE,
    site_access       VARCHAR(500) NOT NULL DEFAULT 'ALL',
    department_access VARCHAR(500),
    contractor_access VARCHAR(500),
    assigned_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by       VARCHAR(200),
    expires_at        TIMESTAMP,
    is_active         BOOLEAN DEFAULT TRUE,
    UNIQUE(user_id, role_id)
);

-- Active sessions (for session management)
CREATE TABLE hse.security_sessions (
    session_id        VARCHAR(255) PRIMARY KEY,
    user_id           INT REFERENCES hse.security_users(user_id) ON DELETE CASCADE,
    ip_address        VARCHAR(45),
    user_agent        TEXT,
    device_info       JSONB,
    last_activity_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at        TIMESTAMP NOT NULL,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    logged_out_at     TIMESTAMP,
    is_active         BOOLEAN DEFAULT TRUE
);

-- Login history (audit trail)
CREATE TABLE hse.security_login_history (
    login_id          SERIAL PRIMARY KEY,
    user_id           INT REFERENCES hse.security_users(user_id) ON DELETE SET NULL,
    email             VARCHAR(200),
    login_type        VARCHAR(20) NOT NULL, -- 'password', 'sso', 'api'
    ip_address        VARCHAR(45),
    user_agent        TEXT,
    device_info       JSONB,
    login_status      VARCHAR(20) NOT NULL, -- 'success', 'failed', 'locked'
    failure_reason    TEXT,
    location          VARCHAR(200),
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for security tables
CREATE INDEX idx_security_users_email ON hse.security_users(email);
CREATE INDEX idx_security_users_active ON hse.security_users(is_active, is_locked);
CREATE INDEX idx_security_sessions_user ON hse.security_sessions(user_id, is_active);
CREATE INDEX idx_security_sessions_expires ON hse.security_sessions(expires_at);
CREATE INDEX idx_security_login_history_user ON hse.security_login_history(user_id, created_at);
CREATE INDEX idx_security_login_history_email ON hse.security_login_history(email, created_at);

-- =============================================
-- SAMPLE SECURITY DATA
-- =============================================

-- Insert roles
INSERT INTO hse.security_roles (role_name, role_display_name, role_description, is_system_role) VALUES
('super_admin', 'Super Admin', 'Full system access with all permissions', TRUE),
('hse_director', 'HSE Director', 'HSE Director with access to all HSE modules', TRUE),
('site_manager', 'Site Manager', 'Site Manager with access to assigned sites', TRUE),
('hse_manager', 'HSE Manager', 'HSE Manager with full HSE module access', TRUE),
('hse_officer', 'HSE Officer', 'HSE Officer with input and monitoring access', TRUE),
('supervisor', 'Supervisor', 'Supervisor with PTW, inspection, and HIRA access', TRUE),
('ict_admin', 'ICT Admin', 'ICT Administrator with infrastructure access', TRUE),
('auditor', 'Auditor', 'Auditor with read-only access and evidence management', TRUE),
('contractor', 'Contractor', 'Contractor with access to own data only', TRUE);

-- Insert permissions (granular)
INSERT INTO hse.security_permissions (permission_name, permission_display_name, module, action, description) VALUES
-- Dashboard
('dashboard:view', 'View Dashboard', 'dashboard', 'view', 'View executive dashboard'),
('dashboard:export', 'Export Dashboard', 'dashboard', 'export', 'Export dashboard to PDF/Excel'),
-- Incident
('incident:view', 'View Incidents', 'incident', 'view', 'View incident records'),
('incident:create', 'Create Incident', 'incident', 'create', 'Create new incident report'),
('incident:edit', 'Edit Incident', 'incident', 'edit', 'Edit incident records'),
('incident:delete', 'Delete Incident', 'incident', 'delete', 'Delete incident records'),
('incident:investigate', 'Investigate Incident', 'incident', 'investigate', 'Conduct incident investigation'),
('incident:close', 'Close Incident', 'incident', 'close', 'Close incident with CAPA'),
-- PTW
('ptw:view', 'View PTW', 'ptw', 'view', 'View PTW records'),
('ptw:create', 'Create PTW', 'ptw', 'create', 'Create new PTW'),
('ptw:edit', 'Edit PTW', 'ptw', 'edit', 'Edit PTW records'),
('ptw:approve', 'Approve PTW', 'ptw', 'approve', 'Approve PTW requests'),
('ptw:close', 'Close PTW', 'ptw', 'close', 'Close PTW'),
('ptw:violate', 'Report Violation', 'ptw', 'violate', 'Report PTW violation'),
-- Training
('training:view', 'View Training', 'training', 'view', 'View training records'),
('training:create', 'Create Training', 'training', 'create', 'Create training program'),
('training:edit', 'Edit Training', 'training', 'edit', 'Edit training records'),
('training:delete', 'Delete Training', 'training', 'delete', 'Delete training records'),
('training:certify', 'Certify Training', 'training', 'certify', 'Issue training certificates'),
-- Environmental
('environmental:view', 'View Environmental', 'environmental', 'view', 'View environmental data'),
('environmental:input', 'Input Environmental', 'environmental', 'input', 'Input environmental readings'),
('environmental:edit', 'Edit Environmental', 'environmental', 'edit', 'Edit environmental data'),
('environmental:export', 'Export Environmental', 'environmental', 'export', 'Export environmental reports'),
-- Equipment
('equipment:view', 'View Equipment', 'equipment', 'view', 'View equipment records'),
('equipment:create', 'Create Equipment', 'equipment', 'create', 'Add new equipment'),
('equipment:edit', 'Edit Equipment', 'equipment', 'edit', 'Edit equipment records'),
('equipment:inspect', 'Inspect Equipment', 'equipment', 'inspect', 'Conduct equipment inspection'),
('equipment:certify', 'Certify Equipment', 'equipment', 'certify', 'Certify equipment'),
-- Audit
('audit:view', 'View Audit', 'audit', 'view', 'View audit findings'),
('audit:create', 'Create Audit', 'audit', 'create', 'Create audit plan'),
('audit:edit', 'Edit Audit', 'audit', 'edit', 'Edit audit records'),
('audit:close', 'Close Audit', 'audit', 'close', 'Close audit findings'),
('audit:evidence', 'Manage Evidence', 'audit', 'evidence', 'Upload/download audit evidence'),
-- User Management
('user:view', 'View Users', 'user', 'view', 'View user accounts'),
('user:create', 'Create User', 'user', 'create', 'Create new user'),
('user:edit', 'Edit User', 'user', 'edit', 'Edit user accounts'),
('user:delete', 'Delete User', 'user', 'delete', 'Delete/deactivate users'),
('user:assign_role', 'Assign Role', 'user', 'assign_role', 'Assign roles to users'),
-- System
('system:config', 'System Config', 'system', 'config', 'Configure system settings'),
('system:monitor', 'System Monitor', 'system', 'monitor', 'View system monitoring'),
('system:backup', 'System Backup', 'system', 'backup', 'Perform system backup');

-- Insert role-permission mappings
-- Super Admin: all permissions
INSERT INTO hse.security_role_permission (role_id, permission_id, granted_by)
SELECT r.role_id, p.permission_id, 'system'
FROM hse.security_roles r, hse.security_permissions p
WHERE r.role_name = 'super_admin';

-- HSE Director: all except system config
INSERT INTO hse.security_role_permission (role_id, permission_id, granted_by)
SELECT r.role_id, p.permission_id, 'system'
FROM hse.security_roles r, hse.security_permissions p
WHERE r.role_name = 'hse_director'
  AND p.module NOT IN ('system', 'user');

-- Site Manager: dashboard view/export, incident view, PTW view/approve/close, training view, environmental view, equipment view, audit view/evidence
INSERT INTO hse.security_role_permission (role_id, permission_id, granted_by)
SELECT r.role_id, p.permission_id, 'system'
FROM hse.security_roles r, hse.security_permissions p
WHERE r.role_name = 'site_manager'
  AND (
    (p.module = 'dashboard' AND p.action IN ('view', 'export'))
    OR (p.module = 'incident' AND p.action IN ('view', 'investigate', 'close'))
    OR (p.module = 'ptw' AND p.action IN ('view', 'approve', 'close'))
    OR (p.module = 'training' AND p.action = 'view')
    OR (p.module = 'environmental' AND p.action IN ('view', 'export'))
    OR (p.module = 'equipment' AND p.action = 'view')
    OR (p.module = 'audit' AND p.action IN ('view', 'evidence'))
  );

-- HSE Manager: all except system config and user delete
INSERT INTO hse.security_role_permission (role_id, permission_id, granted_by)
SELECT r.role_id, p.permission_id, 'system'
FROM hse.security_roles r, hse.security_permissions p
WHERE r.role_name = 'hse_manager'
  AND p.module NOT IN ('system')
  AND NOT (p.module = 'user' AND p.action = 'delete');

-- HSE Officer: view/create/edit incidents, view/create PTW, view/input environmental, view equipment, view training
INSERT INTO hse.security_role_permission (role_id, permission_id, granted_by)
SELECT r.role_id, p.permission_id, 'system'
FROM hse.security_roles r, hse.security_permissions p
WHERE r.role_name = 'hse_officer'
  AND (
    (p.module = 'dashboard' AND p.action = 'view')
    OR (p.module = 'incident' AND p.action IN ('view', 'create', 'edit'))
    OR (p.module = 'ptw' AND p.action IN ('view', 'create', 'edit'))
    OR (p.module = 'training' AND p.action = 'view')
    OR (p.module = 'environmental' AND p.action IN ('view', 'input'))
    OR (p.module = 'equipment' AND p.action = 'view')
    OR (p.module = 'audit' AND p.action = 'view')
  );

-- Supervisor: view dashboard, view/create PTW, view inspections, view HIRA
INSERT INTO hse.security_role_permission (role_id, permission_id, granted_by)
SELECT r.role_id, p.permission_id, 'system'
FROM hse.security_roles r, hse.security_permissions p
WHERE r.role_name = 'supervisor'
  AND (
    (p.module = 'dashboard' AND p.action = 'view')
    OR (p.module = 'ptw' AND p.action IN ('view', 'create'))
    OR (p.module = 'incident' AND p.action = 'view')
    OR (p.module = 'equipment' AND p.action IN ('view', 'inspect'))
    OR (p.module = 'audit' AND p.action = 'view')
  );

-- ICT Admin: system monitor, user view, dashboard view
INSERT INTO hse.security_role_permission (role_id, permission_id, granted_by)
SELECT r.role_id, p.permission_id, 'system'
FROM hse.security_roles r, hse.security_permissions p
WHERE r.role_name = 'ict_admin'
  AND (
    (p.module = 'system' AND p.action = 'monitor')
    OR (p.module = 'user' AND p.action = 'view')
    OR (p.module = 'dashboard' AND p.action = 'view')
  );

-- Auditor: view all except system, evidence management
INSERT INTO hse.security_role_permission (role_id, permission_id, granted_by)
SELECT r.role_id, p.permission_id, 'system'
FROM hse.security_roles r, hse.security_permissions p
WHERE r.role_name = 'auditor'
  AND p.action IN ('view', 'evidence', 'export')
  AND p.module NOT IN ('system', 'user');

-- Contractor: view own data only (dashboard, incident, ptw, training)
INSERT INTO hse.security_role_permission (role_id, permission_id, granted_by)
SELECT r.role_id, p.permission_id, 'system'
FROM hse.security_roles r, hse.security_permissions p
WHERE r.role_name = 'contractor'
  AND (
    (p.module = 'dashboard' AND p.action = 'view')
    OR (p.module = 'incident' AND p.action = 'view')
    OR (p.module = 'ptw' AND p.action IN ('view', 'create'))
    OR (p.module = 'training' AND p.action = 'view')
  );

-- Insert sample users with hashed passwords (password: 'Welcome123!')
INSERT INTO hse.security_users (email, username, full_name, password_hash, is_active, failed_login_attempts, created_by) VALUES
('super.admin@company.com', 'superadmin', 'Super Admin', '$2b$12$LJ3m9.7x9Y9x9Y9x9Y9x9O', TRUE, 0, 'system'),
('hse.director@company.com', 'hsedirector', 'HSE Director', '$2b$12$LJ3m9.7x9Y9x9Y9x9Y9x9O', TRUE, 0, 'system'),
('site.manager.alpha@company.com', 'sitemgr-alpha', 'Site Manager Alpha', '$2b$12$LJ3m9.7x9Y9x9Y9x9Y9x9O', TRUE, 0, 'system'),
('hse.manager@company.com', 'hsemgr', 'HSE Manager', '$2b$12$LJ3m9.7x9Y9x9Y9x9Y9x9O', TRUE, 0, 'system'),
('hse.officer.alpha@company.com', 'hseoff-alpha', 'HSE Officer Alpha', '$2b$12$LJ3m9.7x9Y9x9Y9x9Y9x9O', TRUE, 0, 'system'),
('supervisor.alpha@company.com', 'sup-alpha', 'Supervisor Alpha', '$2b$12$LJ3m9.7x9Y9x9Y9x9Y9x9O', TRUE, 0, 'system'),
('ict.admin@company.com', 'ictadmin', 'ICT Administrator', '$2b$12$LJ3m9.7x9Y9x9Y9x9Y9x9O', TRUE, 0, 'system'),
('auditor.external@company.com', 'auditor-ext', 'External Auditor', '$2b$12$LJ3m9.7x9Y9x9Y9x9Y9x9O', TRUE, 0, 'system'),
('contractor.alpha@company.com', 'ctr-alpha', 'Contractor Alpha', '$2b$12$LJ3m9.7x9Y9x9Y9x9Y9x9O', TRUE, 0, 'system');

-- Assign roles to users
INSERT INTO hse.security_user_role (user_id, role_id, site_access, assigned_by) VALUES
(1, 1, 'ALL', 'system'),  -- Super Admin
(2, 2, 'ALL', 'system'),  -- HSE Director
(3, 3, 'SITE-A,SITE-A-C,SITE-A-O', 'system'),  -- Site Manager Alpha
(4, 4, 'ALL', 'system'),  -- HSE Manager
(5, 5, 'SITE-A,SITE-A-C', 'system'),  -- HSE Officer Alpha
(6, 6, 'SITE-A', 'system'),  -- Supervisor Alpha
(7, 7, 'ALL', 'system'),  -- ICT Admin
(8, 8, 'ALL', 'system'),  -- Auditor
(9, 9, 'SITE-A', 'system'); -- Contractor Alpha

-- Insert sample login history
INSERT INTO hse.security_login_history (user_id, email, login_type, ip_address, user_agent, login_status)
VALUES
(1, 'super.admin@company.com', 'password', '192.168.1.100', 'Mozilla/5.0', 'success'),
(4, 'hse.manager@company.com', 'password', '192.168.1.101', 'Mozilla/5.0', 'success'),
(5, 'hse.officer.alpha@company.com', 'password', '192.168.1.102', 'Mozilla/5.0', 'success');

-- =============================================
-- VIEWS FOR POWER BI / GRAFANA
-- =============================================

-- Daily aggregated view (easier for dashboard)
CREATE OR REPLACE VIEW hse.v_daily_hse_summary AS
SELECT
    f.date_key,
    f.site_key,
    s.site_name,
    s.site_type,
    f.dept_key,
    d.dept_name,
    SUM(f.man_hours_worked) AS man_hours_worked,
    SUM(f.lti_count) AS lti_count,
    SUM(f.mti_count) AS mti_count,
    SUM(f.fai_count) AS fai_count,
    SUM(f.near_miss_count) AS near_miss_count,
    SUM(f.fatality_count) AS fatality_count,
    SUM(f.ptw_issued_count) AS ptw_issued,
    SUM(f.ptw_closed_count) AS ptw_closed,
    SUM(f.ptw_violation_count) AS ptw_violations,
    SUM(f.inspection_count) AS inspection_count,
    SUM(f.observation_count) AS observation_count,
    SUM(f.training_passed_count) AS training_completed,
    AVG(f.audit_score) AS avg_audit_score,
    COUNT(CASE WHEN f.env_exceeded = TRUE THEN 1 END) AS env_exceedances,
    COUNT(DISTINCT f.incident_key) AS incident_count,
    CASE
        WHEN SUM(f.man_hours_worked) > 0
        THEN (SUM(f.lti_count) * 1000000.0) / SUM(f.man_hours_worked)
        ELSE NULL
    END AS ltifr,
    CASE
        WHEN SUM(f.man_hours_worked) > 0
        THEN ((SUM(f.lti_count) + SUM(f.mti_count) + SUM(f.fai_count)) * 200000.0) / SUM(f.man_hours_worked)
        ELSE NULL
    END AS trir
FROM hse.fact_hse f
JOIN hse.dim_site s ON f.site_key = s.site_id
JOIN hse.dim_department d ON f.dept_key = d.dept_id
GROUP BY f.date_key, f.site_key, s.site_name, s.site_type, f.dept_key, d.dept_name;

-- Real-time PTW view for Grafana
CREATE OR REPLACE VIEW hse.v_ptw_current_status AS
SELECT
    p.ptw_id,
    p.ptw_type,
    p.ptw_category,
    p.site_id,
    s.site_name,
    p.workstation,
    p.start_at,
    p.end_at,
    p.ptw_status,
    p.violation_count,
    p.gas_test_done,
    p.gas_test_result,
    CASE
        WHEN p.ptw_status = 'OPEN' AND p.end_at < CURRENT_TIMESTAMP THEN 'OVERDUE'
        WHEN p.ptw_status = 'PENDING' AND p.start_at < CURRENT_TIMESTAMP THEN 'STARTED'
        ELSE p.ptw_status
    END AS computed_status
FROM hse.dim_ptw p
JOIN hse.dim_site s ON p.site_id = s.site_id
WHERE p.is_cancelled = FALSE;

-- Real-time environmental view for Grafana
CREATE OR REPLACE VIEW hse.v_env_realtime AS
SELECT
    CURRENT_DATE AS date_key,
    s.site_id,
    s.site_name,
    e.parameter_name,
    AVG(f.env_reading_value) AS current_value,
    MAX(t.threshold_value) AS threshold_value,
    MAX(t.alert_amber) AS alert_amber,
    MAX(t.alert_red) AS alert_red,
    CASE
        WHEN AVG(f.env_reading_value) > MAX(t.alert_red) THEN 'RED'
        WHEN AVG(f.env_reading_value) > MAX(t.alert_amber) THEN 'AMBER'
        ELSE 'GREEN'
    END AS status
FROM hse.fact_hse f
JOIN hse.dim_site s ON f.site_key = s.site_id
JOIN hse.dim_environmental e ON f.env_sample_id = e.env_id
LEFT JOIN hse.ref_env_threshold t ON e.parameter_name = t.parameter_name
    AND s.site_id = t.site_id
    AND t.active_to = '9999-12-31'
WHERE f.date_key = CURRENT_DATE
GROUP BY s.site_id, s.site_name, e.parameter_name;

-- Equipment compliance view
CREATE OR REPLACE VIEW hse.v_equipment_compliance AS
SELECT
    e.equipment_id,
    e.equipment_type,
    e.manufacturer,
    e.current_site_id,
    s.site_name,
    e.next_inspection,
    e.certification_expiry,
    e.days_since_last_insp,
    CASE
        WHEN e.certification_expiry < CURRENT_DATE THEN 'EXPIRED'
        WHEN e.next_inspection < CURRENT_DATE THEN 'OVERDUE'
        WHEN e.days_since_last_insp > 90 THEN 'DUE SOON'
        ELSE 'VALID'
    END AS compliance_status
FROM hse.dim_equipment e
JOIN hse.dim_site s ON e.current_site_id = s.site_id
WHERE e.active_to = '9999-12-31';

-- Active alerts view (for Early Warning System)
CREATE OR REPLACE VIEW hse.v_active_alerts AS
SELECT
    'LTIFR Critical' AS alert_type,
    f.site_key,
    s.site_name,
    'LTIFR ' || ROUND(ltifr, 2) || ' exceeds threshold (2.0)' AS alert_message,
    'CRITICAL' AS severity,
    f.date_key AS alert_date
FROM hse.v_daily_hse_summary f
JOIN hse.dim_site s ON f.site_key = s.site_id
WHERE f.ltifr > 2.0
  AND f.date_key >= CURRENT_DATE - INTERVAL '7 days'

UNION ALL

SELECT
    'TRIR Critical' AS alert_type,
    f.site_key,
    s.site_name,
    'TRIR ' || ROUND(trir, 2) || ' exceeds threshold (3.5)' AS alert_message,
    'CRITICAL' AS severity,
    f.date_key AS alert_date
FROM hse.v_daily_hse_summary f
JOIN hse.dim_site s ON f.site_key = s.site_id
WHERE f.trir > 3.5
  AND f.date_key >= CURRENT_DATE - INTERVAL '7 days'

UNION ALL

SELECT
    'Environmental Exceedance' AS alert_type,
    f.site_key,
    s.site_name,
    'Parameter ' || e.parameter_name || ' exceeded limit: ' || ROUND(f.env_reading_value, 2) || ' vs ' || ROUND(f.env_limit_value, 2) AS alert_message,
    'CRITICAL' AS severity,
    f.date_key AS alert_date
FROM hse.fact_hse f
JOIN hse.dim_site s ON f.site_key = s.site_id
JOIN hse.dim_environmental e ON f.env_sample_id = e.env_id
WHERE f.env_exceeded = TRUE
  AND f.date_key >= CURRENT_DATE - INTERVAL '7 days'

UNION ALL

SELECT
    'PTW Violations' AS alert_type,
    f.site_key,
    s.site_name,
    f.ptw_violation_count || ' PTW violations detected' AS alert_message,
    'WARNING' AS severity,
    f.date_key AS alert_date
FROM hse.v_daily_hse_summary f
JOIN hse.dim_site s ON f.site_key = s.site_id
WHERE f.ptw_violations > 0
  AND f.date_key >= CURRENT_DATE - INTERVAL '7 days'

UNION ALL

SELECT
    'Equipment Expired' AS alert_type,
    e.current_site_id,
    s.site_name,
    e.equipment_id || ' certification expired on ' || e.certification_expiry::TEXT AS alert_message,
    'CRITICAL' AS severity,
    CURRENT_DATE AS alert_date
FROM hse.dim_equipment e
JOIN hse.dim_site s ON e.current_site_id = s.site_id
WHERE e.certification_expiry < CURRENT_DATE
  AND e.active_to = '9999-12-31';

-- =============================================
-- FUNCTIONS
-- =============================================

-- Dynamic threshold lookup per site
CREATE OR REPLACE FUNCTION hse.get_env_threshold(
    p_site_id VARCHAR(20),
    p_parameter_name VARCHAR(100)
)
RETURNS TABLE (
    threshold_value DECIMAL(15, 4),
    alert_amber DECIMAL(15, 4),
    alert_red DECIMAL(15, 4),
    regulatory_source VARCHAR(200)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.threshold_value,
        t.alert_amber,
        t.alert_red,
        t.regulatory_source
    FROM hse.ref_env_threshold t
    WHERE t.site_id = p_site_id
      AND t.parameter_name = p_parameter_name
      AND t.active_from <= CURRENT_DATE
      AND t.active_to >= CURRENT_DATE
    UNION ALL
    -- Fallback to default if no site-specific threshold
    SELECT
        t.threshold_value,
        t.alert_amber,
        t.alert_red,
        t.regulatory_source
    FROM hse.ref_env_threshold t
    WHERE t.site_id = 'DEFAULT'
      AND t.parameter_name = p_parameter_name
      AND t.active_from <= CURRENT_DATE
      AND t.active_to >= CURRENT_DATE
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Quick KPI calculator
CREATE OR REPLACE FUNCTION hse.calculate_ltifr(
    p_lti_count INT,
    p_man_hours DECIMAL(12, 2)
)
RETURNS DECIMAL(10, 4) AS $$
BEGIN
    IF p_man_hours IS NULL OR p_man_hours = 0 THEN
        RETURN NULL;
    END IF;
    RETURN (p_lti_count * 1000000.0) / p_man_hours;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- =============================================
-- SAMPLE DATA FOR TESTING
-- =============================================

-- Insert sample environmental parameters
INSERT INTO hse.dim_environmental (env_id, parameter_type, parameter_name, monitoring_point, site_id, regulatory_limit, unit_of_measure, frequency) VALUES
('ENV-001', 'Air Quality', 'PM2.5', 'North Pit Berm', 'SITE-A', 50, 'µg/m³', 'Hourly'),
('ENV-002', 'Air Quality', 'PM10', 'Workers Camp', 'SITE-A', 150, 'µg/m³', 'Hourly'),
('ENV-003', 'Noise', 'Leq', 'Drill Rig 05', 'SITE-A', 90, 'dB(A)', 'Shift'),
('ENV-004', 'Water Quality', 'BOD', 'Effluent Pit', 'SITE-A', 30, 'mg/L', 'Daily'),
('ENV-005', 'Air Quality', 'PM2.5', 'Processing Plant', 'SITE-B', 35, 'µg/m³', 'Hourly'),
('ENV-006', 'Noise', 'Leq', 'Crusher Area', 'SITE-B', 85, 'dB(A)', 'Shift');

-- Insert sample incidents
INSERT INTO hse.dim_incident (incident_id, incident_type, incident_category, severity_class, body_part, agency_type, incident_cause, incident_location, ptw_required, case_status, root_cause) VALUES
('INC-001', 'Near Miss', 'Slip/Trip', 'Minor', 'None', 'Contractor', 'Unsafe Condition', 'Workshop Area B', FALSE, 'Closed', 'Inadequate housekeeping'),
('INC-002', 'First Aid', 'Struck By', 'Minor', 'Hand', 'Employee', 'Unsafe Act', 'Warehouse Zone A', FALSE, 'Closed', 'PPE non-compliance'),
('INC-003', 'MTI', 'Caught Between', 'Moderate', 'Hand', 'Contractor', 'Equipment Failure', 'Crushing Plant', FALSE, 'Closed', 'Protective device failure'),
('INC-004', 'Near Miss', 'Fall From Height', 'Minor', 'None', 'Employee', 'Unsafe Act', 'Structure Assembly', FALSE, 'Closed', 'Non-compliant behavior'),
('INC-005', 'LTI', 'Struck By', 'Serious', 'Foot', 'Employee', 'Unsafe Condition', 'Hauling Road A', FALSE, 'Under Investigation', 'Forklift traffic management failure');

-- Insert sample PTW
INSERT INTO hse.dim_ptw (ptw_id, ptw_type, ptw_category, issued_by, approved_by, site_id, workstation, start_at, end_at, hazard_identified, ptw_status, violation_count) VALUES
('PTW-2025-001', 'Hot Work', 'Critical', 'Budi Santoso', 'Siti Rahayu', 'SITE-A', 'Workshop B', '2025-01-20 08:00', '2025-01-20 17:00', 'Fire, explosion', 'CLOSED', 0),
('PTW-2025-002', 'Confined Space', 'Critical', 'Susilo Budi', 'Maya Indira', 'SITE-A', 'Pump Station', '2025-01-21 07:00', '2025-01-21 15:00', 'Toxic atmosphere', 'OPEN', 0),
('PTW-2025-003', 'Electrical', 'Break-in', 'Bambang Sutrisno', 'Hendra Gunawan', 'SITE-B', 'Switchgear Room', '2025-01-23 09:00', '2025-01-23 12:00', 'Electric shock', 'OPEN', 1),
('PTW-2025-004', 'Working at Height', 'Routine', 'Sari Dewi', 'Andi Wijaya', 'SITE-A', 'Structural Steel', '2025-01-24 07:00', '2025-01-24 16:00', 'Fall from height', 'PENDING', 0),
('PTW-2025-005', 'Hot Work', 'Routine', 'Ahmad Fuzi', 'Bambang Sutrisno', 'SITE-A', 'Workshop A', '2025-01-28 10:00', '2025-01-28 12:00', 'Spark ignition', 'CANCELLED', 0);

-- Insert sample equipment
INSERT INTO hse.dim_equipment (equipment_id, equipment_type, category, manufacturer, model, serial_no, current_site_id, next_inspection, certification_expiry) VALUES
('EQ-DT-001', 'Dump Truck', 'Heavy Equipment', 'Komatsu', 'HD785-7', 'KM-785-2020-001', 'SITE-A', '2025-09-15', '2026-03-15'),
('EQ-EX-001', 'Excavator', 'Heavy Equipment', 'Caterpillar', '395FL', 'CAT-395-2021-001', 'SITE-A', '2025-10-10', '2026-04-10'),
('EQ-CR-001', 'Crusher', 'Processing Equipment', 'Metso', 'C160', 'MT-C160-2018-001', 'SITE-B', '2025-11-20', '2026-05-20'),
('EQ-FK-001', 'Forklift', 'Lifting Equipment', 'Toyota', '8FGU25', 'TY-8FGU-2023-001', 'SITE-A-O', '2025-12-12', '2026-06-12');

-- =============================================
-- GRANTS
-- =============================================

-- Power BI / Grafana read-only access
CREATE ROLE hse_reader;
GRANT USAGE ON SCHEMA hse TO hse_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA hse TO hse_reader;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA hse TO hse_reader;
GRANT EXECUTE ON FUNCTION hse.get_env_threshold TO hse_reader;
GRANT EXECUTE ON FUNCTION hse.calculate_ltifr TO hse_reader;

-- Data Engineer write access
CREATE ROLE hse_writer;
GRANT USAGE ON SCHEMA hse TO hse_writer;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA hse TO hse_writer;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA hse TO hse_writer;

-- Create example users (adjust as needed)
-- CREATE USER hse_powerbi WITH PASSWORD 'secure_password';
-- GRANT hse_reader TO hse_powerbi;

-- CREATE USER hse_etl WITH PASSWORD 'secure_password';
-- GRANT hse_writer TO hse_etl;

-- =============================================
-- MAINTENANCE
-- =============================================

-- Update triggers for updated_at (run once after table creation)
-- CREATE OR REPLACE FUNCTION hse.update_updated_at()
-- RETURNS TRIGGER AS $$
-- BEGIN
--     NEW.updated_at = CURRENT_TIMESTAMP;
--     RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql;

-- CREATE TRIGGER trg_fact_hse_updated BEFORE UPDATE ON hse.fact_hse
--     FOR EACH ROW EXECUTE FUNCTION hse.update_updated_at();

-- =============================================
-- VERIFICATION
-- =============================================
-- SELECT COUNT(*) FROM hse.dim_site;
-- SELECT COUNT(*) FROM hse.dim_department;
-- SELECT COUNT(*) FROM hse.fact_hse;
-- SELECT * FROM hse.v_daily_hse_summary ORDER BY date_key DESC LIMIT 10;
-- SELECT * FROM hse.v_active_alerts;
-- SELECT * FROM hse.get_env_threshold('SITE-A', 'PM2.5');

-- =============================================
-- AUDIT TRAIL & EVIDENCE MANAGEMENT TABLES
-- =============================================

CREATE TABLE hse.audit_plans (
    audit_id           VARCHAR(50) PRIMARY KEY,
    audit_type         VARCHAR(30) NOT NULL CHECK (audit_type IN ('internal','external','certification','surveillance','nonconformity','management_review')),
    audit_status       VARCHAR(20) DEFAULT 'planned' CHECK (audit_status IN ('planned','in_progress','completed','cancelled')),
    audit_title        VARCHAR(200) NOT NULL,
    standard_ref       VARCHAR(100),
    site_id            VARCHAR(20) REFERENCES hse.dim_site(site_id),
    department_id      VARCHAR(20) REFERENCES hse.dim_department(dept_id),
    lead_auditor       VARCHAR(200),
    audit_team         JSONB,
    scope              TEXT,
    criteria           TEXT,
    scheduled_start    DATE,
    scheduled_end      DATE,
    actual_start       DATE,
    actual_end         DATE,
    findings_count     INTEGER DEFAULT 0,
    major_findings     INTEGER DEFAULT 0,
    minor_findings     INTEGER DEFAULT 0,
    observations       INTEGER DEFAULT 0,
    compliance_score   NUMERIC(5,2),
    audit_report       TEXT,
    created_by         VARCHAR(200),
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE hse.audit_findings (
    finding_id         VARCHAR(50) PRIMARY KEY,
    audit_id           VARCHAR(50) NOT NULL REFERENCES hse.audit_plans(audit_id) ON DELETE CASCADE,
    finding_type       VARCHAR(20) NOT NULL CHECK (finding_type IN ('major','minor','observation','opportunity')),
    finding_status     VARCHAR(20) DEFAULT 'open' CHECK (finding_status IN ('open','in_progress','closed','overdue')),
    clause_ref         VARCHAR(100),
    description        TEXT NOT NULL,
    objective_evidence TEXT,
    root_cause         TEXT,
    corrective_action  TEXT,
    preventive_action  TEXT,
    pic                VARCHAR(200),
    due_date           DATE,
    closed_date        DATE,
    severity_score     INTEGER,
    created_by         VARCHAR(200),
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE hse.evidence (
    evidence_id        VARCHAR(50) PRIMARY KEY,
    finding_id         VARCHAR(50) REFERENCES hse.audit_findings(finding_id) ON DELETE CASCADE,
    incident_id        VARCHAR(30) REFERENCES hse.dim_incident(incident_id),
    ptw_id             VARCHAR(30) REFERENCES hse.dim_ptw(ptw_id),
    training_id        VARCHAR(30) REFERENCES hse.dim_training(training_id),
    evidence_type      VARCHAR(20) NOT NULL CHECK (evidence_type IN ('photo','document','video','audio','checklist','certificate','report')),
    file_name          VARCHAR(200) NOT NULL,
    file_path          VARCHAR(500) NOT NULL,
    file_size          INTEGER,
    mime_type          VARCHAR(100),
    description        TEXT,
    captured_by        VARCHAR(200),
    captured_at        TIMESTAMP,
    uploaded_by        VARCHAR(200),
    uploaded_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_public          BOOLEAN DEFAULT FALSE,
    tags               JSONB,
    checksum           VARCHAR(64)
);

CREATE TABLE hse.audit_trail (
    trail_id           VARCHAR(50) PRIMARY KEY,
    user_id            INTEGER REFERENCES hse.security_users(user_id),
    user_email         VARCHAR(200),
    action             VARCHAR(100) NOT NULL,
    table_name         VARCHAR(100) NOT NULL,
    record_id          VARCHAR(50) NOT NULL,
    old_values         JSONB,
    new_values         JSONB,
    ip_address         VARCHAR(45),
    user_agent         TEXT,
    session_id         VARCHAR(255),
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE hse.corrective_actions (
    car_id             VARCHAR(50) PRIMARY KEY,
    finding_id         VARCHAR(50) NOT NULL REFERENCES hse.audit_findings(finding_id) ON DELETE CASCADE,
    car_type           VARCHAR(20) NOT NULL CHECK (car_type IN ('corrective','preventive')),
    description        TEXT NOT NULL,
    root_cause         TEXT,
    proposed_action    TEXT,
    pic                VARCHAR(200),
    due_date           DATE,
    completion_date    DATE,
    status             VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open','in_progress','completed','verified','overdue')),
    effectiveness_check TEXT,
    verified_by        VARCHAR(200),
    verified_at        TIMESTAMP,
    created_by         VARCHAR(200),
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_findings_audit ON hse.audit_findings(audit_id);
CREATE INDEX idx_audit_findings_status ON hse.audit_findings(finding_status);
CREATE INDEX idx_audit_plans_site ON hse.audit_plans(site_id);
CREATE INDEX idx_audit_plans_status ON hse.audit_plans(audit_status);
CREATE INDEX idx_evidence_finding ON hse.evidence(finding_id);
CREATE INDEX idx_evidence_type ON hse.evidence(evidence_type);
CREATE INDEX idx_audit_trail_user ON hse.audit_trail(user_id, created_at);
CREATE INDEX idx_audit_trail_table ON hse.audit_trail(table_name, created_at);
CREATE INDEX idx_car_finding ON hse.corrective_actions(finding_id);
CREATE INDEX idx_car_status ON hse.corrective_actions(status);

-- =============================================
-- AUDIT TRIGGER: auto-update audit plan findings count
-- =============================================

CREATE OR REPLACE FUNCTION hse.update_audit_findings_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE hse.audit_plans
    SET findings_count = (
            SELECT COUNT(*) FROM hse.audit_findings WHERE audit_id = NEW.audit_id
        ),
        major_findings = (
            SELECT COUNT(*) FROM hse.audit_findings WHERE audit_id = NEW.audit_id AND finding_type = 'major'
        ),
        minor_findings = (
            SELECT COUNT(*) FROM hse.audit_findings WHERE audit_id = NEW.audit_id AND finding_type = 'minor'
        ),
        observations = (
            SELECT COUNT(*) FROM hse.audit_findings WHERE audit_id = NEW.audit_id AND finding_type = 'observation'
        ),
        updated_at = CURRENT_TIMESTAMP
    WHERE audit_id = NEW.audit_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_findings_count
AFTER INSERT OR UPDATE OR DELETE ON hse.audit_findings
FOR EACH STATEMENT EXECUTE FUNCTION hse.update_audit_findings_count();

-- =============================================
-- EVIDENCE STORAGE DIRECTORY GRANT
-- =============================================
-- Ensure the ETL role can insert evidence records
GRANT INSERT ON hse.audit_plans, hse.audit_findings, hse.evidence, hse.audit_trail, hse.corrective_actions TO hse_writer;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA hse TO hse_writer;

-- =============================================
-- ALERT & NOTIFICATION SYSTEM TABLES
-- =============================================

CREATE TABLE hse.alert_rules (
    rule_id            VARCHAR(50) PRIMARY KEY,
    rule_name          VARCHAR(200) NOT NULL,
    metric_type        VARCHAR(30) NOT NULL CHECK (metric_type IN ('ltifr','trir','env_pm25','env_noise','ptw_violation','equipment_expired','training_expired','near_miss','fatality','custom')),
    condition          VARCHAR(10) NOT NULL CHECK (condition IN ('>','<','>=','<=','==','!=')),
    threshold_value    NUMERIC(15,4) NOT NULL,
    severity           VARCHAR(20) DEFAULT 'warning' CHECK (severity IN ('critical','high','warning','info')),
    site_id            VARCHAR(20) REFERENCES hse.dim_site(site_id),
    department_id      VARCHAR(20) REFERENCES hse.dim_department(dept_id),
    notification_channels JSONB DEFAULT '["dashboard"]',
    recipients         JSONB DEFAULT '[]',
    is_active          BOOLEAN DEFAULT TRUE,
    cooldown_minutes   INTEGER DEFAULT 60,
    last_triggered_at  TIMESTAMP,
    description        TEXT,
    created_by         VARCHAR(200),
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE hse.alerts (
    alert_id           VARCHAR(50) PRIMARY KEY,
    rule_id            VARCHAR(50) REFERENCES hse.alert_rules(rule_id),
    alert_type         VARCHAR(100) NOT NULL,
    severity           VARCHAR(20) DEFAULT 'warning' CHECK (severity IN ('critical','high','warning','info')),
    status             VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active','acknowledged','resolved','suppressed')),
    site_id            VARCHAR(20) REFERENCES hse.dim_site(site_id),
    site_name          VARCHAR(200),
    metric_type        VARCHAR(50),
    metric_value       NUMERIC(15,4),
    threshold_value    NUMERIC(15,4),
    message            TEXT NOT NULL,
    details            JSONB,
    triggered_by       VARCHAR(200),
    acknowledged_by    VARCHAR(200),
    acknowledged_at    TIMESTAMP,
    resolved_by        VARCHAR(200),
    resolved_at        TIMESTAMP,
    resolution_notes   TEXT,
    alert_date         DATE DEFAULT CURRENT_DATE,
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE hse.notification_logs (
    log_id             VARCHAR(50) PRIMARY KEY,
    alert_id           VARCHAR(50) REFERENCES hse.alerts(alert_id),
    channel            VARCHAR(20) NOT NULL CHECK (channel IN ('email','sms','telegram','webhook','dashboard')),
    recipient          VARCHAR(500),
    subject            VARCHAR(500),
    body               TEXT,
    status             VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending','sent','failed','bounced')),
    error_message      TEXT,
    sent_at            TIMESTAMP,
    delivered_at       TIMESTAMP,
    retry_count        INTEGER DEFAULT 0,
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_alert_rules_site ON hse.alert_rules(site_id);
CREATE INDEX idx_alert_rules_active ON hse.alert_rules(is_active);
CREATE INDEX idx_alerts_status ON hse.alerts(status, alert_date);
CREATE INDEX idx_alerts_site ON hse.alerts(site_id, alert_date);
CREATE INDEX idx_alerts_severity ON hse.alerts(severity);
CREATE INDEX idx_notification_alert ON hse.notification_logs(alert_id);
CREATE INDEX idx_notification_status ON hse.notification_logs(status);

GRANT SELECT ON hse.alert_rules, hse.alerts, hse.notification_logs TO hse_reader;
GRANT INSERT, UPDATE, DELETE ON hse.alert_rules, hse.alerts, hse.notification_logs TO hse_writer;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA hse TO hse_writer;

-- =============================================
-- AI SAFETY ASSISTANT - KNOWLEDGE LAYER
-- =============================================

-- pgvector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- AI Documents (SOPs, regulations, audit reports, etc.)
CREATE TABLE hse.ai_documents (
    document_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title            VARCHAR(500) NOT NULL,
    description      TEXT,
    document_type    VARCHAR(50) NOT NULL CHECK (document_type IN ('sop', 'regulation', 'audit_report', 'incident_report', 'ptw', 'training', 'policy', 'procedure', 'guideline')),
    source_system    VARCHAR(100),
    source_id        VARCHAR(100),
    file_name        VARCHAR(500),
    file_path        VARCHAR(1000),
    mime_type        VARCHAR(100),
    file_size        INTEGER,
    page_count       INTEGER,
    language         VARCHAR(10) DEFAULT 'id',
    metadata         JSONB,
    is_active        BOOLEAN DEFAULT TRUE,
    created_by       VARCHAR(200),
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    indexed_at       TIMESTAMP,
    embedding_model  VARCHAR(100)
);

-- AI Document Chunks (text segments with embeddings)
CREATE TABLE hse.ai_document_chunks (
    chunk_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id      UUID NOT NULL REFERENCES hse.ai_documents(document_id) ON DELETE CASCADE,
    chunk_index      INTEGER NOT NULL,
    text             TEXT NOT NULL,
    tokens           INTEGER,
    embedding        VECTOR(1536),
    embedding_model  VARCHAR(100),
    metadata         JSONB,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Conversations
CREATE TABLE hse.ai_conversations (
    conversation_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          INTEGER REFERENCES hse.security_users(user_id) ON DELETE SET NULL,
    title            VARCHAR(500),
    context_type     VARCHAR(50),
    context_id       VARCHAR(100),
    is_active        BOOLEAN DEFAULT TRUE,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Messages
CREATE TABLE hse.ai_messages (
    message_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id  UUID NOT NULL REFERENCES hse.ai_conversations(conversation_id) ON DELETE CASCADE,
    role             VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content          TEXT NOT NULL,
    sources          JSONB,
    confidence       FLOAT,
    feedback         VARCHAR(20) CHECK (feedback IN ('helpful', 'not_helpful', 'inaccurate')),
    tokens_used      INTEGER,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for AI tables
CREATE INDEX idx_ai_documents_type ON hse.ai_documents(document_type, is_active);
CREATE INDEX idx_ai_documents_source ON hse.ai_documents(source_system, source_id);
CREATE INDEX idx_ai_chunks_document ON hse.ai_document_chunks(document_id);
CREATE INDEX idx_ai_chunks_embedding ON hse.ai_document_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_ai_conversations_user ON hse.ai_conversations(user_id, created_at);
CREATE INDEX idx_ai_messages_conversation ON hse.ai_messages(conversation_id, created_at);

-- Grants for AI tables
GRANT SELECT ON hse.ai_documents, hse.ai_document_chunks, hse.ai_conversations, hse.ai_messages TO hse_reader;
GRANT INSERT, UPDATE, DELETE ON hse.ai_documents, hse.ai_document_chunks, hse.ai_conversations, hse.ai_messages TO hse_writer;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA hse TO hse_writer;

-- =============================================
-- HSE OPERATIONS - OPERATIONAL TRANSACTION TABLES
-- =============================================

-- Shared attachments table for all operational modules
CREATE TABLE hse.operational_attachments (
    attachment_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module            VARCHAR(50) NOT NULL CHECK (module IN ('incident', 'ptw', 'training', 'environmental', 'equipment', 'audit', 'observation', 'hira', 'near_miss', 'contractor')),
    record_id         VARCHAR(100) NOT NULL,
    file_name         VARCHAR(500) NOT NULL,
    file_path         VARCHAR(1000) NOT NULL,
    file_type         VARCHAR(100),
    file_size         INTEGER,
    mime_type         VARCHAR(100),
    description       TEXT,
    uploaded_by       VARCHAR(200),
    uploaded_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_public         BOOLEAN DEFAULT FALSE,
    tags              TEXT[],
    checksum          VARCHAR(64),
    metadata          JSONB,
    is_deleted        BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_operational_attachments_module_record ON hse.operational_attachments(module, record_id, is_deleted);
CREATE INDEX idx_operational_attachments_uploaded ON hse.operational_attachments(uploaded_by, uploaded_at);

-- Shared workflow history table
CREATE TABLE hse.workflow_history (
    transition_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module            VARCHAR(50) NOT NULL CHECK (module IN ('incident', 'ptw', 'training', 'environmental', 'equipment', 'audit', 'observation', 'hira', 'near_miss', 'contractor')),
    record_id         VARCHAR(100) NOT NULL,
    from_status       VARCHAR(50),
    to_status         VARCHAR(50) NOT NULL,
    action            VARCHAR(100) NOT NULL,
    remarks           TEXT,
    performed_by      VARCHAR(200) NOT NULL,
    performed_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address        VARCHAR(45),
    user_agent        TEXT,
    metadata          JSONB
);

CREATE INDEX idx_workflow_history_module_record ON hse.workflow_history(module, record_id, performed_at);
CREATE INDEX idx_workflow_history_performed ON hse.workflow_history(performed_by, performed_at);

-- =============================================
-- INCIDENT MANAGEMENT
-- =============================================

CREATE TABLE hse.incident_reports (
    report_id         VARCHAR(50) PRIMARY KEY,
    incident_id       VARCHAR(30) REFERENCES hse.dim_incident(incident_id),
    report_date       DATE NOT NULL DEFAULT CURRENT_DATE,
    report_time       TIME,
    site_id           VARCHAR(20) NOT NULL REFERENCES hse.dim_site(site_id),
    department_id     VARCHAR(20) REFERENCES hse.dim_department(dept_id),
    shift             VARCHAR(20),
    location          VARCHAR(200) NOT NULL,
    latitude          DECIMAL(10, 8),
    longitude         DECIMAL(11, 8),
    category          VARCHAR(100) NOT NULL CHECK (category IN ('Injury', 'Near Miss', 'Property Damage', 'Environmental', 'Security', 'Other')),
    severity          VARCHAR(20) NOT NULL CHECK (severity IN ('Fatality', 'LTI', 'MTI', 'First Aid', 'Near Miss', 'Property Damage')),
    incident_type     VARCHAR(100) NOT NULL,
    description       TEXT NOT NULL,
    immediate_action  TEXT,
    root_cause        TEXT,
    corrective_action TEXT,
    preventive_action TEXT,
    pic               VARCHAR(200),
    witness           VARCHAR(500),
    injured_person    VARCHAR(200),
    body_part         VARCHAR(100),
    lost_days         INTEGER DEFAULT 0,
    restricted_days   INTEGER DEFAULT 0,
    medical_treatment TEXT,
    ptw_required      BOOLEAN DEFAULT FALSE,
    ptw_violated      BOOLEAN DEFAULT FALSE,
    investigation_required BOOLEAN DEFAULT FALSE,
    investigation_lead VARCHAR(200),
    investigation_due DATE,
    case_status       VARCHAR(20) DEFAULT 'Draft' CHECK (case_status IN ('Draft', 'Submitted', 'Under Review', 'Approved', 'Closed', 'Cancelled')),
    workflow_stage    VARCHAR(50) DEFAULT 'Draft' CHECK (workflow_stage IN ('Draft', 'Submitted', 'Review', 'Approval', 'Closed', 'Cancelled')),
    status            VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),
    is_deleted        BOOLEAN DEFAULT FALSE,
    deleted_at        TIMESTAMP,
    deleted_by        VARCHAR(200),
    version           INTEGER DEFAULT 1,
    attachments       JSONB DEFAULT '[]'::jsonb,
    metadata          JSONB DEFAULT '{}'::jsonb,
    created_by        VARCHAR(200) NOT NULL,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by        VARCHAR(200),
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_incident_reports_site_date ON hse.incident_reports(site_id, report_date, is_deleted);
CREATE INDEX idx_incident_reports_status ON hse.incident_reports(case_status, is_deleted);
CREATE INDEX idx_incident_reports_severity ON hse.incident_reports(severity, is_deleted);
CREATE INDEX idx_incident_reports_created ON hse.incident_reports(created_by, created_at);

-- =============================================
-- PTW (PERMIT TO WORK)
-- =============================================

CREATE TABLE hse.ptw_requests (
    request_id        VARCHAR(50) PRIMARY KEY,
    ptw_id            VARCHAR(30) REFERENCES hse.dim_ptw(ptw_id),
    request_date      DATE NOT NULL DEFAULT CURRENT_DATE,
    site_id           VARCHAR(20) NOT NULL REFERENCES hse.dim_site(site_id),
    department_id     VARCHAR(20) REFERENCES hse.dim_department(dept_id),
    ptw_type          VARCHAR(100) NOT NULL,
    ptw_category      VARCHAR(50),
    workstation       VARCHAR(200) NOT NULL,
    location          VARCHAR(200),
    latitude          DECIMAL(10, 8),
    longitude         DECIMAL(11, 8),
    start_at          TIMESTAMP NOT NULL,
    end_at            TIMESTAMP NOT NULL,
    hazard_identified TEXT NOT NULL,
    mitigation_list   TEXT,
    isolation_list    TEXT,
    cna_required      BOOLEAN DEFAULT FALSE,
    gas_test_done     BOOLEAN DEFAULT FALSE,
    gas_test_result   VARCHAR(20) CHECK (gas_test_result IN ('Pass', 'Fail', 'Pending')),
    fire_watch_required BOOLEAN DEFAULT FALSE,
    standby_person    VARCHAR(200),
    work_description  TEXT NOT NULL,
    contractor_involved BOOLEAN DEFAULT FALSE,
    contractor_name   VARCHAR(200),
    pic               VARCHAR(200) NOT NULL,
    approved_by       VARCHAR(200),
    approved_at       TIMESTAMP,
    rejection_reason  TEXT,
    sign_in           TIMESTAMP,
    sign_out          TIMESTAMP,
    actual_start      TIMESTAMP,
    actual_end        TIMESTAMP,
    extension_count   INTEGER DEFAULT 0,
    extension_reason  TEXT,
    violation_count   INTEGER DEFAULT 0,
    violation_notes   TEXT,
    ptw_status        VARCHAR(20) DEFAULT 'Draft' CHECK (ptw_status IN ('Draft', 'Pending Approval', 'Approved', 'Rejected', 'Active', 'Expired', 'Closed', 'Cancelled')),
    workflow_stage    VARCHAR(50) DEFAULT 'Draft' CHECK (workflow_stage IN ('Draft', 'Pending Approval', 'Approval', 'Active', 'Expired', 'Closed', 'Cancelled')),
    status            VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),
    is_deleted        BOOLEAN DEFAULT FALSE,
    deleted_at        TIMESTAMP,
    deleted_by        VARCHAR(200),
    version           INTEGER DEFAULT 1,
    attachments       JSONB DEFAULT '[]'::jsonb,
    metadata          JSONB DEFAULT '{}'::jsonb,
    created_by        VARCHAR(200) NOT NULL,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by        VARCHAR(200),
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ptw_requests_site_status ON hse.ptw_requests(site_id, ptw_status, is_deleted);
CREATE INDEX idx_ptw_requests_dates ON hse.ptw_requests(start_at, end_at, is_deleted);
CREATE INDEX idx_ptw_requests_pic ON hse.ptw_requests(pic, is_deleted);
CREATE INDEX idx_ptw_requests_created ON hse.ptw_requests(created_by, created_at);

-- =============================================
-- TRAINING RECORDS
-- =============================================

CREATE TABLE hse.training_records (
    record_id         VARCHAR(50) PRIMARY KEY,
    training_id       VARCHAR(30) REFERENCES hse.dim_training(training_id),
    training_name     VARCHAR(200) NOT NULL,
    training_type     VARCHAR(50) NOT NULL CHECK (training_type IN ('Initial', 'Refresher', 'Advanced', 'Certification', 'Induction', 'Toolbox Talk')),
    site_id           VARCHAR(20) NOT NULL REFERENCES hse.dim_site(site_id),
    department_id     VARCHAR(20) REFERENCES hse.dim_department(dept_id),
    trainer           VARCHAR(200),
    training_date     DATE NOT NULL,
    expiry_date       DATE,
    duration_hours    DECIMAL(5, 2),
    competency_area   VARCHAR(100),
    certification_name VARCHAR(200),
    cert_number       VARCHAR(100),
    result            VARCHAR(20) NOT NULL CHECK (result IN ('Pass', 'Fail', 'Pending', 'In Progress')),
    score             DECIMAL(5, 2),
    max_score         DECIMAL(5, 2),
    remarks           TEXT,
    evidence_path     VARCHAR(1000),
    status            VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),
    is_deleted        BOOLEAN DEFAULT FALSE,
    deleted_at        TIMESTAMP,
    deleted_by        VARCHAR(200),
    version           INTEGER DEFAULT 1,
    attachments       JSONB DEFAULT '[]'::jsonb,
    metadata          JSONB DEFAULT '{}'::jsonb,
    created_by        VARCHAR(200) NOT NULL,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by        VARCHAR(200),
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_training_records_site_date ON hse.training_records(site_id, training_date, is_deleted);
CREATE INDEX idx_training_records_result ON hse.training_records(result, is_deleted);
CREATE INDEX idx_training_records_expiry ON hse.training_records(expiry_date, is_deleted);
CREATE INDEX idx_training_records_created ON hse.training_records(created_by, created_at);

-- =============================================
-- SAFETY OBSERVATIONS (BBS)
-- =============================================

CREATE TABLE hse.safety_observations (
    observation_id    VARCHAR(50) PRIMARY KEY,
    observation_date  DATE NOT NULL DEFAULT CURRENT_DATE,
    observation_time  TIME,
    site_id           VARCHAR(20) NOT NULL REFERENCES hse.dim_site(site_id),
    department_id     VARCHAR(20) REFERENCES hse.dim_department(dept_id),
    observed_by       VARCHAR(200) NOT NULL,
    observed_person   VARCHAR(200),
    location          VARCHAR(200) NOT NULL,
    latitude          DECIMAL(10, 8),
    longitude         DECIMAL(11, 8),
    observation_type  VARCHAR(20) NOT NULL CHECK (observation_type IN ('Safe', 'Unsafe', 'Near Miss')),
    category          VARCHAR(100),
    description       TEXT NOT NULL,
    immediate_action  TEXT,
    corrective_action TEXT,
    pic               VARCHAR(200),
    due_date          DATE,
    closed_at         TIMESTAMP,
    status            VARCHAR(20) DEFAULT 'Open' CHECK (status IN ('Open', 'In Progress', 'Closed', 'Overdue')),
    is_deleted        BOOLEAN DEFAULT FALSE,
    deleted_at        TIMESTAMP,
    deleted_by        VARCHAR(200),
    version           INTEGER DEFAULT 1,
    attachments       JSONB DEFAULT '[]'::jsonb,
    metadata          JSONB DEFAULT '{}'::jsonb,
    created_by        VARCHAR(200) NOT NULL,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by        VARCHAR(200),
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_safety_observations_site_date ON hse.safety_observations(site_id, observation_date, is_deleted);
CREATE INDEX idx_safety_observations_type ON hse.safety_observations(observation_type, is_deleted);
CREATE INDEX idx_safety_observations_status ON hse.safety_observations(status, is_deleted);

-- =============================================
-- EQUIPMENT INSPECTIONS
-- =============================================

CREATE TABLE hse.equipment_inspections (
    inspection_id     VARCHAR(50) PRIMARY KEY,
    equipment_id      VARCHAR(50) NOT NULL REFERENCES hse.dim_equipment(equipment_id),
    inspection_date   DATE NOT NULL DEFAULT CURRENT_DATE,
    inspection_type   VARCHAR(100) NOT NULL,
    inspector         VARCHAR(200) NOT NULL,
    site_id           VARCHAR(20) NOT NULL REFERENCES hse.dim_site(site_id),
    findings          TEXT,
    defects_found     BOOLEAN DEFAULT FALSE,
    defect_description TEXT,
    corrective_action TEXT,
    result            VARCHAR(20) NOT NULL CHECK (result IN ('Pass', 'Fail', 'Conditional')),
    next_inspection   DATE,
    certification_expiry DATE,
    status            VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),
    is_deleted        BOOLEAN DEFAULT FALSE,
    deleted_at        TIMESTAMP,
    deleted_by        VARCHAR(200),
    version           INTEGER DEFAULT 1,
    attachments       JSONB DEFAULT '[]'::jsonb,
    metadata          JSONB DEFAULT '{}'::jsonb,
    created_by        VARCHAR(200) NOT NULL,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by        VARCHAR(200),
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_equipment_inspections_equipment ON hse.equipment_inspections(equipment_id, inspection_date, is_deleted);
CREATE INDEX idx_equipment_inspections_site ON hse.equipment_inspections(site_id, inspection_date, is_deleted);
CREATE INDEX idx_equipment_inspections_result ON hse.equipment_inspections(result, is_deleted);

-- =============================================
-- HIRA / JSA ASSESSMENTS
-- =============================================

CREATE TABLE hse.hira_assessments (
    assessment_id     VARCHAR(50) PRIMARY KEY,
    assessment_date   DATE NOT NULL DEFAULT CURRENT_DATE,
    site_id           VARCHAR(20) NOT NULL REFERENCES hse.dim_site(site_id),
    department_id     VARCHAR(20) REFERENCES hse.dim_department(dept_id),
    activity          VARCHAR(200) NOT NULL,
    location          VARCHAR(200) NOT NULL,
    task_description  TEXT NOT NULL,
    hazard_id         VARCHAR(20) REFERENCES hse.dim_hazard(hazard_id),
    hazard_type       VARCHAR(100),
    risk_rating       VARCHAR(20) NOT NULL CHECK (risk_rating IN ('Low', 'Medium', 'High', 'Extreme')),
    likelihood        INTEGER CHECK (likelihood BETWEEN 1 AND 5),
    severity          INTEGER CHECK (severity BETWEEN 1 AND 5),
    risk_score        INTEGER NOT NULL,
    control_measures  TEXT NOT NULL,
    ppe_required      TEXT,
    isolation_required BOOLEAN DEFAULT FALSE,
    permit_required   VARCHAR(100),
    emergency_procedure TEXT,
    assessed_by       VARCHAR(200) NOT NULL,
    reviewed_by       VARCHAR(200),
    reviewed_at       TIMESTAMP,
    approved_by       VARCHAR(200),
    approved_at       TIMESTAMP,
    status            VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),
    is_deleted        BOOLEAN DEFAULT FALSE,
    deleted_at        TIMESTAMP,
    deleted_by        VARCHAR(200),
    version           INTEGER DEFAULT 1,
    attachments       JSONB DEFAULT '[]'::jsonb,
    metadata          JSONB DEFAULT '{}'::jsonb,
    created_by        VARCHAR(200) NOT NULL,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by        VARCHAR(200),
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_hira_assessments_site_date ON hse.hira_assessments(site_id, assessment_date, is_deleted);
CREATE INDEX idx_hira_assessments_risk ON hse.hira_assessments(risk_rating, is_deleted);
CREATE INDEX idx_hira_assessments_status ON hse.hira_assessments(status, is_deleted);

-- =============================================
-- NEAR MISS REPORTS
-- =============================================

CREATE TABLE hse.near_miss_reports (
    report_id         VARCHAR(50) PRIMARY KEY,
    report_date       DATE NOT NULL DEFAULT CURRENT_DATE,
    report_time       TIME,
    site_id           VARCHAR(20) NOT NULL REFERENCES hse.dim_site(site_id),
    department_id     VARCHAR(20) REFERENCES hse.dim_department(dept_id),
    location          VARCHAR(200) NOT NULL,
    latitude          DECIMAL(10, 8),
    longitude         DECIMAL(11, 8),
    category          VARCHAR(100) NOT NULL,
    description       TEXT NOT NULL,
    immediate_action  TEXT,
    contributing_factor TEXT,
    corrective_action TEXT,
    pic               VARCHAR(200),
    witness           VARCHAR(500),
    potential_outcome TEXT,
    severity_potential VARCHAR(20) CHECK (severity_potential IN ('Fatality', 'LTI', 'MTI', 'First Aid', 'Property Damage')),
    learning_point    TEXT,
    shared_with_team  BOOLEAN DEFAULT FALSE,
    status            VARCHAR(20) DEFAULT 'Open' CHECK (status IN ('Open', 'Under Review', 'Closed')),
    is_deleted        BOOLEAN DEFAULT FALSE,
    deleted_at        TIMESTAMP,
    deleted_by        VARCHAR(200),
    version           INTEGER DEFAULT 1,
    attachments       JSONB DEFAULT '[]'::jsonb,
    metadata          JSONB DEFAULT '{}'::jsonb,
    created_by        VARCHAR(200) NOT NULL,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by        VARCHAR(200),
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_near_miss_reports_site_date ON hse.near_miss_reports(site_id, report_date, is_deleted);
CREATE INDEX idx_near_miss_reports_status ON hse.near_miss_reports(status, is_deleted);
CREATE INDEX idx_near_miss_reports_severity ON hse.near_miss_reports(severity_potential, is_deleted);

-- =============================================
-- CONTRACTOR MANAGEMENT (Operational)
-- =============================================

CREATE TABLE hse.contractor_records (
    record_id         VARCHAR(50) PRIMARY KEY,
    contractor_id     VARCHAR(20) NOT NULL REFERENCES hse.dim_contractor(contractor_id),
    record_date       DATE NOT NULL DEFAULT CURRENT_DATE,
    record_type       VARCHAR(50) NOT NULL CHECK (record_type IN ('Audit', 'Assessment', 'Incident', 'Observation', 'Certification', 'Insurance')),
    site_id           VARCHAR(20) NOT NULL REFERENCES hse.dim_site(site_id),
    assessment_date   DATE,
    assessor          VARCHAR(200),
    score             DECIMAL(5, 2),
    max_score         DECIMAL(5, 2),
    result            VARCHAR(20) CHECK (result IN ('Pass', 'Fail', 'Conditional')),
    findings          TEXT,
    corrective_action TEXT,
    follow_up_date    DATE,
    status            VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),
    is_deleted        BOOLEAN DEFAULT FALSE,
    deleted_at        TIMESTAMP,
    deleted_by        VARCHAR(200),
    version           INTEGER DEFAULT 1,
    attachments       JSONB DEFAULT '[]'::jsonb,
    metadata          JSONB DEFAULT '{}'::jsonb,
    created_by        VARCHAR(200) NOT NULL,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by        VARCHAR(200),
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_contractor_records_contractor ON hse.contractor_records(contractor_id, record_date, is_deleted);
CREATE INDEX idx_contractor_records_site ON hse.contractor_records(site_id, record_date, is_deleted);
CREATE INDEX idx_contractor_records_type ON hse.contractor_records(record_type, is_deleted);

-- =============================================
-- ENVIRONMENTAL READINGS (Operational)
-- =============================================

CREATE TABLE hse.environmental_readings (
    reading_id        VARCHAR(50) PRIMARY KEY,
    env_id            VARCHAR(30) REFERENCES hse.dim_environmental(env_id),
    reading_date      DATE NOT NULL DEFAULT CURRENT_DATE,
    reading_time      TIME,
    site_id           VARCHAR(20) NOT NULL REFERENCES hse.dim_site(site_id),
    parameter_type    VARCHAR(100) NOT NULL,
    parameter_name    VARCHAR(100) NOT NULL,
    monitoring_point  VARCHAR(200),
    reading_value     DECIMAL(15, 4) NOT NULL,
    limit_value       DECIMAL(15, 4),
    unit_of_measure   VARCHAR(20),
    exceeded          BOOLEAN DEFAULT FALSE,
    lab_method        VARCHAR(100),
    weather_condition VARCHAR(100),
    equipment_used    VARCHAR(200),
    sampled_by        VARCHAR(200),
    analyzed_by       VARCHAR(200),
    verified_by       VARCHAR(200),
    verified_at       TIMESTAMP,
    remarks           TEXT,
    status            VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),
    is_deleted        BOOLEAN DEFAULT FALSE,
    deleted_at        TIMESTAMP,
    deleted_by        VARCHAR(200),
    version           INTEGER DEFAULT 1,
    attachments       JSONB DEFAULT '[]'::jsonb,
    metadata          JSONB DEFAULT '{}'::jsonb,
    created_by        VARCHAR(200) NOT NULL,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by        VARCHAR(200),
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_environmental_readings_site_date ON hse.environmental_readings(site_id, reading_date, is_deleted);
CREATE INDEX idx_environmental_readings_parameter ON hse.environmental_readings(parameter_name, reading_date, is_deleted);
CREATE INDEX idx_environmental_readings_exceeded ON hse.environmental_readings(exceeded, is_deleted);

-- =============================================
-- WORKFLOW STATUS CONFIGURATION
-- =============================================

CREATE TABLE hse.workflow_statuses (
    status_id         VARCHAR(50) PRIMARY KEY,
    module            VARCHAR(50) NOT NULL CHECK (module IN ('incident', 'ptw', 'training', 'environmental', 'equipment', 'audit', 'observation', 'hira', 'near_miss', 'contractor')),
    status_name       VARCHAR(50) NOT NULL,
    display_name      VARCHAR(100) NOT NULL,
    description       TEXT,
    is_initial        BOOLEAN DEFAULT FALSE,
    is_final          BOOLEAN DEFAULT FALSE,
    allowed_actions   TEXT[],
    allowed_roles     TEXT[],
    sort_order        INTEGER DEFAULT 0,
    color             VARCHAR(20) DEFAULT 'gray' CHECK (color IN ('green', 'yellow', 'orange', 'red', 'gray', 'blue')),
    is_active         BOOLEAN DEFAULT TRUE,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(module, status_name)
);

CREATE INDEX idx_workflow_statuses_module ON hse.workflow_statuses(module, is_active);

-- Insert default workflow statuses
INSERT INTO hse.workflow_statuses (status_id, module, status_name, display_name, description, is_initial, is_final, allowed_actions, allowed_roles, sort_order, color) VALUES
-- Incident workflow
('WF-INC-001', 'incident', 'Draft', 'Draft', 'Initial draft of incident report', TRUE, FALSE, ARRAY['save', 'submit', 'delete'], ARRAY['hse_officer', 'hse_manager', 'super_admin'], 1, 'gray'),
('WF-INC-002', 'incident', 'Submitted', 'Submitted', 'Report submitted for review', FALSE, FALSE, ARRAY['review', 'reject', 'approve'], ARRAY['site_manager', 'hse_manager', 'super_admin'], 2, 'yellow'),
('WF-INC-003', 'incident', 'Under Review', 'Under Review', 'Under investigation and review', FALSE, FALSE, ARRAY['update', 'close'], ARRAY['hse_manager', 'super_admin'], 3, 'blue'),
('WF-INC-004', 'incident', 'Approved', 'Approved', 'Report approved', FALSE, FALSE, ARRAY['close'], ARRAY['hse_manager', 'super_admin'], 4, 'green'),
('WF-INC-005', 'incident', 'Closed', 'Closed', 'Case closed with CAPA', FALSE, TRUE, ARRAY['reopen'], ARRAY['hse_manager', 'super_admin'], 5, 'green'),
('WF-INC-006', 'incident', 'Cancelled', 'Cancelled', 'Report cancelled', FALSE, TRUE, ARRAY['reopen'], ARRAY['hse_manager', 'super_admin'], 6, 'red'),
-- PTW workflow
('WF-PTW-001', 'ptw', 'Draft', 'Draft', 'Initial PTW draft', TRUE, FALSE, ARRAY['save', 'submit'], ARRAY['supervisor', 'hse_officer', 'hse_manager'], 1, 'gray'),
('WF-PTW-002', 'ptw', 'Pending Approval', 'Pending Approval', 'Awaiting approval', FALSE, FALSE, ARRAY['approve', 'reject'], ARRAY['site_manager', 'hse_manager', 'super_admin'], 2, 'yellow'),
('WF-PTW-003', 'ptw', 'Approved', 'Approved', 'PTW approved and ready', FALSE, FALSE, ARRAY['activate', 'cancel'], ARRAY['site_manager', 'hse_manager'], 3, 'green'),
('WF-PTW-004', 'ptw', 'Active', 'Active', 'Work in progress', FALSE, FALSE, ARRAY['extend', 'close', 'cancel'], ARRAY['pic', 'site_manager', 'hse_manager'], 4, 'blue'),
('WF-PTW-005', 'ptw', 'Expired', 'Expired', 'PTW expired', FALSE, TRUE, ARRAY['renew', 'close'], ARRAY['site_manager', 'hse_manager'], 5, 'red'),
('WF-PTW-006', 'ptw', 'Closed', 'Closed', 'PTW completed and closed', FALSE, TRUE, ARRAY['reopen'], ARRAY['site_manager', 'hse_manager'], 6, 'green'),
('WF-PTW-007', 'ptw', 'Cancelled', 'Cancelled', 'PTW cancelled', FALSE, TRUE, ARRAY['reopen'], ARRAY['site_manager', 'hse_manager'], 7, 'red');

-- Grants for operational tables
GRANT SELECT ON hse.incident_reports, hse.ptw_requests, hse.training_records, hse.safety_observations, hse.equipment_inspections, hse.hira_assessments, hse.near_miss_reports, hse.contractor_records, hse.environmental_readings TO hse_reader;
GRANT INSERT, UPDATE, DELETE ON hse.incident_reports, hse.ptw_requests, hse.training_records, hse.safety_observations, hse.equipment_inspections, hse.hira_assessments, hse.near_miss_reports, hse.contractor_records, hse.environmental_readings TO hse_writer;
GRANT SELECT, INSERT, UPDATE, DELETE ON hse.operational_attachments, hse.workflow_history, hse.workflow_statuses TO hse_writer;
GRANT SELECT ON hse.operational_attachments, hse.workflow_history, hse.workflow_statuses TO hse_reader;
