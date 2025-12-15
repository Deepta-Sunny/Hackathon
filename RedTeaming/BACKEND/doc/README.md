# Documentation Index

## AI Red Teaming Platform - Technical Documentation

Welcome to the comprehensive documentation for the AI Red Teaming Platform. This index provides navigation to all available documentation.

---

## Quick Navigation

| Document | Description | Audience |
|----------|-------------|----------|
| [01 - High-Level Design](./01_HIGH_LEVEL_DESIGN.md) | System overview, architecture, and technology stack (Updated Dec 2025) | All stakeholders |
| [02 - Low-Level Design](./02_LOW_LEVEL_DESIGN.md) | Detailed technical specifications and class designs | Developers |
| [03 - Architecture Decision Records](./03_ARCHITECTURE_DECISION_RECORDS.md) | Design decisions and rationale | Architects, Tech Leads |
| [04 - C4 Diagrams](./04_C4_DIAGRAMS.md) | Visual architecture at multiple levels | All technical staff |
| [05 - Sequence Diagrams](./05_SEQUENCE_DIAGRAMS.md) | Process flows and interactions | Developers |
| [06 - Functional Documentation](./06_FUNCTIONAL_DOCUMENTATION.md) | Business functionality guide | Non-technical stakeholders |
| [07 - Attack Modes Guide](./07_ATTACK_MODES_GUIDE.md) | Standard, Crescendo, Skeleton Key, Obfuscation | Security Engineers |
| [08 - Frontend Architecture](./08_FRONTEND_ARCHITECTURE.md) | React/Redux/TypeScript frontend details | Frontend Developers |

**Attack-Specific Documentation:**
- [Crescendo Attack Guide](./attack_modes/CRESCENDO.md) - Personality-based social engineering
- [Skeleton Key Attack Guide](./attack_modes/SKELETON_KEY.md) - Jailbreak and system probes
- [Obfuscation Attack Guide](./attack_modes/OBFUSCATION.md) - Filter bypass techniques
- [Standard Attack Guide](./attack_modes/STANDARD.md) - Multi-phase reconnaissance to exploitation

**Latest Updates (Dec 15, 2025):**
- Frontend migrated to React 19 + TypeScript with Redux Toolkit
- WebSocket lifecycle improvements (memory leak fixes)
- Material-UI and Recharts for rich visualization
- Real-time reporting with vulnerability scoring
- **Fixed: Skeleton Key & Obfuscation WebSocket broadcasts** (turn_started/turn_completed)
- **Consolidated documentation** from /doc and /docs folders
- Attack mode documentation organized under /doc/attack_modes/

---

## Document Overview

### 01 - High-Level Design (HLD)

**Purpose:** Provides a bird's-eye view of the entire system.

**Contents:**
- Executive summary and business objectives
- System context diagram
- High-level architecture overview
- Core component descriptions
- Technology stack summary
- Security and scalability considerations
- Integration points
- Deployment architecture

**Best for:** Understanding what the system does and how it fits into the organization.

---

### 02 - Low-Level Design (LLD)

**Purpose:** Detailed technical specifications for implementation and maintenance.

**Contents:**
- Module structure and directory layout
- Data model specifications with class diagrams
- API endpoint specifications
- Component class designs
- Method signatures and parameters
- Error handling strategies
- Configuration system details
- Output formats

**Best for:** Developers implementing features or debugging issues.

---

### 03 - Architecture Decision Records (ADR)

**Purpose:** Documents key architectural decisions and their reasoning.

**Decisions Documented:**
- ADR-001: FastAPI as Backend Framework
- ADR-002: WebSocket for Real-Time Communication
- ADR-003: PyRIT Integration for Memory Management
- ADR-004: Multi-Orchestrator Architecture
- ADR-005: Azure OpenAI for Attack Generation
- ADR-006: DuckDB for Local Persistence
- ADR-007: Three-Tier Memory Architecture
- ADR-008: Strategy Library Pattern
- ADR-009: React + Redux Toolkit Frontend (Dec 10, 2025)
- ADR-010: WebSocket Lifecycle Management Fixes (Dec 15, 2025)

**Best for:** Understanding why specific technologies and patterns were chosen.

---

### 04 - C4 Diagrams

**Purpose:** Visual representation of architecture using the C4 model.

**Diagram Levels:**
- Level 1: System Context - External actors and systems
- Level 2: Container - Major applications and data stores
- Level 3: Component - Internal structure of containers
- Level 4: Code - Detailed class/function level (selected areas)

**Includes:**
- System context diagram
- Container diagram
- Backend component diagram
- Orchestrator component diagram
- Memory system component diagram
- Risk analysis code diagram
- Deployment diagram
- Data flow diagram

**Best for:** Visual learners and architecture presentations.

---

### 05 - Sequence Diagrams

**Purpose:** Shows how components interact over time.

**Flows Documented:**
- Complete attack campaign lifecycle
- Single attack turn execution
- Attack plan generation with fallback
- Risk analysis process
- Memory system operations
- Cross-run learning flow
- WebSocket communication
- Crescendo attack specialization
- Error recovery flows

**Best for:** Understanding process flows and debugging timing issues.

---

### 06 - Functional Documentation

**Purpose:** Explains system functionality for non-technical audiences.

**Contents:**
- Plain-language system explanation
- Business process flows
- Feature descriptions with benefits
- Risk scoring explanation
- Compliance and governance support
- ROI analysis
- Getting started guide
- Key metrics and KPIs

**Best for:** Stakeholders, managers, and compliance officers.

---

## Diagram Rendering

All diagrams in this documentation use **Mermaid.js** format. To view diagrams:

1. **GitHub/GitLab:** Diagrams render automatically
2. **VS Code:** Install "Markdown Preview Mermaid Support" extension
3. **Online:** Use [Mermaid Live Editor](https://mermaid.live/)
4. **Documentation Tools:** Most modern tools support Mermaid

---

## Contributing to Documentation

When updating documentation:

1. Follow existing formatting conventions
2. Use Mermaid.js for diagrams (alphanumeric and underscores only for labels)
3. Update this index if adding new documents
4. Include version and date information
5. Consider both technical and non-technical audiences

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | December 15, 2025 | Updated for React/TypeScript frontend, WebSocket fixes |
| 1.0 | December 2025 | Initial comprehensive documentation |

---

## Contact

For documentation questions or updates, contact the Red Team Development team.
