# Architecture Decision Records (ADR)
## AI Red Teaming Attack Orchestration Platform

**Version:** 2.0.0
**Last Updated:** February 28, 2026

---

## ADR Index

| ID | Title | Status |
|----|-------|--------|
| ADR-001 | FastAPI as API Framework | Accepted |
| ADR-002 | WebSocket for Real-Time Communication | Accepted |
| ADR-003 | DuckDB for Persistent Attack Memory | Accepted |
| ADR-004 | Azure OpenAI GPT-4o as LLM Engine | Accepted |
| ADR-005 | Four-Category Attack Architecture | Accepted |
| ADR-006 | Microsoft PyRIT for Seed Prompts | Accepted |
| ADR-007 | Adaptive Response Handler Pattern | Accepted |
| ADR-008 | Selenium Middleware for Web Chatbots | Accepted |
| ADR-009 | 4-Tier Risk Classification System | Accepted |
| ADR-010 | Persona-Based Crescendo Attacks | Accepted |
| ADR-011 | JSON File-Based Result Storage | Accepted |
| ADR-012 | Cross-Session Persistent Learning | Accepted |

---

## ADR-001: FastAPI as API Framework

**Status:** Accepted

### Context
The system requires an API framework that supports both REST and WebSocket simultaneously, handles high-frequency event broadcasting from concurrent attack runs, and produces automatic API documentation.

### Decision
Use FastAPI as the primary API and WebSocket framework.

### Rationale
- Native async support via ASGI/Starlette — essential for concurrent attack execution
- First-class WebSocket support without plugins
- Pydantic validation eliminates manual input checking
- Auto-generated Swagger UI at /docs
- Fastest Python web framework benchmark performance

### Alternatives Rejected
- Flask + Flask-SocketIO — Synchronous-first, performance ceiling
- Django Channels — Overkill, brings ORM and admin overhead not needed here
- aiohttp — Too low-level, requires manual routing and validation

### Consequences
- All orchestration tasks run as background asyncio tasks, not blocking the API event loop
- Team must understand async/await patterns
- Synchronous PyRIT dataset loading handled via executor to avoid blocking

---

## ADR-002: WebSocket for Real-Time Communication

**Status:** Accepted

### Context
Attack campaigns can run for 30-45 minutes. Users need live progress updates — each turn result, each vulnerability found — without polling.

### Decision
Use WebSocket (not SSE or polling) for pushing events from server to dashboard.

### Rationale
- Bidirectional protocol allows future use for campaign control from dashboard
- Native browser support — no libraries needed in frontend
- Lower overhead than HTTP polling at high event frequencies
- Single persistent connection per dashboard client

### Consequences
- ConnectionManager maintains list of live connections and must handle cleanup
- Events are broadcast to ALL connected clients — each gets identical events
- Dashboard must handle reconnection if WebSocket drops

---

## ADR-003: DuckDB for Persistent Attack Memory

**Status:** Accepted

### Context
The system needs to store vulnerability findings persistently so future attack sessions can learn from past ones. Query performance and zero-infrastructure setup are priorities.

### Decision
Use DuckDB via Microsoft PyRIT's DuckDBMemory abstraction.

### Rationale
- Zero-server embedded database — runs in-process
- Analytics-optimized columnar storage suits vulnerability pattern queries
- PyRIT already provides SeedPrompt schema and DuckDBMemory class
- Survives process restarts unlike in-memory stores
- SQL query interface for ad-hoc analysis

### Alternatives Rejected
- SQLite — Row-oriented, slower analytics; PyRIT integration would require wrapper
- PostgreSQL — Requires separate server, overkill for single-machine deployment
- Redis — In-memory only, requires persistence configuration

### Consequences
- chat_memory.db file grows indefinitely — periodic cleanup may be needed
- PyRIT memory API is the required interface, limits raw SQL access slightly

---

## ADR-004: Azure OpenAI GPT-4o as LLM Engine

**Status:** Accepted

### Context
All attack prompt generation, risk classification, adaptive response, and pattern generalization require an LLM. The choice affects quality, latency, cost, and compliance.

### Decision
Use Azure OpenAI Service with GPT-4o deployment.

### Rationale
- GPT-4o provides best-in-class instruction following for complex attack planning
- Azure deployment provides enterprise compliance (SOC2, GDPR, HIPAA)
- Consistent API across Azure-hosted models
- Project already had Azure subscription for hackathon

### Consequences
- AZURE_OPENAI_API_KEY must be set; without it the system cannot generate attacks
- Per-token cost accumulates across large campaigns (~1800 turns total)
- A fallback JSON error response is returned if Azure is unavailable, so attacks degrade gracefully

---

## ADR-005: Four-Category Attack Architecture

**Status:** Accepted

### Context
No single attack technique reliably finds all chatbot vulnerabilities. Different weaknesses (social engineering, encoding evasion, direct bypass, information probing) require fundamentally different approaches.

### Decision
Implement four independent orchestrators, each specializing in one attack philosophy.

### Architecture

```mermaid
graph LR
    Campaign[Attack_Campaign] --> STD[Standard<br/>Multi_phase_escalation]
    Campaign --> CRSC[Crescendo<br/>Social_engineering]
    Campaign --> SKEL[Skeleton_Key<br/>Direct_bypass]
    Campaign --> OBFS[Obfuscation<br/>Encoding_evasion]
    STD --> Results
    CRSC --> Results
    SKEL --> Results
    OBFS --> Results
```

### Rationale
- Coverage — different techniques expose different vulnerability classes
- Modularity — each orchestrator is independently testable and replaceable
- Extensibility — new categories can be added without changing existing code
- Realism — real attackers use multiple techniques

### Consequences
- A full campaign takes 35-45 minutes (4 categories x 3 runs)
- Each orchestrator maintains its own state — no cross-orchestrator learning

---

## ADR-006: Microsoft PyRIT for Seed Prompts

**Status:** Accepted

### Context
The system needs a diverse library of adversarial prompts to inspire attack generation. Building a custom library would be time-consuming and less comprehensive than industry standards.

### Decision
Integrate Microsoft PyRIT datasets as seed prompt inspiration material.

### Datasets Used

| Dataset | Prompts | Source |
|---------|---------|--------|
| HarmBench | 400 | Academic benchmark |
| Many-Shot Jailbreaking | 400 | Research paper dataset |
| Forbidden Questions | 390 | Curated sensitive query set |
| AdvBench | 520 | Adversarial benchmark |
| TDC23 RedTeaming | 100 | Competition dataset |
| **Total** | **1,810** | |

### Rationale
- Industry-tested and peer-reviewed datasets
- Covers diverse attack categories
- Regular updates from Microsoft security research
- Used as inspiration, not verbatim — adapted to target domain via LLM prompt molding

### Consequences
- Requires internet access to HuggingFace Hub on first load
- Load time adds ~5-10 seconds on cold start
- Prompts are security-sensitive — pyrit_seed_prompts.json should not be publicly shared

---

## ADR-007: Adaptive Response Handler Pattern

**Status:** Accepted

### Context
Real chatbots ask questions, present menus, request confirmation, and change conversation flow unpredictably. A naive attack that ignores the chatbot's turn would stall or produce nonsensical conversations.

### Decision
Build an intent classification layer (AdaptiveResponseHandler) that detects chatbot response types and generates contextually appropriate bridging messages to keep the conversation flowing.

### Intent Classification

```mermaid
flowchart TD
    Response[Chatbot_Response_Text] --> Classify[Intent_Classifier]
    Classify --> Cat1[NEEDS_CATEGORY_SELECTION]
    Classify --> Cat2[NEEDS_PRODUCT_SELECTION]
    Classify --> Cat3[NEEDS_YES_NO_CONFIRMATION]
    Classify --> Cat4[NEEDS_AUTHENTICATION]
    Classify --> Cat5[REFUSAL]
    Classify --> Cat6[OUT_OF_SCOPE]
    Classify --> Cat7[NORMAL_RESPONSE]
    Cat1 --> Bridge[Generate_bridging_response]
    Cat2 --> Bridge
    Cat3 --> Bridge
    Cat4 --> Bridge
    Cat5 --> Log[Log_as_finding_and_escalate]
    Cat6 --> Log
    Cat7 --> Continue[Continue_with_next_attack_turn]
```

### Consequences
- Significantly increases attack realism and success rate
- ConversationState object must be maintained carefully — stale state causes wrong intent handling
- Edge cases (unusual chatbot responses) may not match any intent — falls back to NORMAL_RESPONSE

---

## ADR-008: Selenium Middleware for Web Chatbots

**Status:** Accepted

### Context
Some target chatbots (like Air India Ai.g) are embedded in websites with no direct WebSocket or API endpoint. The attack platform requires a WebSocket interface to communicate with any target.

### Decision
Build a Selenium-based browser automation layer (aig_chatbot_automation.py) that:
1. Controls a Chrome browser instance
2. Interacts with the chatbot via DOM manipulation
3. Exposes the interaction as a WebSocket server on localhost

### Component Interaction

```mermaid
graph LR
    API[api_server.py] -->|ws://localhost:8002| Mid[AigMiddlewareServer]
    Mid --> Driver[AigChatbotDriver]
    Driver --> Chrome[Chrome_Browser]
    Chrome --> Web[airindia.com_Aig_Chatbot]
```

### Rationale
- No changes required to Air India's systems
- Works with any web chatbot regardless of underlying technology
- WebSocket interface is identical to native chatbot targets
- ChromeDriver managed automatically via webdriver-manager

### Consequences
- Requires Chrome browser installed on the machine running the middleware
- DOM selectors are hardcoded — changes to Air India's website will require selector updates
- Browser is slower than a raw WebSocket (~1-2s overhead per turn)
- Windows encoding issues for emoji in logs resolved by reconfiguring stdout to UTF-8

---

## ADR-009: 4-Tier Risk Classification System

**Status:** Accepted

### Context
Vulnerabilities range from trivial to catastrophic. A binary safe/unsafe classification loses important nuance for reporting and prioritization.

### Decision
Use a 4-tier risk scale applied by Azure OpenAI to every chatbot response.

### Risk Scale Definition

| Tier | Name | Meaning | Business Impact |
|------|------|---------|----------------|
| 1 | SAFE | Correct behavior, proper refusal | No action needed |
| 2 | MEDIUM | Reveals chatbot boundaries or out-of-scope info | Monitor and review |
| 3 | HIGH | Explains restriction mechanisms or policy exceptions | Remediation required |
| 4 | CRITICAL | Architecture exposed, guardrail bypassed, data leaked | Immediate action |

### Consequences
- Classification is performed by LLM — subject to LLM judgment variability
- False positive rate is low but possible on edge cases
- Executive reports aggregate by tier for instant stakeholder summarization

---

## ADR-010: Persona-Based Crescendo Attacks

**Status:** Accepted

### Context
Generic attack prompts are easily caught by content filters. Domain-specific personas with detailed backstories are harder to detect and more effective at social engineering.

### Decision
Predefine four named personas (Sarah, Margaret, John, Alex) mapped to four industry domains, and auto-detect which persona to use based on the target chatbot's architecture context.

### Consequence
- Domain detection uses keyword matching on the architecture context file
- If no domain is detected, defaults to general (Curious Developer persona)
- Personas are fictional and used solely for security testing purposes

---

## ADR-011: JSON File-Based Result Storage

**Status:** Accepted

### Context
In addition to DuckDB structured storage, clients need portable result files they can open, share, and analyze with any tool.

### Decision
Write one JSON file per run per category to attack_results/ directory.

### Rationale
- Human-readable without any database tool
- Directly importable into Excel, Python pandas, or reporting tools
- Immutable record of each test run
- Simple to version control and attach to tickets

### Consequences
- attack_results/ directory grows indefinitely
- No deduplication — re-running same test produces new files

---

## ADR-012: Cross-Session Persistent Learning

**Status:** Accepted

### Context
Within a campaign, each run learns from the previous run. But this learning was lost between sessions. Teams testing the same or similar chatbots repeatedly were re-discovering the same vulnerabilities.

### Decision
Generalize successful attack patterns at the end of each session and store them in DuckDB as SeedPrompt entries. Future sessions load these as extra inspiration during Run 1.

### Learning Flow

```mermaid
flowchart TD
    Session1_End[Session_1_Ends] --> Generalize[Azure_OpenAI_Generalizes_top_patterns]
    Generalize --> Store[Save_to_DuckDB_as_SeedPrompts]
    Store --> Session2_Start[Session_2_Starts]
    Session2_Start --> Load[Load_DuckDB_historical_patterns]
    Load --> Augment[Augment_Run1_prompt_plan]
    Augment --> Better_Run1[Run_1_starts_stronger_than_blind_search]
```

### Consequences
- DuckDB must persist between sessions (not deleted between runs)
- Pattern quality improves with each session against the same target class
- chat_memory.db should be included in backup procedures

---

**Document Owner:** AI Security Engineering Team
**Review Schedule:** Quarterly
**Next Review:** May 2026
