"""
Test factories for generating test data.
Uses factory_boy for clean, reusable test fixtures.
"""

import factory
from datetime import date, datetime, timedelta
from app.models.hse_models import (
    SecurityUser, SecurityRole, SecurityPermission,
    SecurityRolePermission, SecurityUserRole,
    FactHSE, DimSite, DimDepartment, DimEmployee,
    DimEquipment, DimContractor, DimIncident, DimPTW,
    DimEnvironmental, DimTraining
)
from app.models.audit import AuditPlan, AuditFinding, Evidence, CorrectiveAction
from app.models.alert import AlertRule, Alert, NotificationLog
from app.utils.security import hash_password


class DimSiteFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DimSite
        sqlalchemy_session = None  # set in conftest
        sqlalchemy_session_persistence = "commit"

    site_id = factory.Sequence(lambda n: f"TEST-SITE-{n:03d}")
    site_name = factory.Sequence(lambda n: f"Test Site {n}")
    site_type = "Mining"
    location_lat = -6.2088
    location_long = 106.8456
    zone = "Test Zone"
    area_type = "Open Pit"
    site_status = "Active"
    managing_director = "Test Director"
    timezone = "Asia/Jakarta"
    active_from = date.today()
    active_to = date(9999, 12, 12)


class DimDepartmentFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DimDepartment
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    dept_id = factory.Sequence(lambda n: f"TEST-DEPT-{n:03d}")
    dept_name = factory.Sequence(lambda n: f"Test Department {n}")
    dept_type = "Operations"
    parent_dept_id = None
    site_id = factory.SubFactory(DimSiteFactory)
    head_of_dept = "Test Head"
    budget_code = factory.Sequence(lambda n: f"BUDGET-{n:03d}")
    active_from = date.today()
    active_to = date(9999, 12, 12)


class SecurityUserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = SecurityUser
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    email = factory.Sequence(lambda n: f"test.user{n}@company.com")
    username = factory.Sequence(lambda n: f"testuser{n}")
    full_name = factory.Sequence(lambda n: f"Test User {n}")
    password_hash = hash_password("TestPass123!")
    is_active = True
    is_locked = False
    failed_login_attempts = 0
    last_login_ip = "127.0.0.1"
    last_login_user_agent = "test-client"
    password_changed_at = datetime.utcnow()
    password_expires_at = datetime.utcnow() + timedelta(days=90)
    must_change_password = False


class SecurityRoleFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = SecurityRole
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    role_name = factory.Sequence(lambda n: f"test_role_{n}")
    role_display_name = factory.Sequence(lambda n: f"Test Role {n}")
    role_description = "Test role description"
    is_system_role = False
    is_active = True


class SecurityPermissionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = SecurityPermission
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    permission_name = factory.Sequence(lambda n: f"test:permission{n}")
    permission_display_name = factory.Sequence(lambda n: f"Test Permission {n}")
    module = "test"
    action = "view"
    description = "Test permission"


class SecurityUserRoleFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = SecurityUserRole
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    user_id = factory.SelfAttribute("user.user_id")
    role_id = factory.SelfAttribute("role.role_id")
    site_access = "ALL"
    department_access = None
    contractor_access = None
    is_active = True
    assigned_by = "system"


class FactHSEFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = FactHSE
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    date_key = date.today()
    site_key = factory.SubFactory(DimSiteFactory)
    dept_key = factory.SubFactory(DimDepartmentFactory)
    emp_key = None
    equip_key = None
    contractor_key = None
    incident_key = None
    ptw_key = None
    hazard_key = None
    train_key = None
    man_hours_worked = 1000.0
    headcount_present = 50
    headcount_leave = 5
    headcount_contractor = 10
    lti_count = 0
    mti_count = 0
    fai_count = 1
    near_miss_count = 2
    fatality_count = 0
    first_aid_count = 0
    property_dmg_count = 0
    env_incident_count = 0
    env_reading_value = 25.0
    env_limit_value = 50.0
    env_exceeded = False
    env_sample_id = None
    ptw_issued_count = 3
    ptw_closed_count = 1
    ptw_open_count = 2
    ptw_violation_count = 0
    gas_clearance_count = 0
    inspection_count = 5
    observation_count = 10
    observation_safe = 8
    observation_unsafe = 2
    training_passed_count = 10
    training_failed_count = 0
    training_pending_count = 5
    equipment_insp_pass_count = 4
    equipment_insp_fail_count = 0
    equipment_down_count = 0
    audit_score = 95.5
    audit_findings = 0
    audit_critical = 0
    audit_major = 0
    audit_minor = 0
    metric_value = None
    metric_type = None
    risk_score = None
    risk_level = None
    weather_condition = "Clear"
    shift_name = "Day"


class AuditPlanFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = AuditPlan
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    audit_id = factory.Sequence(lambda n: f"AUDIT-TEST-{n:03d}")
    audit_type = "internal"
    audit_status = "planned"
    audit_title = factory.Sequence(lambda n: f"Test Audit Plan {n}")
    standard_ref = "ISO 45001"
    site_id = factory.SubFactory(DimSiteFactory)
    department_id = None
    lead_auditor = "Test Auditor"
    audit_team = ["Auditor 1", "Auditor 2"]
    scope = "Test scope"
    criteria = "Test criteria"
    scheduled_start = date.today()
    scheduled_end = date.today() + timedelta(days=7)
    actual_start = None
    actual_end = None
    findings_count = 0
    major_findings = 0
    minor_findings = 0
    observations = 0
    compliance_score = None
    audit_report = None
    created_by = "test@company.com"


class AlertRuleFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = AlertRule
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    rule_id = factory.Sequence(lambda n: f"RULE-TEST-{n:03d}")
    rule_name = factory.Sequence(lambda n: f"Test Alert Rule {n}")
    metric_type = "ltifr"
    condition = ">"
    threshold_value = 2.0
    severity = "warning"
    site_id = factory.SubFactory(DimSiteFactory)
    department_id = None
    notification_channels = ["dashboard"]
    recipients = []
    is_active = True
    cooldown_minutes = 60
    last_triggered_at = None
    description = "Test alert rule"
    created_by = "test@company.com"


class AlertFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Alert
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    alert_id = factory.Sequence(lambda n: f"ALERT-TEST-{n:03d}")
    rule_id = None
    alert_type = "LTIFR Critical"
    severity = "warning"
    status = "active"
    site_id = factory.SubFactory(DimSiteFactory)
    site_name = "Test Site"
    metric_type = "ltifr"
    metric_value = 2.5
    threshold_value = 2.0
    message = "Test alert message"
    details = None
    triggered_by = "system"
    acknowledged_by = None
    acknowledged_at = None
    resolved_by = None
    resolved_at = None
    resolution_notes = None
    alert_date = date.today()
    created_at = datetime.utcnow()
    updated_at = datetime.utcnow()
