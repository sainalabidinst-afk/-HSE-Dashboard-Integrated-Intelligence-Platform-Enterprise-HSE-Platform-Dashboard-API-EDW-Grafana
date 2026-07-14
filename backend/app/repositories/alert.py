"""
Alert & Notification Repositories
"""

from typing import Optional, List, Dict, Any
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
import uuid

from app.models.alert import AlertRule, Alert, NotificationLog
from app.models.hse_models import FactHSE, DimSite, DimEquipment, DimTraining


class AlertRepository:
    """Repository for alert rules and alerts."""

    def __init__(self, db: Session):
        self.db = db

    def get_alert_rules(self, site_id: Optional[str] = None, is_active: Optional[bool] = None) -> List[Dict]:
        query = self.db.query(AlertRule)
        if site_id and site_id != "all":
            query = query.filter(AlertRule.site_id == site_id)
        if is_active is not None:
            query = query.filter(AlertRule.is_active == is_active)
        results = query.order_by(AlertRule.rule_name).all()
        return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in results]

    def get_alert_rule(self, rule_id: str) -> Optional[AlertRule]:
        return self.db.query(AlertRule).filter(AlertRule.rule_id == rule_id).first()

    def create_alert_rule(self, data: Dict) -> AlertRule:
        rule = AlertRule(
            rule_id=str(uuid.uuid4()),
            **data
        )
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def update_alert_rule(self, rule_id: str, data: Dict) -> Optional[AlertRule]:
        rule = self.get_alert_rule(rule_id)
        if not rule:
            return None
        for key, value in data.items():
            if value is not None and hasattr(rule, key):
                setattr(rule, key, value)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def get_alerts(self, site_id: Optional[str] = None, status: Optional[str] = None, severity: Optional[str] = None, limit: int = 100) -> List[Dict]:
        query = self.db.query(Alert)
        if site_id and site_id != "all":
            query = query.filter(Alert.site_id == site_id)
        if status:
            query = query.filter(Alert.status == status)
        if severity:
            query = query.filter(Alert.severity == severity)
        results = query.order_by(desc(Alert.created_at)).limit(limit).all()
        return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in results]

    def get_alert(self, alert_id: str) -> Optional[Alert]:
        return self.db.query(Alert).filter(Alert.alert_id == alert_id).first()

    def create_alert(self, data: Dict) -> Alert:
        alert = Alert(
            alert_id=str(uuid.uuid4()),
            **data
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def acknowledge_alert(self, alert_id: str, user_email: str) -> Optional[Alert]:
        alert = self.get_alert(alert_id)
        if not alert:
            return None
        alert.status = "acknowledged"
        alert.acknowledged_by = user_email
        alert.acknowledged_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def resolve_alert(self, alert_id: str, user_email: str, notes: str = None) -> Optional[Alert]:
        alert = self.get_alert(alert_id)
        if not alert:
            return None
        alert.status = "resolved"
        alert.resolved_by = user_email
        alert.resolved_at = datetime.utcnow()
        alert.resolution_notes = notes
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def log_notification(self, data: Dict) -> NotificationLog:
        log = NotificationLog(
            log_id=str(uuid.uuid4()),
            **data
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_notification_logs(self, alert_id: Optional[str] = None, status: Optional[str] = None, limit: int = 50) -> List[NotificationLog]:
        query = self.db.query(NotificationLog)
        if alert_id:
            query = query.filter(NotificationLog.alert_id == alert_id)
        if status:
            query = query.filter(NotificationLog.status == status)
        return query.order_by(desc(NotificationLog.created_at)).limit(limit).all()

    def evaluate_rules(self) -> List[Dict]:
        """Evaluate all active alert rules and return triggered alerts."""
        triggered = []
        rules = self.db.query(AlertRule).filter(AlertRule.is_active == True).all()
        today = date.today()
        for rule in rules:
            if rule.last_triggered_at and (datetime.utcnow() - rule.last_triggered_at).total_seconds() < (rule.cooldown_minutes or 60) * 60:
                continue
            metric_value = self._get_metric_value(rule.metric_type, rule.site_id)
            if metric_value is None:
                continue
            triggered_val = self._evaluate_condition(metric_value, rule.condition, float(rule.threshold_value))
            if triggered_val:
                alert_data = {
                    "rule_id": rule.rule_id,
                    "alert_type": rule.metric_type.value if hasattr(rule.metric_type, 'value') else str(rule.metric_type),
                    "severity": rule.severity,
                    "site_id": rule.site_id,
                    "site_name": self._get_site_name(rule.site_id),
                    "metric_type": str(rule.metric_type),
                    "metric_value": metric_value,
                    "threshold_value": float(rule.threshold_value),
                    "message": self._build_alert_message(rule, metric_value),
                    "triggered_by": "system",
                    "alert_date": today,
                }
                rule.last_triggered_at = datetime.utcnow()
                self.db.commit()
                triggered.append(alert_data)
        return triggered

    def _get_metric_value(self, metric_type, site_id: Optional[str]) -> Optional[float]:
        try:
            mt = metric_type.value if hasattr(metric_type, 'value') else str(metric_type)
        except Exception:
            mt = str(metric_type)
        end_date = date.today()
        start_date = end_date
        query = self.db.query(func.sum(FactHSE.lti_count)).filter(FactHSE.date_key == start_date)
        if site_id and site_id != "all":
            query = query.filter(FactHSE.site_key == site_id)
        if mt == "ltifr":
            man_hours = self.db.query(func.sum(FactHSE.man_hours_worked)).filter(FactHSE.date_key == start_date)
            if site_id and site_id != "all":
                man_hours = man_hours.filter(FactHSE.site_key == site_id)
            mh = man_hours.scalar() or 0
            lti = query.scalar() or 0
            return (lti * 1_000_000) / mh if mh > 0 else 0
        elif mt == "trir":
            man_hours = self.db.query(func.sum(FactHSE.man_hours_worked)).filter(FactHSE.date_key == start_date)
            if site_id and site_id != "all":
                man_hours = man_hours.filter(FactHSE.site_key == site_id)
            mh = man_hours.scalar() or 0
            lti = self.db.query(func.sum(FactHSE.lti_count)).filter(FactHSE.date_key == start_date)
            mti = self.db.query(func.sum(FactHSE.mti_count)).filter(FactHSE.date_key == start_date)
            fai = self.db.query(func.sum(FactHSE.fai_count)).filter(FactHSE.date_key == start_date)
            if site_id and site_id != "all":
                lti = lti.filter(FactHSE.site_key == site_id)
                mti = mti.filter(FactHSE.site_key == site_id)
                fai = fai.filter(FactHSE.site_key == site_id)
            total = (lti.scalar() or 0) + (mti.scalar() or 0) + (fai.scalar() or 0)
            return (total * 200_000) / mh if mh > 0 else 0
        elif mt in ("env_pm25", "env_noise"):
            return None
        elif mt == "ptw_violation":
            val = query.scalar() or 0
            return float(val)
        elif mt == "equipment_expired":
            eq_query = self.db.query(DimEquipment).filter(DimEquipment.active_to == date(9999, 12, 12))
            if site_id and site_id != "all":
                eq_query = eq_query.filter(DimEquipment.current_site_id == site_id)
            return float(sum(1 for e in eq_query.all() if e.certification_expiry and e.certification_expiry < date.today()))
        elif mt == "near_miss":
            val = query.scalar() or 0
            return float(val)
        return None

    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        ops = {
            ">": value > threshold,
            "<": value < threshold,
            ">=": value >= threshold,
            "<=": value <= threshold,
            "==": value == threshold,
            "!=": value != threshold,
        }
        return ops.get(condition, False)

    def _get_site_name(self, site_id: Optional[str]) -> Optional[str]:
        if not site_id or site_id == "all":
            return "All Sites"
        site = self.db.query(DimSite).filter(DimSite.site_id == site_id).first()
        return site.site_name if site else site_id

    def _build_alert_message(self, rule: AlertRule, value: float) -> str:
        return f"{rule.rule_name}: current value {round(value, 2)} {'>' if rule.condition == '>' else '<'} threshold {rule.threshold_value}"
