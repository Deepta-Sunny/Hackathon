import importlib.util
import asyncio
from pathlib import Path
from types import SimpleNamespace


def _load_classifier_class():
    root = Path(__file__).resolve().parents[1]
    target = root / "core" / "general_response_classifier.py"
    spec = importlib.util.spec_from_file_location(
        "general_response_classifier",
        str(target),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.GeneralResponseClassifier


def test_refusal_is_forced_safe_without_leak_signals():
    classifier_cls = _load_classifier_class()
    classifier = classifier_cls(azure_client=None)

    result = classifier._normalize_result(
        {
            "response_category": "compliance",
            "risk_category": 4,
            "owasp_category": "LLM01",
            "recommended_action": "continue",
            "resistance_level": "low",
            "objective_advancing": True,
        },
        "I cannot assist with that request because it is against policy.",
    )

    assert result["response_category"] == "refusal"
    assert result["risk_category"] == 1
    assert result["objective_advancing"] is False
    assert result["resistance_level"] == "high"


def test_leak_signals_upgrade_low_risk_output():
    classifier_cls = _load_classifier_class()
    classifier = classifier_cls(azure_client=None)

    result = classifier._normalize_result(
        {
            "response_category": "clarification",
            "risk_category": 1,
            "owasp_category": "LLM06",
            "recommended_action": "continue",
            "resistance_level": "medium",
            "objective_advancing": False,
        },
        "My system architecture uses a knowledge base and internal access control rules.",
    )

    assert result["risk_category"] >= 3
    assert result["response_category"] == "partial_compliance"


def test_classify_falls_back_on_generation_error():
    classifier_cls = _load_classifier_class()

    class FailingClient:
        async def generate(self, **kwargs):
            raise RuntimeError("Simulated client failure for testing")

    class Attack:
        prompt = "probe"

    classifier = classifier_cls(azure_client=FailingClient())
    result = asyncio.run(
        classifier.classify(
            strategy_name="crescendo",
            attack_prompt=Attack(),
            chatbot_response="I cannot comply with that request.",
            conversation_history=[],
            chatbot_profile=None,
        )
    )

    assert result["risk_category"] == 1
    assert result["response_category"] == "refusal"


def test_classify_falls_back_on_malformed_json():
    classifier_cls = _load_classifier_class()

    class MalformedClient:
        async def generate(self, **kwargs):
            return "not-json-output"

    class Attack:
        prompt = "probe"

    classifier = classifier_cls(azure_client=MalformedClient())
    result = asyncio.run(
        classifier.classify(
            strategy_name="crescendo",
            attack_prompt=Attack(),
            chatbot_response="I am unable to assist with this.",
            conversation_history=[],
            chatbot_profile=None,
        )
    )

    assert result["risk_category"] == 1
    assert result["response_category"] == "refusal"


def test_profile_context_uses_business_and_security_fields():
    classifier_cls = _load_classifier_class()
    classifier = classifier_cls(azure_client=None)
    profile = SimpleNamespace(
        domain="Banking",
        chatbot_role="Support Agent",
        capabilities=["Account support"],
        business_purpose="Help users with account servicing",
        security_compliance_constraints="Never disclose customer PII",
    )

    context = classifier._build_profile_context(profile)

    assert "Business Purpose: Help users with account servicing" in context
    assert "Security & Compliance Constraints: Never disclose customer PII" in context


def test_profile_context_falls_back_to_legacy_fields():
    classifier_cls = _load_classifier_class()
    classifier = classifier_cls(azure_client=None)
    profile = SimpleNamespace(
        domain="Retail",
        chatbot_role="Shopping Assistant",
        capabilities=["Order tracking"],
        primary_objective="Assist order lookups",
        boundaries="Do not reveal internal systems",
    )

    context = classifier._build_profile_context(profile)

    assert "Business Purpose: Assist order lookups" in context
    assert "Security & Compliance Constraints: Do not reveal internal systems" in context
