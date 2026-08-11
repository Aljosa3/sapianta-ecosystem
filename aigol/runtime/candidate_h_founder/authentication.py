"""Fixture-only Candidate H authentication through durable ResultV2.

The module consumes already accepted context, uses only the public Candidate
store, and stops after one complete durable ResultV2.  It does not select a
Human disposition, create a store or root, orchestrate, replay, execute BEGIN,
activate, deploy, or perform a production action.
"""

from __future__ import annotations

import base64
import hashlib
from dataclasses import dataclass, replace

from .cj1 import cj1_decode, cj1_digest, cj1_encode, cj1_identity, sha256_hex
from .models import (
    HumanFounderAuthenticationCommitmentV2,
    HumanFounderAuthenticationResultReadBackEvidenceV2,
    HumanFounderExternalCapacityEvidenceV2,
)
from .persistence import (
    CandidateHStore,
    CompareAndSwapResult,
    ImmutableWriteResult,
    SlotReadBack,
    SubcontractAddress,
    SubcontractWriteResult,
    SUBCONTRACT_KIND_SPECS,
)
from .validators import (
    ARTIFACT_IDENTITY_SPECS,
    CandidateValidationError,
    expected_artifact_identifiers,
    validate_artifact,
)


class CandidateAuthenticationError(RuntimeError):
    """Stable fail-closed fixture authentication failure."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}:{detail}")


def _fail(code: str, detail: str) -> None:
    raise CandidateAuthenticationError(code, detail)


@dataclass(frozen=True, slots=True)
class FixtureAuthenticationContext:
    capacity: HumanFounderExternalCapacityEvidenceV2
    authentication_commitment: HumanFounderAuthenticationCommitmentV2
    authentication_open_read_back: SlotReadBack
    signer_available_read_back: SlotReadBack
    fixture_public_key: bytes
    fixture_private_seed: bytes | None
    one_use_claim_token_identity: str
    one_use_claim_token_digest: str
    one_use_non_equivocation_proof_identity: str
    one_use_non_equivocation_proof_digest: str
    claim_logical_instant: str
    acceptance_logical_instant: str
    completion_logical_instant: str


@dataclass(frozen=True, slots=True)
class FixtureAuthenticationExecution:
    result: HumanFounderAuthenticationResultReadBackEvidenceV2
    result_write: ImmutableWriteResult
    operation: SubcontractWriteResult
    claim: CompareAndSwapResult
    intent: SubcontractWriteResult
    acceptance: CompareAndSwapResult
    receipt: SubcontractWriteResult
    outcome: CompareAndSwapResult
    outcome_read_back: SubcontractWriteResult
    terminal: CompareAndSwapResult
    authoritative_read_back: SubcontractWriteResult
    logical_human_authorizations: int = 1
    logical_signer_invocations: int = 1
    admissible_results: int = 1
    founding_effects: int = 0


def _base64url_no_pad(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


# Minimal RFC 8032 Ed25519-pure fixture implementation.  It signs and verifies
# the direct message bytes and exposes no algorithm selector or production key.
_Q = 2**255 - 19
_L = 2**252 + 27742317777372353535851937790883648493


def _inverse(value: int) -> int:
    return pow(value, _Q - 2, _Q)


_D = (-121665 * _inverse(121666)) % _Q
_I = pow(2, (_Q - 1) // 4, _Q)


def _recover_x(y_coordinate: int) -> int:
    xx = (y_coordinate * y_coordinate - 1) * _inverse(
        _D * y_coordinate * y_coordinate + 1
    )
    x_coordinate = pow(xx, (_Q + 3) // 8, _Q)
    if (x_coordinate * x_coordinate - xx) % _Q != 0:
        x_coordinate = (x_coordinate * _I) % _Q
    if x_coordinate % 2 != 0:
        x_coordinate = _Q - x_coordinate
    return x_coordinate


_BASE_Y = (4 * _inverse(5)) % _Q
_BASE_POINT = (_recover_x(_BASE_Y), _BASE_Y)


def _edwards_add(
    left: tuple[int, int], right: tuple[int, int]
) -> tuple[int, int]:
    x_left, y_left = left
    x_right, y_right = right
    product = _D * x_left * x_right * y_left * y_right
    return (
        (x_left * y_right + x_right * y_left) * _inverse(1 + product) % _Q,
        (y_left * y_right + x_left * x_right) * _inverse(1 - product) % _Q,
    )


def _scalar_multiply(point: tuple[int, int], scalar: int) -> tuple[int, int]:
    result = (0, 1)
    addend = point
    while scalar:
        if scalar & 1:
            result = _edwards_add(result, addend)
        addend = _edwards_add(addend, addend)
        scalar >>= 1
    return result


def _encode_point(point: tuple[int, int]) -> bytes:
    x_coordinate, y_coordinate = point
    encoded = y_coordinate | ((x_coordinate & 1) << 255)
    return encoded.to_bytes(32, "little")


def _decode_point(encoded: bytes) -> tuple[int, int]:
    if len(encoded) != 32:
        raise ValueError("Ed25519 point must contain 32 octets")
    integer = int.from_bytes(encoded, "little")
    y_coordinate = integer & ((1 << 255) - 1)
    if y_coordinate >= _Q:
        raise ValueError("Ed25519 point is noncanonical")
    x_coordinate = _recover_x(y_coordinate)
    if (x_coordinate & 1) != (integer >> 255):
        x_coordinate = _Q - x_coordinate
    if (
        -x_coordinate * x_coordinate
        + y_coordinate * y_coordinate
        - 1
        - _D * x_coordinate * x_coordinate * y_coordinate * y_coordinate
    ) % _Q != 0:
        raise ValueError("Ed25519 point is not on curve")
    return x_coordinate, y_coordinate


def _expanded_secret(seed: bytes) -> tuple[int, bytes]:
    if len(seed) != 32:
        raise ValueError("Ed25519 seed must contain 32 octets")
    digest = hashlib.sha512(seed).digest()
    scalar_bytes = bytearray(digest[:32])
    scalar_bytes[0] &= 248
    scalar_bytes[31] &= 63
    scalar_bytes[31] |= 64
    return int.from_bytes(scalar_bytes, "little"), digest[32:]


def fixture_ed25519_public_key(seed: bytes) -> bytes:
    scalar, _ = _expanded_secret(seed)
    return _encode_point(_scalar_multiply(_BASE_POINT, scalar))


_FIXTURE_ED25519_SEED = bytes.fromhex(
    "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"
)
_FIXTURE_ED25519_PUBLIC_KEY = fixture_ed25519_public_key(_FIXTURE_ED25519_SEED)


def _ed25519_sign(seed: bytes, message: bytes) -> bytes:
    scalar, prefix = _expanded_secret(seed)
    public_key = _encode_point(_scalar_multiply(_BASE_POINT, scalar))
    nonce = int.from_bytes(hashlib.sha512(prefix + message).digest(), "little") % _L
    encoded_r = _encode_point(_scalar_multiply(_BASE_POINT, nonce))
    challenge = int.from_bytes(
        hashlib.sha512(encoded_r + public_key + message).digest(), "little"
    ) % _L
    encoded_s = ((nonce + challenge * scalar) % _L).to_bytes(32, "little")
    return encoded_r + encoded_s


def fixture_ed25519_verify(
    public_key: bytes,
    message: bytes,
    signature: bytes,
) -> bool:
    try:
        if len(public_key) != 32 or len(signature) != 64:
            return False
        encoded_r = signature[:32]
        scalar_s = int.from_bytes(signature[32:], "little")
        if scalar_s >= _L:
            return False
        point_r = _decode_point(encoded_r)
        point_a = _decode_point(public_key)
        challenge = int.from_bytes(
            hashlib.sha512(encoded_r + public_key + message).digest(), "little"
        ) % _L
        return _scalar_multiply(_BASE_POINT, scalar_s) == _edwards_add(
            point_r, _scalar_multiply(point_a, challenge)
        )
    except (TypeError, ValueError):
        return False


def _subcontract(
    kind: str,
    body: dict[str, object],
) -> tuple[SubcontractAddress, bytes]:
    spec = SUBCONTRACT_KIND_SPECS[kind]
    if set(body) != set(spec.field_names):
        _fail("SUBCONTRACT_SCHEMA_MISMATCH", kind)
    ordered_body = {name: body[name] for name in spec.field_names}
    canonical_bytes = cj1_encode(ordered_body)
    digest_hex = sha256_hex(canonical_bytes)
    return (
        SubcontractAddress(
            kind,
            f"{spec.prefix}:{digest_hex}",
            f"sha256:{digest_hex}",
        ),
        canonical_bytes,
    )


def _pair(address: SubcontractAddress) -> tuple[str, str]:
    return address.identity, address.digest


def _require_pair(identity: object, digest: object, detail: str) -> None:
    if not isinstance(identity, str) or identity.count(":") != 1:
        _fail("SUBCONTRACT_PAIR_MISMATCH", detail)
    _, suffix = identity.split(":", 1)
    if (
        len(suffix) != 64
        or any(character not in "0123456789abcdef" for character in suffix)
        or digest != f"sha256:{suffix}"
    ):
        _fail("SUBCONTRACT_PAIR_MISMATCH", detail)


def _require_slot(
    read_back: SlotReadBack,
    *,
    owner: str,
    slot_identity: str,
    slot_epoch: object,
    status: str,
    detail: str,
) -> None:
    if (
        not isinstance(read_back, SlotReadBack)
        or read_back.owner != owner
        or read_back.slot_identity != slot_identity
        or read_back.slot_epoch != slot_epoch
        or read_back.current_status != status
    ):
        _fail("SUBCONTRACT_STATE_MISMATCH", detail)


def _resolve_authoritative_cas(
    store: CandidateHStore,
    *,
    subcontract_kind: str,
    local_address: SubcontractAddress,
    local_canonical_bytes: bytes,
    result: CompareAndSwapResult,
    owner: str,
    slot_identity: str,
    slot_epoch: object,
    expected_slot_digest: str | None,
    expected_status: str | None,
    successor_status: str,
    logical_instant: str,
    detail: str,
) -> tuple[SubcontractAddress, dict[str, object]]:
    if not isinstance(result, CompareAndSwapResult) or result.outcome not in {
        "WON",
        "IDEMPOTENT",
        "CONFLICT",
    }:
        _fail("RETRY_TUPLE_MISMATCH", f"{detail}:cas outcome")
    read_back = result.read_back
    if not isinstance(read_back, SlotReadBack):
        _fail("RETRY_TUPLE_MISMATCH", f"{detail}:slot read-back")
    authoritative_address = SubcontractAddress(
        subcontract_kind,
        read_back.artifact_identity,
        read_back.artifact_digest,
    )
    authoritative = store.read_subcontract(authoritative_address)
    if (
        authoritative_address != local_address
        or authoritative.address != authoritative_address
        or authoritative.storage_digest != read_back.artifact_storage_digest
        or (
            read_back.owner,
            read_back.slot_identity,
            read_back.slot_epoch,
            read_back.predecessor_slot_digest,
            read_back.predecessor_status,
            read_back.current_status,
            read_back.artifact_identity,
            read_back.artifact_digest,
            read_back.logical_instant,
        )
        != (
            owner,
            slot_identity,
            slot_epoch,
            expected_slot_digest,
            expected_status,
            successor_status,
            authoritative_address.identity,
            authoritative_address.digest,
            logical_instant,
        )
    ):
        _fail("RETRY_TUPLE_MISMATCH", f"{detail}:authoritative binding")
    if authoritative.canonical_bytes != local_canonical_bytes:
        _fail("RETRY_TUPLE_MISMATCH", f"{detail}:canonical bytes")
    authoritative_body = cj1_decode(authoritative.canonical_bytes)
    if not isinstance(authoritative_body, dict):
        _fail("RETRY_TUPLE_MISMATCH", f"{detail}:canonical body")
    return authoritative_address, authoritative_body


def _outcome_values(
    context: FixtureAuthenticationContext,
    message: bytes,
) -> tuple[str, str | None, str | None, str, str | None]:
    seed = context.fixture_private_seed
    if seed is None:
        return (
            "INDETERMINATE_FINAL",
            None,
            None,
            "NOT_APPLICABLE",
            "ACCEPTED_OPERATION_RECONSTRUCTION_UNAVAILABLE",
        )
    try:
        signature_bytes = _ed25519_sign(seed, message)
        derived_public_key = fixture_ed25519_public_key(seed)
    except (TypeError, ValueError):
        return (
            "REJECTED_FINAL",
            None,
            None,
            "FALSE",
            "SIGNER_INPUT_OR_SIGNATURE_INVALID",
        )
    if (
        derived_public_key != context.fixture_public_key
        or not fixture_ed25519_verify(
            context.fixture_public_key, message, signature_bytes
        )
    ):
        return (
            "REJECTED_FINAL",
            None,
            None,
            "FALSE",
            "SIGNER_INPUT_OR_SIGNATURE_INVALID",
        )
    return (
        "VALID_SIGNATURE_FINAL",
        _base64url_no_pad(signature_bytes),
        f"sha256:{sha256_hex(signature_bytes)}",
        "TRUE",
        None,
    )


def _terminal_values(
    outcome_status: str,
    signature: str | None,
) -> tuple[str, str, str | None, str, str]:
    if outcome_status == "VALID_SIGNATURE_FINAL":
        return "AUTHENTICATED_FINAL", "AUTHENTICATED_VALID", signature, "TRUE", "NONE"
    if outcome_status == "REJECTED_FINAL":
        return (
            "INDETERMINATE_EXHAUSTED",
            "AUTHENTICATION_REJECTED_FINAL",
            None,
            "FALSE",
            "RESULT_UNRECOVERABLE_NO_RETRY",
        )
    return (
        "INDETERMINATE_EXHAUSTED",
        "INDETERMINATE_NO_VALID_RESULT",
        None,
        "NOT_APPLICABLE",
        "RESULT_UNRECOVERABLE_NO_RETRY",
    )


def _build_result(
    *,
    owner: str,
    values: dict[str, object],
) -> HumanFounderAuthenticationResultReadBackEvidenceV2:
    model_type = HumanFounderAuthenticationResultReadBackEvidenceV2
    envelope = {
        "artifact_type": model_type.CONSTANTS["artifact_type"],
        "artifact_version": model_type.CONSTANTS["artifact_version"],
        "artifact_identity": "human-founder-auth-result-readback-v2:" + "0" * 64,
        "artifact_digest": "sha256:" + "0" * 64,
        "contract_version": model_type.CONSTANTS["contract_version"],
        "idempotency_identity": "human-founder-auth-result-readback-idem-v2:" + "0" * 64,
        "producing_owner": owner,
        "metadata": {},
    }
    envelope.update(values)
    pending = model_type(**envelope)
    idempotency, identity, digest = expected_artifact_identifiers(pending)
    spec = ARTIFACT_IDENTITY_SPECS[model_type]
    return replace(
        pending,
        idempotency_identity=idempotency,
        **{spec.identity_field: identity, spec.digest_field: digest},
    )


def authenticate_fixture_candidate_h(
    store: CandidateHStore,
    context: FixtureAuthenticationContext,
) -> FixtureAuthenticationExecution:
    """Persist one fixture authentication and stop after complete ResultV2."""

    if not isinstance(store, CandidateHStore):
        _fail("DURABLE_ACCEPTANCE_REQUIRED", "CandidateHStore")
    if not isinstance(context, FixtureAuthenticationContext):
        _fail("SUBCONTRACT_SCHEMA_MISMATCH", "FixtureAuthenticationContext")
    capacity = context.capacity
    if not isinstance(capacity, HumanFounderExternalCapacityEvidenceV2) or not isinstance(
        context.authentication_commitment,
        HumanFounderAuthenticationCommitmentV2,
    ):
        _fail("SUBCONTRACT_SCHEMA_MISMATCH", "capacity/authentication commitment")
    owner = capacity.producing_owner
    owner_bindings = {"RESOLVED_EXTERNAL_PREMISE_AUTHORITY": owner}
    try:
        validate_artifact(capacity, owner_bindings=owner_bindings)
        validate_artifact(context.authentication_commitment)
    except CandidateValidationError as exc:
        _fail("SUBCONTRACT_SCHEMA_MISMATCH", str(exc))
    actor = capacity.human_actor_identity_record.human_actor_identity
    key_record = capacity.authentication_key_binding_record
    public_key = context.fixture_public_key
    if (
        not isinstance(public_key, bytes)
        or len(public_key) != 32
        or public_key != _FIXTURE_ED25519_PUBLIC_KEY
    ):
        _fail("FIXTURE_KEY_MISMATCH", "public key")
    expected_key_identity = f"human-founder-ed25519-key-v1:{sha256_hex(public_key)}"
    if (
        key_record.authentication_public_key != _base64url_no_pad(public_key)
        or key_record.authentication_key_identity != expected_key_identity
        or key_record.authentication_algorithm != "ED25519_RFC8032_PURE"
    ):
        _fail("FIXTURE_KEY_MISMATCH", "capacity binding")
    if (
        capacity.external_premise_identity is None
        or capacity.external_premise_digest is None
    ):
        _fail("SUBCONTRACT_PAIR_MISMATCH", "external premise")
    commitment_payload = context.authentication_commitment.to_cj1_object()
    commitment_pair = (
        cj1_identity("human-founder-auth-commitment-v2-sha256", commitment_payload),
        cj1_digest(commitment_payload),
    )
    message = context.authentication_commitment.to_cj1_bytes()
    if commitment_pair[1] != f"sha256:{sha256_hex(message)}":
        _fail("SUBCONTRACT_PAIR_MISMATCH", "authentication commitment")
    for identity, digest, detail in (
        (
            capacity.external_premise_identity,
            capacity.external_premise_digest,
            "external premise",
        ),
        (
            capacity.artifact_identity,
            capacity.artifact_digest,
            "capacity",
        ),
        (*commitment_pair, "authentication commitment"),
        (
            context.one_use_claim_token_identity,
            context.one_use_claim_token_digest,
            "one-use claim token",
        ),
        (
            context.one_use_non_equivocation_proof_identity,
            context.one_use_non_equivocation_proof_digest,
            "one-use proof",
        ),
    ):
        _require_pair(identity, digest, detail)
    for name in (
        "claim_logical_instant",
        "acceptance_logical_instant",
        "completion_logical_instant",
    ):
        if not isinstance(getattr(context, name), str) or not getattr(context, name):
            _fail("SUBCONTRACT_CONSTANT_MISMATCH", name)
    _require_slot(
        context.authentication_open_read_back,
        owner=owner,
        slot_identity=capacity.human_authentication_slot_identity,
        slot_epoch=capacity.human_authentication_epoch,
        status="OPEN",
        detail="authentication OPEN",
    )
    _require_slot(
        context.signer_available_read_back,
        owner=owner,
        slot_identity=context.signer_available_read_back.slot_identity,
        slot_epoch=context.signer_available_read_back.slot_epoch,
        status="AVAILABLE",
        detail="signer AVAILABLE",
    )

    operation_body = {
        "external_premise_identity": capacity.external_premise_identity,
        "external_premise_digest": capacity.external_premise_digest,
        "human_founder_capacity_identity": capacity.artifact_identity,
        "human_founder_capacity_digest": capacity.artifact_digest,
        "human_actor_identity": actor,
        "human_authentication_slot_identity": capacity.human_authentication_slot_identity,
        "human_authentication_epoch": capacity.human_authentication_epoch,
        "authentication_sequence": 1,
        "authentication_commitment_identity": commitment_pair[0],
        "authentication_commitment_digest": commitment_pair[1],
        "authenticated_message_representation": "EXACT_UTF8_CJ1_P_AUTH_V2_BYTES",
        "authenticated_message_digest": commitment_pair[1],
        "signature_scheme": "ED25519_RFC8032_PURE",
        "signature_key_identity": expected_key_identity,
        "predecessor_authentication_slot_status": "OPEN",
    }
    operation_address, operation_bytes = _subcontract(
        "AUTHENTICATION_OPERATION_V1", operation_body
    )
    operation = store.write_subcontract(operation_address, operation_bytes)

    claim_body = {
        "authentication_operation_identity": operation_address.identity,
        "authentication_operation_digest": operation_address.digest,
        "human_authentication_slot_identity": capacity.human_authentication_slot_identity,
        "human_authentication_epoch": capacity.human_authentication_epoch,
        "authentication_sequence": 1,
        "human_founder_capacity_identity": capacity.artifact_identity,
        "human_founder_capacity_digest": capacity.artifact_digest,
        "predecessor_authentication_slot_status": "OPEN",
        "claimed_authentication_slot_status": "AUTHENTICATING",
        "one_use_claim_token_identity": context.one_use_claim_token_identity,
        "one_use_claim_token_digest": context.one_use_claim_token_digest,
        "claim_logical_instant": context.claim_logical_instant,
        "producing_owner": owner,
        "predecessor_authentication_slot_digest": (
            context.authentication_open_read_back.slot_digest
        ),
    }
    claim_address, claim_bytes = _subcontract("AUTHENTICATION_CLAIM_CAS_V1", claim_body)
    claim = store.compare_and_swap_subcontract(
        owner=owner,
        slot_identity=capacity.human_authentication_slot_identity,
        slot_epoch=capacity.human_authentication_epoch,
        expected_slot_digest=context.authentication_open_read_back.slot_digest,
        expected_status="OPEN",
        successor_status="AUTHENTICATING",
        address=claim_address,
        canonical_bytes=claim_bytes,
        logical_instant=context.claim_logical_instant,
    )
    if claim.outcome == "CONFLICT":
        if claim.read_back.current_status not in {
            "AUTHENTICATED_FINAL",
            "INDETERMINATE_EXHAUSTED",
        } or claim.read_back.predecessor_slot_digest is None:
            _fail("SUBCONTRACT_STATE_MISMATCH", "authentication claim conflict")
        claim_slot_digest = claim.read_back.predecessor_slot_digest
    else:
        claim_slot_digest = claim.read_back.slot_digest

    signer_slot_identity = context.signer_available_read_back.slot_identity
    signer_slot_epoch = context.signer_available_read_back.slot_epoch
    intent_body = {
        "external_premise_identity": capacity.external_premise_identity,
        "external_premise_digest": capacity.external_premise_digest,
        "human_founder_capacity_identity": capacity.artifact_identity,
        "human_founder_capacity_digest": capacity.artifact_digest,
        "human_actor_identity": actor,
        "authentication_operation_identity": operation_address.identity,
        "authentication_operation_digest": operation_address.digest,
        "authentication_claim_cas_identity": claim_address.identity,
        "authentication_claim_cas_digest": claim_address.digest,
        "authentication_commitment_identity": commitment_pair[0],
        "authentication_commitment_digest": commitment_pair[1],
        "authenticated_message_representation": "EXACT_UTF8_CJ1_P_AUTH_V2_BYTES",
        "authenticated_message_digest": commitment_pair[1],
        "signature_scheme": "ED25519_RFC8032_PURE",
        "signature_key_identity": expected_key_identity,
        "signer_operation_slot_identity": signer_slot_identity,
        "signer_operation_slot_epoch": signer_slot_epoch,
        "authentication_sequence": 1,
        "maximum_logical_signer_invocations": 1,
    }
    intent_address, intent_bytes = _subcontract("SIGNER_INVOCATION_INTENT_V1", intent_body)
    intent = store.write_subcontract(intent_address, intent_bytes)

    acceptance_body = {
        "signer_invocation_intent_identity": intent_address.identity,
        "signer_invocation_intent_digest": intent_address.digest,
        "authentication_operation_identity": operation_address.identity,
        "authentication_operation_digest": operation_address.digest,
        "authentication_claim_cas_identity": claim_address.identity,
        "authentication_claim_cas_digest": claim_address.digest,
        "human_founder_capacity_identity": capacity.artifact_identity,
        "human_founder_capacity_digest": capacity.artifact_digest,
        "authenticated_message_representation": "EXACT_UTF8_CJ1_P_AUTH_V2_BYTES",
        "authenticated_message_digest": commitment_pair[1],
        "signature_scheme": "ED25519_RFC8032_PURE",
        "signature_key_identity": expected_key_identity,
        "signer_operation_slot_identity": signer_slot_identity,
        "signer_operation_slot_epoch": signer_slot_epoch,
        "predecessor_signer_slot_status": "AVAILABLE",
        "accepted_signer_slot_status": "ACCEPTED_IN_PROGRESS",
        "invocation_sequence": 1,
        "maximum_logical_signer_invocations": 1,
        "acceptance_logical_instant": context.acceptance_logical_instant,
        "producing_owner": owner,
        "predecessor_signer_slot_digest": context.signer_available_read_back.slot_digest,
    }
    acceptance_address, acceptance_bytes = _subcontract(
        "SIGNER_ACCEPTANCE_CAS_V1", acceptance_body
    )
    acceptance = store.compare_and_swap_subcontract(
        owner=owner,
        slot_identity=signer_slot_identity,
        slot_epoch=signer_slot_epoch,
        expected_slot_digest=context.signer_available_read_back.slot_digest,
        expected_status="AVAILABLE",
        successor_status="ACCEPTED_IN_PROGRESS",
        address=acceptance_address,
        canonical_bytes=acceptance_bytes,
        logical_instant=context.acceptance_logical_instant,
    )
    if acceptance.outcome == "CONFLICT":
        if acceptance.read_back.current_status not in {
            "VALID_SIGNATURE_FINAL",
            "REJECTED_FINAL",
            "INDETERMINATE_FINAL",
        } or acceptance.read_back.predecessor_slot_digest is None:
            _fail("RETRY_TUPLE_MISMATCH", "signer acceptance conflict")
        accepted_slot_digest = acceptance.read_back.predecessor_slot_digest
    else:
        accepted_slot_digest = acceptance.read_back.slot_digest

    receipt_body = {
        "signer_acceptance_cas_identity": acceptance_address.identity,
        "signer_acceptance_cas_digest": acceptance_address.digest,
        "signer_invocation_intent_identity": intent_address.identity,
        "signer_invocation_intent_digest": intent_address.digest,
        "authentication_operation_identity": operation_address.identity,
        "authentication_operation_digest": operation_address.digest,
        "authentication_claim_cas_identity": claim_address.identity,
        "authentication_claim_cas_digest": claim_address.digest,
        "signer_operation_slot_identity": signer_slot_identity,
        "signer_operation_slot_epoch": signer_slot_epoch,
        "invocation_sequence": 1,
        "signer_operation_status": "ACCEPTED_IN_PROGRESS",
        "acceptance_logical_instant": context.acceptance_logical_instant,
        "accepted_slot_digest": accepted_slot_digest,
    }
    receipt_address, receipt_bytes = _subcontract(
        "SIGNER_INVOCATION_RECEIPT_V1", receipt_body
    )
    receipt = store.write_subcontract(receipt_address, receipt_bytes)

    current_signer = store.read_slot(owner, signer_slot_identity, signer_slot_epoch)
    if current_signer.current_status in {
        "VALID_SIGNATURE_FINAL",
        "REJECTED_FINAL",
        "INDETERMINATE_FINAL",
    }:
        outcome_address = SubcontractAddress(
            "SIGNER_OUTCOME_V1",
            current_signer.artifact_identity,
            current_signer.artifact_digest,
        )
        persisted_outcome = store.read_subcontract(outcome_address)
        outcome_bytes = persisted_outcome.canonical_bytes
        outcome_body = cj1_decode(outcome_bytes)
        if not isinstance(outcome_body, dict):
            _fail("SUBCONTRACT_SCHEMA_MISMATCH", "persisted signer outcome")
        expected_pairs = {
            "signer_invocation_intent": _pair(intent_address),
            "signer_acceptance_cas": _pair(acceptance_address),
            "signer_invocation_receipt": _pair(receipt_address),
            "authentication_operation": _pair(operation_address),
            "authentication_claim_cas": _pair(claim_address),
            "human_founder_capacity": (
                capacity.artifact_identity,
                capacity.artifact_digest,
            ),
            "authentication_commitment": commitment_pair,
        }
        for base, expected_pair in expected_pairs.items():
            if (
                outcome_body.get(f"{base}_identity"),
                outcome_body.get(f"{base}_digest"),
            ) != expected_pair:
                _fail("RETRY_TUPLE_MISMATCH", base)
        if (
            outcome_body.get("authenticated_message_digest") != commitment_pair[1]
            or outcome_body.get("signature_key_identity") != expected_key_identity
            or outcome_body.get("signer_operation_slot_identity") != signer_slot_identity
            or outcome_body.get("signer_operation_slot_epoch") != signer_slot_epoch
        ):
            _fail("RETRY_TUPLE_MISMATCH", "message/key/slot")
        outcome = CompareAndSwapResult("IDEMPOTENT", current_signer)
    else:
        if current_signer.current_status != "ACCEPTED_IN_PROGRESS":
            _fail("DURABLE_ACCEPTANCE_REQUIRED", "signer receipt")
        (
            outcome_status,
            signature,
            signature_digest,
            verification_result,
            failure_code,
        ) = _outcome_values(context, message)
        outcome_body = {
            "signer_invocation_intent_identity": intent_address.identity,
            "signer_invocation_intent_digest": intent_address.digest,
            "signer_acceptance_cas_identity": acceptance_address.identity,
            "signer_acceptance_cas_digest": acceptance_address.digest,
            "signer_invocation_receipt_identity": receipt_address.identity,
            "signer_invocation_receipt_digest": receipt_address.digest,
            "authentication_operation_identity": operation_address.identity,
            "authentication_operation_digest": operation_address.digest,
            "authentication_claim_cas_identity": claim_address.identity,
            "authentication_claim_cas_digest": claim_address.digest,
            "human_founder_capacity_identity": capacity.artifact_identity,
            "human_founder_capacity_digest": capacity.artifact_digest,
            "authentication_commitment_identity": commitment_pair[0],
            "authentication_commitment_digest": commitment_pair[1],
            "authenticated_message_representation": "EXACT_UTF8_CJ1_P_AUTH_V2_BYTES",
            "authenticated_message_digest": commitment_pair[1],
            "signature_scheme": "ED25519_RFC8032_PURE",
            "signature_key_identity": expected_key_identity,
            "outcome_status": outcome_status,
            "signature": signature,
            "signature_digest": signature_digest,
            "verification_result": verification_result,
            "failure_code": failure_code,
            "completion_logical_instant": context.completion_logical_instant,
            "terminal": True,
            "producing_owner": owner,
            "signer_operation_slot_identity": signer_slot_identity,
            "signer_operation_slot_epoch": signer_slot_epoch,
            "predecessor_signer_slot_digest": accepted_slot_digest,
            "predecessor_signer_slot_status": "ACCEPTED_IN_PROGRESS",
        }
        outcome_address, outcome_bytes = _subcontract("SIGNER_OUTCOME_V1", outcome_body)
        outcome = store.compare_and_swap_subcontract(
            owner=owner,
            slot_identity=signer_slot_identity,
            slot_epoch=signer_slot_epoch,
            expected_slot_digest=accepted_slot_digest,
            expected_status="ACCEPTED_IN_PROGRESS",
            successor_status=outcome_status,
            address=outcome_address,
            canonical_bytes=outcome_bytes,
            logical_instant=context.completion_logical_instant,
        )

    outcome_address, outcome_body = _resolve_authoritative_cas(
        store,
        subcontract_kind="SIGNER_OUTCOME_V1",
        local_address=outcome_address,
        local_canonical_bytes=outcome_bytes,
        result=outcome,
        owner=owner,
        slot_identity=signer_slot_identity,
        slot_epoch=signer_slot_epoch,
        expected_slot_digest=accepted_slot_digest,
        expected_status="ACCEPTED_IN_PROGRESS",
        successor_status=outcome_body["outcome_status"],
        logical_instant=outcome_body["completion_logical_instant"],
        detail="signer outcome",
    )
    persisted_completion_logical_instant = outcome_body[
        "completion_logical_instant"
    ]
    if context.completion_logical_instant != persisted_completion_logical_instant:
        _fail("RETRY_TUPLE_MISMATCH", "completion_logical_instant")

    outcome_read_back_body = {
        "signer_outcome_identity": outcome_address.identity,
        "signer_outcome_digest": outcome_address.digest,
        "signer_invocation_receipt_identity": receipt_address.identity,
        "signer_invocation_receipt_digest": receipt_address.digest,
        "signer_operation_slot_identity": signer_slot_identity,
        "signer_operation_slot_epoch": signer_slot_epoch,
        "invocation_sequence": 1,
        "signer_outcome_status": outcome_body["outcome_status"],
        "signature_digest": outcome_body["signature_digest"],
        "completion_logical_instant": persisted_completion_logical_instant,
        "terminal_signer_slot_digest": outcome.read_back.slot_digest,
    }
    outcome_read_back_address, outcome_read_back_bytes = _subcontract(
        "SIGNER_OUTCOME_READ_BACK_V1", outcome_read_back_body
    )
    outcome_read_back = store.write_subcontract(
        outcome_read_back_address, outcome_read_back_bytes
    )

    (
        terminal_status,
        authentication_result,
        terminal_signature,
        signature_verification_result,
        conflict_status,
    ) = _terminal_values(outcome_body["outcome_status"], outcome_body["signature"])
    terminal_body = {
        "authentication_operation_identity": operation_address.identity,
        "authentication_operation_digest": operation_address.digest,
        "authentication_claim_cas_identity": claim_address.identity,
        "authentication_claim_cas_digest": claim_address.digest,
        "signer_outcome_read_back_identity": outcome_read_back_address.identity,
        "signer_outcome_read_back_digest": outcome_read_back_address.digest,
        "predecessor_authentication_slot_status": "AUTHENTICATING",
        "terminal_authentication_slot_status": terminal_status,
        "authentication_result": authentication_result,
        "signature": terminal_signature,
        "signature_verification_result": signature_verification_result,
        "one_use_non_equivocation_proof_identity": (
            context.one_use_non_equivocation_proof_identity
        ),
        "one_use_non_equivocation_proof_digest": (
            context.one_use_non_equivocation_proof_digest
        ),
        "conflict_status": conflict_status,
        "capacity_permanently_exhausted": True,
        "completion_logical_instant": persisted_completion_logical_instant,
        "producing_owner": owner,
        "human_authentication_slot_identity": capacity.human_authentication_slot_identity,
        "human_authentication_epoch": capacity.human_authentication_epoch,
        "predecessor_authentication_slot_digest": claim_slot_digest,
    }
    terminal_address, terminal_bytes = _subcontract(
        "AUTHENTICATION_TERMINAL_CAS_V1", terminal_body
    )
    terminal = store.compare_and_swap_subcontract(
        owner=owner,
        slot_identity=capacity.human_authentication_slot_identity,
        slot_epoch=capacity.human_authentication_epoch,
        expected_slot_digest=claim_slot_digest,
        expected_status="AUTHENTICATING",
        successor_status=terminal_status,
        address=terminal_address,
        canonical_bytes=terminal_bytes,
        logical_instant=persisted_completion_logical_instant,
    )

    terminal_address, terminal_body = _resolve_authoritative_cas(
        store,
        subcontract_kind="AUTHENTICATION_TERMINAL_CAS_V1",
        local_address=terminal_address,
        local_canonical_bytes=terminal_bytes,
        result=terminal,
        owner=owner,
        slot_identity=capacity.human_authentication_slot_identity,
        slot_epoch=capacity.human_authentication_epoch,
        expected_slot_digest=claim_slot_digest,
        expected_status="AUTHENTICATING",
        successor_status=terminal_status,
        logical_instant=persisted_completion_logical_instant,
        detail="authentication terminal",
    )
    terminal_status = terminal_body["terminal_authentication_slot_status"]
    authentication_result = terminal_body["authentication_result"]
    terminal_signature = terminal_body["signature"]
    signature_verification_result = terminal_body[
        "signature_verification_result"
    ]
    conflict_status = terminal_body["conflict_status"]

    authoritative_body = {
        "authentication_terminal_cas_identity": terminal_address.identity,
        "authentication_terminal_cas_digest": terminal_address.digest,
        "human_authentication_slot_identity": capacity.human_authentication_slot_identity,
        "human_authentication_epoch": capacity.human_authentication_epoch,
        "authentication_sequence": 1,
        "human_founder_capacity_identity": capacity.artifact_identity,
        "human_founder_capacity_digest": capacity.artifact_digest,
        "authentication_operation_identity": operation_address.identity,
        "authentication_operation_digest": operation_address.digest,
        "terminal_authentication_slot_status": terminal_status,
        "authentication_result": authentication_result,
        "signature_digest": outcome_body["signature_digest"],
        "completion_logical_instant": persisted_completion_logical_instant,
        "read_back_authentication_slot_digest": terminal.read_back.slot_digest,
    }
    authoritative_address, authoritative_bytes = _subcontract(
        "AUTHENTICATION_AUTHORITATIVE_READ_BACK_V1", authoritative_body
    )
    authoritative_read_back = store.write_subcontract(
        authoritative_address, authoritative_bytes
    )

    result_values = {
        "external_premise_identity": capacity.external_premise_identity,
        "external_premise_digest": capacity.external_premise_digest,
        "human_founder_capacity_identity": capacity.artifact_identity,
        "human_founder_capacity_digest": capacity.artifact_digest,
        "human_actor_identity": actor,
        "human_authentication_slot_identity": capacity.human_authentication_slot_identity,
        "human_authentication_epoch": capacity.human_authentication_epoch,
        "authentication_sequence": 1,
        "authentication_operation_identity": operation_address.identity,
        "authentication_operation_digest": operation_address.digest,
        "authentication_commitment_identity": commitment_pair[0],
        "authentication_commitment_digest": commitment_pair[1],
        "authenticated_message_representation": "EXACT_UTF8_CJ1_P_AUTH_V2_BYTES",
        "authenticated_message_digest": commitment_pair[1],
        "signature_scheme": "ED25519_RFC8032_PURE",
        "signature_key_identity": expected_key_identity,
        "signature": outcome_body["signature"],
        "authentication_result": authentication_result,
        "predecessor_authentication_slot_status": "OPEN",
        "claimed_authentication_slot_status": "AUTHENTICATING",
        "terminal_authentication_slot_status": terminal_status,
        "authentication_claim_cas_identity": claim_address.identity,
        "authentication_claim_cas_digest": claim_address.digest,
        "signer_operation_slot_identity": signer_slot_identity,
        "signer_operation_slot_epoch": signer_slot_epoch,
        "signer_invocation_intent_identity": intent_address.identity,
        "signer_invocation_intent_digest": intent_address.digest,
        "signer_acceptance_cas_identity": acceptance_address.identity,
        "signer_acceptance_cas_digest": acceptance_address.digest,
        "signer_invocation_receipt_identity": receipt_address.identity,
        "signer_invocation_receipt_digest": receipt_address.digest,
        "signer_outcome_identity": outcome_address.identity,
        "signer_outcome_digest": outcome_address.digest,
        "signer_outcome_read_back_identity": outcome_read_back_address.identity,
        "signer_outcome_read_back_digest": outcome_read_back_address.digest,
        "signer_outcome_status": outcome_body["outcome_status"],
        "one_use_non_equivocation_proof_identity": (
            context.one_use_non_equivocation_proof_identity
        ),
        "one_use_non_equivocation_proof_digest": (
            context.one_use_non_equivocation_proof_digest
        ),
        "authentication_terminal_cas_identity": terminal_address.identity,
        "authentication_terminal_cas_digest": terminal_address.digest,
        "authoritative_read_back_identity": authoritative_address.identity,
        "authoritative_read_back_digest": authoritative_address.digest,
        "read_back_authentication_slot_digest": terminal.read_back.slot_digest,
        "signature_verification_result": signature_verification_result,
        "conflict_status": conflict_status,
        "retry_permitted": False,
        "second_authentication_permitted": False,
        "capacity_permanently_exhausted": True,
        "completion_logical_instant": persisted_completion_logical_instant,
        "terminal": True,
    }
    result = _build_result(owner=owner, values=result_values)
    try:
        validate_artifact(result, owner_bindings=owner_bindings)
    except Exception as exc:
        _fail("RESULTV2_CONSTRUCTION_MISMATCH", str(exc))
    result_write = store.write_immutable(result, owner_bindings=owner_bindings)
    return FixtureAuthenticationExecution(
        result=result,
        result_write=result_write,
        operation=operation,
        claim=claim,
        intent=intent,
        acceptance=acceptance,
        receipt=receipt,
        outcome=outcome,
        outcome_read_back=outcome_read_back,
        terminal=terminal,
        authoritative_read_back=authoritative_read_back,
    )


__all__ = [
    "CandidateAuthenticationError",
    "FixtureAuthenticationContext",
    "FixtureAuthenticationExecution",
    "authenticate_fixture_candidate_h",
    "fixture_ed25519_public_key",
    "fixture_ed25519_verify",
]
