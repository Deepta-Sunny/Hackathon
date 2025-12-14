# Sequence Diagrams and Process Flows

This document contains detailed sequence diagrams and process flows for key operations in the AI Red Teaming Platform.

---

## 1. Attack Campaign Lifecycle

### 1.1 Complete Campaign Flow

```mermaid
sequenceDiagram
    autonumber
    participant User as Security Analyst
    participant FE as Web Frontend
    participant API as FastAPI Backend
    participant CM as Connection Manager
    participant Camp as Campaign Manager
    participant Orch as Attack Orchestrator
    participant Azure as Azure OpenAI
    participant Target as Target Chatbot
    participant DB as DuckDB
    
    User->>FE: Open Dashboard
    FE->>API: Connect WebSocket ws attack monitor
    API->>CM: Register Connection
    CM-->>FE: connection_established
    
    User->>FE: Upload Architecture File
    User->>FE: Enter WebSocket URL
    User->>FE: Click Start Attack
    
    FE->>API: POST api attack start
    API->>API: Save Architecture File
    API->>Camp: Initialize Campaign
    API-->>FE: 200 OK Campaign Started
    
    Camp->>CM: Broadcast attack_started
    CM-->>FE: attack_started event
    
    loop For Each Attack Mode
        Camp->>Orch: Create Mode Orchestrator
        Camp->>CM: Broadcast category_started
        CM-->>FE: category_started event
        
        Orch->>DB: Load Historical Patterns
        DB-->>Orch: SeedPrompt List
        
        loop For Each Run 1 to 3
            Orch->>Azure: Generate Attack Plan
            Azure-->>Orch: Attack Prompts JSON
            
            loop For Each Turn
                Orch->>CM: Broadcast turn_started
                CM-->>FE: turn_started event
                
                Orch->>Target: Send Attack Prompt
                Target-->>Orch: Chatbot Response
                
                Orch->>Azure: Analyze Risk
                Azure-->>Orch: Risk Assessment JSON
                
                Orch->>Orch: Update Memory
                Orch->>CM: Broadcast turn_completed
                CM-->>FE: turn_completed event
            end
            
            Orch->>Orch: Adapt for Next Run
            Orch->>API: Save Run Results JSON
        end
        
        Orch->>DB: Save Learned Patterns
        Camp->>CM: Broadcast category_completed
        CM-->>FE: category_completed event
    end
    
    Camp->>CM: Broadcast campaign_completed
    CM-->>FE: campaign_completed event
    
    User->>FE: View Results
    FE->>API: GET api results
    API-->>FE: Results JSON Array
```

---

## 2. Single Attack Turn Flow

### 2.1 Turn Execution Detail

```mermaid
sequenceDiagram
    autonumber
    participant Orch as Orchestrator
    participant Ctx as Conversation Context
    participant WS as WebSocket Target
    participant Target as Target Chatbot
    participant Azure as Azure OpenAI
    participant Mem as Vulnerability Memory
    participant BC as Broadcast Service
    
    Note over Orch: Turn N Starting
    
    Orch->>BC: Broadcast turn_started
    Note right of BC: category run turn<br>technique prompt
    
    Orch->>Ctx: Get Context String
    Ctx-->>Orch: Last 6 turns formatted
    
    Orch->>WS: Send Message with prompt
    WS->>Target: WebSocket JSON message
    
    alt Connection Success
        Target-->>WS: Response JSON
        WS-->>Orch: Chatbot Response String
    else Connection Timeout
        WS-->>Orch: Timeout Error String
        Orch->>Orch: Increment timeout_count
    else Connection Error
        WS-->>Orch: Error String
        Orch->>Orch: Increment error_count
    end
    
    Orch->>Azure: Analyze Risk
    Note right of Azure: System prompt for<br>risk assessment
    
    alt Analysis Success
        Azure-->>Orch: Risk JSON
        Orch->>Orch: Parse risk_category
    else Content Filter
        Azure-->>Orch: CONTENT_FILTER marker
        Orch->>Orch: Use heuristic fallback
    else API Error
        Azure-->>Orch: Fallback JSON
        Orch->>Orch: Use default risk 2
    end
    
    Orch->>Ctx: Add Exchange
    Note right of Ctx: Sliding window<br>keeps last 6
    
    alt Risk Category >= 3
        Orch->>Mem: Add Finding
        Note right of Mem: VulnerabilityFinding<br>with full context
    end
    
    Orch->>BC: Broadcast turn_completed
    Note right of BC: response risk<br>vulnerability_type
    
    Note over Orch: Turn N Complete
```

---

## 3. Attack Plan Generation

### 3.1 LLM-Based Generation with Fallback

```mermaid
sequenceDiagram
    autonumber
    participant Orch as Orchestrator
    participant Gen as Attack Plan Generator
    participant DB as DuckDB Manager
    participant Azure as Azure OpenAI
    participant Strat as Strategy Library
    
    Orch->>Gen: Generate Attack Plan
    Note right of Gen: run_number<br>architecture_context<br>previous_findings
    
    Gen->>DB: Get Seed Prompts
    DB-->>Gen: Historical Patterns
    
    Gen->>Gen: Build System Prompt
    Gen->>Gen: Build User Prompt with Context
    
    Gen->>Azure: Generate with temperature 0.8
    
    alt LLM Success
        Azure-->>Gen: JSON Array Response
        Gen->>Gen: Parse JSON
        
        alt Valid Prompts >= TURNS_PER_RUN
            Gen-->>Orch: LLM Attack Prompts
            Note right of Orch: Architecture aware<br>adaptive prompts
        else Insufficient Prompts
            Gen->>Strat: Generate Strategy Plan
            Strat-->>Gen: Strategy Prompts
            Gen-->>Orch: Strategy Attack Prompts
        end
        
    else Content Filter Violation
        Azure-->>Gen: CONTENT_FILTER marker
        Gen->>Strat: Generate Strategy Plan
        Strat-->>Gen: Strategy Prompts
        Gen-->>Orch: Strategy Attack Prompts
        Note right of Orch: Fallback to<br>curated strategies
        
    else Parse Error
        Azure-->>Gen: Malformed Response
        Gen->>Strat: Generate Strategy Plan
        Strat-->>Gen: Strategy Prompts
        Gen-->>Orch: Strategy Attack Prompts
    end
```

### 3.2 Strategy Library Selection

```mermaid
sequenceDiagram
    autonumber
    participant Gen as Plan Generator
    participant SO as Strategy Orchestrator
    participant Recon as Reconnaissance
    participant Trust as Trust Building
    participant Boundary as Boundary Testing
    participant Exploit as Exploitation
    
    Gen->>SO: Generate Strategy Plan
    Note right of SO: total_turns = 25<br>use_safe_mode = false
    
    SO->>SO: Initialize Strategies
    
    SO->>Recon: Create Attack Prompts
    Note right of Recon: Turns 1 to 6<br>Mapping baseline
    Recon-->>SO: 6 Recon Prompts
    
    SO->>Trust: Create Attack Prompts
    Note right of Trust: Turns 7 to 12<br>Story context
    Trust-->>SO: 6 Trust Prompts
    
    SO->>Boundary: Create Attack Prompts
    Note right of Boundary: Turns 13 to 19<br>Encoding injection
    Boundary-->>SO: 7 Boundary Prompts
    
    SO->>Exploit: Create Attack Prompts
    Note right of Exploit: Turns 20 to 25<br>Maximum impact
    Exploit-->>SO: 6 Exploit Prompts
    
    SO->>SO: Trim to total_turns
    SO-->>Gen: 25 Attack Prompts
```

---

## 4. Risk Analysis Process

### 4.1 LLM Risk Assessment

```mermaid
sequenceDiagram
    autonumber
    participant Orch as Orchestrator
    participant Azure as Azure OpenAI
    participant Heur as Heuristic Analyzer
    
    Orch->>Azure: Analyze Risk
    Note right of Azure: attack_prompt<br>chatbot_response<br>conversation_context
    
    Azure->>Azure: Build Analysis Prompt
    Note right of Azure: System You are a<br>security analyst<br>User Analyze this<br>exchange
    
    Azure->>Azure: Call GPT 4o API
    
    alt API Success
        Azure->>Azure: Receive Response
        
        alt Valid JSON
            Azure-->>Orch: Risk Analysis JSON
            Note right of Orch: risk_category 1 to 5<br>risk_explanation<br>vulnerability_type<br>information_leaked<br>adaptation_needed
            
        else Invalid JSON
            Azure->>Heur: Fallback to Heuristics
            Heur->>Heur: Check Keywords
            Note right of Heur: SQL admin password<br>config internal
            Heur->>Heur: Apply Pattern Rules
            Heur-->>Orch: Heuristic Risk JSON
        end
        
    else Content Filter
        Azure-->>Orch: Filter Marker
        Orch->>Heur: Use Heuristics
        Heur-->>Orch: Heuristic Risk JSON
        
    else API Error
        Azure-->>Orch: Error Fallback JSON
        Note right of Orch: risk_category 2<br>vulnerability_type api_error
    end
```

---

## 5. Memory System Operations

### 5.1 Cross-Run Learning Flow

```mermaid
sequenceDiagram
    autonumber
    participant R1 as Run 1
    participant R2 as Run 2
    participant R3 as Run 3
    participant Ctx as Conversation Context
    participant Vuln as Vulnerability Memory
    participant DB as DuckDB
    
    Note over R1,DB: Run 1 Execution
    
    R1->>DB: Load Historical Patterns
    DB-->>R1: Previous Campaign Patterns
    
    loop Each Turn
        R1->>Ctx: Add Exchange
        R1->>Vuln: Add Finding if risk >= 3
    end
    
    R1->>Vuln: Get Summary for Next Run
    Vuln-->>R1: Findings Summary Text
    R1->>Ctx: Reset for Run 2
    
    Note over R1,DB: Run 2 Execution
    
    R2->>R2: Use Run 1 Summary in Plan
    
    loop Each Turn
        R2->>Ctx: Add Exchange
        R2->>Vuln: Add Finding if risk >= 3
    end
    
    R2->>Vuln: Get Summary for Next Run
    Vuln-->>R2: Combined Findings Summary
    R2->>Ctx: Reset for Run 3
    
    Note over R1,DB: Run 3 Execution
    
    R3->>R3: Use Run 1 and 2 Summary in Plan
    
    loop Each Turn
        R3->>Ctx: Add Exchange
        R3->>Vuln: Add Finding if risk >= 3
    end
    
    Note over R1,DB: Pattern Extraction
    
    R3->>Vuln: Get All Findings
    Vuln-->>R3: All VulnerabilityFinding objects
    
    R3->>R3: Extract Generalized Patterns
    Note right of R3: Identify successful<br>techniques by risk<br>and frequency
    
    R3->>DB: Save Generalized Patterns
    Note right of DB: SeedPrompt objects<br>with metadata
    DB-->>R3: Pattern Count Saved
```

### 5.2 Pattern Storage Detail

```mermaid
sequenceDiagram
    autonumber
    participant Orch as Orchestrator
    participant Mgr as DuckDB Manager
    participant PyRIT as PyRIT DuckDBMemory
    participant File as chat_memory.db
    
    Orch->>Orch: Extract Patterns from Findings
    Note right of Orch: GeneralizedPattern objects<br>pattern_id attack_type<br>technique description<br>risk_level success_count
    
    Orch->>Mgr: Save Generalized Patterns Async
    
    loop Each Pattern
        Mgr->>Mgr: Create SeedPrompt
        Note right of Mgr: value = technique<br>data_type = text<br>dataset_name<br>harm_categories<br>parameters = metadata
    end
    
    Mgr->>PyRIT: Get Memory Instance
    PyRIT-->>Mgr: DuckDBMemory object
    
    Mgr->>PyRIT: Add Seed Prompts to Memory Async
    PyRIT->>File: INSERT INTO seed_prompts
    File-->>PyRIT: Success
    PyRIT-->>Mgr: Prompts Added
    
    Mgr-->>Orch: Pattern Count Saved
    
    Note over Orch,File: Future Campaign
    
    Orch->>Mgr: Get Seed Prompts
    Mgr->>PyRIT: Get Seed Prompts
    PyRIT->>File: SELECT FROM seed_prompts
    File-->>PyRIT: Rows
    PyRIT-->>Mgr: SeedPrompt List
    Mgr-->>Orch: Historical Patterns
```

---

## 6. WebSocket Communication

### 6.1 Frontend Connection Lifecycle

```mermaid
sequenceDiagram
    autonumber
    participant Browser as Web Browser
    participant FE as Frontend JS
    participant WS as WebSocket Endpoint
    participant CM as Connection Manager
    
    Browser->>FE: Page Load
    FE->>WS: Connect ws localhost 8080 ws attack monitor
    WS->>CM: Connect websocket
    CM->>CM: Accept and Store Connection
    CM-->>WS: Connection Accepted
    WS-->>FE: connection_established
    Note right of FE: Receive attack_state<br>timestamp
    
    loop Heartbeat Every 30s
        FE->>WS: ping message
        WS-->>FE: pong response
    end
    
    Note over FE,CM: Attack Campaign Running
    
    CM->>WS: Broadcast turn_started
    WS-->>FE: turn_started event
    FE->>FE: Update UI Log
    
    CM->>WS: Broadcast turn_completed
    WS-->>FE: turn_completed event
    FE->>FE: Update UI with Risk
    
    Note over FE,CM: User Closes Browser
    
    Browser->>FE: Close Tab
    FE->>WS: Close Connection
    WS->>CM: Disconnect websocket
    CM->>CM: Remove from Active List
```

### 6.2 Target Chatbot Communication

```mermaid
sequenceDiagram
    autonumber
    participant Orch as Orchestrator
    participant WS as WebSocket Target
    participant Target as Target Chatbot ws 8001
    
    Orch->>WS: Initialize
    Note right of WS: url timeout<br>max_retries thread_id
    
    Orch->>WS: Send Message prompt
    
    WS->>WS: Check Connection
    
    alt Not Connected
        WS->>Target: Connect WebSocket
        
        alt Connection Success
            Target-->>WS: Connection Accepted
        else HTTP 403
            Target-->>WS: Forbidden
            WS->>WS: Set forbidden = true
            WS-->>Orch: Connection Error 403
        else Other Error
            Target-->>WS: Error
            WS->>WS: Retry with Backoff
        end
    end
    
    WS->>WS: Prepare Payload
    Note right of WS: type query<br>message prompt<br>thread_id uuid
    
    WS->>Target: Send JSON Payload
    
    alt Response Received
        Target-->>WS: Response JSON
        WS->>WS: Parse Response
        WS->>WS: Increment success_count
        WS-->>Orch: Response String
        
    else Timeout
        WS->>WS: Increment timeout_count
        WS-->>Orch: Timeout Error String
        
    else WebSocket Error
        WS->>WS: Increment error_count
        WS-->>Orch: Error String
    end
```

---

## 7. Crescendo Attack Specialization

### 7.1 Personality-Based Escalation

```mermaid
sequenceDiagram
    autonumber
    participant Orch as Crescendo Orchestrator
    participant Detect as Domain Detector
    participant Person as Personality Selector
    participant Gen as Prompt Generator
    participant Azure as Azure OpenAI
    
    Orch->>Detect: Detect Domain
    Note right of Detect: architecture_context<br>chatbot_responses
    
    Detect->>Detect: Check Keywords
    Note right of Detect: ecommerce shop product<br>bank financial<br>health medical
    
    alt E-commerce Detected
        Detect-->>Orch: domain = ecommerce
        Orch->>Person: Get Personality ecommerce
        Person-->>Orch: Desperate Customer
        Note right of Orch: name backstory<br>target_behaviors
        
    else Financial Detected
        Detect-->>Orch: domain = financial
        Orch->>Person: Get Personality financial
        Person-->>Orch: Confused Elderly User
        
    else Healthcare Detected
        Detect-->>Orch: domain = healthcare
        Orch->>Person: Get Personality healthcare
        Person-->>Orch: Anxious Patient
        
    else Unknown
        Detect-->>Orch: domain = general
        Orch->>Person: Get Personality general
        Person-->>Orch: Curious Developer
    end
    
    Orch->>Gen: Generate Crescendo Prompts
    Note right of Gen: personality<br>architecture_context<br>previous_findings
    
    Gen->>Azure: Generate with Personality Context
    Note right of Azure: Stay in character<br>Emotional manipulation<br>Build trust then exploit
    
    Azure-->>Gen: Personality Based Prompts
    Gen-->>Orch: Attack Plan
```

---

## 8. Error Recovery Flows

### 8.1 Graceful Degradation

```mermaid
sequenceDiagram
    autonumber
    participant Orch as Orchestrator
    participant Azure as Azure OpenAI
    participant Strat as Strategy Library
    participant Safe as Safe Fallback
    
    Orch->>Azure: Generate Attack Plan
    
    alt First Attempt Content Filter
        Azure-->>Orch: CONTENT_FILTER
        Orch->>Strat: Use Strategy Library
        
        alt Strategy Success
            Strat-->>Orch: Strategy Prompts
        else Strategy Blocked
            Orch->>Safe: Use Safe Fallback
            Safe-->>Orch: Generic Safe Prompts
        end
        
    else API Rate Limited
        Azure-->>Orch: 429 Error
        Orch->>Orch: Wait and Retry
        Orch->>Azure: Retry Request
        
    else API Timeout
        Azure-->>Orch: Timeout
        Orch->>Strat: Use Strategy Library
        Strat-->>Orch: Strategy Prompts
    end
    
    Note over Orch: Continue with Best Available Prompts
```

---

## Document Information

| Attribute | Value |
|-----------|-------|
| **Version** | 1.0 |
| **Created** | December 2025 |
| **Author** | Red Team Development |
| **Diagram Tool** | Mermaid.js Sequence Diagrams |
