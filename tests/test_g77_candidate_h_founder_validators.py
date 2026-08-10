from __future__ import annotations

from dataclasses import fields, replace

import pytest

from aigol.runtime.candidate_h_founder.cj1 import cj1_digest, cj1_identity
from aigol.runtime.candidate_h_founder.models import (
    AUTHENTICATION_CONTRACT_VERSION,
    HFD_ACT_FIELDS,
    MODEL_REGISTRY,
)
from aigol.runtime.candidate_h_founder.validators import (
    ARTIFACT_IDENTITY_SPECS,
    CandidateValidationError,
    NESTED_RECORD_CONSTANTS,
    PREDICATE_CODES,
    PREDICATE_ROW_FIELDS,
    expected_artifact_identifiers,
    validate_artifact,
    validate_p012_structural_bindings,
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
        rule = getattr(model_type, "OWNER_RULE", None)
        fixed = {
            "HUMAN_AUTHORITY",
            "CONSTITUTIONAL_CERTIFICATION_OWNER",
            "CONSTITUTIONAL_GOVERNANCE_OWNER",
            "CONSTITUTIONAL_ROOT_SERIALIZATION_CUSTODIAN",
        }
        values["producing_owner"] = rule if rule in fixed else OWNER
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
    records = {
        "human_actor_identity_record": _nested(
            "HumanFounderActorIdentityRecordV1", human_actor_identity=actor
        ),
        "external_capacity_record": _nested(
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
        ),
        "authority_provenance_record": _nested(
            "HumanFounderAuthorityProvenanceRecordV1",
            external_premise_identity=premise[0],
            external_premise_digest=premise[1],
            human_actor_identity=actor,
            external_capacity_identity=external_capacity[0],
            external_capacity_digest=external_capacity[1],
        ),
        "authority_competence_record": _nested(
            "HumanFounderAuthorityCompetenceRecordV1",
            human_actor_identity=actor,
            external_capacity_identity=external_capacity[0],
            external_capacity_digest=external_capacity[1],
            target_identity=target[0],
            target_digest=target[1],
        ),
        "one_shot_scope_record": _nested(
            "HumanFounderOneShotScopeRecordV1", target_identity=target[0], target_digest=target[1]
        ),
        "authentication_key_binding_record": _nested(
            "HumanFounderAuthenticationKeyBindingRecordV1",
            human_actor_identity=actor,
            external_capacity_identity=external_capacity[0],
            external_capacity_digest=external_capacity[1],
            authentication_key_identity="human-founder-ed25519-key-v1:key",
        ),
        "authentication_verification_profile": _nested(
            "HumanFounderAuthenticationVerificationProfileV1"
        ),
        "capacity_status_read_back_record": _nested(
            "HumanFounderCapacityStatusReadBackRecordV1",
            external_capacity_identity=external_capacity[0],
            external_capacity_digest=external_capacity[1],
        ),
        "capacity_issuance_authentication_record": _nested(
            "HumanFounderCapacityIssuanceAuthenticationRecordV1",
            external_premise_identity=premise[0],
            external_premise_digest=premise[1],
            capacity_issuer_identity=OWNER,
            issued_at=issued_at,
        ),
        "capacity_issuance_custody_read_back_record": _nested(
            "HumanFounderCapacityIssuanceCustodyReadBackRecordV1",
            external_premise_identity=premise[0],
            external_premise_digest=premise[1],
        ),
    }
    model_type = MODEL_REGISTRY["HumanFounderExternalCapacityEvidenceV2"]
    model = model_type(
        **_values(
            model_type,
            external_premise_identity=premise[0],
            external_premise_digest=premise[1],
            target_identity=target[0],
            target_digest=target[1],
            issued_at=issued_at,
            **records,
        )
    )
    return _with_identity(model)


def _authentication_commitment():
    model_type = MODEL_REGISTRY["HumanFounderAuthenticationCommitmentV2"]
    return model_type(**_values(model_type))


def _result(capacity, commitment):
    commitment_payload = commitment.to_cj1_object()
    commitment_pair = (
        cj1_identity("human-founder-auth-commitment-v2-sha256", commitment_payload),
        cj1_digest(commitment_payload),
    )
    key = capacity.authentication_key_binding_record.authentication_key_identity
    actor = capacity.human_actor_identity_record.human_actor_identity
    model_type = MODEL_REGISTRY["HumanFounderAuthenticationResultReadBackEvidenceV2"]
    model = model_type(
        **_values(
            model_type,
            external_premise_identity=capacity.external_premise_identity,
            external_premise_digest=capacity.external_premise_digest,
            human_founder_capacity_identity=capacity.artifact_identity,
            human_founder_capacity_digest=capacity.artifact_digest,
            human_actor_identity=actor,
            authentication_commitment_identity=commitment_pair[0],
            authentication_commitment_digest=commitment_pair[1],
            authenticated_message_digest=commitment_pair[1],
            signature_key_identity=key,
            signature="NON_AUTHORITATIVE_FIXTURE_ONLY_SIGNATURE",
            authentication_result="AUTHENTICATED_VALID",
            terminal_authentication_slot_status="AUTHENTICATED_FINAL",
            signer_outcome_status="VALID_SIGNATURE_FINAL",
            signature_verification_result="TRUE",
            conflict_status="NONE",
        )
    )
    return _with_identity(model)


def _decision(capacity, result, commitment):
    commitment_payload = commitment.to_cj1_object()
    commitment_pair = (
        cj1_identity("human-founder-auth-commitment-v2-sha256", commitment_payload),
        cj1_digest(commitment_payload),
    )
    model_type = MODEL_REGISTRY["ExternalConstituentHumanFirstAdoptionDecisionV2"]
    model = model_type(
        **_values(
            model_type,
            human_founder_external_capacity_evidence_identity=capacity.artifact_identity,
            human_founder_external_capacity_evidence_digest=capacity.artifact_digest,
            authentication_commitment_identity=commitment_pair[0],
            authentication_commitment_digest=commitment_pair[1],
            authentication_result_read_back_identity=result.artifact_identity,
            authentication_result_read_back_digest=result.artifact_digest,
            human_signature_scheme=result.signature_scheme,
            human_signature_key_identity=result.signature_key_identity,
            human_signature=result.signature,
            decision="ADOPT_EXACT_TARGET",
        )
    )
    return _with_identity(model)


def _proof_set(decision, commitment):
    commitment_digest = cj1_digest(commitment.to_cj1_object())
    rows = []
    for rank, code in enumerate(PREDICATE_CODES, start=1):
        row = dict.fromkeys(PREDICATE_ROW_FIELDS, "fixture")
        row.update(
            rank=rank,
            predicate_code=code,
            subject_artifact_type="fixture:subject-type",
            subject_artifact_version="V1",
            subject_identity=f"fixture:subject:{rank}",
            subject_digest=f"sha256:subject:{rank}",
            expected_digest=f"sha256:expected:{rank}",
            observed_digest=f"sha256:observed:{rank}",
            result="TRUE",
        )
        rows.append(row)
    rows[11].update(
        subject_artifact_type="ExternalConstituentHumanFirstAdoptionDecisionV2",
        subject_artifact_version="V2",
        subject_identity=decision.artifact_identity,
        subject_digest=decision.artifact_digest,
        expected_digest=decision.authentication_commitment_digest,
        observed_digest=commitment_digest,
    )
    model_type = MODEL_REGISTRY["ExternalConstituentFoundingEligibilityProofSetV3"]
    model = model_type(
        **_values(
            model_type,
            human_decision_identity=decision.artifact_identity,
            human_decision_digest=decision.artifact_digest,
            ordered_predicate_results=rows,
            predicate_root=cj1_digest(rows),
            proof_result="ELIGIBLE",
            attempt_kind="INITIAL_BEGIN",
            attempt_sequence=1,
            predecessor_attempt_identity=None,
            predecessor_attempt_terminal_read_back_identity=None,
            predecessor_attempt_terminal_read_back_digest=None,
            predecessor_abandoned_commitment_identity=None,
            predecessor_abandoned_commitment_digest=None,
            consuming_disposition_identity=None,
            consuming_disposition_digest=None,
        )
    )
    return _with_identity(model)


def _p012_fixture():
    capacity = _capacity()
    commitment = _authentication_commitment()
    result = _result(capacity, commitment)
    decision = _decision(capacity, result, commitment)
    proof = _proof_set(decision, commitment)
    return proof, decision, capacity, result, commitment


def test_exact_identity_idempotency_digest_and_owner_validation() -> None:
    capacity = _capacity()
    assert validate_artifact(capacity, owner_bindings=OWNER_BINDINGS) is capacity
    assert validate_artifact(capacity, owner_bindings=OWNER_BINDINGS) is capacity


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("artifact_identity", "wrong-domain:abc", "IDENTITY_DOMAIN_MISMATCH"),
        ("artifact_identity", "human-founder-external-capacity-v2:wrong", "ARTIFACT_IDENTITY_MISMATCH"),
        ("artifact_digest", "sha256:wrong", "ARTIFACT_DIGEST_MISMATCH"),
        ("idempotency_identity", "wrong-domain:abc", "IDENTITY_DOMAIN_MISMATCH"),
    ],
)
def test_identity_digest_and_domain_confusion_fail_closed(field: str, value: str, code: str) -> None:
    corrupted = replace(_capacity(), **{field: value})
    with pytest.raises(CandidateValidationError, match=code):
        validate_artifact(corrupted, owner_bindings=OWNER_BINDINGS)


def test_wrong_version_owner_and_null_semantics_fail_closed() -> None:
    capacity = _capacity()
    object.__setattr__(capacity, "artifact_version", "V3")
    with pytest.raises(CandidateValidationError, match="SCHEMA_CONSTANT_MISMATCH"):
        validate_artifact(capacity, owner_bindings=OWNER_BINDINGS)
    capacity = _capacity()
    object.__setattr__(capacity, "producing_owner", "fixture:wrong-owner")
    with pytest.raises(CandidateValidationError, match="OWNER_MISMATCH"):
        validate_artifact(capacity, owner_bindings=OWNER_BINDINGS)
    capacity = _capacity()
    object.__setattr__(capacity, "target_digest", None)
    with pytest.raises(CandidateValidationError, match="INVALID_NULL_SEMANTICS"):
        validate_artifact(capacity, owner_bindings=OWNER_BINDINGS)


def test_contract_version_and_nested_record_tampering_fail_closed() -> None:
    proof, _, capacity, _, _ = _p012_fixture()
    object.__setattr__(proof, "contract_version", "UNKNOWN_CONTRACT")
    with pytest.raises(CandidateValidationError, match="CONTRACT_VERSION_MISMATCH"):
        validate_artifact(proof, owner_bindings=OWNER_BINDINGS)
    bad_record = replace(
        capacity.authentication_key_binding_record,
        record_digest="sha256:wrong",
    )
    corrupted = _with_identity(replace(capacity, authentication_key_binding_record=bad_record))
    with pytest.raises(CandidateValidationError, match="RECORD_DIGEST_MISMATCH"):
        validate_artifact(corrupted, owner_bindings=OWNER_BINDINGS)


def test_valid_p012_revision_3_structural_binding() -> None:
    fixture = _p012_fixture()
    assert validate_p012_structural_bindings(*fixture, owner_bindings=OWNER_BINDINGS)
    assert validate_p012_structural_bindings(*fixture, owner_bindings=OWNER_BINDINGS)


def test_p012_wrong_subject_version_and_binding_fail_closed() -> None:
    proof, decision, capacity, result, commitment = _p012_fixture()
    rows = [dict(row) for row in proof.ordered_predicate_results]
    rows[11]["subject_artifact_version"] = "V1"
    corrupted = replace(proof, ordered_predicate_results=rows, predicate_root=cj1_digest(rows))
    corrupted = _with_identity(corrupted)
    with pytest.raises(CandidateValidationError, match="P012_BINDING_MISMATCH"):
        validate_p012_structural_bindings(
            corrupted, decision, capacity, result, commitment, owner_bindings=OWNER_BINDINGS
        )


def test_hfd_common_base_binding_and_unknown_model_fail_closed() -> None:
    model_type = MODEL_REGISTRY["HumanFounderExternalConstituentActPayloadV2"]
    values = _values(model_type, disposition="ADOPT_EXACT_TARGET")
    base = {name: values[name] for name in HFD_ACT_FIELDS if name not in {"disposition", "candidate_common_base_digest"}}
    act = model_type(**{**values, "candidate_common_base_digest": cj1_digest(base)})
    assert validate_artifact(act) is act
    corrupted = replace(act, candidate_common_base_digest="sha256:wrong")
    with pytest.raises(CandidateValidationError, match="HFD_COMMON_BASE_DIGEST_MISMATCH"):
        validate_artifact(corrupted)
    with pytest.raises(CandidateValidationError, match="UNKNOWN_SCHEMA_VERSION"):
        validate_artifact(object())
