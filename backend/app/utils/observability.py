"""
Observability instrumentation for HSE Enterprise Platform.
Provides:
- OpenTelemetry tracing for FastAPI, Celery, SQLAlchemy
- Prometheus metrics
- Structured logging with correlation IDs
- OTLP export to OpenTelemetry Collector
"""

import os
from typing import Optional
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
import logging

from app.config import settings

# Initialize structured logger
logger = logging.getLogger(__name__)

# Prometheus metrics (always available)
REQUEST_COUNT = Counter(
    "hse_api_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"]
)
REQUEST_LATENCY = Histogram(
    "hse_api_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)
ACTIVE_USERS = Gauge(
    "hse_active_users",
    "Number of active user sessions"
)
CELERY_TASK_DURATION = Histogram(
    "hse_celery_task_duration_seconds",
    "Celery task execution duration",
    ["task_name"],
    buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0]
)
DB_QUERY_DURATION = Histogram(
    "hse_db_query_duration_seconds",
    "Database query duration",
    ["query_type"],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)
ETL_DURATION = Histogram(
    "hse_etl_duration_seconds",
    "ETL job duration in seconds",
    ["job_name"],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0]
)
ALERT_COUNT = Counter(
    "hse_alerts_total",
    "Total alerts generated",
    ["alert_type", "severity", "site_id"]
)
ERROR_COUNT = Counter(
    "hse_errors_total",
    "Total application errors",
    ["error_type", "endpoint"]
)

# Try to import OpenTelemetry - optional dependency
try:
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.celery import CeleryInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    from opentelemetry.sdk.resources import Resource

    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    logger.info("OpenTelemetry packages not installed - tracing disabled")


def setup_observability(app=None, celery_app=None, db_engine=None) -> None:
    """
    Initialize observability stack.
    Call this during application startup.
    """
    # Skip if in test mode
    if os.getenv("TESTING") == "true":
        logger.info("Skipping observability setup in test mode")
        return

    if not OPENTELEMETRY_AVAILABLE:
        logger.warning("OpenTelemetry not available - skipping instrumentation")
        return

    # Initialize OpenTelemetry
    resource = Resource.create({
        "service.name": settings.APP_NAME,
        "service.version": settings.APP_VERSION,
        "environment": "production" if not settings.DEBUG else "development",
    })

    # Tracing
    trace_provider = TracerProvider(resource=resource)
    trace_exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
        insecure=True,
    )
    trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
    trace.set_tracer_provider(trace_provider)

    # Metrics
    metric_exporter = OTLPMetricExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
        insecure=True,
    )
    metric_reader = PeriodicExportingMetricReader(metric_exporter, export_interval_millis=15000)
    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[metric_reader]))

    # Instrument FastAPI
    if app:
        FastAPIInstrumentor.instrument_app(app)
        logger.info("FastAPI instrumentation enabled")

    # Instrument Celery
    if celery_app:
        CeleryInstrumentor().instrument()
        logger.info("Celery instrumentation enabled")

    # Instrument SQLAlchemy
    if db_engine:
        SQLAlchemyInstrumentor().instrument(engine=db_engine)
        logger.info("SQLAlchemy instrumentation enabled")

    logger.info("Observability stack initialized")


def get_prometheus_metrics() -> bytes:
    """Generate Prometheus metrics response."""
    return generate_latest(REGISTRY)


def record_request(method: str, endpoint: str, status_code: int, duration: float) -> None:
    """Record API request metrics."""
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)


def record_celery_task(task_name: str, duration: float) -> None:
    """Record Celery task execution metrics."""
    CELERY_TASK_DURATION.labels(task_name=task_name).observe(duration)


def record_db_query(query_type: str, duration: float) -> None:
    """Record database query metrics."""
    DB_QUERY_DURATION.labels(query_type=query_type).observe(duration)


def record_etl_job(job_name: str, duration: float) -> None:
    """Record ETL job duration metrics."""
    ETL_DURATION.labels(job_name=job_name).observe(duration)


def record_alert(alert_type: str, severity: str, site_id: str) -> None:
    """Record alert generation metrics."""
    ALERT_COUNT.labels(alert_type=alert_type, severity=severity, site_id=site_id).inc()


def record_error(error_type: str, endpoint: str) -> None:
    """Record application error metrics."""
    ERROR_COUNT.labels(error_type=error_type, endpoint=endpoint).inc()


def get_tracer(name: str) -> Optional[object]:
    """Get a tracer instance for creating spans."""
    if not OPENTELEMETRY_AVAILABLE:
        return None
    return trace.get_tracer(name)

