import importlib.util
from pathlib import Path


def _load_strategy_data_loader_class():
    root = Path(__file__).resolve().parents[1]
    target = root / "attack_strategies" / "strategy_data_loader.py"
    spec = importlib.util.spec_from_file_location("strategy_data_loader", str(target))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.StrategyDataLoader


def test_obfuscation_strategy_data_is_available_with_required_keys():
    loader_cls = _load_strategy_data_loader_class()
    data = loader_cls.load("obfuscation")

    assert "agent_info_system_message" in data
    assert "prompt_generation_system_prompt" in data
    assert "classification_system_prompt" in data


def test_obfuscation_strategy_data_includes_expected_principles():
    loader_cls = _load_strategy_data_loader_class()
    data = loader_cls.load("obfuscation")
    prompt = data["prompt_generation_system_prompt"]

    expected_sections = [
        "INPUT OBFUSCATION TECHNIQUES",
        "OUTPUT OBFUSCATION TECHNIQUES",
        "Special Characters",
        "Encoding (Base64)",
        "Keyword Substitution",
        "Variables",
        "Emojis",
        "Splitting Prompts",
        "leet speak",
        "Descriptive Evasion",
        "Combining Techniques",
    ]

    for section in expected_sections:
        assert section in prompt
