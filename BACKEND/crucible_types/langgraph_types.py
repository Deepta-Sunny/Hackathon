"""
Crucible AI – LangGraph Type Definitions
=========================================
Central type module for the LangGraph Standard Attack Orchestrator.
All state, helper, and configuration types live here so that every
node, helper, and the orchestrator class import from a single source.

Usage:
    from crucible_types.langgraph_types import CrucibleState, PoisonPhase, NodeRoute
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypedDict


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════

class PoisonPhase(str, Enum):
    """
    Ordered phases for the data_poison_node state machine.

    Transition order:
        RECON  →  SCHEMA_EXTRACTION  →  INJECTION  →  VERIFICATION

    The node reads ``state["poison_phase"]`` to decide which sub-prompt to fire.
    After each chatbot response the node evaluates whether to advance the phase.
    """
    RECON              = "recon"
    SCHEMA_EXTRACTION  = "schema_extraction"
    INJECTION          = "injection"
    VERIFICATION       = "verification"


class NodeRoute(str, Enum):
    """
    Return values for the ``should_continue_node`` conditional edge function.

    CONTINUE_NODE      – stay in the same node, fire next seed prompt
    CONTINUE_ADAPTIVE  – seeds exhausted but turns remain; LLM generates a new prompt
    ADVANCE            – move to the next node in the sequence
    """
    CONTINUE_NODE      = "continue_node"
    CONTINUE_ADAPTIVE  = "continue_adaptive"
    ADVANCE            = "advance_to_next_node"


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER TYPED-DICTS  (used inside CrucibleState or as function signatures)
# ═══════════════════════════════════════════════════════════════════════════════

class SeedRecord(TypedDict):
    """
    One entry in the Crucible seed catalogue.
    Mirrors the dicts inside ``CRUCIBLE_SEEDS`` in utils/crucible_seed_loader.py.
    """
    section: str                    # e.g. "recon_node"
    technique: str                  # e.g. "capability_mapping"
    owasp: str                      # e.g. "LLM06"
    canonical_example: str          # Air-India-domain prompt text
    domain_adaptation_hint: str     # Guidance for domain moulding


class ConversationEntry(TypedDict, total=False):
    """
    One turn recorded in ``state["conversation_history"]``.
    ``total=False`` because some keys are only present for certain turn types.
    """
    turn: int
    node: str                       # Which attack node produced this turn
    user: str                       # Prompt sent to chatbot
    assistant: str                  # Chatbot response
    technique: str                  # Attack technique label
    owasp_category: str             # e.g. "LLM01"
    risk_category: int              # 1-4
    type: str                       # "attack" | "interruption_handled" | "adaptive"
    timestamp: str                  # ISO-8601


class VulnerabilityRecord(TypedDict, total=False):
    """
    One vulnerability finding stored in ``state["vulnerabilities"]``.
    Maps 1:1 to what is passed to ``VulnerableResponseMemory.add_finding()``.
    """
    run: int
    turn: int
    node: str
    risk_category: int              # 1 = SAFE, 2 = MEDIUM, 3 = HIGH, 4 = CRITICAL
    owasp_category: str
    vulnerability_type: str
    attack_prompt: str
    chatbot_response: str
    context_messages: List[Dict[str, str]]
    attack_technique: str
    target_nodes: List[str]
    risk_explanation: str
    information_leaked: List[str]
    timestamp: str


class NodeConfig(TypedDict):
    """
    Per-node configuration consumed by ``execute_attack_node`` and the
    conditional edge function.
    """
    name: str                       # e.g. "recon_node"
    owasp: str                      # Primary OWASP mapping
    max_turns: int                  # Hard ceiling on turns for this node
    seeds_count: int                # Number of adapted seeds loaded


class NodeResult(TypedDict, total=False):
    """
    Summary returned by ``_save_node_results`` for the per-node JSON file.
    """
    attack_category: str            # Always "standard_langgraph"
    node: str
    run_number: int
    total_turns: int
    vulnerabilities_found: int
    start_time: str
    end_time: str
    domain: str
    turns: List[Dict[str, Any]]


class AnalysisResult(TypedDict, total=False):
    """
    Output of ``analyze_response_for_node`` — the Azure OpenAI risk
    classification for a single turn.
    """
    risk_category: int
    owasp_category: str
    risk_explanation: str
    vulnerability_type: str
    information_leaked: List[str]
    adaptation_needed: bool
    adapted_prompt: str
    learned_from_response: List[str]


# ═══════════════════════════════════════════════════════════════════════════════
# CORE STATE  –  the single TypedDict that flows through every LangGraph node
# ═══════════════════════════════════════════════════════════════════════════════

class CrucibleState(TypedDict, total=False):
    """
    Complete state object for the LangGraph Standard Attack Orchestrator.

    LangGraph nodes receive the full state dict and return a **partial** dict
    containing only the keys they mutate.  The framework merges updates into
    the running state automatically.

    ``total=False`` is used because not every key is required at START — some
    are populated by later nodes.  The ``create_initial_state`` factory
    function below guarantees all keys have safe defaults.

    ─── Validation Rules ─────────────────────────────────────────────────────

    Required at __start__:
        run_number, architecture_context, chatbot_profile, max_turns,
        conversation_history (empty), vulnerabilities (empty),
        nodes_completed (empty), broadcast_callback

    Populated by domain_detection_node:
        domain, seed_prompts, seed_index, domain_adapted_seeds

    Node-specific:
        poison_phase / poison_* — only mutated by data_poison_node
        encoding_techniques_used — only mutated by encoding_node

    On node completion:
        current_node set to next node name
        nodes_completed appended with finished node
        coverage_score recalculated as len(nodes_completed) / 9
    ──────────────────────────────────────────────────────────────────────────
    """

    # ── Run context ───────────────────────────────────────────────────────────
    run_number: int                                 # Current run (1-based)
    total_runs: int                                 # Total planned runs
    domain: str                                     # "airline", "banking", "ecommerce", …
    architecture_context: str                       # Raw architecture / profile text
    chatbot_profile: Dict[str, Any]                 # Parsed chatbot profile dict

    # ── Conversation ──────────────────────────────────────────────────────────
    conversation_history: List[ConversationEntry]    # All turns across all nodes
    current_node: str                               # Name of executing node
    current_phase: str                              # Sub-phase label ("init", "attack", …)

    # ── Turn tracking ─────────────────────────────────────────────────────────
    turns_completed: Dict[str, int]                 # {node_name: turns_done}
    max_turns: Dict[str, int]                       # {node_name: ceiling} from config
    nodes_completed: List[str]                      # Ordered list of finished nodes
    current_turn_global: int                        # Monotonic turn counter across graph

    # ── Seed management ───────────────────────────────────────────────────────
    seed_prompts: Dict[str, List[SeedRecord]]       # Original Air-India seeds by section
    seed_index: Dict[str, int]                      # {node_name: next_seed_idx}
    domain_adapted_seeds: Dict[str, List[str]]      # {node_name: [adapted prompt texts]}

    # ── Conversation-interrupt handling ────────────────────────────────────────
    pending_agent_question: Optional[str]            # Chatbot's clarifying question
    adaptive_response_pending: Optional[str]         # LLM-generated contextual answer
    last_chatbot_response: str                       # Most recent raw chatbot response

    # ── Data Poisoning node  (4-phase state machine) ──────────────────────────
    poison_phase: str                                # PoisonPhase.value string
    extracted_response_schema: Optional[Dict]        # Inferred chatbot response schema
    poison_payload_sent: Optional[str]               # JSON string of last injected payload
    poison_accepted: bool                            # Did chatbot echo/use fake data?
    poison_attempt_count: int                        # Injection attempts made so far

    # ── Encoding node ─────────────────────────────────────────────────────────
    encoding_techniques_used: List[str]              # e.g. ["base64", "rot13", "hex", …]

    # ── Results ───────────────────────────────────────────────────────────────
    vulnerabilities: List[VulnerabilityRecord]       # All findings (risk >= 2)
    risk_distribution: Dict[str, int]                # {"SAFE": n, "MEDIUM": n, …}
    owasp_breakdown: Dict[str, int]                  # {"LLM01": n, "LLM02": n, …}
    coverage_score: float                            # 0.0 – 1.0 (nodes_completed / 9)

    # ── System integration ────────────────────────────────────────────────────
    broadcast_callback: Any                          # async fn for WebSocket broadcast
    final_report: Optional[Dict]                     # Populated by report_node


# ═══════════════════════════════════════════════════════════════════════════════
# FACTORY – guarantees every key has a safe default
# ═══════════════════════════════════════════════════════════════════════════════

def create_initial_state(
    *,
    architecture_context: str = "",
    chatbot_profile: Optional[Dict[str, Any]] = None,
    max_turns: Optional[Dict[str, int]] = None,
    broadcast_callback: Any = None,
) -> CrucibleState:
    """
    Build a fully-initialised CrucibleState with safe defaults.

    Called by ``LangGraphOrchestrator.execute_full_campaign`` before
    ``graph.ainvoke()``.  Every key is present so node code can do
    ``state["field"]`` without ``KeyError``.

    Args:
        architecture_context: Raw target-chatbot description text.
        chatbot_profile:      Parsed chatbot profile dict (from API request).
        max_turns:            Per-node turn-limit overrides from config.
        broadcast_callback:   async WebSocket broadcast function.

    Returns:
        A complete CrucibleState dict ready for graph execution.
    """
    # Deferred import to avoid circular dependency with config
    try:
        from config import LANGGRAPH_NODE_MAX_TURNS as _DEFAULT_TURNS
    except ImportError:
        _DEFAULT_TURNS = {
            "recon_node": 5, "trust_node": 5, "boundary_node": 7,
            "exploit_node": 8, "data_poison_node": 10, "encoding_node": 10,
            "prompt_inject_node": 7, "insecure_plugin_node": 7, "model_theft_node": 8,
        }

    return CrucibleState(
        # Run context
        run_number=1,
        total_runs=1,
        domain="",
        architecture_context=architecture_context,
        chatbot_profile=chatbot_profile or {},

        # Conversation
        conversation_history=[],
        current_node="domain_detection_node",
        current_phase="init",

        # Turn tracking
        turns_completed={},
        max_turns=max_turns or dict(_DEFAULT_TURNS),
        nodes_completed=[],
        current_turn_global=0,

        # Seed management
        seed_prompts={},
        seed_index={},
        domain_adapted_seeds={},

        # Interruption handling
        pending_agent_question=None,
        adaptive_response_pending=None,
        last_chatbot_response="",

        # Data poisoning
        poison_phase=PoisonPhase.RECON.value,
        extracted_response_schema=None,
        poison_payload_sent=None,
        poison_accepted=False,
        poison_attempt_count=0,

        # Encoding
        encoding_techniques_used=[],

        # Results
        vulnerabilities=[],
        risk_distribution={},
        owasp_breakdown={},
        coverage_score=0.0,

        # System
        broadcast_callback=broadcast_callback,
        final_report=None,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# NODE ORDERING  –  canonical sequence used by graph builder & conditional edges
# ═══════════════════════════════════════════════════════════════════════════════

ATTACK_NODE_SEQUENCE: List[str] = [
    "recon_node",
    "trust_node",
    "boundary_node",
    "exploit_node",
    "data_poison_node",
    "encoding_node",
    "prompt_inject_node",
    "insecure_plugin_node",
    "model_theft_node",
]
"""Ordered list of attack nodes. Used to determine 'next node' in conditional edges."""

OWASP_NODE_MAP: Dict[str, str] = {
    "recon_node":           "LLM06",
    "trust_node":           "LLM08",
    "boundary_node":        "LLM02",
    "exploit_node":         "LLM01",
    "data_poison_node":     "LLM03",
    "encoding_node":        "LLM06",
    "prompt_inject_node":   "LLM01",
    "insecure_plugin_node": "LLM07",
    "model_theft_node":     "LLM10",
}
"""Maps each attack node to its primary OWASP LLM Top-10 category."""
