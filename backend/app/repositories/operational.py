"""
Operational Repositories for HSE Operations modules.
Provides generic CRUD pattern for all operational modules.
"""

from typing import List, Dict, Any, Optional, TypeVar, Generic
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func, and_, or_
import uuid
import json
import csv
import io

from app.models.operational import (
    IncidentReport, PTWRequest, TrainingRecord, SafetyObservation,
    EquipmentInspection, HIRAAssessment, NearMissReport,
    ContractorRecord, EnvironmentalReading, OperationalAttachment, WorkflowHistory
)
from app.models.hse_models import DimSite, DimDepartment, DimEmployee


T = TypeVar('T')


class BaseOperationalRepository:
    """Generic base repository for all operational modules."""

    def __init__(self, db: Session, model, module_name: str):
        self.db = db
        self.model = model
        self.module_name = module_name
        self.id_field = self._get_id_field()

    def _get_id_field(self) -> str:
        """Get the primary key field name for the model."""
        pk = [c.name for c in self.model.__table__.primary_key.columns]
        return pk[0] if pk else "id"

    def _build_query(self, site_id: Optional[str] = None, status: Optional[str] = None,
                     start_date: Optional[date] = None, end_date: Optional[date] = None,
                     **filters):
        """Build base query with common filters."""
        query = self.db.query(self.model).filter(self.model.is_deleted == False)

        if site_id and site_id != "all":
            query = query.filter(self.model.site_id == site_id)
        if status and status != "all":
            query = query.filter(self.model.status == status)

        # Date filtering - look for common date field names
        date_field = None
        for field in ["report_date", "request_date", "training_date", "observation_date",
                      "inspection_date", "assessment_date", "record_date", "reading_date"]:
            if hasattr(self.model, field):
                date_field = field
                break

        if date_field and start_date:
            query = query.filter(getattr(self.model, date_field) >= start_date)
        if date_field and end_date:
            query = query.filter(getattr(self.model, date_field) <= end_date)

        # Apply additional filters
        for key, value in filters.items():
            if value is not None and hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)

        return query

    def get_all(self, site_id: Optional[str] = None, status: Optional[str] = None,
                start_date: Optional[date] = None, end_date: Optional[date] = None,
                page: int = 1, page_size: int = 50, sort_by: Optional[str] = None,
                sort_order: str = "desc", **filters) -> Dict[str, Any]:
        """Get all records with pagination, sorting, and filtering."""
        query = self._build_query(site_id=site_id, status=status,
                                  start_date=start_date, end_date=end_date, **filters)

        # Apply sorting
        sort_field = sort_by or "created_at"
        if hasattr(self.model, sort_field):
            sort_col = getattr(self.model, sort_field)
            if sort_order == "asc":
                query = query.order_by(asc(sort_col))
            else:
                query = query.order_by(desc(sort_col))

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()

        return {
            "items": [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 0,
            "filters": {k: v for k, v in filters.items() if v is not None},
            "sort_by": sort_field,
            "sort_order": sort_order,
        }

    def get_by_id(self, record_id: str) -> Optional[Dict]:
        """Get a single record by ID."""
        record = self.db.query(self.model).filter(
            getattr(self.model, self.id_field) == record_id,
            self.model.is_deleted == False
        ).first()
        if not record:
            return None
        return {c.name: getattr(record, c.name) for c in record.__table__.columns}

    def create(self, data: Dict) -> Dict:
        """Create a new record."""
        record_id = data.get(self.id_field) or str(uuid.uuid4())
        data[self.id_field] = record_id
        data["created_by"] = data.get("created_by", "system")
        data["updated_by"] = data.get("updated_by", data.get("created_by", "system"))

        record = self.model(**data)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return {c.name: getattr(record, c.name) for c in record.__table__.columns}

    def update(self, record_id: str, data: Dict) -> Optional[Dict]:
        """Update an existing record."""
        record = self.db.query(self.model).filter(
            getattr(self.model, self.id_field) == record_id,
            self.model.is_deleted == False
        ).first()
        if not record:
            return None

        data.pop(self.id_field, None)
        data.pop("created_by", None)
        data.pop("created_at", None)
        data["updated_by"] = data.get("updated_by", "system")
        data["updated_at"] = datetime.utcnow()
        data["version"] = (record.version or 1) + 1

        for key, value in data.items():
            if value is not None and hasattr(record, key):
                setattr(record, key, value)

        self.db.commit()
        self.db.refresh(record)
        return {c.name: getattr(record, c.name) for c in record.__table__.columns}

    def soft_delete(self, record_id: str, deleted_by: str = "system") -> bool:
        """Soft delete a record."""
        record = self.db.query(self.model).filter(
            getattr(self.model, self.id_field) == record_id,
            self.model.is_deleted == False
        ).first()
        if not record:
            return False
        record.is_deleted = True
        record.deleted_at = datetime.utcnow()
        record.deleted_by = deleted_by
        record.status = "deleted"
        self.db.commit()
        return True

    def record_workflow_transition(self, record_id: str, from_status: str, to_status: str,
                                    action: str, performed_by: str, remarks: str = None,
                                    ip_address: str = None, user_agent: str = None):
        """Record a workflow transition."""
        transition = WorkflowHistory(
            module=self.module_name,
            record_id=record_id,
            from_status=from_status,
            to_status=to_status,
            action=action,
            remarks=remarks,
            performed_by=performed_by,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(transition)
        self.db.commit()
        return transition

    def get_workflow_history(self, record_id: str) -> List[Dict]:
        """Get workflow history for a record."""
        transitions = self.db.query(WorkflowHistory).filter(
            WorkflowHistory.module == self.module_name,
            WorkflowHistory.record_id == record_id
        ).order_by(desc(WorkflowHistory.performed_at)).all()
        return [{c.name: getattr(t, c.name) for c in t.__table__.columns} for t in transitions]

    def get_attachments(self, record_id: str) -> List[Dict]:
        """Get attachments for a record."""
        attachments = self.db.query(OperationalAttachment).filter(
            OperationalAttachment.module == self.module_name,
            OperationalAttachment.record_id == record_id,
            OperationalAttachment.is_deleted == False
        ).order_by(desc(OperationalAttachment.uploaded_at)).all()
        return [{c.name: getattr(a, c.name) for c in a.__table__.columns} for a in attachments]

    def add_attachment(self, record_id: str, file_name: str, file_path: str,
                       file_type: str = None, file_size: int = None,
                       mime_type: str = None, description: str = None,
                       uploaded_by: str = "system", is_public: bool = False) -> Dict:
        """Add an attachment to a record."""
        attachment = OperationalAttachment(
            module=self.module_name,
            record_id=record_id,
            file_name=file_name,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            mime_type=mime_type,
            description=description,
            uploaded_by=uploaded_by,
            is_public=is_public,
        )
        self.db.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)
        return {c.name: getattr(attachment, c.name) for c in attachment.__table__.columns}

    def delete_attachment(self, attachment_id: str) -> bool:
        """Soft delete an attachment."""
        attachment = self.db.query(OperationalAttachment).filter(
            OperationalAttachment.attachment_id == attachment_id,
            OperationalAttachment.module == self.module_name
        ).first()
        if not attachment:
            return False
        attachment.is_deleted = True
        self.db.commit()
        return True


class IncidentRepository(BaseOperationalRepository):
    """Repository for incident reports."""

    def __init__(self, db: Session):
        super().__init__(db, IncidentReport, "incident")

    def get_dashboard_stats(self, site_id: Optional[str] = None, period_days: int = 30) -> Dict:
        """Get incident dashboard statistics."""
        from datetime import date, timedelta
        end_date = date.today()
        start_date = end_date - timedelta(days=period_days)

        query = self.db.query(IncidentReport).filter(
            IncidentReport.is_deleted == False,
            IncidentReport.report_date >= start_date,
            IncidentReport.report_date <= end_date
        )

        if site_id and site_id != "all":
            query = query.filter(IncidentReport.site_id == site_id)

        records = query.all()

        by_severity = {}
        by_status = {}
        by_category = {}
        by_site = {}
        total_lost_days = 0
        total_restricted_days = 0
        open_investigations = 0
        overdue_investigations = 0

        for r in records:
            # By severity
            sev = r.severity or "Unknown"
            by_severity[sev] = by_severity.get(sev, 0) + 1

            # By status
            status = r.case_status or "Unknown"
            by_status[status] = by_status.get(status, 0) + 1

            # By category
            cat = r.category or "Unknown"
            by_category[cat] = by_category.get(cat, 0) + 1

            # By site
            site = r.site_id or "Unknown"
            by_site[site] = by_site.get(site, 0) + 1

            # Days
            total_lost_days += r.lost_days or 0
            total_restricted_days += r.restricted_days or 0

            # Investigations
            if r.investigation_required and r.case_status not in ("Closed", "Cancelled"):
                open_investigations += 1
                if r.investigation_due and r.investigation_due < end_date:
                    overdue_investigations += 1

        # Get site names
        site_names = {}
        sites = self.db.query(DimSite).all()
        for s in sites:
            site_names[s.site_id] = s.site_name

        by_site_named = {site_names.get(k, k): v for k, v in by_site.items()}

        # Trend data
        trend_query = self.db.query(
            IncidentReport.report_date,
            func.count(IncidentReport.report_id).label("count")
        ).filter(
            IncidentReport.is_deleted == False,
            IncidentReport.report_date >= start_date,
            IncidentReport.report_date <= end_date
        )
        if site_id and site_id != "all":
            trend_query = trend_query.filter(IncidentReport.site_id == site_id)
        trend_query = trend_query.group_by(IncidentReport.report_date).order_by(IncidentReport.report_date)

        trend = [
            {"date": t.report_date.isoformat(), "count": t.count}
            for t in trend_query.all()
        ]

        return {
            "total_reports": len(records),
            "by_severity": by_severity,
            "by_status": by_status,
            "by_category": by_category,
            "by_site": by_site_named,
            "open_investigations": open_investigations,
            "overdue_investigations": overdue_investigations,
            "total_lost_days": total_lost_days,
            "total_restricted_days": total_restricted_days,
            "trend": trend,
            "period_start": start_date,
            "period_end": end_date,
        }

    def export_to_csv(self, site_id: Optional[str] = None, start_date: Optional[date] = None,
                      end_date: Optional[date] = None, columns: Optional[List[str]] = None) -> tuple:
        """Export incidents to CSV format."""
        query = self._build_query(site_id=site_id, start_date=start_date, end_date=end_date)
        records = query.order_by(desc(IncidentReport.report_date)).all()

        default_columns = [
            "report_id", "report_date", "site_id", "department_id", "shift", "location",
            "category", "severity", "incident_type", "description", "immediate_action",
            "pic", "witness", "lost_days", "ptw_required", "case_status", "created_by", "created_at"
        ]
        cols = columns or default_columns

        headers = [
            "Report ID", "Date", "Site", "Department", "Shift", "Location",
            "Category", "Severity", "Type", "Description", "Immediate Action",
            "PIC", "Witness", "Lost Days", "PTW Required", "Status", "Created By", "Created At"
        ]

        rows = []
        for r in records:
            row = []
            for col in cols:
                val = getattr(r, col, "")
                if isinstance(val, (datetime, date)):
                    val = val.isoformat() if val else ""
                elif val is None:
                    val = ""
                row.append(val)
            rows.append(row)

        return rows, headers

    def export_to_excel(self, site_id: Optional[str] = None, start_date: Optional[date] = None,
                        end_date: Optional[date] = None) -> tuple:
        """Export incidents to Excel format (CSV for now, can be extended to xlsx)."""
        return self.export_to_csv(site_id=site_id, start_date=start_date, end_date=end_date)

    def import_from_csv(self, file_content: str, created_by: str = "system") -> Dict:
        """Import incidents from CSV content."""
        results = {"success": 0, "failed": 0, "errors": []}
        reader = csv.DictReader(io.StringIO(file_content))

        for i, row in enumerate(reader, start=2):
            try:
                # Validate required fields
                required_fields = ["site_id", "location", "category", "severity", "incident_type", "description"]
                missing = [f for f in required_fields if not row.get(f)]
                if missing:
                    results["errors"].append({
                        "row": i,
                        "error": f"Missing required fields: {', '.join(missing)}",
                        "data": dict(row)
                    })
                    results["failed"] += 1
                    continue

                # Validate site exists
                site = self.db.query(DimSite).filter(DimSite.site_id == row.get("site_id")).first()
                if not site:
                    results["errors"].append({
                        "row": i,
                        "error": f"Site '{row.get('site_id')}' not found",
                        "data": dict(row)
                    })
                    results["failed"] += 1
                    continue

                # Create record
                report_id = f"INC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{i}"
                record = IncidentReport(
                    report_id=report_id,
                    site_id=row.get("site_id"),
                    department_id=row.get("department_id"),
                    shift=row.get("shift"),
                    location=row.get("location"),
                    category=row.get("category"),
                    severity=row.get("severity"),
                    incident_type=row.get("incident_type"),
                    description=row.get("description"),
                    immediate_action=row.get("immediate_action"),
                    pic=row.get("pic"),
                    witness=row.get("witness"),
                    lost_days=int(row.get("lost_days", 0) or 0),
                    ptw_required=row.get("ptw_required", "").lower() in ("true", "1", "yes"),
                    case_status=row.get("case_status", "Draft"),
                    created_by=created_by,
                )
                self.db.add(record)
                results["success"] += 1

            except Exception as e:
                results["errors"].append({
                    "row": i,
                    "error": str(e),
                    "data": dict(row)
                })
                results["failed"] += 1

        self.db.commit()
        return results


class PTWRepository(BaseOperationalRepository):
    """Repository for PTW requests."""

    def __init__(self, db: Session):
        super().__init__(db, PTWRequest, "ptw")

    def get_dashboard_stats(self, site_id: Optional[str] = None, period_days: int = 30) -> Dict:
        """Get PTW dashboard statistics."""
        from datetime import date, timedelta
        end_date = date.today()
        start_date = end_date - timedelta(days=period_days)

        query = self.db.query(PTWRequest).filter(
            PTWRequest.is_deleted == False,
            PTWRequest.request_date >= start_date,
            PTWRequest.request_date <= end_date
        )

        if site_id and site_id != "all":
            query = query.filter(PTWRequest.site_id == site_id)

        records = query.all()

        by_status = {}
        by_type = {}
        total_active = 0
        total_expired = 0
        total_violations = 0

        for r in records:
            status = r.ptw_status or "Unknown"
            by_status[status] = by_status.get(status, 0) + 1

            ptype = r.ptw_type or "Unknown"
            by_type[ptype] = by_type.get(ptype, 0) + 1

            if r.ptw_status == "Active":
                total_active += 1
            elif r.ptw_status == "Expired":
                total_expired += 1

            total_violations += r.violation_count or 0

        return {
            "total_requests": len(records),
            "by_status": by_status,
            "by_type": by_type,
            "active_permits": total_active,
            "expired_permits": total_expired,
            "total_violations": total_violations,
            "period_start": start_date,
            "period_end": end_date,
        }


class TrainingRepository(BaseOperationalRepository):
    """Repository for training records."""

    def __init__(self, db: Session):
        super().__init__(db, TrainingRecord, "training")

    def get_dashboard_stats(self, site_id: Optional[str] = None, period_days: int = 30) -> Dict:
        """Get training dashboard statistics."""
        from datetime import date, timedelta
        end_date = date.today()
        start_date = end_date - timedelta(days=period_days)

        query = self.db.query(TrainingRecord).filter(
            TrainingRecord.is_deleted == False,
            TrainingRecord.training_date >= start_date,
            TrainingRecord.training_date <= end_date
        )

        if site_id and site_id != "all":
            query = query.filter(TrainingRecord.site_id == site_id)

        records = query.all()

        by_result = {}
        by_type = {}
        total_completed = 0
        total_pending = 0
        total_failed = 0
        expiring_soon = 0

        for r in records:
            result = r.result or "Unknown"
            by_result[result] = by_result.get(result, 0) + 1

            ttype = r.training_type or "Unknown"
            by_type[ttype] = by_type.get(ttype, 0) + 1

            if r.result == "Pass":
                total_completed += 1
            elif r.result == "Pending":
                total_pending += 1
            elif r.result == "Fail":
                total_failed += 1

            if r.expiry_date and r.expiry_date <= end_date + __import__('datetime').timedelta(days=30):
                expiring_soon += 1

        return {
            "total_records": len(records),
            "by_result": by_result,
            "by_type": by_type,
            "completed": total_completed,
            "pending": total_pending,
            "failed": total_failed,
            "expiring_soon": expiring_soon,
            "period_start": start_date,
            "period_end": end_date,
        }


class ObservationRepository(BaseOperationalRepository):
    """Repository for safety observations."""

    def __init__(self, db: Session):
        super().__init__(db, SafetyObservation, "observation")

    def get_dashboard_stats(self, site_id: Optional[str] = None, period_days: int = 30) -> Dict:
        """Get observation dashboard statistics."""
        from datetime import date, timedelta
        end_date = date.today()
        start_date = end_date - timedelta(days=period_days)

        query = self.db.query(SafetyObservation).filter(
            SafetyObservation.is_deleted == False,
            SafetyObservation.observation_date >= start_date,
            SafetyObservation.observation_date <= end_date
        )

        if site_id and site_id != "all":
            query = query.filter(SafetyObservation.site_id == site_id)

        records = query.all()

        by_type = {}
        by_status = {}
        total_safe = 0
        total_unsafe = 0
        total_open = 0

        for r in records:
            otype = r.observation_type or "Unknown"
            by_type[otype] = by_type.get(otype, 0) + 1

            status = r.status or "Unknown"
            by_status[status] = by_status.get(status, 0) + 1

            if r.observation_type == "Safe":
                total_safe += 1
            elif r.observation_type == "Unsafe":
                total_unsafe += 1

            if r.status == "Open":
                total_open += 1

        return {
            "total_observations": len(records),
            "by_type": by_type,
            "by_status": by_status,
            "safe_observations": total_safe,
            "unsafe_observations": total_unsafe,
            "open_items": total_open,
            "period_start": start_date,
            "period_end": end_date,
        }


class EquipmentInspectionRepository(BaseOperationalRepository):
    """Repository for equipment inspections."""

    def __init__(self, db: Session):
        super().__init__(db, EquipmentInspection, "equipment")


class HIRARepository(BaseOperationalRepository):
    """Repository for HIRA assessments."""

    def __init__(self, db: Session):
        super().__init__(db, HIRAAssessment, "hira")


class NearMissRepository(BaseOperationalRepository):
    """Repository for near miss reports."""

    def __init__(self, db: Session):
        super().__init__(db, NearMissReport, "near_miss")

    def get_dashboard_stats(self, site_id: Optional[str] = None, period_days: int = 30) -> Dict:
        """Get near miss dashboard statistics."""
        from datetime import date, timedelta
        end_date = date.today()
        start_date = end_date - timedelta(days=period_days)

        query = self.db.query(NearMissReport).filter(
            NearMissReport.is_deleted == False,
            NearMissReport.report_date >= start_date,
            NearMissReport.report_date <= end_date
        )

        if site_id and site_id != "all":
            query = query.filter(NearMissReport.site_id == site_id)

        records = query.all()

        by_status = {}
        by_category = {}
        by_potential_severity = {}

        for r in records:
            status = r.status or "Unknown"
            by_status[status] = by_status.get(status, 0) + 1

            cat = r.category or "Unknown"
            by_category[cat] = by_category.get(cat, 0) + 1

            sev = r.severity_potential or "Unknown"
            by_potential_severity[sev] = by_potential_severity.get(sev, 0) + 1

        return {
            "total_reports": len(records),
            "by_status": by_status,
            "by_category": by_category,
            "by_potential_severity": by_potential_severity,
            "shared_with_team": sum(1 for r in records if r.shared_with_team),
            "period_start": start_date,
            "period_end": end_date,
        }


class ContractorRepository(BaseOperationalRepository):
    """Repository for contractor records."""

    def __init__(self, db: Session):
        super().__init__(db, ContractorRecord, "contractor")


class EnvironmentalRepository(BaseOperationalRepository):
    """Repository for environmental readings."""

    def __init__(self, db: Session):
        super().__init__(db, EnvironmentalReading, "environmental")
