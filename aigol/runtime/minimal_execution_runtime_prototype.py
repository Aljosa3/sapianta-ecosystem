"""Minimal replay-visible execution runtime prototype for AiGOL."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


REQUESTED = "REQUESTED"
VALIDATED = "VALIDATED"
AUTHORIZED = "AUTHORIZED"
EXECUTED = "EXECUTED"
FAILED = "FAILED"
TERMINATED = "TERMINATED"

PROTOTYPE_SURFACE = "PROTOTYPE"
NOOP_CAPABILITY = "NOOP"
BOUNDED_EXECUTION_PARTICIPATION = "BOUNDED_EXECUTION_PARTICIPATION"

REPLAY_STEPS = ("request", "validation", "authorization", "outcome", "termination")
SUCCESS_TRANSITIONS = (
    (REQUESTED, VALIDATED),
    (VALIDATED, AUTHORIZED),
    (AUTHORIZED, EXECUTED),
    (EXECUTED, TERMINATED),
)
TERMINAL_STATES = {FAILED, TERMINATED}
REAL_SURFACES = {"FILESYSTEM", "NETWORK", "CLI", "API"}
DENIED_CAPABILITIES = {
    ("FILESYSTEM", "WRITE"),
    ("FILESYSTEM", "MOVE"),
    ("FILESYSTEM", "DELETE"),
    ("NETWORK", "INBOUND"),
    ("CLI", "MUTATING"),
    ("CLI", "PRIVILEGED"),
    ("API", "CREATE"),
    ("API", "UPDATE"),
    ("API", "DELETE"),
}
RESTRICTED_CAPABILITIES = {
    ("FILESYSTEM", "READ"),
    ("NETWORK", "OUTBOUND"),
    ("CLI", "READ_ONLY"),
    ("API", "QUERY"),
}
AUTHORITY_ESCALATION_TERMS = (
    "governance authority",
    "constitutional mutation",
    "orchestration runtime",
    "agent runtime",
    "worker dispatch",
    "filesystem execution",
    "network execution",
    "shell execution",
    "api execution",
    "continue autonomously",
    "hidden continuation",
)


def create_execution_request(
    *,
    execution_id: str,
    request_id: str,
    requested_surface: str = PROTOTYPE_SURFACE,
    requested_capability: str = NOOP_CAPABILITY,
    requested_authority: str = BOUNDED_EXECUTION_PARTICIPATION,
    created_at: str,
    lineage_parent: str | None = None,
    purpose: str = "bounded replay-visible prototype execution",
) -> dict[str, Any]:
    """Create deterministic execution request evidence."""

    if lineage_parent is not None:
        _require_string(lineage_parent, "lineage_parent")
    request = {
        "execution_id": _require_string(execution_id, "execution_id"),
        "request_id": _require_string(request_id, "request_id"),
        "state": REQUESTED,
        "requested_surface": _normalize_token(requested_surface, "requested_surface"),
        "requested_capability": _normalize_token(requested_capability, "requested_capability"),
        "requested_authority": _require_string(requested_authority, "requested_authority"),
        "created_at": _require_string(created_at, "created_at"),
        "lineage_parent": lineage_parent,
        "purpose": _normalize_text(purpose, "purpose"),
        "filesystem_execution": False,
        "network_execution": False,
        "cli_execution": False,
        "api_execution": False,
        "hidden_state_created": False,
    }
    request["artifact_hash"] = replay_hash(request)
    return request


def validate_execution_request(request: dict[str, Any]) -> dict[str, Any]:
    """Validate bounded request scope and execution boundary compatibility."""

    _verify_artifact_hash(request)
    if request.get("state") != REQUESTED:
        raise FailClosedRuntimeError("execution request must be REQUESTED")
    surface = _normalize_token(request.get("requested_surface"), "requested_surface")
    capability = _normalize_token(request.get("requested_capability"), "requested_capability")
    _reject_authority_escalation(" ".join([request["requested_authority"], request["purpose"]]))
    _ensure_no_real_execution_flags(request)
    if (surface, capability) in DENIED_CAPABILITIES:
        raise FailClosedRuntimeError("execution boundary violation detected")
    if (surface, capability) in RESTRICTED_CAPABILITIES:
        raise FailClosedRuntimeError("execution capability is restricted and not enabled")
    if surface in REAL_SURFACES:
        raise FailClosedRuntimeError("execution surface is not enabled")
    if (surface, capability) != (PROTOTYPE_SURFACE, NOOP_CAPABILITY):
        raise FailClosedRuntimeError("execution classification ambiguity detected")
    validation = {
        "execution_id": request["execution_id"],
        "request_id": request["request_id"],
        "state": VALIDATED,
        "previous_state": REQUESTED,
        "request_hash": request["artifact_hash"],
        "requested_surface": surface,
        "requested_capability": capability,
        "boundary_classification": "ALLOWED",
        "replay_centrality_preserved": True,
        "constitutional_freeze_preserved": True,
        "authority_separation_preserved": True,
        "execution_boundaries_preserved": True,
        "hidden_continuation_detected": False,
        "authority_escalation_detected": False,
    }
    validation["artifact_hash"] = replay_hash(validation)
    return validation


def authorize_execution(validation: dict[str, Any], *, authorized: bool = True) -> dict[str, Any]:
    """Create explicit bounded authorization result."""

    _verify_artifact_hash(validation)
    if validation.get("state") != VALIDATED:
        raise FailClosedRuntimeError("execution authorization requires VALIDATED state")
    if authorized is not True:
        raise FailClosedRuntimeError("execution authorization missing")
    authorization = {
        "execution_id": validation["execution_id"],
        "request_id": validation["request_id"],
        "state": AUTHORIZED,
        "previous_state": VALIDATED,
        "validation_hash": validation["artifact_hash"],
        "authorization_scope": BOUNDED_EXECUTION_PARTICIPATION,
        "governance_authority": False,
        "orchestration_authority": False,
        "filesystem_authority": False,
        "network_authority": False,
        "autonomous_authority": False,
    }
    authorization["artifact_hash"] = replay_hash(authorization)
    return authorization


def create_execution_outcome(authorization: dict[str, Any]) -> dict[str, Any]:
    """Create a bounded no-op execution outcome without touching real surfaces."""

    _verify_artifact_hash(authorization)
    if authorization.get("state") != AUTHORIZED:
        raise FailClosedRuntimeError("execution outcome requires AUTHORIZED state")
    _ensure_authorization_has_no_escalation(authorization)
    outcome = {
        "execution_id": authorization["execution_id"],
        "request_id": authorization["request_id"],
        "state": EXECUTED,
        "previous_state": AUTHORIZED,
        "authorization_hash": authorization["artifact_hash"],
        "outcome_type": "BOUNDED_NOOP",
        "filesystem_actions_executed": False,
        "network_actions_executed": False,
        "cli_commands_executed": False,
        "api_calls_executed": False,
        "hidden_state_created": False,
        "constitutional_baseline_mutated": False,
    }
    outcome["artifact_hash"] = replay_hash(outcome)
    return outcome


def terminate_execution(outcome: dict[str, Any]) -> dict[str, Any]:
    """Create deterministic terminal execution state."""

    _verify_artifact_hash(outcome)
    if outcome.get("state") != EXECUTED:
        raise FailClosedRuntimeError("execution termination requires EXECUTED state")
    termination = {
        "execution_id": outcome["execution_id"],
        "request_id": outcome["request_id"],
        "state": TERMINATED,
        "previous_state": EXECUTED,
        "outcome_hash": outcome["artifact_hash"],
        "final_status": TERMINATED,
        "replay_visible": True,
        "bounded_execution": True,
        "hidden_continuation": False,
    }
    termination["artifact_hash"] = replay_hash(termination)
    return termination


def execute_minimal_execution_runtime(
    *,
    execution_id: str,
    request_id: str,
    created_at: str,
    replay_dir: str | Path,
    requested_surface: str = PROTOTYPE_SURFACE,
    requested_capability: str = NOOP_CAPABILITY,
    requested_authority: str = BOUNDED_EXECUTION_PARTICIPATION,
    lineage_parent: str | None = None,
    purpose: str = "bounded replay-visible prototype execution",
    authorize: bool = True,
) -> dict[str, Any]:
    """Run one bounded replay-visible execution prototype instance."""

    replay_path = Path(replay_dir)
    request = create_execution_request(
        execution_id=execution_id,
        request_id=request_id,
        requested_surface=requested_surface,
        requested_capability=requested_capability,
        requested_authority=requested_authority,
        created_at=created_at,
        lineage_parent=lineage_parent,
        purpose=purpose,
    )
    _persist_step(replay_path, 0, "request", request)
    try:
        validation = validate_execution_request(request)
        _persist_step(replay_path, 1, "validation", validation)
        authorization = authorize_execution(validation, authorized=authorize)
        _persist_step(replay_path, 2, "authorization", authorization)
        outcome = create_execution_outcome(authorization)
        _persist_step(replay_path, 3, "outcome", outcome)
        termination = terminate_execution(outcome)
        _persist_step(replay_path, 4, "termination", termination)
        return _capture(request, validation, authorization, outcome, termination)
    except Exception as exc:
        failure = _failure_artifact(request=request, failure_reason=_failure_reason(exc))
        _persist_failure_sequence(replay_path, failure)
        return _capture(request, None, None, None, failure)


def validate_execution_transition(previous_state: str, next_state: str) -> None:
    """Validate deterministic lifecycle transition semantics."""

    if previous_state in TERMINAL_STATES:
        raise FailClosedRuntimeError("execution lifecycle terminal state cannot transition")
    if next_state == FAILED:
        return
    if (previous_state, next_state) not in SUCCESS_TRANSITIONS:
        raise FailClosedRuntimeError("invalid execution lifecycle transition")


def reconstruct_minimal_execution_runtime_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate persisted execution runtime replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("minimal execution runtime replay ordering mismatch")
        _verify_replay_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("minimal execution runtime replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    states = [wrapper["artifact"]["state"] for wrapper in wrappers]
    _validate_reconstructed_states(states)
    final_artifact = wrappers[-1]["artifact"]
    return {
        "execution_id": final_artifact["execution_id"],
        "final_status": final_artifact["final_status"],
        "lifecycle_transitions": states,
        "replay_artifact_count": len(wrappers),
        "append_only_valid": True,
        "replay_visible": True,
        "lineage_valid": True,
        "constitutional_freeze_preserved": True,
        "authority_separation_preserved": True,
        "execution_boundaries_preserved": True,
        "replay_hash": replay_hash(wrappers),
    }


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("minimal execution runtime replay step ordering mismatch")
    _verify_artifact_hash(artifact)
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_sequence(replay_dir: Path, failure: dict[str, Any]) -> None:
    for index, step in enumerate(REPLAY_STEPS[1:], start=1):
        path = replay_dir / f"{index:03d}_{step}.json"
        if not path.exists():
            _persist_step(replay_dir, index, step, _failure_step(failure, step))


def _failure_artifact(*, request: dict[str, Any], failure_reason: str) -> dict[str, Any]:
    artifact = {
        "execution_id": request["execution_id"],
        "request_id": request["request_id"],
        "state": FAILED,
        "previous_state": request.get("state", REQUESTED),
        "request_hash": request["artifact_hash"],
        "final_status": FAILED,
        "failure_reason": failure_reason,
        "replay_visible": True,
        "bounded_execution": True,
        "continuity_validated": False,
        "authority_escalation_detected": _is_authority_failure(failure_reason),
        "boundary_violation_detected": "boundary" in failure_reason.lower(),
        "hidden_continuation": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failure_step(failure: dict[str, Any], step: str) -> dict[str, Any]:
    artifact = deepcopy(failure)
    artifact["failed_step"] = step
    artifact.pop("artifact_hash", None)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    request: dict[str, Any],
    validation: dict[str, Any] | None,
    authorization: dict[str, Any] | None,
    outcome: dict[str, Any] | None,
    termination: dict[str, Any],
) -> dict[str, Any]:
    capture = {
        "request": deepcopy(request),
        "validation": deepcopy(validation),
        "authorization": deepcopy(authorization),
        "outcome": deepcopy(outcome),
        "termination": deepcopy(termination),
    }
    capture["runtime_hash"] = replay_hash(capture)
    return capture


def _validate_reconstructed_states(states: list[str]) -> None:
    if len(states) != len(REPLAY_STEPS):
        raise FailClosedRuntimeError("minimal execution runtime replay chain incomplete")
    if states[-1] == TERMINATED:
        if states != [REQUESTED, VALIDATED, AUTHORIZED, EXECUTED, TERMINATED]:
            raise FailClosedRuntimeError("minimal execution runtime lifecycle ordering mismatch")
        return
    if states[-1] == FAILED:
        try:
            first_failed_index = states.index(FAILED)
        except ValueError as exc:
            raise FailClosedRuntimeError("minimal execution runtime final status is invalid") from exc
        success_prefix = [REQUESTED, VALIDATED, AUTHORIZED, EXECUTED]
        if states[:first_failed_index] == success_prefix[:first_failed_index] and all(
            state == FAILED for state in states[first_failed_index:]
        ):
            return
    raise FailClosedRuntimeError("minimal execution runtime final status is invalid")


def _ensure_authorization_has_no_escalation(authorization: dict[str, Any]) -> None:
    for field in (
        "governance_authority",
        "orchestration_authority",
        "filesystem_authority",
        "network_authority",
        "autonomous_authority",
    ):
        if authorization.get(field) is not False:
            raise FailClosedRuntimeError("execution authority escalation attempt detected")


def _ensure_no_real_execution_flags(request: dict[str, Any]) -> None:
    for field in (
        "filesystem_execution",
        "network_execution",
        "cli_execution",
        "api_execution",
        "hidden_state_created",
    ):
        if request.get(field) is not False:
            raise FailClosedRuntimeError("execution boundary violation detected")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("minimal execution runtime artifact must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("minimal execution runtime artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("minimal execution runtime artifact hash mismatch")


def _verify_replay_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("minimal execution runtime replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("minimal execution runtime replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "minimal execution runtime failed closed"


def _is_authority_failure(failure_reason: str) -> bool:
    lowered = failure_reason.lower()
    return "authority" in lowered or "escalation" in lowered or "autonomous" in lowered


def _reject_authority_escalation(text: str) -> None:
    lowered = text.lower()
    for term in AUTHORITY_ESCALATION_TERMS:
        if term in lowered:
            raise FailClosedRuntimeError("execution authority escalation attempt detected")


def _normalize_text(value: Any, field_name: str) -> str:
    raw = _require_string(value, field_name)
    normalized = " ".join(raw.split())
    if not normalized:
        raise FailClosedRuntimeError(f"{field_name} is required")
    return normalized


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
