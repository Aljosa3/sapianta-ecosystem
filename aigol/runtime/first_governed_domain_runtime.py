"""First fully governed operational domain demonstration for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.domain_runtime import (
    ACTIVE,
    AIGOL_DOMAIN_RUNTIME_VERSION,
    CREATED,
    DOMAIN_ACTIVATED,
    DOMAIN_CREATED,
    DOMAIN_RETIRED,
    DOMAIN_SUSPENDED,
    DOMAIN_VALIDATED,
    RETIRED,
    SUSPENDED,
    VALIDATED,
    activate_domain,
    create_domain,
    validate_domain,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_FIRST_GOVERNED_DOMAIN_RUNTIME_VERSION = "AIGOL_FIRST_GOVERNED_DOMAIN_V1"
FIRST_GOVERNED_DOMAIN_ID = "AI_DECISION_VALIDATION"
FIRST_GOVERNED_DOMAIN_NAME = "AI Decision Validation"

FIRST_GOVERNED_DOMAIN_LIFECYCLE_ARTIFACT_V1 = "FIRST_GOVERNED_DOMAIN_LIFECYCLE_ARTIFACT_V1"
FIRST_GOVERNED_DOMAIN_EXECUTION_EXAMPLE_ARTIFACT_V1 = "FIRST_GOVERNED_DOMAIN_EXECUTION_EXAMPLE_ARTIFACT_V1"

EXECUTING = "EXECUTING"
DOMAIN_EXECUTED = "DOMAIN_EXECUTED"

REPLAY_STEPS = (
    "domain_created",
    "domain_validated",
    "domain_activated",
    "domain_executed",
    "domain_suspended",
    "domain_retired",
)

EVENTS_BY_STATE = {
    CREATED: DOMAIN_CREATED,
    VALIDATED: DOMAIN_VALIDATED,
    ACTIVE: DOMAIN_ACTIVATED,
    EXECUTING: DOMAIN_EXECUTED,
    SUSPENDED: DOMAIN_SUSPENDED,
    RETIRED: DOMAIN_RETIRED,
}

ALLOWED_TRANSITIONS = {
    CREATED: {VALIDATED},
    VALIDATED: {ACTIVE},
    ACTIVE: {EXECUTING},
    EXECUTING: {SUSPENDED},
    SUSPENDED: {RETIRED},
    RETIRED: set(),
}

DEFAULT_EXECUTION_INPUT = {
    "decision_id": "AI-DECISION-VALIDATION-EXAMPLE-000001",
    "decision_type": "ENTERPRISE_AI_ACTION_REVIEW",
    "requested_action": "approve generated recommendation for operator review",
    "risk_signals": ["requires_human_review", "external_effects_not_authorized"],
}


def run_first_governed_domain_lifecycle(
    *,
    replay_dir: str | Path,
    actor_id: str,
    timestamp: str,
    execution_input: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the certified first governed domain lifecycle demonstration."""

    replay_path = Path(replay_dir)
    _ensure_replay_available(replay_path)
    base_replay = replay_path / "certified_domain_runtime_integration"
    created = create_domain(
        domain_id=FIRST_GOVERNED_DOMAIN_ID,
        display_name=FIRST_GOVERNED_DOMAIN_NAME,
        domain_version="1.0.0",
        capabilities=[
            "AI_DECISION_INTAKE",
            "CONSTITUTIONAL_BOUNDARY_CHECK",
            "REPLAY_VISIBLE_DECISION_REVIEW",
        ],
        governance_scope="Product 1 AI Decision Validator governed operational domain",
        governance_policy_refs=[
            "docs/governance/CONSTITUTIONAL_INVARIANTS.md",
            "docs/governance/GOVERNANCE_LINEAGE_MODEL.md",
            "docs/product_lifecycle/PRODUCT_1_EXECUTION_PHASE_V1.md",
        ],
        actor_id=actor_id,
        timestamp=timestamp,
        replay_reference="FIRST-GOVERNED-DOMAIN:DOMAIN_CREATED",
        replay_dir=base_replay,
        known_gaps=["No external execution authority.", "Execution example is deterministic governance evidence."],
    )
    validated = validate_domain(
        domain_artifact=created["domain_artifact"],
        actor_id=actor_id,
        timestamp=timestamp,
        replay_reference="FIRST-GOVERNED-DOMAIN:DOMAIN_VALIDATED",
        replay_dir=base_replay,
    )
    active = activate_domain(
        domain_artifact=validated["domain_artifact"],
        actor_id=actor_id,
        timestamp=timestamp,
        replay_reference="FIRST-GOVERNED-DOMAIN:DOMAIN_ACTIVATED",
        replay_dir=base_replay,
    )

    created_stage = _stage_artifact(
        source_domain_artifact=created["domain_artifact"],
        lifecycle_state=CREATED,
        previous_artifact=None,
        actor_id=actor_id,
        timestamp=timestamp,
        replay_reference="FIRST-GOVERNED-DOMAIN:DOMAIN_CREATED",
        execution_example=None,
    )
    _persist_step(replay_path, 0, DOMAIN_CREATED, created_stage)
    validated_stage = _stage_artifact(
        source_domain_artifact=validated["domain_artifact"],
        lifecycle_state=VALIDATED,
        previous_artifact=created_stage,
        actor_id=actor_id,
        timestamp=timestamp,
        replay_reference="FIRST-GOVERNED-DOMAIN:DOMAIN_VALIDATED",
        execution_example=None,
    )
    _persist_step(replay_path, 1, DOMAIN_VALIDATED, validated_stage)
    active_stage = _stage_artifact(
        source_domain_artifact=active["domain_artifact"],
        lifecycle_state=ACTIVE,
        previous_artifact=validated_stage,
        actor_id=actor_id,
        timestamp=timestamp,
        replay_reference="FIRST-GOVERNED-DOMAIN:DOMAIN_ACTIVATED",
        execution_example=None,
    )
    _persist_step(replay_path, 2, DOMAIN_ACTIVATED, active_stage)
    execution_example = _execution_example_artifact(
        active_domain_artifact=active["domain_artifact"],
        execution_input=execution_input or DEFAULT_EXECUTION_INPUT,
        actor_id=actor_id,
        timestamp=timestamp,
    )
    executing_stage = _stage_artifact(
        source_domain_artifact=active["domain_artifact"],
        lifecycle_state=EXECUTING,
        previous_artifact=active_stage,
        actor_id=actor_id,
        timestamp=timestamp,
        replay_reference="FIRST-GOVERNED-DOMAIN:DOMAIN_EXECUTED",
        execution_example=execution_example,
    )
    _persist_step(replay_path, 3, DOMAIN_EXECUTED, executing_stage)
    suspended_stage = _stage_artifact(
        source_domain_artifact=active["domain_artifact"],
        lifecycle_state=SUSPENDED,
        previous_artifact=executing_stage,
        actor_id=actor_id,
        timestamp=timestamp,
        replay_reference="FIRST-GOVERNED-DOMAIN:DOMAIN_SUSPENDED",
        execution_example=execution_example,
    )
    _persist_step(replay_path, 4, DOMAIN_SUSPENDED, suspended_stage)
    retired_stage = _stage_artifact(
        source_domain_artifact=active["domain_artifact"],
        lifecycle_state=RETIRED,
        previous_artifact=suspended_stage,
        actor_id=actor_id,
        timestamp=timestamp,
        replay_reference="FIRST-GOVERNED-DOMAIN:DOMAIN_RETIRED",
        execution_example=execution_example,
    )
    _persist_step(replay_path, 5, DOMAIN_RETIRED, retired_stage)
    reconstructed = reconstruct_first_governed_domain_replay(replay_path)
    return {
        "first_governed_domain_artifact": deepcopy(retired_stage),
        "execution_example_artifact": deepcopy(execution_example),
        "base_domain_runtime_version": AIGOL_DOMAIN_RUNTIME_VERSION,
        "base_domain_runtime_replay": str(base_replay),
        "lifecycle_state": reconstructed["lifecycle_state"],
        "lifecycle_events": reconstructed["lifecycle_events"],
        "replay_hash": reconstructed["replay_hash"],
        "status": "CERTIFIED",
    }


def reconstruct_first_governed_domain_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct the first governed domain lifecycle replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    previous: dict[str, Any] | None = None
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("first governed domain replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("first governed domain replay artifact must be a JSON object")
        artifact = _validate_stage_artifact(artifact)
        if wrapper.get("event_type") != artifact["lifecycle_event"]:
            raise FailClosedRuntimeError("first governed domain replay event mismatch")
        _validate_continuity(previous, artifact)
        wrappers.append(wrapper)
        previous = artifact
    final_artifact = wrappers[-1]["artifact"]
    return {
        "domain_id": final_artifact["domain_id"],
        "domain_replay_id": final_artifact["domain_replay_id"],
        "lifecycle_state": final_artifact["lifecycle_state"],
        "lifecycle_events": [wrapper["event_type"] for wrapper in wrappers],
        "execution_example_hash": final_artifact["execution_example_hash"],
        "decision_result": final_artifact["execution_example"]["decision_result"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        "provider_invoked": False,
        "worker_invoked": False,
        "external_execution_performed": False,
        "governance_mutated": False,
    }


def _execution_example_artifact(
    *,
    active_domain_artifact: dict[str, Any],
    execution_input: dict[str, Any],
    actor_id: str,
    timestamp: str,
) -> dict[str, Any]:
    _validate_source_domain(active_domain_artifact, required_state=ACTIVE)
    if not isinstance(execution_input, dict):
        raise FailClosedRuntimeError("first governed domain failed closed: execution input must be a JSON object")
    decision_id = _require_string(execution_input.get("decision_id"), "decision_id")
    risk_signals = execution_input.get("risk_signals")
    if not isinstance(risk_signals, list) or not risk_signals:
        raise FailClosedRuntimeError("first governed domain failed closed: risk_signals are required")
    artifact = {
        "artifact_type": FIRST_GOVERNED_DOMAIN_EXECUTION_EXAMPLE_ARTIFACT_V1,
        "runtime_version": AIGOL_FIRST_GOVERNED_DOMAIN_RUNTIME_VERSION,
        "domain_id": active_domain_artifact["domain_id"],
        "domain_replay_id": active_domain_artifact["domain_replay_id"],
        "active_domain_hash": active_domain_artifact["artifact_hash"],
        "execution_id": f"{decision_id}:GOVERNED-EXECUTION-EXAMPLE",
        "execution_input": deepcopy(execution_input),
        "decision_result": "REQUIRES_HUMAN_REVIEW",
        "boundary_result": "EXTERNAL_EXECUTION_NOT_AUTHORIZED",
        "recorded_by": _require_string(actor_id, "actor_id"),
        "recorded_at": _require_string(timestamp, "timestamp"),
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "external_execution_performed": False,
        "dispatch_requested": False,
        "governance_mutated": False,
        "human_authority_required": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _stage_artifact(
    *,
    source_domain_artifact: dict[str, Any],
    lifecycle_state: str,
    previous_artifact: dict[str, Any] | None,
    actor_id: str,
    timestamp: str,
    replay_reference: str,
    execution_example: dict[str, Any] | None,
) -> dict[str, Any]:
    _validate_source_domain(source_domain_artifact)
    previous_state = previous_artifact["lifecycle_state"] if previous_artifact is not None else None
    previous_hash = previous_artifact["artifact_hash"] if previous_artifact is not None else None
    if previous_state is not None and lifecycle_state not in ALLOWED_TRANSITIONS[previous_state]:
        raise FailClosedRuntimeError("first governed domain failed closed: unauthorized lifecycle transition")
    event = EVENTS_BY_STATE[lifecycle_state]
    chain_input = {
        "domain_id": source_domain_artifact["domain_id"],
        "domain_replay_id": source_domain_artifact["domain_replay_id"],
        "previous_artifact_hash": previous_hash,
        "lifecycle_state": lifecycle_state,
        "lifecycle_event": event,
    }
    artifact = {
        "artifact_type": FIRST_GOVERNED_DOMAIN_LIFECYCLE_ARTIFACT_V1,
        "runtime_version": AIGOL_FIRST_GOVERNED_DOMAIN_RUNTIME_VERSION,
        "domain_runtime_version": AIGOL_DOMAIN_RUNTIME_VERSION,
        "domain_id": source_domain_artifact["domain_id"],
        "domain_replay_id": source_domain_artifact["domain_replay_id"],
        "source_domain_artifact_hash": source_domain_artifact["artifact_hash"],
        "domain_manifest": deepcopy(source_domain_artifact["domain_manifest"]),
        "domain_capability_declaration": deepcopy(source_domain_artifact["domain_capability_declaration"]),
        "domain_governance_binding": deepcopy(source_domain_artifact["domain_governance_binding"]),
        "previous_lifecycle_state": previous_state,
        "lifecycle_state": lifecycle_state,
        "lifecycle_event": event,
        "previous_artifact_hash": previous_hash,
        "chain_hash": replay_hash(chain_input),
        "actor_id": _require_string(actor_id, "actor_id"),
        "timestamp": _require_string(timestamp, "timestamp"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "execution_example": deepcopy(execution_example),
        "execution_example_hash": execution_example["artifact_hash"] if execution_example else None,
        "replay_visible": True,
        "human_authority_required": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "external_execution_performed": False,
        "dispatch_requested": False,
        "governance_mutated": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_stage_artifact(artifact)
    return artifact


def _validate_stage_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if artifact.get("artifact_type") != FIRST_GOVERNED_DOMAIN_LIFECYCLE_ARTIFACT_V1:
        raise FailClosedRuntimeError("first governed domain failed closed: invalid lifecycle artifact")
    _verify_artifact_hash(artifact, "first governed domain lifecycle artifact")
    state = artifact.get("lifecycle_state")
    if state not in EVENTS_BY_STATE:
        raise FailClosedRuntimeError("first governed domain failed closed: invalid lifecycle state")
    if artifact.get("lifecycle_event") != EVENTS_BY_STATE[state]:
        raise FailClosedRuntimeError("first governed domain failed closed: lifecycle event mismatch")
    for flag in ("provider_invoked", "worker_invoked", "external_execution_performed", "dispatch_requested", "governance_mutated"):
        if artifact.get(flag) is not False:
            raise FailClosedRuntimeError(f"first governed domain failed closed: {flag} introduced")
    if artifact.get("human_authority_required") is not True:
        raise FailClosedRuntimeError("first governed domain failed closed: human authority boundary missing")
    expected_chain = replay_hash(
        {
            "domain_id": artifact["domain_id"],
            "domain_replay_id": artifact["domain_replay_id"],
            "previous_artifact_hash": artifact.get("previous_artifact_hash"),
            "lifecycle_state": state,
            "lifecycle_event": artifact["lifecycle_event"],
        }
    )
    if artifact.get("chain_hash") != expected_chain:
        raise FailClosedRuntimeError("first governed domain failed closed: chain hash mismatch")
    if state in {EXECUTING, SUSPENDED, RETIRED}:
        execution = artifact.get("execution_example")
        _validate_execution_example(execution)
        if artifact.get("execution_example_hash") != execution["artifact_hash"]:
            raise FailClosedRuntimeError("first governed domain failed closed: execution example hash mismatch")
    return deepcopy(artifact)


def _validate_execution_example(execution: Any) -> None:
    if not isinstance(execution, dict) or execution.get("artifact_type") != FIRST_GOVERNED_DOMAIN_EXECUTION_EXAMPLE_ARTIFACT_V1:
        raise FailClosedRuntimeError("first governed domain failed closed: execution example is required")
    _verify_artifact_hash(execution, "first governed domain execution example")
    if execution.get("decision_result") != "REQUIRES_HUMAN_REVIEW":
        raise FailClosedRuntimeError("first governed domain failed closed: invalid decision result")
    for flag in ("provider_invoked", "worker_invoked", "external_execution_performed", "dispatch_requested", "governance_mutated"):
        if execution.get(flag) is not False:
            raise FailClosedRuntimeError(f"first governed domain failed closed: execution {flag} introduced")


def _validate_source_domain(source_domain_artifact: dict[str, Any], *, required_state: str | None = None) -> None:
    if not isinstance(source_domain_artifact, dict):
        raise FailClosedRuntimeError("first governed domain failed closed: source domain artifact is required")
    _verify_artifact_hash(source_domain_artifact, "source domain artifact")
    if source_domain_artifact.get("domain_id") != FIRST_GOVERNED_DOMAIN_ID:
        raise FailClosedRuntimeError("first governed domain failed closed: source domain mismatch")
    if required_state is not None and source_domain_artifact.get("lifecycle_state") != required_state:
        raise FailClosedRuntimeError("first governed domain failed closed: source domain must be active")
    if source_domain_artifact.get("replay_visible") is not True:
        raise FailClosedRuntimeError("first governed domain failed closed: source domain replay visibility missing")


def _validate_continuity(previous: dict[str, Any] | None, artifact: dict[str, Any]) -> None:
    if previous is None:
        if artifact["lifecycle_state"] != CREATED:
            raise FailClosedRuntimeError("first governed domain replay continuity mismatch")
        return
    if artifact["domain_replay_id"] != previous["domain_replay_id"]:
        raise FailClosedRuntimeError("first governed domain replay identity continuity mismatch")
    if artifact.get("previous_artifact_hash") != previous["artifact_hash"]:
        raise FailClosedRuntimeError("first governed domain replay hash continuity mismatch")
    if artifact.get("previous_lifecycle_state") != previous["lifecycle_state"]:
        raise FailClosedRuntimeError("first governed domain replay lineage continuity mismatch")
    if artifact["lifecycle_state"] not in ALLOWED_TRANSITIONS[previous["lifecycle_state"]]:
        raise FailClosedRuntimeError("first governed domain replay unauthorized transition")


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, event_type: str, artifact: dict[str, Any]) -> None:
    _verify_artifact_hash(artifact, "first governed domain lifecycle artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": REPLAY_STEPS[index],
        "artifact": deepcopy(artifact),
        "event_type": event_type,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{REPLAY_STEPS[index]}.json", wrapper)


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("first governed domain replay hash missing")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    expected = replay_hash(expected_input)
    if actual != expected:
        raise FailClosedRuntimeError("first governed domain replay hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict) or "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash missing")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    expected = replay_hash(expected_input)
    if actual != expected:
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
