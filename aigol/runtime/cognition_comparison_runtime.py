"""Cognition comparison runtime for multiple LLM cognition artifacts."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.cognition_artifact_runtime import LLM_COGNITION_ARTIFACT_V1
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.multi_provider_cognition_runtime import MULTI_PROVIDER_COGNITION_RESULT_BUNDLE_V1
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_COGNITION_COMPARISON_RUNTIME_V1"
FINAL_CLASSIFICATION = "AIGOL_COGNITION_COMPARISON_RUNTIME_STATUS"
CERTIFIED_CLASSIFICATION = "CERTIFIED_COGNITION_COMPARISON_RUNTIME"

COGNITION_COMPARISON_ARTIFACT_V1 = "COGNITION_COMPARISON_ARTIFACT_V1"
COGNITION_COMPARISON_RETURNED_V1 = "COGNITION_COMPARISON_RETURNED_V1"

STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "cognition_comparison_artifact",
    "cognition_comparison_returned",
)

AUTHORITY_FLAGS = {
    "provider_authority": False,
    "approval_authority": False,
    "execution_authority": False,
    "worker_authority": False,
    "governance_authority": False,
    "replay_authority": False,
}

COGNITION_FIELDS = (
    "findings",
    "assumptions",
    "alternatives",
    "risks",
    "uncertainties",
)

CONFIDENCE_RANK = {
    "UNKNOWN": 0,
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "DETERMINISTIC": 4,
}

PROHIBITED_PHRASES = (
    "i approve",
    "approval granted",
    "execution authorized",
    "execute this",
    "implementation authorized",
    "worker invocation",
    "invoke worker",
    "domain creation authorized",
    "governance mutation",
    "mutate governance",
    "replay mutation",
    "mutate replay",
)


def run_cognition_comparison_runtime(
    *,
    cognition_comparison_id: str,
    multi_provider_result_bundle: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Create one non-authoritative comparison artifact."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        result_bundle = _validate_result_bundle(multi_provider_result_bundle)
        cognition_artifacts = _extract_cognition_artifacts(result_bundle)
        comparison_artifact = create_cognition_comparison_artifact(
            cognition_comparison_id=cognition_comparison_id,
            multi_provider_result_bundle=result_bundle,
            cognition_artifacts=cognition_artifacts,
            created_at=created_at,
        )
        returned = _returned_artifact(comparison_artifact)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], comparison_artifact)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(
            final_status=STATUS_COMPLETED,
            comparison_artifact=comparison_artifact,
            returned_artifact=returned,
            replay_path=replay_path,
            failure_reason="",
        )
    except Exception as exc:
        failure_reason = str(exc) if isinstance(exc, FailClosedRuntimeError) else "cognition comparison failed closed"
        failure = _failure_artifact(
            cognition_comparison_id=(
                cognition_comparison_id if _is_nonempty_string(cognition_comparison_id) else "COGNITION-COMPARISON-INVALID"
            ),
            created_at=created_at if _is_nonempty_string(created_at) else "1970-01-01T00:00:00Z",
            failure_reason=failure_reason,
        )
        returned = _returned_artifact(failure)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], failure)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(
            final_status=STATUS_FAILED_CLOSED,
            comparison_artifact=failure,
            returned_artifact=returned,
            replay_path=replay_path,
            failure_reason=failure_reason,
        )


def create_cognition_comparison_artifact(
    *,
    cognition_comparison_id: str,
    multi_provider_result_bundle: dict[str, Any],
    cognition_artifacts: list[dict[str, Any]],
    created_at: str,
) -> dict[str, Any]:
    result_bundle = _validate_result_bundle(multi_provider_result_bundle)
    artifacts = [_validate_cognition_artifact(artifact) for artifact in cognition_artifacts]
    if len(artifacts) < 2:
        raise FailClosedRuntimeError("at least two cognition artifacts are required for comparison")
    comparison = _compare_cognition_artifacts(artifacts, result_bundle)
    artifact = {
        "artifact_type": COGNITION_COMPARISON_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "classification": CERTIFIED_CLASSIFICATION,
        "cognition_comparison_id": _require_string(cognition_comparison_id, "cognition_comparison_id"),
        "comparison_status": STATUS_COMPLETED,
        "multi_provider_cognition_bundle_id": result_bundle["multi_provider_cognition_bundle_id"],
        "source_result_bundle_hash": result_bundle["artifact_hash"],
        "source_result_bundle_result_hash": result_bundle["result_bundle_hash"],
        "context_hash": result_bundle["context_hash"],
        "source_cognition_artifacts": [_source_summary(artifact) for artifact in artifacts],
        "provider_identities": [deepcopy(artifact["provider_identity"]) for artifact in artifacts],
        "comparison_findings": comparison["comparison_findings"],
        "agreement": comparison["agreement"],
        "disagreement": comparison["disagreement"],
        "conflicting_assumptions": comparison["conflicting_assumptions"],
        "conflicting_risks": comparison["conflicting_risks"],
        "conflicting_alternatives": comparison["conflicting_alternatives"],
        "uncertainty": comparison["uncertainty"],
        "missing_information": comparison["missing_information"],
        "comparison_confidence": comparison["comparison_confidence"],
        "comparison_policy": {
            "comparison_method": "deterministic exact-normalized overlap and provider-divergence review",
            "confidence_model": "bounded source confidence minimum with disagreement penalty",
            "non_authoritative": True,
            "human_review_required": True,
        },
        "lineage_refs": {
            "multi_provider_result_bundle_hash": result_bundle["artifact_hash"],
            "multi_provider_result_bundle_result_hash": result_bundle["result_bundle_hash"],
            "context_hash": result_bundle["context_hash"],
            "source_cognition_artifact_hashes": [artifact["artifact_hash"] for artifact in artifacts],
            "source_cognition_hashes": [artifact["cognition_hash"] for artifact in artifacts],
            "provider_identity_hashes": [replay_hash(artifact["provider_identity"]) for artifact in artifacts],
        },
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "non_authoritative": True,
        "human_review_required": True,
        "comparison_created": True,
        "approval_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["comparison_hash"] = _compute_comparison_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def reconstruct_cognition_comparison_replay(replay_dir: str | Path) -> dict[str, Any]:
    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("cognition comparison replay ordering mismatch")
        _verify_replay_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("cognition comparison replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "cognition comparison replay artifact")
        wrappers.append(wrapper)
    comparison_artifact = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("cognition_comparison_hash") != comparison_artifact["artifact_hash"]:
        raise FailClosedRuntimeError("cognition comparison returned hash mismatch")
    if comparison_artifact.get("comparison_hash") and comparison_artifact["comparison_hash"] != _compute_comparison_hash(
        comparison_artifact
    ):
        raise FailClosedRuntimeError("cognition comparison hash mismatch")
    return {
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "classification": comparison_artifact.get("classification"),
        "final_status": comparison_artifact.get("comparison_status"),
        "cognition_comparison_id": comparison_artifact.get("cognition_comparison_id"),
        "artifact_type": comparison_artifact.get("artifact_type"),
        "context_hash": comparison_artifact.get("context_hash"),
        "source_cognition_artifact_count": len(comparison_artifact.get("source_cognition_artifacts", [])),
        "comparison_confidence": comparison_artifact.get("comparison_confidence"),
        "lineage_refs": deepcopy(comparison_artifact.get("lineage_refs", {})),
        "authority_flags": deepcopy(comparison_artifact.get("authority_flags", {})),
        "replay_visible": True,
        "append_only_valid": True,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def render_cognition_comparison_summary(result: dict[str, Any]) -> str:
    artifact = result.get("cognition_comparison_artifact") or {}
    return "\n".join(
        [
            "AIGOL COGNITION COMPARISON RUNTIME",
            f"status: {result.get('final_status')}",
            f"classification: {result.get('classification')}",
            f"artifact_type: {artifact.get('artifact_type')}",
            f"cognition_comparison_id: {result.get('cognition_comparison_id')}",
            f"comparison_confidence: {artifact.get('comparison_confidence')}",
            f"source_count: {len(artifact.get('source_cognition_artifacts', []))}",
            f"replay_reference: {result.get('replay_reference')}",
            f"fail_closed: {result.get('fail_closed')}",
            f"failure_reason: {result.get('failure_reason') or ''}",
        ]
    )


def _compare_cognition_artifacts(artifacts: list[dict[str, Any]], result_bundle: dict[str, Any]) -> dict[str, Any]:
    provider_count = len(artifacts)
    field_maps = {field: _field_value_map(artifacts, field) for field in COGNITION_FIELDS}
    agreement = _agreement_items(field_maps["findings"], provider_count)
    disagreement = _disagreement_items(field_maps["findings"])
    conflicting_assumptions = _disagreement_items(field_maps["assumptions"])
    conflicting_risks = _disagreement_items(field_maps["risks"])
    conflicting_alternatives = _disagreement_items(field_maps["alternatives"])
    uncertainty = _uncertainty_items(artifacts, result_bundle)
    missing_information = _missing_information_items(artifacts, result_bundle)
    comparison_confidence = _comparison_confidence(
        artifacts=artifacts,
        disagreement=disagreement,
        conflicting_assumptions=conflicting_assumptions,
        conflicting_risks=conflicting_risks,
        conflicting_alternatives=conflicting_alternatives,
        missing_information=missing_information,
        provider_failures=result_bundle.get("provider_failures", []),
    )
    comparison_findings = _comparison_findings(
        agreement=agreement,
        disagreement=disagreement,
        uncertainty=uncertainty,
        missing_information=missing_information,
        comparison_confidence=comparison_confidence,
        provider_count=provider_count,
    )
    return {
        "comparison_findings": comparison_findings,
        "agreement": agreement,
        "disagreement": disagreement,
        "conflicting_assumptions": conflicting_assumptions,
        "conflicting_risks": conflicting_risks,
        "conflicting_alternatives": conflicting_alternatives,
        "uncertainty": uncertainty,
        "missing_information": missing_information,
        "comparison_confidence": comparison_confidence,
    }


def _field_value_map(artifacts: list[dict[str, Any]], field: str) -> dict[str, dict[str, Any]]:
    values: dict[str, dict[str, Any]] = {}
    for artifact in artifacts:
        provider_id = artifact["provider_identity"]["provider_id"]
        for value in artifact.get(field, []):
            _reject_authority_bearing_text(value)
            normalized = _normalize_text(value)
            entry = values.setdefault(normalized, {"text": value, "providers": []})
            entry["providers"].append(provider_id)
    return values


def _agreement_items(values: dict[str, dict[str, Any]], provider_count: int) -> list[dict[str, Any]]:
    return [
        {"text": entry["text"], "providers": sorted(entry["providers"]), "provider_count": len(set(entry["providers"]))}
        for entry in sorted(values.values(), key=lambda item: _normalize_text(item["text"]))
        if len(set(entry["providers"])) == provider_count
    ]


def _disagreement_items(values: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"text": entry["text"], "providers": sorted(set(entry["providers"])), "provider_count": len(set(entry["providers"]))}
        for entry in sorted(values.values(), key=lambda item: _normalize_text(item["text"]))
        if len(set(entry["providers"])) == 1
    ]


def _uncertainty_items(artifacts: list[dict[str, Any]], result_bundle: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for artifact in artifacts:
        provider_id = artifact["provider_identity"]["provider_id"]
        for uncertainty in artifact.get("uncertainties", []):
            items.append({"text": uncertainty, "provider_id": provider_id, "source": "provider_uncertainty"})
    for failure in result_bundle.get("provider_failures", []):
        items.append(
            {
                "text": failure.get("failure_reason", "provider failure"),
                "provider_id": failure.get("provider_id"),
                "source": "provider_failure",
            }
        )
    return sorted(items, key=lambda item: (str(item.get("provider_id")), _normalize_text(item["text"])))


def _missing_information_items(artifacts: list[dict[str, Any]], result_bundle: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    field_names = ("findings", "assumptions", "alternatives", "risks", "uncertainties")
    for artifact in artifacts:
        provider_id = artifact["provider_identity"]["provider_id"]
        for field in field_names:
            if not artifact.get(field):
                items.append({"provider_id": provider_id, "missing": field, "reason": "source cognition artifact field empty"})
    if result_bundle.get("failed_provider_count", 0) > 0:
        items.append(
            {
                "provider_id": "bundle",
                "missing": "complete_provider_set",
                "reason": "one or more provider cognition artifacts failed closed",
            }
        )
    return sorted(items, key=lambda item: (str(item["provider_id"]), item["missing"]))


def _comparison_confidence(
    *,
    artifacts: list[dict[str, Any]],
    disagreement: list[dict[str, Any]],
    conflicting_assumptions: list[dict[str, Any]],
    conflicting_risks: list[dict[str, Any]],
    conflicting_alternatives: list[dict[str, Any]],
    missing_information: list[dict[str, Any]],
    provider_failures: list[dict[str, Any]],
) -> str:
    confidence_values = [_normalize_confidence(artifact.get("confidence")) for artifact in artifacts]
    minimum = min(CONFIDENCE_RANK[value] for value in confidence_values)
    conflict_count = len(disagreement) + len(conflicting_assumptions) + len(conflicting_risks) + len(conflicting_alternatives)
    if provider_failures or missing_information:
        minimum = min(minimum, CONFIDENCE_RANK["MEDIUM"])
    if conflict_count:
        minimum = min(minimum, CONFIDENCE_RANK["MEDIUM"])
    if minimum >= CONFIDENCE_RANK["HIGH"]:
        return "HIGH"
    if minimum >= CONFIDENCE_RANK["MEDIUM"]:
        return "MEDIUM"
    if minimum >= CONFIDENCE_RANK["LOW"]:
        return "LOW"
    return "UNKNOWN"


def _comparison_findings(
    *,
    agreement: list[dict[str, Any]],
    disagreement: list[dict[str, Any]],
    uncertainty: list[dict[str, Any]],
    missing_information: list[dict[str, Any]],
    comparison_confidence: str,
    provider_count: int,
) -> list[str]:
    findings = [
        f"Compared {provider_count} provider cognition artifacts.",
        f"Detected {len(agreement)} shared finding(s).",
        f"Detected {len(disagreement)} provider-specific finding(s).",
        f"Detected {len(uncertainty)} uncertainty item(s).",
        f"Detected {len(missing_information)} missing information item(s).",
        f"Comparison confidence: {comparison_confidence}.",
    ]
    for finding in findings:
        _reject_authority_bearing_text(finding)
    return findings


def _extract_cognition_artifacts(result_bundle: dict[str, Any]) -> list[dict[str, Any]]:
    artifacts = []
    for provider_result in result_bundle.get("provider_results", []):
        artifact = provider_result.get("llm_cognition_artifact")
        if isinstance(artifact, dict):
            artifacts.append(artifact)
    return artifacts


def _source_summary(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "cognition_artifact_id": artifact["cognition_artifact_id"],
        "artifact_hash": artifact["artifact_hash"],
        "cognition_hash": artifact["cognition_hash"],
        "provider_id": artifact["provider_identity"]["provider_id"],
        "provider_identity": deepcopy(artifact["provider_identity"]),
        "context_hash": artifact["context_hash"],
        "request_hash": artifact["request_hash"],
        "response_hash": artifact["response_hash"],
        "confidence": artifact["confidence"],
    }


def _validate_result_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(bundle, dict):
        raise FailClosedRuntimeError("multi-provider result bundle must be a JSON object")
    if bundle.get("artifact_type") != MULTI_PROVIDER_COGNITION_RESULT_BUNDLE_V1:
        raise FailClosedRuntimeError("invalid multi-provider cognition result bundle")
    if bundle.get("bundle_status") != STATUS_COMPLETED:
        raise FailClosedRuntimeError("multi-provider cognition result bundle must be completed")
    _verify_artifact_hash(bundle, "multi-provider cognition result bundle")
    _reject_prohibited_flags(bundle, "multi-provider cognition result bundle")
    if bundle.get("comparison_performed") is not False:
        raise FailClosedRuntimeError("source bundle already contains comparison")
    return deepcopy(bundle)


def _validate_cognition_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("cognition artifact must be a JSON object")
    if artifact.get("artifact_type") != LLM_COGNITION_ARTIFACT_V1:
        raise FailClosedRuntimeError("invalid LLM cognition artifact")
    if artifact.get("cognition_artifact_status") != STATUS_COMPLETED:
        raise FailClosedRuntimeError("LLM cognition artifact must be completed")
    _verify_artifact_hash(artifact, "LLM cognition artifact")
    _reject_prohibited_flags(artifact, "LLM cognition artifact")
    _validate_authority_flags(artifact.get("authority_flags"))
    if artifact.get("non_authoritative") is not True:
        raise FailClosedRuntimeError("LLM cognition artifact must be non-authoritative")
    if not isinstance(artifact.get("provider_identity"), dict):
        raise FailClosedRuntimeError("LLM cognition artifact missing provider identity")
    for field in COGNITION_FIELDS:
        for value in artifact.get(field, []):
            _reject_authority_bearing_text(value)
    return deepcopy(artifact)


def _returned_artifact(comparison_artifact: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(comparison_artifact, "cognition comparison artifact")
    returned = {
        "artifact_type": COGNITION_COMPARISON_RETURNED_V1,
        "runtime_version": MILESTONE_ID,
        "cognition_comparison_reference": comparison_artifact["cognition_comparison_id"],
        "cognition_comparison_hash": comparison_artifact["artifact_hash"],
        "comparison_hash": comparison_artifact.get("comparison_hash"),
        "comparison_status": comparison_artifact["comparison_status"],
        "comparison_confidence": comparison_artifact.get("comparison_confidence"),
        "replay_visible": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "approval_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _failure_artifact(*, cognition_comparison_id: str, created_at: str, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": COGNITION_COMPARISON_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "classification": CERTIFIED_CLASSIFICATION,
        "cognition_comparison_id": cognition_comparison_id,
        "comparison_status": STATUS_FAILED_CLOSED,
        "multi_provider_cognition_bundle_id": None,
        "source_result_bundle_hash": None,
        "source_result_bundle_result_hash": None,
        "context_hash": None,
        "source_cognition_artifacts": [],
        "provider_identities": [],
        "comparison_findings": [],
        "agreement": [],
        "disagreement": [],
        "conflicting_assumptions": [],
        "conflicting_risks": [],
        "conflicting_alternatives": [],
        "uncertainty": [],
        "missing_information": [],
        "comparison_confidence": "UNKNOWN",
        "comparison_policy": {
            "comparison_method": "failed_closed",
            "confidence_model": "failed_closed",
            "non_authoritative": True,
            "human_review_required": True,
        },
        "lineage_refs": {},
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "non_authoritative": True,
        "human_review_required": True,
        "comparison_created": False,
        "failure_reason": failure_reason,
        "approval_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_visible": True,
        "created_at": created_at,
    }
    artifact["comparison_hash"] = _compute_comparison_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    *,
    final_status: str,
    comparison_artifact: dict[str, Any],
    returned_artifact: dict[str, Any],
    replay_path: Path,
    failure_reason: str,
) -> dict[str, Any]:
    result = {
        "command": "aigol cognition comparison run",
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "classification": CERTIFIED_CLASSIFICATION,
        "final_status": final_status,
        "cognition_comparison_id": comparison_artifact.get("cognition_comparison_id"),
        "cognition_comparison_artifact": deepcopy(comparison_artifact),
        "cognition_comparison_returned": deepcopy(returned_artifact),
        "comparison_confidence": comparison_artifact.get("comparison_confidence"),
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "replay_reference": str(replay_path),
        "approval_created": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "fail_closed": final_status != STATUS_COMPLETED,
        "failure_reason": failure_reason,
    }
    result["cognition_comparison_runtime_hash"] = replay_hash(result)
    return result


def _compute_comparison_hash(artifact: dict[str, Any]) -> str:
    return replay_hash(
        {
            "cognition_comparison_id": artifact["cognition_comparison_id"],
            "comparison_status": artifact["comparison_status"],
            "multi_provider_cognition_bundle_id": artifact["multi_provider_cognition_bundle_id"],
            "source_result_bundle_hash": artifact["source_result_bundle_hash"],
            "context_hash": artifact["context_hash"],
            "source_cognition_artifacts": artifact["source_cognition_artifacts"],
            "provider_identities": artifact["provider_identities"],
            "comparison_findings": artifact["comparison_findings"],
            "agreement": artifact["agreement"],
            "disagreement": artifact["disagreement"],
            "conflicting_assumptions": artifact["conflicting_assumptions"],
            "conflicting_risks": artifact["conflicting_risks"],
            "conflicting_alternatives": artifact["conflicting_alternatives"],
            "uncertainty": artifact["uncertainty"],
            "missing_information": artifact["missing_information"],
            "comparison_confidence": artifact["comparison_confidence"],
            "lineage_refs": artifact["lineage_refs"],
            "authority_flags": artifact["authority_flags"],
            "failure_reason": artifact.get("failure_reason"),
        }
    )


def _normalize_confidence(value: Any) -> str:
    confidence = _require_string(value, "confidence").upper()
    if confidence not in CONFIDENCE_RANK:
        raise FailClosedRuntimeError("confidence value is not recognized")
    return confidence


def _normalize_text(value: Any) -> str:
    return " ".join(_require_string(value, "text").lower().split())


def _reject_authority_bearing_text(value: Any) -> None:
    text = _normalize_text(value)
    for phrase in PROHIBITED_PHRASES:
        if phrase in text:
            raise FailClosedRuntimeError("cognition comparison source exceeds authority boundary")


def _reject_prohibited_flags(artifact: dict[str, Any], label: str) -> None:
    for flag in (
        "approval_created",
        "execution_requested",
        "dispatch_requested",
        "worker_invoked",
        "domain_created",
        "governance_modified",
        "replay_modified",
    ):
        if artifact.get(flag) is True:
            raise FailClosedRuntimeError(f"{label} carries prohibited authority flag: {flag}")
    flags = artifact.get("authority_flags")
    if isinstance(flags, dict):
        _validate_authority_flags(flags)


def _validate_authority_flags(flags: Any) -> None:
    if not isinstance(flags, dict):
        raise FailClosedRuntimeError("authority flags are missing")
    for flag, expected in AUTHORITY_FLAGS.items():
        if flags.get(flag) is not expected:
            raise FailClosedRuntimeError(f"authority flag must be false: {flag}")


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("cognition comparison replay step ordering mismatch")
    _verify_artifact_hash(artifact, "cognition comparison replay artifact")
    wrapper = {
        "replay_index": index,
        "replay_step": step,
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
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be a JSON object")
    actual = artifact.get("artifact_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError(f"{label} artifact hash is required")
    expected_input = deepcopy(artifact)
    expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError(f"{label} artifact hash mismatch")


def _verify_replay_wrapper_hash(wrapper: dict[str, Any]) -> None:
    actual = wrapper.get("replay_hash")
    if not isinstance(actual, str):
        raise FailClosedRuntimeError("cognition comparison replay hash is required")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("cognition comparison replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not _is_nonempty_string(value):
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
