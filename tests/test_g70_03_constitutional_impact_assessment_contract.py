from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from hashlib import sha256
from pathlib import Path

import pytest

from aigol.runtime.constitutional_amendment_proposal_contract_v1 import (
    CONSTITUTIONAL_BASELINE_EVIDENCE,
    CONSTITUTIONAL_GOVERNANCE_OWNER,
    GAP_DETERMINATION_EVIDENCE,
    PROPOSER_AUTHORITY_EVIDENCE,
    TARGET_CONSTITUTIONAL_ARTIFACT_EVIDENCE,
    ConstitutionalAmendmentProposalEvidenceReferenceV1,
    create_constitutional_amendment_proposal_v1,
)
from aigol.runtime.constitutional_gap_determination_evidence_contract_v1 import (
    determine_constitutional_gap_v1,
)
from aigol.runtime.constitutional_impact_assessment_contract_v1 import (
    ASSESSOR_AUTHORITY_EVIDENCE,
    BOUNDED_CONSTITUTIONAL_IMPACT,
    CONSTITUTIONAL_BOUNDARY_IMPACT,
    CONSTITUTIONAL_IMPACT_ASSESSMENT_ARTIFACT_VERSION,
    CONSTITUTIONAL_IMPACT_ASSESSMENT_CONTRACT_VERSION,
    CONTRACT_CONFLICT,
    CONTRACT_IMPACT_COMPLETENESS_EVIDENCE,
    CONTRACT_IMPACT_UNRESOLVED,
    CRO_AUTHORITY_EXPANSION_PROPOSED,
    CRO_IMPACT_EVIDENCE,
    CRO_IMPACT_UNRESOLVED,
    CRO_OBSERVATION_EXTENSION_REQUIRED,
    CRO_UNCHANGED,
    CROSS_CONSTITUTIONAL_IMPACT,
    DEPENDENCY_IMPACT,
    IMPACT_ASSESSED_NOT_RATIFIED,
    INVARIANT_CONFLICT,
    INVARIANT_IMPACT_COMPLETENESS_EVIDENCE,
    INVARIANT_IMPACT_UNRESOLVED,
    INVARIANT_MODIFICATION_PROPOSED,
    INVARIANT_PRESERVED,
    NEW_OWNER_PROPOSED,
    ONE_PRODUCTION_PATH_PRESERVED,
    OWNER_IMPACT_COMPLETENESS_EVIDENCE,
    OWNER_IMPACT_UNRESOLVED,
    OWNER_LOCAL_REPLAY_CUSTODIAN,
    OWNER_RESPONSIBILITY_CHANGE_PROPOSED,
    OWNER_RESPONSIBILITY_UNCHANGED,
    PASSIVE_CONSTITUTIONAL_RUNTIME_OBSERVATORY,
    PRODUCTION_PATH_CHANGE_PROPOSED,
    PRODUCTION_PATH_IMPACT_EVIDENCE,
    PRODUCTION_PATH_IMPACT_UNRESOLVED,
    PROPOSAL_BINDING_EVIDENCE,
    REPLAY_CORRELATION_EXTENSION_REQUIRED,
    REPLAY_IMPACT_EVIDENCE,
    REPLAY_IMPACT_UNRESOLVED,
    REPLAY_SAFETY_DEGRADATION_PROPOSED,
    REPLAY_UNCHANGED,
    SUCCESSOR_REQUIRED,
    UNBOUNDED_OWNER_AUTHORITY_PROPOSED,
    UNRESOLVED_CONSTITUTIONAL_IMPACT,
    AffectedConstitutionalContractV1,
    AffectedConstitutionalInvariantV1,
    ConstitutionalImpactEvidenceReferenceV1,
    ConstitutionalOwnerImpactV1,
    assess_constitutional_impact_v1,
    validate_affected_constitutional_contract_v1,
    validate_affected_constitutional_invariant_v1,
    validate_constitutional_impact_assessment_artifact_v1,
    validate_constitutional_impact_evidence_reference_v1,
    validate_constitutional_owner_impact_v1,
)
from aigol.runtime.models import FailClosedRuntimeError


MODULE = Path("aigol/runtime/constitutional_impact_assessment_contract_v1.py")
BASELINE = "constitutional-baseline-G70-02"
PROPOSER = "DECLARED_CONSTITUTIONAL_PROPOSER"
ASSESSOR = "CONSTITUTIONAL_IMPACT_ASSESSMENT_OWNER"
TARGET_OWNER = "CONSTITUTIONAL_FLOW_OWNER"
TARGET_IDENTITY = "CONSTITUTIONAL_FLOW_ARCHITECTURE_SPEC_V1"
TARGET_VERSION = "V1"
ASSESSED_AT = "2026-08-05T14:00:00Z"


def _digest(value: str) -> str:
    return "sha256:" + sha256(value.encode("utf-8")).hexdigest()


def _gap():
    result = determine_constitutional_gap_v1(
        implementation_request_identity="request-G70-03",
        implementation_responsibility="ASSESS_CONSTITUTIONAL_AMENDMENT_IMPACT",
        responsibility_owner="CONSTITUTIONAL_IMPACT_RESPONSIBILITY_OWNER",
        constitutional_baseline_identity=BASELINE,
        evidence_references=(),
        determined_at=ASSESSED_AT,
    )
    assert result.gap_artifact is not None
    return result.gap_artifact


def _proposal_reference(role, owner, identity, digest=None):
    return ConstitutionalAmendmentProposalEvidenceReferenceV1(
        evidence_role=role,
        producing_owner=owner,
        artifact_identity=identity,
        artifact_digest=digest or _digest(identity),
    )


def _proposal():
    gap = _gap()
    evidence = (
        _proposal_reference(
            GAP_DETERMINATION_EVIDENCE,
            gap.responsibility_owner,
            gap.gap_identity,
            gap.artifact_digest,
        ),
        _proposal_reference(
            PROPOSER_AUTHORITY_EVIDENCE,
            PROPOSER,
            "proposal-authority-G70-03",
        ),
        _proposal_reference(
            TARGET_CONSTITUTIONAL_ARTIFACT_EVIDENCE,
            TARGET_OWNER,
            TARGET_IDENTITY,
        ),
        _proposal_reference(
            CONSTITUTIONAL_BASELINE_EVIDENCE,
            CONSTITUTIONAL_GOVERNANCE_OWNER,
            BASELINE,
        ),
    )
    return create_constitutional_amendment_proposal_v1(
        constitutional_gap=gap,
        constitutional_baseline_digest=_digest(BASELINE),
        proposing_owner=PROPOSER,
        target_constitutional_owner=TARGET_OWNER,
        target_constitutional_layer="L1",
        target_constitutional_artifact_identity=TARGET_IDENTITY,
        target_constitutional_artifact_version=TARGET_VERSION,
        target_constitutional_artifact_digest=_digest(TARGET_IDENTITY),
        proposed_successor_version="V2-PROPOSED",
        proposal_title="Assess bounded Constitutional impact",
        normative_change_statement="Add an impact-assessment contract.",
        proposal_rationale="The open Gap has an owner-bound proposal.",
        evidence_references=evidence,
        proposed_at=ASSESSED_AT,
    )


def _contract(
    identity=TARGET_IDENTITY,
    version=TARGET_VERSION,
    owner=TARGET_OWNER,
    kind=SUCCESSOR_REQUIRED,
):
    return AffectedConstitutionalContractV1(
        contract_identity=identity,
        contract_version=version,
        contract_owner=owner,
        impact_kind=kind,
        evidence_producing_owner=owner,
        evidence_artifact_identity=identity,
        evidence_artifact_digest=_digest(identity),
    )


def _invariant(kind=INVARIANT_PRESERVED, identity="ONE_PRODUCTION_PATH"):
    return AffectedConstitutionalInvariantV1(
        invariant_identity=identity,
        invariant_owner="CONSTITUTIONAL_GOVERNANCE_OWNER",
        impact_kind=kind,
        evidence_producing_owner="CONSTITUTIONAL_GOVERNANCE_OWNER",
        evidence_artifact_identity=f"invariant-evidence-{identity}",
        evidence_artifact_digest=_digest(f"invariant-evidence-{identity}"),
    )


def _owner_impact(kind=OWNER_RESPONSIBILITY_UNCHANGED, owner=TARGET_OWNER):
    identity = f"owner-impact-{owner}-{kind}"
    return ConstitutionalOwnerImpactV1(
        owner_identity=owner,
        responsibility_identity="CONSTITUTIONAL_FLOW_OWNERSHIP",
        impact_kind=kind,
        evidence_producing_owner=CONSTITUTIONAL_GOVERNANCE_OWNER,
        evidence_artifact_identity=identity,
        evidence_artifact_digest=_digest(identity),
    )


def _impact_reference(role, owner, identity, digest=None):
    return ConstitutionalImpactEvidenceReferenceV1(
        evidence_role=role,
        producing_owner=owner,
        artifact_identity=identity,
        artifact_digest=digest or _digest(identity),
    )


def _evidence(proposal=None):
    proposal = proposal or _proposal()
    return (
        _impact_reference(
            PROPOSAL_BINDING_EVIDENCE,
            proposal.proposing_owner,
            proposal.proposal_identity,
            proposal.artifact_digest,
        ),
        _impact_reference(
            ASSESSOR_AUTHORITY_EVIDENCE,
            ASSESSOR,
            "impact-assessor-authority",
        ),
        _impact_reference(
            CONTRACT_IMPACT_COMPLETENESS_EVIDENCE,
            ASSESSOR,
            "contract-impact-completeness",
        ),
        _impact_reference(
            INVARIANT_IMPACT_COMPLETENESS_EVIDENCE,
            ASSESSOR,
            "invariant-impact-completeness",
        ),
        _impact_reference(
            REPLAY_IMPACT_EVIDENCE,
            OWNER_LOCAL_REPLAY_CUSTODIAN,
            "replay-impact-evidence",
        ),
        _impact_reference(
            CRO_IMPACT_EVIDENCE,
            PASSIVE_CONSTITUTIONAL_RUNTIME_OBSERVATORY,
            "cro-impact-evidence",
        ),
        _impact_reference(
            PRODUCTION_PATH_IMPACT_EVIDENCE,
            CONSTITUTIONAL_GOVERNANCE_OWNER,
            "production-path-impact-evidence",
        ),
        _impact_reference(
            OWNER_IMPACT_COMPLETENESS_EVIDENCE,
            CONSTITUTIONAL_GOVERNANCE_OWNER,
            "owner-impact-completeness",
        ),
    )


def _assess(**overrides):
    proposal = overrides.pop("amendment_proposal", None) or _proposal()
    values = {
        "amendment_proposal": proposal,
        "assessing_owner": ASSESSOR,
        "affected_contracts": (_contract(),),
        "affected_invariants": (_invariant(),),
        "replay_impact": REPLAY_UNCHANGED,
        "cro_impact": CRO_UNCHANGED,
        "production_path_impact": ONE_PRODUCTION_PATH_PRESERVED,
        "owner_impacts": (_owner_impact(),),
        "evidence_references": _evidence(proposal),
        "assessed_at": ASSESSED_AT,
    }
    values.update(overrides)
    return assess_constitutional_impact_v1(**values)


def test_bounded_assessment_is_immutable_versioned_and_not_ratified():
    assessment = _assess()

    assert assessment.contract_version == (
        CONSTITUTIONAL_IMPACT_ASSESSMENT_CONTRACT_VERSION
    )
    assert assessment.artifact_version == (
        CONSTITUTIONAL_IMPACT_ASSESSMENT_ARTIFACT_VERSION
    )
    assert assessment.assessment_status == IMPACT_ASSESSED_NOT_RATIFIED
    assert assessment.impact_classification == BOUNDED_CONSTITUTIONAL_IMPACT
    with pytest.raises(FrozenInstanceError):
        assessment.impact_classification = CROSS_CONSTITUTIONAL_IMPACT


def test_assessment_identity_is_content_deterministic():
    first = _assess()
    second = _assess()

    assert first == second
    assert first.assessment_identity == second.assessment_identity
    assert first.artifact_digest == second.artifact_digest
    assert first.assessment_identity.startswith("CONSTITUTIONAL-IMPACT-ASSESSMENT-")


@pytest.mark.parametrize(
    "overrides",
    (
        {
            "affected_contracts": (
                _contract(),
                _contract(
                    identity="GOVERNANCE_LINEAGE_MODEL",
                    version="V1",
                    owner="GOVERNANCE_LINEAGE_OWNER",
                    kind=DEPENDENCY_IMPACT,
                ),
            )
        },
        {"affected_invariants": (_invariant(INVARIANT_MODIFICATION_PROPOSED),)},
        {"replay_impact": REPLAY_CORRELATION_EXTENSION_REQUIRED},
        {"cro_impact": CRO_OBSERVATION_EXTENSION_REQUIRED},
        {"owner_impacts": (_owner_impact(OWNER_RESPONSIBILITY_CHANGE_PROPOSED),)},
        {"owner_impacts": (_owner_impact(NEW_OWNER_PROPOSED),)},
    ),
)
def test_cross_constitutional_impacts_are_classified_deterministically(overrides):
    assert _assess(**overrides).impact_classification == CROSS_CONSTITUTIONAL_IMPACT


@pytest.mark.parametrize(
    "overrides",
    (
        {
            "affected_contracts": (
                _contract(),
                _contract(
                    identity="CONFLICTING_CONTRACT",
                    version="V1",
                    owner="CONFLICTING_OWNER",
                    kind=CONTRACT_CONFLICT,
                ),
            )
        },
        {"affected_invariants": (_invariant(INVARIANT_CONFLICT),)},
        {"replay_impact": REPLAY_SAFETY_DEGRADATION_PROPOSED},
        {"cro_impact": CRO_AUTHORITY_EXPANSION_PROPOSED},
        {"production_path_impact": PRODUCTION_PATH_CHANGE_PROPOSED},
        {"owner_impacts": (_owner_impact(UNBOUNDED_OWNER_AUTHORITY_PROPOSED),)},
    ),
)
def test_boundary_impacts_are_classified_without_changing_runtime(overrides):
    assessment = _assess(**overrides)
    assert assessment.impact_classification == CONSTITUTIONAL_BOUNDARY_IMPACT
    assert assessment.production_path_count == 1
    assert assessment.production_behavior_changed is False


@pytest.mark.parametrize(
    "overrides",
    (
        {
            "affected_contracts": (
                _contract(),
                _contract(
                    identity="UNRESOLVED_CONTRACT",
                    version="V1",
                    owner="UNRESOLVED_OWNER",
                    kind=CONTRACT_IMPACT_UNRESOLVED,
                ),
            )
        },
        {"affected_invariants": (_invariant(INVARIANT_IMPACT_UNRESOLVED),)},
        {"replay_impact": REPLAY_IMPACT_UNRESOLVED},
        {"cro_impact": CRO_IMPACT_UNRESOLVED},
        {"production_path_impact": PRODUCTION_PATH_IMPACT_UNRESOLVED},
        {"owner_impacts": (_owner_impact(OWNER_IMPACT_UNRESOLVED),)},
    ),
)
def test_unresolved_impacts_take_fail_closed_classification_precedence(overrides):
    values = dict(overrides)
    values.setdefault("production_path_impact", PRODUCTION_PATH_CHANGE_PROPOSED)
    assessment = _assess(**values)
    assert assessment.impact_classification == UNRESOLVED_CONSTITUTIONAL_IMPACT


def test_target_contract_is_mandatory_and_exactly_proposal_bound():
    with pytest.raises(FailClosedRuntimeError, match="target contract is absent"):
        _assess(
            affected_contracts=(
                _contract(identity="OTHER_CONTRACT", owner="OTHER_OWNER"),
            )
        )
    with pytest.raises(FailClosedRuntimeError, match="binding is invalid"):
        _assess(affected_contracts=(_contract(version="WRONG_VERSION"),))
    with pytest.raises(FailClosedRuntimeError, match="binding is invalid"):
        _assess(affected_contracts=(_contract(kind=DEPENDENCY_IMPACT),))


def test_affected_records_are_canonical_and_duplicate_safe():
    second = _contract(
        identity="A_DEPENDENCY",
        version="V1",
        owner="DEPENDENCY_OWNER",
        kind=DEPENDENCY_IMPACT,
    )
    assessment = _assess(affected_contracts=(_contract(), second))
    assert tuple(item.contract_identity for item in assessment.affected_contracts) == (
        "A_DEPENDENCY",
        TARGET_IDENTITY,
    )

    with pytest.raises(FailClosedRuntimeError, match="duplicated"):
        _assess(affected_contracts=(_contract(), _contract()))
    with pytest.raises(FailClosedRuntimeError, match="duplicated"):
        _assess(affected_invariants=(_invariant(), _invariant()))
    with pytest.raises(FailClosedRuntimeError, match="duplicated"):
        _assess(owner_impacts=(_owner_impact(), _owner_impact()))


def test_public_record_validators_accept_exact_mappings():
    contract = _contract()
    invariant = _invariant()
    owner = _owner_impact()

    assert validate_affected_constitutional_contract_v1(contract.to_dict()) == contract
    assert validate_affected_constitutional_invariant_v1(invariant.to_dict()) == invariant
    assert validate_constitutional_owner_impact_v1(owner.to_dict()) == owner

    with pytest.raises(FailClosedRuntimeError, match="evidence owner is invalid"):
        validate_affected_constitutional_contract_v1(
            replace(contract, evidence_producing_owner="WRONG_OWNER")
        )
    with pytest.raises(FailClosedRuntimeError, match="evidence owner is invalid"):
        validate_affected_constitutional_invariant_v1(
            replace(invariant, evidence_producing_owner="WRONG_OWNER")
        )
    with pytest.raises(FailClosedRuntimeError, match="evidence owner is invalid"):
        validate_constitutional_owner_impact_v1(
            replace(owner, evidence_producing_owner="WRONG_OWNER")
        )


def test_public_evidence_validator_enforces_exact_role_owner_and_proposal():
    proposal = _proposal()
    evidence = _evidence(proposal)[0]

    assert (
        validate_constitutional_impact_evidence_reference_v1(
            value=evidence.to_dict(),
            expected_role=PROPOSAL_BINDING_EVIDENCE,
            expected_owner=proposal.proposing_owner,
            expected_artifact_identity=proposal.proposal_identity,
            expected_artifact_digest=proposal.artifact_digest,
        )
        == evidence
    )
    with pytest.raises(FailClosedRuntimeError, match="role or owner"):
        validate_constitutional_impact_evidence_reference_v1(
            value=replace(evidence, producing_owner="WRONG_OWNER"),
            expected_role=PROPOSAL_BINDING_EVIDENCE,
            expected_owner=proposal.proposing_owner,
        )


def test_incomplete_reordered_or_misbound_assessment_evidence_fails_closed():
    proposal = _proposal()
    evidence = _evidence(proposal)
    with pytest.raises(FailClosedRuntimeError, match="incomplete"):
        _assess(amendment_proposal=proposal, evidence_references=evidence[:-1])
    with pytest.raises(FailClosedRuntimeError, match="order is not canonical"):
        _assess(
            amendment_proposal=proposal,
            evidence_references=tuple(reversed(evidence)),
        )
    with pytest.raises(FailClosedRuntimeError, match="identity is invalid"):
        _assess(
            amendment_proposal=proposal,
            evidence_references=(
                replace(evidence[0], artifact_identity="WRONG_PROPOSAL"),
                *evidence[1:],
            ),
        )


def test_public_artifact_validator_round_trips_and_rejects_tampering():
    assessment = _assess()

    assert (
        validate_constitutional_impact_assessment_artifact_v1(
            assessment.to_dict()
        )
        == assessment
    )
    with pytest.raises(FailClosedRuntimeError, match="classification is invalid"):
        validate_constitutional_impact_assessment_artifact_v1(
            replace(
                assessment,
                impact_classification=CONSTITUTIONAL_BOUNDARY_IMPACT,
            )
        )
    with pytest.raises(FailClosedRuntimeError, match="identity is invalid"):
        validate_constitutional_impact_assessment_artifact_v1(
            replace(assessment, assessed_at="2026-08-05T15:00:00Z")
        )


def test_assessment_preserves_single_topology_and_has_no_later_authority():
    assessment = _assess()

    assert (
        assessment.che_definition_count,
        assessment.production_hic_family_count,
        assessment.production_owner_chain_count,
        assessment.production_path_count,
        assessment.parallel_production_path_count,
    ) == (1, 1, 1, 1, 0)
    assert assessment.human_ratification_performed is False
    assert assessment.amendment_certification_performed is False
    assert assessment.amendment_activation_performed is False
    assert assessment.runtime_mutation_performed is False
    assert assessment.production_behavior_changed is False
    assert assessment.replay_path_created is False
    assert assessment.cro_authority_created is False

    with pytest.raises(FailClosedRuntimeError, match="boundary invariants"):
        validate_constitutional_impact_assessment_artifact_v1(
            replace(assessment, human_ratification_performed=True)
        )


def test_contract_has_no_persistence_ratification_certification_or_activation_calls():
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }

    assert imported_modules == {
        "__future__",
        "dataclasses",
        "hashlib",
        "typing",
        "aigol.runtime.constitutional_amendment_proposal_contract_v1",
        "aigol.runtime.models",
        "aigol.runtime.transport.serialization",
    }
    assert called_names.isdisjoint(
        {
            "open",
            "write_json_immutable",
            "ratify_amendment",
            "certify_amendment",
            "activate_amendment",
            "run_human_interface_runtime_entry",
        }
    )
    source = MODULE.read_text(encoding="utf-8").lower()
    assert "historical implementations" not in source
