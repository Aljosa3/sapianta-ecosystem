"""Durable Candidate H immutable records and one-winner CAS slots.

Only Stage-2-validated canonical models may cross this write boundary.  The
module provides mechanical persistence and authoritative read-back; it does
not authenticate, sign, select a Human disposition, orchestrate, replay,
execute BEGIN, or mutate a constitutional root.
"""

from __future__ import annotations

import fcntl
import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from tempfile import mkstemp
from types import MappingProxyType

from .cj1 import CJ1Error, cj1_decode, cj1_digest, cj1_encode, sha256_hex
from .models import FrozenCanonicalModel
from .validators import (
    ARTIFACT_IDENTITY_SPECS,
    CandidateValidationError,
    validate_artifact,
)


IMMUTABLE_AFTER_TEMP_FSYNC = "IMMUTABLE_AFTER_TEMP_FSYNC"
IMMUTABLE_AFTER_PUBLISH = "IMMUTABLE_AFTER_PUBLISH"
SLOT_AFTER_GENERATION_FSYNC = "SLOT_AFTER_GENERATION_FSYNC"
SLOT_AFTER_GENERATION_PUBLISH = "SLOT_AFTER_GENERATION_PUBLISH"
SLOT_AFTER_POINTER_FSYNC = "SLOT_AFTER_POINTER_FSYNC"
SLOT_AFTER_POINTER_REPLACE = "SLOT_AFTER_POINTER_REPLACE"

CRASH_POINTS = (
    IMMUTABLE_AFTER_TEMP_FSYNC,
    IMMUTABLE_AFTER_PUBLISH,
    SLOT_AFTER_GENERATION_FSYNC,
    SLOT_AFTER_GENERATION_PUBLISH,
    SLOT_AFTER_POINTER_FSYNC,
    SLOT_AFTER_POINTER_REPLACE,
)

CrashHook = Callable[[str], None]


class CandidatePersistenceError(RuntimeError):
    """Stable fail-closed persistence or read-back failure."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}:{detail}")


class InjectedPersistenceCrash(RuntimeError):
    """Fixture-only process-crash surrogate used at declared write boundaries."""


@dataclass(frozen=True, slots=True)
class ArtifactAddress:
    """Mechanical address of one already validated constitutional artifact."""

    artifact_identity: str
    artifact_digest: str


@dataclass(frozen=True, slots=True)
class ImmutableReadBack:
    """Non-canonical operational view of exact persisted artifact bytes."""

    address: ArtifactAddress
    storage_digest: str
    canonical_bytes: bytes


@dataclass(frozen=True, slots=True)
class ImmutableWriteResult:
    outcome: str
    read_back: ImmutableReadBack


@dataclass(frozen=True, slots=True)
class SlotReadBack:
    """Validated current-pointer view; not a constitutional artifact family."""

    owner: str
    slot_identity: str
    slot_epoch: object
    generation: int
    predecessor_slot_digest: str | None
    predecessor_status: str | None
    current_status: str
    artifact_identity: str
    artifact_digest: str
    artifact_storage_digest: str
    logical_instant: str
    slot_digest: str


@dataclass(frozen=True, slots=True)
class CompareAndSwapResult:
    outcome: str
    read_back: SlotReadBack


@dataclass(frozen=True, slots=True)
class SubcontractAddress:
    """Content address for one closed ResultV2 subcontract body."""

    subcontract_kind: str
    identity: str
    digest: str


@dataclass(frozen=True, slots=True)
class SubcontractReadBack:
    """Exact admitted subcontract bytes read from the shared record store."""

    address: SubcontractAddress
    storage_digest: str
    canonical_bytes: bytes


@dataclass(frozen=True, slots=True)
class SubcontractWriteResult:
    outcome: str
    read_back: SubcontractReadBack


@dataclass(frozen=True, slots=True)
class SubcontractKindSpec:
    mode: str
    prefix: str
    field_names: tuple[str, ...]
    fixed_constants: Mapping[str, object]
    closed_values: Mapping[str, frozenset[object]]
    conditional_null_rule: str | None
    pair_bases: tuple[str, ...]
    pair_domain_rules: Mapping[str, str | None]
    cas_argument_bindings: Mapping[str, str]


CAS_ARGUMENT_NAMES = (
    "owner",
    "slot_identity",
    "slot_epoch",
    "expected_slot_digest",
    "expected_status",
    "successor_status",
    "logical_instant",
)


def _field_names(value: str) -> tuple[str, ...]:
    return tuple(value.split())


def _subcontract_spec(
    *,
    mode: str,
    prefix: str,
    field_names: tuple[str, ...],
    fixed_constants: Mapping[str, object] | None = None,
    closed_values: Mapping[str, frozenset[object]] | None = None,
    conditional_null_rule: str | None = None,
    pair_domain_rules: Mapping[str, str | None] | None = None,
    cas_argument_bindings: Mapping[str, str] | None = None,
) -> SubcontractKindSpec:
    domains = dict(pair_domain_rules or {})
    return SubcontractKindSpec(
        mode=mode,
        prefix=prefix,
        field_names=field_names,
        fixed_constants=MappingProxyType(dict(fixed_constants or {})),
        closed_values=MappingProxyType(dict(closed_values or {})),
        conditional_null_rule=conditional_null_rule,
        pair_bases=tuple(domains),
        pair_domain_rules=MappingProxyType(domains),
        cas_argument_bindings=MappingProxyType(dict(cas_argument_bindings or {})),
    )


_SUBCONTRACT_KIND_SPECS = {
    "AUTHENTICATION_OPERATION_V1": _subcontract_spec(
        mode="IMMUTABLE",
        prefix="human-founder-auth-operation-v1",
        field_names=_field_names("""
            external_premise_identity external_premise_digest
            human_founder_capacity_identity human_founder_capacity_digest
            human_actor_identity human_authentication_slot_identity
            human_authentication_epoch authentication_sequence
            authentication_commitment_identity authentication_commitment_digest
            authenticated_message_representation authenticated_message_digest
            signature_scheme signature_key_identity
            predecessor_authentication_slot_status
        """),
        fixed_constants={
            "authentication_sequence": 1,
            "authenticated_message_representation": "EXACT_UTF8_CJ1_P_AUTH_V2_BYTES",
            "signature_scheme": "ED25519_RFC8032_PURE",
            "predecessor_authentication_slot_status": "OPEN",
        },
        pair_domain_rules={
            "external_premise": None,
            "human_founder_capacity": "human-founder-external-capacity-v2",
            "authentication_commitment": "human-founder-auth-commitment-v2-sha256",
        },
    ),
    "AUTHENTICATION_CLAIM_CAS_V1": _subcontract_spec(
        mode="CAS",
        prefix="human-founder-auth-claim-cas-v1",
        field_names=_field_names("""
            authentication_operation_identity authentication_operation_digest
            human_authentication_slot_identity human_authentication_epoch
            authentication_sequence human_founder_capacity_identity
            human_founder_capacity_digest predecessor_authentication_slot_status
            claimed_authentication_slot_status one_use_claim_token_identity
            one_use_claim_token_digest claim_logical_instant producing_owner
            predecessor_authentication_slot_digest
        """),
        fixed_constants={
            "authentication_sequence": 1,
            "predecessor_authentication_slot_status": "OPEN",
            "claimed_authentication_slot_status": "AUTHENTICATING",
        },
        pair_domain_rules={
            "authentication_operation": "human-founder-auth-operation-v1",
            "human_founder_capacity": "human-founder-external-capacity-v2",
            "one_use_claim_token": None,
        },
        cas_argument_bindings={
            "owner": "producing_owner",
            "slot_identity": "human_authentication_slot_identity",
            "slot_epoch": "human_authentication_epoch",
            "expected_slot_digest": "predecessor_authentication_slot_digest",
            "expected_status": "predecessor_authentication_slot_status",
            "successor_status": "claimed_authentication_slot_status",
            "logical_instant": "claim_logical_instant",
        },
    ),
    "SIGNER_INVOCATION_INTENT_V1": _subcontract_spec(
        mode="IMMUTABLE",
        prefix="human-founder-signer-intent-v1",
        field_names=_field_names("""
            external_premise_identity external_premise_digest
            human_founder_capacity_identity human_founder_capacity_digest
            human_actor_identity authentication_operation_identity
            authentication_operation_digest authentication_claim_cas_identity
            authentication_claim_cas_digest authentication_commitment_identity
            authentication_commitment_digest authenticated_message_representation
            authenticated_message_digest signature_scheme signature_key_identity
            signer_operation_slot_identity signer_operation_slot_epoch
            authentication_sequence maximum_logical_signer_invocations
        """),
        fixed_constants={
            "authenticated_message_representation": "EXACT_UTF8_CJ1_P_AUTH_V2_BYTES",
            "signature_scheme": "ED25519_RFC8032_PURE",
            "authentication_sequence": 1,
            "maximum_logical_signer_invocations": 1,
        },
        pair_domain_rules={
            "external_premise": None,
            "human_founder_capacity": "human-founder-external-capacity-v2",
            "authentication_operation": "human-founder-auth-operation-v1",
            "authentication_claim_cas": "human-founder-auth-claim-cas-v1",
            "authentication_commitment": "human-founder-auth-commitment-v2-sha256",
        },
    ),
    "SIGNER_ACCEPTANCE_CAS_V1": _subcontract_spec(
        mode="CAS",
        prefix="human-founder-signer-acceptance-cas-v1",
        field_names=_field_names("""
            signer_invocation_intent_identity signer_invocation_intent_digest
            authentication_operation_identity authentication_operation_digest
            authentication_claim_cas_identity authentication_claim_cas_digest
            human_founder_capacity_identity human_founder_capacity_digest
            authenticated_message_representation authenticated_message_digest
            signature_scheme signature_key_identity signer_operation_slot_identity
            signer_operation_slot_epoch predecessor_signer_slot_status
            accepted_signer_slot_status invocation_sequence
            maximum_logical_signer_invocations acceptance_logical_instant
            producing_owner predecessor_signer_slot_digest
        """),
        fixed_constants={
            "authenticated_message_representation": "EXACT_UTF8_CJ1_P_AUTH_V2_BYTES",
            "signature_scheme": "ED25519_RFC8032_PURE",
            "predecessor_signer_slot_status": "AVAILABLE",
            "accepted_signer_slot_status": "ACCEPTED_IN_PROGRESS",
            "invocation_sequence": 1,
            "maximum_logical_signer_invocations": 1,
        },
        pair_domain_rules={
            "signer_invocation_intent": "human-founder-signer-intent-v1",
            "authentication_operation": "human-founder-auth-operation-v1",
            "authentication_claim_cas": "human-founder-auth-claim-cas-v1",
            "human_founder_capacity": "human-founder-external-capacity-v2",
        },
        cas_argument_bindings={
            "owner": "producing_owner",
            "slot_identity": "signer_operation_slot_identity",
            "slot_epoch": "signer_operation_slot_epoch",
            "expected_slot_digest": "predecessor_signer_slot_digest",
            "expected_status": "predecessor_signer_slot_status",
            "successor_status": "accepted_signer_slot_status",
            "logical_instant": "acceptance_logical_instant",
        },
    ),
    "SIGNER_INVOCATION_RECEIPT_V1": _subcontract_spec(
        mode="IMMUTABLE",
        prefix="human-founder-signer-invocation-receipt-v1",
        field_names=_field_names("""
            signer_acceptance_cas_identity signer_acceptance_cas_digest
            signer_invocation_intent_identity signer_invocation_intent_digest
            authentication_operation_identity authentication_operation_digest
            authentication_claim_cas_identity authentication_claim_cas_digest
            signer_operation_slot_identity signer_operation_slot_epoch
            invocation_sequence signer_operation_status
            acceptance_logical_instant accepted_slot_digest
        """),
        fixed_constants={
            "invocation_sequence": 1,
            "signer_operation_status": "ACCEPTED_IN_PROGRESS",
        },
        pair_domain_rules={
            "signer_acceptance_cas": "human-founder-signer-acceptance-cas-v1",
            "signer_invocation_intent": "human-founder-signer-intent-v1",
            "authentication_operation": "human-founder-auth-operation-v1",
            "authentication_claim_cas": "human-founder-auth-claim-cas-v1",
        },
    ),
    "SIGNER_OUTCOME_V1": _subcontract_spec(
        mode="CAS",
        prefix="human-founder-signer-outcome-v1",
        field_names=_field_names("""
            signer_invocation_intent_identity signer_invocation_intent_digest
            signer_acceptance_cas_identity signer_acceptance_cas_digest
            signer_invocation_receipt_identity signer_invocation_receipt_digest
            authentication_operation_identity authentication_operation_digest
            authentication_claim_cas_identity authentication_claim_cas_digest
            human_founder_capacity_identity human_founder_capacity_digest
            authentication_commitment_identity authentication_commitment_digest
            authenticated_message_representation authenticated_message_digest
            signature_scheme signature_key_identity outcome_status signature
            signature_digest verification_result failure_code
            completion_logical_instant terminal producing_owner
            signer_operation_slot_identity signer_operation_slot_epoch
            predecessor_signer_slot_digest predecessor_signer_slot_status
        """),
        fixed_constants={
            "authenticated_message_representation": "EXACT_UTF8_CJ1_P_AUTH_V2_BYTES",
            "signature_scheme": "ED25519_RFC8032_PURE",
            "predecessor_signer_slot_status": "ACCEPTED_IN_PROGRESS",
            "terminal": True,
        },
        closed_values={
            "outcome_status": frozenset(
                {"VALID_SIGNATURE_FINAL", "REJECTED_FINAL", "INDETERMINATE_FINAL"}
            ),
            "verification_result": frozenset({"TRUE", "FALSE", "NOT_APPLICABLE"}),
        },
        conditional_null_rule="SIGNER_OUTCOME",
        pair_domain_rules={
            "signer_invocation_intent": "human-founder-signer-intent-v1",
            "signer_acceptance_cas": "human-founder-signer-acceptance-cas-v1",
            "signer_invocation_receipt": "human-founder-signer-invocation-receipt-v1",
            "authentication_operation": "human-founder-auth-operation-v1",
            "authentication_claim_cas": "human-founder-auth-claim-cas-v1",
            "human_founder_capacity": "human-founder-external-capacity-v2",
            "authentication_commitment": "human-founder-auth-commitment-v2-sha256",
        },
        cas_argument_bindings={
            "owner": "producing_owner",
            "slot_identity": "signer_operation_slot_identity",
            "slot_epoch": "signer_operation_slot_epoch",
            "expected_slot_digest": "predecessor_signer_slot_digest",
            "expected_status": "predecessor_signer_slot_status",
            "successor_status": "outcome_status",
            "logical_instant": "completion_logical_instant",
        },
    ),
    "SIGNER_OUTCOME_READ_BACK_V1": _subcontract_spec(
        mode="IMMUTABLE",
        prefix="human-founder-signer-outcome-readback-v1",
        field_names=_field_names("""
            signer_outcome_identity signer_outcome_digest
            signer_invocation_receipt_identity signer_invocation_receipt_digest
            signer_operation_slot_identity signer_operation_slot_epoch
            invocation_sequence signer_outcome_status signature_digest
            completion_logical_instant terminal_signer_slot_digest
        """),
        fixed_constants={"invocation_sequence": 1},
        closed_values={
            "signer_outcome_status": frozenset(
                {"VALID_SIGNATURE_FINAL", "REJECTED_FINAL", "INDETERMINATE_FINAL"}
            )
        },
        conditional_null_rule="SIGNER_OUTCOME_READ_BACK",
        pair_domain_rules={
            "signer_outcome": "human-founder-signer-outcome-v1",
            "signer_invocation_receipt": "human-founder-signer-invocation-receipt-v1",
        },
    ),
    "AUTHENTICATION_TERMINAL_CAS_V1": _subcontract_spec(
        mode="CAS",
        prefix="human-founder-auth-terminal-cas-v1",
        field_names=_field_names("""
            authentication_operation_identity authentication_operation_digest
            authentication_claim_cas_identity authentication_claim_cas_digest
            signer_outcome_read_back_identity signer_outcome_read_back_digest
            predecessor_authentication_slot_status terminal_authentication_slot_status
            authentication_result signature signature_verification_result
            one_use_non_equivocation_proof_identity
            one_use_non_equivocation_proof_digest conflict_status
            capacity_permanently_exhausted completion_logical_instant
            producing_owner human_authentication_slot_identity
            human_authentication_epoch predecessor_authentication_slot_digest
        """),
        fixed_constants={
            "predecessor_authentication_slot_status": "AUTHENTICATING",
            "capacity_permanently_exhausted": True,
        },
        closed_values={
            "terminal_authentication_slot_status": frozenset(
                {"AUTHENTICATED_FINAL", "INDETERMINATE_EXHAUSTED"}
            ),
            "authentication_result": frozenset(
                {
                    "AUTHENTICATED_VALID",
                    "AUTHENTICATION_REJECTED_FINAL",
                    "INDETERMINATE_NO_VALID_RESULT",
                }
            ),
            "signature_verification_result": frozenset(
                {"TRUE", "FALSE", "NOT_APPLICABLE"}
            ),
            "conflict_status": frozenset({"NONE", "RESULT_UNRECOVERABLE_NO_RETRY"}),
        },
        conditional_null_rule="AUTHENTICATION_TERMINAL",
        pair_domain_rules={
            "authentication_operation": "human-founder-auth-operation-v1",
            "authentication_claim_cas": "human-founder-auth-claim-cas-v1",
            "signer_outcome_read_back": "human-founder-signer-outcome-readback-v1",
            "one_use_non_equivocation_proof": None,
        },
        cas_argument_bindings={
            "owner": "producing_owner",
            "slot_identity": "human_authentication_slot_identity",
            "slot_epoch": "human_authentication_epoch",
            "expected_slot_digest": "predecessor_authentication_slot_digest",
            "expected_status": "predecessor_authentication_slot_status",
            "successor_status": "terminal_authentication_slot_status",
            "logical_instant": "completion_logical_instant",
        },
    ),
    "AUTHENTICATION_AUTHORITATIVE_READ_BACK_V1": _subcontract_spec(
        mode="IMMUTABLE",
        prefix="human-founder-auth-readback-v1",
        field_names=_field_names("""
            authentication_terminal_cas_identity authentication_terminal_cas_digest
            human_authentication_slot_identity human_authentication_epoch
            authentication_sequence human_founder_capacity_identity
            human_founder_capacity_digest authentication_operation_identity
            authentication_operation_digest terminal_authentication_slot_status
            authentication_result signature_digest completion_logical_instant
            read_back_authentication_slot_digest
        """),
        fixed_constants={"authentication_sequence": 1},
        closed_values={
            "terminal_authentication_slot_status": frozenset(
                {"AUTHENTICATED_FINAL", "INDETERMINATE_EXHAUSTED"}
            ),
            "authentication_result": frozenset(
                {
                    "AUTHENTICATED_VALID",
                    "AUTHENTICATION_REJECTED_FINAL",
                    "INDETERMINATE_NO_VALID_RESULT",
                }
            ),
        },
        conditional_null_rule="AUTHENTICATION_READ_BACK",
        pair_domain_rules={
            "authentication_terminal_cas": "human-founder-auth-terminal-cas-v1",
            "human_founder_capacity": "human-founder-external-capacity-v2",
            "authentication_operation": "human-founder-auth-operation-v1",
        },
    ),
}

SUBCONTRACT_KIND_SPECS: Mapping[str, SubcontractKindSpec] = MappingProxyType(
    _SUBCONTRACT_KIND_SPECS
)


def _validate_subcontract_specs() -> None:
    if len(SUBCONTRACT_KIND_SPECS) != 9:
        raise RuntimeError("closed subcontract specification must contain nine kinds")
    modes = [spec.mode for spec in SUBCONTRACT_KIND_SPECS.values()]
    if modes.count("CAS") != 4 or modes.count("IMMUTABLE") != 5:
        raise RuntimeError("closed subcontract mode cardinality mismatch")
    for kind, spec in SUBCONTRACT_KIND_SPECS.items():
        if not isinstance(kind, str) or not kind or spec.mode not in {"CAS", "IMMUTABLE"}:
            raise RuntimeError("invalid subcontract kind specification")
        if not spec.prefix or len(spec.field_names) != len(set(spec.field_names)):
            raise RuntimeError(f"invalid subcontract field declaration: {kind}")
        field_set = set(spec.field_names)
        if any(not isinstance(name, str) or not name for name in spec.field_names):
            raise RuntimeError(f"invalid subcontract field name: {kind}")
        if not set(spec.fixed_constants).issubset(field_set):
            raise RuntimeError(f"unknown fixed-constant field: {kind}")
        if not set(spec.closed_values).issubset(field_set):
            raise RuntimeError(f"unknown closed-value field: {kind}")
        if set(spec.pair_bases) != set(spec.pair_domain_rules):
            raise RuntimeError(f"pair-domain declaration mismatch: {kind}")
        for base in spec.pair_bases:
            if f"{base}_identity" not in field_set or f"{base}_digest" not in field_set:
                raise RuntimeError(f"unknown pair field: {kind}:{base}")
        bindings = spec.cas_argument_bindings
        if spec.mode == "CAS":
            if tuple(bindings) != CAS_ARGUMENT_NAMES:
                raise RuntimeError(f"incomplete CAS binding keys: {kind}")
            targets = tuple(bindings.values())
            if len(targets) != len(set(targets)):
                raise RuntimeError(f"aliased CAS binding targets: {kind}")
            if any(
                not isinstance(target, str) or not target or target not in field_set
                for target in targets
            ):
                raise RuntimeError(f"unknown CAS binding target: {kind}")
        elif bindings:
            raise RuntimeError(f"immutable kind has CAS bindings: {kind}")


_validate_subcontract_specs()


def _fail(code: str, detail: str) -> None:
    raise CandidatePersistenceError(code, detail)


def _require_text(value: object, detail: str) -> str:
    if not isinstance(value, str) or not value:
        _fail("INVALID_PERSISTENCE_INPUT", detail)
    try:
        cj1_encode(value)
    except CJ1Error as exc:
        _fail("INVALID_PERSISTENCE_INPUT", f"{detail}:{exc}")
    return value


def _is_lower_hex(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _require_sha256(value: object, detail: str, *, code: str) -> str:
    if (
        not isinstance(value, str)
        or not value.startswith("sha256:")
        or not _is_lower_hex(value[7:])
    ):
        _fail(code, detail)
    return value


def _subcontract_spec_for_address(address: object) -> SubcontractKindSpec:
    if not isinstance(address, SubcontractAddress):
        _fail("INVALID_SUBCONTRACT_INPUT", "address")
    if not all(
        isinstance(value, str) and value
        for value in (address.subcontract_kind, address.identity, address.digest)
    ):
        _fail("INVALID_SUBCONTRACT_INPUT", "address fields")
    spec = SUBCONTRACT_KIND_SPECS.get(address.subcontract_kind)
    if spec is None:
        _fail("UNKNOWN_SUBCONTRACT_KIND", address.subcontract_kind)
    return spec


def _validate_subcontract_pair(
    body: Mapping[str, object],
    base: str,
    expected_prefix: str | None,
) -> None:
    identity = body[f"{base}_identity"]
    digest = body[f"{base}_digest"]
    if (identity is None) != (digest is None) or identity is None:
        _fail("SUBCONTRACT_SEMANTIC_ADMISSION_FAILED", f"pair:{base}")
    if not isinstance(identity, str) or identity.count(":") != 1:
        _fail("SUBCONTRACT_SEMANTIC_ADMISSION_FAILED", f"pair:{base}")
    domain, identity_hex = identity.split(":", 1)
    if not domain or not _is_lower_hex(identity_hex):
        _fail("SUBCONTRACT_SEMANTIC_ADMISSION_FAILED", f"pair:{base}")
    if not isinstance(digest, str) or digest != f"sha256:{identity_hex}":
        _fail("SUBCONTRACT_SEMANTIC_ADMISSION_FAILED", f"pair:{base}")
    if expected_prefix is not None and domain != expected_prefix:
        _fail("SUBCONTRACT_SEMANTIC_ADMISSION_FAILED", f"pair_domain:{base}")


def _validate_conditional_nulls(
    body: Mapping[str, object],
    rule: str | None,
) -> None:
    if rule is None:
        return
    if rule == "SIGNER_OUTCOME":
        status = body["outcome_status"]
        expected = {
            "VALID_SIGNATURE_FINAL": (True, "TRUE", None),
            "REJECTED_FINAL": (False, "FALSE", "SIGNER_INPUT_OR_SIGNATURE_INVALID"),
            "INDETERMINATE_FINAL": (
                False,
                "NOT_APPLICABLE",
                "ACCEPTED_OPERATION_RECONSTRUCTION_UNAVAILABLE",
            ),
        }[status]
        has_signature = body["signature"] is not None and body["signature_digest"] is not None
        if (
            has_signature != expected[0]
            or (body["signature"] is None) != (body["signature_digest"] is None)
            or body["verification_result"] != expected[1]
            or body["failure_code"] != expected[2]
        ):
            _fail("SUBCONTRACT_SEMANTIC_ADMISSION_FAILED", "conditional_null:signature")
        return
    if rule == "SIGNER_OUTCOME_READ_BACK":
        requires_digest = body["signer_outcome_status"] == "VALID_SIGNATURE_FINAL"
        if requires_digest != (body["signature_digest"] is not None):
            _fail("SUBCONTRACT_SEMANTIC_ADMISSION_FAILED", "conditional_null:signature_digest")
        return
    if rule == "AUTHENTICATION_TERMINAL":
        result = body["authentication_result"]
        expected = {
            "AUTHENTICATED_VALID": (
                "AUTHENTICATED_FINAL",
                True,
                "TRUE",
                "NONE",
            ),
            "AUTHENTICATION_REJECTED_FINAL": (
                "INDETERMINATE_EXHAUSTED",
                False,
                "FALSE",
                "RESULT_UNRECOVERABLE_NO_RETRY",
            ),
            "INDETERMINATE_NO_VALID_RESULT": (
                "INDETERMINATE_EXHAUSTED",
                False,
                "NOT_APPLICABLE",
                "RESULT_UNRECOVERABLE_NO_RETRY",
            ),
        }[result]
        if (
            body["terminal_authentication_slot_status"] != expected[0]
            or (body["signature"] is not None) != expected[1]
            or body["signature_verification_result"] != expected[2]
            or body["conflict_status"] != expected[3]
        ):
            _fail("SUBCONTRACT_SEMANTIC_ADMISSION_FAILED", "conditional_null:signature")
        return
    if rule == "AUTHENTICATION_READ_BACK":
        result = body["authentication_result"]
        expected_status = (
            "AUTHENTICATED_FINAL"
            if result == "AUTHENTICATED_VALID"
            else "INDETERMINATE_EXHAUSTED"
        )
        requires_digest = result == "AUTHENTICATED_VALID"
        if (
            body["terminal_authentication_slot_status"] != expected_status
            or (body["signature_digest"] is not None) != requires_digest
        ):
            _fail("SUBCONTRACT_SEMANTIC_ADMISSION_FAILED", "conditional_null:signature_digest")
        return
    raise RuntimeError(f"unsupported subcontract conditional-null rule: {rule}")


def _validate_subcontract_admission(
    *,
    address: object,
    canonical_bytes: object,
    expected_mode: str,
    cas_arguments: Mapping[str, object] | None = None,
) -> dict[str, object]:
    spec = _subcontract_spec_for_address(address)
    if not isinstance(canonical_bytes, bytes):
        _fail("INVALID_SUBCONTRACT_INPUT", "canonical_bytes")
    try:
        decoded = cj1_decode(canonical_bytes)
    except CJ1Error as exc:
        _fail("INVALID_SUBCONTRACT_INPUT", f"canonical_bytes:{exc}")
    if not isinstance(decoded, dict):
        _fail("INVALID_SUBCONTRACT_INPUT", "body root")
    if cj1_encode(decoded) != canonical_bytes:
        _fail("INVALID_SUBCONTRACT_INPUT", "noncanonical CJ1")
    if spec.mode != expected_mode:
        _fail("SUBCONTRACT_MODE_MISMATCH", address.subcontract_kind)
    digest_hex = sha256_hex(canonical_bytes)
    if (
        address.identity != f"{spec.prefix}:{digest_hex}"
        or address.digest != f"sha256:{digest_hex}"
    ):
        _fail("SUBCONTRACT_ADDRESS_MISMATCH", address.subcontract_kind)
    declared_field_names = spec.field_names
    if (
        not isinstance(declared_field_names, tuple)
        or len(declared_field_names) != len(set(declared_field_names))
        or any(not isinstance(name, str) or not name for name in declared_field_names)
    ):
        _fail("SUBCONTRACT_SEMANTIC_ADMISSION_FAILED", "field_set:invalid_spec")
    if tuple(decoded.keys()) != tuple(sorted(declared_field_names)):
        _fail("SUBCONTRACT_SEMANTIC_ADMISSION_FAILED", "field_set")
    for name, expected in spec.fixed_constants.items():
        if decoded[name] != expected:
            _fail("SUBCONTRACT_SEMANTIC_ADMISSION_FAILED", f"constant:{name}")
    for name, allowed in spec.closed_values.items():
        if decoded[name] not in allowed:
            _fail("SUBCONTRACT_SEMANTIC_ADMISSION_FAILED", f"closed_value:{name}")
    _validate_conditional_nulls(decoded, spec.conditional_null_rule)
    for base in spec.pair_bases:
        _validate_subcontract_pair(decoded, base, spec.pair_domain_rules[base])
    pair_digest_fields = {f"{base}_digest" for base in spec.pair_bases}
    for name, value in decoded.items():
        if name.endswith("_digest") and name not in pair_digest_fields and value is not None:
            _require_sha256(
                value,
                name,
                code="SUBCONTRACT_SEMANTIC_ADMISSION_FAILED",
            )
        if name in {
            "producing_owner",
            "human_actor_identity",
            "human_authentication_slot_identity",
            "signer_operation_slot_identity",
            "signature_key_identity",
            "claim_logical_instant",
            "acceptance_logical_instant",
            "completion_logical_instant",
        } and (not isinstance(value, str) or not value):
            _fail("SUBCONTRACT_SEMANTIC_ADMISSION_FAILED", f"constant:{name}")
    if spec.mode == "CAS":
        if cas_arguments is None or tuple(cas_arguments) != CAS_ARGUMENT_NAMES:
            _fail("SUBCONTRACT_SEMANTIC_ADMISSION_FAILED", "cas_binding:invalid_arguments")
        if tuple(spec.cas_argument_bindings) != CAS_ARGUMENT_NAMES:
            _fail("SUBCONTRACT_SEMANTIC_ADMISSION_FAILED", "cas_binding:invalid_spec")
        targets = tuple(spec.cas_argument_bindings.values())
        if len(targets) != len(set(targets)) or any(
            target not in spec.field_names for target in targets
        ):
            _fail("SUBCONTRACT_SEMANTIC_ADMISSION_FAILED", "cas_binding:invalid_spec")
        for argument in CAS_ARGUMENT_NAMES:
            if cas_arguments[argument] != decoded[spec.cas_argument_bindings[argument]]:
                _fail(
                    "SUBCONTRACT_SEMANTIC_ADMISSION_FAILED",
                    f"cas_binding:{argument}",
                )
    return decoded


def _write_all(fd: int, data: bytes) -> None:
    view = memoryview(data)
    written = 0
    while written < len(view):
        count = os.write(fd, view[written:])
        if count <= 0:
            _fail("DURABLE_WRITE_FAILED", "zero-byte write")
        written += count


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


class CandidateHReadOnlyStore:
    """Capability-limited read interface with no write or CAS methods."""

    __slots__ = ("_store",)

    def __init__(self, store: "CandidateHStore") -> None:
        self._store = store

    def read_immutable(
        self,
        model_type: type[FrozenCanonicalModel],
        address: ArtifactAddress,
        *,
        owner_bindings: Mapping[str, str] | None = None,
    ) -> tuple[FrozenCanonicalModel, ImmutableReadBack]:
        return self._store.read_immutable(
            model_type, address, owner_bindings=owner_bindings
        )

    def read_slot(self, owner: str, slot_identity: str, slot_epoch: object) -> SlotReadBack:
        return self._store.read_slot(owner, slot_identity, slot_epoch)

    def read_subcontract(
        self,
        address: SubcontractAddress,
    ) -> SubcontractReadBack:
        return self._store.read_subcontract(address)

    def read_slot_generation(
        self,
        owner: str,
        slot_identity: str,
        slot_epoch: object,
        generation: int,
        slot_digest: str,
    ) -> SlotReadBack:
        return self._store.read_slot_generation(
            owner,
            slot_identity,
            slot_epoch,
            generation,
            slot_digest,
        )


class CandidateHStore:
    """Filesystem-backed immutable record store with serialized CAS slots."""

    def __init__(self, root: str | os.PathLike[str]) -> None:
        self._root = Path(root)
        self._records = self._root / "records"
        self._slots = self._root / "slots"
        self._generations = self._root / "slot-generations"
        self._locks = self._root / "locks"
        for path in (self._root, self._records, self._slots, self._generations, self._locks):
            path.mkdir(mode=0o700, parents=True, exist_ok=True)
            if path.is_symlink() or not path.is_dir():
                _fail("UNSAFE_STORE_PATH", str(path))

    def readonly(self) -> CandidateHReadOnlyStore:
        return CandidateHReadOnlyStore(self)

    @staticmethod
    def _key(*parts: object) -> str:
        return sha256_hex(cj1_encode(list(parts)))

    def _record_path(self, artifact_identity: str) -> Path:
        return self._records / f"{self._key(artifact_identity)}.cj1"

    def _slot_key(self, owner: str, slot_identity: str, slot_epoch: object) -> str:
        return self._key(owner, slot_identity, slot_epoch)

    def _pointer_path(self, slot_key: str) -> Path:
        return self._slots / f"{slot_key}.current.cj1"

    def _generation_path(self, slot_key: str, generation: int, slot_digest: str) -> Path:
        digest_hex = slot_digest.removeprefix("sha256:")
        return self._generations / f"{slot_key}.{generation}.{digest_hex}.cj1"

    @staticmethod
    def _invoke(hook: CrashHook | None, point: str) -> None:
        if hook is not None:
            hook(point)

    @staticmethod
    def _artifact_address(
        model: FrozenCanonicalModel,
        artifact_identity: str | None,
        artifact_digest: str | None,
    ) -> ArtifactAddress:
        spec = ARTIFACT_IDENTITY_SPECS.get(type(model))
        if spec is not None:
            expected_identity = getattr(model, spec.identity_field)
            expected_digest = getattr(model, spec.digest_field)
            if artifact_identity is not None and artifact_identity != expected_identity:
                _fail("ARTIFACT_ADDRESS_MISMATCH", "identity")
            if artifact_digest is not None and artifact_digest != expected_digest:
                _fail("ARTIFACT_ADDRESS_MISMATCH", "digest")
            artifact_identity = expected_identity
            artifact_digest = expected_digest
        else:
            if artifact_identity is None or artifact_digest is None:
                _fail("ARTIFACT_ADDRESS_REQUIRED", type(model).__name__)
            expected_digest = cj1_digest(model.to_cj1_object())
            if artifact_digest != expected_digest:
                _fail("ARTIFACT_ADDRESS_MISMATCH", "digest")
            identity_parts = artifact_identity.rsplit(":", 1)
            if len(identity_parts) != 2 or not identity_parts[0] or identity_parts[1] != expected_digest[7:]:
                _fail("ARTIFACT_ADDRESS_MISMATCH", "content identity")
        identity = _require_text(artifact_identity, "artifact_identity")
        digest = _require_text(artifact_digest, "artifact_digest")
        if not digest.startswith("sha256:") or len(digest) != 71:
            _fail("ARTIFACT_ADDRESS_MISMATCH", "digest format")
        return ArtifactAddress(identity, digest)

    def _publish_immutable_bytes(
        self,
        path: Path,
        data: bytes,
        *,
        hook: CrashHook | None,
        fsync_point: str,
        publish_point: str,
    ) -> str:
        if path.exists():
            existing = self._read_exact(path, "CORRUPT_IMMUTABLE_RECORD")
            if existing != data:
                _fail("IMMUTABLE_RECORD_CONFLICT", path.name)
            return "IDEMPOTENT"
        fd, temporary_name = mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
        temporary = Path(temporary_name)
        published = False
        try:
            _write_all(fd, data)
            os.fsync(fd)
            self._invoke(hook, fsync_point)
        finally:
            os.close(fd)
        try:
            os.link(temporary, path)
            published = True
            self._invoke(hook, publish_point)
            _fsync_directory(path.parent)
        except FileExistsError:
            existing = self._read_exact(path, "CORRUPT_IMMUTABLE_RECORD")
            if existing != data:
                _fail("IMMUTABLE_RECORD_CONFLICT", path.name)
        finally:
            if temporary.exists() and (published or path.exists()):
                temporary.unlink()
        return "CREATED" if published else "IDEMPOTENT"

    @staticmethod
    def _read_exact(path: Path, corruption_code: str) -> bytes:
        try:
            data = path.read_bytes()
        except FileNotFoundError:
            raise
        try:
            value = cj1_decode(data)
        except CJ1Error as exc:
            _fail(corruption_code, f"{path.name}:{exc}")
        if cj1_encode(value) != data:
            _fail(corruption_code, path.name)
        return data

    def write_immutable(
        self,
        model: FrozenCanonicalModel,
        *,
        artifact_identity: str | None = None,
        artifact_digest: str | None = None,
        owner_bindings: Mapping[str, str] | None = None,
        _fixture_crash_hook: CrashHook | None = None,
    ) -> ImmutableWriteResult:
        validate_artifact(model, owner_bindings=owner_bindings)
        address = self._artifact_address(model, artifact_identity, artifact_digest)
        canonical_bytes = model.to_cj1_bytes()
        outcome = self._publish_immutable_bytes(
            self._record_path(address.artifact_identity),
            canonical_bytes,
            hook=_fixture_crash_hook,
            fsync_point=IMMUTABLE_AFTER_TEMP_FSYNC,
            publish_point=IMMUTABLE_AFTER_PUBLISH,
        )
        _, read_back = self.read_immutable(
            type(model), address, owner_bindings=owner_bindings
        )
        if read_back.canonical_bytes != canonical_bytes:
            _fail("WRITE_READ_BACK_MISMATCH", address.artifact_identity)
        return ImmutableWriteResult(outcome, read_back)

    def read_immutable(
        self,
        model_type: type[FrozenCanonicalModel],
        address: ArtifactAddress,
        *,
        owner_bindings: Mapping[str, str] | None = None,
    ) -> tuple[FrozenCanonicalModel, ImmutableReadBack]:
        if not isinstance(model_type, type) or not issubclass(model_type, FrozenCanonicalModel):
            _fail("UNKNOWN_SCHEMA_VERSION", getattr(model_type, "__name__", repr(model_type)))
        identity = _require_text(address.artifact_identity, "artifact_identity")
        try:
            canonical_bytes = self._read_exact(
                self._record_path(identity), "CORRUPT_IMMUTABLE_RECORD"
            )
        except FileNotFoundError:
            _fail("MISSING_IMMUTABLE_RECORD", identity)
        try:
            value = cj1_decode(canonical_bytes)
            if not isinstance(value, dict):
                _fail("CORRUPT_IMMUTABLE_RECORD", identity)
            model = model_type(**value)
            validate_artifact(model, owner_bindings=owner_bindings)
        except (CJ1Error, CandidateValidationError, TypeError, ValueError) as exc:
            if isinstance(exc, CandidatePersistenceError):
                raise
            _fail("CORRUPT_IMMUTABLE_RECORD", f"{identity}:{exc}")
        actual_address = self._artifact_address(
            model, address.artifact_identity, address.artifact_digest
        )
        storage_digest = cj1_digest(value)
        return model, ImmutableReadBack(actual_address, storage_digest, canonical_bytes)

    def write_subcontract(
        self,
        address: SubcontractAddress,
        canonical_bytes: bytes,
        *,
        _fixture_crash_hook: CrashHook | None = None,
    ) -> SubcontractWriteResult:
        _validate_subcontract_admission(
            address=address,
            canonical_bytes=canonical_bytes,
            expected_mode="IMMUTABLE",
        )
        outcome = self._publish_immutable_bytes(
            self._record_path(address.identity),
            canonical_bytes,
            hook=_fixture_crash_hook,
            fsync_point=IMMUTABLE_AFTER_TEMP_FSYNC,
            publish_point=IMMUTABLE_AFTER_PUBLISH,
        )
        read_back = self.read_subcontract(address)
        if read_back.canonical_bytes != canonical_bytes:
            _fail("WRITE_READ_BACK_MISMATCH", address.identity)
        return SubcontractWriteResult(outcome, read_back)

    def read_subcontract(
        self,
        address: SubcontractAddress,
    ) -> SubcontractReadBack:
        spec = _subcontract_spec_for_address(address)
        identity = address.identity
        try:
            canonical_bytes = self._read_exact(
                self._record_path(identity), "CORRUPT_IMMUTABLE_RECORD"
            )
        except FileNotFoundError:
            _fail("MISSING_IMMUTABLE_RECORD", identity)
        body = cj1_decode(canonical_bytes)
        _validate_subcontract_admission(
            address=address,
            canonical_bytes=canonical_bytes,
            expected_mode=spec.mode,
            cas_arguments=(
                {
                    argument: body[spec.cas_argument_bindings[argument]]
                    for argument in CAS_ARGUMENT_NAMES
                }
                if spec.mode == "CAS" and isinstance(body, dict)
                else None
            ),
        )
        return SubcontractReadBack(
            address=address,
            storage_digest=address.digest,
            canonical_bytes=canonical_bytes,
        )

    @staticmethod
    def _slot_payload(
        *,
        owner: str,
        slot_identity: str,
        slot_epoch: object,
        generation: int,
        predecessor_slot_digest: str | None,
        predecessor_status: str | None,
        current_status: str,
        address: ArtifactAddress,
        artifact_storage_digest: str,
        logical_instant: str,
    ) -> dict[str, object]:
        return {
            "owner": owner,
            "slot_identity": slot_identity,
            "slot_epoch": slot_epoch,
            "generation": generation,
            "predecessor_slot_digest": predecessor_slot_digest,
            "predecessor_status": predecessor_status,
            "current_status": current_status,
            "artifact_identity": address.artifact_identity,
            "artifact_digest": address.artifact_digest,
            "artifact_storage_digest": artifact_storage_digest,
            "logical_instant": logical_instant,
        }

    @staticmethod
    def _slot_from_payload(payload: object, expected_digest: str) -> SlotReadBack:
        if not isinstance(payload, dict):
            _fail("CORRUPT_SLOT", "generation is not an object")
        expected_fields = (
            "artifact_digest",
            "artifact_identity",
            "artifact_storage_digest",
            "current_status",
            "generation",
            "logical_instant",
            "owner",
            "predecessor_slot_digest",
            "predecessor_status",
            "slot_epoch",
            "slot_identity",
        )
        if tuple(sorted(payload)) != expected_fields:
            _fail("CORRUPT_SLOT", "generation schema")
        if cj1_digest(payload) != expected_digest:
            _fail("CORRUPT_SLOT", "generation digest")
        if not isinstance(payload["generation"], int) or isinstance(payload["generation"], bool) or payload["generation"] < 1:
            _fail("CORRUPT_SLOT", "generation number")
        for name in (
            "owner", "slot_identity", "current_status", "artifact_identity",
            "artifact_digest", "artifact_storage_digest", "logical_instant",
        ):
            _require_text(payload[name], name)
        for name in ("predecessor_slot_digest", "predecessor_status"):
            if payload[name] is not None:
                _require_text(payload[name], name)
        return SlotReadBack(
            owner=payload["owner"],
            slot_identity=payload["slot_identity"],
            slot_epoch=payload["slot_epoch"],
            generation=payload["generation"],
            predecessor_slot_digest=payload["predecessor_slot_digest"],
            predecessor_status=payload["predecessor_status"],
            current_status=payload["current_status"],
            artifact_identity=payload["artifact_identity"],
            artifact_digest=payload["artifact_digest"],
            artifact_storage_digest=payload["artifact_storage_digest"],
            logical_instant=payload["logical_instant"],
            slot_digest=expected_digest,
        )

    def _read_slot_key(self, slot_key: str) -> SlotReadBack:
        pointer_path = self._pointer_path(slot_key)
        try:
            pointer_bytes = self._read_exact(pointer_path, "CORRUPT_SLOT_POINTER")
        except FileNotFoundError:
            _fail("MISSING_SLOT", slot_key)
        pointer = cj1_decode(pointer_bytes)
        if not isinstance(pointer, dict) or tuple(sorted(pointer)) != ("generation", "slot_digest"):
            _fail("CORRUPT_SLOT_POINTER", slot_key)
        generation = pointer["generation"]
        slot_digest = pointer["slot_digest"]
        if not isinstance(generation, int) or isinstance(generation, bool) or generation < 1:
            _fail("CORRUPT_SLOT_POINTER", "generation")
        if not isinstance(slot_digest, str) or not slot_digest.startswith("sha256:"):
            _fail("CORRUPT_SLOT_POINTER", "slot_digest")
        generation_path = self._generation_path(slot_key, generation, slot_digest)
        try:
            generation_bytes = self._read_exact(generation_path, "CORRUPT_SLOT")
        except FileNotFoundError:
            _fail("PARTIAL_SLOT", slot_key)
        return self._slot_from_payload(cj1_decode(generation_bytes), slot_digest)

    def read_slot(self, owner: str, slot_identity: str, slot_epoch: object) -> SlotReadBack:
        owner = _require_text(owner, "owner")
        slot_identity = _require_text(slot_identity, "slot_identity")
        cj1_encode(slot_epoch)
        slot_key = self._slot_key(owner, slot_identity, slot_epoch)
        current = self._read_slot_key(slot_key)
        if (current.owner, current.slot_identity, current.slot_epoch) != (
            owner, slot_identity, slot_epoch
        ):
            _fail("SLOT_BINDING_MISMATCH", slot_key)
        record_path = self._record_path(current.artifact_identity)
        try:
            record_bytes = self._read_exact(record_path, "CORRUPT_IMMUTABLE_RECORD")
        except FileNotFoundError:
            _fail("PARTIAL_SLOT", current.artifact_identity)
        if cj1_digest(cj1_decode(record_bytes)) != current.artifact_storage_digest:
            _fail("SLOT_ARTIFACT_MISMATCH", current.artifact_identity)
        return current

    def read_slot_generation(
        self,
        owner: str,
        slot_identity: str,
        slot_epoch: object,
        generation: int,
        slot_digest: str,
    ) -> SlotReadBack:
        owner = _require_text(owner, "owner")
        slot_identity = _require_text(slot_identity, "slot_identity")
        cj1_encode(slot_epoch)
        if not isinstance(generation, int) or isinstance(generation, bool) or generation < 1:
            _fail("INVALID_PERSISTENCE_INPUT", "generation")
        slot_digest = _require_sha256(
            slot_digest,
            "slot_digest",
            code="INVALID_PERSISTENCE_INPUT",
        )
        slot_key = self._slot_key(owner, slot_identity, slot_epoch)
        generation_path = self._generation_path(slot_key, generation, slot_digest)
        try:
            generation_bytes = self._read_exact(generation_path, "CORRUPT_SLOT")
        except FileNotFoundError:
            _fail("MISSING_SLOT", generation_path.name)
        read_back = self._slot_from_payload(cj1_decode(generation_bytes), slot_digest)
        if (
            read_back.owner,
            read_back.slot_identity,
            read_back.slot_epoch,
            read_back.generation,
            read_back.slot_digest,
        ) != (owner, slot_identity, slot_epoch, generation, slot_digest):
            _fail("SLOT_BINDING_MISMATCH", generation_path.name)
        try:
            record_bytes = self._read_exact(
                self._record_path(read_back.artifact_identity),
                "CORRUPT_IMMUTABLE_RECORD",
            )
        except FileNotFoundError:
            _fail("PARTIAL_SLOT", read_back.artifact_identity)
        if cj1_digest(cj1_decode(record_bytes)) != read_back.artifact_storage_digest:
            _fail("SLOT_ARTIFACT_MISMATCH", read_back.artifact_identity)
        return read_back

    def _replace_pointer(
        self,
        path: Path,
        data: bytes,
        hook: CrashHook | None,
    ) -> None:
        fd, temporary_name = mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
        temporary = Path(temporary_name)
        replaced = False
        try:
            _write_all(fd, data)
            os.fsync(fd)
            self._invoke(hook, SLOT_AFTER_POINTER_FSYNC)
        finally:
            os.close(fd)
        try:
            os.replace(temporary, path)
            replaced = True
            self._invoke(hook, SLOT_AFTER_POINTER_REPLACE)
            _fsync_directory(path.parent)
        finally:
            if temporary.exists() and replaced:
                temporary.unlink()

    def _compare_and_swap_bytes(
        self,
        *,
        owner: str,
        slot_identity: str,
        slot_epoch: object,
        expected_slot_digest: str | None,
        expected_status: str | None,
        successor_status: str,
        address: ArtifactAddress,
        canonical_bytes: bytes,
        storage_digest: str,
        logical_instant: str,
        hook: CrashHook | None,
    ) -> CompareAndSwapResult:
        """Shared checked-byte CAS engine for model and subcontract callers."""

        slot_key = self._slot_key(owner, slot_identity, slot_epoch)
        lock_path = self._locks / f"{slot_key}.lock"
        lock_fd = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX)
            try:
                current = self._read_slot_key(slot_key)
            except CandidatePersistenceError as exc:
                if exc.code != "MISSING_SLOT":
                    raise
                current = None
            if current is not None:
                identical = (
                    current.predecessor_slot_digest == expected_slot_digest
                    and current.predecessor_status == expected_status
                    and current.current_status == successor_status
                    and current.artifact_identity == address.artifact_identity
                    and current.artifact_digest == address.artifact_digest
                    and current.artifact_storage_digest == storage_digest
                    and current.logical_instant == logical_instant
                )
                if identical:
                    return CompareAndSwapResult(
                        "IDEMPOTENT", self.read_slot(owner, slot_identity, slot_epoch)
                    )
            actual_digest = None if current is None else current.slot_digest
            actual_status = None if current is None else current.current_status
            if actual_digest != expected_slot_digest or actual_status != expected_status:
                if current is None:
                    _fail("CAS_CONFLICT_WITH_ABSENT_SLOT", slot_key)
                return CompareAndSwapResult(
                    "CONFLICT", self.read_slot(owner, slot_identity, slot_epoch)
                )
            record_outcome = self._publish_immutable_bytes(
                self._record_path(address.artifact_identity),
                canonical_bytes,
                hook=hook,
                fsync_point=IMMUTABLE_AFTER_TEMP_FSYNC,
                publish_point=IMMUTABLE_AFTER_PUBLISH,
            )
            if record_outcome not in {"CREATED", "IDEMPOTENT"}:
                _fail("DURABLE_WRITE_FAILED", address.artifact_identity)
            generation = 1 if current is None else current.generation + 1
            payload = self._slot_payload(
                owner=owner,
                slot_identity=slot_identity,
                slot_epoch=slot_epoch,
                generation=generation,
                predecessor_slot_digest=expected_slot_digest,
                predecessor_status=expected_status,
                current_status=successor_status,
                address=address,
                artifact_storage_digest=storage_digest,
                logical_instant=logical_instant,
            )
            slot_digest = cj1_digest(payload)
            generation_path = self._generation_path(slot_key, generation, slot_digest)
            self._publish_immutable_bytes(
                generation_path,
                cj1_encode(payload),
                hook=hook,
                fsync_point=SLOT_AFTER_GENERATION_FSYNC,
                publish_point=SLOT_AFTER_GENERATION_PUBLISH,
            )
            pointer = cj1_encode({"generation": generation, "slot_digest": slot_digest})
            self._replace_pointer(self._pointer_path(slot_key), pointer, hook)
            read_back = self.read_slot(owner, slot_identity, slot_epoch)
            if read_back.slot_digest != slot_digest:
                _fail("WRITE_READ_BACK_MISMATCH", slot_key)
            return CompareAndSwapResult("WON", read_back)
        finally:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            os.close(lock_fd)

    def compare_and_swap(
        self,
        *,
        owner: str,
        slot_identity: str,
        slot_epoch: object,
        expected_slot_digest: str | None,
        expected_status: str | None,
        successor_status: str,
        model: FrozenCanonicalModel,
        artifact_identity: str | None = None,
        artifact_digest: str | None = None,
        logical_instant: str,
        owner_bindings: Mapping[str, str] | None = None,
        _fixture_crash_hook: CrashHook | None = None,
    ) -> CompareAndSwapResult:
        owner = _require_text(owner, "owner")
        slot_identity = _require_text(slot_identity, "slot_identity")
        successor_status = _require_text(successor_status, "successor_status")
        logical_instant = _require_text(logical_instant, "logical_instant")
        cj1_encode(slot_epoch)
        if (expected_slot_digest is None) != (expected_status is None):
            _fail("INVALID_EXPECTED_SLOT", "digest/status half-pair")
        if expected_slot_digest is not None:
            _require_text(expected_slot_digest, "expected_slot_digest")
        validate_artifact(model, owner_bindings=owner_bindings)
        if getattr(model, "producing_owner", owner) != owner:
            _fail("PERSISTENCE_OWNER_MISMATCH", type(model).__name__)
        address = self._artifact_address(model, artifact_identity, artifact_digest)
        canonical_bytes = model.to_cj1_bytes()
        storage_digest = cj1_digest(model.to_cj1_object())
        return self._compare_and_swap_bytes(
            owner=owner,
            slot_identity=slot_identity,
            slot_epoch=slot_epoch,
            expected_slot_digest=expected_slot_digest,
            expected_status=expected_status,
            successor_status=successor_status,
            address=address,
            canonical_bytes=canonical_bytes,
            storage_digest=storage_digest,
            logical_instant=logical_instant,
            hook=_fixture_crash_hook,
        )

    def compare_and_swap_subcontract(
        self,
        *,
        owner: str,
        slot_identity: str,
        slot_epoch: object,
        expected_slot_digest: str | None,
        expected_status: str | None,
        successor_status: str,
        address: SubcontractAddress,
        canonical_bytes: bytes,
        logical_instant: str,
        _fixture_crash_hook: CrashHook | None = None,
    ) -> CompareAndSwapResult:
        owner = _require_text(owner, "owner")
        slot_identity = _require_text(slot_identity, "slot_identity")
        successor_status = _require_text(successor_status, "successor_status")
        logical_instant = _require_text(logical_instant, "logical_instant")
        cj1_encode(slot_epoch)
        if (expected_slot_digest is None) != (expected_status is None):
            _fail("INVALID_EXPECTED_SLOT", "digest/status half-pair")
        if expected_slot_digest is not None:
            _require_sha256(
                expected_slot_digest,
                "expected_slot_digest",
                code="INVALID_EXPECTED_SLOT",
            )
        if expected_status is not None:
            _require_text(expected_status, "expected_status")
        cas_arguments = {
            "owner": owner,
            "slot_identity": slot_identity,
            "slot_epoch": slot_epoch,
            "expected_slot_digest": expected_slot_digest,
            "expected_status": expected_status,
            "successor_status": successor_status,
            "logical_instant": logical_instant,
        }
        _validate_subcontract_admission(
            address=address,
            canonical_bytes=canonical_bytes,
            expected_mode="CAS",
            cas_arguments=cas_arguments,
        )
        artifact_address = ArtifactAddress(address.identity, address.digest)
        result = self._compare_and_swap_bytes(
            owner=owner,
            slot_identity=slot_identity,
            slot_epoch=slot_epoch,
            expected_slot_digest=expected_slot_digest,
            expected_status=expected_status,
            successor_status=successor_status,
            address=artifact_address,
            canonical_bytes=canonical_bytes,
            storage_digest=address.digest,
            logical_instant=logical_instant,
            hook=_fixture_crash_hook,
        )
        if result.outcome != "CONFLICT":
            read_back = self.read_subcontract(address)
            if read_back.canonical_bytes != canonical_bytes:
                _fail("WRITE_READ_BACK_MISMATCH", address.identity)
        return result


__all__ = [
    "ArtifactAddress",
    "CRASH_POINTS",
    "CandidateHReadOnlyStore",
    "CandidateHStore",
    "CandidatePersistenceError",
    "CompareAndSwapResult",
    "IMMUTABLE_AFTER_PUBLISH",
    "IMMUTABLE_AFTER_TEMP_FSYNC",
    "ImmutableReadBack",
    "ImmutableWriteResult",
    "InjectedPersistenceCrash",
    "SLOT_AFTER_GENERATION_FSYNC",
    "SLOT_AFTER_GENERATION_PUBLISH",
    "SLOT_AFTER_POINTER_FSYNC",
    "SLOT_AFTER_POINTER_REPLACE",
    "SUBCONTRACT_KIND_SPECS",
    "SlotReadBack",
    "SubcontractAddress",
    "SubcontractReadBack",
    "SubcontractWriteResult",
]
