"""Replay-visible Worker result validation runtime for the current AiGOL chain."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.execution_runtime import EXECUTING
from aigol.runtime.worker_invocation_runtime import (
    _domain_execution_ready_bridge_index,
    _matching_bridge_for_dispatch,
    _resolve_replay_reference,
)
from aigol.runtime.worker_result_capture_runtime import (
    WORKER_RESULT_CAPTURED,
    WORKER_RESULT_CAPTURE_ARTIFACT_V1,
    reconstruct_worker_result_capture_replay,
)


AIGOL_WORKER_RESULT_VALIDATION_RUNTIME_VERSION = "AIGOL_WORKER_RESULT_VALIDATION_RUNTIME_V1"
WORKER_RESULT_VALIDATION_EVIDENCE_ARTIFACT_V1 = "WORKER_RESULT_VALIDATION_EVIDENCE_ARTIFACT_V1"
WORKER_RESULT_VALIDATION_CLASSIFICATION_ARTIFACT_V1 = "WORKER_RESULT_VALIDATION_CLASSIFICATION_ARTIFACT_V1"
WORKER_RESULT_VALIDATION_ARTIFACT_V1 = "WORKER_RESULT_VALIDATION_ARTIFACT_V1"
WORKER_RESULT_VALIDATION_RESULT_ARTIFACT_V1 = "WORKER_RESULT_VALIDATION_RESULT_ARTIFACT_V1"
RESULT_VALIDATED = "RESULT_VALIDATED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "validation_evidence_recorded",
    "validation_classification_recorded",
    "validation_artifact_recorded",
    "validation_result_recorded",
)


def detect_domain_worker_result_validation_entry_intent(human_prompt: str) -> dict[str, Any]:
    """Detect narrow operator prompts for Worker result validation."""

    prompt = _require_string(human_prompt, "human_prompt")
    normalized = " ".join(prompt.strip().rstrip(".?!").split())
    lowered = normalized.lower()
    patterns = (
        r"^validate\s+worker\s+result\s+for\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)$",
        r"^validate\s+result\s+for\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)$",
        r"^continue\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)\s+to\s+result\s+validation$",
        r"^create\s+worker\s+result\s+validation\s+for\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)$",
    )
    for pattern in patterns:
        match = re.match(pattern, normalized, flags=re.IGNORECASE)
        if match:
            if lowered.startswith("continue"):
                action = "CONTINUE_TO_WORKER_RESULT_VALIDATION"
            elif lowered.startswith("create"):
                action = "CREATE_WORKER_RESULT_VALIDATION"
            else:
                action = "VALIDATE_WORKER_RESULT"
            return {
                "worker_result_validation_entry_intent_detected": True,
                "domain_name": match.group("domain"),
                "worker_result_validation_action": action,
                "matched_prompt": normalized,
            }
    return {
        "worker_result_validation_entry_intent_detected": False,
        "domain_name": None,
        "worker_result_validation_action": None,
        "matched_prompt": normalized,
    }


def find_latest_domain_result_capture_for_validation(
    *,
    session_root: str | Path,
    domain_name: str,
) -> dict[str, Any]:
    """Find the latest captured Worker result for a domain without validation."""

    root = Path(session_root)
    domain = _require_string(domain_name, "domain_name")
    if not root.exists():
        raise FailClosedRuntimeError("worker result validation failed closed: session root missing")
    bridge_index = _domain_execution_ready_bridge_index(root, domain)
    candidates: list[dict[str, Any]] = []
    for path in sorted(root.glob("TURN-*/worker_result_capture")):
        try:
            reconstructed = reconstruct_worker_result_capture_replay(path)
            evidence_wrapper = load_json(path / "000_result_capture_evidence_recorded.json")
            capture_wrapper = load_json(path / "002_result_capture_artifact_recorded.json")
            _verify_wrapper_hash(evidence_wrapper)
            _verify_wrapper_hash(capture_wrapper)
            evidence = evidence_wrapper.get("artifact")
            capture = capture_wrapper.get("artifact")
            if not isinstance(evidence, dict) or not isinstance(capture, dict):
                continue
            _verify_artifact_hash(evidence, "worker result capture evidence")
            _verify_artifact_hash(capture, "worker result capture artifact")
            invocation_path = _resolve_replay_reference(
                evidence.get("worker_invocation_replay_reference"),
                anchor=path,
            )
            invocation_evidence_wrapper = load_json(invocation_path / "000_invocation_evidence_recorded.json")
            _verify_wrapper_hash(invocation_evidence_wrapper)
            invocation_evidence = invocation_evidence_wrapper.get("artifact")
            if not isinstance(invocation_evidence, dict):
                continue
            dispatch_path = _resolve_replay_reference(
                invocation_evidence.get("worker_dispatch_replay_reference"),
                anchor=invocation_path,
            )
            dispatch_wrapper = load_json(dispatch_path / "002_dispatch_artifact_recorded.json")
            _verify_wrapper_hash(dispatch_wrapper)
            dispatch = dispatch_wrapper.get("artifact")
            if not isinstance(dispatch, dict):
                continue
            _verify_artifact_hash(dispatch, "worker dispatch artifact")
        except FailClosedRuntimeError:
            continue
        if reconstructed.get("result_capture_status") != WORKER_RESULT_CAPTURED:
            continue
        bridge = _matching_bridge_for_dispatch(dispatch_path, dispatch, bridge_index)
        if bridge is None:
            continue
        if _result_capture_already_validated(
            root,
            result_capture_reference=str(capture.get("worker_result_capture_id") or ""),
            result_capture_hash=str(capture.get("artifact_hash") or ""),
        ):
            continue
        candidates.append(
            {
                "worker_result_capture_replay_reference": str(path),
                "worker_result_capture_artifact": deepcopy(capture),
                "domain_name": bridge["approved_domain"],
                "worker_result_capture_reference": capture["worker_result_capture_id"],
                "worker_result_capture_hash": capture["artifact_hash"],
                "chain_id": capture["chain_id"],
                "turn_id": path.parent.name,
            }
        )
    if not candidates:
        raise FailClosedRuntimeError("worker result validation failed closed: matching result capture not found")
    return candidates[-1]


def validate_worker_result(
    *,
    worker_result_validation_id: str,
    worker_result_capture_artifact: dict[str, Any],
    worker_result_capture_replay_reference: str,
    validated_by: str,
    validated_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Validate a captured Worker result without approval, replay review, or termination."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        lineage = _load_result_capture_lineage(
            Path(worker_result_capture_replay_reference),
            worker_result_capture_artifact,
        )
        result_capture = lineage["result_capture"]
        evidence = _evidence_artifact(
            worker_result_validation_id=worker_result_validation_id,
            result_capture=result_capture,
            lineage=lineage,
            worker_result_capture_replay_reference=worker_result_capture_replay_reference,
            validated_at=validated_at,
        )
        classification = _classification_artifact(
            worker_result_validation_id=worker_result_validation_id,
            evidence=evidence,
            result_capture=result_capture,
            validated_at=validated_at,
        )
        validation = _validation_artifact(
            worker_result_validation_id=worker_result_validation_id,
            evidence=evidence,
            classification=classification,
            result_capture=result_capture,
            validated_by=validated_by,
            validated_at=validated_at,
        )
        result = _result_artifact(
            worker_result_validation_id=worker_result_validation_id,
            evidence=evidence,
            classification=classification,
            validation=validation,
            validated_at=validated_at,
            status=RESULT_VALIDATED,
            failure_reason=None,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], evidence)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], classification)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], validation)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], result)
        return _capture(evidence, classification, validation, result, replay_path)
    except Exception as exc:
        result = _failed_result(
            worker_result_validation_id=worker_result_validation_id,
            worker_result_capture_reference=(
                worker_result_capture_artifact.get("worker_result_capture_id")
                if isinstance(worker_result_capture_artifact, dict)
                else None
            ),
            worker_result_capture_replay_reference=worker_result_capture_replay_reference,
            validated_at=validated_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], result)
        return _capture(None, None, None, result, replay_path)


def reconstruct_worker_result_validation_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Worker result validation replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("worker result validation replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("worker result validation replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "worker result validation replay artifact")
        wrappers.append(wrapper)

    evidence = wrappers[0]["artifact"]
    classification = wrappers[1]["artifact"]
    validation = wrappers[2]["artifact"]
    result = wrappers[3]["artifact"]
    if classification.get("validation_evidence_hash") != evidence["artifact_hash"]:
        raise FailClosedRuntimeError("worker result validation replay evidence lineage mismatch")
    if validation.get("validation_classification_hash") != classification["artifact_hash"]:
        raise FailClosedRuntimeError("worker result validation replay classification lineage mismatch")
    if result.get("worker_result_validation_hash") != validation["artifact_hash"]:
        raise FailClosedRuntimeError("worker result validation replay continuity mismatch")
    if len({evidence["chain_id"], classification["chain_id"], validation["chain_id"], result["chain_id"]}) != 1:
        raise FailClosedRuntimeError("worker result validation replay chain mismatch")
    if evidence["worker_result_capture_hash"] != validation["worker_result_capture_hash"]:
        raise FailClosedRuntimeError("worker result validation replay result capture lineage mismatch")
    _validate_validation_artifact(validation)
    _load_result_capture_lineage(
        Path(evidence["worker_result_capture_replay_reference"]),
        None,
        validation=validation,
    )
    return {
        "worker_result_validation_id": validation["worker_result_validation_id"],
        "validation_status": result["validation_status"],
        "worker_result_capture_reference": validation["worker_result_capture_reference"],
        "execution_reference": validation.get("execution_reference"),
        "execution_hash": validation.get("execution_hash"),
        "execution_replay_reference": validation.get("execution_replay_reference"),
        "worker_invocation_reference": validation["worker_invocation_reference"],
        "worker_dispatch_reference": validation["worker_dispatch_reference"],
        "authorization_reference": validation["authorization_reference"],
        "execution_packet_reference": validation["execution_packet_reference"],
        "worker_id": validation["worker_id"],
        "worker_family": validation["worker_family"],
        "worker_role": validation["worker_role"],
        "chain_id": validation["chain_id"],
        "validation_requirements": deepcopy(validation["validation_requirements"]),
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        **_post_validation_boundary_flags(execution_bound=bool(validation.get("execution_reference"))),
        "failure_reason": result["failure_reason"],
    }


def render_worker_result_validation_summary(capture: dict[str, Any]) -> str:
    lines = [
        "",
        "Worker Result Validation",
        "",
        f"Validation Status: {capture.get('validation_status')}",
        f"Worker Result Validation Reference: {capture.get('worker_result_validation_reference')}",
        f"Worker Result Capture Reference: {capture.get('worker_result_capture_reference')}",
        f"Validated Worker: {capture.get('worker_id')}",
        f"Replay Reference: {capture.get('worker_result_validation_replay_reference')}",
        "",
        "No replay review yet.",
        "No termination yet.",
    ]
    if capture.get("failure_reason"):
        lines.append(f"failure_reason: {capture['failure_reason']}")
    return "\n".join(lines)


def _load_result_capture_lineage(
    result_capture_replay_path: Path,
    provided_result_capture: dict[str, Any] | None,
    *,
    validation: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    reconstructed = reconstruct_worker_result_capture_replay(result_capture_replay_path)
    if reconstructed.get("result_capture_status") != WORKER_RESULT_CAPTURED:
        raise FailClosedRuntimeError("worker result validation failed closed: result capture invalid")
    wrappers = []
    expected = (
        (0, "result_capture_evidence_recorded"),
        (1, "result_capture_classification_recorded"),
        (2, "result_capture_artifact_recorded"),
        (3, "result_capture_result_recorded"),
    )
    for index, step in expected:
        wrapper = load_json(result_capture_replay_path / f"{index:03d}_{step}.json")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("worker result validation failed closed: result capture replay corruption")
        _verify_artifact_hash(artifact, "worker result capture lineage artifact")
        wrappers.append(wrapper)
    evidence = wrappers[0]["artifact"]
    classification = wrappers[1]["artifact"]
    result_capture = wrappers[2]["artifact"]
    result = wrappers[3]["artifact"]
    _validate_result_capture_artifact(result_capture)
    if provided_result_capture is not None:
        _verify_artifact_hash(provided_result_capture, "provided worker result capture artifact")
        if provided_result_capture.get("worker_result_capture_id") != result_capture["worker_result_capture_id"]:
            raise FailClosedRuntimeError("worker result validation failed closed: result capture mismatch")
        if provided_result_capture.get("artifact_hash") != result_capture["artifact_hash"]:
            raise FailClosedRuntimeError("worker result validation failed closed: result capture mismatch")
    if validation is not None:
        if validation.get("worker_result_capture_reference") != result_capture["worker_result_capture_id"]:
            raise FailClosedRuntimeError("worker result validation failed closed: result capture mismatch")
        if validation.get("worker_result_capture_hash") != result_capture["artifact_hash"]:
            raise FailClosedRuntimeError("worker result validation failed closed: result capture mismatch")
    checks = {
        "result_capture_lineage": result["worker_result_capture_hash"] == result_capture["artifact_hash"],
        "invocation_lineage": result_capture["worker_invocation_hash"] == evidence["worker_invocation_hash"],
        "dispatch_lineage": result_capture["worker_dispatch_hash"] == evidence["worker_dispatch_hash"],
        "assignment_lineage": result_capture["worker_assignment_hash"] == evidence["worker_assignment_hash"],
        "authorization_lineage": result_capture["authorization_hash"] == evidence["authorization_hash"],
        "execution_packet_lineage": result_capture["execution_packet_hash"] == evidence["execution_packet_hash"],
        "execution_binding_lineage": _result_capture_execution_binding_continuity(
            result_capture,
            evidence,
            classification,
            result,
        ),
        "worker_identity_continuity": result_capture["worker_id"] == evidence["worker_id"]
        and result_capture["worker_hash"] == evidence["worker_hash"],
        "chain_continuity": result_capture["chain_id"] == evidence["chain_id"],
        "replay_continuity": reconstructed["result_capture_status"] == WORKER_RESULT_CAPTURED,
        "authority_continuity": _result_capture_authority_continuity(result_capture),
    }
    if not all(checks.values()):
        raise FailClosedRuntimeError("worker result validation failed closed: lineage continuity invalid")
    return {
        "result_capture_evidence": evidence,
        "result_capture_classification": classification,
        "result_capture": result_capture,
        "result_capture_result": result,
        "lineage_checks": checks,
    }


def _validate_result_capture_artifact(result_capture: dict[str, Any]) -> None:
    if result_capture.get("artifact_type") != WORKER_RESULT_CAPTURE_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker result validation failed closed: invalid result capture artifact")
    if result_capture.get("result_capture_status") != WORKER_RESULT_CAPTURED:
        raise FailClosedRuntimeError("worker result validation failed closed: result capture invalid")
    execution_bound = _result_capture_execution_bound(result_capture)
    for field, expected in _pre_validation_boundary_flags(execution_bound=execution_bound).items():
        if result_capture.get(field) is not expected:
            raise FailClosedRuntimeError("worker result validation failed closed: authority violation")
    if not _string_list(result_capture.get("allowed_outputs")):
        raise FailClosedRuntimeError("worker result validation failed closed: allowed outputs missing")
    if not _string_list(result_capture.get("produced_outputs")):
        raise FailClosedRuntimeError("worker result validation failed closed: result outside allowed outputs")
    if not set(result_capture["produced_outputs"]).issubset(set(result_capture["allowed_outputs"])):
        raise FailClosedRuntimeError("worker result validation failed closed: result outside allowed outputs")
    if not _string_list(result_capture.get("forbidden_operations")):
        raise FailClosedRuntimeError("worker result validation failed closed: forbidden operations missing")
    if set(result_capture.get("operations", [])).intersection(result_capture["forbidden_operations"]):
        raise FailClosedRuntimeError("worker result validation failed closed: forbidden operation detected")
    validation_requirements = result_capture.get("validation_requirements")
    if not _string_list(validation_requirements):
        raise FailClosedRuntimeError("worker result validation failed closed: validation requirement missing")
    for field in (
        "worker_result_capture_id",
        "worker_invocation_reference",
        "worker_invocation_hash",
        "worker_dispatch_reference",
        "worker_dispatch_hash",
        "worker_assignment_reference",
        "worker_assignment_hash",
        "authorization_reference",
        "authorization_hash",
        "execution_packet_reference",
        "execution_packet_hash",
        "worker_id",
        "worker_hash",
        "worker_family",
        "worker_role",
        "chain_id",
        "worker_output_reference",
        "worker_output_hash",
    ):
        _require_string(result_capture.get(field), field)
    if execution_bound:
        for field in (
            "execution_reference",
            "execution_hash",
            "execution_replay_hash",
            "execution_status",
        ):
            _require_string(result_capture.get(field), field)
        if result_capture.get("execution_status") != EXECUTING:
            raise FailClosedRuntimeError("worker result validation failed closed: invalid execution state")


def _result_capture_execution_binding_continuity(
    result_capture: dict[str, Any],
    evidence: dict[str, Any],
    classification: dict[str, Any],
    result: dict[str, Any],
) -> bool:
    execution_bound = _result_capture_execution_bound(result_capture)
    if not execution_bound:
        return (
            not _has_execution_binding(evidence)
            and not _has_execution_binding(classification)
            and not _has_execution_binding(result)
        )
    required = ("execution_reference", "execution_hash", "execution_replay_hash", "execution_status")
    if any(not isinstance(result_capture.get(field), str) or not result_capture[field].strip() for field in required):
        return False
    if result_capture.get("execution_status") != EXECUTING:
        return False
    if result_capture.get("execution_started") is not True:
        return False
    if evidence.get("execution_reference") != result_capture["execution_reference"]:
        return False
    if evidence.get("execution_hash") != result_capture["execution_hash"]:
        return False
    if evidence.get("execution_replay_hash") != result_capture["execution_replay_hash"]:
        return False
    if evidence.get("execution_replay_reference") != result_capture.get("execution_replay_reference"):
        return False
    if evidence.get("execution_status") != result_capture["execution_status"]:
        return False
    if classification.get("execution_reference") != result_capture["execution_reference"]:
        return False
    if classification.get("execution_hash") != result_capture["execution_hash"]:
        return False
    if classification.get("execution_bound") is not True:
        return False
    if classification.get("execution_lineage_continuous") is not True:
        return False
    if result.get("execution_reference") != result_capture["execution_reference"]:
        return False
    if result.get("execution_hash") != result_capture["execution_hash"]:
        return False
    if result.get("execution_replay_reference") != result_capture.get("execution_replay_reference"):
        return False
    execution_checks = evidence.get("execution_lineage_checks")
    return isinstance(execution_checks, dict) and bool(execution_checks) and all(execution_checks.values())


def _evidence_artifact(
    *,
    worker_result_validation_id: str,
    result_capture: dict[str, Any],
    lineage: dict[str, dict[str, Any]],
    worker_result_capture_replay_reference: str,
    validated_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_RESULT_VALIDATION_EVIDENCE_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_RESULT_VALIDATION_RUNTIME_VERSION,
        "validation_evidence_id": f"{_require_string(worker_result_validation_id, 'worker_result_validation_id')}:EVIDENCE",
        "chain_id": result_capture["chain_id"],
        "worker_result_capture_reference": result_capture["worker_result_capture_id"],
        "worker_result_capture_hash": result_capture["artifact_hash"],
        "worker_result_capture_replay_reference": _require_string(
            worker_result_capture_replay_reference,
            "worker_result_capture_replay_reference",
        ),
        "execution_reference": result_capture.get("execution_reference"),
        "execution_hash": result_capture.get("execution_hash"),
        "execution_replay_hash": result_capture.get("execution_replay_hash"),
        "execution_replay_reference": result_capture.get("execution_replay_reference"),
        "execution_status": result_capture.get("execution_status"),
        "worker_invocation_reference": result_capture["worker_invocation_reference"],
        "worker_invocation_hash": result_capture["worker_invocation_hash"],
        "worker_dispatch_reference": result_capture["worker_dispatch_reference"],
        "worker_dispatch_hash": result_capture["worker_dispatch_hash"],
        "worker_assignment_reference": result_capture["worker_assignment_reference"],
        "worker_assignment_hash": result_capture["worker_assignment_hash"],
        "authorization_reference": result_capture["authorization_reference"],
        "authorization_hash": result_capture["authorization_hash"],
        "execution_packet_reference": result_capture["execution_packet_reference"],
        "execution_packet_hash": result_capture["execution_packet_hash"],
        "worker_id": result_capture["worker_id"],
        "worker_hash": result_capture["worker_hash"],
        "worker_family": result_capture["worker_family"],
        "worker_role": result_capture["worker_role"],
        "allowed_outputs": deepcopy(result_capture["allowed_outputs"]),
        "forbidden_operations": deepcopy(result_capture["forbidden_operations"]),
        "produced_outputs": deepcopy(result_capture["produced_outputs"]),
        "operations": deepcopy(result_capture["operations"]),
        "validation_requirements": deepcopy(result_capture["validation_requirements"]),
        "worker_output_reference": result_capture["worker_output_reference"],
        "worker_output_hash": result_capture["worker_output_hash"],
        "lineage_checks": deepcopy(lineage["lineage_checks"]),
        "recorded_at": _require_string(validated_at, "validated_at"),
        "replay_visible": True,
        **_post_validation_boundary_flags(execution_bound=_result_capture_execution_bound(result_capture)),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _classification_artifact(
    *,
    worker_result_validation_id: str,
    evidence: dict[str, Any],
    result_capture: dict[str, Any],
    validated_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_RESULT_VALIDATION_CLASSIFICATION_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_RESULT_VALIDATION_RUNTIME_VERSION,
        "validation_classification_id": f"{_require_string(worker_result_validation_id, 'worker_result_validation_id')}:CLASSIFICATION",
        "validation_evidence_reference": evidence["validation_evidence_id"],
        "validation_evidence_hash": evidence["artifact_hash"],
        "chain_id": result_capture["chain_id"],
        "execution_reference": result_capture.get("execution_reference"),
        "execution_hash": result_capture.get("execution_hash"),
        "execution_bound": _result_capture_execution_bound(result_capture),
        "execution_binding_continuous": evidence["lineage_checks"]["execution_binding_lineage"],
        "result_capture_lineage_continuous": evidence["lineage_checks"]["result_capture_lineage"],
        "invocation_lineage_continuous": evidence["lineage_checks"]["invocation_lineage"],
        "dispatch_lineage_continuous": evidence["lineage_checks"]["dispatch_lineage"],
        "assignment_lineage_continuous": evidence["lineage_checks"]["assignment_lineage"],
        "authorization_lineage_continuous": evidence["lineage_checks"]["authorization_lineage"],
        "execution_packet_lineage_continuous": evidence["lineage_checks"]["execution_packet_lineage"],
        "worker_identity_continuous": evidence["lineage_checks"]["worker_identity_continuity"],
        "chain_continuous": evidence["lineage_checks"]["chain_continuity"],
        "replay_continuous": evidence["lineage_checks"]["replay_continuity"],
        "authority_continuous": evidence["lineage_checks"]["authority_continuity"],
        "allowed_outputs_valid": set(result_capture["produced_outputs"]).issubset(set(result_capture["allowed_outputs"])),
        "forbidden_operations_absent": not set(result_capture["operations"]).intersection(
            result_capture["forbidden_operations"]
        ),
        "validation_requirements_present": _string_list(result_capture["validation_requirements"]),
        "packet_scope_bound": result_capture["execution_packet_reference"] == evidence["execution_packet_reference"],
        "worker_scope_bound": result_capture["worker_id"] == evidence["worker_id"],
        "classification_status": "WORKER_RESULT_VALIDATION_SCOPE_CLASSIFIED",
        "classified_at": _require_string(validated_at, "validated_at"),
        "replay_visible": True,
        **_post_validation_boundary_flags(execution_bound=_result_capture_execution_bound(result_capture)),
    }
    checks = (
        artifact["execution_binding_continuous"],
        artifact["result_capture_lineage_continuous"],
        artifact["invocation_lineage_continuous"],
        artifact["dispatch_lineage_continuous"],
        artifact["assignment_lineage_continuous"],
        artifact["authorization_lineage_continuous"],
        artifact["execution_packet_lineage_continuous"],
        artifact["worker_identity_continuous"],
        artifact["chain_continuous"],
        artifact["replay_continuous"],
        artifact["authority_continuous"],
        artifact["allowed_outputs_valid"],
        artifact["forbidden_operations_absent"],
        artifact["validation_requirements_present"],
        artifact["packet_scope_bound"],
        artifact["worker_scope_bound"],
    )
    if not all(checks):
        raise FailClosedRuntimeError("worker result validation failed closed: validation eligibility invalid")
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _validation_artifact(
    *,
    worker_result_validation_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    result_capture: dict[str, Any],
    validated_by: str,
    validated_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_RESULT_VALIDATION_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_RESULT_VALIDATION_RUNTIME_VERSION,
        "worker_result_validation_id": _require_string(worker_result_validation_id, "worker_result_validation_id"),
        "validation_status": RESULT_VALIDATED,
        "validation_evidence_reference": evidence["validation_evidence_id"],
        "validation_evidence_hash": evidence["artifact_hash"],
        "validation_classification_reference": classification["validation_classification_id"],
        "validation_classification_hash": classification["artifact_hash"],
        "worker_result_capture_reference": result_capture["worker_result_capture_id"],
        "worker_result_capture_hash": result_capture["artifact_hash"],
        "execution_reference": result_capture.get("execution_reference"),
        "execution_hash": result_capture.get("execution_hash"),
        "execution_replay_hash": result_capture.get("execution_replay_hash"),
        "execution_replay_reference": result_capture.get("execution_replay_reference"),
        "execution_status": result_capture.get("execution_status"),
        "worker_invocation_reference": result_capture["worker_invocation_reference"],
        "worker_invocation_hash": result_capture["worker_invocation_hash"],
        "worker_dispatch_reference": result_capture["worker_dispatch_reference"],
        "worker_dispatch_hash": result_capture["worker_dispatch_hash"],
        "worker_assignment_reference": result_capture["worker_assignment_reference"],
        "worker_assignment_hash": result_capture["worker_assignment_hash"],
        "authorization_reference": result_capture["authorization_reference"],
        "authorization_hash": result_capture["authorization_hash"],
        "execution_packet_reference": result_capture["execution_packet_reference"],
        "execution_packet_hash": result_capture["execution_packet_hash"],
        "worker_id": result_capture["worker_id"],
        "worker_hash": result_capture["worker_hash"],
        "worker_family": result_capture["worker_family"],
        "worker_role": result_capture["worker_role"],
        "allowed_outputs": deepcopy(result_capture["allowed_outputs"]),
        "forbidden_operations": deepcopy(result_capture["forbidden_operations"]),
        "produced_outputs": deepcopy(result_capture["produced_outputs"]),
        "operations": deepcopy(result_capture["operations"]),
        "validation_requirements": deepcopy(result_capture["validation_requirements"]),
        "worker_output_reference": result_capture["worker_output_reference"],
        "worker_output_hash": result_capture["worker_output_hash"],
        "validated_by": _require_string(validated_by, "validated_by"),
        "validated_at": _require_string(validated_at, "validated_at"),
        "chain_id": result_capture["chain_id"],
        "replay_reference": result_capture["replay_reference"],
        "replay_visible": True,
        **_post_validation_boundary_flags(execution_bound=_result_capture_execution_bound(result_capture)),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_validation_artifact(artifact)
    return artifact


def _result_artifact(
    *,
    worker_result_validation_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    validation: dict[str, Any],
    validated_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_RESULT_VALIDATION_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_RESULT_VALIDATION_RUNTIME_VERSION,
        "validation_result_id": f"{_require_string(worker_result_validation_id, 'worker_result_validation_id')}:RESULT",
        "validation_status": status,
        "validation_evidence_reference": evidence["validation_evidence_id"],
        "validation_evidence_hash": evidence["artifact_hash"],
        "validation_classification_reference": classification["validation_classification_id"],
        "validation_classification_hash": classification["artifact_hash"],
        "worker_result_validation_reference": validation["worker_result_validation_id"],
        "worker_result_validation_hash": validation["artifact_hash"],
        "worker_result_capture_reference": validation["worker_result_capture_reference"],
        "worker_result_capture_hash": validation["worker_result_capture_hash"],
        "execution_reference": validation.get("execution_reference"),
        "execution_hash": validation.get("execution_hash"),
        "execution_replay_reference": validation.get("execution_replay_reference"),
        "worker_reference": validation["worker_id"],
        "worker_hash": validation["worker_hash"],
        "chain_id": validation["chain_id"],
        "completed_at": _require_string(validated_at, "validated_at"),
        "replay_visible": True,
        **_post_validation_boundary_flags(execution_bound=bool(validation.get("execution_reference"))),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_result(
    *,
    worker_result_validation_id: str,
    worker_result_capture_reference: str | None,
    worker_result_capture_replay_reference: str,
    validated_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_RESULT_VALIDATION_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_RESULT_VALIDATION_RUNTIME_VERSION,
        "validation_result_id": f"{worker_result_validation_id}:RESULT",
        "validation_status": FAILED_CLOSED,
        "validation_evidence_reference": None,
        "validation_evidence_hash": None,
        "validation_classification_reference": None,
        "validation_classification_hash": None,
        "worker_result_validation_reference": None,
        "worker_result_validation_hash": None,
        "worker_result_capture_reference": worker_result_capture_reference,
        "worker_result_capture_hash": None,
        "worker_result_capture_replay_reference": worker_result_capture_replay_reference,
        "worker_reference": None,
        "worker_hash": None,
        "chain_id": None,
        "completed_at": validated_at,
        "replay_visible": True,
        **_pre_validation_boundary_flags(),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    evidence: dict[str, Any] | None,
    classification: dict[str, Any] | None,
    validation: dict[str, Any] | None,
    result: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = deepcopy(result)
    capture.update(
        {
            "validation_evidence_artifact": deepcopy(evidence),
            "validation_classification_artifact": deepcopy(classification),
            "worker_result_validation_artifact": deepcopy(validation),
            "validation_result_artifact": deepcopy(result),
            "worker_result_validation_reference": validation.get("worker_result_validation_id")
            if validation
            else None,
            "worker_result_capture_reference": validation.get("worker_result_capture_reference")
            if validation
            else None,
            "execution_reference": validation.get("execution_reference") if validation else None,
            "execution_hash": validation.get("execution_hash") if validation else None,
            "execution_replay_reference": validation.get("execution_replay_reference") if validation else None,
            "worker_id": validation.get("worker_id") if validation else None,
            "worker_family": validation.get("worker_family") if validation else None,
            "worker_role": validation.get("worker_role") if validation else None,
            "worker_result_validation_replay_reference": str(replay_path),
            "fail_closed": result["validation_status"] == FAILED_CLOSED,
        }
    )
    capture["worker_result_validation_capture_hash"] = replay_hash(capture)
    return capture


def _result_capture_already_validated(
    root: Path,
    *,
    result_capture_reference: str,
    result_capture_hash: str,
) -> bool:
    for path in root.glob("TURN-*/worker_result_validation"):
        try:
            reconstructed = reconstruct_worker_result_validation_replay(path)
            wrapper = load_json(path / "002_validation_artifact_recorded.json")
            _verify_wrapper_hash(wrapper)
            validation = wrapper.get("artifact")
            if not isinstance(validation, dict):
                continue
            _verify_artifact_hash(validation, "worker result validation artifact")
        except FailClosedRuntimeError:
            continue
        if reconstructed.get("validation_status") != RESULT_VALIDATED:
            continue
        if (
            validation.get("worker_result_capture_reference") == result_capture_reference
            and validation.get("worker_result_capture_hash") == result_capture_hash
        ):
            return True
    return False


def _validate_validation_artifact(validation: dict[str, Any]) -> None:
    if validation.get("artifact_type") != WORKER_RESULT_VALIDATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker result validation failed closed: invalid validation artifact")
    if validation.get("validation_status") != RESULT_VALIDATED:
        raise FailClosedRuntimeError("worker result validation failed closed: invalid validation status")
    execution_bound = bool(validation.get("execution_reference"))
    for field, expected in _post_validation_boundary_flags(execution_bound=execution_bound).items():
        if validation.get(field) is not expected:
            raise FailClosedRuntimeError("worker result validation failed closed: authority violation")
    if not set(validation.get("produced_outputs", [])).issubset(set(validation.get("allowed_outputs", []))):
        raise FailClosedRuntimeError("worker result validation failed closed: result outside allowed outputs")
    if set(validation.get("operations", [])).intersection(validation.get("forbidden_operations", [])):
        raise FailClosedRuntimeError("worker result validation failed closed: forbidden operation detected")
    if not _string_list(validation.get("validation_requirements")):
        raise FailClosedRuntimeError("worker result validation failed closed: validation requirement missing")
    for field in (
        "worker_result_validation_id",
        "worker_result_capture_reference",
        "worker_result_capture_hash",
        "worker_invocation_reference",
        "worker_invocation_hash",
        "worker_dispatch_reference",
        "worker_dispatch_hash",
        "authorization_reference",
        "authorization_hash",
        "execution_packet_reference",
        "execution_packet_hash",
        "worker_id",
        "worker_hash",
        "worker_family",
        "worker_role",
        "chain_id",
        "validated_by",
        "validated_at",
    ):
        _require_string(validation.get(field), field)
    if execution_bound:
        for field in (
            "execution_reference",
            "execution_hash",
            "execution_replay_hash",
            "execution_status",
        ):
            _require_string(validation.get(field), field)
        if validation.get("execution_status") != EXECUTING:
            raise FailClosedRuntimeError("worker result validation failed closed: invalid execution state")


def _result_capture_authority_continuity(result_capture: dict[str, Any]) -> bool:
    execution_bound = _result_capture_execution_bound(result_capture)
    return (
        result_capture.get("approval_created") is False
        and result_capture.get("worker_assigned") is True
        and result_capture.get("worker_dispatched") is True
        and result_capture.get("dispatch_requested") is True
        and result_capture.get("worker_invoked") is True
        and result_capture.get("execution_started") is execution_bound
        and result_capture.get("result_created") is True
        and result_capture.get("worker_result_captured") is True
        and result_capture.get("result_validated") is False
        and result_capture.get("post_execution_replay_reviewed") is False
        and result_capture.get("terminated") is False
        and result_capture.get("governance_mutated") is False
        and result_capture.get("replay_mutated") is False
    )


def _result_capture_execution_bound(result_capture: dict[str, Any]) -> bool:
    if result_capture.get("execution_started") is True:
        return True
    return _has_execution_binding(result_capture)


def _has_execution_binding(artifact: dict[str, Any]) -> bool:
    return any(
        artifact.get(field) is not None
        for field in (
            "execution_reference",
            "execution_hash",
            "execution_replay_hash",
            "execution_replay_reference",
            "execution_status",
        )
    )


def _pre_validation_boundary_flags(*, execution_bound: bool = False) -> dict[str, bool]:
    return {
        "approval_created": False,
        "worker_assigned": True,
        "worker_dispatched": True,
        "dispatch_requested": True,
        "worker_invoked": True,
        "execution_started": execution_bound,
        "result_created": True,
        "worker_result_captured": True,
        "result_validated": False,
        "post_execution_replay_reviewed": False,
        "terminated": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _post_validation_boundary_flags(*, execution_bound: bool = False) -> dict[str, bool]:
    return {
        "approval_created": False,
        "worker_assigned": True,
        "worker_dispatched": True,
        "dispatch_requested": True,
        "worker_invoked": True,
        "execution_started": execution_bound,
        "result_created": True,
        "worker_result_captured": True,
        "result_validated": True,
        "post_execution_replay_reviewed": False,
        "terminated": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("worker result validation replay ordering mismatch")
    _verify_artifact_hash(artifact, "worker result validation artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "event_type": step.upper(),
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(replay_dir / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    try:
        _persist_step(replay_dir, index, step, artifact)
    except FailClosedRuntimeError:
        pass


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        if (replay_path / f"{index:03d}_{step}.json").exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {step}")


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    candidate = deepcopy(artifact)
    actual = candidate.pop("artifact_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("worker result validation replay hash is required")
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("worker result validation replay hash mismatch")


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"worker result validation failed closed: {field} is required")
    return value


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return f"worker result validation failed closed: {exc}"
