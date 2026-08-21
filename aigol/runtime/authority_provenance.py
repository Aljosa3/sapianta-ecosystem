"""Reusable, read-only Profile B authority-provenance resolution.

This module does not issue Human authorization.  It validates immutable root
records and resolves only roots fixed by trusted composition before a gate
caller can submit a lookup reference.  It intentionally exposes no mutation,
registration, persistence, or alternate-resolver path.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from aigol.runtime.canonical_che_evidence_correlation_contract_v1 import (
    RECORDED,
    canonical_che_evidence_correlation_record_path_v1,
    read_canonical_che_evidence_correlation_v1,
    validate_canonical_che_evidence_correlation_v1,
)
from aigol.runtime.canonical_human_authority_act_contract_v1 import (
    AUTHORIZATION,
    HUMAN_AUTHORITY_OWNER,
    bind_canonical_human_authority_act_to_che_v1,
    validate_canonical_human_authority_act_v1,
)
from aigol.runtime.canonical_human_entry_contract_v1 import (
    canonical_che_request_source_act_digest_v1,
    validate_canonical_che_continuation_envelope_v1,
    validate_canonical_che_request_envelope_v1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.profile_a_authority_process_boundary import (
    validate_profile_a_authority_process_context_v1,
)
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
PROFILE_A_OWNER_STATE_EVENT_VERSION = (
    "PROFILE_A_CHE_REPLAY_OWNER_STATE_PROVENANCE_EVENT_V1"
)
PROFILE_A_OWNER_STATE_ISSUED = "ISSUED"
PROFILE_A_OWNER_STATE_SUPERSEDED = "SUPERSEDED"
PROFILE_A_OWNER_STATE_REVOKED = "REVOKED"
PROFILE_A_OWNER_STATE_EVENT_KINDS = frozenset(
    {
        PROFILE_A_OWNER_STATE_ISSUED,
        PROFILE_A_OWNER_STATE_SUPERSEDED,
        PROFILE_A_OWNER_STATE_REVOKED,
    }
)
PROFILE_A_OWNER_STATE_STORE = "canonical_che_profile_a_owner_state_v1"
PROFILE_A_NOT_APPLICABLE = "NOT_APPLICABLE"
PROFILE_A_AUTHORITY_SCOPE = "BOUNDED_EVIDENCE_REDUCTION_POLICY"
PROFILE_A_AUTHORITY_COMMAND = "AUTHORIZE_BOUNDED_EVIDENCE_REDUCTION_POLICY"

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

_PROFILE_A_EVENT_FIELDS = frozenset(
    {
        "event_version",
        "event_identity",
        "runtime_scope_identity",
        "owner_state_identity",
        "owner_revision_before",
        "owner_revision_after",
        "policy_revision",
        "event_kind",
        "predecessor_event_hash",
        "effective_at",
        "expires_at",
        "payload_challenge",
        "correlation_identity",
        "correlation_hash",
        "provenance_root",
        "event_hash",
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


def _instant(value: Any, label: str) -> datetime:
    text = _text(value, label)
    if not text.endswith("Z"):
        raise FailClosedRuntimeError(
            f"authority provenance {label} must be UTC"
        )
    try:
        parsed = datetime.fromisoformat(text[:-1] + "+00:00")
    except ValueError as exc:
        raise FailClosedRuntimeError(
            f"authority provenance {label} is invalid"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(
        parsed
    ):
        raise FailClosedRuntimeError(
            f"authority provenance {label} must be UTC"
        )
    return parsed


def _profile_a_event_identity_facts(value: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: _plain(value[key])
        for key in sorted(
            _PROFILE_A_EVENT_FIELDS - {"event_identity", "event_hash"}
        )
    }


def _profile_a_event_identity(value: Mapping[str, Any]) -> str:
    return "PROFILE-A-OWNER-STATE-EVENT-" + replay_hash(
        _profile_a_event_identity_facts(value)
    ).removeprefix("sha256:")


def _profile_a_event_hash(value: Mapping[str, Any]) -> str:
    return replay_hash(
        {
            key: _plain(value[key])
            for key in sorted(_PROFILE_A_EVENT_FIELDS - {"event_hash"})
        }
    )


def _validate_profile_a_owner_authority_evidence_v1(
    root: Mapping[str, Any],
) -> tuple[dict[str, Any], Any]:
    evidence = root.get("owner_issued_authority_evidence")
    if not isinstance(evidence, Mapping) or set(evidence) != {
        "human_authority_act",
        "che_request",
        "che_continuation",
        "che_evidence_correlation",
    }:
        raise FailClosedRuntimeError(
            "Profile A owner authority evidence is incomplete"
        )
    act = validate_canonical_human_authority_act_v1(
        evidence["human_authority_act"]
    )
    request = validate_canonical_che_request_envelope_v1(
        evidence["che_request"]
    )
    continuation = validate_canonical_che_continuation_envelope_v1(
        evidence["che_continuation"]
    )
    correlation = validate_canonical_che_evidence_correlation_v1(
        evidence["che_evidence_correlation"]
    )
    bind_canonical_human_authority_act_to_che_v1(
        act,
        request,
        continuation,
        expected_authority_kind=AUTHORIZATION,
        expected_target_identity=root["subject_identity"],
        expected_target_revision=root["act_revision"],
        expected_producing_owner=HUMAN_AUTHORITY_OWNER,
        expected_owner=act.expected_owner,
        expected_authority_scope=PROFILE_A_AUTHORITY_SCOPE,
    )
    payload = act.to_dict()["payload"]
    if (
        not isinstance(payload, dict)
        or payload.get("command") != PROFILE_A_AUTHORITY_COMMAND
        or payload.get("policy_id") != root["subject_identity"]
        or payload.get("policy_version")
        != f"V{root['act_revision']}"
        or payload.get("applicable_at_commit") != root["boundary_commit"]
        or act.authority_kind != AUTHORIZATION
        or act.producing_owner != HUMAN_AUTHORITY_OWNER
        or act.authority_scope != PROFILE_A_AUTHORITY_SCOPE
    ):
        raise FailClosedRuntimeError(
            "Profile A Human authority payload binding is invalid"
        )
    if (
        correlation.evidence_status != RECORDED
        or correlation.actor_identity != act.actor_identity
        or correlation.request_identity != act.request_identity
        or correlation.source_act_identity != act.authority_act_identity
        or correlation.source_act_digest
        != canonical_che_request_source_act_digest_v1(request)
        or correlation.continuation_identity != act.continuation_identity
        or correlation.authority_act_identity != act.authority_act_identity
        or correlation.authority_kind != AUTHORIZATION
        or correlation.authority_requesting_owner_identity
        != act.expected_owner
        or correlation.authority_target_identity != act.target_identity
        or correlation.authority_target_revision != act.target_revision
        or correlation.authority_payload_digest != act.payload_digest
        or correlation.owner_state_identity
        != continuation.expected_owner_state_identity
        or correlation.owner_revision_before != act.target_revision
        or correlation.owner_revision_after != act.target_revision + 1
        or correlation.owner_advancement != "ADVANCED"
        or correlation.owner_disposition != "RECORDED"
    ):
        raise FailClosedRuntimeError(
            "Profile A CHE owner-state correlation is invalid"
        )
    correlation_hash = replay_hash(correlation.to_dict())
    if (
        root["request_evidence_correlation_identity"]
        != correlation.correlation_identity
        or root["request_evidence_correlation_hash"] != correlation_hash
    ):
        raise FailClosedRuntimeError(
            "Profile A root correlation binding is invalid"
        )
    expected_root_identity = _profile_a_root_identity_v1(
        authorization_owner_identity=root["authorization_owner_identity"],
        authorization_act_class=root["authorization_act_class"],
        action_kind=root["action_kind"],
        subject_identity=root["subject_identity"],
        scope=root["scope"],
        act_revision=root["act_revision"],
        payload_challenge=act.payload_digest,
        request_evidence_correlation_identity=(
            root["request_evidence_correlation_identity"]
        ),
        request_evidence_correlation_hash=(
            root["request_evidence_correlation_hash"]
        ),
        owner_issued_authority_evidence=evidence,
    )
    if root["provenance_root_identity"] != expected_root_identity:
        raise FailClosedRuntimeError(
            "Profile A owner-state root identity is non-canonical"
        )
    return payload, correlation


def _profile_a_scope_from_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    required = {
        "command",
        "domain_id",
        "policy_id",
        "policy_version",
        "authority_id",
        "applicable_at_commit",
        "allowed_evidence_classes",
        "allowed_reduction_types",
        "obligations_hash",
        "permanent_trail_hash",
        "cohort_hash",
    }
    if set(payload) != required:
        raise FailClosedRuntimeError(
            "Profile A Human authority payload fields are invalid"
        )
    return {
        "domain_id": payload["domain_id"],
        "policy_id": payload["policy_id"],
        "policy_version": payload["policy_version"],
        "applicable_at_commit": payload["applicable_at_commit"],
        "allowed_evidence_classes": _plain(payload["allowed_evidence_classes"]),
        "allowed_reduction_types": _plain(payload["allowed_reduction_types"]),
        "obligations_hash": payload["obligations_hash"],
        "permanent_trail_hash": payload["permanent_trail_hash"],
        "cohort_hash": payload["cohort_hash"],
    }


def _profile_a_root_identity_v1(
    *,
    authorization_owner_identity: str,
    authorization_act_class: str,
    action_kind: str,
    subject_identity: str,
    scope: Mapping[str, Any],
    act_revision: int,
    payload_challenge: str,
    request_evidence_correlation_identity: str,
    request_evidence_correlation_hash: str,
    owner_issued_authority_evidence: Mapping[str, Any],
) -> str:
    """Derive the root identity from every Human-adopted identity binding."""

    return "PROFILE-A-CHE-OWNER-ROOT-" + replay_hash(
        {
            "authorization_owner_identity": authorization_owner_identity,
            "authorization_act_class": authorization_act_class,
            "action_kind": action_kind,
            "subject_identity": subject_identity,
            "scope": _plain(scope),
            "act_revision": act_revision,
            "payload_challenge": payload_challenge,
            "request_evidence_correlation_identity": (
                request_evidence_correlation_identity
            ),
            "request_evidence_correlation_hash": (
                request_evidence_correlation_hash
            ),
            "immutable_owner_issued_authority_evidence_hash": replay_hash(
                _plain(owner_issued_authority_evidence)
            ),
        }
    ).removeprefix("sha256:")


def _create_profile_a_root_from_che_v1(
    *,
    request: Any,
    continuation: Any,
    authority_act: Any,
    correlation: Any,
) -> dict[str, Any]:
    canonical_request = validate_canonical_che_request_envelope_v1(request)
    canonical_continuation = validate_canonical_che_continuation_envelope_v1(
        continuation
    )
    canonical_act = validate_canonical_human_authority_act_v1(authority_act)
    canonical_correlation = validate_canonical_che_evidence_correlation_v1(
        correlation
    )
    payload = canonical_act.to_dict()["payload"]
    if not isinstance(payload, dict):
        raise FailClosedRuntimeError(
            "Profile A Human authority payload is invalid"
        )
    scope = _profile_a_scope_from_payload(payload)
    if (
        canonical_act.authority_kind != AUTHORIZATION
        or canonical_act.authority_scope != PROFILE_A_AUTHORITY_SCOPE
        or payload["command"] != PROFILE_A_AUTHORITY_COMMAND
        or payload["policy_id"] != canonical_act.target_identity
        or payload["policy_version"] != f"V{canonical_act.target_revision}"
        or payload["authority_id"] != canonical_act.expected_owner
    ):
        raise FailClosedRuntimeError(
            "Profile A authorization act is outside the adopted scope"
        )
    correlation_hash = replay_hash(canonical_correlation.to_dict())
    owner_issued_authority_evidence = {
        "human_authority_act": canonical_act.to_dict(),
        "che_request": canonical_request.to_dict(),
        "che_continuation": canonical_continuation.to_dict(),
        "che_evidence_correlation": canonical_correlation.to_dict(),
    }
    root_identity = _profile_a_root_identity_v1(
        authorization_owner_identity=AUTHORIZATION_OWNER_IDENTITY,
        authorization_act_class=OWNER_ISSUED_AUTHORIZATION_ACT_CLASS,
        action_kind=BOUNDED_EVIDENCE_REDUCTION_POLICY_AUTHORIZATION,
        subject_identity=canonical_act.target_identity,
        scope=scope,
        act_revision=canonical_act.target_revision,
        payload_challenge=canonical_act.payload_digest,
        request_evidence_correlation_identity=(
            canonical_correlation.correlation_identity
        ),
        request_evidence_correlation_hash=correlation_hash,
        owner_issued_authority_evidence=owner_issued_authority_evidence,
    )
    root = create_authority_provenance_root_v1(
        provenance_root_identity=root_identity,
        boundary_commit=payload["applicable_at_commit"],
        authorization_owner_identity=AUTHORIZATION_OWNER_IDENTITY,
        authorization_act_class=OWNER_ISSUED_AUTHORIZATION_ACT_CLASS,
        action_kind=BOUNDED_EVIDENCE_REDUCTION_POLICY_AUTHORIZATION,
        subject_identity=canonical_act.target_identity,
        scope=scope,
        act_revision=canonical_act.target_revision,
        request_evidence_correlation_identity=(
            canonical_correlation.correlation_identity
        ),
        request_evidence_correlation_hash=correlation_hash,
        owner_issued_authority_evidence=owner_issued_authority_evidence,
    )
    _validate_profile_a_owner_authority_evidence_v1(root)
    return root


def _create_profile_a_owner_state_event_v1(
    *,
    runtime_scope_identity: str,
    root: Mapping[str, Any],
    event_kind: str,
    predecessor_event_hash: str,
    effective_at: str,
    expires_at: str | None,
) -> dict[str, Any]:
    validated_root = validate_authority_provenance_root_v1(root)
    _, correlation = _validate_profile_a_owner_authority_evidence_v1(
        validated_root
    )
    if event_kind not in PROFILE_A_OWNER_STATE_EVENT_KINDS:
        raise FailClosedRuntimeError("Profile A owner-state event kind is invalid")
    if predecessor_event_hash != PROFILE_A_NOT_APPLICABLE:
        _hash(predecessor_event_hash, "owner-state predecessor event hash")
    effective = _instant(effective_at, "owner-state effective time")
    if expires_at is not None:
        expires = _instant(expires_at, "owner-state expiry time")
        if expires <= effective:
            raise FailClosedRuntimeError(
                "Profile A owner-state expiry is not after issuance"
            )
    event = {
        "event_version": PROFILE_A_OWNER_STATE_EVENT_VERSION,
        "event_identity": "",
        "runtime_scope_identity": _text(
            runtime_scope_identity, "owner-state runtime scope"
        ),
        "owner_state_identity": correlation.owner_state_identity,
        "owner_revision_before": correlation.owner_revision_before,
        "owner_revision_after": correlation.owner_revision_after,
        "policy_revision": validated_root["act_revision"],
        "event_kind": event_kind,
        "predecessor_event_hash": predecessor_event_hash,
        "effective_at": effective_at,
        "expires_at": expires_at,
        "payload_challenge": correlation.authority_payload_digest,
        "correlation_identity": correlation.correlation_identity,
        "correlation_hash": replay_hash(correlation.to_dict()),
        "provenance_root": validated_root,
        "event_hash": "",
    }
    event["event_identity"] = _profile_a_event_identity(event)
    event["event_hash"] = _profile_a_event_hash(event)
    return validate_profile_a_owner_state_event_v1(event)


def validate_profile_a_owner_state_event_v1(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != _PROFILE_A_EVENT_FIELDS:
        raise FailClosedRuntimeError(
            "Profile A owner-state event fields are invalid"
        )
    event = _plain(value)
    if event["event_version"] != PROFILE_A_OWNER_STATE_EVENT_VERSION:
        raise FailClosedRuntimeError(
            "Profile A owner-state event version is invalid"
        )
    for field_name in (
        "event_identity",
        "runtime_scope_identity",
        "owner_state_identity",
        "effective_at",
        "payload_challenge",
        "correlation_identity",
    ):
        _text(event[field_name], f"owner-state {field_name}")
    for field_name in (
        "owner_revision_before",
        "owner_revision_after",
        "policy_revision",
    ):
        if (
            not isinstance(event[field_name], int)
            or isinstance(event[field_name], bool)
            or event[field_name] < 1
        ):
            raise FailClosedRuntimeError(
                f"Profile A owner-state {field_name} is invalid"
            )
    if event["owner_revision_after"] != event["owner_revision_before"] + 1:
        raise FailClosedRuntimeError(
            "Profile A owner-state revision did not advance exactly once"
        )
    if event["policy_revision"] != event["owner_revision_before"]:
        raise FailClosedRuntimeError(
            "Profile A policy and owner-state revisions diverged"
        )
    if event["event_kind"] not in PROFILE_A_OWNER_STATE_EVENT_KINDS:
        raise FailClosedRuntimeError("Profile A owner-state event kind is invalid")
    if event["predecessor_event_hash"] != PROFILE_A_NOT_APPLICABLE:
        _hash(
            event["predecessor_event_hash"],
            "owner-state predecessor event hash",
        )
    _instant(event["effective_at"], "owner-state effective time")
    if event["expires_at"] is not None:
        if _instant(
            event["expires_at"], "owner-state expiry time"
        ) <= _instant(event["effective_at"], "owner-state effective time"):
            raise FailClosedRuntimeError(
                "Profile A owner-state expiry is not after issuance"
            )
    _hash(event["payload_challenge"], "owner-state payload challenge")
    _hash(event["correlation_hash"], "owner-state correlation hash")
    root = validate_authority_provenance_root_v1(event["provenance_root"])
    _, correlation = _validate_profile_a_owner_authority_evidence_v1(root)
    request_facts = root["owner_issued_authority_evidence"]["che_request"]
    act_facts = root["owner_issued_authority_evidence"]["human_authority_act"]
    if (
        event["owner_state_identity"] != correlation.owner_state_identity
        or event["owner_revision_before"] != correlation.owner_revision_before
        or event["owner_revision_after"] != correlation.owner_revision_after
        or event["policy_revision"] != root["act_revision"]
        or event["payload_challenge"] != correlation.authority_payload_digest
        or event["correlation_identity"] != correlation.correlation_identity
        or event["correlation_hash"] != replay_hash(correlation.to_dict())
        or event["effective_at"] != request_facts["created_at"]
        or event["expires_at"]
        != act_facts["metadata"].get("profile_a_expires_at")
    ):
        raise FailClosedRuntimeError(
            "Profile A owner-state event provenance binding is invalid"
        )
    if event["event_identity"] != _profile_a_event_identity(event):
        raise FailClosedRuntimeError(
            "Profile A owner-state event identity is invalid"
        )
    if event["event_hash"] != _profile_a_event_hash(event):
        raise FailClosedRuntimeError(
            "Profile A owner-state event hash is invalid"
        )
    canonical_serialize(event)
    return event


def _profile_a_owner_state_directory_v1(
    owner_state_store_root: str, owner_state_identity: str
) -> Path:
    storage_root = _text(owner_state_store_root, "owner-state storage root")
    owner_state = _text(owner_state_identity, "owner-state identity")
    digest = replay_hash(
        {"owner_state_identity": owner_state}
    ).removeprefix("sha256:")
    return Path(storage_root) / PROFILE_A_OWNER_STATE_STORE / f"state-{digest}"


def _profile_a_owner_state_event_path_v1(
    owner_state_store_root: str,
    owner_state_identity: str,
    policy_revision: int,
) -> Path:
    return _profile_a_owner_state_directory_v1(
        owner_state_store_root, owner_state_identity
    ) / f"event-{policy_revision:020d}.json"


def _load_profile_a_owner_state_events_v1(
    che_runtime_scope_identity: str,
    owner_state_store_root: str,
    owner_state_identity: str,
) -> tuple[dict[str, Any], ...]:
    directory = _profile_a_owner_state_directory_v1(
        owner_state_store_root, owner_state_identity
    )
    if not directory.is_dir():
        raise FailClosedRuntimeError(
            "Profile A CHE/Replay owner state is unavailable"
        )
    events: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json")):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise FailClosedRuntimeError(
                "Profile A owner-state event is unreadable"
            ) from exc
        event = validate_profile_a_owner_state_event_v1(value)
        expected_path = _profile_a_owner_state_event_path_v1(
            owner_state_store_root,
            owner_state_identity,
            event["policy_revision"],
        )
        if path != expected_path:
            raise FailClosedRuntimeError(
                "Profile A owner-state event is aliased or forked"
            )
        if (
            event["runtime_scope_identity"] != che_runtime_scope_identity
            or event["owner_state_identity"] != owner_state_identity
        ):
            raise FailClosedRuntimeError(
                "Profile A owner-state source binding is invalid"
            )
        correlation_path = canonical_che_evidence_correlation_record_path_v1(
            che_runtime_scope_identity, event["correlation_identity"]
        )
        persisted = read_canonical_che_evidence_correlation_v1(
            correlation_path
        )
        if (
            persisted.to_dict()
            != event["provenance_root"]["owner_issued_authority_evidence"][
                "che_evidence_correlation"
            ]
            or replay_hash(persisted.to_dict()) != event["correlation_hash"]
        ):
            raise FailClosedRuntimeError(
                "Profile A owner-state CHE read-back binding is invalid"
            )
        events.append(event)
    if not events:
        raise FailClosedRuntimeError(
            "Profile A CHE/Replay owner state is unresolved"
        )
    return tuple(events)


def _persist_profile_a_owner_state_authorization_v1(
    *,
    request: Any,
    continuation: Any,
    authority_act: Any,
    correlation: Any,
    _authority_process_context: Any = None,
) -> Path:
    authority_context = validate_profile_a_authority_process_context_v1(
        _authority_process_context,
        allow_zero_authority_test=True,
    )
    root = _create_profile_a_root_from_che_v1(
        request=request,
        continuation=continuation,
        authority_act=authority_act,
        correlation=correlation,
    )
    canonical_request = validate_canonical_che_request_envelope_v1(request)
    canonical_act = validate_canonical_human_authority_act_v1(authority_act)
    canonical_correlation = validate_canonical_che_evidence_correlation_v1(
        correlation
    )
    if (
        canonical_request.runtime_scope_identity
        != authority_context.che_runtime_scope_identity
        or canonical_correlation.runtime_scope_identity
        != authority_context.che_runtime_scope_identity
        or canonical_correlation.owner_state_identity
        != authority_context.owner_state_identity
    ):
        raise FailClosedRuntimeError(
            "Profile A owner-state source is not the process startup binding"
        )
    existing_revision_path = _profile_a_owner_state_event_path_v1(
        authority_context.owner_state_store_root,
        authority_context.owner_state_identity,
        canonical_act.target_revision,
    )
    if existing_revision_path.exists():
        try:
            existing_event = validate_profile_a_owner_state_event_v1(
                json.loads(existing_revision_path.read_text(encoding="utf-8"))
            )
        except (OSError, json.JSONDecodeError) as exc:
            raise FailClosedRuntimeError(
                "Profile A owner-state event is unreadable"
            ) from exc
        if (
            existing_event["runtime_scope_identity"]
            != authority_context.che_runtime_scope_identity
            or existing_event["owner_state_identity"]
            != authority_context.owner_state_identity
            or existing_event["provenance_root"] != root
        ):
            raise FailClosedRuntimeError(
                "Profile A owner-state event identity conflicts"
            )
        return existing_revision_path
    try:
        prior_events = _load_profile_a_owner_state_events_v1(
            authority_context.che_runtime_scope_identity,
            authority_context.owner_state_store_root,
            authority_context.owner_state_identity,
        )
    except FailClosedRuntimeError as exc:
        if "unavailable" not in str(exc) and "unresolved" not in str(exc):
            raise
        prior_events = ()
    predecessor = (
        prior_events[-1]["event_hash"]
        if prior_events
        else PROFILE_A_NOT_APPLICABLE
    )
    event_kind = (
        PROFILE_A_OWNER_STATE_SUPERSEDED
        if prior_events
        else PROFILE_A_OWNER_STATE_ISSUED
    )
    if prior_events and (
        prior_events[-1]["event_kind"] == PROFILE_A_OWNER_STATE_REVOKED
        or prior_events[-1]["owner_revision_after"]
        != canonical_correlation.owner_revision_before
    ):
        raise FailClosedRuntimeError(
            "Profile A owner-state predecessor continuity is invalid"
        )
    expires_at = canonical_act.to_dict()["metadata"].get(
        "profile_a_expires_at"
    )
    if expires_at is not None and not isinstance(expires_at, str):
        raise FailClosedRuntimeError(
            "Profile A owner-state expiry metadata is invalid"
        )
    event = _create_profile_a_owner_state_event_v1(
        runtime_scope_identity=canonical_request.runtime_scope_identity,
        root=root,
        event_kind=event_kind,
        predecessor_event_hash=predecessor,
        effective_at=canonical_request.created_at,
        expires_at=expires_at,
    )
    path = _profile_a_owner_state_event_path_v1(
        authority_context.owner_state_store_root,
        authority_context.owner_state_identity,
        event["policy_revision"],
    )
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise FailClosedRuntimeError(
                "Profile A owner-state event is unreadable"
            ) from exc
        if validate_profile_a_owner_state_event_v1(existing) != event:
            raise FailClosedRuntimeError(
                "Profile A owner-state event identity conflicts"
            )
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name = ""
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".profile-a-owner-state-",
            suffix=".tmp",
            dir=path.parent,
            text=True,
        )
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(canonical_serialize(event) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary_name, path)
    except FileExistsError:
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise FailClosedRuntimeError(
                "Profile A owner-state event is unreadable"
            ) from exc
        if validate_profile_a_owner_state_event_v1(existing) != event:
            raise FailClosedRuntimeError(
                "Profile A owner-state event identity conflicts"
            )
    except OSError as exc:
        raise FailClosedRuntimeError(
            "Profile A owner-state event write failed"
        ) from exc
    finally:
        if temporary_name and Path(temporary_name).exists():
            Path(temporary_name).unlink()
    return path


class _ProfileACheReplayOwnerStateResolverV1:
    """Read one fixed CHE/Replay owner state on every gate evaluation."""

    __slots__ = (
        "__authority_process_context",
        "__che_runtime_scope_identity",
        "__owner_state_store_root",
        "__owner_state_identity",
        "__sealed",
    )

    def __init__(
        self,
        *,
        _authority_process_context: Any,
    ) -> None:
        authority_context = validate_profile_a_authority_process_context_v1(
            _authority_process_context,
            allow_zero_authority_test=True,
        )
        object.__setattr__(
            self,
            "_ProfileACheReplayOwnerStateResolverV1__authority_process_context",
            authority_context,
        )
        object.__setattr__(
            self,
            "_ProfileACheReplayOwnerStateResolverV1__che_runtime_scope_identity",
            authority_context.che_runtime_scope_identity,
        )
        object.__setattr__(
            self,
            "_ProfileACheReplayOwnerStateResolverV1__owner_state_store_root",
            authority_context.owner_state_store_root,
        )
        object.__setattr__(
            self,
            "_ProfileACheReplayOwnerStateResolverV1__owner_state_identity",
            authority_context.owner_state_identity,
        )
        object.__setattr__(
            self, "_ProfileACheReplayOwnerStateResolverV1__sealed", True
        )

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(
            self, "_ProfileACheReplayOwnerStateResolverV1__sealed", False
        ):
            raise AttributeError("Profile A owner-state resolver is immutable")
        object.__setattr__(self, name, value)

    @property
    def owner_state_identity(self) -> str:
        return self.__owner_state_identity

    def resolve(self, provenance_root_identity: str) -> tuple[dict[str, Any], str]:
        validate_profile_a_authority_process_context_v1(
            self.__authority_process_context,
            allow_zero_authority_test=True,
        )
        identity = _text(provenance_root_identity, "lookup reference")
        events = _load_profile_a_owner_state_events_v1(
            self.__che_runtime_scope_identity,
            self.__owner_state_store_root,
            self.__owner_state_identity,
        )
        previous: dict[str, Any] | None = None
        seen_roots: set[str] = set()
        first_policy_revision = events[0]["policy_revision"]
        for index, event in enumerate(events):
            expected_revision = first_policy_revision + index
            if event["policy_revision"] != expected_revision:
                raise FailClosedRuntimeError(
                    "Profile A owner-state lineage is missing or rolled back"
                )
            if index == 0:
                if (
                    event["event_kind"] != PROFILE_A_OWNER_STATE_ISSUED
                    or event["predecessor_event_hash"]
                    != PROFILE_A_NOT_APPLICABLE
                ):
                    raise FailClosedRuntimeError(
                        "Profile A owner-state genesis is invalid"
                    )
            else:
                assert previous is not None
                if (
                    event["event_kind"]
                    not in {
                        PROFILE_A_OWNER_STATE_SUPERSEDED,
                        PROFILE_A_OWNER_STATE_REVOKED,
                    }
                    or event["predecessor_event_hash"]
                    != previous["event_hash"]
                    or event["owner_revision_before"]
                    != previous["owner_revision_after"]
                    or previous["event_kind"] == PROFILE_A_OWNER_STATE_REVOKED
                ):
                    raise FailClosedRuntimeError(
                        "Profile A owner-state predecessor or fork is invalid"
                    )
            root_identity = event["provenance_root"][
                "provenance_root_identity"
            ]
            if (
                root_identity in seen_roots
                and event["event_kind"] != PROFILE_A_OWNER_STATE_REVOKED
            ):
                raise FailClosedRuntimeError(
                    "Profile A owner-state root identity is aliased"
                )
            seen_roots.add(root_identity)
            previous = event
        latest = events[-1]
        correlation_root = (
            Path(self.__che_runtime_scope_identity)
            / "canonical_che_evidence_correlations_v1"
        )
        observed_revisions: dict[int, set[str]] = {}
        if correlation_root.is_dir():
            for correlation_path in sorted(
                correlation_root.glob("correlation-*.json")
            ):
                correlation = read_canonical_che_evidence_correlation_v1(
                    correlation_path
                )
                if (
                    correlation.owner_state_identity
                    == self.__owner_state_identity
                    and correlation.authority_kind == AUTHORIZATION
                    and correlation.owner_advancement == "ADVANCED"
                    and correlation.owner_disposition == "RECORDED"
                    and correlation.evidence_status == RECORDED
                ):
                    observed_revisions.setdefault(
                        correlation.owner_revision_after, set()
                    ).add(correlation.correlation_identity)
        expected_owner_revisions = {
            event["owner_revision_after"] for event in events
        }
        if (
            not observed_revisions
            or set(observed_revisions) != expected_owner_revisions
            or max(observed_revisions) != latest["owner_revision_after"]
            or any(len(identities) != 1 for identities in observed_revisions.values())
        ):
            raise FailClosedRuntimeError(
                "Profile A owner-state latest state is rolled back, forked, or unresolved"
            )
        if latest["event_kind"] == PROFILE_A_OWNER_STATE_REVOKED:
            raise FailClosedRuntimeError(
                "Profile A owner-state authority is revoked"
            )
        root = latest["provenance_root"]
        if root["provenance_root_identity"] != identity:
            raise FailClosedRuntimeError(
                "Profile A owner-state root is stale or superseded"
            )
        now = datetime.now(timezone.utc)
        if _instant(latest["effective_at"], "owner-state effective time") > now:
            raise FailClosedRuntimeError(
                "Profile A owner-state authority is future-dated"
            )
        if latest["expires_at"] is not None and _instant(
            latest["expires_at"], "owner-state expiry time"
        ) <= now:
            raise FailClosedRuntimeError(
                "Profile A owner-state authority is expired"
            )
        state_commitment = replay_hash(
            {
                "runtime_scope_identity": self.__che_runtime_scope_identity,
                "owner_state_store_root": self.__owner_state_store_root,
                "owner_state_identity": self.__owner_state_identity,
                "latest_event_identity": latest["event_identity"],
                "latest_event_hash": latest["event_hash"],
                "latest_owner_revision": latest["owner_revision_after"],
                "latest_correlation_hash": latest["correlation_hash"],
            }
        )
        return _plain(root), state_commitment


def _create_profile_a_che_replay_resolver_v1(
    *, _authority_process_context: Any
) -> _ProfileACheReplayOwnerStateResolverV1:
    return _ProfileACheReplayOwnerStateResolverV1(
        _authority_process_context=_authority_process_context,
    )


__all__ = [
    "AUTHORITY_PROVENANCE_CONTRACT_VERSION",
    "AUTHORIZATION_OWNER_IDENTITY",
    "BOUNDED_EVIDENCE_REDUCTION_POLICY_AUTHORIZATION",
    "IMMUTABLE_COMMIT_BOUND",
    "OWNER_ISSUED_AUTHORIZATION_ACT_CLASS",
    "PROFILE_A_OWNER_STATE_EVENT_VERSION",
    "PROFILE_A_OWNER_STATE_ISSUED",
    "PROFILE_A_OWNER_STATE_REVOKED",
    "PROFILE_A_OWNER_STATE_SUPERSEDED",
    "TrustedAuthorityProvenanceBindingV1",
    "TrustedAuthorityProvenanceResolverV1",
    "authority_provenance_content_hash_v1",
    "create_authority_provenance_root_v1",
    "validate_profile_a_owner_state_event_v1",
    "validate_authority_provenance_root_v1",
]
