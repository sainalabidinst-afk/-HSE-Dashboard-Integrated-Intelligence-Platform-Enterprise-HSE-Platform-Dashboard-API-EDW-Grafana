"""
API controller tests.
Tests FastAPI endpoints for auth, dashboard, audit, alerts, reports, and data quality.
"""

import pytest
from fastapi.testclient import TestClient


class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_login_success(self, client: TestClient, sample_user, sample_role, sample_permission, db_session):
        from app.models.hse_models import SecurityUserRole, SecurityRolePermission
        db_session.add_all([
            SecurityUserRole(user_id=sample_user.user_id, role_id=sample_role.role_id, site_access="ALL"),
            SecurityRolePermission(role_id=sample_role.role_id, permission_id=sample_permission.permission_id),
        ])
        db_session.commit()

        response = client.post(
            "/auth/login",
            data={"username": sample_user.email, "password": "TestPass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_password(self, client: TestClient, sample_user):
        response = client.post(
            "/auth/login",
            data={"username": sample_user.email, "password": "WrongPassword!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client: TestClient):
        response = client.post(
            "/auth/login",
            data={"username": "nonexistent@company.com", "password": "password123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 401

    def test_get_current_user(self, client: TestClient, sample_user, sample_role, sample_permission, auth_headers, db_session):
        from app.models.hse_models import SecurityUserRole, SecurityRolePermission
        db_session.add_all([
            SecurityUserRole(user_id=sample_user.user_id, role_id=sample_role.role_id, site_access="ALL"),
            SecurityRolePermission(role_id=sample_role.role_id, permission_id=sample_permission.permission_id),
        ])
        db_session.commit()

        response = client.get("/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["user_email"] == sample_user.email

    def test_get_menu(self, client: TestClient, sample_user, sample_role, sample_permission, auth_headers, db_session):
        from app.models.hse_models import SecurityUserRole, SecurityRolePermission
        db_session.add_all([
            SecurityUserRole(user_id=sample_user.user_id, role_id=sample_role.role_id, site_access="ALL"),
            SecurityRolePermission(role_id=sample_role.role_id, permission_id=sample_permission.permission_id),
        ])
        db_session.commit()

        response = client.get("/auth/menu", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "menu" in data
        assert "permissions" in data

    def test_get_permissions(self, client: TestClient, sample_user, sample_role, sample_permission, auth_headers, db_session):
        from app.models.hse_models import SecurityUserRole, SecurityRolePermission
        db_session.add_all([
            SecurityUserRole(user_id=sample_user.user_id, role_id=sample_role.role_id, site_access="ALL"),
            SecurityRolePermission(role_id=sample_role.role_id, permission_id=sample_permission.permission_id),
        ])
        db_session.commit()

        response = client.get("/auth/permissions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert any(p["permission_name"] == sample_permission.permission_name for p in data)


class TestDashboardEndpoints:
    """Test dashboard endpoints."""

    def test_get_executive_summary(self, client: TestClient, sample_site, sample_department, sample_fact_hse, auth_headers):
        response = client.get("/dashboard/summary?site_id=TEST-SITE-A", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "kpis" in data

    def test_get_incident_summary(self, client: TestClient, sample_site, sample_department, auth_headers):
        response = client.get("/dashboard/incidents?site_id=TEST-SITE-A", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "trend" in data

    def test_get_ptw_summary(self, client: TestClient, auth_headers):
        response = client.get("/dashboard/ptw", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "open_count" in data

    def test_get_training_summary(self, client: TestClient, auth_headers):
        response = client.get("/dashboard/training", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_completed" in data

    def test_get_environmental_summary(self, client: TestClient, auth_headers):
        response = client.get("/dashboard/environmental", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "pm25_current" in data

    def test_get_equipment_summary(self, client: TestClient, auth_headers):
        response = client.get("/dashboard/equipment", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_equipment" in data

    def test_health_check(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data


class TestAuditEndpoints:
    """Test audit endpoints."""

    def test_get_audit_plans(self, client: TestClient, sample_audit_plan, auth_headers):
        response = client.get("/audit/plans", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_audit_plan(self, client: TestClient, sample_site, auth_headers):
        response = client.post(
            "/audit/plans",
            json={
                "audit_type": "internal",
                "audit_status": "planned",
                "audit_title": "New Test Audit",
                "site_id": sample_site.site_id,
                "lead_auditor": "Test Auditor",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["audit_title"] == "New Test Audit"

    def test_get_audit_findings(self, client: TestClient, sample_audit_plan, auth_headers):
        response = client.get("/audit/findings", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_evidence_list(self, client: TestClient, auth_headers):
        response = client.get("/audit/evidence", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_upload_evidence(self, client: TestClient, auth_headers):
        response = client.post(
            "/audit/evidence/upload",
            params={
                "evidence_type": "document",
                "file_name": "test_evidence.pdf",
                "file_path": "/tmp/test_evidence.pdf",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["file_name"] == "test_evidence.pdf"

    def test_get_audit_trail(self, client: TestClient, auth_headers):
        response = client.get("/audit/trail", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestAlertEndpoints:
    """Test alert endpoints."""

    def test_get_alert_rules(self, client: TestClient, sample_alert_rule, auth_headers):
        response = client.get("/alerts/rules", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_active_alerts(self, client: TestClient, sample_site, auth_headers):
        response = client.get("/alerts/active", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_trigger_alert_evaluation(self, client: TestClient, auth_headers):
        response = client.post("/alerts/evaluate", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "triggered" in data


class TestReportEndpoints:
    """Test reporting endpoints."""

    def test_generate_executive_report(self, client: TestClient, auth_headers):
        response = client.post(
            "/reports/generate",
            json={
                "report_type": "executive",
                "start_date": "2026-01-01",
                "end_date": "2026-07-14",
                "format": "csv",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "Executive Summary"
        assert "file_name" in data

    def test_download_csv_report(self, client: TestClient, auth_headers):
        response = client.get(
            "/reports/download?report_type=executive&start_date=2026-01-01&end_date=2026-07-14&format=csv",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"

    def test_download_json_report(self, client: TestClient, auth_headers):
        response = client.get(
            "/reports/download?report_type=executive&start_date=2026-01-01&end_date=2026-07-14&format=json",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    def test_export_data_csv(self, client: TestClient, auth_headers):
        response = client.post(
            "/reports/export",
            json={
                "data_type": "equipment",
                "start_date": "2026-01-01",
                "end_date": "2026-07-14",
                "format": "csv",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"


class TestDataQualityEndpoints:
    """Test data quality endpoints."""

    def test_get_data_quality_report(self, client: TestClient, sample_fact_hse, auth_headers):
        response = client.get("/data/quality", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "checks" in data
        assert "database_status" in data

    def test_data_health_check(self, client: TestClient):
        response = client.get("/data/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
