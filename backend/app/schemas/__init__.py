"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import date, datetime
from typing import Optional, List, Dict, Any


# =============================================
# AUTH SCHEMAS
# =============================================

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_role: str
    site_access: List[str]


class TokenRefresh(BaseModel):
    refresh_token: str


class LoginRequest(BaseModel):
    username: str = Field(..., alias="email")
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_email: str
    user_name: str
    role_name: str
    site_access: List[str]
    can_export: bool
    can_edit: bool
    is_active: bool


class PermissionResponse(BaseModel):
    permission_name: str


class LoginHistoryResponse(BaseModel):
    login_id: int
    email: str
    login_type: str
    ip_address: str
    login_status: str
    created_at: datetime


# =============================================
# DASHBOARD SCHEMAS
# =============================================

class KPICard(BaseModel):
    label: str
    value: Any
    unit: str = ""
    status: str  # green, amber, red, gray
    subtext: str = ""


class ExecutiveSummary(BaseModel):
    kpis: List[KPICard]
    generated_at: datetime
    period_days: int
    site_id: Optional[str] = None


class IncidentSummary(BaseModel):
    trend: List[Dict[str, Any]]
    distribution: Dict[str, int]
    by_department: Dict[str, int]


class PTWSummary(BaseModel):
    open_count: int
    closed_count: int
    pending_count: int
    violation_count: int
    overdue_count: int
    compliance_rate: float


class TrainingSummary(BaseModel):
    total_completed: int
    total_pending: int
    total_failed: int
    compliance_rate: float
    by_department: Dict[str, Dict[str, int]]


class EnvironmentalSummary(BaseModel):
    pm25_current: Optional[float] = None
    pm25_limit: Optional[float] = None
    pm25_status: str = "gray"
    noise_current: Optional[float] = None
    noise_limit: Optional[float] = None
    noise_status: str = "gray"
    exceedances: int
    total_readings: int


class EquipmentSummary(BaseModel):
    total_equipment: int
    valid_cert: int
    expired_cert: int
    overdue_inspection: int
    down_count: int


class ContractorSummary(BaseModel):
    total_contractors: int
    active_contractors: int
    audit_passed: int
    audit_conditional: int
    audit_failed: int
    performance_scores: Dict[str, float]


class AlertItem(BaseModel):
    alert_type: str
    severity: str  # critical, warning, info
    site_id: str
    site_name: str
    message: str
    triggered_at: datetime
    acknowledged: bool = False


# =============================================
# REQUEST SCHEMAS
# =============================================

class DateRangeRequest(BaseModel):
    start_date: date
    end_date: date
    site_id: Optional[str] = None
    department_id: Optional[str] = None


class FilterRequest(BaseModel):
    site_id: Optional[str] = "all"
    department_id: Optional[str] = "all"
    period_days: int = 30
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class AlertRuleCreate(BaseModel):
    rule_name: str
    metric_type: str
    condition: str  # >, <, >=, <=, ==
    threshold: float
    severity: str
    notification_channels: List[str]
    site_id: Optional[str] = None


class IncidentCreate(BaseModel):
    incident_type: str
    incident_category: str
    severity_class: str
    agency_type: str
    incident_cause: str
    incident_location: str
    ptw_required: bool = False
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None


class PTWCreate(BaseModel):
    ptw_type: str
    ptw_category: str
    site_id: str
    workstation: str
    start_at: datetime
    end_at: datetime
    hazard_identified: str
    mitigation_list: str
    isolation_list: str
    cna_required: bool = False


# =============================================
# AUDIT SCHEMAS
# =============================================

class AuditPlanCreate(BaseModel):
    audit_type: str
    audit_title: str
    standard_ref: Optional[str] = None
    site_id: Optional[str] = None
    department_id: Optional[str] = None
    lead_auditor: Optional[str] = None
    audit_team: Optional[List[str]] = None
    scope: Optional[str] = None
    criteria: Optional[str] = None
    scheduled_start: Optional[date] = None
    scheduled_end: Optional[date] = None


class AuditPlanUpdate(BaseModel):
    audit_status: Optional[str] = None
    audit_title: Optional[str] = None
    lead_auditor: Optional[str] = None
    audit_team: Optional[List[str]] = None
    scope: Optional[str] = None
    criteria: Optional[str] = None
    actual_start: Optional[date] = None
    actual_end: Optional[date] = None
    findings_count: Optional[int] = None
    major_findings: Optional[int] = None
    minor_findings: Optional[int] = None
    observations: Optional[int] = None
    compliance_score: Optional[float] = None
    audit_report: Optional[str] = None


class AuditPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    audit_id: str
    audit_type: str
    audit_status: str
    audit_title: str
    standard_ref: Optional[str] = None
    site_id: Optional[str] = None
    department_id: Optional[str] = None
    lead_auditor: Optional[str] = None
    audit_team: Optional[List[str]] = None
    scope: Optional[str] = None
    criteria: Optional[str] = None
    scheduled_start: Optional[date] = None
    scheduled_end: Optional[date] = None
    actual_start: Optional[date] = None
    actual_end: Optional[date] = None
    findings_count: int = 0
    major_findings: int = 0
    minor_findings: int = 0
    observations: int = 0
    compliance_score: Optional[float] = None
    audit_report: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AuditFindingCreate(BaseModel):
    audit_id: str
    finding_type: str
    clause_ref: Optional[str] = None
    description: str
    objective_evidence: Optional[str] = None
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None
    pic: Optional[str] = None
    due_date: Optional[date] = None
    severity_score: Optional[int] = None


class AuditFindingUpdate(BaseModel):
    finding_status: Optional[str] = None
    description: Optional[str] = None
    objective_evidence: Optional[str] = None
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None
    pic: Optional[str] = None
    due_date: Optional[date] = None
    closed_date: Optional[date] = None
    severity_score: Optional[int] = None


class AuditFindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    finding_id: str
    audit_id: str
    finding_type: str
    finding_status: str
    clause_ref: Optional[str] = None
    description: str
    objective_evidence: Optional[str] = None
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None
    pic: Optional[str] = None
    due_date: Optional[date] = None
    closed_date: Optional[date] = None
    severity_score: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class EvidenceUploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    evidence_id: str
    finding_id: Optional[str] = None
    incident_id: Optional[str] = None
    ptw_id: Optional[str] = None
    training_id: Optional[str] = None
    evidence_type: str
    file_name: str
    file_path: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    description: Optional[str] = None
    captured_by: Optional[str] = None
    captured_at: Optional[datetime] = None
    uploaded_by: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    is_public: bool = False
    tags: Optional[List[str]] = None
    checksum: Optional[str] = None


class AuditTrailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    trail_id: str
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    action: str
    table_name: str
    record_id: str
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    created_at: Optional[datetime] = None


class CorrectiveActionCreate(BaseModel):
    finding_id: str
    car_type: str  # corrective | preventive
    description: str
    root_cause: Optional[str] = None
    proposed_action: Optional[str] = None
    pic: Optional[str] = None
    due_date: Optional[date] = None


class CorrectiveActionUpdate(BaseModel):
    car_type: Optional[str] = None
    description: Optional[str] = None
    root_cause: Optional[str] = None
    proposed_action: Optional[str] = None
    status: Optional[str] = None
    completion_date: Optional[date] = None
    effectiveness_check: Optional[str] = None
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None


class CorrectiveActionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    car_id: str
    finding_id: str
    car_type: str
    description: str
    root_cause: Optional[str] = None
    proposed_action: Optional[str] = None
    pic: Optional[str] = None
    due_date: Optional[date] = None
    completion_date: Optional[date] = None
    status: str = "open"
    effectiveness_check: Optional[str] = None
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# =============================================
# ALERT SCHEMAS
# =============================================

class AlertRuleCreate(BaseModel):
    rule_name: str
    metric_type: str
    condition: str  # >, <, >=, <=, ==, !=
    threshold_value: float
    severity: str = "warning"
    site_id: Optional[str] = None
    department_id: Optional[str] = None
    notification_channels: List[str] = ["dashboard"]
    recipients: List[str] = []
    cooldown_minutes: int = 60
    description: Optional[str] = None


class AlertRuleUpdate(BaseModel):
    rule_name: Optional[str] = None
    condition: Optional[str] = None
    threshold_value: Optional[float] = None
    severity: Optional[str] = None
    is_active: Optional[bool] = None
    notification_channels: Optional[List[str]] = None
    recipients: Optional[List[str]] = None
    cooldown_minutes: Optional[int] = None
    description: Optional[str] = None


class AlertRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    rule_id: str
    rule_name: str
    metric_type: str
    condition: str
    threshold_value: float
    severity: str
    site_id: Optional[str] = None
    department_id: Optional[str] = None
    notification_channels: List[str]
    recipients: List[str]
    is_active: bool
    cooldown_minutes: int
    last_triggered_at: Optional[datetime] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    alert_id: str
    rule_id: Optional[str] = None
    alert_type: str
    severity: str
    status: str
    site_id: Optional[str] = None
    site_name: Optional[str] = None
    metric_type: Optional[str] = None
    metric_value: Optional[float] = None
    threshold_value: Optional[float] = None
    message: str
    details: Optional[Dict[str, Any]] = None
    triggered_by: Optional[str] = None
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    alert_date: Optional[date] = None
    created_at: Optional[datetime] = None


class NotificationLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    log_id: str
    alert_id: Optional[str] = None
    channel: str
    recipient: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    retry_count: int = 0
    created_at: Optional[datetime] = None


# =============================================
# REPORT SCHEMAS
# =============================================

class ReportRequest(BaseModel):
    report_type: str = Field(..., description="Report type: executive, incident, ptw, training, environmental, equipment, contractor, audit")
    start_date: date
    end_date: date
    site_id: Optional[str] = "all"
    department_id: Optional[str] = "all"
    format: str = Field("csv", description="Export format: csv, json, markdown")
    include_charts: bool = False


class ReportResponse(BaseModel):
    report_type: str
    format: str
    file_name: str
    generated_at: datetime
    record_count: int
    download_url: str


class ExportRequest(BaseModel):
    data_type: str = Field(..., description="Data type: incidents, ptw, training, environmental, equipment, audit, alerts")
    start_date: date
    end_date: date
    site_id: Optional[str] = "all"
    department_id: Optional[str] = "all"
    format: str = Field("csv", description="Export format: csv, json")
    columns: Optional[List[str]] = None


# =============================================
# DATA QUALITY SCHEMAS
# =============================================

class DataQualityCheckResponse(BaseModel):
    check_name: str
    status: str  # pass, fail, warning
    record_count: int
    details: Optional[str] = None


class DataQualityReport(BaseModel):
    generated_at: datetime
    database_status: str
    checks: List[DataQualityCheckResponse]
    total_records: int
    last_updated: Optional[str] = None


class DataValidationRequest(BaseModel):
    table_name: str
    date_key: Optional[date] = None
    site_id: Optional[str] = None
    validation_type: str = "completeness"  # completeness, consistency, validity


# =============================================
# HEALTH CHECK
# =============================================

class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    redis: Optional[str] = None
    timestamp: datetime


# =============================================
# AI SAFETY ASSISTANT SCHEMAS
# =============================================

class AIDocumentResponse(BaseModel):
    document_id: str
    title: str
    description: Optional[str] = None
    document_type: str
    source_system: Optional[str] = None
    source_id: Optional[str] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    page_count: Optional[int] = None
    language: str = "id"
    metadata_: Optional[Dict[str, Any]] = None
    is_active: bool = True
    created_at: datetime
    indexed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AIDocumentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    document_type: str
    source_system: Optional[str] = None
    source_id: Optional[str] = None
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    mime_type: Optional[str] = None
    page_count: Optional[int] = None
    language: str = "id"
    metadata_: Optional[Dict[str, Any]] = None
    is_active: bool = True


class AIDocumentChunkResponse(BaseModel):
    chunk_id: str
    document_id: str
    chunk_index: int
    text: str
    tokens: Optional[int] = None
    metadata_: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIChatRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None
    context_type: Optional[str] = None  # general, incident, audit, ptw, site
    context_id: Optional[str] = None
    max_sources: int = 5
    include_history: bool = True


class AISource(BaseModel):
    document_id: str
    title: str
    document_type: str
    chunk_index: int
    text: str
    relevance_score: float


class AIChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    answer: str
    sources: List[AISource]
    confidence: float
    suggested_actions: List[str] = []


class AIConversationResponse(BaseModel):
    conversation_id: str
    user_id: Optional[int] = None
    title: Optional[str] = None
    context_type: Optional[str] = None
    context_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    messages: List[Dict[str, Any]] = []

    model_config = ConfigDict(from_attributes=True)


class AIRiskScoreResponse(BaseModel):
    site_id: str
    site_name: str
    overall_score: float  # 0-100
    risk_level: str  # low, medium, high, critical
    factors: Dict[str, Any]
    recommendations: List[str]
    calculated_at: datetime


class AIComplianceGap(BaseModel):
    standard: str  # ISO 45001, ISO 14001, SMKP Minerba, SMK3
    clause: str
    description: str
    gap_count: int
    evidence_count: int
    severity: str  # low, medium, high
    recommendations: List[str]


class AIComplianceResponse(BaseModel):
    site_id: Optional[str] = None
    overall_score: float
    risk_level: str
    gaps: List[AIComplianceGap]
    last_audit_date: Optional[datetime] = None
    next_audit_due: Optional[datetime] = None


class ComplianceGapDetail(BaseModel):
    standard: str
    clause: str
    description: str
    gap_count: int
    evidence_count: int
    missing_evidence: List[str] = []
    severity: str
    recommendations: List[str]


class EnhancedComplianceResponse(BaseModel):
    site_id: Optional[str] = None
    overall_score: float
    risk_level: str
    standards: List[ComplianceGapDetail]
    biggest_gap: Optional[ComplianceGapDetail] = None
    last_audit_date: Optional[datetime] = None
    next_audit_due: Optional[datetime] = None


class PriorityTodayItem(BaseModel):
    category: str
    priority: str
    title: str
    description: str
    count: int = 1
    action: str


class PriorityTodayResponse(BaseModel):
    date: date
    site_id: Optional[str] = None
    risk_score: float
    risk_level: str
    total_critical: int
    total_high: int
    items: List[PriorityTodayItem]
    recommended_action: str


class PredictiveForecastPoint(BaseModel):
    date: date
    predicted_value: float
    lower_bound: float
    upper_bound: float
    confidence: float


class PredictiveSafetyResponse(BaseModel):
    site_id: str
    site_name: str
    metric: str
    current_value: float
    forecast: List[PredictiveForecastPoint]
    trend: str
    risk_level: str
    recommendation: str
    generated_at: datetime


# =============================================
# HSE OPERATIONS SCHEMAS
# =============================================

class OperationalAttachmentResponse(BaseModel):
    attachment_id: str
    module: str
    record_id: str
    file_name: str
    file_path: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    description: Optional[str] = None
    uploaded_by: Optional[str] = None
    uploaded_at: datetime
    is_public: bool = False
    tags: Optional[List[str]] = None
    checksum: Optional[str] = None
    metadata_: Optional[Dict[str, Any]] = None
    is_deleted: bool = False

    model_config = ConfigDict(from_attributes=True)


class WorkflowHistoryResponse(BaseModel):
    transition_id: str
    module: str
    record_id: str
    from_status: Optional[str] = None
    to_status: str
    action: str
    remarks: Optional[str] = None
    performed_by: str
    performed_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata_: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class IncidentReportCreate(BaseModel):
    report_date: date
    report_time: Optional[datetime] = None
    site_id: str
    department_id: Optional[str] = None
    shift: Optional[str] = None
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category: str
    severity: str
    incident_type: str
    description: str
    immediate_action: Optional[str] = None
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None
    pic: Optional[str] = None
    witness: Optional[str] = None
    injured_person: Optional[str] = None
    body_part: Optional[str] = None
    lost_days: int = 0
    restricted_days: int = 0
    medical_treatment: Optional[str] = None
    ptw_required: bool = False
    ptw_violated: bool = False
    investigation_required: bool = False
    investigation_lead: Optional[str] = None
    investigation_due: Optional[date] = None
    case_status: str = "Draft"
    attachments: List[str] = []
    metadata_: Optional[Dict[str, Any]] = None


class IncidentReportUpdate(BaseModel):
    report_date: Optional[date] = None
    report_time: Optional[datetime] = None
    site_id: Optional[str] = None
    department_id: Optional[str] = None
    shift: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category: Optional[str] = None
    severity: Optional[str] = None
    incident_type: Optional[str] = None
    description: Optional[str] = None
    immediate_action: Optional[str] = None
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None
    pic: Optional[str] = None
    witness: Optional[str] = None
    injured_person: Optional[str] = None
    body_part: Optional[str] = None
    lost_days: Optional[int] = None
    restricted_days: Optional[int] = None
    medical_treatment: Optional[str] = None
    ptw_required: Optional[bool] = None
    ptw_violated: Optional[bool] = None
    investigation_required: Optional[bool] = None
    investigation_lead: Optional[str] = None
    investigation_due: Optional[date] = None
    case_status: Optional[str] = None
    attachments: Optional[List[str]] = None
    metadata_: Optional[Dict[str, Any]] = None


class IncidentReportResponse(BaseModel):
    report_id: str
    incident_id: Optional[str] = None
    report_date: date
    report_time: Optional[datetime] = None
    site_id: str
    department_id: Optional[str] = None
    shift: Optional[str] = None
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category: str
    severity: str
    incident_type: str
    description: str
    immediate_action: Optional[str] = None
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None
    pic: Optional[str] = None
    witness: Optional[str] = None
    injured_person: Optional[str] = None
    body_part: Optional[str] = None
    lost_days: int = 0
    restricted_days: int = 0
    medical_treatment: Optional[str] = None
    ptw_required: bool = False
    ptw_violated: bool = False
    investigation_required: bool = False
    investigation_lead: Optional[str] = None
    investigation_due: Optional[date] = None
    case_status: str
    workflow_stage: str
    status: str
    is_deleted: bool = False
    version: int = 1
    attachments: List[Any] = []
    metadata_: Optional[Dict[str, Any]] = None
    created_by: str
    created_at: datetime
    updated_by: Optional[str] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IncidentDashboardResponse(BaseModel):
    total_reports: int
    by_severity: Dict[str, int]
    by_status: Dict[str, int]
    by_category: Dict[str, int]
    by_site: Dict[str, int]
    open_investigations: int
    overdue_investigations: int
    total_lost_days: int
    total_restricted_days: int
    trend: List[Dict[str, Any]]
    period_start: date
    period_end: date


class PTWRequestCreate(BaseModel):
    request_date: date
    site_id: str
    department_id: Optional[str] = None
    ptw_type: str
    ptw_category: Optional[str] = None
    workstation: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    start_at: datetime
    end_at: datetime
    hazard_identified: str
    mitigation_list: Optional[str] = None
    isolation_list: Optional[str] = None
    cna_required: bool = False
    gas_test_done: bool = False
    gas_test_result: Optional[str] = None
    fire_watch_required: bool = False
    standby_person: Optional[str] = None
    work_description: str
    contractor_involved: bool = False
    contractor_name: Optional[str] = None
    pic: str
    ptw_status: str = "Draft"
    attachments: List[str] = []
    metadata_: Optional[Dict[str, Any]] = None


class PTWRequestUpdate(BaseModel):
    request_date: Optional[date] = None
    site_id: Optional[str] = None
    department_id: Optional[str] = None
    ptw_type: Optional[str] = None
    ptw_category: Optional[str] = None
    workstation: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    hazard_identified: Optional[str] = None
    mitigation_list: Optional[str] = None
    isolation_list: Optional[str] = None
    cna_required: Optional[bool] = None
    gas_test_done: Optional[bool] = None
    gas_test_result: Optional[str] = None
    fire_watch_required: Optional[bool] = None
    standby_person: Optional[str] = None
    work_description: Optional[str] = None
    contractor_involved: Optional[bool] = None
    contractor_name: Optional[str] = None
    pic: Optional[str] = None
    ptw_status: Optional[str] = None
    approved_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    attachments: Optional[List[str]] = None
    metadata_: Optional[Dict[str, Any]] = None


class PTWRequestResponse(BaseModel):
    request_id: str
    ptw_id: Optional[str] = None
    request_date: date
    site_id: str
    department_id: Optional[str] = None
    ptw_type: str
    ptw_category: Optional[str] = None
    workstation: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    start_at: datetime
    end_at: datetime
    hazard_identified: str
    mitigation_list: Optional[str] = None
    isolation_list: Optional[str] = None
    cna_required: bool = False
    gas_test_done: bool = False
    gas_test_result: Optional[str] = None
    fire_watch_required: bool = False
    standby_person: Optional[str] = None
    work_description: str
    contractor_involved: bool = False
    contractor_name: Optional[str] = None
    pic: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    sign_in: Optional[datetime] = None
    sign_out: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    extension_count: int = 0
    extension_reason: Optional[str] = None
    violation_count: int = 0
    violation_notes: Optional[str] = None
    ptw_status: str
    workflow_stage: str
    status: str
    is_deleted: bool = False
    version: int = 1
    attachments: List[Any] = []
    metadata_: Optional[Dict[str, Any]] = None
    created_by: str
    created_at: datetime
    updated_by: Optional[str] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TrainingRecordCreate(BaseModel):
    training_id: Optional[str] = None
    training_name: str
    training_type: str
    site_id: str
    department_id: Optional[str] = None
    trainer: Optional[str] = None
    training_date: date
    expiry_date: Optional[date] = None
    duration_hours: Optional[float] = None
    competency_area: Optional[str] = None
    certification_name: Optional[str] = None
    cert_number: Optional[str] = None
    result: str
    score: Optional[float] = None
    max_score: Optional[float] = None
    remarks: Optional[str] = None
    evidence_path: Optional[str] = None
    attachments: List[str] = []
    metadata_: Optional[Dict[str, Any]] = None


class TrainingRecordUpdate(BaseModel):
    training_id: Optional[str] = None
    training_name: Optional[str] = None
    training_type: Optional[str] = None
    site_id: Optional[str] = None
    department_id: Optional[str] = None
    trainer: Optional[str] = None
    training_date: Optional[date] = None
    expiry_date: Optional[date] = None
    duration_hours: Optional[float] = None
    competency_area: Optional[str] = None
    certification_name: Optional[str] = None
    cert_number: Optional[str] = None
    result: Optional[str] = None
    score: Optional[float] = None
    max_score: Optional[float] = None
    remarks: Optional[str] = None
    evidence_path: Optional[str] = None
    attachments: Optional[List[str]] = None
    metadata_: Optional[Dict[str, Any]] = None


class TrainingRecordResponse(BaseModel):
    record_id: str
    training_id: Optional[str] = None
    training_name: str
    training_type: str
    site_id: str
    department_id: Optional[str] = None
    trainer: Optional[str] = None
    training_date: date
    expiry_date: Optional[date] = None
    duration_hours: Optional[float] = None
    competency_area: Optional[str] = None
    certification_name: Optional[str] = None
    cert_number: Optional[str] = None
    result: str
    score: Optional[float] = None
    max_score: Optional[float] = None
    remarks: Optional[str] = None
    evidence_path: Optional[str] = None
    status: str
    is_deleted: bool = False
    version: int = 1
    attachments: List[Any] = []
    metadata_: Optional[Dict[str, Any]] = None
    created_by: str
    created_at: datetime
    updated_by: Optional[str] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OperationalListResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    filters: Dict[str, Any] = {}
    sort_by: Optional[str] = None
    sort_order: str = "asc"
