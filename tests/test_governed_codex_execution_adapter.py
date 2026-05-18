import subprocess
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

from sapianta_system.runtime.codex_execution_adapter import create_codex_execution_request, execute_governed_codex
from sapianta_system.runtime.codex_handoff import create_governed_codex_handoff, create_governed_codex_handoff_request
from sapianta_system.runtime.codex_synthesis import create_governed_codex_task_request, synthesize_governed_codex_task
from sapianta_system.runtime.execution_gate import authorize_downstream_execution, create_execution_authorization_request


ROOT = Path(__file__).resolve().parents[1]
APPROVAL_TIME = "2026-05-18T10:00:00Z"


def _handoff():
    synthesis = synthesize_governed_codex_task(
        create_governed_codex_task_request(natural_language="prepare finalize milestone for replay validation")
    )
    return create_governed_codex_handoff(
        create_governed_codex_handoff_request(
            synthesis_response=synthesis,
            original_human_request="prepare finalize milestone for replay validation",
        )
    )


def _authority():
    return authorize_downstream_execution(
        create_execution_authorization_request(
            handoff_package=_handoff(),
            approved_by="human",
            approval_timestamp=APPROVAL_TIME,
        )
    )


def _request(**overrides):
    return create_codex_execution_request(
        handoff_package=overrides.pop("handoff_package", _handoff()),
        authority_token=overrides.pop("authority_token", _authority()),
        now=overrides.pop("now", "2026-05-18T10:01:00Z"),
        revoked_token_ids=overrides.pop("revoked_token_ids", set()),
        codex_executable=overrides.pop("codex_executable", "codex"),
        timeout_seconds=overrides.pop("timeout_seconds", 30),
    )


def _runner(*args, **kwargs):
    assert args[0][0:2] == ["codex", "exec"]
    assert kwargs["shell"] is False
    assert kwargs["timeout"] == 30
    return SimpleNamespace(returncode=0, stdout="ok", stderr="")


def test_deterministic_execution_receipts_and_replay_identity():
    first = execute_governed_codex(_request(), runner=_runner)
    second = execute_governed_codex(_request(), runner=_runner)
    assert first["status"] == "EXECUTION_ACCEPTED"
    assert first["receipt"]["receipt_id"] == second["receipt"]["receipt_id"]
    assert first["replay_identity"] == second["replay_identity"]


def test_authority_expiration_revocation_and_mismatch_reject():
    assert execute_governed_codex(_request(now="2026-05-18T10:05:01Z"), runner=_runner)["status"] == "AUTHORITY_EXPIRED"
    authority = _authority()
    assert execute_governed_codex(
        _request(authority_token=authority, revoked_token_ids={authority["token_id"]}),
        runner=_runner,
    )["status"] == "AUTHORITY_REVOKED"
    handoff = deepcopy(_handoff())
    handoff["codex_prompt"] = "mutated"
    assert execute_governed_codex(_request(handoff_package=handoff), runner=_runner)["status"] == "HANDOFF_MISMATCH"


def test_orchestration_shell_and_hidden_continuation_reject():
    for field in ("orchestration", "shell_execution", "hidden_continuation"):
        handoff = deepcopy(_handoff())
        handoff[field] = True
        assert execute_governed_codex(_request(handoff_package=handoff), runner=_runner)["status"] in {
            "HANDOFF_MISMATCH",
            "BLOCKED_CAPABILITY_DETECTED",
        }


def test_bounded_subprocess_and_shell_false_enforced():
    seen = {}

    def runner(*args, **kwargs):
        seen["args"] = args
        seen["kwargs"] = kwargs
        return SimpleNamespace(returncode=0, stdout="out", stderr="err")

    execute_governed_codex(_request(), runner=runner)
    assert seen["args"][0][0:2] == ["codex", "exec"]
    assert seen["kwargs"]["shell"] is False
    assert seen["kwargs"]["timeout"] == 30
    assert "capture_output" in seen["kwargs"]


def test_timeout_receipt_and_stdout_stderr_hashing():
    def timeout(*_args, **_kwargs):
        raise subprocess.TimeoutExpired(cmd=["codex", "exec"], timeout=30, output="out", stderr="err")

    result = execute_governed_codex(_request(), runner=timeout)
    assert result["status"] == "EXECUTION_TIMEOUT"
    assert result["receipt"]["stdout_hash"]
    assert result["receipt"]["stderr_hash"]
    assert result["receipt"]["constitutional_statement"] == (
        "Bounded Codex execution remains governance-controlled and does not constitute autonomous execution."
    )


def test_browser_companion_integration():
    html = (ROOT / "browser_companion/popup.html").read_text()
    source = (ROOT / "browser_companion/popup.js").read_text()
    assert 'id="codex-execute"' in html
    assert 'const LOCAL_CODEX_EXECUTE_ENDPOINT = "http://127.0.0.1:8110/governed-codex-execute";' in source
    assert "Authorization is required before governed Codex execution." in source
    assert "Codex execution adapter failed governed validation." in source
