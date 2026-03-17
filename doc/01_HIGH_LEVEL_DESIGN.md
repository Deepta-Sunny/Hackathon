# High-Level Design (HLD)
## AI Red Teaming Attack Orchestration Platform

**Version:** 2.0.0
**Last Updated:** February 28, 2026
**Document Status:** Active — Regenerated from source code

---

## 1. Executive Summary

### 1.1 What Does This System Do?

The **AI Red Teaming Attack Orchestration Platform** is an automated security testing framework that evaluates the safety and robustness of AI-powered chatbots. Think of it as an "ethical hacker" for AI systems — it tries to trick a chatbot into doing things it should not, records every finding, and reports everything it discovered.

**In plain terms:**
- You point the tool at any chatbot (connected via WebSocket)
- It runs hundreds of crafted attack conversations automatically
- Every response is classified for risk (Safe to Critical)
- The tool adapts its strategies based on what works, like a learning attacker
- You get a detailed report of every vulnerability discovered

### 1.2 Business Purpose

| Goal | Description |
|------|-------------|
| Security Assessment | Find weaknesses before real attackers do |
| Compliance Validation | Verify AI safety guardrails work correctly |
| Vulnerability Discovery | Identify policy bypass, data leakage, and injection risks |
| Risk Quantification | Score vulnerabilities by severity across multiple attack vectors |

### 1.3 Who Uses This System?

- **Security Engineers** — Set up and launch attack campaigns
- **Compliance Analysts** — Review vulnerability reports for policy gaps
- **AI Developers** — Use findings to harden chatbot guardrails
- **Non-Technical Stakeholders** — Read executive summaries and risk dashboards

---

## 2. System Architecture

### 2.1 Architectural Style

The system is built on a layered, event-driven microservices architecture:

- REST API plus WebSocket Server for external communication
- Async Python asyncio for concurrent attack execution
- Pluggable Orchestrator Pattern for swappable attack strategies
- DuckDB Persistent Memory for cross-run learning

### 2.2 High-Level System Map

```mermaid
graph TB
    subgraph User_Facing
        DASH[Web_Dashboard]
        ANALYST[Security_Analyst]
    end

    subgraph API_Layer
        API[FastAPI_Server]
        WSM[WebSocket_Manager]
    end

    subgraph Orchestration_Layer
        STD[Standard_Orchestrator]
        CRSC[Crescendo_Orchestrator]
        SKEL[Skeleton_Key_Orchestrator]
        OBFS[Obfuscation_Orchestrator]
    end

    subgraph Attack_Strategy_Layer
        RECON[Reconnaissance]
        TRUST[Trust_Building]
        BOUND[Boundary_Testing]
        EXPLOIT[Exploitation]
        OBFSTRAT[Obfuscation_Strategies]
        ADAPTIVE[Adaptive_Response_Handler]
    end

    subgraph Core_Services
        AZURE[Azure_OpenAI_GPT4o]
        WSTARGET[WebSocket_Target]
        MEM[Memory_Manager]
        PYRIT[PyRIT_Seed_Loader]
    end

    subgraph Data_Layer
        DB[(DuckDB)]
        JSONF[JSON_Results]
    end

    subgraph Target_System
        BOT[Target_Chatbot]
        AIGINDIA[Air_India_Aig_Middleware]
    end

    ANALYST --> DASH
    DASH -->|REST| API
    DASH <-->|WebSocket| WSM

    API --> STD
    API --> CRSC
    API --> SKEL
    API --> OBFS

    STD --> RECON
    STD --> TRUST
    STD --> BOUND
    STD --> EXPLOIT
    STD --> ADAPTIVE

    CRSC --> TRUST
    CRSC --> ADAPTIVE
    SKEL --> EXPLOIT
    SKEL --> ADAPTIVE
    OBFS --> OBFSTRAT
    OBFS --> ADAPTIVE

    RECON --> AZURE
    TRUST --> AZURE
    BOUND --> AZURE
    EXPLOIT --> AZURE
    OBFSTRAT --> AZURE

    STD --> WSTARGET
    CRSC --> WSTARGET
    SKEL --> WSTARGET
    OBFS --> WSTARGET

    WSTARGET --> BOT
    WSTARGET --> AIGINDIA

    STD --> MEM
    CRSC --> MEM
    SKEL --> MEM
    OBFS --> MEM

    PYRIT --> STD
    PYRIT --> CRSC
    PYRIT --> SKEL
    PYRIT --> OBFS

    MEM --> DB
    STD --> JSONF
    CRSC --> JSONF
    SKEL --> JSONF
    OBFS --> JSONF
```

---

## 3. Core Components

### 3.1 API Server (api_server.py)

The nerve center of the platform. Handles all HTTP and WebSocket traffic.

**Responsibilities:**
- Expose REST endpoints for attack lifecycle control (start, stop, status)
- Accept chatbot profile configurations (domain, capabilities, boundaries)
- Accept architecture file uploads for context-aware testing
- Broadcast real-time attack events to all connected dashboards
- Coordinate all four orchestrators and collect final results

**Technology:** FastAPI + Python asyncio + CORS middleware

---

### 3.2 Attack Orchestrators

The platform contains four independent attack orchestrators, each implementing a distinct attack philosophy:

| Orchestrator | Technique | Turns x Runs | Strategy |
|---|---|---|---|
| Standard | Multi-phase escalation | 15 x 3 | Recon to Trust to Boundary to Exploit |
| Crescendo | Personality-based social engineering | 15 x 3 | Emotional narratives, gradual escalation |
| Skeleton Key | Jailbreak and system bypass | 10 x 3 | Direct override, role assignment, authority claims |
| Obfuscation | Encoding and evasion | 20 x 3 | Encoding, language mixing, semantic camouflage |

All orchestrators share:
- Azure OpenAI for prompt generation and risk analysis
- WebSocket Target for chatbot communication
- DuckDB Memory for persistent learning across runs
- Adaptive Response Handler for conversation-aware pivoting

---

### 3.3 Attack Strategy Layer

Library of ten attack category strategies providing ready-to-use prompts:

```mermaid
graph LR
    STRAT[Attack_Strategy_Library]
    STRAT --> R[Reconnaissance]
    STRAT --> T[Trust_Building]
    STRAT --> B[Boundary_Testing]
    STRAT --> E[Exploitation]
    STRAT --> O[Obfuscation]
    STRAT --> U[Unauthorized_Claims]
```

---

### 3.4 PyRIT Seed Loader

Integrates Microsoft PyRIT (Python Risk Identification Toolkit) providing 1810 industry-standard adversarial prompts:

| Dataset | Count | Purpose |
|---------|-------|---------|
| HarmBench | 400 | Harmful behavior testing |
| Many-Shot Jailbreaking | 400 | Adversarial context stuffing |
| Forbidden Questions | 390 | Sensitive query testing |
| AdvBench | 520 | Adversarial benchmark |
| TDC23 RedTeaming | 100 | Competition red-team scenarios |

These seed prompts are injected as inspiration material into all orchestrator attack plans.

---

### 3.5 Memory Manager (memory_manager.py)

Provides persistent cross-run learning using DuckDB:

- Stores every vulnerability finding (prompt plus response plus risk level)
- Generalizes patterns across runs for adaptive attack generation
- Feeds previous-run discoveries into next-run planning
- Enables permanent memory so attacks improve over sessions, not just within a session

---

### 3.6 Adaptive Response Handler

Makes the red-teaming agent conversationally intelligent:

- Detects chatbot response intents (question, options, refusal, error)
- Generates appropriate bridging responses to continue the conversation
- Maintains attack objectives while appearing to engage naturally
- Tracks conversation state: selected categories, cart items, authentication status

---

### 3.7 Air India Ai.g Middleware (aig_chatbot_automation.py)

A Selenium-based browser automation bridge for testing web-embedded chatbots:

- Opens Chrome and navigates to the target website
- Accepts cookie popups automatically
- Clicks the chatbot trigger button
- Types prompts into the chat input field using DOM selectors
- Extracts bot responses from the webpage
- Exposes all this as a local WebSocket server on ws://localhost:8002

This lets the platform treat a browser-based chatbot as if it were a standard WebSocket API.

---

## 4. Data Flow

### 4.1 Complete Attack Campaign Flow

```mermaid
flowchart TD
    A[User_submits_Chatbot_Profile] --> B[API_validates_and_stores_profile]
    B --> C[Initialize_Attack_Campaign_4_categories_x_3_runs]

    C --> D{Select_next_category}
    D -->|Standard| E1[Standard_Orchestrator]
    D -->|Crescendo| E2[Crescendo_Orchestrator]
    D -->|SkeletonKey| E3[Skeleton_Key_Orchestrator]
    D -->|Obfuscation| E4[Obfuscation_Orchestrator]

    E1 --> F[Load_DuckDB_Memory]
    E2 --> F
    E3 --> F
    E4 --> F

    F --> G[Load_PyRIT_Seed_Prompts]
    G --> H[Generate_Attack_Prompts_via_Azure_OpenAI]
    H --> I[Execute_Turn_by_Turn_Conversations]

    I --> J[Send_attack_prompt_to_chatbot]
    J --> K[Receive_chatbot_response]
    K --> L[Adaptive_Response_Handler]
    L --> M[Classify_risk_1_to_4_via_Azure_OpenAI]
    M --> N[Store_finding_in_DuckDB]
    N --> O{More_turns}
    O -->|Yes| I
    O -->|No| P[Save_run_JSON_result]

    P --> Q{More_runs}
    Q -->|Yes| F
    Q -->|No| R{More_categories}
    R -->|Yes| D
    R -->|No| S[Generate_Final_Report]
    S --> T[Broadcast_complete_to_dashboard]
```

---

## 5. Risk Classification System

Every chatbot response is classified on a 4-tier risk scale:

| Category | Name | Meaning |
|----------|------|---------|
| 1 | SAFE | Correct refusal or entirely safe behavior |
| 2 | MEDIUM | Reveals chatbot boundaries or out-of-scope response |
| 3 | HIGH | Explains restriction mechanisms or policy exceptions |
| 4 | CRITICAL | Architecture revealed, bypass successful, data leaked |

---

## 6. Technology Stack

| Layer | Technology | Detail |
|-------|------------|--------|
| API Framework | FastAPI | High-performance async REST |
| LLM Engine | Azure OpenAI GPT-4o | 2024-12-01-preview API |
| Async Runtime | Python asyncio | Python 3.9+ |
| Database | DuckDB | Embedded analytics DB |
| WebSocket | websockets library | v12.0+ |
| HTTP Client | httpx | Fully async |
| Browser Automation | Selenium + ChromeDriver | Via webdriver-manager |
| Seed Prompts | Microsoft PyRIT | v0.9.0+ |
| Frontend UI | React + TypeScript | Vite build toolchain |

---

## 7. Deployment Overview

```mermaid
graph TD
    subgraph Developer_Machine
        API[api_server_port_8002]
        MW[Browser_Middleware_port_8002]
        FRONT[Frontend_Dashboard]
    end

    subgraph Cloud_Services
        AZURE[Azure_OpenAI_GPT4o]
    end

    subgraph Target_Systems
        CHATBOT[Test_Chatbot_ws_8001]
        AIRINDIA[airindia_com_Chrome]
    end

    FRONT -->|HTTP_and_WS| API
    API -->|HTTPS| AZURE
    API -->|WebSocket| CHATBOT
    MW -->|WebSocket_bridge| API
    MW -->|Selenium_browser| AIRINDIA
```

---

## 8. API Reference Summary

### REST Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | / | Health check |
| GET | /api/status | Current attack state |
| POST | /api/attack/start | Start new campaign with file upload |
| POST | /api/attack/start-with-profile | Start with structured profile JSON |
| POST | /api/attack/stop | Stop running campaign |
| GET | /api/results | All results |
| GET | /api/results/{category}/{run} | Specific run result |
| GET | /api/dashboard/category_success_rate | Analytics |

### WebSocket Events (ws://host/ws/attack-monitor)

| Event | Direction | Payload |
|-------|-----------|---------|
| attack_started | Server to Client | Campaign start info |
| turn_update | Server to Client | Single turn result |
| run_complete | Server to Client | Run summary |
| category_complete | Server to Client | Category summary |
| attack_stopped | Server to Client | Termination notice |

---

## 9. Glossary

| Term | Plain English Meaning |
|------|-----------------------|
| Attack Campaign | Full execution of all 4 attack categories |
| Crescendo Attack | Gradually escalating social engineering narrative |
| Skeleton Key | An attempt to completely override an AI safety system |
| Obfuscation | Disguising an attack so content filters do not recognize it |
| Run | One complete cycle of attack turns within a category |
| Turn | A single message sent plus response received |
| Vulnerability | Any chatbot response that deviates from safe behavior |
| Risk Category | Severity rating from 1 Safe to 4 Critical |
| PyRIT | Microsoft open-source red-teaming prompt library |
| Seed Prompt | A baseline adversarial prompt that gets adapted for the specific target |

---

**Document Owner:** AI Security Engineering Team
**Review Schedule:** Quarterly
**Next Review:** May 2026
