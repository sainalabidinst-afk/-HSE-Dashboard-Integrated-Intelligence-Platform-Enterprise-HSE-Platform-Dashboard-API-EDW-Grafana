# Architecture Decision Records (ADR)

**Version:** 2.1  
**Date:** 2026-07-18  
**Status:** Accepted  
**Template:** [ADR-000] Title

---

## ADR-001: API Versioning Strategy

**Date:** 2026-07-18  
**Status:** Accepted  
**Deciders:** Solution Architect, Tech Lead, Security Lead  
**Related:** ADR-002, ADR-005

### Context
The platform currently exposes API routes under `/api/*` without versioning. As the platform evolves, breaking changes to request/response formats, authentication, or business logic are inevitable. Without versioning, any breaking change would impact all existing clients simultaneously, causing outages and requiring coordinated client updates.

### Decision
Add `/v1/` prefix to all API routes, resulting in base path `/api/v1/*`. Future major versions will increment the version number (e.g., `/api/v2/`). This provides:

- **Backward compatibility:** Existing clients continue using `/api/v1/` during migration
- **Parallel operation:** Multiple API versions can coexist during transition
- **Clear migration path:** Clients upgrade at their own pace
- **Standard practice:** Aligns with REST API best practices

### Alternatives Considered
1. **Header-based versioning** (`Accept: application/vnd.hse.v1+json`)
   - Rejected: Less visible, harder to debug, not URL-shareable
2. **URL parameter versioning** (`/api?version=v1`)
   - Rejected: Non-standard, harder to route
3. **No versioning (current)**
   - Rejected: High risk of breaking changes affecting all clients

### Consequences
**Positive:**
- Clean separation of API versions
- Enables gradual client migration
- Supports parallel development of versions
- Industry-standard approach

**Negative:**
- Requires client updates to use new URLs
- Additional routing configuration
- Slightly longer URLs

**Risks:**
- Clients may not update promptly (mitigation: maintain v1 for 6+ months)
- Increased maintenance burden (multiple versions)

### Implementation
1. Update all route definitions to include `/v1/` prefix
2. Update Swagger/OpenAPI documentation
3. Update frontend API client to use `/api/v1/`
4. Maintain v1 for minimum 6 months after v2 release
5. Add deprecation headers to old versions

---

## ADR-002: Database Partitioning Strategy

**Date:** 2026-07-18  
**Status:** Accepted  
**Deciders:** DBA, Solution Architect, Backend Lead  
**Related:** ADR-001, ADR-005

### Context
The `fact_hse` table is the core fact table of the EDW, storing daily HSE metrics across all sites and departments. As the platform scales to 5+ sites and multi-year operations, this table will grow to millions of rows. Without partitioning, query performance will degrade, and data management (archival, deletion) will become complex.

### Decision
Implement **range partitioning** on `fact_hse` by `date_key`, creating monthly partitions. This provides:

- **Improved query performance:** Queries filtered by date only scan relevant partitions
- **Simplified data management:** Old partitions can be archived or dropped efficiently
- **Parallel operations:** Partition-level operations (VACUUM, REINDEX) are faster
- **Scalability:** Supports multi-year data retention without performance degradation

### Alternatives Considered
1. **No partitioning (current)**
   - Rejected: Performance will degrade as data grows
2. **Hash partitioning by site_key**
   - Rejected: Date-range queries still scan all partitions
3. **Hybrid partitioning (date + site)**
   - Rejected: Too complex for current scale, monthly by date is sufficient

### Consequences
**Positive:**
- 10-100x performance improvement for date-filtered queries
- Efficient archival strategy (detach old partitions)
- Simplified data retention compliance

**Negative:**
- Requires partition management logic (auto-create partitions)
- Queries without date filters may be slower
- Requires DBA expertise to maintain

**Risks:**
- Partition management bugs could cause data loss (mitigation: thorough testing)
- Queries without date_key may require constraint exclusion (mitigation: query review)

### Implementation
1. Create partition function and trigger for monthly partitions
2. Migrate existing data to partitioned structure
3. Update application code to ensure date_key is always provided in queries
4. Add partition maintenance job (create next month partition)
5. Archive partitions older than 2 years to `fact_hse_archive`

---

## ADR-003: Caching Strategy

**Date:** 2026-07-18  
**Status:** Accepted  
**Deciders:** Solution Architect, Backend Lead, Platform Lead  
**Related:** ADR-001, ADR-002

### Context
Dashboard summary endpoints (`/api/v1/dashboard/summary`, `/api/v1/dashboard/incidents`, etc.) are read-heavy and compute-intensive, involving aggregations across large fact tables. Without caching, every user request triggers expensive database queries, degrading performance under load.

### Decision
Implement **Redis caching** for dashboard summary endpoints with a **60-second TTL**. This provides:

- **10x performance improvement:** Cached responses served in <10ms vs 100-500ms DB queries
- **Reduced database load:** 80% reduction in dashboard query volume
- **Acceptable staleness:** 60-second TTL is acceptable for HSE dashboards
- **Simple invalidation:** TTL-based invalidation avoids complex cache invalidation logic

### Alternatives Considered
1. **No caching (current)**
   - Rejected: Poor performance under load
2. **CDN caching**
   - Rejected: Dashboard data is user-specific and authenticated
3. **Application-level caching**
   - Rejected: Less scalable, no shared cache across instances
4. **Database materialized views**
   - Rejected: Refresh complexity, less flexible

### Consequences
**Positive:**
- Significant performance improvement
- Reduced database load
- Better user experience

**Negative:**
- Data staleness up to 60 seconds
- Additional infrastructure (Redis)
- Cache invalidation complexity for write operations

**Risks:**
- Stale data during critical incidents (mitigation: manual cache purge endpoint)
- Redis becomes single point of failure (mitigation: Redis Sentinel)

### Implementation
1. Install and configure Redis cluster (primary + replica)
2. Implement cache decorator for dashboard endpoints
3. Set TTL to 60 seconds for summary endpoints
4. Add manual cache purge endpoint for emergency updates
5. Monitor cache hit ratio (target: >80%)
6. Add cache warming for critical dashboards

---

## ADR-004: AI Embedding Strategy

**Date:** 2026-07-18  
**Status:** Accepted  
**Deciders:** AI Lead, Solution Architect, Security Lead  
**Related:** ADR-001, ADR-003

### Context
The AI Safety Assistant uses RAG (Retrieval-Augmented Generation) to answer HSE-related questions. This requires text embeddings for vector search. The platform needs a production-quality embedding solution that balances accuracy, cost, and reliability.

### Decision
Use **OpenAI `text-embedding-3-small`** as the primary embedding model, with a **deterministic mock fallback for development/testing only**. This provides:

- **Production quality:** State-of-the-art embeddings for accurate search
- **Cost control:** `text-embedding-3-small` is cost-effective ($0.02/1M tokens)
- **Development safety:** Mock embeddings enable offline development
- **Fail-hard policy:** Production fails clearly if OpenAI API is unavailable

### Alternatives Considered
1. **Open-source models (Llama, BERT)**
   - Rejected: Lower quality, self-hosting complexity
2. **Azure OpenAI**
   - Rejected: Vendor lock-in, higher cost
3. **Mock embeddings only**
   - Rejected: Meaningless search results in production
4. **No fallback (fail hard always)**
   - Rejected: Prevents development without API access

### Consequences
**Positive:**
- Best-in-class search quality
- Cost-effective at scale
- Supports development offline

**Negative:**
- OpenAI API dependency
- API cost (mitigated by caching and prompt optimization)
- Mock embeddings can mask issues if not properly gated

**Risks:**
- Mock embeddings used in production (mitigation: feature flag, CI check)
- OpenAI API outage (mitigation: fail-hard with clear error)

### Production Policy
**Mock embeddings (`_mock_embedding`) MUST be disabled in production environments.** The application MUST fail with a clear error message if the OpenAI API is unavailable. Mock embeddings are strictly for development and testing environments only, controlled by the `ENABLE_MOCK_EMBEDDINGS` feature flag (default: `false`).

**Implementation:**
1. Set `ENABLE_MOCK_EMBEDDINGS=false` in production environment
2. Add CI check to verify mock embeddings are not used in production code paths
3. Add startup validation to ensure OpenAI API is reachable
4. Log clear error if API unavailable: "OpenAI API unavailable — AI features disabled"
5. Gracefully degrade AI features without crashing the application

---

## ADR-005: Background Task Processing

**Date:** 2026-07-18  
**Status:** Accepted  
**Deciders:** Solution Architect, Backend Lead, DevOps Lead  
**Related:** ADR-001, ADR-002, ADR-003

### Context
The platform requires asynchronous processing for:
- Alert evaluation and notification (email, SMS, Telegram)
- Report generation (PDF, Excel)
- AI tasks (document ingestion, embedding generation)
- Data synchronization (external integrations)

Synchronous processing would block API responses and degrade user experience. A robust background task processing system is needed.

### Decision
Use **Celery with Redis broker**, with **separate queues per domain** (alerts, reports, ai). This provides:

- **Proven reliability:** Celery is battle-tested for production workloads
- **Retry support:** Automatic retries with exponential backoff
- **Monitoring:** Built-in monitoring via Prometheus
- **Scalability:** Workers can be scaled independently per queue
- **Priority separation:** Critical tasks (alerts) can be prioritized

### Alternatives Considered
1. **Dramatiq**
   - Rejected: Smaller ecosystem, less mature
2. **RQ (Redis Queue)**
   - Rejected: Less feature-rich than Celery
3. **In-process async (asyncio)**
   - Rejected: No persistence, no retry, no scaling
4. **AWS SQS / Azure Queue**
   - Rejected: Cloud lock-in, additional cost

### Consequences
**Positive:**
- Reliable task processing with retries
- Scalable worker architecture
- Rich monitoring and debugging
- Supports complex workflows

**Negative:**
- Additional infrastructure (Redis)
- Operational complexity (worker management)
- Learning curve for team

**Risks:**
- Redis becomes bottleneck (mitigation: Redis Sentinel, multiple brokers)
- Task duplication (mitigation: idempotency keys)
- Worker memory leaks (mitigation: worker restart policy)

### Implementation
1. Configure Celery with Redis broker
2. Define queues: `hse-alerts`, `hse-reports`, `hse-ai`, `hse-default`
3. Configure routing by task type
4. Implement retry policy: `max_retries=3, retry_backoff=True`
5. Add dead letter queue for failed tasks
6. Implement idempotency keys for all tasks
7. Set worker concurrency: `--concurrency=4`
8. Add monitoring: Prometheus metrics, Flower dashboard

---

## ADR-006: Security Headers & HTTPS Enforcement

**Date:** 2026-07-18  
**Status:** Proposed  
**Deciders:** Security Lead, Solution Architect, DevOps Lead  
**Related:** ADR-001, ADR-002

### Context
The platform currently lacks comprehensive security headers and HTTPS enforcement. This exposes the application to various attacks including XSS, clickjacking, and MIME-type sniffing. Production deployment requires robust security headers.

### Decision
Implement comprehensive security headers and enforce HTTPS-only in production:

- **Strict-Transport-Security (HSTS):** Enforce HTTPS for 1 year
- **Content-Security-Policy (CSP):** Prevent XSS and data injection
- **X-Frame-Options:** Prevent clickjacking
- **X-Content-Type-Options:** Prevent MIME sniffing
- **Referrer-Policy:** Control referrer information
- **Permissions-Policy:** Restrict browser features

### Alternatives Considered
1. **No security headers (current)**
   - Rejected: Vulnerable to XSS, clickjacking
2. **CSP only**
   - Rejected: Insufficient protection
3. **Third-party security middleware**
   - Rejected: Additional dependency, less control

### Consequences
**Positive:**
- Comprehensive protection against common attacks
- Compliance with security standards
- Improved security posture

**Negative:**
- Requires testing and tuning of CSP
- May break some functionality if not properly configured
- Additional configuration overhead

### Implementation
1. Add security headers middleware to FastAPI
2. Configure CSP with appropriate directives
3. Enforce HTTPS-only in production
4. Test headers with security scanning tools
5. Document exceptions and justifications

---

## ADR-007: Database Connection Pooling Strategy

**Date:** 2026-07-18  
**Status:** Proposed  
**Deciders:** DBA, Solution Architect, Backend Lead  
**Related:** ADR-002, ADR-003

### Context
The platform uses SQLAlchemy's default connection pooling settings. As the platform scales to 100+ concurrent users, connection pool exhaustion may occur, leading to degraded performance or service interruptions.

### Decision
Implement **optimized connection pooling** with the following configuration:

- **Pool size:** 10 connections (base)
- **Max overflow:** 20 connections (burst capacity)
- **Pool recycle:** 3600 seconds (prevent stale connections)
- **Pool pre-ping:** Enabled (detect broken connections)
- **Checkout timeout:** 30 seconds (fail fast)

### Alternatives Considered
1. **Default SQLAlchemy settings**
   - Rejected: Not optimized for production load
2. **Unbounded pool**
   - Rejected: Risk of database overload
3. **External connection pooler (PgBouncer)**
   - Rejected: Additional infrastructure, not needed at current scale

### Consequences
**Positive:**
- Stable performance under load
- Prevents connection exhaustion
- Automatic recovery from network issues

**Negative:**
- Requires tuning as load patterns change
- Additional memory usage for connection pool

### Implementation
1. Update `database.py` with optimized pool settings
2. Monitor pool utilization in production
3. Adjust pool size based on actual usage patterns
4. Add alerts for pool exhaustion

---

*Document End*
