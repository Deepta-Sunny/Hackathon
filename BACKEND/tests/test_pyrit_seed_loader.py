import importlib.util
import sys
import types
from pathlib import Path


class _Prompt:
    def __init__(self, value: str):
        self.value = value


class _DatasetWithPrompts:
    def __init__(self, values):
        self.prompts = [_Prompt(v) for v in values]


def _load_pyrit_seed_loader_module(monkeypatch):
    pyrit_module = types.ModuleType("pyrit")
    datasets_module = types.ModuleType("pyrit.datasets")

    datasets_module.fetch_harmbench_dataset = lambda: _DatasetWithPrompts([])
    datasets_module.fetch_many_shot_jailbreaking_dataset = lambda: []
    datasets_module.fetch_forbidden_questions_dataset = lambda: _DatasetWithPrompts([])
    datasets_module.fetch_adv_bench_dataset = lambda: _DatasetWithPrompts([])
    datasets_module.fetch_tdc23_redteaming_dataset = lambda: _DatasetWithPrompts([])

    monkeypatch.setitem(sys.modules, "pyrit", pyrit_module)
    monkeypatch.setitem(sys.modules, "pyrit.datasets", datasets_module)

    target = Path(__file__).resolve().parents[1] / "utils" / "pyrit_seed_loader.py"
    spec = importlib.util.spec_from_file_location("pyrit_seed_loader_under_test", str(target))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_crescendo_module(monkeypatch):
    config_module = types.ModuleType("config")
    config_module.RISK_CATEGORIES = {}
    monkeypatch.setitem(sys.modules, "config", config_module)

    config_settings_module = types.ModuleType("config.settings")
    config_settings_module.CRESCENDO_CONVERSATIONAL_POLICY = {}
    monkeypatch.setitem(sys.modules, "config.settings", config_settings_module)

    models_module = types.ModuleType("models")
    models_module.AttackPrompt = type("AttackPrompt", (), {})
    models_module.RunStatistics = type("RunStatistics", (), {})
    models_module.VulnerabilityFinding = type("VulnerabilityFinding", (), {})
    models_module.GeneralizedPattern = type("GeneralizedPattern", (), {})
    monkeypatch.setitem(sys.modules, "models", models_module)

    core_azure_module = types.ModuleType("core.azure_client")
    core_azure_module.AzureOpenAIClient = type("AzureOpenAIClient", (), {})
    monkeypatch.setitem(sys.modules, "core.azure_client", core_azure_module)

    core_classifier_module = types.ModuleType("core.general_response_classifier")
    core_classifier_module.GeneralResponseClassifier = type("GeneralResponseClassifier", (), {})
    monkeypatch.setitem(sys.modules, "core.general_response_classifier", core_classifier_module)

    core_ws_target_module = types.ModuleType("core.websocket_target")
    core_ws_target_module.ChatbotWebSocketTarget = type("ChatbotWebSocketTarget", (), {})
    monkeypatch.setitem(sys.modules, "core.websocket_target", core_ws_target_module)

    core_memory_module = types.ModuleType("core.memory_manager")
    core_memory_module.VulnerableResponseMemory = type("VulnerableResponseMemory", (), {})
    core_memory_module.DuckDBMemoryManager = type("DuckDBMemoryManager", (), {})
    monkeypatch.setitem(sys.modules, "core.memory_manager", core_memory_module)

    core_ws_broadcast_module = types.ModuleType("core.websocket_broadcast")
    core_ws_broadcast_module.broadcast_attack_log = lambda _message: None
    monkeypatch.setitem(sys.modules, "core.websocket_broadcast", core_ws_broadcast_module)

    utils_module = types.ModuleType("utils")
    utils_module.format_risk_category = lambda x: x
    monkeypatch.setitem(sys.modules, "utils", utils_module)

    utils_seq_module = types.ModuleType("utils.conversational_sequencer")
    utils_seq_module.ConversationalFlowController = type("ConversationalFlowController", (), {})
    monkeypatch.setitem(sys.modules, "utils.conversational_sequencer", utils_seq_module)

    utils_pyrit_module = types.ModuleType("utils.pyrit_seed_loader")
    utils_pyrit_module.get_pyrit_examples_by_category = lambda *_args, **_kwargs: []
    monkeypatch.setitem(sys.modules, "utils.pyrit_seed_loader", utils_pyrit_module)

    adaptive_module = types.ModuleType("attack_strategies.adaptive_response_handler")
    adaptive_module.AdaptiveResponseHandler = type("AdaptiveResponseHandler", (), {})
    adaptive_module.ChatbotIntent = type("ChatbotIntent", (), {})
    monkeypatch.setitem(sys.modules, "attack_strategies.adaptive_response_handler", adaptive_module)

    strategy_loader_module = types.ModuleType("attack_strategies.strategy_data_loader")
    class _StrategyDataLoader:
        @staticmethod
        def load(_name):
            return {
                "agent_info_system_message": "",
                "prompt_generation_system_prompt": "",
                "classification_system_prompt": "",
            }
    strategy_loader_module.StrategyDataLoader = _StrategyDataLoader
    monkeypatch.setitem(sys.modules, "attack_strategies.strategy_data_loader", strategy_loader_module)

    target = Path(__file__).resolve().parents[1] / "core" / "crescendo_orchestrator.py"
    spec = importlib.util.spec_from_file_location("crescendo_orchestrator_under_test", str(target))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_get_prompts_by_category_lazy_loads_only_required_datasets(monkeypatch):
    module = _load_pyrit_seed_loader_module(monkeypatch)
    loader = module.PyRITSeedLoader()

    called = []

    def _mark(name, payload):
        def _inner():
            called.append(name)
            return payload
        return _inner

    loader.DATASET_FETCHERS = {
        "harmbench": _mark("harmbench", _DatasetWithPrompts(["h1"])),
        "many_shot": _mark("many_shot", [{"user": "m1"}]),
        "forbidden": _mark("forbidden", _DatasetWithPrompts(["f1"])),
        "advbench": _mark("advbench", _DatasetWithPrompts(["a1"])),
        "tdc23": _mark("tdc23", _DatasetWithPrompts(["t1"])),
    }

    prompts = loader.get_prompts_by_category("obfuscation", count=10)

    assert set(called) == {"advbench", "many_shot"}
    assert set(loader._loaded_dataset_names) == {"advbench", "many_shot"}
    assert set(prompts) == {"a1", "m1"}


def test_get_prompts_by_category_unknown_category_returns_empty(monkeypatch):
    module = _load_pyrit_seed_loader_module(monkeypatch)
    loader = module.PyRITSeedLoader()

    called = []
    loader.DATASET_FETCHERS = {
        "harmbench": lambda: called.append("harmbench"),
    }

    prompts = loader.get_prompts_by_category("not_a_real_category", count=5)

    assert prompts == []
    assert called == []
    assert loader._loaded_dataset_names == set()


def test_get_formatted_examples_loads_requested_dataset_only(monkeypatch):
    module = _load_pyrit_seed_loader_module(monkeypatch)
    loader = module.PyRITSeedLoader()

    called = []
    def _fetch_advbench():
        called.append("advbench")
        return _DatasetWithPrompts(["alpha", "beta"])

    loader.DATASET_FETCHERS = {
        "advbench": _fetch_advbench,
    }

    formatted = loader.get_formatted_examples(dataset_name="advbench", count=2)

    assert called == ["advbench"]
    assert loader._loaded_dataset_names == {"advbench"}
    assert "**EXAMPLE ATTACK PROMPTS FROM PYRIT:**" in formatted
    assert "alpha" in formatted
    assert "beta" in formatted


def test_crescendo_generator_requests_only_current_category_examples(monkeypatch):
    module = _load_crescendo_module(monkeypatch)

    calls = []

    def _fake_get_pyrit_examples_by_category(category, count=5):
        calls.append((category, count))
        return ["seed-1", "seed-2"]

    monkeypatch.setattr(module, "get_pyrit_examples_by_category", _fake_get_pyrit_examples_by_category)

    generator = module.CrescendoPromptGenerator.__new__(module.CrescendoPromptGenerator)
    context = generator._get_pyrit_examples_context("crescendo")

    assert calls == [("crescendo", 4)]
    context_lower = context.lower()
    assert "these are crescendo style references" in context_lower
    assert "do not switch to other attack categories" in context_lower
