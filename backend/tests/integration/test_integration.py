"""
Integration tests.
Full-stack tests covering critical user journeys.
"""

import pytest
from datetime import date, timedelta


class TestFullIncidentWorkflow:
    """Integration test: complete incident reporting workflow."""

    def test_incident_reporting_flow(self, client, sample_user, sample_site, sample_department, sample_role, sample_permission, db_session):
        from app.models.hse_models import SecurityUserRole, SecurityRolePermission
        from app.utils.security import hash_password

        user = sample_user
        db_session.add_all([
            SecurityUserRole(user_id=user.user_id, role_id=sample_role.role_id, site_access="ALL"),
            SecurityRolePermission(role_id=sample_role.role_id, permission_id=sample_permission.permission_id),
        ])
        db_session.commit()

        login_resp = client.post(
            "/auth/login",
            data={"username": user.email, "password": "TestPass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        incident_resp = client.get(
            "/dashboard/incidents",
            params={"site_id": sample_site.site_id, "period_days": 30},
            headers=headers,
        )
        assert incident_resp.status_code == 200

        audit_resp = client.get("/audit/plans", headers=headers)
        assert audit_resp.status_code == 200

        alert_resp = client.get("/alerts/active", headers=headers)
        assert alert_resp.status_code == 200

        report_resp = client.post(
            "/reports/generate",
            json={
                "report_type": "executive",
                "start_date": str(date.today() - timedelta(days=30)),
                "end_date": str(date.today()),
                "format": "csv",
            },
            headers=headers,
        )
        assert report_resp.status_code == 200


class TestRBACEnforcement:
    """Integration test: RBAC enforcement across endpoints."""

    def test_unauthorized_access_blocked(self, client):
        response = client.get("/dashboard/summary")
        assert response.status_code == 401

    def test_user_with_permission_can_access(self, client, sample_user, sample_role, sample_permission, db_session):
        from app.models.hse_models import SecurityUserRole, SecurityRolePermission

        user = sample_user
        db_session.add_all([
            SecurityUserRole(user_id=user.user_id, role_id=sample_role.role_id, site_access="ALL"),
            SecurityRolePermission(role_id=sample_role.role_id, permission_id=sample_permission.permission_id),
        ])
        db_session.commit()

        login_resp = client.post(
            "/auth/login",
            data={"username": user.email, "password": "TestPass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/dashboard/summary", headers=headers)
        assert response.status_code == 200
