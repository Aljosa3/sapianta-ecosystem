"""First bounded OCS cognition runtime for AiGOL V1."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.ocs_context_assembly_runtime import (
    OCS_CONTEXT_ASSEMBLED,
    OCS_CONTEXT_ASSEMBLY_ARTIFACT_V1,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


AIGOL_OCS_COGNITION_RUNTIME_VERSION = "AIGOL_OCS_COGNITION_RUNTIME_V1"
OCS_COGNITION_ARTIFACT_V1 = "OCS_COGNITION_ARTIFACT_V1"
OCS_COGNITION_COMPLETED = "OCS_COGNITION_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"

PROVIDER_REQUIRED = "PROVIDER_REQUIRED"
PROVIDER_OPTIONAL = "PROVIDER_OPTIONAL"
PROVIDER_PROHIBITED = "PROVIDER_PROHIBITED"
PROVIDER_UNDETERMINED = "PROVIDER_UNDETERMINED"

REPLAY_STEPS = (
    "ocs_cognition_recorded",
    "ocs_cognition_returned",
)

AUTHORITY_FLAGS = {
    "authorizes_execution": False,
    "authorizes_dispatch": False,
    "authorizes_worker_invocation": False,
    "authorizes_provider_invocation": False,
    "authorizes_governance_mutation": False,
    "authorizes_replay_mutation": False,
    "authorizes_domain_creation": False,
    "authorizes_human_approval": False,
}

PROHIBITED_AUTHORITY_FLAGS = (
    "authority",
    "approval_created",
    "execution_requested",
    "dispatch_requested",
    "worker_assignment_requested",
    "worker_dispatch_requested",
    "worker_invocation_requested",
    "worker_invoked",
    "provider_invoked",
    "domain_created",
    "governance_modified",
    "replay_modified",
    "approval_inferred",
)

KNOWN_DOMAINS = (
    "MARKETING",
    "SERVER_MANAGEMENT",
    "TRADING",
    "HEALTHCARE",
)

WORKER_HINTS = (
    "MARKET_EVIDENCE_NORMALIZATION",
    "STRATEGY",
    "RISK",
    "PORTFOLIO",
    "MARKETING",
    "SERVER_MANAGEMENT",
    "HEALTHCARE",
)


def run_ocs_cognition(
    *,
    cognition_id: str,
    ocs_context_assembly_artifact: dict[str, Any],
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Analyze an OCS context assembly artifact without creating authority."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        context = deepcopy(ocs_context_assembly_artifact)
        _validate_context_artifact(context)
        analysis = _analyze_context(context)
        cognition = _cognition_artifact(
            cognition_id=cognition_id,
            context=context,
            analysis=analysis,
            created_at=created_at,
            cognition_status=OCS_COGNITION_COMPLETED,
            failure_reason=None,
        )
        returned = _returned_artifact(cognition)
        _persist_step(replay_path, 0, REPLAY_STEPS[0], cognition)
        _persist_step(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(cognition, returned, replay_path)
    except Exception as exc:
        failure_reason = _failure_reason(exc)
        cognition = _failed_cognition_artifact(
            cognition_id=cognition_id,
            context=ocs_context_assembly_artifact if isinstance(ocs_context_assembly_artifact, dict) else {},
            created_at=created_at,
            failure_reason=failure_reason,
        )
        returned = _returned_artifact(cognition)
        _persist_failure_if_possible(replay_path, 0, REPLAY_STEPS[0], cognition)
        _persist_failure_if_possible(replay_path, 1, REPLAY_STEPS[1], returned)
        return _capture(cognition, returned, replay_path)


def reconstruct_ocs_cognition_replay(replay_dir: str | Path) -> dict[str, Any]:
    """Reconstruct OCS cognition replay evidence deterministically."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("OCS cognition replay ordering mismatch")
        _verify_wrapper_hash(wrapper)
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("OCS cognition replay artifact must be a JSON object")
        _verify_artifact_hash(artifact)
        wrappers.append(wrapper)

    recorded = wrappers[0]["artifact"]
    returned = wrappers[1]["artifact"]
    if returned.get("cognition_reference") != recorded["cognition_id"]:
        raise FailClosedRuntimeError("OCS cognition replay reference mismatch")
    if returned.get("cognition_artifact_hash") != recorded["artifact_hash"]:
        raise FailClosedRuntimeError("OCS cognition replay artifact hash mismatch")
    if recorded.get("cognition_hash") != _compute_cognition_hash(recorded):
        raise FailClosedRuntimeError("OCS cognition hash mismatch")
    return {
        "cognition_id": recorded["cognition_id"],
        "cognition_status": recorded["cognition_status"],
        "source_context_assembly_id": recorded["source_context_assembly_id"],
        "source_context_hash": recorded["source_context_hash"],
        "task_intent": deepcopy(recorded["task_intent"]),
        "ambiguity": deepcopy(recorded["ambiguity"]),
        "clarification_requirements": deepcopy(recorded["clarification_requirements"]),
        "domain_candidates": deepcopy(recorded["domain_candidates"]),
        "worker_candidates": deepcopy(recorded["worker_candidates"]),
        "provider_necessity": deepcopy(recorded["provider_necessity"]),
        "cognition_hash": recorded["cognition_hash"],
        "authority_flags": deepcopy(recorded["authority_flags"]),
        "replay_visible": True,
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _validate_context_artifact(context: dict[str, Any]) -> None:
    if context.get("artifact_type") != OCS_CONTEXT_ASSEMBLY_ARTIFACT_V1:
        raise FailClosedRuntimeError("OCS cognition failed closed: invalid OCS context artifact")
    _verify_artifact_hash(context)
    if context.get("context_status") != OCS_CONTEXT_ASSEMBLED:
        raise FailClosedRuntimeError("OCS cognition failed closed: OCS context is not assembled")
    if context.get("replay_visible") is not True:
        raise FailClosedRuntimeError("OCS cognition failed closed: OCS context is not replay-visible")
    if not isinstance(context.get("context_hash"), str) or not context["context_hash"].strip():
        raise FailClosedRuntimeError("OCS cognition failed closed: context hash is required")
    if context["context_hash"] != _compute_context_hash_for_validation(context):
        raise FailClosedRuntimeError("OCS cognition failed closed: OCS context hash mismatch")
    for flag in PROHIBITED_AUTHORITY_FLAGS:
        if context.get(flag) is True:
            raise FailClosedRuntimeError(f"OCS cognition failed closed: context carries prohibited authority flag {flag}")
    authority_flags = context.get("authority_flags")
    if not isinstance(authority_flags, dict):
        raise FailClosedRuntimeError("OCS cognition failed closed: context authority flags are required")
    for flag in AUTHORITY_FLAGS:
        if authority_flags.get(flag) is not False:
            raise FailClosedRuntimeError(f"OCS cognition failed closed: context authority flag must be false: {flag}")
    if not isinstance(context.get("accepted_inputs"), list):
        raise FailClosedRuntimeError("OCS cognition failed closed: accepted inputs are required")
    if not isinstance(context.get("context_sections"), list):
        raise FailClosedRuntimeError("OCS cognition failed closed: context sections are required")


def _analyze_context(context: dict[str, Any]) -> dict[str, Any]:
    accepted_inputs = deepcopy(context["accepted_inputs"])
    summaries = [entry.get("summary", {}) for entry in accepted_inputs if isinstance(entry, dict)]
    context_sections = deepcopy(context["context_sections"])

    domain_candidates = _domain_candidates(summaries, accepted_inputs)
    worker_candidates = _worker_candidates(summaries, accepted_inputs)
    task_intent = _task_intent(summaries, accepted_inputs, context_sections)
    ambiguity = _ambiguity(task_intent, domain_candidates, worker_candidates)
    clarification = _clarification_requirements(ambiguity, context_sections)
    provider_necessity = _provider_necessity(task_intent, ambiguity, summaries)

    return {
        "task_intent": task_intent,
        "ambiguity": ambiguity,
        "clarification_requirements": clarification,
        "domain_candidates": domain_candidates,
        "worker_candidates": worker_candidates,
        "provider_necessity": provider_necessity,
    }


def _task_intent(
    summaries: list[dict[str, Any]],
    accepted_inputs: list[dict[str, Any]],
    context_sections: list[dict[str, Any]],
) -> dict[str, Any]:
    if any(summary.get("ppp_resource_status") for summary in summaries):
        intent = "PPP_HANDOFF_INTENT"
        confidence = "HIGH"
        rationale = "PPP context is present."
    elif any("approval" in str(summary).lower() or "decision" in str(summary).lower() for summary in summaries):
        intent = "APPROVAL_CONTEXT_REVIEW"
        confidence = "MEDIUM"
        rationale = "Approval context is present."
    elif any(summary.get("resolution_status") or summary.get("domain_id") or summary.get("requested_domain") for summary in summaries):
        intent = "DOMAIN_CONTEXT_REVIEW"
        confidence = "MEDIUM"
        rationale = "Domain or registry context is present."
    elif any(entry.get("category") == "replay_visible_operation_context" for entry in accepted_inputs):
        intent = "REPLAY_CONTEXT_REVIEW"
        confidence = "MEDIUM"
        rationale = "Replay-visible operation context is present."
    elif any(section.get("category") == "conversation_context" and section.get("source_count", 0) > 0 for section in context_sections):
        intent = "CONVERSATION_CONTEXT_REVIEW"
        confidence = "LOW"
        rationale = "Conversation context is present without stronger downstream evidence."
    else:
        intent = "UNKNOWN_INTENT"
        confidence = "LOW"
        rationale = "No deterministic intent signal was found."
    return {
        "intent": intent,
        "confidence": confidence,
        "rationale": rationale,
        "authority": False,
    }


def _domain_candidates(summaries: list[dict[str, Any]], accepted_inputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: dict[str, set[str]] = {}
    for summary in summaries:
        for field in ("domain_id", "requested_domain"):
            domain = _normalize_domain(summary.get(field))
            if domain:
                candidates.setdefault(domain, set()).add(field)
        bundle_id = summary.get("bundle_id")
        if isinstance(bundle_id, str):
            for domain in KNOWN_DOMAINS:
                if bundle_id.upper().startswith(domain):
                    candidates.setdefault(domain, set()).add("bundle_id")
    for entry in accepted_inputs:
        text = f"{entry.get('source_id', '')} {entry.get('artifact_type', '')}".upper()
        for domain in KNOWN_DOMAINS:
            if domain in text:
                candidates.setdefault(domain, set()).add("source_reference")
    return [
        {
            "domain_id": domain,
            "confidence": "HIGH" if "domain_id" in sources or "requested_domain" in sources else "MEDIUM",
            "evidence": sorted(sources),
            "authority": False,
        }
        for domain, sources in sorted(candidates.items())
    ]


def _worker_candidates(summaries: list[dict[str, Any]], accepted_inputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: dict[str, set[str]] = {}
    for summary in summaries:
        for value in summary.values():
            if isinstance(value, str):
                _collect_worker_hints(value, candidates, "summary")
    for entry in accepted_inputs:
        _collect_worker_hints(str(entry.get("source_id", "")), candidates, "source_id")
        _collect_worker_hints(str(entry.get("artifact_type", "")), candidates, "artifact_type")
    return [
        {
            "worker_family_id": worker,
            "confidence": "MEDIUM",
            "evidence": sorted(sources),
            "authority": False,
        }
        for worker, sources in sorted(candidates.items())
    ]


def _ambiguity(
    task_intent: dict[str, Any],
    domain_candidates: list[dict[str, Any]],
    worker_candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    reasons: list[str] = []
    if task_intent["intent"] == "UNKNOWN_INTENT":
        reasons.append("task intent is unknown")
    if len(domain_candidates) > 1:
        reasons.append("multiple domain candidates")
    if len(worker_candidates) > 1:
        reasons.append("multiple worker candidates")
    return {
        "is_ambiguous": bool(reasons),
        "ambiguity_reasons": sorted(reasons),
        "authority": False,
    }


def _clarification_requirements(ambiguity: dict[str, Any], context_sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    requirements: list[dict[str, Any]] = []
    for reason in ambiguity["ambiguity_reasons"]:
        requirements.append(
            {
                "requirement_id": reason.upper().replace(" ", "_"),
                "reason": reason,
                "required": True,
                "authority": False,
            }
        )
    if not any(section.get("category") == "clarification_context" and section.get("source_count", 0) > 0 for section in context_sections):
        requirements.append(
            {
                "requirement_id": "CLARIFICATION_CONTEXT_NOT_PRESENT",
                "reason": "no clarification context was supplied",
                "required": bool(ambiguity["is_ambiguous"]),
                "authority": False,
            }
        )
    return sorted(requirements, key=lambda item: item["requirement_id"])


def _provider_necessity(
    task_intent: dict[str, Any],
    ambiguity: dict[str, Any],
    summaries: list[dict[str, Any]],
) -> dict[str, Any]:
    explicit = sorted(
        {
            summary["provider_necessity_classification"]
            for summary in summaries
            if isinstance(summary.get("provider_necessity_classification"), str)
        }
    )
    if len(explicit) == 1:
        classification = explicit[0]
        reason = "provider necessity was present in replay-visible context"
    elif len(explicit) > 1:
        classification = PROVIDER_UNDETERMINED
        reason = "conflicting provider necessity classifications"
    elif ambiguity["is_ambiguous"]:
        classification = PROVIDER_UNDETERMINED
        reason = "provider necessity cannot be determined while cognition is ambiguous"
    elif task_intent["intent"] == "PPP_HANDOFF_INTENT":
        classification = PROVIDER_REQUIRED
        reason = "PPP handoff intent requires proposal support before downstream validation"
    elif task_intent["intent"] == "REPLAY_CONTEXT_REVIEW":
        classification = PROVIDER_PROHIBITED
        reason = "replay context review must remain deterministic and evidence-bound"
    else:
        classification = PROVIDER_OPTIONAL
        reason = "context can be analyzed deterministically; provider proposal support is optional"
    return {
        "necessity_classification": classification,
        "reason": reason,
        "provider_invoked": False,
        "authority": False,
    }


def _cognition_artifact(
    *,
    cognition_id: str,
    context: dict[str, Any],
    analysis: dict[str, Any],
    created_at: str,
    cognition_status: str,
    failure_reason: str | None,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": OCS_COGNITION_ARTIFACT_V1,
        "runtime_version": AIGOL_OCS_COGNITION_RUNTIME_VERSION,
        "contract_reference": "AIGOL_OCS_BOUNDARY_AND_CONTEXT_ASSEMBLY_CONTRACT_V1",
        "cognition_id": _require_string(cognition_id, "cognition_id"),
        "source_context_assembly_id": context["context_assembly_id"],
        "source_context_artifact_hash": context["artifact_hash"],
        "source_context_hash": context["context_hash"],
        "task_intent": deepcopy(analysis["task_intent"]),
        "ambiguity": deepcopy(analysis["ambiguity"]),
        "clarification_requirements": deepcopy(analysis["clarification_requirements"]),
        "domain_candidates": deepcopy(analysis["domain_candidates"]),
        "worker_candidates": deepcopy(analysis["worker_candidates"]),
        "provider_necessity": deepcopy(analysis["provider_necessity"]),
        "cognition_status": cognition_status,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "created_at": _require_string(created_at, "created_at"),
        "replay_visible": True,
        "authority": False,
        "approval_created": False,
        "approval_inferred": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_assignment_requested": False,
        "worker_dispatch_requested": False,
        "worker_invocation_requested": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "domain_created": False,
        "governance_modified": False,
        "replay_modified": False,
        "failure_reason": failure_reason,
    }
    artifact["cognition_hash"] = _compute_cognition_hash(artifact)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _failed_cognition_artifact(
    *,
    cognition_id: str,
    context: dict[str, Any],
    created_at: str,
    failure_reason: str,
) -> dict[str, Any]:
    empty_analysis = {
        "task_intent": {
            "intent": "UNKNOWN_INTENT",
            "confidence": "LOW",
            "rationale": "OCS cognition failed closed before analysis completed.",
            "authority": False,
        },
        "ambiguity": {
            "is_ambiguous": True,
            "ambiguity_reasons": ["OCS cognition failed closed"],
            "authority": False,
        },
        "clarification_requirements": [
            {
                "requirement_id": "OCS_COGNITION_FAILED_CLOSED",
                "reason": failure_reason,
                "required": True,
                "authority": False,
            }
        ],
        "domain_candidates": [],
        "worker_candidates": [],
        "provider_necessity": {
            "necessity_classification": PROVIDER_UNDETERMINED,
            "reason": "OCS cognition failed closed",
            "provider_invoked": False,
            "authority": False,
        },
    }
    safe_context = {
        "context_assembly_id": context.get("context_assembly_id", "INVALID_CONTEXT_ASSEMBLY_ID"),
        "artifact_hash": context.get("artifact_hash", "INVALID_CONTEXT_ARTIFACT_HASH"),
        "context_hash": context.get("context_hash", "INVALID_CONTEXT_HASH"),
    }
    return _cognition_artifact(
        cognition_id=cognition_id,
        context=safe_context,
        analysis=empty_analysis,
        created_at=created_at,
        cognition_status=FAILED_CLOSED,
        failure_reason=failure_reason,
    )


def _returned_artifact(cognition: dict[str, Any]) -> dict[str, Any]:
    _verify_artifact_hash(cognition)
    returned = {
        "event_type": "OCS_COGNITION_RETURNED",
        "cognition_reference": cognition["cognition_id"],
        "cognition_artifact_hash": cognition["artifact_hash"],
        "cognition_status": cognition["cognition_status"],
        "cognition_hash": cognition["cognition_hash"],
        "source_context_hash": cognition["source_context_hash"],
        "task_intent": cognition["task_intent"]["intent"],
        "provider_necessity_classification": cognition["provider_necessity"]["necessity_classification"],
        "replay_visible": True,
        "authority": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
        "failure_reason": cognition["failure_reason"],
    }
    returned["artifact_hash"] = replay_hash(returned)
    return returned


def _capture(cognition: dict[str, Any], returned: dict[str, Any], replay_path: Path) -> dict[str, Any]:
    capture = {
        "ocs_cognition_artifact": deepcopy(cognition),
        "ocs_cognition_returned": deepcopy(returned),
        "ocs_cognition_replay_reference": str(replay_path),
        "cognition_status": cognition["cognition_status"],
        "cognition_hash": cognition["cognition_hash"],
        "source_context_hash": cognition["source_context_hash"],
        "task_intent": deepcopy(cognition["task_intent"]),
        "ambiguity": deepcopy(cognition["ambiguity"]),
        "clarification_requirements": deepcopy(cognition["clarification_requirements"]),
        "domain_candidates": deepcopy(cognition["domain_candidates"]),
        "worker_candidates": deepcopy(cognition["worker_candidates"]),
        "provider_necessity": deepcopy(cognition["provider_necessity"]),
        "fail_closed": cognition["cognition_status"] != OCS_COGNITION_COMPLETED,
        "failure_reason": cognition["failure_reason"],
        "provider_invoked": False,
        "worker_invoked": False,
        "execution_requested": False,
        "dispatch_requested": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    capture["ocs_cognition_capture_hash"] = replay_hash(capture)
    return capture


def _compute_cognition_hash(artifact: dict[str, Any]) -> str:
    return replay_hash(
        {
            "contract_reference": artifact["contract_reference"],
            "source_context_assembly_id": artifact["source_context_assembly_id"],
            "source_context_artifact_hash": artifact["source_context_artifact_hash"],
            "source_context_hash": artifact["source_context_hash"],
            "task_intent": artifact["task_intent"],
            "ambiguity": artifact["ambiguity"],
            "clarification_requirements": artifact["clarification_requirements"],
            "domain_candidates": artifact["domain_candidates"],
            "worker_candidates": artifact["worker_candidates"],
            "provider_necessity": artifact["provider_necessity"],
            "cognition_status": artifact["cognition_status"],
            "authority_flags": artifact["authority_flags"],
            "failure_reason": artifact["failure_reason"],
        }
    )


def _compute_context_hash_for_validation(context: dict[str, Any]) -> str:
    return replay_hash(
        {
            "contract_reference": context["contract_reference"],
            "source_chain_id": context.get("source_chain_id"),
            "source_request_reference": context.get("source_request_reference"),
            "input_categories": context["input_categories"],
            "accepted_inputs": context["accepted_inputs"],
            "rejected_inputs": context["rejected_inputs"],
            "context_sections": context["context_sections"],
            "normalization_policy": context["normalization_policy"],
            "known_gaps": context["known_gaps"],
            "authority_flags": context["authority_flags"],
            "context_status": context["context_status"],
            "failure_reason": context["failure_reason"],
        }
    )


def _collect_worker_hints(value: str, candidates: dict[str, set[str]], source: str) -> None:
    normalized = value.upper()
    for hint in WORKER_HINTS:
        if hint in normalized:
            candidates.setdefault(hint, set()).add(source)


def _normalize_domain(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip().upper().replace(" ", "_").replace("-", "_")
    if normalized in KNOWN_DOMAINS:
        return normalized
    return None


def _ensure_replay_available(replay_path: Path) -> None:
    for index, step in enumerate(REPLAY_STEPS):
        path = replay_path / f"{index:03d}_{step}.json"
        if path.exists():
            raise FailClosedRuntimeError(f"append-only runtime artifact already exists: {path.name}")


def _persist_step(replay_dir: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    if REPLAY_STEPS[index] != step:
        raise FailClosedRuntimeError("OCS cognition replay step ordering mismatch")
    _verify_artifact_hash(artifact)
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


def _verify_artifact_hash(artifact: dict[str, Any]) -> None:
    if "artifact_hash" not in artifact:
        raise FailClosedRuntimeError("OCS cognition artifact hash is required")
    expected_input = deepcopy(artifact)
    actual = expected_input.pop("artifact_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("OCS cognition artifact hash mismatch")


def _verify_wrapper_hash(wrapper: dict[str, Any]) -> None:
    if "replay_hash" not in wrapper:
        raise FailClosedRuntimeError("OCS cognition replay hash is required")
    expected_input = deepcopy(wrapper)
    actual = expected_input.pop("replay_hash")
    if actual != replay_hash(expected_input):
        raise FailClosedRuntimeError("OCS cognition replay hash mismatch")


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()


def _failure_reason(exc: Exception) -> str:
    if isinstance(exc, FailClosedRuntimeError):
        return str(exc)
    return "OCS cognition failed closed"
