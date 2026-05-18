from copy import deepcopy
from pathlib import Path

from sapianta_system.runtime.chatgpt_bridge_v2 import bridge_chatgpt_conversation, create_chatgpt_bridge_request
from sapianta_system.runtime.intent_transfer import create_governed_intent_transfer, create_intent_transfer_request
from sapianta_system.runtime.preview.governed_preview_runtime_validator import validate_preview_binding


ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_STATEMENT = "This transfer package is non-executing and requires explicit governance preview and confirmation."


def _bridge():
    return bridge_chatgpt_conversation(create_chatgpt_bridge_request(conversational_input="prepare finalize milestone"))


def _transfer(**overrides):
    bridge = _bridge()
    request = create_intent_transfer_request(
        conversational_input=overrides.pop("conversational_input", "prepare finalize milestone"),
        normalized_governed_request=overrides.pop("normalized_governed_request", bridge["normalized_request"]),
        governance_mode=overrides.pop("governance_mode", bridge["governance_mode"]),
        replay_identity=overrides.pop("replay_identity", bridge["replay_identity"]),
    )
    return create_governed_intent_transfer(request)


def test_deterministic_transfer_package_generation_and_identity_stability():
    first = _transfer()
    second = _transfer()
    assert first["status"] == "TRANSFER_READY"
    assert first["transfer_identity"] == second["transfer_identity"]
    assert first["replay_identity"] == second["replay_identity"]
    assert first["package"]["package_version"] == "GOVERNED_INTENT_TRANSFER_PACKAGE_V1"


def test_preview_confirmation_and_non_executing_requirements_are_enforced():
    result = _transfer()
    package = result["package"]
    assert result["requires_preview"] is True
    assert result["requires_confirmation"] is True
    assert package["requires_preview"] is True
    assert package["requires_confirmation"] is True
    assert package["execution_authority"] is False
    assert package["chatgpt_authority"] is False
    assert package["transfer_boundary_statement"] == BOUNDARY_STATEMENT


def test_blocked_transfer_escalation_cases_fail_closed():
    bridge = _bridge()
    cases = [
        {"conversational_input": "execute finalize milestone"},
        {"conversational_input": "orchestrate finalize milestone"},
        {"conversational_input": "issue authority for finalize milestone"},
        {"conversational_input": "continue automatically"},
        {"normalized_governed_request": {"request_type": "GOVERNED_SYNTHESIS_REQUEST", "text": "dispatch codex"}},
    ]
    for overrides in cases:
        request = create_intent_transfer_request(
            conversational_input=overrides.get("conversational_input", "prepare finalize milestone"),
            normalized_governed_request=overrides.get("normalized_governed_request", bridge["normalized_request"]),
            governance_mode=bridge["governance_mode"],
            replay_identity=bridge["replay_identity"],
        )
        assert create_governed_intent_transfer(request)["status"] == "BLOCKED"


def test_malformed_replay_and_runtime_targets_fail_closed():
    bridge = _bridge()
    request = create_intent_transfer_request(
        conversational_input="prepare finalize milestone",
        normalized_governed_request=bridge["normalized_request"],
        governance_mode=bridge["governance_mode"],
        replay_identity=bridge["replay_identity"],
    )
    broken = deepcopy(request)
    broken["replay_identity"] = "MISMATCH"
    assert create_governed_intent_transfer(broken)["status"] == "BLOCKED"
    assert _transfer(normalized_governed_request={"request_type": "UNSUPPORTED"})["status"] == "BLOCKED"


def test_replay_visibility_and_boundary_state():
    result = _transfer()
    evidence = result["evidence"]
    assert evidence["original_conversational_input"] == "prepare finalize milestone"
    assert evidence["transfer_identity"] == result["transfer_identity"]
    assert evidence["replay_identity"] == result["replay_identity"]
    assert result["boundary_state"] == {
        "chatgpt_authority": False,
        "execution_authority": False,
        "automatic_dispatch": False,
        "orchestration": False,
        "hidden_continuation": False,
        "preview_required": True,
        "confirmation_required": True,
        "transfer_boundary_statement": BOUNDARY_STATEMENT,
    }


def test_browser_companion_integration_and_localhost_only_endpoint():
    html = (ROOT / "browser_companion/popup.html").read_text()
    source = (ROOT / "browser_companion/popup.js").read_text()
    assert 'id="transfer-export"' in html
    assert 'const LOCAL_INTENT_TRANSFER_ENDPOINT = "http://127.0.0.1:8110/governed-intent-transfer";' in source
    assert "Conversational bridge preview is required before transfer export." in source
    assert BOUNDARY_STATEMENT in source
    assert validate_preview_binding(host="127.0.0.1")["valid"] is True
    assert validate_preview_binding(host="0.0.0.0")["valid"] is False


def test_package_layer_has_no_execution_path():
    package = ROOT / "sapianta_system/runtime/intent_transfer"
    source = "\n".join(path.read_text() for path in package.glob("*.py"))
    assert "execute_governed_codex" not in source
    assert "subprocess" not in source
