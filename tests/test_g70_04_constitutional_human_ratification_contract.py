from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from hashlib import sha256
import json
from pathlib import Path

import pytest

from aigol.runtime.canonical_human_authority_act_contract_v1 import (
    APPROVAL,
    CANONICAL_HUMAN_AUTHORITY_ACT_CAPABILITY,
    CANONICAL_HUMAN_AUTHORITY_ACT_CONTRACT_VERSION,
    CONFIRMATION,
    HUMAN_AUTHORITY_OWNER,
    CanonicalHumanAuthorityActV1,
    canonical_human_authority_payload_digest_v1,
)
from aigol.runtime.canonical_human_entry_contract_v1 import (
    ACTIVE_CONTINUATION,
    CANONICAL_CHE_CONTINUATION_CONTRACT_VERSION,
    CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
    HUMAN_ACTOR,
    TERMINAL_CONTINUATION,
    CanonicalContinuationEnvelopeV1,
    CanonicalHumanEntryRequestEnvelopeV1,
    canonical_che_request_source_act_digest_v1,
)
from aigol.runtime.constitutional_amendment_proposal_contract_v1 import (
    CONSTITUTIONAL_BASELINE_EVIDENCE,
    GAP_DETERMINATION_EVIDENCE,
    PROPOSER_AUTHORITY_EVIDENCE,
    TARGET_CONSTITUTIONAL_ARTIFACT_EVIDENCE,
    ConstitutionalAmendmentProposalEvidenceReferenceV1,
    create_constitutional_amendment_proposal_v1,
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
    CONSTITUTIONAL_HUMAN_RATIFICATION_ARTIFACT_VERSION,
    CONSTITUTIONAL_HUMAN_RATIFICATION_CONTRACT_VERSION,
    CONSTITUTIONAL_HUMAN_RATIFICATION_SERIALIZATION_VERSION,
    HUMAN_AUTHORITY_ACT_EVIDENCE,
    HUMAN_RATIFICATION_RECORDED_NOT_CERTIFIED,
    IMPACT_ASSESSMENT_EVIDENCE,
    RATIFY_CONSTITUTIONAL_AMENDMENT,
    ConstitutionalHumanRatificationEvidenceReferenceV1,
    constitutional_ratification_payload_v1,
    create_constitutional_human_ratification_v1,
    deserialize_constitutional_human_ratification_v1,
    serialize_constitutional_human_ratification_v1,
    validate_constitutional_human_ratification_artifact_v1,
    validate_constitutional_human_ratification_evidence_reference_v1,
)
from aigol.runtime.constitutional_impact_assessment_contract_v1 import (
    ASSESSOR_AUTHORITY_EVIDENCE,
    CONTRACT_IMPACT_COMPLETENESS_EVIDENCE,
    CRO_IMPACT_EVIDENCE,
    CRO_UNCHANGED,
    IMPACT_ASSESSED_NOT_RATIFIED,
    INVARIANT_IMPACT_COMPLETENESS_EVIDENCE,
    INVARIANT_PRESERVED,
    ONE_PRODUCTION_PATH_PRESERVED,
    OWNER_IMPACT_COMPLETENESS_EVIDENCE,
    OWNER_LOCAL_REPLAY_CUSTODIAN,
    OWNER_RESPONSIBILITY_UNCHANGED,
    PASSIVE_CONSTITUTIONAL_RUNTIME_OBSERVATORY,
    PRODUCTION_PATH_CHANGE_PROPOSED,
    PRODUCTION_PATH_IMPACT_EVIDENCE,
    PROPOSAL_BINDING_EVIDENCE,
    REPLAY_IMPACT_EVIDENCE,
    REPLAY_IMPACT_UNRESOLVED,
    REPLAY_UNCHANGED,
    SUCCESSOR_REQUIRED,
    AffectedConstitutionalContractV1,
    AffectedConstitutionalInvariantV1,
    ConstitutionalImpactEvidenceReferenceV1,
    ConstitutionalOwnerImpactV1,
    assess_constitutional_impact_v1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize


MODULE = Path("aigol/runtime/constitutional_human_ratification_contract_v1.py")
BASELINE = "constitutional-baseline-G70-03"
PROPOSER = "DECLARED_CONSTITUTIONAL_PROPOSER"
ASSESSOR = "CONSTITUTIONAL_IMPACT_ASSESSMENT_OWNER"
TARGET_OWNER = "CONSTITUTIONAL_FLOW_OWNER"
TARGET_IDENTITY = "CONSTITUTIONAL_FLOW_ARCHITECTURE_SPEC_V1"
TARGET_VERSION = "V1"
HUMAN_IDENTITY = "G70-04-HUMAN"
CREATED_AT = "2026-08-05T15:00:00Z"


def _digest(value) -> str:
    if isinstance(value, str):
        encoded = value.encode("utf-8")
    else:
        encoded = canonical_serialize(value).encode("utf-8")
    return "sha256:" + sha256(encoded).hexdigest()


def _gap():
    result = determine_constitutional_gap_v1(
        implementation_request_identity="request-G70-04",
        implementation_responsibility="RATIFY_CONSTITUTIONAL_AMENDMENT",
        responsibility_owner="CONSTITUTIONAL_RATIFICATION_RESPONSIBILITY_OWNER",
        constitutional_baseline_identity=BASELINE,
        evidence_references=(),
        determined_at=CREATED_AT,
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
            "proposal-authority-G70-04",
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
        proposal_title="Ratify a bounded CAP contract",
        normative_change_statement="Add exact Human ratification evidence.",
        proposal_rationale="CAP requires a Human Authority ratification act.",
        evidence_references=evidence,
        proposed_at=CREATED_AT,
    )


def _impact_reference(role, owner, identity, digest=None):
    return ConstitutionalImpactEvidenceReferenceV1(
        evidence_role=role,
        producing_owner=owner,
        artifact_identity=identity,
        artifact_digest=digest or _digest(identity),
    )


def _assessment(*, replay_impact=REPLAY_UNCHANGED, production_path_impact=None):
    proposal = _proposal()
    contract = AffectedConstitutionalContractV1(
        contract_identity=TARGET_IDENTITY,
        contract_version=TARGET_VERSION,
        contract_owner=TARGET_OWNER,
        impact_kind=SUCCESSOR_REQUIRED,
        evidence_producing_owner=TARGET_OWNER,
        evidence_artifact_identity=TARGET_IDENTITY,
        evidence_artifact_digest=_digest(TARGET_IDENTITY),
    )
    invariant_identity = "ONE_PRODUCTION_PATH"
    invariant = AffectedConstitutionalInvariantV1(
        invariant_identity=invariant_identity,
        invariant_owner=CONSTITUTIONAL_GOVERNANCE_OWNER,
        impact_kind=INVARIANT_PRESERVED,
        evidence_producing_owner=CONSTITUTIONAL_GOVERNANCE_OWNER,
        evidence_artifact_identity=f"invariant-{invariant_identity}",
        evidence_artifact_digest=_digest(f"invariant-{invariant_identity}"),
    )
    owner_identity = "owner-impact-G70-04"
    owner = ConstitutionalOwnerImpactV1(
        owner_identity=TARGET_OWNER,
        responsibility_identity="CONSTITUTIONAL_FLOW_OWNERSHIP",
        impact_kind=OWNER_RESPONSIBILITY_UNCHANGED,
        evidence_producing_owner=CONSTITUTIONAL_GOVERNANCE_OWNER,
        evidence_artifact_identity=owner_identity,
        evidence_artifact_digest=_digest(owner_identity),
    )
    evidence = (
        _impact_reference(
            PROPOSAL_BINDING_EVIDENCE,
            proposal.proposing_owner,
            proposal.proposal_identity,
            proposal.artifact_digest,
        ),
        _impact_reference(
            ASSESSOR_AUTHORITY_EVIDENCE,
            ASSESSOR,
            "assessor-authority-G70-04",
        ),
        _impact_reference(
            CONTRACT_IMPACT_COMPLETENESS_EVIDENCE,
            ASSESSOR,
            "contract-impact-G70-04",
        ),
        _impact_reference(
            INVARIANT_IMPACT_COMPLETENESS_EVIDENCE,
            ASSESSOR,
            "invariant-impact-G70-04",
        ),
        _impact_reference(
            REPLAY_IMPACT_EVIDENCE,
            OWNER_LOCAL_REPLAY_CUSTODIAN,
            "replay-impact-G70-04",
        ),
        _impact_reference(
            CRO_IMPACT_EVIDENCE,
            PASSIVE_CONSTITUTIONAL_RUNTIME_OBSERVATORY,
            "cro-impact-G70-04",
        ),
        _impact_reference(
            PRODUCTION_PATH_IMPACT_EVIDENCE,
            CONSTITUTIONAL_GOVERNANCE_OWNER,
            "production-impact-G70-04",
        ),
        _impact_reference(
            OWNER_IMPACT_COMPLETENESS_EVIDENCE,
            CONSTITUTIONAL_GOVERNANCE_OWNER,
            "owner-impact-G70-04",
        ),
    )
    return assess_constitutional_impact_v1(
        amendment_proposal=proposal,
        assessing_owner=ASSESSOR,
        affected_contracts=(contract,),
        affected_invariants=(invariant,),
        replay_impact=replay_impact,
        cro_impact=CRO_UNCHANGED,
        production_path_impact=(
            production_path_impact or ONE_PRODUCTION_PATH_PRESERVED
        ),
        owner_impacts=(owner,),
        evidence_references=evidence,
        assessed_at=CREATED_AT,
    )


def _transport(
    assessment=None,
    *,
    payload=None,
    authority_kind=APPROVAL,
    expected_owner=CONSTITUTIONAL_GOVERNANCE_OWNER,
    scope=CONSTITUTIONAL_AMENDMENT_RATIFICATION_SCOPE,
    target_identity=None,
    target_revision=None,
    actor_class=HUMAN_ACTOR,
    source_modality="STRUCTURED",
    capabilities=(CANONICAL_HUMAN_AUTHORITY_ACT_CAPABILITY,),
    continuation_state=ACTIVE_CONTINUATION,
):
    assessment = assessment or _assessment()
    payload = (
        constitutional_ratification_payload_v1(assessment)
        if payload is None
        else payload
    )
    target_identity = target_identity or assessment.assessment_identity
    target_revision = (
        assessment.amendment_proposal.proposal_revision
        if target_revision is None
        else target_revision
    )
    act = CanonicalHumanAuthorityActV1(
        contract_version=CANONICAL_HUMAN_AUTHORITY_ACT_CONTRACT_VERSION,
        authority_act_identity="G70-04-HUMAN-ACT",
        authority_kind=authority_kind,
        interaction_identity="G70-04-INTERACTION",
        conversation_identity="G70-04-CONVERSATION",
        session_identity="G70-04-SESSION",
        actor_identity=HUMAN_IDENTITY,
        request_identity="G70-04-REQUEST",
        continuation_identity="G70-04-CONTINUATION",
        target_identity=target_identity,
        target_revision=target_revision,
        producing_owner=HUMAN_AUTHORITY_OWNER,
        expected_owner=expected_owner,
        authority_scope=scope,
        payload=payload,
        payload_digest=canonical_human_authority_payload_digest_v1(payload),
        metadata={"transport_interface_identity": "G70-04-HIC"},
    )
    request = CanonicalHumanEntryRequestEnvelopeV1(
        contract_version=CANONICAL_CHE_REQUEST_CONTRACT_VERSION,
        interface_identity="G70-04-HIC",
        adapter_identity="G70-04-HIC-ADAPTER",
        actor_identity=HUMAN_IDENTITY,
        actor_class=actor_class,
        session_identity="G70-04-SESSION",
        workspace_identity="G70-04-WORKSPACE",
        runtime_scope_identity="G70-04-RUNTIME-SCOPE",
        request_identity="G70-04-REQUEST",
        source_act_identity=act.authority_act_identity,
        order_identity="G70-04-ORDER",
        idempotency_identity="G70-04-IDEMPOTENCY",
        source_payload=act.to_dict(),
        source_encoding="UTF-8",
        source_modality=source_modality,
        declared_capabilities=capabilities,
        metadata={"transport_trace_identity": "G70-04-TRACE"},
        created_at=CREATED_AT,
    )
    continuation = CanonicalContinuationEnvelopeV1(
        contract_version=CANONICAL_CHE_CONTINUATION_CONTRACT_VERSION,
        continuation_identity="G70-04-CONTINUATION",
        interaction_identity="G70-04-INTERACTION",
        conversation_identity="G70-04-CONVERSATION",
        session_identity="G70-04-SESSION",
        actor_identity=HUMAN_IDENTITY,
        workspace_identity="G70-04-WORKSPACE",
        runtime_scope_identity="G70-04-RUNTIME-SCOPE",
        request_identity="G70-04-PRIOR-REQUEST",
        previous_response_identity="G70-04-PRIOR-RESPONSE",
        previous_order_identity="G70-04-PRIOR-ORDER",
        previous_idempotency_identity="G70-04-PRIOR-IDEMPOTENCY",
        continuation_sequence=1,
        expected_next_act_identity=assessment.assessment_identity,
        expected_owner_state_identity="G70-04-RATIFICATION-OWNER-STATE",
        expected_owner_revision=assessment.amendment_proposal.proposal_revision,
        continuation_state=continuation_state,
        correlation_identity="G70-04-CORRELATION",
        metadata={"transport_trace_identity": "G70-04-CONTINUATION-TRACE"},
    )
    return assessment, act, request, continuation


def _ratification_reference(role, owner, identity, digest):
    return ConstitutionalHumanRatificationEvidenceReferenceV1(
        evidence_role=role,
        producing_owner=owner,
        artifact_identity=identity,
        artifact_digest=digest,
    )


def _evidence(assessment, act, request, continuation):
    return (
        _ratification_reference(
            HUMAN_AUTHORITY_ACT_EVIDENCE,
            HUMAN_AUTHORITY_OWNER,
            act.authority_act_identity,
            _digest(act.to_dict()),
        ),
        _ratification_reference(
            CHE_REQUEST_EVIDENCE,
            CANONICAL_HUMAN_ENTRY_OWNER,
            request.request_identity,
            canonical_che_request_source_act_digest_v1(request),
        ),
        _ratification_reference(
            CHE_CONTINUATION_EVIDENCE,
            CANONICAL_HUMAN_ENTRY_OWNER,
            continuation.continuation_identity,
            _digest(continuation.to_dict()),
        ),
        _ratification_reference(
            IMPACT_ASSESSMENT_EVIDENCE,
            assessment.assessing_owner,
            assessment.assessment_identity,
            assessment.artifact_digest,
        ),
    )


def _create(transport=None, evidence=None):
    assessment, act, request, continuation = transport or _transport()
    return create_constitutional_human_ratification_v1(
        impact_assessment=assessment,
        human_authority_act=act,
        che_request=request,
        che_continuation=continuation,
        evidence_references=(
            evidence or _evidence(assessment, act, request, continuation)
        ),
    )


def test_ratification_is_immutable_versioned_human_and_not_certified():
    ratification = _create()

    assert ratification.contract_version == (
        CONSTITUTIONAL_HUMAN_RATIFICATION_CONTRACT_VERSION
    )
    assert ratification.artifact_version == (
        CONSTITUTIONAL_HUMAN_RATIFICATION_ARTIFACT_VERSION
    )
    assert ratification.serialization_version == (
        CONSTITUTIONAL_HUMAN_RATIFICATION_SERIALIZATION_VERSION
    )
    assert ratification.ratification_status == (
        HUMAN_RATIFICATION_RECORDED_NOT_CERTIFIED
    )
    assert ratification.ratifying_human_actor_identity == HUMAN_IDENTITY
    with pytest.raises(FrozenInstanceError):
        ratification.ratification_status = "CERTIFIED"


def test_exact_payload_binds_gap_proposal_assessment_and_classification():
    assessment = _assessment()
    payload = constitutional_ratification_payload_v1(assessment)

    assert set(payload) == {
        "ratification_command",
        "impact_assessment_identity",
        "impact_assessment_digest",
        "impact_classification",
        "amendment_proposal_identity",
        "amendment_proposal_digest",
        "constitutional_gap_identity",
        "constitutional_gap_digest",
    }
    assert payload["ratification_command"] == RATIFY_CONSTITUTIONAL_AMENDMENT
    assert payload["impact_assessment_identity"] == assessment.assessment_identity
    assert payload["amendment_proposal_identity"] == (
        assessment.amendment_proposal.proposal_identity
    )


def test_ratification_identity_and_digest_are_content_deterministic():
    first = _create()
    second = _create()

    assert first == second
    assert first.ratification_identity == second.ratification_identity
    assert first.artifact_digest == second.artifact_digest
    assert first.ratification_identity.startswith("CONSTITUTIONAL-HUMAN-RATIFICATION-")


def test_boundary_impact_may_be_exactly_ratified_without_activation():
    assessment = _assessment(
        production_path_impact=PRODUCTION_PATH_CHANGE_PROPOSED
    )
    ratification = _create(_transport(assessment))

    assert ratification.impact_assessment.impact_classification == (
        "CONSTITUTIONAL_BOUNDARY_IMPACT"
    )
    assert ratification.amendment_activation_performed is False
    assert ratification.production_path_count == 1


def test_unresolved_impact_fails_closed_before_ratification():
    assessment = _assessment(replay_impact=REPLAY_IMPACT_UNRESOLVED)
    with pytest.raises(FailClosedRuntimeError, match="unresolved.*cannot be ratified"):
        _create(_transport(assessment))


@pytest.mark.parametrize(
    "payload,match",
    (
        ("yes", "payload structure is invalid"),
        ({"ratification_command": RATIFY_CONSTITUTIONAL_AMENDMENT}, "structure"),
    ),
)
def test_natural_assent_or_partial_payload_cannot_ratify(payload, match):
    with pytest.raises(FailClosedRuntimeError, match=match):
        _create(_transport(payload=payload))


def test_tampered_exact_payload_fails_closed():
    assessment = _assessment()
    payload = constitutional_ratification_payload_v1(assessment)
    payload["impact_classification"] = "TAMPERED"

    with pytest.raises(FailClosedRuntimeError, match="payload binding is invalid"):
        _create(_transport(assessment, payload=payload))


@pytest.mark.parametrize(
    "transport_kwargs,match",
    (
        ({"authority_kind": CONFIRMATION}, "kind binding is invalid"),
        ({"expected_owner": "WRONG_OWNER"}, "expected owner binding is invalid"),
        ({"scope": "WRONG_SCOPE"}, "scope binding is invalid"),
        ({"target_identity": "WRONG_TARGET"}, "continuation target binding"),
        ({"target_revision": 2}, "revision is stale"),
        ({"actor_class": "ELIGIBLE_SOURCE_ACTOR"}, "authenticated Human actor"),
        ({"source_modality": "TEXT"}, "STRUCTURED modality"),
        ({"capabilities": ("TEXT_INPUT",)}, "payload binding is invalid"),
        ({"continuation_state": TERMINAL_CONTINUATION}, "terminal continuation"),
    ),
)
def test_authority_and_che_binding_mismatches_fail_closed(transport_kwargs, match):
    with pytest.raises(FailClosedRuntimeError, match=match):
        _create(_transport(**transport_kwargs))


def test_public_evidence_validator_and_complete_sequence_are_exact():
    transport = _transport()
    assessment, act, request, continuation = transport
    evidence = _evidence(assessment, act, request, continuation)

    assert (
        validate_constitutional_human_ratification_evidence_reference_v1(
            value=evidence[0].to_dict(),
            expected_role=HUMAN_AUTHORITY_ACT_EVIDENCE,
            expected_owner=HUMAN_AUTHORITY_OWNER,
            expected_artifact_identity=act.authority_act_identity,
            expected_artifact_digest=_digest(act.to_dict()),
        )
        == evidence[0]
    )
    with pytest.raises(FailClosedRuntimeError, match="incomplete"):
        _create(transport, evidence=evidence[:-1])
    with pytest.raises(FailClosedRuntimeError, match="order is not canonical"):
        _create(transport, evidence=tuple(reversed(evidence)))
    with pytest.raises(FailClosedRuntimeError, match="evidence identity is invalid"):
        _create(
            transport,
            evidence=(
                replace(evidence[0], artifact_identity="WRONG_ACT"),
                *evidence[1:],
            ),
        )


def test_public_artifact_validator_round_trips_and_rejects_tampering():
    ratification = _create()

    assert (
        validate_constitutional_human_ratification_artifact_v1(
            ratification.to_dict()
        )
        == ratification
    )
    with pytest.raises(FailClosedRuntimeError, match="version is invalid"):
        validate_constitutional_human_ratification_artifact_v1(
            replace(ratification, artifact_version="RATIFICATION_V2")
        )
    with pytest.raises(FailClosedRuntimeError, match="Human binding is invalid"):
        validate_constitutional_human_ratification_artifact_v1(
            replace(ratification, ratified_at="2026-08-05T16:00:00Z")
        )


def test_serialization_is_canonical_versioned_and_round_trips():
    ratification = _create()
    serialized = serialize_constitutional_human_ratification_v1(ratification)

    assert deserialize_constitutional_human_ratification_v1(serialized) == ratification
    assert deserialize_constitutional_human_ratification_v1(
        serialized.encode("utf-8")
    ) == ratification
    assert serialize_constitutional_human_ratification_v1(ratification) == serialized


def test_noncanonical_and_tampered_serialization_fail_closed():
    ratification = _create()
    canonical = serialize_constitutional_human_ratification_v1(ratification)

    with pytest.raises(FailClosedRuntimeError, match="not canonical"):
        deserialize_constitutional_human_ratification_v1(
            json.dumps(json.loads(canonical), indent=2, sort_keys=True)
        )
    tampered = json.loads(canonical)
    tampered["ratifying_human_actor_identity"] = "TAMPERED"
    with pytest.raises(FailClosedRuntimeError, match="Human binding is invalid"):
        deserialize_constitutional_human_ratification_v1(
            json.dumps(tampered, sort_keys=True, separators=(",", ":"))
        )


def test_ratification_preserves_topology_and_has_no_later_authority():
    ratification = _create()

    assert (
        ratification.che_definition_count,
        ratification.production_hic_family_count,
        ratification.production_owner_chain_count,
        ratification.production_path_count,
        ratification.parallel_production_path_count,
    ) == (1, 1, 1, 1, 0)
    assert ratification.amendment_certification_performed is False
    assert ratification.amendment_activation_performed is False
    assert ratification.runtime_mutation_performed is False
    assert ratification.production_behavior_changed is False
    assert ratification.replay_path_created is False
    assert ratification.cro_authority_created is False

    with pytest.raises(FailClosedRuntimeError, match="boundary invariants"):
        validate_constitutional_human_ratification_artifact_v1(
            replace(ratification, amendment_certification_performed=True)
        )


def test_contract_has_no_persistence_certification_activation_or_production_calls():
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert called_names.isdisjoint(
        {
            "open",
            "write_json_immutable",
            "certify_amendment",
            "activate_amendment",
            "run_human_interface_runtime_entry",
        }
    )
    source = MODULE.read_text(encoding="utf-8").lower()
    assert "historical implementations" not in source
