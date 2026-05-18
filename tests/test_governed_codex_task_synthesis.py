from pathlib import Path

from sapianta_system.runtime.codex_synthesis import create_governed_codex_task_request, synthesize_governed_codex_task


ROOT = Path(__file__).resolve().parents[1]


def _synthesize(text="prepare finalize milestone for replay validation"):
    return synthesize_governed_codex_task(create_governed_codex_task_request(natural_language=text))


def test_deterministic_synthesis_and_replay_identity_stability():
    first = _synthesize()
    second = _synthesize()
    assert first["status"] == "SYNTHESIZED"
    assert first["task_class"] == "FINALIZE_TASK"
    assert first["governance_mode"] == "BOUNDED_CODEX_SYNTHESIS"
    assert first["codex_prompt_preview"] == second["codex_prompt_preview"]
    assert first["replay_identity"] == second["replay_identity"]


def test_prompt_is_bounded_and_contains_required_sections():
    prompt = _synthesize()["codex_prompt_preview"]
    assert len(prompt) < 2400
    for section in (
        "GOAL:",
        "CURRENT CONTEXT:",
        "ALLOWED SCOPE:",
        "PROHIBITED ACTIONS:",
        "VALIDATION REQUIREMENTS:",
        "REPLAY REQUIREMENTS:",
        "TEST REQUIREMENTS:",
        "ACCEPTANCE CRITERIA:",
        "FINAL RESPONSE REQUIREMENTS:",
    ):
        assert section in prompt


def test_shell_orchestration_and_hidden_continuation_fail_closed():
    assert _synthesize("prepare finalize milestone then run shell")["status"] == "BLOCKED"
    assert _synthesize("prepare finalize milestone and orchestrate it")["status"] == "BLOCKED"
    assert _synthesize("prepare finalize milestone and continue automatically")["status"] == "BLOCKED"


def test_unsupported_and_malformed_requests_fail_closed():
    assert _synthesize("please invent a deployment strategy")["status"] == "BLOCKED"
    assert synthesize_governed_codex_task({})["status"] == "BLOCKED"


def test_explicit_approval_and_replay_visibility_are_required():
    result = _synthesize()
    assert result["requires_confirmation"] is True
    assert result["allowed_to_execute_automatically"] is False
    assert result["replay_visible"] is True
    assert result["evidence"]["original_human_input"] == "prepare finalize milestone for replay validation"


def test_browser_companion_exposes_preview_only_codex_mode():
    html = (ROOT / "browser_companion/popup.html").read_text()
    source = (ROOT / "browser_companion/popup.js").read_text()
    assert 'option value="codex"' in html
    assert 'const LOCAL_CODEX_SYNTHESIS_ENDPOINT = "http://127.0.0.1:8110/governed-codex-synthesize";' in source
    assert "Codex synthesis failed governed validation." in source
    assert "Governed Codex Task mode is preview-only and does not execute Codex." in source


def test_no_automatic_execution_or_hidden_routing_is_introduced():
    source = (ROOT / "browser_companion/popup.js").read_text()
    assert "allowed_to_execute_automatically === false" in source
    assert "setInterval" not in source
    assert "subprocess" not in source
    assert "shell" not in source.lower()
