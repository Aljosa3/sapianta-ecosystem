"""Operational G47 binding between Objective Inference and existing planning."""

from __future__ import annotations

from dataclasses import asdict
import hashlib
from pathlib import Path
from typing import Any

from aigol.runtime.constitutional_development_governance_orchestration import (
    CONSTITUTIONAL_DEVELOPMENT_GOVERNANCE_BUNDLE_ARTIFACT_V1,
    DEVELOPMENT_GOVERNANCE_CDD_CLASSIFICATION_ARTIFACT_V1,
    DEVELOPMENT_GOVERNANCE_DISPOSITION_ARTIFACT_V1,
    DEVELOPMENT_GOVERNANCE_EVIDENCE_SNAPSHOT_ARTIFACT_V1,
    DEVELOPMENT_GOVERNANCE_NEED_ASSESSMENT_ARTIFACT_V1,
    DEVELOPMENT_GOVERNANCE_PLANNING_ELIGIBILITY_ARTIFACT_V1,
    DEVELOPMENT_GOVERNANCE_RUNTIME_VERSION,
    DEVELOPMENT_GOVERNANCE_TASK_INTAKE_ARTIFACT_V1,
    ConstitutionalDevelopmentGovernanceBundle,
    DevelopmentGovernanceCDDClassification,
    DevelopmentGovernanceDisposition,
    DevelopmentGovernanceEvidenceReference,
    DevelopmentGovernanceEvidenceSnapshot,
    DevelopmentGovernanceNeedAssessment,
    DevelopmentGovernancePlanningEligibility,
    DevelopmentGovernanceRuntimeError,
    DevelopmentGovernanceStageReference,
    DevelopmentGovernanceTaskIntake,
    compose_governance_eligible_implementation_turn_durable_work_binding,
    derive_bundle_state,
    orchestrate_constitutional_development_governance,
    reconstruct_constitutional_development_governance_bundle,
)
from aigol.runtime.platform_capability_certification_registry import (
    lookup_platform_capability_certification,
)
from aigol.runtime.platform_implementation_turn_durable_work_binding import (
    implementation_turn_planning_scope_from_coverage,
    prepare_implementation_turn_capability_coverage,
    validate_implementation_turn_durable_work_binding,
)
from aigol.runtime.platform_project_objective_inference import (
    validate_platform_project_objective,
)
from aigol.runtime.transport.serialization import (
    load_json,
    replay_hash,
    write_json_immutable,
)


G47_OPERATIONAL_INTEGRATION_VERSION = (
    "G47_01D_DEVELOPMENT_GOVERNANCE_OPERATIONAL_INTEGRATION_V1"
)
G47_OPERATIONAL_INTEGRATION_ARTIFACT_V1 = (
    "G47_DEVELOPMENT_GOVERNANCE_OPERATIONAL_INTEGRATION_ARTIFACT_V1"
)
G47_OPERATIONAL_INTEGRATION_READY = "G47_OPERATIONAL_INTEGRATION_READY"
G47_OPERATIONAL_INTEGRATION_TERMINATED = "G47_OPERATIONAL_INTEGRATION_TERMINATED"
CONSTITUTIONAL_BASELINE = "CONSTITUTIONAL_DEVELOPMENT_POLICY_V1"
GLOBAL_EVIDENCE_SUBJECT = "PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME"
EXPLICIT_PROHIBITIONS = tuple(
    sorted(
        (
            "NO_APPROVAL_BYPASS",
            "NO_AUTHORIZATION_BYPASS",
            "NO_PLANNER_SCOPE_EXPANSION",
            "NO_REPLAY_PROTOCOL_MUTATION",
            "NO_WORKER_OR_PROVIDER_INVOCATION",
        )
    )
)


def integrate_constitutional_development_governance(
    *,
    request: str,
    project_objective_artifact: dict[str, Any],
    knowledge_reuse_artifact: dict[str, Any],
    workspace_state: dict[str, Any] | None,
    workspace: str | Path,
    created_at: str,
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Run the certified G47 barrier before invoking the existing planner."""

    objective = validate_platform_project_objective(project_objective_artifact)
    coverage = prepare_implementation_turn_capability_coverage(
        request=request,
        knowledge_reuse_artifact=knowledge_reuse_artifact,
        workspace_state=workspace_state,
        workspace=workspace,
        created_at=created_at,
    )
    stage_outputs = _compose_stage_outputs(
        request=request,
        objective=objective,
        coverage=coverage,
    )
    bundle = orchestrate_constitutional_development_governance(
        bundle_id=_identity("DG-BUNDLE", objective["artifact_hash"]),
        task_intake=stage_outputs[0],
        cdd_classification=stage_outputs[1],
        evidence_snapshot=stage_outputs[2],
        need_assessment=stage_outputs[3],
        governance_disposition=stage_outputs[4],
        planning_eligibility=stage_outputs[5],
    )
    eligibility = stage_outputs[5]
    disposition = stage_outputs[4]
    bound = None
    if (
        eligibility.planning_eligible is True
        and disposition.governance_disposition == "BOUNDED_PLANNING_PERMITTED"
    ):
        bound = (
            compose_governance_eligible_implementation_turn_durable_work_binding(
                planning_eligibility=eligibility,
                request=request,
                project_objective_artifact=objective,
                knowledge_reuse_artifact=knowledge_reuse_artifact,
                workspace_state=workspace_state,
                workspace=workspace,
                created_at=created_at,
                replay_dir=replay_dir,
                governance_bundle=bundle,
                stage_outputs=stage_outputs,
            )
        )

    record = {
        "artifact_type": G47_OPERATIONAL_INTEGRATION_ARTIFACT_V1,
        "runtime_version": G47_OPERATIONAL_INTEGRATION_VERSION,
        "integration_status": (
            G47_OPERATIONAL_INTEGRATION_READY
            if bound is not None
            else G47_OPERATIONAL_INTEGRATION_TERMINATED
        ),
        "bundle_state": derive_bundle_state(disposition),
        "governance_bundle": asdict(bundle),
        "stage_outputs": [asdict(item) for item in stage_outputs],
        "governance_bundle_hash": bundle.bundle_hash,
        "planning_eligible": eligibility.planning_eligible,
        "governance_disposition": disposition.governance_disposition,
        "residual_gap": list(eligibility.residual_gap),
        "canonical_owners": list(eligibility.canonical_owners),
        "evidence_references": list(stage_outputs[3].evidence_references),
        "governance_prohibitions": list(disposition.explicit_prohibitions),
        "implementation_turn_binding": (
            bound["implementation_turn_binding"] if bound is not None else None
        ),
        "implementation_turn_binding_hash": (
            bound["implementation_turn_binding_hash"] if bound is not None else None
        ),
        "planner_semantics_modified": False,
        "replay_protocol_modified": False,
        "authorization_modified": False,
        "approval_modified": False,
        "worker_modified": False,
        "provider_modified": False,
        "aicli_semantic_authority": False,
    }
    record["artifact_hash"] = replay_hash(record)
    _persist_record(Path(replay_dir), record)
    validate_constitutional_development_governance_operational_record(record)
    return record


def validate_constitutional_development_governance_operational_record(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate additive G47 lineage without acquiring Replay authority."""

    if not isinstance(artifact, dict):
        raise DevelopmentGovernanceRuntimeError(
            "G47 operational integration record must be an object"
        )
    if artifact.get("artifact_type") != G47_OPERATIONAL_INTEGRATION_ARTIFACT_V1:
        raise DevelopmentGovernanceRuntimeError(
            "G47 operational integration artifact type is invalid"
        )
    if artifact.get("runtime_version") != G47_OPERATIONAL_INTEGRATION_VERSION:
        raise DevelopmentGovernanceRuntimeError(
            "G47 operational integration version is invalid"
        )
    if artifact.get("integration_status") not in {
        G47_OPERATIONAL_INTEGRATION_READY,
        G47_OPERATIONAL_INTEGRATION_TERMINATED,
    }:
        raise DevelopmentGovernanceRuntimeError(
            "G47 operational integration status is invalid"
        )
    for field in (
        "planner_semantics_modified",
        "replay_protocol_modified",
        "authorization_modified",
        "approval_modified",
        "worker_modified",
        "provider_modified",
        "aicli_semantic_authority",
    ):
        if artifact.get(field) is not False:
            raise DevelopmentGovernanceRuntimeError(
                f"G47 operational boundary changed: {field}"
            )
    body = dict(artifact)
    actual_hash = body.pop("artifact_hash", None)
    if replay_hash(body) != actual_hash:
        raise DevelopmentGovernanceRuntimeError(
            "G47 operational integration hash mismatch"
        )
    stage_outputs = _stage_outputs_from_dicts(artifact.get("stage_outputs"))
    bundle = _bundle_from_dict(artifact.get("governance_bundle"))
    reconstructed = reconstruct_constitutional_development_governance_bundle(
        bundle=bundle,
        stage_outputs=stage_outputs,
    )
    if reconstructed.bundle_hash != artifact.get("governance_bundle_hash"):
        raise DevelopmentGovernanceRuntimeError(
            "G47 operational bundle lineage mismatch"
        )
    eligible = stage_outputs[5].planning_eligible is True
    ready = artifact["integration_status"] == G47_OPERATIONAL_INTEGRATION_READY
    if ready is not eligible:
        raise DevelopmentGovernanceRuntimeError(
            "G47 operational planner barrier status mismatch"
        )
    if ready and not isinstance(artifact.get("implementation_turn_binding"), dict):
        raise DevelopmentGovernanceRuntimeError(
            "G47 operational ready record lacks durable-work binding"
        )
    if ready:
        binding = validate_implementation_turn_durable_work_binding(
            artifact["implementation_turn_binding"],
            require_ready=True,
        )
        if binding["artifact_hash"] != artifact.get(
            "implementation_turn_binding_hash"
        ):
            raise DevelopmentGovernanceRuntimeError(
                "G47 operational durable-work lineage mismatch"
            )
    if not ready and artifact.get("implementation_turn_binding") is not None:
        raise DevelopmentGovernanceRuntimeError(
            "G47 terminated record contains a planner result"
        )
    disposition = stage_outputs[4]
    eligibility = stage_outputs[5]
    need = stage_outputs[3]
    if (
        artifact.get("bundle_state") != derive_bundle_state(disposition)
        or artifact.get("governance_disposition")
        != disposition.governance_disposition
        or artifact.get("planning_eligible") is not eligibility.planning_eligible
        or artifact.get("residual_gap") != list(eligibility.residual_gap)
        or artifact.get("canonical_owners") != list(eligibility.canonical_owners)
        or artifact.get("evidence_references") != list(need.evidence_references)
        or artifact.get("governance_prohibitions")
        != list(disposition.explicit_prohibitions)
    ):
        raise DevelopmentGovernanceRuntimeError(
            "G47 operational certified output projection mismatch"
        )
    return dict(artifact)


def reconstruct_constitutional_development_governance_operational_replay(
    replay_dir: str | Path,
) -> dict[str, Any]:
    """Reconstruct and verify the additive G47 operational record."""

    wrapper = load_json(
        Path(replay_dir) / "000_development_governance_integration_recorded.json"
    )
    if (
        wrapper.get("replay_index") != 0
        or wrapper.get("replay_step")
        != "development_governance_integration_recorded"
    ):
        raise DevelopmentGovernanceRuntimeError(
            "G47 operational Replay ordering mismatch"
        )
    body = dict(wrapper)
    actual_hash = body.pop("replay_hash", None)
    if replay_hash(body) != actual_hash:
        raise DevelopmentGovernanceRuntimeError(
            "G47 operational Replay hash mismatch"
        )
    return validate_constitutional_development_governance_operational_record(
        wrapper.get("artifact")
    )


def _compose_stage_outputs(
    *,
    request: str,
    objective: dict[str, Any],
    coverage: dict[str, Any],
) -> tuple[Any, ...]:
    planning_scope = implementation_turn_planning_scope_from_coverage(coverage)
    reusable = tuple(
        item
        for item in coverage.get("discovered_reusable_capabilities") or []
        if isinstance(item, dict) and item.get("capability_identifier")
    )
    covered_facets = tuple(
        sorted(
            {
                str(facet)
                for item in reusable
                for facet in item.get("covered_facets") or []
                if isinstance(facet, str) and facet
            }
        )
    )
    objective_facets = tuple(sorted(set(covered_facets) | set(planning_scope)))
    intake_id = _identity("DG-INTAKE", objective["source_request_hash"])
    cdd_id = _identity("DG-CDD", intake_id, *objective_facets)
    snapshot_id = _identity("DG-EVIDENCE", cdd_id, coverage["artifact_hash"])
    evidence = _evidence_items(
        coverage=coverage,
        reusable=reusable,
        covered_facets=covered_facets,
        residual_facets=planning_scope,
    )
    evidence_ids = tuple(sorted(item.evidence_id for item in evidence))
    owners = tuple(
        sorted(
            {
                item.canonical_owner
                for item in evidence
                if item.claim_type == "OBJECTIVE_FACET_COVERAGE"
                and item.claim_value == "COVERED"
            }
        )
    )
    outcome = _need_outcome(
        coverage=coverage,
        residual=planning_scope,
        owner_count=len(owners),
    )
    disposition_value = (
        "BOUNDED_PLANNING_PERMITTED"
        if outcome
        in {
            "COMPLETE_EXISTING_REALIZATION",
            "IMPLEMENT_EXISTING_BINDING",
            "EXTEND_EXISTING_OWNER",
            "COMPOSE_EXISTING_CAPABILITIES",
            "NEW_REALIZATION_JUSTIFIED",
        }
        else "REUSE_REQUIRED"
        if outcome == "REUSE_EXISTING_UNCHANGED"
        else "GOVERNANCE_REVIEW_REQUIRED"
    )
    termination = (
        "GOVERNANCE_REVIEW_REQUIRED"
        if disposition_value == "GOVERNANCE_REVIEW_REQUIRED"
        else "CLASSIFIED"
    )
    capability_impact = (
        "COMPOSE"
        if outcome == "COMPOSE_EXISTING_CAPABILITIES"
        else "EXTEND"
        if outcome == "EXTEND_EXISTING_OWNER"
        else "NEW"
        if outcome == "NEW_REALIZATION_JUSTIFIED"
        else "REUSE"
        if outcome == "REUSE_EXISTING_UNCHANGED"
        else "UNRESOLVED"
    )
    classified_owner = (
        owners[0]
        if len(owners) == 1
        else "PLATFORM_CORE"
        if owners
        else str(
            lookup_platform_capability_certification(
                GLOBAL_EVIDENCE_SUBJECT
            )["capability_owner"]
        )
    )
    task = DevelopmentGovernanceTaskIntake(
        artifact_type=DEVELOPMENT_GOVERNANCE_TASK_INTAKE_ARTIFACT_V1,
        runtime_version=DEVELOPMENT_GOVERNANCE_RUNTIME_VERSION,
        intake_id=intake_id,
        request_identity=objective["source_request_hash"],
        objective=objective["canonical_project_objective"],
        action_mode="REPOSITORY_MUTATION_REQUESTED",
        declared_work_products=("IMPLEMENTATION_PLAN",),
        bounded_scope=objective_facets,
        constraints=EXPLICIT_PROHIBITIONS,
        non_goals=("AUTHORIZATION", "EXECUTION", "PLANNER_REDESIGN"),
        active_baseline_reference=CONSTITUTIONAL_BASELINE,
        clarification_requirements=(),
    )
    cdd = DevelopmentGovernanceCDDClassification(
        artifact_type=DEVELOPMENT_GOVERNANCE_CDD_CLASSIFICATION_ARTIFACT_V1,
        runtime_version=DEVELOPMENT_GOVERNANCE_RUNTIME_VERSION,
        cdd_id=cdd_id,
        intake_id=intake_id,
        baseline_reference=CONSTITUTIONAL_BASELINE,
        action_mode="REPOSITORY_MUTATION_REQUESTED",
        primary_work_class="CAPABILITY",
        secondary_impacts=("IMPLEMENTATION_PLANNING",),
        mutation_layer="L3",
        constitutional_impact="NONE",
        protocol_impact="NONE",
        realization_category="CAPABILITY_RUNTIME",
        realization_impact=(
            "NEW" if outcome == "NEW_REALIZATION_JUSTIFIED" else "REFINE"
        ),
        capability_impact=capability_impact,
        authority_impact="NONE",
        owner=classified_owner,
        affected_scope=objective_facets,
        required_reviews=(),
        explicit_prohibitions=EXPLICIT_PROHIBITIONS,
        unresolved_fields=(
            ("CAPABILITY_OWNER",) if termination != "CLASSIFIED" else ()
        ),
        termination_state=termination,
    )
    snapshot = DevelopmentGovernanceEvidenceSnapshot(
        artifact_type=DEVELOPMENT_GOVERNANCE_EVIDENCE_SNAPSHOT_ARTIFACT_V1,
        runtime_version=DEVELOPMENT_GOVERNANCE_RUNTIME_VERSION,
        snapshot_id=snapshot_id,
        cdd_id=cdd_id,
        baseline_reference=CONSTITUTIONAL_BASELINE,
        evidence_items=evidence,
    )
    need = DevelopmentGovernanceNeedAssessment(
        artifact_type=DEVELOPMENT_GOVERNANCE_NEED_ASSESSMENT_ARTIFACT_V1,
        runtime_version=DEVELOPMENT_GOVERNANCE_RUNTIME_VERSION,
        need_assessment_id=_identity("DG-NEED", snapshot_id),
        cdd_id=cdd_id,
        evidence_snapshot_id=snapshot_id,
        outcome=outcome,
        objective_facets=objective_facets,
        covered_facets=covered_facets,
        reusable_owners=owners,
        residual_gaps=planning_scope,
        duplication_risks=(),
        ownership_risks=(),
        smallest_justified_change_class=outcome,
        governance_impact="BOUNDED_PRE_PLANNING_GATE",
        replay_impact="ADDITIVE_LINEAGE_ONLY",
        evidence_references=evidence_ids,
    )
    disposition = DevelopmentGovernanceDisposition(
        artifact_type=DEVELOPMENT_GOVERNANCE_DISPOSITION_ARTIFACT_V1,
        runtime_version=DEVELOPMENT_GOVERNANCE_RUNTIME_VERSION,
        disposition_id=_identity("DG-DISPOSITION", need.need_assessment_id),
        cdd_id=cdd_id,
        need_assessment_id=need.need_assessment_id,
        baseline_reference=CONSTITUTIONAL_BASELINE,
        exact_scope=objective_facets,
        governance_disposition=disposition_value,
        review_references=(),
        explicit_prohibitions=EXPLICIT_PROHIBITIONS,
    )
    eligibility = DevelopmentGovernancePlanningEligibility(
        artifact_type=DEVELOPMENT_GOVERNANCE_PLANNING_ELIGIBILITY_ARTIFACT_V1,
        runtime_version=DEVELOPMENT_GOVERNANCE_RUNTIME_VERSION,
        planning_eligibility_id=_identity(
            "DG-ELIGIBILITY", disposition.disposition_id
        ),
        disposition_id=disposition.disposition_id,
        baseline_reference=CONSTITUTIONAL_BASELINE,
        planning_eligible=disposition_value == "BOUNDED_PLANNING_PERMITTED",
        residual_gap=(
            planning_scope
            if disposition_value == "BOUNDED_PLANNING_PERMITTED"
            else ()
        ),
        canonical_owners=(
            owners if disposition_value == "BOUNDED_PLANNING_PERMITTED" else ()
        ),
        dependencies=tuple(
            sorted(str(item["capability_identifier"]) for item in reusable)
        ),
        compatibility_requirements=(CONSTITUTIONAL_BASELINE,),
        validation_requirements=("FOCUSED_COMPATIBILITY_VALIDATION",),
        evidence_expectations=evidence_ids,
        replay_expectations=("ADDITIVE_G47_LINEAGE",),
        certification_expectations=("POST_VALIDATION_CERTIFICATION",),
        explicit_prohibitions=EXPLICIT_PROHIBITIONS,
    )
    return (task, cdd, snapshot, need, disposition, eligibility)


def _need_outcome(
    *,
    coverage: dict[str, Any],
    residual: tuple[str, ...],
    owner_count: int,
) -> str:
    classification = str(
        (coverage.get("minimal_required_platform_extension") or {}).get(
            "classification"
        )
        or ""
    )
    if classification == "GENUINELY_NEW_CAPABILITY_REQUIRED":
        return "NEW_REALIZATION_JUSTIFIED"
    if not residual:
        return "REUSE_EXISTING_UNCHANGED"
    if owner_count >= 2:
        return "COMPOSE_EXISTING_CAPABILITIES"
    if owner_count == 1:
        return "EXTEND_EXISTING_OWNER"
    if classification == "MINIMAL_COMPOSITION_SERVICE_REQUIRED":
        return "NEW_REALIZATION_JUSTIFIED"
    return "GOVERNANCE_REVIEW_REQUIRED"


def _evidence_items(
    *,
    coverage: dict[str, Any],
    reusable: tuple[dict[str, Any], ...],
    covered_facets: tuple[str, ...],
    residual_facets: tuple[str, ...],
) -> tuple[DevelopmentGovernanceEvidenceReference, ...]:
    claims: list[DevelopmentGovernanceEvidenceReference] = []
    for item in reusable:
        facets = tuple(
            sorted(
                str(value)
                for value in item.get("covered_facets") or []
                if isinstance(value, str) and value
            )
        )
        claims.append(
            _evidence_reference(
                subject_id=str(item["capability_identifier"]),
                claim_type="OBJECTIVE_FACET_COVERAGE",
                claim_value="COVERED",
                covered_facets=facets,
            )
        )
    if residual_facets:
        claims.append(
            _evidence_reference(
                subject_id=GLOBAL_EVIDENCE_SUBJECT,
                claim_type="OBJECTIVE_FACET_COVERAGE",
                claim_value="UNCOVERED",
                covered_facets=residual_facets,
            )
        )
    required = bool(residual_facets)
    global_claims = [
        ("IMPLEMENTATION_REQUIREMENT", "REQUIRED" if required else "NONE"),
        ("REQUESTED_RESULT_STATE", "NOT_PRODUCED"),
        ("REQUESTER_AMBIGUITY", "ABSENT"),
        ("CONSTITUTIONAL_AMBIGUITY", "ABSENT"),
        ("REQUESTED_STRUCTURE_RELATION", "NEUTRAL"),
        ("ARCHITECTURAL_DUPLICATION", "DISPROVEN"),
    ]
    classification = str(
        (coverage.get("minimal_required_platform_extension") or {}).get(
            "classification"
        )
        or ""
    )
    if classification in {
        "GENUINELY_NEW_CAPABILITY_REQUIRED",
        "MINIMAL_COMPOSITION_SERVICE_REQUIRED",
    } and not reusable:
        global_claims.extend(
            (
                ("EXISTING_CONTRACT", "EXISTS"),
                ("REALIZATION_AVAILABILITY", "NO_CURRENT_REALIZATION"),
                ("CONSTITUTIONAL_DISTINCTION", "NOT_DISTINCT"),
                ("SMALLER_CHANGE_OPTIONS", "DISPROVEN"),
                ("EXPANSION_JUSTIFICATION", "NOT_APPLICABLE"),
            )
        )
    elif len(reusable) >= 2 and required:
        global_claims.extend(
            (
                ("COMPOSITION_COVERAGE", "COMPLETE"),
                ("BINDING_STATE", "PRESENT"),
                ("EXPANSION_JUSTIFICATION", "NOT_APPLICABLE"),
            )
        )
    elif len(reusable) == 1 and required:
        global_claims.extend(
            (
                ("OWNER_EXTENSION_FIT", "WITHIN_OWNER"),
                ("REALIZATION_COMPLETENESS", "COMPLETE"),
                ("BINDING_STATE", "PRESENT"),
                ("COMPOSITION_COVERAGE", "INCOMPLETE"),
                ("EXPANSION_JUSTIFICATION", "NOT_APPLICABLE"),
            )
        )
    for claim_type, claim_value in global_claims:
        claims.append(
            _evidence_reference(
                subject_id=GLOBAL_EVIDENCE_SUBJECT,
                claim_type=claim_type,
                claim_value=claim_value,
                covered_facets=(),
                realization_complete=claim_type == "REALIZATION_COMPLETENESS",
            )
        )
    return tuple(sorted(claims, key=lambda item: item.evidence_id))


def _evidence_reference(
    *,
    subject_id: str,
    claim_type: str,
    claim_value: str,
    covered_facets: tuple[str, ...],
    realization_complete: bool = False,
) -> DevelopmentGovernanceEvidenceReference:
    authority = lookup_platform_capability_certification(subject_id)
    source_reference = str(authority["certification_evidence"][0])
    source_path = Path(__file__).resolve().parents[2] / source_reference
    content_hash = "sha256:" + hashlib.sha256(source_path.read_bytes()).hexdigest()
    responsibilities = (
        ("CERTIFIED_CAPABILITY_RUNTIME",) if realization_complete else ()
    )
    return DevelopmentGovernanceEvidenceReference(
        evidence_id=_identity(
            "DG-EVIDENCE",
            subject_id,
            claim_type,
            claim_value,
            *covered_facets,
        ),
        artifact_type="DEVELOPMENT_GOVERNANCE_EVIDENCE_V1",
        artifact_version="V1",
        subject_id=subject_id,
        subject_type="CAPABILITY",
        claim_type=claim_type,
        claim_value=claim_value,
        source_reference=source_reference,
        content_hash=content_hash,
        canonical_owner=str(authority["capability_owner"]),
        architectural_owner=str(authority["architectural_owner"]),
        baseline_id=CONSTITUTIONAL_BASELINE,
        certification_status=str(authority["certification_status"]),
        certification_scope=str(authority["certification_scope"]),
        certification_required=True,
        supersession_state=(
            "SUPERSEDED"
            if authority["superseded_by"] is not None
            or authority["certification_status"] == "SUPERSEDED"
            else "CURRENT"
        ),
        compatibility_scope=CONSTITUTIONAL_BASELINE,
        compatibility_status="COMPATIBLE",
        reconstruction_required=False,
        covered_facets=covered_facets,
        known_limitations=(),
        residual_responsibilities=(),
        declared_responsibilities=responsibilities,
        implemented_responsibilities=responsibilities,
        source_endpoint=None,
        target_endpoint=None,
        interface_identity=None,
        interface_version=None,
    )


def _identity(prefix: str, *values: str) -> str:
    return f"{prefix}:{replay_hash(list(values))}"


def _persist_record(replay_dir: Path, artifact: dict[str, Any]) -> None:
    wrapper = {
        "replay_index": 0,
        "replay_step": "development_governance_integration_recorded",
        "artifact": artifact,
    }
    wrapper["replay_hash"] = replay_hash(wrapper)
    write_json_immutable(
        replay_dir / "000_development_governance_integration_recorded.json",
        wrapper,
    )


def _stage_outputs_from_dicts(value: Any) -> tuple[Any, ...]:
    if not isinstance(value, list) or len(value) != 6:
        raise DevelopmentGovernanceRuntimeError(
            "G47 operational stage outputs are incomplete"
        )
    items = [dict(item) for item in value]
    evidence_items = []
    for raw_item in items[2]["evidence_items"]:
        item = dict(raw_item)
        for key, field_value in tuple(item.items()):
            if isinstance(field_value, list):
                item[key] = tuple(field_value)
        evidence_items.append(DevelopmentGovernanceEvidenceReference(**item))
    items[2]["evidence_items"] = tuple(evidence_items)
    for index in (0, 1, 3, 4, 5):
        for key, field_value in tuple(items[index].items()):
            if isinstance(field_value, list):
                items[index][key] = tuple(field_value)
    return (
        DevelopmentGovernanceTaskIntake(**items[0]),
        DevelopmentGovernanceCDDClassification(**items[1]),
        DevelopmentGovernanceEvidenceSnapshot(**items[2]),
        DevelopmentGovernanceNeedAssessment(**items[3]),
        DevelopmentGovernanceDisposition(**items[4]),
        DevelopmentGovernancePlanningEligibility(**items[5]),
    )


def _bundle_from_dict(value: Any) -> ConstitutionalDevelopmentGovernanceBundle:
    if not isinstance(value, dict):
        raise DevelopmentGovernanceRuntimeError(
            "G47 operational bundle is missing"
        )
    candidate = dict(value)
    candidate["stage_order"] = tuple(candidate["stage_order"])
    candidate["stage_references"] = tuple(
        DevelopmentGovernanceStageReference(**item)
        for item in candidate["stage_references"]
    )
    if candidate.get("artifact_type") != (
        CONSTITUTIONAL_DEVELOPMENT_GOVERNANCE_BUNDLE_ARTIFACT_V1
    ):
        raise DevelopmentGovernanceRuntimeError(
            "G47 operational bundle type is invalid"
        )
    return ConstitutionalDevelopmentGovernanceBundle(**candidate)


__all__ = [
    "G47_OPERATIONAL_INTEGRATION_ARTIFACT_V1",
    "G47_OPERATIONAL_INTEGRATION_READY",
    "G47_OPERATIONAL_INTEGRATION_TERMINATED",
    "G47_OPERATIONAL_INTEGRATION_VERSION",
    "integrate_constitutional_development_governance",
    "reconstruct_constitutional_development_governance_operational_replay",
    "validate_constitutional_development_governance_operational_record",
]
