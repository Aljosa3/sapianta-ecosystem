import json
from pathlib import Path

from sapianta_system.runtime.codex_handoff import create_governed_codex_handoff, create_governed_codex_handoff_request
from sapianta_system.runtime.codex_handoff.governed_codex_handoff_package import export_handoff_package
from sapianta_system.runtime.codex_handoff.governed_codex_handoff_validator import validate_handoff_package
from sapianta_system.runtime.codex_synthesis import create_governed_codex_task_request, synthesize_governed_codex_task


ROOT = Path(__file__).resolve().parents[1]


def _synthesis():
    return synthesize_governed_codex_task(
        create_governed_codex_task_request(natural_language="prepare finalize milestone for replay validation")
    )


def _handoff():
    return create_governed_codex_handoff(
        create_governed_codex_handoff_request(
            synthesis_response=_synthesis(),
            original_human_request="prepare finalize milestone for replay validation",
        )
    )


def test_deterministic_package_generation_and_replay_identity():
    first = _handoff()
    second = _handoff()
    assert first["status"] == "HANDOFF_READY"
    assert first["replay_identity"] == second["replay_identity"]
    assert first["codex_prompt"] == second["codex_prompt"]


def test_malformed_package_and_downstream_authority_fail_closed():
    assert validate_handoff_package({})["valid"] is False
    package = _handoff()
    package["downstream_execution_authority"] = True
    assert validate_handoff_package(package)["valid"] is False


def test_shell_orchestration_and_hidden_continuation_fields_fail_closed():
    for field in ("shell_execution", "orchestration", "hidden_continuation", "hidden_retry"):
        package = _handoff()
        package[field] = True
        assert validate_handoff_package(package)["valid"] is False


def test_export_generation_is_replay_visible(tmp_path):
    package = _handoff()
    path = export_handoff_package(package=package, export_dir=tmp_path)
    exported = json.loads(path.read_text())
    assert path.name == f"governed_codex_handoff_{package['replay_identity']}.json"
    assert exported["replay_identity"] == package["replay_identity"]
    assert exported["export_identity"] == package["export_identity"]


def test_explicit_approval_requirement_and_downstream_prohibition():
    package = _handoff()
    assert package["requires_confirmation"] is True
    assert package["allowed_to_execute_automatically"] is False
    assert package["downstream_execution_authority"] is False
    assert package["evidence"]["downstream_execution_authority"] is True


def test_browser_companion_integration_is_export_only():
    html = (ROOT / "browser_companion/popup.html").read_text()
    source = (ROOT / "browser_companion/popup.js").read_text()
    assert 'id="export"' in html
    assert 'const LOCAL_CODEX_HANDOFF_ENDPOINT = "http://127.0.0.1:8110/governed-codex-handoff";' in source
    assert "Export governed handoff package" in html
    assert "Explicit Codex preview confirmation is required before export." in source
    assert "Governed Codex Task mode is preview-only and does not execute Codex." in source


def test_no_automatic_execution_is_introduced():
    source = (ROOT / "browser_companion/popup.js").read_text()
    assert "exportGovernedHandoffPackage" in source
    assert "setInterval" not in source
    assert "subprocess" not in source
    assert "shell" not in source.lower()
