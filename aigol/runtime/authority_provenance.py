"""Reusable, read-only Profile B authority-provenance resolution.

This module does not issue Human authorization.  It validates immutable root
records and resolves only roots fixed by trusted composition before a gate
caller can submit a lookup reference.  It intentionally exposes no mutation,
registration, persistence, or alternate-resolver path.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


AUTHORITY_PROVENANCE_CONTRACT_VERSION = (
    "PROFILE_B_OWNER_ISSUED_AUTHORITY_PROVENANCE_ROOT_V1"
)
AUTHORIZATION_OWNER_IDENTITY = "HUMAN_CONSTITUTIONAL_AUTHORITY"
OWNER_ISSUED_AUTHORIZATION_ACT_CLASS = (
    "OWNER_ISSUED_HIGH_IMPACT_HUMAN_AUTHORIZATION_ACT_V1"
)
BOUNDED_EVIDENCE_REDUCTION_POLICY_AUTHORIZATION = (
    "BOUNDED_EVIDENCE_REDUCTION_POLICY_AUTHORIZATION"
)
IMMUTABLE_COMMIT_BOUND = "IMMUTABLE_COMMIT_BOUND"

_ROOT_FIELDS = frozenset(
    {
        "contract_version",
        "provenance_root_identity",
        "boundary_commit",
        "immutability_mode",
        "authorization_owner_identity",
        "authorization_act_class",
        "action_kind",
        "subject_identity",
        "scope",
        "act_revision",
        "request_evidence_correlation_identity",
        "request_evidence_correlation_hash",
        "owner_issued_authority_evidence",
        "immutable_content_hash",
    }
)


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise FailClosedRuntimeError(f"authority provenance {label} is invalid")
    return value


def _hash(value: Any, label: str) -> str:
    text = _text(value, label)
    if not text.startswith("sha256:") or len(text) != 71:
        raise FailClosedRuntimeError(f"authority provenance {label} is invalid")
    try:
        int(text[7:], 16)
    except ValueError as exc:
        raise FailClosedRuntimeError(
            f"authority provenance {label} is invalid"
        ) from exc
    return text


def _commit(value: Any) -> str:
    text = _text(value, "boundary commit")
    if len(text) != 40:
        raise FailClosedRuntimeError(
            "authority provenance boundary commit is invalid"
        )
    try:
        int(text, 16)
    except ValueError as exc:
        raise FailClosedRuntimeError(
            "authority provenance boundary commit is invalid"
        ) from exc
    return text


def _plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _plain(value[key]) for key in sorted(value)}
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    return deepcopy(value)


def _immutable(value: Any) -> Any:
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise FailClosedRuntimeError(
                "authority provenance object keys must be strings"
            )
        return MappingProxyType(
            {key: _immutable(value[key]) for key in sorted(value)}
        )
    if isinstance(value, (list, tuple)):
        return tuple(_immutable(item) for item in value)
    copied = deepcopy(value)
    canonical_serialize(copied)
    return copied


def authority_provenance_content_hash_v1(value: Mapping[str, Any]) -> str:
    """Hash one exact root without trusting its declared content hash."""

    if not isinstance(value, Mapping):
        raise FailClosedRuntimeError("authority provenance root is invalid")
    facts = _plain(value)
    if set(facts) != _ROOT_FIELDS:
        raise FailClosedRuntimeError("authority provenance root fields are invalid")
    facts.pop("immutable_content_hash")
    return replay_hash(facts)


def create_authority_provenance_root_v1(
    *,
    provenance_root_identity: str,
    boundary_commit: str,
    authorization_owner_identity: str,
    authorization_act_class: str,
    action_kind: str,
    subject_identity: str,
    scope: Mapping[str, Any],
    act_revision: int,
    request_evidence_correlation_identity: str,
    request_evidence_correlation_hash: str,
    owner_issued_authority_evidence: Mapping[str, Any],
) -> dict[str, Any]:
    """Materialize an immutable root candidate with zero authority by itself."""

    if not isinstance(scope, Mapping) or not scope:
        raise FailClosedRuntimeError("authority provenance scope is invalid")
    if not isinstance(owner_issued_authority_evidence, Mapping):
        raise FailClosedRuntimeError(
            "authority provenance owner-issued evidence is invalid"
        )
    if (
        not isinstance(act_revision, int)
        or isinstance(act_revision, bool)
        or act_revision < 1
    ):
        raise FailClosedRuntimeError("authority provenance act revision is invalid")
    root = {
        "contract_version": AUTHORITY_PROVENANCE_CONTRACT_VERSION,
        "provenance_root_identity": _text(
            provenance_root_identity, "root identity"
        ),
        "boundary_commit": _commit(boundary_commit),
        "immutability_mode": IMMUTABLE_COMMIT_BOUND,
        "authorization_owner_identity": _text(
            authorization_owner_identity, "owner identity"
        ),
        "authorization_act_class": _text(
            authorization_act_class, "act class"
        ),
        "action_kind": _text(action_kind, "action kind"),
        "subject_identity": _text(subject_identity, "subject identity"),
        "scope": _plain(scope),
        "act_revision": act_revision,
        "request_evidence_correlation_identity": _text(
            request_evidence_correlation_identity,
            "request evidence correlation identity",
        ),
        "request_evidence_correlation_hash": _hash(
            request_evidence_correlation_hash,
            "request evidence correlation hash",
        ),
        "owner_issued_authority_evidence": _plain(
            owner_issued_authority_evidence
        ),
        "immutable_content_hash": "",
    }
    root["immutable_content_hash"] = authority_provenance_content_hash_v1(root)
    validate_authority_provenance_root_v1(root)
    return root


def validate_authority_provenance_root_v1(value: Any) -> dict[str, Any]:
    """Validate structural closure and immutable content identity only."""

    if not isinstance(value, Mapping) or set(value) != _ROOT_FIELDS:
        raise FailClosedRuntimeError("authority provenance root fields are invalid")
    root = _plain(value)
    if root["contract_version"] != AUTHORITY_PROVENANCE_CONTRACT_VERSION:
        raise FailClosedRuntimeError(
            "authority provenance contract version is invalid"
        )
    for field_name in (
        "provenance_root_identity",
        "authorization_owner_identity",
        "authorization_act_class",
        "action_kind",
        "subject_identity",
        "request_evidence_correlation_identity",
    ):
        _text(root[field_name], field_name)
    _commit(root["boundary_commit"])
    if root["immutability_mode"] != IMMUTABLE_COMMIT_BOUND:
        raise FailClosedRuntimeError(
            "authority provenance immutability mode is invalid"
        )
    if not isinstance(root["scope"], dict) or not root["scope"]:
        raise FailClosedRuntimeError("authority provenance scope is invalid")
    canonical_serialize(root["scope"])
    if (
        not isinstance(root["act_revision"], int)
        or isinstance(root["act_revision"], bool)
        or root["act_revision"] < 1
    ):
        raise FailClosedRuntimeError("authority provenance act revision is invalid")
    _hash(
        root["request_evidence_correlation_hash"],
        "request evidence correlation hash",
    )
    if not isinstance(root["owner_issued_authority_evidence"], dict):
        raise FailClosedRuntimeError(
            "authority provenance owner-issued evidence is invalid"
        )
    _hash(root["immutable_content_hash"], "immutable content hash")
    if root["immutable_content_hash"] != authority_provenance_content_hash_v1(
        root
    ):
        raise FailClosedRuntimeError(
            "authority provenance immutable content hash is invalid"
        )
    canonical_serialize(root)
    return root


@dataclass(frozen=True, slots=True)
class TrustedAuthorityProvenanceBindingV1:
    """Trusted-composition binding outside the gate caller's input surface."""

    provenance_root_identity: str
    immutable_content_hash: str
    boundary_commit: str
    current_revision: int
    current: bool
    superseded_by: str | None = None

    def __post_init__(self) -> None:
        _text(self.provenance_root_identity, "binding root identity")
        _hash(self.immutable_content_hash, "binding immutable content hash")
        _commit(self.boundary_commit)
        if (
            not isinstance(self.current_revision, int)
            or isinstance(self.current_revision, bool)
            or self.current_revision < 1
        ):
            raise FailClosedRuntimeError(
                "authority provenance binding revision is invalid"
            )
        if type(self.current) is not bool:
            raise FailClosedRuntimeError(
                "authority provenance binding currentness is invalid"
            )
        if self.superseded_by is not None:
            _text(self.superseded_by, "binding superseding root")
        if self.current is not (self.superseded_by is None):
            raise FailClosedRuntimeError(
                "authority provenance binding supersession is inconsistent"
            )


class TrustedAuthorityProvenanceResolverV1:
    """Resolve a fixed immutable root set without any caller-writable method."""

    __slots__ = ("__roots", "__bindings", "__boundary_commit", "__sealed")

    def __init__(
        self,
        *,
        boundary_commit: str,
        roots: Iterable[Mapping[str, Any]],
        bindings: Iterable[TrustedAuthorityProvenanceBindingV1],
    ) -> None:
        fixed_boundary = _commit(boundary_commit)
        root_map: dict[str, Any] = {}
        for value in roots:
            root = validate_authority_provenance_root_v1(value)
            identity = root["provenance_root_identity"]
            if identity in root_map:
                raise FailClosedRuntimeError(
                    "authority provenance root identity is ambiguous"
                )
            root_map[identity] = _immutable(root)
        binding_map: dict[str, TrustedAuthorityProvenanceBindingV1] = {}
        for binding in bindings:
            if not isinstance(binding, TrustedAuthorityProvenanceBindingV1):
                raise FailClosedRuntimeError(
                    "authority provenance trusted binding is invalid"
                )
            if binding.provenance_root_identity in binding_map:
                raise FailClosedRuntimeError(
                    "authority provenance trusted binding is ambiguous"
                )
            binding_map[binding.provenance_root_identity] = binding
        if not root_map or set(root_map) != set(binding_map):
            raise FailClosedRuntimeError(
                "authority provenance trusted root set is incomplete"
            )
        for identity, root in root_map.items():
            binding = binding_map[identity]
            if (
                root["boundary_commit"] != fixed_boundary
                or binding.boundary_commit != fixed_boundary
                or root["immutable_content_hash"]
                != binding.immutable_content_hash
            ):
                raise FailClosedRuntimeError(
                    "authority provenance trusted root binding is invalid"
                )
        object.__setattr__(
            self,
            "_TrustedAuthorityProvenanceResolverV1__roots",
            MappingProxyType(root_map),
        )
        object.__setattr__(
            self,
            "_TrustedAuthorityProvenanceResolverV1__bindings",
            MappingProxyType(binding_map),
        )
        object.__setattr__(
            self,
            "_TrustedAuthorityProvenanceResolverV1__boundary_commit",
            fixed_boundary,
        )
        object.__setattr__(
            self, "_TrustedAuthorityProvenanceResolverV1__sealed", True
        )

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(
            self, "_TrustedAuthorityProvenanceResolverV1__sealed", False
        ):
            raise AttributeError("authority provenance resolver is immutable")
        object.__setattr__(self, name, value)

    @property
    def boundary_commit(self) -> str:
        return self.__boundary_commit

    def resolve(self, provenance_root_identity: str) -> dict[str, Any]:
        """Return one current pinned root or fail closed."""

        identity = _text(provenance_root_identity, "lookup reference")
        root = self.__roots.get(identity)
        binding = self.__bindings.get(identity)
        if root is None or binding is None:
            raise FailClosedRuntimeError(
                "authority provenance root is unresolved"
            )
        plain = _plain(root)
        if (
            binding.current is not True
            or binding.superseded_by is not None
            or binding.current_revision != plain["act_revision"]
        ):
            raise FailClosedRuntimeError(
                "authority provenance root is stale or superseded"
            )
        if (
            binding.immutable_content_hash != plain["immutable_content_hash"]
            or binding.boundary_commit != plain["boundary_commit"]
        ):
            raise FailClosedRuntimeError(
                "authority provenance trusted binding diverged"
            )
        validate_authority_provenance_root_v1(plain)
        return plain


__all__ = [
    "AUTHORITY_PROVENANCE_CONTRACT_VERSION",
    "AUTHORIZATION_OWNER_IDENTITY",
    "BOUNDED_EVIDENCE_REDUCTION_POLICY_AUTHORIZATION",
    "IMMUTABLE_COMMIT_BOUND",
    "OWNER_ISSUED_AUTHORIZATION_ACT_CLASS",
    "TrustedAuthorityProvenanceBindingV1",
    "TrustedAuthorityProvenanceResolverV1",
    "authority_provenance_content_hash_v1",
    "create_authority_provenance_root_v1",
    "validate_authority_provenance_root_v1",
]
