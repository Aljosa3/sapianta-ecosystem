"""Unified Platform Query Router for Platform Core services.

The router selects an existing Platform Core service for a platform query. It
does not own service logic, perform runtime diagnostics itself, execute
governed development, invoke providers or workers, or mutate replay.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_composition_coverage import (
    PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_VERSION,
    discover_platform_capability_composition_coverage,
)
from aigol.runtime.platform_development_composition_plan import (
    PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_VERSION,
    compose_platform_development_plan_for_query,
)
from aigol.runtime.platform_project_objective_inference import (
    PLATFORM_PROJECT_OBJECTIVE_INFERENCE_VERSION,
    infer_platform_project_objective,
)
from aigol.runtime.platform_durable_governed_work import (
    PLATFORM_DURABLE_GOVERNED_WORK_VERSION,
    compose_durable_governed_work,
)
from aigol.runtime.generation_certification_composition import (
    GENERATION_CERTIFICATION_COMPOSITION_VERSION,
    compose_generation_certification,
)
from aigol.runtime.platform_core_project_services import (
    PLATFORM_CORE_PROJECT_SERVICES_VERSION,
    resolve_development_intent,
)
from aigol.runtime.platform_core_root_cause_trace import (
    PLATFORM_CORE_ROOT_CAUSE_TRACE_VERSION,
    trace_platform_core_root_cause,
)
from aigol.runtime.platform_knowledge_runtime import (
    PLATFORM_KNOWLEDGE_RUNTIME_VERSION,
    query_platform_knowledge,
)
from aigol.runtime.transport.serialization import replay_hash


PLATFORM_QUERY_ROUTER_VERSION = "G19_04_UNIFIED_PLATFORM_QUERY_ROUTER_V1"
PLATFORM_QUERY_ROUTER_RESPONSE_ARTIFACT_V1 = "PLATFORM_QUERY_ROUTER_RESPONSE_ARTIFACT_V1"

ROUTE_READY = "ROUTE_READY"
REQUIRED_EVIDENCE_MISSING = "REQUIRED_EVIDENCE_MISSING"
ROUTE_CLARIFICATION_REQUIRED = "ROUTE_CLARIFICATION_REQUIRED"

PLATFORM_KNOWLEDGE_ROUTE = "PLATFORM_KNOWLEDGE_RUNTIME"
ROOT_CAUSE_TRACE_ROUTE = "DETERMINISTIC_ROOT_CAUSE_TRACE_RUNTIME"
GOVERNED_DEVELOPMENT_ROUTE = "GOVERNED_DEVELOPMENT_RUNTIME"
GENERATION_CERTIFICATION_ROUTE = "GENERATION_CERTIFICATION_COMPOSITION_SERVICE"
CAPABILITY_COMPOSITION_COVERAGE_ROUTE = "PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME"
DEVELOPMENT_COMPOSITION_PLAN_ROUTE = "PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_RUNTIME"
PROJECT_OBJECTIVE_INFERENCE_ROUTE = "PLATFORM_PROJECT_OBJECTIVE_INFERENCE_RUNTIME"
DURABLE_GOVERNED_WORK_ROUTE = "PLATFORM_DURABLE_GOVERNED_WORK_RUNTIME"


ROUTER_BOUNDARY_FLAGS = {
    "platform_core_authority": True,
    "human_interface_authority": False,
    "human_interface_selects_service": False,
    "composition_layer_only": True,
    "semantic_interpretation_owned": False,
    "platform_knowledge_replaced": False,
    "root_cause_trace_replaced": False,
    "governed_development_replaced": False,
    "runtime_diagnostics_performed_by_router": False,
    "governance_modified": False,
    "replay_modified": False,
    "provider_invoked": False,
    "worker_invoked": False,
}


@dataclass(frozen=True)
class PlatformServiceRouteDescriptor:
    """Deterministic route descriptor for one Platform Core service."""

    service_identifier: str
    service_owner: str
    implementation_owner: str
    query_classes: tuple[str, ...]
    required_inputs: tuple[str, ...]
    response_artifact_type: str
    service_version: str
    adapter_name: str
    routing_terms: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        descriptor = {
            "service_identifier": _require_string(self.service_identifier, "service_identifier"),
            "service_owner": _require_string(self.service_owner, "service_owner"),
            "implementation_owner": _require_string(self.implementation_owner, "implementation_owner"),
            "query_classes": _string_tuple(self.query_classes, "query_classes"),
            "required_inputs": tuple(str(item) for item in self.required_inputs),
            "response_artifact_type": _require_string(
                self.response_artifact_type,
                "response_artifact_type",
            ),
            "service_version": _require_string(self.service_version, "service_version"),
            "adapter_name": _require_string(self.adapter_name, "adapter_name"),
            "routing_terms": tuple(str(item) for item in self.routing_terms),
            "route_descriptor_authority": "PLATFORM_CORE",
            "human_interface_authority": False,
            "provider_invoked": False,
            "worker_invoked": False,
            "replay_modified": False,
            "governance_modified": False,
        }
        descriptor["route_descriptor_hash"] = replay_hash(descriptor)
        return descriptor


PLATFORM_QUERY_ROUTE_DESCRIPTORS = (
    PlatformServiceRouteDescriptor(
        service_identifier=DURABLE_GOVERNED_WORK_ROUTE,
        service_owner="PLATFORM_CORE_DEVELOPMENT_LIFECYCLE",
        implementation_owner="aigol.runtime.platform_durable_governed_work",
        query_classes=("DURABLE_GOVERNED_WORK",),
        required_inputs=("query",),
        response_artifact_type="PLATFORM_DURABLE_GOVERNED_WORK_ARTIFACT_V1",
        service_version=PLATFORM_DURABLE_GOVERNED_WORK_VERSION,
        adapter_name="_route_durable_governed_work",
        routing_terms=(
            "durable governed work",
            "durable work artifact",
            "approval-ready governed work",
        ),
    ),
    PlatformServiceRouteDescriptor(
        service_identifier=PROJECT_OBJECTIVE_INFERENCE_ROUTE,
        service_owner="PLATFORM_CORE_HUMAN_INTENT",
        implementation_owner="aigol.runtime.platform_project_objective_inference",
        query_classes=("PROJECT_OBJECTIVE_INFERENCE",),
        required_inputs=("query",),
        response_artifact_type="PLATFORM_CORE_PROJECT_OBJECTIVE_INFERENCE_ARTIFACT_V1",
        service_version=PLATFORM_PROJECT_OBJECTIVE_INFERENCE_VERSION,
        adapter_name="_route_project_objective_inference",
        routing_terms=(
            "project objective inference",
            "infer project objective",
            "objective sufficiency",
        ),
    ),
    PlatformServiceRouteDescriptor(
        service_identifier=DEVELOPMENT_COMPOSITION_PLAN_ROUTE,
        service_owner="PLATFORM_CORE_DEVELOPMENT_PLANNING",
        implementation_owner="aigol.runtime.platform_development_composition_plan",
        query_classes=("DEVELOPMENT_COMPOSITION_PLAN",),
        required_inputs=("query",),
        response_artifact_type="PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_ARTIFACT_V1",
        service_version=PLATFORM_DEVELOPMENT_COMPOSITION_PLAN_VERSION,
        adapter_name="_route_development_composition_plan",
        routing_terms=(
            "development composition plan",
            "governed development plan",
            "platform development plan",
            "ordered implementation sequence",
            "implementation dependency graph",
        ),
    ),
    PlatformServiceRouteDescriptor(
        service_identifier=CAPABILITY_COMPOSITION_COVERAGE_ROUTE,
        service_owner="PLATFORM_CORE_CAPABILITY_DISCOVERY",
        implementation_owner="aigol.runtime.platform_capability_composition_coverage",
        query_classes=("CAPABILITY_COMPOSITION_DISCOVERY",),
        required_inputs=("query",),
        response_artifact_type="PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_ARTIFACT_V1",
        service_version=PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_VERSION,
        adapter_name="_route_capability_composition_coverage",
        routing_terms=(
            "capability composition",
            "composition coverage",
            "composition discovery",
            "reusable capabilities",
            "residual gap",
            "minimal platform composition",
        ),
    ),
    PlatformServiceRouteDescriptor(
        service_identifier=GENERATION_CERTIFICATION_ROUTE,
        service_owner="PLATFORM_CORE_CERTIFICATION",
        implementation_owner="aigol.runtime.generation_certification_composition",
        query_classes=("GENERATION_CERTIFICATION",),
        required_inputs=("query",),
        response_artifact_type="GENERATION_CERTIFICATION_RESULT_V1",
        service_version=GENERATION_CERTIFICATION_COMPOSITION_VERSION,
        adapter_name="_route_generation_certification",
        routing_terms=(
            "generation certification",
            "certify generation",
            "generation certified",
            "generation evidence profile",
        ),
    ),
    PlatformServiceRouteDescriptor(
        service_identifier=PLATFORM_KNOWLEDGE_ROUTE,
        service_owner="PLATFORM_CORE_KNOWLEDGE",
        implementation_owner="aigol.runtime.platform_knowledge_runtime",
        query_classes=("ARCHITECTURAL_KNOWLEDGE", "CERTIFICATION_METADATA", "SERVICE_OWNERSHIP"),
        required_inputs=("query",),
        response_artifact_type="PLATFORM_KNOWLEDGE_RESPONSE_ARTIFACT_V1",
        service_version=PLATFORM_KNOWLEDGE_RUNTIME_VERSION,
        adapter_name="_route_platform_knowledge",
        routing_terms=("does", "exist", "where", "implemented", "owner", "owns", "certified", "service", "capability"),
    ),
    PlatformServiceRouteDescriptor(
        service_identifier=ROOT_CAUSE_TRACE_ROUTE,
        service_owner="PLATFORM_CORE_REPLAY",
        implementation_owner="aigol.runtime.platform_core_root_cause_trace",
        query_classes=("RUNTIME_CAUSALITY", "FAILURE_EXPLANATION", "REPLAY_BACKED_TRACE"),
        required_inputs=("query", "runtime_or_replay_evidence"),
        response_artifact_type="PLATFORM_CORE_ROOT_CAUSE_TRACE_ARTIFACT_V1",
        service_version=PLATFORM_CORE_ROOT_CAUSE_TRACE_VERSION,
        adapter_name="_route_root_cause_trace",
        routing_terms=(
            "why",
            "explain",
            "failure",
            "failed",
            "false",
            "runtime result",
            "root cause",
            "cause",
            "worker_execution_reached",
            "provider_invocation_reached",
            "replay_certification_reached",
            "runtime_status",
        ),
    ),
    PlatformServiceRouteDescriptor(
        service_identifier=GOVERNED_DEVELOPMENT_ROUTE,
        service_owner="PLATFORM_CORE_RUNTIME",
        implementation_owner="aigol.runtime.platform_core_project_services",
        query_classes=("GOVERNED_DEVELOPMENT_INTENT", "IMPLEMENTATION_REQUEST"),
        required_inputs=("query", "human_approval_after_summary"),
        response_artifact_type="PLATFORM_CORE_DEVELOPMENT_INTENT_RESOLUTION_ARTIFACT_V1",
        service_version=PLATFORM_CORE_PROJECT_SERVICES_VERSION,
        adapter_name="_route_governed_development",
        routing_terms=("implement", "build", "add", "change", "modify", "refine", "improve", "create"),
    ),
)


def platform_query_route_descriptors() -> list[dict[str, Any]]:
    """Return routable Platform Core service descriptors."""

    return [descriptor.to_dict() for descriptor in PLATFORM_QUERY_ROUTE_DESCRIPTORS]


def route_platform_query(
    *,
    query: str,
    workspace_state: dict[str, Any] | None = None,
    capability_identifier: str | None = None,
    goal_target: str | None = None,
    observed_field: str | None = None,
    observed_value: Any = None,
    failure_reason: str | None = None,
    artifact_reference: str | None = None,
    replay_reference: str | None = None,
    runtime_result: dict[str, Any] | None = None,
    user_visible_result: dict[str, Any] | None = None,
    generation_identifier: str | None = None,
    generation_evidence_profile: dict[str, Any] | None = None,
    composition_replay_evidence: list[dict[str, Any]] | None = None,
    governance_root: str = ".",
    created_at: str = "2026-07-11T00:00:00Z",
    route_descriptors: list[PlatformServiceRouteDescriptor] | tuple[PlatformServiceRouteDescriptor, ...] | None = None,
    route_adapters: dict[str, Callable[..., dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    """Classify a platform query and dispatch to the selected Platform Core service."""

    raw_query = _require_string(query, "query")
    descriptors = _descriptors(route_descriptors)
    knowledge_probe = query_platform_knowledge(
        query=raw_query,
        capability_identifier=capability_identifier,
        goal_target=goal_target,
        workspace_state=workspace_state,
    )
    development_intent = resolve_development_intent(
        message=raw_query,
        workspace_state=workspace_state,
    )
    candidates = _candidate_routes(
        query=raw_query,
        descriptors=descriptors,
        knowledge_probe=knowledge_probe,
        development_intent=development_intent,
        runtime_or_replay_evidence_supplied=_runtime_or_replay_evidence_supplied(
            observed_field=observed_field,
            failure_reason=failure_reason,
            artifact_reference=artifact_reference,
            replay_reference=replay_reference,
            runtime_result=runtime_result,
            user_visible_result=user_visible_result,
        ),
    )
    selected = _select_route(candidates)
    route_status = _route_status(selected, candidates)
    selected_descriptor = _descriptor_for_service(descriptors, selected["service_identifier"])
    if route_status == ROUTE_READY:
        service_response = _invoke_route(
            selected_service=selected["service_identifier"],
            query=raw_query,
            workspace_state=workspace_state,
            capability_identifier=capability_identifier,
            goal_target=goal_target,
            observed_field=observed_field,
            observed_value=observed_value,
            failure_reason=failure_reason,
            artifact_reference=artifact_reference,
            replay_reference=replay_reference,
            runtime_result=runtime_result,
            user_visible_result=user_visible_result,
            generation_identifier=generation_identifier,
            generation_evidence_profile=generation_evidence_profile,
            composition_replay_evidence=composition_replay_evidence,
            governance_root=governance_root,
            created_at=created_at,
            knowledge_probe=knowledge_probe,
            development_intent=development_intent,
            route_adapters=route_adapters,
        )
    else:
        service_response = None
    response = {
        "artifact_type": PLATFORM_QUERY_ROUTER_RESPONSE_ARTIFACT_V1,
        "platform_query_router_version": PLATFORM_QUERY_ROUTER_VERSION,
        "query": raw_query,
        "query_hash": replay_hash(raw_query),
        "created_at": _require_string(created_at, "created_at"),
        "route_status": route_status,
        "selected_service": selected["service_identifier"],
        "selected_query_class": selected["query_class"],
        "selected_route_score": selected["score"],
        "selected_route_descriptor": selected_descriptor,
        "candidate_routes": candidates,
        "required_evidence_missing": _required_evidence_missing(selected, route_status),
        "ambiguity_detected": route_status == ROUTE_CLARIFICATION_REQUIRED,
        "classification_evidence": {
            "platform_knowledge_query_classification": knowledge_probe["query_classification"],
            "platform_knowledge_artifact_hash": knowledge_probe["artifact_hash"],
            "development_intent_summary_admissible": development_intent["summary_admissible"],
            "development_intent_runtime_binding_admissible": development_intent[
                "runtime_binding_admissible"
            ],
            "development_intent_clarification_required": development_intent["clarification_required"],
            "development_intent_artifact_hash": development_intent["artifact_hash"],
        },
        "service_response": service_response,
        "service_response_hash": _service_response_hash(service_response),
        "service_invoked": service_response is not None,
        "future_services_registerable": True,
        "route_descriptors": [descriptor.to_dict() for descriptor in descriptors],
        **ROUTER_BOUNDARY_FLAGS,
    }
    response["artifact_hash"] = replay_hash(response)
    return response


def validate_platform_query_router_response(response: dict[str, Any]) -> dict[str, Any]:
    """Validate a router response artifact."""

    if not isinstance(response, dict):
        raise FailClosedRuntimeError("platform query router response must be a dict")
    if response.get("artifact_type") != PLATFORM_QUERY_ROUTER_RESPONSE_ARTIFACT_V1:
        raise FailClosedRuntimeError("platform query router response artifact type is invalid")
    if response.get("platform_query_router_version") != PLATFORM_QUERY_ROUTER_VERSION:
        raise FailClosedRuntimeError("platform query router response version is invalid")
    for field_name, expected in ROUTER_BOUNDARY_FLAGS.items():
        if response.get(field_name) is not expected:
            raise FailClosedRuntimeError("platform query router boundary flags invalid")
    artifact_hash = response.get("artifact_hash")
    if not isinstance(artifact_hash, str) or not artifact_hash.startswith("sha256:"):
        raise FailClosedRuntimeError("platform query router response hash is required")
    body = deepcopy(response)
    body.pop("artifact_hash", None)
    if replay_hash(body) != artifact_hash:
        raise FailClosedRuntimeError("platform query router response hash mismatch")
    return deepcopy(response)


def _route_platform_knowledge(
    *,
    query: str,
    workspace_state: dict[str, Any] | None,
    capability_identifier: str | None,
    goal_target: str | None,
    knowledge_probe: dict[str, Any],
    **_: Any,
) -> dict[str, Any]:
    if capability_identifier is None and goal_target is None:
        return deepcopy(knowledge_probe)
    return query_platform_knowledge(
        query=query,
        capability_identifier=capability_identifier,
        goal_target=goal_target,
        workspace_state=workspace_state,
    )


def _route_root_cause_trace(
    *,
    query: str,
    observed_field: str | None,
    observed_value: Any,
    failure_reason: str | None,
    artifact_reference: str | None,
    replay_reference: str | None,
    runtime_result: dict[str, Any] | None,
    user_visible_result: dict[str, Any] | None,
    created_at: str,
    **_: Any,
) -> dict[str, Any]:
    return trace_platform_core_root_cause(
        observed_field=observed_field or _observed_field_from_query(query),
        observed_value=observed_value,
        failure_reason=failure_reason,
        artifact_reference=artifact_reference,
        replay_reference=replay_reference,
        runtime_result=runtime_result,
        user_visible_result=user_visible_result,
        created_at=created_at,
    )


def _route_governed_development(
    *,
    development_intent: dict[str, Any],
    **_: Any,
) -> dict[str, Any]:
    response = deepcopy(development_intent)
    response["router_handoff_status"] = "GOVERNED_DEVELOPMENT_HANDOFF_PREPARED"
    response["runtime_execution_invoked"] = False
    response["requires_human_approval_before_execution"] = response.get("requires_human_approval") is True
    return response


def _route_generation_certification(
    *,
    query: str,
    workspace_state: dict[str, Any] | None,
    generation_identifier: str | None,
    generation_evidence_profile: dict[str, Any] | None,
    governance_root: str,
    created_at: str,
    **_: Any,
) -> dict[str, Any]:
    return compose_generation_certification(
        generation_identifier=generation_identifier or _generation_identifier_from_query(query),
        generation_evidence_profile=generation_evidence_profile,
        query=query,
        workspace_state=workspace_state,
        governance_root=governance_root,
        created_at=created_at,
    )


def _route_capability_composition_coverage(
    *,
    query: str,
    workspace_state: dict[str, Any] | None,
    composition_replay_evidence: list[dict[str, Any]] | None,
    governance_root: str,
    created_at: str,
    **_: Any,
) -> dict[str, Any]:
    return discover_platform_capability_composition_coverage(
        query=query,
        workspace_state=workspace_state,
        replay_evidence=composition_replay_evidence,
        governance_root=governance_root,
        created_at=created_at,
    )


def _route_development_composition_plan(
    *,
    query: str,
    workspace_state: dict[str, Any] | None,
    composition_replay_evidence: list[dict[str, Any]] | None,
    governance_root: str,
    created_at: str,
    **_: Any,
) -> dict[str, Any]:
    return compose_platform_development_plan_for_query(
        query=query,
        workspace_state=workspace_state,
        replay_evidence=composition_replay_evidence,
        governance_root=governance_root,
        created_at=created_at,
    )


def _route_durable_governed_work(
    *,
    query: str,
    workspace_state: dict[str, Any] | None,
    composition_replay_evidence: list[dict[str, Any]] | None,
    governance_root: str,
    created_at: str,
    development_intent: dict[str, Any],
    **_: Any,
) -> dict[str, Any]:
    plan = compose_platform_development_plan_for_query(
        query=query,
        workspace_state=workspace_state,
        replay_evidence=composition_replay_evidence,
        governance_root=governance_root,
        created_at=created_at,
    )
    return compose_durable_governed_work(
        development_plan_artifact=plan,
        source_work_type=str(development_intent.get("work_type") or "AUDIT_ONLY"),
        created_at=created_at,
    )


def _route_project_objective_inference(
    *,
    query: str,
    workspace_state: dict[str, Any] | None,
    development_intent: dict[str, Any],
    created_at: str,
    **_: Any,
) -> dict[str, Any]:
    return infer_platform_project_objective(
        request=query,
        development_intent=development_intent,
        workspace_state=workspace_state,
        created_at=created_at,
    )


ROUTE_ADAPTERS: dict[str, Callable[..., dict[str, Any]]] = {
    DURABLE_GOVERNED_WORK_ROUTE: _route_durable_governed_work,
    PROJECT_OBJECTIVE_INFERENCE_ROUTE: _route_project_objective_inference,
    DEVELOPMENT_COMPOSITION_PLAN_ROUTE: _route_development_composition_plan,
    CAPABILITY_COMPOSITION_COVERAGE_ROUTE: _route_capability_composition_coverage,
    GENERATION_CERTIFICATION_ROUTE: _route_generation_certification,
    PLATFORM_KNOWLEDGE_ROUTE: _route_platform_knowledge,
    ROOT_CAUSE_TRACE_ROUTE: _route_root_cause_trace,
    GOVERNED_DEVELOPMENT_ROUTE: _route_governed_development,
}


def _candidate_routes(
    *,
    query: str,
    descriptors: tuple[PlatformServiceRouteDescriptor, ...],
    knowledge_probe: dict[str, Any],
    development_intent: dict[str, Any],
    runtime_or_replay_evidence_supplied: bool,
) -> list[dict[str, Any]]:
    lowered = query.lower()
    candidates = [
        _candidate(
            service_identifier=DURABLE_GOVERNED_WORK_ROUTE,
            query_class="DURABLE_GOVERNED_WORK",
            score=_durable_governed_work_score(lowered),
            required_evidence_available=True,
            reason="Durable Governed Work binds a validated plan to reviewable lifecycle evidence.",
        ),
        _candidate(
            service_identifier=PROJECT_OBJECTIVE_INFERENCE_ROUTE,
            query_class="PROJECT_OBJECTIVE_INFERENCE",
            score=_project_objective_inference_score(lowered),
            required_evidence_available=True,
            reason="Project Objective Inference composes complete-request objective evidence.",
        ),
        _candidate(
            service_identifier=DEVELOPMENT_COMPOSITION_PLAN_ROUTE,
            query_class="DEVELOPMENT_COMPOSITION_PLAN",
            score=_development_composition_plan_score(lowered),
            required_evidence_available=True,
            reason="Development Composition Plan derives ordered governed work from capability coverage.",
        ),
        _candidate(
            service_identifier=CAPABILITY_COMPOSITION_COVERAGE_ROUTE,
            query_class="CAPABILITY_COMPOSITION_DISCOVERY",
            score=_capability_composition_coverage_score(lowered),
            required_evidence_available=True,
            reason="Capability Composition Coverage resolves reusable capabilities and residual gaps.",
        ),
        _candidate(
            service_identifier=GENERATION_CERTIFICATION_ROUTE,
            query_class="GENERATION_CERTIFICATION",
            score=_generation_certification_score(lowered),
            required_evidence_available=True,
            reason="Generation Certification composes deterministic Platform Core certification evidence.",
        ),
        _candidate(
            service_identifier=PLATFORM_KNOWLEDGE_ROUTE,
            query_class="ARCHITECTURAL_KNOWLEDGE",
            score=_knowledge_score(lowered, knowledge_probe),
            required_evidence_available=True,
            reason="Platform Knowledge handles architectural, certification, owner, and service metadata queries.",
        ),
        _candidate(
            service_identifier=ROOT_CAUSE_TRACE_ROUTE,
            query_class="RUNTIME_CAUSALITY",
            score=_root_cause_score(lowered),
            required_evidence_available=runtime_or_replay_evidence_supplied,
            missing_required_inputs=()
            if runtime_or_replay_evidence_supplied
            else ("runtime_or_replay_evidence",),
            reason="Root Cause Trace handles replay-backed runtime result explanations.",
        ),
        _candidate(
            service_identifier=GOVERNED_DEVELOPMENT_ROUTE,
            query_class="GOVERNED_DEVELOPMENT_INTENT",
            score=_development_score(lowered, development_intent),
            required_evidence_available=True,
            reason="Governed Development handles implementation/change requests through approval-gated runtime.",
        ),
    ]
    built_in_services = {
        DURABLE_GOVERNED_WORK_ROUTE,
        PROJECT_OBJECTIVE_INFERENCE_ROUTE,
        PLATFORM_KNOWLEDGE_ROUTE,
        ROOT_CAUSE_TRACE_ROUTE,
        GOVERNED_DEVELOPMENT_ROUTE,
        GENERATION_CERTIFICATION_ROUTE,
        CAPABILITY_COMPOSITION_COVERAGE_ROUTE,
        DEVELOPMENT_COMPOSITION_PLAN_ROUTE,
    }
    for descriptor in descriptors:
        if descriptor.service_identifier in built_in_services:
            continue
        evidence_available, missing_inputs = _descriptor_required_evidence_available(
            descriptor=descriptor,
            runtime_or_replay_evidence_supplied=runtime_or_replay_evidence_supplied,
        )
        candidates.append(
            _candidate(
                service_identifier=descriptor.service_identifier,
                query_class=descriptor.query_classes[0],
                score=_descriptor_score(lowered, descriptor),
                required_evidence_available=evidence_available,
                missing_required_inputs=missing_inputs,
                reason="Future Platform Core service descriptor matched deterministic routing terms.",
            )
        )
    return sorted(candidates, key=lambda item: (-int(item["score"]), item["service_identifier"]))


def _candidate(
    *,
    service_identifier: str,
    query_class: str,
    score: int,
    required_evidence_available: bool,
    reason: str,
    missing_required_inputs: tuple[str, ...] = (),
) -> dict[str, Any]:
    return {
        "service_identifier": service_identifier,
        "query_class": query_class,
        "score": int(score),
        "required_evidence_available": required_evidence_available,
        "missing_required_inputs": tuple(str(item) for item in missing_required_inputs),
        "routing_reason": reason,
    }


def _knowledge_score(query: str, knowledge_probe: dict[str, Any]) -> int:
    terms = ("does", "exist", "where", "implemented", "owner", "owns", "certified", "service", "capability")
    score = 20 + sum(15 for term in terms if term in query)
    if knowledge_probe.get("certified_capability_exists") is True:
        score += 25
    if knowledge_probe.get("project_capability_detected") is True:
        score += 10
    return min(score, 95)


def _root_cause_score(query: str) -> int:
    terms = ("why", "explain", "failure", "failed", "false", "runtime result", "root cause", "cause")
    score = sum(20 for term in terms if term in query)
    observed_result_terms = (
        "worker_execution_reached",
        "provider_invocation_reached",
        "replay_certification_reached",
        "runtime_status",
    )
    if any(term in query for term in observed_result_terms):
        score += 35
    return min(score, 100)


def _development_score(query: str, development_intent: dict[str, Any]) -> int:
    if any(
        phrase in query
        for phrase in (
            "development composition plan",
            "governed development plan",
            "platform development plan",
            "ordered implementation sequence",
            "implementation dependency graph",
        )
    ):
        return 0
    terms = ("implement", "build", "add", "change", "modify", "refine", "improve", "create")
    score = sum(18 for term in terms if term in query)
    if development_intent.get("summary_admissible") is True:
        score += 35
    if development_intent.get("clarification_required") is True:
        score -= 15
    return max(0, min(score, 100))


def _generation_certification_score(query: str) -> int:
    phrases = (
        "generation certification",
        "certify generation",
        "generation certified",
        "generation evidence profile",
    )
    return min(100, sum(35 for phrase in phrases if phrase in query))


def _capability_composition_coverage_score(query: str) -> int:
    phrases = (
        "capability composition",
        "composition coverage",
        "composition discovery",
        "reusable capabilities",
        "residual gap",
        "minimal platform composition",
    )
    return min(100, sum(30 for phrase in phrases if phrase in query))


def _development_composition_plan_score(query: str) -> int:
    phrases = (
        "development composition plan",
        "governed development plan",
        "platform development plan",
        "ordered implementation sequence",
        "implementation dependency graph",
    )
    matches = sum(1 for phrase in phrases if phrase in query)
    return min(100, matches * 55 + (45 if matches else 0))


def _project_objective_inference_score(query: str) -> int:
    phrases = (
        "project objective inference",
        "infer project objective",
        "objective sufficiency",
    )
    return min(100, sum(35 for phrase in phrases if phrase in query))


def _durable_governed_work_score(query: str) -> int:
    phrases = (
        "durable governed work",
        "durable work artifact",
        "approval-ready governed work",
    )
    matches = sum(1 for phrase in phrases if phrase in query)
    return min(100, matches * 55 + (45 if matches else 0))


def _descriptor_score(query: str, descriptor: PlatformServiceRouteDescriptor) -> int:
    return min(100, sum(20 for term in descriptor.routing_terms if str(term).lower() in query))


def _select_route(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    if not candidates:
        raise FailClosedRuntimeError("platform query router has no candidate routes")
    return deepcopy(candidates[0])


def _route_status(selected: dict[str, Any], candidates: list[dict[str, Any]]) -> str:
    top_score = int(selected["score"])
    if top_score <= 0:
        return ROUTE_CLARIFICATION_REQUIRED
    tied = [
        candidate
        for candidate in candidates
        if int(candidate["score"]) == top_score
    ]
    if len(tied) > 1:
        return ROUTE_CLARIFICATION_REQUIRED
    if selected.get("required_evidence_available") is not True:
        return REQUIRED_EVIDENCE_MISSING
    return ROUTE_READY


def _required_evidence_missing(selected: dict[str, Any], route_status: str) -> list[str]:
    if route_status != REQUIRED_EVIDENCE_MISSING:
        return []
    missing = selected.get("missing_required_inputs")
    if isinstance(missing, tuple) and missing:
        return list(missing)
    return ["required_route_evidence"]


def _invoke_route(
    *,
    selected_service: str,
    route_adapters: dict[str, Callable[..., dict[str, Any]]] | None,
    **kwargs: Any,
) -> dict[str, Any]:
    adapters = dict(ROUTE_ADAPTERS)
    if route_adapters is not None:
        adapters.update(route_adapters)
    adapter = adapters.get(selected_service)
    if adapter is None:
        raise FailClosedRuntimeError("platform query router selected service has no adapter")
    return adapter(**kwargs)


def _descriptor_required_evidence_available(
    *,
    descriptor: PlatformServiceRouteDescriptor,
    runtime_or_replay_evidence_supplied: bool,
) -> tuple[bool, tuple[str, ...]]:
    missing_inputs: list[str] = []
    for required_input in descriptor.required_inputs:
        if required_input == "query":
            continue
        if required_input == "runtime_or_replay_evidence" and runtime_or_replay_evidence_supplied:
            continue
        if required_input == "human_approval_after_summary":
            continue
        missing_inputs.append(str(required_input))
    return not missing_inputs, tuple(missing_inputs)


def _runtime_or_replay_evidence_supplied(
    *,
    observed_field: str | None,
    failure_reason: str | None,
    artifact_reference: str | None,
    replay_reference: str | None,
    runtime_result: dict[str, Any] | None,
    user_visible_result: dict[str, Any] | None,
) -> bool:
    return any(
        [
            isinstance(observed_field, str) and bool(observed_field.strip()),
            isinstance(failure_reason, str) and bool(failure_reason.strip()),
            isinstance(artifact_reference, str) and bool(artifact_reference.strip()),
            isinstance(replay_reference, str) and bool(replay_reference.strip()),
            isinstance(runtime_result, dict),
            isinstance(user_visible_result, dict),
        ]
    )


def _observed_field_from_query(query: str) -> str | None:
    for field in (
        "worker_execution_reached",
        "provider_invocation_reached",
        "replay_certification_reached",
        "runtime_status",
    ):
        if field in query:
            return field
    return None


def _generation_identifier_from_query(query: str) -> str:
    lowered = query.lower().replace("-", " ").replace("_", " ")
    tokens = lowered.split()
    for index, token in enumerate(tokens[:-1]):
        if token == "generation" and tokens[index + 1].isdigit():
            return f"GENERATION_{tokens[index + 1]}"
    return "GENERATION_19"


def _service_response_hash(service_response: dict[str, Any] | None) -> str | None:
    if not isinstance(service_response, dict):
        return None
    for key in ("artifact_hash", "trace_hash"):
        value = service_response.get(key)
        if isinstance(value, str) and value.startswith("sha256:"):
            return value
    return replay_hash(service_response)


def _descriptors(
    route_descriptors: list[PlatformServiceRouteDescriptor] | tuple[PlatformServiceRouteDescriptor, ...] | None,
) -> tuple[PlatformServiceRouteDescriptor, ...]:
    return tuple(route_descriptors) if route_descriptors is not None else PLATFORM_QUERY_ROUTE_DESCRIPTORS


def _descriptor_for_service(
    descriptors: tuple[PlatformServiceRouteDescriptor, ...],
    service_identifier: str,
) -> dict[str, Any]:
    for descriptor in descriptors:
        if descriptor.service_identifier == service_identifier:
            return descriptor.to_dict()
    raise FailClosedRuntimeError("platform query router missing route descriptor")


def _string_tuple(values: tuple[str, ...], field_name: str) -> tuple[str, ...]:
    if not isinstance(values, tuple) or not values:
        raise FailClosedRuntimeError(f"{field_name} is required")
    return tuple(_require_string(value, field_name) for value in values)


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field_name} is required")
    return value.strip()
