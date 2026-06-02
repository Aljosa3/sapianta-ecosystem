"""Replay-visible Improvement Implementation Planning Runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.improvement_approval_runtime import (
    APPROVED,
    IMPROVEMENT_APPROVAL_ARTIFACT_V1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


IMPROVEMENT_IMPLEMENTATION_RUNTIME_VERSION = "IMPROVEMENT_IMPLEMENTATION_RUNTIME_V1"
IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1 = "IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1"
IMPLEMENTATION_PLAN_CREATED = "IMPLEMENTATION_PLAN_CREATED"
IMPROVEMENT_IMPLEMENTATION_PLAN_CREATED = "IMPROVEMENT_IMPLEMENTATION_PLAN_CREATED"
IMPROVEMENT_IMPLEMENTATION_PLAN_RETURNED = "IMPROVEMENT_IMPLEMENTATION_PLAN_RETURNED"

REPLAY_STEPS = ("improvement_implementation_plan_created", "improvement_implementation_plan_returned")
ALLOWED_PLAN_SOURCES = frozenset(
    {
        "AIGOL_DETERMINISTIC_PLANNING",
        "HUMAN_APPROVED_IMPROVEMENT",
        "PROVIDER_ASSISTED_NON_AUTHORITATIVE",
        "WORKER_REPORT_RECORDED",
        "COMBINED_EVIDENCE",
    }
)
FORBIDDEN_PLAN_FIELDS = frozenset(
    {
        "code_mutated",
        "configuration_mutated",
        "execution_request_created",
        "execution_request_reference",
        "worker_dispatched",
        "worker_invoked",
        "implementation_performed",
        "governance_mutation",
        "governance_mutated",
        "replay_repair",
        "replay_mutated",
        "self_modification",
        "self_improvement",
        "self_apply",
        "provider_command",
        "credentials",
        "api_key",
        "secret",
    }
)


def create_improvement_implementation_plan(
    *,
    implementation_plan_id: str,
    improvement_approval_artifact: dict[str, Any],
    canonical_chain_id: str,
    plan_source: str,
    plan_text: str,
    plan_scope: dict[str, Any],
    plan_constraints: dict[str, Any],
    planned_artifact_targets: list[str],
    planned_validation: list[str],
    created_by: str,
    created_at: str,
    replay_reference: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create an implementation plan without creating requests or changing code."""

    replay_path = Path(replay_dir)
    _ensure_plan_replay_available(replay_path)
    chain_id = _require_string(canonical_chain_id, "canonical_chain_id")
    approval = _validate_approval_artifact(improvement_approval_artifact, chain_id)
    scope = _validate_json_object(plan_scope, "plan_scope")
    constraints = _validate_json_object(plan_constraints, "plan_constraints")
    targets = _validate_string_list(planned_artifact_targets, "planned_artifact_targets")
    validation = _validate_string_list(planned_validation, "planned_validation")
    plan = _plan_artifact(
        implementation_plan_id=implementation_plan_id,
        approval=approval,
        canonical_chain_id=chain_id,
        plan_source=plan_source,
        plan_text=plan_text,
        plan_scope=scope,
        plan_constraints=constraints,
        planned_artifact_targets=targets,
        planned_validation=validation,
        created_by=created_by,
        created_at=created_at,
        replay_reference=replay_reference,
    )
    _persist_step(replay_path, 0, REPLAY_STEPS[0], plan)
    returned = _plan_returned(plan)
    _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
    return _capture(plan, returned)


def reconstruct_improvement_implementation_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Improvement Implementation Planning Runtime replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("improvement implementation replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("improvement implementation replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "improvement implementation plan artifact")
        wrappers.append(wrapper)

    plan = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("implementation_plan_reference") != plan["implementation_plan_id"]:
        raise FailClosedRuntimeError("improvement implementation replay reference mismatch")
    if returned.get("implementation_plan_hash") != plan["artifact_hash"]:
        raise FailClosedRuntimeError("improvement implementation replay hash mismatch")
    if returned.get("canonical_chain_id") != plan["canonical_chain_id"]:
        raise FailClosedRuntimeError("improvement implementation replay chain mismatch")
    if returned.get("improvement_approval_reference") != plan["improvement_approval_reference"]:
        raise FailClosedRuntimeError("improvement implementation replay approval reference mismatch")
    if returned.get("improvement_approval_hash") != plan["improvement_approval_hash"]:
        raise FailClosedRuntimeError("improvement implementation replay approval hash mismatch")
    _validate_plan_artifact(plan)
    return {
        "implementation_plan_id": plan["implementation_plan_id"],
        "canonical_chain_id": plan["canonical_chain_id"],
        "improvement_approval_reference": plan["improvement_approval_reference"],
        "improvement_proposal_reference": plan["improvement_proposal_reference"],
        "plan_status": plan["plan_status"],
        "execution_request_created": False,
        "implementation_performed": False,
        "created_at": plan["created_at"],
        "code_mutated": False,
        "configuration_mutated": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "self_improvement_performed": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _plan_artifact(
    *,
    implementation_plan_id: str,
    approval: dict[str, Any],
    canonical_chain_id: str,
    plan_source: str,
    plan_text: str,
    plan_scope: dict[str, Any],
    plan_constraints: dict[str, Any],
    planned_artifact_targets: list[str],
    planned_validation: list[str],
    created_by: str,
    created_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    source = _normalize_token(plan_source, "plan_source")
    if source not in ALLOWED_PLAN_SOURCES:
        raise FailClosedRuntimeError("improvement implementation failed closed: invalid plan source")
    text = _validate_plan_text(plan_text)
    artifact = {
        "artifact_type": IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1,
        "improvement_implementation_plan_version": IMPROVEMENT_IMPLEMENTATION_RUNTIME_VERSION,
        "implementation_plan_id": _require_string(implementation_plan_id, "implementation_plan_id"),
        "canonical_chain_id": canonical_chain_id,
        "improvement_approval_reference": approval["improvement_approval_id"],
        "improvement_approval_hash": approval["artifact_hash"],
        "improvement_review_reference": approval["improvement_review_reference"],
        "improvement_review_hash": approval["improvement_review_hash"],
        "improvement_proposal_reference": approval["improvement_proposal_reference"],
        "improvement_proposal_hash": approval["improvement_proposal_hash"],
        "evaluation_reference": approval["evaluation_reference"],
        "evaluation_hash": approval["evaluation_hash"],
        "result_reference": approval["result_reference"],
        "result_hash": approval["result_hash"],
        "worker_reference": approval["worker_reference"],
        "human_authorization_reference": approval["human_authorization_reference"],
        "plan_source": source,
        "plan_text": text,
        "plan_text_hash": replay_hash(text),
        "plan_scope": deepcopy(plan_scope),
        "plan_scope_hash": replay_hash(plan_scope),
        "plan_constraints": deepcopy(plan_constraints),
        "plan_constraints_hash": replay_hash(plan_constraints),
        "planned_artifact_targets": list(planned_artifact_targets),
        "planned_artifact_targets_hash": replay_hash(planned_artifact_targets),
        "planned_validation": list(planned_validation),
        "planned_validation_hash": replay_hash(planned_validation),
        "plan_status": IMPLEMENTATION_PLAN_CREATED,
        "execution_request_created": False,
        "execution_request_reference": None,
        "implementation_authorized": True,
        "implementation_performed": False,
        "implementation_reference": None,
        "created_by": _normalize_token(created_by, "created_by"),
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
        "provider_authority": False,
        "worker_authority": False,
        "aigol_autonomous_implementation": False,
        "self_improvement_authority": False,
        "governance_mutation_authority": False,
        "code_mutated": False,
        "configuration_mutated": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "self_modification_performed": False,
        "self_improvement_performed": False,
        "self_application_performed": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_plan_artifact(artifact)
    return artifact


def _plan_returned(plan: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(plan, "improvement implementation plan artifact")
    returned = {
        "event_type": IMPROVEMENT_IMPLEMENTATION_PLAN_RETURNED,
        "implementation_plan_reference": plan["implementation_plan_id"],
        "implementation_plan_hash": plan["artifact_hash"],
        "canonical_chain_id": plan["canonical_chain_id"],
        "improvement_approval_reference": plan["improvement_approval_reference"],
        "improvement_approval_hash": plan["improvement_approval_hash"],
        "improvement_proposal_reference": plan["improvement_proposal_reference"],
        "improvement_proposal_hash": plan["improvement_proposal_hash"],
        "plan_status": plan["plan_status"],
        "execution_request_created": False,
        "execution_request_reference": None,
        "implementation_authorized": True,
        "implementation_performed": False,
        "created_at": plan["created_at"],
        "replay_reference": plan["replay_reference"],
        "replay_visible": True,
        "provider_authority": False,
        "worker_authority": False,
        "aigol_autonomous_implementation": False,
        "self_improvement_authority": False,
        "governance_mutation_authority": False,
        "code_mutated": False,
        "configuration_mutated": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "worker_dispatched": False,
        "worker_invoked": False,
        "self_modification_performed": False,
        "self_improvement_performed": False,
        "self_application_performed": False,
        "reconstruction_metadata": {
            "implementation_plan_reconstructable": True,
            "approval_reconstructable": True,
            "canonical_chain_continuous": True,
            "execution_request_created": False,
            "implementation_performed": False,
        },
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(plan: dict[str, Any], returned: dict[str, Any]) -> dict[str, Any]:
    capture = {
        "improvement_implementation_plan_artifact": deepcopy(plan),
        "improvement_implementation_plan_replay": deepcopy(returned),
    }
    capture["improvement_implementation_plan_capture_hash"] = replay_hash(capture)
    return capture


def _ensure_plan_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("improvement implementation replay step ordering mismatch")
    _verify_artifact_hash(artifact, "improvement implementation plan artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
        "event_type": IMPROVEMENT_IMPLEMENTATION_PLAN_CREATED
        if index == 0
        else IMPROVEMENT_IMPLEMENTATION_PLAN_RETURNED,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _validate_approval_artifact(approval: dict[str, Any], canonical_chain_id: str) -> dict[str, Any]:
    if not isinstance(approval, dict):
        raise FailClosedRuntimeError("improvement implementation failed closed: approval artifact is required")
    _verify_artifact_hash(approval, "improvement approval artifact")
    if approval.get("artifact_type") != IMPROVEMENT_APPROVAL_ARTIFACT_V1:
        raise FailClosedRuntimeError("improvement implementation failed closed: invalid approval")
    if approval.get("canonical_chain_id") != canonical_chain_id:
        raise FailClosedRuntimeError("improvement implementation failed closed: chain mismatch")
    if approval.get("decision") != APPROVED or approval.get("approval_status") != APPROVED:
        raise FailClosedRuntimeError("improvement implementation failed closed: approval must be APPROVED")
    if approval.get("implementation_authorized") is not True:
        raise FailClosedRuntimeError("improvement implementation failed closed: implementation is not authorized")
    if approval.get("implementation_reference") is not None:
        raise FailClosedRuntimeError("improvement implementation failed closed: implementation is out of scope")
    if approval.get("decision_reason_hash") != replay_hash(approval.get("decision_reason")):
        raise FailClosedRuntimeError("improvement implementation failed closed: corrupt references")
    if approval.get("replay_visible") is not True:
        raise FailClosedRuntimeError("improvement implementation failed closed: approval replay visibility missing")
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
            raise FailClosedRuntimeError("improvement implementation failed closed: invalid approval authority")
    _require_string(approval.get("improvement_approval_id"), "improvement_approval_id")
    _require_string(approval.get("improvement_review_reference"), "improvement_review_reference")
    _require_string(approval.get("improvement_review_hash"), "improvement_review_hash")
    _require_string(approval.get("improvement_proposal_reference"), "improvement_proposal_reference")
    _require_string(approval.get("improvement_proposal_hash"), "improvement_proposal_hash")
    _require_string(approval.get("evaluation_reference"), "evaluation_reference")
    _require_string(approval.get("evaluation_hash"), "evaluation_hash")
    _require_string(approval.get("result_reference"), "result_reference")
    _require_string(approval.get("result_hash"), "result_hash")
    _require_string(approval.get("human_authorization_reference"), "human_authorization_reference")
    return deepcopy(approval)


def _validate_json_object(value: dict[str, Any], field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"improvement implementation failed closed: {field_name} must be a JSON object")
    if FORBIDDEN_PLAN_FIELDS.intersection(value):
        raise FailClosedRuntimeError("improvement implementation failed closed: authority-bearing plan content")
    for field in (
        "provider_authority",
        "worker_authority",
        "aigol_autonomous_implementation",
        "self_improvement_authority",
        "governance_mutation_authority",
        "execution_request_created",
        "implementation_performed",
        "code_mutated",
        "configuration_mutated",
        "governance_mutated",
        "replay_mutated",
        "worker_dispatched",
        "worker_invoked",
        "self_modification_performed",
        "self_improvement_performed",
    ):
        if field in value and value.get(field) is not False:
            raise FailClosedRuntimeError("improvement implementation failed closed: authority-bearing plan content")
    replay_hash(value)
    return deepcopy(value)


def _validate_string_list(value: list[str], field_name: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise FailClosedRuntimeError(f"improvement implementation failed closed: {field_name} must be a non-empty list")
    normalized = [_require_string(item, field_name) for item in value]
    replay_hash(normalized)
    return normalized


def _validate_plan_text(value: Any) -> str:
    text = _require_string(value, "plan_text")
    lowered = text.lower()
    for forbidden in (
        "modify code now",
        "write code now",
        "execute now",
        "create execution request now",
        "dispatch worker now",
        "invoke worker now",
        "mutate governance",
        "repair replay",
        "self-improve",
        "self improve",
        "apply this change now",
    ):
        if forbidden in lowered:
            raise FailClosedRuntimeError("improvement implementation failed closed: authority-bearing plan text")
    return text


def _validate_plan_artifact(plan: dict[str, Any]) -> None:
    if plan.get("artifact_type") != IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1:
        raise FailClosedRuntimeError("improvement implementation failed closed: invalid plan artifact")
    if plan.get("created_by") != "AIGOL":
        raise FailClosedRuntimeError("improvement implementation failed closed: created_by must be AIGOL")
    if plan.get("plan_status") != IMPLEMENTATION_PLAN_CREATED:
        raise FailClosedRuntimeError("improvement implementation failed closed: invalid plan status")
    if plan.get("plan_source") not in ALLOWED_PLAN_SOURCES:
        raise FailClosedRuntimeError("improvement implementation failed closed: invalid plan source")
    if plan.get("execution_request_created") is not False or plan.get("execution_request_reference") is not None:
        raise FailClosedRuntimeError("improvement implementation failed closed: execution request is out of scope")
    if plan.get("implementation_authorized") is not True:
        raise FailClosedRuntimeError("improvement implementation failed closed: implementation authorization missing")
    if plan.get("implementation_performed") is not False or plan.get("implementation_reference") is not None:
        raise FailClosedRuntimeError("improvement implementation failed closed: implementation is out of scope")
    if plan.get("plan_text_hash") != replay_hash(plan.get("plan_text")):
        raise FailClosedRuntimeError("improvement implementation failed closed: plan text hash mismatch")
    if plan.get("plan_scope_hash") != replay_hash(plan.get("plan_scope")):
        raise FailClosedRuntimeError("improvement implementation failed closed: plan scope hash mismatch")
    if plan.get("plan_constraints_hash") != replay_hash(plan.get("plan_constraints")):
        raise FailClosedRuntimeError("improvement implementation failed closed: plan constraints hash mismatch")
    if plan.get("planned_artifact_targets_hash") != replay_hash(plan.get("planned_artifact_targets")):
        raise FailClosedRuntimeError("improvement implementation failed closed: planned target hash mismatch")
    if plan.get("planned_validation_hash") != replay_hash(plan.get("planned_validation")):
        raise FailClosedRuntimeError("improvement implementation failed closed: planned validation hash mismatch")
    if plan.get("replay_visible") is not True:
        raise FailClosedRuntimeError("improvement implementation failed closed: replay visibility missing")
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
            raise FailClosedRuntimeError("improvement implementation failed closed: forbidden plan authority introduced")
    _require_string(plan.get("implementation_plan_id"), "implementation_plan_id")
    _require_string(plan.get("canonical_chain_id"), "canonical_chain_id")
    _require_string(plan.get("improvement_approval_reference"), "improvement_approval_reference")
    _require_string(plan.get("improvement_approval_hash"), "improvement_approval_hash")
    _require_string(plan.get("improvement_review_reference"), "improvement_review_reference")
    _require_string(plan.get("improvement_review_hash"), "improvement_review_hash")
    _require_string(plan.get("improvement_proposal_reference"), "improvement_proposal_reference")
    _require_string(plan.get("improvement_proposal_hash"), "improvement_proposal_hash")
    _require_string(plan.get("evaluation_reference"), "evaluation_reference")
    _require_string(plan.get("evaluation_hash"), "evaluation_hash")
    _require_string(plan.get("result_reference"), "result_reference")
    _require_string(plan.get("result_hash"), "result_hash")
    _require_string(plan.get("created_at"), "created_at")
    _require_string(plan.get("replay_reference"), "replay_reference")


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
        raise FailClosedRuntimeError("improvement implementation replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("improvement implementation replay hash mismatch")


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
