"""
FastAPI controllers for HSE Operations modules.
All operational module routes.
"""

from datetime import date, datetime
from typing import Optional, List, Dict
import csv
import io

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.rbac import get_current_user, require_permission
from app.schemas import (
    IncidentReportCreate, IncidentReportUpdate, IncidentReportResponse,
    IncidentDashboardResponse,
    PTWRequestCreate, PTWRequestUpdate, PTWRequestResponse,
    TrainingRecordCreate, TrainingRecordUpdate, TrainingRecordResponse,
    OperationalAttachmentResponse, WorkflowHistoryResponse,
    OperationalListResponse
)
from app.services.operational import (
    IncidentService, PTWService, TrainingService,
    ObservationService, NearMissService, EquipmentInspectionService,
    HIRAService, ContractorService
)

router = APIRouter()


# =============================================
# INCIDENT MANAGEMENT
# =============================================

incident_router = APIRouter(prefix="/incidents", tags=["Incident Management"])


@incident_router.get("/dashboard", response_model=IncidentDashboardResponse, tags=["Incident Management"])
async def get_incident_dashboard(
    site_id: Optional[str] = Query(None),
    period_days: int = Query(30, ge=1, le=365),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get incident dashboard statistics."""
    service = IncidentService(db)
    return service.get_dashboard(site_id=site_id, period_days=period_days)


@incident_router.get("/list", response_model=OperationalListResponse, tags=["Incident Management"])
async def list_incidents(
    site_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    sort_by: str = Query("report_date"),
    sort_order: str = Query("desc"),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List incidents with filtering and pagination."""
    service = IncidentService(db)
    result = service.list_incidents(
        site_id=site_id, status=status, severity=severity, category=category,
        page=page, page_size=page_size, sort_by=sort_by, sort_order=sort_order
    )
    return OperationalListResponse(**result)


@incident_router.get("/{report_id}", response_model=IncidentReportResponse, tags=["Incident Management"])
async def get_incident(
    report_id: str,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single incident report with history and attachments."""
    service = IncidentService(db)
    incident = service.get_incident(report_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentReportResponse(**incident)


@incident_router.post("/", response_model=IncidentReportResponse, tags=["Incident Management"])
async def create_incident(
    data: IncidentReportCreate,
    current_user: Dict = Depends(require_permission("incident:create")),
    db: Session = Depends(get_db)
):
    """Create new incident report."""
    service = IncidentService(db)
    result = service.create_incident(data.model_dump(), created_by=current_user["email"])
    return IncidentReportResponse(**result)


@incident_router.put("/{report_id}", response_model=IncidentReportResponse, tags=["Incident Management"])
async def update_incident(
    report_id: str,
    data: IncidentReportUpdate,
    current_user: Dict = Depends(require_permission("incident:edit")),
    db: Session = Depends(get_db)
):
    """Update incident report."""
    service = IncidentService(db)
    result = service.update_incident(report_id, data.model_dump(exclude_none=True), updated_by=current_user["email"])
    if not result:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentReportResponse(**result)


@incident_router.delete("/{report_id}", tags=["Incident Management"])
async def delete_incident(
    report_id: str,
    current_user: Dict = Depends(require_permission("incident:delete")),
    db: Session = Depends(get_db)
):
    """Soft delete incident report."""
    service = IncidentService(db)
    success = service.delete_incident(report_id, deleted_by=current_user["email"])
    if not success:
        raise HTTPException(status_code=404, detail="Incident not found")
    return {"message": "Incident deleted successfully"}


@incident_router.post("/{report_id}/submit", response_model=IncidentReportResponse, tags=["Incident Management"])
async def submit_incident(
    report_id: str,
    current_user: Dict = Depends(require_permission("incident:create")),
    db: Session = Depends(get_db)
):
    """Submit incident for review."""
    service = IncidentService(db)
    result = service.submit_incident(report_id, submitted_by=current_user["email"])
    if not result:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentReportResponse(**result)


@incident_router.post("/{report_id}/approve", response_model=IncidentReportResponse, tags=["Incident Management"])
async def approve_incident(
    report_id: str,
    remarks: Optional[str] = Query(None),
    current_user: Dict = Depends(require_permission("incident:close")),
    db: Session = Depends(get_db)
):
    """Approve incident."""
    service = IncidentService(db)
    result = service.approve_incident(report_id, approved_by=current_user["email"], remarks=remarks)
    if not result:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentReportResponse(**result)


@incident_router.post("/{report_id}/close", response_model=IncidentReportResponse, tags=["Incident Management"])
async def close_incident(
    report_id: str,
    remarks: Optional[str] = Query(None),
    current_user: Dict = Depends(require_permission("incident:close")),
    db: Session = Depends(get_db)
):
    """Close incident."""
    service = IncidentService(db)
    result = service.close_incident(report_id, closed_by=current_user["email"], remarks=remarks)
    if not result:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentReportResponse(**result)


@incident_router.get("/{report_id}/workflow", response_model=List[WorkflowHistoryResponse], tags=["Incident Management"])
async def get_incident_workflow(
    report_id: str,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get workflow history for incident."""
    service = IncidentService(db)
    history = service.repo.get_workflow_history(report_id)
    return [WorkflowHistoryResponse(**h) for h in history]


@incident_router.get("/{report_id}/attachments", response_model=List[OperationalAttachmentResponse], tags=["Incident Management"])
async def get_incident_attachments(
    report_id: str,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get attachments for incident."""
    service = IncidentService(db)
    attachments = service.repo.get_attachments(report_id)
    return [OperationalAttachmentResponse(**a) for a in attachments]


@incident_router.post("/export", tags=["Incident Management"])
async def export_incidents(
    site_id: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    format: str = Query("csv", regex="^(csv|excel)$"),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export incidents to CSV or Excel."""
    service = IncidentService(db)
    result = service.export_incidents(site_id=site_id, start_date=start_date, end_date=end_date, format=format)

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(result["headers"])
        writer.writerows(result["rows"])
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={result['file_name']}"}
        )
    else:
        # Excel format - return as CSV for now
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(result["headers"])
        writer.writerows(result["rows"])
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/vnd.ms-excel",
            headers={"Content-Disposition": f"attachment; filename={result['file_name']}"}
        )


@incident_router.post("/import", tags=["Incident Management"])
async def import_incidents(
    file: UploadFile = File(...),
    current_user: Dict = Depends(require_permission("incident:create")),
    db: Session = Depends(get_db)
):
    """Import incidents from CSV file."""
    service = IncidentService(db)
    content = await file.read()
    file_content = content.decode("utf-8")
    result = service.import_incidents(file_content, created_by=current_user["email"])
    return result


router.include_router(incident_router)


# =============================================
# PTW (PERMIT TO WORK)
# =============================================

ptw_router = APIRouter(prefix="/ptw", tags=["PTW Management"])


@ptw_router.get("/dashboard", tags=["PTW Management"])
async def get_ptw_dashboard(
    site_id: Optional[str] = Query(None),
    period_days: int = Query(30, ge=1, le=365),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get PTW dashboard statistics."""
    service = PTWService(db)
    return service.get_dashboard(site_id=site_id, period_days=period_days)


@ptw_router.get("/list", tags=["PTW Management"])
async def list_ptws(
    site_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    sort_by: str = Query("start_at"),
    sort_order: str = Query("desc"),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List PTW requests with filtering and pagination."""
    service = PTWService(db)
    result = service.list_ptws(
        site_id=site_id, status=status, page=page, page_size=page_size,
        sort_by=sort_by, sort_order=sort_order
    )
    return OperationalListResponse(**result)


@ptw_router.get("/{request_id}", response_model=PTWRequestResponse, tags=["PTW Management"])
async def get_ptw(
    request_id: str,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single PTW request with history and attachments."""
    service = PTWService(db)
    ptw = service.get_ptw(request_id)
    if not ptw:
        raise HTTPException(status_code=404, detail="PTW not found")
    return PTWRequestResponse(**ptw)


@ptw_router.post("/", response_model=PTWRequestResponse, tags=["PTW Management"])
async def create_ptw(
    data: PTWRequestCreate,
    current_user: Dict = Depends(require_permission("ptw:create")),
    db: Session = Depends(get_db)
):
    """Create new PTW request."""
    service = PTWService(db)
    result = service.create_ptw(data.model_dump(), created_by=current_user["email"])
    return PTWRequestResponse(**result)


@ptw_router.put("/{request_id}", response_model=PTWRequestResponse, tags=["PTW Management"])
async def update_ptw(
    request_id: str,
    data: PTWRequestUpdate,
    current_user: Dict = Depends(require_permission("ptw:edit")),
    db: Session = Depends(get_db)
):
    """Update PTW request."""
    service = PTWService(db)
    result = service.update_ptw(request_id, data.model_dump(exclude_none=True), updated_by=current_user["email"])
    if not result:
        raise HTTPException(status_code=404, detail="PTW not found")
    return PTWRequestResponse(**result)


@ptw_router.post("/{request_id}/submit", response_model=PTWRequestResponse, tags=["PTW Management"])
async def submit_ptw(
    request_id: str,
    current_user: Dict = Depends(require_permission("ptw:create")),
    db: Session = Depends(get_db)
):
    """Submit PTW for approval."""
    service = PTWService(db)
    result = service.submit_ptw(request_id, submitted_by=current_user["email"])
    if not result:
        raise HTTPException(status_code=404, detail="PTW not found")
    return PTWRequestResponse(**result)


@ptw_router.post("/{request_id}/approve", response_model=PTWRequestResponse, tags=["PTW Management"])
async def approve_ptw(
    request_id: str,
    current_user: Dict = Depends(require_permission("ptw:approve")),
    db: Session = Depends(get_db)
):
    """Approve PTW."""
    service = PTWService(db)
    result = service.approve_ptw(request_id, approved_by=current_user["email"])
    if not result:
        raise HTTPException(status_code=404, detail="PTW not found")
    return PTWRequestResponse(**result)


@ptw_router.post("/{request_id}/activate", response_model=PTWRequestResponse, tags=["PTW Management"])
async def activate_ptw(
    request_id: str,
    current_user: Dict = Depends(require_permission("ptw:approve")),
    db: Session = Depends(get_db)
):
    """Activate approved PTW."""
    service = PTWService(db)
    result = service.activate_ptw(request_id, activated_by=current_user["email"])
    if not result:
        raise HTTPException(status_code=404, detail="PTW not found")
    return PTWRequestResponse(**result)


@ptw_router.post("/{request_id}/close", response_model=PTWRequestResponse, tags=["PTW Management"])
async def close_ptw(
    request_id: str,
    current_user: Dict = Depends(require_permission("ptw:close")),
    db: Session = Depends(get_db)
):
    """Close PTW."""
    service = PTWService(db)
    result = service.close_ptw(request_id, closed_by=current_user["email"])
    if not result:
        raise HTTPException(status_code=404, detail="PTW not found")
    return PTWRequestResponse(**result)


router.include_router(ptw_router)


# =============================================
# TRAINING RECORDS
# =============================================

training_router = APIRouter(prefix="/training", tags=["Training Management"])


@training_router.get("/dashboard", tags=["Training Management"])
async def get_training_dashboard(
    site_id: Optional[str] = Query(None),
    period_days: int = Query(30, ge=1, le=365),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get training dashboard statistics."""
    service = TrainingService(db)
    return service.get_dashboard(site_id=site_id, period_days=period_days)


@training_router.get("/list", tags=["Training Management"])
async def list_training(
    site_id: Optional[str] = Query(None),
    result: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List training records."""
    service = TrainingService(db)
    result_data = service.list_training(site_id=site_id, result=result, page=page, page_size=page_size)
    return OperationalListResponse(**result_data)


@training_router.get("/{record_id}", response_model=TrainingRecordResponse, tags=["Training Management"])
async def get_training(
    record_id: str,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single training record."""
    service = TrainingService(db)
    record = service.get_training(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Training record not found")
    return TrainingRecordResponse(**record)


@training_router.post("/", response_model=TrainingRecordResponse, tags=["Training Management"])
async def create_training(
    data: TrainingRecordCreate,
    current_user: Dict = Depends(require_permission("training:create")),
    db: Session = Depends(get_db)
):
    """Create training record."""
    service = TrainingService(db)
    result = service.create_training(data.model_dump(), created_by=current_user["email"])
    return TrainingRecordResponse(**result)


@training_router.put("/{record_id}", response_model=TrainingRecordResponse, tags=["Training Management"])
async def update_training(
    record_id: str,
    data: TrainingRecordUpdate,
    current_user: Dict = Depends(require_permission("training:edit")),
    db: Session = Depends(get_db)
):
    """Update training record."""
    service = TrainingService(db)
    result = service.update_training(record_id, data.model_dump(exclude_none=True), updated_by=current_user["email"])
    if not result:
        raise HTTPException(status_code=404, detail="Training record not found")
    return TrainingRecordResponse(**result)


@training_router.delete("/{record_id}", tags=["Training Management"])
async def delete_training(
    record_id: str,
    current_user: Dict = Depends(require_permission("training:delete")),
    db: Session = Depends(get_db)
):
    """Soft delete training record."""
    service = TrainingService(db)
    success = service.delete_training(record_id, deleted_by=current_user["email"])
    if not success:
        raise HTTPException(status_code=404, detail="Training record not found")
    return {"message": "Training record deleted successfully"}


router.include_router(training_router)


# =============================================
# SAFETY OBSERVATIONS
# =============================================

observation_router = APIRouter(prefix="/observations", tags=["Safety Observations"])


@observation_router.get("/dashboard", tags=["Safety Observations"])
async def get_observation_dashboard(
    site_id: Optional[str] = Query(None),
    period_days: int = Query(30, ge=1, le=365),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get observation dashboard statistics."""
    service = ObservationService(db)
    return service.get_dashboard(site_id=site_id, period_days=period_days)


@observation_router.get("/list", tags=["Safety Observations"])
async def list_observations(
    site_id: Optional[str] = Query(None),
    observation_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List safety observations."""
    service = ObservationService(db)
    result = service.list_observations(site_id=site_id, obs_type=observation_type, page=page, page_size=page_size)
    return OperationalListResponse(**result)


@observation_router.post("/", tags=["Safety Observations"])
async def create_observation(
    data: Dict,
    current_user: Dict = Depends(require_permission("incident:create")),
    db: Session = Depends(get_db)
):
    """Create safety observation."""
    service = ObservationService(db)
    result = service.create_observation(data, created_by=current_user["email"])
    return result


router.include_router(observation_router)


# =============================================
# NEAR MISS REPORTS
# =============================================

near_miss_router = APIRouter(prefix="/near-miss", tags=["Near Miss Reports"])


@near_miss_router.get("/dashboard", tags=["Near Miss Reports"])
async def get_near_miss_dashboard(
    site_id: Optional[str] = Query(None),
    period_days: int = Query(30, ge=1, le=365),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get near miss dashboard statistics."""
    service = NearMissService(db)
    return service.get_dashboard(site_id=site_id, period_days=period_days)


@near_miss_router.get("/list", tags=["Near Miss Reports"])
async def list_near_misses(
    site_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List near miss reports."""
    service = NearMissService(db)
    result = service.list_near_misses(site_id=site_id, page=page, page_size=page_size)
    return OperationalListResponse(**result)


@near_miss_router.post("/", tags=["Near Miss Reports"])
async def create_near_miss(
    data: Dict,
    current_user: Dict = Depends(require_permission("incident:create")),
    db: Session = Depends(get_db)
):
    """Create near miss report."""
    service = NearMissService(db)
    result = service.create_near_miss(data, created_by=current_user["email"])
    return result


router.include_router(near_miss_router)


# =============================================
# EQUIPMENT INSPECTIONS
# =============================================

equipment_router = APIRouter(prefix="/equipment", tags=["Equipment Inspections"])


@equipment_router.get("/inspections", tags=["Equipment Inspections"])
async def list_equipment_inspections(
    site_id: Optional[str] = Query(None),
    result: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List equipment inspections."""
    service = EquipmentInspectionService(db)
    result_data = service.list_inspections(site_id=site_id, result=result, page=page, page_size=page_size)
    return OperationalListResponse(**result_data)


@equipment_router.post("/inspections", tags=["Equipment Inspections"])
async def create_equipment_inspection(
    data: Dict,
    current_user: Dict = Depends(require_permission("equipment:inspect")),
    db: Session = Depends(get_db)
):
    """Create equipment inspection."""
    service = EquipmentInspectionService(db)
    result = service.create_inspection(data, created_by=current_user["email"])
    return result


router.include_router(equipment_router)


# =============================================
# HIRA / JSA
# =============================================

hira_router = APIRouter(prefix="/hira", tags=["HIRA / JSA"])


@hira_router.get("/list", tags=["HIRA / JSA"])
async def list_hira(
    site_id: Optional[str] = Query(None),
    risk_rating: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List HIRA assessments."""
    service = HIRAService(db)
    result_data = service.list_assessments(site_id=site_id, risk_rating=risk_rating, page=page, page_size=page_size)
    return OperationalListResponse(**result_data)


@hira_router.post("/", tags=["HIRA / JSA"])
async def create_hira(
    data: Dict,
    current_user: Dict = Depends(require_permission("incident:create")),
    db: Session = Depends(get_db)
):
    """Create HIRA assessment."""
    service = HIRAService(db)
    result = service.create_assessment(data, created_by=current_user["email"])
    return result


router.include_router(hira_router)


# =============================================
# CONTRACTOR MANAGEMENT
# =============================================

contractor_router = APIRouter(prefix="/contractors", tags=["Contractor Management"])


@contractor_router.get("/records", tags=["Contractor Management"])
async def list_contractor_records(
    site_id: Optional[str] = Query(None),
    record_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List contractor records."""
    service = ContractorService(db)
    result_data = service.list_records(site_id=site_id, record_type=record_type, page=page, page_size=page_size)
    return OperationalListResponse(**result_data)


@contractor_router.post("/records", tags=["Contractor Management"])
async def create_contractor_record(
    data: Dict,
    current_user: Dict = Depends(require_permission("audit:create")),
    db: Session = Depends(get_db)
):
    """Create contractor record."""
    service = ContractorService(db)
    result = service.create_record(data, created_by=current_user["email"])
    return result


router.include_router(contractor_router)
