"""Fail-closed Candidate H Stage-2 validators and identity-DAG checks.

The module is read-only.  It derives and compares canonical identities and
validates explicit predecessor views; it does not authenticate a Human,
sign, persist, perform CAS, orchestrate, replay, invoke CRO/CLIA, or mutate a
constitutional root.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, fields
from types import MappingProxyType

from .cj1 import CJ1Error, cj1_digest, cj1_encode, cj1_identity
from .models import (
    AUTHENTICATION_CONTRACT_VERSION,
    G77_62_MODEL_SPECS,
    HFD_ACT_FIELDS,
    HUMAN_AUTHORITY,
    MODEL_OWNER_RULES,
    MODEL_REGISTRY,
    NESTED_RECORD_SCHEMAS,
    CandidateHInputReferenceManifestV2,
    ExternalConstituentFoundingEligibilityProofSetV3,
    ExternalConstituentHumanFirstAdoptionDecisionV2,
    FrozenCanonicalModel,
    HumanFounderActReviewProjectionV2,
    HumanFounderAuthenticationCommitmentV2,
    HumanFounderAuthenticationResultReadBackEvidenceV2,
    HumanFounderExternalCapacityEvidenceV2,
    HumanFounderExternalConstituentActPayloadV2,
)


class CandidateValidationError(ValueError):
    """Stable fail-closed validation failure."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}:{detail}")


@dataclass(frozen=True, slots=True)
class ArtifactIdentitySpec:
    artifact_type: str
    artifact_version: str
    identity_field: str
    digest_field: str
    identity_prefix: str
    idempotency_prefix: str


@dataclass(frozen=True, slots=True)
class EvidenceDescriptor:
    """Read-only descriptor for an already resolved external predecessor."""

    artifact_type: str
    artifact_version: str
    artifact_identity: str
    artifact_digest: str
    producing_owner: str


@dataclass(frozen=True, slots=True)
class PredecessorReference:
    """Exact predecessor pair and expected dispatch tuple."""

    artifact_type: str
    artifact_version: str
    artifact_identity: str
    artifact_digest: str


@dataclass(frozen=True, slots=True)
class IdentityDAGNode:
    """One validation-only DAG node; this is not a persisted artifact family."""

    evidence: FrozenCanonicalModel | EvidenceDescriptor
    predecessors: tuple[PredecessorReference, ...] = ()


@dataclass(frozen=True, slots=True)
class IdentityDAGValidation:
    ordered_identities: tuple[str, ...]
    node_count: int
    edge_count: int
    graph_digest: str


def _artifact_specs() -> dict[type[FrozenCanonicalModel], ArtifactIdentitySpec]:
    result: dict[type[FrozenCanonicalModel], ArtifactIdentitySpec] = {}
    for class_name, raw in G77_62_MODEL_SPECS.items():
        result[MODEL_REGISTRY[class_name]] = ArtifactIdentitySpec(
            artifact_type=str(raw["artifact_type"]),
            artifact_version=str(raw["artifact_version"]),
            identity_field=str(raw["identity_field"]),
            digest_field=str(raw["digest_field"]),
            identity_prefix=str(raw["identity_prefix"]),
            idempotency_prefix=str(raw["idempotency_prefix"]),
        )
    result[HumanFounderExternalCapacityEvidenceV2] = ArtifactIdentitySpec(
        "HumanFounderExternalCapacityEvidence",
        "V2",
        "artifact_identity",
        "artifact_digest",
        "human-founder-external-capacity-v2",
        "human-founder-external-capacity-idem-v2",
    )
    result[HumanFounderAuthenticationResultReadBackEvidenceV2] = ArtifactIdentitySpec(
        "HumanFounderAuthenticationResultReadBackEvidence",
        "V2",
        "artifact_identity",
        "artifact_digest",
        "human-founder-auth-result-readback-v2",
        "human-founder-auth-result-readback-idem-v2",
    )
    result[ExternalConstituentHumanFirstAdoptionDecisionV2] = ArtifactIdentitySpec(
        "ExternalConstituentHumanFirstAdoptionDecision",
        "V2",
        "artifact_identity",
        "artifact_digest",
        "human-founding-decision-v2",
        "human-founding-decision-idem-v2",
    )
    return result


ARTIFACT_IDENTITY_SPECS = MappingProxyType(_artifact_specs())

EXTERNAL_SCHEMA_VERSIONS = MappingProxyType(
    {
        "ExternalConstituentPremiseEvidence": frozenset({"V1"}),
        "ExternalConstituentSourceCommitment": frozenset({"V1"}),
        "ExternalConstituentAdmissibilityUniverse": frozenset({"V1"}),
        "ExternalConstituentCandidateCensus": frozenset({"V1"}),
        "ExternalConstituentAuthoritySourceEvidence": frozenset({"V1"}),
        "ExternalConstituentAuthorityRecognitionProof": frozenset({"V1"}),
        "ConstitutionalMetaRepairNormativeSuccessorPayload": frozenset({"V1"}),
        "ExternalConstituentHumanDecisionFinalityEvidence": frozenset({"V1"}),
        "ExternalConstituentOneShotInstrumentDispositionEvidence": frozenset({"V2", "V3"}),
        "HUMAN_FOUNDER_EXTERNAL_CONSTITUENT_ACT_AUTHENTICATION_COMMITMENT": frozenset({"V2"}),
        "HUMAN_FOUNDER_ACT_REVIEW_PROJECTION": frozenset({"V2"}),
    }
)

PREDICATE_CODES = (
    "P001_UNIVERSE_PREMISE_ADMISSIBLE",
    "P002_UNIVERSE_PROVENANCE_NON_CIRCULAR",
    "P003_UNIVERSE_STATUS_CURRENT",
    "P004_CENSUS_COVERAGE_COMPLETE",
    "P005_SOURCE_SINGLETON",
    "P006_INSTRUMENT_V4_SINGLETON",
    "P007_SOURCE_EVIDENCE_VALID",
    "P008_RECOGNITION_PROOF_VALID",
    "P009_TARGET_V5_EXACT",
    "P010_NORMATIVE_SUCCESSOR_EXACT",
    "P011_G77_38_FREEZE_PRESERVED",
    "P012_HUMAN_DECISION_VALID",
    "P013_HUMAN_FINALITY_NON_EQUIVOCATING",
    "P014_ATTEMPT_AUTHORIZATION_EXACT",
    "P015_ATTEMPT_PREDECESSOR_ROOT_CURRENT",
    "P016_OWNER_EFFECT_BOUNDARIES_EXACT",
    "P017_CAP_AND_META_STATUS_EXACT",
    "P018_TOPOLOGY_1_1_1_1_0",
    "P019_IDENTITY_DAG_FORWARD",
    "P020_NO_PRIOR_SUCCESS_OR_EXTERNAL_CONFLICT",
)

PREDICATE_ROW_FIELDS = (
    "rank",
    "predicate_code",
    "subject_artifact_type",
    "subject_artifact_version",
    "subject_identity",
    "subject_digest",
    "expected_digest",
    "observed_digest",
    "result",
)

NESTED_RECORD_CONSTANTS = MappingProxyType(
    {
        "HumanFounderActorIdentityRecordV1": {
            "record_type": "HUMAN_FOUNDER_ACTOR_IDENTITY_RECORD",
            "record_version": "V1",
            "subject_kind": "HUMAN_NATURAL_PERSON",
            "identity_assurance_profile": "EXTERNAL_PREMISE_OWNER_ATTESTED_EXACT_SUBJECT_V1",
        },
        "HumanFounderExternalCapacityRecordV1": {
            "record_type": "HUMAN_FOUNDER_EXTERNAL_CAPACITY_RECORD",
            "record_version": "V1",
            "capacity_kind": "INDEPENDENT_PRIOR_HUMAN_FOUNDER_ONE_SHOT",
            "capacity_origin": "EXTERNAL_FACT_NOT_MACHINE_DERIVED",
        },
        "HumanFounderAuthorityProvenanceRecordV1": {
            "record_type": "HUMAN_FOUNDER_AUTHORITY_PROVENANCE_RECORD",
            "record_version": "V1",
            "anti_self_authorization_result": "TRUE",
            "forbidden_dependency_count": 0,
        },
        "HumanFounderAuthorityCompetenceRecordV1": {
            "record_type": "HUMAN_FOUNDER_AUTHORITY_COMPETENCE_RECORD",
            "record_version": "V1",
            "competence_kind": "FIRST_ADOPTION_OF_EXACT_TARGET_ONLY",
            "competence_result": "COMPETENT_FOR_EXACT_TARGET",
            "maximum_successful_effects": 1,
            "ordinary_post_founding_authority": False,
        },
        "HumanFounderOneShotScopeRecordV1": {
            "record_type": "HUMAN_FOUNDER_ONE_SHOT_SCOPE_RECORD",
            "record_version": "V1",
            "maximum_dispositions": 1,
            "maximum_reviews": 1,
            "maximum_authentication_operations": 1,
            "maximum_finality_events": 1,
            "maximum_successful_effects": 1,
            "delegation_permitted": False,
            "transfer_permitted": False,
            "reset_permitted": False,
            "reissue_permitted": False,
            "recurrence_permitted": False,
            "revival_permitted": False,
        },
        "HumanFounderAuthenticationKeyBindingRecordV1": {
            "record_type": "HUMAN_FOUNDER_AUTHENTICATION_KEY_BINDING_RECORD",
            "record_version": "V1",
            "authentication_algorithm": "ED25519_RFC8032_PURE",
            "public_key_encoding": "BASE64URL_NO_PAD_RAW_32_OCTETS",
            "binding_method": "EXTERNAL_PREMISE_OWNER_ATTESTED_CAPACITY_BINDING",
            "binding_result": "VALID_FOR_EXACT_CAPACITY",
        },
        "HumanFounderAuthenticationVerificationProfileV1": {
            "record_type": "HUMAN_FOUNDER_AUTHENTICATION_VERIFICATION_PROFILE",
            "record_version": "V1",
            "algorithm_identifier": "ED25519_RFC8032_PURE",
            "algorithm_specification": "RFC8032_ED25519_PURE",
            "public_key_encoding": "BASE64URL_NO_PAD_RAW_32_OCTETS",
            "signature_encoding": "BASE64URL_NO_PAD_RAW_64_OCTETS",
            "message_representation": "EXACT_UTF8_CJ1_P_AUTH_V2_BYTES",
            "digest_before_signature": "NONE",
            "context_string": "EMPTY",
            "prehash_mode": "NONE",
            "key_identity_prefix": "human-founder-ed25519-key-v1",
            "trust_anchor_mode": "PREMISE_ACTOR_CAPACITY_KEY_BINDING",
            "domain_identity": "HUMAN_FOUNDER_CANDIDATE_H_FIRST_ADOPTION_P_AUTH_V2_CJ1_UTF8",
            "malformed_input_result": "FALSE",
            "unknown_algorithm_result": "FALSE",
            "noncanonical_encoding_result": "FALSE",
            "verification_true_result": "TRUE",
            "verification_false_result": "FALSE",
        },
        "HumanFounderCapacityStatusReadBackRecordV1": {
            "record_type": "HUMAN_FOUNDER_CAPACITY_STATUS_READ_BACK_RECORD",
            "record_version": "V1",
            "current_status": "ACTIVE",
            "read_back_result": "EXACT_CAPACITY_STATUS_CURRENT",
        },
        "HumanFounderCapacityIssuanceAuthenticationRecordV1": {
            "record_type": "HUMAN_FOUNDER_CAPACITY_ISSUANCE_AUTHENTICATION_RECORD",
            "record_version": "V1",
            "authenticated_message_representation": "EXACT_UTF8_CJ1_CAPACITY_ISSUE_V2",
            "authentication_algorithm": "ED25519_RFC8032_PURE",
            "public_key_encoding": "BASE64URL_NO_PAD_RAW_32_OCTETS",
            "signature_encoding": "BASE64URL_NO_PAD_RAW_64_OCTETS",
            "signature_verification_result": "TRUE",
        },
        "HumanFounderCapacityIssuanceCustodyReadBackRecordV1": {
            "record_type": "HUMAN_FOUNDER_CAPACITY_ISSUANCE_CUSTODY_READ_BACK_RECORD",
            "record_version": "V1",
            "capacity_issuance_generation": 1,
            "predecessor_issuance_status": "AVAILABLE",
            "current_issuance_status": "ISSUED_FINAL",
            "read_back_result": "EXACT_SIGNED_CAPACITY_ISSUANCE_CURRENT",
        },
    }
)


def _fail(code: str, detail: str) -> None:
    raise CandidateValidationError(code, detail)


def _plain_mapping(value: object, detail: str) -> dict[str, object]:
    if isinstance(value, FrozenCanonicalModel):
        return value.to_cj1_object()
    if isinstance(value, Mapping):
        return dict(value)
    _fail("INVALID_NESTED_RECORD", detail)


def _check_pair(model: FrozenCanonicalModel, identity_field: str, digest_field: str) -> None:
    identity_value = getattr(model, identity_field)
    digest_value = getattr(model, digest_field)
    if (identity_value is None) != (digest_value is None):
        _fail("INVALID_NULL_SEMANTICS", f"half-pair:{identity_field}/{digest_field}")


def _validate_local_schema(model: FrozenCanonicalModel) -> None:
    registered = MODEL_REGISTRY.get(type(model).__name__)
    if registered is not type(model):
        _fail("UNKNOWN_SCHEMA_VERSION", type(model).__name__)
    actual_fields = tuple(field.name for field in fields(model))
    if actual_fields != type(model).FIELD_NAMES:
        _fail("SCHEMA_FIELD_MISMATCH", type(model).__name__)
    for name, expected in type(model).CONSTANTS.items():
        if getattr(model, name) != expected:
            code = "CONTRACT_VERSION_MISMATCH" if name == "contract_version" else "SCHEMA_CONSTANT_MISMATCH"
            _fail(code, f"{type(model).__name__}.{name}")
    for name, allowed in type(model).ALLOWED_VALUES.items():
        if getattr(model, name) not in allowed:
            _fail("UNKNOWN_CLOSED_VALUE", f"{type(model).__name__}.{name}")
    for name in type(model).REQUIRED_NULL_FIELDS:
        if getattr(model, name) is not None:
            _fail("INVALID_NULL_SEMANTICS", f"{type(model).__name__}.{name}")
    names = set(type(model).FIELD_NAMES)
    for name in names:
        if name.endswith("_identity") and f"{name[:-9]}_digest" in names:
            _check_pair(model, name, f"{name[:-9]}_digest")
    class_name = type(model).__name__
    if class_name in {
        "ExternalConstituentInstrumentCommitmentV3",
        "ExternalConstituentOneShotFoundingInstrumentV4",
    } and ((model.not_before is None) != (model.expires_at is None)):
        _fail("INVALID_NULL_SEMANTICS", f"{class_name}.not_before/expires_at")
    if class_name == "HumanFounderAuthenticationResultReadBackEvidenceV2":
        valid = model.authentication_result == "AUTHENTICATED_VALID"
        if valid != (model.signature is not None):
            _fail("INVALID_NULL_SEMANTICS", f"{class_name}.signature")
    if class_name == "CandidateHFoundingAttemptTerminalReadBackV1":
        if model.terminal_result == "CONSUMED" and (
            model.terminal_failure_evidence_identity is not None
            or model.next_attempt_sequence is not None
        ):
            _fail("INVALID_NULL_SEMANTICS", f"{class_name}.CONSUMED")
        if model.terminal_result == "ABANDONED" and (
            model.terminal_failure_evidence_identity is None
            or model.next_attempt_sequence is None
        ):
            _fail("INVALID_NULL_SEMANTICS", f"{class_name}.ABANDONED")
    try:
        cj1_encode(model.to_cj1_object())
    except CJ1Error as exc:
        _fail("NON_CJ1_MODEL", str(exc))


def _validate_owner(
    model: FrozenCanonicalModel,
    owner_bindings: Mapping[str, str],
) -> None:
    rule = MODEL_OWNER_RULES.get(type(model).__name__)
    if rule is None or not hasattr(model, "producing_owner"):
        return
    fixed = {
        HUMAN_AUTHORITY,
        "CONSTITUTIONAL_CERTIFICATION_OWNER",
        "CONSTITUTIONAL_GOVERNANCE_OWNER",
        "CONSTITUTIONAL_ROOT_SERIALIZATION_CUSTODIAN",
    }
    expected = rule if rule in fixed else owner_bindings.get(rule)
    if expected is None:
        _fail("OWNER_BINDING_MISSING", rule)
    if model.producing_owner != expected:
        _fail("OWNER_MISMATCH", f"{type(model).__name__}:{rule}")


def expected_artifact_identifiers(model: FrozenCanonicalModel) -> tuple[str, str, str]:
    """Return expected idempotency identity, artifact identity, and digest."""

    spec = ARTIFACT_IDENTITY_SPECS.get(type(model))
    if spec is None:
        _fail("IDENTITY_FORMULA_UNAVAILABLE", type(model).__name__)
    semantic = {name: getattr(model, name) for name in type(model).SEMANTIC_FIELDS}
    semantic.update(
        {
            "artifact_type": model.artifact_type,
            "artifact_version": model.artifact_version,
            "contract_version": model.contract_version,
            "producing_owner": model.producing_owner,
        }
    )
    idempotency_identity = cj1_identity(spec.idempotency_prefix, semantic)
    identity_payload = dict(semantic)
    identity_payload["idempotency_identity"] = idempotency_identity
    artifact_identity = cj1_identity(spec.identity_prefix, identity_payload)
    artifact_digest = cj1_digest(identity_payload)
    return idempotency_identity, artifact_identity, artifact_digest


def _validate_content_identity(model: FrozenCanonicalModel) -> None:
    spec = ARTIFACT_IDENTITY_SPECS.get(type(model))
    if spec is None:
        return
    expected_idem, expected_identity, expected_digest = expected_artifact_identifiers(model)
    actual_idem = model.idempotency_identity
    actual_identity = getattr(model, spec.identity_field)
    actual_digest = getattr(model, spec.digest_field)
    if not isinstance(actual_idem, str) or not actual_idem.startswith(f"{spec.idempotency_prefix}:"):
        _fail("IDENTITY_DOMAIN_MISMATCH", f"{type(model).__name__}.idempotency_identity")
    if actual_idem != expected_idem:
        _fail("IDEMPOTENCY_IDENTITY_MISMATCH", type(model).__name__)
    if not isinstance(actual_identity, str) or not actual_identity.startswith(f"{spec.identity_prefix}:"):
        _fail("IDENTITY_DOMAIN_MISMATCH", f"{type(model).__name__}.{spec.identity_field}")
    if actual_identity != expected_identity:
        _fail("ARTIFACT_IDENTITY_MISMATCH", type(model).__name__)
    if actual_digest != expected_digest:
        _fail("ARTIFACT_DIGEST_MISMATCH", type(model).__name__)


def _validate_nested_record(model: FrozenCanonicalModel) -> None:
    if type(model).__name__ not in NESTED_RECORD_SCHEMAS:
        return
    for name, expected in NESTED_RECORD_CONSTANTS[type(model).__name__].items():
        if getattr(model, name) != expected:
            _fail("NESTED_RECORD_CONSTANT_MISMATCH", f"{type(model).__name__}.{name}")
    payload = model.to_cj1_object()
    actual_digest = payload.pop("record_digest")
    if actual_digest != cj1_digest(payload):
        _fail("RECORD_DIGEST_MISMATCH", type(model).__name__)


def _validate_capacity_nested_records(
    capacity: HumanFounderExternalCapacityEvidenceV2,
    owner_bindings: Mapping[str, str],
) -> None:
    field_to_class = {
        "human_actor_identity_record": "HumanFounderActorIdentityRecordV1",
        "external_capacity_record": "HumanFounderExternalCapacityRecordV1",
        "authority_provenance_record": "HumanFounderAuthorityProvenanceRecordV1",
        "authority_competence_record": "HumanFounderAuthorityCompetenceRecordV1",
        "one_shot_scope_record": "HumanFounderOneShotScopeRecordV1",
        "authentication_key_binding_record": "HumanFounderAuthenticationKeyBindingRecordV1",
        "authentication_verification_profile": "HumanFounderAuthenticationVerificationProfileV1",
        "capacity_status_read_back_record": "HumanFounderCapacityStatusReadBackRecordV1",
        "capacity_issuance_authentication_record": "HumanFounderCapacityIssuanceAuthenticationRecordV1",
        "capacity_issuance_custody_read_back_record": "HumanFounderCapacityIssuanceCustodyReadBackRecordV1",
    }
    nested: dict[str, FrozenCanonicalModel] = {}
    nested_bindings = dict(owner_bindings)
    nested_bindings["CAPACITY_PRODUCING_OWNER"] = capacity.producing_owner
    for field_name, class_name in field_to_class.items():
        record = getattr(capacity, field_name)
        expected_class = MODEL_REGISTRY[class_name]
        if type(record) is not expected_class:
            _fail("INVALID_NESTED_RECORD", f"{field_name}:{class_name}")
        validate_artifact(record, owner_bindings=nested_bindings)
        nested[field_name] = record
    actor = nested["human_actor_identity_record"]
    external = nested["external_capacity_record"]
    provenance = nested["authority_provenance_record"]
    competence = nested["authority_competence_record"]
    scope = nested["one_shot_scope_record"]
    key = nested["authentication_key_binding_record"]
    status = nested["capacity_status_read_back_record"]
    issuance_auth = nested["capacity_issuance_authentication_record"]
    issuance_read_back = nested["capacity_issuance_custody_read_back_record"]
    equalities = (
        (external.external_premise_identity, capacity.external_premise_identity, "external premise"),
        (external.target_identity, capacity.target_identity, "external target"),
        (external.external_constituent_model_identity, capacity.external_constituent_model_identity, "external model"),
        (external.issued_at, capacity.issued_at, "external issued_at"),
        (provenance.external_premise_identity, capacity.external_premise_identity, "provenance premise"),
        (provenance.human_actor_identity, actor.human_actor_identity, "provenance actor"),
        (competence.human_actor_identity, actor.human_actor_identity, "competence actor"),
        (competence.target_identity, capacity.target_identity, "competence target"),
        (scope.target_identity, capacity.target_identity, "scope target"),
        (key.human_actor_identity, actor.human_actor_identity, "key actor"),
        (status.external_capacity_identity, external.external_capacity_identity, "status capacity"),
        (issuance_auth.external_premise_identity, capacity.external_premise_identity, "issuance premise"),
        (issuance_auth.capacity_issuer_identity, capacity.producing_owner, "issuance owner"),
        (issuance_auth.issued_at, capacity.issued_at, "issuance issued_at"),
        (issuance_read_back.external_premise_identity, capacity.external_premise_identity, "issuance read-back premise"),
    )
    for actual, expected, detail in equalities:
        if actual != expected:
            _fail("NESTED_RECORD_BINDING_MISMATCH", detail)


def _validate_hfd_payload(model: FrozenCanonicalModel) -> None:
    if isinstance(model, HumanFounderExternalConstituentActPayloadV2):
        payload = model.to_cj1_object()
        base = {name: payload[name] for name in HFD_ACT_FIELDS if name not in {"disposition", "candidate_common_base_digest"}}
        if model.candidate_common_base_digest != cj1_digest(base):
            _fail("HFD_COMMON_BASE_DIGEST_MISMATCH", type(model).__name__)
    elif isinstance(model, HumanFounderActReviewProjectionV2):
        if tuple(model.reviewed_field_names) != HFD_ACT_FIELDS:
            _fail("HFD_REVIEW_FIELD_ORDER_MISMATCH", type(model).__name__)
        if model.reviewed_field_name_root != cj1_digest(list(HFD_ACT_FIELDS)):
            _fail("HFD_REVIEW_FIELD_ROOT_MISMATCH", type(model).__name__)
        reviewed = _plain_mapping(model.reviewed_act_payload, "reviewed_act_payload")
        if tuple(reviewed) != HFD_ACT_FIELDS:
            _fail("HFD_REVIEW_PAYLOAD_SCHEMA_MISMATCH", type(model).__name__)
        reviewed_digest = cj1_digest(reviewed)
        if model.reviewed_payload_digest != reviewed_digest or model.canonical_act_digest != reviewed_digest:
            _fail("HFD_REVIEW_PAYLOAD_DIGEST_MISMATCH", type(model).__name__)
        semantic_root = cj1_digest(
            {
                "reviewed_field_count": model.reviewed_field_count,
                "reviewed_field_names": list(model.reviewed_field_names),
                "reviewed_field_name_root": model.reviewed_field_name_root,
                "reviewed_act_payload": reviewed,
                "reviewed_payload_digest": model.reviewed_payload_digest,
                "canonical_act_identity": model.canonical_act_identity,
                "canonical_act_digest": model.canonical_act_digest,
            }
        )
        if model.reviewed_semantic_root != semantic_root:
            _fail("HFD_REVIEW_SEMANTIC_ROOT_MISMATCH", type(model).__name__)
    elif isinstance(model, CandidateHInputReferenceManifestV2):
        lineage = list(model.candidate_h_contract_lineage)
        if len(lineage) != model.candidate_h_contract_lineage_count:
            _fail("HFD_MANIFEST_LINEAGE_COUNT_MISMATCH", type(model).__name__)
        if model.candidate_h_contract_lineage_root != cj1_digest(lineage):
            _fail("HFD_MANIFEST_LINEAGE_ROOT_MISMATCH", type(model).__name__)


def validate_artifact(
    model: FrozenCanonicalModel,
    *,
    owner_bindings: Mapping[str, str] | None = None,
) -> FrozenCanonicalModel:
    """Validate one exact Stage-1 model without mutation or inference."""

    if not isinstance(model, FrozenCanonicalModel):
        _fail("UNKNOWN_SCHEMA_VERSION", type(model).__name__)
    bindings = owner_bindings or {}
    _validate_local_schema(model)
    _validate_owner(model, bindings)
    _validate_content_identity(model)
    _validate_nested_record(model)
    _validate_hfd_payload(model)
    if isinstance(model, HumanFounderExternalCapacityEvidenceV2):
        _validate_capacity_nested_records(model, bindings)
    return model


def descriptor_for(
    evidence: FrozenCanonicalModel | EvidenceDescriptor,
    *,
    owner_bindings: Mapping[str, str] | None = None,
) -> EvidenceDescriptor:
    if isinstance(evidence, EvidenceDescriptor):
        versions = EXTERNAL_SCHEMA_VERSIONS.get(evidence.artifact_type)
        if versions is None or evidence.artifact_version not in versions:
            _fail("UNKNOWN_SCHEMA_VERSION", f"{evidence.artifact_type}/{evidence.artifact_version}")
        if not isinstance(evidence.artifact_identity, str) or ":" not in evidence.artifact_identity:
            _fail("IDENTITY_DOMAIN_MISMATCH", evidence.artifact_type)
        if not isinstance(evidence.artifact_digest, str) or not evidence.artifact_digest.startswith("sha256:"):
            _fail("ARTIFACT_DIGEST_MISMATCH", evidence.artifact_type)
        return evidence
    validate_artifact(evidence, owner_bindings=owner_bindings)
    spec = ARTIFACT_IDENTITY_SPECS.get(type(evidence))
    if spec is None:
        _fail("DAG_NODE_NOT_ADDRESSABLE", type(evidence).__name__)
    return EvidenceDescriptor(
        artifact_type=spec.artifact_type,
        artifact_version=spec.artifact_version,
        artifact_identity=getattr(evidence, spec.identity_field),
        artifact_digest=getattr(evidence, spec.digest_field),
        producing_owner=evidence.producing_owner,
    )


def _model_contains_pair(model: FrozenCanonicalModel, identity: str, digest: str) -> bool:
    names = set(type(model).FIELD_NAMES)
    for name in names:
        if not name.endswith("_identity"):
            continue
        digest_name = f"{name[:-9]}_digest"
        if digest_name in names and getattr(model, name) == identity and getattr(model, digest_name) == digest:
            return True
    return False


def _detect_cycle(edges: Mapping[str, tuple[str, ...]]) -> None:
    active: set[str] = set()
    complete: set[str] = set()

    def visit(identity: str) -> None:
        if identity in active:
            _fail("IDENTITY_CYCLE", identity)
        if identity in complete:
            return
        active.add(identity)
        for predecessor in edges[identity]:
            visit(predecessor)
        active.remove(identity)
        complete.add(identity)

    for identity in edges:
        visit(identity)


def validate_identity_dag(
    nodes: Sequence[IdentityDAGNode],
    *,
    owner_bindings: Mapping[str, str] | None = None,
) -> IdentityDAGValidation:
    """Validate an explicitly ordered, finite, forward-only identity DAG."""

    if not isinstance(nodes, Sequence) or isinstance(nodes, (str, bytes, bytearray)):
        _fail("INVALID_DAG_INPUT", type(nodes).__name__)
    bindings = owner_bindings or {}
    descriptors = [descriptor_for(node.evidence, owner_bindings=bindings) for node in nodes]
    by_identity: dict[str, tuple[int, EvidenceDescriptor, IdentityDAGNode]] = {}
    for index, (descriptor, node) in enumerate(zip(descriptors, nodes, strict=True)):
        if descriptor.artifact_identity in by_identity:
            _fail("DUPLICATE_IDENTITY", descriptor.artifact_identity)
        by_identity[descriptor.artifact_identity] = (index, descriptor, node)
    edges: dict[str, tuple[str, ...]] = {}
    for descriptor, node in zip(descriptors, nodes, strict=True):
        predecessor_ids: list[str] = []
        for reference in node.predecessors:
            resolved = by_identity.get(reference.artifact_identity)
            if resolved is None:
                _fail("MISSING_PREDECESSOR", reference.artifact_identity)
            _, actual, _ = resolved
            if actual.artifact_type != reference.artifact_type:
                _fail("WRONG_PREDECESSOR_TYPE", reference.artifact_identity)
            if actual.artifact_version != reference.artifact_version:
                _fail("WRONG_PREDECESSOR_VERSION", reference.artifact_identity)
            if actual.artifact_digest != reference.artifact_digest:
                _fail("WRONG_PREDECESSOR_DIGEST", reference.artifact_identity)
            if isinstance(node.evidence, FrozenCanonicalModel) and not _model_contains_pair(
                node.evidence, reference.artifact_identity, reference.artifact_digest
            ):
                _fail("PREDECESSOR_BINDING_MISMATCH", descriptor.artifact_identity)
            predecessor_ids.append(reference.artifact_identity)
        edges[descriptor.artifact_identity] = tuple(predecessor_ids)
    _detect_cycle(edges)
    for index, descriptor in enumerate(descriptors):
        for predecessor in edges[descriptor.artifact_identity]:
            predecessor_index = by_identity[predecessor][0]
            if predecessor_index >= index:
                _fail("FORWARD_REFERENCE", f"{descriptor.artifact_identity}->{predecessor}")
    graph_rows = [
        {
            "ordinal": index + 1,
            "artifact_type": descriptor.artifact_type,
            "artifact_version": descriptor.artifact_version,
            "artifact_identity": descriptor.artifact_identity,
            "artifact_digest": descriptor.artifact_digest,
            "predecessor_identities": list(edges[descriptor.artifact_identity]),
        }
        for index, descriptor in enumerate(descriptors)
    ]
    return IdentityDAGValidation(
        ordered_identities=tuple(descriptor.artifact_identity for descriptor in descriptors),
        node_count=len(descriptors),
        edge_count=sum(len(value) for value in edges.values()),
        graph_digest=cj1_digest(graph_rows),
    )


def _artifact_pair(model: FrozenCanonicalModel) -> tuple[str, str]:
    spec = ARTIFACT_IDENTITY_SPECS.get(type(model))
    if spec is None:
        _fail("IDENTITY_FORMULA_UNAVAILABLE", type(model).__name__)
    return getattr(model, spec.identity_field), getattr(model, spec.digest_field)


def _require_equal(actual: object, expected: object, detail: str) -> None:
    if actual != expected:
        _fail("P012_BINDING_MISMATCH", detail)


def _validate_predicate_rows(proof_set: ExternalConstituentFoundingEligibilityProofSetV3) -> Mapping[str, object]:
    rows = list(proof_set.ordered_predicate_results)
    if len(rows) != 20 or proof_set.predicate_count != 20:
        _fail("P012_PREDICATE_COUNT_MISMATCH", "ProofSetV3")
    normalized: list[dict[str, object]] = []
    for rank, (code, raw) in enumerate(zip(PREDICATE_CODES, rows, strict=True), start=1):
        row = _plain_mapping(raw, f"predicate:{rank}")
        if tuple(row) != PREDICATE_ROW_FIELDS:
            _fail("P012_PREDICATE_SCHEMA_MISMATCH", str(rank))
        if row["rank"] != rank or row["predicate_code"] != code:
            _fail("P012_PREDICATE_ORDER_MISMATCH", str(rank))
        if row["result"] not in {"TRUE", "FALSE"}:
            _fail("P012_PREDICATE_RESULT_MISMATCH", str(rank))
        normalized.append(row)
    if proof_set.predicate_root != cj1_digest(normalized):
        _fail("P012_PREDICATE_ROOT_MISMATCH", "ProofSetV3")
    expected_result = "ELIGIBLE" if all(row["result"] == "TRUE" for row in normalized) else "INELIGIBLE"
    if proof_set.proof_result != expected_result:
        _fail("P012_PROOF_RESULT_MISMATCH", "ProofSetV3")
    return normalized[11]


def validate_p012_structural_bindings(
    proof_set: ExternalConstituentFoundingEligibilityProofSetV3,
    decision: ExternalConstituentHumanFirstAdoptionDecisionV2,
    capacity: HumanFounderExternalCapacityEvidenceV2,
    result: HumanFounderAuthenticationResultReadBackEvidenceV2,
    authentication_commitment: HumanFounderAuthenticationCommitmentV2,
    *,
    owner_bindings: Mapping[str, str],
) -> bool:
    """Validate the authorized Revision-3 P012 structural tuple only."""

    validate_artifact(capacity, owner_bindings=owner_bindings)
    validate_artifact(result, owner_bindings=owner_bindings)
    validate_artifact(decision, owner_bindings=owner_bindings)
    validate_artifact(proof_set, owner_bindings=owner_bindings)
    validate_artifact(authentication_commitment, owner_bindings=owner_bindings)
    if proof_set.contract_version != AUTHENTICATION_CONTRACT_VERSION:
        _fail("P012_DISPATCH_CONTRACT_MISMATCH", proof_set.contract_version)
    capacity_pair = _artifact_pair(capacity)
    result_pair = _artifact_pair(result)
    decision_pair = _artifact_pair(decision)
    _require_equal(
        (decision.human_founder_external_capacity_evidence_identity,
         decision.human_founder_external_capacity_evidence_digest),
        capacity_pair,
        "decision/capacity",
    )
    _require_equal(
        (result.human_founder_capacity_identity, result.human_founder_capacity_digest),
        capacity_pair,
        "result/capacity",
    )
    _require_equal(
        (decision.authentication_result_read_back_identity,
         decision.authentication_result_read_back_digest),
        result_pair,
        "decision/result",
    )
    _require_equal(
        (capacity.external_premise_identity, capacity.external_premise_digest),
        (result.external_premise_identity, result.external_premise_digest),
        "capacity/result premise",
    )
    commitment_payload = authentication_commitment.to_cj1_object()
    commitment_pair = (
        cj1_identity("human-founder-auth-commitment-v2-sha256", commitment_payload),
        cj1_digest(commitment_payload),
    )
    _require_equal(
        (decision.authentication_commitment_identity, decision.authentication_commitment_digest),
        commitment_pair,
        "decision/authentication commitment",
    )
    _require_equal(
        (result.authentication_commitment_identity, result.authentication_commitment_digest),
        commitment_pair,
        "result/authentication commitment",
    )
    _require_equal(result.authenticated_message_digest, commitment_pair[1], "result/message digest")
    if (
        result.authentication_result != "AUTHENTICATED_VALID"
        or result.terminal_authentication_slot_status != "AUTHENTICATED_FINAL"
        or result.signature_verification_result != "TRUE"
        or result.conflict_status != "NONE"
        or result.signer_outcome_status != "VALID_SIGNATURE_FINAL"
        or result.signature is None
    ):
        _fail("P012_RESULT_NOT_AUTHENTICATED_FINAL", "ResultV2")
    _require_equal(decision.human_signature_scheme, result.signature_scheme, "decision/result scheme")
    _require_equal(decision.human_signature_key_identity, result.signature_key_identity, "decision/result key")
    _require_equal(decision.human_signature, result.signature, "decision/result signature")
    key_record = _plain_mapping(capacity.authentication_key_binding_record, "capacity key binding")
    _require_equal(result.signature_key_identity, key_record.get("authentication_key_identity"), "capacity/result key")
    _require_equal(result.signature_scheme, key_record.get("authentication_algorithm"), "capacity/result scheme")
    p012 = _validate_predicate_rows(proof_set)
    _require_equal(p012["subject_artifact_type"], "ExternalConstituentHumanFirstAdoptionDecisionV2", "P012 type")
    _require_equal(p012["subject_artifact_version"], "V2", "P012 version")
    _require_equal((p012["subject_identity"], p012["subject_digest"]), decision_pair, "P012 decision pair")
    _require_equal(p012["expected_digest"], decision.authentication_commitment_digest, "P012 expected digest")
    _require_equal(p012["observed_digest"], commitment_pair[1], "P012 observed digest")
    _require_equal(p012["result"], "TRUE", "P012 result")
    return True


__all__ = [
    "ARTIFACT_IDENTITY_SPECS",
    "CandidateValidationError",
    "EvidenceDescriptor",
    "EXTERNAL_SCHEMA_VERSIONS",
    "IdentityDAGNode",
    "IdentityDAGValidation",
    "NESTED_RECORD_CONSTANTS",
    "PREDICATE_CODES",
    "PREDICATE_ROW_FIELDS",
    "PredecessorReference",
    "descriptor_for",
    "expected_artifact_identifiers",
    "validate_artifact",
    "validate_identity_dag",
    "validate_p012_structural_bindings",
]
