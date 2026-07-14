"""
Business logic layer for HSE platform.
Services orchestrate repositories and business rules.
"""

from datetime import date, datetime, timedelta
from typing import Optional, Dict, List, Any

from app.repositories import DashboardRepository, AuthRepository, AlertRepository, AuditRepository, EvidenceRepository
from app.models.audit import AuditPlan, AuditFinding, Evidence, AuditTrail, CorrectiveAction
from app.models.alert import AlertRule, Alert, NotificationLog
from app.config import settings
from app.services.ai import AIService
from app.schemas import (
    ExecutiveSummary, IncidentSummary, PTWSummary, TrainingSummary,
    EnvironmentalSummary, EquipmentSummary, ContractorSummary,
    AlertItem, KPICard
)


class DashboardService:
    """Service for dashboard business logic."""

    def __init__(self, db):
        self.repo = DashboardRepository(db)

    def get_executive_summary(
        self,
        site_id: Optional[str] = None,
        period_days: int = 30
    ) -> ExecutiveSummary:
        """Build executive summary with KPI cards."""
        data = self.repo.get_executive_summary(
            site_id=site_id,
            period_days=period_days
        )

        kpis = [
            KPICard(
                label="LTIFR",
                value=data["ltifr"],
                unit="",
                status=self._rag_status(data["ltifr"], 1.0, 2.0, lower_is_better=True),
                subtext="Target: < 1.0"
            ),
            KPICard(
                label="TRIR",
                value=data["trir"],
                unit="",
                status=self._rag_status(data["trir"], 2.0, 3.5, lower_is_better=True),
                subtext="Target: < 2.0"
            ),
            KPICard(
                label="Severity Rate",
                value=data["severity_rate"],
                unit="",
                status=self._rag_status(data["severity_rate"], 15, 25, lower_is_better=True),
                subtext="Target: < 15"
            ),
            KPICard(
                label="Near Miss Rate",
                value=data["near_miss_rate"],
                unit="/1k",
                status=self._rag_status(data["near_miss_rate"], 15, 10, lower_is_better=False),
                subtext="Target: > 15"
            ),
            KPICard(
                label="Fatality YTD",
                value=data["total_fatality"],
                unit="",
                status="green" if data["total_fatality"] == 0 else "red",
                subtext="Target: 0"
            ),
            KPICard(
                label="Audit Score",
                value=f"{data['avg_audit_score']}%",
                unit="",
                status=self._rag_status(data["avg_audit_score"], 95, 85, lower_is_better=False),
                subtext="Target: > 95%"
            ),
            KPICard(
                label="PTW Violations",
                value=data["total_ptw_violations"],
                unit="",
                status="green" if data["total_ptw_violations"] == 0 else "red",
                subtext="Periode"
            ),
            KPICard(
                label="Env Exceedances",
                value=data["env_exceedances"],
                unit="",
                status="green" if data["env_exceedances"] == 0 else "red",
                subtext="Batas terlampaui"
            ),
        ]

        return ExecutiveSummary(
            kpis=kpis,
            generated_at=datetime.utcnow(),
            period_days=period_days,
            site_id=site_id,
        )

    def get_incident_summary(
        self,
        site_id: Optional[str] = None,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Get incident analysis data."""
        from datetime import date, timedelta
        end_date = date.today()
        start_date = end_date - timedelta(days=period_days)
        trend = self.repo.get_incident_trend(site_id=site_id, start_date=start_date, end_date=end_date)
        distribution = self.repo.get_incident_distribution(site_id=site_id, period_days=period_days)
        by_dept = self.repo.get_incident_by_department(site_id=site_id, period_days=period_days)

        return {
            "trend": trend,
            "distribution": distribution,
            "by_department": by_dept,
        }

    def get_ptw_summary(
        self,
        site_id: Optional[str] = None,
        period_days: int = 30
    ) -> PTWSummary:
        """Get PTW summary."""
        data = self.repo.get_ptw_summary(site_id=site_id, period_days=period_days)
        return PTWSummary(**data)

    def get_training_summary(
        self,
        site_id: Optional[str] = None,
        period_days: int = 30
    ) -> TrainingSummary:
        """Get training compliance summary."""
        data = self.repo.get_training_summary(site_id=site_id, period_days=period_days)
        return TrainingSummary(**data)

    def get_environmental_summary(
        self,
        site_id: Optional[str] = None,
        period_days: int = 30
    ) -> EnvironmentalSummary:
        """Get environmental monitoring summary."""
        data = self.repo.get_environmental_summary(site_id=site_id, period_days=period_days)
        return EnvironmentalSummary(**data)

    def get_equipment_summary(
        self,
        site_id: Optional[str] = None
    ) -> EquipmentSummary:
        """Get equipment compliance summary."""
        data = self.repo.get_equipment_summary(site_id=site_id)
        return EquipmentSummary(**data)

    def get_contractor_summary(self) -> ContractorSummary:
        """Get contractor performance summary."""
        data = self.repo.get_contractor_summary()
        return ContractorSummary(**data)

    def get_alerts(self, site_id: Optional[str] = None) -> List[AlertItem]:
        """Get active alerts."""
        alerts_data = self.repo.get_active_alerts(site_id=site_id)
        return [AlertItem(**a) for a in alerts_data]

    @staticmethod
    def _rag_status(value: float, green_threshold: float, amber_threshold: float, lower_is_better: bool = True) -> str:
        """
        Red/Amber/Green status logic.
        If lower_is_better: green < value < amber (inverted), red > amber
        If higher_is_better: green > value > amber (inverted), red < amber
        """
        if lower_is_better:
            if value <= green_threshold:
                return "green"
            elif value <= amber_threshold:
                return "amber"
            else:
                return "red"
        else:
            if value >= green_threshold:
                return "green"
            elif value >= amber_threshold:
                return "amber"
            else:
                return "red"


class AuthService:
    """Service for authentication and RBAC."""

    def __init__(self, db):
        self.repo = AuthRepository(db)

    def authenticate(self, email: str, password: str, ip_address: str = None, user_agent: str = None) -> Optional[Dict[str, Any]]:
        """
        Authenticate user using RBAC system.
        Returns user data with tokens if valid, None otherwise.
        """
        from app.utils.rbac import authenticate_user
        return authenticate_user(self.repo.db, email, password, ip_address, user_agent)

    def logout(self, user_id: int, session_id: str = None) -> bool:
        """Logout user by invalidating session."""
        from app.utils.rbac import logout_user
        return logout_user(self.repo.db, user_id, session_id)

    def logout_all(self, user_id: int) -> int:
        """Logout all sessions for a user."""
        from app.utils.rbac import logout_all_sessions
        return logout_all_sessions(self.repo.db, user_id)

    def get_user_permissions(self, user_id: int) -> List[str]:
        """Get all permissions for a user."""
        return self.repo.get_user_permissions(user_id)

    def get_user_site_access(self, user_id: int) -> List[str]:
        """Get site access for a user."""
        return self.repo.get_user_site_access(user_id)

    def has_permission(self, user_permissions: List[str], required_permission: str) -> bool:
        """Check if user has required permission."""
        from app.utils.rbac import has_permission
        return has_permission(user_permissions, required_permission)

    def can_access_site(self, user_site_access: List[str], requested_site: str) -> bool:
        """Check if user can access requested site."""
        from app.utils.rbac import can_access_site
        return can_access_site(user_site_access, requested_site)


class AuditService:
    """Service for audit management and evidence handling."""

    def __init__(self, db):
        self.audit_repo = AuditRepository(db)
        self.evidence_repo = EvidenceRepository(db)

    def get_audit_plans(self, site_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict]:
        return self.audit_repo.get_audit_plans(site_id=site_id, status=status)

    def get_audit_plan(self, audit_id: str) -> Optional[Dict]:
        plans = self.audit_repo.get_audit_plans()
        for p in plans:
            if p.get("audit_id") == audit_id:
                return p
        return None

    def create_audit_plan(self, data: Dict) -> Dict:
        import uuid
        plan = AuditPlan(
            audit_id=data.get("audit_id") or str(uuid.uuid4()),
            audit_type=data.get("audit_type"),
            audit_title=data.get("audit_title"),
            standard_ref=data.get("standard_ref"),
            site_id=data.get("site_id"),
            department_id=data.get("department_id"),
            lead_auditor=data.get("lead_auditor"),
            audit_team=data.get("audit_team"),
            scope=data.get("scope"),
            criteria=data.get("criteria"),
            scheduled_start=data.get("scheduled_start"),
            scheduled_end=data.get("scheduled_end"),
            created_by=data.get("created_by"),
        )
        self.audit_repo.db.add(plan)
        self.audit_repo.db.commit()
        self.audit_repo.db.refresh(plan)
        return {c.name: getattr(plan, c.name) for c in plan.__table__.columns}

    def update_audit_plan(self, audit_id: str, data: Dict) -> Optional[Dict]:
        plan = self.audit_repo.db.query(AuditPlan).filter(AuditPlan.audit_id == audit_id).first()
        if not plan:
            return None
        for key, value in data.items():
            if value is not None and hasattr(plan, key):
                setattr(plan, key, value)
        self.audit_repo.db.commit()
        self.audit_repo.db.refresh(plan)
        return {c.name: getattr(plan, c.name) for c in plan.__table__.columns}

    def get_findings(self, audit_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict]:
        return self.audit_repo.get_findings(audit_id=audit_id, status=status)

    def create_finding(self, data: Dict) -> Dict:
        import uuid
        finding = AuditFinding(
            finding_id=str(uuid.uuid4()),
            audit_id=data.get("audit_id"),
            finding_type=data.get("finding_type"),
            clause_ref=data.get("clause_ref"),
            description=data.get("description"),
            objective_evidence=data.get("objective_evidence"),
            root_cause=data.get("root_cause"),
            corrective_action=data.get("corrective_action"),
            preventive_action=data.get("preventive_action"),
            pic=data.get("pic"),
            due_date=data.get("due_date"),
            severity_score=data.get("severity_score"),
            created_by=data.get("created_by"),
        )
        self.audit_repo.db.add(finding)
        self.audit_repo.db.commit()
        self.audit_repo.db.refresh(finding)
        return {c.name: getattr(finding, c.name) for c in finding.__table__.columns}

    def update_finding(self, finding_id: str, data: Dict) -> Optional[Dict]:
        finding = self.audit_repo.db.query(AuditFinding).filter(AuditFinding.finding_id == finding_id).first()
        if not finding:
            return None
        for key, value in data.items():
            if value is not None and hasattr(finding, key):
                setattr(finding, key, value)
        self.audit_repo.db.commit()
        self.audit_repo.db.refresh(finding)
        return {c.name: getattr(finding, c.name) for c in finding.__table__.columns}

    def get_evidence(self, finding_id: Optional[str] = None, evidence_type: Optional[str] = None) -> List[Dict]:
        return self.audit_repo.get_evidence(finding_id=finding_id, evidence_type=evidence_type)

    def get_evidence_by_ref(self, ref_type: str, ref_id: str) -> List[Evidence]:
        return self.evidence_repo.get_evidence_by_ref(ref_type, ref_id)

    def upload_evidence(self, data: Dict) -> Evidence:
        return self.evidence_repo.upload_evidence(**data)

    def create_audit_trail(self, **kwargs) -> AuditTrail:
        return self.audit_repo.create_audit_trail(**kwargs)

    def get_audit_trail(self, user_id: Optional[int] = None, table_name: Optional[str] = None, limit: int = 100) -> List[AuditTrail]:
        return self.audit_repo.get_audit_trail(user_id=user_id, table_name=table_name, limit=limit)

    def create_corrective_action(self, data: Dict) -> Dict:
        import uuid
        car = CorrectiveAction(
            car_id=str(uuid.uuid4()),
            finding_id=data.get("finding_id"),
            car_type=data.get("car_type", "corrective"),
            description=data.get("description"),
            root_cause=data.get("root_cause"),
            proposed_action=data.get("proposed_action"),
            pic=data.get("pic"),
            due_date=data.get("due_date"),
            created_by=data.get("created_by"),
        )
        self.audit_repo.db.add(car)
        self.audit_repo.db.commit()
        self.audit_repo.db.refresh(car)
        return {c.name: getattr(car, c.name) for c in car.__table__.columns}

    def update_corrective_action(self, car_id: str, data: Dict) -> Optional[Dict]:
        car = self.audit_repo.db.query(CorrectiveAction).filter(CorrectiveAction.car_id == car_id).first()
        if not car:
            return None
        for key, value in data.items():
            if value is not None and hasattr(car, key):
                setattr(car, key, value)
        self.audit_repo.db.commit()
        self.audit_repo.db.refresh(car)
        return {c.name: getattr(car, c.name) for c in car.__table__.columns}


class AlertService:
    """Service for alert rules, alert management, and notifications."""

    def __init__(self, db):
        self.repo = AlertRepository(db)

    def get_alert_rules(self, site_id: Optional[str] = None, is_active: Optional[bool] = None) -> List[Dict]:
        return self.repo.get_alert_rules(site_id=site_id, is_active=is_active)

    def get_alert_rule(self, rule_id: str) -> Optional[AlertRule]:
        return self.repo.get_alert_rule(rule_id)

    def create_alert_rule(self, data: Dict, created_by: str) -> AlertRule:
        return self.repo.create_alert_rule({**data, "created_by": created_by})

    def update_alert_rule(self, rule_id: str, data: Dict) -> Optional[AlertRule]:
        return self.repo.update_alert_rule(rule_id, data)

    def get_alerts(self, site_id: Optional[str] = None, status: Optional[str] = None, severity: Optional[str] = None, limit: int = 100) -> List[Dict]:
        return self.repo.get_alerts(site_id=site_id, status=status, severity=severity, limit=limit)

    def acknowledge_alert(self, alert_id: str, user_email: str) -> Optional[Alert]:
        return self.repo.acknowledge_alert(alert_id, user_email)

    def resolve_alert(self, alert_id: str, user_email: str, notes: str = None) -> Optional[Alert]:
        return self.repo.resolve_alert(alert_id, user_email, notes)

    def evaluate_alert_rules(self) -> List[Dict]:
        """Evaluate all active rules and create alerts if triggered."""
        triggered = self.repo.evaluate_rules()
        created_alerts = []
        for alert_data in triggered:
            alert = self.repo.create_alert(alert_data)
            created_alerts.append(alert)
            self._send_notifications(alert)
        return created_alerts

    def _send_notifications(self, alert: Alert) -> None:
        from app.config import settings
        rule = self.repo.get_alert_rule(alert.rule_id) if alert.rule_id else None
        channels = rule.notification_channels if rule else ["dashboard"]
        for channel in channels:
            ch = channel.value if hasattr(channel, 'value') else str(channel)
            self.repo.log_notification({
                "alert_id": alert.alert_id,
                "channel": ch,
                "status": "sent",
                "sent_at": datetime.utcnow(),
            })


class ReportingService:
    """Service for report generation and data export."""

    def __init__(self, db):
        self.repo = DashboardRepository(db)
        self.db = db

    def generate_report(self, data: Dict) -> Dict:
        report_type = data.get("report_type", "executive")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        site_id = data.get("site_id", "all")
        fmt = data.get("format", "csv")
        result = self._build_report_data(report_type, start_date, end_date, site_id)
        result["format"] = fmt
        result["file_name"] = f"{report_type}_report_{start_date}_{end_date}.{fmt}"
        return result

    def _build_report_data(self, report_type: str, start_date: date, end_date: date, site_id: str) -> Dict:
        if report_type == "executive":
            return self._executive_report(start_date, end_date, site_id)
        elif report_type == "incident":
            return self._incident_report(start_date, end_date, site_id)
        elif report_type == "ptw":
            return self._ptw_report(start_date, end_date, site_id)
        elif report_type == "training":
            return self._training_report(start_date, end_date, site_id)
        elif report_type == "environmental":
            return self._environmental_report(start_date, end_date, site_id)
        elif report_type == "equipment":
            return self._equipment_report(site_id)
        elif report_type == "contractor":
            return self._contractor_report()
        elif report_type == "audit":
            return self._audit_report(site_id)
        else:
            return {"error": f"Unknown report type: {report_type}"}

    def _executive_report(self, start_date: date, end_date: date, site_id: str) -> Dict:
        data = self.repo.get_executive_summary(site_id=site_id, start_date=start_date, end_date=end_date)
        return {
            "report_type": "Executive Summary",
            "period": f"{start_date} to {end_date}",
            "site_id": site_id,
            "generated_at": datetime.utcnow().isoformat(),
            "data": data,
            "headers": ["Metric", "Value", "Unit", "Status"],
            "rows": [
                ["LTIFR", data.get("ltifr", 0), "", "Target < 1.0"],
                ["TRIR", data.get("trir", 0), "", "Target < 2.0"],
                ["Severity Rate", data.get("severity_rate", 0), "", "Target < 15"],
                ["Near Miss Rate", data.get("near_miss_rate", 0), "/1k", "Target > 15"],
                ["Fatality YTD", data.get("total_fatality", 0), "", "Target: 0"],
                ["Audit Score", f"{data.get('avg_audit_score', 0)}%", "", "Target > 95%"],
                ["PTW Violations", data.get("total_ptw_violations", 0), "", ""],
                ["Env Exceedances", data.get("env_exceedances", 0), "", ""],
                ["Man Hours", data.get("total_man_hours", 0), "hours", ""],
            ],
        }

    def _incident_report(self, start_date: date, end_date: date, site_id: str) -> Dict:
        summary = self.repo.get_incident_summary(site_id=site_id, start_date=start_date, end_date=end_date)
        return {
            "report_type": "Incident Summary",
            "period": f"{start_date} to {end_date}",
            "site_id": site_id,
            "generated_at": datetime.utcnow().isoformat(),
            "data": summary,
            "headers": ["Department", "Total Incidents"],
            "rows": [[k, v] for k, v in summary.get("by_department", {}).items()],
        }

    def _ptw_report(self, start_date: date, end_date: date, site_id: str) -> Dict:
        data = self.repo.get_ptw_summary(site_id=site_id, start_date=start_date, end_date=end_date)
        return {
            "report_type": "PTW Summary",
            "period": f"{start_date} to {end_date}",
            "site_id": site_id,
            "generated_at": datetime.utcnow().isoformat(),
            "data": data,
            "headers": ["Metric", "Value"],
            "rows": [
                ["Issued", data.get("issued", 0)],
                ["Closed", data.get("closed", 0)],
                ["Open", data.get("open", 0)],
                ["Violations", data.get("violations", 0)],
                ["Compliance Rate", f"{data.get('compliance_rate', 0)}%"],
            ],
        }

    def _training_report(self, start_date: date, end_date: date, site_id: str) -> Dict:
        data = self.repo.get_training_summary(site_id=site_id, start_date=start_date, end_date=end_date)
        return {
            "report_type": "Training Compliance",
            "period": f"{start_date} to {end_date}",
            "site_id": site_id,
            "generated_at": datetime.utcnow().isoformat(),
            "data": data,
            "headers": ["Status", "Count"],
            "rows": [
                ["Completed", data.get("completed", 0)],
                ["Failed", data.get("failed", 0)],
                ["Pending", data.get("pending", 0)],
                ["Compliance Rate", f"{data.get('compliance_rate', 0)}%"],
            ],
        }

    def _environmental_report(self, start_date: date, end_date: date, site_id: str) -> Dict:
        data = self.repo.get_environmental_summary(site_id=site_id, start_date=start_date, end_date=end_date)
        return {
            "report_type": "Environmental Monitoring",
            "period": f"{start_date} to {end_date}",
            "site_id": site_id,
            "generated_at": datetime.utcnow().isoformat(),
            "data": data,
            "headers": ["Parameter", "Current", "Limit", "Status"],
            "rows": [
                ["PM2.5", data.get("pm25_current"), data.get("pm25_limit"), data.get("pm25_status")],
                ["Noise (Leq)", data.get("noise_current"), data.get("noise_limit"), data.get("noise_status")],
                ["Total Exceedances", data.get("exceedances"), "", ""],
                ["Total Readings", data.get("total_readings"), "", ""],
            ],
        }

    def _equipment_report(self, site_id: str) -> Dict:
        data = self.repo.get_equipment_summary(site_id=site_id)
        return {
            "report_type": "Equipment Compliance",
            "site_id": site_id,
            "generated_at": datetime.utcnow().isoformat(),
            "data": data,
            "headers": ["Metric", "Value"],
            "rows": [
                ["Total Equipment", data.get("total", 0)],
                ["Valid Cert", data.get("valid_cert", 0)],
                ["Expired Cert", data.get("expired_cert", 0)],
                ["Overdue Inspection", data.get("overdue_inspection", 0)],
            ],
        }

    def _contractor_report(self) -> Dict:
        data = self.repo.get_contractor_summary()
        return {
            "report_type": "Contractor Performance",
            "generated_at": datetime.utcnow().isoformat(),
            "data": data,
            "headers": ["Metric", "Value"],
            "rows": [
                ["Total Contractors", data.get("total", 0)],
                ["Active", data.get("active", 0)],
                ["Audit Passed", data.get("passed", 0)],
                ["Conditional", data.get("conditional", 0)],
                ["Failed", data.get("failed", 0)],
            ],
        }

    def _audit_report(self, site_id: str) -> Dict:
        from app.models.audit import AuditPlan
        query = self.db.query(AuditPlan)
        if site_id and site_id != "all":
            query = query.filter(AuditPlan.site_id == site_id)
        plans = query.all()
        rows = []
        for p in plans:
            rows.append([
                p.audit_id, p.audit_type, p.audit_status,
                p.audit_title, p.compliance_score, p.findings_count
            ])
        return {
            "report_type": "Audit Plans",
            "site_id": site_id,
            "generated_at": datetime.utcnow().isoformat(),
            "headers": ["Audit ID", "Type", "Status", "Title", "Score", "Findings"],
            "rows": rows,
            "record_count": len(rows),
        }

    def _get_export_data(self, data_type: str, start_date: date, end_date: date, site_id: Optional[str], columns: Optional[List[str]]) -> tuple:
        from app.models.hse_models import FactHSE, DimSite, DimDepartment, DimIncident, DimPTW, DimEquipment
        from sqlalchemy import select
        cols = columns
        if data_type == "incidents":
            q = self.db.query(
                FactHSE.date_key, DimSite.site_name, DimDepartment.dept_name,
                FactHSE.incident_key, FactHSE.lti_count, FactHSE.mti_count,
                FactHSE.fai_count, FactHSE.near_miss_count, FactHSE.fatality_count,
            ).join(DimSite, FactHSE.site_key == DimSite.site_id
            ).join(DimDepartment, FactHSE.dept_key == DimDepartment.dept_id
            ).filter(FactHSE.date_key >= start_date, FactHSE.date_key <= end_date)
            if site_id:
                q = q.filter(FactHSE.site_key == site_id)
            results = q.all()
            headers = ["Date", "Site", "Department", "Incident ID", "LTI", "MTI", "First Aid", "Near Miss", "Fatality"]
            return [list(r) for r in results], headers
        elif data_type == "ptw":
            q = self.db.query(
                FactHSE.date_key, DimSite.site_name,
                FactHSE.ptw_key, FactHSE.ptw_issued_count, FactHSE.ptw_closed_count,
                FactHSE.ptw_violation_count,
            ).join(DimSite, FactHSE.site_key == DimSite.site_id
            ).filter(FactHSE.date_key >= start_date, FactHSE.date_key <= end_date)
            if site_id:
                q = q.filter(FactHSE.site_key == site_id)
            results = q.all()
            headers = ["Date", "Site", "PTW ID", "Issued", "Closed", "Violations"]
            return [list(r) for r in results], headers
        elif data_type == "environmental":
            q = self.db.query(
                FactHSE.date_key, DimSite.site_name, FactHSE.env_sample_id,
                FactHSE.env_reading_value, FactHSE.env_limit_value, FactHSE.env_exceeded,
            ).join(DimSite, FactHSE.site_key == DimSite.site_id
            ).filter(
                FactHSE.date_key >= start_date, FactHSE.date_key <= end_date,
                FactHSE.env_reading_value.is_not(None),
            )
            if site_id:
                q = q.filter(FactHSE.site_key == site_id)
            results = q.all()
            headers = ["Date", "Site", "Parameter", "Reading", "Limit", "Exceeded"]
            return [list(r) for r in results], headers
        elif data_type == "equipment":
            q = self.db.query(DimEquipment).filter(DimEquipment.active_to == date(9999, 12, 12))
            if site_id:
                q = q.filter(DimEquipment.current_site_id == site_id)
            results = q.all()
            headers = ["Equipment ID", "Type", "Manufacturer", "Site", "Next Inspection", "Cert Expiry"]
            return [
                [e.equipment_id, e.equipment_type, e.manufacturer, e.current_site_id,
                 e.next_inspection, e.certification_expiry]
                for e in results
            ], headers
        elif data_type == "audit":
            from app.models.audit import AuditPlan
            q = self.db.query(AuditPlan)
            if site_id:
                q = q.filter(AuditPlan.site_id == site_id)
            results = q.all()
            headers = ["Audit ID", "Type", "Status", "Title", "Score", "Findings"]
            return [
                [r.audit_id, r.audit_type, r.audit_status, r.audit_title,
                 r.compliance_score, r.findings_count]
                for r in results
            ], headers
        elif data_type == "alerts":
            from app.models.alert import Alert
            q = self.db.query(Alert).filter(Alert.alert_date >= start_date, Alert.alert_date <= end_date)
            if site_id:
                q = q.filter(Alert.site_id == site_id)
            results = q.all()
            headers = ["Alert ID", "Type", "Severity", "Status", "Site", "Message", "Created"]
            return [
                [r.alert_id, r.alert_type, r.severity.value if hasattr(r.severity, 'value') else r.severity,
                 r.status.value if hasattr(r.status, 'value') else r.status,
                 r.site_name, r.message, r.created_at]
                for r in results
            ], headers
        return [], []


class DataQualityService:
    """Service for data quality checks and validation."""

    def __init__(self, db):
        self.db = db

    def get_data_quality_report(self) -> Dict:
        checks = []
        try:
            fact_count = self.db.execute("SELECT COUNT(*) FROM hse.fact_hse").scalar() or 0
            checks.append({"check_name": "Total Records in fact_hse", "status": "pass", "record_count": fact_count})
        except Exception as e:
            checks.append({"check_name": "Total Records in fact_hse", "status": "fail", "record_count": 0, "details": str(e)})
        try:
            null_hours = self.db.execute("SELECT COUNT(*) FROM hse.fact_hse WHERE man_hours_worked IS NULL").scalar() or 0
            checks.append({
                "check_name": "Null man_hours_worked",
                "status": "fail" if null_hours > 0 else "pass",
                "record_count": null_hours,
                "details": "Records with null man_hours" if null_hours > 0 else "All records have man_hours",
            })
        except Exception as e:
            checks.append({"check_name": "Null man_hours_worked", "status": "fail", "record_count": 0, "details": str(e)})
        try:
            future_dates = self.db.execute("SELECT COUNT(*) FROM hse.fact_hse WHERE date_key > CURRENT_DATE").scalar() or 0
            checks.append({
                "check_name": "Future dates",
                "status": "fail" if future_dates > 0 else "pass",
                "record_count": future_dates,
                "details": "Records with future dates found" if future_dates > 0 else "No future dates",
            })
        except Exception as e:
            checks.append({"check_name": "Future dates", "status": "fail", "record_count": 0, "details": str(e)})
        try:
            last_updated = self.db.execute("SELECT MAX(updated_at) FROM hse.fact_hse").scalar()
            checks.append({
                "check_name": "Last updated",
                "status": "pass",
                "record_count": 0,
                "details": str(last_updated) if last_updated else "Never updated",
            })
        except Exception as e:
            checks.append({"check_name": "Last updated", "status": "fail", "record_count": 0, "details": str(e)})
        try:
            total_sites = self.db.execute("SELECT COUNT(*) FROM hse.dim_site WHERE site_status = 'Active'").scalar() or 0
            checks.append({"check_name": "Active Sites", "status": "pass", "record_count": total_sites})
        except Exception as e:
            checks.append({"check_name": "Active Sites", "status": "fail", "record_count": 0, "details": str(e)})
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "database_status": "healthy",
            "checks": checks,
            "total_records": fact_count if 'fact_count' in dir() else 0,
            "last_updated": str(last_updated) if 'last_updated' in dir() and last_updated else None,
        }

    def validate_data_completeness(self, table_name: str, date_key: Optional[date] = None, site_id: Optional[str] = None) -> Dict:
        null_checks = {
            "fact_hse": ["date_key", "site_key", "man_hours_worked"],
            "dim_incident": ["incident_id", "incident_type", "severity_class"],
            "dim_ptw": ["ptw_id", "ptw_type", "site_id"],
            "dim_equipment": ["equipment_id", "equipment_type"],
        }
        required_cols = null_checks.get(table_name, [])
        results = []
        for col in required_cols:
            try:
                query = f"SELECT COUNT(*) FROM hse.{table_name} WHERE {col} IS NULL"
                if date_key and "date_key" in table_name:
                    query += f" AND date_key = '{date_key}'"
                count = self.db.execute(query).scalar() or 0
                results.append({"column": col, "null_count": count, "status": "fail" if count > 0 else "pass"})
            except Exception as e:
                results.append({"column": col, "null_count": -1, "status": "error", "details": str(e)})
        return {"table": table_name, "checks": results, "validated_at": datetime.utcnow().isoformat()}
