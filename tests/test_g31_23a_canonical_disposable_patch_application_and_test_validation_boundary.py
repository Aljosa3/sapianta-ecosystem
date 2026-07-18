from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import os
import subprocess
from types import SimpleNamespace

import pytest

from aigol.cli import aicli
from aigol.runtime import (
    codex_satisfied_outcome_disposable_validation_binding_runtime as boundary,
)
from aigol.runtime import validation_command_runner_runtime
from aigol.runtime.codex_satisfied_outcome_disposable_validation_binding_runtime import (
    COMPLETED,
    FAILED_CLOSED,
    execute_disposable_patch_validation,
    prepare_disposable_patch_validation_review,
    reconstruct_disposable_patch_validation_outcome,
    record_disposable_patch_validation_human_decision,
)
from aigol.runtime.codex_task_outcome_human_review_runtime import (
    REWORK_REQUESTED,
    TASK_OUTCOME_SATISFIED,
    TASK_OUTCOME_UNSATISFIED,
    derive_unified_diff_postimages,
    prepare_codex_task_outcome_review,
    record_codex_task_outcome_human_decision,
)
from aigol.runtime.human_decision_runtime import APPROVE, REJECT
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash
from aigol.runtime.validation_command_runner_runtime import (
    create_validation_command_request,
    execute_validation_command,
)
from test_g31_17b_governed_execution_to_codex_worker_activation_binding import (
    RecordingRunner,
    _activate_direct,
)
from test_g31_18_codex_transport_to_worker_result_capture_binding import _capture
from test_g31_20_codex_result_to_semantic_validation_binding import _validate
from test_g31_20f_disposable_repository_scope_grounding_fixture_contract import (
    CREATED_AT,
    _workspace,
)
from test_g31_22c_task_outcome_criteria_unified_diff_alignment import (
    ALIGNMENT_REQUEST,
)


VALID_PATCH = (
    "--- a/aigol/runtime/human_interface.py\n"
    "+++ b/aigol/runtime/human_interface.py\n"
    "@@ -1,2 +1,2 @@\n"
    " def render_summary(value):\n"
    "-    return f'Status: {value}'\n"
    "+    return f'Summary: {value}'\n"
)
PREIMAGE_MISMATCH_PATCH = VALID_PATCH.replace(
    "return f'Status: {value}'", 'return f"Status: {value}"'
)
TRAILING_WHITESPACE_PATCH = VALID_PATCH.replace(
    "return f'Summary: {value}'", "return f'Summary: {value}'  "
)


def _git_baseline(workspace: Path) -> None:
    commands = (
        ["git", "init"],
        ["git", "config", "user.name", "G31 Fixture"],
        ["git", "config", "user.email", "g31@example.invalid"],
        ["git", "add", "aigol/runtime/human_interface.py", "tests/test_human_interface.py"],
        ["git", "commit", "-m", "fixture baseline"],
    )
    for command in commands:
        subprocess.run(
            command,
            cwd=workspace,
            check=True,
            capture_output=True,
            text=True,
            shell=False,
        )


def _fixture(
    tmp_path: Path,
    session: str,
    *,
    patch: str = VALID_PATCH,
    failing_test: bool = False,
) -> dict:
    workspace = _workspace(tmp_path, name=f"{session}-source")
    if failing_test:
        (workspace / "tests" / "test_human_interface.py").write_text(
            "from aigol.runtime.human_interface import render_summary\n\n"
            "def test_render_summary():\n"
            "    assert render_summary('ready') == 'Other: ready'\n",
            encoding="utf-8",
        )
    _git_baseline(workspace)
    runtime_root = tmp_path / f"{session}-runtime"
    inputs = iter([ALIGNMENT_REQUEST, "/send", "/approve", "/approve", "/exit"])
    previous = Path.cwd()
    os.chdir(workspace)
    try:
        result = aicli.run_reference_uhi_session(
            session_id=session,
            created_at=CREATED_AT,
            runtime_root=runtime_root,
            workspace=workspace,
            input_reader=lambda _prompt: next(inputs),
            output_writer=lambda _line: None,
        )
    finally:
        os.chdir(previous)
    runtime = result["runtime_result"]
    root = runtime_root / session
    runner = RecordingRunner(stdout=patch)
    activation = _activate_direct(
        runtime, root, workspace, root / "activation", runner
    )
    capture = _capture(runtime, activation, root, workspace)
    validation = _validate(runtime, activation, capture, root, workspace)
    review = prepare_codex_task_outcome_review(
        result_capture_binding_capture=capture,
        validation_binding_capture=validation,
        activation_capture=activation,
        governed_execution_capture=runtime["governed_worker_execution_capture"],
        execution_candidate_capture=runtime["worker_execution_candidate_capture"],
        session_root=root,
        workspace=workspace,
        prepared_at=CREATED_AT,
        replay_dir=root / "task-outcome-review",
    )
    return {
        "runtime": runtime,
        "activation": activation,
        "capture": capture,
        "validation": validation,
        "review": review,
        "root": root,
        "workspace": workspace,
        "runner": runner,
        "disposable": tmp_path / f"{session}-disposable",
    }


def _task_decision(values: dict, outcome: str = TASK_OUTCOME_SATISFIED) -> dict:
    runtime = values["runtime"]
    return record_codex_task_outcome_human_decision(
        review_capture=values["review"],
        task_outcome_decision=outcome,
        decision_reason=f"Human selected {outcome} for the exact fixture output.",
        decided_by="human.task-reviewer",
        decided_at=CREATED_AT,
        result_capture_binding_capture=values["capture"],
        validation_binding_capture=values["validation"],
        activation_capture=values["activation"],
        governed_execution_capture=runtime["governed_worker_execution_capture"],
        execution_candidate_capture=runtime["worker_execution_candidate_capture"],
        session_root=values["root"],
        workspace=values["workspace"],
        human_decision_replay_dir=values["root"] / f"task-decision-{outcome}",
    )


def _prepare(values: dict, task_decision: dict, *, name: str = "application-review") -> dict:
    runtime = values["runtime"]
    return prepare_disposable_patch_validation_review(
        task_outcome_decision_capture=task_decision,
        review_capture=values["review"],
        result_capture_binding_capture=values["capture"],
        validation_binding_capture=values["validation"],
        activation_capture=values["activation"],
        governed_execution_capture=runtime["governed_worker_execution_capture"],
        execution_candidate_capture=runtime["worker_execution_candidate_capture"],
        session_root=values["root"],
        source_workspace=values["workspace"],
        disposable_workspace=values["disposable"],
        prepared_at=CREATED_AT,
        replay_dir=values["root"] / name,
    )


def _application_decision(
    values: dict,
    task_decision: dict,
    prepared: dict,
    *,
    decision: str = APPROVE,
    name: str = "application-decision",
) -> dict:
    runtime = values["runtime"]
    return record_disposable_patch_validation_human_decision(
        review_binding_capture=prepared,
        decision=decision,
        decision_reason=f"Human selected {decision} for disposable apply and test only.",
        decided_by="human.disposable-validator",
        decided_at=CREATED_AT,
        human_decision_replay_dir=values["root"] / name,
        task_outcome_decision_capture=task_decision,
        review_capture=values["review"],
        result_capture_binding_capture=values["capture"],
        validation_binding_capture=values["validation"],
        activation_capture=values["activation"],
        governed_execution_capture=runtime["governed_worker_execution_capture"],
        execution_candidate_capture=runtime["worker_execution_candidate_capture"],
        session_root=values["root"],
        source_workspace=values["workspace"],
    )


def _execute(
    values: dict,
    task_decision: dict,
    prepared: dict,
    application_decision: dict,
    *,
    name: str = "application-outcome",
) -> dict:
    runtime = values["runtime"]
    return execute_disposable_patch_validation(
        review_binding_capture=prepared,
        application_decision_capture=application_decision,
        task_outcome_decision_capture=task_decision,
        review_capture=values["review"],
        result_capture_binding_capture=values["capture"],
        validation_binding_capture=values["validation"],
        activation_capture=values["activation"],
        governed_execution_capture=runtime["governed_worker_execution_capture"],
        execution_candidate_capture=runtime["worker_execution_candidate_capture"],
        session_root=values["root"],
        source_workspace=values["workspace"],
        executed_by="G31_23A_TEST_OPERATOR",
        executed_at=CREATED_AT,
        replay_dir=values["root"] / name,
    )


def _sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def test_valid_v2_satisfied_patch_applies_and_runs_one_grounded_test(
    tmp_path: Path,
) -> None:
    values = _fixture(tmp_path, "G31-23A-SUCCESS")
    source_file = values["workspace"] / "aigol/runtime/human_interface.py"
    test_file = values["workspace"] / "tests/test_human_interface.py"
    before = {_sha(source_file), _sha(test_file)}
    task_decision = _task_decision(values)
    prepared = _prepare(values, task_decision)
    plan = prepared["disposable_patch_validation_plan_artifact"]
    approval = prepared[
        "disposable_patch_validation_approval_required_artifact"
    ]["approval_resume_packet"]["approval_request_artifact"]
    assert plan["allowed_patch_targets"] == [
        "aigol/runtime/human_interface.py",
        "tests/test_human_interface.py",
    ]
    assert plan["changed_paths"] == ["aigol/runtime/human_interface.py"]
    assert plan["grounded_test_target"] == "tests/test_human_interface.py"
    assert plan["disposable_workspace"] == str(values["disposable"])
    assert approval["approval_scope"] == boundary.APPROVAL_SCOPE
    assert approval["main_repository_mutation_allowed"] is False
    assert approval["arbitrary_command_execution_allowed"] is False
    assert approval["package_installation_allowed"] is False
    assert approval["network_access_allowed"] is False
    assert approval["provider_invocation_allowed"] is False
    assert approval["codex_execution_allowed"] is False
    human = _application_decision(values, task_decision, prepared)
    outcome = _execute(values, task_decision, prepared, human)
    reconstructed = reconstruct_disposable_patch_validation_outcome(
        outcome_capture=outcome,
        review_binding_capture=prepared,
        application_decision_capture=human,
        task_outcome_decision_capture=task_decision,
        review_capture=values["review"],
        result_capture_binding_capture=values["capture"],
        validation_binding_capture=values["validation"],
        activation_capture=values["activation"],
        governed_execution_capture=values["runtime"]["governed_worker_execution_capture"],
        execution_candidate_capture=values["runtime"]["worker_execution_candidate_capture"],
        session_root=values["root"],
        source_workspace=values["workspace"],
    )

    assert outcome["execution_status"] == COMPLETED
    assert outcome["task_outcome_satisfaction_evaluated"] is True
    assert outcome["task_outcome_satisfied"] is True
    assert outcome["task_outcome_criteria_version"].endswith("V2")
    assert outcome["disposable_patch_application_authorized"] is True
    assert outcome["disposable_patch_applied"] is True
    assert outcome["main_repository_mutated"] is False
    assert outcome["content_validation_performed"] is True
    assert outcome["content_validation_passed"] is True
    assert outcome["grounded_test_execution_performed"] is True
    assert outcome["grounded_test_validation_passed"] is True
    assert outcome["generated_content_manifest_created"] is False
    assert outcome["ready_for_generated_content_acceptance"] is False
    assert outcome["result_accepted"] is False
    assert outcome["repository_mutation_authorized"] is False
    assert outcome["provider_invoked"] is False
    assert outcome["codex_process_started"] is False
    assert outcome["commit_created"] is False
    assert reconstructed["execution_status"] == COMPLETED
    assert "Summary: {value}" in (
        values["disposable"] / "aigol/runtime/human_interface.py"
    ).read_text(encoding="utf-8")
    assert {_sha(source_file), _sha(test_file)} == before
    command_result = outcome["grounded_test_validation_capture"][
        "validation_command_result_artifact"
    ]
    assert command_result["command"] == [
        "python", "-m", "pytest", "tests/test_human_interface.py"
    ]
    assert command_result["shell_execution_used"] is False
    assert command_result["maximum_captured_output_bytes"] == 4096


def test_historic_v1_unsatisfied_result_is_explicitly_ineligible() -> None:
    packet = {
        "pre_execution_task_outcome_criteria": {
            "criteria_version": "G31_PRE_EXECUTION_TASK_OUTCOME_CRITERIA_V1"
        }
    }
    decision = {
        "task_outcome_decision": TASK_OUTCOME_UNSATISFIED,
        "task_outcome_satisfaction_evaluated": True,
        "task_outcome_satisfied": False,
    }
    with pytest.raises(FailClosedRuntimeError, match="requires V2"):
        boundary._require_v2_satisfied(packet, decision)


@pytest.mark.parametrize("outcome", (TASK_OUTCOME_UNSATISFIED, REWORK_REQUESTED))
def test_unsatisfied_and_rework_results_cannot_prepare_application(
    tmp_path: Path, outcome: str
) -> None:
    values = _fixture(tmp_path, f"G31-23A-{outcome}")
    decision = _task_decision(values, outcome)
    with pytest.raises(FailClosedRuntimeError, match="TASK_OUTCOME_SATISFIED"):
        _prepare(values, decision)
    assert not values["disposable"].exists()


@pytest.mark.parametrize(
    "patch",
    (
        "not a diff\n",
        "--- a/docs/unapproved.md\n+++ b/docs/unapproved.md\n@@ -1 +1 @@\n-old\n+new\n",
        "--- a/../escape.py\n+++ b/../escape.py\n@@ -1 +1 @@\n-old\n+new\n",
        "--- /tmp/escape.py\n+++ /tmp/escape.py\n@@ -1 +1 @@\n-old\n+new\n",
        "--- a/aigol/runtime/human_interface.py\n+++ b/tests/test_human_interface.py\n@@ -1 +1 @@\n-old\n+new\n",
        "--- /dev/null\n+++ b/aigol/runtime/human_interface.py\n@@ -0,0 +1 @@\n+new\n",
        "GIT binary patch\nliteral 1\nA\n",
    ),
)
def test_malformed_substituted_ungrounded_and_unsupported_patches_fail_preflight(
    patch: str,
) -> None:
    with pytest.raises(FailClosedRuntimeError):
        derive_unified_diff_postimages(
            patch,
            preimages={"aigol/runtime/human_interface.py": "old\n"},
            allowed_targets={"aigol/runtime/human_interface.py"},
        )


def test_preimage_context_mismatch_prevents_copy_application_and_tests(
    tmp_path: Path,
) -> None:
    values = _fixture(
        tmp_path, "G31-23A-PREFLIGHT", patch=PREIMAGE_MISMATCH_PATCH
    )
    decision = _task_decision(values)
    with pytest.raises(FailClosedRuntimeError, match="preimage context mismatch"):
        _prepare(values, decision)
    assert not values["disposable"].exists()


def test_repository_preimage_drift_rejects_before_disposable_mutation(
    tmp_path: Path,
) -> None:
    values = _fixture(tmp_path, "G31-23A-DRIFT")
    decision = _task_decision(values)
    (values["workspace"] / "aigol/runtime/human_interface.py").write_text(
        "def render_summary(value):\n    return value\n", encoding="utf-8"
    )
    with pytest.raises(FailClosedRuntimeError):
        _prepare(values, decision)
    assert not values["disposable"].exists()


def test_changed_patch_capture_and_cross_session_review_fail_before_copy(
    tmp_path: Path,
) -> None:
    values = _fixture(tmp_path, "G31-23A-SUBSTITUTION")
    decision = _task_decision(values)
    changed = deepcopy(values["review"])
    changed["task_outcome_review_packet_artifact"]["exact_worker_output"][
        "text"
    ] += "\n"
    values["review"] = changed
    with pytest.raises(FailClosedRuntimeError):
        _prepare(values, decision)
    assert not values["disposable"].exists()

    values = _fixture(tmp_path, "G31-23A-CROSS-SESSION")
    decision = _task_decision(values)
    runtime = values["runtime"]
    with pytest.raises(FailClosedRuntimeError, match="cross-session"):
        prepare_disposable_patch_validation_review(
            task_outcome_decision_capture=decision,
            review_capture=values["review"],
            result_capture_binding_capture=values["capture"],
            validation_binding_capture=values["validation"],
            activation_capture=values["activation"],
            governed_execution_capture=runtime["governed_worker_execution_capture"],
            execution_candidate_capture=runtime["worker_execution_candidate_capture"],
            session_root=values["root"],
            source_workspace=values["workspace"],
            disposable_workspace=values["disposable"],
            prepared_at=CREATED_AT,
            replay_dir=tmp_path / "outside-session-review",
        )
    assert not values["disposable"].exists()


def test_separate_human_rejection_cannot_authorize_disposable_mutation(
    tmp_path: Path,
) -> None:
    values = _fixture(tmp_path, "G31-23A-REJECT")
    task_decision = _task_decision(values)
    prepared = _prepare(values, task_decision)
    rejected = _application_decision(
        values, task_decision, prepared, decision=REJECT
    )
    with pytest.raises(FailClosedRuntimeError, match="unused human approval"):
        _execute(values, task_decision, prepared, rejected)
    assert not values["disposable"].exists()


def test_duplicate_destination_and_one_time_authority_reuse_fail_closed(
    tmp_path: Path,
) -> None:
    values = _fixture(tmp_path, "G31-23A-ONE-TIME")
    task_decision = _task_decision(values)
    prepared = _prepare(values, task_decision)
    with pytest.raises(FailClosedRuntimeError, match="already exists"):
        _prepare(values, task_decision, name="duplicate-plan")
    human = _application_decision(values, task_decision, prepared)
    _execute(values, task_decision, prepared, human)
    with pytest.raises(FailClosedRuntimeError, match="authority already consumed"):
        _execute(values, task_decision, prepared, human, name="authority-reuse")
    with pytest.raises(FailClosedRuntimeError, match="destination already exists"):
        _execute(values, task_decision, prepared, human)


def test_application_failure_records_failure_and_does_not_run_tests(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    values = _fixture(tmp_path, "G31-23A-APPLICATION-FAILURE")
    task_decision = _task_decision(values)
    prepared = _prepare(values, task_decision)
    human = _application_decision(values, task_decision, prepared)
    monkeypatch.setattr(
        boundary,
        "execute_governed_repository_mutation",
        lambda **_kwargs: {
            "execution_status": FAILED_CLOSED,
            "failure_reason": "injected bounded application failure",
        },
    )
    outcome = _execute(values, task_decision, prepared, human)

    assert outcome["execution_status"] == FAILED_CLOSED
    assert outcome["disposable_patch_applied"] is False
    assert outcome["content_validation_passed"] is False
    assert outcome["grounded_test_execution_performed"] is False
    assert outcome["grounded_test_validation_capture"] is None
    assert "application failure" in outcome["failure_reason"]


def test_content_validation_failure_stops_before_tests(
    tmp_path: Path,
) -> None:
    values = _fixture(
        tmp_path, "G31-23A-CONTENT-FAILURE", patch=TRAILING_WHITESPACE_PATCH
    )
    task_decision = _task_decision(values)
    prepared = _prepare(values, task_decision)
    human = _application_decision(values, task_decision, prepared)
    outcome = _execute(values, task_decision, prepared, human)

    assert outcome["execution_status"] == FAILED_CLOSED
    assert outcome["disposable_patch_applied"] is True
    assert outcome["content_validation_performed"] is True
    assert outcome["content_validation_passed"] is False
    assert outcome["grounded_test_execution_performed"] is False
    assert outcome["ready_for_generated_content_acceptance"] is False


def test_grounded_test_failure_is_preserved_without_retry_or_acceptance(
    tmp_path: Path,
) -> None:
    values = _fixture(tmp_path, "G31-23A-TEST-FAILURE", failing_test=True)
    task_decision = _task_decision(values)
    prepared = _prepare(values, task_decision)
    human = _application_decision(values, task_decision, prepared)
    outcome = _execute(values, task_decision, prepared, human)

    assert outcome["execution_status"] == FAILED_CLOSED
    assert outcome["disposable_patch_applied"] is True
    assert outcome["content_validation_passed"] is True
    assert outcome["grounded_test_execution_performed"] is True
    assert outcome["grounded_test_validation_passed"] is False
    assert outcome["outcome_artifact"]["automatic_retry_performed"] is False
    assert outcome["result_accepted"] is False
    assert outcome["repository_mutation_authorized"] is False
    assert outcome["ready_for_generated_content_acceptance"] is False


def test_validation_command_capture_is_bounded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    request = create_validation_command_request(
        request_id="G31-23A-BOUNDED-OUTPUT",
        command=["python", "-m", "pytest", "tests/test_human_interface.py"],
        cwd=str(tmp_path),
        requested_by="G31_23A_TEST_OPERATOR",
        requested_at=CREATED_AT,
        replay_references=["/tmp/g31-23a-bounded-source"],
        replay_hashes=[replay_hash({"bounded": True})],
        timeout_seconds=30,
    )
    monkeypatch.setattr(
        validation_command_runner_runtime.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=0,
            stdout="é" * 3000,
            stderr="x" * 5000,
        ),
    )
    capture = execute_validation_command(
        request_artifact=request,
        executed_by="G31_23A_TEST_OPERATOR",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "bounded-output-replay",
    )
    result = capture["validation_command_result_artifact"]

    assert result["stdout_byte_length"] == 6000
    assert result["stderr_byte_length"] == 5000
    assert len(result["stdout"].encode("utf-8")) <= 4096
    assert len(result["stderr"].encode("utf-8")) <= 4096
    assert result["stdout_truncated"] is True
    assert result["stderr_truncated"] is True
