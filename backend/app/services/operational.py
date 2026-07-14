"""
Operational Services for HSE Operations modules.
Business logic orchestration for all operational modules.
"""

from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
import uuid

from app.repositories.operational import (
    IncidentRepository, PTWRepository, TrainingRepository,
    ObservationRepository, EquipmentInspectionRepository,
    HIRARepository, NearMissRepository, ContractorRepository,
    EnvironmentalRepository
)


class IncidentService:
    """Service for incident report management."""

    def __init__(self, db: Session):
        self.repo = IncidentRepository(db)

    def get_dashboard(self, site_id: Optional[str] = None, period_days: int = 30) -> Dict:
        """Get incident dashboard data."""
        return self.repo.get_dashboard_stats(site_id=site_id, period_days=period_days)

    def list_incidents(self, site_id: Optional[str] = None, status: Optional[str] = None,
                       severity: Optional[str] = None, category: Optional[str] = None,
                       page: int = 1, page_size: int = 50, sort_by: str = "report_date",
                       sort_order: str = "desc") -> Dict:
        """List incidents with filtering and pagination."""
        filters = {}
        if severity:
            filters["severity"] = severity
        if category:
            filters["category"] = category
        return self.repo.get_all(
            site_id=site_id, status=status, page=page, page_size=page_size,
            sort_by=sort_by, sort_order=sort_order, **filters
        )

    def get_incident(self, report_id: str) -> Optional[Dict]:
        """Get single incident with workflow history and attachments."""
        incident = self.repo.get_by_id(report_id)
        if not incident:
            return None
        incident["workflow_history"] = self.repo.get_workflow_history(report_id)
        incident["attachments"] = self.repo.get_attachments(report_id)
        return incident

    def create_incident(self, data: Dict, created_by: str) -> Dict:
        """Create new incident report."""
        data["report_id"] = data.get("report_id") or f"INC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8]}"
        data["created_by"] = created_by
        data["case_status"] = "Draft"
        data["workflow_stage"] = "Draft"
        result = self.repo.create(data)
        self.repo.record_workflow_transition(
            record_id=result["report_id"],
            from_status=None,
            to_status="Draft",
            action="create",
            performed_by=created_by,
            remarks="Incident report created"
        )
        return result

    def update_incident(self, report_id: str, data: Dict, updated_by: str) -> Optional[Dict]:
        """Update existing incident."""
        data["updated_by"] = updated_by
        result = self.repo.update(report_id, data)
        if result:
            self.repo.record_workflow_transition(
                record_id=report_id,
                from_status=result.get("case_status", "Unknown"),
                to_status=result.get("case_status", "Unknown"),
                action="update",
                performed_by=updated_by,
                remarks="Incident report updated"
            )
        return result

    def delete_incident(self, report_id: str, deleted_by: str) -> bool:
        """Soft delete incident."""
        return self.repo.soft_delete(report_id, deleted_by)

    def submit_incident(self, report_id: str, submitted_by: str) -> Optional[Dict]:
        """Submit incident for review."""
        incident = self.repo.get_by_id(report_id)
        if not incident:
            return None
        if incident["case_status"] != "Draft":
            raise ValueError("Only draft incidents can be submitted")

        result = self.repo.update(report_id, {
            "case_status": "Submitted",
            "workflow_stage": "Submitted"
        }, updated_by=submitted_by)
        if result:
            self.repo.record_workflow_transition(
                record_id=report_id,
                from_status="Draft",
                to_status="Submitted",
                action="submit",
                performed_by=submitted_by,
                remarks="Incident submitted for review"
            )
        return result

    def approve_incident(self, report_id: str, approved_by: str, remarks: str = None) -> Optional[Dict]:
        """Approve incident."""
        incident = self.repo.get_by_id(report_id)
        if not incident:
            return None
        if incident["case_status"] not in ("Submitted", "Under Review"):
            raise ValueError("Incident must be submitted before approval")

        result = self.repo.update(report_id, {
            "case_status": "Approved",
            "workflow_stage": "Approved"
        }, updated_by=approved_by)
        if result:
            self.repo.record_workflow_transition(
                record_id=report_id,
                from_status=incident["case_status"],
                to_status="Approved",
                action="approve",
                performed_by=approved_by,
                remarks=remarks or "Incident approved"
            )
        return result

    def close_incident(self, report_id: str, closed_by: str, remarks: str = None) -> Optional[Dict]:
        """Close incident."""
        incident = self.repo.get_by_id(report_id)
        if not incident:
            return None
        if incident["case_status"] not in ("Approved", "Under Review"):
            raise ValueError("Incident must be approved before closing")

        result = self.repo.update(report_id, {
            "case_status": "Closed",
            "workflow_stage": "Closed"
        }, updated_by=closed_by)
        if result:
            self.repo.record_workflow_transition(
                record_id=report_id,
                from_status=incident["case_status"],
                to_status="Closed",
                action="close",
                performed_by=closed_by,
                remarks=remarks or "Incident closed"
            )
        return result

    def export_incidents(self, site_id: Optional[str] = None, start_date: Optional[date] = None,
                         end_date: Optional[date] = None, format: str = "csv") -> Dict:
        """Export incidents in specified format."""
        if format == "csv":
            rows, headers = self.repo.export_to_csv(site_id=site_id, start_date=start_date, end_date=end_date)
            return {
                "format": "csv",
                "headers": headers,
                "rows": rows,
                "file_name": f"incidents_{start_date}_{end_date}.csv"
            }
        elif format == "excel":
            rows, headers = self.repo.export_to_excel(site_id=site_id, start_date=start_date, end_date=end_date)
            return {
                "format": "excel",
                "headers": headers,
                "rows": rows,
                "file_name": f"incidents_{start_date}_{end_date}.xlsx"
            }
        else:
            raise ValueError(f"Unsupported format: {format}")

    def import_incidents(self, file_content: str, created_by: str = "system") -> Dict:
        """Import incidents from CSV."""
        return self.repo.import_from_csv(file_content, created_by)


class PTWService:
    """Service for PTW management."""

    def __init__(self, db: Session):
        self.repo = PTWRepository(db)

    def get_dashboard(self, site_id: Optional[str] = None, period_days: int = 30) -> Dict:
        """Get PTW dashboard data."""
        return self.repo.get_dashboard_stats(site_id=site_id, period_days=period_days)

    def list_ptws(self, site_id: Optional[str] = None, status: Optional[str] = None,
                  page: int = 1, page_size: int = 50, sort_by: str = "start_at",
                  sort_order: str = "desc") -> Dict:
        """List PTWs with filtering and pagination."""
        return self.repo.get_all(
            site_id=site_id, status=status, page=page, page_size=page_size,
            sort_by=sort_by, sort_order=sort_order
        )

    def get_ptw(self, request_id: str) -> Optional[Dict]:
        """Get single PTW with history and attachments."""
        ptw = self.repo.get_by_id(request_id)
        if not ptw:
            return None
        ptw["workflow_history"] = self.repo.get_workflow_history(request_id)
        ptw["attachments"] = self.repo.get_attachments(request_id)
        return ptw

    def create_ptw(self, data: Dict, created_by: str) -> Dict:
        """Create new PTW request."""
        data["request_id"] = data.get("request_id") or f"PTW-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8]}"
        data["created_by"] = created_by
        data["ptw_status"] = "Draft"
        data["workflow_stage"] = "Draft"
        result = self.repo.create(data)
        self.repo.record_workflow_transition(
            record_id=result["request_id"],
            from_status=None,
            to_status="Draft",
            action="create",
            performed_by=created_by,
            remarks="PTW request created"
        )
        return result

    def update_ptw(self, request_id: str, data: Dict, updated_by: str) -> Optional[Dict]:
        """Update PTW request."""
        data["updated_by"] = updated_by
        result = self.repo.update(request_id, data)
        if result:
            self.repo.record_workflow_transition(
                record_id=request_id,
                from_status=result.get("ptw_status", "Unknown"),
                to_status=result.get("ptw_status", "Unknown"),
                action="update",
                performed_by=updated_by,
                remarks="PTW request updated"
            )
        return result

    def submit_ptw(self, request_id: str, submitted_by: str) -> Optional[Dict]:
        """Submit PTW for approval."""
        ptw = self.repo.get_by_id(request_id)
        if not ptw:
            return None
        if ptw["ptw_status"] != "Draft":
            raise ValueError("Only draft PTWs can be submitted")

        result = self.repo.update(request_id, {
            "ptw_status": "Pending Approval",
            "workflow_stage": "Pending Approval"
        }, updated_by=submitted_by)
        if result:
            self.repo.record_workflow_transition(
                record_id=request_id,
                from_status="Draft",
                to_status="Pending Approval",
                action="submit",
                performed_by=submitted_by,
                remarks="PTW submitted for approval"
            )
        return result

    def approve_ptw(self, request_id: str, approved_by: str) -> Optional[Dict]:
        """Approve PTW."""
        ptw = self.repo.get_by_id(request_id)
        if not ptw:
            return None
        if ptw["ptw_status"] != "Pending Approval":
            raise ValueError("PTW must be pending approval")

        result = self.repo.update(request_id, {
            "ptw_status": "Approved",
            "workflow_stage": "Approved",
            "approved_by": approved_by,
            "approved_at": datetime.utcnow()
        }, updated_by=approved_by)
        if result:
            self.repo.record_workflow_transition(
                record_id=request_id,
                from_status="Pending Approval",
                to_status="Approved",
                action="approve",
                performed_by=approved_by,
                remarks="PTW approved"
            )
        return result

    def activate_ptw(self, request_id: str, activated_by: str) -> Optional[Dict]:
        """Activate approved PTW."""
        ptw = self.repo.get_by_id(request_id)
        if not ptw:
            return None
        if ptw["ptw_status"] != "Approved":
            raise ValueError("PTW must be approved before activation")

        result = self.repo.update(request_id, {
            "ptw_status": "Active",
            "workflow_stage": "Active",
            "actual_start": datetime.utcnow()
        }, updated_by=activated_by)
        if result:
            self.repo.record_workflow_transition(
                record_id=request_id,
                from_status="Approved",
                to_status="Active",
                action="activate",
                performed_by=activated_by,
                remarks="PTW activated"
            )
        return result

    def close_ptw(self, request_id: str, closed_by: str) -> Optional[Dict]:
        """Close PTW."""
        ptw = self.repo.get_by_id(request_id)
        if not ptw:
            return None
        if ptw["ptw_status"] != "Active":
            raise ValueError("Only active PTWs can be closed")

        result = self.repo.update(request_id, {
            "ptw_status": "Closed",
            "workflow_stage": "Closed",
            "actual_end": datetime.utcnow()
        }, updated_by=closed_by)
        if result:
            self.repo.record_workflow_transition(
                record_id=request_id,
                from_status="Active",
                to_status="Closed",
                action="close",
                performed_by=closed_by,
                remarks="PTW closed"
            )
        return result


class TrainingService:
    """Service for training records."""

    def __init__(self, db: Session):
        self.repo = TrainingRepository(db)

    def get_dashboard(self, site_id: Optional[str] = None, period_days: int = 30) -> Dict:
        """Get training dashboard data."""
        return self.repo.get_dashboard_stats(site_id=site_id, period_days=period_days)

    def list_training(self, site_id: Optional[str] = None, result: Optional[str] = None,
                      page: int = 1, page_size: int = 50) -> Dict:
        """List training records."""
        filters = {}
        if result:
            filters["result"] = result
        return self.repo.get_all(site_id=site_id, page=page, page_size=page_size, **filters)

    def get_training(self, record_id: str) -> Optional[Dict]:
        """Get single training record."""
        record = self.repo.get_by_id(record_id)
        if record:
            record["workflow_history"] = self.repo.get_workflow_history(record_id)
            record["attachments"] = self.repo.get_attachments(record_id)
        return record

    def create_training(self, data: Dict, created_by: str) -> Dict:
        """Create training record."""
        data["record_id"] = data.get("record_id") or f"TRN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8]}"
        data["created_by"] = created_by
        return self.repo.create(data)

    def update_training(self, record_id: str, data: Dict, updated_by: str) -> Optional[Dict]:
        """Update training record."""
        data["updated_by"] = updated_by
        return self.repo.update(record_id, data)

    def delete_training(self, record_id: str, deleted_by: str) -> bool:
        """Soft delete training record."""
        return self.repo.soft_delete(record_id, deleted_by)


class ObservationService:
    """Service for safety observations."""

    def __init__(self, db: Session):
        self.repo = ObservationRepository(db)

    def get_dashboard(self, site_id: Optional[str] = None, period_days: int = 30) -> Dict:
        """Get observation dashboard data."""
        return self.repo.get_dashboard_stats(site_id=site_id, period_days=period_days)

    def list_observations(self, site_id: Optional[str] = None, obs_type: Optional[str] = None,
                          page: int = 1, page_size: int = 50) -> Dict:
        """List observations."""
        filters = {}
        if obs_type:
            filters["observation_type"] = obs_type
        return self.repo.get_all(site_id=site_id, page=page, page_size=page_size, **filters)

    def get_observation(self, observation_id: str) -> Optional[Dict]:
        """Get single observation."""
        obs = self.repo.get_by_id(observation_id)
        if obs:
            obs["workflow_history"] = self.repo.get_workflow_history(observation_id)
            obs["attachments"] = self.repo.get_attachments(observation_id)
        return obs

    def create_observation(self, data: Dict, created_by: str) -> Dict:
        """Create observation."""
        data["observation_id"] = data.get("observation_id") or f"OBS-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8]}"
        data["created_by"] = created_by
        return self.repo.create(data)

    def update_observation(self, observation_id: str, data: Dict, updated_by: str) -> Optional[Dict]:
        """Update observation."""
        data["updated_by"] = updated_by
        return self.repo.update(observation_id, data)

    def close_observation(self, observation_id: str, closed_by: str) -> Optional[Dict]:
        """Close observation."""
        obs = self.repo.get_by_id(observation_id)
        if not obs:
            return None
        return self.repo.update(observation_id, {
            "status": "Closed",
            "closed_at": datetime.utcnow()
        }, updated_by=closed_by)


class NearMissService:
    """Service for near miss reports."""

    def __init__(self, db: Session):
        self.repo = NearMissRepository(db)

    def get_dashboard(self, site_id: Optional[str] = None, period_days: int = 30) -> Dict:
        """Get near miss dashboard data."""
        return self.repo.get_dashboard_stats(site_id=site_id, period_days=period_days)

    def list_near_misses(self, site_id: Optional[str] = None, page: int = 1, page_size: int = 50) -> Dict:
        """List near miss reports."""
        return self.repo.get_all(site_id=site_id, page=page, page_size=page_size)

    def create_near_miss(self, data: Dict, created_by: str) -> Dict:
        """Create near miss report."""
        data["report_id"] = data.get("report_id") or f"NM-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8]}"
        data["created_by"] = created_by
        return self.repo.create(data)

    def get_near_miss(self, report_id: str) -> Optional[Dict]:
        """Get single near miss report."""
        report = self.repo.get_by_id(report_id)
        if report:
            report["workflow_history"] = self.repo.get_workflow_history(report_id)
            report["attachments"] = self.repo.get_attachments(report_id)
        return report


class EquipmentInspectionService:
    """Service for equipment inspections."""

    def __init__(self, db: Session):
        self.repo = EquipmentInspectionRepository(db)

    def list_inspections(self, site_id: Optional[str] = None, result: Optional[str] = None,
                         page: int = 1, page_size: int = 50) -> Dict:
        """List equipment inspections."""
        filters = {}
        if result:
            filters["result"] = result
        return self.repo.get_all(site_id=site_id, page=page, page_size=page_size, **filters)

    def create_inspection(self, data: Dict, created_by: str) -> Dict:
        """Create equipment inspection."""
        data["inspection_id"] = data.get("inspection_id") or f"EQ-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8]}"
        data["created_by"] = created_by
        return self.repo.create(data)


class HIRAService:
    """Service for HIRA assessments."""

    def __init__(self, db: Session):
        self.repo = HIRARepository(db)

    def list_assessments(self, site_id: Optional[str] = None, risk_rating: Optional[str] = None,
                         page: int = 1, page_size: int = 50) -> Dict:
        """List HIRA assessments."""
        filters = {}
        if risk_rating:
            filters["risk_rating"] = risk_rating
        return self.repo.get_all(site_id=site_id, page=page, page_size=page_size, **filters)

    def create_assessment(self, data: Dict, created_by: str) -> Dict:
        """Create HIRA assessment."""
        data["assessment_id"] = data.get("assessment_id") or f"HIRA-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8]}"
        data["created_by"] = created_by
        return self.repo.create(data)


class ContractorService:
    """Service for contractor records."""

    def __init__(self, db: Session):
        self.repo = ContractorRepository(db)

    def list_records(self, site_id: Optional[str] = None, record_type: Optional[str] = None,
                     page: int = 1, page_size: int = 50) -> Dict:
        """List contractor records."""
        filters = {}
        if record_type:
            filters["record_type"] = record_type
        return self.repo.get_all(site_id=site_id, page=page, page_size=page_size, **filters)

    def create_record(self, data: Dict, created_by: str) -> Dict:
        """Create contractor record."""
        data["record_id"] = data.get("record_id") or f"CON-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8]}"
        data["created_by"] = created_by
        return self.repo.create(data)
