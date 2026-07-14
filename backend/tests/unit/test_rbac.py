"""
Unit tests for RBAC utilities.
Tests permission checking, site access, and user authentication logic.
"""

import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException

from app.models.hse_models import SecurityUser
from app.utils.security import hash_password

from app.utils.rbac import (
    authenticate_user,
    logout_user,
    logout_all_sessions,
    get_user_permissions,
    get_user_site_access,
    has_permission,
    can_access_site,
    get_current_user,
    require_permission,
)


class TestHasPermission:
    """Test permission checking logic."""

    def test_has_permission_exact_match(self):
        perms = ["incident:view", "incident:create", "ptw:view"]
        assert has_permission(perms, "incident:view") is True

    def test_has_permission_not_found(self):
        perms = ["incident:view", "ptw:view"]
        assert has_permission(perms, "user:delete") is False

    def test_has_permission_empty_list(self):
        assert has_permission([], "incident:view") is False

    def test_has_permission_wildcard(self):
        perms = ["*"]
        assert has_permission(perms, "anything:any") is True

    def test_has_permission_super_admin(self):
        perms = ["admin:*"]
        assert has_permission(perms, "system:config") is True


class TestCanAccessSite:
    """Test site access checking."""

    def test_can_access_site_all(self):
        access = ["ALL"]
        assert can_access_site(access, "SITE-A") is True
        assert can_access_site(access, "SITE-B") is True

    def test_can_access_site_specific(self):
        access = ["SITE-A", "SITE-B"]
        assert can_access_site(access, "SITE-A") is True
        assert can_access_site(access, "SITE-C") is False

    def test_can_access_site_empty(self):
        access = []
        assert can_access_site(access, "SITE-A") is False


class TestAuthenticateUser:
    """Test user authentication logic."""

    def test_authenticate_valid_credentials(self, db_session):
        from app.models.hse_models import SecurityUser, SecurityRole, SecurityUserRole, SecurityPermission, SecurityRolePermission
        from app.utils.security import hash_password

        user = SecurityUser(
            email="auth.test@company.com",
            username="authtest",
            full_name="Auth Test User",
            password_hash=hash_password("AuthPass123!"),
            is_active=True,
            is_locked=False,
        )
        role = SecurityRole(role_name="test_auth_role", role_display_name="Test Auth Role", is_system_role=False, is_active=True)
        db_session.add_all([user, role])
        db_session.commit()
        db_session.refresh(user)
        db_session.refresh(role)

        perm = SecurityPermission(permission_name="dashboard:view", permission_display_name="View Dashboard", module="dashboard", action="view")
        db_session.add(perm)
        db_session.commit()
        db_session.refresh(perm)

        srp = SecurityRolePermission(role_id=role.role_id, permission_id=perm.permission_id)
        sur = SecurityUserRole(user_id=user.user_id, role_id=role.role_id, site_access="ALL")
        db_session.add_all([srp, sur])
        db_session.commit()

        result = authenticate_user(db_session, "auth.test@company.com", "AuthPass123!", "127.0.0.1", "test-agent")
        assert result is not None
        assert result["email"] == "auth.test@company.com"
        assert "access_token" in result

    def test_authenticate_wrong_password(self, db_session):
        from app.utils.security import hash_password
        from fastapi import HTTPException

        user = SecurityUser(
            email="wrongpass@company.com",
            username="wrongpass",
            full_name="Wrong Pass User",
            password_hash=hash_password("CorrectPass123!"),
            is_active=True,
            is_locked=False,
        )
        db_session.add(user)
        db_session.commit()

        with pytest.raises(HTTPException) as exc_info:
            authenticate_user(db_session, "wrongpass@company.com", "WrongPass123!", "127.0.0.1", "test-agent")
        assert exc_info.value.status_code == 401

    def test_authenticate_locked_account(self, db_session):
        from app.utils.security import hash_password
        from datetime import datetime, timedelta
        from fastapi import HTTPException

        user = SecurityUser(
            email="locked@company.com",
            username="lockeduser",
            full_name="Locked User",
            password_hash=hash_password("LockedPass123!"),
            is_active=True,
            is_locked=True,
            locked_until=datetime.utcnow() + timedelta(minutes=15),
        )
        db_session.add(user)
        db_session.commit()

        with pytest.raises(HTTPException) as exc_info:
            authenticate_user(db_session, "locked@company.com", "LockedPass123!", "127.0.0.1", "test-agent")
        assert exc_info.value.status_code == 403

    def test_authenticate_inactive_user(self, db_session):
        from app.utils.security import hash_password
        from fastapi import HTTPException

        user = SecurityUser(
            email="inactive@company.com",
            username="inactiveuser",
            full_name="Inactive User",
            password_hash=hash_password("InactivePass123!"),
            is_active=False,
            is_locked=False,
        )
        db_session.add(user)
        db_session.commit()

        with pytest.raises(HTTPException) as exc_info:
            authenticate_user(db_session, "inactive@company.com", "InactivePass123!", "127.0.0.1", "test-agent")
        assert exc_info.value.status_code == 403


class TestGetUserPermissions:
    """Test permission retrieval for users."""

    def test_get_user_permissions_multiple_roles(self, db_session):
        from app.models.hse_models import SecurityUser, SecurityRole, SecurityUserRole, SecurityPermission, SecurityRolePermission

        user = SecurityUser(email="multirole@company.com", username="multirole", full_name="Multi Role User", password_hash=hash_password("MultiPass123!"), is_active=True)
        role1 = SecurityRole(role_name="multi_role_1", role_display_name="Multi Role 1", is_system_role=False)
        role2 = SecurityRole(role_name="multi_role_2", role_display_name="Multi Role 2", is_system_role=False)
        db_session.add_all([user, role1, role2])
        db_session.commit()
        db_session.refresh(user)
        db_session.refresh(role1)
        db_session.refresh(role2)

        perm1 = SecurityPermission(permission_name="incident:view", permission_display_name="View Incident", module="incident", action="view")
        perm2 = SecurityPermission(permission_name="ptw:create", permission_display_name="Create PTW", module="ptw", action="create")
        db_session.add_all([perm1, perm2])
        db_session.commit()
        db_session.refresh(perm1)
        db_session.refresh(perm2)

        db_session.add_all([
            SecurityUserRole(user_id=user.user_id, role_id=role1.role_id, site_access="ALL"),
            SecurityUserRole(user_id=user.user_id, role_id=role2.role_id, site_access="ALL"),
            SecurityRolePermission(role_id=role1.role_id, permission_id=perm1.permission_id),
            SecurityRolePermission(role_id=role2.role_id, permission_id=perm2.permission_id),
        ])
        db_session.commit()

        perms = get_user_permissions(db_session, user.user_id)
        assert "incident:view" in perms
        assert "ptw:create" in perms
        assert len(perms) == 2

    def test_get_user_permissions_no_roles(self, db_session):
        from app.models.hse_models import SecurityUser
        user = SecurityUser(email="norole@company.com", username="norole", full_name="No Role User", password_hash=hash_password("NoRolePass123!"), is_active=True)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        perms = get_user_permissions(db_session, user.user_id)
        assert perms == []


class TestGetUserSiteAccess:
    """Test site access retrieval."""

    def test_get_user_site_access_all(self, db_session):
        from app.models.hse_models import SecurityUser, SecurityRole, SecurityUserRole
        user = SecurityUser(email="allsite@company.com", username="allsite", full_name="All Site User", password_hash=hash_password("AllSitePass123!"), is_active=True)
        role = SecurityRole(role_name="allsite_role", role_display_name="All Site Role", is_system_role=False)
        db_session.add_all([user, role])
        db_session.commit()
        db_session.refresh(user)
        db_session.refresh(role)
        sur = SecurityUserRole(user_id=user.user_id, role_id=role.role_id, site_access="ALL")
        db_session.add(sur)
        db_session.commit()
        access = get_user_site_access(db_session, user.user_id)
        assert access == ["ALL"]

    def test_get_user_site_access_specific(self, db_session):
        from app.models.hse_models import SecurityUser, SecurityRole, SecurityUserRole
        user = SecurityUser(email="specsite@company.com", username="specsite", full_name="Specific Site User", password_hash=hash_password("SpecSitePass123!"), is_active=True)
        role = SecurityRole(role_name="specsite_role", role_display_name="Specific Site Role", is_system_role=False)
        db_session.add_all([user, role])
        db_session.commit()
        db_session.refresh(user)
        db_session.refresh(role)
        sur = SecurityUserRole(user_id=user.user_id, role_id=role.role_id, site_access="SITE-A,SITE-B")
        db_session.add(sur)
        db_session.commit()
        access = get_user_site_access(db_session, user.user_id)
        assert "SITE-A" in access
        assert "SITE-B" in access
