"""Constitutional G64 completion branch composition for B8.

This bounded composition authenticates one accepted governed-development
mutation branch, hands the unchanged pending capture to the certified G64
completion owner, and binds deterministic completion and Human-return
provenance under the G69-15 branch model.  It does not invoke Canonical Human
Entry or a HIC, add semantics to HIC, create complete branch Replay/CRO
coverage, or cut over a production consumer.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

from aigol.runtime import constitutional_certification_completion_gate as g64_v1
from aigol.runtime.canonical_common_failure_presentation_owner_projection_contract_v1 import (
    TERMINAL_OUTCOME,
    TERMINAL_PRESENTATION,
    CanonicalPresentationV1,
    create_canonical_presentation_v1,
    validate_canonical_presentation_v1,
)
from aigol.runtime.constitutional_governance_certification import (
    ConstitutionalCertification,
)
from aigol.runtime.constitutional_production_workflow_branch_contract_v1 import (
    CONSTITUTIONAL_COMPLETION,
    CONTENT_OR_REPOSITORY_MUTATION,
    GOVERNED_ACTION,
    GOVERNED_DEVELOPMENT,
    HUMAN_RETURN,
    CanonicalProductionWorkflowBranchModelV1,
    CanonicalWorkflowBranchProvenanceV1,
    CanonicalWorkflowEvidenceReferenceV1,
    bind_canonical_workflow_branch_provenance_v1,
    create_canonical_production_workflow_branch_model_v1,
    validate_canonical_production_workflow_branch_model_v1,
    validate_canonical_workflow_branch_journey_v1,
    validate_canonical_workflow_branch_provenance_v1,
)
from aigol.runtime.constitutional_replay_governance import (
    ConstitutionalGovernanceAssessment,
)
from aigol.runtime.governance_promotion_discipline import GovernancePromotionResult
from aigol.runtime.governed_development_workflow_runtime import (
    AWAITING_CONSTITUTIONAL_CERTIFICATION_AND_PROMOTION,
    GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED,
)
from aigol.runtime.governed_repository_mutation_runtime import (
    GOVERNED_REPOSITORY_MUTATION_COMPLETED,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash
from aigol.runtime.validation_command_runner_runtime import VALIDATION_COMMAND_COMPLETED


CONSTITUTIONAL_G64_COMPLETION_BRANCH_COMPOSITION_V1 = (
    "CONSTITUTIONAL_G64_COMPLETION_BRANCH_COMPOSITION_V1"
)
CONSTITUTIONAL_G64_COMPLETION_BRANCH_COMPOSITION_RESULT_V1 = (
    "CONSTITUTIONAL_G64_COMPLETION_BRANCH_COMPOSITION_RESULT_V1"
)
CONSTITUTIONAL_G64_COMPLETION_PROVENANCE_V1 = (
    "CONSTITUTIONAL_G64_COMPLETION_PROVENANCE_V1"
)

COMPLETION_BRANCH_ESTABLISHED = "COMPLETION_BRANCH_ESTABLISHED"
COMPLETION_BRANCH_FAILED_CLOSED = "COMPLETION_BRANCH_FAILED_CLOSED"

G31_ACCEPTED_MUTATION_OWNER = "HUMAN_AUTHORITY_PLUS_MUTATION_AUTHORIZATION"
G64_CONSTITUTIONAL_COMPLETION_OWNER = "G64_CONSTITUTIONAL_COMPLETION_OWNER"
CANONICAL_HIR_PRESENTATION_OWNER = "CANONICAL_HIR_PRESENTATION_OWNER"

_PRE_COMPLETION_BRANCHES = (
    GOVERNED_ACTION,
    GOVERNED_DEVELOPMENT,
    CONTENT_OR_REPOSITORY_MUTATION,
)
_SUCCESS_BRANCHES = (*_PRE_COMPLETION_BRANCHES, CONSTITUTIONAL_COMPLETION, HUMAN_RETURN)
_SUCCESS_OWNER_HANDOFF = (
    G31_ACCEPTED_MUTATION_OWNER,
    G64_CONSTITUTIONAL_COMPLETION_OWNER,
    CANONICAL_HIR_PRESENTATION_OWNER,
)
_ACCEPTED_MUTATION_BINDINGS = {
    "VALIDATED_RESULT": "validation_hash",
    "MUTATION_AUTHORIZATION": "approval_hash",
    "REPLACEMENT_WORKER_RESULT": "worker_mutation_hash",
}
_BOUNDARIES = {
    "canonical_entry_invoked": False,
    "hic_invoked": False,
    "hic_semantic_capability_added": False,
    "natural_conversation_invoked": False,
    "repository_mutated_by_composition": False,
    "worker_invoked_by_composition": False,
    "authorization_created_by_composition": False,
    "branch_replay_coverage_created": False,
    "cro_observation_performed": False,
    "production_cutover_performed": False,
}


def _fail(message: str) -> None:
    raise FailClosedRuntimeError(message)


def _text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        _fail(f"G64 completion branch {field_name} is absent or malformed")
    return value


def _verify_hash_bound_mapping(
    value: Any,
    *,
    hash_field: str,
    field_name: str,
) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        _fail(f"G64 completion branch {field_name} is absent or malformed")
    candidate = deepcopy(dict(value))
    actual = candidate.pop(hash_field, None)
    if not isinstance(actual, str) or actual != replay_hash(candidate):
        _fail(f"G64 completion branch {field_name} integrity is invalid")
    candidate[hash_field] = actual
    return candidate


def _evidence_by_role(
    provenance: CanonicalWorkflowBranchProvenanceV1,
) -> dict[str, CanonicalWorkflowEvidenceReferenceV1]:
    return {item.evidence_role: item for item in provenance.evidence_references}


def _validate_pre_completion_journey(
    *,
    model: CanonicalProductionWorkflowBranchModelV1,
    provenances: tuple[CanonicalWorkflowBranchProvenanceV1, ...],
) -> tuple[CanonicalWorkflowBranchProvenanceV1, ...]:
    if not isinstance(provenances, tuple) or len(provenances) != 3:
        _fail("G64 completion branch accepted-mutation journey is incomplete")
    validated = tuple(
        validate_canonical_workflow_branch_provenance_v1(
            model=model,
            value=item,
        )
        for item in provenances
    )
    if tuple(item.branch_kind for item in validated) != _PRE_COMPLETION_BRANCHES:
        _fail("G64 completion branch accepted-mutation journey is invalid")
    request_identity = validated[0].source_request_identity
    interaction_identity = validated[0].source_interaction_identity
    for index, current in enumerate(validated, start=1):
        if (
            current.branch_sequence != index
            or current.source_request_identity != request_identity
            or current.source_interaction_identity != interaction_identity
        ):
            _fail("G64 completion branch accepted-mutation source binding is invalid")
        if index == 1:
            if current.predecessor_branch_kind is not None:
                _fail("G64 completion branch accepted-mutation predecessor is invalid")
            continue
        previous = validated[index - 2]
        if (
            current.predecessor_branch_kind != previous.branch_kind
            or current.previous_provenance_identity
            != previous.provenance_identity
        ):
            _fail("G64 completion branch accepted-mutation predecessor is invalid")
    return validated


def _validate_accepted_mutation_handoff(
    *,
    accepted_mutation: CanonicalWorkflowBranchProvenanceV1,
    governed_development_capture: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    capture = _verify_hash_bound_mapping(
        governed_development_capture,
        hash_field="governed_development_capture_hash",
        field_name="governed-development capture",
    )
    if (
        capture.get("execution_status")
        != AWAITING_CONSTITUTIONAL_CERTIFICATION_AND_PROMOTION
        or capture.get("approval_bypassed") is not False
        or capture.get("fail_closed") is not False
    ):
        _fail("G64 completion branch pending governed development is inadmissible")
    pending = _verify_hash_bound_mapping(
        capture.get("governed_development_outcome"),
        hash_field="artifact_hash",
        field_name="pending governed-development outcome",
    )
    repository_capture = _verify_hash_bound_mapping(
        capture.get("governed_repository_mutation_capture"),
        hash_field="governed_repository_mutation_capture_hash",
        field_name="governed repository mutation capture",
    )
    repository_outcome = _verify_hash_bound_mapping(
        repository_capture.get("governed_repository_mutation_outcome"),
        hash_field="artifact_hash",
        field_name="governed repository mutation outcome",
    )
    if (
        pending.get("execution_id") != capture.get("execution_id")
        or pending.get("execution_status")
        != AWAITING_CONSTITUTIONAL_CERTIFICATION_AND_PROMOTION
        or pending.get("governed_repository_mutation_hash")
        != repository_outcome.get("artifact_hash")
        or pending.get("constitutional_completion_reached") is not False
        or pending.get("promotion_eligible") is not False
        or repository_outcome.get("execution_status")
        != GOVERNED_REPOSITORY_MUTATION_COMPLETED
        or repository_outcome.get("approval_bypassed") is not False
        or repository_outcome.get("repository_mutation_worker_used") is not True
        or repository_outcome.get("validation_status")
        != VALIDATION_COMMAND_COMPLETED
    ):
        _fail("G64 completion branch accepted mutation is not validated")
    references = _evidence_by_role(accepted_mutation)
    for role, outcome_field in _ACCEPTED_MUTATION_BINDINGS.items():
        reference = references.get(role)
        if (
            reference is None
            or reference.artifact_digest != repository_outcome.get(outcome_field)
        ):
            _fail(f"G64 completion branch {role} hand-off is invalid")
    return capture, pending


def _completion_evidence_references(
    *,
    pending: Mapping[str, Any],
    g48_report_evidence: Mapping[str, Any],
    governance_assessment: ConstitutionalGovernanceAssessment,
    constitutional_certification: ConstitutionalCertification,
    promotion_evidence: GovernancePromotionResult,
) -> tuple[CanonicalWorkflowEvidenceReferenceV1, ...]:
    return (
        CanonicalWorkflowEvidenceReferenceV1(
            evidence_role="GOVERNED_DEVELOPMENT_PENDING_COMPLETION",
            producing_owner=G64_CONSTITUTIONAL_COMPLETION_OWNER,
            artifact_identity=_text(pending.get("execution_id"), "pending identity"),
            artifact_digest=_text(pending.get("artifact_hash"), "pending digest"),
        ),
        CanonicalWorkflowEvidenceReferenceV1(
            evidence_role="EXTERNAL_G48_REPORT",
            producing_owner="G48_REPORTING_OWNER",
            artifact_identity=_text(g48_report_evidence.get("report_id"), "G48 report identity"),
            artifact_digest=_text(g48_report_evidence.get("artifact_hash"), "G48 report digest"),
        ),
        CanonicalWorkflowEvidenceReferenceV1(
            evidence_role="GOVERNANCE_ASSESSMENT",
            producing_owner="DEVELOPMENT_GOVERNANCE_OWNER",
            artifact_identity=_text(governance_assessment.assessment_id, "Governance assessment identity"),
            artifact_digest=_text(governance_assessment.assessment_hash, "Governance assessment digest"),
        ),
        CanonicalWorkflowEvidenceReferenceV1(
            evidence_role="CONSTITUTIONAL_CERTIFICATION",
            producing_owner="CONSTITUTIONAL_CERTIFICATION_OWNER",
            artifact_identity=_text(constitutional_certification.certification_id, "Certification identity"),
            artifact_digest=_text(constitutional_certification.certification_hash, "Certification digest"),
        ),
        CanonicalWorkflowEvidenceReferenceV1(
            evidence_role="PROMOTION_DECISION",
            producing_owner="PROMOTION_OWNER",
            artifact_identity=_text(promotion_evidence.promotion_id, "promotion identity"),
            artifact_digest=_text(promotion_evidence.evidence_hash, "promotion digest"),
        ),
    )


def _validate_g64_success_capture(value: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    capture = _verify_hash_bound_mapping(
        value,
        hash_field="capture_hash",
        field_name="G64 completion capture",
    )
    terminal = _verify_hash_bound_mapping(
        capture.get("constitutional_completion_artifact"),
        hash_field="artifact_hash",
        field_name="G64 completion artifact",
    )
    if (
        capture.get("completion_status") != GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED
        or capture.get("constitutional_completion_reached") is not True
        or capture.get("promotion_eligible") is not True
        or capture.get("fail_closed") is not False
        or capture.get("repository_mutated") is not False
        or capture.get("worker_invoked") is not False
        or capture.get("authorization_created") is not False
        or terminal.get("completion_status")
        != GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED
        or terminal.get("constitutional_completion_reached") is not True
    ):
        _fail("G64 completion branch owner result is invalid")
    return capture, terminal


def _presentation(
    *,
    source_request_identity: str,
    terminal: Mapping[str, Any],
) -> CanonicalPresentationV1:
    finalization_id = _text(terminal.get("finalization_id"), "finalization identity")
    related_change_id = _text(terminal.get("related_change_id"), "related change identity")
    return create_canonical_presentation_v1(
        request_identity=source_request_identity,
        response_identity=f"{finalization_id}:CANONICAL-HUMAN-RETURN",
        presentation_state=TERMINAL_PRESENTATION,
        presentation_kind=TERMINAL_OUTCOME,
        presentation_message=(
            "Constitutional completion established.",
            f"Related change: {related_change_id}",
            f"Finalization: {finalization_id}",
        ),
        presentation_controls=(),
        presentation_metadata={
            "producing_owner": G64_CONSTITUTIONAL_COMPLETION_OWNER,
            "completion_artifact_digest": terminal["artifact_hash"],
        },
    )


def _completion_provenance(
    *,
    model: CanonicalProductionWorkflowBranchModelV1,
    journey: tuple[CanonicalWorkflowBranchProvenanceV1, ...],
    pending: Mapping[str, Any],
    terminal: Mapping[str, Any],
    presentation: CanonicalPresentationV1,
    finalized_at: str,
) -> dict[str, Any]:
    value = {
        "artifact_type": CONSTITUTIONAL_G64_COMPLETION_PROVENANCE_V1,
        "runtime_version": CONSTITUTIONAL_G64_COMPLETION_BRANCH_COMPOSITION_V1,
        "model_identity": model.model_identity,
        "source_request_identity": journey[0].source_request_identity,
        "source_interaction_identity": journey[0].source_interaction_identity,
        "accepted_mutation_provenance_identity": journey[2].provenance_identity,
        "accepted_mutation_artifact_digest": _evidence_by_role(journey[2])[
            "REPLACEMENT_WORKER_RESULT"
        ].artifact_digest,
        "pending_completion_artifact_digest": pending["artifact_hash"],
        "completion_branch_provenance_identity": journey[3].provenance_identity,
        "g64_completion_artifact_digest": terminal["artifact_hash"],
        "canonical_presentation_identity": presentation.presentation_identity,
        "human_return_provenance_identity": journey[4].provenance_identity,
        "branch_sequence": list(_SUCCESS_BRANCHES),
        "owner_handoff_order": list(_SUCCESS_OWNER_HANDOFF),
        "finalized_at": finalized_at,
    }
    value["provenance_hash"] = replay_hash(value)
    return value


def _result(
    *,
    composition_status: str,
    failure_code: str | None,
    g64_finalizer_invoked: bool,
    completion_capture: Mapping[str, Any] | None,
    branch_journey: tuple[CanonicalWorkflowBranchProvenanceV1, ...],
    presentation: CanonicalPresentationV1 | None,
    completion_provenance: Mapping[str, Any] | None,
) -> dict[str, Any]:
    value = {
        "result_type": CONSTITUTIONAL_G64_COMPLETION_BRANCH_COMPOSITION_RESULT_V1,
        "runtime_version": CONSTITUTIONAL_G64_COMPLETION_BRANCH_COMPOSITION_V1,
        "composition_status": composition_status,
        "failure_code": failure_code,
        "g64_finalizer_invoked": g64_finalizer_invoked,
        "owner_handoff_order": (
            list(_SUCCESS_OWNER_HANDOFF)
            if composition_status == COMPLETION_BRANCH_ESTABLISHED
            else []
        ),
        "completion_capture": deepcopy(dict(completion_capture)) if completion_capture else None,
        "branch_journey": [item.to_dict() for item in branch_journey],
        "canonical_presentation": presentation.to_dict() if presentation else None,
        "completion_provenance": deepcopy(dict(completion_provenance)) if completion_provenance else None,
        **deepcopy(_BOUNDARIES),
    }
    value["result_hash"] = replay_hash(value)
    return value


def validate_constitutional_g64_completion_branch_composition_result_v1(
    value: Any,
) -> dict[str, Any]:
    expected_fields = {
        "result_type",
        "runtime_version",
        "composition_status",
        "failure_code",
        "g64_finalizer_invoked",
        "owner_handoff_order",
        "completion_capture",
        "branch_journey",
        "canonical_presentation",
        "completion_provenance",
        *_BOUNDARIES,
        "result_hash",
    }
    if not isinstance(value, Mapping) or set(value) != expected_fields:
        _fail("G64 completion branch result is malformed")
    candidate = deepcopy(dict(value))
    actual_hash = candidate.pop("result_hash")
    if actual_hash != replay_hash(candidate):
        _fail("G64 completion branch result integrity is invalid")
    candidate["result_hash"] = actual_hash
    if (
        candidate["result_type"]
        != CONSTITUTIONAL_G64_COMPLETION_BRANCH_COMPOSITION_RESULT_V1
        or candidate["runtime_version"]
        != CONSTITUTIONAL_G64_COMPLETION_BRANCH_COMPOSITION_V1
        or any(candidate[field] is not False for field in _BOUNDARIES)
    ):
        _fail("G64 completion branch acquired forbidden authority")
    if candidate["composition_status"] == COMPLETION_BRANCH_FAILED_CLOSED:
        if (
            not isinstance(candidate["failure_code"], str)
            or not candidate["failure_code"]
            or not isinstance(candidate["g64_finalizer_invoked"], bool)
            or candidate["owner_handoff_order"] != []
            or candidate["completion_capture"] is not None
            or candidate["branch_journey"] != []
            or candidate["canonical_presentation"] is not None
            or candidate["completion_provenance"] is not None
        ):
            _fail("G64 completion branch failed-closed result is invalid")
        canonical_serialize(candidate)
        return candidate
    if candidate["composition_status"] != COMPLETION_BRANCH_ESTABLISHED:
        _fail("G64 completion branch disposition is invalid")
    if (
        candidate["failure_code"] is not None
        or candidate["g64_finalizer_invoked"] is not True
        or candidate["owner_handoff_order"] != list(_SUCCESS_OWNER_HANDOFF)
        or len(candidate["branch_journey"]) != 5
    ):
        _fail("G64 completion branch established result is incomplete")
    capture, terminal = _validate_g64_success_capture(candidate["completion_capture"])
    presentation = validate_canonical_presentation_v1(
        candidate["canonical_presentation"]
    )
    journey = tuple(
        CanonicalWorkflowBranchProvenanceV1.from_dict(item)
        for item in candidate["branch_journey"]
    )
    if tuple(item.branch_kind for item in journey) != _SUCCESS_BRANCHES:
        _fail("G64 completion branch journey is invalid")
    model = validate_canonical_production_workflow_branch_model_v1(
        create_canonical_production_workflow_branch_model_v1()
    )
    validate_canonical_workflow_branch_journey_v1(
        model=model,
        provenances=journey,
    )
    provenance = deepcopy(candidate["completion_provenance"])
    if not isinstance(provenance, dict):
        _fail("G64 completion branch provenance is absent")
    if set(provenance) != {
        "artifact_type",
        "runtime_version",
        "model_identity",
        "source_request_identity",
        "source_interaction_identity",
        "accepted_mutation_provenance_identity",
        "accepted_mutation_artifact_digest",
        "pending_completion_artifact_digest",
        "completion_branch_provenance_identity",
        "g64_completion_artifact_digest",
        "canonical_presentation_identity",
        "human_return_provenance_identity",
        "branch_sequence",
        "owner_handoff_order",
        "finalized_at",
        "provenance_hash",
    }:
        _fail("G64 completion branch provenance is malformed")
    body = deepcopy(provenance)
    provenance_hash = body.pop("provenance_hash", None)
    completion_references = _evidence_by_role(journey[3])
    human_return_references = _evidence_by_role(journey[4])
    accepted_mutation_references = _evidence_by_role(journey[2])
    if (
        provenance_hash != replay_hash(body)
        or provenance.get("artifact_type")
        != CONSTITUTIONAL_G64_COMPLETION_PROVENANCE_V1
        or provenance.get("model_identity") != model.model_identity
        or provenance.get("source_request_identity")
        != journey[0].source_request_identity
        or provenance.get("source_interaction_identity")
        != journey[0].source_interaction_identity
        or provenance.get("accepted_mutation_provenance_identity")
        != journey[2].provenance_identity
        or provenance.get("accepted_mutation_artifact_digest")
        != accepted_mutation_references["REPLACEMENT_WORKER_RESULT"].artifact_digest
        or provenance.get("pending_completion_artifact_digest")
        != completion_references[
            "GOVERNED_DEVELOPMENT_PENDING_COMPLETION"
        ].artifact_digest
        or provenance.get("completion_branch_provenance_identity")
        != journey[3].provenance_identity
        or provenance.get("g64_completion_artifact_digest")
        != terminal["artifact_hash"]
        or provenance.get("canonical_presentation_identity")
        != presentation.presentation_identity
        or provenance.get("human_return_provenance_identity")
        != journey[4].provenance_identity
        or provenance.get("branch_sequence") != list(_SUCCESS_BRANCHES)
        or provenance.get("owner_handoff_order") != list(_SUCCESS_OWNER_HANDOFF)
        or capture["related_change_id"] != terminal["related_change_id"]
        or completion_references[
            "GOVERNED_DEVELOPMENT_PENDING_COMPLETION"
        ].artifact_identity
        != terminal["related_change_id"]
        or completion_references[
            "GOVERNED_DEVELOPMENT_PENDING_COMPLETION"
        ].artifact_digest
        != terminal["pending_outcome_hash"]
        or completion_references["EXTERNAL_G48_REPORT"].artifact_digest
        != terminal["g48_report_evidence_hash"]
        or completion_references["GOVERNANCE_ASSESSMENT"].artifact_digest
        != terminal["governance_assessment_hash"]
        or completion_references["CONSTITUTIONAL_CERTIFICATION"].artifact_digest
        != terminal["constitutional_certification_hash"]
        or completion_references["PROMOTION_DECISION"].artifact_digest
        != terminal["promotion_evidence_hash"]
        or human_return_references["BRANCH_TERMINAL_EVIDENCE"].artifact_digest
        != terminal["artifact_hash"]
        or human_return_references["CANONICAL_PRESENTATION"].artifact_digest
        != replay_hash(presentation.to_dict())
        or presentation.request_identity != journey[0].source_request_identity
        or presentation.response_identity
        != f"{terminal['finalization_id']}:CANONICAL-HUMAN-RETURN"
        or presentation.presentation_metadata.get("completion_artifact_digest")
        != terminal["artifact_hash"]
    ):
        _fail("G64 completion branch provenance is invalid")
    canonical_serialize(candidate)
    return candidate


def compose_constitutional_g64_completion_branch_v1(
    *,
    workflow_model: CanonicalProductionWorkflowBranchModelV1 | Mapping[str, Any],
    pre_completion_journey: tuple[CanonicalWorkflowBranchProvenanceV1, ...],
    governed_development_capture: Mapping[str, Any],
    g48_report_evidence: Mapping[str, Any],
    governance_assessment: ConstitutionalGovernanceAssessment,
    constitutional_certification: ConstitutionalCertification,
    promotion_evidence: GovernancePromotionResult | Mapping[str, Any],
    finalization_id: str,
    finalized_by: str,
    finalized_at: str,
    completion_replay_dir: str | Path,
) -> dict[str, Any]:
    """Compose accepted mutation -> G64 completion -> canonical Human return."""

    finalizer_invoked = False
    try:
        model = validate_canonical_production_workflow_branch_model_v1(workflow_model)
        prefix = _validate_pre_completion_journey(
            model=model,
            provenances=pre_completion_journey,
        )
        capture, pending = _validate_accepted_mutation_handoff(
            accepted_mutation=prefix[-1],
            governed_development_capture=governed_development_capture,
        )
        report = g64_v1.validate_g48_completion_report_evidence(
            dict(g48_report_evidence)
        )
        promotion = (
            GovernancePromotionResult.from_dict(dict(promotion_evidence))
            if isinstance(promotion_evidence, Mapping)
            else promotion_evidence
        )
        if not isinstance(promotion, GovernancePromotionResult):
            _fail("G64 completion branch promotion evidence is invalid")
        completion_references = _completion_evidence_references(
            pending=pending,
            g48_report_evidence=report,
            governance_assessment=governance_assessment,
            constitutional_certification=constitutional_certification,
            promotion_evidence=promotion,
        )
        finalizer_invoked = True
        completion_capture = g64_v1.finalize_governed_development_completion(
            finalization_id=finalization_id,
            governed_development_capture=capture,
            g48_report_evidence=report,
            governance_assessment=governance_assessment,
            constitutional_certification=constitutional_certification,
            promotion_evidence=promotion,
            finalized_by=finalized_by,
            finalized_at=finalized_at,
            replay_dir=completion_replay_dir,
        )
        completion_capture, terminal = _validate_g64_success_capture(
            completion_capture
        )
        completion_branch = bind_canonical_workflow_branch_provenance_v1(
            model=model,
            source_request_identity=prefix[0].source_request_identity,
            source_interaction_identity=prefix[0].source_interaction_identity,
            branch_sequence=4,
            branch_kind=CONSTITUTIONAL_COMPLETION,
            predecessor_branch_kind=CONTENT_OR_REPOSITORY_MUTATION,
            previous_provenance_identity=prefix[-1].provenance_identity,
            predicate_facts={
                "constitutional_completion_applicability": (
                    "GOVERNED_DEVELOPMENT_CHANGE_VALIDATED"
                )
            },
            evidence_references=completion_references,
            observed_at=finalized_at,
        )
        presentation = _presentation(
            source_request_identity=prefix[0].source_request_identity,
            terminal=terminal,
        )
        human_return = bind_canonical_workflow_branch_provenance_v1(
            model=model,
            source_request_identity=prefix[0].source_request_identity,
            source_interaction_identity=prefix[0].source_interaction_identity,
            branch_sequence=5,
            branch_kind=HUMAN_RETURN,
            predecessor_branch_kind=CONSTITUTIONAL_COMPLETION,
            previous_provenance_identity=completion_branch.provenance_identity,
            predicate_facts={
                "human_return_eligibility": "BRANCH_TERMINAL_EVIDENCE_COMPLETE"
            },
            evidence_references=(
                CanonicalWorkflowEvidenceReferenceV1(
                    evidence_role="BRANCH_TERMINAL_EVIDENCE",
                    producing_owner="BRANCH_TERMINAL_OWNER",
                    artifact_identity=terminal["finalization_id"],
                    artifact_digest=terminal["artifact_hash"],
                ),
                CanonicalWorkflowEvidenceReferenceV1(
                    evidence_role="CANONICAL_PRESENTATION",
                    producing_owner=CANONICAL_HIR_PRESENTATION_OWNER,
                    artifact_identity=presentation.presentation_identity,
                    artifact_digest=replay_hash(presentation.to_dict()),
                ),
            ),
            observed_at=finalized_at,
        )
        journey = validate_canonical_workflow_branch_journey_v1(
            model=model,
            provenances=(*prefix, completion_branch, human_return),
        )
        provenance = _completion_provenance(
            model=model,
            journey=journey,
            pending=pending,
            terminal=terminal,
            presentation=presentation,
            finalized_at=finalized_at,
        )
        return validate_constitutional_g64_completion_branch_composition_result_v1(
            _result(
                composition_status=COMPLETION_BRANCH_ESTABLISHED,
                failure_code=None,
                g64_finalizer_invoked=True,
                completion_capture=completion_capture,
                branch_journey=journey,
                presentation=presentation,
                completion_provenance=provenance,
            )
        )
    except Exception as exc:
        failure_code = str(exc) or exc.__class__.__name__
        return validate_constitutional_g64_completion_branch_composition_result_v1(
            _result(
                composition_status=COMPLETION_BRANCH_FAILED_CLOSED,
                failure_code=failure_code,
                g64_finalizer_invoked=finalizer_invoked,
                completion_capture=None,
                branch_journey=(),
                presentation=None,
                completion_provenance=None,
            )
        )


__all__ = [
    "COMPLETION_BRANCH_ESTABLISHED",
    "COMPLETION_BRANCH_FAILED_CLOSED",
    "CONSTITUTIONAL_G64_COMPLETION_BRANCH_COMPOSITION_RESULT_V1",
    "CONSTITUTIONAL_G64_COMPLETION_BRANCH_COMPOSITION_V1",
    "CONSTITUTIONAL_G64_COMPLETION_PROVENANCE_V1",
    "compose_constitutional_g64_completion_branch_v1",
    "validate_constitutional_g64_completion_branch_composition_result_v1",
]
