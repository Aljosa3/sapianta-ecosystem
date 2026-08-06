"""Constitutional Successor Publication and Activation contract for G70-06.

The contract publishes and makes normatively active one exact Constitutional
successor derived from one G70-05 certified amendment.  It preserves the
predecessor and records migration, compatibility, and rollback evidence.  It
does not implement or activate runtime behavior, mutate production, change an
owner, or certify CAP exclusivity.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

from aigol.runtime.constitutional_amendment_certification_contract_v1 import (
    CONSTITUTIONAL_AMENDMENT_CERTIFIED_NOT_ACTIVATED,
    ConstitutionalAmendmentCertificationArtifactV1,
    validate_constitutional_amendment_certification_artifact_v1,
)
from aigol.runtime.constitutional_human_ratification_contract_v1 import (
    CONSTITUTIONAL_GOVERNANCE_OWNER,
)
from aigol.runtime.constitutional_impact_assessment_contract_v1 import (
    OWNER_LOCAL_REPLAY_CUSTODIAN,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize


CONSTITUTIONAL_SUCCESSOR_PUBLICATION_ACTIVATION_CONTRACT_VERSION = (
    "G70_06_CONSTITUTIONAL_SUCCESSOR_PUBLICATION_ACTIVATION_CONTRACT_V1"
)
CONSTITUTIONAL_SUCCESSOR_ARTIFACT_VERSION = (
    "CONSTITUTIONAL_SUCCESSOR_PUBLICATION_ACTIVATION_ARTIFACT_V1"
)
CONSTITUTIONAL_SUCCESSOR_SERIALIZATION_VERSION = (
    "CONSTITUTIONAL_SUCCESSOR_PUBLICATION_ACTIVATION_SERIALIZATION_V1"
)
CONSTITUTIONAL_PRE_ACTIVATION_LINEAGE_STATE_VERSION = (
    "CONSTITUTIONAL_PRE_ACTIVATION_LINEAGE_STATE_V1"
)
CONSTITUTIONAL_SUCCESSOR_PUBLICATION_RECORD_VERSION = (
    "CONSTITUTIONAL_SUCCESSOR_PUBLICATION_RECORD_V1"
)
CONSTITUTIONAL_SUCCESSOR_ACTIVATION_RECORD_VERSION = (
    "CONSTITUTIONAL_SUCCESSOR_ACTIVATION_RECORD_V1"
)
CONSTITUTIONAL_ACTIVATION_SCOPE_VERSION = "CONSTITUTIONAL_ACTIVATION_SCOPE_V1"

CONSTITUTIONAL_SUCCESSOR_PUBLISHED_AND_NORMATIVELY_ACTIVE = (
    "CONSTITUTIONAL_SUCCESSOR_PUBLISHED_AND_NORMATIVELY_ACTIVE"
)
CONSTITUTIONAL_SUCCESSOR_PUBLISHED = "CONSTITUTIONAL_SUCCESSOR_PUBLISHED"
CONSTITUTIONAL_SUCCESSOR_NORMATIVELY_ACTIVE_RUNTIME_NOT_IMPLEMENTED = (
    "CONSTITUTIONAL_SUCCESSOR_NORMATIVELY_ACTIVE_RUNTIME_NOT_IMPLEMENTED"
)
PREDECESSOR_SUPERSEDED_RETAINED_IMMUTABLE = (
    "PREDECESSOR_SUPERSEDED_RETAINED_IMMUTABLE"
)
EXACT_CERTIFIED_AMENDMENT_SCOPE = "EXACT_CERTIFIED_AMENDMENT_SCOPE"

ROLLBACK_ELIGIBLE = "ROLLBACK_ELIGIBLE"
ROLLBACK_NOT_ELIGIBLE = "ROLLBACK_NOT_ELIGIBLE"
ROLLBACK_ELIGIBILITY_STATUSES = (
    ROLLBACK_ELIGIBLE,
    ROLLBACK_NOT_ELIGIBLE,
)

MIGRATION_PLAN_EVIDENCE = "MIGRATION_PLAN_EVIDENCE"
COMPATIBILITY_EVIDENCE = "COMPATIBILITY_EVIDENCE"
PREDECESSOR_RETENTION_EVIDENCE = "PREDECESSOR_RETENTION_EVIDENCE"
ROLLBACK_ELIGIBILITY_EVIDENCE = "ROLLBACK_ELIGIBILITY_EVIDENCE"
ROLLBACK_INELIGIBILITY_EVIDENCE = "ROLLBACK_INELIGIBILITY_EVIDENCE"
SUCCESSOR_EVIDENCE_ROLES = (
    MIGRATION_PLAN_EVIDENCE,
    COMPATIBILITY_EVIDENCE,
    PREDECESSOR_RETENTION_EVIDENCE,
    ROLLBACK_ELIGIBILITY_EVIDENCE,
    ROLLBACK_INELIGIBILITY_EVIDENCE,
)

CONSTITUTIONAL_SUCCESSOR_MIGRATION_OBLIGATIONS = (
    "PRESERVE_PREDECESSOR_EVIDENCE_AND_READABILITY",
    "IMPLEMENT_RUNTIME_EFFECTS_ONLY_THROUGH_LATER_CDP",
    "PRESERVE_OWNER_AND_AUTHORITY_BOUNDARIES",
    "PRESERVE_REPLAY_AND_GOVERNANCE_LINEAGE",
)
CONSTITUTIONAL_SUCCESSOR_COMPATIBILITY_OBLIGATIONS = (
    "ACCEPT_STILL_CERTIFIED_PREDECESSOR_EVIDENCE",
    "PRESERVE_PREDECESSOR_SEMANTICS_FOR_HISTORICAL_REPLAY",
    "BLOCK_UNIMPLEMENTED_SUCCESSOR_RUNTIME_EFFECTS",
)

_LINEAGE_IDENTITY_PREFIX = "CONSTITUTIONAL-LINEAGE-"
_LINEAGE_STATE_IDENTITY_PREFIX = "CONSTITUTIONAL-LINEAGE-STATE-"
_ACTIVATION_SCOPE_IDENTITY_PREFIX = "CONSTITUTIONAL-ACTIVATION-SCOPE-"
_SUCCESSOR_IDENTITY_PREFIX = "CONSTITUTIONAL-SUCCESSOR-"
_PUBLICATION_IDENTITY_PREFIX = "CONSTITUTIONAL-SUCCESSOR-PUBLICATION-"
_ACTIVATION_IDENTITY_PREFIX = "CONSTITUTIONAL-SUCCESSOR-ACTIVATION-"
_SUCCESSOR_ARTIFACT_IDENTITY_PREFIX = (
    "CONSTITUTIONAL-SUCCESSOR-PUBLICATION-ACTIVATION-"
)


def _require_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise FailClosedRuntimeError(
            f"constitutional successor {field_name} is absent or malformed"
        )
    return value


def _require_sha256(value: Any, field_name: str) -> str:
    text = _require_text(value, field_name)
    if not text.startswith("sha256:") or len(text) != 71:
        raise FailClosedRuntimeError(
            f"constitutional successor {field_name} is not a SHA-256 reference"
        )
    try:
        int(text[7:], 16)
    except ValueError as exc:
        raise FailClosedRuntimeError(
            f"constitutional successor {field_name} is not a SHA-256 reference"
        ) from exc
    return text


def _require_exact_keys(
    value: Any,
    keys: set[str],
    field_name: str,
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != keys:
        raise FailClosedRuntimeError(
            f"constitutional successor {field_name} is malformed"
        )
    return value


def _require_text_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if (
        not isinstance(value, tuple)
        or any(not isinstance(item, str) for item in value)
        or any(not item.strip() or item != item.strip() for item in value)
        or len(value) != len(set(value))
    ):
        raise FailClosedRuntimeError(
            f"constitutional successor {field_name} is malformed"
        )
    return value


def _require_utc_timestamp(value: Any, field_name: str) -> str:
    text = _require_text(value, field_name)
    if not text.endswith("Z"):
        raise FailClosedRuntimeError(
            f"constitutional successor {field_name} is not canonical UTC"
        )
    try:
        parsed = datetime.fromisoformat(text[:-1] + "+00:00")
    except ValueError as exc:
        raise FailClosedRuntimeError(
            f"constitutional successor {field_name} is not canonical UTC"
        ) from exc
    if (
        parsed.tzinfo != timezone.utc
        or parsed.microsecond != 0
        or parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != text
    ):
        raise FailClosedRuntimeError(
            f"constitutional successor {field_name} is not canonical UTC"
        )
    return text


def _timestamp_value(value: str) -> datetime:
    return datetime.fromisoformat(value[:-1] + "+00:00")


def _identity(prefix: str, value: Any) -> str:
    return prefix + sha256(
        canonical_serialize(value).encode("utf-8")
    ).hexdigest()


def _digest(value: Any) -> str:
    return "sha256:" + sha256(
        canonical_serialize(value).encode("utf-8")
    ).hexdigest()


def constitutional_lineage_identity_v1(
    constitutional_artifact_identity: str,
) -> str:
    """Derive the stable lineage identity for one Constitutional artifact."""

    identity = _require_text(
        constitutional_artifact_identity,
        "constitutional_artifact_identity",
    )
    return _LINEAGE_IDENTITY_PREFIX + sha256(identity.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class ConstitutionalPreActivationLineageStateV1:
    """Immutable evidence of the sole active predecessor before activation."""

    state_version: str
    state_identity: str
    artifact_digest: str
    lineage_identity: str
    governing_owner: str
    active_constitution_identity: str
    active_constitution_version: str
    active_constitution_digest: str
    claimed_active_successor_identities: tuple[str, ...]
    observed_at: str

    def __post_init__(self) -> None:
        for field_name in (
            "state_version",
            "state_identity",
            "lineage_identity",
            "governing_owner",
            "active_constitution_identity",
            "active_constitution_version",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_text(getattr(self, field_name), field_name),
            )
        for field_name in ("artifact_digest", "active_constitution_digest"):
            object.__setattr__(
                self,
                field_name,
                _require_sha256(getattr(self, field_name), field_name),
            )
        object.__setattr__(
            self,
            "claimed_active_successor_identities",
            _require_text_tuple(
                self.claimed_active_successor_identities,
                "claimed_active_successor_identities",
            ),
        )
        object.__setattr__(
            self,
            "observed_at",
            _require_utc_timestamp(self.observed_at, "observed_at"),
        )

    def identity_payload(self) -> dict[str, Any]:
        return {
            "state_version": self.state_version,
            "lineage_identity": self.lineage_identity,
            "governing_owner": self.governing_owner,
            "active_constitution_identity": self.active_constitution_identity,
            "active_constitution_version": self.active_constitution_version,
            "active_constitution_digest": self.active_constitution_digest,
            "claimed_active_successor_identities": list(
                self.claimed_active_successor_identities
            ),
            "observed_at": self.observed_at,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "state_identity": self.state_identity,
            "artifact_digest": self.artifact_digest,
            **self.identity_payload(),
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "ConstitutionalPreActivationLineageStateV1":
        exact = _require_exact_keys(
            value,
            {
                "state_version",
                "state_identity",
                "artifact_digest",
                "lineage_identity",
                "governing_owner",
                "active_constitution_identity",
                "active_constitution_version",
                "active_constitution_digest",
                "claimed_active_successor_identities",
                "observed_at",
            },
            "lineage state",
        )
        if not isinstance(exact["claimed_active_successor_identities"], list):
            raise FailClosedRuntimeError(
                "constitutional successor active successor claims are malformed"
            )
        return cls(
            state_version=exact["state_version"],
            state_identity=exact["state_identity"],
            artifact_digest=exact["artifact_digest"],
            lineage_identity=exact["lineage_identity"],
            governing_owner=exact["governing_owner"],
            active_constitution_identity=exact["active_constitution_identity"],
            active_constitution_version=exact["active_constitution_version"],
            active_constitution_digest=exact["active_constitution_digest"],
            claimed_active_successor_identities=tuple(
                exact["claimed_active_successor_identities"]
            ),
            observed_at=exact["observed_at"],
        )


def create_constitutional_pre_activation_lineage_state_v1(
    *,
    governing_owner: str,
    active_constitution_identity: str,
    active_constitution_version: str,
    active_constitution_digest: str,
    claimed_active_successor_identities: Sequence[str],
    observed_at: str,
) -> ConstitutionalPreActivationLineageStateV1:
    """Create immutable explicit lineage state; activation validates conflicts."""

    if isinstance(claimed_active_successor_identities, (str, bytes)) or not isinstance(
        claimed_active_successor_identities, Sequence
    ):
        raise FailClosedRuntimeError(
            "constitutional successor active successor claims are malformed"
        )
    active_identity = _require_text(
        active_constitution_identity,
        "active_constitution_identity",
    )
    provisional = ConstitutionalPreActivationLineageStateV1(
        state_version=CONSTITUTIONAL_PRE_ACTIVATION_LINEAGE_STATE_VERSION,
        state_identity="PENDING-CONSTITUTIONAL-LINEAGE-STATE",
        artifact_digest="sha256:" + ("0" * 64),
        lineage_identity=constitutional_lineage_identity_v1(active_identity),
        governing_owner=_require_text(governing_owner, "governing_owner"),
        active_constitution_identity=active_identity,
        active_constitution_version=_require_text(
            active_constitution_version,
            "active_constitution_version",
        ),
        active_constitution_digest=_require_sha256(
            active_constitution_digest,
            "active_constitution_digest",
        ),
        claimed_active_successor_identities=tuple(
            claimed_active_successor_identities
        ),
        observed_at=_require_utc_timestamp(observed_at, "observed_at"),
    )
    return validate_constitutional_pre_activation_lineage_state_v1(
        replace(
            provisional,
            state_identity=_identity(
                _LINEAGE_STATE_IDENTITY_PREFIX,
                provisional.identity_payload(),
            ),
            artifact_digest=_digest(provisional.identity_payload()),
        )
    )


def validate_constitutional_pre_activation_lineage_state_v1(
    value: ConstitutionalPreActivationLineageStateV1 | Mapping[str, Any],
) -> ConstitutionalPreActivationLineageStateV1:
    """Validate exact immutable lineage-state identity and content."""

    state = (
        value
        if isinstance(value, ConstitutionalPreActivationLineageStateV1)
        else ConstitutionalPreActivationLineageStateV1.from_dict(value)
    )
    if state.state_version != CONSTITUTIONAL_PRE_ACTIVATION_LINEAGE_STATE_VERSION:
        raise FailClosedRuntimeError(
            "constitutional successor lineage state version is invalid"
        )
    if state.governing_owner != CONSTITUTIONAL_GOVERNANCE_OWNER:
        raise FailClosedRuntimeError(
            "constitutional successor lineage state owner is invalid"
        )
    if state.lineage_identity != constitutional_lineage_identity_v1(
        state.active_constitution_identity
    ):
        raise FailClosedRuntimeError(
            "constitutional successor lineage identity is invalid"
        )
    if (
        state.state_identity
        != _identity(_LINEAGE_STATE_IDENTITY_PREFIX, state.identity_payload())
        or state.artifact_digest != _digest(state.identity_payload())
    ):
        raise FailClosedRuntimeError(
            "constitutional successor lineage state identity is invalid"
        )
    return state


@dataclass(frozen=True, slots=True)
class ConstitutionalSuccessorMigrationEvidenceReferenceV1:
    """One immutable owner-produced migration or rollback reference."""

    evidence_role: str
    producing_owner: str
    artifact_identity: str
    artifact_digest: str

    def __post_init__(self) -> None:
        if self.evidence_role not in SUCCESSOR_EVIDENCE_ROLES:
            raise FailClosedRuntimeError(
                "constitutional successor evidence role is not recognized"
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
    ) -> "ConstitutionalSuccessorMigrationEvidenceReferenceV1":
        exact = _require_exact_keys(
            value,
            {
                "evidence_role",
                "producing_owner",
                "artifact_identity",
                "artifact_digest",
            },
            "migration evidence reference",
        )
        return cls(**dict(exact))


@dataclass(frozen=True, slots=True)
class ConstitutionalActivationScopeV1:
    """Exact activation scope copied from the certified amendment proposal."""

    scope_version: str
    scope_identity: str
    artifact_digest: str
    scope_kind: str
    target_constitutional_layer: str
    target_constitutional_owner: str
    target_constitutional_artifact_identity: str
    predecessor_constitution_version: str
    successor_constitution_version: str
    amendment_proposal_identity: str
    amendment_proposal_digest: str
    amendment_certification_identity: str
    amendment_certification_digest: str

    def __post_init__(self) -> None:
        for field_name in (
            "scope_version",
            "scope_identity",
            "scope_kind",
            "target_constitutional_layer",
            "target_constitutional_owner",
            "target_constitutional_artifact_identity",
            "predecessor_constitution_version",
            "successor_constitution_version",
            "amendment_proposal_identity",
            "amendment_certification_identity",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_text(getattr(self, field_name), field_name),
            )
        for field_name in (
            "artifact_digest",
            "amendment_proposal_digest",
            "amendment_certification_digest",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_sha256(getattr(self, field_name), field_name),
            )

    def identity_payload(self) -> dict[str, str]:
        return {
            "scope_version": self.scope_version,
            "scope_kind": self.scope_kind,
            "target_constitutional_layer": self.target_constitutional_layer,
            "target_constitutional_owner": self.target_constitutional_owner,
            "target_constitutional_artifact_identity": (
                self.target_constitutional_artifact_identity
            ),
            "predecessor_constitution_version": (
                self.predecessor_constitution_version
            ),
            "successor_constitution_version": self.successor_constitution_version,
            "amendment_proposal_identity": self.amendment_proposal_identity,
            "amendment_proposal_digest": self.amendment_proposal_digest,
            "amendment_certification_identity": (
                self.amendment_certification_identity
            ),
            "amendment_certification_digest": self.amendment_certification_digest,
        }

    def to_dict(self) -> dict[str, str]:
        return {
            "scope_identity": self.scope_identity,
            "artifact_digest": self.artifact_digest,
            **self.identity_payload(),
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "ConstitutionalActivationScopeV1":
        exact = _require_exact_keys(
            value,
            {
                "scope_version",
                "scope_identity",
                "artifact_digest",
                "scope_kind",
                "target_constitutional_layer",
                "target_constitutional_owner",
                "target_constitutional_artifact_identity",
                "predecessor_constitution_version",
                "successor_constitution_version",
                "amendment_proposal_identity",
                "amendment_proposal_digest",
                "amendment_certification_identity",
                "amendment_certification_digest",
            },
            "activation scope",
        )
        return cls(**dict(exact))


def _create_activation_scope(
    certification: ConstitutionalAmendmentCertificationArtifactV1,
) -> ConstitutionalActivationScopeV1:
    proposal = certification.human_ratification.impact_assessment.amendment_proposal
    provisional = ConstitutionalActivationScopeV1(
        scope_version=CONSTITUTIONAL_ACTIVATION_SCOPE_VERSION,
        scope_identity="PENDING-CONSTITUTIONAL-ACTIVATION-SCOPE",
        artifact_digest="sha256:" + ("0" * 64),
        scope_kind=EXACT_CERTIFIED_AMENDMENT_SCOPE,
        target_constitutional_layer=proposal.target_constitutional_layer,
        target_constitutional_owner=proposal.target_constitutional_owner,
        target_constitutional_artifact_identity=(
            proposal.target_constitutional_artifact_identity
        ),
        predecessor_constitution_version=(
            proposal.target_constitutional_artifact_version
        ),
        successor_constitution_version=proposal.proposed_successor_version,
        amendment_proposal_identity=proposal.proposal_identity,
        amendment_proposal_digest=proposal.artifact_digest,
        amendment_certification_identity=certification.certification_identity,
        amendment_certification_digest=certification.artifact_digest,
    )
    return replace(
        provisional,
        scope_identity=_identity(
            _ACTIVATION_SCOPE_IDENTITY_PREFIX,
            provisional.identity_payload(),
        ),
        artifact_digest=_digest(provisional.identity_payload()),
    )


def validate_constitutional_activation_scope_v1(
    *,
    value: ConstitutionalActivationScopeV1 | Mapping[str, Any],
    certification: ConstitutionalAmendmentCertificationArtifactV1
    | Mapping[str, Any],
) -> ConstitutionalActivationScopeV1:
    """Validate scope equality with the exact certified proposal."""

    scope = (
        value
        if isinstance(value, ConstitutionalActivationScopeV1)
        else ConstitutionalActivationScopeV1.from_dict(value)
    )
    certified = validate_constitutional_amendment_certification_artifact_v1(
        certification
    )
    if scope.scope_version != CONSTITUTIONAL_ACTIVATION_SCOPE_VERSION:
        raise FailClosedRuntimeError(
            "constitutional successor activation scope version is invalid"
        )
    expected = _create_activation_scope(certified)
    if scope != expected:
        raise FailClosedRuntimeError(
            "constitutional successor activation scope exceeds certified amendment"
        )
    return scope


@dataclass(frozen=True, slots=True)
class ConstitutionalSuccessorPublicationRecordV1:
    """Immutable publication record for one exact certified successor."""

    record_version: str
    publication_identity: str
    artifact_digest: str
    publication_status: str
    lineage_identity: str
    successor_constitution_identity: str
    successor_constitution_version: str
    successor_constitution_digest: str
    amendment_certification_identity: str
    amendment_certification_digest: str
    publishing_owner: str
    published_at: str

    def __post_init__(self) -> None:
        for field_name in (
            "record_version",
            "publication_identity",
            "publication_status",
            "lineage_identity",
            "successor_constitution_identity",
            "successor_constitution_version",
            "amendment_certification_identity",
            "publishing_owner",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_text(getattr(self, field_name), field_name),
            )
        for field_name in (
            "artifact_digest",
            "successor_constitution_digest",
            "amendment_certification_digest",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_sha256(getattr(self, field_name), field_name),
            )
        object.__setattr__(
            self,
            "published_at",
            _require_utc_timestamp(self.published_at, "published_at"),
        )

    def identity_payload(self) -> dict[str, str]:
        return {
            "record_version": self.record_version,
            "publication_status": self.publication_status,
            "lineage_identity": self.lineage_identity,
            "successor_constitution_identity": (
                self.successor_constitution_identity
            ),
            "successor_constitution_version": self.successor_constitution_version,
            "successor_constitution_digest": self.successor_constitution_digest,
            "amendment_certification_identity": (
                self.amendment_certification_identity
            ),
            "amendment_certification_digest": self.amendment_certification_digest,
            "publishing_owner": self.publishing_owner,
            "published_at": self.published_at,
        }

    def to_dict(self) -> dict[str, str]:
        return {
            "publication_identity": self.publication_identity,
            "artifact_digest": self.artifact_digest,
            **self.identity_payload(),
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "ConstitutionalSuccessorPublicationRecordV1":
        exact = _require_exact_keys(
            value,
            {
                "record_version",
                "publication_identity",
                "artifact_digest",
                "publication_status",
                "lineage_identity",
                "successor_constitution_identity",
                "successor_constitution_version",
                "successor_constitution_digest",
                "amendment_certification_identity",
                "amendment_certification_digest",
                "publishing_owner",
                "published_at",
            },
            "publication record",
        )
        return cls(**dict(exact))


@dataclass(frozen=True, slots=True)
class ConstitutionalSuccessorActivationRecordV1:
    """Immutable normative activation record with no runtime activation."""

    record_version: str
    activation_identity: str
    artifact_digest: str
    activation_status: str
    publication_identity: str
    publication_digest: str
    lineage_identity: str
    predecessor_constitution_identity: str
    predecessor_constitution_version: str
    successor_constitution_identity: str
    successor_constitution_version: str
    successor_constitution_digest: str
    activation_scope_identity: str
    activating_owner: str
    effective_at: str
    active_successor_count: int = 1
    runtime_feature_activation_performed: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "record_version",
            "activation_identity",
            "activation_status",
            "publication_identity",
            "lineage_identity",
            "predecessor_constitution_identity",
            "predecessor_constitution_version",
            "successor_constitution_identity",
            "successor_constitution_version",
            "activation_scope_identity",
            "activating_owner",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_text(getattr(self, field_name), field_name),
            )
        for field_name in (
            "artifact_digest",
            "publication_digest",
            "successor_constitution_digest",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_sha256(getattr(self, field_name), field_name),
            )
        object.__setattr__(
            self,
            "effective_at",
            _require_utc_timestamp(self.effective_at, "effective_at"),
        )
        if (
            not isinstance(self.active_successor_count, int)
            or isinstance(self.active_successor_count, bool)
            or self.active_successor_count < 0
        ):
            raise FailClosedRuntimeError(
                "constitutional successor active successor count is malformed"
            )
        if not isinstance(self.runtime_feature_activation_performed, bool):
            raise FailClosedRuntimeError(
                "constitutional successor runtime activation boundary is malformed"
            )

    def identity_payload(self) -> dict[str, Any]:
        return {
            "record_version": self.record_version,
            "activation_status": self.activation_status,
            "publication_identity": self.publication_identity,
            "publication_digest": self.publication_digest,
            "lineage_identity": self.lineage_identity,
            "predecessor_constitution_identity": (
                self.predecessor_constitution_identity
            ),
            "predecessor_constitution_version": (
                self.predecessor_constitution_version
            ),
            "successor_constitution_identity": (
                self.successor_constitution_identity
            ),
            "successor_constitution_version": self.successor_constitution_version,
            "successor_constitution_digest": self.successor_constitution_digest,
            "activation_scope_identity": self.activation_scope_identity,
            "activating_owner": self.activating_owner,
            "effective_at": self.effective_at,
            "active_successor_count": self.active_successor_count,
            "runtime_feature_activation_performed": (
                self.runtime_feature_activation_performed
            ),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "activation_identity": self.activation_identity,
            "artifact_digest": self.artifact_digest,
            **self.identity_payload(),
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "ConstitutionalSuccessorActivationRecordV1":
        exact = _require_exact_keys(
            value,
            {
                "record_version",
                "activation_identity",
                "artifact_digest",
                "activation_status",
                "publication_identity",
                "publication_digest",
                "lineage_identity",
                "predecessor_constitution_identity",
                "predecessor_constitution_version",
                "successor_constitution_identity",
                "successor_constitution_version",
                "successor_constitution_digest",
                "activation_scope_identity",
                "activating_owner",
                "effective_at",
                "active_successor_count",
                "runtime_feature_activation_performed",
            },
            "activation record",
        )
        return cls(**dict(exact))


@dataclass(frozen=True, slots=True)
class ConstitutionalSuccessorPublicationActivationV1:
    """One immutable published and normatively active Constitutional successor."""

    contract_version: str
    artifact_version: str
    serialization_version: str
    successor_artifact_identity: str
    artifact_digest: str
    successor_status: str
    certified_amendment: ConstitutionalAmendmentCertificationArtifactV1
    pre_activation_lineage_state: ConstitutionalPreActivationLineageStateV1
    constitutional_baseline_identity: str
    constitutional_baseline_digest: str
    predecessor_constitution_identity: str
    predecessor_constitution_version: str
    predecessor_constitution_digest: str
    successor_constitution_identity: str
    successor_constitution_version: str
    successor_constitution_digest: str
    successor_normative_change_statement: str
    activation_scope: ConstitutionalActivationScopeV1
    publication_record: ConstitutionalSuccessorPublicationRecordV1
    activation_record: ConstitutionalSuccessorActivationRecordV1
    predecessor_lifecycle_status: str
    migration_obligations: tuple[str, ...]
    compatibility_obligations: tuple[str, ...]
    migration_evidence_references: tuple[
        ConstitutionalSuccessorMigrationEvidenceReferenceV1, ...
    ]
    rollback_eligibility: str
    rollback_target_identity: str
    rollback_target_version: str
    rollback_target_digest: str
    predecessor_evidence_immutable: bool = True
    predecessor_history_rewritten: bool = False
    active_constitution_count: int = 1
    che_definition_count: int = 1
    production_hic_family_count: int = 1
    production_owner_chain_count: int = 1
    production_path_count: int = 1
    parallel_production_path_count: int = 0
    constitutional_publication_performed: bool = True
    constitutional_activation_performed: bool = True
    runtime_implementation_performed: bool = False
    runtime_feature_activation_performed: bool = False
    runtime_mutation_performed: bool = False
    production_mutation_performed: bool = False
    owner_mutation_performed: bool = False
    che_mutation_performed: bool = False
    hic_mutation_performed: bool = False
    replay_authority_changed: bool = False
    cro_authority_changed: bool = False
    hic_semantic_capability_introduced: bool = False
    cap_exclusivity_certified: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "contract_version",
            "artifact_version",
            "serialization_version",
            "successor_artifact_identity",
            "successor_status",
            "constitutional_baseline_identity",
            "predecessor_constitution_identity",
            "predecessor_constitution_version",
            "successor_constitution_identity",
            "successor_constitution_version",
            "successor_normative_change_statement",
            "predecessor_lifecycle_status",
            "rollback_eligibility",
            "rollback_target_identity",
            "rollback_target_version",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_text(getattr(self, field_name), field_name),
            )
        for field_name in (
            "artifact_digest",
            "constitutional_baseline_digest",
            "predecessor_constitution_digest",
            "successor_constitution_digest",
            "rollback_target_digest",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_sha256(getattr(self, field_name), field_name),
            )
        for field_name, expected_type in (
            (
                "certified_amendment",
                ConstitutionalAmendmentCertificationArtifactV1,
            ),
            (
                "pre_activation_lineage_state",
                ConstitutionalPreActivationLineageStateV1,
            ),
            ("activation_scope", ConstitutionalActivationScopeV1),
            (
                "publication_record",
                ConstitutionalSuccessorPublicationRecordV1,
            ),
            ("activation_record", ConstitutionalSuccessorActivationRecordV1),
        ):
            if not isinstance(getattr(self, field_name), expected_type):
                raise FailClosedRuntimeError(
                    f"constitutional successor {field_name} is malformed"
                )
        object.__setattr__(
            self,
            "migration_obligations",
            _require_text_tuple(self.migration_obligations, "migration_obligations"),
        )
        object.__setattr__(
            self,
            "compatibility_obligations",
            _require_text_tuple(
                self.compatibility_obligations,
                "compatibility_obligations",
            ),
        )
        if not isinstance(self.migration_evidence_references, tuple) or any(
            not isinstance(
                item,
                ConstitutionalSuccessorMigrationEvidenceReferenceV1,
            )
            for item in self.migration_evidence_references
        ):
            raise FailClosedRuntimeError(
                "constitutional successor migration evidence sequence is malformed"
            )
        for field_name in (
            "active_constitution_count",
            "che_definition_count",
            "production_hic_family_count",
            "production_owner_chain_count",
            "production_path_count",
            "parallel_production_path_count",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise FailClosedRuntimeError(
                    "constitutional successor topology is malformed"
                )
        for field_name in (
            "predecessor_evidence_immutable",
            "predecessor_history_rewritten",
            "constitutional_publication_performed",
            "constitutional_activation_performed",
            "runtime_implementation_performed",
            "runtime_feature_activation_performed",
            "runtime_mutation_performed",
            "production_mutation_performed",
            "owner_mutation_performed",
            "che_mutation_performed",
            "hic_mutation_performed",
            "replay_authority_changed",
            "cro_authority_changed",
            "hic_semantic_capability_introduced",
            "cap_exclusivity_certified",
        ):
            if not isinstance(getattr(self, field_name), bool):
                raise FailClosedRuntimeError(
                    "constitutional successor boundary is malformed"
                )

    def successor_identity_payload(self) -> dict[str, Any]:
        return {
            "constitutional_baseline_identity": self.constitutional_baseline_identity,
            "constitutional_baseline_digest": self.constitutional_baseline_digest,
            "predecessor_constitution_identity": (
                self.predecessor_constitution_identity
            ),
            "predecessor_constitution_version": (
                self.predecessor_constitution_version
            ),
            "predecessor_constitution_digest": self.predecessor_constitution_digest,
            "successor_constitution_version": self.successor_constitution_version,
            "successor_normative_change_statement": (
                self.successor_normative_change_statement
            ),
            "activation_scope": self.activation_scope.to_dict(),
            "amendment_certification_identity": (
                self.certified_amendment.certification_identity
            ),
            "amendment_certification_digest": self.certified_amendment.artifact_digest,
            "migration_obligations": list(self.migration_obligations),
            "compatibility_obligations": list(self.compatibility_obligations),
            "migration_evidence_references": [
                item.to_dict() for item in self.migration_evidence_references
            ],
            "rollback_eligibility": self.rollback_eligibility,
            "rollback_target_identity": self.rollback_target_identity,
            "rollback_target_version": self.rollback_target_version,
            "rollback_target_digest": self.rollback_target_digest,
        }

    def identity_payload(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "artifact_version": self.artifact_version,
            "serialization_version": self.serialization_version,
            "successor_status": self.successor_status,
            "certified_amendment": self.certified_amendment.to_dict(),
            "pre_activation_lineage_state": (
                self.pre_activation_lineage_state.to_dict()
            ),
            "constitutional_baseline_identity": self.constitutional_baseline_identity,
            "constitutional_baseline_digest": self.constitutional_baseline_digest,
            "predecessor_constitution_identity": (
                self.predecessor_constitution_identity
            ),
            "predecessor_constitution_version": (
                self.predecessor_constitution_version
            ),
            "predecessor_constitution_digest": self.predecessor_constitution_digest,
            "successor_constitution_identity": self.successor_constitution_identity,
            "successor_constitution_version": self.successor_constitution_version,
            "successor_constitution_digest": self.successor_constitution_digest,
            "successor_normative_change_statement": (
                self.successor_normative_change_statement
            ),
            "activation_scope": self.activation_scope.to_dict(),
            "publication_record": self.publication_record.to_dict(),
            "activation_record": self.activation_record.to_dict(),
            "predecessor_lifecycle_status": self.predecessor_lifecycle_status,
            "migration_obligations": list(self.migration_obligations),
            "compatibility_obligations": list(self.compatibility_obligations),
            "migration_evidence_references": [
                item.to_dict() for item in self.migration_evidence_references
            ],
            "rollback_eligibility": self.rollback_eligibility,
            "rollback_target_identity": self.rollback_target_identity,
            "rollback_target_version": self.rollback_target_version,
            "rollback_target_digest": self.rollback_target_digest,
            "predecessor_evidence_immutable": self.predecessor_evidence_immutable,
            "predecessor_history_rewritten": self.predecessor_history_rewritten,
            "active_constitution_count": self.active_constitution_count,
            "che_definition_count": self.che_definition_count,
            "production_hic_family_count": self.production_hic_family_count,
            "production_owner_chain_count": self.production_owner_chain_count,
            "production_path_count": self.production_path_count,
            "parallel_production_path_count": self.parallel_production_path_count,
            "constitutional_publication_performed": (
                self.constitutional_publication_performed
            ),
            "constitutional_activation_performed": (
                self.constitutional_activation_performed
            ),
            "runtime_implementation_performed": (
                self.runtime_implementation_performed
            ),
            "runtime_feature_activation_performed": (
                self.runtime_feature_activation_performed
            ),
            "runtime_mutation_performed": self.runtime_mutation_performed,
            "production_mutation_performed": self.production_mutation_performed,
            "owner_mutation_performed": self.owner_mutation_performed,
            "che_mutation_performed": self.che_mutation_performed,
            "hic_mutation_performed": self.hic_mutation_performed,
            "replay_authority_changed": self.replay_authority_changed,
            "cro_authority_changed": self.cro_authority_changed,
            "hic_semantic_capability_introduced": (
                self.hic_semantic_capability_introduced
            ),
            "cap_exclusivity_certified": self.cap_exclusivity_certified,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "successor_artifact_identity": self.successor_artifact_identity,
            "artifact_digest": self.artifact_digest,
            **self.identity_payload(),
        }

    @classmethod
    def from_dict(
        cls, value: Mapping[str, Any]
    ) -> "ConstitutionalSuccessorPublicationActivationV1":
        exact = _require_exact_keys(
            value,
            {
                "contract_version",
                "artifact_version",
                "serialization_version",
                "successor_artifact_identity",
                "artifact_digest",
                "successor_status",
                "certified_amendment",
                "pre_activation_lineage_state",
                "constitutional_baseline_identity",
                "constitutional_baseline_digest",
                "predecessor_constitution_identity",
                "predecessor_constitution_version",
                "predecessor_constitution_digest",
                "successor_constitution_identity",
                "successor_constitution_version",
                "successor_constitution_digest",
                "successor_normative_change_statement",
                "activation_scope",
                "publication_record",
                "activation_record",
                "predecessor_lifecycle_status",
                "migration_obligations",
                "compatibility_obligations",
                "migration_evidence_references",
                "rollback_eligibility",
                "rollback_target_identity",
                "rollback_target_version",
                "rollback_target_digest",
                "predecessor_evidence_immutable",
                "predecessor_history_rewritten",
                "active_constitution_count",
                "che_definition_count",
                "production_hic_family_count",
                "production_owner_chain_count",
                "production_path_count",
                "parallel_production_path_count",
                "constitutional_publication_performed",
                "constitutional_activation_performed",
                "runtime_implementation_performed",
                "runtime_feature_activation_performed",
                "runtime_mutation_performed",
                "production_mutation_performed",
                "owner_mutation_performed",
                "che_mutation_performed",
                "hic_mutation_performed",
                "replay_authority_changed",
                "cro_authority_changed",
                "hic_semantic_capability_introduced",
                "cap_exclusivity_certified",
            },
            "successor artifact",
        )
        for field_name in (
            "migration_obligations",
            "compatibility_obligations",
            "migration_evidence_references",
        ):
            if not isinstance(exact[field_name], list):
                raise FailClosedRuntimeError(
                    f"constitutional successor {field_name} is malformed"
                )
        return cls(
            contract_version=exact["contract_version"],
            artifact_version=exact["artifact_version"],
            serialization_version=exact["serialization_version"],
            successor_artifact_identity=exact["successor_artifact_identity"],
            artifact_digest=exact["artifact_digest"],
            successor_status=exact["successor_status"],
            certified_amendment=(
                ConstitutionalAmendmentCertificationArtifactV1.from_dict(
                    exact["certified_amendment"]
                )
            ),
            pre_activation_lineage_state=(
                ConstitutionalPreActivationLineageStateV1.from_dict(
                    exact["pre_activation_lineage_state"]
                )
            ),
            constitutional_baseline_identity=exact[
                "constitutional_baseline_identity"
            ],
            constitutional_baseline_digest=exact[
                "constitutional_baseline_digest"
            ],
            predecessor_constitution_identity=exact[
                "predecessor_constitution_identity"
            ],
            predecessor_constitution_version=exact[
                "predecessor_constitution_version"
            ],
            predecessor_constitution_digest=exact[
                "predecessor_constitution_digest"
            ],
            successor_constitution_identity=exact[
                "successor_constitution_identity"
            ],
            successor_constitution_version=exact[
                "successor_constitution_version"
            ],
            successor_constitution_digest=exact[
                "successor_constitution_digest"
            ],
            successor_normative_change_statement=exact[
                "successor_normative_change_statement"
            ],
            activation_scope=ConstitutionalActivationScopeV1.from_dict(
                exact["activation_scope"]
            ),
            publication_record=ConstitutionalSuccessorPublicationRecordV1.from_dict(
                exact["publication_record"]
            ),
            activation_record=ConstitutionalSuccessorActivationRecordV1.from_dict(
                exact["activation_record"]
            ),
            predecessor_lifecycle_status=exact["predecessor_lifecycle_status"],
            migration_obligations=tuple(exact["migration_obligations"]),
            compatibility_obligations=tuple(exact["compatibility_obligations"]),
            migration_evidence_references=tuple(
                ConstitutionalSuccessorMigrationEvidenceReferenceV1.from_dict(
                    item
                )
                for item in exact["migration_evidence_references"]
            ),
            rollback_eligibility=exact["rollback_eligibility"],
            rollback_target_identity=exact["rollback_target_identity"],
            rollback_target_version=exact["rollback_target_version"],
            rollback_target_digest=exact["rollback_target_digest"],
            predecessor_evidence_immutable=exact[
                "predecessor_evidence_immutable"
            ],
            predecessor_history_rewritten=exact[
                "predecessor_history_rewritten"
            ],
            active_constitution_count=exact["active_constitution_count"],
            che_definition_count=exact["che_definition_count"],
            production_hic_family_count=exact["production_hic_family_count"],
            production_owner_chain_count=exact[
                "production_owner_chain_count"
            ],
            production_path_count=exact["production_path_count"],
            parallel_production_path_count=exact[
                "parallel_production_path_count"
            ],
            constitutional_publication_performed=exact[
                "constitutional_publication_performed"
            ],
            constitutional_activation_performed=exact[
                "constitutional_activation_performed"
            ],
            runtime_implementation_performed=exact[
                "runtime_implementation_performed"
            ],
            runtime_feature_activation_performed=exact[
                "runtime_feature_activation_performed"
            ],
            runtime_mutation_performed=exact["runtime_mutation_performed"],
            production_mutation_performed=exact[
                "production_mutation_performed"
            ],
            owner_mutation_performed=exact["owner_mutation_performed"],
            che_mutation_performed=exact["che_mutation_performed"],
            hic_mutation_performed=exact["hic_mutation_performed"],
            replay_authority_changed=exact["replay_authority_changed"],
            cro_authority_changed=exact["cro_authority_changed"],
            hic_semantic_capability_introduced=exact[
                "hic_semantic_capability_introduced"
            ],
            cap_exclusivity_certified=exact["cap_exclusivity_certified"],
        )


def validate_constitutional_successor_migration_evidence_reference_v1(
    *,
    value: ConstitutionalSuccessorMigrationEvidenceReferenceV1
    | Mapping[str, Any],
    expected_role: str,
    expected_owner: str,
    expected_artifact_identity: str,
    expected_artifact_digest: str,
) -> ConstitutionalSuccessorMigrationEvidenceReferenceV1:
    """Validate exact migration evidence role, owner, identity, and digest."""

    evidence = (
        value
        if isinstance(value, ConstitutionalSuccessorMigrationEvidenceReferenceV1)
        else ConstitutionalSuccessorMigrationEvidenceReferenceV1.from_dict(value)
    )
    if (
        evidence.evidence_role != _require_text(expected_role, "expected_role")
        or evidence.producing_owner
        != _require_text(expected_owner, "expected_owner")
    ):
        raise FailClosedRuntimeError(
            "constitutional successor evidence role or owner is invalid"
        )
    if evidence.artifact_identity != _require_text(
        expected_artifact_identity,
        "expected_artifact_identity",
    ):
        raise FailClosedRuntimeError(
            "constitutional successor evidence identity is invalid"
        )
    if evidence.artifact_digest != _require_sha256(
        expected_artifact_digest,
        "expected_artifact_digest",
    ):
        raise FailClosedRuntimeError(
            "constitutional successor evidence digest is invalid"
        )
    return evidence


def _migration_evidence_specifications(
    *,
    target_owner: str,
    rollback_eligibility: str,
    evidence_references: tuple[
        ConstitutionalSuccessorMigrationEvidenceReferenceV1, ...
    ],
) -> tuple[tuple[str, str, str, str], ...]:
    rollback_role = (
        ROLLBACK_ELIGIBILITY_EVIDENCE
        if rollback_eligibility == ROLLBACK_ELIGIBLE
        else ROLLBACK_INELIGIBILITY_EVIDENCE
    )
    expected_roles_and_owners = (
        (MIGRATION_PLAN_EVIDENCE, target_owner),
        (COMPATIBILITY_EVIDENCE, target_owner),
        (PREDECESSOR_RETENTION_EVIDENCE, OWNER_LOCAL_REPLAY_CUSTODIAN),
        (rollback_role, target_owner),
    )
    if len(evidence_references) != len(expected_roles_and_owners):
        raise FailClosedRuntimeError(
            "constitutional successor migration evidence is incomplete"
        )
    return tuple(
        (
            role,
            owner,
            evidence.artifact_identity,
            evidence.artifact_digest,
        )
        for evidence, (role, owner) in zip(
            evidence_references,
            expected_roles_and_owners,
            strict=True,
        )
    )


def _validate_migration_evidence(
    *,
    target_owner: str,
    rollback_eligibility: str,
    evidence_references: tuple[
        ConstitutionalSuccessorMigrationEvidenceReferenceV1, ...
    ],
) -> tuple[ConstitutionalSuccessorMigrationEvidenceReferenceV1, ...]:
    specifications = _migration_evidence_specifications(
        target_owner=target_owner,
        rollback_eligibility=rollback_eligibility,
        evidence_references=evidence_references,
    )
    if tuple(item.evidence_role for item in evidence_references) != tuple(
        item[0] for item in specifications
    ):
        raise FailClosedRuntimeError(
            "constitutional successor migration evidence order is not canonical"
        )
    return tuple(
        validate_constitutional_successor_migration_evidence_reference_v1(
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


def _successor_identity_values(
    value: ConstitutionalSuccessorPublicationActivationV1,
) -> tuple[str, str]:
    payload = value.successor_identity_payload()
    return (
        _identity(_SUCCESSOR_IDENTITY_PREFIX, payload),
        _digest(payload),
    )


def _create_publication_record(
    *,
    lineage_identity: str,
    successor_identity: str,
    successor_version: str,
    successor_digest: str,
    certification: ConstitutionalAmendmentCertificationArtifactV1,
    published_at: str,
) -> ConstitutionalSuccessorPublicationRecordV1:
    provisional = ConstitutionalSuccessorPublicationRecordV1(
        record_version=CONSTITUTIONAL_SUCCESSOR_PUBLICATION_RECORD_VERSION,
        publication_identity="PENDING-CONSTITUTIONAL-SUCCESSOR-PUBLICATION",
        artifact_digest="sha256:" + ("0" * 64),
        publication_status=CONSTITUTIONAL_SUCCESSOR_PUBLISHED,
        lineage_identity=lineage_identity,
        successor_constitution_identity=successor_identity,
        successor_constitution_version=successor_version,
        successor_constitution_digest=successor_digest,
        amendment_certification_identity=certification.certification_identity,
        amendment_certification_digest=certification.artifact_digest,
        publishing_owner=CONSTITUTIONAL_GOVERNANCE_OWNER,
        published_at=published_at,
    )
    return replace(
        provisional,
        publication_identity=_identity(
            _PUBLICATION_IDENTITY_PREFIX,
            provisional.identity_payload(),
        ),
        artifact_digest=_digest(provisional.identity_payload()),
    )


def _create_activation_record(
    *,
    publication: ConstitutionalSuccessorPublicationRecordV1,
    predecessor_identity: str,
    predecessor_version: str,
    successor_identity: str,
    successor_version: str,
    successor_digest: str,
    activation_scope_identity: str,
    effective_at: str,
) -> ConstitutionalSuccessorActivationRecordV1:
    provisional = ConstitutionalSuccessorActivationRecordV1(
        record_version=CONSTITUTIONAL_SUCCESSOR_ACTIVATION_RECORD_VERSION,
        activation_identity="PENDING-CONSTITUTIONAL-SUCCESSOR-ACTIVATION",
        artifact_digest="sha256:" + ("0" * 64),
        activation_status=(
            CONSTITUTIONAL_SUCCESSOR_NORMATIVELY_ACTIVE_RUNTIME_NOT_IMPLEMENTED
        ),
        publication_identity=publication.publication_identity,
        publication_digest=publication.artifact_digest,
        lineage_identity=publication.lineage_identity,
        predecessor_constitution_identity=predecessor_identity,
        predecessor_constitution_version=predecessor_version,
        successor_constitution_identity=successor_identity,
        successor_constitution_version=successor_version,
        successor_constitution_digest=successor_digest,
        activation_scope_identity=activation_scope_identity,
        activating_owner=CONSTITUTIONAL_GOVERNANCE_OWNER,
        effective_at=effective_at,
    )
    return replace(
        provisional,
        activation_identity=_identity(
            _ACTIVATION_IDENTITY_PREFIX,
            provisional.identity_payload(),
        ),
        artifact_digest=_digest(provisional.identity_payload()),
    )


def _validate_predecessor_and_time_bindings(
    *,
    certification: ConstitutionalAmendmentCertificationArtifactV1,
    lineage_state: ConstitutionalPreActivationLineageStateV1,
    published_at: str,
    effective_at: str,
) -> None:
    proposal = certification.human_ratification.impact_assessment.amendment_proposal
    if (
        lineage_state.active_constitution_identity
        != proposal.target_constitutional_artifact_identity
        or lineage_state.active_constitution_version
        != proposal.target_constitutional_artifact_version
        or lineage_state.active_constitution_digest
        != proposal.target_constitutional_artifact_digest
    ):
        raise FailClosedRuntimeError(
            "constitutional successor predecessor identity or version is stale"
        )
    if lineage_state.claimed_active_successor_identities:
        raise FailClosedRuntimeError(
            "constitutional successor lineage already claims an active successor"
        )
    certified_at = _require_utc_timestamp(
        certification.certified_at,
        "certified_at",
    )
    publication_time = _require_utc_timestamp(published_at, "published_at")
    activation_time = _require_utc_timestamp(effective_at, "effective_at")
    if not (
        _timestamp_value(certified_at)
        <= _timestamp_value(lineage_state.observed_at)
        <= _timestamp_value(publication_time)
        <= _timestamp_value(activation_time)
    ):
        raise FailClosedRuntimeError(
            "constitutional successor temporal order is invalid"
        )


def publish_and_activate_constitutional_successor_v1(
    *,
    certified_amendment: ConstitutionalAmendmentCertificationArtifactV1
    | Mapping[str, Any],
    pre_activation_lineage_state: ConstitutionalPreActivationLineageStateV1
    | Mapping[str, Any],
    publishing_owner: str,
    activating_owner: str,
    migration_evidence_references: Sequence[
        ConstitutionalSuccessorMigrationEvidenceReferenceV1 | Mapping[str, Any]
    ],
    rollback_eligibility: str,
    published_at: str,
    effective_at: str,
) -> ConstitutionalSuccessorPublicationActivationV1:
    """Publish and normatively activate one exact successor without runtime work."""

    certification = validate_constitutional_amendment_certification_artifact_v1(
        certified_amendment
    )
    if certification.certification_status != (
        CONSTITUTIONAL_AMENDMENT_CERTIFIED_NOT_ACTIVATED
    ):
        raise FailClosedRuntimeError(
            "constitutional successor certification status is invalid"
        )
    lineage_state = validate_constitutional_pre_activation_lineage_state_v1(
        pre_activation_lineage_state
    )
    for owner, field_name in (
        (publishing_owner, "publishing_owner"),
        (activating_owner, "activating_owner"),
    ):
        if _require_text(owner, field_name) != CONSTITUTIONAL_GOVERNANCE_OWNER:
            raise FailClosedRuntimeError(
                "constitutional successor publication or activation owner is invalid"
            )
    if rollback_eligibility not in ROLLBACK_ELIGIBILITY_STATUSES:
        raise FailClosedRuntimeError(
            "constitutional successor rollback eligibility is invalid"
        )
    _validate_predecessor_and_time_bindings(
        certification=certification,
        lineage_state=lineage_state,
        published_at=published_at,
        effective_at=effective_at,
    )
    if isinstance(migration_evidence_references, (str, bytes)) or not isinstance(
        migration_evidence_references,
        Sequence,
    ):
        raise FailClosedRuntimeError(
            "constitutional successor migration evidence collection is malformed"
        )
    evidence = tuple(
        item
        if isinstance(item, ConstitutionalSuccessorMigrationEvidenceReferenceV1)
        else ConstitutionalSuccessorMigrationEvidenceReferenceV1.from_dict(item)
        for item in migration_evidence_references
    )
    proposal = certification.human_ratification.impact_assessment.amendment_proposal
    validated_evidence = _validate_migration_evidence(
        target_owner=proposal.target_constitutional_owner,
        rollback_eligibility=rollback_eligibility,
        evidence_references=evidence,
    )
    activation_scope = _create_activation_scope(certification)
    provisional = ConstitutionalSuccessorPublicationActivationV1(
        contract_version=(
            CONSTITUTIONAL_SUCCESSOR_PUBLICATION_ACTIVATION_CONTRACT_VERSION
        ),
        artifact_version=CONSTITUTIONAL_SUCCESSOR_ARTIFACT_VERSION,
        serialization_version=CONSTITUTIONAL_SUCCESSOR_SERIALIZATION_VERSION,
        successor_artifact_identity="PENDING-CONSTITUTIONAL-SUCCESSOR-ARTIFACT",
        artifact_digest="sha256:" + ("0" * 64),
        successor_status=(
            CONSTITUTIONAL_SUCCESSOR_PUBLISHED_AND_NORMATIVELY_ACTIVE
        ),
        certified_amendment=certification,
        pre_activation_lineage_state=lineage_state,
        constitutional_baseline_identity=proposal.constitutional_baseline_identity,
        constitutional_baseline_digest=proposal.constitutional_baseline_digest,
        predecessor_constitution_identity=(
            proposal.target_constitutional_artifact_identity
        ),
        predecessor_constitution_version=(
            proposal.target_constitutional_artifact_version
        ),
        predecessor_constitution_digest=(
            proposal.target_constitutional_artifact_digest
        ),
        successor_constitution_identity="PENDING-CONSTITUTIONAL-SUCCESSOR",
        successor_constitution_version=proposal.proposed_successor_version,
        successor_constitution_digest="sha256:" + ("0" * 64),
        successor_normative_change_statement=proposal.normative_change_statement,
        activation_scope=activation_scope,
        publication_record=ConstitutionalSuccessorPublicationRecordV1(
            record_version=CONSTITUTIONAL_SUCCESSOR_PUBLICATION_RECORD_VERSION,
            publication_identity="PENDING-PUBLICATION",
            artifact_digest="sha256:" + ("0" * 64),
            publication_status=CONSTITUTIONAL_SUCCESSOR_PUBLISHED,
            lineage_identity=lineage_state.lineage_identity,
            successor_constitution_identity="PENDING-SUCCESSOR",
            successor_constitution_version=proposal.proposed_successor_version,
            successor_constitution_digest="sha256:" + ("0" * 64),
            amendment_certification_identity=certification.certification_identity,
            amendment_certification_digest=certification.artifact_digest,
            publishing_owner=CONSTITUTIONAL_GOVERNANCE_OWNER,
            published_at=_require_utc_timestamp(published_at, "published_at"),
        ),
        activation_record=ConstitutionalSuccessorActivationRecordV1(
            record_version=CONSTITUTIONAL_SUCCESSOR_ACTIVATION_RECORD_VERSION,
            activation_identity="PENDING-ACTIVATION",
            artifact_digest="sha256:" + ("0" * 64),
            activation_status=(
                CONSTITUTIONAL_SUCCESSOR_NORMATIVELY_ACTIVE_RUNTIME_NOT_IMPLEMENTED
            ),
            publication_identity="PENDING-PUBLICATION",
            publication_digest="sha256:" + ("0" * 64),
            lineage_identity=lineage_state.lineage_identity,
            predecessor_constitution_identity=(
                proposal.target_constitutional_artifact_identity
            ),
            predecessor_constitution_version=(
                proposal.target_constitutional_artifact_version
            ),
            successor_constitution_identity="PENDING-SUCCESSOR",
            successor_constitution_version=proposal.proposed_successor_version,
            successor_constitution_digest="sha256:" + ("0" * 64),
            activation_scope_identity=activation_scope.scope_identity,
            activating_owner=CONSTITUTIONAL_GOVERNANCE_OWNER,
            effective_at=_require_utc_timestamp(effective_at, "effective_at"),
        ),
        predecessor_lifecycle_status=(
            PREDECESSOR_SUPERSEDED_RETAINED_IMMUTABLE
        ),
        migration_obligations=CONSTITUTIONAL_SUCCESSOR_MIGRATION_OBLIGATIONS,
        compatibility_obligations=(
            CONSTITUTIONAL_SUCCESSOR_COMPATIBILITY_OBLIGATIONS
        ),
        migration_evidence_references=validated_evidence,
        rollback_eligibility=rollback_eligibility,
        rollback_target_identity=proposal.target_constitutional_artifact_identity,
        rollback_target_version=proposal.target_constitutional_artifact_version,
        rollback_target_digest=proposal.target_constitutional_artifact_digest,
    )
    successor_identity, successor_digest = _successor_identity_values(provisional)
    with_successor = replace(
        provisional,
        successor_constitution_identity=successor_identity,
        successor_constitution_digest=successor_digest,
    )
    publication = _create_publication_record(
        lineage_identity=lineage_state.lineage_identity,
        successor_identity=successor_identity,
        successor_version=proposal.proposed_successor_version,
        successor_digest=successor_digest,
        certification=certification,
        published_at=published_at,
    )
    activation = _create_activation_record(
        publication=publication,
        predecessor_identity=proposal.target_constitutional_artifact_identity,
        predecessor_version=proposal.target_constitutional_artifact_version,
        successor_identity=successor_identity,
        successor_version=proposal.proposed_successor_version,
        successor_digest=successor_digest,
        activation_scope_identity=activation_scope.scope_identity,
        effective_at=effective_at,
    )
    completed = replace(
        with_successor,
        publication_record=publication,
        activation_record=activation,
    )
    return validate_constitutional_successor_publication_activation_v1(
        replace(
            completed,
            successor_artifact_identity=_identity(
                _SUCCESSOR_ARTIFACT_IDENTITY_PREFIX,
                completed.identity_payload(),
            ),
            artifact_digest=_digest(completed.identity_payload()),
        )
    )


def validate_constitutional_successor_publication_record_v1(
    value: ConstitutionalSuccessorPublicationRecordV1 | Mapping[str, Any],
) -> ConstitutionalSuccessorPublicationRecordV1:
    """Validate publication identity, owner, version, status, and digest."""

    record = (
        value
        if isinstance(value, ConstitutionalSuccessorPublicationRecordV1)
        else ConstitutionalSuccessorPublicationRecordV1.from_dict(value)
    )
    if (
        record.record_version
        != CONSTITUTIONAL_SUCCESSOR_PUBLICATION_RECORD_VERSION
        or record.publication_status != CONSTITUTIONAL_SUCCESSOR_PUBLISHED
        or record.publishing_owner != CONSTITUTIONAL_GOVERNANCE_OWNER
    ):
        raise FailClosedRuntimeError(
            "constitutional successor publication record is invalid"
        )
    if (
        record.publication_identity
        != _identity(_PUBLICATION_IDENTITY_PREFIX, record.identity_payload())
        or record.artifact_digest != _digest(record.identity_payload())
    ):
        raise FailClosedRuntimeError(
            "constitutional successor publication identity is invalid"
        )
    return record


def validate_constitutional_successor_activation_record_v1(
    value: ConstitutionalSuccessorActivationRecordV1 | Mapping[str, Any],
) -> ConstitutionalSuccessorActivationRecordV1:
    """Validate normative activation while rejecting runtime activation."""

    record = (
        value
        if isinstance(value, ConstitutionalSuccessorActivationRecordV1)
        else ConstitutionalSuccessorActivationRecordV1.from_dict(value)
    )
    if (
        record.record_version != CONSTITUTIONAL_SUCCESSOR_ACTIVATION_RECORD_VERSION
        or record.activation_status
        != CONSTITUTIONAL_SUCCESSOR_NORMATIVELY_ACTIVE_RUNTIME_NOT_IMPLEMENTED
        or record.activating_owner != CONSTITUTIONAL_GOVERNANCE_OWNER
        or record.active_successor_count != 1
        or record.runtime_feature_activation_performed
    ):
        raise FailClosedRuntimeError(
            "constitutional successor activation record is invalid"
        )
    if (
        record.activation_identity
        != _identity(_ACTIVATION_IDENTITY_PREFIX, record.identity_payload())
        or record.artifact_digest != _digest(record.identity_payload())
    ):
        raise FailClosedRuntimeError(
            "constitutional successor activation identity is invalid"
        )
    return record


def validate_constitutional_successor_publication_activation_v1(
    value: ConstitutionalSuccessorPublicationActivationV1 | Mapping[str, Any],
) -> ConstitutionalSuccessorPublicationActivationV1:
    """Fail closed on any predecessor, successor, evidence, or boundary drift."""

    successor = (
        value
        if isinstance(value, ConstitutionalSuccessorPublicationActivationV1)
        else ConstitutionalSuccessorPublicationActivationV1.from_dict(value)
    )
    if (
        successor.contract_version
        != CONSTITUTIONAL_SUCCESSOR_PUBLICATION_ACTIVATION_CONTRACT_VERSION
        or successor.artifact_version != CONSTITUTIONAL_SUCCESSOR_ARTIFACT_VERSION
        or successor.serialization_version
        != CONSTITUTIONAL_SUCCESSOR_SERIALIZATION_VERSION
    ):
        raise FailClosedRuntimeError(
            "constitutional successor version is invalid"
        )
    if successor.successor_status != (
        CONSTITUTIONAL_SUCCESSOR_PUBLISHED_AND_NORMATIVELY_ACTIVE
    ):
        raise FailClosedRuntimeError(
            "constitutional successor status is invalid"
        )
    certification = validate_constitutional_amendment_certification_artifact_v1(
        successor.certified_amendment
    )
    lineage_state = validate_constitutional_pre_activation_lineage_state_v1(
        successor.pre_activation_lineage_state
    )
    _validate_predecessor_and_time_bindings(
        certification=certification,
        lineage_state=lineage_state,
        published_at=successor.publication_record.published_at,
        effective_at=successor.activation_record.effective_at,
    )
    proposal = certification.human_ratification.impact_assessment.amendment_proposal
    expected_predecessor = (
        proposal.target_constitutional_artifact_identity,
        proposal.target_constitutional_artifact_version,
        proposal.target_constitutional_artifact_digest,
    )
    if (
        successor.constitutional_baseline_identity
        != proposal.constitutional_baseline_identity
        or successor.constitutional_baseline_digest
        != proposal.constitutional_baseline_digest
        or (
            successor.predecessor_constitution_identity,
            successor.predecessor_constitution_version,
            successor.predecessor_constitution_digest,
        )
        != expected_predecessor
        or successor.successor_constitution_version
        != proposal.proposed_successor_version
        or successor.successor_normative_change_statement
        != proposal.normative_change_statement
    ):
        raise FailClosedRuntimeError(
            "constitutional successor certified amendment binding is invalid"
        )
    scope = validate_constitutional_activation_scope_v1(
        value=successor.activation_scope,
        certification=certification,
    )
    if scope != successor.activation_scope:
        raise FailClosedRuntimeError(
            "constitutional successor activation scope correlation is invalid"
        )
    if successor.rollback_eligibility not in ROLLBACK_ELIGIBILITY_STATUSES:
        raise FailClosedRuntimeError(
            "constitutional successor rollback eligibility is invalid"
        )
    if (
        successor.rollback_target_identity,
        successor.rollback_target_version,
        successor.rollback_target_digest,
    ) != expected_predecessor:
        raise FailClosedRuntimeError(
            "constitutional successor rollback target is invalid"
        )
    if successor.migration_obligations != (
        CONSTITUTIONAL_SUCCESSOR_MIGRATION_OBLIGATIONS
    ) or successor.compatibility_obligations != (
        CONSTITUTIONAL_SUCCESSOR_COMPATIBILITY_OBLIGATIONS
    ):
        raise FailClosedRuntimeError(
            "constitutional successor migration or compatibility "
            "obligations are invalid"
        )
    evidence = _validate_migration_evidence(
        target_owner=proposal.target_constitutional_owner,
        rollback_eligibility=successor.rollback_eligibility,
        evidence_references=successor.migration_evidence_references,
    )
    if evidence != successor.migration_evidence_references:
        raise FailClosedRuntimeError(
            "constitutional successor migration evidence correlation is invalid"
        )
    expected_successor_identity, expected_successor_digest = (
        _successor_identity_values(successor)
    )
    if (
        successor.successor_constitution_identity != expected_successor_identity
        or successor.successor_constitution_digest != expected_successor_digest
    ):
        raise FailClosedRuntimeError(
            "constitutional successor identity is invalid"
        )
    publication = validate_constitutional_successor_publication_record_v1(
        successor.publication_record
    )
    expected_publication = _create_publication_record(
        lineage_identity=lineage_state.lineage_identity,
        successor_identity=successor.successor_constitution_identity,
        successor_version=successor.successor_constitution_version,
        successor_digest=successor.successor_constitution_digest,
        certification=certification,
        published_at=publication.published_at,
    )
    if publication != expected_publication:
        raise FailClosedRuntimeError(
            "constitutional successor publication binding is invalid"
        )
    activation = validate_constitutional_successor_activation_record_v1(
        successor.activation_record
    )
    expected_activation = _create_activation_record(
        publication=publication,
        predecessor_identity=successor.predecessor_constitution_identity,
        predecessor_version=successor.predecessor_constitution_version,
        successor_identity=successor.successor_constitution_identity,
        successor_version=successor.successor_constitution_version,
        successor_digest=successor.successor_constitution_digest,
        activation_scope_identity=scope.scope_identity,
        effective_at=activation.effective_at,
    )
    if activation != expected_activation:
        raise FailClosedRuntimeError(
            "constitutional successor activation binding is invalid"
        )
    boundaries = (
        successor.predecessor_lifecycle_status,
        successor.predecessor_evidence_immutable,
        successor.predecessor_history_rewritten,
        successor.active_constitution_count,
        successor.che_definition_count,
        successor.production_hic_family_count,
        successor.production_owner_chain_count,
        successor.production_path_count,
        successor.parallel_production_path_count,
        successor.constitutional_publication_performed,
        successor.constitutional_activation_performed,
        successor.runtime_implementation_performed,
        successor.runtime_feature_activation_performed,
        successor.runtime_mutation_performed,
        successor.production_mutation_performed,
        successor.owner_mutation_performed,
        successor.che_mutation_performed,
        successor.hic_mutation_performed,
        successor.replay_authority_changed,
        successor.cro_authority_changed,
        successor.hic_semantic_capability_introduced,
        successor.cap_exclusivity_certified,
    )
    if boundaries != (
        PREDECESSOR_SUPERSEDED_RETAINED_IMMUTABLE,
        True,
        False,
        1,
        1,
        1,
        1,
        1,
        0,
        True,
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
            "constitutional successor boundary invariants are invalid"
        )
    if (
        successor.successor_artifact_identity
        != _identity(
            _SUCCESSOR_ARTIFACT_IDENTITY_PREFIX,
            successor.identity_payload(),
        )
        or successor.artifact_digest != _digest(successor.identity_payload())
    ):
        raise FailClosedRuntimeError(
            "constitutional successor artifact identity is invalid"
        )
    return successor


def serialize_constitutional_successor_publication_activation_v1(
    successor: ConstitutionalSuccessorPublicationActivationV1
    | Mapping[str, Any],
) -> str:
    """Return canonical successor publication/activation JSON without writing."""

    validated = validate_constitutional_successor_publication_activation_v1(
        successor
    )
    return canonical_serialize(validated.to_dict())


def deserialize_constitutional_successor_publication_activation_v1(
    serialized: str | bytes,
) -> ConstitutionalSuccessorPublicationActivationV1:
    """Parse only canonical UTF-8 successor JSON and fail closed on drift."""

    if isinstance(serialized, bytes):
        try:
            source = serialized.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise FailClosedRuntimeError(
                "constitutional successor serialization is not UTF-8"
            ) from exc
    elif isinstance(serialized, str):
        source = serialized
    else:
        raise FailClosedRuntimeError(
            "constitutional successor serialization is malformed"
        )
    try:
        decoded = json.loads(source)
    except json.JSONDecodeError as exc:
        raise FailClosedRuntimeError(
            "constitutional successor serialization is not valid JSON"
        ) from exc
    successor = validate_constitutional_successor_publication_activation_v1(
        decoded
    )
    if canonical_serialize(successor.to_dict()) != source:
        raise FailClosedRuntimeError(
            "constitutional successor serialization is not canonical"
        )
    return successor


__all__ = [
    "COMPATIBILITY_EVIDENCE",
    "CONSTITUTIONAL_ACTIVATION_SCOPE_VERSION",
    "CONSTITUTIONAL_PRE_ACTIVATION_LINEAGE_STATE_VERSION",
    "CONSTITUTIONAL_SUCCESSOR_ACTIVATION_RECORD_VERSION",
    "CONSTITUTIONAL_SUCCESSOR_ARTIFACT_VERSION",
    "CONSTITUTIONAL_SUCCESSOR_COMPATIBILITY_OBLIGATIONS",
    "CONSTITUTIONAL_SUCCESSOR_MIGRATION_OBLIGATIONS",
    "CONSTITUTIONAL_SUCCESSOR_NORMATIVELY_ACTIVE_RUNTIME_NOT_IMPLEMENTED",
    "CONSTITUTIONAL_SUCCESSOR_PUBLICATION_ACTIVATION_CONTRACT_VERSION",
    "CONSTITUTIONAL_SUCCESSOR_PUBLICATION_RECORD_VERSION",
    "CONSTITUTIONAL_SUCCESSOR_PUBLISHED",
    "CONSTITUTIONAL_SUCCESSOR_PUBLISHED_AND_NORMATIVELY_ACTIVE",
    "CONSTITUTIONAL_SUCCESSOR_SERIALIZATION_VERSION",
    "EXACT_CERTIFIED_AMENDMENT_SCOPE",
    "MIGRATION_PLAN_EVIDENCE",
    "PREDECESSOR_RETENTION_EVIDENCE",
    "PREDECESSOR_SUPERSEDED_RETAINED_IMMUTABLE",
    "ROLLBACK_ELIGIBILITY_EVIDENCE",
    "ROLLBACK_ELIGIBILITY_STATUSES",
    "ROLLBACK_ELIGIBLE",
    "ROLLBACK_INELIGIBILITY_EVIDENCE",
    "ROLLBACK_NOT_ELIGIBLE",
    "ConstitutionalActivationScopeV1",
    "ConstitutionalPreActivationLineageStateV1",
    "ConstitutionalSuccessorActivationRecordV1",
    "ConstitutionalSuccessorMigrationEvidenceReferenceV1",
    "ConstitutionalSuccessorPublicationActivationV1",
    "ConstitutionalSuccessorPublicationRecordV1",
    "constitutional_lineage_identity_v1",
    "create_constitutional_pre_activation_lineage_state_v1",
    "deserialize_constitutional_successor_publication_activation_v1",
    "publish_and_activate_constitutional_successor_v1",
    "serialize_constitutional_successor_publication_activation_v1",
    "validate_constitutional_activation_scope_v1",
    "validate_constitutional_pre_activation_lineage_state_v1",
    "validate_constitutional_successor_activation_record_v1",
    "validate_constitutional_successor_migration_evidence_reference_v1",
    "validate_constitutional_successor_publication_activation_v1",
    "validate_constitutional_successor_publication_record_v1",
]
