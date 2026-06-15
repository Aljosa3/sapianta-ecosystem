"""Replay-visible Implementation Plan to Execution Request Runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.execution_request_runtime import (
    CREATED_STATUS,
    EXECUTION_REQUEST_ARTIFACT_V1,
)
from aigol.runtime.improvement_approval_runtime import (
    APPROVED,
    IMPROVEMENT_APPROVAL_ARTIFACT_V1,
)
from aigol.runtime.improvement_implementation_runtime import (
    IMPLEMENTATION_PLAN_CREATED,
    IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST_RUNTIME_VERSION = (
    "IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST_RUNTIME_V1"
)
IMPLEMENTATION_PLAN_EXECUTION_REQUEST_LINK_ARTIFACT_V1 = (
    "IMPLEMENTATION_PLAN_EXECUTION_REQUEST_LINK_ARTIFACT_V1"
)
IMPLEMENTATION_PLAN_EXECUTION_REQUEST_CREATED = "IMPLEMENTATION_PLAN_EXECUTION_REQUEST_CREATED"
IMPLEMENTATION_PLAN_EXECUTION_REQUEST_LINKED = "IMPLEMENTATION_PLAN_EXECUTION_REQUEST_LINKED"

REPLAY_STEPS = (
    "implementation_plan_execution_request_created",
    "implementation_plan_execution_request_linked",
)
VALID_REQUEST_TYPES = frozenset({"CAPABILITY_EXECUTION_REQUEST"})
FORBIDDEN_PAYLOAD_FIELDS = frozenset(
    {
        "automatic_authorization",
        "approval_decision",
        "authorization_decision",
        "provider_command",
        "worker_command",
        "worker_instruction",
        "dispatch_target",
        "dispatch_now",
        "invoke_worker_now",
        "execute_now",
        "implementation_performed",
        "code_mutated",
        "governance_mutated",
        "replay_mutated",
        "self_apply",
        "self_improvement",
        "credentials",
        "api_key",
        "secret",
    }
)
FORBIDDEN_TEXT_FRAGMENTS = (
    "execute now",
    "dispatch worker now",
    "invoke worker now",
    "self-apply",
    "self apply",
    "self-improve",
    "self improve",
    "mutate governance",
    "repair replay",
)


def create_implementation_plan_execution_request(
    *,
    bridge_id: str,
    execution_request_id: str,
    implementation_plan_artifact: dict[str, Any],
    improvement_approval_artifact: dict[str, Any],
    canonical_chain_id: str,
    human_authorization_reference: str,
    requested_by: str,
    created_at: str,
    request_type: str,
    request_payload: dict[str, Any],
    replay_reference: str,
    replay_dir: str | Path,
    status: str = CREATED_STATUS,
) -> dict[str, Any]:
    """Create a governed execution request from an approved implementation plan."""

    replay_path = Path(replay_dir)
    _ensure_bridge_replay_available(replay_path)
    chain_id = _require_string(canonical_chain_id, "canonical_chain_id")
    plan = _validate_implementation_plan_artifact(implementation_plan_artifact, chain_id)
    approval = _validate_improvement_approval_artifact(improvement_approval_artifact, plan, chain_id)
    authorization = _require_string(human_authorization_reference, "human_authorization_reference")
    if authorization == plan["human_authorization_reference"]:
        raise FailClosedRuntimeError(
            "implementation plan execution request failed closed: explicit execution authorization is required"
        )
    request = _execution_request_artifact(
        execution_request_id=execution_request_id,
        plan=plan,
        approval=approval,
        canonical_chain_id=chain_id,
        human_authorization_reference=authorization,
        requested_by=requested_by,
        created_at=created_at,
        request_type=request_type,
        request_payload=request_payload,
        replay_reference=replay_reference,
        status=status,
    )
    link = _bridge_link_artifact(
        bridge_id=bridge_id,
        request=request,
        plan=plan,
        approval=approval,
        canonical_chain_id=chain_id,
        human_authorization_reference=authorization,
        requested_by=requested_by,
        created_at=created_at,
        replay_reference=replay_reference,
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], request)
    _persist_step(replay_path, 1, REPLAY_STEPS[1], link)
    return _capture(request, link)


def reconstruct_implementation_plan_execution_request_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Implementation Plan to Execution Request replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("implementation plan execution request replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError(
                "implementation plan execution request replay artifact must be a JSON object"
            )
        _verify_artifact_hash(artifact, "implementation plan execution request artifact")
        wrappers.append(wrapper)

    request = wrappers[0]["artifact"]
    link = wrappers[1]["artifact"]
    if link.get("execution_request_reference") != request["execution_request_id"]:
        raise FailClosedRuntimeError("implementation plan execution request replay reference mismatch")
    if link.get("execution_request_hash") != request["artifact_hash"]:
        raise FailClosedRuntimeError("implementation plan execution request replay hash mismatch")
    if link.get("implementation_plan_reference") != request["implementation_plan_reference"]:
        raise FailClosedRuntimeError("implementation plan execution request replay plan reference mismatch")
    if link.get("implementation_plan_hash") != request["implementation_plan_hash"]:
        raise FailClosedRuntimeError("implementation plan execution request replay plan hash mismatch")
    if link.get("canonical_chain_id") != request["canonical_chain_id"]:
        raise FailClosedRuntimeError("implementation plan execution request replay chain mismatch")
    if link.get("human_authorization_reference") != request["human_authorization_reference"]:
        raise FailClosedRuntimeError("implementation plan execution request replay authorization mismatch")
    _validate_execution_request_artifact(request)
    _validate_bridge_link_artifact(link)
    return {
        "bridge_id": link["bridge_id"],
        "execution_request_id": request["execution_request_id"],
        "execution_request_source_type": request["execution_request_source_type"],
        "implementation_plan_reference": request["implementation_plan_reference"],
        "improvement_approval_reference": request["improvement_approval_reference"],
        "canonical_chain_id": request["canonical_chain_id"],
        "human_authorization_reference": request["human_authorization_reference"],
        "requested_by": request["requested_by"],
        "created_at": request["created_at"],
        "request_type": request["request_type"],
        "status": request["status"],
        "execution_request_created": True,
        "automatic_authorization": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_performed": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "self_application_performed": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _execution_request_artifact(
    *,
    execution_request_id: str,
    plan: dict[str, Any],
    approval: dict[str, Any],
    canonical_chain_id: str,
    human_authorization_reference: str,
    requested_by: str,
    created_at: str,
    request_type: str,
    request_payload: dict[str, Any],
    replay_reference: str,
    status: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": EXECUTION_REQUEST_ARTIFACT_V1,
        "execution_request_runtime_version": IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST_RUNTIME_VERSION,
        "execution_request_id": _require_string(execution_request_id, "execution_request_id"),
        "execution_request_source_type": IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1,
        "implementation_plan_reference": plan["implementation_plan_id"],
        "implementation_plan_hash": plan["artifact_hash"],
        "improvement_approval_reference": approval["improvement_approval_id"],
        "improvement_approval_hash": approval["artifact_hash"],
        "improvement_review_reference": plan["improvement_review_reference"],
        "improvement_review_hash": plan["improvement_review_hash"],
        "improvement_proposal_reference": plan["improvement_proposal_reference"],
        "improvement_proposal_hash": plan["improvement_proposal_hash"],
        "evaluation_reference": plan["evaluation_reference"],
        "evaluation_hash": plan["evaluation_hash"],
        "result_reference": plan["result_reference"],
        "result_hash": plan["result_hash"],
        "worker_reference": plan["worker_reference"],
        "canonical_chain_id": canonical_chain_id,
        "human_authorization_reference": human_authorization_reference,
        "requested_by": _normalize_token(requested_by, "requested_by"),
        "created_at": _require_string(created_at, "created_at"),
        "request_type": _normalize_token(request_type, "request_type"),
        "request_payload": _validate_request_payload(request_payload),
        "status": _normalize_token(status, "status"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "provider_authority": False,
        "provider_invoked": False,
        "worker_authority": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_performed": False,
        "completion_performed": False,
        "approval_created": False,
        "automatic_authorization": False,
        "implementation_performed": False,
        "code_mutated": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "self_approved": False,
        "self_authorized": False,
        "self_implemented": False,
        "self_application_performed": False,
    }
    artifact["request_payload_hash"] = replay_hash(artifact["request_payload"])
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_execution_request_artifact(artifact)
    return artifact


def _bridge_link_artifact(
    *,
    bridge_id: str,
    request: dict[str, Any],
    plan: dict[str, Any],
    approval: dict[str, Any],
    canonical_chain_id: str,
    human_authorization_reference: str,
    requested_by: str,
    created_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    _verify_artifact_hash(request, "implementation-plan-derived execution request artifact")
    artifact = {
        "artifact_type": IMPLEMENTATION_PLAN_EXECUTION_REQUEST_LINK_ARTIFACT_V1,
        "implementation_plan_execution_request_runtime_version": (
            IMPLEMENTATION_PLAN_TO_EXECUTION_REQUEST_RUNTIME_VERSION
        ),
        "bridge_id": _require_string(bridge_id, "bridge_id"),
        "execution_request_reference": request["execution_request_id"],
        "execution_request_hash": request["artifact_hash"],
        "execution_request_source_type": IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1,
        "implementation_plan_reference": plan["implementation_plan_id"],
        "implementation_plan_hash": plan["artifact_hash"],
        "improvement_approval_reference": approval["improvement_approval_id"],
        "improvement_approval_hash": approval["artifact_hash"],
        "canonical_chain_id": canonical_chain_id,
        "human_authorization_reference": human_authorization_reference,
        "requested_by": _normalize_token(requested_by, "requested_by"),
        "created_at": _require_string(created_at, "created_at"),
        "status": CREATED_STATUS,
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "execution_request_created": True,
        "automatic_execution_request": False,
        "automatic_authorization": False,
        "provider_authority": False,
        "worker_authority": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "execution_performed": False,
        "completion_performed": False,
        "implementation_performed": False,
        "code_mutated": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "self_approved": False,
        "self_authorized": False,
        "self_implemented": False,
        "self_application_performed": False,
        "reconstruction_metadata": {
            "bridge_reconstructable": True,
            "implementation_plan_reconstructable": True,
            "execution_request_reconstructable": True,
            "human_authorization_required": True,
            "canonical_chain_continuous": True,
            "worker_dispatched": False,
            "worker_invoked": False,
            "execution_performed": False,
        },
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_bridge_link_artifact(artifact)
    return artifact


def _capture(request: dict[str, Any], link: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "execution_request_artifact": deepcopy(request),
        "implementation_plan_execution_request_link_artifact": deepcopy(link),
    }
    capture["implementation_plan_execution_request_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_bridge_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("implementation plan execution request replay step ordering mismatch")
    _verify_artifact_hash(artifact, "implementation plan execution request artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "event_type": IMPLEMENTATION_PLAN_EXECUTION_REQUEST_CREATED
        if index == 0
        else IMPLEMENTATION_PLAN_EXECUTION_REQUEST_LINKED,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _validate_implementation_plan_artifact(plan: dict[str, Any], canonical_chain_id: str) -> dict[str, Any]:
    if not isinstance(plan, dict):
        raise FailClosedRuntimeError("implementation plan execution request failed closed: plan is required")
    _verify_artifact_hash(plan, "implementation plan artifact")
    if plan.get("artifact_type") != IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1:
        raise FailClosedRuntimeError("implementation plan execution request failed closed: invalid implementation plan")
    if plan.get("canonical_chain_id") != canonical_chain_id:
        raise FailClosedRuntimeError("implementation plan execution request failed closed: chain mismatch")
    if plan.get("plan_status") != IMPLEMENTATION_PLAN_CREATED:
        raise FailClosedRuntimeError("implementation plan execution request failed closed: invalid implementation plan")
    if plan.get("implementation_authorized") is not True:
        raise FailClosedRuntimeError("implementation plan execution request failed closed: plan is not authorized")
    if plan.get("execution_request_created") is not False or plan.get("execution_request_reference") is not None:
        raise FailClosedRuntimeError(
            "implementation plan execution request failed closed: automatic execution request creation detected"
        )
    if plan.get("implementation_performed") is not False or plan.get("implementation_reference") is not None:
        raise FailClosedRuntimeError("implementation plan execution request failed closed: implementation performed")
    if plan.get("plan_text_hash") != replay_hash(plan.get("plan_text")):
        raise FailClosedRuntimeError("implementation plan execution request failed closed: corrupt references")
    if plan.get("plan_scope_hash") != replay_hash(plan.get("plan_scope")):
        raise FailClosedRuntimeError("implementation plan execution request failed closed: corrupt references")
    if plan.get("plan_constraints_hash") != replay_hash(plan.get("plan_constraints")):
        raise FailClosedRuntimeError("implementation plan execution request failed closed: corrupt references")
    if plan.get("planned_artifact_targets_hash") != replay_hash(plan.get("planned_artifact_targets")):
        raise FailClosedRuntimeError("implementation plan execution request failed closed: corrupt references")
    if plan.get("planned_validation_hash") != replay_hash(plan.get("planned_validation")):
        raise FailClosedRuntimeError("implementation plan execution request failed closed: corrupt references")
    if plan.get("replay_visible") is not True:
        raise FailClosedRuntimeError("implementation plan execution request failed closed: replay visibility missing")
    for field in (
        "provider_authority",
        "worker_authority",
        "aigol_autonomous_implementation",
        "self_improvement_authority",
        "governance_mutation_authority",
        "code_mutated",
        "configuration_mutated",
        "governance_mutated",
        "replay_mutated",
        "worker_dispatched",
        "worker_invoked",
        "self_modification_performed",
        "self_improvement_performed",
        "self_application_performed",
    ):
        if plan.get(field) is not False:
            raise FailClosedRuntimeError(
                "implementation plan execution request failed closed: invalid implementation plan authority"
            )
    _require_string(plan.get("implementation_plan_id"), "implementation_plan_id")
    _require_string(plan.get("improvement_approval_reference"), "improvement_approval_reference")
    _require_string(plan.get("improvement_approval_hash"), "improvement_approval_hash")
    _require_string(plan.get("human_authorization_reference"), "human_authorization_reference")
    return deepcopy(plan)


def _validate_improvement_approval_artifact(
    approval: dict[str, Any],
    plan: dict[str, Any],
    canonical_chain_id: str,
) -> dict[str, Any]:
    if not isinstance(approval, dict):
        raise FailClosedRuntimeError("implementation plan execution request failed closed: approval is required")
    _verify_artifact_hash(approval, "improvement approval artifact")
    if approval.get("artifact_type") != IMPROVEMENT_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("implementation plan execution request failed closed: invalid approval")
    if approval.get("canonical_chain_id") != canonical_chain_id:
        raise FailClosedRuntimeError("implementation plan execution request failed closed: chain mismatch")
    if approval.get("decision") != APPROVED or approval.get("approval_status") != APPROVED:
        raise FailClosedRuntimeError("implementation plan execution request failed closed: approval must be APPROVED")
    if approval.get("implementation_authorized") is not True:
        raise FailClosedRuntimeError("implementation plan execution request failed closed: implementation is not authorized")
    _require_summary_bound_confirmation(approval)
    if approval.get("improvement_approval_id") != plan["improvement_approval_reference"]:
        raise FailClosedRuntimeError("implementation plan execution request failed closed: approval reference mismatch")
    if approval.get("artifact_hash") != plan["improvement_approval_hash"]:
        raise FailClosedRuntimeError("implementation plan execution request failed closed: approval hash mismatch")
    if approval.get("decision_authority") != "HUMAN":
        raise FailClosedRuntimeError("implementation plan execution request failed closed: decision authority must be HUMAN")
    if approval.get("decision_reason_hash") != replay_hash(approval.get("decision_reason")):
        raise FailClosedRuntimeError("implementation plan execution request failed closed: corrupt references")
    if approval.get("replay_visible") is not True:
        raise FailClosedRuntimeError("implementation plan execution request failed closed: approval replay visibility missing")
    for field in (
        "provider_authority",
        "worker_authority",
        "aigol_autonomous_approval",
        "implementation_authority",
        "self_improvement_authority",
        "governance_mutation_authority",
        "implementation_performed",
        "execution_requested",
        "worker_dispatched",
        "worker_invoked",
        "governance_mutated",
        "replay_mutated",
        "proposal_mutated",
        "review_mutated",
        "evaluation_mutated",
        "result_mutated",
        "execution_history_modified",
        "self_modification_performed",
        "self_improvement_performed",
    ):
        if approval.get(field) is not False:
            raise FailClosedRuntimeError(
                "implementation plan execution request failed closed: invalid approval authority"
            )
    _require_string(approval.get("improvement_approval_id"), "improvement_approval_id")
    _require_string(approval.get("human_authorization_reference"), "human_authorization_reference")
    return deepcopy(approval)


def _require_summary_bound_confirmation(approval: dict[str, Any]) -> None:
    _require_string(approval.get("execution_summary_reference"), "execution_summary_reference")
    _require_hash(approval.get("execution_summary_hash"), "execution_summary_hash")
    _require_string(approval.get("human_confirmation_reference"), "human_confirmation_reference")
    _require_hash(approval.get("human_confirmation_hash"), "human_confirmation_hash")


def _validate_request_payload(request_payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(request_payload, dict) or not request_payload:
        raise FailClosedRuntimeError("implementation plan execution request failed closed: request_payload is required")
    if FORBIDDEN_PAYLOAD_FIELDS.intersection(request_payload):
        raise FailClosedRuntimeError(
            "implementation plan execution request failed closed: authority-bearing request payload"
        )
    serialized = replay_hash(request_payload)
    for value in _walk_values(request_payload):
        if isinstance(value, str):
            lowered = value.lower()
            if any(fragment in lowered for fragment in FORBIDDEN_TEXT_FRAGMENTS):
                raise FailClosedRuntimeError(
                    "implementation plan execution request failed closed: authority-bearing request payload"
                )
    replay_hash(serialized)
    return deepcopy(request_payload)


def _validate_execution_request_artifact(request: dict[str, Any]) -> None:
    if request.get("artifact_type") != EXECUTION_REQUEST_ARTIFACT_V1:
        raise FailClosedRuntimeError("implementation plan execution request failed closed: invalid execution request")
    if request.get("execution_request_source_type") != IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1:
        raise FailClosedRuntimeError("implementation plan execution request failed closed: invalid execution request source")
    if request.get("requested_by") != "AIGOL":
        raise FailClosedRuntimeError("implementation plan execution request failed closed: requested_by must be AIGOL")
    if request.get("request_type") not in VALID_REQUEST_TYPES:
        raise FailClosedRuntimeError("implementation plan execution request failed closed: invalid request_type")
    if request.get("status") != CREATED_STATUS:
        raise FailClosedRuntimeError("implementation plan execution request failed closed: invalid status")
    if request.get("request_payload_hash") != replay_hash(request.get("request_payload")):
        raise FailClosedRuntimeError("implementation plan execution request failed closed: request payload hash mismatch")
    for field in (
        "replay_visible",
    ):
        if request.get(field) is not True:
            raise FailClosedRuntimeError("implementation plan execution request failed closed: replay visibility missing")
    for field in (
        "provider_authority",
        "provider_invoked",
        "worker_authority",
        "worker_dispatched",
        "worker_invoked",
        "execution_performed",
        "completion_performed",
        "approval_created",
        "automatic_authorization",
        "implementation_performed",
        "code_mutated",
        "governance_mutated",
        "replay_mutated",
        "self_approved",
        "self_authorized",
        "self_implemented",
        "self_application_performed",
    ):
        if request.get(field) is not False:
            raise FailClosedRuntimeError(
                "implementation plan execution request failed closed: forbidden request authority introduced"
            )
    _require_string(request.get("execution_request_id"), "execution_request_id")
    _require_string(request.get("implementation_plan_reference"), "implementation_plan_reference")
    _require_string(request.get("implementation_plan_hash"), "implementation_plan_hash")
    _require_string(request.get("improvement_approval_reference"), "improvement_approval_reference")
    _require_string(request.get("improvement_approval_hash"), "improvement_approval_hash")
    _require_string(request.get("canonical_chain_id"), "canonical_chain_id")
    _require_string(request.get("human_authorization_reference"), "human_authorization_reference")
    _require_string(request.get("created_at"), "created_at")
    _require_string(request.get("replay_reference"), "replay_reference")


def _validate_bridge_link_artifact(link: dict[str, Any]) -> None:
    if link.get("artifact_type") != IMPLEMENTATION_PLAN_EXECUTION_REQUEST_LINK_ARTIFACT_V1:
        raise FailClosedRuntimeError("implementation plan execution request failed closed: invalid bridge link")
    if link.get("requested_by") != "AIGOL":
        raise FailClosedRuntimeError("implementation plan execution request failed closed: requested_by must be AIGOL")
    if link.get("status") != CREATED_STATUS:
        raise FailClosedRuntimeError("implementation plan execution request failed closed: invalid bridge status")
    if link.get("execution_request_created") is not True:
        raise FailClosedRuntimeError("implementation plan execution request failed closed: bridge request missing")
    for field in (
        "replay_visible",
    ):
        if link.get(field) is not True:
            raise FailClosedRuntimeError("implementation plan execution request failed closed: replay visibility missing")
    for field in (
        "automatic_execution_request",
        "automatic_authorization",
        "provider_authority",
        "worker_authority",
        "worker_dispatched",
        "worker_invoked",
        "execution_performed",
        "completion_performed",
        "implementation_performed",
        "code_mutated",
        "governance_mutated",
        "replay_mutated",
        "self_approved",
        "self_authorized",
        "self_implemented",
        "self_application_performed",
    ):
        if link.get(field) is not False:
            raise FailClosedRuntimeError(
                "implementation plan execution request failed closed: forbidden bridge authority introduced"
            )
    _require_string(link.get("bridge_id"), "bridge_id")
    _require_string(link.get("execution_request_reference"), "execution_request_reference")
    _require_string(link.get("execution_request_hash"), "execution_request_hash")
    _require_string(link.get("implementation_plan_reference"), "implementation_plan_reference")
    _require_string(link.get("implementation_plan_hash"), "implementation_plan_hash")
    _require_string(link.get("improvement_approval_reference"), "improvement_approval_reference")
    _require_string(link.get("improvement_approval_hash"), "improvement_approval_hash")
    _require_string(link.get("canonical_chain_id"), "canonical_chain_id")
    _require_string(link.get("human_authorization_reference"), "human_authorization_reference")


def _walk_values(value: Any) -> list[Any]:
    if isinstance(value, dict):
        values: list[Any] = []
        for item in value.values():
            values.extend(_walk_values(item))
        return values
    if isinstance(value, list):
        values = []
        for item in value:
            values.extend(_walk_values(item))
        return values
    return [value]


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("implementation plan execution request replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("implementation plan execution request replay hash mismatch")


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value


def _require_hash(value: Any, field_name: str) -> str:
    text = _require_string(value, field_name)
    if not text.startswith("sha256:"):
        raise FailClosedRuntimeError(f"{field_name} must be a replay hash")
    return text
