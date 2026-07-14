"""
SQLAlchemy Models for HSE Operations (Operational Transaction Tables).
These tables support the full operational HSE workflow.
"""

from sqlalchemy import (
    Column, String, Date, DateTime, Boolean, Numeric, Text, Integer,
    ForeignKey, Index, UniqueConstraint, CheckConstraint, JSON
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class OperationalAttachment(Base):
    """Shared attachments table for all operational modules."""
    __tablename__ = "operational_attachments"
    __table_args__ = {"schema": "hse"}

    attachment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module = Column(String(50), nullable=False)
    record_id = Column(String(100), nullable=False)
    file_name = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_type = Column(String(100))
    file_size = Column(Integer)
    mime_type = Column(String(100))
    description = Column(Text)
    uploaded_by = Column(String(200))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    is_public = Column(Boolean, default=False)
    tags = Column(JSON)
    checksum = Column(String(64))
    metadata_ = Column("metadata", JSONB)
    is_deleted = Column(Boolean, default=False)


class WorkflowHistory(Base):
    """Workflow transition history for all operational modules."""
    __tablename__ = "workflow_history"
    __table_args__ = {"schema": "hse"}

    transition_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module = Column(String(50), nullable=False)
    record_id = Column(String(100), nullable=False)
    from_status = Column(String(50))
    to_status = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    remarks = Column(Text)
    performed_by = Column(String(200), nullable=False)
    performed_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    metadata_ = Column("metadata", JSONB)


class IncidentReport(Base):
    """Operational incident reports."""
    __tablename__ = "incident_reports"
    __table_args__ = {"schema": "hse"}

    report_id = Column(String(50), primary_key=True)
    incident_id = Column(String(30), ForeignKey("dim_incident(incident_id)"))
    report_date = Column(Date, nullable=False, default=datetime.utcnow().date)
    report_time = Column(DateTime)
    site_id = Column(String(20), ForeignKey("hse.dim_site.site_id"), nullable=False)
    department_id = Column(String(20), ForeignKey("hse.dim_department.dept_id"))
    shift = Column(String(20))
    location = Column(String(200), nullable=False)
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    category = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)
    incident_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    immediate_action = Column(Text)
    root_cause = Column(Text)
    corrective_action = Column(Text)
    preventive_action = Column(Text)
    pic = Column(String(200))
    witness = Column(String(500))
    injured_person = Column(String(200))
    body_part = Column(String(100))
    lost_days = Column(Integer, default=0)
    restricted_days = Column(Integer, default=0)
    medical_treatment = Column(Text)
    ptw_required = Column(Boolean, default=False)
    ptw_violated = Column(Boolean, default=False)
    investigation_required = Column(Boolean, default=False)
    investigation_lead = Column(String(200))
    investigation_due = Column(Date)
    case_status = Column(String(20), default="Draft")
    workflow_stage = Column(String(50), default="Draft")
    status = Column(String(20), default="active")
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    deleted_by = Column(String(200))
    version = Column(Integer, default=1)
    attachments = Column(JSONB, default=[])
    metadata_ = Column("metadata", JSONB, default={})
    created_by = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(String(200))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PTWRequest(Base):
    """Operational Permit to Work requests."""
    __tablename__ = "ptw_requests"
    __table_args__ = {"schema": "hse"}

    request_id = Column(String(50), primary_key=True)
    ptw_id = Column(String(30), ForeignKey("dim_ptw(ptw_id)"))
    request_date = Column(Date, nullable=False, default=datetime.utcnow().date)
    site_id = Column(String(20), ForeignKey("dim_site(site_id)"), nullable=False)
    department_id = Column(String(20), ForeignKey("dim_department(dept_id)"))
    ptw_type = Column(String(100), nullable=False)
    ptw_category = Column(String(50))
    workstation = Column(String(200), nullable=False)
    location = Column(String(200))
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    hazard_identified = Column(Text, nullable=False)
    mitigation_list = Column(Text)
    isolation_list = Column(Text)
    cna_required = Column(Boolean, default=False)
    gas_test_done = Column(Boolean, default=False)
    gas_test_result = Column(String(20))
    fire_watch_required = Column(Boolean, default=False)
    standby_person = Column(String(200))
    work_description = Column(Text, nullable=False)
    contractor_involved = Column(Boolean, default=False)
    contractor_name = Column(String(200))
    pic = Column(String(200), nullable=False)
    approved_by = Column(String(200))
    approved_at = Column(DateTime)
    rejection_reason = Column(Text)
    sign_in = Column(DateTime)
    sign_out = Column(DateTime)
    actual_start = Column(DateTime)
    actual_end = Column(DateTime)
    extension_count = Column(Integer, default=0)
    extension_reason = Column(Text)
    violation_count = Column(Integer, default=0)
    violation_notes = Column(Text)
    ptw_status = Column(String(20), default="Draft")
    workflow_stage = Column(String(50), default="Draft")
    status = Column(String(20), default="active")
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    deleted_by = Column(String(200))
    version = Column(Integer, default=1)
    attachments = Column(JSONB, default=[])
    metadata_ = Column("metadata", JSONB, default={})
    created_by = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(String(200))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TrainingRecord(Base):
    """Operational training records."""
    __tablename__ = "training_records"
    __table_args__ = {"schema": "hse"}

    record_id = Column(String(50), primary_key=True)
    training_id = Column(String(30), ForeignKey("dim_training(training_id)"))
    training_name = Column(String(200), nullable=False)
    training_type = Column(String(50), nullable=False)
    site_id = Column(String(20), ForeignKey("dim_site(site_id)"), nullable=False)
    department_id = Column(String(20), ForeignKey("dim_department(dept_id)"))
    trainer = Column(String(200))
    training_date = Column(Date, nullable=False)
    expiry_date = Column(Date)
    duration_hours = Column(Numeric(5, 2))
    competency_area = Column(String(100))
    certification_name = Column(String(200))
    cert_number = Column(String(100))
    result = Column(String(20), nullable=False)
    score = Column(Numeric(5, 2))
    max_score = Column(Numeric(5, 2))
    remarks = Column(Text)
    evidence_path = Column(String(1000))
    status = Column(String(20), default="active")
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    deleted_by = Column(String(200))
    version = Column(Integer, default=1)
    attachments = Column(JSONB, default=[])
    metadata_ = Column("metadata", JSONB, default={})
    created_by = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(String(200))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SafetyObservation(Base):
    """Safety observations (BBS - Behavior Based Safety)."""
    __tablename__ = "safety_observations"
    __table_args__ = {"schema": "hse"}

    observation_id = Column(String(50), primary_key=True)
    observation_date = Column(Date, nullable=False, default=datetime.utcnow().date)
    observation_time = Column(DateTime)
    site_id = Column(String(20), ForeignKey("dim_site(site_id)"), nullable=False)
    department_id = Column(String(20), ForeignKey("dim_department(dept_id)"))
    observed_by = Column(String(200), nullable=False)
    observed_person = Column(String(200))
    location = Column(String(200), nullable=False)
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    observation_type = Column(String(20), nullable=False)
    category = Column(String(100))
    description = Column(Text, nullable=False)
    immediate_action = Column(Text)
    corrective_action = Column(Text)
    pic = Column(String(200))
    due_date = Column(Date)
    closed_at = Column(DateTime)
    status = Column(String(20), default="Open")
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    deleted_by = Column(String(200))
    version = Column(Integer, default=1)
    attachments = Column(JSONB, default=[])
    metadata_ = Column("metadata", JSONB, default={})
    created_by = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(String(200))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EquipmentInspection(Base):
    """Equipment inspection records."""
    __tablename__ = "equipment_inspections"
    __table_args__ = {"schema": "hse"}

    inspection_id = Column(String(50), primary_key=True)
    equipment_id = Column(String(50), ForeignKey("dim_equipment(equipment_id)"), nullable=False)
    inspection_date = Column(Date, nullable=False, default=datetime.utcnow().date)
    inspection_type = Column(String(100), nullable=False)
    inspector = Column(String(200), nullable=False)
    site_id = Column(String(20), ForeignKey("dim_site(site_id)"), nullable=False)
    findings = Column(Text)
    defects_found = Column(Boolean, default=False)
    defect_description = Column(Text)
    corrective_action = Column(Text)
    result = Column(String(20), nullable=False)
    next_inspection = Column(Date)
    certification_expiry = Column(Date)
    status = Column(String(20), default="active")
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    deleted_by = Column(String(200))
    version = Column(Integer, default=1)
    attachments = Column(JSONB, default=[])
    metadata_ = Column("metadata", JSONB, default={})
    created_by = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(String(200))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HIRAAssessment(Base):
    """HIRA / JSA assessments."""
    __tablename__ = "hira_assessments"
    __table_args__ = {"schema": "hse"}

    assessment_id = Column(String(50), primary_key=True)
    assessment_date = Column(Date, nullable=False, default=datetime.utcnow().date)
    site_id = Column(String(20), ForeignKey("dim_site(site_id)"), nullable=False)
    department_id = Column(String(20), ForeignKey("dim_department(dept_id)"))
    activity = Column(String(200), nullable=False)
    location = Column(String(200), nullable=False)
    task_description = Column(Text, nullable=False)
    hazard_id = Column(String(20), ForeignKey("dim_hazard(hazard_id)"))
    hazard_type = Column(String(100))
    risk_rating = Column(String(20), nullable=False)
    likelihood = Column(Integer)
    severity = Column(Integer)
    risk_score = Column(Integer, nullable=False)
    control_measures = Column(Text, nullable=False)
    ppe_required = Column(Text)
    isolation_required = Column(Boolean, default=False)
    permit_required = Column(String(100))
    emergency_procedure = Column(Text)
    assessed_by = Column(String(200), nullable=False)
    reviewed_by = Column(String(200))
    reviewed_at = Column(DateTime)
    approved_by = Column(String(200))
    approved_at = Column(DateTime)
    status = Column(String(20), default="active")
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    deleted_by = Column(String(200))
    version = Column(Integer, default=1)
    attachments = Column(JSONB, default=[])
    metadata_ = Column("metadata", JSONB, default={})
    created_by = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(String(200))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NearMissReport(Base):
    """Near miss reports."""
    __tablename__ = "near_miss_reports"
    __table_args__ = {"schema": "hse"}

    report_id = Column(String(50), primary_key=True)
    report_date = Column(Date, nullable=False, default=datetime.utcnow().date)
    report_time = Column(DateTime)
    site_id = Column(String(20), ForeignKey("dim_site(site_id)"), nullable=False)
    department_id = Column(String(20), ForeignKey("dim_department(dept_id)"))
    location = Column(String(200), nullable=False)
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    immediate_action = Column(Text)
    contributing_factor = Column(Text)
    corrective_action = Column(Text)
    pic = Column(String(200))
    witness = Column(String(500))
    potential_outcome = Column(Text)
    severity_potential = Column(String(20))
    learning_point = Column(Text)
    shared_with_team = Column(Boolean, default=False)
    status = Column(String(20), default="Open")
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    deleted_by = Column(String(200))
    version = Column(Integer, default=1)
    attachments = Column(JSONB, default=[])
    metadata_ = Column("metadata", JSONB, default={})
    created_by = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(String(200))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ContractorRecord(Base):
    """Operational contractor management records."""
    __tablename__ = "contractor_records"
    __table_args__ = {"schema": "hse"}

    record_id = Column(String(50), primary_key=True)
    contractor_id = Column(String(20), ForeignKey("dim_contractor(contractor_id)"), nullable=False)
    record_date = Column(Date, nullable=False, default=datetime.utcnow().date)
    record_type = Column(String(50), nullable=False)
    site_id = Column(String(20), ForeignKey("dim_site(site_id)"), nullable=False)
    assessment_date = Column(Date)
    assessor = Column(String(200))
    score = Column(Numeric(5, 2))
    max_score = Column(Numeric(5, 2))
    result = Column(String(20))
    findings = Column(Text)
    corrective_action = Column(Text)
    follow_up_date = Column(Date)
    status = Column(String(20), default="active")
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    deleted_by = Column(String(200))
    version = Column(Integer, default=1)
    attachments = Column(JSONB, default=[])
    metadata_ = Column("metadata", JSONB, default={})
    created_by = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(String(200))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EnvironmentalReading(Base):
    """Operational environmental readings."""
    __tablename__ = "environmental_readings"
    __table_args__ = {"schema": "hse"}

    reading_id = Column(String(50), primary_key=True)
    env_id = Column(String(30), ForeignKey("dim_environmental(env_id)"))
    reading_date = Column(Date, nullable=False, default=datetime.utcnow().date)
    reading_time = Column(DateTime)
    site_id = Column(String(20), ForeignKey("dim_site(site_id)"), nullable=False)
    parameter_type = Column(String(100), nullable=False)
    parameter_name = Column(String(100), nullable=False)
    monitoring_point = Column(String(200))
    reading_value = Column(Numeric(15, 4), nullable=False)
    limit_value = Column(Numeric(15, 4))
    unit_of_measure = Column(String(20))
    exceeded = Column(Boolean, default=False)
    lab_method = Column(String(100))
    weather_condition = Column(String(100))
    equipment_used = Column(String(200))
    sampled_by = Column(String(200))
    analyzed_by = Column(String(200))
    verified_by = Column(String(200))
    verified_at = Column(DateTime)
    remarks = Column(Text)
    status = Column(String(20), default="active")
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)
    deleted_by = Column(String(200))
    version = Column(Integer, default=1)
    attachments = Column(JSONB, default=[])
    metadata_ = Column("metadata", JSONB, default={})
    created_by = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(String(200))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WorkflowStatus(Base):
    """Workflow status configuration."""
    __tablename__ = "workflow_statuses"
    __table_args__ = {"schema": "hse"}

    status_id = Column(String(50), primary_key=True)
    module = Column(String(50), nullable=False)
    status_name = Column(String(50), nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text)
    is_initial = Column(Boolean, default=False)
    is_final = Column(Boolean, default=False)
    allowed_actions = Column(JSON)
    allowed_roles = Column(JSON)
    sort_order = Column(Integer, default=0)
    color = Column(String(20), default="gray")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Indexes
Index("idx_incident_reports_site_date", IncidentReport.site_id, IncidentReport.report_date, IncidentReport.is_deleted)
Index("idx_incident_reports_status", IncidentReport.case_status, IncidentReport.is_deleted)
Index("idx_incident_reports_severity", IncidentReport.severity, IncidentReport.is_deleted)
Index("idx_ptw_requests_site_status", PTWRequest.site_id, PTWRequest.ptw_status, PTWRequest.is_deleted)
Index("idx_ptw_requests_dates", PTWRequest.start_at, PTWRequest.end_at, PTWRequest.is_deleted)
Index("idx_training_records_site_date", TrainingRecord.site_id, TrainingRecord.training_date, TrainingRecord.is_deleted)
Index("idx_safety_observations_site_date", SafetyObservation.site_id, SafetyObservation.observation_date, SafetyObservation.is_deleted)
Index("idx_equipment_inspections_equipment", EquipmentInspection.equipment_id, EquipmentInspection.inspection_date, EquipmentInspection.is_deleted)
Index("idx_hira_assessments_site_date", HIRAAssessment.site_id, HIRAAssessment.assessment_date, HIRAAssessment.is_deleted)
Index("idx_near_miss_reports_site_date", NearMissReport.site_id, NearMissReport.report_date, NearMissReport.is_deleted)
Index("idx_contractor_records_contractor", ContractorRecord.contractor_id, ContractorRecord.record_date, ContractorRecord.is_deleted)
Index("idx_environmental_readings_site_date", EnvironmentalReading.site_id, EnvironmentalReading.reading_date, EnvironmentalReading.is_deleted)
