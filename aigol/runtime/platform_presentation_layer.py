"""Canonical Platform Presentation Layer for Platform Core responses.

The layer normalizes existing Platform Core response artifacts into one
presentation model. It does not create semantic content, select services,
traverse replay, invoke providers or workers, or replace the runtimes whose
responses it presents.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_query_router import PLATFORM_QUERY_ROUTER_RESPONSE_ARTIFACT_V1
from aigol.runtime.transport.serialization import replay_hash


PLATFORM_PRESENTATION_LAYER_VERSION = "G19_06_CANONICAL_PLATFORM_PRESENTATION_LAYER_V1"
CANONICAL_PLATFORM_PRESENTATION_ARTIFACT_V1 = "CANONICAL_PLATFORM_PRESENTATION_ARTIFACT_V1"

PLATFORM_KNOWLEDGE_RESPONSE_ARTIFACT_V1 = "PLATFORM_KNOWLEDGE_RESPONSE_ARTIFACT_V1"
ROOT_CAUSE_TRACE_RESPONSE_ARTIFACT_V1 = "PLATFORM_CORE_ROOT_CAUSE_TRACE_ARTIFACT_V1"
GOVERNED_DEVELOPMENT_RESPONSE_ARTIFACT_V1 = (
    "PLATFORM_CORE_DEVELOPMENT_INTENT_RESOLUTION_ARTIFACT_V1"
)

PLATFORM_KNOWLEDGE_SERVICE = "PLATFORM_KNOWLEDGE_RUNTIME"
ROOT_CAUSE_TRACE_SERVICE = "DETERMINISTIC_ROOT_CAUSE_TRACE_RUNTIME"
GOVERNED_DEVELOPMENT_SERVICE = "GOVERNED_DEVELOPMENT_RUNTIME"
PLATFORM_QUERY_ROUTER_SERVICE = "UNIFIED_PLATFORM_QUERY_ROUTER"

PRESENTATION_READY = "PRESENTATION_READY"
PRESENTATION_MISSING_EVIDENCE = "PRESENTATION_MISSING_EVIDENCE"
PRESENTATION_CLARIFICATION_REQUIRED = "PRESENTATION_CLARIFICATION_REQUIRED"
PRESENTATION_FAILED_CLOSED = "PRESENTATION_FAILED_CLOSED"

PRESENTATION_BOUNDARY_FLAGS = {
    "read_only": True,
    "composition_layer_only": True,
    "platform_core_authority": True,
    "human_interface_authority": False,
    "semantic_content_invented": False,
    "platform_knowledge_replaced": False,
    "root_cause_trace_replaced": False,
    "governed_development_replaced": False,
    "human_conversation_experience_duplicated": False,
    "replay_metadata_duplicated": False,
    "governance_modified": False,
    "replay_modified": False,
    "provider_invoked": False,
    "worker_invoked": False,
}


def present_platform_response(
    response: dict[str, Any],
    *,
    created_at: str = "2026-07-11T00:00:00Z",
) -> dict[str, Any]:
    """Normalize a Platform Core response into a canonical presentation artifact."""

    if not isinstance(response, dict):
        raise FailClosedRuntimeError("platform presentation source response must be a dict")
    source = deepcopy(response)
    router_response = source if source.get("artifact_type") == PLATFORM_QUERY_ROUTER_RESPONSE_ARTIFACT_V1 else None
    service_response = _service_response_from_source(source)
    adapter_result = _presentation_from_response(
        service_response=service_response,
        router_response=router_response,
    )
    source_response_hash = _source_response_hash(source)
    selected_service = _selected_service(
        service_response=service_response,
        router_response=router_response,
    )
    artifact = {
        "artifact_type": CANONICAL_PLATFORM_PRESENTATION_ARTIFACT_V1,
        "presentation_version": PLATFORM_PRESENTATION_LAYER_VERSION,
        "created_at": _require_string(created_at, "created_at"),
        "query": _query_from_sources(service_response=service_response, router_response=router_response),
        "query_hash": _query_hash_from_sources(
            service_response=service_response,
            router_response=router_response,
        ),
        "service": selected_service,
        "selected_service": selected_service,
        "source_artifact_type": service_response.get("artifact_type"),
        "source_response_hash": source_response_hash,
        "router_response_hash": router_response.get("artifact_hash") if isinstance(router_response, dict) else None,
        "presentation_status": adapter_result["presentation_status"],
        "summary": adapter_result["summary"],
        "answer": adapter_result["answer"],
        "confidence": adapter_result["confidence"],
        "evidence": adapter_result["evidence"],
        "reasoning_path": adapter_result["reasoning_path"],
        "sources": adapter_result["sources"],
        "recommended_next_step": adapter_result["recommended_next_step"],
        "certification_status": adapter_result["certification_status"],
        "governance_status": adapter_result["governance_status"],
        "replay_status": adapter_result["replay_status"],
        "warnings": adapter_result["warnings"],
        "actions": adapter_result["actions"],
        "reusable_components": adapter_result["reusable_components"],
        "boundary_flags": deepcopy(PRESENTATION_BOUNDARY_FLAGS),
        **PRESENTATION_BOUNDARY_FLAGS,
    }
    artifact["presentation_hash"] = replay_hash(artifact)
    return artifact


def validate_platform_presentation(response: dict[str, Any]) -> dict[str, Any]:
    """Validate a canonical presentation artifact."""

    if not isinstance(response, dict):
        raise FailClosedRuntimeError("platform presentation artifact must be a dict")
    if response.get("artifact_type") != CANONICAL_PLATFORM_PRESENTATION_ARTIFACT_V1:
        raise FailClosedRuntimeError("platform presentation artifact type is invalid")
    if response.get("presentation_version") != PLATFORM_PRESENTATION_LAYER_VERSION:
        raise FailClosedRuntimeError("platform presentation version is invalid")
    for field_name, expected in PRESENTATION_BOUNDARY_FLAGS.items():
        if response.get(field_name) is not expected:
            raise FailClosedRuntimeError("platform presentation boundary flags invalid")
        boundary_flags = response.get("boundary_flags")
        if not isinstance(boundary_flags, dict) or boundary_flags.get(field_name) is not expected:
            raise FailClosedRuntimeError("platform presentation boundary flags invalid")
    for field_name in (
        "service",
        "presentation_status",
        "summary",
        "answer",
        "confidence",
        "evidence",
        "reasoning_path",
        "sources",
        "recommended_next_step",
        "reusable_components",
    ):
        if field_name not in response:
            raise FailClosedRuntimeError("platform presentation mandatory field missing")
    presentation_hash = response.get("presentation_hash")
    if not isinstance(presentation_hash, str) or not presentation_hash.startswith("sha256:"):
        raise FailClosedRuntimeError("platform presentation hash is required")
    body = deepcopy(response)
    body.pop("presentation_hash", None)
    if replay_hash(body) != presentation_hash:
        raise FailClosedRuntimeError("platform presentation hash mismatch")
    return deepcopy(response)


def _presentation_from_response(
    *,
    service_response: dict[str, Any],
    router_response: dict[str, Any] | None,
) -> dict[str, Any]:
    if isinstance(router_response, dict) and not isinstance(router_response.get("service_response"), dict):
        return _router_only_presentation(router_response)
    artifact_type = service_response.get("artifact_type")
    if artifact_type == PLATFORM_KNOWLEDGE_RESPONSE_ARTIFACT_V1:
        return _knowledge_presentation(service_response, router_response=router_response)
    if artifact_type == ROOT_CAUSE_TRACE_RESPONSE_ARTIFACT_V1:
        return _root_cause_presentation(service_response, router_response=router_response)
    if artifact_type == GOVERNED_DEVELOPMENT_RESPONSE_ARTIFACT_V1:
        return _governed_development_presentation(service_response, router_response=router_response)
    raise FailClosedRuntimeError("platform presentation unsupported source artifact type")


def _knowledge_presentation(
    response: dict[str, Any],
    *,
    router_response: dict[str, Any] | None,
) -> dict[str, Any]:
    capability = response.get("canonical_capability_identifier") or response.get("goal_target") or "platform capability"
    if response.get("certified_capability_exists") is True:
        summary = f"{capability} exists as a certified Platform capability."
    elif response.get("capability_exists") is True:
        summary = f"{capability} exists in Platform project knowledge."
    else:
        summary = f"{capability} was not resolved to existing Platform capability evidence."
    evidence = _source_evidence(response.get("source_evidence"))
    for source in response.get("certification_evidence", ()) or ():
        evidence.append(
            {
                "source_type": "CERTIFICATION_EVIDENCE",
                "reference": str(source),
                "status": response.get("certification_status"),
            }
        )
    sources = [str(item.get("reference") or item.get("source_type")) for item in evidence]
    recommended = (
        f"Reuse {response.get('recommended_platform_service')}."
        if response.get("recommended_platform_service")
        else "Ask a more specific Platform capability question."
    )
    return _adapter_result(
        presentation_status=PRESENTATION_READY,
        summary=summary,
        answer={
            "capability_exists": response.get("capability_exists"),
            "certified_capability_exists": response.get("certified_capability_exists"),
            "capability_owner": response.get("capability_owner"),
            "architectural_owner": response.get("architectural_owner"),
            "implementation_owner": response.get("implementation_owner"),
            "recommended_platform_service": response.get("recommended_platform_service"),
            "reuse_recommended": response.get("reuse_recommended"),
            "knowledge_reuse_classification": response.get("knowledge_reuse_classification"),
        },
        confidence="CERTIFIED" if response.get("is_certified") is True else "PROJECT_KNOWLEDGE_EVIDENCE",
        evidence=evidence,
        reasoning_path=_router_reasoning(router_response)
        + [
            {
                "step": "PLATFORM_KNOWLEDGE_RESPONSE",
                "query_classification": response.get("query_classification"),
                "source_precedence": deepcopy(response.get("source_precedence")),
            }
        ],
        sources=sources,
        recommended_next_step=recommended,
        certification_status=response.get("certification_status"),
        governance_status=None,
        replay_status="REPLAY_METADATA_REFERENCED" if response.get("replay_authority_preserved") else None,
        warnings=list(response.get("unknown_or_missing_evidence") or []),
        actions=[recommended],
        reusable_components=[
            "PLATFORM_KNOWLEDGE_RUNTIME",
            "CAPABILITY_CERTIFICATION_REGISTRY",
            "PLATFORM_CORE_PROJECT_SERVICES",
            "PROJECT_KNOWLEDGE_REUSE",
            "PCCL_REFERENCE_METADATA",
        ],
    )


def _root_cause_presentation(
    response: dict[str, Any],
    *,
    router_response: dict[str, Any] | None,
) -> dict[str, Any]:
    trace_ready = response.get("trace_status") == "ROOT_CAUSE_TRACE_READY"
    missing = deepcopy(response.get("missing_evidence") or [])
    contradictory = deepcopy(response.get("contradictory_evidence") or [])
    replay_sources = [str(source) for source in response.get("replay_sources_inspected", [])]
    evidence = []
    if isinstance(response.get("source_artifact"), dict):
        evidence.append({"source_type": "SOURCE_ARTIFACT", "artifact": deepcopy(response["source_artifact"])})
    if isinstance(response.get("source_projection"), dict):
        evidence.append({"source_type": "SOURCE_PROJECTION", "artifact": deepcopy(response["source_projection"])})
    for item in missing:
        evidence.append({"source_type": "MISSING_EVIDENCE", **deepcopy(item)})
    for item in contradictory:
        evidence.append({"source_type": "CONTRADICTORY_EVIDENCE", **deepcopy(item)})
    for source in replay_sources:
        evidence.append({"source_type": "REPLAY_SOURCE", "reference": source})
    status = PRESENTATION_READY if trace_ready else PRESENTATION_FAILED_CLOSED
    return _adapter_result(
        presentation_status=status,
        summary=str(response.get("root_cause_explanation") or "Root-cause trace did not provide an explanation."),
        answer={
            "observed_result": deepcopy(response.get("observed_result")),
            "producing_component": response.get("producing_component"),
            "runtime_stage": deepcopy(response.get("runtime_stage")),
            "governance_decision": deepcopy(response.get("governance_decision")),
            "originating_request": deepcopy(response.get("originating_request")),
            "replay_backed": response.get("replay_backed"),
            "fail_closed": response.get("fail_closed") is True,
        },
        confidence="REPLAY_BACKED" if response.get("replay_backed") is True else "FAILED_CLOSED",
        evidence=evidence,
        reasoning_path=_router_reasoning(router_response)
        + [
            {"step": "OBSERVED_RESULT", "value": deepcopy(response.get("observed_result"))},
            {"step": "RUNTIME_STAGE", "value": deepcopy(response.get("runtime_stage"))},
            {"step": "GOVERNANCE_DECISION", "value": deepcopy(response.get("governance_decision"))},
            {"step": "CAUSAL_PREDECESSORS", "value": deepcopy(response.get("causal_predecessors") or [])},
        ],
        sources=[str(response.get("replay_reference"))] + replay_sources,
        recommended_next_step=(
            "Inspect the traced source artifact."
            if trace_ready
            else "Provide replay or runtime evidence required by the trace."
        ),
        certification_status=None,
        governance_status=_governance_status(response.get("governance_decision")),
        replay_status="REPLAY_BACKED" if response.get("replay_backed") is True else "REPLAY_EVIDENCE_MISSING",
        warnings=missing + contradictory,
        actions=[
            "Inspect the traced source artifact."
            if trace_ready
            else "Provide replay or runtime evidence required by the trace."
        ],
        reusable_components=[
            "DETERMINISTIC_ROOT_CAUSE_TRACE_RUNTIME",
            "REPLAY_EVIDENCE",
            "GOVERNANCE_EVIDENCE",
            "RUNTIME_PROJECTION_EVIDENCE",
        ],
    )


def _governed_development_presentation(
    response: dict[str, Any],
    *,
    router_response: dict[str, Any] | None,
) -> dict[str, Any]:
    if response.get("clarification_required") is True:
        status = PRESENTATION_CLARIFICATION_REQUIRED
        summary = "Clarification is required before governed development can proceed."
        recommended = "Provide the missing deterministic implementation detail."
        confidence = "CLARIFICATION_REQUIRED"
    elif response.get("summary_admissible") is True:
        status = PRESENTATION_READY
        summary = "Governed development handoff is ready for human approval."
        recommended = "Review and approve the governed implementation summary before runtime execution."
        confidence = "APPROVAL_REQUIRED"
    else:
        status = PRESENTATION_FAILED_CLOSED
        summary = "Governed development did not produce an approval-ready summary."
        recommended = "Refine the request before governed runtime execution."
        confidence = "FAILED_CLOSED"
    evidence = [
        {
            "source_type": "DEVELOPMENT_INTENT_RESOLUTION",
            "artifact_hash": response.get("artifact_hash"),
            "summary_admissible": response.get("summary_admissible"),
            "runtime_binding_admissible": response.get("runtime_binding_admissible"),
            "clarification_required": response.get("clarification_required"),
        }
    ]
    if isinstance(response.get("candidate_capability_discovery"), dict):
        evidence.append(
            {
                "source_type": "CAPABILITY_DISCOVERY",
                "artifact": deepcopy(response.get("candidate_capability_discovery")),
            }
        )
    return _adapter_result(
        presentation_status=status,
        summary=summary,
        answer={
            "raw_prompt": response.get("raw_prompt"),
            "canonical_runtime_prompt": response.get("canonical_runtime_prompt"),
            "summary_admissible": response.get("summary_admissible"),
            "runtime_binding_admissible": response.get("runtime_binding_admissible"),
            "requires_human_approval": response.get("requires_human_approval"),
            "router_handoff_status": response.get("router_handoff_status"),
            "runtime_execution_invoked": response.get("runtime_execution_invoked"),
            "clarification_reason": response.get("clarification_reason"),
        },
        confidence=confidence,
        evidence=evidence,
        reasoning_path=_router_reasoning(router_response)
        + [
            {"step": "DEVELOPMENT_INTENT_RESOLUTION", "artifact_hash": response.get("artifact_hash")},
            {"step": "CAPABILITY_RESOLUTION", "value": response.get("capability_resolution_decision")},
        ],
        sources=[str(response.get("artifact_hash"))],
        recommended_next_step=recommended,
        certification_status=None,
        governance_status="PENDING_HUMAN_APPROVAL" if response.get("requires_human_approval") else None,
        replay_status="REPLAY_VISIBLE" if response.get("replay_visible") is True else None,
        warnings=[response.get("clarification_reason")] if response.get("clarification_reason") else [],
        actions=[recommended],
        reusable_components=[
            "GOVERNED_DEVELOPMENT_RUNTIME",
            "PLATFORM_CORE_PROJECT_SERVICES",
            "HUMAN_CONVERSATION_EXPERIENCE",
            "CAPABILITY_DISCOVERY",
        ],
    )


def _router_only_presentation(router_response: dict[str, Any]) -> dict[str, Any]:
    route_status = str(router_response.get("route_status") or "")
    if route_status == "REQUIRED_EVIDENCE_MISSING":
        status = PRESENTATION_MISSING_EVIDENCE
        summary = "The selected Platform service requires additional evidence before it can answer."
        recommended = "Provide the missing required evidence."
        confidence = "MISSING_EVIDENCE"
    elif route_status == "ROUTE_CLARIFICATION_REQUIRED":
        status = PRESENTATION_CLARIFICATION_REQUIRED
        summary = "The Platform query route is ambiguous and requires clarification."
        recommended = "Clarify which Platform capability or runtime result should be answered."
        confidence = "CLARIFICATION_REQUIRED"
    else:
        status = PRESENTATION_FAILED_CLOSED
        summary = "The Platform query did not produce a service response."
        recommended = "Resubmit with a supported Platform query and required evidence."
        confidence = "FAILED_CLOSED"
    evidence = [
        {
            "source_type": "ROUTER_RESPONSE",
            "route_status": router_response.get("route_status"),
            "selected_service": router_response.get("selected_service"),
            "required_evidence_missing": deepcopy(router_response.get("required_evidence_missing") or []),
        }
    ]
    return _adapter_result(
        presentation_status=status,
        summary=summary,
        answer={
            "selected_service": router_response.get("selected_service"),
            "route_status": router_response.get("route_status"),
            "selected_query_class": router_response.get("selected_query_class"),
            "required_evidence_missing": deepcopy(router_response.get("required_evidence_missing") or []),
            "ambiguity_detected": router_response.get("ambiguity_detected") is True,
        },
        confidence=confidence,
        evidence=evidence,
        reasoning_path=_router_reasoning(router_response),
        sources=[str(router_response.get("artifact_hash"))],
        recommended_next_step=recommended,
        certification_status=None,
        governance_status=None,
        replay_status=None,
        warnings=list(router_response.get("required_evidence_missing") or []),
        actions=[recommended],
        reusable_components=["UNIFIED_PLATFORM_QUERY_ROUTER"],
    )


def _adapter_result(
    *,
    presentation_status: str,
    summary: str,
    answer: dict[str, Any],
    confidence: str,
    evidence: list[dict[str, Any]],
    reasoning_path: list[dict[str, Any]],
    sources: list[str],
    recommended_next_step: str,
    certification_status: str | None,
    governance_status: str | None,
    replay_status: str | None,
    warnings: list[Any],
    actions: list[str],
    reusable_components: list[str],
) -> dict[str, Any]:
    return {
        "presentation_status": _require_string(presentation_status, "presentation_status"),
        "summary": _require_string(summary, "summary"),
        "answer": deepcopy(answer),
        "confidence": _require_string(confidence, "confidence"),
        "evidence": deepcopy(evidence),
        "reasoning_path": deepcopy(reasoning_path),
        "sources": [str(source) for source in sources if source not in (None, "None", "")],
        "recommended_next_step": _require_string(recommended_next_step, "recommended_next_step"),
        "certification_status": certification_status,
        "governance_status": governance_status,
        "replay_status": replay_status,
        "warnings": [warning for warning in warnings if warning],
        "actions": [str(action) for action in actions if action],
        "reusable_components": [str(component) for component in reusable_components],
    }


def _service_response_from_source(source: dict[str, Any]) -> dict[str, Any]:
    if source.get("artifact_type") == PLATFORM_QUERY_ROUTER_RESPONSE_ARTIFACT_V1:
        service_response = source.get("service_response")
        if isinstance(service_response, dict):
            return deepcopy(service_response)
        return {
            "artifact_type": PLATFORM_QUERY_ROUTER_RESPONSE_ARTIFACT_V1,
            "query": source.get("query"),
            "query_hash": source.get("query_hash"),
        }
    return deepcopy(source)


def _selected_service(
    *,
    service_response: dict[str, Any],
    router_response: dict[str, Any] | None,
) -> str:
    if isinstance(router_response, dict) and router_response.get("selected_service"):
        return str(router_response["selected_service"])
    artifact_type = service_response.get("artifact_type")
    if artifact_type == PLATFORM_KNOWLEDGE_RESPONSE_ARTIFACT_V1:
        return PLATFORM_KNOWLEDGE_SERVICE
    if artifact_type == ROOT_CAUSE_TRACE_RESPONSE_ARTIFACT_V1:
        return ROOT_CAUSE_TRACE_SERVICE
    if artifact_type == GOVERNED_DEVELOPMENT_RESPONSE_ARTIFACT_V1:
        return GOVERNED_DEVELOPMENT_SERVICE
    if artifact_type == PLATFORM_QUERY_ROUTER_RESPONSE_ARTIFACT_V1:
        return PLATFORM_QUERY_ROUTER_SERVICE
    raise FailClosedRuntimeError("platform presentation cannot infer selected service")


def _query_from_sources(
    *,
    service_response: dict[str, Any],
    router_response: dict[str, Any] | None,
) -> str | None:
    if isinstance(router_response, dict) and isinstance(router_response.get("query"), str):
        return str(router_response["query"])
    for field_name in ("query", "raw_prompt", "governed_request"):
        value = service_response.get(field_name)
        if isinstance(value, str) and value.strip():
            return value
    return None


def _query_hash_from_sources(
    *,
    service_response: dict[str, Any],
    router_response: dict[str, Any] | None,
) -> str | None:
    if isinstance(router_response, dict) and isinstance(router_response.get("query_hash"), str):
        return str(router_response["query_hash"])
    if isinstance(service_response.get("query_hash"), str):
        return str(service_response["query_hash"])
    query = _query_from_sources(service_response=service_response, router_response=router_response)
    return replay_hash(query) if isinstance(query, str) else None


def _source_response_hash(source: dict[str, Any]) -> str:
    for field_name in ("artifact_hash", "trace_hash", "presentation_hash"):
        value = source.get(field_name)
        if isinstance(value, str) and value.startswith("sha256:"):
            return value
    if source.get("artifact_type") == PLATFORM_QUERY_ROUTER_RESPONSE_ARTIFACT_V1:
        service_hash = source.get("service_response_hash")
        if isinstance(service_hash, str) and service_hash.startswith("sha256:"):
            return service_hash
    return replay_hash(source)


def _source_evidence(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [deepcopy(item) for item in value if isinstance(item, dict)]


def _router_reasoning(router_response: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(router_response, dict):
        return []
    return [
        {
            "step": "PLATFORM_QUERY_ROUTER",
            "route_status": router_response.get("route_status"),
            "selected_service": router_response.get("selected_service"),
            "selected_query_class": router_response.get("selected_query_class"),
            "selected_route_score": router_response.get("selected_route_score"),
            "candidate_routes": deepcopy(router_response.get("candidate_routes") or []),
        }
    ]


def _governance_status(value: Any) -> str | None:
    if not isinstance(value, dict):
        return None
    for field_name in ("authorization_status", "governance_status", "decision_status"):
        if value.get(field_name):
            return str(value[field_name])
    return None


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
