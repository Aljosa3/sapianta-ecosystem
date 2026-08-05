"""Constitutional Human Ratification contract for G70-04.

The contract records one exact authenticated Human Authority approval of one
resolved G70-03 impact assessment.  It reuses the sole structured Human
Authority Act and Canonical Human Entry contracts.  It does not certify,
activate, persist, observe, mutate, or enter production.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

from aigol.runtime.canonical_human_authority_act_contract_v1 import (
    APPROVAL,
    HUMAN_AUTHORITY_OWNER,
    CanonicalHumanAuthorityActV1,
    bind_canonical_human_authority_act_to_che_v1,
    validate_canonical_human_authority_act_v1,
)
from aigol.runtime.canonical_human_entry_contract_v1 import (
    CanonicalContinuationEnvelopeV1,
    CanonicalHumanEntryRequestEnvelopeV1,
    canonical_che_request_source_act_digest_v1,
    validate_canonical_che_continuation_envelope_v1,
    validate_canonical_che_request_envelope_v1,
)
from aigol.runtime.constitutional_impact_assessment_contract_v1 import (
    UNRESOLVED_CONSTITUTIONAL_IMPACT,
    ConstitutionalImpactAssessmentArtifactV1,
    validate_constitutional_impact_assessment_artifact_v1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize


CONSTITUTIONAL_HUMAN_RATIFICATION_CONTRACT_VERSION = (
    "G70_04_CONSTITUTIONAL_HUMAN_RATIFICATION_CONTRACT_V1"
)
CONSTITUTIONAL_HUMAN_RATIFICATION_ARTIFACT_VERSION = (
    "CONSTITUTIONAL_HUMAN_RATIFICATION_ARTIFACT_V1"
)
CONSTITUTIONAL_HUMAN_RATIFICATION_SERIALIZATION_VERSION = (
    "CONSTITUTIONAL_HUMAN_RATIFICATION_SERIALIZATION_V1"
)

HUMAN_RATIFICATION_RECORDED_NOT_CERTIFIED = (
    "HUMAN_RATIFICATION_RECORDED_NOT_CERTIFIED"
)
CONSTITUTIONAL_AMENDMENT_RATIFICATION_SCOPE = (
    "CONSTITUTIONAL_AMENDMENT_RATIFICATION"
)
RATIFY_CONSTITUTIONAL_AMENDMENT = "RATIFY_CONSTITUTIONAL_AMENDMENT"
CONSTITUTIONAL_GOVERNANCE_OWNER = "CONSTITUTIONAL_GOVERNANCE_OWNER"
CANONICAL_HUMAN_ENTRY_OWNER = "CANONICAL_HUMAN_ENTRY"

HUMAN_AUTHORITY_ACT_EVIDENCE = "HUMAN_AUTHORITY_ACT_EVIDENCE"
CHE_REQUEST_EVIDENCE = "CHE_REQUEST_EVIDENCE"
CHE_CONTINUATION_EVIDENCE = "CHE_CONTINUATION_EVIDENCE"
IMPACT_ASSESSMENT_EVIDENCE = "IMPACT_ASSESSMENT_EVIDENCE"
HUMAN_RATIFICATION_EVIDENCE_ORDER = (
    HUMAN_AUTHORITY_ACT_EVIDENCE,
    CHE_REQUEST_EVIDENCE,
    CHE_CONTINUATION_EVIDENCE,
    IMPACT_ASSESSMENT_EVIDENCE,
)

_RATIFICATION_IDENTITY_PREFIX = "CONSTITUTIONAL-HUMAN-RATIFICATION-"
_RATIFICATION_PAYLOAD_FIELDS = {
    "ratification_command",
    "impact_assessment_identity",
    "impact_assessment_digest",
    "impact_classification",
    "amendment_proposal_identity",
    "amendment_proposal_digest",
    "constitutional_gap_identity",
    "constitutional_gap_digest",
}


def _require_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise FailClosedRuntimeError(
            f"constitutional ratification {field_name} is absent or malformed"
        )
    return value


def _require_sha256(value: Any, field_name: str) -> str:
    text = _require_text(value, field_name)
    if not text.startswith("sha256:") or len(text) != 71:
        raise FailClosedRuntimeError(
            f"constitutional ratification {field_name} is not a SHA-256 reference"
        )
    try:
        int(text[7:], 16)
    except ValueError as exc:
        raise FailClosedRuntimeError(
            f"constitutional ratification {field_name} is not a SHA-256 reference"
        ) from exc
    return text


def _require_exact_keys(
    value: Any,
    keys: set[str],
    field_name: str,
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != keys:
        raise FailClosedRuntimeError(
            f"constitutional ratification {field_name} is malformed"
        )
    return value


def _identity(value: Any) -> str:
    return _RATIFICATION_IDENTITY_PREFIX + sha256(
        canonical_serialize(value).encode("utf-8")
    ).hexdigest()


def _digest(value: Any) -> str:
    return "sha256:" + sha256(
        canonical_serialize(value).encode("utf-8")
    ).hexdigest()


def constitutional_ratification_payload_v1(
    assessment: ConstitutionalImpactAssessmentArtifactV1 | Mapping[str, Any],
) -> dict[str, str]:
    """Return the sole exact Human payload that can ratify this assessment."""

    validated = validate_constitutional_impact_assessment_artifact_v1(assessment)
    proposal = validated.amendment_proposal
    gap = proposal.constitutional_gap
    return {
        "ratification_command": RATIFY_CONSTITUTIONAL_AMENDMENT,
        "impact_assessment_identity": validated.assessment_identity,
        "impact_assessment_digest": validated.artifact_digest,
        "impact_classification": validated.impact_classification,
        "amendment_proposal_identity": proposal.proposal_identity,
        "amendment_proposal_digest": proposal.artifact_digest,
        "constitutional_gap_identity": gap.gap_identity,
        "constitutional_gap_digest": gap.artifact_digest,
    }


@dataclass(frozen=True, slots=True)
class ConstitutionalHumanRatificationEvidenceReferenceV1:
    """One immutable owner-produced ratification evidence reference."""

    evidence_role: str
    producing_owner: str
    artifact_identity: str
    artifact_digest: str

    def __post_init__(self) -> None:
        if self.evidence_role not in HUMAN_RATIFICATION_EVIDENCE_ORDER:
            raise FailClosedRuntimeError(
                "constitutional ratification evidence role is not recognized"
            )
        for field_name in ("producing_owner", "artifact_identity"):
            object.__setattr__(
                self,
                field_name,
                _require_text(getattr(self, field_name), field_name),
            )
        object.__setattr__(
            self,
            "artifact_digest",
            _require_sha256(self.artifact_digest, "artifact_digest"),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "evidence_role": self.evidence_role,
            "producing_owner": self.producing_owner,
            "artifact_identity": self.artifact_identity,
            "artifact_digest": self.artifact_digest,
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "ConstitutionalHumanRatificationEvidenceReferenceV1":
        exact = _require_exact_keys(
            value,
            {
                "evidence_role",
                "producing_owner",
                "artifact_identity",
                "artifact_digest",
            },
            "evidence reference",
        )
        return cls(**dict(exact))


@dataclass(frozen=True, slots=True)
class ConstitutionalHumanRatificationArtifactV1:
    """Immutable exact Human ratification; never Certification or activation."""

    contract_version: str
    artifact_version: str
    serialization_version: str
    ratification_identity: str
    artifact_digest: str
    ratification_status: str
    impact_assessment: ConstitutionalImpactAssessmentArtifactV1
    human_authority_act: CanonicalHumanAuthorityActV1
    che_request: CanonicalHumanEntryRequestEnvelopeV1
    che_continuation: CanonicalContinuationEnvelopeV1
    ratifying_human_actor_identity: str
    ratification_payload_digest: str
    evidence_references: tuple[
        ConstitutionalHumanRatificationEvidenceReferenceV1, ...
    ]
    ratified_at: str
    che_definition_count: int = 1
    production_hic_family_count: int = 1
    production_owner_chain_count: int = 1
    production_path_count: int = 1
    parallel_production_path_count: int = 0
    amendment_certification_performed: bool = False
    amendment_activation_performed: bool = False
    runtime_mutation_performed: bool = False
    production_behavior_changed: bool = False
    replay_path_created: bool = False
    cro_authority_created: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "contract_version",
            "artifact_version",
            "serialization_version",
            "ratification_identity",
            "ratification_status",
            "ratifying_human_actor_identity",
            "ratified_at",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_text(getattr(self, field_name), field_name),
            )
        for field_name in ("artifact_digest", "ratification_payload_digest"):
            object.__setattr__(
                self,
                field_name,
                _require_sha256(getattr(self, field_name), field_name),
            )
        if not isinstance(
            self.impact_assessment, ConstitutionalImpactAssessmentArtifactV1
        ):
            raise FailClosedRuntimeError(
                "constitutional ratification impact assessment is malformed"
            )
        if not isinstance(self.human_authority_act, CanonicalHumanAuthorityActV1):
            raise FailClosedRuntimeError(
                "constitutional ratification Human Authority Act is malformed"
            )
        if not isinstance(self.che_request, CanonicalHumanEntryRequestEnvelopeV1):
            raise FailClosedRuntimeError(
                "constitutional ratification CHE Request is malformed"
            )
        if not isinstance(self.che_continuation, CanonicalContinuationEnvelopeV1):
            raise FailClosedRuntimeError(
                "constitutional ratification CHE Continuation is malformed"
            )
        if (
            not isinstance(self.evidence_references, tuple)
            or any(
                not isinstance(
                    item,
                    ConstitutionalHumanRatificationEvidenceReferenceV1,
                )
                for item in self.evidence_references
            )
        ):
            raise FailClosedRuntimeError(
                "constitutional ratification evidence sequence is malformed"
            )
        for field_name in (
            "che_definition_count",
            "production_hic_family_count",
            "production_owner_chain_count",
            "production_path_count",
            "parallel_production_path_count",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise FailClosedRuntimeError(
                    "constitutional ratification topology is malformed"
                )
        for field_name in (
            "amendment_certification_performed",
            "amendment_activation_performed",
            "runtime_mutation_performed",
            "production_behavior_changed",
            "replay_path_created",
            "cro_authority_created",
        ):
            if not isinstance(getattr(self, field_name), bool):
                raise FailClosedRuntimeError(
                    "constitutional ratification boundary is malformed"
                )

    def identity_payload(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "artifact_version": self.artifact_version,
            "serialization_version": self.serialization_version,
            "ratification_status": self.ratification_status,
            "impact_assessment": self.impact_assessment.to_dict(),
            "human_authority_act": self.human_authority_act.to_dict(),
            "che_request": self.che_request.to_dict(),
            "che_continuation": self.che_continuation.to_dict(),
            "ratifying_human_actor_identity": self.ratifying_human_actor_identity,
            "ratification_payload_digest": self.ratification_payload_digest,
            "evidence_references": [
                item.to_dict() for item in self.evidence_references
            ],
            "ratified_at": self.ratified_at,
            "che_definition_count": self.che_definition_count,
            "production_hic_family_count": self.production_hic_family_count,
            "production_owner_chain_count": self.production_owner_chain_count,
            "production_path_count": self.production_path_count,
            "parallel_production_path_count": self.parallel_production_path_count,
            "amendment_certification_performed": (
                self.amendment_certification_performed
            ),
            "amendment_activation_performed": self.amendment_activation_performed,
            "runtime_mutation_performed": self.runtime_mutation_performed,
            "production_behavior_changed": self.production_behavior_changed,
            "replay_path_created": self.replay_path_created,
            "cro_authority_created": self.cro_authority_created,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "ratification_identity": self.ratification_identity,
            "artifact_digest": self.artifact_digest,
            **self.identity_payload(),
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "ConstitutionalHumanRatificationArtifactV1":
        exact = _require_exact_keys(
            value,
            {
                "contract_version",
                "artifact_version",
                "serialization_version",
                "ratification_identity",
                "artifact_digest",
                "ratification_status",
                "impact_assessment",
                "human_authority_act",
                "che_request",
                "che_continuation",
                "ratifying_human_actor_identity",
                "ratification_payload_digest",
                "evidence_references",
                "ratified_at",
                "che_definition_count",
                "production_hic_family_count",
                "production_owner_chain_count",
                "production_path_count",
                "parallel_production_path_count",
                "amendment_certification_performed",
                "amendment_activation_performed",
                "runtime_mutation_performed",
                "production_behavior_changed",
                "replay_path_created",
                "cro_authority_created",
            },
            "artifact",
        )
        if not isinstance(exact["evidence_references"], list):
            raise FailClosedRuntimeError(
                "constitutional ratification evidence sequence is malformed"
            )
        return cls(
            contract_version=exact["contract_version"],
            artifact_version=exact["artifact_version"],
            serialization_version=exact["serialization_version"],
            ratification_identity=exact["ratification_identity"],
            artifact_digest=exact["artifact_digest"],
            ratification_status=exact["ratification_status"],
            impact_assessment=ConstitutionalImpactAssessmentArtifactV1.from_dict(
                exact["impact_assessment"]
            ),
            human_authority_act=CanonicalHumanAuthorityActV1.from_dict(
                exact["human_authority_act"]
            ),
            che_request=CanonicalHumanEntryRequestEnvelopeV1.from_dict(
                exact["che_request"]
            ),
            che_continuation=CanonicalContinuationEnvelopeV1.from_dict(
                exact["che_continuation"]
            ),
            ratifying_human_actor_identity=exact[
                "ratifying_human_actor_identity"
            ],
            ratification_payload_digest=exact["ratification_payload_digest"],
            evidence_references=tuple(
                ConstitutionalHumanRatificationEvidenceReferenceV1.from_dict(item)
                for item in exact["evidence_references"]
            ),
            ratified_at=exact["ratified_at"],
            che_definition_count=exact["che_definition_count"],
            production_hic_family_count=exact["production_hic_family_count"],
            production_owner_chain_count=exact["production_owner_chain_count"],
            production_path_count=exact["production_path_count"],
            parallel_production_path_count=exact[
                "parallel_production_path_count"
            ],
            amendment_certification_performed=exact[
                "amendment_certification_performed"
            ],
            amendment_activation_performed=exact[
                "amendment_activation_performed"
            ],
            runtime_mutation_performed=exact["runtime_mutation_performed"],
            production_behavior_changed=exact["production_behavior_changed"],
            replay_path_created=exact["replay_path_created"],
            cro_authority_created=exact["cro_authority_created"],
        )


def _ratification_evidence_specifications(
    *,
    assessment: ConstitutionalImpactAssessmentArtifactV1,
    act: CanonicalHumanAuthorityActV1,
    request: CanonicalHumanEntryRequestEnvelopeV1,
    continuation: CanonicalContinuationEnvelopeV1,
) -> tuple[tuple[str, str, str, str], ...]:
    return (
        (
            HUMAN_AUTHORITY_ACT_EVIDENCE,
            HUMAN_AUTHORITY_OWNER,
            act.authority_act_identity,
            _digest(act.to_dict()),
        ),
        (
            CHE_REQUEST_EVIDENCE,
            CANONICAL_HUMAN_ENTRY_OWNER,
            request.request_identity,
            canonical_che_request_source_act_digest_v1(request),
        ),
        (
            CHE_CONTINUATION_EVIDENCE,
            CANONICAL_HUMAN_ENTRY_OWNER,
            continuation.continuation_identity,
            _digest(continuation.to_dict()),
        ),
        (
            IMPACT_ASSESSMENT_EVIDENCE,
            assessment.assessing_owner,
            assessment.assessment_identity,
            assessment.artifact_digest,
        ),
    )


def validate_constitutional_human_ratification_evidence_reference_v1(
    *,
    value: ConstitutionalHumanRatificationEvidenceReferenceV1
    | Mapping[str, Any],
    expected_role: str,
    expected_owner: str,
    expected_artifact_identity: str,
    expected_artifact_digest: str,
) -> ConstitutionalHumanRatificationEvidenceReferenceV1:
    """Validate exact ratification evidence role, owner, identity, and digest."""

    evidence = (
        value
        if isinstance(value, ConstitutionalHumanRatificationEvidenceReferenceV1)
        else ConstitutionalHumanRatificationEvidenceReferenceV1.from_dict(value)
    )
    if (
        evidence.evidence_role != _require_text(expected_role, "expected_role")
        or evidence.producing_owner
        != _require_text(expected_owner, "expected_owner")
    ):
        raise FailClosedRuntimeError(
            "constitutional ratification evidence role or owner is invalid"
        )
    if evidence.artifact_identity != _require_text(
        expected_artifact_identity, "expected_artifact_identity"
    ):
        raise FailClosedRuntimeError(
            "constitutional ratification evidence identity is invalid"
        )
    if evidence.artifact_digest != _require_sha256(
        expected_artifact_digest, "expected_artifact_digest"
    ):
        raise FailClosedRuntimeError(
            "constitutional ratification evidence digest is invalid"
        )
    return evidence


def _validate_ratification_evidence(
    *,
    evidence_references: tuple[
        ConstitutionalHumanRatificationEvidenceReferenceV1, ...
    ],
    specifications: tuple[tuple[str, str, str, str], ...],
) -> tuple[ConstitutionalHumanRatificationEvidenceReferenceV1, ...]:
    if not isinstance(evidence_references, tuple) or len(
        evidence_references
    ) != len(specifications):
        raise FailClosedRuntimeError(
            "constitutional ratification evidence is incomplete"
        )
    if tuple(item.evidence_role for item in evidence_references) != tuple(
        item[0] for item in specifications
    ):
        raise FailClosedRuntimeError(
            "constitutional ratification evidence order is not canonical"
        )
    return tuple(
        validate_constitutional_human_ratification_evidence_reference_v1(
            value=evidence,
            expected_role=role,
            expected_owner=owner,
            expected_artifact_identity=identity,
            expected_artifact_digest=digest,
        )
        for evidence, (role, owner, identity, digest) in zip(
            evidence_references, specifications, strict=True
        )
    )


def _bind_ratification_act(
    *,
    assessment: ConstitutionalImpactAssessmentArtifactV1,
    act: CanonicalHumanAuthorityActV1,
    request: CanonicalHumanEntryRequestEnvelopeV1,
    continuation: CanonicalContinuationEnvelopeV1,
) -> CanonicalHumanAuthorityActV1:
    if assessment.impact_classification == UNRESOLVED_CONSTITUTIONAL_IMPACT:
        raise FailClosedRuntimeError(
            "unresolved Constitutional impact cannot be ratified"
        )
    bound = bind_canonical_human_authority_act_to_che_v1(
        act,
        request,
        continuation,
        expected_authority_kind=APPROVAL,
        expected_target_identity=assessment.assessment_identity,
        expected_target_revision=(
            assessment.amendment_proposal.proposal_revision
        ),
        expected_producing_owner=HUMAN_AUTHORITY_OWNER,
        expected_owner=CONSTITUTIONAL_GOVERNANCE_OWNER,
        expected_authority_scope=CONSTITUTIONAL_AMENDMENT_RATIFICATION_SCOPE,
    )
    payload = bound.to_dict()["payload"]
    if not isinstance(payload, dict) or set(payload) != _RATIFICATION_PAYLOAD_FIELDS:
        raise FailClosedRuntimeError(
            "constitutional ratification payload structure is invalid"
        )
    if payload != constitutional_ratification_payload_v1(assessment):
        raise FailClosedRuntimeError(
            "constitutional ratification payload binding is invalid"
        )
    return bound


def create_constitutional_human_ratification_v1(
    *,
    impact_assessment: ConstitutionalImpactAssessmentArtifactV1
    | Mapping[str, Any],
    human_authority_act: CanonicalHumanAuthorityActV1 | Mapping[str, Any],
    che_request: CanonicalHumanEntryRequestEnvelopeV1 | Mapping[str, Any],
    che_continuation: CanonicalContinuationEnvelopeV1 | Mapping[str, Any],
    evidence_references: Sequence[
        ConstitutionalHumanRatificationEvidenceReferenceV1 | Mapping[str, Any]
    ],
) -> ConstitutionalHumanRatificationArtifactV1:
    """Create one exact Human ratification and stop before Certification."""

    assessment = validate_constitutional_impact_assessment_artifact_v1(
        impact_assessment
    )
    act = validate_canonical_human_authority_act_v1(human_authority_act)
    request = validate_canonical_che_request_envelope_v1(che_request)
    continuation = validate_canonical_che_continuation_envelope_v1(
        che_continuation
    )
    bound_act = _bind_ratification_act(
        assessment=assessment,
        act=act,
        request=request,
        continuation=continuation,
    )
    if isinstance(evidence_references, (str, bytes)) or not isinstance(
        evidence_references, Sequence
    ):
        raise FailClosedRuntimeError(
            "constitutional ratification evidence collection is malformed"
        )
    evidence = tuple(
        item
        if isinstance(item, ConstitutionalHumanRatificationEvidenceReferenceV1)
        else ConstitutionalHumanRatificationEvidenceReferenceV1.from_dict(item)
        for item in evidence_references
    )
    specifications = _ratification_evidence_specifications(
        assessment=assessment,
        act=bound_act,
        request=request,
        continuation=continuation,
    )
    validated_evidence = _validate_ratification_evidence(
        evidence_references=evidence,
        specifications=specifications,
    )
    provisional = ConstitutionalHumanRatificationArtifactV1(
        contract_version=CONSTITUTIONAL_HUMAN_RATIFICATION_CONTRACT_VERSION,
        artifact_version=CONSTITUTIONAL_HUMAN_RATIFICATION_ARTIFACT_VERSION,
        serialization_version=(
            CONSTITUTIONAL_HUMAN_RATIFICATION_SERIALIZATION_VERSION
        ),
        ratification_identity="PENDING-CONSTITUTIONAL-HUMAN-RATIFICATION",
        artifact_digest="sha256:" + ("0" * 64),
        ratification_status=HUMAN_RATIFICATION_RECORDED_NOT_CERTIFIED,
        impact_assessment=assessment,
        human_authority_act=bound_act,
        che_request=request,
        che_continuation=continuation,
        ratifying_human_actor_identity=bound_act.actor_identity,
        ratification_payload_digest=bound_act.payload_digest,
        evidence_references=validated_evidence,
        ratified_at=request.created_at,
    )
    return validate_constitutional_human_ratification_artifact_v1(
        replace(
            provisional,
            ratification_identity=_identity(provisional.identity_payload()),
            artifact_digest=_digest(provisional.identity_payload()),
        )
    )


def validate_constitutional_human_ratification_artifact_v1(
    value: ConstitutionalHumanRatificationArtifactV1 | Mapping[str, Any],
) -> ConstitutionalHumanRatificationArtifactV1:
    """Fail-closed validate exact Human, CHE, assessment, and evidence bindings."""

    ratification = (
        value
        if isinstance(value, ConstitutionalHumanRatificationArtifactV1)
        else ConstitutionalHumanRatificationArtifactV1.from_dict(value)
    )
    if (
        ratification.contract_version
        != CONSTITUTIONAL_HUMAN_RATIFICATION_CONTRACT_VERSION
        or ratification.artifact_version
        != CONSTITUTIONAL_HUMAN_RATIFICATION_ARTIFACT_VERSION
        or ratification.serialization_version
        != CONSTITUTIONAL_HUMAN_RATIFICATION_SERIALIZATION_VERSION
    ):
        raise FailClosedRuntimeError(
            "constitutional ratification version is invalid"
        )
    if (
        ratification.ratification_status
        != HUMAN_RATIFICATION_RECORDED_NOT_CERTIFIED
    ):
        raise FailClosedRuntimeError(
            "constitutional ratification status is invalid"
        )
    assessment = validate_constitutional_impact_assessment_artifact_v1(
        ratification.impact_assessment
    )
    act = validate_canonical_human_authority_act_v1(
        ratification.human_authority_act
    )
    request = validate_canonical_che_request_envelope_v1(ratification.che_request)
    continuation = validate_canonical_che_continuation_envelope_v1(
        ratification.che_continuation
    )
    bound_act = _bind_ratification_act(
        assessment=assessment,
        act=act,
        request=request,
        continuation=continuation,
    )
    if (
        ratification.ratifying_human_actor_identity != bound_act.actor_identity
        or ratification.ratification_payload_digest != bound_act.payload_digest
        or ratification.ratified_at != request.created_at
    ):
        raise FailClosedRuntimeError(
            "constitutional ratification Human binding is invalid"
        )
    specifications = _ratification_evidence_specifications(
        assessment=assessment,
        act=bound_act,
        request=request,
        continuation=continuation,
    )
    evidence = _validate_ratification_evidence(
        evidence_references=ratification.evidence_references,
        specifications=specifications,
    )
    if evidence != ratification.evidence_references:
        raise FailClosedRuntimeError(
            "constitutional ratification evidence correlation is invalid"
        )
    boundaries = (
        ratification.che_definition_count,
        ratification.production_hic_family_count,
        ratification.production_owner_chain_count,
        ratification.production_path_count,
        ratification.parallel_production_path_count,
        ratification.amendment_certification_performed,
        ratification.amendment_activation_performed,
        ratification.runtime_mutation_performed,
        ratification.production_behavior_changed,
        ratification.replay_path_created,
        ratification.cro_authority_created,
    )
    if boundaries != (
        1,
        1,
        1,
        1,
        0,
        False,
        False,
        False,
        False,
        False,
        False,
    ):
        raise FailClosedRuntimeError(
            "constitutional ratification boundary invariants are invalid"
        )
    expected_identity = _identity(ratification.identity_payload())
    expected_digest = _digest(ratification.identity_payload())
    if (
        ratification.ratification_identity != expected_identity
        or ratification.artifact_digest != expected_digest
    ):
        raise FailClosedRuntimeError(
            "constitutional ratification identity is invalid"
        )
    return ratification


def serialize_constitutional_human_ratification_v1(
    ratification: ConstitutionalHumanRatificationArtifactV1 | Mapping[str, Any],
) -> str:
    """Return canonical versioned ratification JSON without persistence."""

    validated = validate_constitutional_human_ratification_artifact_v1(
        ratification
    )
    return canonical_serialize(validated.to_dict())


def deserialize_constitutional_human_ratification_v1(
    serialized: str | bytes,
) -> ConstitutionalHumanRatificationArtifactV1:
    """Parse only canonical UTF-8 V1 ratification JSON and validate it."""

    if isinstance(serialized, bytes):
        try:
            source = serialized.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise FailClosedRuntimeError(
                "constitutional ratification serialization is not UTF-8"
            ) from exc
    elif isinstance(serialized, str):
        source = serialized
    else:
        raise FailClosedRuntimeError(
            "constitutional ratification serialization is malformed"
        )
    try:
        decoded = json.loads(source)
    except json.JSONDecodeError as exc:
        raise FailClosedRuntimeError(
            "constitutional ratification serialization is not valid JSON"
        ) from exc
    ratification = validate_constitutional_human_ratification_artifact_v1(
        decoded
    )
    if canonical_serialize(ratification.to_dict()) != source:
        raise FailClosedRuntimeError(
            "constitutional ratification serialization is not canonical"
        )
    return ratification


__all__ = [
    "CANONICAL_HUMAN_ENTRY_OWNER",
    "CHE_CONTINUATION_EVIDENCE",
    "CHE_REQUEST_EVIDENCE",
    "CONSTITUTIONAL_AMENDMENT_RATIFICATION_SCOPE",
    "CONSTITUTIONAL_GOVERNANCE_OWNER",
    "CONSTITUTIONAL_HUMAN_RATIFICATION_ARTIFACT_VERSION",
    "CONSTITUTIONAL_HUMAN_RATIFICATION_CONTRACT_VERSION",
    "CONSTITUTIONAL_HUMAN_RATIFICATION_SERIALIZATION_VERSION",
    "HUMAN_AUTHORITY_ACT_EVIDENCE",
    "HUMAN_RATIFICATION_EVIDENCE_ORDER",
    "HUMAN_RATIFICATION_RECORDED_NOT_CERTIFIED",
    "IMPACT_ASSESSMENT_EVIDENCE",
    "RATIFY_CONSTITUTIONAL_AMENDMENT",
    "ConstitutionalHumanRatificationArtifactV1",
    "ConstitutionalHumanRatificationEvidenceReferenceV1",
    "constitutional_ratification_payload_v1",
    "create_constitutional_human_ratification_v1",
    "deserialize_constitutional_human_ratification_v1",
    "serialize_constitutional_human_ratification_v1",
    "validate_constitutional_human_ratification_artifact_v1",
    "validate_constitutional_human_ratification_evidence_reference_v1",
]
