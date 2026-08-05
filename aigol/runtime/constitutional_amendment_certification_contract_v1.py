"""Constitutional Amendment Certification contract for G70-05.

The contract certifies one exact G70-01 Gap, G70-02 Proposal, G70-03 Impact
Assessment, and G70-04 Human Ratification evidence chain.  Certification is
governance evidence only.  It does not publish or activate a Constitutional
successor and it does not mutate runtime, production, owners, CHE, HIC,
Replay, or CRO.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

from aigol.runtime.canonical_human_authority_act_contract_v1 import (
    HUMAN_AUTHORITY_OWNER,
)
from aigol.runtime.constitutional_amendment_proposal_contract_v1 import (
    ConstitutionalAmendmentProposalArtifactV1,
    validate_constitutional_amendment_proposal_artifact_v1,
)
from aigol.runtime.constitutional_gap_determination_evidence_contract_v1 import (
    CONSTITUTIONAL_CERTIFICATION_OWNER,
    ConstitutionalGapArtifactV1,
    validate_constitutional_gap_artifact_v1,
)
from aigol.runtime.constitutional_human_ratification_contract_v1 import (
    ConstitutionalHumanRatificationArtifactV1,
    validate_constitutional_human_ratification_artifact_v1,
)
from aigol.runtime.constitutional_impact_assessment_contract_v1 import (
    UNRESOLVED_CONSTITUTIONAL_IMPACT,
    ConstitutionalImpactAssessmentArtifactV1,
    validate_constitutional_impact_assessment_artifact_v1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize


CONSTITUTIONAL_AMENDMENT_CERTIFICATION_CONTRACT_VERSION = (
    "G70_05_CONSTITUTIONAL_AMENDMENT_CERTIFICATION_CONTRACT_V1"
)
CONSTITUTIONAL_AMENDMENT_CERTIFICATION_ARTIFACT_VERSION = (
    "CONSTITUTIONAL_AMENDMENT_CERTIFICATION_ARTIFACT_V1"
)
CONSTITUTIONAL_AMENDMENT_CERTIFICATION_SERIALIZATION_VERSION = (
    "CONSTITUTIONAL_AMENDMENT_CERTIFICATION_SERIALIZATION_V1"
)

CONSTITUTIONAL_AMENDMENT_CERTIFIED_NOT_ACTIVATED = (
    "CONSTITUTIONAL_AMENDMENT_CERTIFIED_NOT_ACTIVATED"
)
CERTIFICATION_RULE_SATISFIED = "SATISFIED"

CONSTITUTIONAL_GAP_CERTIFICATION_EVIDENCE = (
    "CONSTITUTIONAL_GAP_CERTIFICATION_EVIDENCE"
)
CONSTITUTIONAL_PROPOSAL_CERTIFICATION_EVIDENCE = (
    "CONSTITUTIONAL_PROPOSAL_CERTIFICATION_EVIDENCE"
)
CONSTITUTIONAL_IMPACT_CERTIFICATION_EVIDENCE = (
    "CONSTITUTIONAL_IMPACT_CERTIFICATION_EVIDENCE"
)
HUMAN_RATIFICATION_CERTIFICATION_EVIDENCE = (
    "HUMAN_RATIFICATION_CERTIFICATION_EVIDENCE"
)

CONSTITUTIONAL_AMENDMENT_CERTIFICATION_SCOPE = (
    "CONSTITUTIONAL_GAP",
    "CONSTITUTIONAL_AMENDMENT_PROPOSAL",
    "CONSTITUTIONAL_IMPACT_ASSESSMENT",
    "CONSTITUTIONAL_HUMAN_RATIFICATION",
)
CONSTITUTIONAL_AMENDMENT_CERTIFICATION_EVIDENCE_ORDER = (
    CONSTITUTIONAL_GAP_CERTIFICATION_EVIDENCE,
    CONSTITUTIONAL_PROPOSAL_CERTIFICATION_EVIDENCE,
    CONSTITUTIONAL_IMPACT_CERTIFICATION_EVIDENCE,
    HUMAN_RATIFICATION_CERTIFICATION_EVIDENCE,
)
CONSTITUTIONAL_AMENDMENT_CERTIFICATION_RULE_ORDER = (
    "CONSTITUTIONAL_GAP_VALID",
    "CONSTITUTIONAL_PROPOSAL_VALID_AND_GAP_BOUND",
    "CONSTITUTIONAL_IMPACT_VALID_RESOLVED_AND_PROPOSAL_BOUND",
    "HUMAN_RATIFICATION_VALID_AND_IMPACT_BOUND",
    "CERTIFICATION_EVIDENCE_COMPLETE_AND_OWNER_BOUND",
    "CERTIFICATION_SCOPE_CLOSED",
    "NON_ACTIVATING_BOUNDARIES_PRESERVED",
)

_CERTIFICATION_IDENTITY_PREFIX = "CONSTITUTIONAL-AMENDMENT-CERTIFICATION-"


def _require_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise FailClosedRuntimeError(
            "constitutional amendment certification "
            f"{field_name} is absent or malformed"
        )
    return value


def _require_sha256(value: Any, field_name: str) -> str:
    text = _require_text(value, field_name)
    if not text.startswith("sha256:") or len(text) != 71:
        raise FailClosedRuntimeError(
            "constitutional amendment certification "
            f"{field_name} is not a SHA-256 reference"
        )
    try:
        int(text[7:], 16)
    except ValueError as exc:
        raise FailClosedRuntimeError(
            "constitutional amendment certification "
            f"{field_name} is not a SHA-256 reference"
        ) from exc
    return text


def _require_exact_keys(
    value: Any,
    keys: set[str],
    field_name: str,
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != keys:
        raise FailClosedRuntimeError(
            f"constitutional amendment certification {field_name} is malformed"
        )
    return value


def _identity(value: Any) -> str:
    return _CERTIFICATION_IDENTITY_PREFIX + sha256(
        canonical_serialize(value).encode("utf-8")
    ).hexdigest()


def _digest(value: Any) -> str:
    return "sha256:" + sha256(
        canonical_serialize(value).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True, slots=True)
class ConstitutionalAmendmentCertificationRuleResultV1:
    """One immutable result for one closed deterministic certification rule."""

    rule_id: str
    rule_status: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "rule_id", _require_text(self.rule_id, "rule_id"))
        if self.rule_id not in CONSTITUTIONAL_AMENDMENT_CERTIFICATION_RULE_ORDER:
            raise FailClosedRuntimeError(
                "constitutional amendment certification rule is not recognized"
            )
        if self.rule_status != CERTIFICATION_RULE_SATISFIED:
            raise FailClosedRuntimeError(
                "constitutional amendment certification rule is not satisfied"
            )

    def to_dict(self) -> dict[str, str]:
        return {"rule_id": self.rule_id, "rule_status": self.rule_status}

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "ConstitutionalAmendmentCertificationRuleResultV1":
        exact = _require_exact_keys(
            value,
            {"rule_id", "rule_status"},
            "rule result",
        )
        return cls(**dict(exact))


@dataclass(frozen=True, slots=True)
class ConstitutionalAmendmentCertificationEvidenceReferenceV1:
    """One immutable reference to one and only one certified CAP artifact."""

    evidence_role: str
    producing_owner: str
    artifact_identity: str
    artifact_digest: str

    def __post_init__(self) -> None:
        if self.evidence_role not in (
            CONSTITUTIONAL_AMENDMENT_CERTIFICATION_EVIDENCE_ORDER
        ):
            raise FailClosedRuntimeError(
                "constitutional amendment certification evidence role is not recognized"
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
    ) -> "ConstitutionalAmendmentCertificationEvidenceReferenceV1":
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
class ConstitutionalAmendmentCertificationArtifactV1:
    """Immutable certification of the exact four-artifact CAP evidence chain."""

    contract_version: str
    artifact_version: str
    serialization_version: str
    certification_identity: str
    artifact_digest: str
    certification_status: str
    certification_scope: tuple[str, ...]
    human_ratification: ConstitutionalHumanRatificationArtifactV1
    certifying_owner: str
    rule_results: tuple[ConstitutionalAmendmentCertificationRuleResultV1, ...]
    evidence_references: tuple[
        ConstitutionalAmendmentCertificationEvidenceReferenceV1, ...
    ]
    certified_at: str
    che_definition_count: int = 1
    production_hic_family_count: int = 1
    production_owner_chain_count: int = 1
    production_path_count: int = 1
    parallel_production_path_count: int = 0
    amendment_certification_performed: bool = True
    amendment_publication_performed: bool = False
    amendment_activation_performed: bool = False
    constitutional_successor_activation_performed: bool = False
    runtime_mutation_performed: bool = False
    production_mutation_performed: bool = False
    owner_mutation_performed: bool = False
    che_mutation_performed: bool = False
    hic_mutation_performed: bool = False
    replay_mutation_performed: bool = False
    cro_mutation_performed: bool = False
    hic_semantic_capability_introduced: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "contract_version",
            "artifact_version",
            "serialization_version",
            "certification_identity",
            "certification_status",
            "certifying_owner",
            "certified_at",
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
        if not isinstance(self.certification_scope, tuple) or any(
            not isinstance(item, str) for item in self.certification_scope
        ):
            raise FailClosedRuntimeError(
                "constitutional amendment certification scope is malformed"
            )
        if not isinstance(
            self.human_ratification, ConstitutionalHumanRatificationArtifactV1
        ):
            raise FailClosedRuntimeError(
                "constitutional amendment certification ratification is malformed"
            )
        if not isinstance(self.rule_results, tuple) or any(
            not isinstance(item, ConstitutionalAmendmentCertificationRuleResultV1)
            for item in self.rule_results
        ):
            raise FailClosedRuntimeError(
                "constitutional amendment certification rule sequence is malformed"
            )
        if not isinstance(self.evidence_references, tuple) or any(
            not isinstance(
                item,
                ConstitutionalAmendmentCertificationEvidenceReferenceV1,
            )
            for item in self.evidence_references
        ):
            raise FailClosedRuntimeError(
                "constitutional amendment certification evidence sequence is malformed"
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
                    "constitutional amendment certification topology is malformed"
                )
        for field_name in (
            "amendment_certification_performed",
            "amendment_publication_performed",
            "amendment_activation_performed",
            "constitutional_successor_activation_performed",
            "runtime_mutation_performed",
            "production_mutation_performed",
            "owner_mutation_performed",
            "che_mutation_performed",
            "hic_mutation_performed",
            "replay_mutation_performed",
            "cro_mutation_performed",
            "hic_semantic_capability_introduced",
        ):
            if not isinstance(getattr(self, field_name), bool):
                raise FailClosedRuntimeError(
                    "constitutional amendment certification boundary is malformed"
                )

    def identity_payload(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "artifact_version": self.artifact_version,
            "serialization_version": self.serialization_version,
            "certification_status": self.certification_status,
            "certification_scope": list(self.certification_scope),
            "human_ratification": self.human_ratification.to_dict(),
            "certifying_owner": self.certifying_owner,
            "rule_results": [item.to_dict() for item in self.rule_results],
            "evidence_references": [
                item.to_dict() for item in self.evidence_references
            ],
            "certified_at": self.certified_at,
            "che_definition_count": self.che_definition_count,
            "production_hic_family_count": self.production_hic_family_count,
            "production_owner_chain_count": self.production_owner_chain_count,
            "production_path_count": self.production_path_count,
            "parallel_production_path_count": self.parallel_production_path_count,
            "amendment_certification_performed": (
                self.amendment_certification_performed
            ),
            "amendment_publication_performed": (
                self.amendment_publication_performed
            ),
            "amendment_activation_performed": self.amendment_activation_performed,
            "constitutional_successor_activation_performed": (
                self.constitutional_successor_activation_performed
            ),
            "runtime_mutation_performed": self.runtime_mutation_performed,
            "production_mutation_performed": self.production_mutation_performed,
            "owner_mutation_performed": self.owner_mutation_performed,
            "che_mutation_performed": self.che_mutation_performed,
            "hic_mutation_performed": self.hic_mutation_performed,
            "replay_mutation_performed": self.replay_mutation_performed,
            "cro_mutation_performed": self.cro_mutation_performed,
            "hic_semantic_capability_introduced": (
                self.hic_semantic_capability_introduced
            ),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "certification_identity": self.certification_identity,
            "artifact_digest": self.artifact_digest,
            **self.identity_payload(),
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "ConstitutionalAmendmentCertificationArtifactV1":
        exact = _require_exact_keys(
            value,
            {
                "contract_version",
                "artifact_version",
                "serialization_version",
                "certification_identity",
                "artifact_digest",
                "certification_status",
                "certification_scope",
                "human_ratification",
                "certifying_owner",
                "rule_results",
                "evidence_references",
                "certified_at",
                "che_definition_count",
                "production_hic_family_count",
                "production_owner_chain_count",
                "production_path_count",
                "parallel_production_path_count",
                "amendment_certification_performed",
                "amendment_publication_performed",
                "amendment_activation_performed",
                "constitutional_successor_activation_performed",
                "runtime_mutation_performed",
                "production_mutation_performed",
                "owner_mutation_performed",
                "che_mutation_performed",
                "hic_mutation_performed",
                "replay_mutation_performed",
                "cro_mutation_performed",
                "hic_semantic_capability_introduced",
            },
            "artifact",
        )
        for field_name in (
            "certification_scope",
            "rule_results",
            "evidence_references",
        ):
            if not isinstance(exact[field_name], list):
                raise FailClosedRuntimeError(
                    f"constitutional amendment certification {field_name} is malformed"
                )
        return cls(
            contract_version=exact["contract_version"],
            artifact_version=exact["artifact_version"],
            serialization_version=exact["serialization_version"],
            certification_identity=exact["certification_identity"],
            artifact_digest=exact["artifact_digest"],
            certification_status=exact["certification_status"],
            certification_scope=tuple(exact["certification_scope"]),
            human_ratification=ConstitutionalHumanRatificationArtifactV1.from_dict(
                exact["human_ratification"]
            ),
            certifying_owner=exact["certifying_owner"],
            rule_results=tuple(
                ConstitutionalAmendmentCertificationRuleResultV1.from_dict(item)
                for item in exact["rule_results"]
            ),
            evidence_references=tuple(
                ConstitutionalAmendmentCertificationEvidenceReferenceV1.from_dict(
                    item
                )
                for item in exact["evidence_references"]
            ),
            certified_at=exact["certified_at"],
            che_definition_count=exact["che_definition_count"],
            production_hic_family_count=exact["production_hic_family_count"],
            production_owner_chain_count=exact[
                "production_owner_chain_count"
            ],
            production_path_count=exact["production_path_count"],
            parallel_production_path_count=exact[
                "parallel_production_path_count"
            ],
            amendment_certification_performed=exact[
                "amendment_certification_performed"
            ],
            amendment_publication_performed=exact[
                "amendment_publication_performed"
            ],
            amendment_activation_performed=exact[
                "amendment_activation_performed"
            ],
            constitutional_successor_activation_performed=exact[
                "constitutional_successor_activation_performed"
            ],
            runtime_mutation_performed=exact["runtime_mutation_performed"],
            production_mutation_performed=exact[
                "production_mutation_performed"
            ],
            owner_mutation_performed=exact["owner_mutation_performed"],
            che_mutation_performed=exact["che_mutation_performed"],
            hic_mutation_performed=exact["hic_mutation_performed"],
            replay_mutation_performed=exact["replay_mutation_performed"],
            cro_mutation_performed=exact["cro_mutation_performed"],
            hic_semantic_capability_introduced=exact[
                "hic_semantic_capability_introduced"
            ],
        )


def validate_constitutional_amendment_certification_rule_result_v1(
    *,
    value: ConstitutionalAmendmentCertificationRuleResultV1
    | Mapping[str, Any],
    expected_rule_id: str,
) -> ConstitutionalAmendmentCertificationRuleResultV1:
    """Validate one exact satisfied rule at its declared rule identity."""

    rule = (
        value
        if isinstance(value, ConstitutionalAmendmentCertificationRuleResultV1)
        else ConstitutionalAmendmentCertificationRuleResultV1.from_dict(value)
    )
    if rule.rule_id != _require_text(expected_rule_id, "expected_rule_id"):
        raise FailClosedRuntimeError(
            "constitutional amendment certification rule identity is invalid"
        )
    if rule.rule_status != CERTIFICATION_RULE_SATISFIED:
        raise FailClosedRuntimeError(
            "constitutional amendment certification rule is not satisfied"
        )
    return rule


def validate_constitutional_amendment_certification_evidence_reference_v1(
    *,
    value: ConstitutionalAmendmentCertificationEvidenceReferenceV1
    | Mapping[str, Any],
    expected_role: str,
    expected_owner: str,
    expected_artifact_identity: str,
    expected_artifact_digest: str,
) -> ConstitutionalAmendmentCertificationEvidenceReferenceV1:
    """Validate one exact certification evidence owner and artifact binding."""

    evidence = (
        value
        if isinstance(
            value,
            ConstitutionalAmendmentCertificationEvidenceReferenceV1,
        )
        else ConstitutionalAmendmentCertificationEvidenceReferenceV1.from_dict(
            value
        )
    )
    if (
        evidence.evidence_role != _require_text(expected_role, "expected_role")
        or evidence.producing_owner
        != _require_text(expected_owner, "expected_owner")
    ):
        raise FailClosedRuntimeError(
            "constitutional amendment certification evidence role or owner is invalid"
        )
    if evidence.artifact_identity != _require_text(
        expected_artifact_identity, "expected_artifact_identity"
    ):
        raise FailClosedRuntimeError(
            "constitutional amendment certification evidence identity is invalid"
        )
    if evidence.artifact_digest != _require_sha256(
        expected_artifact_digest, "expected_artifact_digest"
    ):
        raise FailClosedRuntimeError(
            "constitutional amendment certification evidence digest is invalid"
        )
    return evidence


def _validated_certification_chain(
    ratification: ConstitutionalHumanRatificationArtifactV1 | Mapping[str, Any],
) -> tuple[
    ConstitutionalHumanRatificationArtifactV1,
    ConstitutionalImpactAssessmentArtifactV1,
    ConstitutionalAmendmentProposalArtifactV1,
    ConstitutionalGapArtifactV1,
]:
    validated_ratification = validate_constitutional_human_ratification_artifact_v1(
        ratification
    )
    assessment = validate_constitutional_impact_assessment_artifact_v1(
        validated_ratification.impact_assessment
    )
    if assessment.impact_classification == UNRESOLVED_CONSTITUTIONAL_IMPACT:
        raise FailClosedRuntimeError(
            "unresolved Constitutional impact cannot be certified"
        )
    proposal = validate_constitutional_amendment_proposal_artifact_v1(
        assessment.amendment_proposal
    )
    gap = validate_constitutional_gap_artifact_v1(proposal.constitutional_gap)
    if (
        validated_ratification.impact_assessment != assessment
        or assessment.amendment_proposal != proposal
        or proposal.constitutional_gap != gap
    ):
        raise FailClosedRuntimeError(
            "constitutional amendment certification predecessor binding is invalid"
        )
    return validated_ratification, assessment, proposal, gap


def _evidence_specifications(
    *,
    ratification: ConstitutionalHumanRatificationArtifactV1,
    assessment: ConstitutionalImpactAssessmentArtifactV1,
    proposal: ConstitutionalAmendmentProposalArtifactV1,
    gap: ConstitutionalGapArtifactV1,
) -> tuple[tuple[str, str, str, str], ...]:
    return (
        (
            CONSTITUTIONAL_GAP_CERTIFICATION_EVIDENCE,
            gap.responsibility_owner,
            gap.gap_identity,
            gap.artifact_digest,
        ),
        (
            CONSTITUTIONAL_PROPOSAL_CERTIFICATION_EVIDENCE,
            proposal.proposing_owner,
            proposal.proposal_identity,
            proposal.artifact_digest,
        ),
        (
            CONSTITUTIONAL_IMPACT_CERTIFICATION_EVIDENCE,
            assessment.assessing_owner,
            assessment.assessment_identity,
            assessment.artifact_digest,
        ),
        (
            HUMAN_RATIFICATION_CERTIFICATION_EVIDENCE,
            HUMAN_AUTHORITY_OWNER,
            ratification.ratification_identity,
            ratification.artifact_digest,
        ),
    )


def _validate_rule_results(
    rule_results: tuple[ConstitutionalAmendmentCertificationRuleResultV1, ...],
) -> tuple[ConstitutionalAmendmentCertificationRuleResultV1, ...]:
    if not isinstance(rule_results, tuple) or len(rule_results) != len(
        CONSTITUTIONAL_AMENDMENT_CERTIFICATION_RULE_ORDER
    ):
        raise FailClosedRuntimeError(
            "constitutional amendment certification rules are incomplete"
        )
    if tuple(item.rule_id for item in rule_results) != (
        CONSTITUTIONAL_AMENDMENT_CERTIFICATION_RULE_ORDER
    ):
        raise FailClosedRuntimeError(
            "constitutional amendment certification rule order is not canonical"
        )
    return tuple(
        validate_constitutional_amendment_certification_rule_result_v1(
            value=result,
            expected_rule_id=rule_id,
        )
        for result, rule_id in zip(
            rule_results,
            CONSTITUTIONAL_AMENDMENT_CERTIFICATION_RULE_ORDER,
            strict=True,
        )
    )


def _validate_evidence(
    *,
    evidence_references: tuple[
        ConstitutionalAmendmentCertificationEvidenceReferenceV1, ...
    ],
    specifications: tuple[tuple[str, str, str, str], ...],
) -> tuple[ConstitutionalAmendmentCertificationEvidenceReferenceV1, ...]:
    if not isinstance(evidence_references, tuple) or len(
        evidence_references
    ) != len(specifications):
        raise FailClosedRuntimeError(
            "constitutional amendment certification evidence is incomplete"
        )
    if tuple(item.evidence_role for item in evidence_references) != tuple(
        item[0] for item in specifications
    ):
        raise FailClosedRuntimeError(
            "constitutional amendment certification evidence order is not canonical"
        )
    return tuple(
        validate_constitutional_amendment_certification_evidence_reference_v1(
            value=evidence,
            expected_role=role,
            expected_owner=owner,
            expected_artifact_identity=identity,
            expected_artifact_digest=digest,
        )
        for evidence, (role, owner, identity, digest) in zip(
            evidence_references,
            specifications,
            strict=True,
        )
    )


def certify_constitutional_amendment_v1(
    *,
    human_ratification: ConstitutionalHumanRatificationArtifactV1
    | Mapping[str, Any],
    certifying_owner: str,
    evidence_references: Sequence[
        ConstitutionalAmendmentCertificationEvidenceReferenceV1
        | Mapping[str, Any]
    ],
    certified_at: str,
) -> ConstitutionalAmendmentCertificationArtifactV1:
    """Certify the exact four-artifact CAP chain and stop before publication."""

    if _require_text(certifying_owner, "certifying_owner") != (
        CONSTITUTIONAL_CERTIFICATION_OWNER
    ):
        raise FailClosedRuntimeError(
            "constitutional amendment certification owner is invalid"
        )
    ratification, assessment, proposal, gap = _validated_certification_chain(
        human_ratification
    )
    if isinstance(evidence_references, (str, bytes)) or not isinstance(
        evidence_references, Sequence
    ):
        raise FailClosedRuntimeError(
            "constitutional amendment certification evidence collection is malformed"
        )
    evidence = tuple(
        item
        if isinstance(
            item,
            ConstitutionalAmendmentCertificationEvidenceReferenceV1,
        )
        else ConstitutionalAmendmentCertificationEvidenceReferenceV1.from_dict(
            item
        )
        for item in evidence_references
    )
    specifications = _evidence_specifications(
        ratification=ratification,
        assessment=assessment,
        proposal=proposal,
        gap=gap,
    )
    validated_evidence = _validate_evidence(
        evidence_references=evidence,
        specifications=specifications,
    )
    rules = tuple(
        ConstitutionalAmendmentCertificationRuleResultV1(
            rule_id=rule_id,
            rule_status=CERTIFICATION_RULE_SATISFIED,
        )
        for rule_id in CONSTITUTIONAL_AMENDMENT_CERTIFICATION_RULE_ORDER
    )
    provisional = ConstitutionalAmendmentCertificationArtifactV1(
        contract_version=CONSTITUTIONAL_AMENDMENT_CERTIFICATION_CONTRACT_VERSION,
        artifact_version=CONSTITUTIONAL_AMENDMENT_CERTIFICATION_ARTIFACT_VERSION,
        serialization_version=(
            CONSTITUTIONAL_AMENDMENT_CERTIFICATION_SERIALIZATION_VERSION
        ),
        certification_identity="PENDING-CONSTITUTIONAL-AMENDMENT-CERTIFICATION",
        artifact_digest="sha256:" + ("0" * 64),
        certification_status=CONSTITUTIONAL_AMENDMENT_CERTIFIED_NOT_ACTIVATED,
        certification_scope=CONSTITUTIONAL_AMENDMENT_CERTIFICATION_SCOPE,
        human_ratification=ratification,
        certifying_owner=CONSTITUTIONAL_CERTIFICATION_OWNER,
        rule_results=rules,
        evidence_references=validated_evidence,
        certified_at=_require_text(certified_at, "certified_at"),
    )
    return validate_constitutional_amendment_certification_artifact_v1(
        replace(
            provisional,
            certification_identity=_identity(provisional.identity_payload()),
            artifact_digest=_digest(provisional.identity_payload()),
        )
    )


def validate_constitutional_amendment_certification_artifact_v1(
    value: ConstitutionalAmendmentCertificationArtifactV1 | Mapping[str, Any],
) -> ConstitutionalAmendmentCertificationArtifactV1:
    """Fail closed on any chain, rule, scope, evidence, or boundary mismatch."""

    certification = (
        value
        if isinstance(value, ConstitutionalAmendmentCertificationArtifactV1)
        else ConstitutionalAmendmentCertificationArtifactV1.from_dict(value)
    )
    if (
        certification.contract_version
        != CONSTITUTIONAL_AMENDMENT_CERTIFICATION_CONTRACT_VERSION
        or certification.artifact_version
        != CONSTITUTIONAL_AMENDMENT_CERTIFICATION_ARTIFACT_VERSION
        or certification.serialization_version
        != CONSTITUTIONAL_AMENDMENT_CERTIFICATION_SERIALIZATION_VERSION
    ):
        raise FailClosedRuntimeError(
            "constitutional amendment certification version is invalid"
        )
    if (
        certification.certification_status
        != CONSTITUTIONAL_AMENDMENT_CERTIFIED_NOT_ACTIVATED
    ):
        raise FailClosedRuntimeError(
            "constitutional amendment certification status is invalid"
        )
    if certification.certification_scope != (
        CONSTITUTIONAL_AMENDMENT_CERTIFICATION_SCOPE
    ):
        raise FailClosedRuntimeError(
            "constitutional amendment certification scope is invalid"
        )
    if certification.certifying_owner != CONSTITUTIONAL_CERTIFICATION_OWNER:
        raise FailClosedRuntimeError(
            "constitutional amendment certification owner is invalid"
        )
    ratification, assessment, proposal, gap = _validated_certification_chain(
        certification.human_ratification
    )
    rules = _validate_rule_results(certification.rule_results)
    if rules != certification.rule_results:
        raise FailClosedRuntimeError(
            "constitutional amendment certification rule correlation is invalid"
        )
    specifications = _evidence_specifications(
        ratification=ratification,
        assessment=assessment,
        proposal=proposal,
        gap=gap,
    )
    evidence = _validate_evidence(
        evidence_references=certification.evidence_references,
        specifications=specifications,
    )
    if evidence != certification.evidence_references:
        raise FailClosedRuntimeError(
            "constitutional amendment certification evidence correlation is invalid"
        )
    boundaries = (
        certification.che_definition_count,
        certification.production_hic_family_count,
        certification.production_owner_chain_count,
        certification.production_path_count,
        certification.parallel_production_path_count,
        certification.amendment_certification_performed,
        certification.amendment_publication_performed,
        certification.amendment_activation_performed,
        certification.constitutional_successor_activation_performed,
        certification.runtime_mutation_performed,
        certification.production_mutation_performed,
        certification.owner_mutation_performed,
        certification.che_mutation_performed,
        certification.hic_mutation_performed,
        certification.replay_mutation_performed,
        certification.cro_mutation_performed,
        certification.hic_semantic_capability_introduced,
    )
    if boundaries != (
        1,
        1,
        1,
        1,
        0,
        True,
        False,
        False,
        False,
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
            "constitutional amendment certification boundary invariants are invalid"
        )
    expected_identity = _identity(certification.identity_payload())
    expected_digest = _digest(certification.identity_payload())
    if (
        certification.certification_identity != expected_identity
        or certification.artifact_digest != expected_digest
    ):
        raise FailClosedRuntimeError(
            "constitutional amendment certification identity is invalid"
        )
    return certification


def serialize_constitutional_amendment_certification_v1(
    certification: ConstitutionalAmendmentCertificationArtifactV1
    | Mapping[str, Any],
) -> str:
    """Return canonical versioned certification JSON without persistence."""

    validated = validate_constitutional_amendment_certification_artifact_v1(
        certification
    )
    return canonical_serialize(validated.to_dict())


def deserialize_constitutional_amendment_certification_v1(
    serialized: str | bytes,
) -> ConstitutionalAmendmentCertificationArtifactV1:
    """Parse only canonical UTF-8 V1 certification JSON and validate it."""

    if isinstance(serialized, bytes):
        try:
            source = serialized.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise FailClosedRuntimeError(
                "constitutional amendment certification serialization is not UTF-8"
            ) from exc
    elif isinstance(serialized, str):
        source = serialized
    else:
        raise FailClosedRuntimeError(
            "constitutional amendment certification serialization is malformed"
        )
    try:
        decoded = json.loads(source)
    except json.JSONDecodeError as exc:
        raise FailClosedRuntimeError(
            "constitutional amendment certification serialization is not valid JSON"
        ) from exc
    certification = validate_constitutional_amendment_certification_artifact_v1(
        decoded
    )
    if canonical_serialize(certification.to_dict()) != source:
        raise FailClosedRuntimeError(
            "constitutional amendment certification serialization is not canonical"
        )
    return certification


__all__ = [
    "CERTIFICATION_RULE_SATISFIED",
    "CONSTITUTIONAL_AMENDMENT_CERTIFICATION_ARTIFACT_VERSION",
    "CONSTITUTIONAL_AMENDMENT_CERTIFICATION_CONTRACT_VERSION",
    "CONSTITUTIONAL_AMENDMENT_CERTIFICATION_EVIDENCE_ORDER",
    "CONSTITUTIONAL_AMENDMENT_CERTIFICATION_RULE_ORDER",
    "CONSTITUTIONAL_AMENDMENT_CERTIFICATION_SCOPE",
    "CONSTITUTIONAL_AMENDMENT_CERTIFICATION_SERIALIZATION_VERSION",
    "CONSTITUTIONAL_AMENDMENT_CERTIFIED_NOT_ACTIVATED",
    "CONSTITUTIONAL_GAP_CERTIFICATION_EVIDENCE",
    "CONSTITUTIONAL_IMPACT_CERTIFICATION_EVIDENCE",
    "CONSTITUTIONAL_PROPOSAL_CERTIFICATION_EVIDENCE",
    "HUMAN_RATIFICATION_CERTIFICATION_EVIDENCE",
    "ConstitutionalAmendmentCertificationArtifactV1",
    "ConstitutionalAmendmentCertificationEvidenceReferenceV1",
    "ConstitutionalAmendmentCertificationRuleResultV1",
    "certify_constitutional_amendment_v1",
    "deserialize_constitutional_amendment_certification_v1",
    "serialize_constitutional_amendment_certification_v1",
    "validate_constitutional_amendment_certification_artifact_v1",
    "validate_constitutional_amendment_certification_evidence_reference_v1",
    "validate_constitutional_amendment_certification_rule_result_v1",
]
