#!/usr/bin/env python3
"""
Database initialization script.
Creates tables, indexes, sample data, and views.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.database import Base, engine
from app.config import settings
from app.models.hse_models import (
    DimSite, DimDepartment, DimEmployee, DimEquipment,
    DimIncident, DimPTW, DimEnvironmental, DimTraining,
    DimContractor, SecurityUserRole
)


def create_tables():
    """Create all tables from SQLAlchemy models."""
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")


def create_indexes():
    """Create additional indexes for performance."""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_fact_hse_date_site ON hse.fact_hse(date_key, site_key)",
        "CREATE INDEX IF NOT EXISTS idx_fact_hse_dept ON hse.fact_hse(dept_key)",
        "CREATE INDEX IF NOT EXISTS idx_dim_site_type ON hse.dim_site(site_type)",
        "CREATE INDEX IF NOT EXISTS idx_dim_equipment_site ON hse.dim_equipment(current_site_id)",
        "CREATE INDEX IF NOT EXISTS idx_dim_equipment_cert ON hse.dim_equipment(certification_expiry)",
    ]

    with engine.connect() as conn:
        for idx_sql in indexes:
            try:
                conn.execute(text(idx_sql))
                conn.commit()
                print(f"✓ Created index: {idx_sql[:50]}...")
            except Exception as e:
                print(f"✗ Index creation failed: {e}")


def seed_sample_data():
    """Insert sample data for testing."""
    sample_sites = [
        DimSite(site_id="SITE-A", site_name="Site Alpha Kutai", site_type="Mining",
                location_lat=-0.4240, location_long=116.9830, zone="North Pit",
                area_type="Open Pit", permit_no="IUP-2024-001", managing_director="Budi Santoso"),
        DimSite(site_id="SITE-B", site_name="Site Beta Balikpapan", site_type="Oil & Gas",
                location_lat=-1.2653, location_long=116.8312, zone="Processing Plant",
                permit_no="IUP-2024-002", managing_director="Siti Rahayu"),
    ]

    sample_departments = [
        DimDepartment(dept_id="DEPT-MIN", dept_name="Mining Operations", dept_type="Mining", site_id="SITE-A", head_of_dept="Joko Susilo"),
        DimDepartment(dept_id="DEPT-HSE", dept_name="HSE Operations", dept_type="HSE", site_id="SITE-A", head_of_dept="Maya Indira"),
    ]

    sample_users = [
        SecurityUserRole(
            user_email="admin@hse.local",
            user_name="System Admin",
            role_name="ICT",
            site_access="ALL",
            page_access="ALL",
            can_export=True,
            can_edit=True,
            can_configure_alerts=True,
        ),
        SecurityUserRole(
            user_email="manager@hse.local",
            user_name="HSE Manager",
            role_name="HSEManager",
            site_access="ALL",
            page_access="ALL",
            can_export=True,
            can_edit=True,
            can_configure_alerts=True,
        ),
    ]

    with engine.connect() as conn:
        try:
            for site in sample_sites:
                conn.merge(site)
            for dept in sample_departments:
                conn.merge(dept)
            for user in sample_users:
                conn.merge(user)
            conn.commit()
            print("✓ Sample data seeded")
        except Exception as e:
            print(f"✗ Sample data seeding failed: {e}")


def create_views():
    """Create database views."""
    views = [
        """
        CREATE OR REPLACE VIEW hse.v_daily_hse_summary AS
        SELECT
            f.date_key,
            f.site_key,
            s.site_name,
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
            CASE WHEN SUM(f.man_hours_worked) > 0
                THEN (SUM(f.lti_count) * 1000000.0) / SUM(f.man_hours_worked)
                ELSE NULL END AS ltifr,
            CASE WHEN SUM(f.man_hours_worked) > 0
                THEN ((SUM(f.lti_count) + SUM(f.mti_count) + SUM(f.fai_count)) * 200000.0) / SUM(f.man_hours_worked)
                ELSE NULL END AS trir
        FROM hse.fact_hse f
        JOIN hse.dim_site s ON f.site_key = s.site_id
        JOIN hse.dim_department d ON f.dept_key = d.dept_id
        GROUP BY f.date_key, f.site_key, s.site_name, f.dept_key, d.dept_name
        """,
        """
        CREATE OR REPLACE VIEW hse.v_ptw_current_status AS
        SELECT
            p.ptw_id, p.ptw_type, p.site_id, s.site_name,
            p.ptw_status, p.violation_count, p.start_at, p.end_at,
            CASE WHEN p.ptw_status = 'OPEN' AND p.end_at < CURRENT_TIMESTAMP
                THEN 'OVERDUE' ELSE p.ptw_status END AS computed_status
        FROM hse.dim_ptw p
        JOIN hse.dim_site s ON p.site_id = s.site_id
        WHERE p.is_cancelled = FALSE
        """,
        """
        CREATE OR REPLACE VIEW hse.v_equipment_compliance AS
        SELECT
            e.equipment_id, e.equipment_type, e.current_site_id, s.site_name,
            e.next_inspection, e.certification_expiry,
            CASE WHEN e.certification_expiry < CURRENT_DATE THEN 'EXPIRED'
                 WHEN e.next_inspection < CURRENT_DATE THEN 'OVERDUE'
                 ELSE 'VALID' END AS compliance_status
        FROM hse.dim_equipment e
        JOIN hse.dim_site s ON e.current_site_id = s.site_id
        WHERE e.active_to = '9999-12-31'
        """,
    ]

    with engine.connect() as conn:
        for view_sql in views:
            try:
                conn.execute(text(view_sql))
                conn.commit()
                print(f"✓ Created view: {view_sql[:60].strip()}...")
            except Exception as e:
                print(f"✗ View creation failed: {e}")


def main():
    """Run database initialization."""
    print("=" * 60)
    print("HSE Database Initialization")
    print("=" * 60)

    try:
        create_tables()
        create_indexes()
        seed_sample_data()
        create_views()

        print("=" * 60)
        print("✓ Database initialization complete")
        print("=" * 60)

    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
