"""
FastAPI controllers (API routes).
Each file handles a specific domain.
"""

from datetime import date, datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.rbac import get_current_user, require_permission
from app.config import settings
from app.schemas import (
    ExecutiveSummary, IncidentSummary, PTWSummary, TrainingSummary,
    EnvironmentalSummary, EquipmentSummary, ContractorSummary,
    AlertItem, Token, LoginRequest, HealthResponse, FilterRequest,
    UserResponse, PermissionResponse,
    AuditPlanCreate, AuditPlanUpdate, AuditPlanResponse,
    AuditFindingCreate, AuditFindingUpdate, AuditFindingResponse,
    EvidenceUploadResponse, AuditTrailResponse,
    CorrectiveActionCreate, CorrectiveActionUpdate, CorrectiveActionResponse,
    AlertRuleCreate, AlertRuleUpdate, AlertRuleResponse,
    AlertResponse, NotificationLogResponse,
    ReportRequest, ReportResponse, ExportRequest,
    DataQualityCheckResponse, DataQualityReport, DataValidationRequest,
    AIDocumentResponse, AIDocumentCreate, AIChatRequest, AIChatResponse,
    AIConversationResponse, AIRiskScoreResponse, AIComplianceResponse,
    PriorityTodayResponse, PredictiveSafetyResponse, PredictiveForecastPoint,
    EnhancedComplianceResponse, ComplianceGapDetail, PriorityTodayItem
)
from app.services import DashboardService, AuthService, AuditService, AlertService, ReportingService, DataQualityService, AIService
from app.services.operational import (
    IncidentService, PTWService, TrainingService,
    ObservationService, NearMissService
)
from app.repositories import AuthRepository
from app.controllers import operational as operational_controller

router = APIRouter()


# =============================================
# HEALTH CHECK
# =============================================

@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint for monitoring."""
    from app.database import check_database_connection
    from app.config import settings

    db_status = check_database_connection()

    return HealthResponse(
        status="healthy" if db_status["status"] == "healthy" else "degraded",
        version=settings.APP_VERSION,
        database=db_status["status"],
        timestamp=datetime.utcnow(),
    )


@router.get("/ready", tags=["Health"])
async def readiness_check():
    """Readiness check for Kubernetes/Docker."""
    return {"status": "ready"}


@router.get("/live", tags=["Health"])
async def liveness_check():
    """Liveness check for Kubernetes/Docker."""
    return {"status": "alive"}


# =============================================
# AUTHENTICATION
# =============================================

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@auth_router.post("/login", response_model=Token, tags=["Authentication"])
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login endpoint with RBAC.
    Returns JWT access token and refresh token with permissions.
    """
    auth_service = AuthService(db)
    user_data = auth_service.authenticate(
        email=form_data.username,
        password=form_data.password,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials or account disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(
        access_token=user_data["access_token"],
        refresh_token=user_data["refresh_token"],
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_role=user_data["role"],
        site_access=user_data["site_access"],
    )


@auth_router.post("/refresh", response_model=Token, tags=["Authentication"])
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    from app.utils.security import decode_token, create_access_token

    try:
        payload = decode_token(refresh_token)
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        auth_service = AuthService(db)
        user = auth_service.authenticate(email, "")
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        access_token = create_access_token(
            data={"sub": user["email"], "role": user["role"], "site_access": user["site_access"]}
        )

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_role=user["role"],
            site_access=user["site_access"],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@auth_router.post("/logout", tags=["Authentication"])
async def logout(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout current user by invalidating session."""
    auth_service = AuthService(db)
    auth_service.logout(current_user["user_id"], current_user.get("session_id"))
    return {"message": "Logged out successfully"}


@auth_router.post("/logout-all", tags=["Authentication"])
async def logout_all(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout all sessions for current user."""
    auth_service = AuthService(db)
    count = auth_service.logout_all(current_user["user_id"])
    return {"message": f"Logged out from {count} sessions"}


@auth_router.get("/me", response_model=UserResponse, tags=["Authentication"])
async def get_current_user_info(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user information with permissions."""
    auth_service = AuthService(db)
    permissions = auth_service.get_user_permissions(current_user["user_id"])
    site_access = auth_service.get_user_site_access(current_user["user_id"])

    return UserResponse(
        user_email=current_user["email"],
        user_name=current_user["full_name"],
        role_name=current_user["role"],
        site_access=site_access,
        can_export="dashboard:export" in permissions,
        can_edit="dashboard:edit" in permissions,
        is_active=True,
    )


@auth_router.get("/permissions", response_model=List[PermissionResponse], tags=["Authentication"])
async def get_user_permissions(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all permissions for current user."""
    auth_service = AuthService(db)
    permissions = auth_service.get_user_permissions(current_user["user_id"])

    return [PermissionResponse(permission_name=p) for p in permissions]


@auth_router.get("/menu", tags=["Authentication"])
async def get_dynamic_menu(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dynamic menu based on user permissions.
    Frontend uses this to render menu items.
    """
    auth_service = AuthService(db)
    permissions = auth_service.get_user_permissions(current_user["user_id"])

    # Define menu structure with required permissions
    menu_structure = [
        {
            "id": "dashboard",
            "label": "Dashboard",
            "icon": "📊",
            "permission": "dashboard:view",
            "children": []
        },
        {
            "id": "incident",
            "label": "Incident",
            "icon": "🚨",
            "permission": "incident:view",
            "children": [
                {"id": "incident-list", "label": "Incident Register", "permission": "incident:view"},
                {"id": "incident-create", "label": "Report Incident", "permission": "incident:create"},
                {"id": "incident-investigate", "label": "Investigation", "permission": "incident:investigate"},
            ]
        },
        {
            "id": "ptw",
            "label": "PTW",
            "icon": "📋",
            "permission": "ptw:view",
            "children": [
                {"id": "ptw-list", "label": "PTW Register", "permission": "ptw:view"},
                {"id": "ptw-create", "label": "Create PTW", "permission": "ptw:create"},
                {"id": "ptw-approve", "label": "Approve PTW", "permission": "ptw:approve"},
            ]
        },
        {
            "id": "training",
            "label": "Training",
            "icon": "🎓",
            "permission": "training:view",
            "children": [
                {"id": "training-list", "label": "Training Records", "permission": "training:view"},
                {"id": "training-create", "label": "Create Training", "permission": "training:create"},
                {"id": "training-certify", "label": "Certification", "permission": "training:certify"},
            ]
        },
        {
            "id": "environmental",
            "label": "Environmental",
            "icon": "🌿",
            "permission": "environmental:view",
            "children": [
                {"id": "env-monitoring", "label": "Monitoring", "permission": "environmental:view"},
                {"id": "env-input", "label": "Input Data", "permission": "environmental:input"},
                {"id": "env-export", "label": "Export Report", "permission": "environmental:export"},
            ]
        },
        {
            "id": "equipment",
            "label": "Equipment",
            "icon": "🔧",
            "permission": "equipment:view",
            "children": [
                {"id": "equip-list", "label": "Equipment List", "permission": "equipment:view"},
                {"id": "equip-inspect", "label": "Inspection", "permission": "equipment:inspect"},
                {"id": "equip-certify", "label": "Certification", "permission": "equipment:certify"},
            ]
        },
        {
            "id": "audit",
            "label": "Audit",
            "icon": "📋",
            "permission": "audit:view",
            "children": [
                {"id": "audit-findings", "label": "Findings", "permission": "audit:view"},
                {"id": "audit-evidence", "label": "Evidence", "permission": "audit:evidence"},
                {"id": "audit-close", "label": "Close Audit", "permission": "audit:close"},
            ]
        },
        {
            "id": "admin",
            "label": "Administration",
            "icon": "⚙️",
            "permission": "user:view",
            "children": [
                {"id": "user-management", "label": "User Management", "permission": "user:view"},
                {"id": "role-management", "label": "Role Management", "permission": "user:assign_role"},
                {"id": "system-config", "label": "System Config", "permission": "system:config"},
            ]
        },
    ]

    # Filter menu based on permissions
    def has_access(menu_item):
        if not menu_item.get("permission"):
            return True
        return auth_service.has_permission(permissions, menu_item["permission"])

    def filter_menu(items):
        result = []
        for item in items:
            if has_access(item):
                filtered_item = {k: v for k, v in item.items() if k != "children" or k == "children"}
                if "children" in item:
                    filtered_item["children"] = filter_menu(item["children"])
                result.append(filtered_item)
        return result

    filtered_menu = filter_menu(menu_structure)

    return {
        "menu": filtered_menu,
        "permissions": permissions,
        "user": {
            "id": current_user["user_id"],
            "email": current_user["email"],
            "name": current_user["full_name"],
            "role": current_user["role"],
            "site_access": current_user["site_access"],
        }
    }


router.include_router(auth_router)


# =============================================
# DASHBOARD API
# =============================================

dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@dashboard_router.get("/summary", response_model=ExecutiveSummary, tags=["Dashboard"])
async def get_executive_summary(
    site_id: Optional[str] = Query(None, description="Filter by site ID (default: all)"),
    period_days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get executive summary with KPI cards.
    Returns calculated KPIs with red/amber/green status.
    """
    service = DashboardService(db)
    return service.get_executive_summary(site_id=site_id, period_days=period_days)


@dashboard_router.get("/incidents", response_model=IncidentSummary, tags=["Dashboard"])
async def get_incident_summary(
    site_id: Optional[str] = Query(None),
    period_days: int = Query(30, ge=1, le=365),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get incident analysis with trend and distribution."""
    service = DashboardService(db)
    data = service.get_incident_summary(site_id=site_id, period_days=period_days)
    return IncidentSummary(**data)


@dashboard_router.get("/ptw", response_model=PTWSummary, tags=["Dashboard"])
async def get_ptw_summary(
    site_id: Optional[str] = Query(None),
    period_days: int = Query(30, ge=1, le=365),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get PTW (Permit to Work) summary."""
    service = DashboardService(db)
    return service.get_ptw_summary(site_id=site_id, period_days=period_days)


@dashboard_router.get("/training", response_model=TrainingSummary, tags=["Dashboard"])
async def get_training_summary(
    site_id: Optional[str] = Query(None),
    period_days: int = Query(30, ge=1, le=365),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get training compliance summary."""
    service = DashboardService(db)
    return service.get_training_summary(site_id=site_id, period_days=period_days)


@dashboard_router.get("/environmental", response_model=EnvironmentalSummary, tags=["Dashboard"])
async def get_environmental_summary(
    site_id: Optional[str] = Query(None),
    period_days: int = Query(30, ge=1, le=365),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get environmental monitoring summary."""
    service = DashboardService(db)
    return service.get_environmental_summary(site_id=site_id, period_days=period_days)


@dashboard_router.get("/equipment", response_model=EquipmentSummary, tags=["Dashboard"])
async def get_equipment_summary(
    site_id: Optional[str] = Query(None),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get equipment safety compliance summary."""
    service = DashboardService(db)
    return service.get_equipment_summary(site_id=site_id)


@dashboard_router.get("/contractor", response_model=ContractorSummary, tags=["Dashboard"])
async def get_contractor_summary(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get contractor performance summary."""
    service = DashboardService(db)
    return service.get_contractor_summary()


@dashboard_router.get("/alerts", response_model=List[AlertItem], tags=["Dashboard"])
async def get_active_alerts(
    site_id: Optional[str] = Query(None),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get active alerts for dashboard."""
    service = DashboardService(db)
    return service.get_alerts(site_id=site_id)


router.include_router(dashboard_router)


# =============================================
# ADMIN
# =============================================

admin_router = APIRouter(prefix="/admin", tags=["Administration"])


@admin_router.post("/refresh-materialized-views", tags=["Administration"])
async def refresh_views(db: Session = Depends(get_db)):
    """Refresh materialized views (for production use)."""
    try:
        views = [
            "v_daily_hse_summary",
            "v_ptw_current_status",
            "v_env_realtime",
            "v_equipment_compliance",
            "v_active_alerts",
        ]
        for view in views:
            db.execute(f"CREATE OR REPLACE VIEW hse.{view} AS SELECT * FROM hse.{view}")
        db.commit()
        return {"status": "success", "views_refreshed": len(views)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@admin_router.get("/data-quality", tags=["Administration"])
async def data_quality_report(db: Session = Depends(get_db)):
    """Generate data quality report."""
    checks = {
        "fact_hse_count": db.execute("SELECT COUNT(*) FROM hse.fact_hse").scalar(),
        "fact_hse_null_hours": db.execute("SELECT COUNT(*) FROM hse.fact_hse WHERE man_hours_worked IS NULL").scalar(),
        "fact_hse_future_dates": db.execute(
            "SELECT COUNT(*) FROM hse.fact_hse WHERE date_key > CURRENT_DATE"
        ).scalar(),
        "active_alerts": db.execute("SELECT COUNT(*) FROM hse.v_active_alerts").scalar(),
        "last_updated": db.execute("SELECT MAX(updated_at) FROM hse.fact_hse").scalar(),
    }
    return checks


router.include_router(admin_router)


# =============================================
# AUDIT TRAIL & EVIDENCE MANAGEMENT
# =============================================

audit_router = APIRouter(prefix="/audit", tags=["Audit"])


@audit_router.get("/plans", response_model=List[AuditPlanResponse], tags=["Audit"])
async def get_audit_plans(
    site_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all audit plans with optional filtering."""
    service = AuditService(db)
    plans = service.get_audit_plans(site_id=site_id, status=status)
    return [AuditPlanResponse(**p) for p in plans]


@audit_router.post("/plans", response_model=AuditPlanResponse, tags=["Audit"])
async def create_audit_plan(
    data: AuditPlanCreate,
    current_user: Dict = Depends(require_permission("audit:create")),
    db: Session = Depends(get_db)
):
    """Create a new audit plan."""
    service = AuditService(db)
    plan = service.create_audit_plan({**data.model_dump(), "created_by": current_user["email"]})
    return AuditPlanResponse(**plan)


@audit_router.get("/plans/{audit_id}", response_model=AuditPlanResponse, tags=["Audit"])
async def get_audit_plan(
    audit_id: str,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific audit plan by ID."""
    service = AuditService(db)
    plan = service.get_audit_plan(audit_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Audit plan not found")
    return AuditPlanResponse(**plan)


@audit_router.put("/plans/{audit_id}", response_model=AuditPlanResponse, tags=["Audit"])
async def update_audit_plan(
    audit_id: str,
    data: AuditPlanUpdate,
    current_user: Dict = Depends(require_permission("audit:edit")),
    db: Session = Depends(get_db)
):
    """Update an existing audit plan."""
    service = AuditService(db)
    plan = service.update_audit_plan(audit_id, data.model_dump(exclude_none=True))
    if not plan:
        raise HTTPException(status_code=404, detail="Audit plan not found")
    return AuditPlanResponse(**plan)


@audit_router.get("/findings", response_model=List[AuditFindingResponse], tags=["Audit"])
async def get_audit_findings(
    audit_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get audit findings with optional filtering."""
    service = AuditService(db)
    findings = service.get_findings(audit_id=audit_id, status=status)
    return [AuditFindingResponse(**f) for f in findings]


@audit_router.post("/findings", response_model=AuditFindingResponse, tags=["Audit"])
async def create_audit_finding(
    data: AuditFindingCreate,
    current_user: Dict = Depends(require_permission("audit:create")),
    db: Session = Depends(get_db)
):
    """Create a new audit finding."""
    service = AuditService(db)
    finding = service.create_finding({**data.model_dump(), "created_by": current_user["email"]})
    return AuditFindingResponse(**finding)


@audit_router.put("/findings/{finding_id}", response_model=AuditFindingResponse, tags=["Audit"])
async def update_audit_finding(
    finding_id: str,
    data: AuditFindingUpdate,
    current_user: Dict = Depends(require_permission("audit:edit")),
    db: Session = Depends(get_db)
):
    """Update an existing audit finding."""
    service = AuditService(db)
    finding = service.update_finding(finding_id, data.model_dump(exclude_none=True))
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return AuditFindingResponse(**finding)


@audit_router.get("/evidence", response_model=List[EvidenceUploadResponse], tags=["Audit"])
async def get_evidence_list(
    finding_id: Optional[str] = Query(None),
    evidence_type: Optional[str] = Query(None),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get evidence files with optional filtering."""
    service = AuditService(db)
    evidence_list = service.get_evidence(finding_id=finding_id, evidence_type=evidence_type)
    return [EvidenceUploadResponse(**e) for e in evidence_list]


@audit_router.get("/evidence/ref/{ref_type}/{ref_id}", response_model=List[EvidenceUploadResponse], tags=["Audit"])
async def get_evidence_by_reference(
    ref_type: str,
    ref_id: str,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get evidence files by reference type (finding, incident, ptw, training)."""
    if ref_type not in ("finding", "incident", "ptw", "training"):
        raise HTTPException(status_code=400, detail="Invalid reference type")
    service = AuditService(db)
    evidence_list = service.get_evidence_by_ref(ref_type, ref_id)
    return [EvidenceUploadResponse(**e) for e in evidence_list]


@audit_router.post("/evidence/upload", response_model=EvidenceUploadResponse, tags=["Audit"])
async def upload_evidence(
    evidence_type: str = Query(..., description="Type: photo, document, video, audio, checklist, certificate, report"),
    file_name: str = Query(..., description="Original file name"),
    file_path: str = Query(..., description="Storage path or URL"),
    finding_id: Optional[str] = Query(None),
    incident_id: Optional[str] = Query(None),
    ptw_id: Optional[str] = Query(None),
    training_id: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    current_user: Dict = Depends(require_permission("audit:evidence")),
    db: Session = Depends(get_db)
):
    """Register an evidence file upload."""
    import os
    file_size = None
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
    mime_type = None
    if file_name:
        ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
        mime_map = {"pdf": "application/pdf", "jpg": "image/jpeg", "jpeg": "image/jpeg",
                     "png": "image/png", "doc": "application/msword",
                     "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                     "xls": "application/vnd.ms-excel", "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}
        mime_type = mime_map.get(ext)
    service = AuditService(db)
    evidence = service.upload_evidence({
        "evidence_type": evidence_type,
        "file_name": file_name,
        "file_path": file_path,
        "uploaded_by": current_user["email"],
        "finding_id": finding_id,
        "incident_id": incident_id,
        "ptw_id": ptw_id,
        "training_id": training_id,
        "description": description,
        "tags": ["uploaded"],
    })
    return EvidenceUploadResponse(
        evidence_id=evidence.evidence_id,
        finding_id=evidence.finding_id,
        incident_id=evidence.incident_id,
        ptw_id=evidence.ptw_id,
        training_id=evidence.training_id,
        evidence_type=evidence.evidence_type.value if hasattr(evidence.evidence_type, 'value') else evidence.evidence_type,
        file_name=evidence.file_name,
        file_path=evidence.file_path,
        file_size=evidence.file_size or file_size,
        mime_type=evidence.mime_type or mime_type,
        description=evidence.description,
        captured_by=evidence.captured_by,
        captured_at=evidence.captured_at,
        uploaded_by=evidence.uploaded_by,
        uploaded_at=evidence.uploaded_at,
        is_public=evidence.is_public,
        tags=evidence.tags,
        checksum=evidence.checksum,
    )


@audit_router.get("/trail", response_model=List[AuditTrailResponse], tags=["Audit"])
async def get_audit_trail(
    user_id: Optional[int] = Query(None),
    table_name: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    current_user: Dict = Depends(require_permission("audit:view")),
    db: Session = Depends(get_db)
):
    """Get audit trail log with optional filtering."""
    service = AuditService(db)
    trails = service.get_audit_trail(user_id=user_id, table_name=table_name, limit=limit)
    return [AuditTrailResponse(
        trail_id=t.trail_id,
        user_id=t.user_id,
        user_email=t.user_email,
        action=t.action,
        table_name=t.table_name,
        record_id=t.record_id,
        old_values=t.old_values,
        new_values=t.new_values,
        ip_address=t.ip_address,
        user_agent=t.user_agent,
        session_id=t.session_id,
        created_at=t.created_at,
    ) for t in trails]


@audit_router.post("/trail", response_model=AuditTrailResponse, tags=["Audit"])
async def create_audit_trail_entry(
    action: str = Query(..., description="Action performed: create, update, delete, view, export"),
    table_name: str = Query(..., description="Database table name"),
    record_id: str = Query(..., description="Record identifier"),
    old_values: Optional[str] = Query(None, description="JSON string of old values"),
    new_values: Optional[str] = Query(None, description="JSON string of new values"),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record an audit trail entry."""
    import json
    service = AuditService(db)
    old_vals = json.loads(old_values) if old_values else None
    new_vals = json.loads(new_values) if new_values else None
    trail = service.create_audit_trail(
        user_id=current_user.get("user_id"),
        action=action,
        table_name=table_name,
        record_id=record_id,
        old_values=old_vals,
        new_values=new_vals,
        ip_address=current_user.get("ip_address"),
        user_agent=current_user.get("user_agent"),
        session_id=current_user.get("session_id"),
    )
    return AuditTrailResponse(
        trail_id=trail.trail_id,
        user_id=trail.user_id,
        user_email=trail.user_email,
        action=trail.action,
        table_name=trail.table_name,
        record_id=trail.record_id,
        old_values=trail.old_values,
        new_values=trail.new_values,
        ip_address=trail.ip_address,
        user_agent=trail.user_agent,
        session_id=trail.session_id,
        created_at=trail.created_at,
    )


@audit_router.post("/corrective-actions", response_model=CorrectiveActionResponse, tags=["Audit"])
async def create_corrective_action(
    data: CorrectiveActionCreate,
    current_user: Dict = Depends(require_permission("audit:create")),
    db: Session = Depends(get_db)
):
    """Create a corrective or preventive action (CAR)."""
    service = AuditService(db)
    car = service.create_corrective_action({**data.model_dump(), "created_by": current_user["email"]})
    return CorrectiveActionResponse(**car)


@audit_router.put("/corrective-actions/{car_id}", response_model=CorrectiveActionResponse, tags=["Audit"])
async def update_corrective_action(
    car_id: str,
    data: CorrectiveActionUpdate,
    current_user: Dict = Depends(require_permission("audit:edit")),
    db: Session = Depends(get_db)
):
    """Update a corrective action record."""
    service = AuditService(db)
    car = service.update_corrective_action(car_id, data.model_dump(exclude_none=True))
    if not car:
        raise HTTPException(status_code=404, detail="Corrective action not found")
    return CorrectiveActionResponse(**car)


router.include_router(audit_router)


# =============================================
# ALERT & NOTIFICATION SYSTEM
# =============================================

alert_router = APIRouter(prefix="/alerts", tags=["Alerts"])


@alert_router.get("/rules", response_model=List[AlertRuleResponse], tags=["Alerts"])
async def get_alert_rules(
    site_id: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all alert rules."""
    service = AlertService(db)
    rules = service.get_alert_rules(site_id=site_id, is_active=is_active)
    return [AlertRuleResponse(**r) for r in rules]


@alert_router.post("/rules", response_model=AlertRuleResponse, tags=["Alerts"])
async def create_alert_rule(
    data: AlertRuleCreate,
    current_user: Dict = Depends(require_permission("system:config")),
    db: Session = Depends(get_db)
):
    """Create a new alert rule."""
    service = AlertService(db)
    rule = service.create_alert_rule(data.model_dump(), created_by=current_user["email"])
    return AlertRuleResponse(
        rule_id=rule.rule_id,
        rule_name=rule.rule_name,
        metric_type=rule.metric_type.value if hasattr(rule.metric_type, 'value') else rule.metric_type,
        condition=rule.condition,
        threshold_value=float(rule.threshold_value),
        severity=rule.severity.value if hasattr(rule.severity, 'value') else rule.severity,
        site_id=rule.site_id,
        department_id=rule.department_id,
        notification_channels=rule.notification_channels or [],
        recipients=rule.recipients or [],
        is_active=rule.is_active,
        cooldown_minutes=rule.cooldown_minutes,
        last_triggered_at=rule.last_triggered_at,
        description=rule.description,
        created_at=rule.created_at,
        updated_at=rule.updated_at,
    )


@alert_router.put("/rules/{rule_id}", response_model=AlertRuleResponse, tags=["Alerts"])
async def update_alert_rule(
    rule_id: str,
    data: AlertRuleUpdate,
    current_user: Dict = Depends(require_permission("system:config")),
    db: Session = Depends(get_db)
):
    """Update an existing alert rule."""
    service = AlertService(db)
    rule = service.update_alert_rule(rule_id, data.model_dump(exclude_none=True))
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    return AlertRuleResponse(
        rule_id=rule.rule_id,
        rule_name=rule.rule_name,
        metric_type=rule.metric_type.value if hasattr(rule.metric_type, 'value') else rule.metric_type,
        condition=rule.condition,
        threshold_value=float(rule.threshold_value),
        severity=rule.severity.value if hasattr(rule.severity, 'value') else rule.severity,
        site_id=rule.site_id,
        department_id=rule.department_id,
        notification_channels=rule.notification_channels or [],
        recipients=rule.recipients or [],
        is_active=rule.is_active,
        cooldown_minutes=rule.cooldown_minutes,
        last_triggered_at=rule.last_triggered_at,
        description=rule.description,
        created_at=rule.created_at,
        updated_at=rule.updated_at,
    )


@alert_router.get("/active", response_model=List[AlertResponse], tags=["Alerts"])
async def get_active_alerts(
    site_id: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get active (unresolved) alerts."""
    service = AlertService(db)
    alerts = service.get_alerts(site_id=site_id, status="active", severity=severity, limit=limit)
    return [AlertResponse(**a) for a in alerts]


@alert_router.get("/all", response_model=List[AlertResponse], tags=["Alerts"])
async def get_all_alerts(
    site_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all alerts with optional filtering."""
    service = AlertService(db)
    alerts = service.get_alerts(site_id=site_id, status=status, limit=limit)
    return [AlertResponse(**a) for a in alerts]


@alert_router.post("/{alert_id}/acknowledge", response_model=AlertResponse, tags=["Alerts"])
async def acknowledge_alert(
    alert_id: str,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Acknowledge an active alert."""
    service = AlertService(db)
    alert = service.acknowledge_alert(alert_id, current_user["email"])
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return AlertResponse(
        alert_id=alert.alert_id,
        rule_id=alert.rule_id,
        alert_type=alert.alert_type,
        severity=alert.severity.value if hasattr(alert.severity, 'value') else alert.severity,
        status=alert.status.value if hasattr(alert.status, 'value') else alert.status,
        site_id=alert.site_id,
        site_name=alert.site_name,
        metric_type=alert.metric_type,
        metric_value=float(alert.metric_value) if alert.metric_value else None,
        threshold_value=float(alert.threshold_value) if alert.threshold_value else None,
        message=alert.message,
        details=alert.details,
        triggered_by=alert.triggered_by,
        acknowledged_by=alert.acknowledged_by,
        acknowledged_at=alert.acknowledged_at,
        resolved_by=alert.resolved_by,
        resolved_at=alert.resolved_at,
        resolution_notes=alert.resolution_notes,
        alert_date=alert.alert_date,
        created_at=alert.created_at,
    )


@alert_router.post("/{alert_id}/resolve", response_model=AlertResponse, tags=["Alerts"])
async def resolve_alert(
    alert_id: str,
    resolution_notes: Optional[str] = Query(None),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resolve an acknowledged alert."""
    service = AlertService(db)
    alert = service.resolve_alert(alert_id, current_user["email"], notes=resolution_notes)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return AlertResponse(
        alert_id=alert.alert_id,
        rule_id=alert.rule_id,
        alert_type=alert.alert_type,
        severity=alert.severity.value if hasattr(alert.severity, 'value') else alert.severity,
        status=alert.status.value if hasattr(alert.status, 'value') else alert.status,
        site_id=alert.site_id,
        site_name=alert.site_name,
        metric_type=alert.metric_type,
        metric_value=float(alert.metric_value) if alert.metric_value else None,
        threshold_value=float(alert.threshold_value) if alert.threshold_value else None,
        message=alert.message,
        details=alert.details,
        triggered_by=alert.triggered_by,
        acknowledged_by=alert.acknowledged_by,
        acknowledged_at=alert.acknowledged_at,
        resolved_by=alert.resolved_by,
        resolved_at=alert.resolved_at,
        resolution_notes=alert.resolution_notes,
        alert_date=alert.alert_date,
        created_at=alert.created_at,
    )


@alert_router.get("/logs", response_model=List[NotificationLogResponse], tags=["Alerts"])
async def get_notification_logs(
    alert_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    current_user: Dict = Depends(require_permission("system:monitor")),
    db: Session = Depends(get_db)
):
    """Get notification delivery logs."""
    service = AlertService(db)
    logs = service.repo.get_notification_logs(alert_id=alert_id, status=status, limit=limit)
    return [NotificationLogResponse(
        log_id=l.log_id,
        alert_id=l.alert_id,
        channel=l.channel.value if hasattr(l.channel, 'value') else l.channel,
        recipient=l.recipient,
        subject=l.subject,
        body=l.body,
        status=l.status,
        error_message=l.error_message,
        sent_at=l.sent_at,
        delivered_at=l.delivered_at,
        retry_count=l.retry_count,
        created_at=l.created_at,
    ) for l in logs]


@alert_router.post("/evaluate", tags=["Alerts"])
async def trigger_alert_evaluation(
    current_user: Dict = Depends(require_permission("system:config")),
    db: Session = Depends(get_db)
):
    """Manually trigger alert rule evaluation (for testing/scheduling)."""
    service = AlertService(db)
    alerts = service.evaluate_alert_rules()
    return {"triggered": len(alerts), "message": f"{len(alerts)} alert(s) triggered"}


router.include_router(alert_router)


# =============================================
# REPORTING & EXPORT
# =============================================

report_router = APIRouter(prefix="/reports", tags=["Reports"])


@report_router.post("/generate", response_model=ReportResponse, tags=["Reports"])
async def generate_report(
    data: ReportRequest,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a formatted HSE report."""
    service = ReportingService(db)
    result = service.generate_report(data.model_dump())
    return ReportResponse(
        report_type=result.get("report_type", data.report_type),
        format=result.get("format", data.format),
        file_name=result.get("file_name", f"{data.report_type}_report.{data.format}"),
        generated_at=datetime.utcnow(),
        record_count=len(result.get("rows", [])),
        download_url=f"/api/reports/download?type={data.report_type}&start={data.start_date}&end={data.end_date}&format={data.format}",
    )


@report_router.get("/download", tags=["Reports"])
async def download_report(
    report_type: str = Query(..., description="Report type: executive, incident, ptw, training, environmental, equipment, contractor, audit"),
    start_date: date = Query(...),
    end_date: date = Query(...),
    site_id: str = Query("all"),
    format: str = Query("csv", description="Format: csv, json, markdown"),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download a report in the specified format."""
    from fastapi.responses import StreamingResponse
    import io
    service = ReportingService(db)
    result = service.generate_report({
        "report_type": report_type,
        "start_date": start_date,
        "end_date": end_date,
        "site_id": site_id,
        "format": format,
    })
    rows = result.get("rows", [])
    headers = result.get("headers", [])
    file_name = result.get("file_name", f"{report_type}_report.{format}")
    if format == "csv":
        import csv
        output = io.StringIO()
        writer = csv.writer(output)
        if headers:
            writer.writerow(headers)
        writer.writerows(rows)
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={file_name}"},
        )
    elif format == "json":
        import json
        output = io.BytesIO(json.dumps(result, indent=2, default=str).encode("utf-8"))
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={file_name}"},
        )
    elif format == "markdown":
        lines = [f"# {result.get('report_type', 'HSE Report')}", ""]
        lines.append(f"**Period:** {result.get('period', start_date + ' to ' + end_date)}")
        lines.append(f"**Site:** {site_id}")
        lines.append(f"**Generated:** {result.get('generated_at', datetime.utcnow().isoformat())}")
        lines.append("")
        if headers and rows:
            lines.append("| " + " | ".join(headers) + " |")
            lines.append("|" + "|".join(["---"] * len(headers)) + "|")
            for row in rows:
                lines.append("| " + " | ".join(str(v) for v in row) + " |")
        md_content = "\n".join(lines)
        output = io.BytesIO(md_content.encode("utf-8"))
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename={file_name}"},
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")


@report_router.post("/export", tags=["Reports"])
async def export_data(
    data: ExportRequest,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export raw data in CSV or JSON format."""
    from fastapi.responses import StreamingResponse
    import io, csv, json
    service = ReportingService(db)
    end_date = data.end_date
    start_date = data.start_date
    site_filter = data.site_id if data.site_id and data.site_id != "all" else None
    data_rows, col_headers = service._get_export_data(data.data_type, start_date, end_date, site_filter, data.columns)
    file_name = f"{data.data_type}_export_{start_date}_{end_date}.{data.format}"
    if data.format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        if col_headers:
            writer.writerow(col_headers)
        writer.writerows(data_rows)
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={file_name}"},
        )
    elif data.format == "json":
        rows_as_dicts = [dict(zip(col_headers, row)) for row in data_rows] if col_headers else data_rows
        output = io.BytesIO(json.dumps(rows_as_dicts, indent=2, default=str).encode("utf-8"))
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={file_name}"},
        )
    raise HTTPException(status_code=400, detail=f"Unsupported format: {data.format}")


# =============================================
# DATA QUALITY & MANAGEMENT
# =============================================

data_router = APIRouter(prefix="/data", tags=["Data Management"])


@data_router.get("/quality", response_model=DataQualityReport, tags=["Data Management"])
async def get_data_quality_report(
    current_user: Dict = Depends(require_permission("system:monitor")),
    db: Session = Depends(get_db)
):
    """Run data quality checks and return results."""
    service = DataQualityService(db)
    result = service.get_data_quality_report()
    return DataQualityReport(
        generated_at=datetime.fromisoformat(result["generated_at"].replace("Z", "+00:00")) if isinstance(result["generated_at"], str) else result["generated_at"],
        database_status=result.get("database_status", "unknown"),
        checks=[DataQualityCheckResponse(**c) for c in result.get("checks", [])],
        total_records=result.get("total_records", 0),
        last_updated=result.get("last_updated"),
    )


@data_router.post("/validate", tags=["Data Management"])
async def validate_data(
    data: DataValidationRequest,
    current_user: Dict = Depends(require_permission("system:monitor")),
    db: Session = Depends(get_db)
):
    """Validate data completeness, consistency, or validity for a table."""
    service = DataQualityService(db)
    if data.validation_type == "completeness":
        result = service.validate_data_completeness(data.table_name, data.date_key, data.site_id)
        return result
    raise HTTPException(status_code=400, detail=f"Unsupported validation type: {data.validation_type}")


@data_router.get("/health", response_model=HealthResponse, tags=["Data Management"])
async def data_health_check(db: Session = Depends(get_db)):
    """Check data freshness and completeness."""
    from app.database import check_database_connection
    db_status = check_database_connection()
    try:
        last_updated = db.execute("SELECT MAX(updated_at) FROM hse.fact_hse").scalar()
        record_count = db.execute("SELECT COUNT(*) FROM hse.fact_hse").scalar() or 0
        return HealthResponse(
            status=db_status["status"],
            version="1.0.0",
            database=db_status["status"],
            timestamp=datetime.utcnow(),
        )
    except Exception as e:
        return HealthResponse(
            status="degraded",
            version="1.0.0",
            database=f"error: {str(e)}",
            timestamp=datetime.utcnow(),
        )


# =============================================
# AI SAFETY ASSISTANT
# =============================================

ai_router = APIRouter()


@ai_router.post("/chat", response_model=AIChatResponse, tags=["AI Safety Assistant"])
async def chat_with_ai(
    request: AIChatRequest,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI Safety Assistant - Ask questions about HSE data.
    Uses RAG (Retrieval-Augmented Generation) with knowledge base.
    """
    service = AIService(db)
    result = service.chat(
        user_id=current_user.get("user_id"),
        question=request.question,
        conversation_id=request.conversation_id,
        context_type=request.context_type,
        context_id=request.context_id,
        max_sources=request.max_sources,
    )
    return AIChatResponse(**result)


@ai_router.post("/documents", response_model=AIDocumentResponse, tags=["AI Safety Assistant"])
async def ingest_document(
    data: AIDocumentCreate,
    current_user: Dict = Depends(require_permission("system:config")),
    db: Session = Depends(get_db)
):
    """Ingest a document into the AI knowledge base."""
    from app.utils.security import generate_uuid
    service = AIService(db)

    doc_data = data.model_dump()
    doc_data["document_id"] = generate_uuid()
    doc_data["created_by"] = current_user.get("email")

    result = service.ingest_document(doc_data, chunks=[])
    return AIDocumentResponse(**result)


@ai_router.get("/documents", response_model=List[AIDocumentResponse], tags=["AI Safety Assistant"])
async def get_documents(
    document_type: Optional[str] = Query(None),
    source_system: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get knowledge base documents."""
    service = AIService(db)
    documents = service.repo.get_documents(document_type=document_type, source_system=source_system, limit=limit)
    return [AIDocumentResponse(**doc) for doc in documents]


@ai_router.get("/conversations", response_model=List[AIConversationResponse], tags=["AI Safety Assistant"])
async def get_conversations(
    limit: int = Query(20, ge=1, le=100),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's conversation history."""
    service = AIService(db)
    conversations = service.repo.get_user_conversations(current_user.get("user_id"), limit=limit)
    return [AIConversationResponse(**conv) for conv in conversations]


@ai_router.get("/conversations/{conversation_id}", response_model=AIConversationResponse, tags=["AI Safety Assistant"])
async def get_conversation(
    conversation_id: str,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation with messages."""
    service = AIService(db)
    conv = service.repo.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = service.repo.get_conversation_messages(conversation_id)
    conv_data = {c.name: getattr(conv, c.name) for c in conv.__table__.columns}
    conv_data["messages"] = messages
    return AIConversationResponse(**conv_data)


@ai_router.get("/risk-score/{site_id}", response_model=AIRiskScoreResponse, tags=["AI Safety Assistant"])
async def get_risk_score(
    site_id: str,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered risk intelligence for a site."""
    service = AIService(db)
    risk_data = service.calculate_risk_score(site_id)
    return AIRiskScoreResponse(**risk_data)


@ai_router.get("/compliance", response_model=AIComplianceResponse, tags=["AI Safety Assistant"])
async def get_compliance_intelligence(
    site_id: Optional[str] = Query(None),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered compliance intelligence."""
    service = AIService(db)
    compliance_data = service.get_compliance_intelligence(site_id=site_id)
    return AIComplianceResponse(**compliance_data)


@ai_router.get("/compliance/enhanced", response_model=EnhancedComplianceResponse, tags=["AI Safety Assistant"])
async def get_enhanced_compliance_intelligence(
    site_id: Optional[str] = Query(None),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get enhanced AI-powered compliance intelligence with granular gap details."""
    service = AIService(db)
    compliance_data = service.get_compliance_intelligence(site_id=site_id)
    return EnhancedComplianceResponse(**compliance_data)


@ai_router.get("/priority-today", response_model=PriorityTodayResponse, tags=["Executive Decision Support"])
async def get_priority_today(
    site_id: Optional[str] = Query(None),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get executive decision support - Priority Today actions."""
    service = AIService(db)
    priority_data = service.get_priority_today(site_id=site_id)
    return PriorityTodayResponse(**priority_data)


@ai_router.get("/predictive/{site_id}", response_model=PredictiveSafetyResponse, tags=["Predictive Safety"])
async def get_predictive_safety(
    site_id: str,
    metric: str = Query("ltifr", description="Metric to forecast: ltifr, trir, near_miss"),
    forecast_days: int = Query(30, ge=7, le=90),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get predictive safety forecast for a site."""
    service = AIService(db)
    forecast_data = service.get_predictive_safety(site_id=site_id, metric=metric, forecast_days=forecast_days)
    return PredictiveSafetyResponse(**forecast_data)


@ai_router.get("/knowledge/stats", tags=["AI Safety Assistant"])
async def get_knowledge_stats(
    current_user: Dict = Depends(require_permission("system:monitor")),
    db: Session = Depends(get_db)
):
    """Get knowledge base statistics."""
    service = AIService(db)
    return service.get_knowledge_base_stats()


router.include_router(report_router)
router.include_router(data_router)
router.include_router(ai_router)
router.include_router(operational_controller.router)
