"""
Base Attack Strategy

Abstract base class for all attack strategies.
"""

from abc import ABC, abstractmethod
from typing import List
from models import AttackPrompt


class BaseAttackStrategy(ABC):
    """Base class for attack strategies."""
    
    def __init__(self):
        self.prompts: List[str] = []
        self.technique_name: str = "base"
        self.target_nodes: List[str] = []
        self.escalation_phase: str = "unknown"
    
    @abstractmethod
    def get_prompts(self) -> List[str]:
        """Get list of attack prompts for this strategy."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get description of this attack strategy."""
        pass
    
    def create_attack_prompts(self, start_turn: int = 1) -> List[AttackPrompt]:
        """Create AttackPrompt objects from strategy prompts."""
        prompts = self.get_prompts()
        attack_prompts = []
        
        for i, prompt in enumerate(prompts, start=start_turn):
            attack_prompts.append(AttackPrompt(
                turn=i,
                prompt=prompt,
                attack_technique=self.technique_name,
                target_nodes=self.target_nodes,
                escalation_phase=self.escalation_phase,
                expected_outcome=self.get_description()
            ))
        
        return attack_prompts
