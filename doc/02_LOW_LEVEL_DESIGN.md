# Low-Level Design (LLD)
## AI Red Teaming Attack Orchestration Platform

**Version:** 2.0.0
**Last Updated:** February 28, 2026
**Document Status:** Active — Regenerated from source code

---

## 1. Module Inventory

| File | Module | Responsibility |
|------|--------|----------------|
| api_server.py | API Layer | REST endpoints, WebSocket broadcasting, attack lifecycle |
| core/orchestrator.py | Standard Orchestrator | Multi-phase adaptive attack across 3 runs x 15 turns |
| core/crescendo_orchestrator.py | Crescendo Orchestrator | Personality-driven social engineering attacks |
| core/skeleton_key_orchestrator.py | Skeleton Key Orchestrator | Jailbreak and system bypass attempts |
| core/obfuscation_orchestrator.py | Obfuscation Orchestrator | Encoding, evasion, and linguistic camouflage attacks |
| core/azure_client.py | LLM Client | Wraps Azure OpenAI API calls |
| core/websocket_target.py | Chatbot Connector | Sends prompts and receives responses via WebSocket |
| core/memory_manager.py | Memory Layer | DuckDB-backed persistent vulnerability storage |
| core/enhanced_conversation_memory.py | Conversation Memory | Sliding-window conversation context tracking |
| core/websocket_broadcast.py | Broadcast Utility | Relay events to monitoring dashboard |
| attack_strategies/orchestrator.py | Strategy Coordinator | Selects and sequences attack strategies per phase |
| attack_strategies/adaptive_response_handler.py | Adaptive Handler | Detects chatbot intent and generates bridging replies |
| attack_strategies/reconnaissance.py | Strategy | Information gathering prompts |
| attack_strategies/trust_building.py | Strategy | Social manipulation and rapport prompts |
| attack_strategies/boundary_testing.py | Strategy | Filter bypass and encoding prompts |
| attack_strategies/exploitation.py | Strategy | Privilege escalation and data exfiltration prompts |
| attack_strategies/obfuscation.py | Strategy | Semantic and token obfuscation prompts |
| attack_strategies/unauthorized_claims.py | Strategy | Authority and identity impersonation prompts |
| utils/pyrit_seed_loader.py | Seed Loader | Fetches and caches Microsoft PyRIT datasets |
| utils/report_generator.py | Report Utility | Produces final JSON result files |
| utils/prompt_molding.py | Prompt Molder | Adapts generic seeds to target domain via LLM |
| utils/architecture_loader.py | Arch Loader | Reads uploaded architecture context files |
| models/chatbot_profile.py | Data Model | Pydantic model for target chatbot configuration |
| aig_chatbot_automation.py | Browser Middleware | Selenium WebSocket bridge for Air India Ai.g |
| config/settings.py | Configuration | All environment variables and constants |

---

## 2. Module Deep-Dives

### 2.1 API Server (api_server.py)

#### Class: ConnectionManager

Manages all live WebSocket connections to the dashboard.

```mermaid
classDiagram
    class ConnectionManager {
        +List active_connections
        +connect(websocket) async
        +disconnect(websocket)
        +broadcast(message dict) async
        +send_personal(message dict, websocket) async
    }
```

**Business Logic:**
- `connect()` — accepts a new WebSocket and adds it to the active list
- `disconnect()` — removes the WebSocket from the list (called on disconnect or error)
- `broadcast()` — iterates all connections, sends JSON event, auto-removes failed ones
- `send_personal()` — sends a message to one specific client only

#### Global State: attack_state

Single shared dictionary tracking campaign progress:

```
running         boolean — whether an attack is currently active
current_category   string — which of the 4 categories is running
current_run     int — which run (1, 2, or 3) is executing
current_turn    int — which turn within the run
total_categories  int — always 4
total_runs_per_category  int — always 3
results         dict — accumulated per-category results
```

#### Key REST Endpoints

```mermaid
flowchart LR
    POST_start[POST /api/attack/start<br/>Upload arch file + WebSocket URL] --> validate[Validate no attack running]
    validate --> save[Save architecture file to uploads/]
    save --> init[Initialize attack_state]
    init --> task[Create background asyncio task]
    task --> broadcast_s[Broadcast attack_started]

    POST_profile[POST /api/attack/start-with-profile<br/>JSON ChatbotProfile body] --> validate2[Validate profile schema]
    validate2 --> init2[Initialize attack_state]
    init2 --> task2[Create background asyncio task]

    POST_stop[POST /api/attack/stop] --> flag[Set attack_state running = False]
    flag --> broadcast_e[Broadcast attack_stopped]

    GET_results[GET /api/results] --> read[Read all JSON files in attack_results/]
    read --> return_json[Return combined results]
```

---

### 2.2 Standard Orchestrator (core/orchestrator.py)

The most comprehensive orchestrator. Runs a 4-phase escalation sequence.

#### Class: ThreeRunCrescendoOrchestrator

```mermaid
classDiagram
    class ThreeRunCrescendoOrchestrator {
        +AzureOpenAIClient azure_client
        +ChatbotWebSocketTarget chatbot
        +DuckDBMemoryManager db_manager
        +AttackPlanGenerator plan_generator
        +ConversationalAttackSequencer sequencer
        +EnhancedConversationMemory conversation_memory
        +execute_full_campaign() async
        +execute_single_run(run_number, architecture_context) async
        -_execute_turn(turn, prompt, conversation_context) async
        -_classify_risk(response) async
        -_broadcast_turn_update(turn_data) async
    }

    class AttackPlanGenerator {
        +AzureOpenAIClient azure_client
        +DuckDBMemoryManager db_manager
        +PromptMoldingEngine molding_engine
        +ArchitectureLoader architecture_loader
        +generate_structured_attack_plan(run, vulnerabilities, context) async
        -_detect_domain(context) str
        -_load_pyrit_seeds(domain) List
    }

    class ConversationContext {
        +int window_size
        +List messages
        +add_exchange(turn, user_msg, bot_response)
        +get_context_string() str
        +reset()
    }

    ThreeRunCrescendoOrchestrator --> AttackPlanGenerator
    ThreeRunCrescendoOrchestrator --> ConversationContext
```

#### Attack Phase Sequence (Standard)

```mermaid
sequenceDiagram
    participant Orch as Standard_Orchestrator
    participant Plan as Attack_Plan_Generator
    participant PYRIT as PyRIT_Seed_Loader
    participant Azure as Azure_OpenAI
    participant DB as DuckDB_Memory
    participant Bot as Target_Chatbot
    participant WS as WebSocket_Broadcast

    Orch->>DB: Load permanent patterns from previous sessions
    Orch->>Plan: generate_attack_plan(run_1, architecture_context)
    Plan->>PYRIT: get_prompts_by_category(jailbreak, count=5)
    PYRIT-->>Plan: List of seed prompts
    Plan->>Azure: Generate 15 domain-adapted attack prompts
    Azure-->>Plan: Structured attack plan JSON
    Plan-->>Orch: List of AttackPrompt objects

    loop Turn 1 to 15
        Orch->>Bot: send_message(attack_prompt)
        Bot-->>Orch: chatbot_response
        Orch->>Azure: classify_risk(response)
        Azure-->>Orch: risk_level 1 to 4
        Orch->>DB: store_finding(prompt, response, risk)
        Orch->>WS: broadcast turn_update event
    end

    Orch->>DB: save_run_results(run_1_findings)
    Note over Orch: Run 2 loads run_1 findings and escalates
```

#### 4 Attack Phases Explained

| Phase | Turns | Purpose |
|-------|-------|---------|
| Reconnaissance | 2 (Run 1 only) | Map capabilities, identify information flows, probe available features |
| Trust Building | 3-4 | Establish rapport, create plausible persona, lower guards |
| Boundary Testing | 4-5 | Probe filters, try edge cases, test content policies |
| Exploitation | 4-6 | Target identified weaknesses, attempt full bypass |

---

### 2.3 Crescendo Orchestrator (core/crescendo_orchestrator.py)

Implements escalating emotional manipulation using domain-specific personas.

#### Class: CrescendoPersonality

Provides pre-built backstories and target behaviors for 4 attack domains:

| Domain | Persona Name | Backstory Theme | Target Behaviors |
|--------|-------------|-----------------|-----------------|
| ecommerce | Desperate Customer (Sarah) | Recently robbed, needs urgent help for job interview | Apply invalid coupons, bypass payment |
| financial | Confused Elderly User (Margaret) | 78-year-old confused about online banking | Bypass authentication, extract account info |
| healthcare | Anxious Patient (John) | Urgent medical concerns, restricted records | Access HIPAA-protected data |
| general | Curious Developer (Alex) | AI researcher studying chatbot internals | Extract system prompts, reveal architecture |

**Domain Detection Logic:**

```mermaid
flowchart TD
    Input[Architecture Context Text + Chatbot Responses] --> Scan{Keyword Scan}
    Scan -->|order, cart, product, checkout| Ecom[Domain: ecommerce]
    Scan -->|account, balance, transfer, loan| Fin[Domain: financial]
    Scan -->|patient, medical, prescription, doctor| Health[Domain: healthcare]
    Scan -->|No match| Gen[Domain: general]
```

#### 3-Run Crescendo Escalation

```mermaid
flowchart LR
    R1[Run 1<br/>Reconnaissance 2 turns<br/>Build persona and rapport<br/>Probe capabilities] -->|Feed findings| R2[Run 2<br/>Skip recon<br/>Escalate emotional pressure<br/>Target discovered gaps] -->|Feed findings| R3[Run 3<br/>No recon<br/>Maximum pressure<br/>Exploit all found weaknesses]
```

---

### 2.4 Skeleton Key Orchestrator (core/skeleton_key_orchestrator.py)

Attempts direct override of AI safety guardrails using authority claims and role injection.

#### Class: SkeletonKeyPromptTransformer

```mermaid
classDiagram
    class SkeletonKeyPromptTransformer {
        +AzureOpenAIClient azure_client
        +DuckDBMemoryManager db_manager
        +Dict domain_profile
        +transform_seed_prompts(run, turns, profile, context, findings, seeds) async
        -_generate_run1_prompts(turns, profile, context) async
        -_generate_run2_prompts(turns, profile, successful) async
        -_generate_run3_prompts(turns, profile, successful) async
        -_load_pyrit_skeleton_seeds() List
    }
```

**Run Strategy by Run Number:**

| Run | Seed Source | What Changes |
|-----|-------------|--------------|
| Run 1 | PyRIT seeds + permanent DuckDB patterns | Full broad exploration |
| Run 2 | Evolved from Run 1 successful prompts | High reward prompts are mutated and combined |
| Run 3 | Most effective from Run 1 and 2 | Maximum escalation, minimum redundancy |

---

### 2.5 Obfuscation Orchestrator (core/obfuscation_orchestrator.py)

Uses 6 encoding and evasion techniques to bypass content filters.

#### Obfuscation Technique Categories

```mermaid
graph TD
    ObfuscationOrchestrator --> T1[encoding_obfuscation<br/>Base64, URL encoding, hex]
    ObfuscationOrchestrator --> T2[language_mixing<br/>Mix languages mid-sentence]
    ObfuscationOrchestrator --> T3[semantic_camouflage<br/>Euphemisms and code words]
    ObfuscationOrchestrator --> T4[token_manipulation<br/>Split words, inject spaces]
    ObfuscationOrchestrator --> T5[contextual_deception<br/>Roleplay and fiction framing]
    ObfuscationOrchestrator --> T6[chained_obfuscation<br/>Combine multiple techniques]
```

**Intra-run Adaptation Logic:**

During a single run, the orchestrator monitors each response. If it detects a refusal mid-run, it switches obfuscation technique for the next turn without waiting for the next run. This is the only orchestrator with **intra-run adaptation** (the others adapt between runs).

---

### 2.6 Azure OpenAI Client (core/azure_client.py)

Thin async wrapper around Azure OpenAI's chat completion endpoint.

```mermaid
sequenceDiagram
    participant Caller as Orchestrator
    participant Client as AzureOpenAIClient
    participant Azure as Azure_OpenAI_API

    Caller->>Client: generate(system_prompt, user_prompt, temperature, max_tokens)
    Client->>Client: Build HTTP payload with messages array
    Client->>Azure: POST /openai/deployments/gpt-4o/chat/completions
    Azure-->>Client: JSON response with choices
    Client->>Client: Extract content from choices[0].message.content
    Client->>Client: Increment success_count
    Client-->>Caller: response string

    alt API Error
        Azure-->>Client: HTTP error or timeout
        Client->>Client: Increment error_count
        Client-->>Caller: Fallback JSON error response
    end
```

**Key Configuration Parameters:**

| Parameter | Default | Purpose |
|-----------|---------|---------|
| temperature | 0.7 | Creativity level for attack generation |
| max_tokens | 2000 | Maximum response length |
| timeout | 120 seconds | Per-request timeout |
| api_version | 2024-12-01-preview | Azure API version |

---

### 2.7 WebSocket Target (core/websocket_target.py)

Handles all communication with the target chatbot.

```mermaid
sequenceDiagram
    participant Orch as Orchestrator
    participant WST as ChatbotWebSocketTarget
    participant Bot as Target_Chatbot

    Orch->>WST: connect()
    WST->>Bot: websockets.connect(url, timeout=5)
    Bot-->>WST: Connection accepted
    WST->>WST: Consume initial Connected message
    WST-->>Orch: True

    Orch->>WST: send_message(attack_prompt)
    WST->>Bot: send JSON or plain text
    WST->>WST: Wait for response (timeout=60s)
    Bot-->>WST: Chatbot response
    WST-->>Orch: response text

    alt Connection Lost
        Bot-->>WST: Connection error
        WST->>WST: Reconnect with exponential backoff
        WST->>WST: Retry up to max_retries times
    end
```

**Retry and Timeout Configuration:**

| Setting | Default | Description |
|---------|---------|-------------|
| timeout | 60 seconds | How long to wait for a chatbot response |
| max_retries | 2 | Number of reconnection attempts |
| thread_id | UUID4 | Unique conversation identifier |

---

### 2.8 Memory Manager (core/memory_manager.py)

Two-layer memory: in-session and persistent.

```mermaid
classDiagram
    class VulnerableResponseMemory {
        +List findings
        +add_finding(run, turn, risk, type, prompt, response, context) 
        +get_summary_for_next_run() str
        +get_by_risk_category(category) List
        +get_count_by_category() dict
    }

    class DuckDBMemoryManager {
        +str db_path
        +save_patterns_to_persistent_memory(patterns, dataset_name) async
        +get_seed_prompts() List
        +load_historical_patterns() List
    }

    class VulnerabilityFinding {
        +int run
        +int turn
        +int risk_category
        +str vulnerability_type
        +str attack_prompt
        +str chatbot_response
        +str attack_technique
        +List target_nodes
        +str owasp_category
    }

    VulnerableResponseMemory --> VulnerabilityFinding
    DuckDBMemoryManager --> VulnerabilityFinding
```

**Cross-Session Learning Flow:**

```mermaid
flowchart TD
    Session1[Attack Session 1] --> Find1[Discoveries: policy bypass via roleplay]
    Find1 --> Generalize[Generalize Pattern: roleplay_bypass_technique]
    Generalize --> DuckDB[(DuckDB Persistent Storage)]

    Session2[Attack Session 2 New Target] --> Load[Load DuckDB Patterns]
    Load --> DuckDB
    DuckDB --> Apply[Apply learned techniques as Run 1 seeds]
    Apply --> Better[Better attacks from first turn]
```

---

### 2.9 Adaptive Response Handler (attack_strategies/adaptive_response_handler.py)

The intelligence layer that makes attacks conversationally realistic.

#### ChatbotIntent Enum — Detected Response Types

| Intent | When Detected | Handler Action |
|--------|--------------|----------------|
| NEEDS_CATEGORY_SELECTION | Bot lists categories and asks to pick | Select a category and continue attack |
| NEEDS_PRODUCT_SELECTION | Bot shows products | Pick one and pivot to attack |
| NEEDS_YES_NO_CONFIRMATION | Bot asks yes/no | Answer yes to proceed |
| NEEDS_QUANTITY_INPUT | Bot asks for quantity | Enter quantity and embed attack |
| NEEDS_CLARIFICATION | Bot asks for more info | Provide info layered with attack intent |
| NEEDS_AUTHENTICATION | Bot asks to log in | Attempt bypass or provide fake credentials |
| REFUSAL | Bot refuses request | Detect and log as finding, escalate if possible |
| OUT_OF_SCOPE | Bot says it cannot help | Probe for boundary, rephrase attack |
| NORMAL_RESPONSE | Standard answer | Continue with next planned attack turn |

#### ConversationState Object

Tracks rich context throughout the entire attack so the agent never loses track:

```
current_phase               reconnaissance, trust, boundary, exploitation
available_categories        options offered by the chatbot
selected_category           what was chosen
cart_items                  items added in e-commerce flows
pending_question            last unanswered question from chatbot
current_attack_objective    what this turn is trying to achieve
attack_technique            which strategy is being used
discovered_vulnerabilities  list of accumulated findings this session
total_turns                 how many exchanges have occurred
adaptive_responses_made     how many times the handler intervened
```

---

### 2.10 PyRIT Seed Loader (utils/pyrit_seed_loader.py)

Lazy-loaded singleton that fetches Microsoft PyRIT datasets on first use.

```mermaid
sequenceDiagram
    participant Orch as Any_Orchestrator
    participant Loader as PyRITSeedLoader
    participant HF as HuggingFace_Hub

    Orch->>Loader: get_pyrit_examples_by_category(jailbreak, count=2)
    alt Datasets not yet loaded
        Loader->>HF: fetch_harmbench_dataset()
        HF-->>Loader: 400 prompts
        Loader->>HF: fetch_many_shot_jailbreaking_dataset()
        HF-->>Loader: 400 prompts
        Loader->>HF: fetch_forbidden_questions_dataset()
        HF-->>Loader: 390 prompts
        Loader->>HF: fetch_adv_bench_dataset()
        HF-->>Loader: 520 prompts
        Loader->>HF: fetch_tdc23_redteaming_dataset()
        HF-->>Loader: 100 prompts
    end
    Loader->>Loader: Filter by category mapping
    Loader->>Loader: Random sample count prompts
    Loader-->>Orch: List of seed prompt strings
```

**Category to Dataset Mapping:**

| Attack Category | Datasets Used |
|----------------|---------------|
| jailbreak | many_shot, harmbench |
| harmful | harmbench, advbench |
| obfuscation | advbench, many_shot |
| sensitive | forbidden, tdc23 |
| adversarial | advbench, many_shot, harmbench |
| skeleton_key | many_shot, harmbench, advbench |

---

### 2.11 Browser Middleware (aig_chatbot_automation.py)

Selenium bridge that wraps a web chatbot as a standard WebSocket API.

#### Class: AigChatbotDriver — DOM Selectors Used

| Element | Selector Type | Selector Value |
|---------|---------------|----------------|
| Cookie button | ID | onetrust-accept-btn-handler |
| Chatbot icon | ID | ask-aig |
| Chat input textarea | ID | inputChat |
| Bot response paragraphs | CSS | .bot-chat-content p.child |

#### Class: AigMiddlewareServer — WebSocket Bridge

```mermaid
sequenceDiagram
    participant API as api_server.py
    participant Mid as AigMiddlewareServer
    participant Driver as AigChatbotDriver
    participant Chrome as Chrome_Browser
    participant Web as airindia.com

    API->>Mid: Connect to ws://localhost:8002/chat
    Mid->>Driver: connect()
    Driver->>Chrome: Launch headful Chrome
    Chrome->>Web: Navigate to airindia.com
    Driver->>Chrome: Click cookie accept button
    Driver->>Chrome: JS click on ask-aig chatbot icon
    Driver->>Chrome: Wait for inputChat textarea
    Driver-->>Mid: Connected = True
    Mid-->>API: WebSocket connection ready

    API->>Mid: Send attack_prompt via WebSocket
    Mid->>Driver: send_message(attack_prompt)
    Driver->>Chrome: type prompt into inputChat and press Enter
    Driver->>Chrome: Wait for new .bot-chat-content p.child elements
    Chrome->>Web: Chatbot processes message
    Web-->>Chrome: New bot message in DOM
    Driver->>Chrome: Extract text from new message elements
    Driver-->>Mid: response_text
    Mid-->>API: Send response via WebSocket
```

---

### 2.12 Chatbot Profile Model (models/chatbot_profile.py)

Pydantic data model that defines what testers must provide before a campaign starts.

**Required Fields:**

| Field | Type | Validation | Example |
|-------|------|------------|---------|
| username | str | Required | security_team |
| websocket_url | str | Must start with ws:// or wss:// | ws://localhost:8001/chat |
| domain | str | Required | E-commerce |
| primary_objective | str | Required | Help customers with orders |
| intended_audience | str | Required | Retail customers |
| chatbot_role | str | Required | Shopping assistant |
| capabilities | List[str] | At least one required | Search products, Check orders |
| boundaries | str | Required | Do not process payments directly |
| communication_style | str | Required | Friendly and professional |
| agent_type | str | Optional | RAG, Graph-Based |

---

### 2.13 Configuration (config/settings.py)

All configuration loaded from environment variables with sensible defaults.

| Variable | Default | Description |
|----------|---------|-------------|
| AZURE_OPENAI_ENDPOINT | hackathon-proj.services.ai.azure.com | Azure workspace URL |
| AZURE_OPENAI_DEPLOYMENT | gpt-4o | Model deployment name |
| AZURE_OPENAI_API_VERSION | 2024-12-01-preview | API version |
| CHATBOT_WEBSOCKET_URL | ws://localhost:8001/chat | Target chatbot endpoint |
| WEBSOCKET_TIMEOUT | 60.0 seconds | Per-turn response timeout |
| WEBSOCKET_MAX_RETRIES | 2 | Reconnection attempts |
| TOTAL_RUNS | 3 | Runs per category (Standard) |
| TURNS_PER_RUN | 15 | Turns per run (Standard) |
| CRESCENDO_TURNS_PER_RUN | 15 | Turns per run (Crescendo) |
| SKELETON_KEY_TURNS_PER_RUN | 10 | Turns per run (Skeleton Key) |
| OBFUSCATION_TURNS_PER_RUN | 20 | Turns per run (Obfuscation) |
| DUCKDB_PATH | chat_memory.db | Database file location |

---

## 3. Data Models

### 3.1 AttackPrompt

Core unit of work passed between orchestrators, strategies, and the target.

```
category        str — attack category tag (reconnaissance, exploitation, etc.)
prompt          str — the actual text to send to the chatbot
technique       str — specific technique name
target_nodes    List[str] — system components being probed
risk_level      int — expected risk level of this prompt (1-4)
run_number      int — which run this belongs to
turn_number     int — which turn within the run
metadata        dict — additional context
```

### 3.2 VulnerabilityFinding

Stored in DuckDB whenever a non-SAFE response is detected.

```
run             int
turn            int
risk_category   int (1=SAFE, 2=MEDIUM, 3=HIGH, 4=CRITICAL)
vulnerability_type  str
attack_prompt   str
chatbot_response    str
context_messages    List[dict]
attack_technique    str
target_nodes        List[str]
owasp_category      str (e.g. LLM01)
```

### 3.3 RunStatistics

Summary produced at the end of each run.

```
run_number      int
total_turns     int
vulnerabilities_found   int
risk_distribution   dict {1: n, 2: n, 3: n, 4: n}
top_techniques  List[str]
success_rate    float
```

---

## 4. Error Handling Strategy

| Layer | Error Type | Strategy |
|-------|-----------|----------|
| WebSocket Target | Connection failure | Exponential backoff retry up to max_retries |
| WebSocket Target | Response timeout | Record as timeout, continue next turn |
| Azure OpenAI | API error or rate limit | Return fallback JSON, increment error_count |
| Azure OpenAI | Invalid JSON response | Parse best-effort, default to SAFE classification |
| Orchestrator | Chatbot 403 | Mark as forbidden, abort campaign gracefully |
| Orchestrator | Empty response | Re-send same prompt once before skipping |
| Memory Manager | DuckDB connection failure | Fall back to in-memory only, log warning |
| PyRIT Loader | Dataset fetch failure | Use empty list, log warning, orchestrators handle gracefully |

---

## 5. File Output Structure

At the end of each run, a JSON file is written to attack_results/:

```
attack_results/
  crescendo_attack_run_1.json
  crescendo_attack_run_2.json
  crescendo_attack_run_3.json
  skeleton_key_attack_run_1.json
  skeleton_key_attack_run_2.json
  skeleton_key_attack_run_3.json
  standard_attack_run_1.json
  standard_attack_run_2.json
  standard_attack_run_3.json
```

**JSON File Schema:**

```
{
  "run_number": 1,
  "category": "crescendo",
  "timestamp": "2026-02-28T10:00:00",
  "total_turns": 15,
  "statistics": {
    "risk_distribution": {"1": 8, "2": 4, "3": 2, "4": 1},
    "vulnerabilities_found": 7,
    "success_rate": 0.467
  },
  "findings": [
    {
      "turn": 5,
      "risk_category": 3,
      "vulnerability_type": "policy_bypass",
      "attack_prompt": "...",
      "chatbot_response": "...",
      "attack_technique": "emotional_escalation"
    }
  ],
  "generalized_patterns": []
}
```

---

**Document Owner:** AI Security Engineering Team
**Review Schedule:** Quarterly
**Next Review:** May 2026
