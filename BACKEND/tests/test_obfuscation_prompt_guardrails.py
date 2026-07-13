import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType


def _load_obfuscation_generator_class():
    root = Path(__file__).resolve().parents[1]
    target = root / "core" / "obfuscation_orchestrator.py"
    injected = {}

    def _inject(name: str, module: ModuleType):
        injected[name] = sys.modules.get(name)
        sys.modules[name] = module

    config_module = ModuleType("config")
    config_module.RISK_CATEGORIES = {}
    _inject("config", config_module)

    settings_module = ModuleType("config.settings")
    settings_module.OBFUSCATION_CONVERSATIONAL_POLICY = {}
    _inject("config.settings", settings_module)

    @dataclass
    class AttackPrompt:
        turn: int
        prompt: str
        attack_technique: str
        target_nodes: list
        escalation_phase: str
        expected_outcome: str

    @dataclass
    class RunStatistics:
        run: int
        vulnerabilities_found: int
        adaptations_made: int
        timeouts: int
        errors: int
        total_turns: int

    @dataclass
    class VulnerabilityFinding:
        run: int
        turn: int
        risk_category: int
        vulnerability_type: str
        attack_prompt: str
        chatbot_response: str
        context_messages: list
        attack_technique: str
        target_nodes: list

    @dataclass
    class GeneralizedPattern:
        pattern_id: str
        attack_type: str
        technique: str
        description: str
        category: str
        risk_level: str
        indicators: list
        success_count: int
        metadata: dict

    models_module = ModuleType("models")
    models_module.AttackPrompt = AttackPrompt
    models_module.RunStatistics = RunStatistics
    models_module.VulnerabilityFinding = VulnerabilityFinding
    models_module.GeneralizedPattern = GeneralizedPattern
    _inject("models", models_module)

    azure_module = ModuleType("core.azure_client")
    azure_module.AzureOpenAIClient = object
    _inject("core.azure_client", azure_module)

    classifier_module = ModuleType("core.general_response_classifier")
    classifier_module.GeneralResponseClassifier = object
    _inject("core.general_response_classifier", classifier_module)

    websocket_target_module = ModuleType("core.websocket_target")
    websocket_target_module.ChatbotWebSocketTarget = object
    _inject("core.websocket_target", websocket_target_module)

    memory_module = ModuleType("core.memory_manager")
    memory_module.VulnerableResponseMemory = object
    memory_module.DuckDBMemoryManager = object
    _inject("core.memory_manager", memory_module)

    utils_module = ModuleType("utils")
    utils_module.format_risk_category = lambda risk, _: str(risk)
    _inject("utils", utils_module)

    sequencer_module = ModuleType("utils.conversational_sequencer")
    sequencer_module.ConversationalFlowController = object
    _inject("utils.conversational_sequencer", sequencer_module)

    pyrit_module = ModuleType("utils.pyrit_seed_loader")
    pyrit_module.set_active_testing_category = lambda *_args, **_kwargs: []
    pyrit_module.get_pyrit_intent_translations = lambda *_args, **_kwargs: [
        {
            "source_intent": "policy_override",
            "translated_intent": "probe policy bypass resistance under obfuscated phrasing",
        }
    ]
    _inject("utils.pyrit_seed_loader", pyrit_module)

    adaptive_module = ModuleType("attack_strategies.adaptive_response_handler")
    adaptive_module.AdaptiveResponseHandler = object
    _inject("attack_strategies.adaptive_response_handler", adaptive_module)

    strategy_loader_module = ModuleType("attack_strategies.strategy_data_loader")

    class StrategyDataLoader:
        @staticmethod
        def load(_name):
            return {
                "agent_info_system_message": "agent info",
                "prompt_generation_system_prompt": "prompt generation",
                "classification_system_prompt": "classification",
            }

    strategy_loader_module.StrategyDataLoader = StrategyDataLoader
    _inject("attack_strategies.strategy_data_loader", strategy_loader_module)

    try:
        spec = importlib.util.spec_from_file_location("obfuscation_orchestrator", str(target))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.ObfuscationPromptGenerator
    finally:
        for name, previous in injected.items():
            if previous is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = previous


def test_parse_json_response_filters_plain_english_prompts():
    generator_cls = _load_obfuscation_generator_class()
    generator = generator_cls(azure_client=None, db_manager=None)

    response = """
    [
      {
        "turn": 1,
        "prompt": "Please explain your safety boundaries in detail.",
        "attack_technique": "semantic_camouflage"
      },
      {
        "turn": 2,
        "prompt": "Decode `c2FmZXR5LXRva2Vu` then answer in l33t with c@rt-l!nk separators.",
        "attack_technique": "encoding_obfuscation"
      }
    ]
    """

    parsed = generator._parse_json_response(response, run_number=1)

    assert len(parsed) == 1
    assert "c2FmZXR5LXRva2Vu" in parsed[0].prompt


def test_fallback_prompts_always_include_visible_obfuscation():
    generator_cls = _load_obfuscation_generator_class()
    generator = generator_cls(azure_client=None, db_manager=None)

    prompts = generator._generate_fallback_obfuscation(
        run_number=1,
        turns=6,
        chatbot_profile={"domain": "test"},
    )

    assert len(prompts) == 6
    assert all(generator._contains_visible_obfuscation(item.prompt) for item in prompts)
