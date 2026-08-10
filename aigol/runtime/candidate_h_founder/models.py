"""Frozen canonical Candidate H model schemas.

The declarations in this module are a direct, data-only rendering of the
closed HFD-04 and G77-62/64/71/73/77 contracts.  They intentionally contain
no validator graph, persistence, authentication, Replay, CRO, or root logic.
"""

from __future__ import annotations

from dataclasses import Field, fields, make_dataclass
from types import MappingProxyType
from collections.abc import Mapping, Sequence
from typing import ClassVar

from .cj1 import cj1_encode


G77_62_CONTRACT_VERSION = (
    "G77_62_EXTERNAL_CONSTITUENT_CANDIDATE_H_INSTANTIATION_CONTRACT_REVISION_3_V1"
)
AUTHENTICATION_CONTRACT_VERSION = "CANDIDATE_H_AUTHENTICATION_REDESIGN_REVISION_3_V1"
HFD_PROTOCOL_VERSION = "V2"
HUMAN_AUTHORITY = "HUMAN_AUTHORITY"


class CanonicalModelError(ValueError):
    """Raised when a frozen model violates its closed local schema."""


def _names(text: str) -> tuple[str, ...]:
    return tuple(text.split())


class FrozenCanonicalModel:
    """Shared behavior for generated frozen, keyword-only schema records."""

    FIELD_NAMES: ClassVar[tuple[str, ...]]
    SEMANTIC_FIELDS: ClassVar[tuple[str, ...]]
    REQUIRED_NULL_FIELDS: ClassVar[frozenset[str]] = frozenset()
    CONSTANTS: ClassVar[MappingProxyType] = MappingProxyType({})
    ALLOWED_VALUES: ClassVar[MappingProxyType] = MappingProxyType({})

    def __post_init__(self) -> None:
        for name, expected in self.CONSTANTS.items():
            if getattr(self, name) != expected:
                raise CanonicalModelError(
                    f"{type(self).__name__}.{name} must equal {expected!r}"
                )
        for name, allowed in self.ALLOWED_VALUES.items():
            if getattr(self, name) not in allowed:
                raise CanonicalModelError(
                    f"{type(self).__name__}.{name} is outside the closed vocabulary"
                )
        for name in self.REQUIRED_NULL_FIELDS:
            if getattr(self, name) is not None:
                raise CanonicalModelError(
                    f"{type(self).__name__}.{name} must be canonical null"
                )
        for field in fields(self):
            object.__setattr__(self, field.name, _immutable(getattr(self, field.name)))
        names = set(self.FIELD_NAMES)
        for name in self.FIELD_NAMES:
            if not name.endswith("_identity"):
                continue
            digest_name = f"{name[:-9]}_digest"
            if digest_name in names and ((getattr(self, name) is None) != (getattr(self, digest_name) is None)):
                raise CanonicalModelError(
                    f"{type(self).__name__} contains half-pair {name}/{digest_name}"
                )
        _check_conditional_nulls(self)
        cj1_encode(self.to_cj1_object())

    def to_cj1_object(self) -> dict[str, object]:
        return {field.name: _json_value(getattr(self, field.name)) for field in fields(self)}

    def to_cj1_bytes(self) -> bytes:
        return cj1_encode(self.to_cj1_object())


def _immutable(value: object) -> object:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _immutable(item) for key, item in value.items()})
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray, memoryview)):
        return tuple(_immutable(item) for item in value)
    return value


def _json_value(value: object) -> object:
    if isinstance(value, FrozenCanonicalModel):
        return value.to_cj1_object()
    if isinstance(value, Mapping):
        return {key: _json_value(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray, memoryview)):
        return [_json_value(item) for item in value]
    return value


def _check_conditional_nulls(model: FrozenCanonicalModel) -> None:
    name = type(model).__name__
    if name in {
        "ExternalConstituentInstrumentCommitmentV3",
        "ExternalConstituentOneShotFoundingInstrumentV4",
    }:
        if (model.not_before is None) != (model.expires_at is None):
            raise CanonicalModelError("not_before and expires_at must be both null or both non-null")
    if name == "HumanFounderAuthenticationResultReadBackEvidenceV2":
        if model.authentication_result == "AUTHENTICATED_VALID":
            if model.signature is None:
                raise CanonicalModelError("authenticated result requires a signature")
        elif model.authentication_result in {
            "AUTHENTICATION_REJECTED_FINAL",
            "INDETERMINATE_NO_VALID_RESULT",
        } and model.signature is not None:
            raise CanonicalModelError("non-valid terminal result requires canonical-null signature")
    if name == "CandidateHFoundingAttemptTerminalReadBackV1":
        if model.terminal_result == "CONSUMED":
            if model.terminal_failure_evidence_identity is not None or model.next_attempt_sequence is not None:
                raise CanonicalModelError("CONSUMED terminal read-back forbids failure and retry")
        elif model.terminal_result == "ABANDONED":
            if model.terminal_failure_evidence_identity is None or model.next_attempt_sequence is None:
                raise CanonicalModelError("ABANDONED terminal read-back requires failure and retry sequence")


MODEL_REGISTRY: dict[str, type[FrozenCanonicalModel]] = {}


def _define(
    name: str,
    field_names: tuple[str, ...],
    *,
    semantic_fields: tuple[str, ...] | None = None,
    constants: dict[str, object] | None = None,
    allowed_values: dict[str, frozenset[object]] | None = None,
    required_null_fields: frozenset[str] = frozenset(),
) -> type[FrozenCanonicalModel]:
    if len(field_names) != len(set(field_names)):
        raise RuntimeError(f"duplicate field in closed schema {name}")
    namespace = {
        "__module__": __name__,
        "FIELD_NAMES": field_names,
        "SEMANTIC_FIELDS": semantic_fields if semantic_fields is not None else field_names,
        "CONSTANTS": MappingProxyType(dict(constants or {})),
        "ALLOWED_VALUES": MappingProxyType(dict(allowed_values or {})),
        "REQUIRED_NULL_FIELDS": required_null_fields,
    }
    cls = make_dataclass(
        name,
        [(field_name, object) for field_name in field_names],
        bases=(FrozenCanonicalModel,),
        namespace=namespace,
        frozen=True,
        slots=True,
        kw_only=True,
    )
    MODEL_REGISTRY[name] = cls
    globals()[name] = cls
    return cls


_COMMON_ENVELOPE_HEAD = _names(
    "artifact_type artifact_version artifact_identity artifact_digest contract_version "
    "idempotency_identity producing_owner"
)


def _enveloped(semantic_fields: tuple[str, ...]) -> tuple[str, ...]:
    return _COMMON_ENVELOPE_HEAD + semantic_fields + ("metadata",)


# HFD-04 external compatibility payloads.
HFD_ACT_FIELDS = _names("""
protocol_source_identity protocol_source_digest protocol_version act_artifact_type
act_artifact_version predecessor_protocol_identity predecessor_protocol_digest
independent_assessment_identity independent_assessment_digest external_constituent_model_identity
human_founder_external_capacity_reference_identity human_founder_external_capacity_reference_digest
external_authority_evidence_manifest_identity external_authority_evidence_manifest_digest
authority_provenance_evidence_identity authority_provenance_evidence_digest
authority_competence_evidence_identity authority_competence_evidence_digest
candidate_h_input_reference_manifest_identity candidate_h_input_reference_manifest_digest
g77_64_identity g77_64_digest g77_65_identity g77_65_digest g77_66_identity g77_66_digest
g77_67_identity g77_67_digest g77_68_identity g77_68_digest hfd_01_identity hfd_01_digest
founding_target_identity founding_target_digest disposition disposition_sequence
maximum_authoritative_dispositions exact_target_only delegation_permitted
transfer_within_sapianta_permitted reset_permitted reissue_permitted
target_substitution_permitted recurrence_permitted post_terminal_revival_permitted
permanent_exhaustion_required founder_post_founding_special_authority
ordinary_post_founding_governance_only production_paths parallel_production_paths
persistent_founding_paths immediate_effect_ceiling publication_authorized
normative_activation_authorized g69_cdp_authorized implementation_authorized
candidate_h_instantiation_authorized begin_authorized clia_validation_authorized
deployment_authorized production_authorized authentication_domain_identity
authentication_domain_digest human_review_contract_identity
human_review_contract_source_identity human_review_contract_source_digest
human_finality_domain_identity human_finality_domain_digest human_finality_slot_identity
human_finality_epoch predecessor_finality_slot_status finality_sequence finality_required
non_equivocation_required exhaustion_evidence_required issued_at candidate_common_base_digest
""")
_define(
    "HumanFounderExternalConstituentActPayloadV2",
    HFD_ACT_FIELDS,
    constants={
        "protocol_version": "V2",
        "act_artifact_type": "HUMAN_FOUNDER_EXTERNAL_CONSTITUENT_ACT",
        "act_artifact_version": "V2",
        "external_constituent_model_identity": "HUMAN_FOUNDER_ONE_SHOT_EXTERNAL_CONSTITUENT_V1",
        "disposition_sequence": 1,
        "maximum_authoritative_dispositions": 1,
        "exact_target_only": True,
        "delegation_permitted": False,
        "transfer_within_sapianta_permitted": False,
        "reset_permitted": False,
        "reissue_permitted": False,
        "target_substitution_permitted": False,
        "recurrence_permitted": False,
        "post_terminal_revival_permitted": False,
        "permanent_exhaustion_required": True,
        "founder_post_founding_special_authority": False,
        "ordinary_post_founding_governance_only": True,
        "production_paths": 1,
        "parallel_production_paths": 0,
        "persistent_founding_paths": 0,
        "immediate_effect_ceiling": "EXTERNAL_CONSTITUENT_ADOPTION_RECORDED_ONLY",
        "publication_authorized": False,
        "normative_activation_authorized": False,
        "g69_cdp_authorized": False,
        "implementation_authorized": False,
        "candidate_h_instantiation_authorized": False,
        "begin_authorized": False,
        "clia_validation_authorized": False,
        "deployment_authorized": False,
        "production_authorized": False,
        "predecessor_finality_slot_status": "OPEN",
        "finality_sequence": 1,
        "finality_required": True,
        "non_equivocation_required": True,
        "exhaustion_evidence_required": True,
    },
    allowed_values={"disposition": frozenset({"ADOPT_EXACT_TARGET", "REFUSE_EXACT_TARGET"})},
)

HFD_REVIEW_FIELDS = _names("""
review_artifact_type review_artifact_version review_contract_source_identity
review_contract_source_digest canonical_act_identity canonical_act_digest
reviewed_field_count reviewed_field_names reviewed_field_name_root reviewed_act_payload
reviewed_payload_digest reviewed_semantic_root review_completeness display_contract metadata
""")
_define(
    "HumanFounderActReviewProjectionV2",
    HFD_REVIEW_FIELDS,
    constants={
        "review_artifact_type": "HUMAN_FOUNDER_ACT_REVIEW_PROJECTION",
        "review_artifact_version": "V2",
        "reviewed_field_count": 77,
        "review_completeness": "COMPLETE_EXACT_NESTED_PAYLOAD",
        "display_contract": "EXACT_CJ1_UTF8_BYTE_VIEW",
        "metadata": {},
    },
)

HFD_MANIFEST_FIELDS = _names("""
manifest_artifact_type manifest_artifact_version protocol_source_identity protocol_source_digest
producing_external_capacity_identity producing_external_capacity_digest external_premise_identity
external_premise_digest source_commitment_identity source_commitment_digest
instrument_commitment_v3_identity instrument_commitment_v3_digest universe_identity universe_digest
census_identity census_digest source_evidence_identity source_evidence_digest
recognition_proof_identity recognition_proof_digest normative_successor_payload_identity
normative_successor_payload_digest target_v5_identity target_v5_digest instrument_v4_identity
instrument_v4_digest authority_scope_identity authority_scope_digest validation_schema_identity
validation_schema_digest target_disposition_domain_identity target_disposition_domain_digest
target_disposition_slot_identity target_disposition_epoch human_finality_domain_identity
human_finality_domain_digest human_decision_slot_identity human_decision_epoch
candidate_h_contract_lineage candidate_h_contract_lineage_count candidate_h_contract_lineage_root
mapping_contract metadata
""")
_define(
    "CandidateHInputReferenceManifestV2",
    HFD_MANIFEST_FIELDS,
    constants={
        "manifest_artifact_type": "HUMAN_FOUNDER_CANDIDATE_H_INPUT_REFERENCE_MANIFEST",
        "manifest_artifact_version": "V2",
        "candidate_h_contract_lineage_count": 7,
        "mapping_contract": "DIRECT_RETAINED_PAIR_OR_EXACT_PROJECTION_V2",
        "metadata": {},
    },
)

HFD_AUTH_COMMITMENT_FIELDS = _names("""
authentication_commitment_type authentication_commitment_version authentication_domain_identity
authentication_domain_digest canonical_act_identity canonical_act_digest review_projection_identity
review_projection_digest candidate_common_base_digest candidate_h_input_reference_manifest_identity
candidate_h_input_reference_manifest_digest human_founder_external_capacity_reference_identity
human_founder_external_capacity_reference_digest external_authority_evidence_manifest_identity
external_authority_evidence_manifest_digest authority_provenance_evidence_identity
authority_provenance_evidence_digest authority_competence_evidence_identity
authority_competence_evidence_digest human_finality_domain_identity human_finality_domain_digest
human_finality_slot_identity human_finality_epoch finality_sequence permanent_exhaustion_required
""")
_define(
    "HumanFounderAuthenticationCommitmentV2",
    HFD_AUTH_COMMITMENT_FIELDS,
    constants={
        "authentication_commitment_type": "HUMAN_FOUNDER_EXTERNAL_CONSTITUENT_ACT_AUTHENTICATION_COMMITMENT",
        "authentication_commitment_version": "V2",
        "finality_sequence": 1,
        "permanent_exhaustion_required": True,
    },
)

HFD_EXHAUSTION_FIELDS = _names("""
exhaustion_artifact_type exhaustion_artifact_version protocol_source_identity protocol_source_digest
canonical_act_identity canonical_act_digest review_projection_identity review_projection_digest
authentication_commitment_identity authentication_commitment_digest authentication_evidence_identity
authentication_evidence_digest candidate_h_input_reference_manifest_identity
candidate_h_input_reference_manifest_digest candidate_h_human_decision_identity
candidate_h_human_decision_digest candidate_h_human_finality_identity candidate_h_human_finality_digest
human_finality_domain_identity human_finality_domain_digest human_finality_slot_identity
human_finality_epoch finality_sequence finality_operation_identity finality_operation_digest
non_equivocation_proof_identity non_equivocation_proof_digest finality_domain_cas_identity
finality_domain_cas_digest read_back_finality_slot_digest final_disposition founding_target_identity
founding_target_digest human_founder_external_capacity_reference_identity
human_founder_external_capacity_reference_digest authoritative_disposition_count authority_status
delegation_permitted transfer_permitted reset_permitted reissue_permitted recurrence_permitted
revival_permitted post_founding_special_authority ordinary_post_founding_governance_only exhausted_at metadata
""")
_define(
    "HumanFounderOneShotExhaustionEvidenceV2",
    HFD_EXHAUSTION_FIELDS,
    constants={
        "exhaustion_artifact_type": "HUMAN_FOUNDER_ONE_SHOT_EXHAUSTION_EVIDENCE",
        "exhaustion_artifact_version": "V2",
        "finality_sequence": 1,
        "authoritative_disposition_count": 1,
        "authority_status": "PERMANENTLY_EXHAUSTED",
        "delegation_permitted": False,
        "transfer_permitted": False,
        "reset_permitted": False,
        "reissue_permitted": False,
        "recurrence_permitted": False,
        "revival_permitted": False,
        "post_founding_special_authority": False,
        "ordinary_post_founding_governance_only": True,
        "metadata": {},
    },
)


# G77-73 authenticated capacity and durable authentication result.
CAPACITY_V2_SEMANTIC_FIELDS = _names("""
external_premise_identity external_premise_digest external_constituent_model_identity
human_actor_identity_record external_capacity_record authority_provenance_record
authority_competence_record one_shot_scope_record authentication_key_binding_record
authentication_verification_profile capacity_status_read_back_record target_identity target_digest
human_finality_domain_identity human_finality_domain_digest human_authentication_slot_identity
human_authentication_epoch human_decision_slot_identity human_decision_epoch
maximum_authoritative_dispositions maximum_human_reviews maximum_authentication_operations
maximum_finality_events delegation_permitted transfer_permitted reset_permitted reissue_permitted
recurrence_permitted revival_permitted post_founding_special_authority
ordinary_post_founding_governance_only issued_at capacity_issuance_authentication_record
capacity_issuance_custody_read_back_record
""")
_define(
    "HumanFounderExternalCapacityEvidenceV2",
    _enveloped(CAPACITY_V2_SEMANTIC_FIELDS),
    semantic_fields=CAPACITY_V2_SEMANTIC_FIELDS,
    constants={
        "artifact_type": "HumanFounderExternalCapacityEvidence",
        "artifact_version": "V2",
        "contract_version": AUTHENTICATION_CONTRACT_VERSION,
        "external_constituent_model_identity": "HUMAN_FOUNDER_ONE_SHOT_EXTERNAL_CONSTITUENT_V1",
        "maximum_authoritative_dispositions": 1,
        "maximum_human_reviews": 1,
        "maximum_authentication_operations": 1,
        "maximum_finality_events": 1,
        "delegation_permitted": False,
        "transfer_permitted": False,
        "reset_permitted": False,
        "reissue_permitted": False,
        "recurrence_permitted": False,
        "revival_permitted": False,
        "post_founding_special_authority": False,
        "ordinary_post_founding_governance_only": True,
        "metadata": {},
    },
)

AUTH_RESULT_V2_SEMANTIC_FIELDS = _names("""
external_premise_identity external_premise_digest human_founder_capacity_identity
human_founder_capacity_digest human_actor_identity human_authentication_slot_identity
human_authentication_epoch authentication_sequence authentication_operation_identity
authentication_operation_digest authentication_commitment_identity authentication_commitment_digest
authenticated_message_representation authenticated_message_digest signature_scheme
signature_key_identity signature authentication_result predecessor_authentication_slot_status
claimed_authentication_slot_status terminal_authentication_slot_status authentication_claim_cas_identity
authentication_claim_cas_digest signer_operation_slot_identity signer_operation_slot_epoch
signer_invocation_intent_identity signer_invocation_intent_digest signer_acceptance_cas_identity
signer_acceptance_cas_digest signer_invocation_receipt_identity signer_invocation_receipt_digest
signer_outcome_identity signer_outcome_digest signer_outcome_read_back_identity
signer_outcome_read_back_digest signer_outcome_status one_use_non_equivocation_proof_identity
one_use_non_equivocation_proof_digest authentication_terminal_cas_identity
authentication_terminal_cas_digest authoritative_read_back_identity authoritative_read_back_digest
read_back_authentication_slot_digest signature_verification_result conflict_status retry_permitted
second_authentication_permitted capacity_permanently_exhausted completion_logical_instant terminal
""")
_define(
    "HumanFounderAuthenticationResultReadBackEvidenceV2",
    _enveloped(AUTH_RESULT_V2_SEMANTIC_FIELDS),
    semantic_fields=AUTH_RESULT_V2_SEMANTIC_FIELDS,
    constants={
        "artifact_type": "HumanFounderAuthenticationResultReadBackEvidence",
        "artifact_version": "V2",
        "contract_version": AUTHENTICATION_CONTRACT_VERSION,
        "authentication_sequence": 1,
        "authenticated_message_representation": "EXACT_UTF8_CJ1_P_AUTH_V2_BYTES",
        "signature_scheme": "ED25519_RFC8032_PURE",
        "predecessor_authentication_slot_status": "OPEN",
        "claimed_authentication_slot_status": "AUTHENTICATING",
        "retry_permitted": False,
        "second_authentication_permitted": False,
        "capacity_permanently_exhausted": True,
        "terminal": True,
        "metadata": {},
    },
    allowed_values={
        "authentication_result": frozenset(
            {
                "AUTHENTICATED_VALID",
                "AUTHENTICATION_REJECTED_FINAL",
                "INDETERMINATE_NO_VALID_RESULT",
            }
        )
    },
)

HUMAN_DECISION_V2_SEMANTIC_FIELDS = _names("""
universe_identity universe_digest source_identity source_digest instrument_identity instrument_digest
target_identity target_digest human_custody_owner_identity human_actor_identity
human_founder_external_capacity_evidence_identity human_founder_external_capacity_evidence_digest
human_finality_domain_identity human_finality_domain_digest human_decision_slot_identity
human_decision_epoch human_decision_sequence decision supersession_permitted
predecessor_finality_slot_status human_confirmation_identity human_confirmation_digest
authentication_commitment_identity authentication_commitment_digest
authentication_result_read_back_identity authentication_result_read_back_digest
authenticated_message_representation human_signature_scheme human_signature_key_identity
human_signature decision_effective_at
""")
_define(
    "ExternalConstituentHumanFirstAdoptionDecisionV2",
    _enveloped(HUMAN_DECISION_V2_SEMANTIC_FIELDS),
    semantic_fields=HUMAN_DECISION_V2_SEMANTIC_FIELDS,
    constants={
        "artifact_type": "ExternalConstituentHumanFirstAdoptionDecision",
        "artifact_version": "V2",
        "contract_version": AUTHENTICATION_CONTRACT_VERSION,
        "producing_owner": HUMAN_AUTHORITY,
        "human_custody_owner_identity": HUMAN_AUTHORITY,
        "human_decision_sequence": 1,
        "supersession_permitted": False,
        "predecessor_finality_slot_status": "OPEN",
        "authenticated_message_representation": "EXACT_UTF8_CJ1_P_AUTH_V2_BYTES",
        "human_signature_scheme": "ED25519_RFC8032_PURE",
        "metadata": {},
    },
    allowed_values={"decision": frozenset({"ADOPT_EXACT_TARGET", "REFUSE_EXACT_TARGET"})},
)


# Exact G77-62 successor schemas.  Each entry declares its artifact-specific
# identity/digest envelope names, conceptual semantic order, version, and
# content-identity domain prefixes.
G77_62_MODEL_SPECS: dict[str, dict[str, object]] = {}


def _g77_model(
    name: str,
    identity_field: str,
    digest_field: str,
    version: str,
    identity_prefix: str,
    idempotency_prefix: str,
    semantic_fields: tuple[str, ...],
    *,
    constants: dict[str, object] | None = None,
    allowed_values: dict[str, frozenset[object]] | None = None,
    required_null_fields: frozenset[str] = frozenset(),
) -> None:
    complete = (
        "artifact_type",
        "artifact_version",
        identity_field,
        digest_field,
        "contract_version",
        "idempotency_identity",
        "producing_owner",
    ) + semantic_fields + ("metadata",)
    fixed = {"artifact_type": name.removesuffix(version), "artifact_version": version, "metadata": {}}
    fixed.update(constants or {})
    cls = _define(
        name,
        complete,
        semantic_fields=semantic_fields,
        constants=fixed,
        allowed_values=allowed_values,
        required_null_fields=required_null_fields,
    )
    spec = MappingProxyType(
        {
            "artifact_type": fixed["artifact_type"],
            "artifact_version": version,
            "identity_field": identity_field,
            "digest_field": digest_field,
            "identity_prefix": identity_prefix,
            "idempotency_prefix": idempotency_prefix,
            "semantic_fields": semantic_fields,
        }
    )
    cls.MODEL_SPEC = spec
    G77_62_MODEL_SPECS[name] = spec


_g77_model(
    "ConstitutionalMetaRepairInitialAdoptionTargetV5", "target_identity", "target_digest", "V5",
    "founding-target-v5", "founding-target-idem-v5", _names("""
g77_36_identity g77_36_digest g77_37_identity g77_37_digest g77_38_identity g77_38_digest
g77_39_identity g77_39_digest g77_44_identity g77_44_digest g77_45_identity g77_45_digest
g77_45_assessment_classification historical_target_v3_status g77_52_identity g77_52_digest
g77_53_identity g77_53_digest g77_53_assessment_classification g77_57_identity g77_57_digest
g77_57_audit_classification g77_58_identity g77_58_digest g77_59_identity g77_59_digest
g77_59_assessment_classification g77_60_identity g77_60_digest g77_61_identity g77_61_digest
g77_61_assessment_classification g77_62_identity g77_62_digest g77_62_assessment_identity
g77_62_assessment_digest g77_62_assessment_classification founding_event_origin_root_pointer_identity
founding_event_origin_root_pointer_digest founding_event_origin_root_identity
founding_event_origin_root_digest founding_event_origin_root_generation
founding_event_origin_constitutional_state_identity founding_event_origin_constitutional_state_digest
founding_event_origin_active_constitution_identity founding_event_origin_active_constitution_digest
normative_successor_payload_identity normative_successor_payload_digest founding_scope_identity
founding_scope_digest root_binding_mode required_successor_meta_repair_status required_successor_cap_status
required_topology_tuple required_successor_root_contract required_success_contract
required_attempt_terminal_contract
"""),
)

_g77_model(
    "ExternalConstituentInstrumentCommitmentV3", "instrument_commitment_identity",
    "instrument_commitment_digest", "V3", "external-instrument-commitment-v3",
    "external-instrument-commitment-idem-v3", _names("""
premise_identity premise_digest source_commitment_identity source_commitment_digest
instrument_subject_identity target_identity target_digest g77_44_identity g77_44_digest
g77_45_identity g77_45_digest g77_45_assessment_classification historical_instrument_v2_status
g77_62_identity g77_62_digest g77_62_assessment_identity g77_62_assessment_digest
g77_62_assessment_classification instrument_sequence maximum_successful_effects reissuance_permitted
reset_permitted target_substitution_permitted human_finality_domain_identity human_finality_domain_digest
human_decision_slot_identity human_decision_epoch target_disposition_domain_identity
target_disposition_domain_digest status_linearization_mode verification_owner root_effect_owner
root_serialization_domain_identity authority_scope_identity authority_scope_digest status_epoch
not_before expires_at revocation_status signature_scheme signature_key_identity signature issued_at
"""),
)

_g77_model(
    "ExternalConstituentOneShotFoundingInstrumentV4", "instrument_identity", "instrument_digest", "V4",
    "founding-instrument-v4", "founding-instrument-idem-v4", _names("""
universe_identity universe_digest census_identity census_digest instrument_commitment_identity
instrument_commitment_digest source_evidence_identity source_evidence_digest recognition_proof_identity
recognition_proof_digest target_identity target_digest g77_44_identity g77_44_digest g77_45_identity
g77_45_digest g77_45_assessment_classification historical_instrument_v3_status g77_62_identity
g77_62_digest g77_62_assessment_identity g77_62_assessment_digest g77_62_assessment_classification
instrument_sequence maximum_successful_effects reissuance_permitted reset_permitted
target_substitution_permitted human_finality_domain_identity human_finality_domain_digest
human_decision_slot_identity human_decision_epoch target_disposition_domain_identity
target_disposition_domain_digest status_linearization_mode verification_owner root_effect_owner
root_serialization_domain_identity terminal_state_vocabulary authority_scope_identity
authority_scope_digest status_epoch not_before expires_at revocation_status signature_scheme
signature_key_identity signature issued_at
"""),
)

PROOF_SET_V3_FIELDS = _names("""
universe_identity universe_digest census_identity census_digest source_evidence_identity
source_evidence_digest recognition_proof_identity recognition_proof_digest target_identity target_digest
normative_successor_payload_identity normative_successor_payload_digest instrument_identity
instrument_digest human_decision_identity human_decision_digest human_finality_identity
human_finality_digest decision_disposition_evidence_identity decision_disposition_evidence_digest
consuming_disposition_identity consuming_disposition_digest founding_event_identity attempt_identity
attempt_sequence attempt_kind predecessor_attempt_identity predecessor_attempt_terminal_read_back_identity
predecessor_attempt_terminal_read_back_digest predecessor_abandoned_commitment_identity
predecessor_abandoned_commitment_digest current_root_pointer_identity current_root_pointer_digest
current_root_identity current_root_digest current_root_generation current_constitutional_state_identity
current_constitutional_state_digest ordered_predicate_results predicate_count predicate_root
eligible_source_count eligible_instrument_count proof_result
""")
_g77_model(
    "ExternalConstituentFoundingEligibilityProofSetV3", "proof_set_identity", "proof_set_digest", "V3",
    "founding-proofset-v3", "founding-proofset-idem-v3", PROOF_SET_V3_FIELDS,
    constants={"contract_version": AUTHENTICATION_CONTRACT_VERSION, "predicate_count": 20,
               "eligible_source_count": 1, "eligible_instrument_count": 1},
)

CERTIFICATION_V3_FIELDS = _names("""
proof_set_identity proof_set_digest universe_identity universe_digest target_identity target_digest
instrument_identity instrument_digest human_finality_identity human_finality_digest
decision_disposition_evidence_identity decision_disposition_evidence_digest consuming_disposition_identity
consuming_disposition_digest founding_event_identity attempt_identity attempt_sequence attempt_kind
predecessor_attempt_terminal_read_back_identity predecessor_attempt_terminal_read_back_digest
current_root_pointer_identity current_root_pointer_digest current_root_identity current_root_digest
current_root_generation predicate_count predicate_root certification_result certified_at
""")
_g77_model(
    "ExternalConstituentFoundingEligibilityCertificationV3", "certification_identity",
    "certification_digest", "V3", "founding-certification-v3", "founding-certification-idem-v3",
    CERTIFICATION_V3_FIELDS,
    constants={"contract_version": AUTHENTICATION_CONTRACT_VERSION, "predicate_count": 20},
)

TRANSITION_V3_FIELDS = _names("""
certification_identity certification_digest proof_set_identity proof_set_digest universe_identity
universe_digest target_identity target_digest normative_successor_payload_identity
normative_successor_payload_digest instrument_identity instrument_digest human_decision_identity
human_decision_digest human_finality_identity human_finality_digest decision_disposition_evidence_identity
decision_disposition_evidence_digest consuming_disposition_identity consuming_disposition_digest
founding_event_identity attempt_identity attempt_sequence attempt_kind predecessor_attempt_identity
predecessor_attempt_terminal_read_back_identity predecessor_attempt_terminal_read_back_digest
predecessor_abandoned_commitment_identity predecessor_abandoned_commitment_digest
predecessor_root_pointer_identity predecessor_root_pointer_digest predecessor_root_identity
predecessor_root_digest predecessor_root_generation predecessor_constitutional_state_identity
predecessor_constitutional_state_digest reserved_successor_root_generation
reserved_successor_meta_repair_status reserved_successor_cap_status reserved_dormancy_status
begin_transition_mode root_effect_owner effective_at
""")
_g77_model(
    "ExternalConstituentFoundingAdoptionTransitionV3", "transition_identity", "transition_digest", "V3",
    "founding-transition-v3", "founding-transition-idem-v3", TRANSITION_V3_FIELDS,
    constants={"contract_version": AUTHENTICATION_CONTRACT_VERSION},
)

_g77_model(
    "ConstitutionalExistingOrdinaryRepairChainCensusV2", "ordinary_chain_census_identity",
    "ordinary_chain_census_digest", "V2", "ordinary-chain-census-v2", "ordinary-chain-census-idem-v2",
    _names("""
route_census_kind authority_manifest_identity authority_manifest_digest coverage_proof_identity
coverage_proof_digest active_baseline_identity active_baseline_digest target_artifact_type
target_artifact_version target_constitutional_contract_identity target_constitutional_contract_digest
included_route_categories ordered_route_entry_count ordered_route_entries_root ordered_route_entries_digest
applicable_route_count applicable_routes_root ordered_g70_chain_results g70_chain_result_count
g70_machine_evidence_registry_identity g70_machine_evidence_registry_digest
g70_machine_evidence_registry_root g70_machine_evidence_registry_epoch route_exists
alternative_constituent_route_count alternative_constituent_route_exists derived_at
"""),
)

_g77_model(
    "OrdinaryCAPReachabilityStateV2", "reachability_state_identity", "reachability_state_digest", "V2",
    "ordinary-cap-reachability-v2", "ordinary-cap-reachability-idem-v2", _names("""
predecessor_reachability_state_identity predecessor_reachability_state_digest reachability_epoch
active_baseline_identity active_baseline_digest active_baseline_pointer_identity
active_baseline_pointer_digest authority_manifest_identity authority_manifest_digest
cap_contract_set_identity cap_contract_set_digest cap_entry_contract_identity cap_entry_contract_digest
cap_entry_required_predecessor_set_identity cap_entry_required_predecessor_set_digest
cap_entry_evidence_registry_identity cap_entry_evidence_registry_digest cap_entry_reachability
unreachable_requirement_identity unreachable_requirement_digest exact_target_artifact_type
exact_target_artifact_version exact_target_identity exact_target_digest
ordinary_chain_census_artifact_version ordinary_chain_census_identity ordinary_chain_census_digest
exact_target_chain_status computed_at committed_at
"""),
)

_g77_model(
    "CandidateHOneShotDormancyRebaseGuardV2", "guard_identity", "guard_digest", "V2",
    "candidate-h-dormancy-rebase-guard-v2", "candidate-h-dormancy-rebase-guard-idem-v2", _names("""
candidate_h_founding_transition_identity candidate_h_founding_transition_digest
external_consuming_disposition_identity external_consuming_disposition_digest
external_status_snapshot_identity external_status_snapshot_digest external_status_version_fence_identity
external_status_version_fence_digest external_target_disposition_pointer_identity
external_target_disposition_pointer_digest expected_consuming_slot_digest expected_consuming_slot_generation
founding_event_identity attempt_identity attempt_sequence attempt_kind one_shot_lifecycle_predecessor_status
one_shot_lifecycle_terminal_status allocated_root_identity allocated_root_digest allocation_root_generation
token_identity token_digest token_ordinal operation_kind operation_idempotency_identity
successor_baseline_identity successor_baseline_digest successor_logical_pointer_identity
successor_logical_pointer_digest successor_cap_state_identity successor_cap_state_digest
candidate_h_target_identity candidate_h_target_digest reserved_successor_meta_repair_status
terminal_commitment_contract_identity terminal_commitment_contract_version terminal_eligibility_rule guarded_at
"""),
)

_g77_model(
    "ConstitutionalMetaRepairTransitionV3", "meta_repair_transition_identity",
    "meta_repair_transition_digest", "V3", "meta-repair-transition-v3", "meta-repair-transition-idem-v3",
    _names("""
transition_kind predecessor_current_pointer_identity predecessor_current_pointer_digest
predecessor_state_identity predecessor_state_digest reserved_successor_status repair_identity
active_baseline_identity active_baseline_digest target_constitutional_contract_identity
target_constitutional_contract_digest cap_reachability_current_pointer_identity
cap_reachability_current_pointer_digest cap_reachability_state_identity cap_reachability_state_digest
reachability_epoch authorizing_artifact_type authorizing_artifact_version authorizing_artifact_identity
authorizing_artifact_digest founding_event_identity attempt_identity attempt_sequence
candidate_h_founding_transition_identity candidate_h_founding_transition_digest transition_prepared_at
"""), required_null_fields=frozenset({"repair_identity"}),
)

_g77_model(
    "ConstitutionalMetaRepairStateV3", "meta_repair_state_identity", "meta_repair_state_digest", "V3",
    "meta-repair-state-v3", "meta-repair-state-idem-v3", _names("""
predecessor_meta_repair_state_identity predecessor_meta_repair_state_digest state_status repair_epoch
repair_identity active_baseline_identity active_baseline_digest target_constitutional_contract_identity
target_constitutional_contract_digest cap_reachability_state_identity cap_reachability_state_digest
reachability_epoch liveness_failure_proof_identity liveness_failure_proof_digest
proof_issuance_slot_state_identity proof_issuance_slot_state_digest repair_scope_manifest_identity
repair_scope_manifest_digest normative_diff_identity normative_diff_digest independent_assessment_identity
independent_assessment_digest human_constituent_decision_identity human_constituent_decision_digest
constituent_certification_identity constituent_certification_digest transition_identity transition_digest
one_shot_dormancy_rebase_guard_identity one_shot_dormancy_rebase_guard_digest
candidate_h_founding_transition_identity candidate_h_founding_transition_digest
external_consuming_disposition_identity external_consuming_disposition_digest founding_event_identity
attempt_identity attempt_sequence effective_at
"""), required_null_fields=frozenset({
        "repair_identity", "target_constitutional_contract_identity", "target_constitutional_contract_digest",
        "liveness_failure_proof_identity", "liveness_failure_proof_digest",
        "proof_issuance_slot_state_identity", "proof_issuance_slot_state_digest",
        "repair_scope_manifest_identity", "repair_scope_manifest_digest", "normative_diff_identity",
        "normative_diff_digest", "independent_assessment_identity", "independent_assessment_digest",
        "human_constituent_decision_identity", "human_constituent_decision_digest",
        "constituent_certification_identity", "constituent_certification_digest",
    }),
)

TERMINAL_COMMITMENT_V3_FIELDS = _names("""
commitment_contract_identity commitment_contract_version root_artifact_type root_artifact_version
canonical_serialization_version transaction_domain_identity predecessor_snapshot_pointer_identity
predecessor_snapshot_pointer_digest allocated_snapshot_root_identity allocated_snapshot_root_digest
predecessor_root_generation allocation_root_generation reserved_terminal_root_generation target_identity
target_digest instrument_identity instrument_digest human_finality_identity human_finality_digest
decision_disposition_identity decision_disposition_digest consuming_disposition_identity
consuming_disposition_digest founding_event_identity attempt_identity attempt_sequence attempt_kind
predecessor_attempt_identity predecessor_attempt_terminal_read_back_identity
predecessor_attempt_terminal_read_back_digest candidate_h_founding_transition_identity
candidate_h_founding_transition_digest operation_seed_identity operation_seed_digest operation_kind
operation_idempotency_identity token_identity token_digest token_ordinal token_owner_identity
expected_successor_component_mask successor_active_baseline_identity successor_active_baseline_digest
successor_logical_active_baseline_pointer_identity successor_logical_active_baseline_pointer_digest
successor_meta_repair_state_identity successor_meta_repair_state_digest
successor_cap_reachability_state_identity successor_cap_reachability_state_digest
successor_normative_registry_identity successor_normative_registry_digest successor_normative_registry_root
successor_normative_registry_entry_count successor_authority_projection_identity
successor_authority_projection_digest successor_authority_manifest_identity
successor_authority_manifest_digest successor_source_evidence_registry_identity
successor_source_evidence_registry_digest successor_source_evidence_registry_root
successor_source_evidence_registry_epoch successor_proof_slot_map_state_identity
successor_proof_slot_map_state_digest one_shot_dormancy_rebase_guard_identity
one_shot_dormancy_rebase_guard_digest meta_repair_transition_identity meta_repair_transition_digest
terminal_failure_evidence_identity terminal_failure_evidence_digest terminal_logical_instant
expected_terminal_result
""")
_g77_model(
    "ConstitutionalTerminalRootSemanticImageCommitmentV3", "terminal_root_commitment_identity",
    "terminal_root_commitment_digest", "V3", "terminal-root-image-v3", "terminal-root-image-idem-v3",
    TERMINAL_COMMITMENT_V3_FIELDS,
)

COORDINATOR_STATE_V4_FIELDS = _names("""
predecessor_coordinator_state_identity predecessor_coordinator_state_digest allocation_intent_identity
allocation_intent_digest consume_intent_identity consume_intent_digest coordinator_status token_ordinal
next_token_ordinal current_token_identity current_token_digest owning_operation_seed_identity
owning_operation_seed_digest owning_operation_kind owning_operation_idempotency_identity
token_owner_identity allocation_logical_instant allocation_snapshot_root_identity
allocation_snapshot_root_digest allocation_root_generation terminal_snapshot_root_identity
terminal_snapshot_root_digest terminal_root_commitment_artifact_version terminal_root_commitment_identity
terminal_root_commitment_digest founding_event_identity attempt_identity attempt_sequence attempt_kind
predecessor_attempt_identity predecessor_attempt_terminal_read_back_identity
predecessor_attempt_terminal_read_back_digest terminal_root_generation terminal_result
terminal_failure_evidence_identity terminal_failure_evidence_digest terminal_logical_instant
""")
_g77_model(
    "ConstitutionalRootSerializationCoordinatorStateV4", "coordinator_state_identity",
    "coordinator_state_digest", "V4", "root-coordinator-state-v4", "root-coordinator-state-idem-v4",
    COORDINATOR_STATE_V4_FIELDS,
)

ROOT_SNAPSHOT_V4_FIELDS = _names("""
transaction_domain_identity predecessor_snapshot_pointer_identity predecessor_snapshot_pointer_digest
predecessor_snapshot_root_identity predecessor_snapshot_root_digest predecessor_root_generation
root_generation canonical_serialization_version active_baseline_identity active_baseline_digest
logical_active_baseline_pointer_identity logical_active_baseline_pointer_digest meta_repair_state_identity
meta_repair_state_digest cap_reachability_state_identity cap_reachability_state_digest
normative_registry_identity normative_registry_digest normative_registry_root normative_registry_entry_count
authority_projection_identity authority_projection_digest authority_manifest_identity
authority_manifest_digest source_evidence_registry_identity source_evidence_registry_digest
source_evidence_registry_root source_evidence_registry_epoch proof_slot_map_state_identity
proof_slot_map_state_digest serialization_coordinator_state_identity serialization_coordinator_state_digest
root_state_idempotency_identity effective_logical_instant
""")
_g77_model(
    "ConstitutionalRootEvolutionSnapshotV4", "root_identity", "root_digest", "V4",
    "constitutional-root-v4", "constitutional-root-idem-v4", ROOT_SNAPSHOT_V4_FIELDS,
)

ATTEMPT_TERMINAL_READ_BACK_V1_FIELDS = _names("""
target_identity target_digest instrument_identity instrument_digest human_finality_identity
human_finality_digest decision_disposition_identity decision_disposition_digest
consuming_disposition_identity consuming_disposition_digest founding_event_identity attempt_identity
attempt_sequence attempt_kind predecessor_attempt_identity predecessor_attempt_terminal_read_back_identity
predecessor_attempt_terminal_read_back_digest candidate_h_founding_transition_identity
candidate_h_founding_transition_digest terminal_root_commitment_identity terminal_root_commitment_digest
terminal_coordinator_state_identity terminal_coordinator_state_digest resulting_root_identity
resulting_root_digest resulting_root_generation root_snapshot_cas_intent_identity
root_snapshot_cas_intent_digest root_snapshot_cas_identity root_snapshot_cas_digest
root_commit_marker_identity root_commit_marker_digest root_read_back_identity root_read_back_digest
read_back_current_root_identity read_back_current_root_digest read_back_current_root_generation
terminal_result terminal_failure_evidence_identity terminal_failure_evidence_digest next_attempt_sequence
next_token_ordinal terminal_logical_instant read_back_result
""")
_g77_model(
    "CandidateHFoundingAttemptTerminalReadBackV1", "attempt_terminal_read_back_identity",
    "attempt_terminal_read_back_digest", "V1", "candidate-h-attempt-terminal-readback-v1",
    "candidate-h-attempt-terminal-readback-idem-v1", ATTEMPT_TERMINAL_READ_BACK_V1_FIELDS,
    constants={"read_back_result": "EXACT_ATTEMPT_TERMINAL_ROOT_CURRENT"},
    allowed_values={"terminal_result": frozenset({"CONSUMED", "ABANDONED"})},
)


# Closed nested G77-71/73 record schemas.  These records are embedded values,
# not separately addressable artifact families.
NESTED_RECORD_SCHEMAS = MappingProxyType(
    {
        "HumanFounderActorIdentityRecordV1": _names("record_type record_version producing_owner human_actor_identity human_actor_identity_scheme subject_kind identity_assurance_profile identity_evidence_payload identity_evidence_payload_digest issued_at record_digest"),
        "HumanFounderExternalCapacityRecordV1": _names("record_type record_version producing_owner external_capacity_identity external_capacity_digest human_actor_identity external_premise_identity external_premise_digest external_constituent_model_identity target_identity target_digest scope_digest capacity_kind capacity_origin issued_at record_digest"),
        "HumanFounderAuthorityProvenanceRecordV1": _names("record_type record_version producing_owner external_premise_identity external_premise_digest human_actor_identity external_capacity_identity external_capacity_digest ordered_predecessor_rows predecessor_count predecessor_root anti_self_authorization_result forbidden_dependency_count record_digest"),
        "HumanFounderAuthorityCompetenceRecordV1": _names("record_type record_version producing_owner human_actor_identity external_capacity_identity external_capacity_digest target_identity target_digest scope_digest competence_kind competence_result maximum_successful_effects ordinary_post_founding_authority record_digest"),
        "HumanFounderOneShotScopeRecordV1": _names("record_type record_version producing_owner target_identity target_digest maximum_dispositions maximum_reviews maximum_authentication_operations maximum_finality_events maximum_successful_effects delegation_permitted transfer_permitted reset_permitted reissue_permitted recurrence_permitted revival_permitted record_digest"),
        "HumanFounderAuthenticationKeyBindingRecordV1": _names("record_type record_version producing_owner human_actor_identity external_capacity_identity external_capacity_digest authentication_algorithm public_key_encoding authentication_public_key authentication_key_identity binding_method binding_result record_digest"),
        "HumanFounderAuthenticationVerificationProfileV1": _names("record_type record_version producing_owner algorithm_identifier algorithm_specification public_key_encoding signature_encoding message_representation digest_before_signature context_string prehash_mode key_identity_prefix trust_anchor_mode trust_anchor_digest domain_identity malformed_input_result unknown_algorithm_result noncanonical_encoding_result verification_true_result verification_false_result record_digest"),
        "HumanFounderCapacityStatusReadBackRecordV1": _names("record_type record_version producing_owner external_capacity_identity external_capacity_digest status_authority_identity status_slot_identity status_epoch status_generation predecessor_status current_status status_cas_identity status_cas_digest authoritative_read_back_identity authoritative_read_back_digest read_back_status_digest status_effective_logical_instant read_back_result record_digest"),
        "HumanFounderCapacityIssuanceAuthenticationRecordV1": _names("record_type record_version producing_owner external_premise_identity external_premise_digest capacity_issuer_identity capacity_issuer_identity_scheme capacity_issuance_commitment_identity capacity_issuance_commitment_digest authenticated_message_representation authentication_algorithm public_key_encoding capacity_issuer_public_key capacity_issuer_key_identity signature_encoding capacity_issuer_signature premise_owner_trust_binding_digest signature_verification_result issued_at record_digest"),
        "HumanFounderCapacityIssuanceCustodyReadBackRecordV1": _names("record_type record_version producing_owner external_premise_identity external_premise_digest capacity_issuance_commitment_identity capacity_issuance_commitment_digest capacity_issuance_authentication_record_digest capacity_issuer_signature_digest capacity_issuance_slot_identity capacity_issuance_epoch capacity_issuance_generation predecessor_issuance_status current_issuance_status capacity_issuance_cas_identity capacity_issuance_cas_digest capacity_issuance_read_back_identity capacity_issuance_read_back_digest stored_core_digest stored_authentication_record_digest issuance_logical_instant read_back_result record_digest"),
    }
)
for _record_name, _record_fields in NESTED_RECORD_SCHEMAS.items():
    _define(_record_name, _record_fields)


MODEL_OWNER_RULES = {
    "HumanFounderExternalCapacityEvidenceV2": "RESOLVED_EXTERNAL_PREMISE_AUTHORITY",
    "HumanFounderAuthenticationResultReadBackEvidenceV2": "RESOLVED_EXTERNAL_PREMISE_AUTHORITY",
    "ExternalConstituentHumanFirstAdoptionDecisionV2": HUMAN_AUTHORITY,
    "ConstitutionalMetaRepairInitialAdoptionTargetV5": "CONSTITUTIONAL_ROOT_SERIALIZATION_CUSTODIAN",
    "ExternalConstituentInstrumentCommitmentV3": "EXACT_EXTERNAL_SOURCE",
    "ExternalConstituentOneShotFoundingInstrumentV4": "EXTERNAL_UNIVERSE_CUSTODIAN",
    "ExternalConstituentFoundingEligibilityProofSetV3": "CONSTITUTIONAL_CERTIFICATION_OWNER",
    "ExternalConstituentFoundingEligibilityCertificationV3": "CONSTITUTIONAL_CERTIFICATION_OWNER",
    "ExternalConstituentFoundingAdoptionTransitionV3": "CONSTITUTIONAL_ROOT_SERIALIZATION_CUSTODIAN",
    "ConstitutionalExistingOrdinaryRepairChainCensusV2": "CONSTITUTIONAL_GOVERNANCE_OWNER",
    "OrdinaryCAPReachabilityStateV2": "CONSTITUTIONAL_GOVERNANCE_OWNER",
    "CandidateHOneShotDormancyRebaseGuardV2": "CONSTITUTIONAL_GOVERNANCE_OWNER",
    "ConstitutionalMetaRepairTransitionV3": "CONSTITUTIONAL_GOVERNANCE_OWNER",
    "ConstitutionalMetaRepairStateV3": "CONSTITUTIONAL_GOVERNANCE_OWNER",
    "ConstitutionalTerminalRootSemanticImageCommitmentV3": "CONSTITUTIONAL_ROOT_SERIALIZATION_CUSTODIAN",
    "ConstitutionalRootSerializationCoordinatorStateV4": "CONSTITUTIONAL_ROOT_SERIALIZATION_CUSTODIAN",
    "ConstitutionalRootEvolutionSnapshotV4": "CONSTITUTIONAL_ROOT_SERIALIZATION_CUSTODIAN",
    "CandidateHFoundingAttemptTerminalReadBackV1": "CONSTITUTIONAL_ROOT_SERIALIZATION_CUSTODIAN",
}
for _record_name in NESTED_RECORD_SCHEMAS:
    MODEL_OWNER_RULES[_record_name] = "CAPACITY_PRODUCING_OWNER"
for _model_name, _owner_rule in MODEL_OWNER_RULES.items():
    MODEL_REGISTRY[_model_name].OWNER_RULE = _owner_rule
    if _model_name in G77_62_MODEL_SPECS:
        _spec = dict(G77_62_MODEL_SPECS[_model_name])
        _spec["owner_rule"] = _owner_rule
        _frozen_spec = MappingProxyType(_spec)
        G77_62_MODEL_SPECS[_model_name] = _frozen_spec
        MODEL_REGISTRY[_model_name].MODEL_SPEC = _frozen_spec


MODEL_REGISTRY = MappingProxyType(dict(MODEL_REGISTRY))
G77_62_MODEL_SPECS = MappingProxyType(dict(G77_62_MODEL_SPECS))
MODEL_OWNER_RULES = MappingProxyType(dict(MODEL_OWNER_RULES))

__all__ = [
    "ATTEMPT_TERMINAL_READ_BACK_V1_FIELDS",
    "AUTHENTICATION_CONTRACT_VERSION",
    "AUTH_RESULT_V2_SEMANTIC_FIELDS",
    "CAPACITY_V2_SEMANTIC_FIELDS",
    "CanonicalModelError",
    "FrozenCanonicalModel",
    "G77_62_CONTRACT_VERSION",
    "G77_62_MODEL_SPECS",
    "HFD_ACT_FIELDS",
    "HFD_AUTH_COMMITMENT_FIELDS",
    "HFD_EXHAUSTION_FIELDS",
    "HFD_MANIFEST_FIELDS",
    "HFD_PROTOCOL_VERSION",
    "HFD_REVIEW_FIELDS",
    "HUMAN_AUTHORITY",
    "HUMAN_DECISION_V2_SEMANTIC_FIELDS",
    "MODEL_REGISTRY",
    "MODEL_OWNER_RULES",
    "NESTED_RECORD_SCHEMAS",
] + sorted(MODEL_REGISTRY)
