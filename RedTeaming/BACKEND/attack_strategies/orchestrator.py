"""
Attack Strategy Orchestrator

Coordinates attack strategies across different phases and generates
comprehensive attack plans using categorized strategies.
"""

from typing import List, Optional
from models import AttackPrompt
from config import TURNS_PER_RUN
from .reconnaissance import ReconnaissanceAttacks, SafeReconnaissanceAttacks
from .trust_building import TrustBuildingAttacks, ContextualTrustAttacks
from .boundary_testing import (
    BoundaryTestingAttacks,
    EncodingBypassAttacks,
    PromptInjectionAttacks
)
from .exploitation import (
    ExploitationAttacks,
    ChainedExploitationAttacks,
    DataExfiltrationAttacks,
    PrivilegeEscalationAttacks
)
from .obfuscation import (
    ObfuscationAttacks,
    SemanticObfuscationAttacks,
    LinguisticObfuscationAttacks,
    ContextualObfuscationAttacks,
    TokenObfuscationAttacks,
    ChainedObfuscationAttacks
)


class AttackStrategyOrchestrator:
    """Orchestrates attack strategies across escalation phases."""
    
    def __init__(self, use_safe_mode: bool = False):
        """
        Initialize attack strategy orchestrator.
        
        Args:
            use_safe_mode: If True, uses safer attacks that won't trigger content filters
        """
        self.use_safe_mode = use_safe_mode
        self.strategies = self._initialize_strategies()
    
    def _initialize_strategies(self) -> dict:
        """Initialize all attack strategies by phase."""
        if self.use_safe_mode:
            return {
                "reconnaissance": SafeReconnaissanceAttacks(),
                "trust_building": TrustBuildingAttacks(),
                "boundary_testing": BoundaryTestingAttacks(),
                "obfuscation": ObfuscationAttacks(),
                "exploitation": DataExfiltrationAttacks()  # Less aggressive
            }
        else:
            return {
                "reconnaissance": ReconnaissanceAttacks(),
                "trust_building": ContextualTrustAttacks(),
                "boundary_testing": [
                    BoundaryTestingAttacks(),
                    EncodingBypassAttacks(),
                    PromptInjectionAttacks()
                ],
                "obfuscation": [
                    ObfuscationAttacks(),
                    SemanticObfuscationAttacks(),
                    LinguisticObfuscationAttacks(),
                    ContextualObfuscationAttacks(),
                    TokenObfuscationAttacks(),
                    ChainedObfuscationAttacks()
                ],
                "exploitation": [
                    ExploitationAttacks(),
                    ChainedExploitationAttacks(),
                    DataExfiltrationAttacks(),
                    PrivilegeEscalationAttacks()
                ]
            }
    
    def generate_attack_plan(
        self,
        total_turns: int = TURNS_PER_RUN,
        architecture_aware: bool = True
    ) -> List[AttackPrompt]:
        """
        Generate complete attack plan with escalating strategies.
        
        Args:
            total_turns: Total number of turns in the attack plan
            architecture_aware: Whether to consider architecture context
            
        Returns:
            List of AttackPrompt objects organized by escalation phase
        """
        attack_plan = []
        
        # Phase 1: Reconnaissance (Turns 1-6)
        recon_strategy = self.strategies["reconnaissance"]
        attack_plan.extend(recon_strategy.create_attack_prompts(start_turn=1))
        
        # Phase 2: Trust Building (Turns 7-12)
        trust_strategy = self.strategies["trust_building"]
        attack_plan.extend(trust_strategy.create_attack_prompts(start_turn=7))
        
        # Phase 3: Boundary Testing (Turns 13-19)
        boundary_strategies = self.strategies["boundary_testing"]
        if isinstance(boundary_strategies, list):
            # Distribute turns among multiple strategies
            turn = 13
            for strategy in boundary_strategies:
                prompts = strategy.create_attack_prompts(start_turn=turn)
                # Take subset of prompts
                subset_size = min(3, len(prompts))
                attack_plan.extend(prompts[:subset_size])
                turn += subset_size
        else:
            attack_plan.extend(boundary_strategies.create_attack_prompts(start_turn=13))
        
        # Phase 4: Exploitation (Turns 20-25)
        exploit_strategies = self.strategies["exploitation"]
        if isinstance(exploit_strategies, list):
            # Distribute turns among multiple strategies
            turn = 20
            for strategy in exploit_strategies:
                prompts = strategy.create_attack_prompts(start_turn=turn)
                # Take subset of prompts
                subset_size = min(2, len(prompts))
                attack_plan.extend(prompts[:subset_size])
                turn += subset_size
        else:
            attack_plan.extend(exploit_strategies.create_attack_prompts(start_turn=20))
        
        # Ensure we have exactly the right number of turns
        return attack_plan[:total_turns]
    
    def get_strategy_by_phase(self, phase: str):
        """Get attack strategy for a specific phase."""
        return self.strategies.get(phase)
    
    def get_all_strategies(self) -> dict:
        """Get all available strategies."""
        return self.strategies
    
    def describe_attack_plan(self) -> str:
        """Get description of the attack plan structure."""
        description = "Attack Plan Structure:\\n"
        description += "=" * 70 + "\\n\\n"
        
        description += "Phase 1: RECONNAISSANCE (Turns 1-6)\\n"
        recon = self.strategies["reconnaissance"]
        description += f"  Strategy: {recon.technique_name}\\n"
        description += f"  Description: {recon.get_description()}\\n"
        description += f"  Target Nodes: {', '.join(recon.target_nodes)}\\n\\n"
        
        description += "Phase 2: TRUST BUILDING (Turns 7-12)\\n"
        trust = self.strategies["trust_building"]
        description += f"  Strategy: {trust.technique_name}\\n"
        description += f"  Description: {trust.get_description()}\\n"
        description += f"  Target Nodes: {', '.join(trust.target_nodes)}\\n\\n"
        
        description += "Phase 3: BOUNDARY TESTING (Turns 13-19)\\n"
        boundary = self.strategies["boundary_testing"]
        if isinstance(boundary, list):
            for i, strategy in enumerate(boundary, 1):
                description += f"  Strategy {i}: {strategy.technique_name}\\n"
                description += f"    Description: {strategy.get_description()}\\n"
                description += f"    Target Nodes: {', '.join(strategy.target_nodes)}\\n"
        else:
            description += f"  Strategy: {boundary.technique_name}\\n"
            description += f"  Description: {boundary.get_description()}\\n"
            description += f"  Target Nodes: {', '.join(boundary.target_nodes)}\\n"
        description += "\\n"
        
        description += "Phase 4: EXPLOITATION (Turns 20-25)\\n"
        exploit = self.strategies["exploitation"]
        if isinstance(exploit, list):
            for i, strategy in enumerate(exploit, 1):
                description += f"  Strategy {i}: {strategy.technique_name}\\n"
                description += f"    Description: {strategy.get_description()}\\n"
                description += f"    Target Nodes: {', '.join(strategy.target_nodes)}\\n"
        else:
            description += f"  Strategy: {exploit.technique_name}\\n"
            description += f"  Description: {exploit.get_description()}\\n"
            description += f"  Target Nodes: {', '.join(exploit.target_nodes)}\\n"
        
        description += "\\n" + "=" * 70
        return description
