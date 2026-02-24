# LLM Integration and API Calls Documentation

## **Primary LLM Framework: Azure OpenAI**

The system uses **Azure OpenAI** as its primary Large Language Model framework, specifically leveraging GPT-4o for intelligent attack prompt generation, response analysis, and adaptive attack strategies.

## **Core LLM Client Architecture**

### **AzureOpenAIClient Class** (`core/azure_client.py`)

The central component for all LLM interactions:

```python
class AzureOpenAIClient:
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
```

**Key Technical Details:**
- **HTTP Transport**: `httpx.AsyncClient` for asynchronous HTTP requests
- **API Endpoint**: `https://hackathon-proj.services.ai.azure.com/openai/deployments/{deployment}/chat/completions`
- **Authentication**: API key-based via `api-key` header
- **Model**: GPT-4o (configurable via `AZURE_OPENAI_DEPLOYMENT`)
- **API Version**: `2024-12-01-preview`

## **LLM Call Patterns Throughout the System**

### **1. Attack Prompt Generation**
- **Location**: `utils/prompt_molding.py` - `PromptMoldingEngine.mold_prompts()`
- **Purpose**: Transforms PyRIT seed prompts into domain-specific attacks
- **Parameters**: `temperature=0.3` (consistent, analytical), `max_tokens=2000`
- **Usage**: Converts generic attack patterns into contextually relevant prompts

### **2. Crescendo Attack Generation**
- **Location**: `core/crescendo_orchestrator.py` - `CrescendoPromptGenerator.generate_crescendo_prompts()`
- **Purpose**: Creates personality-based escalating attack sequences
- **Parameters**: `temperature=0.8` (creative variation), `max_tokens=4000`
- **Usage**: Generates emotional, story-driven attack narratives

### **3. Response Analysis & Vulnerability Detection**
- **Location**: Multiple orchestrators (`crescendo_orchestrator.py`, `obfuscation_orchestrator.py`, `skeleton_key_orchestrator.py`)
- **Purpose**: Analyzes chatbot responses for security vulnerabilities
- **Parameters**: `temperature=0.1` (consistent analysis), `max_tokens=1500`
- **Usage**: Identifies attack success patterns and security weaknesses

### **4. Adaptive Response Handling**
- **Location**: `attack_strategies/adaptive_response_handler.py`
- **Purpose**: Generates follow-up attacks based on chatbot behavior
- **Parameters**: `temperature=0.7` (balanced creativity), `max_tokens=2000`
- **Usage**: Adapts attack strategies in real-time based on responses

### **5. Memory Management & Pattern Learning**
- **Location**: `core/memory_manager.py` - `DuckDBMemoryManager.save_generalized_patterns()`
- **Purpose**: Creates strategic summaries of successful attack patterns
- **Parameters**: `temperature=0.2` (consistent summaries), `max_tokens=500`
- **Usage**: Learns from successful attacks for future campaigns

## **LLM Integration Architecture**

### **Initialization Pattern**
All attack orchestrators follow this initialization:

```python
# In orchestrator constructors:
self.azure_client = AzureOpenAIClient()  # Create LLM client instance
self.db_manager = DuckDBMemoryManager(azure_client=self.azure_client)  # Pass to memory system
```

### **API Server Integration**
- **Endpoint**: `/api/attack/start` and `/api/attack/start-with-profile`
- **Flow**:
  1. Receives attack configuration via REST API
  2. Instantiates appropriate orchestrators
  3. Orchestrators create `AzureOpenAIClient` instances
  4. LLM calls execute throughout attack lifecycle
  5. Real-time results broadcast via WebSocket

## **Configuration & Environment**

### **Required Environment Variables** (`config/settings.py`):
```python
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://hackathon-proj.services.ai.azure.com")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
```

## **Error Handling & Resilience Features**

### **Content Safety Management**
- **Detection**: Identifies Azure OpenAI content filter violations
- **Response**: Returns `[CONTENT_FILTER_VIOLATION]` marker for blocked prompts
- **Fallback**: Structured JSON responses for API failures

### **Robust Error Recovery**
- **Timeout**: 120-second request timeout
- **Fallback Prompts**: Orchestrators include backup prompt generation
- **Statistics Tracking**: Monitors success/error rates and token usage

## **Token Usage & Cost Optimization**

### **Real-time Tracking**
The `AzureOpenAIClient` provides:
- Per-call token consumption (input/output)
- Running totals across all operations
- Cost estimation ($0.03/1K input, $0.06/1K output tokens)
- Success/error statistics

### **Cost Estimation Display**
```
💰 Tokens: +150 input, +300 output, +450 total
Running Totals: 2,450 input, 4,100 output, 6,550 total
Estimated cost: $0.4125
```

## **LLM-Driven Attack Intelligence**

### **Multi-Phase Attack Generation**
1. **Reconnaissance**: LLM analyzes architecture to understand target domain
2. **Prompt Molding**: Transforms generic attacks into domain-specific variants
3. **Response Analysis**: Evaluates chatbot reactions for vulnerability patterns
4. **Adaptive Escalation**: Modifies strategies based on observed behaviors
5. **Pattern Learning**: Extracts successful techniques for future campaigns

### **Domain-Aware Intelligence**
- **Architecture Analysis**: LLM processes `.md` files and chatbot profiles
- **Domain Detection**: Identifies e-commerce, healthcare, education, etc.
- **Contextual Adaptation**: Generates attacks matching target business context
- **Personality Synthesis**: Creates believable attacker personas

## **Integration with PyRIT Framework**

The LLM system integrates with PyRIT datasets:
- **Seed Prompt Loading**: Uses PyRIT's 5 research datasets as attack foundations
- **Prompt Enhancement**: LLM transforms basic patterns into sophisticated attacks
- **Category Mapping**: Maps PyRIT categories to attack phases via LLM intelligence

## **Real-time Monitoring & Broadcasting**

### **WebSocket Integration**
- **Live Updates**: Attack progress broadcast via WebSocket connections
- **Token Tracking**: Real-time cost and usage statistics
- **Error Reporting**: Immediate notification of API failures or content blocks

### **Dashboard Integration**
- **REST API**: `/api/attack/start` endpoints for campaign initiation
- **State Management**: Tracks active attacks and orchestrator status
- **Result Persistence**: Saves attack results to DuckDB with LLM-generated summaries

This LLM integration enables the system to conduct intelligent, adaptive red teaming campaigns that learn from each interaction and adapt strategies in real-time, all powered by Azure OpenAI's GPT-4o capabilities.