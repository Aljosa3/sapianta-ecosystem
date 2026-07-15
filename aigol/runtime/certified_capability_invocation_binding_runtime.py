"""Bounded invocation binding for certified read-only Platform Core capabilities."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable

from aigol.runtime.governed_repository_mutation_runtime import (
    GOVERNED_REPOSITORY_MUTATION_PROPOSAL_ARTIFACT_V1,
)
from aigol.runtime.implementation_manifest_runtime import IMPLEMENTATION_MANIFEST_ARTIFACT_V1
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_composition_coverage import (
    COVERAGE_FAILED_CLOSED,
    PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_ARTIFACT_V1,
    PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_REQUEST_ARTIFACT_V1,
    discover_platform_capability_composition_coverage,
    validate_platform_capability_composition_coverage,
    validate_platform_capability_composition_coverage_request,
)
from aigol.runtime.platform_capability_certification_registry import (
    CERTIFIED_STATES,
    PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION,
    lookup_platform_capability_certification,
)
from aigol.runtime.platform_change_impact_analysis_runtime import (
    FAILED_CLOSED as IMPACT_FAILED_CLOSED,
    PLATFORM_CHANGE_IMPACT_ARTIFACT_V1,
    analyze_platform_change_impact,
    validate_platform_change_impact_artifact,
)
from aigol.runtime.platform_change_normalization_runtime import (
    FAILED_CLOSED as NORMALIZATION_FAILED_CLOSED,
    NORMALIZED_CHANGE_ARTIFACT_V1,
    normalize_platform_change,
    validate_normalized_change_artifact,
)
from aigol.runtime.platform_knowledge_runtime import (
    PLATFORM_KNOWLEDGE_RESPONSE_ARTIFACT_V1,
    validate_platform_knowledge_response,
)
from aigol.runtime.platform_validation_planning_runtime import (
    FAILED_CLOSED as PLANNING_FAILED_CLOSED,
    PLATFORM_VALIDATION_PLAN_ARTIFACT_V1,
    plan_platform_validation,
    validate_platform_validation_plan_artifact,
)
from aigol.runtime.transport.serialization import load_json, replay_hash, write_json_immutable


CERTIFIED_CAPABILITY_INVOCATION_BINDING_RUNTIME_VERSION = (
    "G28_02_CERTIFIED_CAPABILITY_INVOCATION_BINDING_RUNTIME_V1"
)
CERTIFIED_CAPABILITY_INVOCATION_RESULT_ARTIFACT_V1 = (
    "CERTIFIED_CAPABILITY_INVOCATION_RESULT_ARTIFACT_V1"
)
CERTIFIED_CAPABILITY_INVOCATION_COMPLETED = "CERTIFIED_CAPABILITY_INVOCATION_COMPLETED"
FAILED_CLOSED = "FAILED_CLOSED"

PLATFORM_CHANGE_NORMALIZATION = "PLATFORM_CHANGE_NORMALIZATION"
PLATFORM_CHANGE_IMPACT_ANALYSIS = "PLATFORM_CHANGE_IMPACT_ANALYSIS"
PLATFORM_VALIDATION_PLANNING = "PLATFORM_VALIDATION_PLANNING"
PLATFORM_CAPABILITY_COMPOSITION_COVERAGE = (
    "PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME"
)

REPLAY_STEPS = (
    "platform_knowledge_discovery_source_recorded",
    "certified_capability_resolution_recorded",
    "invocation_adapter_selection_recorded",
    "validated_capability_inputs_recorded",
    "capability_invocation_result_recorded",
    "capability_invocation_returned",
)

AUTHORITY_FLAGS = {
    "human_interface_authority": False,
    "discovery_treated_as_authorization": False,
    "authorizes_execution": False,
    "authorizes_worker_invocation": False,
    "authorizes_provider_invocation": False,
    "authorizes_repository_mutation": False,
    "invokes_workers": False,
    "invokes_providers": False,
    "mutates_repository": False,
    "certifies_results": False,
    "uses_dynamic_imports": False,
    "uses_arbitrary_execution": False,
}


AdapterCallable = Callable[[str, dict[str, Any], str, Path], dict[str, Any]]


@dataclass(frozen=True)
class CapabilityInvocationAdapter:
    capability_identifier: str
    adapter_identifier: str
    canonical_entry_point: str
    accepted_input_artifact_types: tuple[str, ...]
    required_input_fields: tuple[str, ...]
    output_artifact_type: str
    output_capture_field: str
    output_reference_field: str
    output_status_field: str
    failed_status: str
    invoke: AdapterCallable

    def metadata(self) -> dict[str, Any]:
        artifact = {
            "capability_identifier": self.capability_identifier,
            "adapter_identifier": self.adapter_identifier,
            "canonical_entry_point": self.canonical_entry_point,
            "accepted_input_artifact_types": list(self.accepted_input_artifact_types),
            "required_input_fields": list(self.required_input_fields),
            "output_artifact_type": self.output_artifact_type,
            "mutation_status": "READ_ONLY_NO_REPOSITORY_MUTATION",
            "approval_requirement": "NOT_REQUIRED",
            "governance_requirement": "EXISTING_CAPABILITY_BOUNDARY",
            "replay_policy": "CANONICAL_BINDING_SUBDIRECTORY",
            "worker_invocation_allowed": False,
            "provider_invocation_allowed": False,
            "dynamic_import_allowed": False,
        }
        artifact["adapter_metadata_hash"] = replay_hash(artifact)
        return artifact


def _invoke_normalization(
    invocation_id: str,
    inputs: dict[str, Any],
    invoked_at: str,
    replay_dir: Path,
) -> dict[str, Any]:
    return normalize_platform_change(
        normalization_id=invocation_id,
        source_artifact=inputs["source_artifact"],
        source_reference=inputs["source_reference"],
        source_hash=inputs["source_hash"],
        created_at=invoked_at,
        replay_dir=replay_dir,
    )


def _invoke_impact_analysis(
    invocation_id: str,
    inputs: dict[str, Any],
    invoked_at: str,
    replay_dir: Path,
) -> dict[str, Any]:
    return analyze_platform_change_impact(
        impact_analysis_id=invocation_id,
        normalized_change_artifact=inputs["normalized_change_artifact"],
        normalized_change_reference=inputs["normalized_change_reference"],
        normalized_change_hash=inputs["normalized_change_hash"],
        created_at=invoked_at,
        replay_dir=replay_dir,
    )


def _invoke_validation_planning(
    invocation_id: str,
    inputs: dict[str, Any],
    invoked_at: str,
    replay_dir: Path,
) -> dict[str, Any]:
    return plan_platform_validation(
        validation_plan_id=invocation_id,
        platform_change_impact_artifact=inputs["platform_change_impact_artifact"],
        platform_change_impact_reference=inputs["platform_change_impact_reference"],
        platform_change_impact_hash=inputs["platform_change_impact_hash"],
        created_at=invoked_at,
        replay_dir=replay_dir,
    )


def _invoke_capability_composition_coverage(
    invocation_id: str,
    inputs: dict[str, Any],
    invoked_at: str,
    replay_dir: Path,
) -> dict[str, Any]:
    del invocation_id
    request = validate_platform_capability_composition_coverage_request(
        inputs["composition_coverage_request_artifact"]
    )
    artifact = discover_platform_capability_composition_coverage(
        query=request["query"],
        created_at=invoked_at,
    )
    wrapper = {
        "replay_index": 0,
        "replay_step": "platform_capability_composition_coverage_recorded",
        "artifact": deepcopy(artifact),
    }
    wrapper["wrapper_hash"] = replay_hash(wrapper)
    write_json_immutable(
        replay_dir / "000_platform_capability_composition_coverage_recorded.json",
        wrapper,
    )
    return {"platform_capability_composition_coverage_artifact": artifact}


_ADAPTERS = MappingProxyType(
    {
        PLATFORM_CAPABILITY_COMPOSITION_COVERAGE: CapabilityInvocationAdapter(
            capability_identifier=PLATFORM_CAPABILITY_COMPOSITION_COVERAGE,
            adapter_identifier=(
                "G30_02_PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_ADAPTER_V1"
            ),
            canonical_entry_point=(
                "aigol.runtime.platform_capability_composition_coverage."
                "discover_platform_capability_composition_coverage"
            ),
            accepted_input_artifact_types=(
                PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_REQUEST_ARTIFACT_V1,
            ),
            required_input_fields=(
                "composition_coverage_request_artifact",
                "composition_coverage_request_reference",
                "composition_coverage_request_hash",
            ),
            output_artifact_type=PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_ARTIFACT_V1,
            output_capture_field="platform_capability_composition_coverage_artifact",
            output_reference_field="query_hash",
            output_status_field="coverage_status",
            failed_status=COVERAGE_FAILED_CLOSED,
            invoke=_invoke_capability_composition_coverage,
        ),
        PLATFORM_CHANGE_NORMALIZATION: CapabilityInvocationAdapter(
            capability_identifier=PLATFORM_CHANGE_NORMALIZATION,
            adapter_identifier="G28_02_PLATFORM_CHANGE_NORMALIZATION_ADAPTER_V1",
            canonical_entry_point=(
                "aigol.runtime.platform_change_normalization_runtime.normalize_platform_change"
            ),
            accepted_input_artifact_types=(
                IMPLEMENTATION_MANIFEST_ARTIFACT_V1,
                GOVERNED_REPOSITORY_MUTATION_PROPOSAL_ARTIFACT_V1,
            ),
            required_input_fields=("source_artifact", "source_reference", "source_hash"),
            output_artifact_type=NORMALIZED_CHANGE_ARTIFACT_V1,
            output_capture_field="normalized_change_artifact",
            output_reference_field="normalization_id",
            output_status_field="normalization_status",
            failed_status=NORMALIZATION_FAILED_CLOSED,
            invoke=_invoke_normalization,
        ),
        PLATFORM_CHANGE_IMPACT_ANALYSIS: CapabilityInvocationAdapter(
            capability_identifier=PLATFORM_CHANGE_IMPACT_ANALYSIS,
            adapter_identifier="G28_02_PLATFORM_CHANGE_IMPACT_ANALYSIS_ADAPTER_V1",
            canonical_entry_point=(
                "aigol.runtime.platform_change_impact_analysis_runtime.analyze_platform_change_impact"
            ),
            accepted_input_artifact_types=(NORMALIZED_CHANGE_ARTIFACT_V1,),
            required_input_fields=(
                "normalized_change_artifact",
                "normalized_change_reference",
                "normalized_change_hash",
            ),
            output_artifact_type=PLATFORM_CHANGE_IMPACT_ARTIFACT_V1,
            output_capture_field="platform_change_impact_artifact",
            output_reference_field="impact_analysis_id",
            output_status_field="impact_status",
            failed_status=IMPACT_FAILED_CLOSED,
            invoke=_invoke_impact_analysis,
        ),
        PLATFORM_VALIDATION_PLANNING: CapabilityInvocationAdapter(
            capability_identifier=PLATFORM_VALIDATION_PLANNING,
            adapter_identifier="G28_02_PLATFORM_VALIDATION_PLANNING_ADAPTER_V1",
            canonical_entry_point=(
                "aigol.runtime.platform_validation_planning_runtime.plan_platform_validation"
            ),
            accepted_input_artifact_types=(PLATFORM_CHANGE_IMPACT_ARTIFACT_V1,),
            required_input_fields=(
                "platform_change_impact_artifact",
                "platform_change_impact_reference",
                "platform_change_impact_hash",
            ),
            output_artifact_type=PLATFORM_VALIDATION_PLAN_ARTIFACT_V1,
            output_capture_field="platform_validation_plan_artifact",
            output_reference_field="validation_plan_id",
            output_status_field="planning_status",
            failed_status=PLANNING_FAILED_CLOSED,
            invoke=_invoke_validation_planning,
        ),
    }
)


def certified_capability_invocation_adapters() -> dict[str, dict[str, Any]]:
    """Return immutable adapter metadata without exposing callable objects."""

    return {
        capability_id: adapter.metadata()
        for capability_id, adapter in sorted(_ADAPTERS.items())
    }


_SEMANTIC_DESCRIPTORS = MappingProxyType(
    {
        PLATFORM_CAPABILITY_COMPOSITION_COVERAGE: {
            "capability_identifier": PLATFORM_CAPABILITY_COMPOSITION_COVERAGE,
            "objective_terms": (
                "platform capability composition coverage",
                "capability composition coverage",
                "certified capability coverage",
                "reusable capability coverage",
            ),
            "supported_actions": ("analyze", "assess", "discover", "evaluate", "review"),
            "supported_subjects": (
                "capability composition",
                "capability coverage",
                "certified capabilities",
                "reusable capabilities",
            ),
            "expected_outcomes": (
                "capability coverage",
                "certified composition",
                "residual gaps",
            ),
            "excluded_meanings": (
                "normalize change",
                "analyze change impact",
                "validation plan",
            ),
            "supported_work_types": ("AUDIT_ONLY", "ANALYSIS", "REVIEW"),
            "required_semantic_slots": (
                "capability_action",
                "capability_subject",
                "input_artifact_family",
            ),
            "clarification_label": "analyze certified Platform capability composition coverage",
        },
        PLATFORM_CHANGE_NORMALIZATION: {
            "capability_identifier": PLATFORM_CHANGE_NORMALIZATION,
            "objective_terms": (
                "normalize platform change",
                "normalize repository change",
                "canonical change artifact",
                "normalized change",
            ),
            "supported_actions": ("normalize", "canonicalize", "structure", "prepare"),
            "supported_subjects": (
                "implementation change",
                "platform change",
                "repository change",
                "implementation manifest",
                "mutation proposal",
            ),
            "expected_outcomes": ("normalized change", "canonical change evidence"),
            "excluded_meanings": ("impact analysis", "analyze impact", "validation plan"),
            "supported_work_types": ("AUDIT_ONLY", "ANALYSIS", "IMPLEMENTATION", "REVIEW"),
            "required_semantic_slots": ("capability_action", "capability_subject", "input_artifact_family"),
            "clarification_label": "normalize a described implementation change",
        },
        PLATFORM_CHANGE_IMPACT_ANALYSIS: {
            "capability_identifier": PLATFORM_CHANGE_IMPACT_ANALYSIS,
            "objective_terms": (
                "platform change impact analysis",
                "analyze platform change impact",
                "repository change impact",
                "change impact",
            ),
            "supported_actions": ("analyze", "analyse", "assess", "evaluate", "inspect"),
            "supported_subjects": (
                "normalized change",
                "change impact",
                "platform impact",
                "repository impact",
            ),
            "expected_outcomes": ("impact analysis", "affected surfaces", "validation implications"),
            "excluded_meanings": ("normalize change", "validation plan", "plan validation"),
            "supported_work_types": ("AUDIT_ONLY", "ANALYSIS", "IMPLEMENTATION", "REVIEW"),
            "required_semantic_slots": ("capability_action", "capability_subject", "input_artifact_family"),
            "clarification_label": "analyze an existing normalized change",
        },
        PLATFORM_VALIDATION_PLANNING: {
            "capability_identifier": PLATFORM_VALIDATION_PLANNING,
            "objective_terms": (
                "platform validation planning",
                "create validation plan",
                "plan platform validation",
                "validation plan",
            ),
            "supported_actions": ("plan", "prepare", "compose", "create"),
            "supported_subjects": (
                "validation plan",
                "platform validation",
                "impact analysis",
                "change impact artifact",
            ),
            "expected_outcomes": ("validation plan", "validation coverage", "validation requirements"),
            "excluded_meanings": ("normalize change", "analyze impact", "analyse impact"),
            "supported_work_types": ("AUDIT_ONLY", "ANALYSIS", "IMPLEMENTATION", "REVIEW"),
            "required_semantic_slots": ("capability_action", "capability_subject", "input_artifact_family"),
            "clarification_label": "create a validation plan from an existing impact analysis",
        },
    }
)


def certified_capability_semantic_descriptors() -> dict[str, dict[str, Any]]:
    """Return immutable selection metadata for the explicit G28 adapter allowlist."""

    descriptors: dict[str, dict[str, Any]] = {}
    adapter_metadata = certified_capability_invocation_adapters()
    for capability_id, source in sorted(_SEMANTIC_DESCRIPTORS.items()):
        descriptor = {
            **{
                key: list(value) if isinstance(value, tuple) else deepcopy(value)
                for key, value in source.items()
            },
            "accepted_canonical_input_artifact_types": list(
                adapter_metadata[capability_id]["accepted_input_artifact_types"]
            ),
            "required_canonical_input_fields": list(
                adapter_metadata[capability_id]["required_input_fields"]
            ),
            "semantic_descriptor_authority": "PLATFORM_CORE",
            "human_interface_authority": False,
        }
        descriptor["semantic_descriptor_hash"] = replay_hash(descriptor)
        descriptors[capability_id] = descriptor
    return descriptors


def invoke_certified_capability(
    *,
    invocation_id: str,
    session_id: str,
    platform_knowledge_response: dict[str, Any],
    platform_knowledge_response_reference: str,
    discovered_capability_identifier: str,
    capability_inputs: dict[str, Any],
    invoked_by: str,
    invoked_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Resolve and invoke one explicitly allowlisted, certified read-only capability."""

    replay_path = Path(replay_dir)
    try:
        _ensure_replay_available(replay_path)
        identifier = _require_string(invocation_id, "invocation_id")
        session = _require_string(session_id, "session_id")
        response_reference = _require_string(
            platform_knowledge_response_reference,
            "platform_knowledge_response_reference",
        )
        capability_id = _normalize_identifier(
            discovered_capability_identifier,
            "discovered_capability_identifier",
        )
        discovery = _validated_discovery(platform_knowledge_response, capability_id)
        certification = _validated_certification(discovery, capability_id)
        adapter = _allowed_adapter(capability_id)
        validated_inputs, input_evidence = _validated_inputs(adapter, capability_inputs)
        actor = _require_string(invoked_by, "invoked_by")
        timestamp = _require_string(invoked_at, "invoked_at")

        discovery_record = _record_artifact(
            "CERTIFIED_CAPABILITY_DISCOVERY_SOURCE_ARTIFACT_V1",
            {
                "invocation_id": identifier,
                "session_id": session,
                "platform_knowledge_response_reference": response_reference,
                "platform_knowledge_response_hash": discovery["artifact_hash"],
                "platform_knowledge_response": discovery,
                "discovered_capability_identifier": capability_id,
            },
        )
        resolution_record = _record_artifact(
            "CERTIFIED_CAPABILITY_RESOLUTION_ARTIFACT_V1",
            {
                "invocation_id": identifier,
                "discovery_source_hash": discovery_record["artifact_hash"],
                "capability_identifier": capability_id,
                "certification_registry_version": (
                    PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION
                ),
                "certification_record_reference": capability_id,
                "certification_record": certification,
                "certification_record_hash": certification["certification_record_hash"],
                "resolution_status": "CERTIFIED_CAPABILITY_RESOLVED",
            },
        )
        adapter_record = _record_artifact(
            "CERTIFIED_CAPABILITY_INVOCATION_ADAPTER_SELECTION_ARTIFACT_V1",
            {
                "invocation_id": identifier,
                "capability_resolution_hash": resolution_record["artifact_hash"],
                "capability_identifier": capability_id,
                "adapter": adapter.metadata(),
                "adapter_selection_status": "ALLOWLISTED_ADAPTER_SELECTED",
            },
        )
        inputs_record = _record_artifact(
            "CERTIFIED_CAPABILITY_VALIDATED_INPUTS_ARTIFACT_V1",
            {
                "invocation_id": identifier,
                "adapter_selection_hash": adapter_record["artifact_hash"],
                "capability_identifier": capability_id,
                "input_evidence": input_evidence,
                "input_validation_status": "CAPABILITY_INPUTS_VALIDATED",
            },
        )

        capture = adapter.invoke(
            identifier,
            validated_inputs,
            timestamp,
            replay_path / "capability_runtime",
        )
        output = _validated_output(adapter, capture)
        result = _completed_result_artifact(
            invocation_id=identifier,
            session_id=session,
            discovery_reference=response_reference,
            discovery_hash=discovery["artifact_hash"],
            certification=certification,
            resolution_hash=resolution_record["artifact_hash"],
            adapter=adapter,
            adapter_record_hash=adapter_record["artifact_hash"],
            input_record_hash=inputs_record["artifact_hash"],
            input_evidence=input_evidence,
            output=output,
            invoked_by=actor,
            invoked_at=timestamp,
            capability_replay_reference=str(replay_path / "capability_runtime"),
        )
        returned = _returned_artifact(result)
        for index, artifact in enumerate(
            (
                discovery_record,
                resolution_record,
                adapter_record,
                inputs_record,
                result,
                returned,
            )
        ):
            _persist_step(replay_path, index, REPLAY_STEPS[index], artifact)
        return _capture(result, returned, replay_path)
    except Exception as exc:
        result = _failed_result_artifact(
            invocation_id=invocation_id,
            session_id=session_id,
            discovery=platform_knowledge_response,
            discovery_reference=platform_knowledge_response_reference,
            capability_identifier=discovered_capability_identifier,
            invoked_by=invoked_by,
            invoked_at=invoked_at,
            failure_reason=_failure_reason(exc),
        )
        returned = _returned_artifact(result)
        _persist_failure_if_possible(replay_path, result, returned)
        return _capture(result, returned, replay_path)


def run_certified_capability_invocation_binding(**kwargs: Any) -> dict[str, Any]:
    """Canonical descriptive alias for the bounded invocation entry point."""

    return invoke_certified_capability(**kwargs)


def validate_certified_capability_invocation_result_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate one canonical invocation-binding result artifact."""

    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError("certified capability invocation result must be an object")
    candidate = deepcopy(artifact)
    _verify_artifact_hash(candidate, "certified capability invocation result")
    if candidate.get("artifact_type") != CERTIFIED_CAPABILITY_INVOCATION_RESULT_ARTIFACT_V1:
        raise FailClosedRuntimeError("certified capability invocation result artifact type mismatch")
    if candidate.get("invocation_status") not in {
        CERTIFIED_CAPABILITY_INVOCATION_COMPLETED,
        FAILED_CLOSED,
    }:
        raise FailClosedRuntimeError("certified capability invocation status invalid")
    if candidate.get("authority_flags") != AUTHORITY_FLAGS:
        raise FailClosedRuntimeError("certified capability invocation authority flags invalid")
    if candidate.get("replay_visible") is not True:
        raise FailClosedRuntimeError("certified capability invocation must be replay-visible")
    if candidate.get("invocation_status") == FAILED_CLOSED:
        if candidate.get("capability_invoked") is not False:
            raise FailClosedRuntimeError("failed capability invocation cannot claim invocation")
        return candidate
    if candidate.get("capability_invoked") is not True:
        raise FailClosedRuntimeError("completed capability invocation must record invocation")
    evidence = candidate.get("input_evidence")
    if not isinstance(evidence, dict):
        raise FailClosedRuntimeError("certified capability invocation input evidence missing")
    _verify_named_hash(
        evidence,
        "input_evidence_hash",
        "certified capability invocation input evidence hash mismatch",
    )
    if candidate.get("output_artifact_type") != candidate.get("output_artifact", {}).get(
        "artifact_type"
    ):
        raise FailClosedRuntimeError("certified capability invocation output type mismatch")
    output = candidate.get("output_artifact")
    if not isinstance(output, dict):
        raise FailClosedRuntimeError("certified capability invocation output missing")
    _verify_artifact_hash(output, "certified capability invocation output")
    if candidate.get("output_artifact_hash") != output["artifact_hash"]:
        raise FailClosedRuntimeError("certified capability invocation output hash mismatch")
    return candidate


def reconstruct_certified_capability_invocation_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct and cross-check one completed invocation binding Replay."""

    replay_path = Path(replay_dir)
    wrappers: list[dict[str, Any]] = []
    artifacts: list[dict[str, Any]] = []
    for index, step in enumerate(REPLAY_STEPS):
        wrapper = load_json(replay_path / f"{index:03d}_{step}.json")
        if wrapper.get("replay_index") != index or wrapper.get("replay_step") != step:
            raise FailClosedRuntimeError("certified capability invocation replay ordering mismatch")
        _verify_named_hash(
            wrapper,
            "replay_hash",
            "certified capability invocation replay hash mismatch",
        )
        artifact = wrapper.get("artifact")
        if not isinstance(artifact, dict):
            raise FailClosedRuntimeError("certified capability invocation replay artifact missing")
        _verify_artifact_hash(artifact, "certified capability invocation replay artifact")
        wrappers.append(wrapper)
        artifacts.append(artifact)

    discovery, resolution, adapter_selection, inputs, result, returned = artifacts
    validated_discovery = validate_platform_knowledge_response(
        discovery.get("platform_knowledge_response")
    )
    validated_result = validate_certified_capability_invocation_result_artifact(result)
    if validated_result["invocation_status"] != CERTIFIED_CAPABILITY_INVOCATION_COMPLETED:
        raise FailClosedRuntimeError("completed certified capability invocation replay required")
    if discovery.get("platform_knowledge_response_hash") != validated_discovery["artifact_hash"]:
        raise FailClosedRuntimeError("certified capability invocation discovery hash mismatch")
    if resolution.get("discovery_source_hash") != discovery["artifact_hash"]:
        raise FailClosedRuntimeError("certified capability invocation resolution lineage mismatch")
    capability_id = result.get("capability_identifier")
    certification = resolution.get("certification_record")
    if not isinstance(certification, dict):
        raise FailClosedRuntimeError("certified capability invocation certification record missing")
    _verify_named_hash(
        certification,
        "certification_record_hash",
        "certified capability invocation certification record hash mismatch",
    )
    current_certification = lookup_platform_capability_certification(str(capability_id))
    if (
        certification.get("certification_record_hash")
        != current_certification["certification_record_hash"]
    ):
        raise FailClosedRuntimeError("certified capability invocation certification record drift")
    if resolution.get("certification_record_reference") != capability_id:
        raise FailClosedRuntimeError("certified capability invocation certification reference mismatch")
    if adapter_selection.get("capability_resolution_hash") != resolution["artifact_hash"]:
        raise FailClosedRuntimeError("certified capability invocation adapter lineage mismatch")
    adapter = _allowed_adapter(str(capability_id))
    if adapter_selection.get("adapter") != adapter.metadata():
        raise FailClosedRuntimeError("certified capability invocation adapter selection mismatch")
    if inputs.get("adapter_selection_hash") != adapter_selection["artifact_hash"]:
        raise FailClosedRuntimeError("certified capability invocation input lineage mismatch")
    input_evidence = inputs.get("input_evidence")
    if not isinstance(input_evidence, dict):
        raise FailClosedRuntimeError("certified capability invocation input evidence missing")
    _verify_named_hash(
        input_evidence,
        "input_evidence_hash",
        "certified capability invocation input evidence hash mismatch",
    )
    if result.get("validated_inputs_record_hash") != inputs["artifact_hash"]:
        raise FailClosedRuntimeError("certified capability invocation result lineage mismatch")
    if result.get("input_evidence") != input_evidence:
        raise FailClosedRuntimeError("certified capability invocation result input mismatch")
    if result.get("platform_knowledge_response_hash") != validated_discovery["artifact_hash"]:
        raise FailClosedRuntimeError("certified capability invocation result discovery mismatch")
    if result.get("capability_resolution_hash") != resolution["artifact_hash"]:
        raise FailClosedRuntimeError("certified capability invocation result resolution mismatch")
    if result.get("adapter_selection_record_hash") != adapter_selection["artifact_hash"]:
        raise FailClosedRuntimeError("certified capability invocation result adapter mismatch")
    if returned.get("invocation_result_reference") != result["invocation_id"]:
        raise FailClosedRuntimeError("certified capability invocation returned reference mismatch")
    if returned.get("invocation_result_hash") != result["artifact_hash"]:
        raise FailClosedRuntimeError("certified capability invocation returned hash mismatch")
    capability_ids = {
        discovery.get("discovered_capability_identifier"),
        resolution.get("capability_identifier"),
        adapter_selection.get("capability_identifier"),
        inputs.get("capability_identifier"),
        result.get("capability_identifier"),
        returned.get("capability_identifier"),
    }
    if len(capability_ids) != 1:
        raise FailClosedRuntimeError("certified capability invocation capability lineage mismatch")
    if capability_id == PLATFORM_CAPABILITY_COMPOSITION_COVERAGE:
        _reconstruct_capability_composition_coverage_replay(
            replay_path=Path(str(result["capability_replay_reference"])),
            expected_output=result["output_artifact"],
        )
    return {
        "invocation_id": result["invocation_id"],
        "session_id": result["session_id"],
        "invocation_status": result["invocation_status"],
        "capability_identifier": result["capability_identifier"],
        "adapter_identifier": result["adapter_identifier"],
        "output_artifact_type": result["output_artifact_type"],
        "output_artifact_reference": result["output_artifact_reference"],
        "output_artifact_hash": result["output_artifact_hash"],
        "capability_replay_reference": result["capability_replay_reference"],
        "replay_visible": True,
        "worker_invoked": False,
        "provider_invoked": False,
        "repository_mutated": False,
        "dynamic_import_used": False,
        "artifact_hash": result["artifact_hash"],
        "replay_artifact_count": len(wrappers),
        "replay_hash": replay_hash(wrappers),
    }


def _reconstruct_capability_composition_coverage_replay(
    *, replay_path: Path, expected_output: dict[str, Any]
) -> None:
    wrapper = load_json(
        replay_path / "000_platform_capability_composition_coverage_recorded.json"
    )
    if wrapper.get("replay_index") != 0 or wrapper.get("replay_step") != (
        "platform_capability_composition_coverage_recorded"
    ):
        raise FailClosedRuntimeError(
            "capability composition coverage replay ordering mismatch"
        )
    _verify_named_hash(
        wrapper,
        "wrapper_hash",
        "capability composition coverage replay wrapper hash mismatch",
    )
    artifact = validate_platform_capability_composition_coverage(
        wrapper.get("artifact")
    )
    if artifact.get("artifact_hash") != expected_output.get("artifact_hash"):
        raise FailClosedRuntimeError(
            "capability composition coverage replay output mismatch"
        )


def _validated_discovery(response: Any, capability_id: str) -> dict[str, Any]:
    discovery = validate_platform_knowledge_response(response)
    if discovery.get("canonical_capability_identifier") != capability_id:
        raise FailClosedRuntimeError(
            "certified capability invocation failed closed: discovered capability mismatch"
        )
    if discovery.get("certified_capability_exists") is not True:
        raise FailClosedRuntimeError(
            "certified capability invocation failed closed: certified capability required"
        )
    if discovery.get("is_certified") is not True:
        raise FailClosedRuntimeError(
            "certified capability invocation failed closed: capability is uncertified"
        )
    if discovery.get("capability_exists") is not True:
        raise FailClosedRuntimeError(
            "certified capability invocation failed closed: discovered capability absent"
        )
    return discovery


def _validated_certification(
    discovery: dict[str, Any],
    capability_id: str,
) -> dict[str, Any]:
    record = lookup_platform_capability_certification(capability_id)
    if record.get("certification_status") not in CERTIFIED_STATES:
        raise FailClosedRuntimeError(
            "certified capability invocation failed closed: capability is uncertified"
        )
    if record.get("superseded_by") is not None:
        raise FailClosedRuntimeError(
            "certified capability invocation failed closed: capability is superseded"
        )
    if discovery.get("certification_status") != record["certification_status"]:
        raise FailClosedRuntimeError(
            "certified capability invocation failed closed: certification status mismatch"
        )
    if discovery.get("certification_record_hash") != record["certification_record_hash"]:
        raise FailClosedRuntimeError(
            "certified capability invocation failed closed: certification record mismatch"
        )
    if discovery.get("implementation_owner") != record["implementation_owner"]:
        raise FailClosedRuntimeError(
            "certified capability invocation failed closed: implementation owner mismatch"
        )
    return record


def _allowed_adapter(capability_id: str) -> CapabilityInvocationAdapter:
    adapter = _ADAPTERS.get(capability_id)
    if adapter is None:
        raise FailClosedRuntimeError(
            "certified capability invocation failed closed: no allowlisted invocation adapter"
        )
    return adapter


def _validated_inputs(
    adapter: CapabilityInvocationAdapter,
    capability_inputs: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if not isinstance(capability_inputs, dict):
        raise FailClosedRuntimeError(
            "certified capability invocation failed closed: capability inputs required"
        )
    inputs = deepcopy(capability_inputs)
    expected_fields = set(adapter.required_input_fields)
    missing = sorted(expected_fields - set(inputs))
    unexpected = sorted(set(inputs) - expected_fields)
    if missing:
        raise FailClosedRuntimeError(
            "certified capability invocation failed closed: missing required input: "
            + ", ".join(missing)
        )
    if unexpected:
        raise FailClosedRuntimeError(
            "certified capability invocation failed closed: unexpected capability input: "
            + ", ".join(unexpected)
        )
    if adapter.capability_identifier == PLATFORM_CHANGE_NORMALIZATION:
        artifact = _validate_normalization_input(inputs)
        reference = inputs["source_reference"]
        semantic_hash = inputs["source_hash"]
    elif adapter.capability_identifier == PLATFORM_CAPABILITY_COMPOSITION_COVERAGE:
        artifact = validate_platform_capability_composition_coverage_request(
            inputs["composition_coverage_request_artifact"]
        )
        reference = _require_string(
            inputs["composition_coverage_request_reference"],
            "composition_coverage_request_reference",
        )
        semantic_hash = _require_hash(
            inputs["composition_coverage_request_hash"],
            "composition_coverage_request_hash",
        )
        if artifact["request_id"] != reference:
            raise FailClosedRuntimeError(
                "certified capability invocation failed closed: input reference mismatch"
            )
        if artifact["artifact_hash"] != semantic_hash:
            raise FailClosedRuntimeError(
                "certified capability invocation failed closed: input hash mismatch"
            )
    elif adapter.capability_identifier == PLATFORM_CHANGE_IMPACT_ANALYSIS:
        artifact = validate_normalized_change_artifact(inputs["normalized_change_artifact"])
        reference = _require_string(
            inputs["normalized_change_reference"],
            "normalized_change_reference",
        )
        semantic_hash = _require_hash(inputs["normalized_change_hash"], "normalized_change_hash")
        if artifact["normalization_id"] != reference:
            raise FailClosedRuntimeError(
                "certified capability invocation failed closed: input reference mismatch"
            )
        if artifact["normalized_change_hash"] != semantic_hash:
            raise FailClosedRuntimeError(
                "certified capability invocation failed closed: input hash mismatch"
            )
    else:
        artifact = validate_platform_change_impact_artifact(
            inputs["platform_change_impact_artifact"]
        )
        reference = _require_string(
            inputs["platform_change_impact_reference"],
            "platform_change_impact_reference",
        )
        semantic_hash = _require_hash(
            inputs["platform_change_impact_hash"],
            "platform_change_impact_hash",
        )
        if artifact["impact_analysis_id"] != reference:
            raise FailClosedRuntimeError(
                "certified capability invocation failed closed: input reference mismatch"
            )
        if artifact["platform_change_impact_hash"] != semantic_hash:
            raise FailClosedRuntimeError(
                "certified capability invocation failed closed: input hash mismatch"
            )
    if artifact.get("artifact_type") not in adapter.accepted_input_artifact_types:
        raise FailClosedRuntimeError(
            "certified capability invocation failed closed: input artifact type is not accepted"
        )
    evidence = {
        "input_artifact_type": artifact["artifact_type"],
        "input_artifact_reference": reference,
        "input_artifact_hash": artifact["artifact_hash"],
        "input_semantic_hash": semantic_hash,
        "required_input_fields": list(adapter.required_input_fields),
        "capability_specific_prerequisites_validated": True,
    }
    evidence["input_evidence_hash"] = replay_hash(evidence)
    return inputs, evidence


def _validate_normalization_input(inputs: dict[str, Any]) -> dict[str, Any]:
    artifact = inputs["source_artifact"]
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(
            "certified capability invocation failed closed: input artifact required"
        )
    artifact = deepcopy(artifact)
    _verify_artifact_hash(artifact, "certified capability invocation input")
    if artifact.get("artifact_type") not in {
        IMPLEMENTATION_MANIFEST_ARTIFACT_V1,
        GOVERNED_REPOSITORY_MUTATION_PROPOSAL_ARTIFACT_V1,
    }:
        raise FailClosedRuntimeError(
            "certified capability invocation failed closed: input artifact type is not accepted"
        )
    reference_field = (
        "manifest_id"
        if artifact["artifact_type"] == IMPLEMENTATION_MANIFEST_ARTIFACT_V1
        else "proposal_id"
    )
    reference = _require_string(inputs["source_reference"], "source_reference")
    source_hash = _require_hash(inputs["source_hash"], "source_hash")
    if artifact.get(reference_field) != reference:
        raise FailClosedRuntimeError(
            "certified capability invocation failed closed: input reference mismatch"
        )
    if artifact["artifact_hash"] != source_hash:
        raise FailClosedRuntimeError(
            "certified capability invocation failed closed: input hash mismatch"
        )
    if artifact.get("replay_visible") is not True:
        raise FailClosedRuntimeError(
            "certified capability invocation failed closed: input artifact is not replay-visible"
        )
    return artifact


def _validated_output(
    adapter: CapabilityInvocationAdapter,
    capture: Any,
) -> dict[str, Any]:
    if not isinstance(capture, dict):
        raise FailClosedRuntimeError(
            "certified capability invocation failed closed: capability capture invalid"
        )
    output = capture.get(adapter.output_capture_field)
    if not isinstance(output, dict):
        raise FailClosedRuntimeError(
            "certified capability invocation failed closed: capability output missing"
        )
    if output.get("artifact_type") != adapter.output_artifact_type:
        raise FailClosedRuntimeError(
            "certified capability invocation failed closed: unexpected output artifact"
        )
    if output.get(adapter.output_status_field) == adapter.failed_status:
        raise FailClosedRuntimeError(
            "certified capability invocation failed closed: capability failed closed: "
            + str(output.get("failure_reason") or "unknown capability failure")
        )
    if adapter.capability_identifier == PLATFORM_CHANGE_NORMALIZATION:
        return validate_normalized_change_artifact(output)
    if adapter.capability_identifier == PLATFORM_CHANGE_IMPACT_ANALYSIS:
        return validate_platform_change_impact_artifact(output)
    if adapter.capability_identifier == PLATFORM_CAPABILITY_COMPOSITION_COVERAGE:
        return validate_platform_capability_composition_coverage(output)
    return validate_platform_validation_plan_artifact(output)


def _completed_result_artifact(
    *,
    invocation_id: str,
    session_id: str,
    discovery_reference: str,
    discovery_hash: str,
    certification: dict[str, Any],
    resolution_hash: str,
    adapter: CapabilityInvocationAdapter,
    adapter_record_hash: str,
    input_record_hash: str,
    input_evidence: dict[str, Any],
    output: dict[str, Any],
    invoked_by: str,
    invoked_at: str,
    capability_replay_reference: str,
) -> dict[str, Any]:
    artifact = {
        "artifact_type": CERTIFIED_CAPABILITY_INVOCATION_RESULT_ARTIFACT_V1,
        "runtime_version": CERTIFIED_CAPABILITY_INVOCATION_BINDING_RUNTIME_VERSION,
        "invocation_id": invocation_id,
        "session_id": session_id,
        "invocation_status": CERTIFIED_CAPABILITY_INVOCATION_COMPLETED,
        "platform_knowledge_response_reference": discovery_reference,
        "platform_knowledge_response_hash": discovery_hash,
        "capability_identifier": adapter.capability_identifier,
        "certification_record_hash": certification["certification_record_hash"],
        "capability_resolution_hash": resolution_hash,
        "adapter_identifier": adapter.adapter_identifier,
        "adapter_selection_record_hash": adapter_record_hash,
        "validated_inputs_record_hash": input_record_hash,
        "input_evidence": deepcopy(input_evidence),
        "output_artifact_type": output["artifact_type"],
        "output_artifact_reference": output[adapter.output_reference_field],
        "output_artifact_hash": output["artifact_hash"],
        "output_artifact": deepcopy(output),
        "capability_replay_reference": capability_replay_reference,
        "invoked_by": invoked_by,
        "invoked_at": invoked_at,
        "capability_invoked": True,
        "replay_visible": True,
        "read_only": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": None,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return validate_certified_capability_invocation_result_artifact(artifact)


def _failed_result_artifact(
    *,
    invocation_id: Any,
    session_id: Any,
    discovery: Any,
    discovery_reference: Any,
    capability_identifier: Any,
    invoked_by: Any,
    invoked_at: Any,
    failure_reason: str,
) -> dict[str, Any]:
    source = discovery if isinstance(discovery, dict) else {}
    artifact = {
        "artifact_type": CERTIFIED_CAPABILITY_INVOCATION_RESULT_ARTIFACT_V1,
        "runtime_version": CERTIFIED_CAPABILITY_INVOCATION_BINDING_RUNTIME_VERSION,
        "invocation_id": _safe_string(invocation_id),
        "session_id": _safe_string(session_id),
        "invocation_status": FAILED_CLOSED,
        "platform_knowledge_response_reference": _safe_string(discovery_reference),
        "platform_knowledge_response_hash": _safe_hash(source.get("artifact_hash")),
        "capability_identifier": _safe_identifier(capability_identifier),
        "certification_record_hash": None,
        "capability_resolution_hash": None,
        "adapter_identifier": None,
        "adapter_selection_record_hash": None,
        "validated_inputs_record_hash": None,
        "input_evidence": None,
        "output_artifact_type": None,
        "output_artifact_reference": None,
        "output_artifact_hash": None,
        "output_artifact": None,
        "capability_replay_reference": None,
        "invoked_by": _safe_string(invoked_by),
        "invoked_at": _safe_string(invoked_at),
        "capability_invoked": False,
        "replay_visible": True,
        "read_only": True,
        "authority_flags": deepcopy(AUTHORITY_FLAGS),
        "failure_reason": failure_reason,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return validate_certified_capability_invocation_result_artifact(artifact)


def _returned_artifact(result: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "event_type": "CERTIFIED_CAPABILITY_INVOCATION_RETURNED",
        "invocation_result_reference": result["invocation_id"],
        "invocation_result_hash": result["artifact_hash"],
        "invocation_status": result["invocation_status"],
        "capability_identifier": result["capability_identifier"],
        "output_artifact_reference": result["output_artifact_reference"],
        "output_artifact_hash": result["output_artifact_hash"],
        "replay_visible": True,
        "worker_invoked": False,
        "provider_invoked": False,
        "repository_mutated": False,
        "human_interface_authority": False,
        "failure_reason": result["failure_reason"],
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _record_artifact(artifact_type: str, fields: dict[str, Any]) -> dict[str, Any]:
    artifact = {
        "artifact_type": artifact_type,
        "runtime_version": CERTIFIED_CAPABILITY_INVOCATION_BINDING_RUNTIME_VERSION,
        **deepcopy(fields),
        "replay_visible": True,
        "human_interface_authority": False,
        "worker_invoked": False,
        "provider_invoked": False,
        "repository_mutated": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _capture(
    result: dict[str, Any],
    returned: dict[str, Any],
    replay_path: Path,
) -> dict[str, Any]:
    capture = {
        "runtime_version": CERTIFIED_CAPABILITY_INVOCATION_BINDING_RUNTIME_VERSION,
        "invocation_id": result["invocation_id"],
        "session_id": result["session_id"],
        "invocation_status": result["invocation_status"],
        "capability_identifier": result["capability_identifier"],
        "certified_capability_invocation_result_artifact": deepcopy(result),
        "certified_capability_invocation_returned_artifact": deepcopy(returned),
        "capability_output_artifact": deepcopy(result["output_artifact"]),
        "capability_invocation_replay_reference": str(replay_path),
        "capability_replay_reference": result["capability_replay_reference"],
        "capability_invoked": result["capability_invoked"],
        "replay_visible": True,
        "fail_closed": result["invocation_status"] == FAILED_CLOSED,
        "failure_reason": result["failure_reason"],
        "worker_invoked": False,
        "provider_invoked": False,
        "repository_mutated": False,
        "human_interface_authority": False,
        "dynamic_import_used": False,
    }
    capture["capture_hash"] = replay_hash(capture)
    return capture


def _persist_step(path: Path, index: int, step: str, artifact: dict[str, Any]) -> None:
    wrapper = {
        "replay_index": index,
        "replay_step": step,
        "artifact": deepcopy(artifact),
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(path / f"{index:03d}_{step}.json", wrapper)


def _persist_failure_if_possible(
    path: Path,
    result: dict[str, Any],
    returned: dict[str, Any],
) -> None:
    try:
        _persist_step(path, 4, REPLAY_STEPS[4], result)
        _persist_step(path, 5, REPLAY_STEPS[5], returned)
    except Exception:
        return


def _ensure_replay_available(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise FailClosedRuntimeError(
            "certified capability invocation failed closed: replay directory is not empty"
        )


def _verify_artifact_hash(artifact: Any, label: str) -> None:
    if not isinstance(artifact, dict):
        raise FailClosedRuntimeError(f"{label} must be an object")
    _verify_named_hash(artifact, "artifact_hash", f"{label} hash mismatch")


def _verify_named_hash(artifact: dict[str, Any], field: str, message: str) -> None:
    actual = _require_hash(artifact.get(field), field)
    body = deepcopy(artifact)
    body.pop(field, None)
    if replay_hash(body) != actual:
        raise FailClosedRuntimeError(message)


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"certified capability invocation requires {field}")
    return value.strip()


def _require_hash(value: Any, field: str) -> str:
    token = _require_string(value, field)
    if not token.startswith("sha256:"):
        raise FailClosedRuntimeError(f"certified capability invocation requires valid {field}")
    return token


def _normalize_identifier(value: Any, field: str) -> str:
    return _require_string(value, field).upper().replace("-", "_").replace(" ", "_")


def _safe_string(value: Any) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else "INVALID"


def _safe_identifier(value: Any) -> str:
    try:
        return _normalize_identifier(value, "capability_identifier")
    except Exception:
        return "INVALID"


def _safe_hash(value: Any) -> str | None:
    return value if isinstance(value, str) and value.startswith("sha256:") else None


def _failure_reason(exc: Exception) -> str:
    return str(exc) or exc.__class__.__name__
