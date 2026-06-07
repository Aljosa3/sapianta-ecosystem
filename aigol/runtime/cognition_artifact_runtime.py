"""Canonical LLM cognition artifact normalization runtime."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from aigol.runtime.llm_cognition_provider_runtime import (
    LLM_COGNITION_PROVIDER_REQUEST_ARTIFACT_V1,
    LLM_COGNITION_PROVIDER_RESPONSE_ARTIFACT_V1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_context_assembly_runtime import (
    OCS_CONTEXT_ASSEMBLED,
    OCS_CONTEXT_ASSEMBLY_ARTIFACT_V1,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


MILESTONE_ID = "AIGOL_COGNITION_ARTIFACT_RUNTIME_V1"
FINAL_CLASSIFICATION = "AIGOL_COGNITION_ARTIFACT_RUNTIME_STATUS"
CERTIFIED_CLASSIFICATION = "CERTIFIED_COGNITION_ARTIFACT_RUNTIME"

LLM_COGNITION_ARTIFACT_V1 = "LLM_COGNITION_ARTIFACT_V1"
LLM_COGNITION_ARTIFACT_RETURNED_V1 = "LLM_COGNITION_ARTIFACT_RETURNED_V1"

STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED_CLOSED = "FAILED_CLOSED"

REPLAY_STEPS = (
    "llm_cognition_artifact",
    "llm_cognition_artifact_returned",
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

OPTIONAL_OPERATOR_COGNITION_FIELDS = (
    "clarification_questions",
    "recommended_next_milestone",
)

CONFIDENCE_VALUES = {"LOW", "MEDIUM", "HIGH", "DETERMINISTIC", "UNKNOWN"}

PROHIBITED_RESPONSE_PHRASES = (
    "i approve",
    "approved for execution",
    "approval granted",
    "i authorize",
    "authorized for execution",
    "execution authorized",
    "execution instruction",
    "execute this",
    "implementation authorized",
    "implementation authority",
    "invoke worker",
    "worker invocation",
    "domain creation authorized",
    "create the domain now",
    "governance mutation",
    "mutate governance",
    "replay mutation",
    "mutate replay",
)


def run_cognition_artifact_runtime(
    *,
    cognition_artifact_id: str,
    ocs_context_artifact: dict[str, Any],
    provider_request_artifact: dict[str, Any],
    provider_response_artifact: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Normalize one provider response into `LLM_COGNITION_ARTIFACT_V1`."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        context = _validate_ocs_context_artifact(ocs_context_artifact)
        request_artifact = _validate_provider_request_artifact(provider_request_artifact, context)
        response_artifact = _validate_provider_response_artifact(provider_response_artifact, context, request_artifact)
        cognition_artifact = create_llm_cognition_artifact(
            cognition_artifact_id=cognition_artifact_id,
            ocs_context_artifact=context,
            provider_request_artifact=request_artifact,
            provider_response_artifact=response_artifact,
            created_at=created_at,
        )
        returned = _returned_artifact(cognition_artifact)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], cognition_artifact)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(
            final_status=STATUS_COMPLETED,
            cognition_artifact=cognition_artifact,
            returned_artifact=returned,
            replay_path=replay_path,
            failure_reason="",
        )
    except Exception as exc:
        failure_reason = str(exc) if isinstance(exc, FailClosedRuntimeError) else "cognition artifact runtime failed closed"
        failure = _failure_artifact(
            cognition_artifact_id=(
                cognition_artifact_id if _is_nonempty_string(cognition_artifact_id) else "LLM-COGNITION-ARTIFACT-INVALID"
            ),
            created_at=created_at if _is_nonempty_string(created_at) else "1970-01-01T00:00:00Z",
            failure_reason=failure_reason,
        )
        returned = _returned_artifact(failure)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], failure)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(
            final_status=STATUS_FAILED_CLOSED,
            cognition_artifact=failure,
            returned_artifact=returned,
            replay_path=replay_path,
            failure_reason=failure_reason,
        )


def create_llm_cognition_artifact(
    *,
    cognition_artifact_id: str,
    ocs_context_artifact: dict[str, Any],
    provider_request_artifact: dict[str, Any],
    provider_response_artifact: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    """Create the canonical provider-assisted cognition artifact."""

    context = _validate_ocs_context_artifact(ocs_context_artifact)
    request_artifact = _validate_provider_request_artifact(provider_request_artifact, context)
    response_artifact = _validate_provider_response_artifact(provider_response_artifact, context, request_artifact)
    normalized = _normalize_provider_cognition(response_artifact["response_text"])
    artifact = {
        "artifact_type": LLM_COGNITION_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "classification": CERTIFIED_CLASSIFICATION,
        "cognition_artifact_id": _require_string(cognition_artifact_id, "cognition_artifact_id"),
        "cognition_artifact_status": STATUS_COMPLETED,
        "provider_assisted_cognition": True,
        "canonical_provider_assisted_cognition_output": True,
        "findings": normalized["findings"],
        "assumptions": normalized["assumptions"],
        "alternatives": normalized["alternatives"],
        "risks": normalized["risks"],
        "uncertainties": normalized["uncertainties"],
        "clarification_questions": normalized["clarification_questions"],
        "recommended_next_milestone": normalized["recommended_next_milestone"],
        "confidence": normalized["confidence"],
        "normalization": {
            "normalization_status": "NORMALIZED",
            "normalization_policy": "AIGOL_COGNITION_ARTIFACT_NORMALIZATION_POLICY_V1",
            "source_format": normalized["source_format"],
            "authority_boundary_checked": True,
            "allowed_fields": list(COGNITION_FIELDS) + list(OPTIONAL_OPERATOR_COGNITION_FIELDS) + ["confidence"],
        },
        "context_hash": context["context_hash"],
        "request_hash": request_artifact["request_hash"],
        "response_hash": response_artifact["response_hash"],
        "provider_identity": deepcopy(response_artifact["provider_identity"]),
        "provider_metadata": deepcopy(response_artifact["provider_metadata"]),
        "lineage_refs": {
            "ocs_context_hash": context["context_hash"],
            "ocs_context_artifact_hash": context["artifact_hash"],
            "llm_cognition_provider_request_hash": request_artifact["artifact_hash"],
            "llm_cognition_provider_request_content_hash": request_artifact["request_hash"],
            "llm_cognition_provider_response_hash": response_artifact["artifact_hash"],
            "llm_cognition_provider_response_content_hash": response_artifact["response_hash"],
            "provider_contract_hash": request_artifact["provider_contract_hash"],
            "provider_identity_hash": replay_hash(response_artifact["provider_identity"]),
        },
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "untrusted_provider_output_normalized": True,
        "non_authoritative": True,
        "human_review_required": True,
        "replay_visible": True,
        "provider_invoked": True,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["cognition_hash"] = _compute_cognition_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def reconstruct_cognition_artifact_replay(replay_dir: str | Path) -> dict[str, Any]:
    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("cognition artifact replay ordering mismatch")
        _verify_replay_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("cognition artifact replay artifact must be a JSON object")
        _verify_artifact_hash(artifact, "cognition artifact replay artifact")
        wrappers.append(wrapper)
    cognition_artifact = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("cognition_artifact_hash") != cognition_artifact["artifact_hash"]:
        raise FailClosedRuntimeError("cognition artifact returned hash mismatch")
    if cognition_artifact.get("cognition_hash") and cognition_artifact["cognition_hash"] != _compute_cognition_hash(
        cognition_artifact
    ):
        raise FailClosedRuntimeError("cognition artifact cognition hash mismatch")
    return {
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "classification": cognition_artifact.get("classification"),
        "final_status": cognition_artifact.get("cognition_artifact_status"),
        "cognition_artifact_id": cognition_artifact.get("cognition_artifact_id"),
        "artifact_type": cognition_artifact.get("artifact_type"),
        "context_hash": cognition_artifact.get("context_hash"),
        "request_hash": cognition_artifact.get("request_hash"),
        "response_hash": cognition_artifact.get("response_hash"),
        "provider_identity": deepcopy(cognition_artifact.get("provider_identity")),
        "lineage_refs": deepcopy(cognition_artifact.get("lineage_refs", {})),
        "authority_flags": deepcopy(cognition_artifact.get("authority_flags", {})),
        "replay_artifact_count": len(wrappers),
        "replay_visible": True,
        "append_only_valid": True,
        "canonical_provider_assisted_cognition_output": (
            cognition_artifact.get("canonical_provider_assisted_cognition_output") is True
        ),
        "replay_hash": replay_hash(wrappers),
    }


def render_cognition_artifact_summary(result: dict[str, Any]) -> str:
    artifact = result.get("llm_cognition_artifact") or {}
    return "\n".join(
        [
            "AIGOL COGNITION ARTIFACT RUNTIME",
            f"status: {result.get('final_status')}",
            f"classification: {result.get('classification')}",
            f"artifact_type: {artifact.get('artifact_type')}",
            f"cognition_artifact_id: {result.get('cognition_artifact_id')}",
            f"context_hash: {artifact.get('context_hash')}",
            f"request_hash: {artifact.get('request_hash')}",
            f"response_hash: {artifact.get('response_hash')}",
            f"replay_reference: {result.get('replay_reference')}",
            f"fail_closed: {result.get('fail_closed')}",
            f"failure_reason: {result.get('failure_reason') or ''}",
        ]
    )


def _normalize_provider_cognition(response_text: str) -> dict[str, Any]:
    text = _require_string(response_text, "provider_response_text")
    _reject_authority_bearing_text(text)
    parsed = _parse_json_response(text)
    source_format = "json" if parsed is not None else "plain_text"
    source = parsed if parsed is not None else {"findings": [text], "confidence": "UNKNOWN"}
    source = _expand_nested_cognition_json(source)
    normalized = {
        "source_format": source_format,
        "findings": _normalize_string_list(source.get("findings"), "findings", required=True),
        "assumptions": _normalize_string_list(source.get("assumptions"), "assumptions"),
        "alternatives": _normalize_string_list(source.get("alternatives"), "alternatives"),
        "risks": _normalize_string_list(source.get("risks"), "risks"),
        "uncertainties": _normalize_string_list(source.get("uncertainties"), "uncertainties"),
        "clarification_questions": _normalize_string_list(source.get("clarification_questions"), "clarification_questions"),
        "recommended_next_milestone": _normalize_optional_string(
            source.get("recommended_next_milestone"),
            "recommended_next_milestone",
        ),
        "confidence": _normalize_confidence(source.get("confidence")),
    }
    for field in COGNITION_FIELDS + ("clarification_questions",):
        for item in normalized[field]:
            _reject_authority_bearing_text(item)
    if normalized["recommended_next_milestone"]:
        _reject_authority_bearing_text(normalized["recommended_next_milestone"])
    return normalized


def _expand_nested_cognition_json(source: dict[str, Any]) -> dict[str, Any]:
    expanded = deepcopy(source)
    findings = source.get("findings")
    if not isinstance(findings, list):
        return expanded
    retained_findings: list[Any] = []
    nested_documents: list[dict[str, Any]] = []
    for item in findings:
        nested = _parse_nested_cognition_document(item)
        if nested is None:
            retained_findings.append(item)
        else:
            nested_documents.append(nested)
    if not nested_documents:
        return expanded
    expanded["findings"] = retained_findings
    for nested in nested_documents:
        for field in COGNITION_FIELDS + ("clarification_questions",):
            if field in nested:
                expanded[field] = _merge_json_cognition_values(expanded.get(field), nested.get(field))
        if nested.get("recommended_next_milestone") and not expanded.get("recommended_next_milestone"):
            expanded["recommended_next_milestone"] = nested["recommended_next_milestone"]
        if nested.get("confidence") and not expanded.get("confidence"):
            expanded["confidence"] = nested["confidence"]
    return expanded


def _parse_nested_cognition_document(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    if not (stripped.startswith("{") and stripped.endswith("}")):
        return None
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    allowed = set(COGNITION_FIELDS) | set(OPTIONAL_OPERATOR_COGNITION_FIELDS) | {"confidence"}
    if not any(field in parsed for field in allowed):
        return None
    return parsed


def _merge_json_cognition_values(existing: Any, nested: Any) -> list[Any]:
    merged: list[Any] = []
    for value in (existing, nested):
        if value is None:
            continue
        if isinstance(value, list):
            merged.extend(value)
        else:
            merged.append(value)
    return merged


def _parse_json_response(response_text: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(response_text)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        raise FailClosedRuntimeError("provider cognition response JSON must be an object")
    return parsed


def _normalize_string_list(value: Any, field_name: str, *, required: bool = False) -> list[str]:
    if value is None:
        if required:
            raise FailClosedRuntimeError(f"{field_name} must include at least one bounded item")
        return []
    raw_items = value if isinstance(value, list) else [value]
    normalized: list[str] = []
    for item in raw_items:
        text = _require_string(item, field_name)
        normalized.append(" ".join(text.split()))
    if required and not normalized:
        raise FailClosedRuntimeError(f"{field_name} must include at least one bounded item")
    return normalized


def _normalize_optional_string(value: Any, field_name: str) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        normalized = _normalize_string_list(value, field_name)
        return normalized[0] if normalized else ""
    return " ".join(_require_string(value, field_name).split())


def _normalize_confidence(value: Any) -> str:
    if value is None:
        return "UNKNOWN"
    confidence = _require_string(value, "confidence").upper()
    if confidence not in CONFIDENCE_VALUES:
        raise FailClosedRuntimeError("confidence value is not recognized")
    return confidence


def _validate_ocs_context_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("OCS context artifact must be a JSON object")
    if artifact.get("artifact_type") != OCS_CONTEXT_ASSEMBLY_ARTIFACT_V1:
        raise FailClosedRuntimeError("invalid OCS context assembly artifact")
    if artifact.get("context_status") != OCS_CONTEXT_ASSEMBLED:
        raise FailClosedRuntimeError("OCS context must be assembled")
    if artifact.get("replay_visible") is not True:
        raise FailClosedRuntimeError("OCS context artifact is not replay-visible")
    _verify_artifact_hash(artifact, "OCS context artifact")
    _reject_prohibited_flags(artifact, "OCS context artifact")
    return deepcopy(artifact)


def _validate_provider_request_artifact(artifact: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("provider request artifact must be a JSON object")
    if artifact.get("artifact_type") != LLM_COGNITION_PROVIDER_REQUEST_ARTIFACT_V1:
        raise FailClosedRuntimeError("invalid LLM cognition provider request artifact")
    _verify_artifact_hash(artifact, "LLM cognition provider request artifact")
    _reject_prohibited_flags(artifact, "LLM cognition provider request artifact")
    refs = artifact.get("ocs_context_reference")
    if not isinstance(refs, dict):
        raise FailClosedRuntimeError("provider request missing OCS context reference")
    if refs.get("context_hash") != context["context_hash"]:
        raise FailClosedRuntimeError("provider request context hash mismatch")
    if refs.get("context_artifact_hash") != context["artifact_hash"]:
        raise FailClosedRuntimeError("provider request context artifact hash mismatch")
    if not _is_nonempty_string(artifact.get("request_hash")):
        raise FailClosedRuntimeError("provider request content hash is required")
    return deepcopy(artifact)


def _validate_provider_response_artifact(
    artifact: dict[str, Any], context: dict[str, Any], request_artifact: dict[str, Any]
) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("provider response artifact must be a JSON object")
    if artifact.get("artifact_type") != LLM_COGNITION_PROVIDER_RESPONSE_ARTIFACT_V1:
        raise FailClosedRuntimeError("invalid LLM cognition provider response artifact")
    _verify_artifact_hash(artifact, "LLM cognition provider response artifact")
    _reject_prohibited_flags(artifact, "LLM cognition provider response artifact")
    if artifact.get("provider_request_hash") != request_artifact["artifact_hash"]:
        raise FailClosedRuntimeError("provider response request artifact hash mismatch")
    if artifact.get("request_hash") != request_artifact["request_hash"]:
        raise FailClosedRuntimeError("provider response request content hash mismatch")
    if artifact.get("ocs_context_hash") != context["context_hash"]:
        raise FailClosedRuntimeError("provider response context hash mismatch")
    if artifact.get("provider_invoked") is not True:
        raise FailClosedRuntimeError("provider response must come from an invoked cognition provider")
    if artifact.get("non_authoritative") is not True:
        raise FailClosedRuntimeError("provider response must be marked non-authoritative")
    if not isinstance(artifact.get("provider_identity"), dict):
        raise FailClosedRuntimeError("provider response missing provider identity")
    if not _is_nonempty_string(artifact.get("response_hash")):
        raise FailClosedRuntimeError("provider response content hash is required")
    _reject_authority_bearing_text(artifact.get("response_text"))
    return deepcopy(artifact)


def _returned_artifact(cognition_artifact: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(cognition_artifact, "LLM cognition artifact")
    returned = {
        "artifact_type": LLM_COGNITION_ARTIFACT_RETURNED_V1,
        "runtime_version": MILESTONE_ID,
        "cognition_artifact_reference": cognition_artifact["cognition_artifact_id"],
        "cognition_artifact_hash": cognition_artifact["artifact_hash"],
        "cognition_hash": cognition_artifact.get("cognition_hash"),
        "context_hash": cognition_artifact.get("context_hash"),
        "request_hash": cognition_artifact.get("request_hash"),
        "response_hash": cognition_artifact.get("response_hash"),
        "final_status": cognition_artifact["cognition_artifact_status"],
        "replay_visible": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "provider_invoked": cognition_artifact.get("provider_invoked") is True,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _failure_artifact(*, cognition_artifact_id: str, created_at: str, failure_reason: str) -> dict[str, Any]:
    artifact = {
        "artifact_type": LLM_COGNITION_ARTIFACT_V1,
        "runtime_version": MILESTONE_ID,
        "classification": CERTIFIED_CLASSIFICATION,
        "cognition_artifact_id": cognition_artifact_id,
        "cognition_artifact_status": STATUS_FAILED_CLOSED,
        "provider_assisted_cognition": False,
        "canonical_provider_assisted_cognition_output": False,
        "findings": [],
        "assumptions": [],
        "alternatives": [],
        "risks": [],
        "uncertainties": [],
        "confidence": "UNKNOWN",
        "normalization": {
            "normalization_status": "FAILED_CLOSED",
            "normalization_policy": "AIGOL_COGNITION_ARTIFACT_NORMALIZATION_POLICY_V1",
            "source_format": "none",
            "authority_boundary_checked": True,
            "allowed_fields": list(COGNITION_FIELDS) + ["confidence"],
        },
        "context_hash": None,
        "request_hash": None,
        "response_hash": None,
        "provider_identity": None,
        "provider_metadata": None,
        "lineage_refs": {},
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "untrusted_provider_output_normalized": False,
        "non_authoritative": True,
        "human_review_required": True,
        "failure_reason": failure_reason,
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "created_at": created_at,
    }
    artifact["cognition_hash"] = _compute_cognition_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    *,
    final_status: str,
    cognition_artifact: dict[str, Any],
    returned_artifact: dict[str, Any],
    replay_path: Path,
    failure_reason: str,
) -> dict[str, Any]:
    result = {
        "command": "aigol cognition artifact normalize",
        "milestone_id": MILESTONE_ID,
        "final_classification": FINAL_CLASSIFICATION,
        "classification": CERTIFIED_CLASSIFICATION,
        "final_status": final_status,
        "cognition_artifact_id": cognition_artifact.get("cognition_artifact_id"),
        "llm_cognition_artifact": deepcopy(cognition_artifact),
        "llm_cognition_artifact_returned": deepcopy(returned_artifact),
        "replay_reference": str(replay_path),
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "provider_invoked": cognition_artifact.get("provider_invoked") is True,
        "worker_invoked": False,
        "approval_created": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "fail_closed": final_status != STATUS_COMPLETED,
        "failure_reason": failure_reason,
    }
    result["cognition_artifact_runtime_hash"] = replay_hash(result)
    return result


def _compute_cognition_hash(artifact: dict[str, Any]) -> str:
    return replay_hash(
        {
            "cognition_artifact_id": artifact["cognition_artifact_id"],
            "cognition_artifact_status": artifact["cognition_artifact_status"],
            "findings": artifact["findings"],
            "assumptions": artifact["assumptions"],
            "alternatives": artifact["alternatives"],
            "risks": artifact["risks"],
            "uncertainties": artifact["uncertainties"],
            "confidence": artifact["confidence"],
            "context_hash": artifact["context_hash"],
            "request_hash": artifact["request_hash"],
            "response_hash": artifact["response_hash"],
            "provider_identity": artifact["provider_identity"],
            "lineage_refs": artifact["lineage_refs"],
            "authority_flags": artifact["authority_flags"],
            "failure_reason": artifact.get("failure_reason"),
        }
    )


def _reject_authority_bearing_text(value: Any) -> None:
    text = _require_string(value, "provider_response_text").lower()
    for phrase in PROHIBITED_RESPONSE_PHRASES:
        if phrase in text:
            raise FailClosedRuntimeError("provider output exceeds cognition artifact authority boundary")


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
        for flag, value in flags.items():
            if value is True:
                raise FailClosedRuntimeError(f"{label} carries prohibited authority flag: {flag}")


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("cognition artifact replay step ordering mismatch")
    _verify_artifact_hash(artifact, "cognition artifact replay artifact")
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
        raise FailClosedRuntimeError("cognition artifact replay hash is required")
    expected_input = deepcopy(wrapper)
    expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("cognition artifact replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not _is_nonempty_string(value):
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
