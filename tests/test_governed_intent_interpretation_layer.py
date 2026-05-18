from copy import deepcopy
from pathlib import Path

from sapianta_system.runtime.intent import create_governed_intent_request, interpret_governed_intent
from sapianta_system.runtime.intent.governed_artifact_synthesizer import synthesize_governed_artifact


ROOT = Path(__file__).resolve().parents[1]


def _interpret(text="create governance artifact for operational replay proof"):
    return interpret_governed_intent(create_governed_intent_request(natural_language=text))


def test_successful_bounded_interpretation():
    result = _interpret()
    assert result["status"] == "INTERPRETED"
    assert result["intent_class"] == "GOVERNANCE_ARTIFACT_CREATION"
    assert result["governance_mode"] == "BOUNDED_ARTIFACT_SYNTHESIS"
    assert result["artifact_candidate"] == "TEST_OPERATIONAL_REPLAY_PROOF_V1"
    assert result["requires_confirmation"] is True
    assert result["allowed_to_execute_automatically"] is False


def test_deterministic_artifact_synthesis():
    assert synthesize_governed_artifact("RUNTIME_VALIDATION_REQUEST") == {
        "valid": True,
        "artifact_candidate": "GOVERNED_RUNTIME_VALIDATION_V1",
        "governance_mode": "BOUNDED_RUNTIME_VALIDATION_PREVIEW",
    }


def test_replay_identity_is_stable():
    assert _interpret()["replay_identity"] == _interpret()["replay_identity"]


def test_ambiguous_and_invalid_intents_fail_closed():
    assert _interpret("governance artifact and replay inspection")["status"] == "BLOCKED"
    assert _interpret("please do something useful")["status"] == "BLOCKED"


def test_hidden_execution_shell_and_codex_escalation_fail_closed():
    assert _interpret("create governance artifact then continue automatically")["status"] == "BLOCKED"
    assert _interpret("create governance artifact and run shell command")["status"] == "BLOCKED"
    assert _interpret("create governance artifact with codex")["status"] == "BLOCKED"


def test_replay_mismatch_and_malformed_request_fail_closed():
    request = create_governed_intent_request(natural_language="inspect replay")
    broken = deepcopy(request)
    broken["replay_identity"] = "MISMATCH"
    assert interpret_governed_intent(broken)["status"] == "BLOCKED"
    assert interpret_governed_intent({})["status"] == "BLOCKED"


def test_browser_companion_exposes_preview_confirm_then_invoke_path():
    html = (ROOT / "browser_companion/popup.html").read_text()
    source = (ROOT / "browser_companion/popup.js").read_text()
    assert 'option value="intent"' in html
    assert 'id="preview"' in html
    assert 'id="confirm"' in html
    assert 'const LOCAL_INTERPRET_ENDPOINT = "http://127.0.0.1:8110/governed-interpret";' in source
    assert "allowed_to_execute_automatically === false" in source
    assert "Explicit confirmation is required before invoke." in source


def test_no_automatic_execution_is_introduced():
    source = (ROOT / "browser_companion/popup.js").read_text()
    assert 'addEventListener("click", previewIntent)' in source
    assert 'addEventListener("click", confirmIntentPreview)' in source
    assert 'addEventListener("click", invokeGovernedRuntime)' in source
    assert "setInterval" not in source
    assert "automatic" not in source.lower().replace("allowed_to_execute_automatically", "")
