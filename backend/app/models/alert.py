"""
Alert & Notification System Models
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Numeric, ForeignKey, Text, Enum as SQLEnum, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class AlertSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    WARNING = "warning"
    INFO = "info"


class AlertStatus(str, enum.Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


class AlertChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    TELEGRAM = "telegram"
    WEBHOOK = "webhook"
    DASHBOARD = "dashboard"


class MetricType(str, enum.Enum):
    LTIFR = "ltifr"
    TRIR = "trir"
    ENV_PM25 = "env_pm25"
    ENV_NOISE = "env_noise"
    PTW_VIOLATION = "ptw_violation"
    EQUIPMENT_EXPIRED = "equipment_expired"
    TRAINING_EXPIRED = "training_expired"
    NEAR_MISS = "near_miss"
    FATALITY = "fatality"
    CUSTOM = "custom"


class AlertRule(Base):
    __tablename__ = "alert_rules"
    __table_args__ = {"schema": "hse"}

    rule_id = Column(String(50), primary_key=True)
    rule_name = Column(String(200), nullable=False)
    metric_type = Column(SQLEnum(MetricType), nullable=False)
    condition = Column(String(10), nullable=False)  # >, <, >=, <=, ==, !=
    threshold_value = Column(Numeric(15, 4), nullable=False)
    severity = Column(SQLEnum(AlertSeverity), default=AlertSeverity.WARNING)
    site_id = Column(String(20), ForeignKey("hse.dim_site.site_id"))
    department_id = Column(String(20), ForeignKey("hse.dim_department.dept_id"))
    notification_channels = Column(JSONB, default=list)
    recipients = Column(JSONB, default=list)
    is_active = Column(Boolean, default=True)
    cooldown_minutes = Column(Integer, default=60)
    last_triggered_at = Column(DateTime)
    description = Column(Text)
    created_by = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = {"schema": "hse"}

    alert_id = Column(String(50), primary_key=True)
    rule_id = Column(String(50), ForeignKey("hse.alert_rules.rule_id"))
    alert_type = Column(String(100), nullable=False)
    severity = Column(SQLEnum(AlertSeverity), default=AlertSeverity.WARNING)
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.ACTIVE)
    site_id = Column(String(20), ForeignKey("hse.dim_site.site_id"))
    site_name = Column(String(200))
    metric_type = Column(String(50))
    metric_value = Column(Numeric(15, 4))
    threshold_value = Column(Numeric(15, 4))
    message = Column(Text, nullable=False)
    details = Column(JSONB)
    triggered_by = Column(String(200))
    acknowledged_by = Column(String(200))
    acknowledged_at = Column(DateTime)
    resolved_by = Column(String(200))
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    alert_date = Column(Date, default=datetime.utcnow().date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NotificationLog(Base):
    __tablename__ = "notification_logs"
    __table_args__ = {"schema": "hse"}

    log_id = Column(String(50), primary_key=True)
    alert_id = Column(String(50), ForeignKey("hse.alerts.alert_id"))
    channel = Column(SQLEnum(AlertChannel), nullable=False)
    recipient = Column(String(500))
    subject = Column(String(500))
    body = Column(Text)
    status = Column(String(20), default="pending")  # pending, sent, failed, bounced
    error_message = Column(Text)
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


Index("idx_alert_rules_site", AlertRule.site_id)
Index("idx_alert_rules_active", AlertRule.is_active)
Index("idx_alerts_status", Alert.status, Alert.alert_date)
Index("idx_alerts_site", Alert.site_id, Alert.alert_date)
Index("idx_alerts_severity", Alert.severity)
Index("idx_notification_alert", NotificationLog.alert_id)
Index("idx_notification_status", NotificationLog.status)
