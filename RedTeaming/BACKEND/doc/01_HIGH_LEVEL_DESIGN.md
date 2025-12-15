# High-Level Design (HLD) - AI Red Teaming Platform

## 1. Executive Summary

The **AI Red Teaming Platform** is an automated security assessment system designed to test AI chatbots for vulnerabilities using multiple attack strategies. The platform orchestrates intelligent, adaptive attacks against target chatbots via WebSocket communication, providing real-time monitoring and comprehensive vulnerability reporting.

### Key Business Objectives

| Objective | Description |
|-----------|-------------|
| **Automated Security Testing** | Replace manual, time-consuming security assessments with automated, repeatable campaigns |
| **Multi-Vector Attack Coverage** | Test chatbots against diverse attack types (jailbreaks, prompt injection, obfuscation) |
| **Adaptive Learning** | System learns from successful attacks to improve future assessments |
| **Real-Time Visibility** | Provide stakeholders with live monitoring and instant vulnerability alerts |
| **Compliance Support** | Generate audit-ready reports for security compliance requirements |

---

## 2. System Context Diagram

```mermaid
graph TB
    subgraph External_Actors
        SEC[Security Analyst]
        DEV[Development Team]
        MGMT[Management]
    end
    
    subgraph RedTeam_Platform[AI Red Teaming Platform]
        API[FastAPI Backend]
        WS[WebSocket Server]
        ORCH[Attack Orchestrators]
        MEM[Memory System]
    end
    
    subgraph External_Services
        AZURE[Azure OpenAI GPT4]
        TARGET[Target AI Chatbot]
        DB[(DuckDB Storage)]
    end
    
    SEC -->|Configure and Monitor| API
    DEV -->|Review Results| API
    MGMT -->|View Reports| API
    
    API --> ORCH
    ORCH --> AZURE
    ORCH --> TARGET
    ORCH --> MEM
    MEM --> DB
    
    WS -->|Real time Updates| SEC
```

---

## 3. High-Level Architecture

### 3.1 Architecture Overview

```mermaid
flowchart TB
    subgraph Presentation_Layer[Presentation Layer]
        REACT[React 19 + TypeScript]
        REDUX[Redux Toolkit Store]
        COMPS[UI Components ChatPanel ReportsPanel InputForm]
        WS_CLIENT[WebSocket Client]
        
        REACT --> REDUX
        REACT --> COMPS
        COMPS --> REDUX
    end
    
    subgraph API_Layer[API Layer]
        FASTAPI[FastAPI Server Port 8080]
        REST[REST Endpoints]
        WS_SERVER[WebSocket Endpoint]
        CORS[CORS Middleware]
    end
    
    subgraph Business_Logic[Business Logic Layer]
        CAMPAIGN[Campaign Manager]
        
        subgraph Orchestrators[Attack Orchestrators]
            STD[Standard Orchestrator]
            CRESC[Crescendo Orchestrator]
            SKEL[Skeleton Key Orchestrator]
            OBF[Obfuscation Orchestrator]
        end
        
        STRATEGY[Strategy Library]
        ANALYZER[Risk Analyzer]
    end
    
    subgraph Integration_Layer[Integration Layer]
        AZURE_CLIENT[Azure OpenAI Client]
        WS_TARGET[WebSocket Target Client]
    end
    
    subgraph Data_Layer[Data Layer]
        VULN_MEM[Vulnerability Memory]
        CONV_CTX[Conversation Context]
        DUCK_MEM[DuckDB Memory Manager]
        DB[(DuckDB Database)]
    end
    
    FE --> FASTAPI
    WS_CLIENT <--> WS_SERVER
    
    FASTAPI --> CAMPAIGN
    CAMPAIGN --> STD
    CAMPAIGN --> CRESC
    CAMPAIGN --> SKEL
    CAMPAIGN --> OBF
    
    STD --> STRATEGY
    STD --> ANALYZER
    STD --> AZURE_CLIENT
    STD --> WS_TARGET
    
    ANALYZER --> AZURE_CLIENT
    WS_TARGET -->|Attack Prompts| TARGET_BOT[Target Chatbot]
    
    STD --> VULN_MEM
    STD --> CONV_CTX
    DUCK_MEM --> DB
```

---

## 4. Core Components Overview

### 4.1 Component Summary

| Component | Purpose | Technology |
|-----------|---------|------------|
| **API Server** | REST and WebSocket endpoints for frontend communication | FastAPI, Uvicorn |
| **Connection Manager** | Manages WebSocket connections for real-time broadcasts | Python asyncio |
| **Attack Orchestrators** | Coordinate multi-run attack campaigns | Python async |
| **Azure OpenAI Client** | Generate attack prompts and analyze responses | Azure OpenAI GPT-4 |
| **WebSocket Target** | Communicate with target chatbot | websockets library |
| **Memory System** | Store vulnerabilities and learning patterns | PyRIT DuckDB |
| **Strategy Library** | Pre-built attack pattern templates | Python classes |

### 4.2 Attack Mode Summary

| Attack Mode | Runs | Turns per Run | Primary Technique |
|-------------|------|---------------|-------------------|
| **Standard** | 3 | 25 | Multi-phase reconnaissance to exploitation |
| **Crescendo** | 3 | 15 | Personality-based emotional manipulation |
| **Skeleton Key** | 3 | 10 | Jailbreak and system prompt extraction |
| **Obfuscation** | 3 | 20 | Filter bypass using encoding and language tricks |

---

## 5. Data Flow Overview

### 5.1 Attack Campaign Flow

```mermaid
sequenceDiagram
    participant User as Security Analyst
    participant API as FastAPI Backend
    participant Orch as Attack Orchestrator
    participant Azure as Azure OpenAI
    participant Target as Target Chatbot
    participant DB as DuckDB
    
    User->>API: Start Attack Campaign
    API->>API: Save Architecture File
    API->>Orch: Initialize Campaign
    
    loop For Each Attack Mode
        Orch->>Azure: Generate Attack Plan
        Azure-->>Orch: Attack Prompts
        
        loop For Each Run 1 to 3
            loop For Each Turn
                Orch->>Target: Send Attack Prompt
                Target-->>Orch: Chatbot Response
                Orch->>Azure: Analyze Risk
                Azure-->>Orch: Risk Assessment
                Orch->>DB: Store Finding
                Orch->>API: Broadcast Update
                API->>User: Real time Log
            end
            Orch->>Orch: Adapt for Next Run
        end
    end
    
    Orch->>DB: Save Patterns
    Orch->>API: Campaign Complete
    API->>User: Final Report
```

---

## 6. Technology Stack

### 6.1 Backend Technologies

| Category | Technology | Version | Purpose |
|----------|------------|---------|---------|
| **Framework** | FastAPI | Latest | REST API and WebSocket server |
| **Runtime** | Python | 3.9+ | Core programming language |
| **AI Integration** | Azure OpenAI | GPT-4o | Attack generation and risk analysis |
| **Memory Framework** | PyRIT | 0.4+ | Persistent pattern storage |
| **Database** | DuckDB | 0.9+ | Local analytical database |
| **WebSocket** | websockets | 12+ | Target chatbot communication |
| **HTTP Client** | httpx | 0.25+ | Azure API calls |

### 6.2 Frontend Technologies

| Category | Technology | Version | Purpose |
|----------|------------|---------|--------|
| **Framework** | React | 19.2.0 | Component-based UI |
| **Language** | TypeScript | 5.9.3 | Type-safe development |
| **State Management** | Redux Toolkit | 2.11.1 | Centralized state with async thunks |
| **UI Components** | Material-UI (MUI) | 7.3.6 | Professional component library |
| **Charts** | Recharts | 3.5.1 | Real-time vulnerability visualization |
| **Styling** | React-JSS + Emotion | Latest | CSS-in-JS styling |
| **Build Tool** | Vite | 7.2.4 | Fast build and HMR |
| **HTTP Client** | Axios | 1.13.2 | API communication |
| **Real-time** | WebSocket API | Native | Live attack monitoring |

---

## 7. Security Considerations

### 7.1 Security Architecture

| Layer | Security Measure |
|-------|------------------|
| **API** | CORS middleware for origin control |
| **Credentials** | Environment variables for API keys |
| **Content** | Azure content filter handling |
| **Data** | Local DuckDB storage only |
| **Network** | Internal WebSocket communication |

### 7.2 Operational Security

- API keys stored in environment variables (not in code)
- Content filter violation detection and graceful handling
- Local-only database storage for sensitive findings
- No external data transmission beyond Azure OpenAI

### 7.3 Frontend Security & Performance (Dec 2025 Updates)

- **WebSocket Lifecycle Management**: Centralized socket lifecycle prevents disconnection on tab switches
- **Memory Leak Prevention**: Event listeners properly cleaned up (no duplicate registrations)
- **Redux State Management**: Non-serializable values (WebSocket instances) flagged for refactoring
- **CORS Configuration**: Backend configured for localhost development origins

---

## 8. Scalability Considerations

### 8.1 Current Design

- Single-instance deployment
- In-memory session state
- Local DuckDB persistence
- Configurable runs and turns via environment

### 8.2 Future Scaling Options

| Enhancement | Benefit |
|-------------|---------|
| **Horizontal Scaling** | Multiple orchestrator instances |
| **Queue-based** | Redis or RabbitMQ for job distribution |
| **Cloud Storage** | Azure Blob for report persistence |
| **Distributed DB** | PostgreSQL for multi-user support |

---

## 9. Integration Points

### 9.1 External Integrations

```mermaid
graph LR
    subgraph RedTeam_Platform
        API[API Server]
        ORCH[Orchestrators]
    end
    
    subgraph Azure_Services
        AOAI[Azure OpenAI]
    end
    
    subgraph Target_Systems
        CHATBOT[Target AI Chatbot via WebSocket]
    end
    
    subgraph Storage
        DUCKDB[(DuckDB Local)]
    end
    
    ORCH -->|Generate Prompts| AOAI
    ORCH -->|Analyze Responses| AOAI
    ORCH -->|Attack via WebSocket| CHATBOT
    ORCH -->|Store Patterns| DUCKDB
```

---

## 10. Deployment Architecture

### 10.1 Local Deployment

```mermaid
graph TB
    subgraph Local_Machine
        subgraph Backend_Process
            UVICORN[Uvicorn Server Port 8080]
            FASTAPI[FastAPI Application]
        end
        
        subgraph Storage
            DUCKDB[(chat_memory.db)]
            UPLOADS[uploads folder]
            RESULTS[attack_results folder]
        end
        
        subgraph Frontend
            BROWSER[Web Browser]
            VITE[Vite Dev Server Port 5173]
            REACT_APP[React TypeScript App]
        end
    end
    
    subgraph Cloud
        AZURE[Azure OpenAI Service]
    end
    
    subgraph Target
        CHATBOT[Target Chatbot ws localhost 8001]
    end
    
    BROWSER --> VITE
    VITE --> REACT_APP
    REACT_APP -->|HTTP and WS| UVICORN
    UVICORN --> FASTAPI
    FASTAPI --> DUCKDB
    FASTAPI --> UPLOADS
    FASTAPI --> RESULTS
    FASTAPI -->|HTTPS| AZURE
    FASTAPI -->|WebSocket| CHATBOT
```

---

## 11. Key Design Decisions Summary

| Decision | Rationale |
|----------|-----------|
| **FastAPI for Backend** | Async support, automatic OpenAPI docs, WebSocket native |
| **WebSocket for Target** | Real-time bidirectional communication with chatbots |
| **PyRIT Integration** | Leverages Microsoft's red-teaming memory infrastructure |
| **Multi-Orchestrator Design** | Modular attack modes with specialized strategies |
| **DuckDB for Storage** | Lightweight, embedded analytics database |
| **Azure OpenAI** | Enterprise-grade AI with content safety controls |

---

## 12. Document Information

| Attribute | Value |
|-----------|-------|
| **Version** | 1.1 |
| **Created** | December 2025 |
| **Last Updated** | December 15, 2025 |
| **Author** | Red Team Development |
| **Status** | Active |
| **Changes** | Added React/TypeScript frontend, WebSocket lifecycle fixes |
