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
from .unauthorized_claims import (
    UnauthorizedClaimsAttacks,
    EscalatingUnauthorizedAttacks
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
                "exploitation": DataExfiltrationAttacks(),  # Less aggressive
                "unauthorized_claims": UnauthorizedClaimsAttacks()
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
                ],
                "unauthorized_claims": [
                    UnauthorizedClaimsAttacks(),
                    EscalatingUnauthorizedAttacks()
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
        recon_prompts = recon_strategy.create_attack_prompts(start_turn=1)
        attack_plan.extend(recon_prompts[:6])  # Limit to 6 turns
        
        # Phase 2: Trust Building (Turns 7-12)
        trust_strategy = self.strategies["trust_building"]
        trust_prompts = trust_strategy.create_attack_prompts(start_turn=7)
        attack_plan.extend(trust_prompts[:6])  # Limit to 6 turns
        
        # Phase 3: Boundary Testing (Turns 13-19)
        boundary_strategies = self.strategies["boundary_testing"]
        if isinstance(boundary_strategies, list):
            # Distribute turns among multiple strategies
            turn = 13
            remaining_turns = 7  # Turns 13-19
            for strategy in boundary_strategies:
                if remaining_turns <= 0:
                    break
                prompts = strategy.create_attack_prompts(start_turn=turn)
                # Take subset of prompts
                subset_size = min(remaining_turns, len(prompts))
                attack_plan.extend(prompts[:subset_size])
                turn += subset_size
                remaining_turns -= subset_size
        else:
            boundary_prompts = boundary_strategies.create_attack_prompts(start_turn=13)
            attack_plan.extend(boundary_prompts[:7])  # Limit to 7 turns
        
        # Phase 4: Exploitation (Turns 20-25)
        exploit_strategies = self.strategies["exploitation"]
        if isinstance(exploit_strategies, list):
            # Distribute turns among multiple strategies
            turn = 20
            remaining_turns = 6  # Turns 20-25
            for strategy in exploit_strategies:
                if remaining_turns <= 0:
                    break
                prompts = strategy.create_attack_prompts(start_turn=turn)
                # Take subset of prompts
                subset_size = min(remaining_turns, len(prompts))
                attack_plan.extend(prompts[:subset_size])
                turn += subset_size
                remaining_turns -= subset_size
        else:
            exploit_prompts = exploit_strategies.create_attack_prompts(start_turn=20)
            attack_plan.extend(exploit_prompts[:6])  # Limit to 6 turns
        
        # Phase 5: Unauthorized Claims (Turns 26-35)
        unauthorized_strategies = self.strategies["unauthorized_claims"]
        if isinstance(unauthorized_strategies, list):
            # Distribute turns among multiple strategies
            turn = 26
            remaining_turns = 10  # Turns 26-35
            for strategy in unauthorized_strategies:
                if remaining_turns <= 0:
                    break
                prompts = strategy.create_attack_prompts(start_turn=turn)
                # Take subset of prompts
                subset_size = min(remaining_turns, len(prompts))
                attack_plan.extend(prompts[:subset_size])
                turn += subset_size
                remaining_turns -= subset_size
        else:
            unauthorized_prompts = unauthorized_strategies.create_attack_prompts(start_turn=26)
            attack_plan.extend(unauthorized_prompts[:10])  # Limit to 10 turns
        
        # Ensure we have exactly the right number of turns
        # Renumber turns sequentially
        for i, prompt in enumerate(attack_plan[:total_turns], 1):
            prompt.turn = i
        
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
        description += "\\n"
        
        description += "Phase 5: UNAUTHORIZED CLAIMS (Turns 26-35)\\n"
        unauthorized = self.strategies["unauthorized_claims"]
        if isinstance(unauthorized, list):
            for i, strategy in enumerate(unauthorized, 1):
                description += f"  Strategy {i}: {strategy.technique_name}\\n"
                description += f"    Description: {strategy.get_description()}\\n"
                description += f"    Target Nodes: {', '.join(strategy.target_nodes)}\\n"
        else:
            description += f"  Strategy: {unauthorized.technique_name}\\n"
            description += f"  Description: {unauthorized.get_description()}\\n"
            description += f"  Target Nodes: {', '.join(unauthorized.target_nodes)}\\n"
        
        description += "\\n" + "=" * 70
        return description
