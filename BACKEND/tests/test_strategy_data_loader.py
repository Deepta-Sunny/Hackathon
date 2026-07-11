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
    assert isinstance(data["agent_info_system_message"], str) and data["agent_info_system_message"].strip()
    assert isinstance(data["prompt_generation_system_prompt"], str) and data["prompt_generation_system_prompt"].strip()
    assert isinstance(data["classification_system_prompt"], str) and data["classification_system_prompt"].strip()


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


def test_crescendo_strategy_data_includes_centralized_prompt_assets():
    loader_cls = _load_strategy_data_loader_class()
    data = loader_cls.load("crescendo")

    assert "generation_prompt" in data
    assert "user_prompt_template" in data["generation_prompt"]
    assert "mission_template" in data["generation_prompt"]
    assert "pyrit_examples" in data
    assert isinstance(data["pyrit_examples"].get("categories"), list)
    assert data["pyrit_examples"]["categories"]
    assert any(category.get("name") == "crescendo" for category in data["pyrit_examples"]["categories"])
