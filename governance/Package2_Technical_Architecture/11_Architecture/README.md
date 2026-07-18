# Architecture Views

**Version:** 2.1  
**Date:** 2026-07-18  
**Purpose:** Visual architecture specifications for Enterprise HSE Platform

---

## How to Use This Folder

This folder contains architecture diagrams in multiple formats:

1. **PlantUML** (`.puml` files) — Render using PlantUML CLI, VS Code extension, or online renderer
2. **Mermaid** (`.mmd` files) — Render using Mermaid CLI, GitHub Markdown, or online renderer
3. **Markdown** (`.md` files) — Text-based diagrams and descriptions

### Rendering Tools

**PlantUML:**
- VS Code: Install "PlantUML" extension
- CLI: `java -jar plantuml.jar diagram.puml`
- Online: https://www.plantuml.com/plantuml

**Mermaid:**
- VS Code: Install "Markdown Preview Mermaid" extension
- CLI: `npx @mermaid-js/mermaid-cli diagram.mmd`
- GitHub: Automatically rendered in Markdown files

---

## Directory Structure

```
11_Architecture/
├── README.md                           # This file
├── Executive/
│   └── context_diagram.puml            # C4 Level 1: Context diagram
├── Solution/
│   ├── container_diagram.puml          # C4 Level 2: Container diagram
│   └── component_diagram.puml          # C4 Level 3: Component diagram (API layer)
├── Infrastructure/
│   ├── deployment_diagram.puml         # C4 Level 4: Deployment diagram
│   └── network_zones.puml              # Network zones and trust boundaries
├── Security/
│   └── threat_model.puml               # STRIDE threat model
├── Data/
│   ├── erd_diagram.puml                # Simplified ERD
│   └── data_flow_diagram.md            # Data flow diagrams (DFD)
├── Integration/
│   ├── integration_landscape.puml      # Integration landscape matrix
│   └── sequence_diagram.puml           # Integration sequence diagram
└── Operations/
    └── operations_architecture.md      # Backup/recovery and incident response flows
```

---

## Diagram Index

### Executive
- **Context Diagram** (`context_diagram.puml`): C4 Level 1 showing users, external systems, and platform boundaries

### Solution
- **Container Diagram** (`container_diagram.puml`): C4 Level 2 showing major containers (API, workers, databases, observability)
- **Component Diagram** (`component_diagram.puml`): C4 Level 3 showing internal structure of FastAPI backend

### Infrastructure
- **Deployment Diagram** (`deployment_diagram.puml`): C4 Level 4 showing Docker containers, volumes, and network connections
- **Network Zones** (`network_zones.puml`): Trust boundaries, security zones, and firewall rules

### Security
- **Threat Model** (`threat_model.puml`): STRIDE analysis per component with mitigations

### Data
- **ERD** (`erd_diagram.puml`): Simplified entity relationship diagram showing all major tables
- **Data Flow Diagram** (`data_flow_diagram.md`): Level 0-2 DFDs showing data movement through the platform

### Integration
- **Integration Landscape** (`integration_landscape.puml`): All external systems, protocols, and integration patterns
- **Sequence Diagram** (`sequence_diagram.puml`): Integration flows for SAP, HRIS, SCADA, Power BI, etc.

### Operations
- **Operations Architecture** (`operations_architecture.md`): Backup/recovery flow, incident response flow, runbook structure

---

## Rendering Examples

### PlantUML Example
```bash
# Using PlantUML CLI
java -jar plantuml.jar context_diagram.puml

# Output: context_diagram.png
```

### Mermaid Example
```bash
# Using Mermaid CLI
npx @mermaid-js/mermaid-cli diagram.mmd -o diagram.png
```

---

## Maintenance

- **Update frequency:** Quarterly or after major architecture changes
- **Owner:** Solution Architect
- **Review:** Architecture Review Board (ARB)
- **Versioning:** Align with document version (currently 2.1)

---

*Document End*
