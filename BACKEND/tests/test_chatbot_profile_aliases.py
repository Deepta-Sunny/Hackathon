import importlib.util
from pathlib import Path


def _load_profile_class():
    root = Path(__file__).resolve().parents[1]
    target = root / "models" / "chatbot_profile.py"
    spec = importlib.util.spec_from_file_location(
        "chatbot_profile",
        str(target),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.ChatbotProfile


def test_profile_syncs_business_and_security_aliases():
    profile_cls = _load_profile_class()
    profile = profile_cls(
        username="tester",
        websocket_url="ws://localhost:9000/ws",
        domain="Healthcare",
        business_purpose="Triage patient appointment requests",
        intended_audience="Patients",
        chatbot_role="Assistant",
        capabilities=["Book appointment"],
        security_compliance_constraints="Never expose PHI",
        communication_style="formal",
    )

    assert profile.primary_objective == "Triage patient appointment requests"
    assert profile.boundaries == "Never expose PHI"
    assert profile.to_dict()["business_purpose"] == "Triage patient appointment requests"
    assert profile.to_dict()["security_compliance_constraints"] == "Never expose PHI"
