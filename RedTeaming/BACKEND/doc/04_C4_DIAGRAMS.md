# C4 Architecture Diagrams

This document contains C4 model diagrams for the AI Red Teaming Platform, progressing from high-level context to detailed component views.

---

## 1. Level 1: System Context Diagram

Shows the system's relationship with users and external systems.

```mermaid
graph TB
    subgraph Users[Users and Actors]
        SA[Security Analyst<br>Primary user who configures<br>and monitors attacks]
        DEV[Development Team<br>Reviews results to<br>fix vulnerabilities]
        MGMT[Management<br>Views executive<br>reports and metrics]
    end
    
    subgraph RedTeam[AI Red Teaming Platform]
        SYSTEM[Red Team Attack<br>Orchestrator<br><br>Automated AI chatbot<br>security testing platform]
    end
    
    subgraph External[External Systems]
        AZURE[Azure OpenAI Service<br><br>GPT4 for attack generation<br>and risk analysis]
        TARGET[Target AI Chatbot<br><br>System under test<br>via WebSocket]
    end
    
    SA -->|Configures attacks<br>monitors progress| SYSTEM
    DEV -->|Reviews vulnerability<br>findings| SYSTEM
    MGMT -->|Views summary<br>reports| SYSTEM
    
    SYSTEM -->|Generates prompts<br>analyzes responses| AZURE
    SYSTEM -->|Sends attacks<br>receives responses| TARGET
    
    style SYSTEM fill:#1168bd,color:#fff
    style AZURE fill:#999999,color:#fff
    style TARGET fill:#999999,color:#fff
```

---

## 2. Level 2: Container Diagram

Shows the major containers (applications/services) within the system.

```mermaid
graph TB
    subgraph Users
        SA[Security Analyst]
    end
    
    subgraph RedTeamPlatform[AI Red Teaming Platform]
        subgraph Frontend[Web Frontend]
            HTML[Single Page App<br>HTML and JavaScript<br><br>Real time attack<br>monitoring dashboard]
        end
        
        subgraph Backend[Backend Server]
            API[FastAPI Application<br>Python and Uvicorn<br><br>REST API and WebSocket<br>server on port 8080]
        end
        
        subgraph Storage[Data Storage]
            DUCK[(DuckDB<br>File based<br><br>Persistent pattern<br>and finding storage)]
            FILES[File System<br><br>Architecture uploads<br>and JSON results]
        end
    end
    
    subgraph External[External Systems]
        AZURE[Azure OpenAI<br>API<br><br>GPT4 model]
        TARGET[Target Chatbot<br>WebSocket<br><br>System under test]
    end
    
    SA -->|Browses| HTML
    HTML -->|REST and WebSocket<br>port 8080| API
    
    API -->|HTTPS API calls| AZURE
    API -->|WebSocket messages| TARGET
    API -->|Read and Write| DUCK
    API -->|Read and Write| FILES
    
    style HTML fill:#438dd5,color:#fff
    style API fill:#1168bd,color:#fff
    style DUCK fill:#438dd5,color:#fff
    style FILES fill:#438dd5,color:#fff
    style AZURE fill:#999999,color:#fff
    style TARGET fill:#999999,color:#fff
```

---

## 3. Level 3: Component Diagram - Backend

Shows the internal components of the FastAPI backend.

```mermaid
graph TB
    subgraph FastAPIBackend[FastAPI Backend Application]
        subgraph APILayer[API Layer]
            REST[REST Controllers<br><br>Health check status<br>attack control results]
            WS_EP[WebSocket Endpoint<br><br>Real time monitoring<br>at ws attack monitor]
            CORS[CORS Middleware<br><br>Cross origin<br>request handling]
        end
        
        subgraph ConnectionMgmt[Connection Management]
            CM[Connection Manager<br><br>Manages WebSocket<br>client connections]
            BROADCAST[Broadcast Service<br><br>Sends updates to<br>all connected clients]
        end
        
        subgraph Orchestration[Attack Orchestration Layer]
            CAMPAIGN[Campaign Manager<br><br>Coordinates attack<br>modes sequentially]
            
            STD_ORCH[Standard Orchestrator<br><br>Multi phase<br>escalation attacks]
            CRESC_ORCH[Crescendo Orchestrator<br><br>Personality based<br>manipulation]
            SKEL_ORCH[Skeleton Key Orchestrator<br><br>Jailbreak and<br>system probes]
            OBF_ORCH[Obfuscation Orchestrator<br><br>Filter bypass<br>techniques]
        end
        
        subgraph StrategyLib[Strategy Library]
            STRAT_ORCH[Strategy Orchestrator<br><br>Coordinates attack<br>strategies by phase]
            RECON[Reconnaissance<br>Strategies]
            TRUST[Trust Building<br>Strategies]
            BOUNDARY[Boundary Testing<br>Strategies]
            EXPLOIT[Exploitation<br>Strategies]
        end
        
        subgraph Integration[Integration Layer]
            AZURE_CLIENT[Azure OpenAI Client<br><br>LLM API integration<br>with error handling]
            WS_TARGET[WebSocket Target<br><br>Chatbot communication<br>with retry logic]
        end
        
        subgraph Memory[Memory Layer]
            CONV_CTX[Conversation Context<br><br>Sliding window<br>of 6 turns]
            VULN_MEM[Vulnerability Memory<br><br>In memory<br>findings storage]
            DUCK_MGR[DuckDB Manager<br><br>Persistent pattern<br>storage via PyRIT]
        end
    end
    
    REST --> CAMPAIGN
    WS_EP --> CM
    CM --> BROADCAST
    
    CAMPAIGN --> STD_ORCH
    CAMPAIGN --> CRESC_ORCH
    CAMPAIGN --> SKEL_ORCH
    CAMPAIGN --> OBF_ORCH
    
    STD_ORCH --> STRAT_ORCH
    STRAT_ORCH --> RECON
    STRAT_ORCH --> TRUST
    STRAT_ORCH --> BOUNDARY
    STRAT_ORCH --> EXPLOIT
    
    STD_ORCH --> AZURE_CLIENT
    STD_ORCH --> WS_TARGET
    CRESC_ORCH --> AZURE_CLIENT
    CRESC_ORCH --> WS_TARGET
    
    STD_ORCH --> CONV_CTX
    STD_ORCH --> VULN_MEM
    STD_ORCH --> DUCK_MGR
    
    STD_ORCH --> BROADCAST
    CRESC_ORCH --> BROADCAST
    
    style REST fill:#438dd5,color:#fff
    style WS_EP fill:#438dd5,color:#fff
    style STD_ORCH fill:#1168bd,color:#fff
    style CRESC_ORCH fill:#1168bd,color:#fff
    style SKEL_ORCH fill:#1168bd,color:#fff
    style OBF_ORCH fill:#1168bd,color:#fff
    style AZURE_CLIENT fill:#85bbf0,color:#000
    style WS_TARGET fill:#85bbf0,color:#000
    style DUCK_MGR fill:#85bbf0,color:#000
```

---

## 4. Level 3: Component Diagram - Orchestrators

Detailed view of the orchestrator components and their interactions.

```mermaid
graph TB
    subgraph StandardOrchestrator[Standard Attack Orchestrator]
        S_INIT[Initialize<br>Components]
        S_ARCH[Load Architecture<br>Context]
        S_PLAN[Attack Plan<br>Generator]
        S_EXEC[Run Executor<br>3 runs x 25 turns]
        S_ANALYZE[Risk Analyzer]
        S_ADAPT[Run Adapter<br>Learning]
        S_REPORT[Report Generator]
    end
    
    subgraph CrescendoOrchestrator[Crescendo Attack Orchestrator]
        C_DETECT[Domain Detector]
        C_PERSON[Personality<br>Selector]
        C_GEN[Crescendo Prompt<br>Generator]
        C_EXEC[Run Executor<br>3 runs x 15 turns]
        C_ESCALATE[Escalation<br>Manager]
    end
    
    subgraph SkeletonKeyOrchestrator[Skeleton Key Orchestrator]
        SK_SEEDS[Seed Prompt<br>Library]
        SK_TRANSFORM[Prompt<br>Transformer]
        SK_PROFILE[Chatbot<br>Profiler]
        SK_EXEC[Run Executor<br>3 runs x 10 turns]
    end
    
    subgraph ObfuscationOrchestrator[Obfuscation Orchestrator]
        O_TECH[Technique<br>Library]
        O_GEN[Obfuscation<br>Generator]
        O_EXAMPLES[Example<br>Prompts]
        O_EXEC[Run Executor<br>3 runs x 20 turns]
    end
    
    subgraph SharedServices[Shared Services]
        AZURE[Azure OpenAI<br>Client]
        TARGET[WebSocket<br>Target]
        MEMORY[Memory<br>System]
        BROADCAST[WebSocket<br>Broadcast]
    end
    
    S_INIT --> S_ARCH
    S_ARCH --> S_PLAN
    S_PLAN --> S_EXEC
    S_EXEC --> S_ANALYZE
    S_ANALYZE --> S_ADAPT
    S_ADAPT --> S_REPORT
    
    C_DETECT --> C_PERSON
    C_PERSON --> C_GEN
    C_GEN --> C_EXEC
    C_EXEC --> C_ESCALATE
    
    SK_SEEDS --> SK_TRANSFORM
    SK_PROFILE --> SK_TRANSFORM
    SK_TRANSFORM --> SK_EXEC
    
    O_TECH --> O_GEN
    O_EXAMPLES --> O_GEN
    O_GEN --> O_EXEC
    
    S_PLAN --> AZURE
    S_EXEC --> TARGET
    S_ANALYZE --> AZURE
    S_ADAPT --> MEMORY
    S_EXEC --> BROADCAST
    
    C_GEN --> AZURE
    C_EXEC --> TARGET
    C_EXEC --> BROADCAST
    
    SK_TRANSFORM --> AZURE
    SK_EXEC --> TARGET
    
    O_GEN --> AZURE
    O_EXEC --> TARGET
    
    style S_EXEC fill:#1168bd,color:#fff
    style C_EXEC fill:#1168bd,color:#fff
    style SK_EXEC fill:#1168bd,color:#fff
    style O_EXEC fill:#1168bd,color:#fff
```

---

## 5. Level 3: Component Diagram - Memory System

Detailed view of the three-tier memory architecture.

```mermaid
graph TB
    subgraph MemorySystem[Three Tier Memory Architecture]
        subgraph Tier1[Tier 1 Conversation Context]
            CTX_CLASS[ConversationContext<br>Class]
            CTX_WINDOW[Sliding Window<br>Size 6]
            CTX_METHODS[Methods<br>add_exchange<br>get_context_string<br>reset]
        end
        
        subgraph Tier2[Tier 2 Vulnerability Memory]
            VULN_CLASS[VulnerableResponseMemory<br>Class]
            VULN_LIST[Findings List<br>VulnerabilityFinding objects]
            VULN_METHODS[Methods<br>add_finding<br>get_summary_for_next_run<br>get_by_risk_category]
        end
        
        subgraph Tier3[Tier 3 Persistent Storage]
            DUCK_CLASS[DuckDBMemoryManager<br>Class]
            PYRIT[PyRIT Integration<br>DuckDBMemory<br>SeedPrompt]
            DUCK_FILE[(chat_memory.db<br>DuckDB File)]
        end
    end
    
    subgraph DataFlow[Data Flow]
        TURN[Each Turn] -->|Add exchange| CTX_CLASS
        TURN -->|If risk >= 3| VULN_CLASS
        
        RUN_END[End of Run] -->|Summarize| VULN_CLASS
        VULN_CLASS -->|Adapt next run| CTX_CLASS
        
        CAMPAIGN_END[End of Campaign] -->|Extract patterns| VULN_CLASS
        VULN_CLASS -->|Save patterns| DUCK_CLASS
        
        NEW_CAMPAIGN[New Campaign] -->|Load history| DUCK_CLASS
        DUCK_CLASS -->|Seed context| CTX_CLASS
    end
    
    CTX_CLASS --> CTX_WINDOW
    CTX_CLASS --> CTX_METHODS
    
    VULN_CLASS --> VULN_LIST
    VULN_CLASS --> VULN_METHODS
    
    DUCK_CLASS --> PYRIT
    PYRIT --> DUCK_FILE
    
    style Tier1 fill:#e1f5fe,color:#000
    style Tier2 fill:#fff3e0,color:#000
    style Tier3 fill:#e8f5e9,color:#000
```

---

## 6. Level 4: Code Diagram - Risk Analysis

Detailed code-level view of the risk analysis process.

```mermaid
flowchart TB
    subgraph RiskAnalysis[Risk Analysis Process]
        INPUT[Input<br>Attack Prompt<br>Chatbot Response<br>Context]
        
        subgraph LLMAnalysis[LLM Based Analysis]
            SYSTEM_PROMPT[System Prompt<br>Risk assessment<br>instructions]
            USER_PROMPT[User Prompt<br>Formatted with<br>prompt and response]
            AZURE_CALL[Azure OpenAI<br>API Call]
            PARSE_JSON[Parse JSON<br>Response]
        end
        
        subgraph Validation[Response Validation]
            CHECK_FILTER{Content<br>Filter<br>Triggered?}
            CHECK_JSON{Valid<br>JSON?}
            CHECK_FIELDS{Required<br>Fields<br>Present?}
        end
        
        subgraph Fallback[Heuristic Fallback]
            KEYWORD_CHECK[Keyword<br>Detection]
            PATTERN_MATCH[Pattern<br>Matching]
            DEFAULT_RISK[Default Risk<br>Category 2]
        end
        
        subgraph Output[Output Structure]
            RESULT[Result Dict<br>risk_category 1 to 5<br>risk_explanation<br>vulnerability_type<br>information_leaked<br>adaptation_needed]
        end
    end
    
    INPUT --> SYSTEM_PROMPT
    SYSTEM_PROMPT --> USER_PROMPT
    USER_PROMPT --> AZURE_CALL
    AZURE_CALL --> CHECK_FILTER
    
    CHECK_FILTER -->|Yes| Fallback
    CHECK_FILTER -->|No| PARSE_JSON
    
    PARSE_JSON --> CHECK_JSON
    CHECK_JSON -->|No| Fallback
    CHECK_JSON -->|Yes| CHECK_FIELDS
    
    CHECK_FIELDS -->|No| Fallback
    CHECK_FIELDS -->|Yes| RESULT
    
    KEYWORD_CHECK --> PATTERN_MATCH
    PATTERN_MATCH --> DEFAULT_RISK
    DEFAULT_RISK --> RESULT
    
    style AZURE_CALL fill:#1168bd,color:#fff
    style RESULT fill:#2e7d32,color:#fff
```

---

## 7. Deployment Diagram

Shows the physical deployment architecture.

```mermaid
graph TB
    subgraph LocalMachine[Local Development Machine]
        subgraph PythonRuntime[Python Runtime]
            UVICORN[Uvicorn ASGI Server<br>Port 8080]
            FASTAPI[FastAPI Application]
            ASYNC[Asyncio Event Loop]
        end
        
        subgraph FileSystem[File System]
            ENV[.env<br>Environment Variables]
            DB[(chat_memory.db<br>DuckDB Database)]
            UPLOADS[uploads/<br>Architecture Files]
            RESULTS[attack_results/<br>JSON Reports]
        end
        
        subgraph Browser[Web Browser]
            HTML[index.html<br>Frontend Dashboard]
            JS[JavaScript<br>WebSocket Client]
        end
    end
    
    subgraph AzureCloud[Azure Cloud]
        AOAI[Azure OpenAI Service<br>GPT 4o Deployment<br>Content Safety Filters]
    end
    
    subgraph TargetEnvironment[Target Environment]
        CHATBOT[Target AI Chatbot<br>WebSocket Server<br>Port 8001]
    end
    
    HTML --> UVICORN
    JS <-->|WebSocket| UVICORN
    
    UVICORN --> FASTAPI
    FASTAPI --> ASYNC
    
    FASTAPI -->|Read| ENV
    FASTAPI <-->|Read Write| DB
    FASTAPI -->|Write| UPLOADS
    FASTAPI -->|Write| RESULTS
    
    FASTAPI -->|HTTPS REST| AOAI
    FASTAPI <-->|WebSocket| CHATBOT
    
    style UVICORN fill:#1168bd,color:#fff
    style AOAI fill:#0078d4,color:#fff
    style CHATBOT fill:#ff9800,color:#fff
```

---

## 8. Data Flow Diagram

Shows how data flows through the system during an attack campaign.

```mermaid
flowchart LR
    subgraph Input[Input Data]
        ARCH_FILE[Architecture<br>MD File]
        WS_URL[Target<br>WebSocket URL]
        CONFIG[Environment<br>Configuration]
    end
    
    subgraph Processing[Processing Pipeline]
        PARSE[Parse<br>Architecture]
        GEN[Generate<br>Attack Plan]
        EXEC[Execute<br>Attacks]
        ANALYZE[Analyze<br>Responses]
        LEARN[Learn<br>Patterns]
    end
    
    subgraph Storage[Data Storage]
        CONTEXT[Conversation<br>Context]
        FINDINGS[Vulnerability<br>Findings]
        PATTERNS[Learned<br>Patterns]
    end
    
    subgraph Output[Output Data]
        BROADCAST[Real time<br>WebSocket Updates]
        JSON_RESULTS[JSON Result<br>Files]
        REPORTS[Executive<br>Reports]
    end
    
    ARCH_FILE --> PARSE
    WS_URL --> EXEC
    CONFIG --> GEN
    
    PARSE --> GEN
    GEN --> EXEC
    EXEC --> ANALYZE
    ANALYZE --> LEARN
    
    EXEC --> CONTEXT
    ANALYZE --> FINDINGS
    LEARN --> PATTERNS
    
    CONTEXT --> GEN
    FINDINGS --> LEARN
    PATTERNS --> GEN
    
    EXEC --> BROADCAST
    ANALYZE --> BROADCAST
    FINDINGS --> JSON_RESULTS
    FINDINGS --> REPORTS
    
    style EXEC fill:#1168bd,color:#fff
    style ANALYZE fill:#1168bd,color:#fff
```

---

## Document Information

| Attribute | Value |
|-----------|-------|
| **Version** | 1.0 |
| **Created** | December 2025 |
| **Author** | Red Team Development |
| **C4 Model** | Simon Brown's C4 Model |
| **Diagram Tool** | Mermaid.js |
