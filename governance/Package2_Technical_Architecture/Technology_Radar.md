# Technology Radar

**Version:** 2.1  
**Date:** 2026-07-18  
**Owner:** Enterprise Architect  
**Review Cycle:** Quarterly  
**Status:** Approved

---

## Purpose

This Technology Radar provides a snapshot of the technology choices for the Enterprise HSE Platform. It helps teams make consistent technology decisions and signals industry direction.

---

## Radar Summary

| Quadrant | Count | Description |
|----------|-------|-------------|
| **Adopt** | 8 | Proven technologies we should use confidently |
| **Trial** | 6 | Technologies worth pursuing with limited scope |
| **Assess** | 5 | Technologies to evaluate for future use |
| **Hold** | 3 | Technologies to use with caution or phase out |

---

## Adopt

Technologies we have high confidence in, proven in production, and recommend for widespread use.

| Technology | Domain | Adoption Target | Notes |
|------------|--------|-----------------|-------|
| FastAPI | Backend Framework | Q3 2024 | Primary API framework; async support, auto-docs, type hints |
| SQLAlchemy 2.0 | ORM | Q3 2024 | Core data access; 2.0 async style adopted |
| PostgreSQL 15 | Database | Q3 2024 | Primary EDW; pgvector for AI embeddings |
| Docker Compose | Container Orchestration | Q3 2024 | Local and production deployment standard |
| Pydantic v2 | Validation | Q3 2024 | Request/response schemas, settings management |
| Redis 7 | Cache/Broker | Q3 2024 | Caching, rate limiting, Celery broker |
| Celery 5.3 | Task Queue | Q3 2024 | Async processing: ETL, alerts, reports |
| OpenTelemetry | Observability | Q4 2024 | Traces, metrics, logs; vendor-neutral |

---

## Trial

Technologies worth pursuing in limited scope to understand their applicability.

| Technology | Domain | Adoption Target | Notes |
|------------|--------|-----------------|-------|
| Grafana | Visualization | Q4 2024 | Operational dashboards; replacing custom charts |
| Loki | Log Aggregation | Q4 2024 | Centralized logging with Promtail |
| Tempo | Distributed Tracing | Q4 2024 | Trace storage and visualization |
| Prometheus | Metrics | Q4 2024 | Metrics collection and alerting |
| PgBouncer | Connection Pooler | Q1 2025 | Evaluate for high-concurrency scenarios |
| GitHub Actions | CI/CD | Q1 2025 | Pipeline automation; replacing manual scripts |

---

## Assess

Technologies to evaluate for future adoption; not yet production-ready for our use case.

| Technology | Domain | Adoption Target | Notes |
|------------|--------|-----------------|-------|
| GraphQL | API Layer | Q2 2025 | Evaluate for mobile/SPA clients; reduces over-fetching |
| Kafka | Event Streaming | Q2 2025 | Real-time event pipeline for IoT/SCADA integration |
| Kubernetes | Container Orchestration | Q3 2025 | Evaluate for multi-service scaling beyond Compose |
| Rust | Performance-Critical Services | Q3 2025 | Evaluate for high-throughput ETL or edge processing |
| MLflow | Model Management | Q4 2025 | AI model registry and deployment tracking |

---

## Hold

Technologies to use with caution, avoid for new development, or phase out.

| Technology | Domain | Rationale | Migration Path |
|------------|--------|-----------|----------------|
| Mock Embeddings (production) | AI | Security risk; non-deterministic in production; violates ADR-004 | Remove in Sprint 0; use real OpenAI embeddings |
| Plain JWT without jti | Auth | Vulnerable to replay attacks; no revocation mechanism | Add jti validation in Sprint 0 |
| Synchronous DB Queries | Performance | Blocks event loop; poor scalability | Migrate to async SQLAlchemy in Sprint 1 |

---

## Technology Selection Criteria

New technology adoption requires:

1. **Proof of Concept:** 2-4 week trial with measurable outcomes
2. **Security Review:** Security team sign-off
3. **Cost Analysis:** TCO over 3 years including licensing, training, operations
4. **Team Capability:** Existing team skills or training plan
5. **Viability:** Vendor health, community support, roadmap alignment
6. **Exit Strategy:** Migration path if technology fails

---

## Lifecycle Management

| Stage | Criteria | Action |
|-------|----------|--------|
| **Adopt** | Production-ready, team trained, documented | Use for new features |
| **Trial** | PoC complete, value demonstrated | Expand scope gradually |
| **Assess** | Initial research complete | Conduct PoC |
| **Hold** | Risk identified, replacement available | Plan migration, stop new use |

---

## Related Documents

- `Architecture_Principles_Catalog.md` — Principles governing technology choices
- `Architecture_Decision_Records.md` — Detailed ADRs for key technology decisions
- `Technical_Architecture_Audit.md` — Domain-specific technology assessments

---

*Document End*
