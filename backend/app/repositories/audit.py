"""
Audit Trail & Evidence Management Repositories
"""

from typing import Optional, List, Dict, Any
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import uuid

from app.models.audit import (
    AuditPlan, AuditFinding, Evidence, AuditTrail, CorrectiveAction
)
from app.models.hse_models import SecurityUser


class AuditRepository:
    """Repository for audit management."""

    def __init__(self, db: Session):
        self.db = db

    def get_audit_plans(
        self,
        site_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        query = self.db.query(AuditPlan)
        if site_id and site_id != "all":
            query = query.filter(AuditPlan.site_id == site_id)
        if status:
            query = query.filter(AuditPlan.audit_status == status)
        results = query.order_by(desc(AuditPlan.created_at)).limit(limit).all()
        return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in results]

    def get_findings(
        self,
        audit_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        query = self.db.query(AuditFinding)
        if audit_id:
            query = query.filter(AuditFinding.audit_id == audit_id)
        if status:
            query = query.filter(AuditFinding.finding_status == status)
        results = query.order_by(desc(AuditFinding.created_at)).all()
        return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in results]

    def get_evidence(
        self,
        finding_id: Optional[str] = None,
        evidence_type: Optional[str] = None
    ) -> List[Dict]:
        query = self.db.query(Evidence)
        if finding_id:
            query = query.filter(Evidence.finding_id == finding_id)
        if evidence_type:
            query = query.filter(Evidence.evidence_type == evidence_type)
        results = query.order_by(desc(Evidence.uploaded_at)).all()
        return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in results]

    def create_audit_trail(
        self,
        user_id: int,
        action: str,
        table_name: str,
        record_id: str,
        old_values: Dict = None,
        new_values: Dict = None,
        ip_address: str = None,
        user_agent: str = None,
        session_id: str = None
    ) -> AuditTrail:
        trail = AuditTrail(
            trail_id=str(uuid.uuid4()),
            user_id=user_id,
            action=action,
            table_name=table_name,
            record_id=record_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
        )
        self.db.add(trail)
        self.db.commit()
        self.db.refresh(trail)
        return trail

    def get_audit_trail(
        self,
        user_id: Optional[int] = None,
        table_name: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditTrail]:
        query = self.db.query(AuditTrail)
        if user_id:
            query = query.filter(AuditTrail.user_id == user_id)
        if table_name:
            query = query.filter(AuditTrail.table_name == table_name)
        return query.order_by(desc(AuditTrail.created_at)).limit(limit).all()


class EvidenceRepository:
    """Repository for evidence management."""

    def __init__(self, db: Session):
        self.db = db

    def upload_evidence(
        self,
        evidence_type: str,
        file_name: str,
        file_path: str,
        uploaded_by: str,
        finding_id: Optional[str] = None,
        incident_id: Optional[str] = None,
        ptw_id: Optional[str] = None,
        training_id: Optional[str] = None,
        description: str = None,
        tags: List[str] = None
    ) -> Evidence:
        evidence = Evidence(
            evidence_id=str(uuid.uuid4()),
            finding_id=finding_id,
            incident_id=incident_id,
            ptw_id=ptw_id,
            training_id=training_id,
            evidence_type=evidence_type,
            file_name=file_name,
            file_path=file_path,
            uploaded_by=uploaded_by,
            description=description,
            tags=tags or [],
        )
        self.db.add(evidence)
        self.db.commit()
        self.db.refresh(evidence)
        return evidence

    def get_evidence_by_ref(
        self,
        ref_type: str,
        ref_id: str
    ) -> List[Evidence]:
        query = self.db.query(Evidence)
        if ref_type == "finding":
            query = query.filter(Evidence.finding_id == ref_id)
        elif ref_type == "incident":
            query = query.filter(Evidence.incident_id == ref_id)
        elif ref_type == "ptw":
            query = query.filter(Evidence.ptw_id == ref_id)
        elif ref_type == "training":
            query = query.filter(Evidence.training_id == ref_id)
        return query.order_by(desc(Evidence.uploaded_at)).all()

    def get_evidence(self, finding_id: Optional[str] = None, incident_id: Optional[str] = None) -> List[Evidence]:
        """Get evidence by finding or incident ID."""
        query = self.db.query(Evidence)
        if finding_id:
            query = query.filter(Evidence.finding_id == finding_id)
        if incident_id:
            query = query.filter(Evidence.incident_id == incident_id)
        return query.order_by(desc(Evidence.uploaded_at)).all()
