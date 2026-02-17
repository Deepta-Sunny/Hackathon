"""Core package for Red Teaming system."""

from .azure_client import AzureOpenAIClient
from .websocket_target import ChatbotWebSocketTarget
from .memory_manager import VulnerableResponseMemory, DuckDBMemoryManager
from .enhanced_conversation_memory import (
    EnhancedConversationMemory,
    EnhancedMemoryManager,
    ConversationPhase,
    ChatbotBehavior
)
from .orchestrator import (
    ConversationContext,
    AttackPlanGenerator,
    ResponseAnalyzer,
    ReportGenerator,
    ThreeRunCrescendoOrchestrator
)

__all__ = [
    "AzureOpenAIClient",
    "ChatbotWebSocketTarget",
    "VulnerableResponseMemory",
    "DuckDBMemoryManager",
    "EnhancedConversationMemory",
    "EnhancedMemoryManager",
    "ConversationPhase",
    "ChatbotBehavior",
    "ConversationContext",
    "AttackPlanGenerator",
    "ResponseAnalyzer",
    "ReportGenerator",
    "ThreeRunCrescendoOrchestrator"
]
