"""Deterministic replay gap detection runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_REPLAY_GAP_DETECTION_RUNTIME_VERSION = "AIGOL_REPLAY_GAP_DETECTION_RUNTIME_V1"
GAP_DETECTION_ARTIFACT_V1 = "GAP_DETECTION_ARTIFACT_V1"
GAP_CLASSIFICATION_ARTIFACT_V1 = "GAP_CLASSIFICATION_ARTIFACT_V1"
GAP_EVIDENCE_ARTIFACT_V1 = "GAP_EVIDENCE_ARTIFACT_V1"

GAPS_DETECTED = "GAPS_DETECTED"
NO_GAPS_DETECTED = "NO_GAPS_DETECTED"
FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "gap_evidence_recorded",
    "gap_classification_recorded",
    "gap_detection_recorded",
    "gap_detection_returned",
)

SUPPORTED_DOMAINS = {"TRADING", "MARKETING", "HEALTHCARE", "HR", "AIGOL_CORE"}

DEFAULT_THRESHOLDS = {
    "performance_gap_ratio": 0.1,
    "repeated_failure_count": 3,
    "domain_effectiveness_gap_ratio": 0.15,
}

GAP_CATEGORIES = {
    "PERFORMANCE_METRIC": "PERFORMANCE_GAP",
    "POLICY_RESULT": "POLICY_GAP",
    "VALIDATION_RESULT": "VALIDATION_GAP",
    "REPLAY_INTEGRITY": "REPLAY_INTEGRITY_GAP",
    "DOMAIN_EFFECTIVENESS": "DOMAIN_EFFECTIVENESS_GAP",
    "FAILURE_PATTERN": "REPEATED_FAILURE_PATTERN",
}


def detect_replay_gaps(
    *,
    detection_id: str,
    replay_artifacts: list[dict[str, Any]],
    created_at: str,
    replay_dir: str | Path,
    domain_id: str = "AIGOL_CORE",
    thresholds: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Detect replay-visible gaps without creating proposals, invoking PPP, or executing work."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        active_thresholds = _thresholds(thresholds)
        domain = _normalize_domain(domain_id)
        evidence = _evidence_artifact(
            detection_id=detection_id,
            replay_artifacts=replay_artifacts,
            domain_id=domain,
            thresholds=active_thresholds,
            created_at=created_at,
            evidence_status="GAP_EVIDENCE_CAPTURED",
            failure_reason=None,
        )
        classifications = _classify_evidence(deepcopy(evidence["evidence_items"]), active_thresholds)
        classification = _classification_artifact(
            detection_id=detection_id,
            evidence=evidence,
            classifications=classifications,
            created_at=created_at,
            classification_status="GAP_CLASSIFICATION_COMPLETED",
            failure_reason=None,
        )
        detection = _detection_artifact(
            detection_id=detection_id,
            evidence=evidence,
            classification=classification,
            created_at=created_at,
            detection_status=GAPS_DETECTED if classifications else NO_GAPS_DETECTED,
            failure_reason=None,
        )
        returned = _returned_artifact(detection)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], evidence)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], classification)
        _persist_step(replay_path, 2, REPLAY_STEPS[2], detection)
        _persist_step(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(evidence, classification, detection, returned, replay_path)
    except Exception as exc:
        evidence = _failed_evidence_artifact(
            detection_id=detection_id,
            replay_artifacts=replay_artifacts,
            domain_id=domain_id,
            thresholds=thresholds,
            created_at=created_at,
            failure_reason=_failure_reason(exc),
        )
        classification = _failed_classification_artifact(detection_id=detection_id, evidence=evidence, created_at=created_at)
        detection = _failed_detection_artifact(
            detection_id=detection_id,
            evidence=evidence,
            classification=classification,
            created_at=created_at,
            failure_reason=evidence["failure_reason"],
        )
        returned = _returned_artifact(detection)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], evidence)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], classification)
        _persist_failure_if_possible(replay_path, 2, REPLAY_STEPS[2], detection)
        _persist_failure_if_possible(replay_path, 3, REPLAY_STEPS[3], returned)
        return _capture(evidence, classification, detection, returned, replay_path)


def reconstruct_replay_gap_detection_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct replay gap detection evidence."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("replay gap detection replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("replay gap detection replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "replay gap detection artifact")
        wrappers.append(wrapper)
    evidence = wrappers[0]["artifact"]
    classification = wrappers[1]["artifact"]
    detection = wrappers[2]["artifact"]
    returned = wrappers[3]["artifact"]
    if classification.get("evidence_reference") != evidence["evidence_id"]:
        raise FailClosedRuntimeError("replay gap detection evidence reference mismatch")
    if classification.get("evidence_hash") != evidence["artifact_hash"]:
        raise FailClosedRuntimeError("replay gap detection evidence hash mismatch")
    if detection.get("classification_reference") != classification["classification_id"]:
        raise FailClosedRuntimeError("replay gap detection classification reference mismatch")
    if detection.get("classification_hash") != classification["artifact_hash"]:
        raise FailClosedRuntimeError("replay gap detection classification hash mismatch")
    if returned.get("detection_reference") != detection["detection_id"]:
        raise FailClosedRuntimeError("replay gap detection returned reference mismatch")
    if returned.get("detection_hash") != detection["artifact_hash"]:
        raise FailClosedRuntimeError("replay gap detection returned hash mismatch")
    return {
        "detection_id": detection["detection_id"],
        "detection_status": detection["detection_status"],
        "domain_id": detection["domain_id"],
        "gap_count": detection["gap_count"],
        "gap_categories": deepcopy(detection["gap_categories"]),
        "confidence": detection["confidence"],
        "human_review_required": detection["human_review_required"],
        "improvement_intent_allowed": detection["improvement_intent_allowed"],
        "failure_reason": detection["failure_reason"],
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _evidence_artifact(
    *,
    detection_id: str,
    replay_artifacts: list[dict[str, Any]],
    domain_id: str,
    thresholds: dict[str, Any],
    created_at: str,
    evidence_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    evidence_items = _normalize_evidence(replay_artifacts, thresholds)
    artifact = {
        "artifact_type": GAP_EVIDENCE_ARTIFACT_V1,
        "runtime_version": AIGOL_REPLAY_GAP_DETECTION_RUNTIME_VERSION,
        "evidence_id": f"{_require_string(detection_id, 'detection_id')}:GAP-EVIDENCE",
        "detection_reference": detection_id,
        "domain_id": _normalize_domain(domain_id),
        "supported_domains": sorted(SUPPORTED_DOMAINS),
        "thresholds": deepcopy(thresholds),
        "evidence_items": evidence_items,
        "evidence_count": len(evidence_items),
        "evidence_status": evidence_status,
        "false_positive_controls": {
            "evidence_references_required": True,
            "threshold_checks_required": True,
            "replay_references_required": True,
            "confidence_classification_required": True,
        },
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _classification_artifact(
    *,
    detection_id: str,
    evidence: dict[str, Any],
    classifications: list[dict[str, Any]],
    created_at: str,
    classification_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    confidence = _overall_confidence(classifications)
    artifact = {
        "artifact_type": GAP_CLASSIFICATION_ARTIFACT_V1,
        "runtime_version": AIGOL_REPLAY_GAP_DETECTION_RUNTIME_VERSION,
        "classification_id": f"{_require_string(detection_id, 'detection_id')}:GAP-CLASSIFICATION",
        "detection_reference": detection_id,
        "evidence_reference": evidence["evidence_id"],
        "evidence_hash": evidence["artifact_hash"],
        "domain_id": evidence["domain_id"],
        "classification_status": classification_status,
        "gap_classifications": deepcopy(classifications),
        "gap_count": len(classifications),
        "gap_categories": sorted({item["gap_category"] for item in classifications}),
        "confidence": confidence,
        "human_review_required": any(item["human_review_required"] for item in classifications),
        "improvement_intent_allowed": bool(classifications) and confidence in {"HIGH", "DETERMINISTIC"},
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _detection_artifact(
    *,
    detection_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    created_at: str,
    detection_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": GAP_DETECTION_ARTIFACT_V1,
        "runtime_version": AIGOL_REPLAY_GAP_DETECTION_RUNTIME_VERSION,
        "detection_id": _require_string(detection_id, "detection_id"),
        "detection_status": detection_status,
        "domain_id": evidence["domain_id"],
        "evidence_reference": evidence["evidence_id"],
        "evidence_hash": evidence["artifact_hash"],
        "classification_reference": classification["classification_id"],
        "classification_hash": classification["artifact_hash"],
        "gap_count": classification["gap_count"],
        "gap_categories": deepcopy(classification["gap_categories"]),
        "confidence": classification["confidence"],
        "human_review_required": classification["human_review_required"],
        "improvement_intent_allowed": classification["improvement_intent_allowed"],
        "proposal_created": False,
        "improvement_proposal_created": False,
        "improvement_intent_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "authorization_created": False,
        "governance_mutated": False,
        "replay_mutated": False,
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _classify_evidence(evidence_items: list[dict[str, Any]], thresholds: dict[str, Any]) -> list[dict[str, Any]]:
    classifications = []
    for item in evidence_items:
        category = _category_for(item, thresholds)
        if category is None:
            continue
        severity = _severity_for(category, item)
        classifications.append(
            {
                "gap_id": f"{item['evidence_id']}:GAP",
                "evidence_reference": item["evidence_id"],
                "source_replay_reference": item["source_replay_reference"],
                "source_replay_hash": item["source_replay_hash"],
                "gap_category": category,
                "observed_condition": item["observed_condition"],
                "expected_condition": item["expected_condition"],
                "severity": severity,
                "confidence": item["confidence"],
                "threshold_check": item["threshold_check"],
                "human_review_required": severity in {"HIGH", "CRITICAL"} or item["confidence"] != "DETERMINISTIC",
                "improvement_intent_allowed": item["confidence"] in {"HIGH", "DETERMINISTIC"},
            }
        )
    return classifications


def _category_for(item: dict[str, Any], thresholds: dict[str, Any]) -> str | None:
    evidence_type = item["evidence_type"]
    if evidence_type == "PERFORMANCE_METRIC":
        value = _require_number(item.get("observed_value"), "observed_value")
        expected = _require_number(item.get("expected_value"), "expected_value")
        ratio = abs(expected - value) / abs(expected) if expected else abs(value)
        item["threshold_check"] = {"threshold": thresholds["performance_gap_ratio"], "observed_gap_ratio": ratio}
        return "PERFORMANCE_GAP" if ratio >= thresholds["performance_gap_ratio"] else None
    if evidence_type == "POLICY_RESULT":
        status = _normalize_key(item.get("status"), "status")
        item["threshold_check"] = {"status": status}
        return "POLICY_GAP" if status in {"FAILED", "REJECTED", "VIOLATION"} else None
    if evidence_type == "VALIDATION_RESULT":
        status = _normalize_key(item.get("status"), "status")
        item["threshold_check"] = {"status": status}
        return "VALIDATION_GAP" if status in {"FAILED", "REJECTED", "INVALID"} else None
    if evidence_type == "REPLAY_INTEGRITY":
        status = _normalize_key(item.get("status"), "status")
        item["threshold_check"] = {"status": status}
        return "REPLAY_INTEGRITY_GAP" if status in {"BROKEN", "HASH_MISMATCH", "CHAIN_FAILURE"} else None
    if evidence_type == "DOMAIN_EFFECTIVENESS":
        value = _require_number(item.get("observed_value"), "observed_value")
        expected = _require_number(item.get("expected_value"), "expected_value")
        ratio = abs(expected - value) / abs(expected) if expected else abs(value)
        item["threshold_check"] = {
            "threshold": thresholds["domain_effectiveness_gap_ratio"],
            "observed_gap_ratio": ratio,
        }
        return "DOMAIN_EFFECTIVENESS_GAP" if ratio >= thresholds["domain_effectiveness_gap_ratio"] else None
    if evidence_type == "FAILURE_PATTERN":
        count = int(_require_number(item.get("failure_count"), "failure_count"))
        item["threshold_check"] = {"threshold": thresholds["repeated_failure_count"], "failure_count": count}
        return "REPEATED_FAILURE_PATTERN" if count >= thresholds["repeated_failure_count"] else None
    raise FailClosedRuntimeError("replay gap detection failed closed: classification ambiguous")


def _normalize_evidence(replay_artifacts: list[dict[str, Any]], thresholds: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(replay_artifacts, list) or not replay_artifacts:
        raise FailClosedRuntimeError("replay gap detection failed closed: evidence missing")
    normalized = []
    for index, item in enumerate(replay_artifacts):
        if not isinstance(item, dict):
            raise FailClosedRuntimeError("replay gap detection failed closed: evidence missing")
        evidence_id = _require_string(item.get("evidence_id") or f"EVIDENCE-{index:06d}", "evidence_id")
        source_ref = _require_string(item.get("source_replay_reference"), "source_replay_reference")
        source_hash = _require_string(item.get("source_replay_hash"), "source_replay_hash")
        payload = item.get("source_replay_payload")
        if payload is not None and replay_hash(payload) != source_hash:
            raise FailClosedRuntimeError("replay gap detection failed closed: replay broken")
        evidence_type = _normalize_key(item.get("evidence_type"), "evidence_type")
        if evidence_type in {"PERFORMANCE_METRIC", "DOMAIN_EFFECTIVENESS"}:
            _require_defined(thresholds, "performance_gap_ratio" if evidence_type == "PERFORMANCE_METRIC" else "domain_effectiveness_gap_ratio")
        if evidence_type == "FAILURE_PATTERN":
            _require_defined(thresholds, "repeated_failure_count")
        normalized.append(
            {
                **deepcopy(item),
                "evidence_id": evidence_id,
                "source_replay_reference": source_ref,
                "source_replay_hash": source_hash,
                "evidence_type": evidence_type,
                "observed_condition": _require_string(item.get("observed_condition"), "observed_condition"),
                "expected_condition": _require_string(item.get("expected_condition"), "expected_condition"),
                "confidence": _normalize_confidence(item.get("confidence")),
                "threshold_check": None,
            }
        )
    return normalized


def _failed_evidence_artifact(
    *,
    detection_id: str,
    replay_artifacts: Any,
    domain_id: str,
    thresholds: dict[str, Any] | None,
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": GAP_EVIDENCE_ARTIFACT_V1,
        "runtime_version": AIGOL_REPLAY_GAP_DETECTION_RUNTIME_VERSION,
        "evidence_id": f"{detection_id}:GAP-EVIDENCE" if isinstance(detection_id, str) else "INVALID_DETECTION:GAP-EVIDENCE",
        "detection_reference": detection_id if isinstance(detection_id, str) else "INVALID_DETECTION",
        "domain_id": domain_id if isinstance(domain_id, str) else None,
        "supported_domains": sorted(SUPPORTED_DOMAINS),
        "thresholds": deepcopy(thresholds) if isinstance(thresholds, dict) else None,
        "evidence_items": replay_artifacts if isinstance(replay_artifacts, list) else [],
        "evidence_count": len(replay_artifacts) if isinstance(replay_artifacts, list) else 0,
        "evidence_status": FAILED_CLOSED,
        "false_positive_controls": {
            "evidence_references_required": True,
            "threshold_checks_required": True,
            "replay_references_required": True,
            "confidence_classification_required": True,
        },
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "created_at": created_at,
        "replay_visible": True,
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_classification_artifact(*, detection_id: str, evidence: dict[str, Any], created_at: str) -> dict[str, Any]:
    return _classification_artifact(
        detection_id=detection_id if isinstance(detection_id, str) else "INVALID_DETECTION",
        evidence=evidence,
        classifications=[],
        created_at=created_at,
        classification_status=FAILED_CLOSED,
        failure_reason=evidence["failure_reason"],
    )


def _failed_detection_artifact(
    *,
    detection_id: str,
    evidence: dict[str, Any],
    classification: dict[str, Any],
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    return _detection_artifact(
        detection_id=detection_id if isinstance(detection_id, str) else "INVALID_DETECTION",
        evidence=evidence,
        classification=classification,
        created_at=created_at,
        detection_status=FAILED_CLOSED,
        failure_reason=failure_reason,
    )


def _returned_artifact(detection: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(detection, "replay gap detection artifact")
    artifact = {
        "event_type": "REPLAY_GAP_DETECTION_RETURNED",
        "detection_reference": detection["detection_id"],
        "detection_hash": detection["artifact_hash"],
        "detection_status": detection["detection_status"],
        "gap_count": detection["gap_count"],
        "gap_categories": deepcopy(detection["gap_categories"]),
        "human_review_required": detection["human_review_required"],
        "improvement_intent_allowed": detection["improvement_intent_allowed"],
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "replay_visible": True,
        "failure_reason": detection["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    evidence: dict[str, Any],
    classification: dict[str, Any],
    detection: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "gap_evidence_artifact": deepcopy(evidence),
        "gap_classification_artifact": deepcopy(classification),
        "gap_detection_artifact": deepcopy(detection),
        "gap_detection_replay": deepcopy(returned),
        "gap_detection_replay_reference": str(replay_path),
        "detection_status": detection["detection_status"],
        "gap_count": detection["gap_count"],
        "gap_categories": deepcopy(detection["gap_categories"]),
        "confidence": detection["confidence"],
        "human_review_required": detection["human_review_required"],
        "improvement_intent_allowed": detection["improvement_intent_allowed"],
        "fail_closed": detection["detection_status"] == FAILED_CLOSED,
        "failure_reason": detection["failure_reason"],
        "proposal_created": False,
        "ppp_invoked": False,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
    }
    capture["gap_detection_capture_hash"] = replay_hash(capture)
    return capture


def _thresholds(thresholds: dict[str, Any] | None) -> dict[str, Any]:
    active = deepcopy(DEFAULT_THRESHOLDS)
    if thresholds is not None:
        if not isinstance(thresholds, dict):
            raise FailClosedRuntimeError("replay gap detection failed closed: thresholds undefined")
        active.update(thresholds)
    for key in DEFAULT_THRESHOLDS:
        _require_defined(active, key)
        _require_number(active[key], key)
    return active


def _severity_for(category: str, item: dict[str, Any]) -> str:
    if category == "REPLAY_INTEGRITY_GAP":
        return "CRITICAL"
    if category in {"POLICY_GAP", "VALIDATION_GAP"}:
        return "HIGH"
    if category == "REPEATED_FAILURE_PATTERN":
        return "HIGH" if int(item["threshold_check"]["failure_count"]) >= int(item["threshold_check"]["threshold"]) else "MEDIUM"
    return "MEDIUM"


def _overall_confidence(classifications: list[dict[str, Any]]) -> str:
    if not classifications:
        return "NONE"
    values = [item["confidence"] for item in classifications]
    if all(value == "DETERMINISTIC" for value in values):
        return "DETERMINISTIC"
    if all(value in {"HIGH", "DETERMINISTIC"} for value in values):
        return "HIGH"
    if any(value == "LOW" for value in values):
        return "LOW"
    return "MEDIUM"


def _normalize_domain(domain_id: str) -> str:
    domain = _normalize_key(domain_id, "domain_id")
    if domain not in SUPPORTED_DOMAINS:
        raise FailClosedRuntimeError("replay gap detection failed closed: unsupported domain")
    return domain


def _normalize_confidence(value: Any) -> str:
    confidence = _normalize_key(value, "confidence")
    if confidence not in {"LOW", "MEDIUM", "HIGH", "DETERMINISTIC"}:
        raise FailClosedRuntimeError("replay gap detection failed closed: confidence classification missing")
    return confidence


def _normalize_key(value: Any, label: str) -> str:
    return _require_string(value, label).strip().upper().replace("-", "_").replace(" ", "_")


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"replay gap detection failed closed: {label} missing")
    return value


def _require_number(value: Any, label: str) -> float:
    if not isinstance(value, int | float) or isinstance(value, bool):
        raise FailClosedRuntimeError(f"replay gap detection failed closed: {label} missing")
    return float(value)


def _require_defined(mapping: dict[str, Any], key: str) -> None:
    if key not in mapping or mapping[key] is None:
        raise FailClosedRuntimeError("replay gap detection failed closed: thresholds undefined")


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("replay gap detection replay step ordering mismatch")
    _verify_artifact_hash(artifact, "replay gap detection artifact")
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


def _verify_artifact_hash(artifact: dict[str, Any], label: str) -> None:
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError(f"{label} hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("replay gap detection replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("replay gap detection replay hash mismatch")


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "replay gap detection failed closed"
