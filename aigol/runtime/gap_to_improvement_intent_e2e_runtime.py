"""End-to-end replay gap to improvement intent proof runtime."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.replay_gap_detection_runtime import GAPS_DETECTED, detect_replay_gaps
from aigol.runtime.replay_to_improvement_intent_runtime import (
    IMPROVEMENT_INTENT_CREATED,
    create_improvement_intent_from_replay_gap,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_GAP_TO_IMPROVEMENT_INTENT_E2E_VERSION = "AIGOL_GAP_TO_IMPROVEMENT_INTENT_E2E_V1"
EXECUTION_REPLAY_EVIDENCE_ARTIFACT_V1 = "EXECUTION_REPLAY_EVIDENCE_ARTIFACT_V1"
HUMAN_REVIEW_GATE_ARTIFACT_V1 = "HUMAN_REVIEW_GATE_ARTIFACT_V1"
GAP_TO_IMPROVEMENT_INTENT_E2E_ARTIFACT_V1 = "GAP_TO_IMPROVEMENT_INTENT_E2E_ARTIFACT_V1"
GAP_TO_IMPROVEMENT_INTENT_E2E_PASSED = "GAP_TO_IMPROVEMENT_INTENT_E2E_PASSED"
FAILED_CLOSED = "FAILED_CLOSED"
PENDING_HUMAN_REVIEW = "PENDING_HUMAN_REVIEW"

GOVERNANCE_GUARDS = {
    "self_modification_prevented": True,
    "repair_prevented": True,
    "provider_driven_changes_prevented": True,
    "worker_execution_prevented": True,
    "ppp_invoked": False,
    "proposal_created": False,
    "approval_granted": False,
    "implementation_authorized": False,
    "execution_requested": False,
    "dispatch_requested": False,
    "worker_invoked": False,
    "provider_invoked": False,
}


def run_gap_to_improvement_intent_e2e(
    *,
    run_id: str,
    execution_replay_artifacts: list[dict[str, Any]],
    canonical_chain_id: str,
    created_at: str,
    replay_dir: str | Path,
    domain_id: str = "AIGOL_CORE",
    affected_layer: str = "AIGOL_CORE",
    affected_worker_family: str | None = None,
) -> dict[str, Any]:
    """Prove Execution -> Replay -> Gap -> Improvement Intent -> Human Review."""

    replay_path = Path(replay_dir)
    _ensure_replay_available(replay_path)
    chain_id = _require_string(canonical_chain_id, "canonical_chain_id")
    execution_replay = _execution_replay_evidence_artifact(
        run_id=run_id,
        execution_replay_artifacts=execution_replay_artifacts,
        canonical_chain_id=chain_id,
        created_at=created_at,
    )
    write_json_immutable(
        replay_path / "000_execution_replay_evidence.json",
        _wrapper(0, "execution_replay_evidence", execution_replay),
    )

    gap = detect_replay_gaps(
        detection_id=f"{run_id}:REPLAY-GAP-DETECTION",
        replay_artifacts=execution_replay["normalized_replay_artifacts"],
        created_at=created_at,
        replay_dir=replay_path / "gap_detection",
        domain_id=domain_id,
    )
    intent = create_improvement_intent_from_replay_gap(
        improvement_intent_id=f"{run_id}:IMPROVEMENT-INTENT",
        gap_detection_artifact=gap["gap_detection_artifact"],
        gap_classification_artifact=gap["gap_classification_artifact"],
        gap_evidence_artifact=gap["gap_evidence_artifact"],
        canonical_chain_id=chain_id,
        created_at=created_at,
        replay_dir=replay_path / "improvement_intent",
        affected_layer=affected_layer,
        affected_worker_family=affected_worker_family,
    )
    human_review_gate = _human_review_gate_artifact(
        run_id=run_id,
        improvement_intent_artifact=intent["improvement_intent_artifact"],
        gap_detection_artifact=gap["gap_detection_artifact"],
        canonical_chain_id=chain_id,
        created_at=created_at,
        replay_reference=str(replay_path / "human_review_gate"),
    )
    write_json_immutable(
        replay_path / "001_human_review_gate.json",
        _wrapper(1, "human_review_gate", human_review_gate),
    )
    e2e = _e2e_artifact(
        run_id=run_id,
        execution_replay=execution_replay,
        gap=gap,
        intent=intent,
        human_review_gate=human_review_gate,
        created_at=created_at,
        replay_reference=str(replay_path),
    )
    write_json_immutable(
        replay_path / "002_gap_to_improvement_intent_e2e.json",
        _wrapper(2, "gap_to_improvement_intent_e2e", e2e),
    )
    return {
        "runtime_version": AIGOL_GAP_TO_IMPROVEMENT_INTENT_E2E_VERSION,
        "run_id": run_id,
        "execution_replay_evidence_artifact": execution_replay,
        "gap_detection_capture": gap,
        "improvement_intent_capture": intent,
        "human_review_gate_artifact": human_review_gate,
        "gap_to_improvement_intent_e2e_artifact": e2e,
        "replay_reference": str(replay_path),
        "replay_lineage_preserved": e2e["replay_lineage_preserved"],
        "human_approval_required": e2e["human_approval_required"],
        "self_modification_prevented": e2e["self_modification_prevented"],
        "repair_prevented": e2e["repair_prevented"],
        "ready_for_ppp_integration": e2e["ready_for_ppp_integration"],
    }


def reconstruct_gap_to_improvement_intent_e2e(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct and verify the E2E proof replay."""

    replay_path = Path(replay_dir)
    wrappers = [
        load_json(replay_path / "000_execution_replay_evidence.json"),
        load_json(replay_path / "001_human_review_gate.json"),
        load_json(replay_path / "002_gap_to_improvement_intent_e2e.json"),
    ]
    for index, wrapper in enumerate(wrappers):
        if wrapper.get("replay_index") != index:
            raise FailClosedRuntimeError("gap to improvement intent e2e replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("gap to improvement intent e2e artifact must be a JSON object")
        _verify_artifact_hash(artifact)
    execution_replay = wrappers[0]["artifact"]
    human_review_gate = wrappers[1]["artifact"]
    e2e = wrappers[2]["artifact"]
    if e2e["execution_replay_hash"] != execution_replay["artifact_hash"]:
        raise FailClosedRuntimeError("gap to improvement intent e2e execution replay hash mismatch")
    if e2e["human_review_gate_hash"] != human_review_gate["artifact_hash"]:
        raise FailClosedRuntimeError("gap to improvement intent e2e human review hash mismatch")
    return {
        "e2e_status": e2e["e2e_status"],
        "improvement_intent_artifact_generated": e2e["improvement_intent_artifact_generated"],
        "replay_lineage_preserved": e2e["replay_lineage_preserved"],
        "human_approval_required": e2e["human_approval_required"],
        "self_modification_prevented": e2e["self_modification_prevented"],
        "repair_prevented": e2e["repair_prevented"],
        "ready_for_ppp_integration": e2e["ready_for_ppp_integration"],
        "replay_hash": replay_hash(wrappers),
    }


def _execution_replay_evidence_artifact(
    *,
    run_id: str,
    execution_replay_artifacts: list[dict[str, Any]],
    canonical_chain_id: str,
    created_at: str,
) -> dict[str, Any]:
    normalized = [_normalize_execution_replay_item(item, canonical_chain_id) for item in execution_replay_artifacts]
    if not normalized:
        raise FailClosedRuntimeError("gap to improvement intent e2e failed closed: execution replay required")
    artifact = {
        "artifact_type": EXECUTION_REPLAY_EVIDENCE_ARTIFACT_V1,
        "runtime_version": AIGOL_GAP_TO_IMPROVEMENT_INTENT_E2E_VERSION,
        "run_id": _require_string(run_id, "run_id"),
        "canonical_chain_id": canonical_chain_id,
        "normalized_replay_artifacts": normalized,
        "execution_replay_count": len(normalized),
        "execution_performed_by_runtime": False,
        "worker_execution_performed": False,
        "provider_change_performed": False,
        "repair_performed": False,
        "self_modification_performed": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _normalize_execution_replay_item(item: dict[str, Any], canonical_chain_id: str) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise FailClosedRuntimeError("gap to improvement intent e2e failed closed: invalid execution replay item")
    payload = item.get("source_replay_payload")
    if not isinstance(payload, dict):
        raise FailClosedRuntimeError("gap to improvement intent e2e failed closed: replay payload required")
    payload_hash = item.get("source_replay_hash") or replay_hash(payload)
    if payload_hash != replay_hash(payload):
        raise FailClosedRuntimeError("gap to improvement intent e2e failed closed: replay hash mismatch")
    item_chain = item.get("canonical_chain_id", canonical_chain_id)
    if item_chain != canonical_chain_id:
        raise FailClosedRuntimeError("gap to improvement intent e2e failed closed: chain continuity failed")
    return {
        "evidence_id": _require_string(item.get("evidence_id"), "evidence_id"),
        "evidence_type": _require_string(item.get("evidence_type"), "evidence_type"),
        "source_replay_reference": _require_string(item.get("source_replay_reference"), "source_replay_reference"),
        "source_replay_payload": deepcopy(payload),
        "source_replay_hash": payload_hash,
        "canonical_chain_id": canonical_chain_id,
        "observed_condition": _require_string(item.get("observed_condition"), "observed_condition"),
        "expected_condition": _require_string(item.get("expected_condition"), "expected_condition"),
        "confidence": str(item.get("confidence") or "DETERMINISTIC"),
        **{key: deepcopy(value) for key, value in item.items() if key not in _NORMALIZED_ITEM_KEYS},
    }


def _human_review_gate_artifact(
    *,
    run_id: str,
    improvement_intent_artifact: dict[str, Any],
    gap_detection_artifact: dict[str, Any],
    canonical_chain_id: str,
    created_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    _verify_artifact_hash(improvement_intent_artifact)
    if improvement_intent_artifact.get("intent_status") != IMPROVEMENT_INTENT_CREATED:
        raise FailClosedRuntimeError("gap to improvement intent e2e failed closed: improvement intent required")
    artifact = {
        "artifact_type": HUMAN_REVIEW_GATE_ARTIFACT_V1,
        "runtime_version": AIGOL_GAP_TO_IMPROVEMENT_INTENT_E2E_VERSION,
        "human_review_gate_id": f"{_require_string(run_id, 'run_id')}:HUMAN-REVIEW-GATE",
        "canonical_chain_id": canonical_chain_id,
        "gap_detection_reference": gap_detection_artifact["detection_id"],
        "gap_detection_hash": gap_detection_artifact["artifact_hash"],
        "improvement_intent_reference": improvement_intent_artifact["improvement_intent_id"],
        "improvement_intent_hash": improvement_intent_artifact["artifact_hash"],
        "review_status": PENDING_HUMAN_REVIEW,
        "human_review_required": True,
        "approval_required": True,
        "approval_granted": False,
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "repair_invoked": False,
        "self_modification_performed": False,
        "implementation_authorized": False,
        "allowed_next_step": "HUMAN_REVIEW",
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _e2e_artifact(
    *,
    run_id: str,
    execution_replay: dict[str, Any],
    gap: dict[str, Any],
    intent: dict[str, Any],
    human_review_gate: dict[str, Any],
    created_at: str,
    replay_reference: str,
) -> dict[str, Any]:
    gap_detection = gap["gap_detection_artifact"]
    improvement_intent = intent["improvement_intent_artifact"]
    passed = (
        gap_detection["detection_status"] == GAPS_DETECTED
        and improvement_intent["intent_status"] == IMPROVEMENT_INTENT_CREATED
        and human_review_gate["review_status"] == PENDING_HUMAN_REVIEW
        and _guards_preserved(improvement_intent, human_review_gate)
    )
    artifact = {
        "artifact_type": GAP_TO_IMPROVEMENT_INTENT_E2E_ARTIFACT_V1,
        "runtime_version": AIGOL_GAP_TO_IMPROVEMENT_INTENT_E2E_VERSION,
        "run_id": _require_string(run_id, "run_id"),
        "e2e_status": GAP_TO_IMPROVEMENT_INTENT_E2E_PASSED if passed else FAILED_CLOSED,
        "execution_replay_reference": execution_replay["run_id"],
        "execution_replay_hash": execution_replay["artifact_hash"],
        "gap_detection_reference": gap_detection["detection_id"],
        "gap_detection_hash": gap_detection["artifact_hash"],
        "improvement_intent_reference": improvement_intent["improvement_intent_id"],
        "improvement_intent_hash": improvement_intent["artifact_hash"],
        "human_review_gate_reference": human_review_gate["human_review_gate_id"],
        "human_review_gate_hash": human_review_gate["artifact_hash"],
        "improvement_intent_artifact_generated": improvement_intent["intent_status"] == IMPROVEMENT_INTENT_CREATED,
        "replay_lineage_preserved": _lineage_preserved(gap, intent, human_review_gate),
        "human_approval_required": human_review_gate["approval_required"] is True,
        "self_modification_prevented": improvement_intent["self_modification_authority"] is False
        and human_review_gate["self_modification_performed"] is False,
        "repair_prevented": human_review_gate["repair_invoked"] is False,
        "ready_for_ppp_integration": improvement_intent["ppp_eligible"] is True and human_review_gate["approval_granted"] is False,
        "governance_guards": deepcopy(GOVERNANCE_GUARDS),
        "created_at": _require_string(created_at, "created_at"),
        "replay_reference": _require_string(replay_reference, "replay_reference"),
        "replay_visible": True,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _lineage_preserved(gap: dict[str, Any], intent: dict[str, Any], human_review_gate: dict[str, Any]) -> bool:
    gap_detection = gap["gap_detection_artifact"]
    improvement_intent = intent["improvement_intent_artifact"]
    return (
        improvement_intent["gap_reference"] == gap_detection["detection_id"]
        and improvement_intent["gap_hash"] == gap_detection["artifact_hash"]
        and human_review_gate["improvement_intent_reference"] == improvement_intent["improvement_intent_id"]
        and human_review_gate["improvement_intent_hash"] == improvement_intent["artifact_hash"]
    )


def _guards_preserved(improvement_intent: dict[str, Any], human_review_gate: dict[str, Any]) -> bool:
    return (
        improvement_intent["proposal_created"] is False
        and improvement_intent["ppp_invoked"] is False
        and improvement_intent["provider_invoked"] is False
        and improvement_intent["worker_invoked"] is False
        and improvement_intent["execution_requested"] is False
        and improvement_intent["self_modification_authority"] is False
        and human_review_gate["approval_granted"] is False
        and human_review_gate["repair_invoked"] is False
        and human_review_gate["self_modification_performed"] is False
    )


def _wrapper(index: int, step: str, artifact: dict[str, Any]) -> dict[str, Any]:
    wrapper = {
        "event_type": step.upper(),
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    return wrapper


def _ensure_replay_available(replay_path: Path) -> None:
    for name in (
        "000_execution_replay_evidence.json",
        "001_human_review_gate.json",
        "002_gap_to_improvement_intent_e2e.json",
    ):
        if (replay_path / name).exists():
            raise FailClosedRuntimeError("gap to improvement intent e2e failed closed: replay already exists")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"gap to improvement intent e2e failed closed: {field_name} is required")
    return value.strip()


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("gap to improvement intent e2e artifact hash is required")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("gap to improvement intent e2e artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("gap to improvement intent e2e replay hash is required")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("gap to improvement intent e2e replay hash mismatch")


_NORMALIZED_ITEM_KEYS = {
    "evidence_id",
    "evidence_type",
    "source_replay_reference",
    "source_replay_payload",
    "source_replay_hash",
    "canonical_chain_id",
    "observed_condition",
    "expected_condition",
    "confidence",
}
