from __future__ import annotations

from dataclasses import fields, replace

import pytest

from aigol.runtime.candidate_h_founder.cj1 import cj1_digest
from aigol.runtime.candidate_h_founder.models import MODEL_REGISTRY
from aigol.runtime.candidate_h_founder.validators import (
    ARTIFACT_IDENTITY_SPECS,
    CandidateValidationError,
    EvidenceDescriptor,
    IdentityDAGNode,
    NESTED_RECORD_CONSTANTS,
    PredecessorReference,
    expected_artifact_identifiers,
    validate_identity_dag,
)


OWNER = "fixture:external-premise-authority"
OWNER_BINDINGS = {
    "RESOLVED_EXTERNAL_PREMISE_AUTHORITY": OWNER,
    "CAPACITY_PRODUCING_OWNER": OWNER,
}


def _values(model_type: type, **changes: object) -> dict[str, object]:
    values = {field.name: f"fixture:{field.name}" for field in fields(model_type)}
    values.update(model_type.CONSTANTS)
    for name, allowed in model_type.ALLOWED_VALUES.items():
        values[name] = sorted(allowed, key=repr)[0]
    for name in model_type.REQUIRED_NULL_FIELDS:
        values[name] = None
    if "producing_owner" in values:
        values["producing_owner"] = OWNER
    values.update(changes)
    return values


def _nested(class_name: str, **changes: object):
    model_type = MODEL_REGISTRY[class_name]
    values = _values(model_type)
    values.update(NESTED_RECORD_CONSTANTS[class_name])
    values.update(changes)
    values["record_digest"] = "sha256:pending"
    pending = model_type(**values)
    payload = pending.to_cj1_object()
    payload.pop("record_digest")
    return replace(pending, record_digest=cj1_digest(payload))


def _with_identity(model):
    idem, identity, digest = expected_artifact_identifiers(model)
    spec = ARTIFACT_IDENTITY_SPECS[type(model)]
    return replace(
        model,
        idempotency_identity=idem,
        **{spec.identity_field: identity, spec.digest_field: digest},
    )


def _capacity():
    premise = ("external-premise-v1:premise", "sha256:premise")
    target = ("founding-target-v5:target", "sha256:target")
    actor = "fixture:human-actor"
    external_capacity = ("human-founder-capacity-v1:capacity", "sha256:capacity")
    issued_at = "fixture:logical-instant"
    actor_record = _nested("HumanFounderActorIdentityRecordV1", human_actor_identity=actor)
    external_record = _nested(
        "HumanFounderExternalCapacityRecordV1",
        external_capacity_identity=external_capacity[0],
        external_capacity_digest=external_capacity[1],
        human_actor_identity=actor,
        external_premise_identity=premise[0],
        external_premise_digest=premise[1],
        external_constituent_model_identity="HUMAN_FOUNDER_ONE_SHOT_EXTERNAL_CONSTITUENT_V1",
        target_identity=target[0],
        target_digest=target[1],
        issued_at=issued_at,
    )
    provenance = _nested(
        "HumanFounderAuthorityProvenanceRecordV1",
        external_premise_identity=premise[0],
        external_premise_digest=premise[1],
        human_actor_identity=actor,
        external_capacity_identity=external_capacity[0],
        external_capacity_digest=external_capacity[1],
    )
    competence = _nested(
        "HumanFounderAuthorityCompetenceRecordV1",
        human_actor_identity=actor,
        external_capacity_identity=external_capacity[0],
        external_capacity_digest=external_capacity[1],
        target_identity=target[0],
        target_digest=target[1],
    )
    scope = _nested(
        "HumanFounderOneShotScopeRecordV1",
        target_identity=target[0],
        target_digest=target[1],
    )
    key = _nested(
        "HumanFounderAuthenticationKeyBindingRecordV1",
        human_actor_identity=actor,
        external_capacity_identity=external_capacity[0],
        external_capacity_digest=external_capacity[1],
        authentication_key_identity="human-founder-ed25519-key-v1:key",
    )
    profile = _nested("HumanFounderAuthenticationVerificationProfileV1")
    status = _nested(
        "HumanFounderCapacityStatusReadBackRecordV1",
        external_capacity_identity=external_capacity[0],
        external_capacity_digest=external_capacity[1],
    )
    issuance_auth = _nested(
        "HumanFounderCapacityIssuanceAuthenticationRecordV1",
        external_premise_identity=premise[0],
        external_premise_digest=premise[1],
        capacity_issuer_identity=OWNER,
        issued_at=issued_at,
    )
    issuance_readback = _nested(
        "HumanFounderCapacityIssuanceCustodyReadBackRecordV1",
        external_premise_identity=premise[0],
        external_premise_digest=premise[1],
    )
    model_type = MODEL_REGISTRY["HumanFounderExternalCapacityEvidenceV2"]
    model = model_type(
        **_values(
            model_type,
            external_premise_identity=premise[0],
            external_premise_digest=premise[1],
            target_identity=target[0],
            target_digest=target[1],
            issued_at=issued_at,
            human_actor_identity_record=actor_record,
            external_capacity_record=external_record,
            authority_provenance_record=provenance,
            authority_competence_record=competence,
            one_shot_scope_record=scope,
            authentication_key_binding_record=key,
            authentication_verification_profile=profile,
            capacity_status_read_back_record=status,
            capacity_issuance_authentication_record=issuance_auth,
            capacity_issuance_custody_read_back_record=issuance_readback,
        )
    )
    return _with_identity(model)


def _reference(descriptor: EvidenceDescriptor) -> PredecessorReference:
    return PredecessorReference(
        descriptor.artifact_type,
        descriptor.artifact_version,
        descriptor.artifact_identity,
        descriptor.artifact_digest,
    )


def _fixture_graph():
    premise = EvidenceDescriptor(
        "ExternalConstituentPremiseEvidence",
        "V1",
        "external-premise-v1:premise",
        "sha256:premise",
        OWNER,
    )
    capacity = _capacity()
    capacity_descriptor = EvidenceDescriptor(
        capacity.artifact_type,
        capacity.artifact_version,
        capacity.artifact_identity,
        capacity.artifact_digest,
        capacity.producing_owner,
    )
    return premise, capacity, capacity_descriptor


def test_valid_complete_dag_is_forward_deterministic() -> None:
    premise, capacity, _ = _fixture_graph()
    nodes = (
        IdentityDAGNode(premise),
        IdentityDAGNode(capacity, (_reference(premise),)),
    )
    first = validate_identity_dag(nodes, owner_bindings=OWNER_BINDINGS)
    second = validate_identity_dag(nodes, owner_bindings=OWNER_BINDINGS)
    assert first == second
    assert first.node_count == 2
    assert first.edge_count == 1
    assert first.ordered_identities == (premise.artifact_identity, capacity.artifact_identity)


def test_missing_predecessor_fails_closed() -> None:
    premise, capacity, _ = _fixture_graph()
    with pytest.raises(CandidateValidationError, match="MISSING_PREDECESSOR"):
        validate_identity_dag(
            (IdentityDAGNode(capacity, (_reference(premise),)),),
            owner_bindings=OWNER_BINDINGS,
        )


@pytest.mark.parametrize(
    ("change", "code"),
    [
        ({"artifact_type": "ExternalConstituentAdmissibilityUniverse"}, "WRONG_PREDECESSOR_TYPE"),
        ({"artifact_version": "V2"}, "WRONG_PREDECESSOR_VERSION"),
        ({"artifact_digest": "sha256:wrong"}, "WRONG_PREDECESSOR_DIGEST"),
    ],
)
def test_wrong_predecessor_tuple_fails_closed(change: dict[str, str], code: str) -> None:
    premise, capacity, _ = _fixture_graph()
    reference = replace(_reference(premise), **change)
    with pytest.raises(CandidateValidationError, match=code):
        validate_identity_dag(
            (IdentityDAGNode(premise), IdentityDAGNode(capacity, (reference,))),
            owner_bindings=OWNER_BINDINGS,
        )


def test_predecessor_identity_binding_mismatch_fails_closed() -> None:
    premise, capacity, _ = _fixture_graph()
    universe = EvidenceDescriptor(
        "ExternalConstituentAdmissibilityUniverse",
        "V1",
        "external-universe-v1:unbound",
        "sha256:unbound",
        OWNER,
    )
    with pytest.raises(CandidateValidationError, match="PREDECESSOR_BINDING_MISMATCH"):
        validate_identity_dag(
            (
                IdentityDAGNode(premise),
                IdentityDAGNode(universe),
                IdentityDAGNode(capacity, (_reference(universe),)),
            ),
            owner_bindings=OWNER_BINDINGS,
        )


def test_cycle_attempt_is_rejected_before_order_inference() -> None:
    premise = EvidenceDescriptor(
        "ExternalConstituentPremiseEvidence", "V1", "external-premise-v1:a", "sha256:a", OWNER
    )
    universe = EvidenceDescriptor(
        "ExternalConstituentAdmissibilityUniverse", "V1", "external-universe-v1:b", "sha256:b", OWNER
    )
    with pytest.raises(CandidateValidationError, match="IDENTITY_CYCLE"):
        validate_identity_dag(
            (
                IdentityDAGNode(premise, (_reference(universe),)),
                IdentityDAGNode(universe, (_reference(premise),)),
            )
        )


def test_forward_reference_is_rejected() -> None:
    premise = EvidenceDescriptor(
        "ExternalConstituentPremiseEvidence", "V1", "external-premise-v1:a", "sha256:a", OWNER
    )
    universe = EvidenceDescriptor(
        "ExternalConstituentAdmissibilityUniverse", "V1", "external-universe-v1:b", "sha256:b", OWNER
    )
    with pytest.raises(CandidateValidationError, match="FORWARD_REFERENCE"):
        validate_identity_dag(
            (IdentityDAGNode(universe, (_reference(premise),)), IdentityDAGNode(premise))
        )


def test_unknown_external_schema_or_version_fails_closed() -> None:
    unknown = EvidenceDescriptor("UnknownCandidateArtifact", "V9", "unknown:x", "sha256:x", OWNER)
    with pytest.raises(CandidateValidationError, match="UNKNOWN_SCHEMA_VERSION"):
        validate_identity_dag((IdentityDAGNode(unknown),))
