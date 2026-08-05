"""Constitutional Gap determination and evidence contract for G70-01.

The contract classifies one proposed implementation responsibility using a
closed, owner-bound evidence set.  Complete evidence yields
``CONSTITUTION_ALREADY_SUFFICIENT``.  Any unsatisfied or absent predicate
yields one immutable ``CONSTITUTIONAL_GAP`` artifact.  Malformed evidence
fails closed.

This module does not propose, approve, certify, or activate an amendment.  It
does not persist Replay, observe through CRO, mutate runtime state, or enter a
production path.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize


CONSTITUTIONAL_GAP_CONTRACT_VERSION = (
    "G70_01_CONSTITUTIONAL_GAP_DETERMINATION_AND_EVIDENCE_CONTRACT_V1"
)
CONSTITUTIONAL_GAP_ARTIFACT_VERSION = "CONSTITUTIONAL_GAP_ARTIFACT_V1"
CONSTITUTIONAL_GAP_SERIALIZATION_VERSION = (
    "CONSTITUTIONAL_GAP_SERIALIZATION_V1"
)

CONSTITUTION_ALREADY_SUFFICIENT = "CONSTITUTION_ALREADY_SUFFICIENT"
CONSTITUTIONAL_GAP = "CONSTITUTIONAL_GAP"
OPEN = "OPEN"

SATISFIED = "SATISFIED"
UNSATISFIED = "UNSATISFIED"
ABSENT = "ABSENT"
EVIDENCE_STATUSES = (SATISFIED, UNSATISFIED, ABSENT)

RESPONSIBILITY_OWNER = "RESPONSIBILITY_OWNER"
G47_DEVELOPMENT_GOVERNANCE_OWNER = "G47_DEVELOPMENT_GOVERNANCE_OWNER"
CONSTITUTIONAL_GOVERNANCE_OWNER = "CONSTITUTIONAL_GOVERNANCE_OWNER"
OWNER_LOCAL_REPLAY_CUSTODIAN = "OWNER_LOCAL_REPLAY_CUSTODIAN"
PASSIVE_CONSTITUTIONAL_RUNTIME_OBSERVATORY = (
    "PASSIVE_CONSTITUTIONAL_RUNTIME_OBSERVATORY"
)
CONSTITUTIONAL_CERTIFICATION_OWNER = "CONSTITUTIONAL_CERTIFICATION_OWNER"

RESPONSIBILITY_IDENTIFIED = "RESPONSIBILITY_IDENTIFIED"
AUTHORITATIVE_OWNER_IDENTIFIED = "AUTHORITATIVE_OWNER_IDENTIFIED"
NORMATIVE_CONTRACT_COMPLETE = "NORMATIVE_CONTRACT_COMPLETE"
CONSTITUTIONAL_VERSION_IDENTIFIED = "CONSTITUTIONAL_VERSION_IDENTIFIED"
IMPLEMENTATION_DERIVABLE_WITHOUT_HISTORICAL_BEHAVIOR = (
    "IMPLEMENTATION_DERIVABLE_WITHOUT_HISTORICAL_BEHAVIOR"
)
CERTIFIED_REUSE_ASSESSED = "CERTIFIED_REUSE_ASSESSED"
PREDECESSOR_CONTRACTS_COMPLETE = "PREDECESSOR_CONTRACTS_COMPLETE"
FAILURE_SEMANTICS_COMPLETE = "FAILURE_SEMANTICS_COMPLETE"
OWNER_EVIDENCE_COMPLETE = "OWNER_EVIDENCE_COMPLETE"
REPLAY_EVIDENCE_COMPLETE = "REPLAY_EVIDENCE_COMPLETE"
CRO_OBSERVATION_COMPLETE = "CRO_OBSERVATION_COMPLETE"
LAYER_MUTATION_AUTHORITY_SATISFIED = "LAYER_MUTATION_AUTHORITY_SATISFIED"
CERTIFICATION_REQUIREMENTS_COMPLETE = "CERTIFICATION_REQUIREMENTS_COMPLETE"


@dataclass(frozen=True, slots=True)
class ConstitutionalGapPredicateDefinitionV1:
    """One closed Constitutional sufficiency predicate and its evidence owner."""

    predicate_id: str
    evidence_owner_rule: str


CONSTITUTIONAL_GAP_PREDICATE_DEFINITIONS = (
    ConstitutionalGapPredicateDefinitionV1(
        RESPONSIBILITY_IDENTIFIED, RESPONSIBILITY_OWNER
    ),
    ConstitutionalGapPredicateDefinitionV1(
        AUTHORITATIVE_OWNER_IDENTIFIED, G47_DEVELOPMENT_GOVERNANCE_OWNER
    ),
    ConstitutionalGapPredicateDefinitionV1(
        NORMATIVE_CONTRACT_COMPLETE, RESPONSIBILITY_OWNER
    ),
    ConstitutionalGapPredicateDefinitionV1(
        CONSTITUTIONAL_VERSION_IDENTIFIED, RESPONSIBILITY_OWNER
    ),
    ConstitutionalGapPredicateDefinitionV1(
        IMPLEMENTATION_DERIVABLE_WITHOUT_HISTORICAL_BEHAVIOR,
        G47_DEVELOPMENT_GOVERNANCE_OWNER,
    ),
    ConstitutionalGapPredicateDefinitionV1(
        CERTIFIED_REUSE_ASSESSED, G47_DEVELOPMENT_GOVERNANCE_OWNER
    ),
    ConstitutionalGapPredicateDefinitionV1(
        PREDECESSOR_CONTRACTS_COMPLETE, RESPONSIBILITY_OWNER
    ),
    ConstitutionalGapPredicateDefinitionV1(
        FAILURE_SEMANTICS_COMPLETE, RESPONSIBILITY_OWNER
    ),
    ConstitutionalGapPredicateDefinitionV1(
        OWNER_EVIDENCE_COMPLETE, RESPONSIBILITY_OWNER
    ),
    ConstitutionalGapPredicateDefinitionV1(
        REPLAY_EVIDENCE_COMPLETE, OWNER_LOCAL_REPLAY_CUSTODIAN
    ),
    ConstitutionalGapPredicateDefinitionV1(
        CRO_OBSERVATION_COMPLETE, PASSIVE_CONSTITUTIONAL_RUNTIME_OBSERVATORY
    ),
    ConstitutionalGapPredicateDefinitionV1(
        LAYER_MUTATION_AUTHORITY_SATISFIED, CONSTITUTIONAL_GOVERNANCE_OWNER
    ),
    ConstitutionalGapPredicateDefinitionV1(
        CERTIFICATION_REQUIREMENTS_COMPLETE, CONSTITUTIONAL_CERTIFICATION_OWNER
    ),
)
CONSTITUTIONAL_GAP_PREDICATE_ORDER = tuple(
    item.predicate_id for item in CONSTITUTIONAL_GAP_PREDICATE_DEFINITIONS
)

_GAP_IDENTITY_PREFIX = "CONSTITUTIONAL-GAP-"
_DETERMINATION_IDENTITY_PREFIX = "CONSTITUTIONAL-GAP-DETERMINATION-"


def _require_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise FailClosedRuntimeError(
            f"constitutional gap {field_name} is absent or malformed"
        )
    return value


def _require_optional_text(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    return _require_text(value, field_name)


def _require_sha256(value: Any, field_name: str) -> str:
    text = _require_text(value, field_name)
    if not text.startswith("sha256:") or len(text) != 71:
        raise FailClosedRuntimeError(
            f"constitutional gap {field_name} is not a SHA-256 reference"
        )
    try:
        int(text[7:], 16)
    except ValueError as exc:
        raise FailClosedRuntimeError(
            f"constitutional gap {field_name} is not a SHA-256 reference"
        ) from exc
    return text


def _identity(prefix: str, value: Any) -> str:
    digest = sha256(canonical_serialize(value).encode("utf-8")).hexdigest()
    return prefix + digest


def _digest(value: Any) -> str:
    return "sha256:" + sha256(
        canonical_serialize(value).encode("utf-8")
    ).hexdigest()


def _require_exact_keys(
    value: Any,
    keys: set[str],
    field_name: str,
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != keys:
        raise FailClosedRuntimeError(
            f"constitutional gap {field_name} is malformed"
        )
    return value


def _expected_evidence_owner(
    predicate_id: str,
    responsibility_owner: str,
) -> str:
    definition = next(
        (
            item
            for item in CONSTITUTIONAL_GAP_PREDICATE_DEFINITIONS
            if item.predicate_id == predicate_id
        ),
        None,
    )
    if definition is None:
        raise FailClosedRuntimeError(
            "constitutional gap evidence predicate is not recognized"
        )
    if definition.evidence_owner_rule == RESPONSIBILITY_OWNER:
        return responsibility_owner
    return definition.evidence_owner_rule


@dataclass(frozen=True, slots=True)
class ConstitutionalGapEvidenceReferenceV1:
    """Immutable owner-produced evidence for one sufficiency predicate."""

    predicate_id: str
    evidence_status: str
    producing_owner: str
    artifact_identity: str | None
    artifact_digest: str | None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "predicate_id",
            _require_text(self.predicate_id, "predicate_id"),
        )
        if self.predicate_id not in CONSTITUTIONAL_GAP_PREDICATE_ORDER:
            raise FailClosedRuntimeError(
                "constitutional gap evidence predicate is not recognized"
            )
        if self.evidence_status not in EVIDENCE_STATUSES:
            raise FailClosedRuntimeError(
                "constitutional gap evidence status is not recognized"
            )
        object.__setattr__(
            self,
            "producing_owner",
            _require_text(self.producing_owner, "producing_owner"),
        )
        if self.evidence_status == ABSENT:
            if self.artifact_identity is not None or self.artifact_digest is not None:
                raise FailClosedRuntimeError(
                    "absent constitutional gap evidence cannot claim an artifact"
                )
        else:
            object.__setattr__(
                self,
                "artifact_identity",
                _require_text(self.artifact_identity, "artifact_identity"),
            )
            object.__setattr__(
                self,
                "artifact_digest",
                _require_sha256(self.artifact_digest, "artifact_digest"),
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "predicate_id": self.predicate_id,
            "evidence_status": self.evidence_status,
            "producing_owner": self.producing_owner,
            "artifact_identity": self.artifact_identity,
            "artifact_digest": self.artifact_digest,
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "ConstitutionalGapEvidenceReferenceV1":
        exact = _require_exact_keys(
            value,
            {
                "predicate_id",
                "evidence_status",
                "producing_owner",
                "artifact_identity",
                "artifact_digest",
            },
            "evidence reference",
        )
        return cls(**dict(exact))


@dataclass(frozen=True, slots=True)
class ConstitutionalGapArtifactV1:
    """One immutable, open Constitutional Gap and all determining evidence."""

    contract_version: str
    artifact_version: str
    serialization_version: str
    gap_identity: str
    artifact_digest: str
    determination_identity: str
    implementation_request_identity: str
    implementation_responsibility: str
    responsibility_owner: str
    constitutional_baseline_identity: str
    gap_status: str
    ordered_gap_predicates: tuple[str, ...]
    first_gap_predicate: str
    ordered_evidence: tuple[ConstitutionalGapEvidenceReferenceV1, ...]
    determined_at: str

    def __post_init__(self) -> None:
        for field_name in (
            "contract_version",
            "artifact_version",
            "serialization_version",
            "gap_identity",
            "determination_identity",
            "implementation_request_identity",
            "implementation_responsibility",
            "responsibility_owner",
            "constitutional_baseline_identity",
            "gap_status",
            "first_gap_predicate",
            "determined_at",
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
        if (
            not isinstance(self.ordered_gap_predicates, tuple)
            or not self.ordered_gap_predicates
            or any(
                item not in CONSTITUTIONAL_GAP_PREDICATE_ORDER
                for item in self.ordered_gap_predicates
            )
            or len(self.ordered_gap_predicates)
            != len(set(self.ordered_gap_predicates))
        ):
            raise FailClosedRuntimeError(
                "constitutional gap predicate sequence is malformed"
            )
        if (
            not isinstance(self.ordered_evidence, tuple)
            or any(
                not isinstance(item, ConstitutionalGapEvidenceReferenceV1)
                for item in self.ordered_evidence
            )
        ):
            raise FailClosedRuntimeError(
                "constitutional gap evidence sequence is malformed"
            )

    def identity_payload(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "artifact_version": self.artifact_version,
            "serialization_version": self.serialization_version,
            "determination_identity": self.determination_identity,
            "implementation_request_identity": self.implementation_request_identity,
            "implementation_responsibility": self.implementation_responsibility,
            "responsibility_owner": self.responsibility_owner,
            "constitutional_baseline_identity": self.constitutional_baseline_identity,
            "gap_status": self.gap_status,
            "ordered_gap_predicates": list(self.ordered_gap_predicates),
            "first_gap_predicate": self.first_gap_predicate,
            "ordered_evidence": [item.to_dict() for item in self.ordered_evidence],
            "determined_at": self.determined_at,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "gap_identity": self.gap_identity,
            "artifact_digest": self.artifact_digest,
            **self.identity_payload(),
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "ConstitutionalGapArtifactV1":
        exact = _require_exact_keys(
            value,
            {
                "contract_version",
                "artifact_version",
                "serialization_version",
                "gap_identity",
                "artifact_digest",
                "determination_identity",
                "implementation_request_identity",
                "implementation_responsibility",
                "responsibility_owner",
                "constitutional_baseline_identity",
                "gap_status",
                "ordered_gap_predicates",
                "first_gap_predicate",
                "ordered_evidence",
                "determined_at",
            },
            "artifact",
        )
        if not isinstance(exact["ordered_gap_predicates"], list) or not isinstance(
            exact["ordered_evidence"], list
        ):
            raise FailClosedRuntimeError(
                "constitutional gap artifact sequences are malformed"
            )
        return cls(
            contract_version=exact["contract_version"],
            artifact_version=exact["artifact_version"],
            serialization_version=exact["serialization_version"],
            gap_identity=exact["gap_identity"],
            artifact_digest=exact["artifact_digest"],
            determination_identity=exact["determination_identity"],
            implementation_request_identity=exact[
                "implementation_request_identity"
            ],
            implementation_responsibility=exact["implementation_responsibility"],
            responsibility_owner=exact["responsibility_owner"],
            constitutional_baseline_identity=exact[
                "constitutional_baseline_identity"
            ],
            gap_status=exact["gap_status"],
            ordered_gap_predicates=tuple(exact["ordered_gap_predicates"]),
            first_gap_predicate=exact["first_gap_predicate"],
            ordered_evidence=tuple(
                ConstitutionalGapEvidenceReferenceV1.from_dict(item)
                for item in exact["ordered_evidence"]
            ),
            determined_at=exact["determined_at"],
        )


@dataclass(frozen=True, slots=True)
class ConstitutionalGapDeterminationResultV1:
    """Immutable binary authorization result; never an amendment decision."""

    contract_version: str
    determination_identity: str
    implementation_request_identity: str
    implementation_responsibility: str
    responsibility_owner: str
    constitutional_baseline_identity: str
    disposition: str
    ordered_evidence: tuple[ConstitutionalGapEvidenceReferenceV1, ...]
    gap_artifact: ConstitutionalGapArtifactV1 | None
    determined_at: str
    che_definition_count: int = 1
    production_hic_family_count: int = 1
    production_owner_chain_count: int = 1
    production_path_count: int = 1
    parallel_production_path_count: int = 0
    amendment_authority_created: bool = False
    runtime_mutation_performed: bool = False
    production_behavior_changed: bool = False
    replay_path_created: bool = False
    cro_authority_created: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "contract_version",
            "determination_identity",
            "implementation_request_identity",
            "implementation_responsibility",
            "responsibility_owner",
            "constitutional_baseline_identity",
            "disposition",
            "determined_at",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_text(getattr(self, field_name), field_name),
            )
        if (
            not isinstance(self.ordered_evidence, tuple)
            or any(
                not isinstance(item, ConstitutionalGapEvidenceReferenceV1)
                for item in self.ordered_evidence
            )
        ):
            raise FailClosedRuntimeError(
                "constitutional gap determination evidence is malformed"
            )
        if self.gap_artifact is not None and not isinstance(
            self.gap_artifact, ConstitutionalGapArtifactV1
        ):
            raise FailClosedRuntimeError(
                "constitutional gap determination artifact is malformed"
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
                    "constitutional gap determination topology is malformed"
                )
        for field_name in (
            "amendment_authority_created",
            "runtime_mutation_performed",
            "production_behavior_changed",
            "replay_path_created",
            "cro_authority_created",
        ):
            if not isinstance(getattr(self, field_name), bool):
                raise FailClosedRuntimeError(
                    "constitutional gap determination boundary is malformed"
                )

    def identity_payload(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "implementation_request_identity": self.implementation_request_identity,
            "implementation_responsibility": self.implementation_responsibility,
            "responsibility_owner": self.responsibility_owner,
            "constitutional_baseline_identity": self.constitutional_baseline_identity,
            "disposition": self.disposition,
            "ordered_evidence": [item.to_dict() for item in self.ordered_evidence],
            "determined_at": self.determined_at,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "determination_identity": self.determination_identity,
            **self.identity_payload(),
            "gap_artifact": (
                None if self.gap_artifact is None else self.gap_artifact.to_dict()
            ),
            "che_definition_count": self.che_definition_count,
            "production_hic_family_count": self.production_hic_family_count,
            "production_owner_chain_count": self.production_owner_chain_count,
            "production_path_count": self.production_path_count,
            "parallel_production_path_count": self.parallel_production_path_count,
            "amendment_authority_created": self.amendment_authority_created,
            "runtime_mutation_performed": self.runtime_mutation_performed,
            "production_behavior_changed": self.production_behavior_changed,
            "replay_path_created": self.replay_path_created,
            "cro_authority_created": self.cro_authority_created,
        }


def validate_constitutional_gap_evidence_reference_v1(
    *,
    value: ConstitutionalGapEvidenceReferenceV1 | Mapping[str, Any],
    responsibility_owner: str,
) -> ConstitutionalGapEvidenceReferenceV1:
    """Validate one reference and its exact Constitutional evidence owner."""

    owner = _require_text(responsibility_owner, "responsibility_owner")
    evidence = (
        value
        if isinstance(value, ConstitutionalGapEvidenceReferenceV1)
        else ConstitutionalGapEvidenceReferenceV1.from_dict(value)
    )
    if evidence.producing_owner != _expected_evidence_owner(
        evidence.predicate_id, owner
    ):
        raise FailClosedRuntimeError(
            "constitutional gap evidence is not bound to its required owner"
        )
    return evidence


def _normalize_evidence(
    *,
    evidence_references: Sequence[
        ConstitutionalGapEvidenceReferenceV1 | Mapping[str, Any]
    ],
    responsibility_owner: str,
) -> tuple[ConstitutionalGapEvidenceReferenceV1, ...]:
    if isinstance(evidence_references, (str, bytes)) or not isinstance(
        evidence_references, Sequence
    ):
        raise FailClosedRuntimeError(
            "constitutional gap evidence collection is malformed"
        )
    by_predicate: dict[str, ConstitutionalGapEvidenceReferenceV1] = {}
    for candidate in evidence_references:
        evidence = validate_constitutional_gap_evidence_reference_v1(
            value=candidate,
            responsibility_owner=responsibility_owner,
        )
        if evidence.predicate_id in by_predicate:
            raise FailClosedRuntimeError(
                "constitutional gap evidence predicate is duplicated"
            )
        by_predicate[evidence.predicate_id] = evidence
    ordered = []
    for predicate_id in CONSTITUTIONAL_GAP_PREDICATE_ORDER:
        ordered.append(
            by_predicate.get(predicate_id)
            or ConstitutionalGapEvidenceReferenceV1(
                predicate_id=predicate_id,
                evidence_status=ABSENT,
                producing_owner=_expected_evidence_owner(
                    predicate_id, responsibility_owner
                ),
                artifact_identity=None,
                artifact_digest=None,
            )
        )
    return tuple(ordered)


def _validate_ordered_evidence(
    *,
    ordered_evidence: tuple[ConstitutionalGapEvidenceReferenceV1, ...],
    responsibility_owner: str,
) -> tuple[ConstitutionalGapEvidenceReferenceV1, ...]:
    if (
        not isinstance(ordered_evidence, tuple)
        or tuple(item.predicate_id for item in ordered_evidence)
        != CONSTITUTIONAL_GAP_PREDICATE_ORDER
    ):
        raise FailClosedRuntimeError(
            "constitutional gap evidence order is not canonical"
        )
    return tuple(
        validate_constitutional_gap_evidence_reference_v1(
            value=item,
            responsibility_owner=responsibility_owner,
        )
        for item in ordered_evidence
    )


def _create_gap_artifact(
    *,
    determination_identity: str,
    implementation_request_identity: str,
    implementation_responsibility: str,
    responsibility_owner: str,
    constitutional_baseline_identity: str,
    ordered_evidence: tuple[ConstitutionalGapEvidenceReferenceV1, ...],
    determined_at: str,
) -> ConstitutionalGapArtifactV1:
    gap_predicates = tuple(
        item.predicate_id
        for item in ordered_evidence
        if item.evidence_status != SATISFIED
    )
    provisional = ConstitutionalGapArtifactV1(
        contract_version=CONSTITUTIONAL_GAP_CONTRACT_VERSION,
        artifact_version=CONSTITUTIONAL_GAP_ARTIFACT_VERSION,
        serialization_version=CONSTITUTIONAL_GAP_SERIALIZATION_VERSION,
        gap_identity="PENDING-CONSTITUTIONAL-GAP-IDENTITY",
        artifact_digest="sha256:" + ("0" * 64),
        determination_identity=determination_identity,
        implementation_request_identity=implementation_request_identity,
        implementation_responsibility=implementation_responsibility,
        responsibility_owner=responsibility_owner,
        constitutional_baseline_identity=constitutional_baseline_identity,
        gap_status=OPEN,
        ordered_gap_predicates=gap_predicates,
        first_gap_predicate=gap_predicates[0],
        ordered_evidence=ordered_evidence,
        determined_at=determined_at,
    )
    return replace(
        provisional,
        gap_identity=_identity(_GAP_IDENTITY_PREFIX, provisional.identity_payload()),
        artifact_digest=_digest(provisional.identity_payload()),
    )


def determine_constitutional_gap_v1(
    *,
    implementation_request_identity: str,
    implementation_responsibility: str,
    responsibility_owner: str,
    constitutional_baseline_identity: str,
    evidence_references: Sequence[
        ConstitutionalGapEvidenceReferenceV1 | Mapping[str, Any]
    ],
    determined_at: str,
) -> ConstitutionalGapDeterminationResultV1:
    """Return the sole binary authorization classification for one responsibility."""

    request_identity = _require_text(
        implementation_request_identity, "implementation_request_identity"
    )
    responsibility = _require_text(
        implementation_responsibility, "implementation_responsibility"
    )
    owner = _require_text(responsibility_owner, "responsibility_owner")
    baseline = _require_text(
        constitutional_baseline_identity, "constitutional_baseline_identity"
    )
    observed = _require_text(determined_at, "determined_at")
    ordered_evidence = _normalize_evidence(
        evidence_references=evidence_references,
        responsibility_owner=owner,
    )
    disposition = (
        CONSTITUTION_ALREADY_SUFFICIENT
        if all(item.evidence_status == SATISFIED for item in ordered_evidence)
        else CONSTITUTIONAL_GAP
    )
    provisional = ConstitutionalGapDeterminationResultV1(
        contract_version=CONSTITUTIONAL_GAP_CONTRACT_VERSION,
        determination_identity="PENDING-CONSTITUTIONAL-GAP-DETERMINATION",
        implementation_request_identity=request_identity,
        implementation_responsibility=responsibility,
        responsibility_owner=owner,
        constitutional_baseline_identity=baseline,
        disposition=disposition,
        ordered_evidence=ordered_evidence,
        gap_artifact=None,
        determined_at=observed,
    )
    determination_identity = _identity(
        _DETERMINATION_IDENTITY_PREFIX,
        provisional.identity_payload(),
    )
    gap_artifact = None
    if disposition == CONSTITUTIONAL_GAP:
        gap_artifact = _create_gap_artifact(
            determination_identity=determination_identity,
            implementation_request_identity=request_identity,
            implementation_responsibility=responsibility,
            responsibility_owner=owner,
            constitutional_baseline_identity=baseline,
            ordered_evidence=ordered_evidence,
            determined_at=observed,
        )
    return validate_constitutional_gap_determination_result_v1(
        replace(
            provisional,
            determination_identity=determination_identity,
            gap_artifact=gap_artifact,
        )
    )


def validate_constitutional_gap_artifact_v1(
    value: ConstitutionalGapArtifactV1 | Mapping[str, Any],
) -> ConstitutionalGapArtifactV1:
    """Validate version, owner evidence, ordering, status, and content identity."""

    artifact = (
        value
        if isinstance(value, ConstitutionalGapArtifactV1)
        else ConstitutionalGapArtifactV1.from_dict(value)
    )
    if (
        artifact.contract_version != CONSTITUTIONAL_GAP_CONTRACT_VERSION
        or artifact.artifact_version != CONSTITUTIONAL_GAP_ARTIFACT_VERSION
        or artifact.serialization_version
        != CONSTITUTIONAL_GAP_SERIALIZATION_VERSION
    ):
        raise FailClosedRuntimeError(
            "constitutional gap artifact version is invalid"
        )
    if artifact.gap_status != OPEN:
        raise FailClosedRuntimeError("constitutional gap status is invalid")
    evidence = _validate_ordered_evidence(
        ordered_evidence=artifact.ordered_evidence,
        responsibility_owner=artifact.responsibility_owner,
    )
    expected_gaps = tuple(
        item.predicate_id for item in evidence if item.evidence_status != SATISFIED
    )
    if (
        not expected_gaps
        or artifact.ordered_gap_predicates != expected_gaps
        or artifact.first_gap_predicate != expected_gaps[0]
    ):
        raise FailClosedRuntimeError(
            "constitutional gap predicate reduction is invalid"
        )
    expected_identity = _identity(
        _GAP_IDENTITY_PREFIX, artifact.identity_payload()
    )
    expected_digest = _digest(artifact.identity_payload())
    if (
        artifact.gap_identity != expected_identity
        or artifact.artifact_digest != expected_digest
    ):
        raise FailClosedRuntimeError(
            "constitutional gap artifact identity is invalid"
        )
    return artifact


def validate_constitutional_gap_determination_result_v1(
    result: ConstitutionalGapDeterminationResultV1,
) -> ConstitutionalGapDeterminationResultV1:
    """Validate binary disposition, artifact correlation, and topology invariants."""

    if not isinstance(result, ConstitutionalGapDeterminationResultV1):
        raise FailClosedRuntimeError(
            "constitutional gap determination result is malformed"
        )
    if result.contract_version != CONSTITUTIONAL_GAP_CONTRACT_VERSION:
        raise FailClosedRuntimeError(
            "constitutional gap determination contract version is invalid"
        )
    evidence = _validate_ordered_evidence(
        ordered_evidence=result.ordered_evidence,
        responsibility_owner=result.responsibility_owner,
    )
    expected_disposition = (
        CONSTITUTION_ALREADY_SUFFICIENT
        if all(item.evidence_status == SATISFIED for item in evidence)
        else CONSTITUTIONAL_GAP
    )
    if result.disposition != expected_disposition:
        raise FailClosedRuntimeError(
            "constitutional gap determination disposition is invalid"
        )
    expected_identity = _identity(
        _DETERMINATION_IDENTITY_PREFIX, result.identity_payload()
    )
    if result.determination_identity != expected_identity:
        raise FailClosedRuntimeError(
            "constitutional gap determination identity is invalid"
        )
    if expected_disposition == CONSTITUTION_ALREADY_SUFFICIENT:
        if result.gap_artifact is not None:
            raise FailClosedRuntimeError(
                "sufficient Constitution cannot carry a Gap artifact"
            )
    else:
        if result.gap_artifact is None:
            raise FailClosedRuntimeError(
                "constitutional gap disposition requires a Gap artifact"
            )
        artifact = validate_constitutional_gap_artifact_v1(result.gap_artifact)
        if (
            artifact.determination_identity != result.determination_identity
            or artifact.implementation_request_identity
            != result.implementation_request_identity
            or artifact.implementation_responsibility
            != result.implementation_responsibility
            or artifact.responsibility_owner != result.responsibility_owner
            or artifact.constitutional_baseline_identity
            != result.constitutional_baseline_identity
            or artifact.ordered_evidence != result.ordered_evidence
            or artifact.determined_at != result.determined_at
        ):
            raise FailClosedRuntimeError(
                "constitutional gap artifact is not bound to its determination"
            )
    invariants = (
        result.che_definition_count,
        result.production_hic_family_count,
        result.production_owner_chain_count,
        result.production_path_count,
        result.parallel_production_path_count,
        result.amendment_authority_created,
        result.runtime_mutation_performed,
        result.production_behavior_changed,
        result.replay_path_created,
        result.cro_authority_created,
    )
    if invariants != (1, 1, 1, 1, 0, False, False, False, False, False):
        raise FailClosedRuntimeError(
            "constitutional gap contract boundary invariants are invalid"
        )
    return result


def serialize_constitutional_gap_artifact_v1(
    artifact: ConstitutionalGapArtifactV1 | Mapping[str, Any],
) -> str:
    """Return the sole canonical versioned JSON representation; write nothing."""

    validated = validate_constitutional_gap_artifact_v1(artifact)
    return canonical_serialize(validated.to_dict())


def deserialize_constitutional_gap_artifact_v1(
    serialized: str | bytes,
) -> ConstitutionalGapArtifactV1:
    """Parse only canonical V1 serialization and validate it fail closed."""

    if isinstance(serialized, bytes):
        try:
            source = serialized.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise FailClosedRuntimeError(
                "constitutional gap serialization is not UTF-8"
            ) from exc
    elif isinstance(serialized, str):
        source = serialized
    else:
        raise FailClosedRuntimeError(
            "constitutional gap serialization is malformed"
        )
    try:
        decoded = json.loads(source)
    except json.JSONDecodeError as exc:
        raise FailClosedRuntimeError(
            "constitutional gap serialization is not valid JSON"
        ) from exc
    artifact = validate_constitutional_gap_artifact_v1(decoded)
    if canonical_serialize(artifact.to_dict()) != source:
        raise FailClosedRuntimeError(
            "constitutional gap serialization is not canonical"
        )
    return artifact


__all__ = [
    "ABSENT",
    "CONSTITUTION_ALREADY_SUFFICIENT",
    "CONSTITUTIONAL_GAP",
    "CONSTITUTIONAL_GAP_ARTIFACT_VERSION",
    "CONSTITUTIONAL_GAP_CONTRACT_VERSION",
    "CONSTITUTIONAL_GAP_PREDICATE_DEFINITIONS",
    "CONSTITUTIONAL_GAP_PREDICATE_ORDER",
    "CONSTITUTIONAL_GAP_SERIALIZATION_VERSION",
    "EVIDENCE_STATUSES",
    "OPEN",
    "SATISFIED",
    "UNSATISFIED",
    "ConstitutionalGapArtifactV1",
    "ConstitutionalGapDeterminationResultV1",
    "ConstitutionalGapEvidenceReferenceV1",
    "ConstitutionalGapPredicateDefinitionV1",
    "deserialize_constitutional_gap_artifact_v1",
    "determine_constitutional_gap_v1",
    "serialize_constitutional_gap_artifact_v1",
    "validate_constitutional_gap_artifact_v1",
    "validate_constitutional_gap_determination_result_v1",
    "validate_constitutional_gap_evidence_reference_v1",
]
