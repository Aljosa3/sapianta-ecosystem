"""Replay-visible Worker result capture runtime for the current AiGOL execution chain."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any

from aigol.runtime.execution_runtime import (
    EXECUTING,
    EXECUTION_ARTIFACT_V1,
    EXECUTION_RETURNED,
    reconstruct_execution_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable
from aigol.runtime.worker_invocation_runtime import (
    WORKER_INVOCATION_ARTIFACT_V1,
    WORKER_INVOKED,
    _domain_execution_ready_bridge_index,
    _matching_bridge_for_dispatch,
    _resolve_replay_reference,
    reconstruct_worker_invocation_replay,
)


AIGOL_WORKER_RESULT_CAPTURE_RUNTIME_VERSION = "AIGOL_WORKER_RESULT_CAPTURE_RUNTIME_V1"
WORKER_RESULT_CAPTURE_EVIDENCE_ARTIFACT_V1 = "WORKER_RESULT_CAPTURE_EVIDENCE_ARTIFACT_V1"
WORKER_RESULT_CAPTURE_CLASSIFICATION_ARTIFACT_V1 = "WORKER_RESULT_CAPTURE_CLASSIFICATION_ARTIFACT_V1"
WORKER_RESULT_CAPTURE_ARTIFACT_V1 = "WORKER_RESULT_CAPTURE_ARTIFACT_V1"
WORKER_RESULT_CAPTURE_RESULT_ARTIFACT_V1 = "WORKER_RESULT_CAPTURE_RESULT_ARTIFACT_V1"
WORKER_RESULT_CAPTURED = "WORKER_RESULT_CAPTURED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "result_capture_evidence_recorded",
    "result_capture_classification_recorded",
    "result_capture_artifact_recorded",
    "result_capture_result_recorded",
)

FORBIDDEN_OUTPUT_FIELDS = frozenset(
    {
        "approval_created",
        "approval_decision",
        "authorization_decision",
        "governance_mutated",
        "replay_mutated",
        "result_validated",
        "semantic_validation",
        "post_execution_replay_reviewed",
        "terminated",
        "credentials",
        "api_key",
        "secret",
    }
)


def detect_domain_worker_result_capture_entry_intent(human_prompt: str) -> dict[str, Any]:
    """Detect narrow operator prompts for domain Worker result capture."""

    prompt = _require_string(human_prompt, "human_prompt")
    normalized = " ".join(prompt.strip().rstrip(".?!").split())
    lowered = normalized.lower()
    patterns = (
        r"^capture\s+worker\s+result\s+for\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)$",
        r"^capture\s+result\s+for\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)$",
        r"^continue\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)\s+to\s+result\s+capture$",
        r"^create\s+worker\s+result\s+capture\s+for\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)$",
        r"^create\s+result\s+capture\s+for\s+(?P<domain>[A-Za-z][A-Za-z0-9_-]*)$",
    )
    for pattern in patterns:
        match = re.match(pattern, normalized, flags=re.IGNORECASE)
        if match:
            if lowered.startswith("continue"):
                action = "CONTINUE_TO_WORKER_RESULT_CAPTURE"
            elif lowered.startswith("create"):
                action = "CREATE_WORKER_RESULT_CAPTURE"
            else:
                action = "CAPTURE_WORKER_RESULT"
            return {
                "worker_result_capture_entry_intent_detected": True,
                "domain_name": match.group("domain"),
                "worker_result_capture_action": action,
                "matched_prompt": normalized,
            }
    return {
        "worker_result_capture_entry_intent_detected": False,
        "domain_name": None,
        "worker_result_capture_action": None,
        "matched_prompt": normalized,
    }


def find_latest_domain_execution_for_result_capture(
    *,
    session_root: str | Path,
    domain_name: str,
) -> dict[str, Any]:
    """Find the latest execution replay for a domain without result capture."""

    root = Path(session_root)
    domain = _require_string(domain_name, "domain_name")
    if not root.exists():
        raise FailClosedRuntimeError("worker result capture failed closed: session root missing")
    bridge_index = _domain_execution_ready_bridge_index(root, domain)
    candidates: list[dict[str, Any]] = []
    for path in sorted(root.glob("TURN-*/execution_runtime")):
        try:
            reconstructed = reconstruct_execution_replay(path)
            execution_wrapper = load_json(path / "000_execution_started.json")
            replay_wrapper = load_json(path / "001_execution_returned.json")
            _verify_wrapper_hash(execution_wrapper)
            _verify_wrapper_hash(replay_wrapper)
            execution = execution_wrapper.get("artifact")
            execution_replay = replay_wrapper.get("artifact")
            if not isinstance(execution, dict) or not isinstance(execution_replay, dict):
                continue
            _verify_artifact_hash(execution, "execution artifact")
            _verify_artifact_hash(execution_replay, "execution replay artifact")
        except FailClosedRuntimeError:
            continue
        if reconstructed.get("execution_status") != EXECUTING:
            continue
        try:
            invocation_path, invocation, invocation_evidence = _invocation_for_execution(root, execution)
            dispatch_replay_path = _resolve_replay_reference(
                invocation_evidence.get("worker_dispatch_replay_reference"),
                anchor=invocation_path,
            )
            dispatch_wrapper = load_json(dispatch_replay_path / "002_dispatch_artifact_recorded.json")
            _verify_wrapper_hash(dispatch_wrapper)
            dispatch = dispatch_wrapper.get("artifact")
            if not isinstance(dispatch, dict):
                continue
            _verify_artifact_hash(dispatch, "worker dispatch artifact")
        except FailClosedRuntimeError:
            continue
        bridge = _matching_bridge_for_dispatch(dispatch_replay_path, dispatch, bridge_index)
        if bridge is None:
            continue
        if _execution_already_result_captured(
            root,
            execution_reference=str(execution.get("execution_id") or ""),
            execution_hash=str(execution.get("artifact_hash") or ""),
        ):
            continue
        candidates.append(
            {
                "execution_replay_reference": str(path),
                "execution_artifact": deepcopy(execution),
                "execution_replay": deepcopy(execution_replay),
                "worker_invocation_artifact": deepcopy(invocation),
                "worker_invocation_replay_reference": str(invocation_path),
                "domain_execution_ready_bridge_replay_reference": bridge[
                    "domain_execution_ready_bridge_replay_reference"
                ],
                "domain_name": bridge["approved_domain"],
                "execution_reference": execution["execution_id"],
                "execution_hash": execution["artifact_hash"],
                "worker_invocation_reference": invocation["worker_invocation_id"],
                "chain_id": invocation["chain_id"],
                "worker_id": invocation["worker_id"],
                "worker_role": invocation["worker_role"],
                "turn_id": path.parent.name,
            }
        )
    if not candidates:
        raise FailClosedRuntimeError("worker result capture failed closed: matching execution not found")
    return candidates[-1]


def capture_worker_result(
    *,
    worker_result_capture_id: str,
    worker_invocation_artifact: dict[str, Any],
    worker_invocation_replay_reference: str,
    worker_output: dict[str, Any],
    captured_by: str,
    captured_at: str,
    replay_dir: str | Path,
    execution_artifact: dict[str, Any] | None = None,
    execution_replay: dict[str, Any] | None = None,
    execution_replay_reference: str | None = None,
) -> dict[str, Any]:
    """Capture Worker output without semantic validation, replay review, or termination."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        lineage = _load_invocation_lineage(Path(worker_invocation_replay_reference), worker_invocation_artifact)
        invocation = lineage["invocation"]
        execution_binding = _validate_execution_binding(
            execution_artifact=execution_artifact,
            execution_replay=execution_replay,
            execution_replay_reference=execution_replay_reference,
            invocation=invocation,
        )
        output = _validate_worker_output(worker_output, invocation)
        evidence = _evidence_artifact(
            worker_result_capture_id=worker_result_capture_id,
            invocation=invocation,
            lineage=lineage,
            worker_invocation_replay_reference=worker_invocation_replay_reference,
            execution_binding=execution_binding,
            worker_output=output,
            captured_at=captured_at,
        )
        classification = _classification_artifact(
            worker_result_capture_id=worker_result_capture_id,
            evidence=evidence,
            invocation=invocation,
            execution_binding=execution_binding,
            worker_output=output,
            captured_at=captured_at,
        )
        capture_artifact = _result_capture_artifact(
            worker_result_capture_id=worker_result_capture_id,
            evidence=evidence,
            classification=classification,
            invocation=invocation,
            execution_binding=execution_binding,
            worker_output=output,
            captured_by=captured_by,
            captured_at=captured_at,
        )
        result = _result_artifact(
            worker_result_capture_id=worker_result_capture_id,
            evidence=evidence,
            classification=classification,
            capture_artifact=capture_artifact,
            captured_at=captured_at,
            status=WORKER_RESULT_CAPTURED,
            failure_reason=None,
        )
        _persist_step(replay_path, 0, REPLAY_STEPS[0], evidence)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], classification)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], capture_artifact)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], result)
        return _capture(evidence, classification, capture_artifact, result, replay_path)
    except Exception as exc:
        result = _failed_result(
            worker_result_capture_id=worker_result_capture_id,
            worker_invocation_reference=(
                worker_invocation_artifact.get("worker_invocation_id")
                if isinstance(worker_invocation_artifact, dict)
                else None
            ),
            worker_invocation_replay_reference=worker_invocation_replay_reference,
            captured_at=captured_at,
            failure_reason=_failure_reason(exc),
        )
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], result)
        return _capture(None, None, None, result, replay_path)


def reconstruct_worker_result_capture_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct Worker result capture replay deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("worker result capture replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("worker result capture replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "worker result capture replay artifact")
        wrappers.append(wrapper)

    evidence = wrappers[0]["artifact"]
    classification = wrappers[1]["artifact"]
    capture_artifact = wrappers[2]["artifact"]
    result = wrappers[3]["artifact"]
    if classification.get("result_capture_evidence_hash") != evidence["artifact_hash"]:
        raise FailClosedRuntimeError("worker result capture replay evidence lineage mismatch")
    if capture_artifact.get("result_capture_classification_hash") != classification["artifact_hash"]:
        raise FailClosedRuntimeError("worker result capture replay classification lineage mismatch")
    if result.get("worker_result_capture_hash") != capture_artifact["artifact_hash"]:
        raise FailClosedRuntimeError("worker result capture replay continuity mismatch")
    if len({evidence["chain_id"], classification["chain_id"], capture_artifact["chain_id"], result["chain_id"]}) != 1:
        raise FailClosedRuntimeError("worker result capture replay chain mismatch")
    if evidence["worker_invocation_hash"] != capture_artifact["worker_invocation_hash"]:
        raise FailClosedRuntimeError("worker result capture replay invocation lineage mismatch")
    _validate_result_capture_artifact(capture_artifact)
    _load_invocation_lineage(
        Path(evidence["worker_invocation_replay_reference"]),
        None,
        result_capture=capture_artifact,
    )
    return {
        "worker_result_capture_id": capture_artifact["worker_result_capture_id"],
        "result_capture_status": result["result_capture_status"],
        "worker_invocation_reference": capture_artifact["worker_invocation_reference"],
        "worker_dispatch_reference": capture_artifact["worker_dispatch_reference"],
        "worker_assignment_reference": capture_artifact["worker_assignment_reference"],
        "execution_reference": capture_artifact.get("execution_reference"),
        "execution_hash": capture_artifact.get("execution_hash"),
        "execution_replay_reference": capture_artifact.get("execution_replay_reference"),
        "authorization_reference": capture_artifact["authorization_reference"],
        "execution_packet_reference": capture_artifact["execution_packet_reference"],
        "worker_id": capture_artifact["worker_id"],
        "worker_family": capture_artifact["worker_family"],
        "worker_role": capture_artifact["worker_role"],
        "chain_id": capture_artifact["chain_id"],
        "produced_outputs": deepcopy(capture_artifact["produced_outputs"]),
        "operations": deepcopy(capture_artifact["operations"]),
        "worker_output_hash": capture_artifact["worker_output_hash"],
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
        **_post_capture_boundary_flags(execution_bound=bool(capture_artifact.get("execution_reference"))),
        "failure_reason": result["failure_reason"],
    }


def render_worker_result_capture_summary(capture: dict[str, Any]) -> str:
    lines = [
        "",
        "Worker Result Capture",
        "",
        f"Result Capture Status: {capture.get('result_capture_status')}",
        f"Worker Result Capture Reference: {capture.get('worker_result_capture_reference')}",
        f"Worker Invocation Reference: {capture.get('worker_invocation_reference')}",
        f"Captured Worker: {capture.get('worker_id')}",
        f"Replay Reference: {capture.get('worker_result_capture_replay_reference')}",
        "",
        "No semantic validation yet.",
        "No replay review yet.",
        "No termination yet.",
    ]
    if capture.get("failure_reason"):
        lines.append(f"failure_reason: {capture['failure_reason']}")
    return "\n".join(lines)


def default_worker_output_for_invocation(invocation: dict[str, Any], *, captured_at: str) -> dict[str, Any]:
    """Return deterministic in-memory Worker output for CLI continuity."""

    _validate_invocation_artifact(invocation)
    produced_outputs = deepcopy(invocation["allowed_outputs"])
    output = {
        "worker_output_id": f"{invocation['worker_invocation_id']}:WORKER-OUTPUT",
        "worker_id": invocation["worker_id"],
        "worker_family": invocation["worker_family"],
        "worker_role": invocation["worker_role"],
        "worker_invocation_reference": invocation["worker_invocation_id"],
        "worker_dispatch_reference": invocation["worker_dispatch_reference"],
        "authorization_reference": invocation["authorization_reference"],
        "execution_packet_reference": invocation["execution_packet_reference"],
        "chain_id": invocation["chain_id"],
        "produced_outputs": produced_outputs,
        "operations": ["CAPTURE_WORKER_OUTPUT"],
        "payload": {
            "capture_summary": "Worker output captured for governed result capture only.",
            "produced_output_count": len(produced_outputs),
        },
        "created_at": _require_string(captured_at, "captured_at"),
        "replay_visible": True,
    }
    output["artifact_hash"] = replay_hash(output)
    return output


def _load_invocation_lineage(
    invocation_replay_path: Path,
    provided_invocation: dict[str, Any] | None,
    *,
    result_capture: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    reconstructed = reconstruct_worker_invocation_replay(invocation_replay_path)
    if reconstructed.get("invocation_status") != WORKER_INVOKED:
        raise FailClosedRuntimeError("worker result capture failed closed: invocation invalid")
    wrappers = []
    expected = (
        (0, "invocation_evidence_recorded"),
        (1, "invocation_classification_recorded"),
        (2, "invocation_artifact_recorded"),
        (3, "invocation_result_recorded"),
    )
    for index, step in expected:
        wrapper = load_json(invocation_replay_path / f"{index:03d}_{step}.json")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("worker result capture failed closed: invocation replay corruption")
        _verify_artifact_hash(artifact, "worker invocation lineage artifact")
        wrappers.append(wrapper)
    evidence = wrappers[0]["artifact"]
    classification = wrappers[1]["artifact"]
    invocation = wrappers[2]["artifact"]
    result = wrappers[3]["artifact"]
    _validate_invocation_artifact(invocation)
    if provided_invocation is not None:
        _verify_artifact_hash(provided_invocation, "provided worker invocation artifact")
        if provided_invocation.get("worker_invocation_id") != invocation["worker_invocation_id"]:
            raise FailClosedRuntimeError("worker result capture failed closed: invocation mismatch")
        if provided_invocation.get("artifact_hash") != invocation["artifact_hash"]:
            raise FailClosedRuntimeError("worker result capture failed closed: invocation mismatch")
    if result_capture is not None:
        if result_capture.get("worker_invocation_reference") != invocation["worker_invocation_id"]:
            raise FailClosedRuntimeError("worker result capture failed closed: invocation mismatch")
        if result_capture.get("worker_invocation_hash") != invocation["artifact_hash"]:
            raise FailClosedRuntimeError("worker result capture failed closed: invocation mismatch")
    checks = {
        "invocation_lineage": result["worker_invocation_hash"] == invocation["artifact_hash"],
        "dispatch_lineage": invocation["worker_dispatch_hash"] == evidence["worker_dispatch_hash"],
        "assignment_lineage": invocation["worker_assignment_hash"] == evidence["worker_assignment_hash"],
        "authorization_lineage": invocation["authorization_hash"] == evidence["authorization_hash"],
        "execution_packet_lineage": invocation["execution_packet_hash"] == evidence["execution_packet_hash"],
        "worker_identity_continuity": invocation["worker_id"] == evidence["worker_id"]
        and invocation["worker_hash"] == evidence["worker_hash"],
        "chain_continuity": invocation["chain_id"] == evidence["chain_id"],
        "replay_continuity": reconstructed["invocation_status"] == WORKER_INVOKED,
        "authority_continuity": _invocation_authority_continuity(invocation),
    }
    if not all(checks.values()):
        raise FailClosedRuntimeError("worker result capture failed closed: lineage continuity invalid")
    return {
        "invocation_evidence": evidence,
        "invocation_classification": classification,
        "invocation": invocation,
        "invocation_result": result,
        "lineage_checks": checks,
    }


def _validate_execution_binding(
    *,
    execution_artifact: dict[str, Any] | None,
    execution_replay: dict[str, Any] | None,
    execution_replay_reference: str | None,
    invocation: dict[str, Any],
) -> dict[str, Any] | None:
    if execution_artifact is None and execution_replay is None and execution_replay_reference is None:
        return None
    if execution_artifact is None or execution_replay is None:
        raise FailClosedRuntimeError("worker result capture failed closed: execution binding incomplete")
    _verify_artifact_hash(execution_artifact, "execution artifact")
    _verify_artifact_hash(execution_replay, "execution replay artifact")
    if execution_artifact.get("artifact_type") != EXECUTION_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker result capture failed closed: invalid execution artifact")
    if execution_artifact.get("execution_status") != EXECUTING:
        raise FailClosedRuntimeError("worker result capture failed closed: invalid execution state")
    if execution_replay.get("event_type") != EXECUTION_RETURNED:
        raise FailClosedRuntimeError("worker result capture failed closed: invalid execution replay event")
    for field in (
        "provider_authority",
        "worker_self_started",
        "completion_recorded",
        "result_certified",
        "self_improvement_performed",
        "governance_mutated",
        "replay_mutated",
        "scope_expansion",
    ):
        if execution_artifact.get(field) is not False:
            raise FailClosedRuntimeError("worker result capture failed closed: execution authority violation")
    if execution_artifact.get("execution_started") is not True:
        raise FailClosedRuntimeError("worker result capture failed closed: execution start missing")
    if execution_artifact.get("replay_visible") is not True or execution_replay.get("replay_visible") is not True:
        raise FailClosedRuntimeError("worker result capture failed closed: execution replay visibility missing")
    if execution_artifact.get("worker_invocation_reference") != invocation["worker_invocation_id"]:
        raise FailClosedRuntimeError("worker result capture failed closed: execution invocation mismatch")
    if execution_artifact.get("worker_invocation_hash") != invocation["artifact_hash"]:
        raise FailClosedRuntimeError("worker result capture failed closed: execution invocation mismatch")
    if execution_artifact.get("dispatch_reference") != invocation["worker_dispatch_reference"]:
        raise FailClosedRuntimeError("worker result capture failed closed: execution dispatch mismatch")
    if execution_artifact.get("dispatch_hash") != invocation["worker_dispatch_hash"]:
        raise FailClosedRuntimeError("worker result capture failed closed: execution dispatch mismatch")
    if execution_artifact.get("worker_assignment_reference") != invocation["worker_assignment_reference"]:
        raise FailClosedRuntimeError("worker result capture failed closed: execution assignment mismatch")
    if execution_artifact.get("worker_assignment_hash") != invocation["worker_assignment_hash"]:
        raise FailClosedRuntimeError("worker result capture failed closed: execution assignment mismatch")
    if execution_artifact.get("worker_reference") != invocation["worker_id"]:
        raise FailClosedRuntimeError("worker result capture failed closed: execution worker mismatch")
    if execution_artifact.get("worker_hash") != invocation["worker_hash"]:
        raise FailClosedRuntimeError("worker result capture failed closed: execution worker mismatch")
    if execution_artifact.get("canonical_chain_id") != invocation["chain_id"]:
        raise FailClosedRuntimeError("worker result capture failed closed: execution chain mismatch")
    if execution_artifact.get("execution_request_reference") != invocation["worker_invocation_request_reference"]:
        raise FailClosedRuntimeError("worker result capture failed closed: execution request mismatch")
    if execution_artifact.get("readiness_reference") != invocation["execution_packet_reference"]:
        raise FailClosedRuntimeError("worker result capture failed closed: execution packet mismatch")

    replay_checks = {
        "execution_reference": execution_replay.get("execution_reference") == execution_artifact["execution_id"],
        "execution_hash": execution_replay.get("execution_hash") == execution_artifact["artifact_hash"],
        "worker_invocation_reference": execution_replay.get("worker_invocation_reference")
        == execution_artifact["worker_invocation_reference"],
        "worker_invocation_hash": execution_replay.get("worker_invocation_hash")
        == execution_artifact["worker_invocation_hash"],
        "dispatch_reference": execution_replay.get("dispatch_reference") == execution_artifact["dispatch_reference"],
        "dispatch_hash": execution_replay.get("dispatch_hash") == execution_artifact["dispatch_hash"],
        "worker_assignment_reference": execution_replay.get("worker_assignment_reference")
        == execution_artifact["worker_assignment_reference"],
        "worker_reference": execution_replay.get("worker_reference") == execution_artifact["worker_reference"],
        "worker_hash": execution_replay.get("worker_hash") == execution_artifact["worker_hash"],
        "chain_continuity": execution_replay.get("canonical_chain_id") == execution_artifact["canonical_chain_id"],
        "execution_started": execution_replay.get("execution_started") is True,
        "completion_absent": execution_replay.get("completion_recorded") is False,
        "result_certification_absent": execution_replay.get("result_certified") is False,
        "authority_continuity": execution_replay.get("provider_authority") is False
        and execution_replay.get("worker_self_started") is False
        and execution_replay.get("governance_mutated") is False
        and execution_replay.get("replay_mutated") is False
        and execution_replay.get("scope_expansion") is False,
    }
    if not all(replay_checks.values()):
        raise FailClosedRuntimeError("worker result capture failed closed: execution replay mismatch")
    if execution_replay_reference is not None:
        reconstructed = reconstruct_execution_replay(Path(execution_replay_reference))
        if reconstructed.get("execution_id") != execution_artifact["execution_id"]:
            raise FailClosedRuntimeError("worker result capture failed closed: execution replay mismatch")
        if reconstructed.get("worker_invocation_reference") != invocation["worker_invocation_id"]:
            raise FailClosedRuntimeError("worker result capture failed closed: execution replay mismatch")
        if reconstructed.get("canonical_chain_id") != invocation["chain_id"]:
            raise FailClosedRuntimeError("worker result capture failed closed: execution replay mismatch")
    return {
        "execution_reference": execution_artifact["execution_id"],
        "execution_hash": execution_artifact["artifact_hash"],
        "execution_replay_hash": execution_replay["artifact_hash"],
        "execution_replay_reference": execution_replay_reference,
        "execution_status": execution_artifact["execution_status"],
        "execution_lineage_checks": replay_checks,
    }


def _validate_invocation_artifact(invocation: dict[str, Any]) -> None:
    if invocation.get("artifact_type") != WORKER_INVOCATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker result capture failed closed: invalid invocation artifact")
    if invocation.get("invocation_status") != WORKER_INVOKED:
        raise FailClosedRuntimeError("worker result capture failed closed: invocation invalid")
    for field, expected in _pre_capture_boundary_flags().items():
        if invocation.get(field) is not expected:
            raise FailClosedRuntimeError("worker result capture failed closed: authority violation")
    if not _string_list(invocation.get("allowed_outputs")):
        raise FailClosedRuntimeError("worker result capture failed closed: allowed outputs missing")
    if not _string_list(invocation.get("forbidden_operations")):
        raise FailClosedRuntimeError("worker result capture failed closed: forbidden operations missing")
    for field in (
        "worker_invocation_id",
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
    ):
        _require_string(invocation.get(field), field)


def _validate_worker_output(worker_output: dict[str, Any], invocation: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(worker_output, dict):
        raise FailClosedRuntimeError("worker result capture failed closed: worker output is required")
    output = deepcopy(worker_output)
    _verify_artifact_hash(output, "worker output artifact")
    if FORBIDDEN_OUTPUT_FIELDS.intersection(output):
        raise FailClosedRuntimeError("worker result capture failed closed: authority violation")
    if output.get("worker_id") != invocation["worker_id"]:
        raise FailClosedRuntimeError("worker result capture failed closed: worker mismatch")
    if output.get("worker_family") != invocation["worker_family"]:
        raise FailClosedRuntimeError("worker result capture failed closed: worker mismatch")
    if output.get("worker_role") != invocation["worker_role"]:
        raise FailClosedRuntimeError("worker result capture failed closed: worker mismatch")
    if output.get("worker_invocation_reference") != invocation["worker_invocation_id"]:
        raise FailClosedRuntimeError("worker result capture failed closed: invocation mismatch")
    if output.get("worker_dispatch_reference") != invocation["worker_dispatch_reference"]:
        raise FailClosedRuntimeError("worker result capture failed closed: dispatch mismatch")
    if output.get("authorization_reference") != invocation["authorization_reference"]:
        raise FailClosedRuntimeError("worker result capture failed closed: authorization mismatch")
    if output.get("execution_packet_reference") != invocation["execution_packet_reference"]:
        raise FailClosedRuntimeError("worker result capture failed closed: packet mismatch")
    if output.get("chain_id") != invocation["chain_id"]:
        raise FailClosedRuntimeError("worker result capture failed closed: chain mismatch")
    produced_outputs = output.get("produced_outputs")
    if not _string_list(produced_outputs):
        raise FailClosedRuntimeError("worker result capture failed closed: output outside allowed scope")
    allowed_outputs = set(invocation["allowed_outputs"])
    if not set(produced_outputs).issubset(allowed_outputs):
        raise FailClosedRuntimeError("worker result capture failed closed: output outside allowed scope")
    operations = output.get("operations")
    if not _string_list(operations):
        raise FailClosedRuntimeError("worker result capture failed closed: operations are required")
    forbidden = set(invocation["forbidden_operations"])
    if forbidden.intersection(operations):
        raise FailClosedRuntimeError("worker result capture failed closed: forbidden operation detected")
    if output.get("replay_visible") is not True:
        raise FailClosedRuntimeError("worker result capture failed closed: replay visibility missing")
    _require_string(output.get("worker_output_id"), "worker_output_id")
    return output


def _evidence_artifact(
    *,
    worker_result_capture_id: str,
    invocation: dict[str, Any],
    lineage: dict[str, dict[str, Any]],
    worker_invocation_replay_reference: str,
    execution_binding: dict[str, Any] | None,
    worker_output: dict[str, Any],
    captured_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_RESULT_CAPTURE_EVIDENCE_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_RESULT_CAPTURE_RUNTIME_VERSION,
        "result_capture_evidence_id": f"{_require_string(worker_result_capture_id, 'worker_result_capture_id')}:EVIDENCE",
        "chain_id": invocation["chain_id"],
        "worker_invocation_reference": invocation["worker_invocation_id"],
        "worker_invocation_hash": invocation["artifact_hash"],
        "worker_invocation_replay_reference": _require_string(
            worker_invocation_replay_reference,
            "worker_invocation_replay_reference",
        ),
        "execution_reference": _optional_binding_value(execution_binding, "execution_reference"),
        "execution_hash": _optional_binding_value(execution_binding, "execution_hash"),
        "execution_replay_hash": _optional_binding_value(execution_binding, "execution_replay_hash"),
        "execution_replay_reference": _optional_binding_value(execution_binding, "execution_replay_reference"),
        "execution_status": _optional_binding_value(execution_binding, "execution_status"),
        "worker_dispatch_reference": invocation["worker_dispatch_reference"],
        "worker_dispatch_hash": invocation["worker_dispatch_hash"],
        "worker_assignment_reference": invocation["worker_assignment_reference"],
        "worker_assignment_hash": invocation["worker_assignment_hash"],
        "worker_invocation_request_reference": invocation["worker_invocation_request_reference"],
        "worker_invocation_request_hash": invocation["worker_invocation_request_hash"],
        "authorization_reference": invocation["authorization_reference"],
        "authorization_hash": invocation["authorization_hash"],
        "execution_packet_reference": invocation["execution_packet_reference"],
        "execution_packet_hash": invocation["execution_packet_hash"],
        "worker_id": invocation["worker_id"],
        "worker_hash": invocation["worker_hash"],
        "worker_family": invocation["worker_family"],
        "worker_role": invocation["worker_role"],
        "allowed_outputs": deepcopy(invocation["allowed_outputs"]),
        "forbidden_operations": deepcopy(invocation["forbidden_operations"]),
        "validation_requirements": deepcopy(invocation["validation_requirements"]),
        "produced_outputs": deepcopy(worker_output["produced_outputs"]),
        "operations": deepcopy(worker_output["operations"]),
        "worker_output_reference": worker_output["worker_output_id"],
        "worker_output_hash": worker_output["artifact_hash"],
        "lineage_checks": deepcopy(lineage["lineage_checks"]),
        "execution_lineage_checks": deepcopy(_optional_binding_value(execution_binding, "execution_lineage_checks")),
        "recorded_at": _require_string(captured_at, "captured_at"),
        "replay_visible": True,
        **_post_capture_boundary_flags(execution_bound=execution_binding is not None),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _classification_artifact(
    *,
    worker_result_capture_id: str,
    evidence: dict[str, Any],
    invocation: dict[str, Any],
    execution_binding: dict[str, Any] | None,
    worker_output: dict[str, Any],
    captured_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_RESULT_CAPTURE_CLASSIFICATION_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_RESULT_CAPTURE_RUNTIME_VERSION,
        "result_capture_classification_id": f"{_require_string(worker_result_capture_id, 'worker_result_capture_id')}:CLASSIFICATION",
        "result_capture_evidence_reference": evidence["result_capture_evidence_id"],
        "result_capture_evidence_hash": evidence["artifact_hash"],
        "chain_id": invocation["chain_id"],
        "execution_reference": _optional_binding_value(execution_binding, "execution_reference"),
        "execution_hash": _optional_binding_value(execution_binding, "execution_hash"),
        "execution_bound": execution_binding is not None,
        "execution_lineage_continuous": execution_binding is None
        or all(execution_binding["execution_lineage_checks"].values()),
        "worker_identity_continuous": evidence["lineage_checks"]["worker_identity_continuity"],
        "invocation_lineage_continuous": evidence["lineage_checks"]["invocation_lineage"],
        "dispatch_lineage_continuous": evidence["lineage_checks"]["dispatch_lineage"],
        "assignment_lineage_continuous": evidence["lineage_checks"]["assignment_lineage"],
        "authorization_lineage_continuous": evidence["lineage_checks"]["authorization_lineage"],
        "execution_packet_lineage_continuous": evidence["lineage_checks"]["execution_packet_lineage"],
        "replay_continuous": evidence["lineage_checks"]["replay_continuity"],
        "authority_continuous": evidence["lineage_checks"]["authority_continuity"],
        "chain_continuous": evidence["lineage_checks"]["chain_continuity"],
        "output_within_allowed_scope": set(worker_output["produced_outputs"]).issubset(set(invocation["allowed_outputs"])),
        "forbidden_operations_absent": not set(worker_output["operations"]).intersection(invocation["forbidden_operations"]),
        "worker_scope_bound": worker_output["worker_id"] == invocation["worker_id"],
        "packet_scope_bound": worker_output["execution_packet_reference"] == invocation["execution_packet_reference"],
        "classification_status": "WORKER_RESULT_CAPTURE_SCOPE_CLASSIFIED",
        "classified_at": _require_string(captured_at, "captured_at"),
        "replay_visible": True,
        **_post_capture_boundary_flags(execution_bound=execution_binding is not None),
    }
    checks = (
        artifact["execution_lineage_continuous"],
        artifact["worker_identity_continuous"],
        artifact["invocation_lineage_continuous"],
        artifact["dispatch_lineage_continuous"],
        artifact["assignment_lineage_continuous"],
        artifact["authorization_lineage_continuous"],
        artifact["execution_packet_lineage_continuous"],
        artifact["replay_continuous"],
        artifact["authority_continuous"],
        artifact["chain_continuous"],
        artifact["output_within_allowed_scope"],
        artifact["forbidden_operations_absent"],
        artifact["worker_scope_bound"],
        artifact["packet_scope_bound"],
    )
    if not all(checks):
        raise FailClosedRuntimeError("worker result capture failed closed: capture eligibility invalid")
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _result_capture_artifact(
    *,
    worker_result_capture_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    invocation: dict[str, Any],
    execution_binding: dict[str, Any] | None,
    worker_output: dict[str, Any],
    captured_by: str,
    captured_at: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_RESULT_CAPTURE_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_RESULT_CAPTURE_RUNTIME_VERSION,
        "worker_result_capture_id": _require_string(worker_result_capture_id, "worker_result_capture_id"),
        "result_capture_status": WORKER_RESULT_CAPTURED,
        "result_capture_evidence_reference": evidence["result_capture_evidence_id"],
        "result_capture_evidence_hash": evidence["artifact_hash"],
        "result_capture_classification_reference": classification["result_capture_classification_id"],
        "result_capture_classification_hash": classification["artifact_hash"],
        "worker_invocation_reference": invocation["worker_invocation_id"],
        "worker_invocation_hash": invocation["artifact_hash"],
        "execution_reference": _optional_binding_value(execution_binding, "execution_reference"),
        "execution_hash": _optional_binding_value(execution_binding, "execution_hash"),
        "execution_replay_hash": _optional_binding_value(execution_binding, "execution_replay_hash"),
        "execution_replay_reference": _optional_binding_value(execution_binding, "execution_replay_reference"),
        "execution_status": _optional_binding_value(execution_binding, "execution_status"),
        "worker_dispatch_reference": invocation["worker_dispatch_reference"],
        "worker_dispatch_hash": invocation["worker_dispatch_hash"],
        "worker_assignment_reference": invocation["worker_assignment_reference"],
        "worker_assignment_hash": invocation["worker_assignment_hash"],
        "worker_invocation_request_reference": invocation["worker_invocation_request_reference"],
        "worker_invocation_request_hash": invocation["worker_invocation_request_hash"],
        "authorization_reference": invocation["authorization_reference"],
        "authorization_hash": invocation["authorization_hash"],
        "execution_packet_reference": invocation["execution_packet_reference"],
        "execution_packet_hash": invocation["execution_packet_hash"],
        "worker_id": invocation["worker_id"],
        "worker_hash": invocation["worker_hash"],
        "worker_family": invocation["worker_family"],
        "worker_role": invocation["worker_role"],
        "allowed_outputs": deepcopy(invocation["allowed_outputs"]),
        "forbidden_operations": deepcopy(invocation["forbidden_operations"]),
        "validation_requirements": deepcopy(invocation["validation_requirements"]),
        "produced_outputs": deepcopy(worker_output["produced_outputs"]),
        "operations": deepcopy(worker_output["operations"]),
        "worker_output_reference": worker_output["worker_output_id"],
        "worker_output_hash": worker_output["artifact_hash"],
        "worker_output_payload_hash": replay_hash(worker_output["payload"]),
        "captured_by": _require_string(captured_by, "captured_by"),
        "captured_at": _require_string(captured_at, "captured_at"),
        "chain_id": invocation["chain_id"],
        "replay_reference": invocation["replay_reference"],
        "replay_visible": True,
        **_post_capture_boundary_flags(execution_bound=execution_binding is not None),
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    _validate_result_capture_artifact(artifact)
    return artifact


def _result_artifact(
    *,
    worker_result_capture_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    capture_artifact: dict[str, Any],
    captured_at: str,
    status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_RESULT_CAPTURE_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_RESULT_CAPTURE_RUNTIME_VERSION,
        "result_capture_result_id": f"{_require_string(worker_result_capture_id, 'worker_result_capture_id')}:RESULT",
        "result_capture_status": status,
        "result_capture_evidence_reference": evidence["result_capture_evidence_id"],
        "result_capture_evidence_hash": evidence["artifact_hash"],
        "result_capture_classification_reference": classification["result_capture_classification_id"],
        "result_capture_classification_hash": classification["artifact_hash"],
        "worker_result_capture_reference": capture_artifact["worker_result_capture_id"],
        "worker_result_capture_hash": capture_artifact["artifact_hash"],
        "worker_invocation_reference": capture_artifact["worker_invocation_reference"],
        "worker_invocation_hash": capture_artifact["worker_invocation_hash"],
        "execution_reference": capture_artifact.get("execution_reference"),
        "execution_hash": capture_artifact.get("execution_hash"),
        "execution_replay_reference": capture_artifact.get("execution_replay_reference"),
        "worker_dispatch_reference": capture_artifact["worker_dispatch_reference"],
        "worker_reference": capture_artifact["worker_id"],
        "worker_hash": capture_artifact["worker_hash"],
        "chain_id": capture_artifact["chain_id"],
        "completed_at": _require_string(captured_at, "captured_at"),
        "replay_visible": True,
        **_post_capture_boundary_flags(execution_bound=bool(capture_artifact.get("execution_reference"))),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_result(
    *,
    worker_result_capture_id: str,
    worker_invocation_reference: str | None,
    worker_invocation_replay_reference: str,
    captured_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": WORKER_RESULT_CAPTURE_RESULT_ARTIFACT_V1,
        "runtime_version": AIGOL_WORKER_RESULT_CAPTURE_RUNTIME_VERSION,
        "result_capture_result_id": f"{worker_result_capture_id}:RESULT",
        "result_capture_status": FAILED_CLOSED,
        "result_capture_evidence_reference": None,
        "result_capture_evidence_hash": None,
        "result_capture_classification_reference": None,
        "result_capture_classification_hash": None,
        "worker_result_capture_reference": None,
        "worker_result_capture_hash": None,
        "worker_invocation_reference": worker_invocation_reference,
        "worker_invocation_hash": None,
        "worker_invocation_replay_reference": worker_invocation_replay_reference,
        "worker_dispatch_reference": None,
        "worker_reference": None,
        "worker_hash": None,
        "chain_id": None,
        "completed_at": captured_at,
        "replay_visible": True,
        **_pre_capture_boundary_flags(),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    evidence: dict[str, Any] | None,
    classification: dict[str, Any] | None,
    capture_artifact: dict[str, Any] | None,
    result: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = deepcopy(result)
    capture.update(
        {
            "result_capture_evidence_artifact": deepcopy(evidence),
            "result_capture_classification_artifact": deepcopy(classification),
            "worker_result_capture_artifact": deepcopy(capture_artifact),
            "result_capture_result_artifact": deepcopy(result),
            "worker_result_capture_reference": capture_artifact.get("worker_result_capture_id")
            if capture_artifact
            else None,
            "worker_invocation_reference": capture_artifact.get("worker_invocation_reference")
            if capture_artifact
            else None,
            "execution_reference": capture_artifact.get("execution_reference") if capture_artifact else None,
            "execution_hash": capture_artifact.get("execution_hash") if capture_artifact else None,
            "execution_replay_reference": capture_artifact.get("execution_replay_reference")
            if capture_artifact
            else None,
            "worker_dispatch_reference": capture_artifact.get("worker_dispatch_reference")
            if capture_artifact
            else None,
            "worker_id": capture_artifact.get("worker_id") if capture_artifact else None,
            "worker_family": capture_artifact.get("worker_family") if capture_artifact else None,
            "worker_role": capture_artifact.get("worker_role") if capture_artifact else None,
            "worker_result_capture_replay_reference": str(replay_path),
            "fail_closed": result["result_capture_status"] == FAILED_CLOSED,
        }
    )
    capture["worker_result_capture_capture_hash"] = replay_hash(capture)
    return capture


def _invocation_for_execution(root: Path, execution: dict[str, Any]) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    for path in sorted(root.glob("TURN-*/worker_invocation")):
        try:
            reconstructed = reconstruct_worker_invocation_replay(path)
            evidence_wrapper = load_json(path / "000_invocation_evidence_recorded.json")
            invocation_wrapper = load_json(path / "002_invocation_artifact_recorded.json")
            _verify_wrapper_hash(evidence_wrapper)
            _verify_wrapper_hash(invocation_wrapper)
            evidence = evidence_wrapper.get("artifact")
            invocation = invocation_wrapper.get("artifact")
            if not isinstance(evidence, dict) or not isinstance(invocation, dict):
                continue
            _verify_artifact_hash(evidence, "worker invocation evidence artifact")
            _verify_artifact_hash(invocation, "worker invocation artifact")
        except FailClosedRuntimeError:
            continue
        if reconstructed.get("invocation_status") != WORKER_INVOKED:
            continue
        if invocation.get("worker_invocation_id") != execution.get("worker_invocation_reference"):
            continue
        if invocation.get("artifact_hash") != execution.get("worker_invocation_hash"):
            continue
        return path, deepcopy(invocation), deepcopy(evidence)
    raise FailClosedRuntimeError("worker result capture failed closed: matching invocation not found")


def _execution_already_result_captured(
    session_root: Path,
    *,
    execution_reference: str,
    execution_hash: str,
) -> bool:
    for path in sorted(session_root.glob("TURN-*/worker_result_capture")):
        try:
            reconstructed = reconstruct_worker_result_capture_replay(path)
            wrapper = load_json(path / "002_result_capture_artifact_recorded.json")
            _verify_wrapper_hash(wrapper)
            capture_artifact = wrapper.get("artifact")
            if not isinstance(capture_artifact, dict):
                continue
            _verify_artifact_hash(capture_artifact, "worker result capture artifact")
        except FailClosedRuntimeError:
            continue
        if reconstructed.get("result_capture_status") != WORKER_RESULT_CAPTURED:
            continue
        if capture_artifact.get("execution_reference") == execution_reference:
            return True
        if capture_artifact.get("execution_hash") == execution_hash:
            return True
    return False


def _validate_result_capture_artifact(capture_artifact: dict[str, Any]) -> None:
    if capture_artifact.get("artifact_type") != WORKER_RESULT_CAPTURE_ARTIFACT_V1:
        raise FailClosedRuntimeError("worker result capture failed closed: invalid result capture artifact")
    if capture_artifact.get("result_capture_status") != WORKER_RESULT_CAPTURED:
        raise FailClosedRuntimeError("worker result capture failed closed: invalid result capture status")
    for field, expected in _post_capture_boundary_flags(
        execution_bound=bool(capture_artifact.get("execution_reference"))
    ).items():
        if capture_artifact.get(field) is not expected:
            raise FailClosedRuntimeError("worker result capture failed closed: authority violation")
    if not set(capture_artifact.get("produced_outputs", [])).issubset(set(capture_artifact.get("allowed_outputs", []))):
        raise FailClosedRuntimeError("worker result capture failed closed: output outside allowed scope")
    if set(capture_artifact.get("operations", [])).intersection(capture_artifact.get("forbidden_operations", [])):
        raise FailClosedRuntimeError("worker result capture failed closed: forbidden operation detected")
    if not _string_list(capture_artifact.get("validation_requirements")):
        raise FailClosedRuntimeError("worker result capture failed closed: validation requirements missing")
    for field in (
        "worker_result_capture_id",
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
        "worker_output_reference",
        "worker_output_hash",
        "chain_id",
        "captured_by",
        "captured_at",
    ):
        _require_string(capture_artifact.get(field), field)
    if capture_artifact.get("execution_reference") is not None:
        for field in (
            "execution_reference",
            "execution_hash",
            "execution_replay_hash",
            "execution_status",
        ):
            _require_string(capture_artifact.get(field), field)
        if capture_artifact.get("execution_status") != EXECUTING:
            raise FailClosedRuntimeError("worker result capture failed closed: invalid execution state")


def _invocation_authority_continuity(invocation: dict[str, Any]) -> bool:
    return (
        invocation.get("approval_created") is False
        and invocation.get("worker_assigned") is True
        and invocation.get("worker_dispatched") is True
        and invocation.get("dispatch_requested") is True
        and invocation.get("worker_invoked") is True
        and invocation.get("execution_started") is False
        and invocation.get("result_created") is False
        and invocation.get("result_validated") is False
        and invocation.get("post_execution_replay_reviewed") is False
        and invocation.get("terminated") is False
        and invocation.get("governance_mutated") is False
        and invocation.get("replay_mutated") is False
    )


def _pre_capture_boundary_flags() -> dict[str, bool]:
    return {
        "approval_created": False,
        "worker_assigned": True,
        "worker_dispatched": True,
        "dispatch_requested": True,
        "worker_invoked": True,
        "execution_started": False,
        "result_created": False,
        "result_validated": False,
        "post_execution_replay_reviewed": False,
        "terminated": False,
        "governance_mutated": False,
        "replay_mutated": False,
    }


def _post_capture_boundary_flags(*, execution_bound: bool = False) -> dict[str, bool]:
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


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("worker result capture replay ordering mismatch")
    _verify_artifact_hash(artifact, "worker result capture artifact")
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
        raise FailClosedRuntimeError("worker result capture replay hash is required")
    candidate = deepcopy(wrapper)
    actual = candidate.pop("replay_hash")
    if actual != replay_hash(candidate):
        raise FailClosedRuntimeError("worker result capture replay hash mismatch")


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def _optional_binding_value(binding: dict[str, Any] | None, field: str) -> Any:
    if binding is None:
        return None
    return binding.get(field)


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"worker result capture failed closed: {field} is required")
    return value


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return f"worker result capture failed closed: {exc}"
