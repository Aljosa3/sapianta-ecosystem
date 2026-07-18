from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import subprocess

from aigol.cli.commands.execution import run_execution_handoff
from aigol.cli.commands.ingress import generate_ingress_artifact
from aigol.runtime import codex_worker_result_to_semantic_validation_binding_runtime as bridge
from aigol.runtime.transport.serialization import replay_hash
from aigol.runtime.worker_result_validation_runtime import (
    CANONICAL_RESULT_VALIDATION_MEANING,
    FAILED_CLOSED,
    RESULT_VALIDATED,
    validate_worker_result,
)
from test_g31_20_codex_result_to_semantic_validation_binding import (
    _call_canonical_with_semantically_invalid_capture,
    _captured,
    _validate,
)
from test_g31_17b_governed_execution_to_codex_worker_activation_binding import (
    RecordingRunner,
)


PROTECTED = (
    ".runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/diagnostic_evidence.json",
    ".runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/governed_return.json",
    ".runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/lineage.json",
    ".runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stderr.txt",
    ".runtime/aigol/evidence/CHATGPT-INGRESS-REPLAY-d0ae9d30ff81b04e4feae7f5/provider_stdout.txt",
    ".runtime/aigol/ledger/governed_returns.jsonl",
    "WORKER_INVOCATION_ARTIFACT_V1",
    "WORKER_INVOKED",
    "invocation",
)


def _ingress() -> dict:
    return generate_ingress_artifact(
        human_request="Run isolated CODEX diagnostic.",
        semantic_intent="Protected evidence isolation proof",
    )


def _hashes(root: Path) -> dict[str, str]:
    return {
        name: sha256((root / name).read_bytes()).hexdigest()
        for name in PROTECTED
    }


def test_codex_version_diagnostic_persists_only_to_explicit_disposable_runtime(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repository = Path(__file__).resolve().parents[1]
    before = _hashes(repository)
    calls: list[list[str]] = []

    def fake_run(command, **_kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(
            command, 0, stdout="codex-cli isolated-test\n", stderr=""
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    runtime_root = tmp_path / "explicit-runtime"
    result = run_execution_handoff(
        ingress_artifact=_ingress(),
        workspace_path=str(tmp_path),
        timeout_seconds=10,
        runtime_root=runtime_root,
    )

    assert calls == [["codex", "--version"]]
    assert result["persistence"]["status"] == "PERSISTED"
    assert Path(result["persistence"]["evidence_path"]).is_relative_to(runtime_root)
    assert (runtime_root / "ledger" / "governed_returns.jsonl").is_file()
    assert _hashes(repository) == before


def test_missing_runtime_root_fails_closed_without_default_evidence_write(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    def fake_run(command, **_kwargs):
        return subprocess.CompletedProcess(command, 0, stdout="codex-cli isolated\n", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = run_execution_handoff(
        ingress_artifact=_ingress(),
        workspace_path=str(tmp_path),
        timeout_seconds=10,
    )

    assert result["persistence"] == {
        "status": "PERSISTENCE_FAILED",
        "fail_closed": True,
        "errors": [
            "explicit runtime_root is required; implicit default persistence is disabled"
        ],
    }
    assert result["fail_closed"] is True
    assert not (tmp_path / ".runtime" / "aigol").exists()


def test_authentic_policy_valid_output_does_not_claim_task_outcome_satisfaction(
    tmp_path: Path,
) -> None:
    runtime, activation, capture, root, workspace, _ = _captured(
        tmp_path,
        "G31-20D-TASK-MARKER",
        runner=RecordingRunner(stdout="EXPECTED_UNIQUE_TASK_MARKER"),
    )
    validation = _validate(runtime, activation, capture, root, workspace)

    assert validation["validation_status"] == RESULT_VALIDATED
    assert validation["canonical_validation_meaning"] == CANONICAL_RESULT_VALIDATION_MEANING
    assert validation["task_outcome_satisfaction_evaluated"] is False
    assert validation["task_outcome_satisfied"] is False


def test_authentic_but_irrelevant_output_has_same_governance_validation_meaning(
    tmp_path: Path,
) -> None:
    runtime, activation, capture, root, workspace, _ = _captured(
        tmp_path,
        "G31-20D-IRRELEVANT",
        runner=RecordingRunner(stdout="Authentic but irrelevant bounded text."),
    )
    validation = _validate(runtime, activation, capture, root, workspace)

    assert validation["validation_status"] == RESULT_VALIDATED
    assert validation["task_outcome_satisfaction_evaluated"] is False
    assert validation["task_outcome_satisfied"] is False


def test_forbidden_operation_output_fails_policy_validation(tmp_path: Path) -> None:
    runtime, activation, capture, root, workspace, _ = _captured(
        tmp_path, "G31-20D-FORBIDDEN"
    )
    canonical = bridge.result_validation.validate_worker_result

    def forbidden(**kwargs):
        return _call_canonical_with_semantically_invalid_capture(canonical, kwargs)

    bridge.result_validation.validate_worker_result = forbidden
    try:
        validation = _validate(runtime, activation, capture, root, workspace)
    finally:
        bridge.result_validation.validate_worker_result = canonical

    assert validation["validation_status"] == FAILED_CLOSED
    assert validation["result_validated"] is False


def test_substituted_validation_requirements_fail_closed(tmp_path: Path) -> None:
    runtime, activation, capture, root, workspace, _ = _captured(
        tmp_path, "G31-20D-CRITERIA"
    )
    changed = deepcopy(capture["worker_result_capture_artifact"])
    changed["validation_requirements"] = ["SUBSTITUTED_EXPECTED_CRITERIA"]
    changed["artifact_hash"] = replay_hash(
        {key: value for key, value in changed.items() if key != "artifact_hash"}
    )
    result = validate_worker_result(
        worker_result_validation_id="G31-20D-SUBSTITUTED-CRITERIA",
        worker_result_capture_artifact=changed,
        worker_result_capture_replay_reference=capture[
            "worker_result_capture_replay_reference"
        ],
        validated_by="G31_20D_TEST",
        validated_at="2026-07-18T06:00:00Z",
        replay_dir=root / "substituted-criteria-validation",
    )

    assert result["validation_status"] == FAILED_CLOSED
    assert "result capture mismatch" in result["failure_reason"]


def test_duplicate_validation_fails_closed_without_task_outcome_claim(
    tmp_path: Path,
) -> None:
    runtime, activation, capture, root, workspace, _ = _captured(
        tmp_path, "G31-20D-DUPLICATE"
    )
    first = _validate(runtime, activation, capture, root, workspace, name="one-validation")
    second = _validate(runtime, activation, capture, root, workspace, name="one-validation")

    assert first["validation_status"] == RESULT_VALIDATED
    assert second["validation_status"] == FAILED_CLOSED
    assert second["task_outcome_satisfaction_evaluated"] is False
    assert second["task_outcome_satisfied"] is False
