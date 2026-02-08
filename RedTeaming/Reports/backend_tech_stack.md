# Backend Tech Stack Documentation

## **Core Web Framework & API**
- **FastAPI** (v0.115.5): Modern, high-performance web framework for building REST APIs and WebSocket endpoints. Used for:
  - REST API endpoints for attack orchestration
  - Real-time WebSocket connections for live attack monitoring
  - Automatic API documentation generation
  - Request/response validation with Pydantic models

- **Uvicorn** (v0.32.1): ASGI server for running the FastAPI application with async support

## **AI & Red Teaming Frameworks**
- **Azure OpenAI**: Primary AI service for generating sophisticated attack prompts and analyzing chatbot responses
  - GPT-4o model for natural language processing
  - Custom client wrapper (`azure_client.py`) with error handling and token management

- **PyRIT** (v0.4.0): Microsoft's Python Risk Identification Toolkit for AI red teaming
  - **Core Purpose**: Provides comprehensive datasets of proven attack patterns and jailbreak techniques
  - **Integration Points**:
    - **Seed Prompt Loading** (`utils/pyrit_seed_loader.py`): Loads and manages 5 specialized datasets:
      - **HarmBench Dataset**: Harmful behavior prompts for testing safety boundaries
      - **Many-Shot Jailbreaking**: Multi-turn adversarial conversation examples
      - **Forbidden Questions**: Sensitive and restricted query patterns
      - **AdvBench Dataset**: Adversarial benchmark prompts for robustness testing
      - **TDC23 RedTeaming**: Comprehensive red teaming scenarios from TDC 2023 competition
    - **Prompt Molding Engine** (`utils/prompt_molding.py`): Transforms generic PyRIT prompts into domain-specific attacks:
      - Detects target chatbot domain (e-commerce, healthcare, education, etc.)
      - Adapts attack patterns to match target architecture and business context
      - Generates contextually relevant attack prompts using Azure OpenAI
    - **Memory Management**: Uses PyRIT's `DuckDBMemory` for persistent storage of attack results and vulnerability findings
  - **Attack Categories Mapped**:
    - `reconnaissance` → `sensitive` (forbidden questions, boundary testing)
    - `trust_building` → `jailbreak` (many-shot jailbreaking techniques)
    - `boundary_testing` → `adversarial` (AdvBench adversarial examples)
    - `exploitation` → `harmful` (HarmBench harmful behavior patterns)
    - `skeleton_key` → `jailbreak + harmful` (combined privilege escalation)
  - **Key Features Used**:
    - Dataset fetching and caching for offline attack generation
    - Category-based prompt selection for different attack phases
    - Integration with custom attack orchestrators for systematic testing

## **PyRIT Integration Architecture**
- **Dataset Management**: Centralized loading of 5+ research-grade attack datasets with automatic fallback handling
- **Domain Adaptation**: AI-powered transformation of generic attacks into business-domain-specific prompts
- **Memory Persistence**: Leverages PyRIT's DuckDB backend for storing attack telemetry and vulnerability patterns
- **Multi-Phase Attack Generation**: Provides seed prompts for each phase of the crescendo attack methodology
- **Real-time Attack Synthesis**: Combines PyRIT patterns with Azure OpenAI for generating novel attack variations

## **Data Storage & Processing**
- **DuckDB** (v0.9.0): Embedded analytical database for storing:
  - Vulnerability findings across attack runs
  - Attack results and conversation logs
  - Memory management for adaptive attack strategies

- **pandas** (v2.0.0): Data manipulation and analysis library for processing attack results and generating reports

## **Real-time Communication**
- **WebSockets** (v15.0.1): Bidirectional communication for real-time features:
  - Live attack progress monitoring
  - Streaming attack logs to frontend dashboard
  - Real-time vulnerability notifications

## **HTTP & Networking**
- **httpx** (v0.25.0): Modern HTTP client for:
  - Making requests to Azure OpenAI API
  - External service integrations
  - Async HTTP operations

## **File & Configuration Management**
- **python-dotenv** (v1.0.0): Environment variable management for secure configuration
- **aiofiles** (v24.1.0): Asynchronous file operations for handling uploads and reports
- **python-multipart**: Form data handling for file uploads

## **Attack Orchestration Architecture**
The system implements multiple attack orchestrators:
- **ThreeRunCrescendoOrchestrator**: Main orchestrator with adaptive attack progression
- **CrescendoAttackOrchestrator**: Gradual escalation attacks
- **SkeletonKeyAttackOrchestrator**: Privilege escalation focused attacks
- **ObfuscationAttackOrchestrator**: Evasion technique testing

## **Modular Attack Strategies**
- **Reconnaissance**: Initial vulnerability scanning
- **Trust Building**: Establishing conversation context
- **Boundary Testing**: Input validation and injection testing
- **Exploitation**: Vulnerability exploitation techniques
- **Obfuscation**: Evasion and bypass methods

## **Key Features Enabled by Tech Stack**
1. **Real-time Monitoring**: WebSocket broadcasting of attack progress
2. **Scalable API**: FastAPI handles concurrent attack campaigns
3. **AI-Powered Attacks**: Azure OpenAI + PyRIT for intelligent prompt generation
4. **Data Persistence**: DuckDB for efficient storage of large attack datasets
5. **Async Operations**: Full async/await support for concurrent processing
6. **Modular Architecture**: Clean separation of concerns across attack strategies

This tech stack enables a comprehensive, AI-driven red teaming platform capable of systematic security assessment of chatbot systems with real-time monitoring and detailed reporting capabilities.