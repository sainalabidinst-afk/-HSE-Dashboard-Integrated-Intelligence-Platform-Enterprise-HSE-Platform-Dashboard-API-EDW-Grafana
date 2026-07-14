"""
Repository tests.
Tests data access layer for Auth, Dashboard, Audit, and Alert repositories.
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import Integer

from app.repositories import AuthRepository, DashboardRepository, AlertRepository, AuditRepository, EvidenceRepository
from app.models.audit import AuditPlan, AuditFinding, Evidence
from app.models.audit import AuditPlan, AuditFinding, Evidence


class TestAuthRepository:
    """Test AuthRepository methods."""

    def test_get_user_by_email(self, db_session, sample_user):
        repo = AuthRepository(db_session)
        user = repo.get_user_by_email(sample_user.email)
        assert user is not None
        assert user.user_id == sample_user.user_id

    def test_get_user_by_email_not_found(self, db_session):
        repo = AuthRepository(db_session)
        user = repo.get_user_by_email("nonexistent@company.com")
        assert user is None

    def test_get_user_by_id(self, db_session, sample_user):
        repo = AuthRepository(db_session)
        user = repo.get_user_by_id(sample_user.user_id)
        assert user is not None
        assert user.email == sample_user.email

    def test_get_user_roles(self, db_session, sample_user, sample_role):
        repo = AuthRepository(db_session)
        from app.models.hse_models import SecurityUserRole
        sur = SecurityUserRole(user_id=sample_user.user_id, role_id=sample_role.role_id, site_access="ALL")
        db_session.add(sur)
        db_session.commit()
        roles = repo.get_user_roles(sample_user.user_id)
        assert len(roles) == 1
        assert roles[0].role_id == sample_role.role_id

    def test_get_user_permissions(self, db_session, sample_user, sample_role, sample_permission):
        repo = AuthRepository(db_session)
        from app.models.hse_models import SecurityUserRole, SecurityRolePermission
        db_session.add_all([
            SecurityUserRole(user_id=sample_user.user_id, role_id=sample_role.role_id, site_access="ALL"),
            SecurityRolePermission(role_id=sample_role.role_id, permission_id=sample_permission.permission_id),
        ])
        db_session.commit()
        perms = repo.get_user_permissions(sample_user.user_id)
        assert sample_permission.permission_name in perms

    def test_get_user_site_access_all(self, db_session, sample_user, sample_role):
        repo = AuthRepository(db_session)
        from app.models.hse_models import SecurityUserRole
        sur = SecurityUserRole(user_id=sample_user.user_id, role_id=sample_role.role_id, site_access="ALL")
        db_session.add(sur)
        db_session.commit()
        access = repo.get_user_site_access(sample_user.user_id)
        assert access == ["ALL"]

    def test_get_user_site_access_specific(self, db_session, sample_user, sample_role):
        repo = AuthRepository(db_session)
        from app.models.hse_models import SecurityUserRole
        sur = SecurityUserRole(user_id=sample_user.user_id, role_id=sample_role.role_id, site_access="SITE-A,SITE-B")
        db_session.add(sur)
        db_session.commit()
        access = repo.get_user_site_access(sample_user.user_id)
        assert "SITE-A" in access
        assert "SITE-B" in access

    def test_create_and_get_session(self, db_session, sample_user):
        repo = AuthRepository(db_session)
        session = repo.create_session("sess-001", sample_user.user_id, "127.0.0.1", "test-agent")
        assert session.session_id == "sess-001"
        assert session.user_id == sample_user.user_id

        active = repo.get_active_session("sess-001")
        assert active is not None
        assert active.session_id == "sess-001"

    def test_invalidate_session(self, db_session, sample_user):
        repo = AuthRepository(db_session)
        repo.create_session("sess-002", sample_user.user_id, "127.0.0.1", "test-agent")
        result = repo.invalidate_session("sess-002")
        assert result is True
        active = repo.get_active_session("sess-002")
        assert active is None

    def test_record_login_attempt(self, db_session, sample_user):
        repo = AuthRepository(db_session)
        history = repo.record_login_attempt(
            user_id=sample_user.user_id,
            email=sample_user.email,
            login_type="password",
            ip_address="127.0.0.1",
            user_agent="test-agent",
            login_status="success",
        )
        assert history.login_id is not None
        assert history.login_status == "success"

    def test_increment_failed_login(self, db_session, sample_user):
        repo = AuthRepository(db_session)
        repo.increment_failed_login(sample_user)
        assert sample_user.failed_login_attempts == 1
        assert sample_user.is_locked is False

        for _ in range(4):
            repo.increment_failed_login(sample_user)
        assert sample_user.is_locked is True
        assert sample_user.locked_until is not None


class TestDashboardRepository:
    """Test DashboardRepository methods."""

    def test_get_executive_summary(self, db_session, sample_site, sample_department, sample_fact_hse):
        repo = DashboardRepository(db_session)
        data = repo.get_executive_summary(site_id="TEST-SITE-A", period_days=30)
        assert "total_man_hours" in data
        assert "ltifr" in data
        assert "trir" in data
        assert data["total_man_hours"] > 0

    def test_get_executive_summary_all_sites(self, db_session, sample_fact_hse):
        repo = DashboardRepository(db_session)
        data = repo.get_executive_summary(site_id="all", period_days=30)
        assert "ltifr" in data
        assert data["total_man_hours"] > 0

    def test_get_incident_trend(self, db_session, sample_site, sample_department):
        repo = DashboardRepository(db_session)
        from app.models.hse_models import FactHSE, DimIncident
        inc = DimIncident(
            incident_id="INC-TEST-001",
            incident_type="Near Miss",
            incident_category="Slip/Trip",
            severity_class="Minor",
            agency_type="Employee",
            incident_cause="Unsafe Condition",
            incident_location="Test Area",
            case_status="Closed",
        )
        db_session.add(inc)
        db_session.commit()
        db_session.refresh(inc)
        fact = FactHSE(
            date_key=date.today(),
            site_key=sample_site.site_id,
            dept_key=sample_department.dept_id,
            incident_key=inc.incident_id,
            man_hours_worked=1000.0,
            near_miss_count=1,
        )
        db_session.add(fact)
        db_session.commit()

        trend = repo.get_incident_trend(site_id="TEST-SITE-A", start_date=date.today() - timedelta(days=7), end_date=date.today())
        assert len(trend) > 0
        assert "date" in trend[0]
        assert "near_miss" in trend[0]

    def test_get_ptw_summary(self, db_session, sample_site, sample_department):
        repo = DashboardRepository(db_session)
        from app.models.hse_models import FactHSE
        fact = FactHSE(
            date_key=date.today(),
            site_key=sample_site.site_id,
            dept_key=sample_department.dept_id,
            ptw_issued_count=10,
            ptw_closed_count=5,
            ptw_open_count=3,
            ptw_violation_count=1,
            man_hours_worked=1000.0,
        )
        db_session.add(fact)
        db_session.commit()
        summary = repo.get_ptw_summary(site_id="TEST-SITE-A", period_days=30)
        assert summary["issued"] == 10
        assert summary["closed_count"] == 5
        assert summary["open_count"] == 3
        assert summary["compliance_rate"] == 50.0


class TestAlertRepository:
    """Test AlertRepository methods."""

    def test_create_and_get_alert_rule(self, db_session, sample_site):
        repo = AlertRepository(db_session)
        from app.models.alert import MetricType, AlertSeverity
        rule = repo.create_alert_rule({
            "rule_name": "Repo Test Rule",
            "metric_type": MetricType.LTIFR,
            "condition": ">",
            "threshold_value": 2.0,
            "severity": AlertSeverity.WARNING,
            "site_id": sample_site.site_id,
            "notification_channels": ["dashboard"],
            "recipients": [],
            "is_active": True,
        })
        assert rule.rule_id is not None

        fetched = repo.get_alert_rule(rule.rule_id)
        assert fetched is not None
        assert fetched.rule_name == "Repo Test Rule"

    def test_get_alert_rules_filter_by_site(self, db_session, sample_site):
        repo = AlertRepository(db_session)
        from app.models.alert import MetricType, AlertSeverity
        rule1 = repo.create_alert_rule({
            "rule_name": "Site A Rule",
            "metric_type": MetricType.LTIFR,
            "condition": ">",
            "threshold_value": 2.0,
            "severity": AlertSeverity.WARNING,
            "site_id": sample_site.site_id,
            "notification_channels": ["dashboard"],
            "recipients": [],
            "is_active": True,
        })
        rules = repo.get_alert_rules(site_id=sample_site.site_id)
        assert any(r["rule_id"] == rule1.rule_id for r in rules)

    def test_create_and_acknowledge_alert(self, db_session, sample_site):
        repo = AlertRepository(db_session)
        alert = repo.create_alert({
            "alert_type": "Test Alert",
            "severity": "warning",
            "status": "active",
            "site_id": sample_site.site_id,
            "site_name": sample_site.site_name,
            "message": "Test alert message",
            "triggered_by": "system",
        })
        assert alert.alert_id is not None

        acked = repo.acknowledge_alert(alert.alert_id, "test@company.com")
        assert acked is not None
        assert acked.status == "acknowledged"
        assert acked.acknowledged_by == "test@company.com"


class TestAuditRepository:
    """Test AuditRepository and EvidenceRepository methods."""

    def test_create_and_get_audit_plan(self, db_session, sample_site):
        from app.models.audit import AuditPlan
        from datetime import date, timedelta
        plan = AuditPlan(
            audit_id="AUDIT-REPO-001",
            audit_type="internal",
            audit_status="planned",
            audit_title="Repo Test Audit",
            site_id=sample_site.site_id,
            lead_auditor="Test Auditor",
            scope="Test scope",
            criteria="Test criteria",
            scheduled_start=date.today(),
            scheduled_end=date.today() + timedelta(days=7),
            created_by="test@company.com",
        )
        db_session.add(plan)
        db_session.commit()

        repo = AuditRepository(db_session)
        plans = repo.get_audit_plans(site_id=sample_site.site_id)
        assert any(p["audit_id"] == "AUDIT-REPO-001" for p in plans)

    def test_create_and_get_evidence(self, db_session):
        repo = EvidenceRepository(db_session)
        evidence = repo.upload_evidence(
            evidence_type="document",
            file_name="test_evidence.pdf",
            file_path="/tmp/test_evidence.pdf",
            uploaded_by="test@company.com",
            finding_id="FINDING-001",
            description="Test evidence file",
        )
        assert evidence.evidence_id is not None

        evidence_list = repo.get_evidence(finding_id="FINDING-001")
        assert len(evidence_list) == 1
