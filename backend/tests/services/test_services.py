"""
Service layer tests.
Tests business logic for DashboardService, AuthService, AuditService, AlertService.
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal

from app.services import DashboardService, AuthService, AuditService, AlertService
from app.models.audit import AuditPlan, AuditFinding


class TestDashboardService:
    """Test DashboardService business logic."""

    def test_get_executive_summary_with_data(self, db_session, sample_site, sample_department, sample_fact_hse):
        service = DashboardService(db_session)
        summary = service.get_executive_summary(site_id="TEST-SITE-A", period_days=30)
        assert hasattr(summary, "kpis")
        assert len(summary.kpis) > 0
        assert summary.period_days == 30

    def test_rag_status_lower_is_better(self, db_session):
        service = DashboardService(db_session)
        assert service._rag_status(0.5, 1.0, 2.0, lower_is_better=True) == "green"
        assert service._rag_status(1.5, 1.0, 2.0, lower_is_better=True) == "amber"
        assert service._rag_status(3.0, 1.0, 2.0, lower_is_better=True) == "red"

    def test_rag_status_higher_is_better(self, db_session):
        service = DashboardService(db_session)
        assert service._rag_status(96.0, 95.0, 85.0, lower_is_better=False) == "green"
        assert service._rag_status(90.0, 95.0, 85.0, lower_is_better=False) == "amber"
        assert service._rag_status(80.0, 95.0, 85.0, lower_is_better=False) == "red"

    def test_get_incident_summary(self, db_session, sample_site, sample_department):
        service = DashboardService(db_session)
        summary = service.get_incident_summary(site_id="TEST-SITE-A", period_days=30)
        assert "trend" in summary
        assert "distribution" in summary
        assert "by_department" in summary

    def test_get_ptw_summary(self, db_session):
        service = DashboardService(db_session)
        from app.models.hse_models import FactHSE, DimSite, DimDepartment
        from datetime import date
        site = db_session.query(DimSite).first()
        dept = db_session.query(DimDepartment).first()
        if site and dept:
            fact = FactHSE(
                date_key=date.today(),
                site_key=site.site_id,
                dept_key=dept.dept_id,
                ptw_issued_count=10,
                ptw_closed_count=5,
                ptw_open_count=3,
                ptw_violation_count=1,
                man_hours_worked=1000.0,
            )
            db_session.add(fact)
            db_session.commit()
        summary = service.get_ptw_summary(site_id="all", period_days=30)
        assert hasattr(summary, "open_count")
        assert hasattr(summary, "closed_count")
        assert hasattr(summary, "compliance_rate")

    def test_get_environmental_summary(self, db_session, sample_site, sample_department):
        service = DashboardService(db_session)
        from app.models.hse_models import FactHSE, DimEnvironmental
        env_param = DimEnvironmental(
            env_id="ENV-TEST-001",
            parameter_type="Air Quality",
            parameter_name="PM2.5",
            monitoring_point="Test Point",
            site_id=sample_site.site_id,
            regulatory_limit=50.0,
            unit_of_measure="µg/m³",
            frequency="Hourly",
        )
        db_session.add(env_param)
        db_session.commit()
        db_session.refresh(env_param)

        fact = FactHSE(
            date_key=date.today(),
            site_key=sample_site.site_id,
            dept_key=sample_department.dept_id,
            env_sample_id=env_param.env_id,
            env_reading_value=30.0,
            env_limit_value=50.0,
            env_exceeded=False,
            man_hours_worked=1000.0,
        )
        db_session.add(fact)
        db_session.commit()

        summary = service.get_environmental_summary(site_id="TEST-SITE-A", period_days=30)
        assert hasattr(summary, "pm25_current")
        assert hasattr(summary, "noise_current")
        assert hasattr(summary, "exceedances")


class TestAuthService:
    """Test AuthService business logic."""

    def test_authenticate_success(self, db_session, sample_user, sample_role, sample_permission):
        service = AuthService(db_session)
        from app.models.hse_models import SecurityUserRole, SecurityRolePermission
        db_session.add_all([
            SecurityUserRole(user_id=sample_user.user_id, role_id=sample_role.role_id, site_access="ALL"),
            SecurityRolePermission(role_id=sample_role.role_id, permission_id=sample_permission.permission_id),
        ])
        db_session.commit()

        result = service.authenticate(sample_user.email, "TestPass123!", "127.0.0.1", "test-agent")
        assert result is not None
        assert "access_token" in result
        assert "refresh_token" in result
        assert result["role"] == "test_role"

    def test_authenticate_failure(self, db_session, sample_user):
        service = AuthService(db_session)
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            service.authenticate(sample_user.email, "WrongPassword!", "127.0.0.1", "test-agent")
        assert exc_info.value.status_code == 401

    def test_get_user_permissions(self, db_session, sample_user, sample_role, sample_permission):
        service = AuthService(db_session)
        from app.models.hse_models import SecurityUserRole, SecurityRolePermission
        db_session.add_all([
            SecurityUserRole(user_id=sample_user.user_id, role_id=sample_role.role_id, site_access="ALL"),
            SecurityRolePermission(role_id=sample_role.role_id, permission_id=sample_permission.permission_id),
        ])
        db_session.commit()
        perms = service.get_user_permissions(sample_user.user_id)
        assert sample_permission.permission_name in perms

    def test_has_permission_service(self, db_session):
        service = AuthService(db_session)
        assert service.has_permission(["incident:view"], "incident:view") is True
        assert service.has_permission(["incident:view"], "user:delete") is False

    def test_can_access_site_service(self, db_session):
        service = AuthService(db_session)
        assert service.can_access_site(["ALL"], "SITE-A") is True
        assert service.can_access_site(["SITE-A"], "SITE-B") is False


class TestAuditService:
    """Test AuditService business logic."""

    def test_create_and_get_audit_plan(self, db_session, sample_site):
        service = AuditService(db_session)
        plan = service.create_audit_plan({
            "audit_id": "AUDIT-SVC-001",
            "audit_type": "internal",
            "audit_status": "planned",
            "audit_title": "Service Test Audit",
            "site_id": sample_site.site_id,
            "lead_auditor": "Test Auditor",
            "created_by": "test@company.com",
        })
        assert plan["audit_id"] == "AUDIT-SVC-001"
        assert plan["audit_title"] == "Service Test Audit"

        fetched = service.get_audit_plan("AUDIT-SVC-001")
        assert fetched is not None
        assert fetched["audit_title"] == "Service Test Audit"

    def test_update_audit_plan(self, db_session, sample_site):
        service = AuditService(db_session)
        plan = service.create_audit_plan({
            "audit_id": "AUDIT-SVC-002",
            "audit_type": "external",
            "audit_status": "planned",
            "audit_title": "Original Title",
            "site_id": sample_site.site_id,
            "created_by": "test@company.com",
        })
        updated = service.update_audit_plan("AUDIT-SVC-002", {"audit_title": "Updated Title", "audit_status": "in_progress"})
        assert updated["audit_title"] == "Updated Title"
        assert updated["audit_status"] == "in_progress"

    def test_create_and_get_finding(self, db_session, sample_site):
        service = AuditService(db_session)
        plan = service.create_audit_plan({
            "audit_id": "AUDIT-SVC-003",
            "audit_type": "internal",
            "audit_status": "planned",
            "audit_title": "Finding Test Audit",
            "site_id": sample_site.site_id,
            "created_by": "test@company.com",
        })
        finding = service.create_finding({
            "audit_id": "AUDIT-SVC-003",
            "finding_type": "minor",
            "description": "Test finding description",
            "created_by": "test@company.com",
        })
        assert finding["audit_id"] == "AUDIT-SVC-003"
        assert finding["finding_type"] == "minor"

        findings = service.get_findings(audit_id="AUDIT-SVC-003")
        assert len(findings) == 1

    def test_upload_evidence(self, db_session):
        service = AuditService(db_session)
        evidence = service.upload_evidence({
            "evidence_type": "document",
            "file_name": "test_evidence.pdf",
            "file_path": "/tmp/test_evidence.pdf",
            "uploaded_by": "test@company.com",
            "finding_id": "FINDING-001",
            "description": "Test evidence",
        })
        assert evidence.evidence_id is not None
        assert evidence.file_name == "test_evidence.pdf"

        evidence_list = service.get_evidence(finding_id="FINDING-001")
        assert len(evidence_list) == 1

    def test_create_audit_trail(self, db_session):
        service = AuditService(db_session)
        trail = service.create_audit_trail(
            user_id=1,
            action="create",
            table_name="audit_plans",
            record_id="AUDIT-001",
            old_values=None,
            new_values={"audit_title": "Test"},
            ip_address="127.0.0.1",
            user_agent="test",
            session_id="sess-001",
        )
        assert trail.trail_id is not None
        assert trail.action == "create"
        assert trail.table_name == "audit_plans"


class TestAlertService:
    """Test AlertService business logic."""

    def test_create_and_get_alert_rule(self, db_session, sample_site):
        service = AlertService(db_session)
        rule = service.create_alert_rule({
            "rule_name": "Service Test Rule",
            "metric_type": "ltifr",
            "condition": ">",
            "threshold_value": 2.0,
            "severity": "warning",
            "site_id": sample_site.site_id,
            "notification_channels": ["dashboard"],
            "recipients": [],
            "is_active": True,
        }, created_by="test@company.com")
        assert rule.rule_id is not None

        rules = service.get_alert_rules(site_id=sample_site.site_id)
        assert any(r["rule_id"] == rule.rule_id for r in rules)

    def test_create_and_acknowledge_alert(self, db_session, sample_site):
        service = AlertService(db_session)
        alert = service.repo.create_alert({
            "alert_type": "Test Alert",
            "severity": "warning",
            "status": "active",
            "site_id": sample_site.site_id,
            "site_name": sample_site.site_name,
            "message": "Test alert",
            "triggered_by": "system",
        })
        assert alert.alert_id is not None

        acked = service.acknowledge_alert(alert.alert_id, "test@company.com")
        assert acked is not None
        assert acked.status == "acknowledged"

    def test_resolve_alert(self, db_session, sample_site):
        service = AlertService(db_session)
        alert = service.repo.create_alert({
            "alert_type": "Test Alert 2",
            "severity": "critical",
            "status": "active",
            "site_id": sample_site.site_id,
            "site_name": sample_site.site_name,
            "message": "Test alert 2",
            "triggered_by": "system",
        })
        assert alert.alert_id is not None

        resolved = service.resolve_alert(alert.alert_id, "test@company.com", notes="Resolved")
        assert resolved is not None
        assert resolved.status == "resolved"
        assert resolved.resolution_notes == "Resolved"
