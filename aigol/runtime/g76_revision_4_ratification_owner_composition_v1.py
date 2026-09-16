"""G76 Revision 4 composition into the existing G70/CHE contracts.

This module is deliberately a binding owner, not a new authority or artifact
family.  It authenticates fixed repository evidence, materializes it through
the existing G70-01/02/03 constructors, presents the validated assessment
through the sole CHE implementation, and exposes (without invoking) the
future G70-04 Human-act consumption boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from aigol.runtime.canonical_human_authority_act_contract_v1 import (
    APPROVAL,
    HUMAN_AUTHORITY_OWNER,
    CanonicalHumanAuthorityActV1,
    bind_canonical_human_authority_act_to_che_v1,
    canonical_human_authority_act_from_request_v1,
)
from aigol.runtime.canonical_human_entry_contract_v1 import (
    ACTIVE_CONTINUATION,
    HUMAN_ACTOR,
    CanonicalContinuationEnvelopeV1,
    CanonicalHumanEntryRequestEnvelopeV1,
    canonical_che_request_source_act_digest_v1,
    validate_canonical_che_continuation_envelope_v1,
    validate_canonical_che_request_envelope_v1,
)
from aigol.runtime.constitutional_amendment_proposal_contract_v1 import (
    CONSTITUTIONAL_BASELINE_EVIDENCE,
    GAP_DETERMINATION_EVIDENCE,
    PREVIOUS_PROPOSAL_EVIDENCE,
    PROPOSER_AUTHORITY_EVIDENCE,
    TARGET_CONSTITUTIONAL_ARTIFACT_EVIDENCE,
    ConstitutionalAmendmentProposalArtifactV1,
    ConstitutionalAmendmentProposalEvidenceReferenceV1,
    create_constitutional_amendment_proposal_v1,
    validate_constitutional_amendment_proposal_artifact_v1,
)
from aigol.runtime.constitutional_gap_determination_evidence_contract_v1 import (
    determine_constitutional_gap_v1,
)
from aigol.runtime.constitutional_human_ratification_contract_v1 import (
    CANONICAL_HUMAN_ENTRY_OWNER,
    CHE_CONTINUATION_EVIDENCE,
    CHE_REQUEST_EVIDENCE,
    CONSTITUTIONAL_AMENDMENT_RATIFICATION_SCOPE,
    CONSTITUTIONAL_GOVERNANCE_OWNER,
    HUMAN_AUTHORITY_ACT_EVIDENCE,
    IMPACT_ASSESSMENT_EVIDENCE,
    ConstitutionalHumanRatificationArtifactV1,
    ConstitutionalHumanRatificationEvidenceReferenceV1,
    constitutional_ratification_payload_v1,
    create_constitutional_human_ratification_v1,
    validate_constitutional_human_ratification_artifact_v1,
)
from aigol.runtime.constitutional_impact_assessment_contract_v1 import (
    ASSESSOR_AUTHORITY_EVIDENCE,
    CONTRACT_IMPACT_COMPLETENESS_EVIDENCE,
    CRO_IMPACT_EVIDENCE,
    CRO_OBSERVATION_EXTENSION_REQUIRED,
    DEPENDENCY_IMPACT,
    INVARIANT_IMPACT_COMPLETENESS_EVIDENCE,
    INVARIANT_PRESERVED,
    ONE_PRODUCTION_PATH_PRESERVED,
    OWNER_IMPACT_COMPLETENESS_EVIDENCE,
    OWNER_LOCAL_REPLAY_CUSTODIAN,
    OWNER_RESPONSIBILITY_CHANGE_PROPOSED,
    OWNER_RESPONSIBILITY_UNCHANGED,
    PASSIVE_CONSTITUTIONAL_RUNTIME_OBSERVATORY,
    PRODUCTION_PATH_IMPACT_EVIDENCE,
    PROPOSAL_BINDING_EVIDENCE,
    REPLAY_CORRELATION_EXTENSION_REQUIRED,
    REPLAY_IMPACT_EVIDENCE,
    SUCCESSOR_REQUIRED,
    AffectedConstitutionalContractV1,
    AffectedConstitutionalInvariantV1,
    ConstitutionalImpactAssessmentArtifactV1,
    ConstitutionalImpactEvidenceReferenceV1,
    ConstitutionalOwnerImpactV1,
    assess_constitutional_impact_v1,
    validate_constitutional_impact_assessment_artifact_v1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


G76_REVISION_4_OWNER_COMPOSITION_VERSION = (
    "G76_REVISION_4_G70_RATIFICATION_OWNER_COMPOSITION_V1"
)
G76_REVISION_4_PRESENTATION_COMMAND = (
    "PRESENT_G76_REVISION_4_CONSTITUTIONAL_RATIFICATION_BOUNDARY"
)
G76_REVISION_4_RATIFICATION_OWNER_STATUS = (
    "G76_REVISION_4_RATIFICATION_HUMAN_DECISION_REQUIRED"
)
G76_REVISION_4_RATIFICATION_RECORDED_STATUS = (
    "G76_REVISION_4_HUMAN_RATIFICATION_RECORDED_NOT_CERTIFIED"
)
G76_REVISION_4_OWNER_STATE_PREFIX = "G70-04-G76-R4-OWNER-STATE-"

_G76_07_PATH = Path(
    "docs/governance/"
    "G76_07_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_4_"
    "RELEASE_DECISION_ARTIFACT_V1.md"
)
_G76_08_PATH = Path(
    "docs/governance/"
    "G76_08_CONSTITUTIONAL_IMPACT_ASSESSMENT_RELEASE_DECISION_"
    "ARTIFACT_REVISION_4_V1.md"
)
_G76_09_PATH = Path(
    "docs/governance/"
    "G76_09_CONSTITUTIONAL_HUMAN_RATIFICATION_RELEASE_DECISION_"
    "ARTIFACT_REVISION_4_V1.md"
)
_G76_04_PATH = Path(
    "docs/governance/"
    "G76_04_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_3_"
    "RELEASE_DECISION_ARTIFACT_V1.md"
)
_G76_06_PATH = Path(
    "docs/governance/"
    "G76_06_CONSTITUTIONAL_ARTIFACT_IDENTITY_MODEL_"
    "RECONSTRUCTION_REPORT_V1.md"
)
_G72_00_PATH = Path(
    "docs/governance/"
    "G72_00_CONSTITUTIONAL_CORE_CLOSURE_AND_OPERATIONAL_"
    "READINESS_CERTIFICATION_REPORT_V1.md"
)
_G69_19_PATH = Path(
    "docs/governance/"
    "G69_19_CONSTITUTIONAL_PRODUCTION_CUTOVER_CERTIFICATION_REPORT_V1.md"
)

_EXPECTED_DIGESTS = {
    _G76_07_PATH: "c1149c62dea32ffc6b2bb7a3b417cb2079e4cae4905b3a194dcb7c1d127d2532",
    _G76_08_PATH: "23ca77ed1dfb021a5fdab9e335642899170f252a700ab426efb01d3b52141a45",
    _G76_09_PATH: "9c76ab4834a9c3c74a1f6909af75f70a991ee02b42df4a1085dbb10e2fa9ff26",
    _G76_04_PATH: "c62f1ecf1ba7985de6613bf44cb00d49384a0e3801f5a0a74ed912fac3a1f648",
    _G76_06_PATH: "29f06a93d5b7ce610c161487bc1e3a01f6d7d063b22393e0347b0da20b281dbc",
    _G72_00_PATH: "80e57a914761982cdbdeb6899e45de5e29d5066bc069c93e7a3e8c942da8cd59",
    _G69_19_PATH: "afde74400a07bb337eadf57fd6304e5c958ac4daccfb28436f16b4dac398c26e",
}

_G76_07_IDENTITY = (
    "G76_07_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_4_RELEASE_DECISION_ARTIFACT_V1"
)
_G76_08_IDENTITY = (
    "G76_08_CONSTITUTIONAL_IMPACT_ASSESSMENT_RELEASE_DECISION_ARTIFACT_REVISION_4_V1"
)
_G76_04_IDENTITY = (
    "G76_04_CONSTITUTIONAL_AMENDMENT_PROPOSAL_REVISION_3_RELEASE_DECISION_ARTIFACT_V1"
)
_G76_06_IDENTITY = (
    "G76_06_CONSTITUTIONAL_ARTIFACT_IDENTITY_MODEL_RECONSTRUCTION_REPORT_V1"
)
_TARGET_IDENTITY = "AI_GOL_CONSTITUTIONAL_CORE_BASELINE_V1_ESTABLISHED"
_TARGET_VERSION = "V1"
_SUCCESSOR_VERSION = "V1.1-RELEASE-DECISION-ARTIFACT-R4"
_G69_19_IDENTITY = "G69_19_CONSTITUTIONAL_PRODUCTION_CUTOVER_CERTIFICATION_REPORT_V1"
_ASSESSOR = CONSTITUTIONAL_GOVERNANCE_OWNER
_RELEASE_OWNER = "RELEASE_CUTOVER_PRODUCTION_STATUS_OWNER"
_EXPECTED_MACHINE_PROPOSAL_IDENTITY = (
    "CONSTITUTIONAL-AMENDMENT-PROPOSAL-"
    "b6821f60f69b234d904cfb4bb1093f5ff0dffbecf4152206acce5b88296c799c"
)
_EXPECTED_MACHINE_PROPOSAL_DIGEST = (
    "sha256:b6821f60f69b234d904cfb4bb1093f5ff0dffbecf4152206acce5b88296c799c"
)
_EXPECTED_MACHINE_ASSESSMENT_IDENTITY = (
    "CONSTITUTIONAL-IMPACT-ASSESSMENT-"
    "1a8f9c018cf1e36491e125f081f47d1fc213ce52f075581eedcf68e58c219981"
)
_EXPECTED_MACHINE_ASSESSMENT_DIGEST = (
    "sha256:1a8f9c018cf1e36491e125f081f47d1fc213ce52f075581eedcf68e58c219981"
)


@dataclass(frozen=True, slots=True)
class G76Revision4RatificationPackageV1:
    """Validated machine G70-02/G70-03 package bound to source bytes."""

    contract_version: str
    source_digests: Mapping[str, str]
    amendment_proposal: ConstitutionalAmendmentProposalArtifactV1
    impact_assessment: ConstitutionalImpactAssessmentArtifactV1


def _sha256_bytes(value: bytes) -> str:
    return sha256(value).hexdigest()


def _sha256_reference(value: Any) -> str:
    return "sha256:" + sha256(
        canonical_serialize(value).encode("utf-8")
    ).hexdigest()


def _authenticate_sources(repository_root: str | Path) -> dict[str, str]:
    root = Path(repository_root).resolve()
    authenticated: dict[str, str] = {}
    contents: dict[Path, str] = {}
    for relative, expected in _EXPECTED_DIGESTS.items():
        path = root / relative
        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise FailClosedRuntimeError(
                f"G76 Revision 4 source evidence is unavailable: {relative}"
            ) from exc
        actual = _sha256_bytes(raw)
        if actual != expected:
            raise FailClosedRuntimeError(
                f"G76 Revision 4 source digest mismatch: {relative}"
            )
        authenticated[str(relative)] = "sha256:" + actual
        contents[relative] = raw.decode("utf-8")

    required_facts = {
        _G76_07_PATH: (
            "Proposal revision: 4",
            "Proposal status: `PROPOSAL_ONLY_UNASSESSED`",
            _G76_04_IDENTITY,
            _SUCCESSOR_VERSION,
        ),
        _G76_08_PATH: (
            "Impact classification: `CROSS_CONSTITUTIONAL_IMPACT`",
            "G70-03 impact resolution:            COMPLETE",
            _G76_07_IDENTITY,
        ),
        _G76_09_PATH: (
            "Human Ratification",
            "Authenticated G76-08 SHA-256",
        ),
    }
    for relative, facts in required_facts.items():
        text = contents[relative]
        if any(fact not in text for fact in facts):
            raise FailClosedRuntimeError(
                f"G76 Revision 4 required source fact is absent: {relative}"
            )
    return authenticated


def _proposal_reference(
    role: str, owner: str, identity: str, digest: str
) -> ConstitutionalAmendmentProposalEvidenceReferenceV1:
    return ConstitutionalAmendmentProposalEvidenceReferenceV1(
        evidence_role=role,
        producing_owner=owner,
        artifact_identity=identity,
        artifact_digest=digest,
    )


def _impact_reference(
    role: str, owner: str, source_identity: str, source_digest: str
) -> ConstitutionalImpactEvidenceReferenceV1:
    return ConstitutionalImpactEvidenceReferenceV1(
        evidence_role=role,
        producing_owner=owner,
        artifact_identity=f"{source_identity}#{role}",
        artifact_digest=source_digest,
    )


def materialize_g76_revision_4_ratification_package_v1(
    repository_root: str | Path,
) -> G76Revision4RatificationPackageV1:
    """Materialize authenticated G76 evidence through unchanged G70 validators."""

    sources = _authenticate_sources(repository_root)
    baseline_digest = sources[str(_G76_06_PATH)]
    target_digest = sources[str(_G72_00_PATH)]
    proposal_source_digest = sources[str(_G76_07_PATH)]
    assessment_source_digest = sources[str(_G76_08_PATH)]

    gap_result = determine_constitutional_gap_v1(
        implementation_request_identity=(
            "AIGOL_GOVERNED_READINESS_STEP_7_G76_REVISION_4_"
            "CURRENT_MATERIALIZATION_REQUEST_V1"
        ),
        implementation_responsibility=(
            "DEFINE_RELEASE_DECISION_ARTIFACT_REVISION_4_CONSTITUTIONAL_SUCCESSOR"
        ),
        responsibility_owner=CONSTITUTIONAL_GOVERNANCE_OWNER,
        constitutional_baseline_identity=_G76_06_IDENTITY,
        evidence_references=(),
        determined_at="2026-09-16",
    )
    gap = gap_result.gap_artifact
    if gap is None:
        raise FailClosedRuntimeError(
            "G76 Revision 4 materialization requires the authenticated open Gap"
        )

    proposal_evidence = (
        _proposal_reference(
            GAP_DETERMINATION_EVIDENCE,
            gap.responsibility_owner,
            gap.gap_identity,
            gap.artifact_digest,
        ),
        _proposal_reference(
            PROPOSER_AUTHORITY_EVIDENCE,
            CONSTITUTIONAL_GOVERNANCE_OWNER,
            _G76_07_IDENTITY,
            proposal_source_digest,
        ),
        _proposal_reference(
            TARGET_CONSTITUTIONAL_ARTIFACT_EVIDENCE,
            CONSTITUTIONAL_GOVERNANCE_OWNER,
            _TARGET_IDENTITY,
            target_digest,
        ),
        _proposal_reference(
            CONSTITUTIONAL_BASELINE_EVIDENCE,
            CONSTITUTIONAL_GOVERNANCE_OWNER,
            _G76_06_IDENTITY,
            baseline_digest,
        ),
        _proposal_reference(
            PREVIOUS_PROPOSAL_EVIDENCE,
            CONSTITUTIONAL_GOVERNANCE_OWNER,
            _G76_04_IDENTITY,
            sources[str(_G76_04_PATH)],
        ),
    )
    proposal = create_constitutional_amendment_proposal_v1(
        constitutional_gap=gap,
        constitutional_baseline_digest=baseline_digest,
        proposing_owner=CONSTITUTIONAL_GOVERNANCE_OWNER,
        target_constitutional_owner=CONSTITUTIONAL_GOVERNANCE_OWNER,
        target_constitutional_layer="L1",
        target_constitutional_artifact_identity=_TARGET_IDENTITY,
        target_constitutional_artifact_version=_TARGET_VERSION,
        target_constitutional_artifact_digest=target_digest,
        proposed_successor_version=_SUCCESSOR_VERSION,
        proposal_title="Release Decision Artifact Revision 4",
        normative_change_statement=(
            "Add the Revision 4 Release Decision Artifact successor with the "
            "authenticated forward-only identity dependency model."
        ),
        proposal_rationale=(
            "G75-02 requires CAP and G76-07 resolves the remaining Revision 3 "
            "identity-model impacts without changing Human authority or topology."
        ),
        evidence_references=proposal_evidence,
        proposed_at="2026-08-06",
        proposal_revision=4,
        previous_proposal_identity=_G76_04_IDENTITY,
        previous_proposal_digest=sources[str(_G76_04_PATH)],
    )
    proposal = validate_constitutional_amendment_proposal_artifact_v1(proposal)

    affected_contracts = (
        AffectedConstitutionalContractV1(
            contract_identity=_TARGET_IDENTITY,
            contract_version=_TARGET_VERSION,
            contract_owner=CONSTITUTIONAL_GOVERNANCE_OWNER,
            impact_kind=SUCCESSOR_REQUIRED,
            evidence_producing_owner=CONSTITUTIONAL_GOVERNANCE_OWNER,
            evidence_artifact_identity=_TARGET_IDENTITY,
            evidence_artifact_digest=target_digest,
        ),
        AffectedConstitutionalContractV1(
            contract_identity=_G69_19_IDENTITY,
            contract_version="V1",
            contract_owner=_RELEASE_OWNER,
            impact_kind=DEPENDENCY_IMPACT,
            evidence_producing_owner=_RELEASE_OWNER,
            evidence_artifact_identity=_G69_19_IDENTITY,
            evidence_artifact_digest=sources[str(_G69_19_PATH)],
        ),
    )
    affected_invariants = (
        AffectedConstitutionalInvariantV1(
            invariant_identity="CONSTITUTIONAL_ARTIFACT_IDENTITY_DAG",
            invariant_owner=CONSTITUTIONAL_GOVERNANCE_OWNER,
            impact_kind=INVARIANT_PRESERVED,
            evidence_producing_owner=CONSTITUTIONAL_GOVERNANCE_OWNER,
            evidence_artifact_identity=_G76_06_IDENTITY,
            evidence_artifact_digest=baseline_digest,
        ),
        AffectedConstitutionalInvariantV1(
            invariant_identity="ONE_PRODUCTION_PATH",
            invariant_owner=CONSTITUTIONAL_GOVERNANCE_OWNER,
            impact_kind=INVARIANT_PRESERVED,
            evidence_producing_owner=CONSTITUTIONAL_GOVERNANCE_OWNER,
            evidence_artifact_identity=f"{_G76_08_IDENTITY}#ONE_PRODUCTION_PATH",
            evidence_artifact_digest=assessment_source_digest,
        ),
    )
    owner_impacts = (
        ConstitutionalOwnerImpactV1(
            owner_identity=HUMAN_AUTHORITY_OWNER,
            responsibility_identity="CONSTITUTIONAL_HUMAN_RATIFICATION",
            impact_kind=OWNER_RESPONSIBILITY_UNCHANGED,
            evidence_producing_owner=CONSTITUTIONAL_GOVERNANCE_OWNER,
            evidence_artifact_identity=f"{_G76_08_IDENTITY}#HUMAN_AUTHORITY",
            evidence_artifact_digest=assessment_source_digest,
        ),
        ConstitutionalOwnerImpactV1(
            owner_identity=_RELEASE_OWNER,
            responsibility_identity="RELEASE_DECISION_LIFECYCLE_CUSTODY",
            impact_kind=OWNER_RESPONSIBILITY_CHANGE_PROPOSED,
            evidence_producing_owner=CONSTITUTIONAL_GOVERNANCE_OWNER,
            evidence_artifact_identity=f"{_G76_08_IDENTITY}#RELEASE_OWNER",
            evidence_artifact_digest=assessment_source_digest,
        ),
    )
    assessment_evidence = (
        ConstitutionalImpactEvidenceReferenceV1(
            evidence_role=PROPOSAL_BINDING_EVIDENCE,
            producing_owner=proposal.proposing_owner,
            artifact_identity=proposal.proposal_identity,
            artifact_digest=proposal.artifact_digest,
        ),
        _impact_reference(
            ASSESSOR_AUTHORITY_EVIDENCE,
            _ASSESSOR,
            _G76_08_IDENTITY,
            assessment_source_digest,
        ),
        _impact_reference(
            CONTRACT_IMPACT_COMPLETENESS_EVIDENCE,
            _ASSESSOR,
            _G76_08_IDENTITY,
            assessment_source_digest,
        ),
        _impact_reference(
            INVARIANT_IMPACT_COMPLETENESS_EVIDENCE,
            _ASSESSOR,
            _G76_08_IDENTITY,
            assessment_source_digest,
        ),
        _impact_reference(
            REPLAY_IMPACT_EVIDENCE,
            OWNER_LOCAL_REPLAY_CUSTODIAN,
            _G76_08_IDENTITY,
            assessment_source_digest,
        ),
        _impact_reference(
            CRO_IMPACT_EVIDENCE,
            PASSIVE_CONSTITUTIONAL_RUNTIME_OBSERVATORY,
            _G76_08_IDENTITY,
            assessment_source_digest,
        ),
        _impact_reference(
            PRODUCTION_PATH_IMPACT_EVIDENCE,
            CONSTITUTIONAL_GOVERNANCE_OWNER,
            _G76_08_IDENTITY,
            assessment_source_digest,
        ),
        _impact_reference(
            OWNER_IMPACT_COMPLETENESS_EVIDENCE,
            CONSTITUTIONAL_GOVERNANCE_OWNER,
            _G76_08_IDENTITY,
            assessment_source_digest,
        ),
    )
    assessment = assess_constitutional_impact_v1(
        amendment_proposal=proposal,
        assessing_owner=_ASSESSOR,
        affected_contracts=affected_contracts,
        affected_invariants=affected_invariants,
        replay_impact=REPLAY_CORRELATION_EXTENSION_REQUIRED,
        cro_impact=CRO_OBSERVATION_EXTENSION_REQUIRED,
        production_path_impact=ONE_PRODUCTION_PATH_PRESERVED,
        owner_impacts=owner_impacts,
        evidence_references=assessment_evidence,
        assessed_at="2026-08-06",
    )
    assessment = validate_constitutional_impact_assessment_artifact_v1(assessment)
    return G76Revision4RatificationPackageV1(
        contract_version=G76_REVISION_4_OWNER_COMPOSITION_VERSION,
        source_digests=MappingProxyType(dict(sorted(sources.items()))),
        amendment_proposal=proposal,
        impact_assessment=assessment,
    )


def validate_g76_revision_4_ratification_package_v1(
    package: G76Revision4RatificationPackageV1,
) -> G76Revision4RatificationPackageV1:
    if not isinstance(package, G76Revision4RatificationPackageV1):
        raise FailClosedRuntimeError("G76 Revision 4 package is malformed")
    if package.contract_version != G76_REVISION_4_OWNER_COMPOSITION_VERSION:
        raise FailClosedRuntimeError("G76 Revision 4 package version is invalid")
    proposal = validate_constitutional_amendment_proposal_artifact_v1(
        package.amendment_proposal
    )
    assessment = validate_constitutional_impact_assessment_artifact_v1(
        package.impact_assessment
    )
    if assessment.amendment_proposal != proposal or proposal.proposal_revision != 4:
        raise FailClosedRuntimeError("G76 Revision 4 package lineage is invalid")
    identities = (
        proposal.proposal_identity,
        proposal.artifact_digest,
        assessment.assessment_identity,
        assessment.artifact_digest,
    )
    if identities != (
        _EXPECTED_MACHINE_PROPOSAL_IDENTITY,
        _EXPECTED_MACHINE_PROPOSAL_DIGEST,
        _EXPECTED_MACHINE_ASSESSMENT_IDENTITY,
        _EXPECTED_MACHINE_ASSESSMENT_DIGEST,
    ):
        raise FailClosedRuntimeError(
            "G76 Revision 4 package machine identity is invalid"
        )
    expected_sources = {
        str(path): "sha256:" + digest for path, digest in _EXPECTED_DIGESTS.items()
    }
    if dict(package.source_digests) != dict(sorted(expected_sources.items())):
        raise FailClosedRuntimeError("G76 Revision 4 package source binding is invalid")
    return package


def constitutional_ratification_owner_state_identity_v1(
    assessment_identity: str, proposal_revision: int
) -> str:
    digest = replay_hash(
        {
            "owner": CONSTITUTIONAL_GOVERNANCE_OWNER,
            "scope": CONSTITUTIONAL_AMENDMENT_RATIFICATION_SCOPE,
            "assessment_identity": assessment_identity,
            "proposal_revision": proposal_revision,
        }
    ).removeprefix("sha256:")
    return G76_REVISION_4_OWNER_STATE_PREFIX + digest


def constitutional_ratification_owner_result_v1(
    package: G76Revision4RatificationPackageV1,
) -> dict[str, Any]:
    validated = validate_g76_revision_4_ratification_package_v1(package)
    assessment = validated.impact_assessment
    revision = assessment.amendment_proposal.proposal_revision
    state_identity = constitutional_ratification_owner_state_identity_v1(
        assessment.assessment_identity, revision
    )
    return {
        "constitutional_ratification_owner_presentation": {
            "contract_version": G76_REVISION_4_OWNER_COMPOSITION_VERSION,
            "owner_status": G76_REVISION_4_RATIFICATION_OWNER_STATUS,
            "producing_owner": CONSTITUTIONAL_GOVERNANCE_OWNER,
            "conversation_identity": state_identity,
            "owner_state_identity": state_identity,
            "proposal_revision": revision,
            "proposal_identity": assessment.amendment_proposal.proposal_identity,
            "proposal_digest": assessment.amendment_proposal.artifact_digest,
            "assessment_identity": assessment.assessment_identity,
            "assessment_digest": assessment.artifact_digest,
            "assessment_classification": assessment.impact_classification,
            "authority_kind": APPROVAL,
            "authority_scope": CONSTITUTIONAL_AMENDMENT_RATIFICATION_SCOPE,
            "ratification_payload": constitutional_ratification_payload_v1(
                assessment
            ),
            "source_digests": dict(validated.source_digests),
        },
        "human_visible_completion_result": (
            "G76 Revision 4 Proposal and Impact Assessment are validated. "
            "An authenticated Human APPROVAL is required through the active "
            "CHE continuation; no Human decision has been issued or consumed."
        ),
    }


def present_g76_revision_4_ratification_boundary_v1(
    *,
    package: G76Revision4RatificationPackageV1,
    request: CanonicalHumanEntryRequestEnvelopeV1 | dict[str, Any],
):
    """Use the sole CHE to issue the owner presentation and active Continuation."""

    canonical_request = validate_canonical_che_request_envelope_v1(request)
    if canonical_request.actor_class != HUMAN_ACTOR:
        raise FailClosedRuntimeError(
            "G76 Revision 4 owner presentation requires a Human actor"
        )
    if (
        canonical_request.source_modality != "TEXT"
        or canonical_request.to_dict()["source_payload"]
        != G76_REVISION_4_PRESENTATION_COMMAND
    ):
        raise FailClosedRuntimeError(
            "G76 Revision 4 owner presentation command is invalid"
        )
    validated = validate_g76_revision_4_ratification_package_v1(package)
    from aigol.runtime.human_interface_runtime_entry_service import (
        _execute_canonical_che_request_v1,
    )

    return _execute_canonical_che_request_v1(
        canonical_request,
        lambda _request: constitutional_ratification_owner_result_v1(validated),
        bind_continuation=True,
    )


def validate_constitutional_ratification_che_owner_binding_v1(
    request: CanonicalHumanEntryRequestEnvelopeV1,
    continuation: CanonicalContinuationEnvelopeV1,
    act: CanonicalHumanAuthorityActV1,
) -> CanonicalHumanAuthorityActV1:
    """Validate the exact owner-issued G70-04 binding without Human inference."""

    request = validate_canonical_che_request_envelope_v1(request)
    continuation = validate_canonical_che_continuation_envelope_v1(continuation)
    expected_state = constitutional_ratification_owner_state_identity_v1(
        continuation.expected_next_act_identity,
        continuation.expected_owner_revision,
    )
    if (
        continuation.continuation_state != ACTIVE_CONTINUATION
        or continuation.conversation_identity != expected_state
        or continuation.expected_owner_state_identity != expected_state
    ):
        raise FailClosedRuntimeError(
            "constitutional ratification CHE owner state is invalid"
        )
    return bind_canonical_human_authority_act_to_che_v1(
        act,
        request,
        continuation,
        expected_authority_kind=APPROVAL,
        expected_target_identity=continuation.expected_next_act_identity,
        expected_target_revision=continuation.expected_owner_revision,
        expected_producing_owner=HUMAN_AUTHORITY_OWNER,
        expected_owner=CONSTITUTIONAL_GOVERNANCE_OWNER,
        expected_authority_scope=CONSTITUTIONAL_AMENDMENT_RATIFICATION_SCOPE,
    )


def compose_g76_revision_4_human_ratification_v1(
    *,
    package: G76Revision4RatificationPackageV1,
    human_authority_act: CanonicalHumanAuthorityActV1 | Mapping[str, Any],
    che_request: CanonicalHumanEntryRequestEnvelopeV1 | Mapping[str, Any],
    che_continuation: CanonicalContinuationEnvelopeV1 | Mapping[str, Any],
) -> ConstitutionalHumanRatificationArtifactV1:
    """Existing-owner G70-04 composition; callable only with a real Human act."""

    validated = validate_g76_revision_4_ratification_package_v1(package)
    request = validate_canonical_che_request_envelope_v1(che_request)
    continuation = validate_canonical_che_continuation_envelope_v1(
        che_continuation
    )
    request_act = canonical_human_authority_act_from_request_v1(request)
    if human_authority_act is None:
        raise FailClosedRuntimeError(
            "constitutional ratification requires a Human Authority Act"
        )
    supplied_act = (
        human_authority_act
        if isinstance(human_authority_act, CanonicalHumanAuthorityActV1)
        else CanonicalHumanAuthorityActV1.from_dict(dict(human_authority_act))
    )
    if request_act is None or request_act.to_dict() != supplied_act.to_dict():
        raise FailClosedRuntimeError(
            "constitutional ratification requires the exact structured Human act"
        )
    bound_act = validate_constitutional_ratification_che_owner_binding_v1(
        request, continuation, supplied_act
    )
    assessment = validated.impact_assessment
    evidence = (
        ConstitutionalHumanRatificationEvidenceReferenceV1(
            evidence_role=HUMAN_AUTHORITY_ACT_EVIDENCE,
            producing_owner=HUMAN_AUTHORITY_OWNER,
            artifact_identity=bound_act.authority_act_identity,
            artifact_digest=_sha256_reference(bound_act.to_dict()),
        ),
        ConstitutionalHumanRatificationEvidenceReferenceV1(
            evidence_role=CHE_REQUEST_EVIDENCE,
            producing_owner=CANONICAL_HUMAN_ENTRY_OWNER,
            artifact_identity=request.request_identity,
            artifact_digest=canonical_che_request_source_act_digest_v1(request),
        ),
        ConstitutionalHumanRatificationEvidenceReferenceV1(
            evidence_role=CHE_CONTINUATION_EVIDENCE,
            producing_owner=CANONICAL_HUMAN_ENTRY_OWNER,
            artifact_identity=continuation.continuation_identity,
            artifact_digest=_sha256_reference(continuation.to_dict()),
        ),
        ConstitutionalHumanRatificationEvidenceReferenceV1(
            evidence_role=IMPACT_ASSESSMENT_EVIDENCE,
            producing_owner=assessment.assessing_owner,
            artifact_identity=assessment.assessment_identity,
            artifact_digest=assessment.artifact_digest,
        ),
    )
    return validate_constitutional_human_ratification_artifact_v1(
        create_constitutional_human_ratification_v1(
            impact_assessment=assessment,
            human_authority_act=bound_act,
            che_request=request,
            che_continuation=continuation,
            evidence_references=evidence,
        )
    )


def submit_g76_revision_4_human_ratification_v1(
    *,
    package: G76Revision4RatificationPackageV1,
    request: CanonicalHumanEntryRequestEnvelopeV1 | dict[str, Any],
    continuation: CanonicalContinuationEnvelopeV1 | dict[str, Any],
):
    """Future Human boundary: consume, but never create, the exact Human act."""

    validated = validate_g76_revision_4_ratification_package_v1(package)
    canonical_request = validate_canonical_che_request_envelope_v1(request)
    canonical_continuation = validate_canonical_che_continuation_envelope_v1(
        continuation
    )
    act = canonical_human_authority_act_from_request_v1(canonical_request)
    if act is None:
        raise FailClosedRuntimeError(
            "G76 Revision 4 ratification submission requires Human Authority Act"
        )
    from aigol.runtime.human_interface_runtime_entry_service import (
        _execute_canonical_che_request_v1,
    )

    def owner_executor(
        _request: CanonicalHumanEntryRequestEnvelopeV1,
    ) -> dict[str, Any]:
        ratification = compose_g76_revision_4_human_ratification_v1(
            package=validated,
            human_authority_act=act,
            che_request=canonical_request,
            che_continuation=canonical_continuation,
        )
        state_identity = constitutional_ratification_owner_state_identity_v1(
            ratification.impact_assessment.assessment_identity,
            ratification.impact_assessment.amendment_proposal.proposal_revision,
        )
        return {
            "constitutional_ratification_owner_result": {
                "contract_version": G76_REVISION_4_OWNER_COMPOSITION_VERSION,
                "owner_status": G76_REVISION_4_RATIFICATION_RECORDED_STATUS,
                "producing_owner": CONSTITUTIONAL_GOVERNANCE_OWNER,
                "conversation_identity": state_identity,
                "owner_state_identity": state_identity,
                "owner_revision": (
                    ratification.impact_assessment.amendment_proposal.proposal_revision
                ),
                "ratification_artifact": ratification.to_dict(),
            },
            "human_visible_completion_result": (
                "Human ratification was recorded and remains not certified."
            ),
        }

    return _execute_canonical_che_request_v1(
        canonical_request,
        owner_executor,
        continuation_envelope=canonical_continuation,
        bind_continuation=True,
        authority_act=act,
    )


__all__ = [
    "G76_REVISION_4_OWNER_COMPOSITION_VERSION",
    "G76_REVISION_4_PRESENTATION_COMMAND",
    "G76_REVISION_4_RATIFICATION_OWNER_STATUS",
    "G76Revision4RatificationPackageV1",
    "compose_g76_revision_4_human_ratification_v1",
    "constitutional_ratification_owner_result_v1",
    "constitutional_ratification_owner_state_identity_v1",
    "materialize_g76_revision_4_ratification_package_v1",
    "present_g76_revision_4_ratification_boundary_v1",
    "submit_g76_revision_4_human_ratification_v1",
    "validate_constitutional_ratification_che_owner_binding_v1",
    "validate_g76_revision_4_ratification_package_v1",
]
