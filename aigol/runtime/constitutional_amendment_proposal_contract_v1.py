"""Constitutional Amendment Proposal contract for G70-02.

The contract creates and validates one immutable, versioned proposal bound to
an open G70-01 Constitutional Gap and exact owner-produced evidence.  A valid
proposal remains proposal-only and unassessed.  It has no ratification,
certification, activation, runtime, production, Replay-writing, or CRO
authority.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

from aigol.runtime.constitutional_gap_determination_evidence_contract_v1 import (
    ConstitutionalGapArtifactV1,
    validate_constitutional_gap_artifact_v1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize


CONSTITUTIONAL_AMENDMENT_PROPOSAL_CONTRACT_VERSION = (
    "G70_02_CONSTITUTIONAL_AMENDMENT_PROPOSAL_CONTRACT_V1"
)
CONSTITUTIONAL_AMENDMENT_PROPOSAL_ARTIFACT_VERSION = (
    "CONSTITUTIONAL_AMENDMENT_PROPOSAL_ARTIFACT_V1"
)
CONSTITUTIONAL_AMENDMENT_PROPOSAL_SERIALIZATION_VERSION = (
    "CONSTITUTIONAL_AMENDMENT_PROPOSAL_SERIALIZATION_V1"
)

PROPOSAL_ONLY_UNASSESSED = "PROPOSAL_ONLY_UNASSESSED"
CONSTITUTIONAL_LAYERS = ("L0", "L1", "L2", "L3", "L4")

GAP_DETERMINATION_EVIDENCE = "GAP_DETERMINATION_EVIDENCE"
PROPOSER_AUTHORITY_EVIDENCE = "PROPOSER_AUTHORITY_EVIDENCE"
TARGET_CONSTITUTIONAL_ARTIFACT_EVIDENCE = (
    "TARGET_CONSTITUTIONAL_ARTIFACT_EVIDENCE"
)
CONSTITUTIONAL_BASELINE_EVIDENCE = "CONSTITUTIONAL_BASELINE_EVIDENCE"
PREVIOUS_PROPOSAL_EVIDENCE = "PREVIOUS_PROPOSAL_EVIDENCE"

BASE_PROPOSAL_EVIDENCE_ORDER = (
    GAP_DETERMINATION_EVIDENCE,
    PROPOSER_AUTHORITY_EVIDENCE,
    TARGET_CONSTITUTIONAL_ARTIFACT_EVIDENCE,
    CONSTITUTIONAL_BASELINE_EVIDENCE,
)
CONSTITUTIONAL_GOVERNANCE_OWNER = "CONSTITUTIONAL_GOVERNANCE_OWNER"

_PROPOSAL_IDENTITY_PREFIX = "CONSTITUTIONAL-AMENDMENT-PROPOSAL-"


def _require_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise FailClosedRuntimeError(
            f"constitutional amendment proposal {field_name} is absent or malformed"
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
            f"constitutional amendment proposal {field_name} is not a SHA-256 reference"
        )
    try:
        int(text[7:], 16)
    except ValueError as exc:
        raise FailClosedRuntimeError(
            f"constitutional amendment proposal {field_name} is not a SHA-256 reference"
        ) from exc
    return text


def _require_optional_sha256(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    return _require_sha256(value, field_name)


def _require_positive_integer(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise FailClosedRuntimeError(
            f"constitutional amendment proposal {field_name} is malformed"
        )
    return value


def _require_exact_keys(
    value: Any,
    keys: set[str],
    field_name: str,
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != keys:
        raise FailClosedRuntimeError(
            f"constitutional amendment proposal {field_name} is malformed"
        )
    return value


def _identity(value: Any) -> str:
    return _PROPOSAL_IDENTITY_PREFIX + sha256(
        canonical_serialize(value).encode("utf-8")
    ).hexdigest()


def _digest(value: Any) -> str:
    return "sha256:" + sha256(
        canonical_serialize(value).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True, slots=True)
class ConstitutionalAmendmentProposalEvidenceReferenceV1:
    """One immutable owner-produced reference required by a proposal."""

    evidence_role: str
    producing_owner: str
    artifact_identity: str
    artifact_digest: str

    def __post_init__(self) -> None:
        if self.evidence_role not in {
            *BASE_PROPOSAL_EVIDENCE_ORDER,
            PREVIOUS_PROPOSAL_EVIDENCE,
        }:
            raise FailClosedRuntimeError(
                "constitutional amendment proposal evidence role is not recognized"
            )
        for field_name in (
            "producing_owner",
            "artifact_identity",
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
    ) -> "ConstitutionalAmendmentProposalEvidenceReferenceV1":
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
class ConstitutionalAmendmentProposalArtifactV1:
    """Immutable proposal-only artifact; never amendment authority."""

    contract_version: str
    artifact_version: str
    serialization_version: str
    proposal_identity: str
    artifact_digest: str
    proposal_revision: int
    previous_proposal_identity: str | None
    previous_proposal_digest: str | None
    proposal_status: str
    constitutional_gap: ConstitutionalGapArtifactV1
    constitutional_baseline_identity: str
    constitutional_baseline_digest: str
    proposing_owner: str
    target_constitutional_owner: str
    target_constitutional_layer: str
    target_constitutional_artifact_identity: str
    target_constitutional_artifact_version: str
    target_constitutional_artifact_digest: str
    proposed_successor_version: str
    proposal_title: str
    normative_change_statement: str
    proposal_rationale: str
    evidence_references: tuple[
        ConstitutionalAmendmentProposalEvidenceReferenceV1, ...
    ]
    proposed_at: str
    che_definition_count: int = 1
    production_hic_family_count: int = 1
    production_owner_chain_count: int = 1
    production_path_count: int = 1
    parallel_production_path_count: int = 0
    impact_assessment_performed: bool = False
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
            "serialization_version",
            "proposal_identity",
            "proposal_status",
            "constitutional_baseline_identity",
            "proposing_owner",
            "target_constitutional_owner",
            "target_constitutional_artifact_identity",
            "target_constitutional_artifact_version",
            "proposed_successor_version",
            "proposal_title",
            "normative_change_statement",
            "proposal_rationale",
            "proposed_at",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_text(getattr(self, field_name), field_name),
            )
        for field_name in (
            "artifact_digest",
            "constitutional_baseline_digest",
            "target_constitutional_artifact_digest",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_sha256(getattr(self, field_name), field_name),
            )
        object.__setattr__(
            self,
            "previous_proposal_identity",
            _require_optional_text(
                self.previous_proposal_identity, "previous_proposal_identity"
            ),
        )
        object.__setattr__(
            self,
            "previous_proposal_digest",
            _require_optional_sha256(
                self.previous_proposal_digest, "previous_proposal_digest"
            ),
        )
        _require_positive_integer(self.proposal_revision, "proposal_revision")
        if self.target_constitutional_layer not in CONSTITUTIONAL_LAYERS:
            raise FailClosedRuntimeError(
                "constitutional amendment proposal target layer is not recognized"
            )
        if not isinstance(self.constitutional_gap, ConstitutionalGapArtifactV1):
            raise FailClosedRuntimeError(
                "constitutional amendment proposal Gap artifact is malformed"
            )
        if (
            not isinstance(self.evidence_references, tuple)
            or any(
                not isinstance(
                    item,
                    ConstitutionalAmendmentProposalEvidenceReferenceV1,
                )
                for item in self.evidence_references
            )
        ):
            raise FailClosedRuntimeError(
                "constitutional amendment proposal evidence sequence is malformed"
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
                    "constitutional amendment proposal topology is malformed"
                )
        for field_name in (
            "impact_assessment_performed",
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
                    "constitutional amendment proposal boundary is malformed"
                )

    def identity_payload(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "artifact_version": self.artifact_version,
            "serialization_version": self.serialization_version,
            "proposal_revision": self.proposal_revision,
            "previous_proposal_identity": self.previous_proposal_identity,
            "previous_proposal_digest": self.previous_proposal_digest,
            "proposal_status": self.proposal_status,
            "constitutional_gap": self.constitutional_gap.to_dict(),
            "constitutional_baseline_identity": self.constitutional_baseline_identity,
            "constitutional_baseline_digest": self.constitutional_baseline_digest,
            "proposing_owner": self.proposing_owner,
            "target_constitutional_owner": self.target_constitutional_owner,
            "target_constitutional_layer": self.target_constitutional_layer,
            "target_constitutional_artifact_identity": (
                self.target_constitutional_artifact_identity
            ),
            "target_constitutional_artifact_version": (
                self.target_constitutional_artifact_version
            ),
            "target_constitutional_artifact_digest": (
                self.target_constitutional_artifact_digest
            ),
            "proposed_successor_version": self.proposed_successor_version,
            "proposal_title": self.proposal_title,
            "normative_change_statement": self.normative_change_statement,
            "proposal_rationale": self.proposal_rationale,
            "evidence_references": [
                item.to_dict() for item in self.evidence_references
            ],
            "proposed_at": self.proposed_at,
            "che_definition_count": self.che_definition_count,
            "production_hic_family_count": self.production_hic_family_count,
            "production_owner_chain_count": self.production_owner_chain_count,
            "production_path_count": self.production_path_count,
            "parallel_production_path_count": self.parallel_production_path_count,
            "impact_assessment_performed": self.impact_assessment_performed,
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
            "proposal_identity": self.proposal_identity,
            "artifact_digest": self.artifact_digest,
            **self.identity_payload(),
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "ConstitutionalAmendmentProposalArtifactV1":
        exact = _require_exact_keys(
            value,
            {
                "contract_version",
                "artifact_version",
                "serialization_version",
                "proposal_identity",
                "artifact_digest",
                "proposal_revision",
                "previous_proposal_identity",
                "previous_proposal_digest",
                "proposal_status",
                "constitutional_gap",
                "constitutional_baseline_identity",
                "constitutional_baseline_digest",
                "proposing_owner",
                "target_constitutional_owner",
                "target_constitutional_layer",
                "target_constitutional_artifact_identity",
                "target_constitutional_artifact_version",
                "target_constitutional_artifact_digest",
                "proposed_successor_version",
                "proposal_title",
                "normative_change_statement",
                "proposal_rationale",
                "evidence_references",
                "proposed_at",
                "che_definition_count",
                "production_hic_family_count",
                "production_owner_chain_count",
                "production_path_count",
                "parallel_production_path_count",
                "impact_assessment_performed",
                "human_ratification_performed",
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
                "constitutional amendment proposal evidence sequence is malformed"
            )
        return cls(
            contract_version=exact["contract_version"],
            artifact_version=exact["artifact_version"],
            serialization_version=exact["serialization_version"],
            proposal_identity=exact["proposal_identity"],
            artifact_digest=exact["artifact_digest"],
            proposal_revision=exact["proposal_revision"],
            previous_proposal_identity=exact["previous_proposal_identity"],
            previous_proposal_digest=exact["previous_proposal_digest"],
            proposal_status=exact["proposal_status"],
            constitutional_gap=ConstitutionalGapArtifactV1.from_dict(
                exact["constitutional_gap"]
            ),
            constitutional_baseline_identity=exact[
                "constitutional_baseline_identity"
            ],
            constitutional_baseline_digest=exact[
                "constitutional_baseline_digest"
            ],
            proposing_owner=exact["proposing_owner"],
            target_constitutional_owner=exact["target_constitutional_owner"],
            target_constitutional_layer=exact["target_constitutional_layer"],
            target_constitutional_artifact_identity=exact[
                "target_constitutional_artifact_identity"
            ],
            target_constitutional_artifact_version=exact[
                "target_constitutional_artifact_version"
            ],
            target_constitutional_artifact_digest=exact[
                "target_constitutional_artifact_digest"
            ],
            proposed_successor_version=exact["proposed_successor_version"],
            proposal_title=exact["proposal_title"],
            normative_change_statement=exact["normative_change_statement"],
            proposal_rationale=exact["proposal_rationale"],
            evidence_references=tuple(
                ConstitutionalAmendmentProposalEvidenceReferenceV1.from_dict(item)
                for item in exact["evidence_references"]
            ),
            proposed_at=exact["proposed_at"],
            che_definition_count=exact["che_definition_count"],
            production_hic_family_count=exact["production_hic_family_count"],
            production_owner_chain_count=exact["production_owner_chain_count"],
            production_path_count=exact["production_path_count"],
            parallel_production_path_count=exact[
                "parallel_production_path_count"
            ],
            impact_assessment_performed=exact["impact_assessment_performed"],
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


def _required_evidence_specifications(
    *,
    gap: ConstitutionalGapArtifactV1,
    proposing_owner: str,
    target_constitutional_owner: str,
    target_constitutional_artifact_identity: str,
    target_constitutional_artifact_digest: str,
    constitutional_baseline_identity: str,
    constitutional_baseline_digest: str,
    proposal_revision: int,
    previous_proposal_identity: str | None,
    previous_proposal_digest: str | None,
) -> tuple[tuple[str, str, str | None, str | None], ...]:
    required = [
        (
            GAP_DETERMINATION_EVIDENCE,
            gap.responsibility_owner,
            gap.gap_identity,
            gap.artifact_digest,
        ),
        (PROPOSER_AUTHORITY_EVIDENCE, proposing_owner, None, None),
        (
            TARGET_CONSTITUTIONAL_ARTIFACT_EVIDENCE,
            target_constitutional_owner,
            target_constitutional_artifact_identity,
            target_constitutional_artifact_digest,
        ),
        (
            CONSTITUTIONAL_BASELINE_EVIDENCE,
            CONSTITUTIONAL_GOVERNANCE_OWNER,
            constitutional_baseline_identity,
            constitutional_baseline_digest,
        ),
    ]
    if proposal_revision > 1:
        required.append(
            (
                PREVIOUS_PROPOSAL_EVIDENCE,
                proposing_owner,
                previous_proposal_identity,
                previous_proposal_digest,
            )
        )
    return tuple(required)


def validate_constitutional_amendment_proposal_evidence_reference_v1(
    *,
    value: ConstitutionalAmendmentProposalEvidenceReferenceV1
    | Mapping[str, Any],
    expected_role: str,
    expected_owner: str,
    expected_artifact_identity: str | None = None,
    expected_artifact_digest: str | None = None,
) -> ConstitutionalAmendmentProposalEvidenceReferenceV1:
    """Validate one proposal evidence reference against its exact owner and role."""

    evidence = (
        value
        if isinstance(value, ConstitutionalAmendmentProposalEvidenceReferenceV1)
        else ConstitutionalAmendmentProposalEvidenceReferenceV1.from_dict(value)
    )
    role = _require_text(expected_role, "expected_role")
    owner = _require_text(expected_owner, "expected_owner")
    if evidence.evidence_role != role or evidence.producing_owner != owner:
        raise FailClosedRuntimeError(
            "constitutional amendment proposal evidence role or owner is invalid"
        )
    if (
        expected_artifact_identity is not None
        and evidence.artifact_identity != expected_artifact_identity
    ):
        raise FailClosedRuntimeError(
            "constitutional amendment proposal evidence identity is invalid"
        )
    if (
        expected_artifact_digest is not None
        and evidence.artifact_digest != expected_artifact_digest
    ):
        raise FailClosedRuntimeError(
            "constitutional amendment proposal evidence digest is invalid"
        )
    return evidence


def _validate_revision_lineage(
    *,
    proposal_revision: int,
    previous_proposal_identity: str | None,
    previous_proposal_digest: str | None,
) -> None:
    _require_positive_integer(proposal_revision, "proposal_revision")
    if proposal_revision == 1:
        if (
            previous_proposal_identity is not None
            or previous_proposal_digest is not None
        ):
            raise FailClosedRuntimeError(
                "initial constitutional amendment proposal cannot claim a predecessor"
            )
    elif previous_proposal_identity is None or previous_proposal_digest is None:
        raise FailClosedRuntimeError(
            "revised constitutional amendment proposal requires a predecessor"
        )


def _validate_evidence_sequence(
    *,
    evidence_references: tuple[
        ConstitutionalAmendmentProposalEvidenceReferenceV1, ...
    ],
    specifications: tuple[tuple[str, str, str | None, str | None], ...],
) -> tuple[ConstitutionalAmendmentProposalEvidenceReferenceV1, ...]:
    if not isinstance(evidence_references, tuple) or len(
        evidence_references
    ) != len(specifications):
        raise FailClosedRuntimeError(
            "constitutional amendment proposal evidence is incomplete"
        )
    if tuple(item.evidence_role for item in evidence_references) != tuple(
        item[0] for item in specifications
    ):
        raise FailClosedRuntimeError(
            "constitutional amendment proposal evidence order is not canonical"
        )
    return tuple(
        validate_constitutional_amendment_proposal_evidence_reference_v1(
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


def create_constitutional_amendment_proposal_v1(
    *,
    constitutional_gap: ConstitutionalGapArtifactV1 | Mapping[str, Any],
    constitutional_baseline_digest: str,
    proposing_owner: str,
    target_constitutional_owner: str,
    target_constitutional_layer: str,
    target_constitutional_artifact_identity: str,
    target_constitutional_artifact_version: str,
    target_constitutional_artifact_digest: str,
    proposed_successor_version: str,
    proposal_title: str,
    normative_change_statement: str,
    proposal_rationale: str,
    evidence_references: Sequence[
        ConstitutionalAmendmentProposalEvidenceReferenceV1 | Mapping[str, Any]
    ],
    proposed_at: str,
    proposal_revision: int = 1,
    previous_proposal_identity: str | None = None,
    previous_proposal_digest: str | None = None,
) -> ConstitutionalAmendmentProposalArtifactV1:
    """Create one proposal-only artifact from a valid open G70-01 Gap."""

    gap = validate_constitutional_gap_artifact_v1(constitutional_gap)
    baseline_digest = _require_sha256(
        constitutional_baseline_digest, "constitutional_baseline_digest"
    )
    proposer = _require_text(proposing_owner, "proposing_owner")
    target_owner = _require_text(
        target_constitutional_owner, "target_constitutional_owner"
    )
    target_identity = _require_text(
        target_constitutional_artifact_identity,
        "target_constitutional_artifact_identity",
    )
    target_version = _require_text(
        target_constitutional_artifact_version,
        "target_constitutional_artifact_version",
    )
    target_digest = _require_sha256(
        target_constitutional_artifact_digest,
        "target_constitutional_artifact_digest",
    )
    successor_version = _require_text(
        proposed_successor_version, "proposed_successor_version"
    )
    previous_identity = _require_optional_text(
        previous_proposal_identity, "previous_proposal_identity"
    )
    previous_digest = _require_optional_sha256(
        previous_proposal_digest, "previous_proposal_digest"
    )
    _validate_revision_lineage(
        proposal_revision=proposal_revision,
        previous_proposal_identity=previous_identity,
        previous_proposal_digest=previous_digest,
    )
    if target_version == successor_version:
        raise FailClosedRuntimeError(
            "constitutional amendment proposal successor version must be distinct"
        )
    if isinstance(evidence_references, (str, bytes)) or not isinstance(
        evidence_references, Sequence
    ):
        raise FailClosedRuntimeError(
            "constitutional amendment proposal evidence collection is malformed"
        )
    evidence = tuple(
        item
        if isinstance(item, ConstitutionalAmendmentProposalEvidenceReferenceV1)
        else ConstitutionalAmendmentProposalEvidenceReferenceV1.from_dict(item)
        for item in evidence_references
    )
    specifications = _required_evidence_specifications(
        gap=gap,
        proposing_owner=proposer,
        target_constitutional_owner=target_owner,
        target_constitutional_artifact_identity=target_identity,
        target_constitutional_artifact_digest=target_digest,
        constitutional_baseline_identity=gap.constitutional_baseline_identity,
        constitutional_baseline_digest=baseline_digest,
        proposal_revision=proposal_revision,
        previous_proposal_identity=previous_identity,
        previous_proposal_digest=previous_digest,
    )
    validated_evidence = _validate_evidence_sequence(
        evidence_references=evidence,
        specifications=specifications,
    )
    provisional = ConstitutionalAmendmentProposalArtifactV1(
        contract_version=CONSTITUTIONAL_AMENDMENT_PROPOSAL_CONTRACT_VERSION,
        artifact_version=CONSTITUTIONAL_AMENDMENT_PROPOSAL_ARTIFACT_VERSION,
        serialization_version=(
            CONSTITUTIONAL_AMENDMENT_PROPOSAL_SERIALIZATION_VERSION
        ),
        proposal_identity="PENDING-CONSTITUTIONAL-AMENDMENT-PROPOSAL",
        artifact_digest="sha256:" + ("0" * 64),
        proposal_revision=proposal_revision,
        previous_proposal_identity=previous_identity,
        previous_proposal_digest=previous_digest,
        proposal_status=PROPOSAL_ONLY_UNASSESSED,
        constitutional_gap=gap,
        constitutional_baseline_identity=gap.constitutional_baseline_identity,
        constitutional_baseline_digest=baseline_digest,
        proposing_owner=proposer,
        target_constitutional_owner=target_owner,
        target_constitutional_layer=target_constitutional_layer,
        target_constitutional_artifact_identity=target_identity,
        target_constitutional_artifact_version=target_version,
        target_constitutional_artifact_digest=target_digest,
        proposed_successor_version=successor_version,
        proposal_title=proposal_title,
        normative_change_statement=normative_change_statement,
        proposal_rationale=proposal_rationale,
        evidence_references=validated_evidence,
        proposed_at=proposed_at,
    )
    return validate_constitutional_amendment_proposal_artifact_v1(
        replace(
            provisional,
            proposal_identity=_identity(provisional.identity_payload()),
            artifact_digest=_digest(provisional.identity_payload()),
        )
    )


def validate_constitutional_amendment_proposal_artifact_v1(
    value: ConstitutionalAmendmentProposalArtifactV1 | Mapping[str, Any],
) -> ConstitutionalAmendmentProposalArtifactV1:
    """Validate a proposal without assessing, ratifying, certifying, or activating."""

    proposal = (
        value
        if isinstance(value, ConstitutionalAmendmentProposalArtifactV1)
        else ConstitutionalAmendmentProposalArtifactV1.from_dict(value)
    )
    if (
        proposal.contract_version
        != CONSTITUTIONAL_AMENDMENT_PROPOSAL_CONTRACT_VERSION
        or proposal.artifact_version
        != CONSTITUTIONAL_AMENDMENT_PROPOSAL_ARTIFACT_VERSION
        or proposal.serialization_version
        != CONSTITUTIONAL_AMENDMENT_PROPOSAL_SERIALIZATION_VERSION
    ):
        raise FailClosedRuntimeError(
            "constitutional amendment proposal version is invalid"
        )
    if proposal.proposal_status != PROPOSAL_ONLY_UNASSESSED:
        raise FailClosedRuntimeError(
            "constitutional amendment proposal status is invalid"
        )
    gap = validate_constitutional_gap_artifact_v1(proposal.constitutional_gap)
    if (
        proposal.constitutional_baseline_identity
        != gap.constitutional_baseline_identity
    ):
        raise FailClosedRuntimeError(
            "constitutional amendment proposal baseline binding is invalid"
        )
    if (
        proposal.target_constitutional_artifact_version
        == proposal.proposed_successor_version
    ):
        raise FailClosedRuntimeError(
            "constitutional amendment proposal successor version must be distinct"
        )
    _validate_revision_lineage(
        proposal_revision=proposal.proposal_revision,
        previous_proposal_identity=proposal.previous_proposal_identity,
        previous_proposal_digest=proposal.previous_proposal_digest,
    )
    specifications = _required_evidence_specifications(
        gap=gap,
        proposing_owner=proposal.proposing_owner,
        target_constitutional_owner=proposal.target_constitutional_owner,
        target_constitutional_artifact_identity=(
            proposal.target_constitutional_artifact_identity
        ),
        target_constitutional_artifact_digest=(
            proposal.target_constitutional_artifact_digest
        ),
        constitutional_baseline_identity=proposal.constitutional_baseline_identity,
        constitutional_baseline_digest=proposal.constitutional_baseline_digest,
        proposal_revision=proposal.proposal_revision,
        previous_proposal_identity=proposal.previous_proposal_identity,
        previous_proposal_digest=proposal.previous_proposal_digest,
    )
    _validate_evidence_sequence(
        evidence_references=proposal.evidence_references,
        specifications=specifications,
    )
    invariants = (
        proposal.che_definition_count,
        proposal.production_hic_family_count,
        proposal.production_owner_chain_count,
        proposal.production_path_count,
        proposal.parallel_production_path_count,
        proposal.impact_assessment_performed,
        proposal.human_ratification_performed,
        proposal.amendment_certification_performed,
        proposal.amendment_activation_performed,
        proposal.runtime_mutation_performed,
        proposal.production_behavior_changed,
        proposal.replay_path_created,
        proposal.cro_authority_created,
    )
    if invariants != (
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
        False,
    ):
        raise FailClosedRuntimeError(
            "constitutional amendment proposal boundary invariants are invalid"
        )
    expected_identity = _identity(proposal.identity_payload())
    expected_digest = _digest(proposal.identity_payload())
    if (
        proposal.proposal_identity != expected_identity
        or proposal.artifact_digest != expected_digest
    ):
        raise FailClosedRuntimeError(
            "constitutional amendment proposal identity is invalid"
        )
    return proposal


def serialize_constitutional_amendment_proposal_v1(
    proposal: ConstitutionalAmendmentProposalArtifactV1 | Mapping[str, Any],
) -> str:
    """Return canonical versioned proposal JSON without writing it."""

    validated = validate_constitutional_amendment_proposal_artifact_v1(proposal)
    return canonical_serialize(validated.to_dict())


def deserialize_constitutional_amendment_proposal_v1(
    serialized: str | bytes,
) -> ConstitutionalAmendmentProposalArtifactV1:
    """Parse and fail-closed validate only canonical V1 proposal JSON."""

    if isinstance(serialized, bytes):
        try:
            source = serialized.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise FailClosedRuntimeError(
                "constitutional amendment proposal serialization is not UTF-8"
            ) from exc
    elif isinstance(serialized, str):
        source = serialized
    else:
        raise FailClosedRuntimeError(
            "constitutional amendment proposal serialization is malformed"
        )
    try:
        decoded = json.loads(source)
    except json.JSONDecodeError as exc:
        raise FailClosedRuntimeError(
            "constitutional amendment proposal serialization is not valid JSON"
        ) from exc
    proposal = validate_constitutional_amendment_proposal_artifact_v1(decoded)
    if canonical_serialize(proposal.to_dict()) != source:
        raise FailClosedRuntimeError(
            "constitutional amendment proposal serialization is not canonical"
        )
    return proposal


__all__ = [
    "BASE_PROPOSAL_EVIDENCE_ORDER",
    "CONSTITUTIONAL_AMENDMENT_PROPOSAL_ARTIFACT_VERSION",
    "CONSTITUTIONAL_AMENDMENT_PROPOSAL_CONTRACT_VERSION",
    "CONSTITUTIONAL_AMENDMENT_PROPOSAL_SERIALIZATION_VERSION",
    "CONSTITUTIONAL_BASELINE_EVIDENCE",
    "CONSTITUTIONAL_GOVERNANCE_OWNER",
    "CONSTITUTIONAL_LAYERS",
    "GAP_DETERMINATION_EVIDENCE",
    "PREVIOUS_PROPOSAL_EVIDENCE",
    "PROPOSAL_ONLY_UNASSESSED",
    "PROPOSER_AUTHORITY_EVIDENCE",
    "TARGET_CONSTITUTIONAL_ARTIFACT_EVIDENCE",
    "ConstitutionalAmendmentProposalArtifactV1",
    "ConstitutionalAmendmentProposalEvidenceReferenceV1",
    "create_constitutional_amendment_proposal_v1",
    "deserialize_constitutional_amendment_proposal_v1",
    "serialize_constitutional_amendment_proposal_v1",
    "validate_constitutional_amendment_proposal_artifact_v1",
    "validate_constitutional_amendment_proposal_evidence_reference_v1",
]
