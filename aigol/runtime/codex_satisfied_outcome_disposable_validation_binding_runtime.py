"""G31 binding from one satisfied V2 CODEX diff to disposable validation."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import shutil
import tempfile
from typing import Any

from aigol.runtime.codex_task_outcome_human_review_runtime import (
    TASK_OUTCOME_SATISFIED,
    derive_unified_diff_postimages,
    reconstruct_codex_task_outcome_human_decision,
    reconstruct_codex_task_outcome_review,
)
from aigol.runtime.codex_worker_activation_binding_runtime import (
    reconstruct_codex_worker_activation_binding,
)
from aigol.runtime.conversation_to_ppp_handoff_execution import HUMAN_APPROVAL_REQUIRED
from aigol.runtime.governed_repository_mutation_runtime import (
    APPROVED,
    GOVERNED_REPOSITORY_MUTATION_COMPLETED,
    create_governed_repository_mutation_approval,
    create_governed_repository_mutation_proposal,
    execute_governed_repository_mutation,
    reconstruct_governed_repository_mutation_replay,
)
from aigol.runtime.human_decision_runtime import (
    APPROVE,
    reconstruct_human_decision_replay,
    record_human_decision,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import (
    load_json,
    replay_hash,
    verify_replay_hash,
    write_json_immutable,
)
from aigol.runtime.validation_command_runner_runtime import (
    VALIDATION_COMMAND_COMPLETED,
    VALIDATION_COMMAND_FAILED,
    create_validation_command_request,
    execute_validation_command,
    reconstruct_validation_command_replay,
)


RUNTIME_VERSION = "G31_23A_DISPOSABLE_PATCH_APPLICATION_AND_TEST_VALIDATION_V1"
PLAN_ARTIFACT_V1 = "DISPOSABLE_PATCH_VALIDATION_PLAN_ARTIFACT_V1"
APPROVAL_REQUIRED_ARTIFACT_V1 = (
    "DISPOSABLE_PATCH_VALIDATION_APPROVAL_REQUIRED_ARTIFACT_V1"
)
APPROVAL_REQUEST_ARTIFACT_V1 = (
    "DISPOSABLE_PATCH_VALIDATION_APPROVAL_REQUEST_ARTIFACT_V1"
)
OUTCOME_ARTIFACT_V1 = "DISPOSABLE_PATCH_VALIDATION_OUTCOME_ARTIFACT_V1"
APPROVAL_SCOPE = (
    "APPLY_REVIEWED_PATCH_AND_RUN_GROUNDED_TESTS_IN_DISPOSABLE_WORKSPACE_ONLY"
)
CRITERIA_VERSION = "G31_PRE_EXECUTION_TASK_OUTCOME_CRITERIA_V2"
READY = "DISPOSABLE_PATCH_VALIDATION_APPROVAL_REQUIRED"
COMPLETED = "DISPOSABLE_PATCH_AND_TEST_VALIDATION_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"
TEST_TIMEOUT_SECONDS = 30
PLAN_REPLAY_STEPS = (
    "disposable_patch_validation_plan_recorded",
    "disposable_patch_validation_approval_required_recorded",
)
OUTCOME_REPLAY_STEP = "disposable_patch_validation_outcome_recorded"
DENIED_AUTHORITIES = {
    "main_repository_mutation_allowed": False,
    "arbitrary_command_execution_allowed": False,
    "package_installation_allowed": False,
    "network_access_allowed": False,
    "provider_invocation_allowed": False,
    "codex_execution_allowed": False,
    "commit_allowed": False,
    "deployment_allowed": False,
    "release_allowed": False,
}


def prepare_disposable_patch_validation_review(
    *,
    task_outcome_decision_capture: dict[str, Any],
    review_capture: dict[str, Any],
    result_capture_binding_capture: dict[str, Any],
    validation_binding_capture: dict[str, Any],
    activation_capture: dict[str, Any],
    governed_execution_capture: dict[str, Any],
    execution_candidate_capture: dict[str, Any],
    session_root: str | Path,
    source_workspace: str | Path,
    disposable_workspace: str | Path,
    prepared_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Prepare one non-mutating review for disposable application and testing."""

    root = Path(session_root).resolve()
    replay_path = Path(replay_dir).resolve()
    disposable = _disposable_destination(disposable_workspace, source_workspace)
    if not replay_path.is_relative_to(root):
        raise FailClosedRuntimeError("disposable validation review is cross-session")
    _ensure_plan_replay_available(replay_path)
    if disposable.exists():
        raise FailClosedRuntimeError("disposable validation workspace already exists")
    sources = _reconstruct_sources(
        task_outcome_decision_capture=task_outcome_decision_capture,
        review_capture=review_capture,
        result_capture_binding_capture=result_capture_binding_capture,
        validation_binding_capture=validation_binding_capture,
        activation_capture=activation_capture,
        governed_execution_capture=governed_execution_capture,
        execution_candidate_capture=execution_candidate_capture,
        session_root=root,
        source_workspace=source_workspace,
    )
    plan = _plan_artifact(
        sources=sources,
        disposable_workspace=disposable,
        prepared_at=_required(prepared_at, "prepared_at"),
        replay_reference=str(replay_path),
    )
    _reject_duplicate_plan(root, plan["plan_identity"])
    approval_required = _approval_required(plan)
    _persist_plan_step(replay_path, 0, plan)
    _persist_plan_step(replay_path, 1, approval_required)
    return {
        "runtime_version": RUNTIME_VERSION,
        "boundary_status": READY,
        "disposable_patch_validation_plan_artifact": deepcopy(plan),
        "disposable_patch_validation_approval_required_artifact": deepcopy(
            approval_required
        ),
        "disposable_patch_validation_replay_reference": str(replay_path),
        "replay_artifact_count": 2,
        "disposable_patch_application_authorized": False,
        "disposable_patch_applied": False,
        "grounded_test_execution_performed": False,
        "result_accepted": False,
        "repository_mutation_authorized": False,
        "main_repository_mutated": False,
        "provider_invoked": False,
        "codex_process_started": False,
    }


def reconstruct_disposable_patch_validation_review(
    *,
    review_binding_capture: dict[str, Any],
    task_outcome_decision_capture: dict[str, Any],
    review_capture: dict[str, Any],
    result_capture_binding_capture: dict[str, Any],
    validation_binding_capture: dict[str, Any],
    activation_capture: dict[str, Any],
    governed_execution_capture: dict[str, Any],
    execution_candidate_capture: dict[str, Any],
    session_root: str | Path,
    source_workspace: str | Path,
) -> dict[str, Any]:
    root = Path(session_root).resolve()
    replay_path = Path(
        review_binding_capture.get(
            "disposable_patch_validation_replay_reference", ""
        )
    ).resolve()
    if not replay_path.is_relative_to(root):
        raise FailClosedRuntimeError("disposable validation review Replay is cross-session")
    wrappers = _load_plan_wrappers(replay_path)
    plan, approval_required = (wrapper["artifact"] for wrapper in wrappers)
    if review_binding_capture.get("disposable_patch_validation_plan_artifact") != plan:
        raise FailClosedRuntimeError("disposable validation plan capture mismatch")
    if review_binding_capture.get(
        "disposable_patch_validation_approval_required_artifact"
    ) != approval_required:
        raise FailClosedRuntimeError("disposable validation approval capture mismatch")
    sources = _reconstruct_sources(
        task_outcome_decision_capture=task_outcome_decision_capture,
        review_capture=review_capture,
        result_capture_binding_capture=result_capture_binding_capture,
        validation_binding_capture=validation_binding_capture,
        activation_capture=activation_capture,
        governed_execution_capture=governed_execution_capture,
        execution_candidate_capture=execution_candidate_capture,
        session_root=root,
        source_workspace=source_workspace,
    )
    expected = _plan_artifact(
        sources=sources,
        disposable_workspace=Path(plan.get("disposable_workspace", "")).resolve(),
        prepared_at=plan.get("prepared_at", ""),
        replay_reference=str(replay_path),
    )
    if plan != expected or approval_required != _approval_required(expected):
        raise FailClosedRuntimeError(
            "disposable validation lineage, patch, criteria, preimage, or scope was substituted"
        )
    return {
        "plan": deepcopy(plan),
        "approval_required": deepcopy(approval_required),
        "sources": sources,
        "replay_reference": str(replay_path),
        "replay_hash": replay_hash(wrappers),
        "replay_artifact_count": 2,
    }


def record_disposable_patch_validation_human_decision(
    *,
    review_binding_capture: dict[str, Any],
    decision: str,
    decision_reason: str,
    decided_by: str,
    decided_at: str,
    human_decision_replay_dir: str | Path,
    task_outcome_decision_capture: dict[str, Any],
    review_capture: dict[str, Any],
    result_capture_binding_capture: dict[str, Any],
    validation_binding_capture: dict[str, Any],
    activation_capture: dict[str, Any],
    governed_execution_capture: dict[str, Any],
    execution_candidate_capture: dict[str, Any],
    session_root: str | Path,
    source_workspace: str | Path,
) -> dict[str, Any]:
    root = Path(session_root).resolve()
    decision_path = Path(human_decision_replay_dir).resolve()
    if not decision_path.is_relative_to(root):
        raise FailClosedRuntimeError("disposable validation human decision is cross-session")
    reconstructed = reconstruct_disposable_patch_validation_review(
        review_binding_capture=review_binding_capture,
        task_outcome_decision_capture=task_outcome_decision_capture,
        review_capture=review_capture,
        result_capture_binding_capture=result_capture_binding_capture,
        validation_binding_capture=validation_binding_capture,
        activation_capture=activation_capture,
        governed_execution_capture=governed_execution_capture,
        execution_candidate_capture=execution_candidate_capture,
        session_root=root,
        source_workspace=source_workspace,
    )
    approval_required = reconstructed["approval_required"]
    _reject_existing_application_decision(root, approval_required["artifact_hash"])
    return record_human_decision(
        human_decision_id=(
            f"{reconstructed['plan']['plan_id']}:HUMAN-DISPOSABLE-VALIDATION-DECISION"
        ),
        approval_required_artifact=approval_required,
        decision=decision,
        decision_reason=_required(decision_reason, "decision_reason"),
        decided_by=_required(decided_by, "decided_by"),
        decided_at=_required(decided_at, "decided_at"),
        replay_dir=decision_path,
    )


def execute_disposable_patch_validation(
    *,
    review_binding_capture: dict[str, Any],
    application_decision_capture: dict[str, Any],
    task_outcome_decision_capture: dict[str, Any],
    review_capture: dict[str, Any],
    result_capture_binding_capture: dict[str, Any],
    validation_binding_capture: dict[str, Any],
    activation_capture: dict[str, Any],
    governed_execution_capture: dict[str, Any],
    execution_candidate_capture: dict[str, Any],
    session_root: str | Path,
    source_workspace: str | Path,
    executed_by: str,
    executed_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Copy, apply, content-check, and test one exact approved V2 patch."""

    root = Path(session_root).resolve()
    outcome_path = Path(replay_dir).resolve()
    if not outcome_path.is_relative_to(root):
        raise FailClosedRuntimeError("disposable validation outcome is cross-session")
    _ensure_outcome_replay_available(outcome_path)
    reconstructed = reconstruct_disposable_patch_validation_review(
        review_binding_capture=review_binding_capture,
        task_outcome_decision_capture=task_outcome_decision_capture,
        review_capture=review_capture,
        result_capture_binding_capture=result_capture_binding_capture,
        validation_binding_capture=validation_binding_capture,
        activation_capture=activation_capture,
        governed_execution_capture=governed_execution_capture,
        execution_candidate_capture=execution_candidate_capture,
        session_root=root,
        source_workspace=source_workspace,
    )
    plan = reconstructed["plan"]
    human = _validate_application_decision(
        application_decision_capture,
        reconstructed["approval_required"],
        root,
    )
    _reject_authority_reuse(root, human["artifact_hash"])
    disposable = Path(plan["disposable_workspace"]).resolve()
    status = FAILED_CLOSED
    failure_reason: str | None = None
    governed_capture: dict[str, Any] | None = None
    test_capture: dict[str, Any] | None = None
    application_attempted = False
    patch_applied = False
    content_performed = False
    content_passed = False
    test_performed = False
    test_passed = False
    try:
        if disposable.exists():
            raise FailClosedRuntimeError("disposable validation workspace already exists")
        _copy_repository(Path(plan["source_workspace"]), disposable)
        _verify_workspace_hashes(disposable, plan["preimage_sha256"])
        proposal = create_governed_repository_mutation_proposal(
            proposal_id=f"{plan['plan_id']}:DISPOSABLE-MUTATION-PROPOSAL",
            original_request_reference=plan["original_request_sha256"],
            resolved_intent_reference=plan["task_outcome_decision_hash"],
            file_mutations=deepcopy(plan["file_mutations"]),
            validation_command=["git", "diff", "--check"],
            replay_references=[
                reconstructed["replay_reference"],
                application_decision_capture["human_decision_replay_reference"],
            ],
            replay_hashes=[
                reconstructed["replay_hash"],
                reconstruct_human_decision_replay(
                    application_decision_capture["human_decision_replay_reference"]
                )["replay_hash"],
            ],
            created_by=_required(executed_by, "executed_by"),
            created_at=_required(executed_at, "executed_at"),
        )
        approval = create_governed_repository_mutation_approval(
            approval_id=f"{plan['plan_id']}:DISPOSABLE-MUTATION-APPROVAL",
            proposal_artifact=proposal,
            decision=APPROVED,
            approved_by=human["decided_by"],
            approved_at=human["decided_at"],
            replay_references=[
                application_decision_capture["human_decision_replay_reference"]
            ],
            replay_hashes=[human["artifact_hash"]],
        )
        application_attempted = True
        content_performed = True
        governed_capture = execute_governed_repository_mutation(
            execution_id=f"{plan['plan_id']}:DISPOSABLE-MUTATION",
            request_artifact=_hashed_artifact({
                "request_id": f"{plan['plan_id']}:REQUEST",
                "approval_scope": APPROVAL_SCOPE,
                "plan_hash": plan["artifact_hash"],
            }),
            intent_artifact=_hashed_artifact({
                "intent_id": f"{plan['plan_id']}:INTENT",
                "intent": APPROVAL_SCOPE,
                "patch_sha256": plan["patch_sha256"],
            }),
            workflow_artifact=_hashed_artifact({
                "workflow_id": "GOVERNED_REPOSITORY_MUTATION"
            }),
            repository_context_artifact=_hashed_artifact({
                "context_id": f"{plan['plan_id']}:DISPOSABLE-CONTEXT",
                "target_paths": plan["changed_paths"],
                "context_fresh": True,
                "disposable_workspace": str(disposable),
            }),
            proposal_artifact=proposal,
            approval_artifact=approval,
            repository_root=disposable,
            executed_by=_required(executed_by, "executed_by"),
            executed_at=_required(executed_at, "executed_at"),
            replay_dir=outcome_path / "governed_repository_mutation",
        )
        patch_applied = _workspace_hashes_match(disposable, plan["postimage_sha256"])
        content_passed = (
            governed_capture["execution_status"]
            == GOVERNED_REPOSITORY_MUTATION_COMPLETED
            and patch_applied
        )
        if not content_passed:
            raise FailClosedRuntimeError(
                governed_capture.get("failure_reason")
                or "disposable content validation failed closed"
            )
        test_request = create_validation_command_request(
            request_id=f"{plan['plan_id']}:GROUNDED-TEST",
            command=deepcopy(plan["grounded_test_command"]),
            cwd=str(disposable),
            requested_by=_required(executed_by, "executed_by"),
            requested_at=_required(executed_at, "executed_at"),
            replay_references=[
                governed_capture["governed_repository_mutation_replay_reference"]
            ],
            replay_hashes=[
                governed_capture["governed_repository_mutation_outcome"]["artifact_hash"]
            ],
            timeout_seconds=TEST_TIMEOUT_SECONDS,
        )
        test_capture = execute_validation_command(
            request_artifact=test_request,
            executed_by=_required(executed_by, "executed_by"),
            executed_at=_required(executed_at, "executed_at"),
            replay_dir=outcome_path / "grounded_test_validation",
        )
        command_status = test_capture["validation_command_result_artifact"][
            "command_status"
        ]
        test_performed = command_status in {
            VALIDATION_COMMAND_COMPLETED,
            VALIDATION_COMMAND_FAILED,
        }
        test_passed = (
            command_status == VALIDATION_COMMAND_COMPLETED
            and test_capture["validation_command_result_artifact"]["exit_code"] == 0
        )
        if not test_passed:
            raise FailClosedRuntimeError("grounded focused test validation failed")
        status = COMPLETED
    except Exception as exc:
        failure_reason = _failure_reason(exc)
    source_unchanged = (
        _workspace_hashes_match(
            Path(plan["source_workspace"]), plan["preimage_sha256"]
        )
        and _repository_file_hashes(Path(plan["source_workspace"]))
        == plan["source_repository_snapshot_sha256"]
    )
    if not source_unchanged:
        raise FailClosedRuntimeError("source repository changed during disposable validation")
    outcome = _outcome_artifact(
        plan=plan,
        human=human,
        status=status,
        governed_capture=governed_capture,
        test_capture=test_capture,
        application_attempted=application_attempted,
        patch_applied=patch_applied,
        content_performed=content_performed,
        content_passed=content_passed,
        test_performed=test_performed,
        test_passed=test_passed,
        source_unchanged=source_unchanged,
        executed_by=executed_by,
        executed_at=executed_at,
        failure_reason=failure_reason,
    )
    _persist_outcome(outcome_path, outcome)
    return _outcome_capture(outcome, governed_capture, test_capture, outcome_path)


def reconstruct_disposable_patch_validation_outcome(
    *,
    outcome_capture: dict[str, Any],
    review_binding_capture: dict[str, Any],
    application_decision_capture: dict[str, Any],
    task_outcome_decision_capture: dict[str, Any],
    review_capture: dict[str, Any],
    result_capture_binding_capture: dict[str, Any],
    validation_binding_capture: dict[str, Any],
    activation_capture: dict[str, Any],
    governed_execution_capture: dict[str, Any],
    execution_candidate_capture: dict[str, Any],
    session_root: str | Path,
    source_workspace: str | Path,
) -> dict[str, Any]:
    root = Path(session_root).resolve()
    replay_path = Path(outcome_capture.get("outcome_replay_reference", "")).resolve()
    if not replay_path.is_relative_to(root):
        raise FailClosedRuntimeError("disposable validation outcome Replay is cross-session")
    review = reconstruct_disposable_patch_validation_review(
        review_binding_capture=review_binding_capture,
        task_outcome_decision_capture=task_outcome_decision_capture,
        review_capture=review_capture,
        result_capture_binding_capture=result_capture_binding_capture,
        validation_binding_capture=validation_binding_capture,
        activation_capture=activation_capture,
        governed_execution_capture=governed_execution_capture,
        execution_candidate_capture=execution_candidate_capture,
        session_root=root,
        source_workspace=source_workspace,
    )
    human = _validate_application_decision(
        application_decision_capture, review["approval_required"], root
    )
    wrapper = load_json(replay_path / f"000_{OUTCOME_REPLAY_STEP}.json")
    verify_replay_hash(wrapper)
    outcome = wrapper.get("artifact")
    _verify_artifact(outcome, "disposable validation outcome")
    if outcome_capture.get("outcome_artifact") != outcome:
        raise FailClosedRuntimeError("disposable validation outcome capture mismatch")
    if not all((
        outcome.get("plan_hash") == review["plan"]["artifact_hash"],
        outcome.get("application_decision_hash") == human["artifact_hash"],
        _workspace_hashes_match(
            Path(review["plan"]["source_workspace"]),
            review["plan"]["preimage_sha256"],
        ),
    )):
        raise FailClosedRuntimeError("disposable validation outcome lineage mismatch")
    if outcome.get("content_validation_passed") is True:
        reconstruct_governed_repository_mutation_replay(
            outcome["governed_repository_mutation_replay_reference"]
        )
    if outcome.get("grounded_test_execution_performed") is True:
        reconstruct_validation_command_replay(outcome["test_validation_replay_reference"])
    if outcome.get("disposable_patch_applied") is True and not _workspace_hashes_match(
        Path(review["plan"]["disposable_workspace"]),
        review["plan"]["postimage_sha256"],
    ):
        raise FailClosedRuntimeError("disposable postimage drifted")
    return {
        "execution_status": outcome["execution_status"],
        "outcome_id": outcome["outcome_id"],
        "outcome_hash": outcome["artifact_hash"],
        "replay_hash": replay_hash(wrapper),
        "replay_artifact_count": 1,
        **{
            key: outcome[key]
            for key in (
                "disposable_patch_applied",
                "content_validation_passed",
                "grounded_test_validation_passed",
                "ready_for_generated_content_acceptance",
                "result_accepted",
                "main_repository_mutated",
            )
        },
    }


def _reconstruct_sources(
    *,
    task_outcome_decision_capture: dict[str, Any],
    review_capture: dict[str, Any],
    result_capture_binding_capture: dict[str, Any],
    validation_binding_capture: dict[str, Any],
    activation_capture: dict[str, Any],
    governed_execution_capture: dict[str, Any],
    execution_candidate_capture: dict[str, Any],
    session_root: Path,
    source_workspace: str | Path,
) -> dict[str, Any]:
    source = Path(source_workspace).resolve()
    activation = reconstruct_codex_worker_activation_binding(
        activation_capture=activation_capture,
        governed_execution_capture=governed_execution_capture,
        execution_candidate_capture=execution_candidate_capture,
        session_root=session_root,
        workspace=source,
    )
    review = reconstruct_codex_task_outcome_review(
        review_capture=review_capture,
        result_capture_binding_capture=result_capture_binding_capture,
        validation_binding_capture=validation_binding_capture,
        activation_capture=activation_capture,
        governed_execution_capture=governed_execution_capture,
        execution_candidate_capture=execution_candidate_capture,
        session_root=session_root,
        workspace=source,
    )
    decision = reconstruct_codex_task_outcome_human_decision(
        decision_capture=task_outcome_decision_capture,
        review_capture=review_capture,
        result_capture_binding_capture=result_capture_binding_capture,
        validation_binding_capture=validation_binding_capture,
        activation_capture=activation_capture,
        governed_execution_capture=governed_execution_capture,
        execution_candidate_capture=execution_candidate_capture,
        session_root=session_root,
        workspace=source,
    )
    task_decision_replay = reconstruct_human_decision_replay(
        task_outcome_decision_capture["human_decision_replay_reference"]
    )
    packet = review["review_packet"]
    _require_v2_satisfied(packet, decision)
    grounding = activation["lineage"]["grounding"]
    evidence = grounding.get("target_evidence") or []
    allowed_targets = {item["target_path"] for item in evidence}
    changed_paths = set(packet["task_outcome_observations"].get("changed_paths") or [])
    if not changed_paths or not changed_paths.issubset(allowed_targets):
        raise FailClosedRuntimeError("disposable validation patch target is ungrounded")
    evidence_by_path = {item["target_path"]: item for item in evidence}
    preimages: dict[str, str] = {}
    preimage_sha256: dict[str, str] = {}
    for target in sorted(allowed_targets):
        raw = (source / target).read_bytes()
        digest = "sha256:" + sha256(raw).hexdigest()
        if digest != evidence_by_path[target].get("source_content_hash"):
            raise FailClosedRuntimeError("disposable validation repository preimage drift")
        preimage_sha256[target] = digest
        if target in changed_paths:
            try:
                preimages[target] = raw.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise FailClosedRuntimeError(
                    "disposable validation requires UTF-8 text preimages"
                ) from exc
    patch_text = packet["exact_worker_output"]["text"]
    postimages = derive_unified_diff_postimages(
        patch_text,
        preimages=preimages,
        allowed_targets=allowed_targets,
    )
    postimage_sha256 = {
        path: "sha256:" + sha256(content.encode("utf-8")).hexdigest()
        for path, content in postimages.items()
    }
    focused_tests = [
        item["target_path"] for item in evidence if item["target_role"] == "FOCUSED_TEST"
    ]
    if len(focused_tests) != 1:
        raise FailClosedRuntimeError("disposable validation requires one grounded test")
    return {
        "activation": activation,
        "review": review,
        "decision": decision,
        "task_outcome_decision_capture_hash": task_outcome_decision_capture[
            "task_outcome_decision_capture_hash"
        ],
        "task_outcome_decision_replay_reference": task_outcome_decision_capture[
            "human_decision_replay_reference"
        ],
        "task_outcome_decision_replay_hash": task_decision_replay["replay_hash"],
        "packet": packet,
        "grounding": grounding,
        "source_workspace": str(source),
        "source_repository_snapshot_sha256": _repository_file_hashes(source),
        "allowed_targets": sorted(allowed_targets),
        "changed_paths": sorted(changed_paths),
        "preimage_sha256": preimage_sha256,
        "postimage_sha256": postimage_sha256,
        "postimages": postimages,
        "patch_text": patch_text,
        "focused_test": focused_tests[0],
    }


def _require_v2_satisfied(packet: dict[str, Any], decision: dict[str, Any]) -> None:
    criteria = packet.get("pre_execution_task_outcome_criteria") or {}
    if criteria.get("criteria_version") != CRITERIA_VERSION:
        raise FailClosedRuntimeError("disposable validation requires V2 task-outcome criteria")
    if not all((
        decision.get("task_outcome_decision") == TASK_OUTCOME_SATISFIED,
        decision.get("task_outcome_satisfaction_evaluated") is True,
        decision.get("task_outcome_satisfied") is True,
        packet.get("task_outcome_satisfaction_eligible") is True,
        packet.get("required_output_type") == "UNIFIED_DIFF",
        packet.get("patch_applied") is False,
        packet.get("tests_run_against_applied_patch") is False,
    )):
        raise FailClosedRuntimeError(
            "disposable validation requires one eligible TASK_OUTCOME_SATISFIED result"
        )


def _plan_artifact(
    *, sources: dict[str, Any], disposable_workspace: Path, prepared_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    packet = sources["packet"]
    file_mutations = [
        {
            "target_path": path,
            "operation": "REPLACE_CONTENT",
            "new_content": sources["postimages"][path],
            "new_content_hash": replay_hash(sources["postimages"][path]),
            "approved": True,
        }
        for path in sources["changed_paths"]
    ]
    seed = {
        "task_outcome_decision_hash": sources[
            "task_outcome_decision_capture_hash"
        ],
        "exact_worker_output_sha256": packet["exact_worker_output"]["sha256"],
        "criteria_hash": packet["pre_execution_task_outcome_criteria"]["criteria_hash"],
        "preimage_sha256": sources["preimage_sha256"],
        "postimage_sha256": sources["postimage_sha256"],
        "source_repository_snapshot_sha256": sources[
            "source_repository_snapshot_sha256"
        ],
        "disposable_workspace": str(disposable_workspace),
    }
    identity = replay_hash(seed)
    artifact = {
        "artifact_type": PLAN_ARTIFACT_V1,
        "runtime_version": RUNTIME_VERSION,
        "plan_id": f"G31-DISPOSABLE-VALIDATION-{identity[-24:]}",
        "plan_identity": identity,
        "approval_scope": APPROVAL_SCOPE,
        "original_authorized_request": packet["original_contextual_request"],
        "original_request_sha256": "sha256:" + sha256(
            packet["original_contextual_request"].encode("utf-8")
        ).hexdigest(),
        "task_outcome_decision": TASK_OUTCOME_SATISFIED,
        "task_outcome_decision_hash": sources[
            "task_outcome_decision_capture_hash"
        ],
        "task_outcome_decision_replay_reference": sources[
            "task_outcome_decision_replay_reference"
        ],
        "task_outcome_decision_replay_hash": sources[
            "task_outcome_decision_replay_hash"
        ],
        "task_outcome_criteria_version": CRITERIA_VERSION,
        "task_outcome_criteria_hash": packet["pre_execution_task_outcome_criteria"][
            "criteria_hash"
        ],
        "patch_text": sources["patch_text"],
        "patch_sha256": "sha256:" + sha256(
            sources["patch_text"].encode("utf-8")
        ).hexdigest(),
        "allowed_patch_targets": sources["allowed_targets"],
        "changed_paths": sources["changed_paths"],
        "grounded_test_target": sources["focused_test"],
        "grounded_test_command": ["python", "-m", "pytest", sources["focused_test"]],
        "test_timeout_seconds": TEST_TIMEOUT_SECONDS,
        "source_workspace": sources["source_workspace"],
        "disposable_workspace": str(disposable_workspace),
        "source_repository_snapshot_sha256": deepcopy(
            sources["source_repository_snapshot_sha256"]
        ),
        "preimage_sha256": deepcopy(sources["preimage_sha256"]),
        "postimage_sha256": deepcopy(sources["postimage_sha256"]),
        "file_mutations": file_mutations,
        "grounding_hash": sources["grounding"]["artifact_hash"],
        "activation_replay_reference": packet["activation_binding"][
            "replay_reference"
        ],
        "activation_replay_hash": packet["activation_binding"]["replay_hash"],
        "capture_replay_reference": packet["capture_binding"]["replay_reference"],
        "capture_replay_hash": packet["capture_binding"]["replay_hash"],
        "governance_validation_replay_reference": packet[
            "governance_validation_binding"
        ]["replay_reference"],
        "governance_validation_replay_hash": packet[
            "governance_validation_binding"
        ]["replay_hash"],
        "task_outcome_review_replay_reference": packet["replay_reference"],
        "task_outcome_review_hash": packet["artifact_hash"],
        "application_owner": "AIGOL_GOVERNED_REPOSITORY_MUTATION_RUNTIME_V1",
        "test_execution_owner": "AIGOL_VALIDATION_COMMAND_RUNNER_RUNTIME_V1",
        "generated_content_manifest_created": False,
        "generated_content_acceptance_prerequisite_gap": (
            "IMPLEMENTATION_MANIFEST_ARTIFACT_V1 supports CREATE_ONLY and cannot "
            "truthfully describe an existing-file REPLACE_CONTENT patch."
        ),
        "ready_for_generated_content_acceptance": False,
        "disposable_patch_application_allowed_after_separate_human_approval": True,
        **deepcopy(DENIED_AUTHORITIES),
        "prepared_at": prepared_at,
        "replay_reference": replay_reference,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _approval_required(plan: dict[str, Any]) -> dict[str, Any]:
    request = {
        "artifact_type": APPROVAL_REQUEST_ARTIFACT_V1,
        "approval_id": f"{plan['plan_id']}:HUMAN-APPROVAL-REQUEST",
        "approval_status": HUMAN_APPROVAL_REQUIRED,
        "approval_scope": APPROVAL_SCOPE,
        "proposal_reference": plan["plan_id"],
        "proposal_hash": plan["artifact_hash"],
        "disposable_workspace": plan["disposable_workspace"],
        "disposable_patch_application_allowed": True,
        "grounded_test_execution_allowed": True,
        "implementation_authorization_allowed": False,
        **deepcopy(DENIED_AUTHORITIES),
        "created_at": plan["prepared_at"],
        "human_final_authority": True,
        "replay_visible": True,
    }
    request["artifact_hash"] = replay_hash(request)
    packet = {
        "approval_request_artifact": request,
        "proposal_reference": plan["plan_id"],
        "proposal_hash": plan["artifact_hash"],
        "canonical_chain_id": plan["plan_identity"],
    }
    packet["packet_hash"] = replay_hash(packet)
    required = {
        "artifact_type": APPROVAL_REQUIRED_ARTIFACT_V1,
        "runtime_version": RUNTIME_VERSION,
        "execution_id": f"{plan['plan_id']}:APPROVAL-REQUIRED",
        "terminal_status": HUMAN_APPROVAL_REQUIRED,
        "canonical_chain_id": plan["plan_identity"],
        "approval_status": HUMAN_APPROVAL_REQUIRED,
        "approval_hash": request["artifact_hash"],
        "approval_scope": APPROVAL_SCOPE,
        "plan_reference": plan["plan_id"],
        "plan_hash": plan["artifact_hash"],
        "approval_resume_packet": packet,
        "main_repository_mutation_authorized": False,
        "arbitrary_command_execution_authorized": False,
        "provider_invocation_authorized": False,
        "codex_execution_authorized": False,
        "replay_visible": True,
    }
    required["artifact_hash"] = replay_hash(required)
    return required


def _validate_application_decision(
    capture: dict[str, Any], approval_required: dict[str, Any], root: Path
) -> dict[str, Any]:
    replay_path = Path(capture.get("human_decision_replay_reference", "")).resolve()
    if not replay_path.is_relative_to(root):
        raise FailClosedRuntimeError("disposable validation authority is cross-session")
    reconstructed = reconstruct_human_decision_replay(replay_path)
    wrapper = load_json(replay_path / "000_human_decision_recorded.json")
    verify_replay_hash(wrapper)
    human = wrapper.get("artifact")
    _verify_artifact(human, "disposable validation human decision")
    if not all((
        capture.get("human_decision_artifact") == human,
        reconstructed.get("decision") == APPROVE,
        reconstructed.get("approval_scope") == APPROVAL_SCOPE,
        human.get("approval_required_hash") == approval_required["artifact_hash"],
        human.get("proposal_hash") == approval_required["plan_hash"],
        human.get("implementation_authorized") is False,
        human.get("provider_invoked") is False,
        human.get("worker_invoked") is False,
    )):
        raise FailClosedRuntimeError(
            "disposable validation requires one exact unused human approval"
        )
    return human


def _outcome_artifact(
    *, plan: dict[str, Any], human: dict[str, Any], status: str,
    governed_capture: dict[str, Any] | None, test_capture: dict[str, Any] | None,
    application_attempted: bool, patch_applied: bool, content_performed: bool,
    content_passed: bool, test_performed: bool, test_passed: bool,
    source_unchanged: bool, executed_by: str, executed_at: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": OUTCOME_ARTIFACT_V1,
        "runtime_version": RUNTIME_VERSION,
        "outcome_id": f"{plan['plan_id']}:OUTCOME",
        "execution_status": status,
        "plan_id": plan["plan_id"],
        "plan_hash": plan["artifact_hash"],
        "application_decision_id": human["human_decision_id"],
        "application_decision_hash": human["artifact_hash"],
        "approval_scope": APPROVAL_SCOPE,
        "task_outcome_satisfaction_evaluated": True,
        "task_outcome_satisfied": True,
        "task_outcome_criteria_version": CRITERIA_VERSION,
        "disposable_patch_application_authorized": True,
        "disposable_patch_application_attempted": application_attempted,
        "disposable_patch_applied": patch_applied,
        "disposable_workspace": plan["disposable_workspace"],
        "patch_sha256": plan["patch_sha256"],
        "preimage_sha256": deepcopy(plan["preimage_sha256"]),
        "postimage_sha256": deepcopy(plan["postimage_sha256"]),
        "changed_paths": deepcopy(plan["changed_paths"]),
        "content_validation_performed": content_performed,
        "content_validation_passed": content_passed,
        "governed_repository_mutation_replay_reference": (
            governed_capture.get("governed_repository_mutation_replay_reference")
            if isinstance(governed_capture, dict) else None
        ),
        "governed_repository_mutation_outcome_hash": (
            governed_capture.get("governed_repository_mutation_outcome", {}).get(
                "artifact_hash"
            ) if isinstance(governed_capture, dict) else None
        ),
        "grounded_test_command": deepcopy(plan["grounded_test_command"]),
        "grounded_test_execution_performed": test_performed,
        "grounded_test_validation_passed": test_passed,
        "test_validation_replay_reference": (
            test_capture.get("validation_command_replay_reference")
            if isinstance(test_capture, dict) else None
        ),
        "test_validation_result_hash": (
            test_capture.get("validation_command_result_artifact", {}).get(
                "artifact_hash"
            ) if isinstance(test_capture, dict) else None
        ),
        "generated_content_manifest_created": False,
        "generated_content_validation_artifact_created": False,
        "generated_test_validation_artifact_created": False,
        "ready_for_generated_content_acceptance": False,
        "acceptance_prerequisite_gap": plan[
            "generated_content_acceptance_prerequisite_gap"
        ],
        "source_repository_unchanged": source_unchanged,
        "main_repository_mutated": False,
        "result_accepted": False,
        "repository_mutation_authorized": False,
        "commit_created": False,
        "provider_invoked": False,
        "codex_process_started": False,
        "automatic_retry_performed": False,
        "package_installed": False,
        "network_accessed": False,
        "deployed": False,
        "released": False,
        "executed_by": _required(executed_by, "executed_by"),
        "executed_at": _required(executed_at, "executed_at"),
        "failure_reason": failure_reason,
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _outcome_capture(
    outcome: dict[str, Any], governed: dict[str, Any] | None,
    test: dict[str, Any] | None, replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "runtime_version": RUNTIME_VERSION,
        "execution_status": outcome["execution_status"],
        "outcome_artifact": deepcopy(outcome),
        "governed_repository_mutation_capture": deepcopy(governed),
        "grounded_test_validation_capture": deepcopy(test),
        "outcome_replay_reference": str(replay_path),
        **{
            key: outcome[key]
            for key in (
                "task_outcome_satisfaction_evaluated",
                "task_outcome_satisfied",
                "task_outcome_criteria_version",
                "disposable_patch_application_authorized",
                "disposable_patch_applied",
                "main_repository_mutated",
                "content_validation_performed",
                "content_validation_passed",
                "grounded_test_execution_performed",
                "grounded_test_validation_passed",
                "generated_content_manifest_created",
                "ready_for_generated_content_acceptance",
                "result_accepted",
                "repository_mutation_authorized",
                "commit_created",
                "provider_invoked",
                "codex_process_started",
                "deployed",
                "released",
                "failure_reason",
            )
        },
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _disposable_destination(value: str | Path, source_workspace: str | Path) -> Path:
    path = Path(value).resolve()
    temporary_root = Path(tempfile.gettempdir()).resolve()
    source = Path(source_workspace).resolve()
    if path == temporary_root or not path.is_relative_to(temporary_root):
        raise FailClosedRuntimeError("disposable validation workspace must be a bounded /tmp child")
    if path == source or path.is_relative_to(source) or source.is_relative_to(path):
        raise FailClosedRuntimeError("disposable validation workspace overlaps source repository")
    return path


def _verify_workspace_hashes(root: Path, expected: dict[str, str]) -> None:
    if not _workspace_hashes_match(root, expected):
        raise FailClosedRuntimeError("disposable validation workspace preimage or postimage mismatch")


def _copy_repository(source: Path, destination: Path) -> None:
    if any(path.is_symlink() for path in source.rglob("*")):
        raise FailClosedRuntimeError(
            "disposable validation source repository contains a symlink"
        )
    shutil.copytree(source, destination, symlinks=False)


def _repository_file_hashes(root: Path) -> dict[str, str]:
    resolved = root.resolve()
    hashes: dict[str, str] = {}
    for path in sorted(resolved.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(resolved)
        if relative.parts and relative.parts[0] == ".git":
            continue
        if "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        hashes[relative.as_posix()] = "sha256:" + sha256(path.read_bytes()).hexdigest()
    return hashes


def _workspace_hashes_match(root: Path, expected: dict[str, str]) -> bool:
    try:
        if not expected:
            return False
        resolved_root = root.resolve()
        for relative, digest in expected.items():
            path = (resolved_root / relative).resolve()
            if not path.is_relative_to(resolved_root) or not path.is_file():
                return False
            if "sha256:" + sha256(path.read_bytes()).hexdigest() != digest:
                return False
        return True
    except OSError:
        return False


def _hashed_artifact(value: dict[str, Any]) -> dict[str, Any]:
    artifact = deepcopy(value)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _ensure_plan_replay_available(path: Path) -> None:
    if any(
        (path / f"{index:03d}_{step}.json").exists()
        for index, step in enumerate(PLAN_REPLAY_STEPS)
    ):
        raise FailClosedRuntimeError("disposable validation review destination already exists")


def _ensure_outcome_replay_available(path: Path) -> None:
    if (path / f"000_{OUTCOME_REPLAY_STEP}.json").exists():
        raise FailClosedRuntimeError("disposable validation outcome destination already exists")


def _persist_plan_step(root: Path, index: int, artifact: dict[str, Any]) -> None:
    step = PLAN_REPLAY_STEPS[index]
    wrapper = {
        "event_type": step.upper(),
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(root / f"{index:03d}_{step}.json", wrapper)


def _persist_outcome(root: Path, artifact: dict[str, Any]) -> None:
    wrapper = {
        "event_type": OUTCOME_REPLAY_STEP.upper(),
        "replay_index": 0,
        "replay_step": OUTCOME_REPLAY_STEP,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(root / f"000_{OUTCOME_REPLAY_STEP}.json", wrapper)


def _load_plan_wrappers(root: Path) -> list[dict[str, Any]]:
    wrappers = []
    for index, step in enumerate(PLAN_REPLAY_STEPS):
        wrapper = load_json(root / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("disposable validation review Replay ordering mismatch")
        verify_replay_hash(wrapper)
        _verify_artifact(wrapper.get("artifact"), "disposable validation review")
        wrappers.append(wrapper)
    return wrappers


def _reject_duplicate_plan(root: Path, identity: str) -> None:
    for path in root.rglob(f"000_{PLAN_REPLAY_STEPS[0]}.json"):
        wrapper = load_json(path)
        verify_replay_hash(wrapper)
        if (wrapper.get("artifact") or {}).get("plan_identity") == identity:
            raise FailClosedRuntimeError("disposable validation plan already exists")


def _reject_existing_application_decision(root: Path, approval_hash: str) -> None:
    for path in root.rglob("000_human_decision_recorded.json"):
        wrapper = load_json(path)
        verify_replay_hash(wrapper)
        if (wrapper.get("artifact") or {}).get("approval_required_hash") == approval_hash:
            raise FailClosedRuntimeError("disposable validation decision already recorded")


def _reject_authority_reuse(root: Path, decision_hash: str) -> None:
    for path in root.rglob(f"000_{OUTCOME_REPLAY_STEP}.json"):
        wrapper = load_json(path)
        verify_replay_hash(wrapper)
        if (wrapper.get("artifact") or {}).get("application_decision_hash") == decision_hash:
            raise FailClosedRuntimeError("disposable validation one-time authority already consumed")


def _verify_artifact(value: Any, label: str) -> None:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{label} is missing")
    candidate = deepcopy(value)
    actual = candidate.pop("artifact_hash", None)
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _required(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"disposable validation requires {label}")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "disposable patch application or test validation failed closed"


__all__ = [
    "APPROVAL_SCOPE",
    "COMPLETED",
    "CRITERIA_VERSION",
    "FAILED_CLOSED",
    "prepare_disposable_patch_validation_review",
    "record_disposable_patch_validation_human_decision",
    "execute_disposable_patch_validation",
    "reconstruct_disposable_patch_validation_review",
    "reconstruct_disposable_patch_validation_outcome",
]
