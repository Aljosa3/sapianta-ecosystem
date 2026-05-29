"""First external read-only runtime inspection worker attachment."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.minimal_execution_runtime_prototype import AUTHORIZED, FAILED, TERMINATED
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.providers.metadata_inspection_provider import MetadataInspectionProvider
from aigol.runtime.read_only_capability_attachment import (
    EXECUTED,
    READ_ONLY_RUNTIME_INSPECTION,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


EXTERNAL_RUNTIME_INSPECTION_WORKER = "EXTERNAL_RUNTIME_INSPECTION_WORKER"
WORKER_TYPE = "READ_ONLY_INSPECTION_WORKER"
WORKER_VERSION = "V1"

WORKER_IDENTITY_CAPTURED = "WORKER_IDENTITY_CAPTURED"
EXECUTION_REQUEST_REFERENCED = "EXECUTION_REQUEST_REFERENCED"
EXECUTION_EVIDENCE_CAPTURED = "EXECUTION_EVIDENCE_CAPTURED"
WORKER_RESULT_CAPTURED = "WORKER_RESULT_CAPTURED"

REPLAY_STEPS = (
    "worker_identity",
    "execution_request_reference",
    "execution_evidence",
    "worker_result",
    "termination_record",
)
SUCCESS_STATES = [
    WORKER_IDENTITY_CAPTURED,
    EXECUTION_REQUEST_REFERENCED,
    EXECUTION_EVIDENCE_CAPTURED,
    WORKER_RESULT_CAPTURED,
    TERMINATED,
]

AUTHORIZATION_SCOPES = frozenset(
    {
        "READ_ONLY_EXECUTION_BRIDGE",
        "READ_ONLY_CAPABILITY_EXECUTION",
        "EXTERNAL_WORKER_READ_ONLY_INSPECTION",
    }
)
FORBIDDEN_AUTHORITY_FIELDS = (
    "write_authority",
    "delete_authority",
    "move_authority",
    "filesystem_write_authority",
    "filesystem_mutation_authority",
    "network_authority",
    "shell_authority",
    "api_authority",
    "governance_authority",
    "authorization_authority",
    "proposal_authority",
    "replay_authority",
    "orchestration_authority",
    "capability_expansion_authority",
    "worker_self_authorized",
    "cognition_self_authorized",
    "hidden_continuation",
)
FORBIDDEN_OPERATION_FIELDS = (
    "requested_operation",
    "operation",
    "intent",
    "purpose",
    "requested_authority",
)
FORBIDDEN_OPERATION_TERMS = (
    "write",
    "delete",
    "move",
    "modify",
    "mutate",
    "shell",
    "network",
    "api",
    "authorize",
    "governance",
    "replay mutation",
    "continue autonomously",
    "hidden continuation",
    "orchestrate",
)


def execute_external_runtime_inspection_worker(
    *,
    worker_attachment_id: str,
    authorized_execution_request: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
    worker_id: str = EXTERNAL_RUNTIME_INSPECTION_WORKER,
    provider: MetadataInspectionProvider | None = None,
) -> dict[str, Any]:
    """Execute one authorized request through an external read-only worker."""

    replay_path = Path(replay_dir)
    identity: dict[str, Any] | None = None
    try:
        identity = create_worker_identity(
            worker_attachment_id=worker_attachment_id,
            worker_id=worker_id,
            created_at=created_at,
        )
        _persist_step(replay_path, 0, "worker_identity", identity)
        reference = create_execution_request_reference(
            identity=identity,
            authorized_execution_request=authorized_execution_request,
        )
        _persist_step(replay_path, 1, "execution_request_reference", reference)
        evidence = execute_authorized_external_worker_request(
            reference,
            provider=provider or MetadataInspectionProvider(timestamp_provider=lambda: created_at),
        )
        _persist_step(replay_path, 2, "execution_evidence", evidence)
        result = create_worker_result(identity=identity, reference=reference, execution_evidence=evidence)
        _persist_step(replay_path, 3, "worker_result", result)
        termination = terminate_external_worker(result)
        _persist_step(replay_path, 4, "termination_record", termination)
        return _capture(identity, reference, evidence, result, termination)
    except Exception as exc:
        if identity is None:
            identity = _identity_failure_artifact(
                worker_attachment_id=worker_attachment_id,
                worker_id=worker_id,
                created_at=created_at,
                failure_reason=_failure_reason(exc),
            )
        if not (replay_path / "000_worker_identity.json").exists():
            _persist_step(replay_path, 0, "worker_identity", identity)
        failure = _failure_artifact(identity=identity, failure_reason=_failure_reason(exc))
        _persist_failure_sequence(replay_path, failure)
        return _capture(identity, None, None, None, failure)


def create_worker_identity(*, worker_attachment_id: str, worker_id: str, created_at: str) -> dict[str, Any]:
    """Create explicit external worker identity evidence."""

    normalized_worker_id = _normalize_token(worker_id, "worker_id")
    if normalized_worker_id != EXTERNAL_RUNTIME_INSPECTION_WORKER:
        raise FailClosedRuntimeError("external worker identity corruption detected")
    identity = {
        "worker_attachment_id": _require_string(worker_attachment_id, "worker_attachment_id"),
        "worker_identity": normalized_worker_id,
        "worker_type": WORKER_TYPE,
        "worker_version": WORKER_VERSION,
        "state": WORKER_IDENTITY_CAPTURED,
        "created_at": _require_string(created_at, "created_at"),
        "worker_role": "EXECUTION_PARTICIPANT_ONLY",
        "read_only": True,
        "inspection_only": True,
        "proposal_authority": False,
        "authorization_authority": False,
        "governance_authority": False,
        "replay_authority": False,
        "capability_expansion_authority": False,
        "worker_autonomy": False,
        "hidden_continuation": False,
    }
    identity["artifact_hash"] = replay_hash(identity)
    return identity


def create_execution_request_reference(
    *,
    identity: dict[str, Any],
    authorized_execution_request: dict[str, Any],
) -> dict[str, Any]:
    """Bind an AiGOL-authorized execution request to the external worker."""

    _verify_artifact_hash(identity)
    _validate_authorized_execution_request(authorized_execution_request)
    request_hash = _artifact_or_replay_hash(authorized_execution_request)
    reference = {
        "worker_attachment_id": identity["worker_attachment_id"],
        "worker_identity": identity["worker_identity"],
        "state": EXECUTION_REQUEST_REFERENCED,
        "previous_state": WORKER_IDENTITY_CAPTURED,
        "worker_identity_hash": identity["artifact_hash"],
        "execution_id": _require_string(authorized_execution_request["execution_id"], "execution_id"),
        "request_id": _require_string(authorized_execution_request["request_id"], "request_id"),
        "target_capability": _normalize_token(
            authorized_execution_request["target_capability"],
            "target_capability",
        ),
        "authorization_hash": _require_string(
            authorized_execution_request["authorization_hash"],
            "authorization_hash",
        ),
        "authorized_execution_request_hash": request_hash,
        "authorized_execution_request": deepcopy(authorized_execution_request),
        "worker_receives_authorized_request_only": True,
        "direct_provider_to_worker_path": False,
        "direct_human_to_worker_path": False,
        "replay_bypass": False,
        "read_only": True,
        "inspection_only": True,
    }
    reference["artifact_hash"] = replay_hash(reference)
    return reference


def execute_authorized_external_worker_request(
    reference: dict[str, Any],
    *,
    provider: MetadataInspectionProvider,
) -> dict[str, Any]:
    """Inspect runtime metadata only after worker boundary validation."""

    _verify_artifact_hash(reference)
    if reference.get("state") != EXECUTION_REQUEST_REFERENCED:
        raise FailClosedRuntimeError("external worker execution request reference is required")
    _validate_authorized_execution_request(reference["authorized_execution_request"])
    evidence = provider.inspect_runtime()
    _verify_provider_evidence(evidence)
    execution_evidence = {
        "worker_attachment_id": reference["worker_attachment_id"],
        "worker_identity": reference["worker_identity"],
        "execution_id": reference["execution_id"],
        "request_id": reference["request_id"],
        "target_capability": reference["target_capability"],
        "state": EXECUTION_EVIDENCE_CAPTURED,
        "previous_state": EXECUTION_REQUEST_REFERENCED,
        "execution_request_reference_hash": reference["artifact_hash"],
        "execution_evidence": deepcopy(evidence),
        "execution_evidence_hash": evidence["evidence_hash"],
        "worker_executed": True,
        "worker_result_status": EXECUTED,
        "read_only": True,
        "inspection_only": True,
        "write_performed": False,
        "delete_performed": False,
        "move_performed": False,
        "filesystem_mutation": False,
        "network_invocation": False,
        "shell_invocation": False,
        "api_invocation": False,
        "hidden_continuation": False,
    }
    execution_evidence["artifact_hash"] = replay_hash(execution_evidence)
    return execution_evidence


def create_worker_result(
    *,
    identity: dict[str, Any],
    reference: dict[str, Any],
    execution_evidence: dict[str, Any],
) -> dict[str, Any]:
    """Create governed worker result evidence from the inspection evidence."""

    _verify_artifact_hash(identity)
    _verify_artifact_hash(reference)
    _verify_artifact_hash(execution_evidence)
    if execution_evidence.get("state") != EXECUTION_EVIDENCE_CAPTURED:
        raise FailClosedRuntimeError("external worker execution evidence is required")
    if execution_evidence.get("worker_identity") != identity.get("worker_identity"):
        raise FailClosedRuntimeError("external worker identity lineage mismatch")
    if execution_evidence.get("execution_id") != reference.get("execution_id"):
        raise FailClosedRuntimeError("external worker execution lineage mismatch")
    result = {
        "worker_attachment_id": identity["worker_attachment_id"],
        "worker_identity": identity["worker_identity"],
        "execution_id": reference["execution_id"],
        "request_id": reference["request_id"],
        "target_capability": reference["target_capability"],
        "state": WORKER_RESULT_CAPTURED,
        "previous_state": EXECUTION_EVIDENCE_CAPTURED,
        "execution_evidence_hash": execution_evidence["artifact_hash"],
        "worker_result": {
            "status": EXECUTED,
            "reason": "external runtime inspection worker completed read-only inspection",
            "evidence_hash": execution_evidence["execution_evidence_hash"],
        },
        "final_worker_execution_status": EXECUTED,
        "read_only": True,
        "inspection_only": True,
        "worker_authorized_itself": False,
        "governance_authority": False,
        "replay_authority": False,
        "capability_expansion_authority": False,
        "hidden_continuation": False,
    }
    result["artifact_hash"] = replay_hash(result)
    return result


def terminate_external_worker(result: dict[str, Any]) -> dict[str, Any]:
    """Create deterministic external worker termination evidence."""

    _verify_artifact_hash(result)
    if result.get("state") != WORKER_RESULT_CAPTURED:
        raise FailClosedRuntimeError("external worker result is required for termination")
    termination = {
        "worker_attachment_id": result["worker_attachment_id"],
        "worker_identity": result["worker_identity"],
        "execution_id": result["execution_id"],
        "request_id": result["request_id"],
        "target_capability": result["target_capability"],
        "state": TERMINATED,
        "previous_state": WORKER_RESULT_CAPTURED,
        "worker_result_hash": result["artifact_hash"],
        "termination_record": {
            "final_status": TERMINATED,
            "worker_terminated": True,
            "hidden_continuation": False,
        },
        "final_status": TERMINATED,
        "replay_visible": True,
        "append_only_replay": True,
        "read_only": True,
        "inspection_only": True,
        "worker_autonomy": False,
        "hidden_continuation": False,
    }
    termination["artifact_hash"] = replay_hash(termination)
    return termination


def reconstruct_external_runtime_inspection_worker_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and validate persisted external worker replay evidence."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("external worker replay ordering mismatch")
        _verify_replay_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("external worker replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)
    states = [wrapper["artifact"]["state"] for wrapper in wrappers]
    _validate_reconstructed_states(states)
    final_artifact = wrappers[-1]["artifact"]
    identity_artifact = wrappers[0]["artifact"]
    return {
        "worker_identity": identity_artifact["worker_identity"],
        "execution_id": final_artifact["execution_id"],
        "request_id": final_artifact["request_id"],
        "target_capability": final_artifact["target_capability"],
        "final_status": final_artifact["final_status"],
        "lifecycle_transitions": states,
        "replay_artifact_count": len(wrappers),
        "append_only_valid": True,
        "replay_visible": True,
        "read_only": True,
        "inspection_only": True,
        "worker_authority": False,
        "governance_authority": False,
        "replay_hash": replay_hash(wrappers),
    }


def _validate_authorized_execution_request(request: dict[str, Any]) -> None:
    if not isinstance(request, dict):
        raise FailClosedRuntimeError("authorized execution request must be a JSON object")
    if request.get("state") != AUTHORIZED:
        raise FailClosedRuntimeError("external worker requires authorized execution request")
    if _normalize_token(request.get("target_capability"), "target_capability") != READ_ONLY_RUNTIME_INSPECTION:
        raise FailClosedRuntimeError("external worker capability mismatch")
    if _normalize_token(request.get("authorization_scope"), "authorization_scope") not in AUTHORIZATION_SCOPES:
        raise FailClosedRuntimeError("external worker authorization scope is invalid")
    _require_string(request.get("execution_id"), "execution_id")
    _require_string(request.get("request_id"), "request_id")
    _require_string(request.get("authorization_hash"), "authorization_hash")
    _ensure_no_authority_escalation(request)
    _reject_forbidden_operations(request)


def _ensure_no_authority_escalation(request: dict[str, Any]) -> None:
    for field in FORBIDDEN_AUTHORITY_FIELDS:
        if request.get(field, False) is not False:
            raise FailClosedRuntimeError("external worker boundary violation detected")


def _reject_forbidden_operations(request: dict[str, Any]) -> None:
    text_parts = []
    for field in FORBIDDEN_OPERATION_FIELDS:
        value = request.get(field)
        if isinstance(value, str):
            text_parts.append(value)
    lowered = " ".join(text_parts).lower()
    for term in FORBIDDEN_OPERATION_TERMS:
        if term in lowered:
            raise FailClosedRuntimeError("external worker boundary violation detected")


def _artifact_or_replay_hash(artifact: dict[str, Any]) -> str:
    if "artifact_hash" in artifact:
        _verify_artifact_hash(artifact)
        return artifact["artifact_hash"]
    return replay_hash(artifact)


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("external worker replay step ordering mismatch")
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


def _failure_artifact(*, identity: dict[str, Any], failure_reason: str) -> dict[str, Any]:
    artifact = {
        "worker_attachment_id": identity["worker_attachment_id"],
        "worker_identity": identity["worker_identity"],
        "execution_id": "UNAVAILABLE",
        "request_id": "UNAVAILABLE",
        "target_capability": "UNAVAILABLE",
        "state": FAILED,
        "previous_state": identity.get("state", WORKER_IDENTITY_CAPTURED),
        "worker_identity_hash": identity["artifact_hash"],
        "final_status": FAILED,
        "failure_reason": failure_reason,
        "replay_visible": True,
        "append_only_replay": True,
        "read_only": True,
        "inspection_only": True,
        "authorization_validated": False,
        "worker_authority": False,
        "boundary_violation_detected": "boundary" in failure_reason.lower() or "capability" in failure_reason.lower(),
        "identity_violation_detected": "identity" in failure_reason.lower(),
        "hidden_continuation": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _identity_failure_artifact(
    *,
    worker_attachment_id: str,
    worker_id: str,
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "worker_attachment_id": worker_attachment_id if isinstance(worker_attachment_id, str) else "UNAVAILABLE",
        "worker_identity": worker_id if isinstance(worker_id, str) and worker_id.strip() else "UNAVAILABLE",
        "worker_type": WORKER_TYPE,
        "worker_version": WORKER_VERSION,
        "state": FAILED,
        "created_at": created_at if isinstance(created_at, str) else "UNAVAILABLE",
        "failure_reason": failure_reason,
        "final_status": FAILED,
        "replay_visible": True,
        "read_only": True,
        "inspection_only": True,
        "worker_authority": False,
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
    identity: dict[str, Any],
    reference: dict[str, Any] | None,
    execution_evidence: dict[str, Any] | None,
    worker_result: dict[str, Any] | None,
    termination_record: dict[str, Any],
) -> dict[str, Any]:
    capture = {
        "worker_identity": deepcopy(identity),
        "execution_request_reference": deepcopy(reference),
        "execution_evidence": deepcopy(execution_evidence),
        "worker_result": deepcopy(worker_result),
        "termination_record": deepcopy(termination_record),
    }
    capture["external_worker_attachment_hash"] = replay_hash(capture)
    return capture


def _validate_reconstructed_states(states: list[str]) -> None:
    if states == SUCCESS_STATES:
        return
    if states[-1] == FAILED:
        try:
            first_failed_index = states.index(FAILED)
        except ValueError as exc:
            raise FailClosedRuntimeError("external worker replay final status is invalid") from exc
        if states[:first_failed_index] == SUCCESS_STATES[:first_failed_index] and all(
            state == FAILED for state in states[first_failed_index:]
        ):
            return
    raise FailClosedRuntimeError("external worker lifecycle ordering mismatch")


def _verify_provider_evidence(evidence: dict[str, Any]) -> None:
    if not isinstance(evidence, dict):
        raise FailClosedRuntimeError("external worker evidence must be a JSON object")
    if evidence.get("operation") != "inspect_runtime":
        raise FailClosedRuntimeError("external worker operation is invalid")
    indicators = evidence.get("metadata", {}).get("replay_capability_indicators", {})
    if indicators.get("read_only") is not True:
        raise FailClosedRuntimeError("external worker evidence is not read-only")
    expected_input = deepcopy(evidence)
    actual = expected_input.pop("evidence_hash", None)
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("external worker evidence hash mismatch")


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("external worker artifact must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("external worker artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("external worker artifact hash mismatch")


def _verify_replay_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("external worker replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("external worker replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "external worker failed closed"


def _normalize_token(value: Any, field_name: str) -> str:
    return _require_string(value, field_name).strip().upper().replace("-", "_")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value
