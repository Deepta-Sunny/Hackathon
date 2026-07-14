import asyncio
import importlib.util
import os
from pathlib import Path


def _load_sequencer_class():
    root = Path(__file__).resolve().parents[1]
    target = root / "utils" / "conversational_sequencer.py"
    spec = importlib.util.spec_from_file_location(
        "conversational_sequencer",
        str(target),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.ConversationalAttackSequencer


def test_sequencer_tracks_emotional_technique_in_metadata():
    os.environ.setdefault("AZURE_OPENAI_API_KEY", "test-key")
    os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com")
    sequencer_cls = _load_sequencer_class()
    sequencer = sequencer_cls()

    _, meta = asyncio.run(
        sequencer.get_next_attack_prompt(domain="general", last_response="", last_risk_category=1)
    )

    expected_initial = list(sequencer.EMOTIONAL_TECHNIQUE_CATALOG.keys())[0]
    assert meta["emotional_technique"] == expected_initial
    assert meta["emotional_technique"] in sequencer.EMOTIONAL_TECHNIQUE_CATALOG
    assert meta["switch_reason"] == "continue_current_technique"


def test_sequencer_switches_technique_after_clear_rejection():
    os.environ.setdefault("AZURE_OPENAI_API_KEY", "test-key")
    os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com")
    sequencer_cls = _load_sequencer_class()
    sequencer = sequencer_cls()

    _, first_meta = asyncio.run(
        sequencer.get_next_attack_prompt(domain="general", last_response="", last_risk_category=1)
    )
    _, second_meta = asyncio.run(
        sequencer.get_next_attack_prompt(
            domain="general",
            last_response="I cannot assist with that request due to policy.",
            last_risk_category=1
        )
    )

    assert second_meta["clear_rejection_detected"] is True
    assert second_meta["switch_reason"] == "clear_rejection_switch"
    assert second_meta["emotional_technique"] in sequencer.EMOTIONAL_TECHNIQUE_CATALOG
    assert second_meta["emotional_technique"] != first_meta["emotional_technique"]
