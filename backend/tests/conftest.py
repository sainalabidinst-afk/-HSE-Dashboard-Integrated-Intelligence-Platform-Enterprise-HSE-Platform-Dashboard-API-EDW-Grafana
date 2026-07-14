"""
Pytest configuration and shared fixtures.
"""

import os
import sys
import pytest
from datetime import date, datetime, timedelta
from typing import Generator, Dict, Any

# Ensure backend/ is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set testing flag BEFORE any app imports
os.environ["TESTING"] = "true"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.hse_models import (
    SecurityUser, SecurityRole, SecurityPermission,
    SecurityRolePermission, SecurityUserRole,
    FactHSE, DimSite, DimDepartment
)
from app.models.audit import AuditPlan, AuditFinding
from app.models.alert import AlertRule, Alert

# Patch schema and JSONB for SQLite compatibility during tests
from sqlalchemy import JSON, Column
from sqlalchemy.dialects.postgresql import JSONB

for table in Base.metadata.tables.values():
    table.schema = None
    for column in table.columns:
        if isinstance(column.type, JSONB):
            column.type = JSON()

# Patch VectorType for SQLite compatibility
from app.models.ai import VectorType
for table in Base.metadata.tables.values():
    for column in table.columns:
        if isinstance(column.type, VectorType):
            column.type = JSON()

# Use SQLite in-memory for fast tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine (session-scoped)."""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """Create a test client with overridden database dependency."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_site(db_session: Session) -> DimSite:
    """Create a sample site for testing."""
    site = DimSite(
        site_id="TEST-SITE-A",
        site_name="Test Site Alpha",
        site_type="Mining",
        location_lat=-6.2088,
        location_long=106.8456,
        zone="Test Zone",
        area_type="Open Pit",
        site_status="Active",
        managing_director="Test Director",
        timezone="Asia/Jakarta",
    )
    db_session.add(site)
    db_session.commit()
    db_session.refresh(site)
    return site


@pytest.fixture
def sample_department(db_session: Session, sample_site: DimSite) -> DimDepartment:
    """Create a sample department for testing."""
    dept = DimDepartment(
        dept_id="TEST-DEPT-01",
        dept_name="Test Department",
        dept_type="Operations",
        site_id=sample_site.site_id,
        head_of_dept="Test Head",
        budget_code="TEST-001",
    )
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)
    return dept


@pytest.fixture
def sample_user(db_session: Session) -> SecurityUser:
    """Create a sample user for testing."""
    from app.utils.security import hash_password
    user = SecurityUser(
        email="test.user@company.com",
        username="testuser",
        full_name="Test User",
        password_hash=hash_password("TestPass123!"),
        is_active=True,
        is_locked=False,
        failed_login_attempts=0,
        last_login_ip="127.0.0.1",
        last_login_user_agent="test-client",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_role(db_session: Session) -> SecurityRole:
    """Create a sample role for testing."""
    role = SecurityRole(
        role_name="test_role",
        role_display_name="Test Role",
        role_description="Role for testing",
        is_system_role=False,
        is_active=True,
    )
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


@pytest.fixture
def sample_permission(db_session: Session) -> SecurityPermission:
    """Create a sample permission for testing."""
    perm = SecurityPermission(
        permission_name="test:view",
        permission_display_name="View Test",
        module="test",
        action="view",
        description="Test permission",
    )
    db_session.add(perm)
    db_session.commit()
    db_session.refresh(perm)
    return perm


@pytest.fixture
def sample_user_role(db_session: Session, sample_user: SecurityUser, sample_role: SecurityRole) -> SecurityUserRole:
    """Create a sample user-role assignment."""
    ur = SecurityUserRole(
        user_id=sample_user.user_id,
        role_id=sample_role.role_id,
        site_access="ALL",
        department_access="",
        contractor_access="",
        is_active=True,
    )
    db_session.add(ur)
    db_session.commit()
    db_session.refresh(ur)
    return ur


@pytest.fixture
def auth_headers(sample_user: SecurityUser, db_session: Session) -> Dict[str, str]:
    """Generate Authorization headers for a sample user."""
    from app.utils.security import create_access_token
    from app.repositories import AuthRepository

    repo = AuthRepository(db_session)
    session = repo.create_session(
        session_id="test-session-001",
        user_id=sample_user.user_id,
        ip_address="127.0.0.1",
        user_agent="test-client",
    )

    token = create_access_token(data={
        "sub": str(sample_user.user_id),
        "email": sample_user.email,
        "role": "admin",
        "roles": ["admin"],
        "permissions": ["*:*"],
        "site_access": ["ALL"],
        "user_id": sample_user.user_id,
        "session_id": session.session_id,
    })
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_fact_hse(db_session: Session, sample_site: DimSite, sample_department: DimDepartment) -> FactHSE:
    """Create a sample fact HSE record."""
    record = FactHSE(
        date_key=date.today(),
        site_key=sample_site.site_id,
        dept_key=sample_department.dept_id,
        man_hours_worked=1000.0,
        headcount_present=50,
        lti_count=0,
        mti_count=0,
        fai_count=1,
        near_miss_count=2,
        fatality_count=0,
        ptw_issued_count=3,
        ptw_closed_count=1,
        ptw_open_count=2,
        ptw_violation_count=0,
        training_passed_count=10,
        training_failed_count=0,
        training_pending_count=5,
        audit_score=95.5,
        env_reading_value=25.0,
        env_limit_value=50.0,
        env_exceeded=False,
    )
    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)
    return record


@pytest.fixture
def sample_audit_plan(db_session: Session, sample_site: DimSite) -> AuditPlan:
    """Create a sample audit plan."""
    plan = AuditPlan(
        audit_id="AUDIT-TEST-001",
        audit_type="internal",
        audit_status="planned",
        audit_title="Test Audit Plan",
        standard_ref="ISO 45001",
        site_id=sample_site.site_id,
        lead_auditor="Test Auditor",
        scope="Test scope",
        criteria="Test criteria",
        scheduled_start=date.today(),
        scheduled_end=date.today() + timedelta(days=7),
        findings_count=0,
        major_findings=0,
        minor_findings=0,
        observations=0,
    )
    db_session.add(plan)
    db_session.commit()
    db_session.refresh(plan)
    return plan


@pytest.fixture
def sample_alert_rule(db_session: Session, sample_site: DimSite) -> AlertRule:
    """Create a sample alert rule."""
    from app.models.alert import MetricType, AlertSeverity
    rule = AlertRule(
        rule_id="RULE-TEST-001",
        rule_name="Test Alert Rule",
        metric_type=MetricType.LTIFR,
        condition=">",
        threshold_value=2.0,
        severity=AlertSeverity.WARNING,
        site_id=sample_site.site_id,
        notification_channels=["dashboard"],
        recipients=[],
        is_active=True,
        cooldown_minutes=60,
    )
    db_session.add(rule)
    db_session.commit()
    db_session.refresh(rule)
    return rule
