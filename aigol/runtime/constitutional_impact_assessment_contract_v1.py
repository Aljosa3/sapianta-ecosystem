"""Constitutional Impact Assessment contract for G70-03.

The contract revalidates one G70-02 proposal and deterministically classifies
explicit owner-produced impact facts.  It records impact only.  It does not
interpret proposal prose, ratify, certify, activate, persist, observe, mutate,
or enter production.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
from typing import Any, Mapping, Sequence

from aigol.runtime.constitutional_amendment_proposal_contract_v1 import (
    ConstitutionalAmendmentProposalArtifactV1,
    validate_constitutional_amendment_proposal_artifact_v1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize


CONSTITUTIONAL_IMPACT_ASSESSMENT_CONTRACT_VERSION = (
    "G70_03_CONSTITUTIONAL_IMPACT_ASSESSMENT_CONTRACT_V1"
)
CONSTITUTIONAL_IMPACT_ASSESSMENT_ARTIFACT_VERSION = (
    "CONSTITUTIONAL_IMPACT_ASSESSMENT_ARTIFACT_V1"
)
IMPACT_ASSESSED_NOT_RATIFIED = "IMPACT_ASSESSED_NOT_RATIFIED"

BOUNDED_CONSTITUTIONAL_IMPACT = "BOUNDED_CONSTITUTIONAL_IMPACT"
CROSS_CONSTITUTIONAL_IMPACT = "CROSS_CONSTITUTIONAL_IMPACT"
CONSTITUTIONAL_BOUNDARY_IMPACT = "CONSTITUTIONAL_BOUNDARY_IMPACT"
UNRESOLVED_CONSTITUTIONAL_IMPACT = "UNRESOLVED_CONSTITUTIONAL_IMPACT"
IMPACT_CLASSIFICATIONS = (
    BOUNDED_CONSTITUTIONAL_IMPACT,
    CROSS_CONSTITUTIONAL_IMPACT,
    CONSTITUTIONAL_BOUNDARY_IMPACT,
    UNRESOLVED_CONSTITUTIONAL_IMPACT,
)

DIRECT_MODIFICATION_PROPOSED = "DIRECT_MODIFICATION_PROPOSED"
SUCCESSOR_REQUIRED = "SUCCESSOR_REQUIRED"
SUPERSESSION_PROPOSED = "SUPERSESSION_PROPOSED"
DEPENDENCY_IMPACT = "DEPENDENCY_IMPACT"
CONTRACT_CONFLICT = "CONTRACT_CONFLICT"
CONTRACT_IMPACT_UNRESOLVED = "CONTRACT_IMPACT_UNRESOLVED"
CONTRACT_IMPACT_KINDS = (
    DIRECT_MODIFICATION_PROPOSED,
    SUCCESSOR_REQUIRED,
    SUPERSESSION_PROPOSED,
    DEPENDENCY_IMPACT,
    CONTRACT_CONFLICT,
    CONTRACT_IMPACT_UNRESOLVED,
)
TARGET_CONTRACT_IMPACT_KINDS = (
    DIRECT_MODIFICATION_PROPOSED,
    SUCCESSOR_REQUIRED,
    SUPERSESSION_PROPOSED,
)

INVARIANT_PRESERVED = "INVARIANT_PRESERVED"
INVARIANT_MODIFICATION_PROPOSED = "INVARIANT_MODIFICATION_PROPOSED"
INVARIANT_CONFLICT = "INVARIANT_CONFLICT"
INVARIANT_IMPACT_UNRESOLVED = "INVARIANT_IMPACT_UNRESOLVED"
INVARIANT_IMPACT_KINDS = (
    INVARIANT_PRESERVED,
    INVARIANT_MODIFICATION_PROPOSED,
    INVARIANT_CONFLICT,
    INVARIANT_IMPACT_UNRESOLVED,
)

REPLAY_UNCHANGED = "REPLAY_UNCHANGED"
REPLAY_CORRELATION_EXTENSION_REQUIRED = "REPLAY_CORRELATION_EXTENSION_REQUIRED"
REPLAY_SAFETY_DEGRADATION_PROPOSED = "REPLAY_SAFETY_DEGRADATION_PROPOSED"
REPLAY_IMPACT_UNRESOLVED = "REPLAY_IMPACT_UNRESOLVED"
REPLAY_IMPACT_CLASSES = (
    REPLAY_UNCHANGED,
    REPLAY_CORRELATION_EXTENSION_REQUIRED,
    REPLAY_SAFETY_DEGRADATION_PROPOSED,
    REPLAY_IMPACT_UNRESOLVED,
)

CRO_UNCHANGED = "CRO_UNCHANGED"
CRO_OBSERVATION_EXTENSION_REQUIRED = "CRO_OBSERVATION_EXTENSION_REQUIRED"
CRO_AUTHORITY_EXPANSION_PROPOSED = "CRO_AUTHORITY_EXPANSION_PROPOSED"
CRO_IMPACT_UNRESOLVED = "CRO_IMPACT_UNRESOLVED"
CRO_IMPACT_CLASSES = (
    CRO_UNCHANGED,
    CRO_OBSERVATION_EXTENSION_REQUIRED,
    CRO_AUTHORITY_EXPANSION_PROPOSED,
    CRO_IMPACT_UNRESOLVED,
)

ONE_PRODUCTION_PATH_PRESERVED = "ONE_PRODUCTION_PATH_PRESERVED"
PRODUCTION_PATH_CHANGE_PROPOSED = "PRODUCTION_PATH_CHANGE_PROPOSED"
PRODUCTION_PATH_IMPACT_UNRESOLVED = "PRODUCTION_PATH_IMPACT_UNRESOLVED"
PRODUCTION_PATH_IMPACT_CLASSES = (
    ONE_PRODUCTION_PATH_PRESERVED,
    PRODUCTION_PATH_CHANGE_PROPOSED,
    PRODUCTION_PATH_IMPACT_UNRESOLVED,
)

OWNER_RESPONSIBILITY_UNCHANGED = "OWNER_RESPONSIBILITY_UNCHANGED"
OWNER_RESPONSIBILITY_CHANGE_PROPOSED = "OWNER_RESPONSIBILITY_CHANGE_PROPOSED"
NEW_OWNER_PROPOSED = "NEW_OWNER_PROPOSED"
OWNER_REMOVAL_PROPOSED = "OWNER_REMOVAL_PROPOSED"
UNBOUNDED_OWNER_AUTHORITY_PROPOSED = "UNBOUNDED_OWNER_AUTHORITY_PROPOSED"
OWNER_IMPACT_UNRESOLVED = "OWNER_IMPACT_UNRESOLVED"
OWNER_IMPACT_KINDS = (
    OWNER_RESPONSIBILITY_UNCHANGED,
    OWNER_RESPONSIBILITY_CHANGE_PROPOSED,
    NEW_OWNER_PROPOSED,
    OWNER_REMOVAL_PROPOSED,
    UNBOUNDED_OWNER_AUTHORITY_PROPOSED,
    OWNER_IMPACT_UNRESOLVED,
)

PROPOSAL_BINDING_EVIDENCE = "PROPOSAL_BINDING_EVIDENCE"
ASSESSOR_AUTHORITY_EVIDENCE = "ASSESSOR_AUTHORITY_EVIDENCE"
CONTRACT_IMPACT_COMPLETENESS_EVIDENCE = (
    "CONTRACT_IMPACT_COMPLETENESS_EVIDENCE"
)
INVARIANT_IMPACT_COMPLETENESS_EVIDENCE = (
    "INVARIANT_IMPACT_COMPLETENESS_EVIDENCE"
)
REPLAY_IMPACT_EVIDENCE = "REPLAY_IMPACT_EVIDENCE"
CRO_IMPACT_EVIDENCE = "CRO_IMPACT_EVIDENCE"
PRODUCTION_PATH_IMPACT_EVIDENCE = "PRODUCTION_PATH_IMPACT_EVIDENCE"
OWNER_IMPACT_COMPLETENESS_EVIDENCE = "OWNER_IMPACT_COMPLETENESS_EVIDENCE"
IMPACT_ASSESSMENT_EVIDENCE_ORDER = (
    PROPOSAL_BINDING_EVIDENCE,
    ASSESSOR_AUTHORITY_EVIDENCE,
    CONTRACT_IMPACT_COMPLETENESS_EVIDENCE,
    INVARIANT_IMPACT_COMPLETENESS_EVIDENCE,
    REPLAY_IMPACT_EVIDENCE,
    CRO_IMPACT_EVIDENCE,
    PRODUCTION_PATH_IMPACT_EVIDENCE,
    OWNER_IMPACT_COMPLETENESS_EVIDENCE,
)

OWNER_LOCAL_REPLAY_CUSTODIAN = "OWNER_LOCAL_REPLAY_CUSTODIAN"
PASSIVE_CONSTITUTIONAL_RUNTIME_OBSERVATORY = (
    "PASSIVE_CONSTITUTIONAL_RUNTIME_OBSERVATORY"
)
CONSTITUTIONAL_GOVERNANCE_OWNER = "CONSTITUTIONAL_GOVERNANCE_OWNER"

_ASSESSMENT_IDENTITY_PREFIX = "CONSTITUTIONAL-IMPACT-ASSESSMENT-"


def _require_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise FailClosedRuntimeError(
            f"constitutional impact {field_name} is absent or malformed"
        )
    return value


def _require_sha256(value: Any, field_name: str) -> str:
    text = _require_text(value, field_name)
    if not text.startswith("sha256:") or len(text) != 71:
        raise FailClosedRuntimeError(
            f"constitutional impact {field_name} is not a SHA-256 reference"
        )
    try:
        int(text[7:], 16)
    except ValueError as exc:
        raise FailClosedRuntimeError(
            f"constitutional impact {field_name} is not a SHA-256 reference"
        ) from exc
    return text


def _require_exact_keys(
    value: Any,
    keys: set[str],
    field_name: str,
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != keys:
        raise FailClosedRuntimeError(
            f"constitutional impact {field_name} is malformed"
        )
    return value


def _identity(value: Any) -> str:
    return _ASSESSMENT_IDENTITY_PREFIX + sha256(
        canonical_serialize(value).encode("utf-8")
    ).hexdigest()


def _digest(value: Any) -> str:
    return "sha256:" + sha256(
        canonical_serialize(value).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True, slots=True)
class ConstitutionalImpactEvidenceReferenceV1:
    """One owner-produced reference supporting the complete assessment."""

    evidence_role: str
    producing_owner: str
    artifact_identity: str
    artifact_digest: str

    def __post_init__(self) -> None:
        if self.evidence_role not in IMPACT_ASSESSMENT_EVIDENCE_ORDER:
            raise FailClosedRuntimeError(
                "constitutional impact evidence role is not recognized"
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
    ) -> "ConstitutionalImpactEvidenceReferenceV1":
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
class AffectedConstitutionalContractV1:
    """One affected normative contract and exact owner evidence."""

    contract_identity: str
    contract_version: str
    contract_owner: str
    impact_kind: str
    evidence_producing_owner: str
    evidence_artifact_identity: str
    evidence_artifact_digest: str

    def __post_init__(self) -> None:
        for field_name in (
            "contract_identity",
            "contract_version",
            "contract_owner",
            "evidence_producing_owner",
            "evidence_artifact_identity",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_text(getattr(self, field_name), field_name),
            )
        if self.impact_kind not in CONTRACT_IMPACT_KINDS:
            raise FailClosedRuntimeError(
                "constitutional contract impact kind is not recognized"
            )
        if self.evidence_producing_owner != self.contract_owner:
            raise FailClosedRuntimeError(
                "constitutional contract impact evidence owner is invalid"
            )
        object.__setattr__(
            self,
            "evidence_artifact_digest",
            _require_sha256(
                self.evidence_artifact_digest,
                "evidence_artifact_digest",
            ),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "contract_identity": self.contract_identity,
            "contract_version": self.contract_version,
            "contract_owner": self.contract_owner,
            "impact_kind": self.impact_kind,
            "evidence_producing_owner": self.evidence_producing_owner,
            "evidence_artifact_identity": self.evidence_artifact_identity,
            "evidence_artifact_digest": self.evidence_artifact_digest,
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "AffectedConstitutionalContractV1":
        exact = _require_exact_keys(
            value,
            {
                "contract_identity",
                "contract_version",
                "contract_owner",
                "impact_kind",
                "evidence_producing_owner",
                "evidence_artifact_identity",
                "evidence_artifact_digest",
            },
            "affected contract",
        )
        return cls(**dict(exact))


@dataclass(frozen=True, slots=True)
class AffectedConstitutionalInvariantV1:
    """One reviewed invariant and exact owner evidence."""

    invariant_identity: str
    invariant_owner: str
    impact_kind: str
    evidence_producing_owner: str
    evidence_artifact_identity: str
    evidence_artifact_digest: str

    def __post_init__(self) -> None:
        for field_name in (
            "invariant_identity",
            "invariant_owner",
            "evidence_producing_owner",
            "evidence_artifact_identity",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_text(getattr(self, field_name), field_name),
            )
        if self.impact_kind not in INVARIANT_IMPACT_KINDS:
            raise FailClosedRuntimeError(
                "constitutional invariant impact kind is not recognized"
            )
        if self.evidence_producing_owner != self.invariant_owner:
            raise FailClosedRuntimeError(
                "constitutional invariant impact evidence owner is invalid"
            )
        object.__setattr__(
            self,
            "evidence_artifact_digest",
            _require_sha256(
                self.evidence_artifact_digest,
                "evidence_artifact_digest",
            ),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "invariant_identity": self.invariant_identity,
            "invariant_owner": self.invariant_owner,
            "impact_kind": self.impact_kind,
            "evidence_producing_owner": self.evidence_producing_owner,
            "evidence_artifact_identity": self.evidence_artifact_identity,
            "evidence_artifact_digest": self.evidence_artifact_digest,
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "AffectedConstitutionalInvariantV1":
        exact = _require_exact_keys(
            value,
            {
                "invariant_identity",
                "invariant_owner",
                "impact_kind",
                "evidence_producing_owner",
                "evidence_artifact_identity",
                "evidence_artifact_digest",
            },
            "affected invariant",
        )
        return cls(**dict(exact))


@dataclass(frozen=True, slots=True)
class ConstitutionalOwnerImpactV1:
    """One reviewed owner responsibility and Governance-produced evidence."""

    owner_identity: str
    responsibility_identity: str
    impact_kind: str
    evidence_producing_owner: str
    evidence_artifact_identity: str
    evidence_artifact_digest: str

    def __post_init__(self) -> None:
        for field_name in (
            "owner_identity",
            "responsibility_identity",
            "evidence_producing_owner",
            "evidence_artifact_identity",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_text(getattr(self, field_name), field_name),
            )
        if self.impact_kind not in OWNER_IMPACT_KINDS:
            raise FailClosedRuntimeError(
                "constitutional owner impact kind is not recognized"
            )
        if self.evidence_producing_owner != CONSTITUTIONAL_GOVERNANCE_OWNER:
            raise FailClosedRuntimeError(
                "constitutional owner impact evidence owner is invalid"
            )
        object.__setattr__(
            self,
            "evidence_artifact_digest",
            _require_sha256(
                self.evidence_artifact_digest,
                "evidence_artifact_digest",
            ),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "owner_identity": self.owner_identity,
            "responsibility_identity": self.responsibility_identity,
            "impact_kind": self.impact_kind,
            "evidence_producing_owner": self.evidence_producing_owner,
            "evidence_artifact_identity": self.evidence_artifact_identity,
            "evidence_artifact_digest": self.evidence_artifact_digest,
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "ConstitutionalOwnerImpactV1":
        exact = _require_exact_keys(
            value,
            {
                "owner_identity",
                "responsibility_identity",
                "impact_kind",
                "evidence_producing_owner",
                "evidence_artifact_identity",
                "evidence_artifact_digest",
            },
            "owner impact",
        )
        return cls(**dict(exact))


@dataclass(frozen=True, slots=True)
class ConstitutionalImpactAssessmentArtifactV1:
    """Immutable assessment-only artifact with no amendment authority."""

    contract_version: str
    artifact_version: str
    assessment_identity: str
    artifact_digest: str
    assessment_status: str
    impact_classification: str
    amendment_proposal: ConstitutionalAmendmentProposalArtifactV1
    assessing_owner: str
    affected_contracts: tuple[AffectedConstitutionalContractV1, ...]
    affected_invariants: tuple[AffectedConstitutionalInvariantV1, ...]
    replay_impact: str
    cro_impact: str
    production_path_impact: str
    owner_impacts: tuple[ConstitutionalOwnerImpactV1, ...]
    evidence_references: tuple[ConstitutionalImpactEvidenceReferenceV1, ...]
    assessed_at: str
    che_definition_count: int = 1
    production_hic_family_count: int = 1
    production_owner_chain_count: int = 1
    production_path_count: int = 1
    parallel_production_path_count: int = 0
    human_ratification_performed: bool = False
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
            "assessment_identity",
            "assessment_status",
            "impact_classification",
            "assessing_owner",
            "replay_impact",
            "cro_impact",
            "production_path_impact",
            "assessed_at",
        ):
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
        if not isinstance(
            self.amendment_proposal, ConstitutionalAmendmentProposalArtifactV1
        ):
            raise FailClosedRuntimeError(
                "constitutional impact proposal is malformed"
            )
        for field_name, item_type in (
            ("affected_contracts", AffectedConstitutionalContractV1),
            ("affected_invariants", AffectedConstitutionalInvariantV1),
            ("owner_impacts", ConstitutionalOwnerImpactV1),
            ("evidence_references", ConstitutionalImpactEvidenceReferenceV1),
        ):
            value = getattr(self, field_name)
            if not isinstance(value, tuple) or any(
                not isinstance(item, item_type) for item in value
            ):
                raise FailClosedRuntimeError(
                    f"constitutional impact {field_name} is malformed"
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
                    "constitutional impact topology is malformed"
                )
        for field_name in (
            "human_ratification_performed",
            "amendment_certification_performed",
            "amendment_activation_performed",
            "runtime_mutation_performed",
            "production_behavior_changed",
            "replay_path_created",
            "cro_authority_created",
        ):
            if not isinstance(getattr(self, field_name), bool):
                raise FailClosedRuntimeError(
                    "constitutional impact boundary is malformed"
                )

    def identity_payload(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "artifact_version": self.artifact_version,
            "assessment_status": self.assessment_status,
            "impact_classification": self.impact_classification,
            "amendment_proposal": self.amendment_proposal.to_dict(),
            "assessing_owner": self.assessing_owner,
            "affected_contracts": [
                item.to_dict() for item in self.affected_contracts
            ],
            "affected_invariants": [
                item.to_dict() for item in self.affected_invariants
            ],
            "replay_impact": self.replay_impact,
            "cro_impact": self.cro_impact,
            "production_path_impact": self.production_path_impact,
            "owner_impacts": [item.to_dict() for item in self.owner_impacts],
            "evidence_references": [
                item.to_dict() for item in self.evidence_references
            ],
            "assessed_at": self.assessed_at,
            "che_definition_count": self.che_definition_count,
            "production_hic_family_count": self.production_hic_family_count,
            "production_owner_chain_count": self.production_owner_chain_count,
            "production_path_count": self.production_path_count,
            "parallel_production_path_count": self.parallel_production_path_count,
            "human_ratification_performed": self.human_ratification_performed,
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
            "assessment_identity": self.assessment_identity,
            "artifact_digest": self.artifact_digest,
            **self.identity_payload(),
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "ConstitutionalImpactAssessmentArtifactV1":
        exact = _require_exact_keys(
            value,
            {
                "contract_version",
                "artifact_version",
                "assessment_identity",
                "artifact_digest",
                "assessment_status",
                "impact_classification",
                "amendment_proposal",
                "assessing_owner",
                "affected_contracts",
                "affected_invariants",
                "replay_impact",
                "cro_impact",
                "production_path_impact",
                "owner_impacts",
                "evidence_references",
                "assessed_at",
                "che_definition_count",
                "production_hic_family_count",
                "production_owner_chain_count",
                "production_path_count",
                "parallel_production_path_count",
                "human_ratification_performed",
                "amendment_certification_performed",
                "amendment_activation_performed",
                "runtime_mutation_performed",
                "production_behavior_changed",
                "replay_path_created",
                "cro_authority_created",
            },
            "assessment artifact",
        )
        for field_name in (
            "affected_contracts",
            "affected_invariants",
            "owner_impacts",
            "evidence_references",
        ):
            if not isinstance(exact[field_name], list):
                raise FailClosedRuntimeError(
                    f"constitutional impact {field_name} is malformed"
                )
        return cls(
            contract_version=exact["contract_version"],
            artifact_version=exact["artifact_version"],
            assessment_identity=exact["assessment_identity"],
            artifact_digest=exact["artifact_digest"],
            assessment_status=exact["assessment_status"],
            impact_classification=exact["impact_classification"],
            amendment_proposal=ConstitutionalAmendmentProposalArtifactV1.from_dict(
                exact["amendment_proposal"]
            ),
            assessing_owner=exact["assessing_owner"],
            affected_contracts=tuple(
                AffectedConstitutionalContractV1.from_dict(item)
                for item in exact["affected_contracts"]
            ),
            affected_invariants=tuple(
                AffectedConstitutionalInvariantV1.from_dict(item)
                for item in exact["affected_invariants"]
            ),
            replay_impact=exact["replay_impact"],
            cro_impact=exact["cro_impact"],
            production_path_impact=exact["production_path_impact"],
            owner_impacts=tuple(
                ConstitutionalOwnerImpactV1.from_dict(item)
                for item in exact["owner_impacts"]
            ),
            evidence_references=tuple(
                ConstitutionalImpactEvidenceReferenceV1.from_dict(item)
                for item in exact["evidence_references"]
            ),
            assessed_at=exact["assessed_at"],
            che_definition_count=exact["che_definition_count"],
            production_hic_family_count=exact["production_hic_family_count"],
            production_owner_chain_count=exact["production_owner_chain_count"],
            production_path_count=exact["production_path_count"],
            parallel_production_path_count=exact[
                "parallel_production_path_count"
            ],
            human_ratification_performed=exact["human_ratification_performed"],
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


def validate_affected_constitutional_contract_v1(
    value: AffectedConstitutionalContractV1 | Mapping[str, Any],
) -> AffectedConstitutionalContractV1:
    """Public exact-model validator for one affected contract."""

    return (
        value
        if isinstance(value, AffectedConstitutionalContractV1)
        else AffectedConstitutionalContractV1.from_dict(value)
    )


def validate_affected_constitutional_invariant_v1(
    value: AffectedConstitutionalInvariantV1 | Mapping[str, Any],
) -> AffectedConstitutionalInvariantV1:
    """Public exact-model validator for one reviewed invariant."""

    return (
        value
        if isinstance(value, AffectedConstitutionalInvariantV1)
        else AffectedConstitutionalInvariantV1.from_dict(value)
    )


def validate_constitutional_owner_impact_v1(
    value: ConstitutionalOwnerImpactV1 | Mapping[str, Any],
) -> ConstitutionalOwnerImpactV1:
    """Public exact-model validator for one owner impact."""

    return (
        value
        if isinstance(value, ConstitutionalOwnerImpactV1)
        else ConstitutionalOwnerImpactV1.from_dict(value)
    )


def validate_constitutional_impact_evidence_reference_v1(
    *,
    value: ConstitutionalImpactEvidenceReferenceV1 | Mapping[str, Any],
    expected_role: str,
    expected_owner: str,
    expected_artifact_identity: str | None = None,
    expected_artifact_digest: str | None = None,
) -> ConstitutionalImpactEvidenceReferenceV1:
    """Validate exact role, owner, and optional artifact correlation."""

    evidence = (
        value
        if isinstance(value, ConstitutionalImpactEvidenceReferenceV1)
        else ConstitutionalImpactEvidenceReferenceV1.from_dict(value)
    )
    if (
        evidence.evidence_role != _require_text(expected_role, "expected_role")
        or evidence.producing_owner
        != _require_text(expected_owner, "expected_owner")
    ):
        raise FailClosedRuntimeError(
            "constitutional impact evidence role or owner is invalid"
        )
    if (
        expected_artifact_identity is not None
        and evidence.artifact_identity != expected_artifact_identity
    ):
        raise FailClosedRuntimeError(
            "constitutional impact evidence identity is invalid"
        )
    if (
        expected_artifact_digest is not None
        and evidence.artifact_digest != expected_artifact_digest
    ):
        raise FailClosedRuntimeError(
            "constitutional impact evidence digest is invalid"
        )
    return evidence


def _normalize_contracts(
    values: Sequence[AffectedConstitutionalContractV1 | Mapping[str, Any]],
) -> tuple[AffectedConstitutionalContractV1, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise FailClosedRuntimeError(
            "constitutional impact affected contracts are malformed"
        )
    contracts = tuple(validate_affected_constitutional_contract_v1(item) for item in values)
    ordered = tuple(sorted(contracts, key=lambda item: item.contract_identity))
    if not ordered or len({item.contract_identity for item in ordered}) != len(ordered):
        raise FailClosedRuntimeError(
            "constitutional impact affected contracts are absent or duplicated"
        )
    return ordered


def _normalize_invariants(
    values: Sequence[AffectedConstitutionalInvariantV1 | Mapping[str, Any]],
) -> tuple[AffectedConstitutionalInvariantV1, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise FailClosedRuntimeError(
            "constitutional impact affected invariants are malformed"
        )
    invariants = tuple(validate_affected_constitutional_invariant_v1(item) for item in values)
    ordered = tuple(sorted(invariants, key=lambda item: item.invariant_identity))
    if len({item.invariant_identity for item in ordered}) != len(ordered):
        raise FailClosedRuntimeError(
            "constitutional impact affected invariants are duplicated"
        )
    return ordered


def _normalize_owner_impacts(
    values: Sequence[ConstitutionalOwnerImpactV1 | Mapping[str, Any]],
) -> tuple[ConstitutionalOwnerImpactV1, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise FailClosedRuntimeError(
            "constitutional impact owner impacts are malformed"
        )
    impacts = tuple(validate_constitutional_owner_impact_v1(item) for item in values)
    ordered = tuple(
        sorted(impacts, key=lambda item: (item.owner_identity, item.responsibility_identity))
    )
    keys = tuple((item.owner_identity, item.responsibility_identity) for item in ordered)
    if len(set(keys)) != len(keys):
        raise FailClosedRuntimeError(
            "constitutional impact owner impacts are duplicated"
        )
    return ordered


def _validate_target_contract(
    proposal: ConstitutionalAmendmentProposalArtifactV1,
    contracts: tuple[AffectedConstitutionalContractV1, ...],
) -> None:
    target = next(
        (
            item
            for item in contracts
            if item.contract_identity
            == proposal.target_constitutional_artifact_identity
        ),
        None,
    )
    if target is None:
        raise FailClosedRuntimeError(
            "constitutional impact target contract is absent"
        )
    if (
        target.contract_version != proposal.target_constitutional_artifact_version
        or target.contract_owner != proposal.target_constitutional_owner
        or target.evidence_artifact_identity
        != proposal.target_constitutional_artifact_identity
        or target.evidence_artifact_digest
        != proposal.target_constitutional_artifact_digest
        or target.impact_kind not in TARGET_CONTRACT_IMPACT_KINDS
    ):
        raise FailClosedRuntimeError(
            "constitutional impact target contract binding is invalid"
        )


def _classify_impact(
    *,
    contracts: tuple[AffectedConstitutionalContractV1, ...],
    invariants: tuple[AffectedConstitutionalInvariantV1, ...],
    replay_impact: str,
    cro_impact: str,
    production_path_impact: str,
    owner_impacts: tuple[ConstitutionalOwnerImpactV1, ...],
) -> str:
    unresolved = (
        any(item.impact_kind == CONTRACT_IMPACT_UNRESOLVED for item in contracts)
        or any(
            item.impact_kind == INVARIANT_IMPACT_UNRESOLVED
            for item in invariants
        )
        or any(item.impact_kind == OWNER_IMPACT_UNRESOLVED for item in owner_impacts)
        or replay_impact == REPLAY_IMPACT_UNRESOLVED
        or cro_impact == CRO_IMPACT_UNRESOLVED
        or production_path_impact == PRODUCTION_PATH_IMPACT_UNRESOLVED
    )
    if unresolved:
        return UNRESOLVED_CONSTITUTIONAL_IMPACT
    boundary = (
        any(item.impact_kind == CONTRACT_CONFLICT for item in contracts)
        or any(item.impact_kind == INVARIANT_CONFLICT for item in invariants)
        or any(
            item.impact_kind == UNBOUNDED_OWNER_AUTHORITY_PROPOSED
            for item in owner_impacts
        )
        or replay_impact == REPLAY_SAFETY_DEGRADATION_PROPOSED
        or cro_impact == CRO_AUTHORITY_EXPANSION_PROPOSED
        or production_path_impact == PRODUCTION_PATH_CHANGE_PROPOSED
    )
    if boundary:
        return CONSTITUTIONAL_BOUNDARY_IMPACT
    cross = (
        len(contracts) > 1
        or any(
            item.impact_kind
            in {
                DEPENDENCY_IMPACT,
                SUPERSESSION_PROPOSED,
            }
            for item in contracts
        )
        or any(
            item.impact_kind == INVARIANT_MODIFICATION_PROPOSED
            for item in invariants
        )
        or any(
            item.impact_kind != OWNER_RESPONSIBILITY_UNCHANGED
            for item in owner_impacts
        )
        or replay_impact == REPLAY_CORRELATION_EXTENSION_REQUIRED
        or cro_impact == CRO_OBSERVATION_EXTENSION_REQUIRED
    )
    if cross:
        return CROSS_CONSTITUTIONAL_IMPACT
    return BOUNDED_CONSTITUTIONAL_IMPACT


def _evidence_specifications(
    *,
    proposal: ConstitutionalAmendmentProposalArtifactV1,
    assessing_owner: str,
) -> tuple[tuple[str, str, str | None, str | None], ...]:
    return (
        (
            PROPOSAL_BINDING_EVIDENCE,
            proposal.proposing_owner,
            proposal.proposal_identity,
            proposal.artifact_digest,
        ),
        (ASSESSOR_AUTHORITY_EVIDENCE, assessing_owner, None, None),
        (CONTRACT_IMPACT_COMPLETENESS_EVIDENCE, assessing_owner, None, None),
        (INVARIANT_IMPACT_COMPLETENESS_EVIDENCE, assessing_owner, None, None),
        (REPLAY_IMPACT_EVIDENCE, OWNER_LOCAL_REPLAY_CUSTODIAN, None, None),
        (
            CRO_IMPACT_EVIDENCE,
            PASSIVE_CONSTITUTIONAL_RUNTIME_OBSERVATORY,
            None,
            None,
        ),
        (
            PRODUCTION_PATH_IMPACT_EVIDENCE,
            CONSTITUTIONAL_GOVERNANCE_OWNER,
            None,
            None,
        ),
        (
            OWNER_IMPACT_COMPLETENESS_EVIDENCE,
            CONSTITUTIONAL_GOVERNANCE_OWNER,
            None,
            None,
        ),
    )


def _normalize_evidence(
    *,
    values: Sequence[ConstitutionalImpactEvidenceReferenceV1 | Mapping[str, Any]],
    specifications: tuple[tuple[str, str, str | None, str | None], ...],
) -> tuple[ConstitutionalImpactEvidenceReferenceV1, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise FailClosedRuntimeError(
            "constitutional impact evidence collection is malformed"
        )
    evidence = tuple(
        item
        if isinstance(item, ConstitutionalImpactEvidenceReferenceV1)
        else ConstitutionalImpactEvidenceReferenceV1.from_dict(item)
        for item in values
    )
    if len(evidence) != len(specifications):
        raise FailClosedRuntimeError(
            "constitutional impact evidence is incomplete"
        )
    if tuple(item.evidence_role for item in evidence) != tuple(
        item[0] for item in specifications
    ):
        raise FailClosedRuntimeError(
            "constitutional impact evidence order is not canonical"
        )
    return tuple(
        validate_constitutional_impact_evidence_reference_v1(
            value=reference,
            expected_role=role,
            expected_owner=owner,
            expected_artifact_identity=identity,
            expected_artifact_digest=digest,
        )
        for reference, (role, owner, identity, digest) in zip(
            evidence, specifications, strict=True
        )
    )


def assess_constitutional_impact_v1(
    *,
    amendment_proposal: ConstitutionalAmendmentProposalArtifactV1
    | Mapping[str, Any],
    assessing_owner: str,
    affected_contracts: Sequence[
        AffectedConstitutionalContractV1 | Mapping[str, Any]
    ],
    affected_invariants: Sequence[
        AffectedConstitutionalInvariantV1 | Mapping[str, Any]
    ],
    replay_impact: str,
    cro_impact: str,
    production_path_impact: str,
    owner_impacts: Sequence[ConstitutionalOwnerImpactV1 | Mapping[str, Any]],
    evidence_references: Sequence[
        ConstitutionalImpactEvidenceReferenceV1 | Mapping[str, Any]
    ],
    assessed_at: str,
) -> ConstitutionalImpactAssessmentArtifactV1:
    """Assess exact owner facts and return an immutable non-authoritative artifact."""

    proposal = validate_constitutional_amendment_proposal_artifact_v1(
        amendment_proposal
    )
    assessor = _require_text(assessing_owner, "assessing_owner")
    assessed_time = _require_text(assessed_at, "assessed_at")
    if replay_impact not in REPLAY_IMPACT_CLASSES:
        raise FailClosedRuntimeError(
            "constitutional Replay impact is not recognized"
        )
    if cro_impact not in CRO_IMPACT_CLASSES:
        raise FailClosedRuntimeError("constitutional CRO impact is not recognized")
    if production_path_impact not in PRODUCTION_PATH_IMPACT_CLASSES:
        raise FailClosedRuntimeError(
            "constitutional production path impact is not recognized"
        )
    contracts = _normalize_contracts(affected_contracts)
    invariants = _normalize_invariants(affected_invariants)
    owners = _normalize_owner_impacts(owner_impacts)
    _validate_target_contract(proposal, contracts)
    specifications = _evidence_specifications(
        proposal=proposal,
        assessing_owner=assessor,
    )
    evidence = _normalize_evidence(
        values=evidence_references,
        specifications=specifications,
    )
    classification = _classify_impact(
        contracts=contracts,
        invariants=invariants,
        replay_impact=replay_impact,
        cro_impact=cro_impact,
        production_path_impact=production_path_impact,
        owner_impacts=owners,
    )
    provisional = ConstitutionalImpactAssessmentArtifactV1(
        contract_version=CONSTITUTIONAL_IMPACT_ASSESSMENT_CONTRACT_VERSION,
        artifact_version=CONSTITUTIONAL_IMPACT_ASSESSMENT_ARTIFACT_VERSION,
        assessment_identity="PENDING-CONSTITUTIONAL-IMPACT-ASSESSMENT",
        artifact_digest="sha256:" + ("0" * 64),
        assessment_status=IMPACT_ASSESSED_NOT_RATIFIED,
        impact_classification=classification,
        amendment_proposal=proposal,
        assessing_owner=assessor,
        affected_contracts=contracts,
        affected_invariants=invariants,
        replay_impact=replay_impact,
        cro_impact=cro_impact,
        production_path_impact=production_path_impact,
        owner_impacts=owners,
        evidence_references=evidence,
        assessed_at=assessed_time,
    )
    return validate_constitutional_impact_assessment_artifact_v1(
        replace(
            provisional,
            assessment_identity=_identity(provisional.identity_payload()),
            artifact_digest=_digest(provisional.identity_payload()),
        )
    )


def validate_constitutional_impact_assessment_artifact_v1(
    value: ConstitutionalImpactAssessmentArtifactV1 | Mapping[str, Any],
) -> ConstitutionalImpactAssessmentArtifactV1:
    """Public complete validator for one deterministic assessment artifact."""

    assessment = (
        value
        if isinstance(value, ConstitutionalImpactAssessmentArtifactV1)
        else ConstitutionalImpactAssessmentArtifactV1.from_dict(value)
    )
    if (
        assessment.contract_version
        != CONSTITUTIONAL_IMPACT_ASSESSMENT_CONTRACT_VERSION
        or assessment.artifact_version
        != CONSTITUTIONAL_IMPACT_ASSESSMENT_ARTIFACT_VERSION
    ):
        raise FailClosedRuntimeError(
            "constitutional impact assessment version is invalid"
        )
    if assessment.assessment_status != IMPACT_ASSESSED_NOT_RATIFIED:
        raise FailClosedRuntimeError(
            "constitutional impact assessment status is invalid"
        )
    proposal = validate_constitutional_amendment_proposal_artifact_v1(
        assessment.amendment_proposal
    )
    if assessment.replay_impact not in REPLAY_IMPACT_CLASSES:
        raise FailClosedRuntimeError(
            "constitutional Replay impact is not recognized"
        )
    if assessment.cro_impact not in CRO_IMPACT_CLASSES:
        raise FailClosedRuntimeError("constitutional CRO impact is not recognized")
    if assessment.production_path_impact not in PRODUCTION_PATH_IMPACT_CLASSES:
        raise FailClosedRuntimeError(
            "constitutional production path impact is not recognized"
        )
    contracts = _normalize_contracts(assessment.affected_contracts)
    invariants = _normalize_invariants(assessment.affected_invariants)
    owners = _normalize_owner_impacts(assessment.owner_impacts)
    if (
        contracts != assessment.affected_contracts
        or invariants != assessment.affected_invariants
        or owners != assessment.owner_impacts
    ):
        raise FailClosedRuntimeError(
            "constitutional impact artifact order is not canonical"
        )
    _validate_target_contract(proposal, contracts)
    specifications = _evidence_specifications(
        proposal=proposal,
        assessing_owner=assessment.assessing_owner,
    )
    evidence = _normalize_evidence(
        values=assessment.evidence_references,
        specifications=specifications,
    )
    expected_classification = _classify_impact(
        contracts=contracts,
        invariants=invariants,
        replay_impact=assessment.replay_impact,
        cro_impact=assessment.cro_impact,
        production_path_impact=assessment.production_path_impact,
        owner_impacts=owners,
    )
    if assessment.impact_classification != expected_classification:
        raise FailClosedRuntimeError(
            "constitutional impact classification is invalid"
        )
    if evidence != assessment.evidence_references:
        raise FailClosedRuntimeError(
            "constitutional impact evidence correlation is invalid"
        )
    invariants_tuple = (
        assessment.che_definition_count,
        assessment.production_hic_family_count,
        assessment.production_owner_chain_count,
        assessment.production_path_count,
        assessment.parallel_production_path_count,
        assessment.human_ratification_performed,
        assessment.amendment_certification_performed,
        assessment.amendment_activation_performed,
        assessment.runtime_mutation_performed,
        assessment.production_behavior_changed,
        assessment.replay_path_created,
        assessment.cro_authority_created,
    )
    if invariants_tuple != (
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
        False,
    ):
        raise FailClosedRuntimeError(
            "constitutional impact boundary invariants are invalid"
        )
    expected_identity = _identity(assessment.identity_payload())
    expected_digest = _digest(assessment.identity_payload())
    if (
        assessment.assessment_identity != expected_identity
        or assessment.artifact_digest != expected_digest
    ):
        raise FailClosedRuntimeError(
            "constitutional impact assessment identity is invalid"
        )
    return assessment


__all__ = [
    "ASSESSOR_AUTHORITY_EVIDENCE",
    "BOUNDED_CONSTITUTIONAL_IMPACT",
    "CONSTITUTIONAL_GOVERNANCE_OWNER",
    "CONSTITUTIONAL_BOUNDARY_IMPACT",
    "CONSTITUTIONAL_IMPACT_ASSESSMENT_ARTIFACT_VERSION",
    "CONSTITUTIONAL_IMPACT_ASSESSMENT_CONTRACT_VERSION",
    "CONTRACT_CONFLICT",
    "CONTRACT_IMPACT_COMPLETENESS_EVIDENCE",
    "CONTRACT_IMPACT_KINDS",
    "CONTRACT_IMPACT_UNRESOLVED",
    "CROSS_CONSTITUTIONAL_IMPACT",
    "CRO_AUTHORITY_EXPANSION_PROPOSED",
    "CRO_IMPACT_CLASSES",
    "CRO_IMPACT_EVIDENCE",
    "CRO_IMPACT_UNRESOLVED",
    "CRO_OBSERVATION_EXTENSION_REQUIRED",
    "CRO_UNCHANGED",
    "DEPENDENCY_IMPACT",
    "DIRECT_MODIFICATION_PROPOSED",
    "IMPACT_ASSESSED_NOT_RATIFIED",
    "IMPACT_ASSESSMENT_EVIDENCE_ORDER",
    "IMPACT_CLASSIFICATIONS",
    "INVARIANT_CONFLICT",
    "INVARIANT_IMPACT_COMPLETENESS_EVIDENCE",
    "INVARIANT_IMPACT_KINDS",
    "INVARIANT_IMPACT_UNRESOLVED",
    "INVARIANT_MODIFICATION_PROPOSED",
    "INVARIANT_PRESERVED",
    "NEW_OWNER_PROPOSED",
    "ONE_PRODUCTION_PATH_PRESERVED",
    "OWNER_IMPACT_COMPLETENESS_EVIDENCE",
    "OWNER_IMPACT_KINDS",
    "OWNER_IMPACT_UNRESOLVED",
    "OWNER_LOCAL_REPLAY_CUSTODIAN",
    "OWNER_REMOVAL_PROPOSED",
    "OWNER_RESPONSIBILITY_CHANGE_PROPOSED",
    "OWNER_RESPONSIBILITY_UNCHANGED",
    "PASSIVE_CONSTITUTIONAL_RUNTIME_OBSERVATORY",
    "PRODUCTION_PATH_CHANGE_PROPOSED",
    "PRODUCTION_PATH_IMPACT_CLASSES",
    "PRODUCTION_PATH_IMPACT_EVIDENCE",
    "PRODUCTION_PATH_IMPACT_UNRESOLVED",
    "PROPOSAL_BINDING_EVIDENCE",
    "REPLAY_CORRELATION_EXTENSION_REQUIRED",
    "REPLAY_IMPACT_CLASSES",
    "REPLAY_IMPACT_EVIDENCE",
    "REPLAY_IMPACT_UNRESOLVED",
    "REPLAY_SAFETY_DEGRADATION_PROPOSED",
    "REPLAY_UNCHANGED",
    "SUCCESSOR_REQUIRED",
    "SUPERSESSION_PROPOSED",
    "TARGET_CONTRACT_IMPACT_KINDS",
    "UNBOUNDED_OWNER_AUTHORITY_PROPOSED",
    "UNRESOLVED_CONSTITUTIONAL_IMPACT",
    "AffectedConstitutionalContractV1",
    "AffectedConstitutionalInvariantV1",
    "ConstitutionalImpactAssessmentArtifactV1",
    "ConstitutionalImpactEvidenceReferenceV1",
    "ConstitutionalOwnerImpactV1",
    "assess_constitutional_impact_v1",
    "validate_affected_constitutional_contract_v1",
    "validate_affected_constitutional_invariant_v1",
    "validate_constitutional_impact_assessment_artifact_v1",
    "validate_constitutional_impact_evidence_reference_v1",
    "validate_constitutional_owner_impact_v1",
]
