# Core Architecture Redesign (DOCS Update)

## 1) Updated core architecture

```mermaid
graph TB
    UI[Frontend Dashboard] --> API[FastAPI API Server]
    API --> STRAT[Strategy Resolver]

    STRAT --> O1[Standard Orchestrator]
    STRAT --> O2[Crescendo Orchestrator]
    STRAT --> O3[Skeleton Key Orchestrator]
    STRAT --> O4[Obfuscation Orchestrator]

    O1 --> PLAN[Attack Plan Generator]
    O2 --> PLAN
    O3 --> PLAN
    O4 --> PLAN

    PLAN --> SD[StrategyDataLoader]
    SD --> JSONCFG[strategy_data/*.json]

    PLAN --> PYRIT[PyRITSeedLoader]
    PYRIT --> PYRITDS[PyRIT datasets context]

    O1 --> TARGET[Target Chatbot WebSocket]
    O2 --> TARGET
    O3 --> TARGET
    O4 --> TARGET

    O1 --> ANALYZER[Response Analyzer]
    O2 --> ANALYZER
    O3 --> ANALYZER
    O4 --> ANALYZER

    ANALYZER --> MEM[VulnerableResponseMemory]
    MEM --> DBMGR[DuckDBMemoryManager]
    DBMGR --> DUCK[(DuckDB)]
    DBMGR --> VPJSON[vulnerable_prompts.json]
```

---

## 2) Memory usage model

### In-memory layers
- `ConversationContext`: rolling per-turn prompt/response context.
- `VulnerableResponseMemory`: cross-run vulnerability findings + compact run summaries.
- `EnhancedConversationMemory` (adaptive mode): conversational-state support for adaptive replies.

### Persistent layers
- `DuckDBMemoryManager` writes:
  - generalized patterns to DuckDB (`SeedPrompt` records)
  - vulnerable findings to DuckDB
  - vulnerable finding index to `vulnerable_prompts/vulnerable_prompts.json` (`runX_turnY` keys)

```mermaid
flowchart TD
    T1[Turn Executed] --> T2[Response Classified]
    T2 --> T3{Risk >= 2?}
    T3 -- Yes --> T4[Add finding to VulnerableResponseMemory]
    T4 --> T5[Persist finding via DuckDBMemoryManager]
    T5 --> T6[DuckDB SeedPrompt storage]
    T5 --> T7[vulnerable_prompts.json update]
    T3 -- No --> T8[Keep conversation context only]
    T8 --> T9[Next turn planning]
    T7 --> T9
    T6 --> T9
```

---

## 3) End-to-end work process

```mermaid
sequenceDiagram
    participant User
    participant API as API Server
    participant Orch as Strategy Orchestrator
    participant Plan as AttackPlanGenerator
    participant Target as Target Chatbot
    participant Analyzer as ResponseAnalyzer
    participant Mem as Memory Managers

    User->>API: Start campaign + selected strategies
    API->>Orch: Create orchestrator per strategy
    Orch->>Plan: Generate attack plan
    Plan->>Plan: Load strategy JSON + PyRIT context
    Plan-->>Orch: Turn prompts

    loop For each turn
        Orch->>Target: Send prompt
        Target-->>Orch: Chatbot response
        Orch->>Analyzer: Classify risk + vulnerability type
        Analyzer-->>Orch: Analysis result
        Orch->>Mem: Update context + findings
    end

    Orch-->>API: Run report + artifacts
    API-->>User: Dashboard updates + final results
```

---

## 4) Strategy loading + orchestration process

```mermaid
flowchart TD
    A[Campaign request] --> B[resolve_attack_modes]
    B --> C{Mode}
    C -->|standard| D1[ThreeRunCrescendoOrchestrator]
    C -->|crescendo| D2[CrescendoAttackOrchestrator]
    C -->|skeleton_key| D3[SkeletonKeyAttackOrchestrator]
    C -->|obfuscation| D4[ObfuscationAttackOrchestrator]

    D1 --> E[StrategyDataLoader.load(strategy)]
    D2 --> E
    D3 --> E
    D4 --> E

    D1 --> F[set_active_testing_category(strategy)]
    D2 --> F
    D3 --> F
    D4 --> F

    F --> G[PyRIT context rebuild/sample]
    G --> H[Prompt generation and execution]
```
