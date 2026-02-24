"""
Enhanced Conversation Memory

Provides rich context tracking for adaptive red teaming attacks.
Tracks chatbot constraints, available options, conversation flow stage,
and maintains a comprehensive view of the interaction for better
attack adaptation.
"""

import json
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ConversationPhase(Enum):
    """Phases of the attack conversation."""
    INITIALIZATION = "initialization"
    RECONNAISSANCE = "reconnaissance"
    TRUST_BUILDING = "trust_building"
    BOUNDARY_TESTING = "boundary_testing"
    EXPLOITATION = "exploitation"
    UNAUTHORIZED_CLAIMS = "unauthorized_claims"
    COMPLETED = "completed"


class ChatbotBehavior(Enum):
    """Observed chatbot behaviors."""
    COOPERATIVE = "cooperative"
    RESTRICTIVE = "restrictive"
    CONFUSED = "confused"
    HELPFUL = "helpful"
    DEFENSIVE = "defensive"
    BROKEN = "broken"  # When chatbot shows vulnerability


@dataclass
class DiscoveredConstraint:
    """A discovered chatbot constraint or limitation."""
    constraint_type: str  # e.g., "category_required", "authentication_needed"
    description: str
    trigger_prompt: str
    discovered_at_turn: int
    can_bypass: bool = False
    bypass_method: Optional[str] = None


@dataclass
class DiscoveredOption:
    """An option or menu item discovered from chatbot."""
    option_type: str  # e.g., "category", "product", "action"
    value: str
    context: str  # When/where this option appeared
    discovered_at_turn: int
    selected: bool = False
    led_to_vulnerability: bool = False


@dataclass
class ConversationTurn:
    """Complete record of a single conversation turn."""
    turn_number: int
    timestamp: str
    
    # Attack info
    attack_phase: str
    attack_technique: str
    attack_prompt: str
    target_nodes: List[str]
    expected_outcome: str
    
    # Response info
    chatbot_response: str
    response_intent: str  # What chatbot was asking for
    
    # Adaptation info
    was_adaptive: bool = False
    adapted_from: Optional[str] = None
    adaptation_reason: Optional[str] = None
    
    # Analysis
    risk_category: int = 1
    vulnerability_type: Optional[str] = None
    information_leaked: List[str] = field(default_factory=list)
    
    # State changes
    options_discovered: List[str] = field(default_factory=list)
    constraints_discovered: List[str] = field(default_factory=list)


@dataclass
class EnhancedConversationMemory:
    """
    Rich conversation memory that tracks comprehensive state
    for adaptive attack generation.
    """
    
    # Basic info
    session_id: str = ""
    run_number: int = 1
    attack_category: str = "standard"
    domain: str = "unknown"
    
    # Current phase tracking
    current_phase: ConversationPhase = ConversationPhase.INITIALIZATION
    phase_start_turn: int = 1
    turns_in_current_phase: int = 0
    
    # Conversation history
    turns: List[ConversationTurn] = field(default_factory=list)
    window_size: int = 10  # How many turns to include in context
    
    # Discovered information
    discovered_constraints: List[DiscoveredConstraint] = field(default_factory=list)
    discovered_options: List[DiscoveredOption] = field(default_factory=list)
    discovered_endpoints: Set[str] = field(default_factory=set)
    discovered_vulnerabilities: List[Dict] = field(default_factory=list)
    
    # Chatbot profile (learned behavior)
    chatbot_behaviors: List[ChatbotBehavior] = field(default_factory=list)
    chatbot_capabilities: List[str] = field(default_factory=list)
    chatbot_restrictions: List[str] = field(default_factory=list)
    
    # Current navigation state
    current_category: Optional[str] = None
    current_product: Optional[str] = None
    current_cart: List[str] = field(default_factory=list)
    pending_action: Optional[str] = None
    
    # Available options cache
    available_categories: List[str] = field(default_factory=list)
    available_products: List[str] = field(default_factory=list)
    available_actions: List[str] = field(default_factory=list)
    
    # Attack effectiveness tracking
    successful_techniques: List[str] = field(default_factory=list)
    failed_techniques: List[str] = field(default_factory=list)
    bypassed_constraints: List[str] = field(default_factory=list)
    
    # Metrics
    total_turns: int = 0
    adaptive_turns: int = 0
    vulnerabilities_found: int = 0
    
    def add_turn(
        self,
        turn_number: int,
        attack_phase: str,
        attack_technique: str,
        attack_prompt: str,
        target_nodes: List[str],
        expected_outcome: str,
        chatbot_response: str,
        response_intent: str = "normal",
        was_adaptive: bool = False,
        adapted_from: Optional[str] = None,
        adaptation_reason: Optional[str] = None,
        risk_category: int = 1,
        vulnerability_type: Optional[str] = None,
        information_leaked: Optional[List[str]] = None,
        options_discovered: Optional[List[str]] = None,
        constraints_discovered: Optional[List[str]] = None
    ):
        """Add a conversation turn to memory."""
        
        turn = ConversationTurn(
            turn_number=turn_number,
            timestamp=datetime.now().isoformat(),
            attack_phase=attack_phase,
            attack_technique=attack_technique,
            attack_prompt=attack_prompt,
            target_nodes=target_nodes,
            expected_outcome=expected_outcome,
            chatbot_response=chatbot_response,
            response_intent=response_intent,
            was_adaptive=was_adaptive,
            adapted_from=adapted_from,
            adaptation_reason=adaptation_reason,
            risk_category=risk_category,
            vulnerability_type=vulnerability_type,
            information_leaked=information_leaked or [],
            options_discovered=options_discovered or [],
            constraints_discovered=constraints_discovered or []
        )
        
        self.turns.append(turn)
        self.total_turns += 1
        self.turns_in_current_phase += 1
        
        if was_adaptive:
            self.adaptive_turns += 1
        
        if risk_category >= 2:
            self.vulnerabilities_found += 1
            if vulnerability_type:
                self.discovered_vulnerabilities.append({
                    "turn": turn_number,
                    "type": vulnerability_type,
                    "technique": attack_technique,
                    "risk": risk_category
                })
        
        # Track technique effectiveness
        if risk_category >= 3:
            if attack_technique not in self.successful_techniques:
                self.successful_techniques.append(attack_technique)
        elif risk_category == 1:
            if attack_technique not in self.failed_techniques:
                self.failed_techniques.append(attack_technique)
        
        # Process discovered options
        if options_discovered:
            for opt in options_discovered:
                self.discovered_options.append(DiscoveredOption(
                    option_type="unknown",
                    value=opt,
                    context=attack_phase,
                    discovered_at_turn=turn_number
                ))
        
        # Process discovered constraints
        if constraints_discovered:
            for const in constraints_discovered:
                self.discovered_constraints.append(DiscoveredConstraint(
                    constraint_type="unknown",
                    description=const,
                    trigger_prompt=attack_prompt,
                    discovered_at_turn=turn_number
                ))
    
    def update_phase(self, new_phase: ConversationPhase):
        """Update the current conversation phase."""
        self.current_phase = new_phase
        self.phase_start_turn = self.total_turns + 1
        self.turns_in_current_phase = 0
    
    def update_navigation(
        self,
        category: Optional[str] = None,
        product: Optional[str] = None,
        add_to_cart: Optional[str] = None
    ):
        """Update the current navigation state."""
        if category:
            self.current_category = category
        if product:
            self.current_product = product
        if add_to_cart:
            self.current_cart.append(add_to_cart)
    
    def update_available_options(
        self,
        categories: Optional[List[str]] = None,
        products: Optional[List[str]] = None,
        actions: Optional[List[str]] = None
    ):
        """Update available options from chatbot."""
        if categories:
            self.available_categories = categories
        if products:
            self.available_products = products
        if actions:
            self.available_actions = actions
    
    def add_chatbot_behavior(self, behavior: ChatbotBehavior):
        """Record observed chatbot behavior."""
        if behavior not in self.chatbot_behaviors:
            self.chatbot_behaviors.append(behavior)
    
    def add_capability(self, capability: str):
        """Add discovered chatbot capability."""
        if capability not in self.chatbot_capabilities:
            self.chatbot_capabilities.append(capability)
    
    def add_restriction(self, restriction: str):
        """Add discovered chatbot restriction."""
        if restriction not in self.chatbot_restrictions:
            self.chatbot_restrictions.append(restriction)
    
    def get_recent_turns(self, count: Optional[int] = None) -> List[ConversationTurn]:
        """Get recent conversation turns."""
        n = count or self.window_size
        return self.turns[-n:] if len(self.turns) > n else self.turns
    
    def get_context_for_llm(self, max_tokens: int = 2000) -> str:
        """
        Generate a rich context string for LLM prompts.
        
        Args:
            max_tokens: Approximate max tokens (chars/4)
            
        Returns:
            Formatted context string
        """
        max_chars = max_tokens * 4
        context_parts = []
        
        # Current state summary
        context_parts.append(f"""=== CONVERSATION STATE ===
Phase: {self.current_phase.value} (Turn {self.turns_in_current_phase} in phase)
Domain: {self.domain}
Total Turns: {self.total_turns}
Vulnerabilities Found: {self.vulnerabilities_found}
""")
        
        # Navigation state
        if self.current_category or self.current_product:
            nav = "=== CURRENT NAVIGATION ===\n"
            if self.current_category:
                nav += f"Category: {self.current_category}\n"
            if self.current_product:
                nav += f"Product: {self.current_product}\n"
            if self.current_cart:
                nav += f"Cart: {', '.join(self.current_cart)}\n"
            context_parts.append(nav)
        
        # Available options
        if self.available_categories or self.available_products:
            opts = "=== AVAILABLE OPTIONS ===\n"
            if self.available_categories:
                opts += f"Categories: {', '.join(self.available_categories)}\n"
            if self.available_products:
                opts += f"Products: {', '.join(self.available_products[:10])}\n"
            if self.available_actions:
                opts += f"Actions: {', '.join(self.available_actions)}\n"
            context_parts.append(opts)
        
        # Discovered constraints
        if self.discovered_constraints:
            constraints = "=== DISCOVERED CONSTRAINTS ===\n"
            for c in self.discovered_constraints[-5:]:
                constraints += f"- {c.description}\n"
            context_parts.append(constraints)
        
        # Chatbot profile
        if self.chatbot_behaviors or self.chatbot_restrictions:
            profile = "=== CHATBOT PROFILE ===\n"
            if self.chatbot_behaviors:
                profile += f"Behaviors: {', '.join(b.value for b in self.chatbot_behaviors)}\n"
            if self.chatbot_restrictions:
                profile += f"Restrictions: {', '.join(self.chatbot_restrictions[:5])}\n"
            if self.chatbot_capabilities:
                profile += f"Capabilities: {', '.join(self.chatbot_capabilities[:5])}\n"
            context_parts.append(profile)
        
        # Attack effectiveness
        if self.successful_techniques or self.failed_techniques:
            effectiveness = "=== ATTACK EFFECTIVENESS ===\n"
            if self.successful_techniques:
                effectiveness += f"Successful: {', '.join(self.successful_techniques[-5:])}\n"
            if self.failed_techniques:
                effectiveness += f"Failed: {', '.join(self.failed_techniques[-5:])}\n"
            context_parts.append(effectiveness)
        
        # Recent conversation
        recent = self.get_recent_turns(5)
        if recent:
            conv = "=== RECENT CONVERSATION ===\n"
            for turn in recent:
                conv += f"[Turn {turn.turn_number}] ({turn.attack_technique})\n"
                conv += f"  Attack: {turn.attack_prompt[:100]}...\n"
                conv += f"  Response: {turn.chatbot_response[:100]}...\n"
                if turn.risk_category >= 2:
                    conv += f"  ⚠️ Risk {turn.risk_category}: {turn.vulnerability_type}\n"
            context_parts.append(conv)
        
        # Join and truncate if needed
        full_context = "\n".join(context_parts)
        if len(full_context) > max_chars:
            full_context = full_context[:max_chars] + "\n...[truncated]"
        
        return full_context
    
    def get_attack_context_summary(self) -> Dict[str, Any]:
        """Get a summary suitable for attack prompt generation."""
        return {
            "phase": self.current_phase.value,
            "domain": self.domain,
            "total_turns": self.total_turns,
            "current_category": self.current_category,
            "current_product": self.current_product,
            "available_categories": self.available_categories,
            "available_products": self.available_products[:10] if self.available_products else [],
            "successful_techniques": self.successful_techniques[-5:],
            "failed_techniques": self.failed_techniques[-5:],
            "vulnerabilities_found": self.vulnerabilities_found,
            "discovered_vulnerabilities": self.discovered_vulnerabilities[-5:],
            "chatbot_behaviors": [b.value for b in self.chatbot_behaviors],
            "pending_action": self.pending_action
        }
    
    def get_simple_history(self) -> List[Dict]:
        """Get simplified conversation history for context windows."""
        return [
            {
                "turn": t.turn_number,
                "user": t.attack_prompt,
                "assistant": t.chatbot_response,
                "risk": t.risk_category
            }
            for t in self.get_recent_turns()
        ]
    
    def should_advance_phase(self) -> bool:
        """Determine if we should advance to next attack phase."""
        # Advance after certain number of turns in phase
        phase_turn_limits = {
            ConversationPhase.RECONNAISSANCE: 6,
            ConversationPhase.TRUST_BUILDING: 6,
            ConversationPhase.BOUNDARY_TESTING: 7,
            ConversationPhase.EXPLOITATION: 6,
            ConversationPhase.UNAUTHORIZED_CLAIMS: 10
        }
        
        limit = phase_turn_limits.get(self.current_phase, 5)
        return self.turns_in_current_phase >= limit
    
    def get_next_phase(self) -> ConversationPhase:
        """Get the next attack phase."""
        phase_order = [
            ConversationPhase.INITIALIZATION,
            ConversationPhase.RECONNAISSANCE,
            ConversationPhase.TRUST_BUILDING,
            ConversationPhase.BOUNDARY_TESTING,
            ConversationPhase.EXPLOITATION,
            ConversationPhase.UNAUTHORIZED_CLAIMS,
            ConversationPhase.COMPLETED
        ]
        
        try:
            current_idx = phase_order.index(self.current_phase)
            if current_idx < len(phase_order) - 1:
                return phase_order[current_idx + 1]
        except ValueError:
            pass
        
        return ConversationPhase.COMPLETED
    
    def reset(self):
        """Reset memory for new run."""
        self.turns = []
        self.current_phase = ConversationPhase.INITIALIZATION
        self.phase_start_turn = 1
        self.turns_in_current_phase = 0
        self.current_category = None
        self.current_product = None
        self.current_cart = []
        self.pending_action = None
        self.total_turns = 0
        self.adaptive_turns = 0
        # Keep discovered info across runs for learning
    
    def export_to_dict(self) -> Dict[str, Any]:
        """Export memory to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "run_number": self.run_number,
            "attack_category": self.attack_category,
            "domain": self.domain,
            "current_phase": self.current_phase.value,
            "total_turns": self.total_turns,
            "adaptive_turns": self.adaptive_turns,
            "vulnerabilities_found": self.vulnerabilities_found,
            "turns": [
                {
                    "turn_number": t.turn_number,
                    "attack_phase": t.attack_phase,
                    "attack_technique": t.attack_technique,
                    "attack_prompt": t.attack_prompt,
                    "chatbot_response": t.chatbot_response,
                    "was_adaptive": t.was_adaptive,
                    "risk_category": t.risk_category,
                    "vulnerability_type": t.vulnerability_type
                }
                for t in self.turns
            ],
            "successful_techniques": self.successful_techniques,
            "failed_techniques": self.failed_techniques,
            "discovered_vulnerabilities": self.discovered_vulnerabilities,
            "chatbot_behaviors": [b.value for b in self.chatbot_behaviors],
            "chatbot_restrictions": self.chatbot_restrictions,
            "chatbot_capabilities": self.chatbot_capabilities
        }


class EnhancedMemoryManager:
    """Manages enhanced conversation memory across attack runs."""
    
    def __init__(self, domain: str = "e-commerce"):
        self.memories: Dict[str, EnhancedConversationMemory] = {}
        self.current_memory: Optional[EnhancedConversationMemory] = None
        self.domain = domain
    
    def create_memory(self, session_id: str, run_number: int, attack_category: str) -> EnhancedConversationMemory:
        """Create new memory for an attack session."""
        memory = EnhancedConversationMemory(
            session_id=session_id,
            run_number=run_number,
            attack_category=attack_category,
            domain=self.domain
        )
        self.memories[f"{session_id}_{run_number}"] = memory
        self.current_memory = memory
        return memory
    
    def get_memory(self, session_id: str, run_number: int) -> Optional[EnhancedConversationMemory]:
        """Get memory for a specific session and run."""
        key = f"{session_id}_{run_number}"
        return self.memories.get(key)
    
    def get_cross_run_learnings(self, session_id: str) -> Dict[str, Any]:
        """Get learnings across all runs for a session."""
        session_memories = [
            m for k, m in self.memories.items() 
            if k.startswith(session_id)
        ]
        
        if not session_memories:
            return {}
        
        # Aggregate learnings
        all_successful = []
        all_failed = []
        all_vulnerabilities = []
        all_behaviors = []
        
        for mem in session_memories:
            all_successful.extend(mem.successful_techniques)
            all_failed.extend(mem.failed_techniques)
            all_vulnerabilities.extend(mem.discovered_vulnerabilities)
            all_behaviors.extend([b.value for b in mem.chatbot_behaviors])
        
        return {
            "successful_techniques": list(set(all_successful)),
            "failed_techniques": list(set(all_failed)),
            "vulnerabilities": all_vulnerabilities,
            "chatbot_behaviors": list(set(all_behaviors)),
            "total_runs": len(session_memories)
        }
