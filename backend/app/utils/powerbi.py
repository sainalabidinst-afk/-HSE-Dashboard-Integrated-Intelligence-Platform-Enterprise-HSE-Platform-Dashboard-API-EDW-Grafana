"""
Power BI Enterprise Integration for HSE Platform
Provides data sources, datasets, and export functionality for Power BI
"""

from typing import Dict, List, Any, Optional
from datetime import date, datetime
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db


class PowerBIIntegration:
    """Power BI integration service."""

    def __init__(self, db: Session):
        self.db = db

    def get_dataset_summary(self, site_id: Optional[str] = None, period_days: int = 30) -> Dict[str, Any]:
        """Get summary dataset for Power BI."""
        end_date = date.today()
        start_date = end_date - pd.Timedelta(days=period_days)

        query = text("""
            SELECT
                f.date_key,
                s.site_name,
                s.site_type,
                d.dept_name,
                f.man_hours_worked,
                f.lti_count,
                f.mti_count,
                f.fai_count,
                f.near_miss_count,
                f.fatality_count,
                f.ptw_issued_count,
                f.ptw_violation_count,
                f.training_passed_count,
                f.audit_score,
                f.env_reading_value,
                f.env_exceeded
            FROM hse.fact_hse f
            JOIN hse.dim_site s ON f.site_key = s.site_id
            JOIN hse.dim_department d ON f.dept_key = d.dept_id
            WHERE f.date_key BETWEEN :start_date AND :end_date
            AND (:site_id = 'all' OR f.site_key = :site_id)
            ORDER BY f.date_key DESC
        """)

        result = self.db.execute(query, {"start_date": start_date, "end_date": end_date, "site_id": site_id or "all"})
        rows = result.fetchall()

        return {
            "columns": [col for col in result.keys()],
            "rows": [dict(row._mapping) for row in rows],
            "count": len(rows),
        }

    def get_incident_register(self, site_id: Optional[str] = None) -> Dict[str, Any]:
        """Get incident register for Power BI."""
        query = text("""
            SELECT
                i.incident_id,
                i.incident_type,
                i.incident_category,
                i.severity_class,
                i.body_part,
                i.agency_type,
                i.incident_cause,
                i.incident_location,
                i.ptw_required,
                i.ptw_used,
                i.ptw_approved,
                i.case_status,
                i.investigation_lead,
                i.investigation_due,
                i.root_cause,
                i.corrective_action,
                i.preventive_action,
                i.lost_days,
                i.restricted_days,
                s.site_name,
                d.dept_name,
                e.employee_id,
                e.full_name
            FROM hse.dim_incident i
            LEFT JOIN hse.fact_hse f ON i.incident_id = f.incident_key
            LEFT JOIN hse.dim_site s ON f.site_key = s.site_id
            LEFT JOIN hse.dim_department d ON f.dept_key = d.dept_id
            LEFT JOIN hse.dim_employee e ON f.emp_key = e.employee_id
            WHERE (:site_id = 'all' OR f.site_key = :site_id)
            ORDER BY i.incident_id DESC
        """)

        result = self.db.execute(query, {"site_id": site_id or "all"})
        rows = result.fetchall()

        return {
            "columns": [col for col in result.keys()],
            "rows": [dict(row._mapping) for row in rows],
            "count": len(rows),
        }

    def export_to_csv(self, dataset_name: str, site_id: Optional[str] = None) -> str:
        """Export dataset to CSV for Power BI import."""
        if dataset_name == "summary":
            data = self.get_dataset_summary(site_id)
        elif dataset_name == "incident_register":
            data = self.get_incident_register(site_id)
        else:
            raise ValueError(f"Unknown dataset: {dataset_name}")

        df = pd.DataFrame(data["rows"], columns=data["columns"])
        csv_path = f"/tmp/hse_{dataset_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(csv_path, index=False)
        return csv_path

    def get_powerbi_dataset_schema(self) -> Dict[str, Any]:
        """Get Power BI dataset schema for DirectQuery or Import."""
        return {
            "name": "HSE Enterprise Dataset",
            "version": "1.0",
            "tables": [
                {
                    "name": "Fact HSE",
                    "source": "SELECT * FROM hse.fact_hse",
                    "columns": [
                        {"name": "date_key", "type": "DateTime"},
                        {"name": "site_key", "type": "String"},
                        {"name": "dept_key", "type": "String"},
                        {"name": "man_hours_worked", "type": "Double"},
                        {"name": "lti_count", "type": "Int32"},
                        {"name": "mti_count", "type": "Int32"},
                        {"name": "fai_count", "type": "Int32"},
                        {"name": "near_miss_count", "type": "Int32"},
                        {"name": "fatality_count", "type": "Int32"},
                        {"name": "ptw_issued_count", "type": "Int32"},
                        {"name": "ptw_violation_count", "type": "Int32"},
                        {"name": "training_passed_count", "type": "Int32"},
                        {"name": "audit_score", "type": "Double"},
                        {"name": "env_reading_value", "type": "Double"},
                        {"name": "env_exceeded", "type": "Boolean"},
                    ],
                },
                {
                    "name": "Dim Site",
                    "source": "SELECT * FROM hse.dim_site",
                    "columns": [
                        {"name": "site_id", "type": "String"},
                        {"name": "site_name", "type": "String"},
                        {"name": "site_type", "type": "String"},
                        {"name": "zone", "type": "String"},
                        {"name": "area_type", "type": "String"},
                        {"name": "managing_director", "type": "String"},
                    ],
                },
                {
                    "name": "Dim Department",
                    "source": "SELECT * FROM hse.dim_department",
                    "columns": [
                        {"name": "dept_id", "type": "String"},
                        {"name": "dept_name", "type": "String"},
                        {"name": "dept_type", "type": "String"},
                        {"name": "head_of_dept", "type": "String"},
                    ],
                },
                {
                    "name": "Dim Incident",
                    "source": "SELECT * FROM hse.dim_incident",
                    "columns": [
                        {"name": "incident_id", "type": "String"},
                        {"name": "incident_type", "type": "String"},
                        {"name": "incident_category", "type": "String"},
                        {"name": "severity_class", "type": "String"},
                        {"name": "agency_type", "type": "String"},
                        {"name": "incident_cause", "type": "String"},
                        {"name": "case_status", "type": "String"},
                    ],
                },
                {
                    "name": "Audit Plans",
                    "source": "SELECT * FROM hse.audit_plans",
                    "columns": [
                        {"name": "audit_id", "type": "String"},
                        {"name": "audit_type", "type": "String"},
                        {"name": "audit_status", "type": "String"},
                        {"name": "audit_title", "type": "String"},
                        {"name": "site_id", "type": "String"},
                        {"name": "compliance_score", "type": "Double"},
                        {"name": "findings_count", "type": "Int32"},
                        {"name": "major_findings", "type": "Int32"},
                        {"name": "minor_findings", "type": "Int32"},
                    ],
                },
                {
                    "name": "Audit Findings",
                    "source": "SELECT * FROM hse.audit_findings",
                    "columns": [
                        {"name": "finding_id", "type": "String"},
                        {"name": "audit_id", "type": "String"},
                        {"name": "finding_type", "type": "String"},
                        {"name": "finding_status", "type": "String"},
                        {"name": "clause_ref", "type": "String"},
                        {"name": "description", "type": "String"},
                        {"name": "due_date", "type": "DateTime"},
                        {"name": "closed_date", "type": "DateTime"},
                    ],
                },
                {
                    "name": "Alerts",
                    "source": "SELECT * FROM hse.alerts",
                    "columns": [
                        {"name": "alert_id", "type": "String"},
                        {"name": "alert_type", "type": "String"},
                        {"name": "severity", "type": "String"},
                        {"name": "status", "type": "String"},
                        {"name": "site_id", "type": "String"},
                        {"name": "message", "type": "String"},
                        {"name": "alert_date", "type": "DateTime"},
                    ],
                },
            ],
            "relationships": [
                {
                    "from_table": "Fact HSE",
                    "from_column": "site_key",
                    "to_table": "Dim Site",
                    "to_column": "site_id",
                    "cross_filter": "single",
                },
                {
                    "from_table": "Fact HSE",
                    "from_column": "dept_key",
                    "to_table": "Dim Department",
                    "to_column": "dept_id",
                    "cross_filter": "single",
                },
                {
                    "from_table": "Audit Findings",
                    "from_column": "audit_id",
                    "to_table": "Audit Plans",
                    "to_column": "audit_id",
                    "cross_filter": "single",
                },
            ],
        }
