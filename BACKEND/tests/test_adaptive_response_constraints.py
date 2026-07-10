import importlib.util
from pathlib import Path


def _load_handler_class():
    root = Path(__file__).resolve().parents[1]
    target = root / "attack_strategies" / "adaptive_response_handler.py"
    spec = importlib.util.spec_from_file_location(
        "adaptive_response_handler",
        str(target),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.AdaptiveResponseHandler


def test_extract_constraints_too_long():
    handler_cls = _load_handler_class()
    handler = handler_cls(azure_client=None)
    result = handler._extract_response_constraints("Your message is too long. Please try again.")
    assert result["has_length_limit"] is True
    assert result["max_chars"] is None


def test_extract_constraints_limit_with_number():
    handler_cls = _load_handler_class()
    handler = handler_cls(azure_client=None)
    result = handler._extract_response_constraints(
        "Your message is too long. Please limit your input to 500 characters and try again."
    )
    assert result["has_length_limit"] is True
    assert result["max_chars"] == 500


def test_extract_constraints_limit_phrase():
    handler_cls = _load_handler_class()
    handler = handler_cls(azure_client=None)
    result = handler._extract_response_constraints("Please limit your input and try again.")
    assert result["has_length_limit"] is True
