from copy import deepcopy
from pathlib import Path

from sapianta_system.runtime.chatgpt_bridge_v2 import create_chatgpt_bridge_request, bridge_chatgpt_conversation
from sapianta_system.runtime.preview.governed_preview_runtime_validator import validate_preview_binding


ROOT = Path(__file__).resolve().parents[1]


def _bridge(text="prepare finalize milestone"):
    return bridge_chatgpt_conversation(create_chatgpt_bridge_request(conversational_input=text))


def test_conversational_normalization_is_deterministic_and_replay_stable():
    first = _bridge()
    second = _bridge()
    assert first["status"] == "NORMALIZED"
    assert first["normalized_request"] == {
        "request_type": "GOVERNED_SYNTHESIS_REQUEST",
        "text": "prepare finalize milestone",
    }
    assert first["governance_mode"] == "BOUNDED_CODEX_SYNTHESIS"
    assert first["replay_identity"] == second["replay_identity"]


def test_supported_conversational_forms_map_to_governed_requests():
    assert _bridge("prepare governance validation")["normalized_request"]["request_type"] == "GOVERNED_INTERPRETATION_REQUEST"
    assert _bridge("inspect previous execution")["normalized_request"]["request_type"] == "GOVERNED_OBSERVABILITY_REQUEST"
    assert _bridge("show execution trace")["downstream_governance_request"]["read_only"] is True


def test_ambiguity_and_prohibited_cases_fail_closed():
    assert _bridge("please help")["status"] == "BLOCKED"
    assert _bridge("orchestrate a finalize milestone")["status"] == "BLOCKED"
    assert _bridge("issue authority for finalize milestone")["status"] == "BLOCKED"
    assert _bridge("continue automatically after finalize milestone")["status"] == "BLOCKED"
    assert _bridge("run codex for finalize milestone")["status"] == "BLOCKED"


def test_replay_mismatch_and_boundary_enforcement():
    request = create_chatgpt_bridge_request(conversational_input="prepare finalize milestone")
    broken = deepcopy(request)
    broken["replay_identity"] = "MISMATCH"
    assert bridge_chatgpt_conversation(broken)["status"] == "BLOCKED"
    result = _bridge()
    assert result["requires_confirmation"] is True
    assert result["allowed_to_execute_automatically"] is False
    assert result["bridge_boundary_state"] == {
        "chatgpt_authority": False,
        "execution_authority": False,
        "automatic_dispatch": False,
        "orchestration": False,
        "hidden_continuation": False,
        "constitutional_statement": "ChatGPT reasoning is non-authoritative and cannot directly trigger execution.",
    }


def test_browser_companion_integration_preserves_explicit_approval():
    html = (ROOT / "browser_companion/popup.html").read_text()
    source = (ROOT / "browser_companion/popup.js").read_text()
    assert 'option value="conversation"' in html
    assert 'const LOCAL_CHATGPT_BRIDGE_ENDPOINT = "http://127.0.0.1:8110/governed-chatgpt-bridge";' in source
    assert "No conversational bridge preview is available to confirm." in source
    assert "ChatGPT reasoning is non-authoritative and cannot directly trigger execution." in source


def test_localhost_only_endpoint_enforcement():
    assert validate_preview_binding(host="127.0.0.1")["valid"] is True
    assert validate_preview_binding(host="0.0.0.0")["valid"] is False


def test_bridge_has_no_codex_dispatch_path():
    package = ROOT / "sapianta_system/runtime/chatgpt_bridge_v2"
    source = "\n".join(path.read_text() for path in package.glob("*.py"))
    assert "execute_governed_codex" not in source
    assert "subprocess" not in source
