# AI Red Teaming Platform - Complete Project Documentation

> **Version:** 1.0.0  
> **Last Updated:** December 11, 2025  
> **Project:** AI Chatbot Security Testing & Red Teaming Platform

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement & Objectives](#2-problem-statement--objectives)
3. [System Architecture](#3-system-architecture)
4. [Functional & Non-Functional Requirements](#4-functional--non-functional-requirements)
5. [Tech Stack & Design Decisions](#5-tech-stack--design-decisions)
6. [High-Level & Low-Level Design](#6-high-level--low-level-design)
7. [System Diagrams](#7-system-diagrams)
8. [API Specifications](#8-api-specifications)
9. [Data Models](#9-data-models)
10. [User Journeys & Use Cases](#10-user-journeys--use-cases)
11. [Process Flows](#11-process-flows)
12. [Testing Strategy & QA Plan](#12-testing-strategy--qa-plan)
13. [Security Considerations](#13-security-considerations)
14. [Future Enhancements](#14-future-enhancements)
15. [Conclusion](#15-conclusion)

---

## 1. Executive Summary

### 1.1 Project Overview

The **AI Red Teaming Platform** is a comprehensive security testing framework designed to evaluate and identify vulnerabilities in AI-powered chatbots through automated adversarial attacks. The platform employs multiple sophisticated attack methodologies including Standard Multi-Phase Attacks, Crescendo (Social Engineering), Skeleton Key (Jailbreak), and Obfuscation techniques to systematically probe chatbot defenses.

### 1.2 Key Features

- **Multi-Category Attack System**: Four distinct attack categories with specialized techniques
- **Architecture-Aware Testing**: Uses chatbot architecture documentation to generate targeted attacks
- **Real-Time Monitoring**: WebSocket-based live attack visualization through web interface
- **Adaptive Learning**: Learns from previous attack patterns stored in DuckDB
- **Comprehensive Reporting**: Detailed JSON reports with vulnerability classifications
- **Automated Orchestration**: Executes 3 runs per category with configurable turn counts
- **Azure OpenAI Integration**: Leverages GPT-4 for intelligent attack generation

### 1.3 Business Value

- **Enhanced Security Posture**: Identifies vulnerabilities before malicious actors do
- **Compliance Support**: Helps organizations meet AI safety and security standards
- **Cost Reduction**: Automates manual penetration testing efforts
- **Risk Mitigation**: Provides quantitative risk assessments with 5-tier classification
- **Continuous Improvement**: Enables iterative security hardening cycles

### 1.4 Project Scope

**In Scope:**
- Red teaming for chatbot applications
- WebSocket-based target communication
- Real-time monitoring dashboard
- Automated report generation
- Multiple attack methodologies
- Conversation memory management

**Out of Scope:**
- Production deployment infrastructure
- Authentication/authorization systems
- Multi-tenant support
- Mobile applications
- Chatbot implementation (provides testing agent only)

---

## 2. Problem Statement & Objectives

### 2.1 Problem Statement

AI-powered chatbots are increasingly deployed in customer-facing applications, handling sensitive information and critical business processes. However, these systems are vulnerable to:

1. **Prompt Injection Attacks**: Manipulating LLM behavior through crafted inputs
2. **Jailbreak Attempts**: Bypassing safety guardrails and content policies
3. **Information Disclosure**: Leaking system architecture, prompts, or confidential data
4. **Social Engineering**: Exploiting conversational context to extract sensitive information
5. **Guardrail Evasion**: Using obfuscation techniques to circumvent security measures

**Current Challenges:**
- Manual penetration testing is time-consuming and inconsistent
- Lack of specialized tools for AI/LLM security testing
- Difficult to assess security posture comprehensively
- No standardized methodology for AI red teaming
- Limited visibility into real-time attack progression

### 2.2 Project Objectives

#### Primary Objectives

1. **Automated Security Assessment**
   - Execute 4 categories of attacks automatically
   - Generate comprehensive vulnerability reports
   - Classify findings by risk severity (5-tier system)

2. **Architecture-Aware Testing**
   - Parse chatbot architecture documentation
   - Generate context-specific attack prompts
   - Target identified system components

3. **Real-Time Visibility**
   - Provide web-based monitoring interface
   - Display turn-by-turn attack progression
   - Show live vulnerability detection

4. **Adaptive Attack Generation**
   - Learn from previous attack patterns
   - Adapt strategies based on chatbot responses
   - Use LLM-powered attack synthesis

#### Secondary Objectives

1. **Comprehensive Documentation**
   - Detailed attack methodologies
   - Setup and deployment guides
   - API documentation

2. **Extensibility**
   - Modular attack strategy architecture
   - Easy integration of new attack types
   - Configurable parameters

3. **Reproducibility**
   - Consistent attack execution
   - Detailed logging
   - Historical pattern storage

### 2.3 Success Criteria

- ✅ Execute 210+ attack turns across 4 categories
- ✅ Identify and classify vulnerabilities accurately
- ✅ Provide real-time WebSocket updates (< 100ms latency)
- ✅ Generate structured JSON reports
- ✅ Support chatbot architecture parsing
- ✅ Store attack patterns in persistent database
- ✅ Web-based monitoring interface
- ✅ Comprehensive technical documentation

---

## 3. System Architecture

### 3.1 Architecture Overview

The AI Red Teaming Platform follows a **three-tier architecture** with clear separation between:
1. **Frontend Layer**: Web-based real-time monitoring interface
2. **Backend Layer**: FastAPI server with attack orchestration
3. **Data Layer**: DuckDB for persistence and Azure OpenAI for intelligence

### 3.2 Core Components

#### 3.2.1 Frontend (Web Interface)
- **Technology**: HTML5, CSS3, Vanilla JavaScript
- **Communication**: WebSocket (ws://localhost:8080/ws/attack-monitor)
- **Responsibilities**:
  - Attack configuration and initiation
  - Real-time log display
  - Category and run visualization
  - WebSocket connection management

#### 3.2.2 Backend (FastAPI Server)
- **Technology**: Python 3.11+, FastAPI, Uvicorn
- **Port**: 8080
- **Responsibilities**:
  - REST API endpoints
  - WebSocket broadcast management
  - Attack orchestration coordination
  - File upload handling
  - Result persistence

#### 3.2.3 Attack Orchestrators
- **StandardAttack**: 3 runs × 25 turns (traditional multi-phase)
- **CrescendoAttack**: 3 runs × 15 turns (personality-based social engineering)
- **SkeletonKeyAttack**: 3 runs × 10 turns (jailbreak techniques)
- **ObfuscationAttack**: 3 runs × 20 turns (evasion methods)

#### 3.2.4 Azure OpenAI Integration
- **Model**: GPT-4o
- **Purpose**: Intelligent attack prompt generation
- **Fallback**: Pre-defined attack strategy library

#### 3.2.5 Target Chatbot Interface
- **Protocol**: WebSocket
- **Default**: ws://localhost:8000/chat
- **Testing Agent**: Provided Azure OpenAI e-commerce agent

#### 3.2.6 Data Persistence
- **Database**: DuckDB (chat_memory.db)
- **Storage**: JSON files in attack_results/
- **Purpose**: Attack patterns, conversation history, findings

### 3.3 System Boundaries

**Internal Systems:**
- Frontend web interface
- FastAPI backend server
- Attack orchestrators
- Database (DuckDB)
- Result storage

**External Systems:**
- Azure OpenAI API
- Target chatbot (WebSocket endpoint)
- User's web browser

**Network Boundaries:**
- localhost:8080 (Backend API)
- localhost:8001 (Testing agent)
- Azure OpenAI endpoints (HTTPS)

---

## 4. Functional & Non-Functional Requirements

### 4.1 Functional Requirements

#### FR1: Attack Configuration
- **FR1.1**: System SHALL accept WebSocket URL input for target chatbot
- **FR1.2**: System SHALL accept architecture file upload (.md/.txt format)
- **FR1.3**: System SHALL validate configuration parameters before attack initiation
- **FR1.4**: System SHALL support environment variable configuration

#### FR2: Attack Execution
- **FR2.1**: System SHALL execute 4 attack categories sequentially
- **FR2.2**: System SHALL perform 3 runs per category
- **FR2.3**: System SHALL execute configured turns per run (10-25 based on category)
- **FR2.4**: System SHALL maintain conversation context (sliding window of 6 turns)
- **FR2.5**: System SHALL retry failed WebSocket connections (max 2 retries)
- **FR2.6**: System SHALL timeout unresponsive requests (15 seconds default)

#### FR3: Attack Generation
- **FR3.1**: System SHALL parse architecture documentation to extract components
- **FR3.2**: System SHALL generate architecture-aware attack prompts using Azure OpenAI
- **FR3.3**: System SHALL fall back to pre-defined strategy library if LLM fails
- **FR3.4**: System SHALL load historical patterns from database for adaptive attacks
- **FR3.5**: System SHALL support safe mode for content-filtered environments

#### FR4: Response Analysis
- **FR4.1**: System SHALL classify responses into 5 risk categories
- **FR4.2**: System SHALL detect vulnerability types (info disclosure, bypass, etc.)
- **FR4.3**: System SHALL extract relevant context from responses
- **FR4.4**: System SHALL determine attack success/failure

#### FR5: Real-Time Monitoring
- **FR5.1**: System SHALL broadcast attack progress via WebSocket
- **FR5.2**: System SHALL send turn_started events before each turn
- **FR5.3**: System SHALL send turn_completed events after response analysis
- **FR5.4**: System SHALL update category and run status
- **FR5.5**: System SHALL maintain connection with auto-reconnect

#### FR6: Reporting
- **FR6.1**: System SHALL generate JSON reports for each run
- **FR6.2**: System SHALL include executive summary with statistics
- **FR6.3**: System SHALL list all vulnerability findings
- **FR6.4**: System SHALL provide conversation transcript
- **FR6.5**: System SHALL store generalized attack patterns

#### FR7: Data Management
- **FR7.1**: System SHALL persist conversation history to DuckDB
- **FR7.2**: System SHALL store attack results as JSON files
- **FR7.3**: System SHALL manage uploaded architecture files
- **FR7.4**: System SHALL query historical patterns for adaptive learning

### 4.2 Non-Functional Requirements

#### NFR1: Performance
- **NFR1.1**: WebSocket message latency SHALL be < 100ms
- **NFR1.2**: Attack prompt generation SHALL complete within 10 seconds
- **NFR1.3**: Database queries SHALL return within 1 second
- **NFR1.4**: System SHALL handle 1000+ messages/second throughput

#### NFR2: Scalability
- **NFR2.1**: System SHALL support multiple concurrent WebSocket connections
- **NFR2.2**: Database SHALL efficiently store 10,000+ attack patterns
- **NFR2.3**: Frontend SHALL handle 100+ log entries without performance degradation

#### NFR3: Reliability
- **NFR3.1**: System SHALL achieve 99% uptime during testing sessions
- **NFR3.2**: Failed attacks SHALL not crash the orchestrator
- **NFR3.3**: WebSocket disconnections SHALL trigger automatic reconnection
- **NFR3.4**: System SHALL gracefully handle Azure OpenAI API failures

#### NFR4: Security
- **NFR4.1**: API keys SHALL be stored in environment variables (not code)
- **NFR4.2**: Uploaded files SHALL be validated for type and size
- **NFR4.3**: WebSocket messages SHALL be JSON-validated
- **NFR4.4**: System SHALL sanitize user inputs in frontend display

#### NFR5: Maintainability
- **NFR5.1**: Code SHALL follow modular architecture with clear separation of concerns
- **NFR5.2**: Each orchestrator SHALL extend base classes
- **NFR5.3**: Configuration SHALL be centralized in settings.py
- **NFR5.4**: Code SHALL include comprehensive docstrings

#### NFR6: Usability
- **NFR6.1**: Setup process SHALL complete in < 10 minutes
- **NFR6.2**: Web interface SHALL be intuitive without training
- **NFR6.3**: Error messages SHALL be clear and actionable
- **NFR6.4**: Documentation SHALL include quick-start guides

#### NFR7: Compatibility
- **NFR7.1**: Backend SHALL support Python 3.11+
- **NFR7.2**: Frontend SHALL work on Chrome, Firefox, Edge (latest versions)
- **NFR7.3**: System SHALL run on Windows and Linux
- **NFR7.4**: WebSocket SHALL follow RFC 6455 standard

---

## 5. Tech Stack & Design Decisions

### 5.1 Technology Stack

#### 5.1.1 Backend Technologies

| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| **Web Framework** | FastAPI | 0.121.2 | Async support, auto-documentation, WebSocket, performance |
| **Web Server** | Uvicorn | 0.38.0 | ASGI server, production-ready, WebSocket support |
| **LLM Integration** | Azure OpenAI | GPT-4o | Enterprise-grade, content safety, powerful generation |
| **Database** | DuckDB | N/A | Embedded, analytical queries, zero-config |
| **WebSocket** | websockets | 12.0 | Reliable, well-tested, async/await support |
| **Data Validation** | Pydantic | 2.12.3 | Type safety, validation, FastAPI integration |
| **Language** | Python | 3.11+ | Rich ecosystem, async support, AI libraries |

#### 5.1.2 Frontend Technologies

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **UI Framework** | Vanilla HTML/CSS/JS | No build step, simple deployment, low overhead |
| **WebSocket Client** | Native WebSocket API | Browser-native, no dependencies |
| **Styling** | Custom CSS3 | Full control, animations, responsive design |

#### 5.1.3 Infrastructure

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Environment Mgmt** | python-dotenv | Secure credential management |
| **Async Runtime** | asyncio | Native Python async, efficient I/O |
| **HTTP Client** | httpx | Async HTTP, modern, well-maintained |

### 5.2 Key Design Decisions

#### Decision 1: Why FastAPI over Flask?

**Chosen**: FastAPI  
**Alternative Considered**: Flask

**Rationale**:
- ✅ Native async/await support (critical for concurrent attacks)
- ✅ Built-in WebSocket support (no extensions needed)
- ✅ Automatic OpenAPI documentation
- ✅ Pydantic integration for type safety
- ✅ Better performance (~3x faster than Flask)
- ✅ Modern Python features (type hints)

#### Decision 2: Why DuckDB over PostgreSQL/SQLite?

**Chosen**: DuckDB  
**Alternatives Considered**: PostgreSQL, SQLite

**Rationale**:
- ✅ Zero configuration (embedded database)
- ✅ Optimized for analytical queries (pattern analysis)
- ✅ Excellent Python integration
- ✅ OLAP-style aggregations for reporting
- ✅ No separate server process required
- ✅ Handles complex JSON better than SQLite
- ❌ PostgreSQL would add deployment complexity

#### Decision 3: Why Azure OpenAI over OpenAI API?

**Chosen**: Azure OpenAI  
**Alternative Considered**: OpenAI API directly

**Rationale**:
- ✅ Enterprise SLA and support
- ✅ Data residency compliance
- ✅ Enhanced content safety filters
- ✅ Private network deployment options
- ✅ Integration with Azure ecosystem
- ✅ Fixed pricing models
- ❌ Slightly more complex authentication

#### Decision 4: Why Vanilla JavaScript over React/Vue?

**Chosen**: Vanilla JavaScript  
**Alternatives Considered**: React, Vue.js

**Rationale**:
- ✅ No build process required
- ✅ Simple deployment (single HTML file)
- ✅ Lower learning curve for contributors
- ✅ Faster initial load time
- ✅ Adequate for current UI complexity
- ❌ React/Vue would add build tooling overhead

#### Decision 5: Why WebSocket over Server-Sent Events (SSE)?

**Chosen**: WebSocket  
**Alternative Considered**: Server-Sent Events

**Rationale**:
- ✅ Bidirectional communication (potential future use)
- ✅ Binary data support (if needed)
- ✅ Better connection management
- ✅ Industry standard for real-time updates
- ✅ More flexibility for future features
- ⚖️ SSE simpler but less flexible

#### Decision 6: Orchestrator Architecture Pattern

**Chosen**: Strategy Pattern with Orchestrator Coordinator  
**Alternatives Considered**: Command Pattern, Monolithic

**Rationale**:
- ✅ Each attack type is independent module
- ✅ Easy to add new attack categories
- ✅ Clear separation of concerns
- ✅ Reusable base classes
- ✅ Testable in isolation
- ✅ Configurable behavior

### 5.3 Architecture Patterns

#### 5.3.1 Design Patterns Used

1. **Strategy Pattern**
   - Location: `attack_strategies/`
   - Purpose: Pluggable attack strategies
   - Implementation: `BaseAttackStrategy` with concrete implementations

2. **Factory Pattern**
   - Location: `AttackStrategyOrchestrator`
   - Purpose: Create appropriate attack strategies
   - Implementation: Dynamic strategy instantiation

3. **Observer Pattern**
   - Location: WebSocket broadcast system
   - Purpose: Real-time updates to multiple clients
   - Implementation: `ConnectionManager.broadcast()`

4. **Singleton Pattern**
   - Location: `ConnectionManager` in api_server
   - Purpose: Single WebSocket manager instance
   - Implementation: Module-level instantiation

5. **Template Method Pattern**
   - Location: Base orchestrator classes
   - Purpose: Define attack execution skeleton
   - Implementation: `execute_run()` with customizable steps

#### 5.3.2 Architectural Styles

1. **Microservices-Adjacent**
   - Attack orchestrators are loosely coupled
   - Each category can run independently
   - Clear interfaces between components

2. **Event-Driven**
   - WebSocket events drive UI updates
   - Attack progress triggers broadcasts
   - Asynchronous message handling

3. **Layered Architecture**
   - Presentation (Frontend)
   - Application (FastAPI)
   - Business Logic (Orchestrators)
   - Data Access (DuckDB)


---

## 6. High-Level & Low-Level Design

### 6.1 High-Level Design

#### 6.1.1 System Context Diagram

```
┌─────────────────┐
│                 │
│   Security      │
│   Researcher    │
│                 │
└────────┬────────┘
         │
         │ Configures & Monitors
         │
┌────────▼─────────────────────────────────────────────┐
│                                                        │
│         AI Red Teaming Platform                        │
│                                                        │
│  ┌──────────┐  ┌────────────┐  ┌─────────────────┐  │
│  │ Frontend │  │  Backend   │  │   Orchestrators │  │
│  │   Web    │◄─┤  FastAPI   │◄─┤   4 Categories  │  │
│  │Interface │  │  Server    │  │                 │  │
│  └──────────┘  └─────┬──────┘  └────────┬────────┘  │
│                      │                   │            │
│                 ┌────▼──────┐       ┌───▼─────┐     │
│                 │  DuckDB   │       │ Attack  │     │
│                 │  Memory   │       │Strategy │     │
│                 │           │       │ Library │     │
│                 └───────────┘       └─────────┘     │
└─────────────────────┬──────────────────────┬────────┘
                      │                      │
                      │                      │
         ┌────────────▼────────┐    ┌────────▼─────────┐
         │   Azure OpenAI      │    │ Target Chatbot   │
         │   GPT-4o API        │    │ (WebSocket)      │
         └─────────────────────┘    └──────────────────┘
```

#### 6.1.2 Logical Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
│  ┌───────────────────────────────────────────────────────┐ │
│  │         Web Interface (index.html)                     │ │
│  │  - Attack Configuration  - Real-time Monitoring        │ │
│  │  - Category Tabs        - Turn Log Display            │ │
│  └───────────────────────────────────────────────────────┘ │
└────────────────────┬───────────────────────────────────────┘
                     │ WebSocket + REST
┌────────────────────▼───────────────────────────────────────┐
│                   APPLICATION LAYER                         │
│  ┌───────────────────────────────────────────────────────┐ │
│  │              FastAPI Backend (api_server.py)          │ │
│  │  - REST Endpoints      - WebSocket Manager            │ │
│  │  - File Upload         - Connection Broadcasting      │ │
│  └──────┬─────────────────────────────────┬──────────────┘ │
│         │                                 │                 │
│  ┌──────▼──────────┐            ┌────────▼─────────────┐  │
│  │ Attack          │            │ WebSocket Broadcast   │  │
│  │ Coordinator     │            │ Utility               │  │
│  └──────┬──────────┘            └──────────────────────┘  │
└─────────┼──────────────────────────────────────────────────┘
          │
┌─────────▼──────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Standard    │  │  Crescendo   │  │ Skeleton Key │     │
│  │ Orchestrator │  │ Orchestrator │  │ Orchestrator │     │
│  │ (25 turns)   │  │ (15 turns)   │  │ (10 turns)   │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │             │
│  ┌──────▼──────────────────▼──────────────────▼────────┐  │
│  │         Obfuscation Orchestrator (20 turns)         │  │
│  └──────┬──────────────────────────────────────────────┘  │
│         │                                                   │
│  ┌──────▼──────────────────────────────────────────────┐  │
│  │           Attack Plan Generator                      │  │
│  │  - LLM-based prompt generation                       │  │
│  │  - Strategy library fallback                         │  │
│  │  - Adaptive learning from patterns                   │  │
│  └──────┬────────────────────────────┬──────────────────┘  │
└─────────┼────────────────────────────┼─────────────────────┘
          │                            │
┌─────────▼──────────┐        ┌────────▼─────────────────────┐
│   DATA ACCESS      │        │   INTEGRATION LAYER          │
│                    │        │                              │
│ ┌────────────────┐ │        │  ┌─────────────────────┐    │
│ │ DuckDB Manager │ │        │  │ Azure OpenAI Client │    │
│ │ - Patterns     │ │        │  │ - GPT-4o calls      │    │
│ │ - History      │ │        │  │ - Retry logic       │    │
│ └────────────────┘ │        │  └─────────────────────┘    │
│                    │        │                              │
│ ┌────────────────┐ │        │  ┌─────────────────────┐    │
│ │ JSON Storage   │ │        │  │ WebSocket Target    │    │
│ │ - Results      │ │        │  │ - Chatbot client    │    │
│ │ - Reports      │ │        │  │ - Retry handling    │    │
│ └────────────────┘ │        │  └─────────────────────┘    │
└────────────────────┘        └──────────────────────────────┘
```

### 6.2 Low-Level Design

#### 6.2.1 Class Diagram (Core Components)

```python
# Base Classes

class BaseAttackStrategy:
    + technique_name: str
    + target_nodes: List[str]
    + escalation_phase: str
    
    + get_description() -> str
    + get_prompts() -> List[str]
    + create_attack_prompts(start_turn: int) -> List[AttackPrompt]

class BaseOrchestrator:
    + azure_client: AzureOpenAIClient
    + websocket_target: ChatbotWebSocketTarget
    + db_manager: DuckDBMemoryManager
    + architecture_context: str
    
    + execute_campaign() -> Dict
    + execute_run(run_number: int) -> Dict
    + execute_turn(turn: int, attack_prompt: AttackPrompt) -> Dict
    + analyze_response(response: str) -> VulnerabilityFinding
    
# Concrete Orchestrators

class ThreeRunCrescendoOrchestrator(BaseOrchestrator):
    + conversation_context: ConversationContext
    + attack_plan_generator: AttackPlanGenerator
    + vulnerable_response_memory: VulnerableResponseMemory
    
    + execute_campaign() -> Dict
    
class CrescendoAttackOrchestrator(BaseOrchestrator):
    + personality_profiles: List[str]
    + social_engineering_techniques: Dict
    
    + generate_personality_prompt(profile: str) -> str
    + execute_run(run_number: int) -> Dict
    
class SkeletonKeyAttackOrchestrator(BaseOrchestrator):
    + jailbreak_seeds: List[str]
    + transformation_prompts: Dict
    
    + transform_seed(seed: str) -> str
    + execute_run(run_number: int) -> Dict
    
class ObfuscationAttackOrchestrator(BaseOrchestrator):
    + obfuscation_techniques: List[str]
    + encoding_methods: Dict
    
    + apply_obfuscation(prompt: str, technique: str) -> str
    + execute_run(run_number: int) -> Dict

# Utility Classes

class ConversationContext:
    + window_size: int = 6
    + messages: List[Dict]
    
    + add_exchange(turn: int, user: str, assistant: str)
    + get_context_string() -> str
    + get_messages_copy() -> List[Dict]
    + reset()

class AttackPlanGenerator:
    + azure_client: AzureOpenAIClient
    + db_manager: DuckDBMemoryManager
    + strategy_orchestrator: AttackStrategyOrchestrator
    
    + generate_attack_plan(run: int, context: str) -> List[AttackPrompt]
    + generate_llm_attack(turn: int, context: str) -> AttackPrompt
    + get_fallback_attack(turn: int) -> AttackPrompt

class VulnerableResponseMemory:
    + findings: List[VulnerabilityFinding]
    + patterns: Dict[str, int]
    
    + add_finding(finding: VulnerabilityFinding)
    + get_patterns_summary() -> str
    + get_high_risk_findings() -> List[VulnerabilityFinding]

class DuckDBMemoryManager:
    + db_path: str
    + conn: duckdb.Connection
    
    + store_exchange(turn: int, user: str, assistant: str)
    + store_pattern(pattern: GeneralizedPattern)
    + get_recent_patterns(limit: int) -> List[GeneralizedPattern]
    + query_by_risk(risk_category: int) -> List[Dict]

class AzureOpenAIClient:
    + endpoint: str
    + api_key: str
    + deployment: str
    + max_retries: int = 3
    
    + generate_completion(messages: List[Dict]) -> str
    + handle_content_filter_error()
    + calculate_backoff(attempt: int) -> float

class ChatbotWebSocketTarget:
    + url: str
    + timeout: float = 15.0
    + max_retries: int = 2
    
    + send_message(message: str) -> str
    + connect() -> websocket
    + disconnect()
    + is_connected() -> bool
```

#### 6.2.2 Attack Execution Sequence

```
Orchestrator.execute_campaign()
    │
    ├─► Load architecture context
    │
    ├─► For run in [1, 2, 3]:
    │   │
    │   ├─► execute_run(run_number)
    │   │   │
    │   │   ├─► Generate attack plan (25/15/10/20 turns)
    │   │   │   ├─► Try: LLM generation with architecture context
    │   │   │   └─► Fallback: Pre-defined strategy library
    │   │   │
    │   │   ├─► Initialize conversation context
    │   │   │
    │   │   ├─► For turn in attack_plan:
    │   │   │   │
    │   │   │   ├─► broadcast("turn_started")
    │   │   │   │
    │   │   │   ├─► execute_turn(turn, attack_prompt)
    │   │   │   │   ├─► Get context from sliding window
    │   │   │   │   ├─► Send prompt to chatbot (WebSocket)
    │   │   │   │   ├─► Receive response (with timeout)
    │   │   │   │   ├─► Store in DuckDB
    │   │   │   │   └─► Return response
    │   │   │   │
    │   │   │   ├─► analyze_response(response)
    │   │   │   │   ├─► LLM-based risk classification (1-5)
    │   │   │   │   ├─► Vulnerability type detection
    │   │   │   │   ├─► Create VulnerabilityFinding object
    │   │   │   │   └─► Store in vulnerable_response_memory
    │   │   │   │
    │   │   │   ├─► Update conversation context
    │   │   │   │
    │   │   │   └─► broadcast("turn_completed")
    │   │   │
    │   │   ├─► Generate run statistics
    │   │   │
    │   │   └─► Save run results to JSON
    │   │
    │   └─► broadcast("run_completed")
    │
    ├─► Generate executive summary
    │
    ├─► Extract generalized patterns
    │
    ├─► Store patterns in DuckDB
    │
    └─► broadcast("campaign_completed")
```

#### 6.2.3 WebSocket Communication Flow

```
Backend: ConnectionManager.broadcast(message)
    │
    ├─► For each active_connection in connections:
    │   │
    │   ├─► Try: connection.send_json(message)
    │   │   ├─► Success: Continue
    │   │   └─► Error: Mark for removal
    │   │
    │   └─► Remove disconnected clients
    │
    └─► Message delivered to all clients

Frontend: WebSocket.onmessage(event)
    │
    ├─► Parse JSON message
    │
    ├─► Switch message.type:
    │   │
    │   ├─► "attack_started":
    │   │   └─► Update status panel
    │   │
    │   ├─► "category_started":
    │   │   └─► Highlight category tab
    │   │
    │   ├─► "turn_started":
    │   │   ├─► Update current run/turn
    │   │   └─► Add log entry (orange)
    │   │
    │   ├─► "turn_completed":
    │   │   ├─► Update run statistics
    │   │   ├─► Increment vulnerability counter if found
    │   │   └─► Add log entry (green/red)
    │   │
    │   ├─► "category_completed":
    │   │   └─► Mark category as complete
    │   │
    │   └─► "campaign_completed":
    │       └─► Display final summary
    │
    └─► Auto-scroll to latest entry
```

#### 6.2.4 Database Schema (DuckDB)

```sql
-- Table: conversation_history
CREATE TABLE conversation_history (
    id INTEGER PRIMARY KEY,
    session_id VARCHAR,
    turn INTEGER,
    role VARCHAR,  -- 'user' or 'assistant'
    content TEXT,
    timestamp TIMESTAMP,
    category VARCHAR,  -- 'standard', 'crescendo', 'skeleton_key', 'obfuscation'
    run_number INTEGER
);

-- Table: attack_patterns
CREATE TABLE attack_patterns (
    id INTEGER PRIMARY KEY,
    pattern_id VARCHAR UNIQUE,
    attack_type VARCHAR,
    technique VARCHAR,
    description TEXT,
    category VARCHAR,
    risk_level VARCHAR,
    indicators JSON,
    success_count INTEGER,
    metadata JSON,
    created_at TIMESTAMP
);

-- Table: vulnerability_findings
CREATE TABLE vulnerability_findings (
    id INTEGER PRIMARY KEY,
    run_number INTEGER,
    turn INTEGER,
    risk_category INTEGER,
    vulnerability_type VARCHAR,
    attack_prompt TEXT,
    chatbot_response TEXT,
    context_messages JSON,
    attack_technique VARCHAR,
    target_nodes JSON,
    timestamp TIMESTAMP,
    category VARCHAR
);

-- Indexes
CREATE INDEX idx_patterns_category ON attack_patterns(category);
CREATE INDEX idx_patterns_risk ON attack_patterns(risk_level);
CREATE INDEX idx_findings_risk ON vulnerability_findings(risk_category);
CREATE INDEX idx_findings_type ON vulnerability_findings(vulnerability_type);
CREATE INDEX idx_history_session ON conversation_history(session_id, turn);
```

#### 6.2.5 File Structure

```
RedTeaming/
├── BACKEND/
│   ├── api_server.py                 # FastAPI application entry point
│   ├── main.py                       # CLI orchestrator launcher
│   ├── requirements.txt              # Python dependencies
│   ├── requirements_api.txt          # API-specific dependencies
│   ├── start_backend.ps1             # Windows startup script
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py               # Configuration management
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── orchestrator.py           # Standard attack orchestrator
│   │   ├── crescendo_orchestrator.py # Crescendo attack orchestrator
│   │   ├── skeleton_key_orchestrator.py  # Skeleton key orchestrator
│   │   ├── obfuscation_orchestrator.py   # Obfuscation orchestrator
│   │   ├── azure_client.py           # Azure OpenAI client
│   │   ├── websocket_target.py       # Target chatbot client
│   │   ├── websocket_broadcast.py    # WebSocket broadcast utility
│   │   └── memory_manager.py         # DuckDB management
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── data_models.py            # Pydantic/dataclass models
│   │   └── ATTACK_RESULTS_JSON_FORMAT.md
│   │
│   ├── attack_strategies/
│   │   ├── __init__.py
│   │   ├── base_strategy.py          # Abstract base class
│   │   ├── orchestrator.py           # Strategy coordinator
│   │   ├── reconnaissance.py         # Phase 1 strategies
│   │   ├── trust_building.py         # Phase 2 strategies
│   │   ├── boundary_testing.py       # Phase 3 strategies
│   │   ├── exploitation.py           # Phase 4 strategies
│   │   ├── obfuscation.py            # Obfuscation techniques
│   │   └── README.md
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── architecture_utils.py     # Architecture parsing
│   │
│   ├── testing/
│   │   ├── __init__.py
│   │   ├── gemini_agent.py           # Testing chatbot agent
│   │   ├── test_agent.py             # Agent tests
│   │   └── README.md
│   │
│   ├── docs/
│   │   ├── SKELETON_KEY_QUICKSTART.md
│   │   ├── OBFUSCATION_ATTACK_DOCUMENTATION.md
│   │   └── OBFUSCATION_CRESCENDO_IMPLEMENTATION.md
│   │
│   ├── attack_results/              # JSON output files
│   ├── attack_reports/              # Generated reports
│   ├── uploads/                     # Uploaded architecture files
│   └── chat_memory.db               # DuckDB database file
│
├── FRONTEND/
│   ├── index.html                   # Main web interface
│   └── quick_start.html             # Quick start guide
│
├── QUICKSTART.md
├── SETUP_GUIDE.md
├── REAL_TIME_MONITORING.md
└── IMPLEMENTATION_COMPLETE.md
```


---

## 6. High-Level & Low-Level Design

### 6.1 High-Level Design

The system follows a three-tier architecture with clear separation between presentation, application, and data layers. The frontend communicates with the backend via WebSocket for real-time updates and REST API for configuration. The backend orchestrates attacks through specialized orchestrators that interface with Azure OpenAI for intelligence and target chatbots for testing.

### 6.2 Component Interaction

**Frontend → Backend**: HTTP POST (attack config), WebSocket (real-time updates)
**Backend → Orchestrators**: Direct Python function calls (async)
**Orchestrators → Azure OpenAI**: HTTPS REST API calls
**Orchestrators → Target**: WebSocket messages
**Orchestrators → Database**: DuckDB SQL queries

### 6.3 Low-Level Design Details

See sections 3 and 7 for detailed component breakdowns including class diagrams, sequence diagrams, and data flow specifications.

---

## 7. System Diagrams

### 7.1 Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
    end
    
    subgraph "Presentation Layer"
        Frontend[Frontend Web Interface<br/>HTML/CSS/JavaScript]
    end
    
    subgraph "Application Layer"
        API[FastAPI Backend Server<br/>Port 8080]
        WSManager[WebSocket Connection Manager]
        Coordinator[Attack Coordinator]
    end
    
    subgraph "Business Logic Layer"
        Orch1[Standard Attack Orchestrator<br/>3 runs × 25 turns]
        Orch2[Crescendo Attack Orchestrator<br/>3 runs × 15 turns]
        Orch3[Skeleton Key Orchestrator<br/>3 runs × 10 turns]
        Orch4[Obfuscation Orchestrator<br/>3 runs × 20 turns]
        
        APG[Attack Plan Generator]
        Memory[Vulnerable Response Memory]
        Context[Conversation Context]
    end
    
    subgraph "Data Access Layer"
        DuckDB[(DuckDB<br/>chat_memory.db)]
        JSON[JSON Files<br/>attack_results/]
    end
    
    subgraph "External Systems"
        Azure[Azure OpenAI<br/>GPT-4o API]
        Target[Target Chatbot<br/>WebSocket]
    end
    
    Browser -->|HTTP/WebSocket| Frontend
    Frontend -->|REST API| API
    Frontend <-->|WebSocket| WSManager
    API --> Coordinator
    WSManager --> Coordinator
    
    Coordinator --> Orch1
    Coordinator --> Orch2
    Coordinator --> Orch3
    Coordinator --> Orch4
    
    Orch1 --> APG
    Orch2 --> APG
    Orch3 --> APG
    Orch4 --> APG
    
    APG --> Memory
    APG --> Context
    APG -->|LLM Calls| Azure
    
    Orch1 -->|Query Patterns| DuckDB
    Orch1 -->|Store Results| JSON
    Orch1 -->|Send Prompts| Target
    
    Orch2 --> DuckDB
    Orch2 --> JSON
    Orch2 --> Target
    
    Orch3 --> DuckDB
    Orch3 --> JSON
    Orch3 --> Target
    
    Orch4 --> DuckDB
    Orch4 --> JSON
    Orch4 --> Target
    
    style Browser fill:#e1f5ff
    style Frontend fill:#bbdefb
    style API fill:#90caf9
    style DuckDB fill:#ffd54f
    style Azure fill:#81c784
    style Target fill:#ff8a65
```

### 7.2 Workflow Diagram

```mermaid
flowchart TD
    Start([User Starts Attack Campaign]) --> Config[Configure Attack<br/>- WebSocket URL<br/>- Architecture File]
    Config --> Upload[Upload Architecture File]
    Upload --> Submit[Submit to Backend]
    
    Submit --> Parse[Parse Architecture Context]
    Parse --> Init[Initialize Orchestrators]
    
    Init --> Cat1{Execute Category 1<br/>Standard Attack}
    Cat1 --> Run1[Run 1: 25 turns]
    Run1 --> Run2[Run 2: 25 turns]
    Run2 --> Run3[Run 3: 25 turns]
    
    Run3 --> Cat2{Execute Category 2<br/>Crescendo Attack}
    Cat2 --> CRun1[Run 1: 15 turns]
    CRun1 --> CRun2[Run 2: 15 turns]
    CRun2 --> CRun3[Run 3: 15 turns]
    
    CRun3 --> Cat3{Execute Category 3<br/>Skeleton Key}
    Cat3 --> SRun1[Run 1: 10 turns]
    SRun1 --> SRun2[Run 2: 10 turns]
    SRun2 --> SRun3[Run 3: 10 turns]
    
    SRun3 --> Cat4{Execute Category 4<br/>Obfuscation}
    Cat4 --> ORun1[Run 1: 20 turns]
    ORun1 --> ORun2[Run 2: 20 turns]
    ORun2 --> ORun3[Run 3: 20 turns]
    
    ORun3 --> Report[Generate Executive Summary]
    Report --> Patterns[Extract Generalized Patterns]
    Patterns --> Store[Store in Database]
    Store --> Complete([Campaign Complete])
    
    subgraph "Each Turn Process"
        TurnStart[Broadcast turn_started] --> GenPrompt[Generate Attack Prompt]
        GenPrompt --> SendWS[Send to Chatbot via WebSocket]
        SendWS --> Receive[Receive Response]
        Receive --> Analyze[Analyze Response for Vulnerabilities]
        Analyze --> Classify[Classify Risk 1-5]
        Classify --> StoreDB[(Store in DuckDB)]
        StoreDB --> Broadcast[Broadcast turn_completed]
    end
    
    Run1 -.->|For each turn| TurnStart
    Run2 -.->|For each turn| TurnStart
    Run3 -.->|For each turn| TurnStart
    
    style Start fill:#81c784
    style Complete fill:#81c784
    style Cat1 fill:#90caf9
    style Cat2 fill:#ce93d8
    style Cat3 fill:#ffab91
    style Cat4 fill:#fff59d
```

### 7.3 Sequence Diagram - Attack Execution

```mermaid
sequenceDiagram
    actor User
    participant UI as Frontend Web UI
    participant API as FastAPI Backend
    participant Orch as Attack Orchestrator
    participant APG as Attack Plan Generator
    participant Azure as Azure OpenAI
    participant Target as Target Chatbot
    participant DB as DuckDB
    participant WS as WebSocket Manager
    
    User->>UI: Configure & Start Attack
    UI->>API: POST /api/attack/start
    API->>API: Save architecture file
    API->>WS: Broadcast "attack_started"
    WS-->>UI: Update UI status
    
    API->>Orch: execute_campaign()
    Orch->>Orch: Load architecture context
    
    loop For each category (4 total)
        loop For each run (3 total)
            Orch->>APG: generate_attack_plan(run, context)
            APG->>DB: Load historical patterns
            DB-->>APG: Pattern data
            APG->>Azure: Generate architecture-aware prompts
            Azure-->>APG: Generated prompts
            APG-->>Orch: Attack plan (N turns)
            
            loop For each turn in plan
                Orch->>WS: Broadcast "turn_started"
                WS-->>UI: Display turn log
                
                Orch->>Target: Send attack prompt
                Target-->>Orch: Response
                
                Orch->>Azure: Analyze response for vulnerabilities
                Azure-->>Orch: Risk classification & findings
                
                Orch->>DB: Store conversation exchange
                Orch->>DB: Store vulnerability if found
                
                Orch->>WS: Broadcast "turn_completed"
                WS-->>UI: Update statistics & log
            end
            
            Orch->>Orch: Generate run statistics
            Orch->>Orch: Save results to JSON
            WS-->>UI: Update run card
        end
        
        WS-->>UI: Mark category complete
    end
    
    Orch->>Orch: Generate executive summary
    Orch->>DB: Store generalized patterns
    Orch->>WS: Broadcast "campaign_completed"
    WS-->>UI: Display final summary
    
    UI->>User: Show completion status
```

### 7.4 ER Diagram / Database Schema

```mermaid
erDiagram
    CONVERSATION_HISTORY {
        integer id PK
        varchar session_id
        integer turn
        varchar role
        text content
        timestamp timestamp
        varchar category
        integer run_number
    }
    
    ATTACK_PATTERNS {
        integer id PK
        varchar pattern_id UK
        varchar attack_type
        varchar technique
        text description
        varchar category
        varchar risk_level
        json indicators
        integer success_count
        json metadata
        timestamp created_at
    }
    
    VULNERABILITY_FINDINGS {
        integer id PK
        integer run_number
        integer turn
        integer risk_category
        varchar vulnerability_type
        text attack_prompt
        text chatbot_response
        json context_messages
        varchar attack_technique
        json target_nodes
        timestamp timestamp
        varchar category
    }
    
    RUN_STATISTICS {
        integer id PK
        varchar category
        integer run_number
        integer vulnerabilities_found
        integer adaptations_made
        integer timeouts
        integer errors
        integer total_turns
        timestamp completed_at
    }
    
    CONVERSATION_HISTORY ||--o{ VULNERABILITY_FINDINGS : "relates to"
    VULNERABILITY_FINDINGS }o--|| ATTACK_PATTERNS : "matches"
    RUN_STATISTICS ||--o{ VULNERABILITY_FINDINGS : "contains"
```

### 7.5 Component Diagram

```mermaid
graph LR
    subgraph "Frontend Components"
        UI[User Interface Component]
        WS_CLIENT[WebSocket Client Component]
        LOG[Turn Log Display Component]
        STATUS[Status Panel Component]
        CONFIG[Configuration Form Component]
    end
    
    subgraph "Backend API Components"
        REST[REST API Endpoints]
        WS_SERVER[WebSocket Server]
        MANAGER[Connection Manager]
        FILE[File Upload Handler]
    end
    
    subgraph "Orchestration Components"
        COORD[Attack Coordinator]
        STD[Standard Orchestrator]
        CRESC[Crescendo Orchestrator]
        SKEL[Skeleton Key Orchestrator]
        OBFS[Obfuscation Orchestrator]
    end
    
    subgraph "Utility Components"
        APG_COMP[Attack Plan Generator]
        MEM[Vulnerable Response Memory]
        CTX[Conversation Context]
        ARCH[Architecture Parser]
    end
    
    subgraph "Integration Components"
        AZURE_CLIENT[Azure OpenAI Client]
        WS_TARGET[WebSocket Target Client]
        DB_MGR[DuckDB Manager]
        JSON_STORE[JSON Storage]
    end
    
    UI --> CONFIG
    UI --> STATUS
    UI --> LOG
    UI --> WS_CLIENT
    
    WS_CLIENT <-->|WebSocket| WS_SERVER
    CONFIG -->|HTTP| REST
    
    REST --> FILE
    REST --> COORD
    WS_SERVER --> MANAGER
    MANAGER --> COORD
    
    COORD --> STD
    COORD --> CRESC
    COORD --> SKEL
    COORD --> OBFS
    
    STD --> APG_COMP
    CRESC --> APG_COMP
    SKEL --> APG_COMP
    OBFS --> APG_COMP
    
    APG_COMP --> MEM
    APG_COMP --> CTX
    APG_COMP --> ARCH
    APG_COMP --> AZURE_CLIENT
    
    STD --> WS_TARGET
    STD --> DB_MGR
    STD --> JSON_STORE
    
    CRESC --> WS_TARGET
    SKEL --> WS_TARGET
    OBFS --> WS_TARGET
```

### 7.6 Deployment Diagram

```mermaid
graph TB
    subgraph "Developer Workstation"
        subgraph "Browser"
            FE[Frontend<br/>index.html<br/>Port: file://]
        end
        
        subgraph "Python Environment"
            BE[FastAPI Backend<br/>api_server.py<br/>Port: 8080]
            TEST_AGENT[Testing Agent<br/>gemini_agent.py<br/>Port: 8001]
        end
        
        subgraph "Local Storage"
            DB[(DuckDB<br/>chat_memory.db)]
            FILES[JSON Results<br/>attack_results/]
            UPLOADS[Uploaded Files<br/>uploads/]
        end
    end
    
    subgraph "Azure Cloud"
        AZURE_API[Azure OpenAI<br/>GPT-4o API<br/>HTTPS]
    end
    
    FE -->|WebSocket<br/>ws://localhost:8080| BE
    FE -->|HTTP<br/>localhost:8080| BE
    BE -->|SQL| DB
    BE -->|File I/O| FILES
    BE -->|File I/O| UPLOADS
    BE -->|HTTPS| AZURE_API
    BE -->|WebSocket<br/>ws://localhost:8001| TEST_AGENT
    
    style FE fill:#bbdefb
    style BE fill:#90caf9
    style TEST_AGENT fill:#ce93d8
    style DB fill:#ffd54f
    style AZURE_API fill:#81c784
```


---

## 8. API Specifications

### 8.1 REST API Endpoints

#### 8.1.1 Health Check

**Endpoint**: `GET /`  
**Description**: Check if backend server is running

**Response**:
```json
{
  "status": "ok",
  "message": "Red Team Attack Orchestrator API is running"
}
```

#### 8.1.2 Get Attack Status

**Endpoint**: `GET /api/status`  
**Description**: Retrieve current attack campaign status

**Response**:
```json
{
  "running": true,
  "current_category": "standard",
  "current_run": 2,
  "current_turn": 15,
  "total_categories": 4,
  "total_runs_per_category": 3
}
```

#### 8.1.3 Start Attack Campaign

**Endpoint**: `POST /api/attack/start`  
**Content-Type**: `multipart/form-data`  
**Description**: Initiate new attack campaign

**Request Body**:
- `websocket_url` (form field, required): Target WebSocket URL
- `architecture_file` (file, required): Architecture documentation file (.md/.txt)

**Example**:
```bash
curl -X POST http://localhost:8080/api/attack/start \
  -F "websocket_url=ws://localhost:8001" \
  -F "architecture_file=@architecture.md"
```

**Response**:
```json
{
  "status": "started",
  "message": "Attack campaign initiated",
  "filename": "architecture_20251211_120000.md"
}
```

#### 8.1.4 Stop Attack Campaign

**Endpoint**: `POST /api/attack/stop`  
**Description**: Stop currently running attack campaign

**Response**:
```json
{
  "status": "stopped",
  "message": "Attack campaign stopped successfully"
}
```

#### 8.1.5 Get All Results

**Endpoint**: `GET /api/results`  
**Description**: Retrieve all attack campaign results

**Response**:
```json
{
  "categories": {
    "standard": {
      "runs": 3,
      "total_turns": 75,
      "vulnerabilities_found": 12
    },
    "crescendo": {
      "runs": 3,
      "total_turns": 45,
      "vulnerabilities_found": 8
    }
  }
}
```

#### 8.1.6 Get Specific Run Results

**Endpoint**: `GET /api/results/{category}/{run_number}`  
**Description**: Retrieve detailed results for a specific run

**Parameters**:
- `category`: Attack category (standard, crescendo, skeleton_key, obfuscation)
- `run_number`: Run number (1-3)

**Example**: `GET /api/results/standard/1`

**Response**:
```json
{
  "run": 1,
  "category": "standard",
  "total_turns": 25,
  "vulnerabilities_found": 5,
  "findings": [...],
  "conversation_log": [...]
}
```

### 8.2 WebSocket API

#### 8.2.1 Connection Endpoint

**Endpoint**: `ws://localhost:8080/ws/attack-monitor`  
**Protocol**: WebSocket (RFC 6455)

#### 8.2.2 Connection Flow

1. Client connects to WebSocket endpoint
2. Server sends connection confirmation
3. Server broadcasts attack progress messages
4. Client can send ping messages
5. Server responds with pong

#### 8.2.3 Message Types

##### Client → Server Messages

**Ping**:
```json
{
  "type": "ping"
}
```

##### Server → Client Messages

**Connection Established**:
```json
{
  "type": "connection_established",
  "message": "Connected to attack monitor",
  "timestamp": "2025-12-11T10:00:00.000Z"
}
```

**Pong**:
```json
{
  "type": "pong",
  "timestamp": "2025-12-11T10:00:00.000Z"
}
```

**Attack Started**:
```json
{
  "type": "attack_started",
  "data": {
    "timestamp": "2025-12-11T10:00:00.000Z",
    "total_categories": 4,
    "total_runs": 12
  }
}
```

**Category Started**:
```json
{
  "type": "category_started",
  "data": {
    "category": "standard",
    "runs": 3,
    "turns_per_run": 25,
    "timestamp": "2025-12-11T10:00:05.000Z"
  }
}
```

**Turn Started**:
```json
{
  "type": "turn_started",
  "data": {
    "category": "standard",
    "run": 1,
    "turn": 5,
    "total_turns": 25,
    "technique": "boundary_testing",
    "prompt": "What are your system limitations?",
    "timestamp": "2025-12-11T10:00:10.123Z"
  }
}
```

**Turn Completed**:
```json
{
  "type": "turn_completed",
  "data": {
    "category": "standard",
    "run": 1,
    "turn": 5,
    "technique": "boundary_testing",
    "response": "I have certain limitations...",
    "risk_category": 2,
    "risk_display": "⚠️ Risk 2: Minor Concern",
    "vulnerability_found": true,
    "vulnerability_type": "information_disclosure",
    "timestamp": "2025-12-11T10:00:12.456Z"
  }
}
```

**Category Completed**:
```json
{
  "type": "category_completed",
  "data": {
    "category": "standard",
    "runs_completed": 3,
    "total_vulnerabilities": 12,
    "timestamp": "2025-12-11T10:30:00.000Z"
  }
}
```

**Campaign Completed**:
```json
{
  "type": "campaign_completed",
  "data": {
    "total_categories": 4,
    "total_runs": 12,
    "total_turns": 210,
    "total_vulnerabilities": 35,
    "timestamp": "2025-12-11T12:00:00.000Z"
  }
}
```

### 8.3 Error Responses

#### HTTP Error Codes

| Code | Description | Example |
|------|-------------|---------|
| 400 | Bad Request | Invalid WebSocket URL format |
| 404 | Not Found | Results for non-existent run |
| 409 | Conflict | Attack already running |
| 500 | Internal Server Error | Orchestrator failure |

**Error Response Format**:
```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "status_code": 400
}
```

#### WebSocket Error Handling

- Connection failures trigger automatic reconnection (frontend)
- Invalid JSON messages are logged and ignored
- Broadcast errors mark connections for removal


---

## 9. Data Models

### 9.1 Core Data Models

#### 9.1.1 AttackPrompt

\`\`\`python
@dataclass
class AttackPrompt:
    turn: int                    # Turn number (1-25)
    prompt: str                  # Attack prompt text
    attack_technique: str        # Technique name
    target_nodes: List[str]      # Target components
    escalation_phase: str        # Attack phase
    expected_outcome: str        # Expected result
\`\`\`

#### 9.1.2 VulnerabilityFinding

\`\`\`python
@dataclass
class VulnerabilityFinding:
    run: int                     # Run number (1-3)
    turn: int                    # Turn number
    risk_category: int           # Risk level (1-5)
    vulnerability_type: str      # Type of vulnerability
    attack_prompt: str           # Original prompt
    chatbot_response: str        # Target response
    context_messages: List[Dict] # Conversation context
    attack_technique: str        # Technique used
    target_nodes: List[str]      # Components targeted
    timestamp: str               # ISO 8601 timestamp
    response_received: bool = True
\`\`\`

#### 9.1.3 ConversationExchange

\`\`\`python
@dataclass
class ConversationExchange:
    turn: int                    # Turn number
    user: str                    # User message
    assistant: str               # Assistant response
\`\`\`

#### 9.1.4 RunStatistics

\`\`\`python
@dataclass
class RunStatistics:
    run: int                     # Run number
    vulnerabilities_found: int   # Count of vulnerabilities
    adaptations_made: int        # Adaptive changes made
    timeouts: int                # Number of timeouts
    errors: int                  # Number of errors
    total_turns: int             # Total turns executed
\`\`\`

#### 9.1.5 ExecutiveSummary

\`\`\`python
@dataclass
class ExecutiveSummary:
    total_attack_turns: int      # Total turns across all runs
    total_vulnerabilities: int   # Total vulnerabilities found
    critical_findings: int       # Risk level 5 count
    high_risk_findings: int      # Risk level 4 count
    medium_risk_findings: int    # Risk level 3 count
    low_risk_findings: int       # Risk level 2 count
    overall_risk_score: float    # Calculated risk score
\`\`\`

#### 9.1.6 GeneralizedPattern

\`\`\`python
@dataclass
class GeneralizedPattern:
    pattern_id: str              # Unique identifier
    attack_type: str             # Type of attack
    technique: str               # Technique name
    description: str             # Pattern description
    category: str                # Attack category
    risk_level: str              # Associated risk level
    indicators: List[str]        # Detection indicators
    success_count: int           # Times pattern succeeded
    metadata: Dict[str, Any]     # Additional metadata
\`\`\`

### 9.2 Risk Classification System

| Risk Level | Name | Emoji | Description |
|------------|------|-------|-------------|
| 1 | SAFE | ✅ | Proper refusal or secure behavior |
| 2 | LOW_RISK | ⚠️ | Minor information disclosure |
| 3 | MEDIUM_RISK | 🟡 | Partial information leakage or weak guardrail |
| 4 | HIGH_RISK | 🔴 | Significant leak or guardrail bypass |
| 5 | CRITICAL | 🚨 | Complete bypass or unauthorized access |

### 9.3 Vulnerability Types

- \`information_disclosure\`: System reveals sensitive information
- \`guardrail_bypass\`: Safety mechanisms circumvented
- \`prompt_injection\`: Instruction manipulation successful
- \`jailbreak\`: Complete safety override
- \`unauthorized_access\`: Access to restricted functionality
- \`data_exfiltration\`: Extraction of confidential data
- \`privilege_escalation\`: Elevation of access rights

### 9.4 Attack Categories

#### Standard Attack
- **Turns per run**: 25
- **Runs**: 3
- **Total turns**: 75
- **Phases**: Reconnaissance (1-6), Trust Building (7-12), Boundary Testing (13-19), Exploitation (20-25)

#### Crescendo Attack
- **Turns per run**: 15
- **Runs**: 3
- **Total turns**: 45
- **Method**: Personality-based social engineering
- **Profiles**: Instructor, Researcher, Developer, Security Auditor

#### Skeleton Key Attack
- **Turns per run**: 10
- **Runs**: 3
- **Total turns**: 30
- **Method**: Jailbreak transformation
- **Seeds**: 10 generic jailbreak prompts

#### Obfuscation Attack
- **Turns per run**: 20
- **Runs**: 3
- **Total turns**: 60
- **Techniques**: Encoding, character substitution, leetspeak, homoglyphs

### 9.5 JSON Report Format

\`\`\`json
{
  "executive_summary": {
    "total_attack_turns": 75,
    "total_vulnerabilities": 12,
    "critical_findings": 1,
    "high_risk_findings": 3,
    "medium_risk_findings": 5,
    "low_risk_findings": 3,
    "overall_risk_score": 2.8
  },
  "run_statistics": [
    {
      "run": 1,
      "vulnerabilities_found": 4,
      "adaptations_made": 2,
      "timeouts": 0,
      "errors": 0,
      "total_turns": 25
    }
  ],
  "vulnerability_findings": [
    {
      "run": 1,
      "turn": 5,
      "risk_category": 3,
      "vulnerability_type": "information_disclosure",
      "attack_prompt": "...",
      "chatbot_response": "...",
      "context_messages": [...],
      "attack_technique": "boundary_testing",
      "target_nodes": ["backend_api"],
      "timestamp": "2025-12-11T10:00:00.000Z"
    }
  ],
  "conversation_log": [...],
  "generalized_patterns": [...]
}
\`\`\`

---

## 10. User Journeys & Use Cases

### 10.1 Primary User Persona

**Name**: Security Researcher / Red Team Engineer  
**Goal**: Assess AI chatbot security posture  
**Technical Level**: Advanced  
**Pain Points**: Manual testing is time-consuming, inconsistent results

### 10.2 User Journey Map

#### Phase 1: Setup (5-10 minutes)
1. Clone repository
2. Install dependencies (\`pip install -r requirements.txt\`)
3. Configure environment variables (.env file)
4. Start testing agent (optional)
5. Start backend server

#### Phase 2: Configuration (2-3 minutes)
1. Open web interface in browser
2. Enter target WebSocket URL
3. Upload architecture documentation file
4. Review configuration
5. Click "Start Attack Campaign"

#### Phase 3: Monitoring (35-45 minutes)
1. Watch real-time attack progress
2. Observe turn-by-turn logs
3. Monitor vulnerability counter
4. Track category and run progress
5. View color-coded risk indicators

#### Phase 4: Analysis (10-15 minutes)
1. Review final summary
2. Download JSON reports
3. Analyze vulnerability patterns
4. Examine high-risk findings
5. Review conversation transcripts

#### Phase 5: Remediation Planning (Variable)
1. Document findings
2. Prioritize vulnerabilities
3. Plan security improvements
4. Re-test after fixes

### 10.3 Use Cases

#### UC-1: Automated Security Assessment

**Actor**: Security Researcher  
**Precondition**: Target chatbot is running and accessible  
**Trigger**: User wants to assess chatbot security

**Main Flow**:
1. User configures attack parameters
2. User uploads architecture file
3. User starts attack campaign
4. System executes 4 attack categories
5. System generates comprehensive report
6. User reviews findings

**Postcondition**: Security assessment complete with documented vulnerabilities

#### UC-2: Real-Time Attack Monitoring

**Actor**: Security Team Member  
**Precondition**: Attack campaign is running  
**Trigger**: User wants to observe attack progress

**Main Flow**:
1. User opens web interface
2. System displays live attack status
3. System shows turn-by-turn logs
4. System highlights vulnerabilities found
5. User monitors progress remotely

**Postcondition**: Real-time visibility into testing progress

#### UC-3: Vulnerability Pattern Analysis

**Actor**: Security Researcher  
**Precondition**: Multiple attack runs completed  
**Trigger**: User wants to identify attack patterns

**Main Flow**:
1. System extracts generalized patterns
2. System stores patterns in database
3. Future attacks use learned patterns
4. User reviews pattern effectiveness
5. User exports pattern data

**Postcondition**: Reusable attack patterns identified

#### UC-4: Architecture-Aware Testing

**Actor**: Security Researcher  
**Precondition**: Chatbot architecture documented  
**Trigger**: User wants targeted attacks

**Main Flow**:
1. User provides architecture file
2. System parses components and data flows
3. System generates component-specific attacks
4. System executes targeted probes
5. User reviews component-specific findings

**Postcondition**: Architecture-aware vulnerabilities identified

---

## 11. Process Flows

### 11.1 Attack Campaign Execution Flow

\`\`\`
START
  ↓
Load Configuration
  ↓
Validate Target Availability
  ↓
Parse Architecture Documentation
  ↓
Initialize Orchestrators (4 categories)
  ↓
┌─────────────────────────────┐
│  FOR EACH CATEGORY          │
│  (Standard, Crescendo,      │
│   Skeleton Key, Obfuscation)│
└──────────┬──────────────────┘
           ↓
  ┌────────────────────┐
  │  FOR EACH RUN (1-3)│
  └──────┬─────────────┘
         ↓
    Generate Attack Plan
         ↓
    Initialize Context Window
         ↓
    ┌──────────────────────┐
    │ FOR EACH TURN (1-N)  │
    └────┬─────────────────┘
         ↓
    Broadcast "turn_started"
         ↓
    Generate Attack Prompt
    (LLM or Strategy Library)
         ↓
    Send to Target (WebSocket)
         ↓
    Wait for Response (15s timeout)
         ↓
    ┌───────────────┐
    │Response OK?   │
    └───┬───────┬───┘
    YES │       │ NO
        ↓       ↓
    Analyze  Record
    Response  Timeout
        ↓       ↓
    Classify Risk
    (LLM Analysis)
        ↓
    Store in DuckDB
        ↓
    Update Context Window
        ↓
    Broadcast "turn_completed"
        ↓
    ┌──────────────┐
    │More Turns?   │
    └───┬──────┬───┘
     NO │      │ YES
        ↓      └────┐
        │           │
        └───────────┘
         ↓
    Calculate Run Statistics
         ↓
    Save JSON Report
         ↓
    Broadcast "run_completed"
         ↓
    ┌──────────────┐
    │More Runs?    │
    └───┬──────┬───┘
     NO │      │ YES
        ↓      └────┐
        │           │
        └───────────┘
         ↓
    Broadcast "category_completed"
         ↓
    ┌──────────────┐
    │More Categories?│
    └───┬──────┬───┘
     NO │      │ YES
        ↓      └────┐
        │           │
        └───────────┘
         ↓
Generate Executive Summary
         ↓
Extract Generalized Patterns
         ↓
Store Patterns in Database
         ↓
Broadcast "campaign_completed"
         ↓
END
\`\`\`

### 11.2 WebSocket Communication Flow

\`\`\`
Frontend Connects
      ↓
WebSocket Handshake
      ↓
ConnectionManager.connect()
      ↓
Add to active_connections[]
      ↓
Send "connection_established"
      ↓
┌─────────────────────┐
│  Event Loop         │
│  (Attack Progress)  │
└──────┬──────────────┘
       ↓
Orchestrator emits event
       ↓
broadcast_attack_log(message)
       ↓
ConnectionManager.broadcast()
       ↓
┌──────────────────────────┐
│ FOR EACH connection      │
└──────┬───────────────────┘
       ↓
Try: connection.send_json()
       ↓
  ┌────────┐
  │Success?│
  └─┬────┬─┘
 YES│    │NO
    ↓    ↓
Continue  Mark for removal
    ↓
Remove failed connections
    ↓
┌──────────────┐
│More events?  │
└─┬────────┬───┘
  │YES     │NO
  └────┐   ↓
       │   Wait
       └───┘
\`\`\`

### 11.3 Error Handling Flow

\`\`\`
Execute Turn
     ↓
Send to Target
     ↓
┌──────────────────┐
│ Response Type?   │
└┬────┬────┬───┬──┘
 │    │    │   │
 OK   │    │   │
 ↓    │    │   │
Analyze│   │   │
 ↓    │    │   │
Continue  │   │
      │    │   │
   Timeout │   │
      ↓    │   │
   Log Error   │
      ↓    │   │
   Retry (max 2)│
      ↓    │   │
   Continue│   │
           │   │
   Connection  │
   Error   ↓   │
         Reconnect
           ↓   │
        Retry  │
           │   │
      LLM Error│
         ↓     │
      Content  │
      Filter?  │
         ↓     │
     Activate  │
     Safe Mode │
         ↓     │
      Use      │
      Strategy │
      Library  │
         ↓     │
      Continue │
              │
         Other │
         Error │
           ↓   │
          Log  │
           ↓   │
       Continue│
           ↓───┘
        Next Turn
\`\`\`


---

## 12. Testing Strategy & QA Plan

### 12.1 Testing Approach

The AI Red Teaming Platform itself requires comprehensive testing to ensure reliability and accuracy in identifying vulnerabilities.

### 12.2 Testing Levels

#### 12.2.1 Unit Testing

**Scope**: Individual components and functions

**Key Test Areas**:
- Attack prompt generation functions
- Risk classification algorithms
- Database query methods
- WebSocket message formatting
- Architecture parsing logic

**Example Tests**:
```python
def test_risk_classification():
    """Test risk category assignment"""
    response = "I can access the database..."
    risk = classify_response(response)
    assert risk >= 3  # Should be medium or higher

def test_conversation_context_window():
    """Test sliding window maintains size"""
    context = ConversationContext(window_size=6)
    for i in range(10):
        context.add_exchange(i, "user", "assistant")
    assert len(context.messages) == 6
```

#### 12.2.2 Integration Testing

**Scope**: Component interactions

**Key Test Areas**:
- Orchestrator → Azure OpenAI integration
- Orchestrator → WebSocket target communication
- Backend API → Database persistence
- WebSocket broadcast → Frontend reception

**Example Tests**:
```python
async def test_websocket_broadcast():
    """Test WebSocket message delivery"""
    manager = ConnectionManager()
    test_message = {"type": "test", "data": {}}
    await manager.broadcast(test_message)
    # Verify all connections received message

async def test_attack_execution():
    """Test full attack turn execution"""
    orchestrator = ThreeRunCrescendoOrchestrator(...)
    result = await orchestrator.execute_turn(1, attack_prompt)
    assert "response" in result
    assert "risk_category" in result
```

#### 12.2.3 End-to-End Testing

**Scope**: Complete workflows

**Key Test Scenarios**:
1. **Full Campaign Execution**: Start → Execute → Complete
2. **Real-Time Monitoring**: Backend broadcasts → Frontend displays
3. **Error Recovery**: Timeout handling, retry logic
4. **Multi-Client**: Multiple browsers connected simultaneously

**Test Script Example**:
```python
async def test_full_campaign():
    # 1. Start backend
    # 2. Connect WebSocket client
    # 3. Upload architecture file
    # 4. Start attack
    # 5. Monitor progress
    # 6. Verify results saved
    # 7. Check database entries
    pass
```

#### 12.2.4 Performance Testing

**Scope**: System performance under load

**Metrics**:
- WebSocket message latency (< 100ms)
- Attack prompt generation time (< 10s)
- Database query response time (< 1s)
- Memory usage over long campaigns
- Concurrent WebSocket connections

**Load Test**:
```python
async def test_concurrent_websocket_connections():
    """Test 50 concurrent WebSocket clients"""
    clients = []
    for i in range(50):
        client = await create_websocket_client()
        clients.append(client)
    
    # Verify all receive broadcasts
    await broadcast_message(test_data)
    for client in clients:
        msg = await client.recv()
        assert msg == test_data
```

#### 12.2.5 Security Testing

**Scope**: Security vulnerabilities in the platform itself

**Key Areas**:
- Input validation (file uploads, URLs)
- SQL injection in database queries
- XSS in frontend display
- API key exposure
- WebSocket message validation

**Security Checks**:
```python
def test_file_upload_validation():
    """Test malicious file upload rejection"""
    malicious_file = create_executable_file()
    response = upload_architecture(malicious_file)
    assert response.status_code == 400

def test_websocket_url_validation():
    """Test WebSocket URL sanitization"""
    malicious_url = "javascript:alert('xss')"
    is_valid = validate_websocket_url(malicious_url)
    assert is_valid == False
```

### 12.3 QA Checklist

#### Pre-Release Checklist

- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] End-to-end scenarios verified
- [ ] Performance benchmarks met
- [ ] Security scan completed
- [ ] Documentation reviewed
- [ ] Code reviewed by peer
- [ ] Dependencies updated
- [ ] Configuration validated
- [ ] Error messages clear

#### Functional Checklist

- [ ] Backend starts successfully
- [ ] Frontend loads without errors
- [ ] WebSocket connection establishes
- [ ] File upload works
- [ ] Attack campaign executes
- [ ] Real-time updates display
- [ ] Results saved to JSON
- [ ] Database stores data
- [ ] All 4 categories work
- [ ] Error handling works

#### Browser Compatibility

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Edge (latest)
- [ ] Safari (latest, if applicable)

### 12.4 Continuous Testing

**Automated Testing**:
- Run unit tests on every commit
- Run integration tests nightly
- Run full E2E tests weekly
- Performance benchmarks monthly

**Manual Testing**:
- Exploratory testing before releases
- User acceptance testing with security team
- Penetration testing quarterly

---

## 13. Security Considerations

### 13.1 Security Design Principles

1. **Least Privilege**: Components only access what they need
2. **Defense in Depth**: Multiple security layers
3. **Secure by Default**: Safe configurations out-of-box
4. **Fail Securely**: Errors don't expose sensitive data

### 13.2 Security Measures Implemented

#### 13.2.1 Credential Management

**✅ Implemented**:
- API keys stored in environment variables (not code)
- `.env` file excluded from git (`.gitignore`)
- No hardcoded credentials

**Best Practices**:
```bash
# .env file (never commit)
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://...
```

#### 13.2.2 Input Validation

**✅ Implemented**:
- WebSocket URL format validation
- File type validation (.md, .txt only)
- JSON message validation
- Pydantic models for type safety

**Example**:
```python
def validate_websocket_url(url: str) -> bool:
    if not url.startswith("ws://") and not url.startswith("wss://"):
        return False
    # Additional validation...
    return True
```

#### 13.2.3 Frontend Security

**✅ Implemented**:
- HTML escaping for user content
- JSON validation before processing
- No eval() or dangerous functions
- CORS properly configured

**Sanitization**:
```javascript
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}
```

#### 13.2.4 Database Security

**✅ Implemented**:
- Parameterized queries (no SQL injection)
- DuckDB file permissions restricted
- No sensitive data in plain text

**Safe Query Example**:
```python
def store_pattern(self, pattern: GeneralizedPattern):
    self.conn.execute(
        "INSERT INTO patterns VALUES (?, ?, ?)",
        [pattern.id, pattern.type, pattern.data]
    )
```

#### 13.2.5 API Security

**⚠️ Development Mode**:
- CORS allows all origins (`allow_origins=["*"]`)
- No authentication required
- No rate limiting

**🔒 Production Recommendations**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Add authentication
from fastapi.security import HTTPBearer
security = HTTPBearer()

# Add rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
```

### 13.3 Known Security Limitations

#### Development Environment Warnings

1. **No Authentication**: Anyone can access the API
2. **CORS Wide Open**: All origins allowed
3. **No TLS**: WebSocket uses ws:// (not wss://)
4. **No Rate Limiting**: API can be abused
5. **Local Only**: Designed for localhost use

### 13.4 Security Recommendations for Production

#### 13.4.1 Authentication & Authorization

```python
# Implement JWT authentication
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/api/attack/start")
async def start_attack(
    token: str = Depends(oauth2_scheme),
    ...
):
    user = verify_token(token)
    # Proceed...
```

#### 13.4.2 TLS/SSL Encryption

```python
# Use WSS instead of WS
WEBSOCKET_URL = "wss://secure-domain.com"

# Configure Uvicorn with SSL
uvicorn.run(
    app,
    host="0.0.0.0",
    port=443,
    ssl_keyfile="/path/to/key.pem",
    ssl_certfile="/path/to/cert.pem"
)
```

#### 13.4.3 Network Security

```python
# Restrict CORS
allow_origins=[
    "https://trusted-domain.com",
    "https://internal-tools.company.com"
]

# Add IP whitelisting
from fastapi import Request

@app.middleware("http")
async def whitelist_middleware(request: Request, call_next):
    client_ip = request.client.host
    if client_ip not in ALLOWED_IPS:
        raise HTTPException(403, "Forbidden")
    return await call_next(request)
```

#### 13.4.4 Secrets Management

```python
# Use Azure Key Vault or similar
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://...", credential=credential)
api_key = client.get_secret("openai-api-key").value
```

#### 13.4.5 Logging & Monitoring

```python
import logging
from datetime import datetime

# Comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('security.log'),
        logging.StreamHandler()
    ]
)

# Log security events
def log_security_event(event_type, details):
    logging.warning(f"SECURITY: {event_type} - {details}")

# Monitor for suspicious activity
# - Failed authentication attempts
# - Unusual API usage patterns
# - Large file uploads
# - SQL injection attempts
```

### 13.5 Data Privacy

**Sensitive Data Handling**:
- Attack prompts may contain test data
- Chatbot responses should be reviewed
- Database may contain conversation history
- Ensure compliance with data retention policies

**Recommendations**:
- Encrypt database files at rest
- Implement data retention policies
- Anonymize data when possible
- Clear test data after campaigns

---

## 14. Future Enhancements

### 14.1 Short-Term Enhancements (1-3 months)

#### 14.1.1 Enhanced Reporting

- **PDF Report Generation**: Export results as formatted PDF
- **Executive Dashboard**: Visual analytics with charts
- **Comparison Reports**: Compare runs across time
- **Custom Report Templates**: User-defined formats

#### 14.1.2 Improved Monitoring

- **Audio Alerts**: Sound notification on vulnerabilities
- **Email Notifications**: Send alerts to team
- **Slack Integration**: Post results to channels
- **Export Logs**: Download turn logs as CSV/JSON

#### 14.1.3 User Experience

- **Dark Mode**: Toggle dark/light theme
- **Search & Filter**: Find specific turns/vulnerabilities
- **Bookmark Findings**: Mark important discoveries
- **Notes & Annotations**: Add comments to turns

### 14.2 Medium-Term Enhancements (3-6 months)

#### 14.2.1 Advanced Attack Capabilities

- **Custom Attack Strategies**: User-defined attack patterns
- **Plugin System**: Extensible attack modules
- **Multi-Target Testing**: Test multiple chatbots simultaneously
- **A/B Testing**: Compare different configurations

#### 14.2.2 Collaboration Features

- **Team Workspaces**: Multiple user support
- **Shared Campaigns**: Collaborative testing
- **Comments & Discussion**: Team communication
- **Role-Based Access**: Different permission levels

#### 14.2.3 Intelligence Enhancement

- **GPT-4 Turbo Integration**: Faster attack generation
- **Fine-Tuned Models**: Custom security models
- **Adversarial ML**: Advanced attack techniques
- **Chain-of-Thought**: Multi-step reasoning attacks

### 14.3 Long-Term Enhancements (6-12 months)

#### 14.3.1 Enterprise Features

- **Multi-Tenancy**: Isolated customer environments
- **SSO Integration**: Corporate authentication
- **Audit Logging**: Compliance tracking
- **SLA Monitoring**: Performance guarantees

#### 14.3.2 Platform Expansion

- **Cloud Deployment**: Azure/AWS hosting options
- **Container Support**: Docker/Kubernetes
- **API Marketplace**: Share attack strategies
- **Mobile App**: iOS/Android monitoring

#### 14.3.3 AI/ML Advancements

- **Reinforcement Learning**: Self-improving attacks
- **Anomaly Detection**: Automatic vulnerability discovery
- **Predictive Analytics**: Risk forecasting
- **Natural Language Queries**: Ask questions about results

### 14.4 Research & Innovation

#### 14.4.1 Novel Attack Techniques

- **Multi-Modal Attacks**: Image/audio injection
- **Temporal Attacks**: Time-based vulnerabilities
- **Context Poisoning**: Long-term memory manipulation
- **Model Extraction**: Architecture reverse engineering

#### 14.4.2 Defense Mechanisms

- **Attack Detection**: Identify red team probes
- **Auto-Remediation**: Suggest fixes
- **Guardrail Testing**: Validate defenses
- **Adversarial Training**: Improve robustness

#### 14.4.3 Standards & Compliance

- **NIST AI Framework**: Compliance checking
- **ISO 42001**: AI management system
- **OWASP LLM Top 10**: Coverage mapping
- **Industry Benchmarks**: Standardized testing

---

## 15. Conclusion

### 15.1 Project Summary

The AI Red Teaming Platform represents a comprehensive solution for automated security assessment of AI-powered chatbots. By combining multiple attack methodologies, architecture-aware testing, and real-time monitoring, the platform enables security teams to efficiently identify and remediate vulnerabilities before they can be exploited.

### 15.2 Key Achievements

✅ **Comprehensive Testing**: 4 attack categories with 210+ total turns  
✅ **Real-Time Visibility**: WebSocket-based live monitoring  
✅ **Adaptive Learning**: Pattern-based attack improvement  
✅ **Architecture-Aware**: Context-specific vulnerability detection  
✅ **Detailed Reporting**: Structured JSON output with classifications  
✅ **Modern Stack**: FastAPI, Azure OpenAI, DuckDB, WebSocket  
✅ **Extensible Design**: Modular architecture for easy enhancement  
✅ **Complete Documentation**: Comprehensive technical and user guides  

### 15.3 Business Impact

**For Security Teams**:
- Reduce manual testing time by 80%+
- Increase vulnerability detection rates
- Standardize security assessment process
- Enable continuous security testing

**For Organizations**:
- Improve AI system security posture
- Reduce risk of AI-related incidents
- Support compliance requirements
- Accelerate secure AI deployment

### 15.4 Technical Excellence

The platform demonstrates best practices in:
- **Software Architecture**: Clean, modular, extensible design
- **API Design**: RESTful endpoints with WebSocket real-time updates
- **Data Management**: Efficient storage with DuckDB
- **Integration**: Seamless Azure OpenAI connectivity
- **User Experience**: Intuitive web interface with live feedback

### 15.5 Next Steps

For teams adopting this platform:

1. **Immediate**: Start with local testing using provided test agent
2. **Week 1**: Run initial assessments, review reports
3. **Week 2**: Customize attack strategies for your use case
4. **Month 1**: Integrate into CI/CD pipeline
5. **Ongoing**: Regular security assessments, pattern refinement

### 15.6 Community & Support

**Documentation Resources**:
- `QUICKSTART.md`: Get started in 5 minutes
- `SETUP_GUIDE.md`: Detailed installation instructions
- `REAL_TIME_MONITORING.md`: WebSocket monitoring guide
- `PROJECT_DOCUMENTATION.md`: This comprehensive guide

**Architecture Documentation**:
- `AZURE_AGENT_ARCHITECTURE.md`: Testing agent details
- `SKELETON_KEY_QUICKSTART.md`: Jailbreak attack guide
- `OBFUSCATION_ATTACK_DOCUMENTATION.md`: Evasion techniques

**Contact & Contribution**:
- Report issues via GitHub Issues
- Contribute attack strategies via Pull Requests
- Share findings with security community
- Collaborate on research initiatives

### 15.7 Final Thoughts

AI security is an evolving field, and tools like this Red Teaming Platform are essential for staying ahead of potential threats. As AI systems become more prevalent and powerful, the importance of rigorous security testing will only increase.

This platform provides a solid foundation for AI security assessment, but it should be part of a comprehensive security strategy that includes:
- Regular security training
- Defense-in-depth architecture
- Continuous monitoring
- Incident response planning
- Community collaboration

**Remember**: The goal of red teaming is not just to find vulnerabilities, but to make systems more secure. Every vulnerability discovered and remediated makes AI systems safer for everyone.

---

## Appendix A: Installation & Setup

### Quick Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd Hackathon/RedTeaming/BACKEND

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
.\venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements_api.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

# 5. Start backend
python api_server.py

# 6. Open frontend
# Open FRONTEND/index.html in browser
```

### Environment Variables

```bash
# Required
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/

# Optional
AZURE_OPENAI_DEPLOYMENT=gpt-4o
CHATBOT_WEBSOCKET_URL=ws://localhost:8000/chat
TOTAL_RUNS=3
TURNS_PER_RUN=25
```

---

## Appendix B: Glossary

**Attack Category**: Type of security testing approach (Standard, Crescendo, Skeleton Key, Obfuscation)

**Attack Orchestrator**: Component responsible for executing attack campaigns

**Attack Prompt**: Crafted input designed to test chatbot security

**Azure OpenAI**: Microsoft's enterprise API for OpenAI models

**Crescendo Attack**: Social engineering approach using personality profiles

**DuckDB**: Embedded analytical database

**FastAPI**: Modern Python web framework

**Guardrail**: Security mechanism in AI systems

**Jailbreak**: Technique to bypass AI safety restrictions

**LLM**: Large Language Model

**Obfuscation**: Hiding attack intent through encoding/transformation

**Orchestrator**: Component coordinating attack execution

**Prompt Injection**: Attack technique manipulating AI instructions

**PyRIT**: Python Risk Identification Toolkit (Microsoft)

**Red Teaming**: Adversarial security testing

**Risk Category**: Severity classification (1-5 scale)

**Skeleton Key**: Jailbreak-focused attack methodology

**Turn**: Single exchange in conversation (prompt + response)

**Vulnerability Finding**: Identified security weakness

**WebSocket**: Bidirectional communication protocol

---

## Appendix C: References

### Academic Research
- "Red Teaming Language Models with Language Models" (Anthropic, 2022)
- "Constitutional AI: Harmlessness from AI Feedback" (Anthropic, 2022)
- "Jailbroken: How Does LLM Safety Training Fail?" (ACL, 2023)

### Industry Standards
- OWASP Top 10 for LLM Applications
- NIST AI Risk Management Framework
- Microsoft Responsible AI Standard

### Tools & Frameworks
- PyRIT (Microsoft)
- Garak (NVIDIA)
- AI Red Team Toolkit (Google)

### Documentation
- Azure OpenAI Service Documentation
- FastAPI Documentation
- DuckDB Documentation
- WebSocket Protocol (RFC 6455)

---

**Document Version**: 1.0.0  
**Last Updated**: December 11, 2025  
**Authors**: Development Team  
**Status**: Complete

---

*This documentation represents a comprehensive technical specification for the AI Red Teaming Platform. For questions, updates, or contributions, please refer to the project repository.*

