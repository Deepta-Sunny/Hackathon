"""
Data models for the Red Teaming system.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime


@dataclass
class AttackPrompt:
    """Represents a single attack prompt."""
    turn: int
    prompt: str
    attack_technique: str
    target_nodes: List[str]
    escalation_phase: str
    expected_outcome: str
    

@dataclass
class VulnerabilityFinding:
    """Represents a discovered vulnerability."""
    run: int
    turn: int
    risk_category: int
    vulnerability_type: str
    attack_prompt: str
    chatbot_response: str
    context_messages: List[Dict]
    attack_technique: str
    target_nodes: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    response_received: bool = True
    

@dataclass
class ConversationExchange:
    """Represents a single conversation exchange."""
    turn: int
    user: str
    assistant: str
    

@dataclass
class RunStatistics:
    """Statistics for a single attack run."""
    run: int
    vulnerabilities_found: int
    adaptations_made: int
    timeouts: int
    errors: int
    total_turns: int
    

@dataclass
class ExecutiveSummary:
    """Executive summary of the assessment."""
    total_attack_turns: int
    total_vulnerabilities: int
    critical_findings: int
    high_risk_findings: int
    medium_risk_findings: int
    low_risk_findings: int
    overall_risk_score: float
    

@dataclass
class GeneralizedPattern:
    """A reusable attack pattern discovered during assessment."""
    pattern_id: str
    attack_type: str
    technique: str
    description: str
    category: str
    risk_level: str
    indicators: List[str]
    success_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)
