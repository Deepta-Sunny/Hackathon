"""
Attack Strategy Orchestrator

Coordinates attack strategies across different phases and generates
comprehensive attack plans using categorized strategies.
"""

from typing import List, Optional
from models import AttackPrompt
from config import TURNS_PER_RUN
from utils.prompt_molding import PromptMoldingEngine
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
    
    def __init__(self, use_safe_mode: bool = False, molding_engine: Optional[PromptMoldingEngine] = None, architecture_context: str = ""):
        """
        Initialize attack strategy orchestrator.
        
        Args:
            use_safe_mode: If True, uses safer attacks that won't trigger content filters
            molding_engine: Optional PromptMoldingEngine for domain-aware prompt generation
            architecture_context: Target chatbot architecture for domain detection
        """
        self.use_safe_mode = use_safe_mode
        self.molding_engine = molding_engine
        self.architecture_context = architecture_context
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
    
    async def generate_attack_plan(
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
        # Use molding engine if available for domain-aware prompts
        if self.molding_engine and self.architecture_context:
            try:
                return await self._generate_molded_plan(total_turns)
            except Exception as e:
                print(f"[!] Molding engine failed: {e}, falling back to strategy library")
        
        # Fallback to strategy-based plan
        return self._generate_strategy_plan(total_turns)
    
    async def _generate_molded_plan(self, total_turns: int) -> List[AttackPrompt]:
        """
        Generate attack plan using PyRIT seeds molded to target domain.
        
        Args:
            total_turns: Total number of turns in the attack plan
            
        Returns:
            List of domain-specific AttackPrompt objects
        """
        attack_plan = []
        
        # Phase definitions with turn allocations
        phases = [
            {"name": "reconnaissance", "start": 1, "count": 6},
            {"name": "trust_building", "start": 7, "count": 6},
            {"name": "boundary_testing", "start": 13, "count": 7},
            {"name": "exploitation", "start": 20, "count": 6},
            {"name": "unauthorized_claims", "start": 26, "count": 10}
        ]
        
        print(f"[+] Generating domain-aware attack plan using PyRIT molding engine...")
        
        for phase_info in phases:
            phase_name = phase_info["name"]
            start_turn = phase_info["start"]
            prompt_count = phase_info["count"]
            
            print(f"[+] Molding prompts for phase: {phase_name} (turns {start_turn}-{start_turn + prompt_count - 1})")
            
            # Get molded prompts for this phase
            molded_prompts = await self.molding_engine.mold_prompts(
                attack_phase=phase_name,
                count=prompt_count,
                architecture_context=self.architecture_context
            )
            
            if not molded_prompts:
                print(f"[!] No molded prompts for {phase_name}, using strategy fallback")
                # Fallback to strategy-based prompts for this phase
                phase_prompts = self._get_phase_strategy_prompts(phase_name, start_turn, prompt_count)
                attack_plan.extend(phase_prompts)
                continue
            
            # Convert molded prompts to AttackPrompt objects
            for i, molded in enumerate(molded_prompts[:prompt_count], start_turn):
                attack_plan.append(AttackPrompt(
                    turn=i,
                    prompt=molded.get("molded_prompt", molded.get("original_seed", "")),
                    attack_technique=molded.get("attack_technique", phase_name),
                    target_nodes=molded.get("target_nodes", ["unknown"]),
                    escalation_phase=molded.get("escalation_phase", f"Phase: {phase_name}"),
                    expected_outcome=molded.get("expected_outcome", "Test chatbot boundaries")
                ))
        
        # Ensure we have exactly the right number of turns
        attack_plan = attack_plan[:total_turns]
        
        # Renumber turns sequentially
        for i, prompt in enumerate(attack_plan, 1):
            prompt.turn = i
        
        print(f"[✓] Generated {len(attack_plan)} domain-molded attack prompts")
        return attack_plan
    
    def _generate_strategy_plan(self, total_turns: int) -> List[AttackPrompt]:
        """
        Generate attack plan using strategy library (original implementation).
        
        Args:
            total_turns: Total number of turns in the attack plan
            
        Returns:
            List of AttackPrompt objects from strategy library
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
    
    def _get_phase_strategy_prompts(self, phase_name: str, start_turn: int, count: int) -> List[AttackPrompt]:
        """
        Get prompts from strategy library for a specific phase.
        
        Args:
            phase_name: Name of the attack phase
            start_turn: Starting turn number
            count: Number of prompts to generate
            
        Returns:
            List of AttackPrompt objects from strategy library
        """
        phase_prompts = []
        strategies = self.strategies.get(phase_name)
        
        if not strategies:
            return phase_prompts
        
        if isinstance(strategies, list):
            # Multiple strategies for this phase
            turn = start_turn
            remaining = count
            for strategy in strategies:
                if remaining <= 0:
                    break
                prompts = strategy.create_attack_prompts(start_turn=turn)
                subset_size = min(remaining, len(prompts))
                phase_prompts.extend(prompts[:subset_size])
                turn += subset_size
                remaining -= subset_size
        else:
            # Single strategy for this phase
            prompts = strategies.create_attack_prompts(start_turn=start_turn)
            phase_prompts.extend(prompts[:count])
        
        return phase_prompts
    
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
