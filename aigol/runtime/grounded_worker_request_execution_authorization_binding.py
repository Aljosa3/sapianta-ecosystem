"""Bind grounded Worker requests to the existing execution-authorization review."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.approved_durable_work_repository_scope_grounding import (
    REPOSITORY_SCOPE_GROUNDED,
    reconstruct_approved_durable_work_repository_scope_grounding,
    validate_approved_durable_work_repository_scope_grounding,
)
from aigol.runtime.execution_authorization_runtime import (
    EXECUTION_AUTHORIZATION_ARTIFACT_V1,
    EXECUTION_AUTHORIZATION_DECISION_ARTIFACT_V1,
    EXECUTION_AUTHORIZATION_REQUEST_ARTIFACT_V1,
)
from aigol.runtime.execution_summary_runtime import (
    EXECUTION_SUMMARY_HUMAN_CONFIRMATION_ARTIFACT_V1,
    PENDING_HUMAN_CONFIRMATION,
    create_execution_summary,
    verify_execution_summary,
)
from aigol.runtime.implementation_request_to_worker_request_bridge_runtime import (
    validate_worker_request_artifact,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import (
    load_json,
    replay_hash,
    verify_replay_hash,
    write_json_immutable,
)


GROUNDED_WORKER_AUTHORIZATION_BINDING_VERSION = (
    "G31_08_GROUNDED_WORKER_REQUEST_EXECUTION_AUTHORIZATION_BINDING_V1"
)
GROUNDED_WORKER_AUTHORIZATION_REVIEW_BINDING_ARTIFACT_V1 = (
    "GROUNDED_WORKER_REQUEST_EXECUTION_AUTHORIZATION_REVIEW_BINDING_ARTIFACT_V1"
)
EXECUTION_AUTHORIZATION_REVIEW_REQUIRED = (
    "GROUNDED_WORKER_REQUEST_EXECUTION_AUTHORIZATION_REVIEW_REQUIRED"
)
EXECUTION_AUTHORIZATION_REVIEW_FAILED_CLOSED = (
    "GROUNDED_WORKER_REQUEST_EXECUTION_AUTHORIZATION_REVIEW_FAILED_CLOSED"
)
REPLAY_STEPS = (
    "repository_scope_grounding_source_recorded",
    "execution_authorization_review_binding_recorded",
)

FALSE_BOUNDARIES = {
    "proposal_approval_is_execution_authorization": False,
    "human_confirmation_recorded": False,
    "authorization_request_created": False,
    "authorization_decision_created": False,
    "execution_authorization_created": False,
    "execution_authorized": False,
    "worker_selected": False,
    "worker_assigned": False,
    "worker_dispatched": False,
    "worker_invoked": False,
    "provider_invoked": False,
    "execution_started": False,
    "repository_mutated": False,
    "validation_executed": False,
    "certification_reached": False,
    "human_interface_authority": False,
    "human_interface_authorization_authority": False,
    "human_interface_policy_authority": False,
    "human_interface_worker_authority": False,
    "human_interface_mutation_authority": False,
    "human_interface_replay_authority": False,
}


def bind_grounded_worker_request_to_execution_authorization_review(
    *,
    repository_scope_grounding_artifact: dict[str, Any],
    workspace: str | Path,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create one pending authorization review without authorizing execution."""

    replay_root = Path(replay_dir)
    _ensure_replay_available(replay_root)
    source_observation = deepcopy(repository_scope_grounding_artifact)
    _persist_step(replay_root, 0, REPLAY_STEPS[0], source_observation)
    try:
        grounding = validate_approved_durable_work_repository_scope_grounding(
            repository_scope_grounding_artifact,
            workspace=workspace,
        )
        if grounding.get("grounding_status") != REPOSITORY_SCOPE_GROUNDED:
            raise FailClosedRuntimeError(
                "execution authorization review requires grounded repository scope"
            )
        reconstructed = reconstruct_approved_durable_work_repository_scope_grounding(
            grounding["replay_reference"],
            workspace=workspace,
        )
        if reconstructed["artifact_hash"] != grounding["artifact_hash"]:
            raise FailClosedRuntimeError(
                "execution authorization review grounding Replay mismatch"
            )
        worker_request = validate_worker_request_artifact(
            grounding["grounded_worker_request_artifact"]
        )
        authorization_scope = _exact_authorization_scope(
            grounding=grounding,
            worker_request=worker_request,
        )
        execution_summary = _pending_execution_summary(
            grounding=grounding,
            worker_request=worker_request,
            authorization_scope=authorization_scope,
            created_at=created_at,
        )
        binding = _review_binding_artifact(
            grounding=grounding,
            worker_request=worker_request,
            authorization_scope=authorization_scope,
            execution_summary=execution_summary,
            created_at=created_at,
            replay_reference=str(replay_root),
        )
        validate_grounded_worker_request_execution_authorization_review(
            binding,
            workspace=workspace,
        )
    except Exception as exc:
        binding = _failed_review_binding_artifact(
            source_observation=source_observation,
            created_at=created_at,
            replay_reference=str(replay_root),
            failure_reason=_failure_reason(exc),
        )
    _persist_step(replay_root, 1, REPLAY_STEPS[1], binding)
    return deepcopy(binding)


def validate_grounded_worker_request_execution_authorization_review(
    artifact: dict[str, Any],
    *,
    workspace: str | Path | None = None,
) -> dict[str, Any]:
    """Validate exact scope, lineage, pending human review, and authority limits."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("execution authorization review must be a dict")
    candidate = deepcopy(artifact)
    if candidate.get("artifact_type") != (
        GROUNDED_WORKER_AUTHORIZATION_REVIEW_BINDING_ARTIFACT_V1
    ):
        raise FailClosedRuntimeError("execution authorization review type is invalid")
    if candidate.get("runtime_version") != GROUNDED_WORKER_AUTHORIZATION_BINDING_VERSION:
        raise FailClosedRuntimeError("execution authorization review version is invalid")
    verify_replay_hash(candidate, hash_field="artifact_hash")
    for field, expected in FALSE_BOUNDARIES.items():
        if candidate.get(field) is not expected:
            raise FailClosedRuntimeError(
                f"execution authorization review authority boundary mismatch: {field}"
            )
    status = candidate.get("authorization_review_status")
    if status == EXECUTION_AUTHORIZATION_REVIEW_FAILED_CLOSED:
        if candidate.get("fail_closed") is not True or not candidate.get(
            "failure_reason"
        ):
            raise FailClosedRuntimeError(
                "failed execution authorization review requires a reason"
            )
        if candidate.get("authorization_scope") or candidate.get(
            "execution_summary_artifact"
        ):
            raise FailClosedRuntimeError(
                "failed execution authorization review cannot contain scope"
            )
        return candidate
    if status != EXECUTION_AUTHORIZATION_REVIEW_REQUIRED:
        raise FailClosedRuntimeError("execution authorization review status is invalid")
    if candidate.get("fail_closed") is not False:
        raise FailClosedRuntimeError("pending execution authorization review failed closed")
    grounding = validate_approved_durable_work_repository_scope_grounding(
        candidate.get("source_repository_scope_grounding_artifact"),
        workspace=workspace,
    )
    if grounding.get("grounding_status") != REPOSITORY_SCOPE_GROUNDED:
        raise FailClosedRuntimeError("execution authorization review source is not grounded")
    worker_request = validate_worker_request_artifact(
        grounding["grounded_worker_request_artifact"]
    )
    for field, expected in _upstream_identities(grounding).items():
        if candidate.get(field) != expected:
            raise FailClosedRuntimeError(
                f"execution authorization review upstream identity mismatch: {field}"
            )
    expected_scope = _exact_authorization_scope(
        grounding=grounding,
        worker_request=worker_request,
    )
    if candidate.get("authorization_scope") != expected_scope:
        raise FailClosedRuntimeError("execution authorization review scope mismatch")
    if candidate.get("authorization_scope_hash") != expected_scope["scope_hash"]:
        raise FailClosedRuntimeError("execution authorization review scope hash mismatch")
    summary = verify_execution_summary(candidate.get("execution_summary_artifact"))
    if summary.get("execution_scope") != expected_scope:
        raise FailClosedRuntimeError("execution summary scope differs from grounding")
    if summary.get("summary_status") != PENDING_HUMAN_CONFIRMATION:
        raise FailClosedRuntimeError("execution authorization review is not pending")
    if candidate.get("execution_summary_hash") != summary["artifact_hash"]:
        raise FailClosedRuntimeError("execution authorization review summary hash mismatch")
    if candidate.get("distinct_human_execution_authorization_required") is not True:
        raise FailClosedRuntimeError("distinct human execution authorization is required")
    if candidate.get("dispatch_blocked_pending_authorization") is not True:
        raise FailClosedRuntimeError("authorization review must block dispatch")
    if candidate.get("stop_before_worker_selection") is not True:
        raise FailClosedRuntimeError("authorization review crossed Worker selection")
    if candidate.get("human_confirmation_artifact") is not None:
        raise FailClosedRuntimeError("authorization review cannot synthesize confirmation")
    return candidate


def reconstruct_grounded_worker_request_execution_authorization_review(
    replay_dir: str | Path,
    *,
    workspace: str | Path | None = None,
) -> dict[str, Any]:
    """Reconstruct ordered grounding-to-authorization-review Replay."""

    root = Path(replay_dir)
    wrappers = [
        load_json(root / f"{index:03d}_{step}.json")
        for index, step in enumerate(REPLAY_STEPS)
    ]
    for index, (step, wrapper) in enumerate(zip(REPLAY_STEPS, wrappers)):
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError(
                "execution authorization review Replay ordering mismatch"
            )
        verify_replay_hash(wrapper, hash_field="replay_hash")
    binding = validate_grounded_worker_request_execution_authorization_review(
        wrappers[1]["artifact"],
        workspace=workspace,
    )
    if binding["authorization_review_status"] == (
        EXECUTION_AUTHORIZATION_REVIEW_FAILED_CLOSED
    ):
        if binding.get("source_grounding_observation_hash") != replay_hash(
            wrappers[0]["artifact"]
        ):
            raise FailClosedRuntimeError(
                "failed authorization review source observation mismatch"
            )
        return binding
    grounding = validate_approved_durable_work_repository_scope_grounding(
        wrappers[0]["artifact"],
        workspace=workspace,
    )
    reconstructed = reconstruct_approved_durable_work_repository_scope_grounding(
        grounding["replay_reference"],
        workspace=workspace,
    )
    if reconstructed["artifact_hash"] != grounding["artifact_hash"]:
        raise FailClosedRuntimeError(
            "execution authorization review source Replay mismatch"
        )
    if binding["source_repository_scope_grounding_hash"] != grounding["artifact_hash"]:
        raise FailClosedRuntimeError(
            "execution authorization review Replay lineage mismatch"
        )
    return binding


def render_grounded_worker_request_execution_authorization_review(
    artifact: dict[str, Any],
) -> str:
    review = validate_grounded_worker_request_execution_authorization_review(artifact)
    return "\n".join(
        [
            "Grounded Worker request execution-authorization review",
            f"authorization_review_status: {review['authorization_review_status']}",
            f"repository_scope_grounding_hash: {review.get('source_repository_scope_grounding_hash')}",
            f"grounded_worker_request_hash: {review.get('source_grounded_worker_request_hash')}",
            f"authorization_scope_hash: {review.get('authorization_scope_hash')}",
            f"execution_summary_hash: {review.get('execution_summary_hash')}",
            f"distinct_human_execution_authorization_required: {review.get('distinct_human_execution_authorization_required')}",
            f"proposal_approval_is_execution_authorization: {review['proposal_approval_is_execution_authorization']}",
            f"execution_authorized: {review['execution_authorized']}",
            f"worker_selected: {review['worker_selected']}",
            f"worker_dispatched: {review['worker_dispatched']}",
            f"provider_invoked: {review['provider_invoked']}",
            f"worker_invoked: {review['worker_invoked']}",
            f"repository_mutated: {review['repository_mutated']}",
            f"failure_reason: {review['failure_reason']}",
            f"replay_reference: {review['replay_reference']}",
        ]
    )


def _exact_authorization_scope(
    *,
    grounding: dict[str, Any],
    worker_request: dict[str, Any],
) -> dict[str, Any]:
    implementation_scope = worker_request["implementation_scope"]
    target_evidence = deepcopy(grounding["target_evidence"])
    scope = {
        "workspace_root": grounding["workspace_root"],
        "repository_scope_grounding_identity": grounding["grounding_identity"],
        "repository_scope_grounding_hash": grounding["artifact_hash"],
        "repository_cognition_snapshot_hash": grounding[
            "repository_cognition_snapshot_hash"
        ],
        "grounding_evidence_hash": grounding["grounding_evidence_hash"],
        "grounded_worker_request_reference": worker_request["worker_request_id"],
        "grounded_worker_request_hash": worker_request["artifact_hash"],
        "repository_targets": deepcopy(grounding["grounded_repository_targets"]),
        "source_paths": deepcopy(grounding["grounded_source_targets"]),
        "focused_test_paths": deepcopy(grounding["grounded_focused_test_targets"]),
        "target_evidence": target_evidence,
        "symbols_by_path": [
            {
                "target_path": item["target_path"],
                "symbols": deepcopy(item["symbols"]),
                "source_content_hash": item["source_content_hash"],
                "target_evidence_hash": item["target_evidence_hash"],
            }
            for item in target_evidence
        ],
        "mutation_layers": [
            {
                "target_path": item["target_path"],
                "mutation_layer": item["mutation_layer"],
                "mapping_rule": item["mutation_layer_mapping_rule"],
            }
            for item in target_evidence
        ],
        "validation_requirements": deepcopy(
            implementation_scope["validation_requirements"]
        ),
        "original_human_goal": implementation_scope["original_human_goal"],
        "original_human_goal_hash": implementation_scope[
            "original_human_goal_hash"
        ],
        "canonical_project_objective": implementation_scope[
            "canonical_project_objective"
        ],
        "project_objective_hash": implementation_scope["project_objective_hash"],
        "approved_bounded_work": deepcopy(implementation_scope["bounded_work_scope"]),
        "worker_objective": worker_request["worker_objective"],
        "approved_work_lineage": deepcopy(
            worker_request["canonical_approved_work_lineage"]
        ),
    }
    scope["scope_hash"] = replay_hash(scope)
    return scope


def _pending_execution_summary(
    *,
    grounding: dict[str, Any],
    worker_request: dict[str, Any],
    authorization_scope: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    return create_execution_summary(
        summary_id=f"{grounding['grounding_identity']}:EXECUTION-AUTHORIZATION-REVIEW",
        original_request=authorization_scope["original_human_goal"],
        interpreted_intent={
            "intent_type": "GROUNDED_WORKER_REQUEST_EXECUTION_AUTHORIZATION_REVIEW",
            "canonical_project_objective": authorization_scope[
                "canonical_project_objective"
            ],
            "project_objective_hash": authorization_scope[
                "project_objective_hash"
            ],
            "worker_objective": worker_request["worker_objective"],
        },
        selected_route={
            "route_type": "EXECUTION_AUTHORIZATION_RUNTIME",
            "current_stage": "PENDING_DISTINCT_HUMAN_CONFIRMATION",
            "repository_scope_grounding_hash": grounding["artifact_hash"],
        },
        planned_actions=[
            {
                "action": "REVIEW_EXACT_GROUNDED_SCOPE_FOR_EXECUTION_AUTHORIZATION",
                "scope_hash": authorization_scope["scope_hash"],
            }
        ],
        expected_outputs=[
            {
                "artifact_type": EXECUTION_SUMMARY_HUMAN_CONFIRMATION_ARTIFACT_V1,
                "status": "REQUIRES_SEPARATE_HUMAN_DECISION",
            }
        ],
        assumptions=[
            "G31-06 grounding Replay and current repository evidence were reconstructed and validated."
        ],
        constraints=[
            "Proposal approval is not execution authorization.",
            "No Worker selection, assignment, dispatch, invocation, or repository mutation is permitted by this review.",
            "Any later authorization scope must equal this grounded scope exactly.",
        ],
        risk_classification={
            "risk_level": "GOVERNED_EXECUTION_AUTHORIZATION_REVIEW",
            "reason": "A later human decision may enable an execution-capable transition.",
        },
        execution_scope=authorization_scope,
        replay_references=[grounding["replay_reference"]],
        created_by="PLATFORM_CORE_EXECUTION_AUTHORIZATION_REVIEW",
        created_at=_required_text(created_at, "created_at"),
    )


def _review_binding_artifact(
    *,
    grounding: dict[str, Any],
    worker_request: dict[str, Any],
    authorization_scope: dict[str, Any],
    execution_summary: dict[str, Any],
    created_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": GROUNDED_WORKER_AUTHORIZATION_REVIEW_BINDING_ARTIFACT_V1,
        "runtime_version": GROUNDED_WORKER_AUTHORIZATION_BINDING_VERSION,
        "authorization_review_status": EXECUTION_AUTHORIZATION_REVIEW_REQUIRED,
        "created_at": _required_text(created_at, "created_at"),
        "replay_reference": replay_reference,
        "source_repository_scope_grounding_artifact": deepcopy(grounding),
        **_upstream_identities(grounding),
        "authorization_scope": deepcopy(authorization_scope),
        "authorization_scope_hash": authorization_scope["scope_hash"],
        "execution_summary_artifact": deepcopy(execution_summary),
        "execution_summary_hash": execution_summary["artifact_hash"],
        "human_confirmation_artifact_type": (
            EXECUTION_SUMMARY_HUMAN_CONFIRMATION_ARTIFACT_V1
        ),
        "human_confirmation_artifact": None,
        "downstream_authorization_request_artifact_type": (
            EXECUTION_AUTHORIZATION_REQUEST_ARTIFACT_V1
        ),
        "downstream_authorization_decision_artifact_type": (
            EXECUTION_AUTHORIZATION_DECISION_ARTIFACT_V1
        ),
        "downstream_execution_authorization_artifact_type": (
            EXECUTION_AUTHORIZATION_ARTIFACT_V1
        ),
        "distinct_human_execution_authorization_required": True,
        "required_human_decision": "APPROVE_OR_REJECT_EXECUTION_AUTHORIZATION",
        "dispatch_blocked_pending_authorization": True,
        "stop_before_worker_selection": True,
        "fail_closed": False,
        "failure_reason": None,
        "replay_visible": True,
        **FALSE_BOUNDARIES,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_review_binding_artifact(
    *,
    source_observation: Any,
    created_at: Any,
    replay_reference: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": GROUNDED_WORKER_AUTHORIZATION_REVIEW_BINDING_ARTIFACT_V1,
        "runtime_version": GROUNDED_WORKER_AUTHORIZATION_BINDING_VERSION,
        "authorization_review_status": EXECUTION_AUTHORIZATION_REVIEW_FAILED_CLOSED,
        "created_at": created_at if isinstance(created_at, str) else "INVALID",
        "replay_reference": replay_reference,
        "source_grounding_observation_hash": replay_hash(source_observation),
        "source_repository_scope_grounding_artifact": None,
        "authorization_scope": {},
        "authorization_scope_hash": None,
        "execution_summary_artifact": None,
        "execution_summary_hash": None,
        "human_confirmation_artifact_type": (
            EXECUTION_SUMMARY_HUMAN_CONFIRMATION_ARTIFACT_V1
        ),
        "human_confirmation_artifact": None,
        "downstream_authorization_request_artifact_type": (
            EXECUTION_AUTHORIZATION_REQUEST_ARTIFACT_V1
        ),
        "downstream_authorization_decision_artifact_type": (
            EXECUTION_AUTHORIZATION_DECISION_ARTIFACT_V1
        ),
        "downstream_execution_authorization_artifact_type": (
            EXECUTION_AUTHORIZATION_ARTIFACT_V1
        ),
        "distinct_human_execution_authorization_required": True,
        "required_human_decision": None,
        "dispatch_blocked_pending_authorization": True,
        "stop_before_worker_selection": True,
        "fail_closed": True,
        "failure_reason": failure_reason,
        "replay_visible": True,
        **FALSE_BOUNDARIES,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _upstream_identities(grounding: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_repository_scope_grounding_hash": grounding["artifact_hash"],
        "source_grounding_evidence_hash": grounding["grounding_evidence_hash"],
        "source_repository_cognition_snapshot_hash": grounding[
            "repository_cognition_snapshot_hash"
        ],
        "source_worker_payload_binding_hash": grounding[
            "source_worker_payload_binding_hash"
        ],
        "source_implementation_turn_binding_hash": grounding[
            "source_implementation_turn_binding_hash"
        ],
        "source_approval_consumption_hash": grounding[
            "source_approval_consumption_hash"
        ],
        "source_development_composition_plan_hash": grounding[
            "source_development_composition_plan_hash"
        ],
        "source_durable_governed_work_hash": grounding[
            "source_durable_governed_work_hash"
        ],
        "source_proposal_preview_hash": grounding["source_proposal_preview_hash"],
        "source_approval_request_hash": grounding["source_approval_request_hash"],
        "source_ppp_task_package_hash": grounding["source_ppp_task_package_hash"],
        "source_implementation_request_hash": grounding[
            "source_implementation_request_hash"
        ],
        "source_worker_implementation_payload_hash": grounding[
            "source_worker_implementation_payload_hash"
        ],
        "source_grounded_worker_request_hash": grounding[
            "grounded_worker_request_hash"
        ],
    }


def _ensure_replay_available(root: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (root / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError(
                "execution authorization review Replay already exists"
            )


def _persist_step(
    root: Path,
    index: int,
    step: str,
    artifact: dict[str, Any],
) -> None:
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(root / f"{index:03d}_{step}.json", wrapper)


def _required_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"execution authorization review {field_name} required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "execution authorization review failed closed"
