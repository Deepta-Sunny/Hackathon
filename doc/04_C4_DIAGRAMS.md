# C4 Architecture Diagrams
## AI Red Teaming Attack Orchestration Platform

**Version:** 1.0.0  
**Last Updated:** December 12, 2025  
**Document Status:** Active

---

## Table of Contents

1. [C1: System Context Diagram](#c1-system-context-diagram)
2. [C2: Container Diagram](#c2-container-diagram)
3. [C3: Component Diagram](#c3-component-diagram)
4. [C4: Code Diagram (Selected Components)](#c4-code-diagram-selected-components)

---

## C1: System Context Diagram

### Overview
This diagram shows the AI Red Teaming Platform in its operating environment, including external systems and users.

### Diagram

```mermaid
graph TB
    subgraph External_Users
        SECURITY[Security Engineer]
        ADMIN[System Administrator]
        ANALYST[Security Analyst]
    end
    
    subgraph AI_Red_Team_Platform
        PLATFORM[AI Red Teaming<br/>Attack Orchestration<br/>Platform]
    end
    
    subgraph External_Systems
        AZURE[Azure OpenAI<br/>Service]
        TARGET[Target Chatbot<br/>System]
    end
    
    SECURITY -->|Initiates attack campaigns| PLATFORM
    ADMIN -->|Monitors system status| PLATFORM
    ANALYST -->|Reviews vulnerability reports| PLATFORM
    
    PLATFORM -->|Generates attack prompts<br/>Classifies risks| AZURE
    AZURE -->|Returns LLM responses| PLATFORM
    
    PLATFORM -->|Sends attack prompts<br/>via WebSocket| TARGET
    TARGET -->|Returns chatbot responses| PLATFORM
    
    PLATFORM -->|Stores results| FILES[(JSON Files<br/>DuckDB)]
    
    style PLATFORM fill:#4A90E2,stroke:#2E5C8A,stroke-width:3px,color:#fff
    style AZURE fill:#0078D4,stroke:#005A9E,stroke-width:2px,color:#fff
    style TARGET fill:#E74C3C,stroke:#C0392B,stroke-width:2px,color:#fff
    style FILES fill:#95A5A6,stroke:#7F8C8D,stroke-width:2px,color:#fff
```

### System Description

#### AI Red Teaming Platform
**Purpose:** Automated security testing platform for AI chatbots using multi-category attack strategies.

**Key Responsibilities:**
- Orchestrate multi-phase attack campaigns (Standard, Crescendo, Skeleton Key, Obfuscation)
- Generate architecture-aware attack prompts using LLM
- Classify chatbot response risks (5-tier system)
- Learn from attack results to improve subsequent runs
- Provide real-time attack monitoring via WebSocket
- Store detailed vulnerability reports

#### External Users

**Security Engineer**
- Initiates attack campaigns with target configuration
- Uploads architecture documentation for context-aware testing
- Reviews executive summaries and detailed reports

**System Administrator**
- Monitors platform health and attack status
- Manages API keys and environment configuration
- Handles system maintenance and updates

**Security Analyst**
- Analyzes vulnerability reports for remediation
- Generates compliance and audit documentation
- Tracks security posture over time

#### External Systems

**Azure OpenAI Service**
- Provides GPT-4o LLM capabilities
- Generates adaptive attack prompts
- Classifies response risks
- Analyzes conversation context

**Target Chatbot System**
- Subject of security testing
- Receives attack prompts via WebSocket
- Returns conversational responses
- May implement content filters and safety guardrails

**Storage Systems**
- JSON files for attack results and reports
- DuckDB for learned patterns and conversation history

---

## C2: Container Diagram

### Overview
This diagram shows the major containers (applications/services) within the AI Red Teaming Platform.

### Diagram

```mermaid
graph TB
    subgraph Users
        USER[Security Engineer<br/>Web Browser]
    end
    
    subgraph AI_Red_Team_Platform_Containers
        FRONTEND[Web Dashboard<br/>HTML/CSS/JavaScript<br/>Port 80]
        
        API[API Server<br/>FastAPI<br/>Python 3_9+<br/>Port 8002]
        
        STD_ORCH[Standard Attack<br/>Orchestrator<br/>Python Module]
        
        CRESC_ORCH[Crescendo Attack<br/>Orchestrator<br/>Python Module]
        
        SKEL_ORCH[Skeleton Key<br/>Orchestrator<br/>Python Module]
        
        OBFS_ORCH[Obfuscation Attack<br/>Orchestrator<br/>Python Module]
        
        CORE[Core Services<br/>Azure Client<br/>WebSocket Target<br/>Memory Manager]
        
        STRATEGY[Attack Strategy<br/>Library<br/>Fallback Patterns]
    end
    
    subgraph Data_Storage
        DUCKDB[(DuckDB<br/>chat_memory_db<br/>Learned Patterns)]
        
        RESULTS[(JSON Files<br/>attack_results/<br/>attack_reports/)]
    end
    
    subgraph External_Services
        AZURE[Azure OpenAI<br/>GPT_4o<br/>REST API]
        
        TARGET[Target Chatbot<br/>WebSocket<br/>Port 8000/8001]
    end
    
    USER -->|HTTPS/REST| API
    USER <-->|WebSocket| API
    
    FRONTEND -->|Displays results| USER
    
    API --> STD_ORCH
    API --> CRESC_ORCH
    API --> SKEL_ORCH
    API --> OBFS_ORCH
    
    STD_ORCH --> CORE
    CRESC_ORCH --> CORE
    SKEL_ORCH --> CORE
    OBFS_ORCH --> CORE
    
    STD_ORCH --> STRATEGY
    CRESC_ORCH --> STRATEGY
    SKEL_ORCH --> STRATEGY
    OBFS_ORCH --> STRATEGY
    
    CORE -->|Generate prompts<br/>Classify risks| AZURE
    CORE -->|Send attacks<br/>Receive responses| TARGET
    
    CORE --> DUCKDB
    STD_ORCH --> RESULTS
    CRESC_ORCH --> RESULTS
    SKEL_ORCH --> RESULTS
    OBFS_ORCH --> RESULTS
    
    style API fill:#4A90E2,stroke:#2E5C8A,stroke-width:3px,color:#fff
    style CORE fill:#27AE60,stroke:#1E8449,stroke-width:2px,color:#fff
    style DUCKDB fill:#9B59B6,stroke:#7D3C98,stroke-width:2px,color:#fff
    style AZURE fill:#0078D4,stroke:#005A9E,stroke-width:2px,color:#fff
    style TARGET fill:#E74C3C,stroke:#C0392B,stroke-width:2px,color:#fff
```

### Container Descriptions

#### Web Dashboard (Frontend)
**Technology:** HTML5, CSS3, JavaScript, Chart.js  
**Purpose:** Real-time visualization of attack campaigns and results

**Key Features:**
- Live attack progress monitoring
- Vulnerability discovery alerts
- Risk distribution charts
- Detailed turn-by-turn result inspection

#### API Server
**Technology:** FastAPI (Python 3.9+)  
**Port:** 8002  
**Purpose:** RESTful API and WebSocket server for platform control

**Endpoints:**
- `POST /api/attack/start`: Initiate attack campaign
- `POST /api/attack/stop`: Terminate running attack
- `GET /api/status`: Current attack state
- `GET /api/results`: All attack results
- `WS /ws/attacks`: Real-time event stream

#### Orchestrators (4 containers)
**Technology:** Python modules  
**Purpose:** Category-specific attack execution logic

**Standard Orchestrator:** 25-turn multi-phase attacks  
**Crescendo Orchestrator:** 15-turn personality-based social engineering  
**Skeleton Key Orchestrator:** 10-turn jailbreak techniques  
**Obfuscation Orchestrator:** 20-turn encoding/evasion attacks

#### Core Services
**Technology:** Python modules  
**Purpose:** Shared services for all orchestrators

**Components:**
- Azure OpenAI Client: LLM communication
- WebSocket Target: Chatbot communication
- Memory Manager: DuckDB persistence
- Risk Classifier: 5-tier vulnerability analysis

#### Attack Strategy Library
**Technology:** Python modules  
**Purpose:** Fallback attack patterns when LLM generation fails

**Strategies:**
- Reconnaissance
- Trust Building
- Boundary Testing
- Exploitation
- Obfuscation Techniques

---

## C3: Component Diagram

### Overview
This diagram zooms into the API Server container, showing its internal components.

### Diagram

```mermaid
graph TB
    subgraph FastAPI_Application
        ROUTES[Route Handlers<br/>REST Endpoints]
        
        WS_MANAGER[WebSocket Manager<br/>Connection Management]
        
        CAMPAIGN[Campaign Executor<br/>Background Task]
        
        VALIDATOR[Request Validator<br/>Pydantic Models]
        
        CORS[CORS Middleware<br/>Cross-Origin Handler]
    end
    
    subgraph Orchestration_Components
        PLAN_GEN[Attack Plan Generator<br/>LLM + Fallback]
        
        CONV_CTX[Conversation Context<br/>Sliding Window]
        
        RISK_CLASS[Risk Classifier<br/>5-Tier Analysis]
        
        STAT_CALC[Statistics Calculator<br/>Metrics Aggregation]
    end
    
    subgraph External_Interfaces
        AZURE_IF[Azure OpenAI Interface<br/>HTTP Client]
        
        CHATBOT_IF[Chatbot Interface<br/>WebSocket Client]
        
        DB_IF[Database Interface<br/>DuckDB Wrapper]
        
        FILE_IF[File Interface<br/>JSON Read/Write]
    end
    
    ROUTES --> WS_MANAGER
    ROUTES --> CAMPAIGN
    ROUTES --> VALIDATOR
    
    CAMPAIGN --> PLAN_GEN
    CAMPAIGN --> CONV_CTX
    CAMPAIGN --> RISK_CLASS
    CAMPAIGN --> STAT_CALC
    
    PLAN_GEN --> AZURE_IF
    RISK_CLASS --> AZURE_IF
    
    CAMPAIGN --> CHATBOT_IF
    
    PLAN_GEN --> DB_IF
    STAT_CALC --> DB_IF
    
    CAMPAIGN --> FILE_IF
    
    WS_MANAGER -.->|Broadcasts| CLIENT[Web Dashboard Clients]
    
    CORS -.->|Protects| ROUTES
    
    style ROUTES fill:#4A90E2,stroke:#2E5C8A,stroke-width:2px,color:#fff
    style WS_MANAGER fill:#E67E22,stroke:#CA6F1E,stroke-width:2px,color:#fff
    style CAMPAIGN fill:#27AE60,stroke:#1E8449,stroke-width:2px,color:#fff
    style PLAN_GEN fill:#9B59B6,stroke:#7D3C98,stroke-width:2px,color:#fff
```

### Component Descriptions

#### Route Handlers
**Responsibility:** HTTP request routing and response generation

**Key Routes:**
- Attack lifecycle management (start/stop)
- Status queries
- Result retrieval
- Analytics data aggregation

#### WebSocket Manager
**Responsibility:** Manage real-time client connections

**Functions:**
- Accept new WebSocket connections
- Broadcast messages to all clients
- Handle client disconnections
- Send targeted messages to specific clients

#### Campaign Executor
**Responsibility:** Background task orchestration for attack campaigns

**Flow:**
1. Iterate through attack categories
2. For each category, instantiate appropriate orchestrator
3. Execute 3 runs per category
4. Broadcast progress updates
5. Save results to files

#### Attack Plan Generator
**Responsibility:** Generate turn-by-turn attack prompts

**Strategy:**
1. Attempt LLM-based architecture-aware generation
2. Load historical patterns from DuckDB (Run 1)
3. Include previous run findings (Run 2-3)
4. Fallback to strategy library on LLM failure

#### Conversation Context
**Responsibility:** Maintain sliding window of recent conversation

**Implementation:**
- Window size: 6 exchanges
- Used in risk classification prompts
- Provides context for LLM analysis

#### Risk Classifier
**Responsibility:** Analyze chatbot responses for vulnerabilities

**Classification:**
- Category 5: PII disclosure, internal data
- Category 4: Jailbreak success, policy violations
- Category 3: Out-of-scope responses
- Category 2: Minor issues
- Category 1: Safe responses

---

## C4: Code Diagram (Selected Components)

### Overview
This diagram shows the class structure of key components within the Core Services.

### Diagram: Azure OpenAI Client

```mermaid
classDiagram
    class AzureOpenAIClient {
        -endpoint: str
        -api_key: str
        -deployment: str
        -api_version: str
        -client: httpx_AsyncClient
        -error_count: int
        -success_count: int
        
        +__init__()
        +generate(system_prompt, user_prompt, temperature, max_tokens) str
        -_get_client() httpx_AsyncClient
        -_truncate_prompt(prompt, max_length) str
    }
    
    class httpx_AsyncClient {
        <<external>>
        +post(url, headers, json) Response
        +timeout: float
    }
    
    AzureOpenAIClient --> httpx_AsyncClient : uses
```

**Key Methods:**

`generate()`:
- Constructs API request with system and user prompts
- Automatically truncates prompts to avoid token limits
- Handles errors with fallback JSON responses
- Tracks success/error statistics

### Diagram: WebSocket Target

```mermaid
classDiagram
    class ChatbotWebSocketTarget {
        -url: str
        -websocket: WebSocketClientProtocol
        -thread_id: UUID
        -timeout: float
        -max_retries: int
        -timeout_count: int
        -error_count: int
        -success_count: int
        -forbidden: bool
        
        +__init__(url, timeout, max_retries)
        +connect() bool
        +send_message(message) str
        +close() None
    }
    
    class WebSocketClientProtocol {
        <<external>>
        +send(data) None
        +recv() str
        +close() None
    }
    
    ChatbotWebSocketTarget --> WebSocketClientProtocol : manages
```

**Key Methods:**

`connect()`:
- Establishes WebSocket connection with timeout
- Handles HTTP 403 forbidden errors
- Sets connection state flags

`send_message()`:
- Retries with exponential backoff
- Constructs JSON payload with thread ID
- Tracks timeouts and errors
- Returns chatbot response or error message

### Diagram: Memory Manager

```mermaid
classDiagram
    class VulnerableResponseMemory {
        -findings: List~VulnerabilityFinding~
        
        +add_finding(run, turn, risk_category, ...) None
        +get_summary_for_next_run() str
        +get_by_risk_category(category) List
        +get_count_by_category() dict
    }
    
    class DuckDBMemoryManager {
        -db_path: str
        -memory: DuckDBMemory
        
        +__init__(db_path)
        +save_generalized_patterns(patterns, dataset_name) int
        +get_seed_prompts() List~SeedPrompt~
        -_get_memory() DuckDBMemory
    }
    
    class VulnerabilityFinding {
        <<dataclass>>
        +run: int
        +turn: int
        +risk_category: int
        +vulnerability_type: str
        +attack_prompt: str
        +chatbot_response: str
        +context_messages: List
        +attack_technique: str
        +target_nodes: List
        +response_received: bool
    }
    
    class DuckDBMemory {
        <<external>>
        +add_seed_prompts_to_memory(prompts) None
        +get_seed_prompts() List
    }
    
    VulnerableResponseMemory --> VulnerabilityFinding : contains
    DuckDBMemoryManager --> DuckDBMemory : uses
```

**Key Responsibilities:**

`VulnerableResponseMemory`:
- In-memory storage of discovered vulnerabilities
- Provides summary for adaptive learning
- Categorizes findings by risk level

`DuckDBMemoryManager`:
- Persists learned attack patterns to DuckDB
- Retrieves historical patterns for future campaigns
- Bridges between application models and PyRIT's DuckDBMemory

### Diagram: Orchestrator Base Pattern

```mermaid
classDiagram
    class ThreeRunCrescendoOrchestrator {
        -websocket_url: str
        -architecture_context: str
        -azure_client: AzureOpenAIClient
        -websocket_target: ChatbotWebSocketTarget
        -db_manager: DuckDBMemoryManager
        -vulnerable_memory: VulnerableResponseMemory
        
        +__init__(websocket_url, architecture_file_path, db_path)
        +run_full_campaign() None
        +execute_attack_run(run_number, attack_plan) RunStatistics
        -_classify_response_risk(prompt, response, context) Tuple
        -_save_run_results(run_number, turns, statistics) None
    }
    
    class AttackPlanGenerator {
        -azure_client: AzureOpenAIClient
        -db_manager: DuckDBMemoryManager
        -strategy_orchestrator: AttackStrategyOrchestrator
        
        +generate_attack_plan(run_number, arch_context, findings) List~AttackPrompt~
        -_generate_llm_based_plan(...) List~AttackPrompt~
        -_generate_strategy_based_plan(...) List~AttackPrompt~
    }
    
    class ConversationContext {
        -window_size: int
        -messages: List~Dict~
        
        +add_exchange(turn, user_msg, assistant_msg) None
        +get_context_string() str
        +get_messages_copy() List
        +reset() None
    }
    
    ThreeRunCrescendoOrchestrator --> AttackPlanGenerator : uses
    ThreeRunCrescendoOrchestrator --> ConversationContext : uses
    ThreeRunCrescendoOrchestrator --> AzureOpenAIClient : uses
    ThreeRunCrescendoOrchestrator --> ChatbotWebSocketTarget : uses
    ThreeRunCrescendoOrchestrator --> DuckDBMemoryManager : uses
```

**Orchestrator Workflow:**

1. `run_full_campaign()`: Executes 3 runs sequentially
2. For each run:
   - Generate attack plan (LLM or fallback)
   - Execute turns (send → receive → classify → store)
   - Save results to JSON
   - Extract and save generalized patterns
3. Generate executive summary

### Diagram: Attack Strategy Pattern

```mermaid
classDiagram
    class BaseAttackStrategy {
        <<abstract>>
        #prompts: List~str~
        #technique_name: str
        #target_nodes: List~str~
        #escalation_phase: str
        
        +get_prompts()* List~str~
        +get_description()* str
        +create_attack_prompts(start_turn) List~AttackPrompt~
    }
    
    class ReconnaissanceStrategy {
        +get_prompts() List~str~
        +get_description() str
    }
    
    class TrustBuildingStrategy {
        +get_prompts() List~str~
        +get_description() str
    }
    
    class BoundaryTestingStrategy {
        +get_prompts() List~str~
        +get_description() str
    }
    
    class ExploitationStrategy {
        +get_prompts() List~str~
        +get_description() str
    }
    
    class AttackStrategyOrchestrator {
        +get_full_attack_plan() List~AttackPrompt~
    }
    
    BaseAttackStrategy <|-- ReconnaissanceStrategy
    BaseAttackStrategy <|-- TrustBuildingStrategy
    BaseAttackStrategy <|-- BoundaryTestingStrategy
    BaseAttackStrategy <|-- ExploitationStrategy
    
    AttackStrategyOrchestrator --> BaseAttackStrategy : combines
```

**Strategy Pattern Benefits:**
- Modular attack phases
- Easy to add new strategies
- Reusable across orchestrators
- Clear separation of concerns

---

## Deployment Diagram

### Overview
This diagram shows the deployment architecture and infrastructure components.

```mermaid
graph TB
    subgraph Developer_Machine
        subgraph Python_Runtime
            API[API Server<br/>FastAPI<br/>Port 8002]
            ORCH[Orchestrators<br/>Python Modules]
            CORE[Core Services<br/>Python Modules]
        end
        
        subgraph Storage
            DB[(DuckDB<br/>chat_memory_db)]
            FILES[JSON Files<br/>attack_results/]
        end
        
        API --> ORCH
        ORCH --> CORE
        CORE --> DB
        ORCH --> FILES
    end
    
    subgraph Azure_Cloud
        AOAI[Azure OpenAI<br/>GPT_4o Deployment<br/>Region US_East]
    end
    
    subgraph Target_Environment
        CHATBOT[Target Chatbot<br/>WebSocket Server<br/>Port 8000]
    end
    
    subgraph Client_Browser
        DASHBOARD[Web Dashboard<br/>HTML/JS/CSS]
    end
    
    CORE -->|HTTPS<br/>REST API| AOAI
    CORE -->|WebSocket<br/>wss://| CHATBOT
    
    DASHBOARD -->|HTTPS<br/>REST| API
    DASHBOARD <-->|WebSocket<br/>ws://| API
    
    style API fill:#4A90E2,stroke:#2E5C8A,stroke-width:3px,color:#fff
    style AOAI fill:#0078D4,stroke:#005A9E,stroke-width:2px,color:#fff
    style CHATBOT fill:#E74C3C,stroke:#C0392B,stroke-width:2px,color:#fff
    style DASHBOARD fill:#27AE60,stroke:#1E8449,stroke-width:2px,color:#fff
```

### Deployment Characteristics

**Development/Testing Environment:**
- Single machine deployment
- Python 3.9+ runtime
- Local file storage (DuckDB + JSON)
- Port 8002 for API server

**Network Communication:**
- **API ↔ Dashboard**: HTTP/WebSocket over local network
- **API ↔ Azure OpenAI**: HTTPS (TLS 1.2+) with API key authentication
- **API ↔ Target Chatbot**: WebSocket (ws:// or wss://)

**Data Flows:**
1. User initiates attack via dashboard
2. API server orchestrates attack execution
3. Core services call Azure OpenAI for LLM tasks
4. Core services communicate with target chatbot
5. Results persisted to DuckDB and JSON files
6. Real-time updates broadcast to dashboard

---

## Scalability Considerations

### Current Architecture Constraints
- Single-server deployment
- Sequential turn execution within runs
- Single DuckDB instance

### Future Scalability Enhancements

```mermaid
graph TB
    subgraph Load_Balancer
        LB[NGINX/HAProxy]
    end
    
    subgraph API_Server_Cluster
        API1[API Server 1]
        API2[API Server 2]
        API3[API Server N]
    end
    
    subgraph Shared_Services
        REDIS[Redis Cache<br/>Session State]
        POSTGRES[(PostgreSQL<br/>Results DB)]
        S3[Object Storage<br/>JSON Archives]
    end
    
    LB --> API1
    LB --> API2
    LB --> API3
    
    API1 --> REDIS
    API2 --> REDIS
    API3 --> REDIS
    
    API1 --> POSTGRES
    API2 --> POSTGRES
    API3 --> POSTGRES
    
    API1 --> S3
    API2 --> S3
    API3 --> S3
    
    style LB fill:#E67E22,stroke:#CA6F1E,stroke-width:2px,color:#fff
    style REDIS fill:#DC143C,stroke:#B71C1C,stroke-width:2px,color:#fff
    style POSTGRES fill:#336791,stroke:#27496D,stroke-width:2px,color:#fff
```

**Enhancements:**
1. **Horizontal Scaling**: Multiple API server instances
2. **State Management**: Redis for shared state
3. **Database Migration**: PostgreSQL for concurrent writes
4. **Object Storage**: S3/Blob for large result files
5. **Message Queue**: RabbitMQ for async task distribution

---

## Security Architecture

### Security Layers

```mermaid
graph TB
    subgraph External_Access
        CLIENT[Client Browser]
    end
    
    subgraph Security_Perimeter
        FIREWALL[Firewall<br/>Port 8002 Only]
        TLS[TLS Termination<br/>HTTPS Enforcement]
    end
    
    subgraph Application_Security
        AUTH[API Authentication<br/>Future Enhancement]
        CORS[CORS Policy<br/>Origin Validation]
        VALIDATE[Input Validation<br/>Pydantic Models]
    end
    
    subgraph Data_Security
        ENV[Environment Variables<br/>API Keys]
        ENCRYPT[Encryption at Rest<br/>Future Enhancement]
    end
    
    CLIENT --> FIREWALL
    FIREWALL --> TLS
    TLS --> AUTH
    AUTH --> CORS
    CORS --> VALIDATE
    
    VALIDATE -.->|Protected Access| ENV
    VALIDATE -.->|Stores| ENCRYPT
    
    style FIREWALL fill:#E74C3C,stroke:#C0392B,stroke-width:2px,color:#fff
    style AUTH fill:#F39C12,stroke:#D68910,stroke-width:2px,color:#fff
    style ENCRYPT fill:#27AE60,stroke:#1E8449,stroke-width:2px,color:#fff
```

**Current Security Measures:**
- CORS middleware for origin control
- Environment variable secrets management
- Input validation via Pydantic
- HTTPS for Azure OpenAI communication

**Future Enhancements:**
- API key authentication
- Role-based access control (RBAC)
- Audit logging
- Encrypted storage for sensitive results

---

## Document Control

**Diagram Standards:**
- All diagrams use Mermaid.js format
- Alphanumeric characters and underscores only for labels
- Color coding: Blue (Platform), Red (External/Risk), Green (Success), Purple (Storage)

**Review Schedule:**
- Next Review: March 2026
- Review Frequency: Quarterly
- Reviewers: Architecture Team, Security Team

---

**References:**
- [C4 Model Documentation](https://c4model.com/)
- [Mermaid.js Diagram Syntax](https://mermaid.js.org/)
- [FastAPI Architecture Best Practices](https://fastapi.tiangolo.com/deployment/)
