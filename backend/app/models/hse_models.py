"""
SQLAlchemy Models for HSE Enterprise Platform.
Maps to PostgreSQL EDW tables.
"""

from sqlalchemy import (
    Column, Integer, String, Date, DateTime, Boolean, Numeric,
    ForeignKey, Text, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

from app.database import Base


class DimSite(Base):
    __tablename__ = "dim_site"
    __table_args__ = {"schema": "hse"}

    site_id = Column(String(20), primary_key=True)
    site_name = Column(String(200), nullable=False)
    site_type = Column(String(50))
    location_lat = Column(Numeric(10, 8))
    location_long = Column(Numeric(11, 8))
    zone = Column(String(100))
    area_type = Column(String(50))
    site_status = Column(String(20), default="Active")
    permit_no = Column(String(100))
    managing_director = Column(String(100))
    timezone = Column(String(50), default="Asia/Jakarta")
    active_from = Column(Date, default=datetime.now().date)
    active_to = Column(Date, default=datetime(9999, 12, 12).date())


class DimDepartment(Base):
    __tablename__ = "dim_department"
    __table_args__ = {"schema": "hse"}

    dept_id = Column(String(20), primary_key=True)
    dept_name = Column(String(100), nullable=False)
    dept_type = Column(String(50))
    parent_dept_id = Column(String(20))
    site_id = Column(String(20), ForeignKey("hse.dim_site.site_id"))
    head_of_dept = Column(String(100))
    budget_code = Column(String(50))
    active_from = Column(Date, default=datetime.now().date)
    active_to = Column(Date, default=datetime(9999, 12, 12).date())


class DimEmployee(Base):
    __tablename__ = "dim_employee"
    __table_args__ = {"schema": "hse"}

    employee_id = Column(String(20), primary_key=True)
    employment_type = Column(String(50))
    nationality = Column(String(50))
    job_title = Column(String(100))
    job_grade = Column(String(20))
    department_id = Column(String(20), ForeignKey("hse.dim_department.dept_id"))
    site_id = Column(String(20), ForeignKey("hse.dim_site.site_id"))
    certification_lvl = Column(String(100))
    hse_training_due = Column(Date)
    medical_clearance = Column(Date)
    drug_test_status = Column(String(20))
    blood_group = Column(String(5))
    active_from = Column(Date, default=datetime.now().date)
    active_to = Column(Date, default=datetime(9999, 12, 12).date())


class DimEquipment(Base):
    __tablename__ = "dim_equipment"
    __table_args__ = {"schema": "hse"}

    equipment_id = Column(String(50), primary_key=True)
    equipment_type = Column(String(100))
    category = Column(String(50))
    manufacturer = Column(String(100))
    model = Column(String(50))
    serial_no = Column(String(100))
    installed_at = Column(Date)
    ownership = Column(String(20))
    current_site_id = Column(String(20), ForeignKey("hse.dim_site.site_id"))
    current_owner = Column(String(50))
    inspection_type = Column(String(100))
    certification_type = Column(String(100))
    next_inspection = Column(Date)
    certification_expiry = Column(Date)
    operational_hours = Column(Numeric(10, 2), default=0)
    days_since_last_insp = Column(Integer)
    active_from = Column(Date, default=datetime.now().date)
    active_to = Column(Date, default=datetime(9999, 12, 12).date())


class DimIncident(Base):
    __tablename__ = "dim_incident"
    __table_args__ = {"schema": "hse"}

    incident_id = Column(String(30), primary_key=True)
    incident_type = Column(String(50))
    incident_category = Column(String(100))
    severity_class = Column(String(20))
    body_part = Column(String(50))
    agency_type = Column(String(20))
    incident_cause = Column(String(100))
    preliminary_cause = Column(String(200))
    incident_location = Column(String(200))
    ptw_required = Column(Boolean, default=False)
    ptw_used = Column(Boolean, default=False)
    ptw_approved = Column(Boolean, default=False)
    investigation_required = Column(Boolean, default=False)
    case_status = Column(String(20), default="Reported")
    investigation_lead = Column(String(100))
    investigation_due = Column(Date)
    root_cause = Column(Text)
    corrective_action = Column(Text)
    preventive_action = Column(Text)
    insurance_claim = Column(Boolean, default=False)
    claim_amt_usd = Column(Numeric(15, 2), default=0)
    lost_days = Column(Integer, default=0)
    restricted_days = Column(Integer, default=0)


class DimPTW(Base):
    __tablename__ = "dim_ptw"
    __table_args__ = {"schema": "hse"}

    ptw_id = Column(String(30), primary_key=True)
    ptw_type = Column(String(100))
    ptw_category = Column(String(50))
    issued_by = Column(String(100))
    approved_by = Column(String(100))
    site_id = Column(String(20), ForeignKey("hse.dim_site.site_id"))
    workstation = Column(String(200))
    start_at = Column(DateTime)
    end_at = Column(DateTime)
    hazard_identified = Column(String(200))
    mitigation_list = Column(Text)
    isolation_list = Column(Text)
    cna_required = Column(Boolean, default=False)
    gas_test_done = Column(Boolean, default=False)
    gas_test_result = Column(String(20))
    sign_in = Column(DateTime)
    sign_out = Column(DateTime)
    is_cancelled = Column(Boolean, default=False)
    cancellation_reason = Column(Text)
    violation_count = Column(Integer, default=0)
    ptw_status = Column(String(20), default="OPEN")


class DimEnvironmental(Base):
    __tablename__ = "dim_environmental"
    __table_args__ = {"schema": "hse"}

    env_id = Column(String(30), primary_key=True)
    parameter_type = Column(String(100))
    parameter_name = Column(String(100))
    monitoring_point = Column(String(200))
    site_id = Column(String(20), ForeignKey("hse.dim_site.site_id"))
    lab_method = Column(String(100))
    regulatory_limit = Column(Numeric(15, 4))
    unit_of_measure = Column(String(20))
    frequency = Column(String(20))
    data_quality_flag = Column(String(20), default="Valid")


class DimTraining(Base):
    __tablename__ = "dim_training"
    __table_args__ = {"schema": "hse"}

    training_id = Column(String(30), primary_key=True)
    training_program = Column(String(200))
    training_type = Column(String(50))
    certification_name = Column(String(200))
    cert_validity_months = Column(Integer)
    competency_area = Column(String(100))
    mandatory_frequency = Column(String(50))


class DimContractor(Base):
    __tablename__ = "dim_contractor"
    __table_args__ = {"schema": "hse"}

    contractor_id = Column(String(20), primary_key=True)
    contractor_name = Column(String(200), nullable=False)
    contractor_type = Column(String(100))
    risk_rating = Column(String(20))
    hse_cert_expiry = Column(Date)
    insurance_valid = Column(Date)
    site_access_until = Column(Date)
    hse_audit_result = Column(String(20))
    lat_audit_date = Column(Date)
    active_from = Column(Date, default=datetime.now().date)
    active_to = Column(Date, default=datetime(9999, 12, 12).date())


class FactHSE(Base):
    __tablename__ = "fact_hse"
    __table_args__ = {"schema": "hse"}

    fact_id = Column(Integer, primary_key=True, autoincrement=True)
    date_key = Column(Date, nullable=False)
    site_key = Column(String(20), ForeignKey("hse.dim_site.site_id"), nullable=False)
    dept_key = Column(String(20), ForeignKey("hse.dim_department.dept_id"))
    emp_key = Column(String(20), ForeignKey("hse.dim_employee.employee_id"))
    equip_key = Column(String(50), ForeignKey("hse.dim_equipment.equipment_id"))
    contractor_key = Column(String(20), ForeignKey("hse.dim_contractor.contractor_id"))
    incident_key = Column(String(30), ForeignKey("hse.dim_incident.incident_id"))
    ptw_key = Column(String(30), ForeignKey("hse.dim_ptw.ptw_id"))
    hazard_key = Column(String(20))
    train_key = Column(String(30), ForeignKey("hse.dim_training.training_id"))

    man_hours_worked = Column(Numeric(12, 2), default=0)
    headcount_present = Column(Integer, default=0)
    headcount_leave = Column(Integer, default=0)
    headcount_contractor = Column(Integer, default=0)

    lti_count = Column(Integer, default=0)
    mti_count = Column(Integer, default=0)
    fai_count = Column(Integer, default=0)
    near_miss_count = Column(Integer, default=0)
    fatality_count = Column(Integer, default=0)
    first_aid_count = Column(Integer, default=0)
    property_dmg_count = Column(Integer, default=0)
    env_incident_count = Column(Integer, default=0)

    env_reading_value = Column(Numeric(15, 4))
    env_limit_value = Column(Numeric(15, 4), default=9999)
    env_exceeded = Column(Boolean, default=False)
    env_sample_id = Column(String(50))

    ptw_issued_count = Column(Integer, default=0)
    ptw_closed_count = Column(Integer, default=0)
    ptw_open_count = Column(Integer, default=0)
    ptw_violation_count = Column(Integer, default=0)
    gas_clearance_count = Column(Integer, default=0)

    inspection_count = Column(Integer, default=0)
    observation_count = Column(Integer, default=0)
    observation_safe = Column(Integer, default=0)
    observation_unsafe = Column(Integer, default=0)

    training_passed_count = Column(Integer, default=0)
    training_failed_count = Column(Integer, default=0)
    training_pending_count = Column(Integer, default=0)

    equipment_insp_pass_count = Column(Integer, default=0)
    equipment_insp_fail_count = Column(Integer, default=0)
    equipment_down_count = Column(Integer, default=0)

    audit_score = Column(Numeric(5, 2))
    audit_findings = Column(Integer, default=0)
    audit_critical = Column(Integer, default=0)
    audit_major = Column(Integer, default=0)
    audit_minor = Column(Integer, default=0)

    metric_value = Column(Numeric(15, 4))
    metric_type = Column(String(50))

    risk_score = Column(Numeric(5, 2))
    risk_level = Column(String(20))

    weather_condition = Column(String(50))
    shift_name = Column(String(20))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("date_key", "site_key", "dept_key", "metric_type", name="uq_daily_metric"),
        {"schema": "hse"},
    )


class SecurityUserRole(Base):
    __tablename__ = "security_user_role"
    __table_args__ = {"schema": "hse"}

    user_role_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("hse.security_users.user_id"), nullable=False)
    role_id = Column(Integer, ForeignKey("hse.security_roles.role_id"), nullable=False)
    site_access = Column(String(500), nullable=False, default="ALL")
    department_access = Column(String(500))
    contractor_access = Column(String(500))
    assigned_at = Column(DateTime, default=datetime.utcnow)
    assigned_by = Column(String(200))
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_role"),
        {"schema": "hse"},
    )


class SecurityUser(Base):
    __tablename__ = "security_users"
    __table_args__ = {"schema": "hse"}

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(200), unique=True, nullable=False)
    username = Column(String(100), unique=True)
    full_name = Column(String(200), nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_locked = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    last_login_at = Column(DateTime)
    last_login_ip = Column(String(45))
    last_login_user_agent = Column(Text)
    password_changed_at = Column(DateTime, default=datetime.utcnow)
    password_expires_at = Column(DateTime, default=datetime.utcnow() + timedelta(days=90))
    must_change_password = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(200))
    updated_by = Column(String(200))


class SecurityRole(Base):
    __tablename__ = "security_roles"
    __table_args__ = {"schema": "hse"}

    role_id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(50), unique=True, nullable=False)
    role_display_name = Column(String(100), nullable=False)
    role_description = Column(Text)
    parent_role_id = Column(Integer, ForeignKey("hse.security_roles.role_id"))
    is_system_role = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SecurityPermission(Base):
    __tablename__ = "security_permissions"
    __table_args__ = {"schema": "hse"}

    permission_id = Column(Integer, primary_key=True, autoincrement=True)
    permission_name = Column(String(100), unique=True, nullable=False)
    permission_display_name = Column(String(100), nullable=False)
    module = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class SecurityRolePermission(Base):
    __tablename__ = "security_role_permission"
    __table_args__ = {"schema": "hse"}

    role_id = Column(Integer, ForeignKey("hse.security_roles.role_id", ondelete="CASCADE"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("hse.security_permissions.permission_id", ondelete="CASCADE"), primary_key=True)
    granted_at = Column(DateTime, default=datetime.utcnow)
    granted_by = Column(String(200))


class SecuritySession(Base):
    __tablename__ = "security_sessions"
    __table_args__ = {"schema": "hse"}

    session_id = Column(String(255), primary_key=True)
    user_id = Column(Integer, ForeignKey("hse.security_users.user_id", ondelete="CASCADE"), nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    device_info = Column(JSONB)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    logged_out_at = Column(DateTime)
    is_active = Column(Boolean, default=True)


class SecurityLoginHistory(Base):
    __tablename__ = "security_login_history"
    __table_args__ = {"schema": "hse"}

    login_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("hse.security_users.user_id", ondelete="SET NULL"))
    email = Column(String(200))
    login_type = Column(String(20), nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    device_info = Column(JSONB)
    login_status = Column(String(20), nullable=False)
    failure_reason = Column(Text)
    location = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)


# Indexes (for query performance)
Index("idx_fact_hse_date_site", FactHSE.date_key, FactHSE.site_key)
Index("idx_fact_hse_dept", FactHSE.dept_key)
Index("idx_fact_hse_emp", FactHSE.emp_key)
Index("idx_fact_hse_ptw", FactHSE.ptw_key)
Index("idx_fact_hse_incident", FactHSE.incident_key)
Index("idx_fact_hse_equip", FactHSE.equip_key)
Index("idx_fact_hse_env_exceeded", FactHSE.env_exceeded, postgresql_where=FactHSE.env_exceeded == True)
Index("idx_fact_hse_metric", FactHSE.metric_type, FactHSE.date_key)

Index("idx_security_users_email", SecurityUser.email)
Index("idx_security_users_active", SecurityUser.is_active, SecurityUser.is_locked)
Index("idx_security_sessions_user", SecuritySession.user_id, SecuritySession.is_active)
Index("idx_security_sessions_expires", SecuritySession.expires_at)
Index("idx_security_login_history_user", SecurityLoginHistory.user_id, SecurityLoginHistory.created_at)
Index("idx_security_login_history_email", SecurityLoginHistory.email, SecurityLoginHistory.created_at)
