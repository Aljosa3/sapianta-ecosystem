from __future__ import annotations

from dataclasses import FrozenInstanceError, fields

import pytest

from aigol.runtime.candidate_h_founder.cj1 import cj1_decode
from aigol.runtime.candidate_h_founder.models import (
    AUTHENTICATION_CONTRACT_VERSION,
    AUTH_RESULT_V2_SEMANTIC_FIELDS,
    CAPACITY_V2_SEMANTIC_FIELDS,
    G77_62_MODEL_SPECS,
    HFD_ACT_FIELDS,
    HFD_REVIEW_FIELDS,
    HUMAN_AUTHORITY,
    HUMAN_DECISION_V2_SEMANTIC_FIELDS,
    MODEL_REGISTRY,
    MODEL_OWNER_RULES,
    CanonicalModelError,
    ExternalConstituentHumanFirstAdoptionDecisionV2,
    ExternalConstituentInstrumentCommitmentV3,
    HumanFounderAuthenticationResultReadBackEvidenceV2,
    HumanFounderExternalCapacityEvidenceV2,
    HumanFounderExternalConstituentActPayloadV2,
)


def _values(model_type: type, **changes: object) -> dict[str, object]:
    values = {field.name: f"fixture:{field.name}" for field in fields(model_type)}
    values.update(model_type.CONSTANTS)
    for name, allowed in model_type.ALLOWED_VALUES.items():
        values[name] = sorted(allowed, key=repr)[0]
    for name in model_type.REQUIRED_NULL_FIELDS:
        values[name] = None
    values.update(changes)
    return values


def test_exact_primary_semantic_field_counts_and_order() -> None:
    assert len(HFD_ACT_FIELDS) == 77
    assert len(HFD_REVIEW_FIELDS) == 15
    assert len(CAPACITY_V2_SEMANTIC_FIELDS) == 34
    assert len(AUTH_RESULT_V2_SEMANTIC_FIELDS) == 50
    assert len(HUMAN_DECISION_V2_SEMANTIC_FIELDS) == 31
    assert HumanFounderExternalCapacityEvidenceV2.SEMANTIC_FIELDS == CAPACITY_V2_SEMANTIC_FIELDS
    assert (
        HumanFounderAuthenticationResultReadBackEvidenceV2.SEMANTIC_FIELDS
        == AUTH_RESULT_V2_SEMANTIC_FIELDS
    )
    assert ExternalConstituentHumanFirstAdoptionDecisionV2.SEMANTIC_FIELDS == (
        HUMAN_DECISION_V2_SEMANTIC_FIELDS
    )


def test_complete_g77_62_successor_registry_versions_and_prefixes() -> None:
    assert len(G77_62_MODEL_SPECS) == 15
    expected_versions = {
        "ConstitutionalMetaRepairInitialAdoptionTargetV5": "V5",
        "ExternalConstituentInstrumentCommitmentV3": "V3",
        "ExternalConstituentOneShotFoundingInstrumentV4": "V4",
        "ExternalConstituentFoundingEligibilityProofSetV3": "V3",
        "ExternalConstituentFoundingEligibilityCertificationV3": "V3",
        "ExternalConstituentFoundingAdoptionTransitionV3": "V3",
        "ConstitutionalExistingOrdinaryRepairChainCensusV2": "V2",
        "OrdinaryCAPReachabilityStateV2": "V2",
        "CandidateHOneShotDormancyRebaseGuardV2": "V2",
        "ConstitutionalMetaRepairTransitionV3": "V3",
        "ConstitutionalMetaRepairStateV3": "V3",
        "ConstitutionalTerminalRootSemanticImageCommitmentV3": "V3",
        "ConstitutionalRootSerializationCoordinatorStateV4": "V4",
        "ConstitutionalRootEvolutionSnapshotV4": "V4",
        "CandidateHFoundingAttemptTerminalReadBackV1": "V1",
    }
    assert {name: spec["artifact_version"] for name, spec in G77_62_MODEL_SPECS.items()} == expected_versions
    assert len({spec["identity_prefix"] for spec in G77_62_MODEL_SPECS.values()}) == 15
    assert len({spec["idempotency_prefix"] for spec in G77_62_MODEL_SPECS.values()}) == 15
    assert G77_62_MODEL_SPECS["ConstitutionalRootEvolutionSnapshotV4"]["owner_rule"] == (
        "CONSTITUTIONAL_ROOT_SERIALIZATION_CUSTODIAN"
    )
    assert G77_62_MODEL_SPECS["ExternalConstituentFoundingEligibilityProofSetV3"][
        "owner_rule"
    ] == "CONSTITUTIONAL_CERTIFICATION_OWNER"


def test_exact_versions_tokens_owners_and_frozen_behavior() -> None:
    capacity = HumanFounderExternalCapacityEvidenceV2(**_values(HumanFounderExternalCapacityEvidenceV2))
    decision = ExternalConstituentHumanFirstAdoptionDecisionV2(
        **_values(ExternalConstituentHumanFirstAdoptionDecisionV2)
    )
    assert capacity.artifact_version == "V2"
    assert capacity.contract_version == AUTHENTICATION_CONTRACT_VERSION
    assert decision.producing_owner == HUMAN_AUTHORITY
    assert decision.human_custody_owner_identity == HUMAN_AUTHORITY
    assert MODEL_OWNER_RULES["HumanFounderExternalCapacityEvidenceV2"] == (
        "RESOLVED_EXTERNAL_PREMISE_AUTHORITY"
    )
    with pytest.raises(FrozenInstanceError):
        capacity.artifact_version = "V3"
    nested = HumanFounderExternalConstituentActPayloadV2(
        **_values(
            HumanFounderExternalConstituentActPayloadV2,
            candidate_common_base_digest={"fixture": ["immutable"]},
        )
    )
    with pytest.raises(TypeError):
        nested.candidate_common_base_digest["fixture"] = []


def test_required_fields_unknown_fields_and_constant_mismatch_fail_closed() -> None:
    values = _values(HumanFounderExternalConstituentActPayloadV2)
    values.pop("issued_at")
    with pytest.raises(TypeError):
        HumanFounderExternalConstituentActPayloadV2(**values)
    values = _values(HumanFounderExternalConstituentActPayloadV2)
    values["unknown_field"] = "forbidden"
    with pytest.raises(TypeError):
        HumanFounderExternalConstituentActPayloadV2(**values)
    with pytest.raises(CanonicalModelError, match="protocol_version"):
        HumanFounderExternalConstituentActPayloadV2(
            **_values(HumanFounderExternalConstituentActPayloadV2, protocol_version="V3")
        )
    with pytest.raises(CanonicalModelError, match="closed vocabulary"):
        HumanFounderExternalConstituentActPayloadV2(
            **_values(HumanFounderExternalConstituentActPayloadV2, disposition="MAYBE")
        )


def test_pair_and_conditional_null_semantics() -> None:
    with pytest.raises(CanonicalModelError, match="half-pair"):
        HumanFounderExternalCapacityEvidenceV2(
            **_values(HumanFounderExternalCapacityEvidenceV2, target_digest=None)
        )
    with pytest.raises(CanonicalModelError, match="both null or both non-null"):
        ExternalConstituentInstrumentCommitmentV3(
            **_values(ExternalConstituentInstrumentCommitmentV3, not_before=None)
        )
    valid = HumanFounderAuthenticationResultReadBackEvidenceV2(
        **_values(
            HumanFounderAuthenticationResultReadBackEvidenceV2,
            authentication_result="AUTHENTICATED_VALID",
            signature="NON_AUTHORITATIVE_FIXTURE_ONLY_SIGNATURE",
        )
    )
    assert valid.signature is not None
    with pytest.raises(CanonicalModelError, match="requires a signature"):
        HumanFounderAuthenticationResultReadBackEvidenceV2(
            **_values(
                HumanFounderAuthenticationResultReadBackEvidenceV2,
                authentication_result="AUTHENTICATED_VALID",
                signature=None,
            )
        )
    rejected = HumanFounderAuthenticationResultReadBackEvidenceV2(
        **_values(
            HumanFounderAuthenticationResultReadBackEvidenceV2,
            authentication_result="AUTHENTICATION_REJECTED_FINAL",
            signature=None,
        )
    )
    assert rejected.signature is None


def test_every_declared_model_is_frozen_and_cj1_compatible() -> None:
    assert len(MODEL_REGISTRY) == 33
    for model_type in MODEL_REGISTRY.values():
        model = model_type(**_values(model_type))
        assert tuple(field.name for field in fields(model)) == model_type.FIELD_NAMES
        assert cj1_decode(model.to_cj1_bytes()) == model.to_cj1_object()
        first = fields(model)[0].name
        with pytest.raises(FrozenInstanceError):
            setattr(model, first, "changed")
