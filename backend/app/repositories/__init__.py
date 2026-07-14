"""
Data access layer for HSE platform.
Repositories encapsulate database queries.
"""

from typing import Optional, List, Dict, Any
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, asc, Integer

from app.models.hse_models import (
    FactHSE, DimSite, DimDepartment, DimIncident, DimPTW,
    DimEquipment, DimContractor, DimTraining, DimEnvironmental,
    SecurityUser, SecurityRole, SecurityPermission,
    SecurityRolePermission, SecurityUserRole, SecuritySession,
    SecurityLoginHistory
)

from app.repositories.audit import AuditRepository, EvidenceRepository
from app.repositories.alert import AlertRepository


class BaseRepository:
    """Base repository with common operations."""

    def __init__(self, db: Session):
        self.db = db


class AuthRepository(BaseRepository):
    """Repository for authentication, RBAC, session, and audit."""

    def get_user_by_email(self, email: str) -> Optional[SecurityUser]:
        return self.db.query(SecurityUser).filter(SecurityUser.email == email).first()

    def get_user_by_id(self, user_id: int) -> Optional[SecurityUser]:
        return self.db.query(SecurityUser).filter(SecurityUser.user_id == user_id).first()

    def get_user_roles(self, user_id: int) -> List[SecurityUserRole]:
        return self.db.query(SecurityUserRole).filter(
            SecurityUserRole.user_id == user_id,
            SecurityUserRole.is_active == True
        ).all()

    def get_user_permissions(self, user_id: int) -> List[str]:
        """Get all permission names for a user."""
        user_roles = self.get_user_roles(user_id)
        permissions = []
        for ur in user_roles:
            role_perms = self.db.query(SecurityRolePermission).filter(
                SecurityRolePermission.role_id == ur.role_id
            ).all()
            for rp in role_perms:
                perm = self.db.query(SecurityPermission).filter(
                    SecurityPermission.permission_id == rp.permission_id
                ).first()
                if perm:
                    permissions.append(perm.permission_name)
        return list(set(permissions))

    def get_user_site_access(self, user_id: int) -> List[str]:
        """Get site access list for a user."""
        user_roles = self.get_user_roles(user_id)
        site_access = []
        for ur in user_roles:
            if ur.site_access == "ALL":
                return ["ALL"]
            if ur.site_access:
                site_access.extend(ur.site_access.split(","))
        return list(set(site_access)) if site_access else ["ALL"]

    def get_active_session(self, session_id: str) -> Optional[SecuritySession]:
        return self.db.query(SecuritySession).filter(
            SecuritySession.session_id == session_id,
            SecuritySession.is_active == True,
            SecuritySession.expires_at > datetime.utcnow()
        ).first()

    def create_session(self, session_id: str, user_id: int, ip_address: str, user_agent: str) -> SecuritySession:
        session = SecuritySession(
            session_id=session_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def invalidate_session(self, session_id: str) -> bool:
        session = self.db.query(SecuritySession).filter(
            SecuritySession.session_id == session_id,
            SecuritySession.is_active == True
        ).first()
        if session:
            session.is_active = False
            session.logged_out_at = datetime.utcnow()
            self.db.commit()
            return True
        return False

    def invalidate_all_user_sessions(self, user_id: int) -> int:
        sessions = self.db.query(SecuritySession).filter(
            SecuritySession.user_id == user_id,
            SecuritySession.is_active == True
        ).all()
        for session in sessions:
            session.is_active = False
            session.logged_out_at = datetime.utcnow()
        self.db.commit()
        return len(sessions)

    def record_login_attempt(self, **kwargs) -> SecurityLoginHistory:
        history = SecurityLoginHistory(**kwargs)
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history

    def get_login_history(self, user_id: Optional[int] = None, limit: int = 50) -> List[SecurityLoginHistory]:
        query = self.db.query(SecurityLoginHistory)
        if user_id:
            query = query.filter(SecurityLoginHistory.user_id == user_id)
        return query.order_by(desc(SecurityLoginHistory.created_at)).limit(limit).all()

    def increment_failed_login(self, user: SecurityUser) -> None:
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
        if user.failed_login_attempts >= 5:
            user.is_locked = True
            user.locked_until = datetime.utcnow() + timedelta(minutes=15)
        self.db.commit()

    def reset_failed_login(self, user: SecurityUser) -> None:
        user.failed_login_attempts = 0
        user.is_locked = False
        user.locked_until = None
        user.last_login_at = datetime.utcnow()
        self.db.commit()


class DashboardRepository(BaseRepository):
    """Repository for dashboard aggregations."""

    def get_executive_summary(
        self,
        site_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Get aggregated KPI data for executive dashboard."""
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=period_days)

        query = self.db.query(
            func.sum(FactHSE.man_hours_worked).label("total_man_hours"),
            func.sum(FactHSE.lti_count).label("total_lti"),
            func.sum(FactHSE.mti_count).label("total_mti"),
            func.sum(FactHSE.fai_count).label("total_fai"),
            func.sum(FactHSE.near_miss_count).label("total_near_miss"),
            func.sum(FactHSE.fatality_count).label("total_fatality"),
            func.sum(FactHSE.ptw_issued_count).label("total_ptw_issued"),
            func.sum(FactHSE.ptw_violation_count).label("total_ptw_violations"),
            func.sum(FactHSE.observation_count).label("total_observations"),
            func.sum(FactHSE.inspection_count).label("total_inspections"),
            func.sum(FactHSE.training_passed_count).label("total_training_passed"),
            func.avg(FactHSE.audit_score).label("avg_audit_score"),
            func.sum(FactHSE.env_exceeded.cast(Integer)).label("env_exceedances"),
        ).filter(
            FactHSE.date_key >= start_date,
            FactHSE.date_key <= end_date,
        )

        if site_id and site_id != "all":
            query = query.filter(FactHSE.site_key == site_id)

        result = query.first()

        total_man_hours = float(result.total_man_hours or 0)
        total_lti = int(result.total_lti or 0)
        total_mti = int(result.total_mti or 0)
        total_fai = int(result.total_fai or 0)
        total_near_miss = int(result.total_near_miss or 0)
        total_fatality = int(result.total_fatality or 0)

        ltifr = (total_lti * 1_000_000) / total_man_hours if total_man_hours > 0 else 0
        trir = ((total_lti + total_mti + total_fai) * 200_000) / total_man_hours if total_man_hours > 0 else 0
        severity_rate = (total_mti * 200_000) / total_man_hours if total_man_hours > 0 else 0
        near_miss_rate = (total_near_miss * 1_000) / total_man_hours if total_man_hours > 0 else 0

        return {
            "total_man_hours": total_man_hours,
            "ltifr": round(ltifr, 2),
            "trir": round(trir, 2),
            "severity_rate": round(severity_rate, 2),
            "near_miss_rate": round(near_miss_rate, 2),
            "total_fatality": total_fatality,
            "total_lti": total_lti,
            "total_mti": total_mti,
            "total_fai": total_fai,
            "total_ptw_issued": int(result.total_ptw_issued or 0),
            "total_ptw_violations": int(result.total_ptw_violations or 0),
            "total_observations": int(result.total_observations or 0),
            "total_training_passed": int(result.total_training_passed or 0),
            "avg_audit_score": round(float(result.avg_audit_score or 0), 1),
            "env_exceedances": int(result.env_exceedances or 0),
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "period_days": period_days,
        }

    def get_incident_trend(
        self,
        site_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """Get daily incident counts for trend chart."""
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=90)

        query = self.db.query(
            FactHSE.date_key,
            func.sum(FactHSE.lti_count).label("lti"),
            func.sum(FactHSE.mti_count).label("mti"),
            func.sum(FactHSE.fai_count).label("fai"),
            func.sum(FactHSE.near_miss_count).label("near_miss"),
            func.sum(FactHSE.man_hours_worked).label("man_hours"),
        ).filter(
            FactHSE.date_key >= start_date,
            FactHSE.date_key <= end_date,
        )

        if site_id and site_id != "all":
            query = query.filter(FactHSE.site_key == site_id)

        results = query.group_by(FactHSE.date_key).order_by(FactHSE.date_key).all()

        return [
            {
                "date": r.date_key.isoformat(),
                "lti": int(r.lti or 0),
                "mti": int(r.mti or 0),
                "fai": int(r.fai or 0),
                "near_miss": int(r.near_miss or 0),
                "ltifr": round((float(r.lti or 0) * 1_000_000) / float(r.man_hours or 1), 2),
                "trir": round(((float(r.lti or 0) + float(r.mti or 0) + float(r.fai or 0)) * 200_000) / float(r.man_hours or 1), 2),
            }
            for r in results
        ]

    def get_incident_distribution(
        self,
        site_id: Optional[str] = None,
        period_days: int = 30
    ) -> Dict[str, int]:
        """Get incident counts by type."""
        end_date = date.today()
        start_date = end_date - timedelta(days=period_days)

        query = self.db.query(
            func.sum(FactHSE.lti_count).label("lti"),
            func.sum(FactHSE.mti_count).label("mti"),
            func.sum(FactHSE.fai_count).label("fai"),
            func.sum(FactHSE.near_miss_count).label("near_miss"),
            func.sum(FactHSE.fatality_count).label("fatality"),
        ).filter(
            FactHSE.date_key >= start_date,
            FactHSE.date_key <= end_date,
        )

        if site_id and site_id != "all":
            query = query.filter(FactHSE.site_key == site_id)

        result = query.first()
        return {
            "LTI": int(result.lti or 0),
            "MTI": int(result.mti or 0),
            "First Aid": int(result.fai or 0),
            "Near Miss": int(result.near_miss or 0),
            "Fatality": int(result.fatality or 0),
        }

    def get_incident_by_department(
        self,
        site_id: Optional[str] = None,
        period_days: int = 30
    ) -> Dict[str, int]:
        """Get incident counts grouped by department."""
        end_date = date.today()
        start_date = end_date - timedelta(days=period_days)

        query = self.db.query(
            DimDepartment.dept_name,
            func.sum(FactHSE.lti_count + FactHSE.mti_count + FactHSE.fai_count).label("total")
        ).join(
            FactHSE, FactHSE.dept_key == DimDepartment.dept_id
        ).filter(
            FactHSE.date_key >= start_date,
            FactHSE.date_key <= end_date,
        )

        if site_id and site_id != "all":
            query = query.filter(FactHSE.site_key == site_id)

        results = query.group_by(DimDepartment.dept_name).all()
        return {r.dept_name: int(r.total or 0) for r in results if r.dept_name}

    def get_ptw_summary(
        self,
        site_id: Optional[str] = None,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Get PTW summary statistics."""
        end_date = date.today()
        start_date = end_date - timedelta(days=period_days)

        query = self.db.query(
            func.sum(FactHSE.ptw_issued_count).label("issued"),
            func.sum(FactHSE.ptw_closed_count).label("closed"),
            func.sum(FactHSE.ptw_open_count).label("open"),
            func.sum(FactHSE.ptw_violation_count).label("violations"),
        ).filter(
            FactHSE.date_key >= start_date,
            FactHSE.date_key <= end_date,
        )

        if site_id and site_id != "all":
            query = query.filter(FactHSE.site_key == site_id)

        result = query.first()
        issued = int(result.issued or 0)
        closed = int(result.closed or 0)
        violations = int(result.violations or 0)
        open_count = int(result.open or 0)

        return {
            "issued": issued,
            "closed_count": closed,
            "open_count": open_count,
            "pending_count": open_count,
            "violation_count": violations,
            "overdue_count": 0,
            "compliance_rate": round((closed / issued * 100), 1) if issued > 0 else 100.0,
        }

    def get_training_summary(
        self,
        site_id: Optional[str] = None,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Get training completion summary."""
        end_date = date.today()
        start_date = end_date - timedelta(days=period_days)

        query = self.db.query(
            func.sum(FactHSE.training_passed_count).label("passed"),
            func.sum(FactHSE.training_failed_count).label("failed"),
            func.sum(FactHSE.training_pending_count).label("pending"),
        ).filter(
            FactHSE.date_key >= start_date,
            FactHSE.date_key <= end_date,
        )

        if site_id and site_id != "all":
            query = query.filter(FactHSE.site_key == site_id)

        result = query.first()
        passed = int(result.passed or 0)
        failed = int(result.failed or 0)
        pending = int(result.pending or 0)
        total = passed + failed + pending

        return {
            "total_completed": passed,
            "total_pending": pending,
            "total_failed": failed,
            "compliance_rate": round((passed / total * 100), 1) if total > 0 else 0,
            "by_department": {},
        }

    def get_environmental_summary(
        self,
        site_id: Optional[str] = None,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Get environmental monitoring summary."""
        end_date = date.today()
        start_date = end_date - timedelta(days=period_days)

        query = self.db.query(
            FactHSE.env_sample_id,
            FactHSE.env_reading_value,
            FactHSE.env_limit_value,
            FactHSE.env_exceeded,
        ).filter(
            FactHSE.date_key >= start_date,
            FactHSE.date_key <= end_date,
            FactHSE.env_reading_value.is_not(None),
        )

        if site_id and site_id != "all":
            query = query.filter(FactHSE.site_key == site_id)

        results = query.order_by(desc(FactHSE.date_key)).all()

        pm25_readings = [r for r in results if "PM2.5" in (r.env_sample_id or "")]
        latest_pm25 = pm25_readings[0] if pm25_readings else None

        noise_readings = [r for r in results if "Noise" in (r.env_sample_id or "") or "Leq" in (r.env_sample_id or "")]
        latest_noise = noise_readings[0] if noise_readings else None

        exceedances = sum(1 for r in results if r.env_exceeded)

        return {
            "pm25_current": float(latest_pm25.env_reading_value) if latest_pm25 else None,
            "pm25_limit": float(latest_pm25.env_limit_value) if latest_pm25 else None,
            "pm25_status": "normal" if (not latest_pm25 or not latest_pm25.env_exceeded) else "exceeded",
            "noise_current": float(latest_noise.env_reading_value) if latest_noise else None,
            "noise_limit": float(latest_noise.env_limit_value) if latest_noise else None,
            "noise_status": "normal" if (not latest_noise or not latest_noise.env_exceeded) else "exceeded",
            "exceedances": exceedances,
            "total_readings": len(results),
        }

    def get_equipment_summary(
        self,
        site_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get equipment compliance summary."""
        query = self.db.query(DimEquipment).filter(
            DimEquipment.active_to == datetime(9999, 12, 12).date()
        )

        if site_id and site_id != "all":
            query = query.filter(DimEquipment.current_site_id == site_id)

        equipments = query.all()
        now = date.today()

        expired = sum(1 for e in equipments if e.certification_expiry and e.certification_expiry < now)
        valid = len(equipments) - expired
        overdue = sum(1 for e in equipments if e.next_inspection and e.next_inspection < now)

        return {
            "total_equipment": len(equipments),
            "valid_cert": valid,
            "expired_cert": expired,
            "overdue_inspection": overdue,
            "down_count": 0,
        }

    def get_contractor_summary(self) -> Dict[str, Any]:
        """Get contractor performance summary."""
        contractors = self.db.query(DimContractor).filter(
            DimContractor.active_to == datetime(9999, 12, 12).date()
        ).all()

        total = len(contractors)
        passed = sum(1 for c in contractors if c.hse_audit_result == "Passed")
        conditional = sum(1 for c in contractors if c.hse_audit_result == "Conditional")
        failed = sum(1 for c in contractors if c.hse_audit_result == "Failed")

        performance = {}
        for c in contractors:
            base_score = 85 if c.hse_audit_result == "Passed" else 60 if c.hse_audit_result == "Conditional" else 40
            performance[c.contractor_name] = min(100, base_score + 10)

        return {
            "total": total,
            "active": total,
            "passed": passed,
            "conditional": conditional,
            "failed": failed,
            "performance_scores": performance,
        }

