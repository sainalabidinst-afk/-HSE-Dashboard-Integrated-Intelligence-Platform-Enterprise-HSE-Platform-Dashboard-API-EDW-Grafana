# Enterprise HSE Platform — Operations Architecture

## Backup & Recovery Flow

```mermaid
flowchart TD
    Start[Start Backup] --> CheckEnv{Environment?}
    CheckEnv -->|Production| Verify[Verify Backup Directory]
    CheckEnv -->|Dev/Test| Skip[Skip Backup]
    
    Verify --> Lock[Lock Database Connections]
    Lock --> Dump[pg_dump with compression]
    Dump --> Encrypt[Encrypt backup file]
    Encrypt --> Checksum[Generate checksum]
    Checksum --> Store[Store in backup directory]
    Store --> Upload[Upload to offsite storage]
    Upload --> Unlock[Unlock database]
    Unlock --> Verify2[Verify backup integrity]
    Verify2 --> Log[Log backup status]
    Log --> End[End]
    
    Skip --> End
    
    style Start fill:#2e7d32,color:#fff
    style End fill:#2e7d32,color:#fff
    style Verify2 fill:#f57c00,color:#fff
```

**Recovery Flow:**

```mermaid
flowchart TD
    Start[Recovery Initiated] --> Assess[Assess failure scope]
    Assess --> Decision{Recovery Strategy?}
    
    Decision -->|Point-in-time| PITR[Point-in-time recovery]
    Decision -->|Full restore| Full[Full database restore]
    Decision -->|Partial restore| Partial[Table-level restore]
    
    PITR --> StopAPI[Stop API services]
    Full --> StopAPI
    Partial --> StopAPI
    
    StopAPI --> Restore[Restore from backup]
    Restore --> Verify[Verify data integrity]
    Verify --> Migrate[Run pending migrations]
    Migrate --> Seed[Seed required data]
    Seed --> StartAPI[Start API services]
    StartAPI --> HealthCheck{Run health checks}
    
    HealthCheck -->|Pass| Notify[Notify stakeholders]
    HealthCheck -->|Fail| Rollback[Rollback to previous state]
    
    Notify --> End[Recovery complete]
    Rollback --> End
    
    style Start fill:#c62828,color:#fff
    style End fill:#2e7d32,color:#fff
    style Rollback fill:#f57c00,color:#fff
```

---

## Incident Response Flow

```mermaid
flowchart TD
    Start[Incident Detected] --> Triage[Triage & Classify]
    Triage --> Severity{Severity?}
    
    Severity -->|P1 Critical| P1[Immediate response\n15 min]
    Severity -->|P2 High| P2[1 hour response]
    Severity -->|P3 Medium| P3[4 hour response]
    Severity -->|P4 Low| P4[24 hour response]
    
    P1 --> Assign[Assign incident commander]
    P2 --> Assign
    P3 --> Assign
    P4 --> Assign
    
    Assign --> Contain[Contain incident]
    Contain --> Mitigate[Mitigate impact]
    Mitigate --> Resolve[Resolve root cause]
    Resolve --> Verify[Verify resolution]
    Verify --> Document[Document incident]
    Document --> Review[Post-mortem review]
    Review --> Action[Action items]
    Action --> End[Incident closed]
    
    style Start fill:#c62828,color:#fff
    style End fill:#2e7d32,color:#fff
    style P1 fill:#c62828,color:#fff
    style P2 fill:#f57c00,color:#fff
```

---

## Runbook Structure

### 1. Incident Runbook
**Trigger:** Monitoring alert or user report  
**Owner:** On-call engineer  
**Steps:**
1. Acknowledge alert in PagerDuty
2. Assess severity (P1-P4)
3. Check Grafana dashboard for metrics
4. Check Loki for error logs
5. Check Tempo for trace analysis
6. Identify root cause
7. Implement mitigation or rollback
8. Update stakeholders
9. Document in incident tracker
10. Schedule post-mortem if P1/P2

### 2. Deployment Runbook
**Trigger:** Scheduled deployment or hotfix  
**Owner:** DevOps engineer  
**Steps:**
1. Verify pre-deployment checklist
2. Deploy to green environment
3. Run smoke tests
4. Switch traffic (blue → green)
5. Monitor for 15 minutes
6. Keep blue as rollback for 1 hour
7. Decommission blue after validation

### 3. Backup Restore Runbook
**Trigger:** Data loss or corruption  
**Owner:** DBA  
**Steps:**
1. Stop API services
2. Identify latest valid backup
3. Restore database from backup
4. Verify table counts and row counts
5. Run pending migrations
6. Start API services
7. Run health checks
8. Notify stakeholders

### 4. Security Incident Runbook
**Trigger:** Security alert or vulnerability discovery  
**Owner:** Security Lead  
**Steps:**
1. Isolate affected systems
2. Preserve evidence (logs, snapshots)
3. Assess scope of compromise
4. Patch vulnerability
5. Rotate compromised credentials
6. Notify security team
7. Document in security incident tracker
8. Conduct post-mortem
9. Update security controls

---

*Document End*
