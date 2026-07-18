"""Human review of one exact governance-valid captured CODEX task outcome."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path, PurePosixPath
import re
from typing import Any

from aigol.runtime import worker_result_capture_runtime as canonical_capture
from aigol.runtime import worker_result_validation_runtime as canonical_validation
from aigol.runtime.codex_transport_to_worker_result_capture_binding_runtime import (
    SUCCESS as CAPTURE_SUCCESS,
    reconstruct_codex_worker_result_capture_binding,
)
from aigol.runtime.codex_worker_activation_binding_runtime import (
    reconstruct_codex_worker_activation_binding,
)
from aigol.runtime.codex_worker_result_to_semantic_validation_binding_runtime import (
    SUCCESS as VALIDATION_SUCCESS,
    reconstruct_codex_worker_semantic_validation_binding,
)
from aigol.runtime.conversation_to_ppp_handoff_execution import HUMAN_APPROVAL_REQUIRED
from aigol.runtime.human_decision_runtime import (
    APPROVE,
    REJECT,
    REQUEST_MODIFICATION,
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


RUNTIME_VERSION = "G31_22A_CANONICAL_TASK_OUTCOME_HUMAN_REVIEW_V1"
TASK_OUTCOME_REVIEW_PACKET_ARTIFACT_V1 = "TASK_OUTCOME_REVIEW_PACKET_ARTIFACT_V1"
TASK_OUTCOME_REVIEW_REQUIRED_ARTIFACT_V1 = "TASK_OUTCOME_REVIEW_REQUIRED_ARTIFACT_V1"
TASK_OUTCOME_REVIEW_APPROVAL_REQUEST_ARTIFACT_V1 = (
    "TASK_OUTCOME_REVIEW_APPROVAL_REQUEST_ARTIFACT_V1"
)
REVIEW_REQUIRED = "TASK_OUTCOME_HUMAN_REVIEW_REQUIRED"
APPROVAL_SCOPE = "REVIEW_CAPTURED_WORKER_TASK_OUTCOME_ONLY"
TASK_OUTCOME_SATISFIED = "TASK_OUTCOME_SATISFIED"
TASK_OUTCOME_UNSATISFIED = "TASK_OUTCOME_UNSATISFIED"
REWORK_REQUESTED = "REWORK_REQUESTED"
DECISION_TO_HUMAN_DECISION = {
    TASK_OUTCOME_SATISFIED: APPROVE,
    TASK_OUTCOME_UNSATISFIED: REJECT,
    REWORK_REQUESTED: REQUEST_MODIFICATION,
}
HUMAN_DECISION_TO_DECISION = {
    value: key for key, value in DECISION_TO_HUMAN_DECISION.items()
}
REPLAY_STEPS = (
    "task_outcome_review_packet_recorded",
    "task_outcome_review_required_recorded",
)
STOP_TRUTH = {
    "result_accepted": False,
    "repository_mutation_authorized": False,
    "repository_mutated": False,
    "automatic_retry_performed": False,
    "additional_worker_process_started": False,
    "provider_invoked": False,
    "commit_created": False,
    "deployed": False,
    "released": False,
}
AICLI_BOUNDARIES = {
    "aicli_reviews": False,
    "aicli_accepts": False,
    "aicli_authorizes_mutation": False,
    "aicli_executes_rework": False,
}


def prepare_codex_task_outcome_review(
    *,
    result_capture_binding_capture: dict[str, Any],
    validation_binding_capture: dict[str, Any],
    activation_capture: dict[str, Any],
    governed_execution_capture: dict[str, Any],
    execution_candidate_capture: dict[str, Any],
    session_root: str | Path,
    workspace: str | Path,
    prepared_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create one review-only packet from exact in-memory bytes and valid lineage."""

    root = Path(session_root).resolve()
    destination = Path(replay_dir).resolve()
    if not destination.is_relative_to(root):
        raise FailClosedRuntimeError("task-outcome review destination is cross-session")
    _ensure_review_destination_available(destination)
    sources = _reconstruct_sources(
        result_capture_binding_capture=result_capture_binding_capture,
        validation_binding_capture=validation_binding_capture,
        activation_capture=activation_capture,
        governed_execution_capture=governed_execution_capture,
        execution_candidate_capture=execution_candidate_capture,
        session_root=root,
        workspace=workspace,
    )
    packet = _review_packet(
        sources=sources,
        prepared_at=_required(prepared_at, "prepared_at"),
        replay_reference=str(destination),
    )
    _reject_duplicate_review(root, packet["review_identity"])
    approval_required = _approval_required(packet)
    _persist(destination, 0, packet)
    _persist(destination, 1, approval_required)
    return {
        "runtime_version": RUNTIME_VERSION,
        "review_status": REVIEW_REQUIRED,
        "task_outcome_review_packet_artifact": deepcopy(packet),
        "task_outcome_review_required_artifact": deepcopy(approval_required),
        "task_outcome_review_replay_reference": str(destination),
        "review_replay_artifact_count": 2,
        "human_task_outcome_decision_recorded": False,
        "task_outcome_satisfaction_evaluated": False,
        "task_outcome_satisfied": False,
        "rework_requested": False,
        "governance_result_validated": True,
        **deepcopy(STOP_TRUTH),
        **deepcopy(AICLI_BOUNDARIES),
    }


def reconstruct_codex_task_outcome_review(
    *,
    review_capture: dict[str, Any],
    result_capture_binding_capture: dict[str, Any],
    validation_binding_capture: dict[str, Any],
    activation_capture: dict[str, Any],
    governed_execution_capture: dict[str, Any],
    execution_candidate_capture: dict[str, Any],
    session_root: str | Path,
    workspace: str | Path,
) -> dict[str, Any]:
    """Reconstruct one packet and rebind it to current exact bytes and lineage."""

    root = Path(session_root).resolve()
    replay_path = Path(
        review_capture.get("task_outcome_review_replay_reference", "")
    ).resolve()
    if not replay_path.is_relative_to(root):
        raise FailClosedRuntimeError("task-outcome review Replay is cross-session")
    wrappers = _load_review_wrappers(replay_path)
    packet, approval_required = (wrapper["artifact"] for wrapper in wrappers)
    if review_capture.get("task_outcome_review_packet_artifact") != packet:
        raise FailClosedRuntimeError("task-outcome review packet capture mismatch")
    if review_capture.get("task_outcome_review_required_artifact") != approval_required:
        raise FailClosedRuntimeError("task-outcome review-required capture mismatch")
    sources = _reconstruct_sources(
        result_capture_binding_capture=result_capture_binding_capture,
        validation_binding_capture=validation_binding_capture,
        activation_capture=activation_capture,
        governed_execution_capture=governed_execution_capture,
        execution_candidate_capture=execution_candidate_capture,
        session_root=root,
        workspace=workspace,
    )
    expected_packet = _review_packet(
        sources=sources,
        prepared_at=packet.get("prepared_at", ""),
        replay_reference=str(replay_path),
    )
    if packet != expected_packet:
        raise FailClosedRuntimeError(
            "task-outcome criteria, output, grounding, capture, or validation was substituted"
        )
    expected_required = _approval_required(packet)
    if approval_required != expected_required:
        raise FailClosedRuntimeError("task-outcome human-review authority was substituted")
    return {
        "review_packet": deepcopy(packet),
        "approval_required": deepcopy(approval_required),
        "review_replay_reference": str(replay_path),
        "review_replay_hash": replay_hash(wrappers),
        "review_replay_artifact_count": 2,
        "governance_result_validated": True,
        "exact_worker_output_sha256": packet["exact_worker_output"]["sha256"],
        **deepcopy(STOP_TRUTH),
    }


def record_codex_task_outcome_human_decision(
    *,
    review_capture: dict[str, Any],
    task_outcome_decision: str,
    decision_reason: str,
    decided_by: str,
    decided_at: str,
    result_capture_binding_capture: dict[str, Any],
    validation_binding_capture: dict[str, Any],
    activation_capture: dict[str, Any],
    governed_execution_capture: dict[str, Any],
    execution_candidate_capture: dict[str, Any],
    session_root: str | Path,
    workspace: str | Path,
    human_decision_replay_dir: str | Path,
) -> dict[str, Any]:
    """Record satisfied, unsatisfied, or rework without acceptance or execution."""

    outcome = _decision(task_outcome_decision)
    root = Path(session_root).resolve()
    decision_destination = Path(human_decision_replay_dir).resolve()
    if not decision_destination.is_relative_to(root):
        raise FailClosedRuntimeError("task-outcome human decision is cross-session")
    review = reconstruct_codex_task_outcome_review(
        review_capture=review_capture,
        result_capture_binding_capture=result_capture_binding_capture,
        validation_binding_capture=validation_binding_capture,
        activation_capture=activation_capture,
        governed_execution_capture=governed_execution_capture,
        execution_candidate_capture=execution_candidate_capture,
        session_root=root,
        workspace=workspace,
    )
    approval_required = review["approval_required"]
    blockers = review["review_packet"].get(
        "deterministic_satisfaction_blockers", []
    )
    if outcome == TASK_OUTCOME_SATISFIED and blockers:
        raise FailClosedRuntimeError(
            "task-outcome satisfaction failed closed: " + "; ".join(blockers)
        )
    _reject_repeated_decision(root, approval_required["artifact_hash"])
    human = record_human_decision(
        human_decision_id=(
            f"{review['review_packet']['review_id']}:HUMAN-TASK-OUTCOME-DECISION"
        ),
        approval_required_artifact=approval_required,
        decision=DECISION_TO_HUMAN_DECISION[outcome],
        decision_reason=_required(decision_reason, "decision_reason"),
        decided_by=_required(decided_by, "decided_by"),
        decided_at=_required(decided_at, "decided_at"),
        replay_dir=decision_destination,
    )
    _validate_human_decision(human, approval_required, outcome)
    capture = _task_outcome_decision_capture(
        review=review,
        human=human,
        outcome=outcome,
    )
    capture["task_outcome_decision_capture_hash"] = replay_hash(capture)
    return capture


def reconstruct_codex_task_outcome_human_decision(
    *,
    decision_capture: dict[str, Any],
    review_capture: dict[str, Any],
    result_capture_binding_capture: dict[str, Any],
    validation_binding_capture: dict[str, Any],
    activation_capture: dict[str, Any],
    governed_execution_capture: dict[str, Any],
    execution_candidate_capture: dict[str, Any],
    session_root: str | Path,
    workspace: str | Path,
) -> dict[str, Any]:
    """Reconstruct the reused human decision and its task-outcome interpretation."""

    review = reconstruct_codex_task_outcome_review(
        review_capture=review_capture,
        result_capture_binding_capture=result_capture_binding_capture,
        validation_binding_capture=validation_binding_capture,
        activation_capture=activation_capture,
        governed_execution_capture=governed_execution_capture,
        execution_candidate_capture=execution_candidate_capture,
        session_root=session_root,
        workspace=workspace,
    )
    replay_path = Path(
        decision_capture.get("human_decision_replay_reference", "")
    ).resolve()
    root = Path(session_root).resolve()
    if not replay_path.is_relative_to(root):
        raise FailClosedRuntimeError("task-outcome human decision Replay is cross-session")
    reconstructed = reconstruct_human_decision_replay(replay_path)
    decision_wrapper = load_json(replay_path / "000_human_decision_recorded.json")
    returned_wrapper = load_json(replay_path / "001_human_decision_returned.json")
    for wrapper in (decision_wrapper, returned_wrapper):
        verify_replay_hash(wrapper)
    human = decision_capture.get("human_decision_capture")
    if not isinstance(human, dict):
        raise FailClosedRuntimeError("task-outcome human decision capture is missing")
    if human.get("human_decision_artifact") != decision_wrapper["artifact"]:
        raise FailClosedRuntimeError("task-outcome human decision artifact mismatch")
    if human.get("human_decision_replay") != returned_wrapper["artifact"]:
        raise FailClosedRuntimeError("task-outcome human decision return mismatch")
    outcome = HUMAN_DECISION_TO_DECISION.get(reconstructed.get("decision"))
    if outcome is None:
        raise FailClosedRuntimeError("task-outcome human decision is invalid")
    _validate_human_decision(human, review["approval_required"], outcome)
    expected = _task_outcome_decision_capture(
        review=review,
        human=human,
        outcome=outcome,
    )
    expected["task_outcome_decision_capture_hash"] = replay_hash(expected)
    if decision_capture != expected:
        raise FailClosedRuntimeError(
            "task satisfaction, acceptance, mutation, or rework truth was substituted"
        )
    return {
        "task_outcome_decision": outcome,
        "human_decision_replay_hash": reconstructed["replay_hash"],
        "human_decision_replay_artifact_count": 2,
        **{
            key: expected[key]
            for key in (
                "task_outcome_satisfaction_evaluated",
                "task_outcome_satisfied",
                "human_task_outcome_decision_recorded",
                "rework_requested",
                "governance_result_validated",
                "result_accepted",
                "repository_mutation_authorized",
                "repository_mutated",
                "automatic_retry_performed",
                "additional_worker_process_started",
            )
        },
    }


def render_codex_task_outcome_review(review_capture: dict[str, Any]) -> str:
    """Render exact review evidence without granting AiCLI review authority."""

    packet = review_capture.get("task_outcome_review_packet_artifact") or {}
    _verify_artifact(packet, "task-outcome review packet")
    output = packet.get("exact_worker_output") or {}
    text = output.get("text")
    if not isinstance(text, str) or sha256(text.encode("utf-8")).hexdigest() != output.get(
        "sha256"
    ):
        raise FailClosedRuntimeError("task-outcome review exact output is invalid")
    targets = packet.get("grounded_targets") or {}
    criteria = packet.get("pre_execution_task_outcome_criteria") or {}
    observations = packet.get("task_outcome_observations") or {}
    lines = [
        "Captured CODEX Task-Outcome Human Review",
        f"Approval Scope: {APPROVAL_SCOPE}",
        f"Original Task: {packet.get('original_contextual_request')}",
        f"Implementation Target: {targets.get('implementation_target')}",
        f"Focused Test Target: {targets.get('focused_test_target')}",
        f"Required Output Type: {packet.get('required_output_type')}",
        "Canonical Validation Meaning: GOVERNANCE_POLICY_AND_LINEAGE_VALIDATION_ONLY",
        f"Task Criteria: {criteria.get('requirements')}",
        f"Task Observations: {observations}",
        "Missing Evidence: applied-patch evidence and tests against an applied patch.",
        "Exact Proposed Output:",
        text,
        "Available Decisions: TASK_OUTCOME_SATISFIED, TASK_OUTCOME_UNSATISFIED, REWORK_REQUESTED",
        "AiCLI displays only; it does not review, accept, authorize mutation, or execute rework.",
    ]
    if "task_outcome_satisfaction_eligible" in packet:
        lines.extend((
            "Deterministic Satisfaction Eligible: "
            f"{packet['task_outcome_satisfaction_eligible']}",
            "Deterministic Satisfaction Blockers: "
            f"{packet['deterministic_satisfaction_blockers']}",
        ))
    return "\n".join(lines)


def render_codex_task_outcome_decision(decision_capture: dict[str, Any]) -> str:
    return "\n".join((
        "Captured CODEX Task-Outcome Human Decision",
        f"Decision: {decision_capture.get('task_outcome_decision')}",
        "Task Satisfaction Evaluated: "
        f"{decision_capture.get('task_outcome_satisfaction_evaluated')}",
        f"Task Outcome Satisfied: {decision_capture.get('task_outcome_satisfied')}",
        f"Rework Requested: {decision_capture.get('rework_requested')}",
        "Result Accepted: False",
        "Repository Mutation Authorized: False",
        "Automatic Retry Performed: False",
    ))


def _reconstruct_sources(
    *,
    result_capture_binding_capture: dict[str, Any],
    validation_binding_capture: dict[str, Any],
    activation_capture: dict[str, Any],
    governed_execution_capture: dict[str, Any],
    execution_candidate_capture: dict[str, Any],
    session_root: Path,
    workspace: str | Path,
) -> dict[str, Any]:
    activation = reconstruct_codex_worker_activation_binding(
        activation_capture=activation_capture,
        governed_execution_capture=governed_execution_capture,
        execution_candidate_capture=execution_candidate_capture,
        session_root=session_root,
        workspace=workspace,
    )
    capture = reconstruct_codex_worker_result_capture_binding(
        binding_capture=result_capture_binding_capture,
        activation_capture=activation_capture,
        governed_execution_capture=governed_execution_capture,
        execution_candidate_capture=execution_candidate_capture,
        session_root=session_root,
        workspace=workspace,
    )
    validation = reconstruct_codex_worker_semantic_validation_binding(
        validation_binding_capture=validation_binding_capture,
        result_capture_binding_capture=result_capture_binding_capture,
        activation_capture=activation_capture,
        governed_execution_capture=governed_execution_capture,
        execution_candidate_capture=execution_candidate_capture,
        session_root=session_root,
        workspace=workspace,
    )
    if not all((
        result_capture_binding_capture.get("g31_result_capture_status")
        == CAPTURE_SUCCESS,
        validation_binding_capture.get("g31_semantic_validation_status")
        == VALIDATION_SUCCESS,
        validation.get("validation_status") == canonical_validation.RESULT_VALIDATED,
        validation.get("result_validated") is True,
    )):
        raise FailClosedRuntimeError(
            "task-outcome review requires one governance-valid captured result"
        )
    worker_output = result_capture_binding_capture.get(
        "semantic_worker_output_artifact"
    )
    _verify_artifact(worker_output, "semantic Worker output")
    payload = worker_output.get("payload") or {}
    output_text = payload.get("semantic_output")
    if not isinstance(output_text, str) or not output_text:
        raise FailClosedRuntimeError("task-outcome review requires exact Worker-output bytes")
    encoded = output_text.encode("utf-8")
    output_sha256 = sha256(encoded).hexdigest()
    if not all((
        payload.get("semantic_output_encoding") == "utf-8",
        payload.get("semantic_output_byte_length") == len(encoded),
        payload.get("semantic_output_sha256") == output_sha256,
        payload.get("transport_stdout_hash") == output_sha256,
        validation.get("semantic_output_sha256") == output_sha256,
    )):
        raise FailClosedRuntimeError("task-outcome review output bytes or hash mismatch")
    capture_replay_path = Path(
        result_capture_binding_capture.get("worker_result_capture_replay_reference", "")
    ).resolve()
    validation_replay_path = Path(
        validation_binding_capture.get("worker_result_validation_replay_reference", "")
    ).resolve()
    for path in (capture_replay_path, validation_replay_path):
        if not path.is_relative_to(session_root):
            raise FailClosedRuntimeError("task-outcome source Replay is cross-session")
    capture_replay = canonical_capture.reconstruct_worker_result_capture_replay(
        capture_replay_path
    )
    validation_replay = canonical_validation.reconstruct_worker_result_validation_replay(
        validation_replay_path
    )
    capture_wrapper = load_json(
        capture_replay_path / "002_result_capture_artifact_recorded.json"
    )
    validation_wrapper = load_json(
        validation_replay_path / "002_validation_artifact_recorded.json"
    )
    for wrapper in (capture_wrapper, validation_wrapper):
        verify_replay_hash(wrapper)
    capture_artifact = capture_wrapper.get("artifact") or {}
    validation_artifact = validation_wrapper.get("artifact") or {}
    _verify_artifact(capture_artifact, "result capture")
    _verify_artifact(validation_artifact, "result validation")
    contract = (
        activation_capture.get("synthesis_preflight_capture", {})
        .get("worker_execution_contract")
    )
    if not isinstance(contract, dict):
        raise FailClosedRuntimeError("task-outcome review Worker contract is missing")
    criteria = contract.get("task_outcome_criteria")
    _verify_embedded_hash(criteria, "criteria_hash", "pre-execution task criteria")
    if not all((
        contract
        == activation["codex_execution_request"]["handoff_package"].get(
            "worker_execution_contract"
        ),
        criteria.get("established_before_worker_execution") is True,
        criteria.get("authorized_task") == contract.get("authorized_task"),
        criteria.get("required_output_type") == contract.get("requested_output_type"),
        criteria.get("grounded_targets") == contract.get("grounded_targets"),
        activation["activation_review_artifact"].get("interpreted_intent", {}).get(
            "task_outcome_criteria_hash"
        ) == criteria["criteria_hash"],
        activation["activation_approval_artifact"].get(
            "task_outcome_criteria_hash"
        ) == criteria["criteria_hash"],
    )):
        raise FailClosedRuntimeError("pre-execution task criteria were substituted")
    return {
        "activation": activation,
        "activation_capture": activation_capture,
        "capture": capture,
        "capture_artifact": capture_artifact,
        "capture_replay": capture_replay,
        "capture_replay_reference": str(capture_replay_path),
        "validation": validation,
        "validation_artifact": validation_artifact,
        "validation_replay": validation_replay,
        "validation_replay_reference": str(validation_replay_path),
        "contract": deepcopy(contract),
        "criteria": deepcopy(criteria),
        "worker_output": deepcopy(worker_output),
        "output_text": output_text,
        "output_sha256": output_sha256,
        "output_byte_length": len(encoded),
    }


def _review_packet(
    *, sources: dict[str, Any], prepared_at: str, replay_reference: str
) -> dict[str, Any]:
    activation = sources["activation"]
    lineage = activation["lineage"]
    grounding = lineage["grounding"]
    worker_request = grounding.get("grounded_worker_request_artifact") or {}
    implementation_scope = worker_request.get("implementation_scope") or {}
    contract = sources["contract"]
    targets = {
        item["target_role"]: item["target_path"]
        for item in contract["grounded_targets"]
    }
    grounded_targets = {
        "implementation_capability": grounding.get("canonical_capability_target"),
        "implementation_target": targets["IMPLEMENTATION"],
        "test_capability": grounding.get("canonical_capability_target"),
        "focused_test_target": targets["FOCUSED_TEST"],
        "repository_scope_grounding_hash": grounding["artifact_hash"],
        "repository_cognition_snapshot_hash": grounding[
            "repository_cognition_snapshot_hash"
        ],
    }
    identity_seed = {
        "criteria_hash": sources["criteria"]["criteria_hash"],
        "activation_replay_hash": activation["activation_replay_hash"],
        "capture_artifact_hash": sources["capture_artifact"]["artifact_hash"],
        "validation_artifact_hash": sources["validation_artifact"]["artifact_hash"],
        "exact_worker_output_sha256": sources["output_sha256"],
    }
    review_identity = replay_hash(identity_seed)
    observations = _output_observations(
        sources["output_text"],
        allowed_targets={
            grounded_targets["implementation_target"],
            grounded_targets["focused_test_target"],
        },
        implementation_targets={grounded_targets["implementation_target"]},
        criteria=sources["criteria"],
    )
    packet = {
        "artifact_type": TASK_OUTCOME_REVIEW_PACKET_ARTIFACT_V1,
        "runtime_version": RUNTIME_VERSION,
        "review_id": f"G31-TASK-OUTCOME-REVIEW-{review_identity[-24:]}",
        "review_identity": review_identity,
        "approval_scope": APPROVAL_SCOPE,
        "original_contextual_request": lineage["original_request"],
        "grounded_project_goal": {
            "original_human_goal": implementation_scope.get("original_human_goal"),
            "canonical_project_objective": implementation_scope.get(
                "canonical_project_objective"
            ),
            "project_objective_hash": implementation_scope.get(
                "project_objective_hash"
            ),
        },
        "grounded_targets": grounded_targets,
        "required_output_type": contract["requested_output_type"],
        "authorized_worker_task": contract["authorized_task"],
        "final_approved_worker_prompt": activation["codex_execution_request"][
            "handoff_package"
        ]["codex_prompt"],
        "final_approved_worker_prompt_sha256": activation[
            "codex_execution_request"
        ]["bounded_prompt_sha256"],
        "pre_execution_task_outcome_criteria": deepcopy(sources["criteria"]),
        "activation_binding": {
            "request": deepcopy(activation["codex_execution_request"]),
            "receipt": deepcopy(activation["transport_receipt"]),
            "replay_reference": activation["activation_replay_reference"],
            "replay_hash": activation["activation_replay_hash"],
        },
        "exact_worker_output": {
            "text": sources["output_text"],
            "encoding": "utf-8",
            "byte_length": sources["output_byte_length"],
            "sha256": sources["output_sha256"],
            "worker_output_id": sources["worker_output"]["worker_output_id"],
            "worker_output_hash": sources["worker_output"]["artifact_hash"],
        },
        "capture_binding": {
            "artifact": deepcopy(sources["capture_artifact"]),
            "replay_reference": sources["capture_replay_reference"],
            "replay_hash": sources["capture_replay"]["replay_hash"],
            "replay_artifact_count": sources["capture_replay"][
                "replay_artifact_count"
            ],
        },
        "governance_validation_binding": {
            "artifact": deepcopy(sources["validation_artifact"]),
            "status": canonical_validation.RESULT_VALIDATED,
            "canonical_meaning": (
                canonical_validation.CANONICAL_RESULT_VALIDATION_MEANING
            ),
            "replay_reference": sources["validation_replay_reference"],
            "replay_hash": sources["validation_replay"]["replay_hash"],
            "replay_artifact_count": sources["validation_replay"][
                "replay_artifact_count"
            ],
        },
        "task_outcome_observations": observations,
        "patch_applied": False,
        "tests_run_against_applied_patch": False,
        "missing_acceptance_evidence": [
            "IMPLEMENTATION_MANIFEST_ARTIFACT_V1",
            "GENERATED_CONTENT_VALIDATION_ARTIFACT_V1",
            "GENERATED_TEST_VALIDATION_ARTIFACT_V1",
            "HUMAN_GENERATED_CONTENT_ACCEPTANCE",
        ],
        "available_human_decisions": list(DECISION_TO_HUMAN_DECISION),
        "task_outcome_satisfaction_evaluated": False,
        "task_outcome_satisfied": False,
        "human_task_outcome_decision_recorded": False,
        "governance_result_validated": True,
        **deepcopy(STOP_TRUTH),
        **deepcopy(AICLI_BOUNDARIES),
        "prepared_at": _required(prepared_at, "prepared_at"),
        "replay_reference": replay_reference,
        "replay_visible": True,
    }
    if sources["criteria"].get("criteria_version") != (
        "G31_PRE_EXECUTION_TASK_OUTCOME_CRITERIA_V1"
    ):
        blockers = _deterministic_satisfaction_blockers(observations)
        packet["deterministic_satisfaction_blockers"] = blockers
        packet["task_outcome_satisfaction_eligible"] = not blockers
    packet["artifact_hash"] = replay_hash(packet)
    return packet


def _approval_required(packet: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact(packet, "task-outcome review packet")
    request = {
        "artifact_type": TASK_OUTCOME_REVIEW_APPROVAL_REQUEST_ARTIFACT_V1,
        "approval_id": f"{packet['review_id']}:HUMAN-DECISION-REQUEST",
        "approval_status": HUMAN_APPROVAL_REQUIRED,
        "canonical_chain_id": packet["review_identity"],
        "approval_scope": APPROVAL_SCOPE,
        "proposal_reference": packet["review_id"],
        "proposal_hash": packet["artifact_hash"],
        "validation_reference": packet["governance_validation_binding"][
            "artifact"
        ]["worker_result_validation_id"],
        "validation_hash": packet["governance_validation_binding"]["artifact"][
            "artifact_hash"
        ],
        "implementation_authorization_allowed": False,
        "result_acceptance_allowed": False,
        "repository_mutation_authority": False,
        "worker_execution_authority": False,
        "created_at": packet["prepared_at"],
        "human_final_authority": True,
        "replay_visible": True,
    }
    request["artifact_hash"] = replay_hash(request)
    resume_packet = {
        "approval_request_artifact": request,
        "proposal_reference": packet["review_id"],
        "proposal_hash": packet["artifact_hash"],
        "canonical_chain_id": packet["review_identity"],
    }
    resume_packet["packet_hash"] = replay_hash(resume_packet)
    required = {
        "artifact_type": TASK_OUTCOME_REVIEW_REQUIRED_ARTIFACT_V1,
        "runtime_version": RUNTIME_VERSION,
        "execution_id": f"{packet['review_id']}:REVIEW-REQUIRED",
        "terminal_status": HUMAN_APPROVAL_REQUIRED,
        "canonical_chain_id": packet["review_identity"],
        "approval_status": HUMAN_APPROVAL_REQUIRED,
        "approval_hash": request["artifact_hash"],
        "approval_scope": APPROVAL_SCOPE,
        "task_outcome_review_reference": packet["review_id"],
        "task_outcome_review_hash": packet["artifact_hash"],
        "approval_resume_packet": resume_packet,
        "implementation_authorized": False,
        "result_accepted": False,
        "repository_mutation_authorized": False,
        "worker_invoked": False,
        "automatic_retry_performed": False,
        "replay_visible": True,
    }
    required["artifact_hash"] = replay_hash(required)
    return required


def _task_outcome_decision_capture(
    *, review: dict[str, Any], human: dict[str, Any], outcome: str
) -> dict[str, Any]:
    satisfied = outcome == TASK_OUTCOME_SATISFIED
    return {
        "runtime_version": RUNTIME_VERSION,
        "task_outcome_decision": outcome,
        "approval_scope": APPROVAL_SCOPE,
        "review_id": review["review_packet"]["review_id"],
        "review_hash": review["review_packet"]["artifact_hash"],
        "exact_worker_output_sha256": review["exact_worker_output_sha256"],
        "human_decision_capture": deepcopy(human),
        "human_decision_replay_reference": human[
            "human_decision_replay_reference"
        ],
        "task_outcome_satisfaction_evaluated": True,
        "task_outcome_satisfied": satisfied,
        "human_task_outcome_decision_recorded": True,
        "rework_requested": outcome == REWORK_REQUESTED,
        "governance_result_validated": True,
        "implementation_authorized": False,
        **deepcopy(STOP_TRUTH),
        **deepcopy(AICLI_BOUNDARIES),
    }


def _validate_human_decision(
    human: dict[str, Any], approval_required: dict[str, Any], outcome: str
) -> None:
    expected_decision = DECISION_TO_HUMAN_DECISION[outcome]
    checks = (
        human.get("fail_closed") is False,
        human.get("decision") == expected_decision,
        human.get("approval_scope") == APPROVAL_SCOPE,
        human.get("approval_required_hash") == approval_required["artifact_hash"],
        human.get("proposal_hash")
        == approval_required["task_outcome_review_hash"],
        human.get("implementation_authorization_allowed") is False,
        human.get("implementation_authorized") is False,
        human.get("implementation_rejected") is False,
        human.get("worker_invoked") is False,
        human.get("execution_requested") is False,
        human.get("dispatch_requested") is False,
        human.get("provider_invoked") is False,
    )
    if not all(checks):
        raise FailClosedRuntimeError(
            "task-outcome human decision scope or authority mismatch"
        )


def _output_observations(
    output: str,
    *,
    allowed_targets: set[str],
    implementation_targets: set[str],
    criteria: dict[str, Any],
) -> dict[str, Any]:
    if criteria.get("criteria_version") == "G31_PRE_EXECUTION_TASK_OUTCOME_CRITERIA_V1":
        return _legacy_output_observations(output, allowed_targets=allowed_targets)

    parsed = _parse_unified_diff(output)
    changed_paths = set(parsed["changed_paths"])
    removed = parsed["removed_lines"]
    added = parsed["added_lines"]
    semantic = _explicit_semantic_change(criteria.get("authorized_task", ""))
    semantic_present = (
        any(semantic[0] in line for line in removed)
        and any(semantic[1] in line for line in added)
        if semantic is not None
        else None
    )
    return {
        "grounded_filenames": sorted(allowed_targets),
        "grounded_filenames_referenced_in_output": sorted(
            target for target in allowed_targets if target in output
        ),
        "both_grounded_filenames_referenced_in_output": all(
            target in output for target in allowed_targets
        ),
        "unified_diff_markers_present": parsed["markers_present"],
        "unified_diff_syntactically_valid": parsed["valid"],
        "unified_diff_errors": parsed["errors"],
        "diff_targets": sorted(changed_paths),
        "changed_paths": sorted(changed_paths),
        "changed_grounded_implementation_targets": sorted(
            changed_paths.intersection(implementation_targets)
        ),
        "at_least_one_grounded_implementation_target_changed": bool(
            changed_paths.intersection(implementation_targets)
        ),
        "all_changed_paths_grounded": changed_paths.issubset(allowed_targets),
        "no_ungrounded_path_changed": changed_paths.issubset(allowed_targets),
        "additional_target_present": not changed_paths.issubset(allowed_targets),
        "path_traversal_present": parsed["path_traversal_present"],
        "absolute_path_present": parsed["absolute_path_present"],
        "renamed_or_substituted_target_present": parsed[
            "renamed_or_substituted_target_present"
        ],
        "fake_or_empty_diff_section_present": parsed[
            "fake_or_empty_diff_section_present"
        ],
        "removed_lines": removed,
        "added_lines": added,
        "requested_semantic_change": (
            {"removed_term": semantic[0], "added_term": semantic[1]}
            if semantic is not None
            else None
        ),
        "requested_semantic_change_machine_check_available": semantic is not None,
        "requested_semantic_change_present": semantic_present,
        "status_to_summary_change_present": any(
            "Status:" in line for line in removed
        ) and any("Summary:" in line for line in added),
        "tests_passed_claim_present": _tests_passed_claim_present(output),
        "patch_applied_claim_present": _patch_applied_claim_present(output),
        "grounded_file_inspection_proven": False,
        "grounded_file_inspection_evidence_gap": (
            "A unified diff proves changed paths, not which unchanged files were read."
        ),
        "downstream_task_description_only": not parsed["markers_present"],
    }


def _legacy_output_observations(
    output: str, *, allowed_targets: set[str]
) -> dict[str, Any]:
    lines = output.splitlines()
    old_headers = [line[4:] for line in lines if line.startswith("--- ")]
    new_headers = [line[4:] for line in lines if line.startswith("+++ ")]
    diff_targets = {
        value[2:] if value.startswith(("a/", "b/")) else value
        for value in (*old_headers, *new_headers)
        if value != "/dev/null"
    }
    removed = [
        line[1:] for line in lines if line.startswith("-") and not line.startswith("---")
    ]
    added = [
        line[1:] for line in lines if line.startswith("+") and not line.startswith("+++")
    ]
    return {
        "grounded_filenames": sorted(allowed_targets),
        "grounded_filenames_referenced_in_output": sorted(
            target for target in allowed_targets if target in output
        ),
        "both_grounded_filenames_referenced_in_output": all(
            target in output for target in allowed_targets
        ),
        "unified_diff_markers_present": bool(old_headers and new_headers),
        "diff_targets": sorted(diff_targets),
        "additional_target_present": not diff_targets.issubset(allowed_targets),
        "removed_lines": removed,
        "added_lines": added,
        "status_to_summary_change_present": any(
            "Status:" in line for line in removed
        ) and any("Summary:" in line for line in added),
        "downstream_task_description_only": not bool(old_headers and new_headers),
    }


def _parse_unified_diff(output: str) -> dict[str, Any]:
    lines = output.splitlines()
    errors: list[str] = []
    changed_paths: list[str] = []
    removed_lines: list[str] = []
    added_lines: list[str] = []
    path_traversal_present = False
    absolute_path_present = False
    renamed_or_substituted_target_present = False
    fake_or_empty_diff_section_present = False
    index = 0
    section_count = 0

    while index < len(lines):
        git_header_paths: tuple[str | None, str | None] | None = None
        if lines[index].startswith("diff --git "):
            parts = lines[index].split(" ")
            if len(parts) != 4:
                errors.append("malformed diff --git header")
                break
            git_old_path, git_old_error = _canonical_diff_path(parts[2])
            git_new_path, git_new_error = _canonical_diff_path(parts[3])
            for error in (git_old_error, git_new_error):
                if error:
                    errors.append(error)
                path_traversal_present |= "traversal" in error
                absolute_path_present |= "absolute" in error
            git_header_paths = (git_old_path, git_new_path)
            if git_old_path != git_new_path:
                renamed_or_substituted_target_present = True
                errors.append("renamed or substituted diff --git target")
            index += 1
            if index < len(lines) and lines[index].startswith("index "):
                index += 1
        if index >= len(lines) or not lines[index].startswith("--- "):
            errors.append("content outside a unified-diff file section")
            break
        old_raw = _header_path(lines[index][4:])
        index += 1
        if index >= len(lines) or not lines[index].startswith("+++ "):
            errors.append("missing unified-diff new-file header")
            break
        new_raw = _header_path(lines[index][4:])
        index += 1
        old_path, old_error = _canonical_diff_path(old_raw)
        new_path, new_error = _canonical_diff_path(new_raw)
        for raw, error in ((old_raw, old_error), (new_raw, new_error)):
            if error:
                errors.append(error)
            path_traversal_present |= "traversal" in error
            absolute_path_present |= "absolute" in error
        if old_path is None or new_path is None:
            continue
        if old_path != new_path:
            renamed_or_substituted_target_present = True
            errors.append("renamed or substituted unified-diff target")
        if git_header_paths is not None and git_header_paths != (old_path, new_path):
            renamed_or_substituted_target_present = True
            errors.append("diff --git and unified-diff targets do not match")
        target = new_path
        section_count += 1
        section_hunks = 0
        section_changes = 0
        while index < len(lines) and not lines[index].startswith(("--- ", "diff --git ")):
            match = re.fullmatch(
                r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(?: .*)?",
                lines[index],
            )
            if match is None:
                errors.append("malformed unified-diff hunk header")
                index += 1
                while index < len(lines) and not lines[index].startswith(
                    ("--- ", "diff --git ")
                ):
                    index += 1
                break
            section_hunks += 1
            expected_old = int(match.group(2) or "1")
            expected_new = int(match.group(4) or "1")
            actual_old = actual_new = 0
            index += 1
            while index < len(lines) and not lines[index].startswith(
                ("@@ ", "--- ", "diff --git ")
            ):
                line = lines[index]
                if line.startswith("\\ No newline at end of file"):
                    index += 1
                    continue
                if not line or line[0] not in {" ", "+", "-"}:
                    errors.append("malformed unified-diff hunk line")
                    index += 1
                    continue
                if line[0] in {" ", "-"}:
                    actual_old += 1
                if line[0] in {" ", "+"}:
                    actual_new += 1
                if line[0] == "-":
                    removed_lines.append(line[1:])
                    section_changes += 1
                elif line[0] == "+":
                    added_lines.append(line[1:])
                    section_changes += 1
                index += 1
            if actual_old != expected_old or actual_new != expected_new:
                errors.append("unified-diff hunk line counts do not match header")
        if section_hunks == 0 or section_changes == 0:
            fake_or_empty_diff_section_present = True
            errors.append("empty or change-free unified-diff file section")
        if target not in changed_paths:
            changed_paths.append(target)

    if section_count == 0:
        errors.append("unified diff contains no changed file section")
    return {
        "valid": not errors,
        "errors": list(dict.fromkeys(errors)),
        "markers_present": any(line.startswith("--- ") for line in lines)
        and any(line.startswith("+++ ") for line in lines),
        "changed_paths": changed_paths,
        "removed_lines": removed_lines,
        "added_lines": added_lines,
        "path_traversal_present": path_traversal_present,
        "absolute_path_present": absolute_path_present,
        "renamed_or_substituted_target_present": (
            renamed_or_substituted_target_present
        ),
        "fake_or_empty_diff_section_present": fake_or_empty_diff_section_present,
    }


def _header_path(value: str) -> str:
    return value.split("\t", 1)[0]


def _canonical_diff_path(value: str) -> tuple[str | None, str]:
    if not value or value == "/dev/null":
        return None, "created or deleted paths are outside this grounded repair contract"
    if value.startswith("/"):
        return None, "absolute unified-diff path"
    candidate = value[2:] if value.startswith(("a/", "b/")) else value
    if "\\" in candidate:
        return None, "path traversal or non-POSIX unified-diff path"
    path = PurePosixPath(candidate)
    if not candidate or candidate.startswith("/"):
        return None, "absolute unified-diff path"
    if any(part in {"", ".", ".."} for part in path.parts):
        return None, "path traversal in unified-diff target"
    return path.as_posix(), ""


def _explicit_semantic_change(value: Any) -> tuple[str, str] | None:
    if not isinstance(value, str):
        return None
    token = r"[A-Za-z0-9_.]+:?"
    patterns = (
        rf"(?P<old>{token})\s*(?:->|-to-)\s*(?P<new>{token})",
        rf"\b(?:change|changing|replace|replacing)\s+"
        rf"(?P<old>{token})\s+(?:to|with)\s+(?P<new>{token})",
    )
    for pattern in patterns:
        match = re.search(pattern, value, flags=re.IGNORECASE)
        if match is not None:
            return match.group("old"), match.group("new")
    return None


def _tests_passed_claim_present(output: str) -> bool:
    lowered = output.casefold()
    return any(
        phrase in lowered
        for phrase in ("tests passed", "all tests pass", "test suite passed")
    )


def _patch_applied_claim_present(output: str) -> bool:
    lowered = output.casefold()
    return any(
        phrase in lowered
        for phrase in ("patch applied", "changes applied", "files modified")
    )


def _deterministic_satisfaction_blockers(
    observations: dict[str, Any],
) -> list[str]:
    blockers = []
    checks = (
        ("unified_diff_syntactically_valid", "unified diff is malformed"),
        (
            "at_least_one_grounded_implementation_target_changed",
            "no grounded implementation target changed",
        ),
        ("all_changed_paths_grounded", "an ungrounded path changed"),
    )
    blockers.extend(message for field, message in checks if observations.get(field) is not True)
    if observations.get("requested_semantic_change_machine_check_available") is True and (
        observations.get("requested_semantic_change_present") is not True
    ):
        blockers.append("requested semantic change is absent")
    if observations.get("tests_passed_claim_present") is True:
        blockers.append("output claims tests passed before patch application")
    if observations.get("patch_applied_claim_present") is True:
        blockers.append("output claims the patch was applied")
    return blockers


def _load_review_wrappers(replay_path: Path) -> list[dict[str, Any]]:
    wrappers = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("task-outcome review Replay ordering mismatch")
        verify_replay_hash(wrapper)
        _verify_artifact(wrapper.get("artifact"), "task-outcome review Replay artifact")
        wrappers.append(wrapper)
    return wrappers


def _persist(root: Path, index: int, artifact: dict[str, Any]) -> None:
    step = REPLAY_STEPS[index]
    wrapper = {
        "event_type": step.upper(),
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(root / f"{index:03d}_{step}.json", wrapper)


def _ensure_review_destination_available(root: Path) -> None:
    if any(
        (root / f"{index:03d}_{step}.json").exists()
        for index, step in enumerate(REPLAY_STEPS)
    ):
        raise FailClosedRuntimeError("task-outcome review Replay destination already exists")


def _reject_duplicate_review(root: Path, review_identity: str) -> None:
    for path in root.rglob("000_task_outcome_review_packet_recorded.json"):
        wrapper = load_json(path)
        verify_replay_hash(wrapper)
        if (wrapper.get("artifact") or {}).get("review_identity") == review_identity:
            raise FailClosedRuntimeError("task-outcome result lineage was already reviewed")


def _reject_repeated_decision(root: Path, approval_required_hash: str) -> None:
    for path in root.rglob("000_human_decision_recorded.json"):
        wrapper = load_json(path)
        verify_replay_hash(wrapper)
        if (wrapper.get("artifact") or {}).get(
            "approval_required_hash"
        ) == approval_required_hash:
            raise FailClosedRuntimeError("task-outcome human decision already recorded")


def _verify_artifact(artifact: Any, label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} is missing")
    candidate = deepcopy(artifact)
    actual = candidate.pop("artifact_hash", None)
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_embedded_hash(artifact: Any, field: str, label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} is missing")
    candidate = deepcopy(artifact)
    actual = candidate.pop(field, None)
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _decision(value: Any) -> str:
    if not isinstance(value, str) or value.strip().upper() not in DECISION_TO_HUMAN_DECISION:
        raise FailClosedRuntimeError("task-outcome decision is invalid")
    return value.strip().upper()


def _required(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"task-outcome review requires {label}")
    return value.strip()
