"""
Audit Trail & Evidence Management Models
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Numeric, ForeignKey, Text, Enum as SQLEnum, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class AuditType(str, enum.Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"
    CERTIFICATION = "certification"
    SURVEILLANCE = "surveillance"
    NONCONFORMITY = "nonconformity"
    MANAGEMENT_REVIEW = "management_review"


class AuditStatus(str, enum.Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class FindingType(str, enum.Enum):
    MAJOR = "major"
    MINOR = "minor"
    OBSERVATION = "observation"
    OPPORTUNITY = "opportunity"


class FindingStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"
    OVERDUE = "overdue"


class EvidenceType(str, enum.Enum):
    PHOTO = "photo"
    DOCUMENT = "document"
    VIDEO = "video"
    AUDIO = "audio"
    CHECKLIST = "checklist"
    CERTIFICATE = "certificate"
    REPORT = "report"


class AuditFinding(Base):
    __tablename__ = "audit_findings"
    __table_args__ = {"schema": "hse"}

    finding_id = Column(String(50), primary_key=True)
    audit_id = Column(String(50), ForeignKey("hse.audit_plans.audit_id"), nullable=False)
    finding_type = Column(SQLEnum(FindingType), nullable=False)
    finding_status = Column(SQLEnum(FindingStatus), default=FindingStatus.OPEN)
    clause_ref = Column(String(100))
    description = Column(Text, nullable=False)
    objective_evidence = Column(Text)
    root_cause = Column(Text)
    corrective_action = Column(Text)
    preventive_action = Column(Text)
    pic = Column(String(200))
    due_date = Column(Date)
    closed_date = Column(Date)
    severity_score = Column(Integer)
    created_by = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditPlan(Base):
    __tablename__ = "audit_plans"
    __table_args__ = {"schema": "hse"}

    audit_id = Column(String(50), primary_key=True)
    audit_type = Column(SQLEnum(AuditType), nullable=False)
    audit_status = Column(SQLEnum(AuditStatus), default=AuditStatus.PLANNED)
    audit_title = Column(String(200), nullable=False)
    standard_ref = Column(String(100))
    site_id = Column(String(20), ForeignKey("hse.dim_site.site_id"))
    department_id = Column(String(20), ForeignKey("hse.dim_department.dept_id"))
    lead_auditor = Column(String(200))
    audit_team = Column(JSONB)
    scope = Column(Text)
    criteria = Column(Text)
    scheduled_start = Column(Date)
    scheduled_end = Column(Date)
    actual_start = Column(Date)
    actual_end = Column(Date)
    findings_count = Column(Integer, default=0)
    major_findings = Column(Integer, default=0)
    minor_findings = Column(Integer, default=0)
    observations = Column(Integer, default=0)
    compliance_score = Column(Numeric(5, 2))
    audit_report = Column(Text)
    created_by = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Evidence(Base):
    __tablename__ = "evidence"
    __table_args__ = {"schema": "hse"}

    evidence_id = Column(String(50), primary_key=True)
    finding_id = Column(String(50), ForeignKey("hse.audit_findings.finding_id"))
    incident_id = Column(String(30), ForeignKey("hse.dim_incident.incident_id"))
    ptw_id = Column(String(30), ForeignKey("hse.dim_ptw.ptw_id"))
    training_id = Column(String(30), ForeignKey("hse.dim_training.training_id"))
    evidence_type = Column(SQLEnum(EvidenceType), nullable=False)
    file_name = Column(String(200), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    description = Column(Text)
    captured_by = Column(String(200))
    captured_at = Column(DateTime)
    uploaded_by = Column(String(200))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    is_public = Column(Boolean, default=False)
    tags = Column(JSONB)
    checksum = Column(String(64))


class AuditTrail(Base):
    __tablename__ = "audit_trail"
    __table_args__ = {"schema": "hse"}

    trail_id = Column(String(50), primary_key=True)
    user_id = Column(Integer, ForeignKey("hse.security_users.user_id"))
    user_email = Column(String(200))
    action = Column(String(100), nullable=False)
    table_name = Column(String(100), nullable=False)
    record_id = Column(String(50), nullable=False)
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    session_id = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)


class CorrectiveAction(Base):
    __tablename__ = "corrective_actions"
    __table_args__ = {"schema": "hse"}

    car_id = Column(String(50), primary_key=True)
    finding_id = Column(String(50), ForeignKey("hse.audit_findings.finding_id"))
    car_type = Column(String(20))  # corrective | preventive
    description = Column(Text, nullable=False)
    root_cause = Column(Text)
    proposed_action = Column(Text)
    pic = Column(String(200))
    due_date = Column(Date)
    completion_date = Column(Date)
    status = Column(String(20), default="open")
    effectiveness_check = Column(Text)
    verified_by = Column(String(200))
    verified_at = Column(DateTime)
    created_by = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


Index("idx_audit_findings_audit", AuditFinding.audit_id)
Index("idx_audit_plans_site", AuditPlan.site_id)
Index("idx_audit_trail_user", AuditTrail.user_id, AuditTrail.created_at)
Index("idx_evidence_finding", Evidence.finding_id)
Index("idx_car_finding", CorrectiveAction.finding_id)
