"""OS/process-isolated Profile A authority boundary.

Production authority is available only when a root-owned immutable binding at
the fixed production path identifies distinct canonical-entry and authority
OS principals.  The authority process owns the protected owner-state root and
authenticates its IPC peer with kernel-provided Unix credentials.

The explicit test boundary is zero-authority.  It may exercise the same wire
protocol and validation path, but it can never emit the production ALLOW
decision value and is rejected by the production client.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import socket
import stat
import struct
from typing import Any, Mapping

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import (
    canonical_serialize,
    load_json,
    replay_hash,
    verify_replay_hash,
    write_json_immutable,
)


PROFILE_A_AUTHORITY_BOUNDARY_VERSION = (
    "DEDICATED_OS_PROCESS_ISOLATION_BOUNDARY_V1"
)
PROFILE_A_AUTHORITY_PRINCIPAL_IDENTITY = (
    "HUMAN_CONSTITUTIONAL_AUTHORITY_DESIGNATED_OS_AUTHORITY_PRINCIPAL_V1"
)
PROFILE_A_PRODUCTION_MODE = "PRODUCTION_AUTHORITY"
PROFILE_A_ZERO_AUTHORITY_TEST_MODE = "ZERO_AUTHORITY_TEST"
PROFILE_A_TEST_PRINCIPAL_IDENTITY = (
    "PROFILE_A_ZERO_AUTHORITY_TEST_PRINCIPAL_V1"
)
PROFILE_A_TEST_ONLY_ALLOW = (
    "TEST_ONLY_ALLOW_BOUNDED_EVIDENCE_REDUCTION__ZERO_AUTHORITY"
)
PROFILE_A_PROCESS_INTERNAL_ALLOW_CANDIDATE = (
    "PROFILE_A_PROCESS_INTERNAL_ALLOW_CANDIDATE__NO_CALLER_AUTHORITY_EFFECT"
)
PROFILE_A_PRODUCTION_ORIGIN_VERIFIED = (
    "VERIFIED_PROFILE_A_PRODUCTION_AUTHORITY_PROCESS_ORIGIN"
)
PROFILE_A_TEST_ORIGIN_VERIFIED = (
    "VERIFIED_PROFILE_A_ZERO_AUTHORITY_TEST_ORIGIN"
)

PROFILE_A_ISSUE_OWNER_STATE = "ISSUE_PROFILE_A_OWNER_STATE"
PROFILE_A_EVALUATE_DECISION = "EVALUATE_BOUNDED_EVIDENCE_REDUCTION"
PROFILE_A_VERIFY_DECISION_ORIGIN = "VERIFY_PROFILE_A_DECISION_ORIGIN"
PROFILE_A_IPC_OPERATIONS = frozenset(
    {
        PROFILE_A_ISSUE_OWNER_STATE,
        PROFILE_A_EVALUATE_DECISION,
        PROFILE_A_VERIFY_DECISION_ORIGIN,
    }
)

PROFILE_A_PRODUCTION_BINDING_PATH = Path(
    "/etc/sapianta/profile_a_authority_boundary_v1.json"
)
PROFILE_A_PRODUCTION_SOCKET_PATH = Path(
    "/run/sapianta/profile_a_authority_boundary_v1.sock"
)
PROFILE_A_AUTHORITY_RECEIPT_DIRECTORY = (
    "profile_a_authority_ipc_receipts_v1"
)
PROFILE_A_DECISION_ORIGIN_DIRECTORY = (
    "profile_a_decision_origin_receipts_v1"
)
PROFILE_A_DECISION_CONSUMPTION_DIRECTORY = (
    "profile_a_decision_origin_consumptions_v1"
)
PROFILE_A_ACTUAL_MANIFEST_CONSUMER = "ACTUAL_MANIFEST_CREATION"
PROFILE_A_RUNTIMELEDGER_CONSUMER = "RUNTIMELEDGER_ACTUAL_EFFECT_RECORDING"
PROFILE_A_TEST_VERIFICATION_CONSUMER = "ZERO_AUTHORITY_TEST_VERIFICATION"
PROFILE_A_DECISION_CONSUMERS = frozenset(
    {
        PROFILE_A_ACTUAL_MANIFEST_CONSUMER,
        PROFILE_A_RUNTIMELEDGER_CONSUMER,
        PROFILE_A_TEST_VERIFICATION_CONSUMER,
    }
)

_BINDING_FIELDS = frozenset(
    {
        "binding_version",
        "boundary_mechanism",
        "principal_identity",
        "authority_uid",
        "canonical_entry_uid",
        "ipc_gid",
        "che_runtime_scope_identity",
        "owner_state_store_root",
        "owner_state_identity",
        "socket_path",
        "binding_hash",
    }
)
_REQUEST_FIELDS = frozenset(
    {
        "boundary_version",
        "operation",
        "request_identity",
        "payload",
        "request_hash",
    }
)
_RESPONSE_FIELDS = frozenset(
    {
        "boundary_version",
        "boundary_mode",
        "principal_identity",
        "request_identity",
        "request_hash",
        "status",
        "failure_code",
        "result",
        "response_hash",
    }
)
_DECISION_ORIGIN_FIELDS = frozenset(
    {
        "origin_version",
        "boundary_version",
        "boundary_mode",
        "authority_process_identity",
        "authority_uid",
        "binding_hash",
        "request_identity",
        "request_hash",
        "correlation_identity",
        "owner_state_identity",
        "owner_state_commitment",
        "policy_revision",
        "subject",
        "scope",
        "immutable_input_identities",
        "lifecycle_state",
        "decision_identity",
        "decision_hash",
        "receipt_identity",
        "receipt_hash",
    }
)
_DECISION_RECORD_FIELDS = frozenset(
    {
        "record_version",
        "origin_evidence",
        "decision",
        "decision_inputs",
        "record_hash",
    }
)
_MAX_FRAME_BYTES = 8 * 1024 * 1024
_FRAME_HEADER = struct.Struct("!I")
_PEER_CREDENTIALS = struct.Struct("3i")


@dataclass(frozen=True, slots=True)
class _ProfileAAuthorityProcessContextV1:
    boundary_mode: str
    principal_identity: str
    authority_uid: int
    canonical_entry_uid: int
    ipc_gid: int
    che_runtime_scope_identity: str
    owner_state_store_root: str
    owner_state_identity: str
    socket_path: str
    binding_hash: str
    process_id: int


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise FailClosedRuntimeError(f"Profile A authority {label} is invalid")
    return value


def _integer(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise FailClosedRuntimeError(f"Profile A authority {label} is invalid")
    return value


def _plain(value: Any) -> Any:
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return _plain(value.to_dict())
    if isinstance(value, Mapping):
        return {key: _plain(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    canonical_serialize(value)
    return value


def _with_hash(value: Mapping[str, Any], field: str) -> dict[str, Any]:
    result = _plain(value)
    result.pop(field, None)
    result[field] = replay_hash(result)
    return result


def _validate_hash_bound(value: Mapping[str, Any], field: str) -> dict[str, Any]:
    result = _plain(value)
    verify_replay_hash(result, field)
    return result


def _secure_regular_file(path: Path, *, required_owner_uid: int) -> os.stat_result:
    try:
        details = path.lstat()
    except OSError as exc:
        raise FailClosedRuntimeError(
            "Profile A authority production binding is unavailable"
        ) from exc
    if not stat.S_ISREG(details.st_mode) or path.is_symlink():
        raise FailClosedRuntimeError(
            "Profile A authority production binding is not a regular file"
        )
    if details.st_uid != required_owner_uid:
        raise FailClosedRuntimeError(
            "Profile A authority production binding owner is invalid"
        )
    if details.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
        raise FailClosedRuntimeError(
            "Profile A authority production binding is caller-writable"
        )
    return details


def _secure_directory(
    path: Path,
    *,
    required_owner_uid: int,
    label: str,
) -> os.stat_result:
    try:
        details = path.lstat()
    except OSError as exc:
        raise FailClosedRuntimeError(
            f"Profile A authority {label} is unavailable"
        ) from exc
    if not stat.S_ISDIR(details.st_mode) or path.is_symlink():
        raise FailClosedRuntimeError(
            f"Profile A authority {label} is not a directory"
        )
    if details.st_uid != required_owner_uid:
        raise FailClosedRuntimeError(
            f"Profile A authority {label} owner is invalid"
        )
    if details.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
        raise FailClosedRuntimeError(
            f"Profile A authority {label} is caller-writable"
        )
    return details


def _load_profile_a_production_binding_v1() -> dict[str, Any]:
    _secure_regular_file(
        PROFILE_A_PRODUCTION_BINDING_PATH,
        required_owner_uid=0,
    )
    binding = load_json(PROFILE_A_PRODUCTION_BINDING_PATH)
    if set(binding) != _BINDING_FIELDS:
        raise FailClosedRuntimeError(
            "Profile A authority production binding fields are invalid"
        )
    binding = _validate_hash_bound(binding, "binding_hash")
    if (
        binding["binding_version"] != PROFILE_A_AUTHORITY_BOUNDARY_VERSION
        or binding["boundary_mechanism"]
        != PROFILE_A_AUTHORITY_BOUNDARY_VERSION
        or binding["principal_identity"]
        != PROFILE_A_AUTHORITY_PRINCIPAL_IDENTITY
    ):
        raise FailClosedRuntimeError(
            "Profile A authority production binding identity is invalid"
        )
    authority_uid = _integer(binding["authority_uid"], "authority UID")
    canonical_entry_uid = _integer(
        binding["canonical_entry_uid"], "canonical-entry UID"
    )
    _integer(binding["ipc_gid"], "IPC GID")
    if authority_uid == 0 or authority_uid == canonical_entry_uid:
        raise FailClosedRuntimeError(
            "Profile A authority requires distinct non-root OS principals"
        )
    for field_name in (
        "che_runtime_scope_identity",
        "owner_state_store_root",
        "owner_state_identity",
        "socket_path",
    ):
        _text(binding[field_name], field_name.replace("_", " "))
    if Path(binding["socket_path"]) != PROFILE_A_PRODUCTION_SOCKET_PATH:
        raise FailClosedRuntimeError(
            "Profile A authority production socket path is not fixed"
        )
    for field_name in ("che_runtime_scope_identity", "owner_state_store_root"):
        if not Path(binding[field_name]).is_absolute():
            raise FailClosedRuntimeError(
                "Profile A authority production storage path is not absolute"
            )
    return binding


def _establish_profile_a_production_authority_context_v1(
) -> _ProfileAAuthorityProcessContextV1:
    binding = _load_profile_a_production_binding_v1()
    effective_uid = os.geteuid()
    if effective_uid != binding["authority_uid"]:
        raise FailClosedRuntimeError(
            "Profile A authority process principal is not authenticated"
        )
    if binding["ipc_gid"] not in {os.getegid(), *os.getgroups()}:
        raise FailClosedRuntimeError(
            "Profile A authority process IPC group is not authenticated"
        )
    _secure_directory(
        Path(binding["owner_state_store_root"]),
        required_owner_uid=effective_uid,
        label="protected owner-state root",
    )
    return _ProfileAAuthorityProcessContextV1(
        boundary_mode=PROFILE_A_PRODUCTION_MODE,
        principal_identity=PROFILE_A_AUTHORITY_PRINCIPAL_IDENTITY,
        authority_uid=effective_uid,
        canonical_entry_uid=binding["canonical_entry_uid"],
        ipc_gid=binding["ipc_gid"],
        che_runtime_scope_identity=binding["che_runtime_scope_identity"],
        owner_state_store_root=binding["owner_state_store_root"],
        owner_state_identity=binding["owner_state_identity"],
        socket_path=binding["socket_path"],
        binding_hash=binding["binding_hash"],
        process_id=os.getpid(),
    )


def create_profile_a_zero_authority_test_context_v1(
    *,
    che_runtime_scope_identity: str | Path,
    owner_state_identity: str,
    socket_path: str | Path | None = None,
) -> _ProfileAAuthorityProcessContextV1:
    """Create an explicitly non-production test context.

    This context is intentionally caller-constructible.  Its mode is preserved
    through every resolver, gate and IPC response and can never produce the
    production ALLOW value.
    """

    che_root = Path(che_runtime_scope_identity).resolve()
    che_root.mkdir(parents=True, exist_ok=True)
    protected_root = che_root / "profile_a_zero_authority_test_owner_state_v1"
    protected_root.mkdir(mode=0o700, parents=True, exist_ok=True)
    endpoint = (
        Path(socket_path).resolve()
        if socket_path is not None
        else protected_root / "profile_a_zero_authority_test.sock"
    )
    if protected_root not in endpoint.parents:
        raise FailClosedRuntimeError(
            "Profile A test endpoint is outside its zero-authority namespace"
        )
    binding = {
        "binding_version": PROFILE_A_AUTHORITY_BOUNDARY_VERSION,
        "boundary_mode": PROFILE_A_ZERO_AUTHORITY_TEST_MODE,
        "principal_identity": PROFILE_A_TEST_PRINCIPAL_IDENTITY,
        "effective_uid": os.geteuid(),
        "che_runtime_scope_identity": che_root.as_posix(),
        "owner_state_store_root": protected_root.as_posix(),
        "owner_state_identity": _text(
            owner_state_identity, "test owner-state identity"
        ),
        "socket_path": endpoint.as_posix(),
    }
    binding_hash = replay_hash(binding)
    return _ProfileAAuthorityProcessContextV1(
        boundary_mode=PROFILE_A_ZERO_AUTHORITY_TEST_MODE,
        principal_identity=PROFILE_A_TEST_PRINCIPAL_IDENTITY,
        authority_uid=os.geteuid(),
        canonical_entry_uid=os.geteuid(),
        ipc_gid=os.getegid(),
        che_runtime_scope_identity=che_root.as_posix(),
        owner_state_store_root=protected_root.as_posix(),
        owner_state_identity=binding["owner_state_identity"],
        socket_path=endpoint.as_posix(),
        binding_hash=binding_hash,
        process_id=os.getpid(),
    )


def validate_profile_a_authority_process_context_v1(
    value: Any,
    *,
    allow_zero_authority_test: bool,
) -> _ProfileAAuthorityProcessContextV1:
    if type(value) is not _ProfileAAuthorityProcessContextV1:
        raise FailClosedRuntimeError(
            "Profile A authority requires an OS process context"
        )
    if value.process_id != os.getpid() or value.authority_uid != os.geteuid():
        raise FailClosedRuntimeError(
            "Profile A authority process context crossed a process boundary"
        )
    if value.boundary_mode == PROFILE_A_PRODUCTION_MODE:
        current = _establish_profile_a_production_authority_context_v1()
        if value != current:
            raise FailClosedRuntimeError(
                "Profile A production authority context is stale or substituted"
            )
        return value
    if (
        allow_zero_authority_test
        and value.boundary_mode == PROFILE_A_ZERO_AUTHORITY_TEST_MODE
        and value.principal_identity == PROFILE_A_TEST_PRINCIPAL_IDENTITY
        and value.authority_uid == value.canonical_entry_uid
    ):
        protected_root = Path(value.owner_state_store_root)
        if not protected_root.is_dir() or Path(
            value.che_runtime_scope_identity
        ) not in protected_root.parents:
            raise FailClosedRuntimeError(
                "Profile A zero-authority test context is invalid"
            )
        return value
    raise FailClosedRuntimeError(
        "Profile A authority context is not production-authenticated"
    )


def profile_a_context_is_production_v1(value: Any) -> bool:
    try:
        validate_profile_a_authority_process_context_v1(
            value, allow_zero_authority_test=False
        )
    except FailClosedRuntimeError:
        return False
    return True


def _peer_credentials(connection: socket.socket) -> tuple[int, int, int]:
    if not hasattr(socket, "SO_PEERCRED"):
        raise FailClosedRuntimeError(
            "Profile A authority requires OS-provided Unix peer credentials"
        )
    try:
        packed = connection.getsockopt(
            socket.SOL_SOCKET,
            socket.SO_PEERCRED,
            _PEER_CREDENTIALS.size,
        )
    except OSError as exc:
        raise FailClosedRuntimeError(
            "Profile A authority peer credentials are unavailable"
        ) from exc
    return _PEER_CREDENTIALS.unpack(packed)


def _authenticate_peer_uid(connection: socket.socket, expected_uid: int) -> None:
    _, peer_uid, _ = _peer_credentials(connection)
    if peer_uid != expected_uid:
        raise FailClosedRuntimeError(
            "Profile A authority IPC OS peer is not authenticated"
        )


def _recv_exact(connection: socket.socket, size: int) -> bytes:
    chunks: list[bytes] = []
    remaining = size
    while remaining:
        chunk = connection.recv(remaining)
        if not chunk:
            raise FailClosedRuntimeError(
                "Profile A authority IPC frame is incomplete"
            )
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def _recv_frame(connection: socket.socket) -> dict[str, Any]:
    raw_size = _recv_exact(connection, _FRAME_HEADER.size)
    (size,) = _FRAME_HEADER.unpack(raw_size)
    if size < 2 or size > _MAX_FRAME_BYTES:
        raise FailClosedRuntimeError(
            "Profile A authority IPC frame size is invalid"
        )
    raw = _recv_exact(connection, size)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FailClosedRuntimeError(
            "Profile A authority IPC frame is malformed"
        ) from exc
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(
            "Profile A authority IPC frame is not an object"
        )
    return value


def _send_frame(connection: socket.socket, value: Mapping[str, Any]) -> None:
    raw = canonical_serialize(_plain(value)).encode("utf-8")
    if len(raw) > _MAX_FRAME_BYTES:
        raise FailClosedRuntimeError(
            "Profile A authority IPC response is too large"
        )
    connection.sendall(_FRAME_HEADER.pack(len(raw)) + raw)


def _request(
    *, operation: str, request_identity: str, payload: Mapping[str, Any]
) -> dict[str, Any]:
    if operation not in PROFILE_A_IPC_OPERATIONS:
        raise FailClosedRuntimeError(
            "Profile A authority IPC operation is not authorized"
        )
    value = {
        "boundary_version": PROFILE_A_AUTHORITY_BOUNDARY_VERSION,
        "operation": operation,
        "request_identity": _text(request_identity, "request identity"),
        "payload": _plain(payload),
        "request_hash": "",
    }
    return _with_hash(value, "request_hash")


def _validate_request(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != _REQUEST_FIELDS:
        raise FailClosedRuntimeError(
            "Profile A authority IPC request fields are invalid"
        )
    request = _validate_hash_bound(value, "request_hash")
    if (
        request["boundary_version"] != PROFILE_A_AUTHORITY_BOUNDARY_VERSION
        or request["operation"] not in PROFILE_A_IPC_OPERATIONS
        or not isinstance(request["payload"], dict)
    ):
        raise FailClosedRuntimeError(
            "Profile A authority IPC request identity is invalid"
        )
    _text(request["request_identity"], "request identity")
    return request


def _response(
    *,
    context: _ProfileAAuthorityProcessContextV1,
    request_identity: str,
    request_hash: str,
    status: str,
    failure_code: str,
    result: Any,
) -> dict[str, Any]:
    value = {
        "boundary_version": PROFILE_A_AUTHORITY_BOUNDARY_VERSION,
        "boundary_mode": context.boundary_mode,
        "principal_identity": context.principal_identity,
        "request_identity": request_identity,
        "request_hash": request_hash,
        "status": status,
        "failure_code": failure_code,
        "result": _plain(result),
        "response_hash": "",
    }
    return _with_hash(value, "response_hash")


def _validate_response(
    value: Any,
    *,
    expected_request: Mapping[str, Any],
    expected_mode: str,
) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != _RESPONSE_FIELDS:
        raise FailClosedRuntimeError(
            "Profile A authority IPC response fields are invalid"
        )
    response = _validate_hash_bound(value, "response_hash")
    if (
        response["boundary_version"] != PROFILE_A_AUTHORITY_BOUNDARY_VERSION
        or response["boundary_mode"] != expected_mode
        or response["request_identity"] != expected_request["request_identity"]
        or response["request_hash"] != expected_request["request_hash"]
    ):
        raise FailClosedRuntimeError(
            "Profile A authority IPC response binding is invalid"
        )
    expected_principal = (
        PROFILE_A_AUTHORITY_PRINCIPAL_IDENTITY
        if expected_mode == PROFILE_A_PRODUCTION_MODE
        else PROFILE_A_TEST_PRINCIPAL_IDENTITY
    )
    if response["principal_identity"] != expected_principal:
        raise FailClosedRuntimeError(
            "Profile A authority IPC response principal is invalid"
        )
    return response


def _receipt_path(
    context: _ProfileAAuthorityProcessContextV1, request_identity: str
) -> Path:
    digest = replay_hash(
        {"request_identity": request_identity}
    ).removeprefix("sha256:")
    return (
        Path(context.owner_state_store_root)
        / PROFILE_A_AUTHORITY_RECEIPT_DIRECTORY
        / f"request-{digest}.json"
    )


def _decision_origin_path(
    context: _ProfileAAuthorityProcessContextV1, receipt_identity: str
) -> Path:
    digest = replay_hash(
        {"receipt_identity": receipt_identity}
    ).removeprefix("sha256:")
    return (
        Path(context.owner_state_store_root)
        / PROFILE_A_DECISION_ORIGIN_DIRECTORY
        / f"decision-{digest}.json"
    )


def _decision_consumption_path(
    context: _ProfileAAuthorityProcessContextV1,
    receipt_identity: str,
    consumer_kind: str,
) -> Path:
    digest = replay_hash(
        {
            "receipt_identity": receipt_identity,
            "consumer_kind": consumer_kind,
        }
    ).removeprefix("sha256:")
    return (
        Path(context.owner_state_store_root)
        / PROFILE_A_DECISION_CONSUMPTION_DIRECTORY
        / f"consumption-{digest}.json"
    )


def _decision_origin_bindings(
    *,
    context: _ProfileAAuthorityProcessContextV1,
    request: Mapping[str, Any],
    decision: Mapping[str, Any],
    decision_inputs: Mapping[str, Any],
) -> dict[str, Any]:
    required_inputs = {
        "policy",
        "obligations",
        "permanent_trail",
        "planned_manifest",
        "authorization",
        "cohort",
        "authority_provenance_reference",
        "authority_evidence",
    }
    if set(decision_inputs) != required_inputs:
        raise FailClosedRuntimeError(
            "Profile A decision-origin inputs are incomplete"
        )
    policy = decision_inputs["policy"]
    planned = decision_inputs["planned_manifest"]
    authorization = decision_inputs["authorization"]
    permanent_trail = decision_inputs["permanent_trail"]
    if not all(
        isinstance(value, Mapping)
        for value in (policy, planned, authorization, permanent_trail)
    ):
        raise FailClosedRuntimeError(
            "Profile A decision-origin subject is unresolved"
        )
    input_identities = decision.get("input_hashes")
    if not isinstance(input_identities, Mapping):
        raise FailClosedRuntimeError(
            "Profile A decision-origin input identities are unresolved"
        )
    subject = {
        "domain_id": _text(policy.get("domain_id"), "decision domain"),
        "policy_id": _text(policy.get("policy_id"), "decision policy"),
        "authority_id": _text(
            policy.get("authority_id"), "decision authority"
        ),
        "subject_reference": _text(
            permanent_trail.get("subject_reference"),
            "decision subject reference",
        ),
    }
    scope = {
        "evidence_class": _text(
            planned.get("evidence_class"), "decision evidence class"
        ),
        "reduction_type": _text(
            planned.get("reduction_type"), "decision reduction type"
        ),
        "planned_manifest_hash": _text(
            planned.get("replay_hash"), "planned manifest hash"
        ),
        "authorization_hash": _text(
            authorization.get("replay_hash"), "authorization hash"
        ),
    }
    return {
        "correlation_identity": _text(
            policy.get("authority_evidence_reference"),
            "decision correlation identity",
        ),
        "owner_state_identity": context.owner_state_identity,
        "owner_state_commitment": _text(
            input_identities.get("authority_provenance"),
            "owner-state commitment",
        ),
        "policy_revision": _text(
            policy.get("policy_version"), "policy revision"
        ),
        "subject": subject,
        "scope": scope,
        "immutable_input_identities": _plain(input_identities),
        "lifecycle_state": (
            "CURRENT__NOT_EXPIRED__NOT_SUPERSEDED__NOT_REVOKED__LINEAGE_RESOLVED"
        ),
        "decision_identity": _text(
            decision.get("decision_id"), "decision identity"
        ),
        "decision_hash": _text(
            decision.get("replay_hash"), "decision hash"
        ),
        "request_identity": request["request_identity"],
        "request_hash": request["request_hash"],
    }


def _materialize_process_decision(
    context: _ProfileAAuthorityProcessContextV1,
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    value = _validate_hash_bound(decision, "replay_hash")
    current = value.get("decision")
    if context.boundary_mode == PROFILE_A_PRODUCTION_MODE:
        if current == PROFILE_A_PROCESS_INTERNAL_ALLOW_CANDIDATE:
            basis = dict(value)
            basis.pop("replay_hash")
            basis["decision"] = "ALLOW_BOUNDED_EVIDENCE_REDUCTION"
            return _with_hash(basis, "replay_hash")
        if current == PROFILE_A_TEST_ONLY_ALLOW:
            raise FailClosedRuntimeError(
                "Profile A production process rejected test classification"
            )
        return value
    if current == PROFILE_A_PROCESS_INTERNAL_ALLOW_CANDIDATE or current == (
        "ALLOW_BOUNDED_EVIDENCE_REDUCTION"
    ):
        raise FailClosedRuntimeError(
            "Profile A zero-authority process rejected production classification"
        )
    return value


def _build_decision_origin_evidence(
    *,
    context: _ProfileAAuthorityProcessContextV1,
    request: Mapping[str, Any],
    decision: Mapping[str, Any],
    decision_inputs: Mapping[str, Any],
) -> dict[str, Any]:
    bindings = _decision_origin_bindings(
        context=context,
        request=request,
        decision=decision,
        decision_inputs=decision_inputs,
    )
    seed = {
        "origin_version": "PROFILE_A_OS_BOUND_DECISION_ORIGIN_V1",
        "boundary_version": PROFILE_A_AUTHORITY_BOUNDARY_VERSION,
        "boundary_mode": context.boundary_mode,
        "authority_process_identity": context.principal_identity,
        "authority_uid": context.authority_uid,
        "binding_hash": context.binding_hash,
        **bindings,
    }
    receipt_digest = replay_hash(seed).removeprefix("sha256:")
    return _with_hash(
        {
            **seed,
            "receipt_identity": (
                f"PROFILE-A-DECISION-ORIGIN-{receipt_digest[:32]}"
            ),
        },
        "receipt_hash",
    )


def _validate_decision_origin_evidence(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != _DECISION_ORIGIN_FIELDS:
        raise FailClosedRuntimeError(
            "Profile A decision-origin evidence fields are invalid"
        )
    evidence = _validate_hash_bound(value, "receipt_hash")
    if (
        evidence["origin_version"]
        != "PROFILE_A_OS_BOUND_DECISION_ORIGIN_V1"
        or evidence["boundary_version"]
        != PROFILE_A_AUTHORITY_BOUNDARY_VERSION
    ):
        raise FailClosedRuntimeError(
            "Profile A decision-origin evidence identity is invalid"
        )
    for field_name in (
        "authority_process_identity",
        "binding_hash",
        "request_identity",
        "request_hash",
        "correlation_identity",
        "owner_state_identity",
        "owner_state_commitment",
        "policy_revision",
        "lifecycle_state",
        "decision_identity",
        "decision_hash",
        "receipt_identity",
    ):
        _text(evidence[field_name], field_name.replace("_", " "))
    _integer(evidence["authority_uid"], "origin authority UID")
    if not all(
        isinstance(evidence[field_name], dict)
        for field_name in ("subject", "scope", "immutable_input_identities")
    ):
        raise FailClosedRuntimeError(
            "Profile A decision-origin bound content is invalid"
        )
    return evidence


def _store_decision_origin_record(
    *,
    context: _ProfileAAuthorityProcessContextV1,
    request: Mapping[str, Any],
    decision: Mapping[str, Any],
    decision_inputs: Mapping[str, Any],
) -> dict[str, Any]:
    evidence = _build_decision_origin_evidence(
        context=context,
        request=request,
        decision=decision,
        decision_inputs=decision_inputs,
    )
    path = _decision_origin_path(context, evidence["receipt_identity"])
    record = _with_hash(
        {
            "record_version": "PROFILE_A_PROTECTED_DECISION_RECORD_V1",
            "origin_evidence": evidence,
            "decision": _plain(decision),
            "decision_inputs": _plain(decision_inputs),
        },
        "record_hash",
    )
    write_json_immutable(path, record)
    return evidence


def _load_decision_origin_record(
    context: _ProfileAAuthorityProcessContextV1,
    origin_evidence: Mapping[str, Any],
) -> dict[str, Any]:
    evidence = _validate_decision_origin_evidence(origin_evidence)
    path = _decision_origin_path(context, evidence["receipt_identity"])
    try:
        record = load_json(path)
    except (FailClosedRuntimeError, OSError, ValueError) as exc:
        raise FailClosedRuntimeError(
            "Profile A protected decision-origin record is unavailable"
        ) from exc
    if set(record) != _DECISION_RECORD_FIELDS:
        raise FailClosedRuntimeError(
            "Profile A protected decision-origin record fields are invalid"
        )
    record = _validate_hash_bound(record, "record_hash")
    if (
        record["record_version"]
        != "PROFILE_A_PROTECTED_DECISION_RECORD_V1"
        or record["origin_evidence"] != evidence
    ):
        raise FailClosedRuntimeError(
            "Profile A protected decision-origin record binding is invalid"
        )
    return record


def _verify_decision_origin_inside_process(
    *,
    context: _ProfileAAuthorityProcessContextV1,
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    from aigol.runtime.evidence_reduction_gate import (
        _compose_profile_a_bounded_evidence_reduction_gate_inside_authority_process_v1,
    )

    expected = {
        "origin_evidence",
        "decision_hash",
        "planned_manifest_hash",
        "authorization_hash",
        "consumer_kind",
        "effect_identity",
    }
    if set(payload) != expected:
        raise FailClosedRuntimeError(
            "Profile A decision-origin verification fields are invalid"
        )
    record = _load_decision_origin_record(
        context, payload["origin_evidence"]
    )
    evidence = record["origin_evidence"]
    consumer_kind = _text(payload["consumer_kind"], "origin consumer kind")
    effect_identity = _text(payload["effect_identity"], "effect identity")
    if consumer_kind not in PROFILE_A_DECISION_CONSUMERS:
        raise FailClosedRuntimeError(
            "Profile A decision-origin consumer is not authorized"
        )
    if context.boundary_mode == PROFILE_A_PRODUCTION_MODE:
        if consumer_kind == PROFILE_A_TEST_VERIFICATION_CONSUMER:
            raise FailClosedRuntimeError(
                "Profile A production origin rejected a test consumer"
            )
    elif consumer_kind != PROFILE_A_TEST_VERIFICATION_CONSUMER:
        raise FailClosedRuntimeError(
            "Profile A test origin rejected a production consumer"
        )
    if (
        evidence["boundary_mode"] != context.boundary_mode
        or evidence["authority_process_identity"] != context.principal_identity
        or evidence["authority_uid"] != context.authority_uid
        or evidence["binding_hash"] != context.binding_hash
        or evidence["owner_state_identity"] != context.owner_state_identity
        or evidence["decision_hash"] != payload["decision_hash"]
        or evidence["scope"]["planned_manifest_hash"]
        != payload["planned_manifest_hash"]
        or evidence["scope"]["authorization_hash"]
        != payload["authorization_hash"]
    ):
        raise FailClosedRuntimeError(
            "Profile A decision-origin verification binding mismatch"
        )
    gate = (
        _compose_profile_a_bounded_evidence_reduction_gate_inside_authority_process_v1(
            _authority_process_context=context
        )
    )
    recomputed = _materialize_process_decision(
        context, gate.evaluate(**record["decision_inputs"])
    )
    if recomputed != record["decision"]:
        raise FailClosedRuntimeError(
            "Profile A decision origin is stale or no longer current"
        )
    expected_evidence = _build_decision_origin_evidence(
        context=context,
        request={
            "request_identity": evidence["request_identity"],
            "request_hash": evidence["request_hash"],
        },
        decision=recomputed,
        decision_inputs=record["decision_inputs"],
    )
    if expected_evidence != evidence:
        raise FailClosedRuntimeError(
            "Profile A decision-origin evidence was reconstructed or altered"
        )
    if context.boundary_mode == PROFILE_A_PRODUCTION_MODE:
        if recomputed.get("decision") != "ALLOW_BOUNDED_EVIDENCE_REDUCTION":
            raise FailClosedRuntimeError(
                "Profile A production decision origin is not allow-capable"
            )
        status = PROFILE_A_PRODUCTION_ORIGIN_VERIFIED
    else:
        if recomputed.get("decision") != PROFILE_A_TEST_ONLY_ALLOW:
            raise FailClosedRuntimeError(
                "Profile A test decision origin is not zero-authority"
            )
        status = PROFILE_A_TEST_ORIGIN_VERIFIED
    consumption_path = _decision_consumption_path(
        context, evidence["receipt_identity"], consumer_kind
    )
    if consumption_path.exists():
        raise FailClosedRuntimeError(
            "Profile A decision origin was already consumed for this effect"
        )
    consumption = _with_hash(
        {
            "consumption_version": "PROFILE_A_DECISION_CONSUMPTION_V1",
            "boundary_mode": context.boundary_mode,
            "receipt_identity": evidence["receipt_identity"],
            "receipt_hash": evidence["receipt_hash"],
            "decision_hash": evidence["decision_hash"],
            "consumer_kind": consumer_kind,
            "effect_identity": effect_identity,
            "verification_status": status,
        },
        "consumption_hash",
    )
    write_json_immutable(consumption_path, consumption)
    return {
        "verification_status": status,
        "receipt_identity": evidence["receipt_identity"],
        "receipt_hash": evidence["receipt_hash"],
        "decision_hash": evidence["decision_hash"],
        "currentness": evidence["lifecycle_state"],
        "consumer_kind": consumer_kind,
        "effect_identity": effect_identity,
        "consumption_hash": consumption["consumption_hash"],
    }


def _handle_request(
    context: _ProfileAAuthorityProcessContextV1,
    request: Mapping[str, Any],
) -> dict[str, Any]:
    from aigol.runtime.authority_provenance import (
        _persist_profile_a_owner_state_authorization_v1,
    )
    from aigol.runtime.evidence_reduction_gate import (
        _compose_profile_a_bounded_evidence_reduction_gate_inside_authority_process_v1,
    )

    validated_context = validate_profile_a_authority_process_context_v1(
        context, allow_zero_authority_test=True
    )
    request = _validate_request(request)
    receipt_path = _receipt_path(
        validated_context, request["request_identity"]
    )
    if receipt_path.exists():
        receipt = load_json(receipt_path)
        prior_request = receipt.get("request")
        failure = (
            "IPC_REQUEST_REPLAYED_OR_DUPLICATE"
            if isinstance(prior_request, dict)
            and prior_request.get("request_hash") == request["request_hash"]
            else "IPC_REQUEST_IDENTITY_CONFLICT"
        )
        return _response(
            context=validated_context,
            request_identity=request["request_identity"],
            request_hash=request["request_hash"],
            status="DENIED",
            failure_code=failure,
            result=None,
        )

    try:
        if request["operation"] == PROFILE_A_ISSUE_OWNER_STATE:
            expected = {"request", "continuation", "authority_act", "correlation"}
            if set(request["payload"]) != expected:
                raise FailClosedRuntimeError(
                    "Profile A issuance payload fields are invalid"
                )
            path = _persist_profile_a_owner_state_authorization_v1(
                request=request["payload"]["request"],
                continuation=request["payload"]["continuation"],
                authority_act=request["payload"]["authority_act"],
                correlation=request["payload"]["correlation"],
                _authority_process_context=validated_context,
            )
            result: Any = {
                "owner_state_event_hash": replay_hash(
                    json.loads(path.read_text(encoding="utf-8"))
                ),
                "owner_state_identity": validated_context.owner_state_identity,
            }
        elif request["operation"] == PROFILE_A_EVALUATE_DECISION:
            if set(request["payload"]) != {"decision_inputs"} or not isinstance(
                request["payload"]["decision_inputs"], dict
            ):
                raise FailClosedRuntimeError(
                    "Profile A decision payload fields are invalid"
                )
            gate = (
                _compose_profile_a_bounded_evidence_reduction_gate_inside_authority_process_v1(
                    _authority_process_context=validated_context
                )
            )
            decision_inputs = request["payload"]["decision_inputs"]
            decision = _materialize_process_decision(
                validated_context,
                gate.evaluate(**decision_inputs),
            )
            if decision.get("decision") in {
                "ALLOW_BOUNDED_EVIDENCE_REDUCTION",
                PROFILE_A_TEST_ONLY_ALLOW,
            }:
                origin_evidence = _store_decision_origin_record(
                    context=validated_context,
                    request=request,
                    decision=decision,
                    decision_inputs=decision_inputs,
                )
            else:
                origin_evidence = None
            result = {
                "decision": decision,
                "origin_evidence": origin_evidence,
            }
        else:
            result = _verify_decision_origin_inside_process(
                context=validated_context,
                payload=request["payload"],
            )
        response = _response(
            context=validated_context,
            request_identity=request["request_identity"],
            request_hash=request["request_hash"],
            status="COMPLETED",
            failure_code="NONE",
            result=result,
        )
    except (FailClosedRuntimeError, OSError, TypeError, ValueError):
        response = _response(
            context=validated_context,
            request_identity=request["request_identity"],
            request_hash=request["request_hash"],
            status="DENIED",
            failure_code="AUTHORITY_REQUEST_FAILED_CLOSED",
            result=None,
        )

    write_json_immutable(
        receipt_path,
        {
            "boundary_version": PROFILE_A_AUTHORITY_BOUNDARY_VERSION,
            "boundary_mode": validated_context.boundary_mode,
            "request": request,
            "response": response,
            "receipt_hash": replay_hash(
                {"request": request, "response": response}
            ),
        },
    )
    return response


def _serve(
    context: _ProfileAAuthorityProcessContextV1,
    *,
    maximum_requests: int | None,
) -> None:
    validated = validate_profile_a_authority_process_context_v1(
        context, allow_zero_authority_test=True
    )
    endpoint = Path(validated.socket_path)
    endpoint.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if endpoint.exists() or endpoint.is_symlink():
        raise FailClosedRuntimeError(
            "Profile A authority IPC endpoint already exists"
        )
    listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    served = 0
    try:
        listener.bind(endpoint.as_posix())
        if validated.boundary_mode == PROFILE_A_PRODUCTION_MODE:
            os.chown(endpoint, validated.authority_uid, validated.ipc_gid)
            os.chmod(endpoint, 0o660)
        else:
            os.chmod(endpoint, 0o600)
        listener.listen(8)
        while maximum_requests is None or served < maximum_requests:
            connection, _ = listener.accept()
            with connection:
                served += 1
                try:
                    _authenticate_peer_uid(
                        connection, validated.canonical_entry_uid
                    )
                    request = _recv_frame(connection)
                    response = _handle_request(validated, request)
                except (FailClosedRuntimeError, OSError, ValueError):
                    response = _response(
                        context=validated,
                        request_identity="UNRESOLVED",
                        request_hash="UNRESOLVED",
                        status="DENIED",
                        failure_code="MALFORMED_OR_UNAUTHENTICATED_IPC",
                        result=None,
                    )
                try:
                    _send_frame(connection, response)
                except OSError:
                    pass
    finally:
        listener.close()
        try:
            details = endpoint.lstat()
        except OSError:
            pass
        else:
            if stat.S_ISSOCK(details.st_mode) and details.st_uid == os.geteuid():
                endpoint.unlink()


def serve_profile_a_authority_process_v1() -> None:
    """Serve the fixed production boundary until externally terminated."""

    _serve(
        _establish_profile_a_production_authority_context_v1(),
        maximum_requests=None,
    )


def serve_profile_a_zero_authority_test_process_v1(
    *,
    che_runtime_scope_identity: str | Path,
    owner_state_identity: str,
    socket_path: str | Path,
    maximum_requests: int,
) -> None:
    """Serve a bounded test process that cannot emit production ALLOW."""

    if (
        not isinstance(maximum_requests, int)
        or isinstance(maximum_requests, bool)
        or maximum_requests < 1
    ):
        raise FailClosedRuntimeError(
            "Profile A test request bound is invalid"
        )
    context = create_profile_a_zero_authority_test_context_v1(
        che_runtime_scope_identity=che_runtime_scope_identity,
        owner_state_identity=owner_state_identity,
        socket_path=socket_path,
    )
    _serve(context, maximum_requests=maximum_requests)


def _connect_and_request(
    *,
    endpoint: Path,
    expected_authority_uid: int,
    expected_mode: str,
    request: Mapping[str, Any],
) -> dict[str, Any]:
    connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        connection.connect(endpoint.as_posix())
        _authenticate_peer_uid(connection, expected_authority_uid)
        _send_frame(connection, request)
        response = _recv_frame(connection)
    finally:
        connection.close()
    return _validate_response(
        response,
        expected_request=request,
        expected_mode=expected_mode,
    )


def _production_request(request: Mapping[str, Any]) -> dict[str, Any]:
    binding = _load_profile_a_production_binding_v1()
    if os.geteuid() != binding["canonical_entry_uid"]:
        raise FailClosedRuntimeError(
            "Profile A authority client is not the canonical-entry principal"
        )
    endpoint = Path(binding["socket_path"])
    try:
        details = endpoint.lstat()
    except OSError as exc:
        raise FailClosedRuntimeError(
            "Profile A authority process is unavailable"
        ) from exc
    if (
        not stat.S_ISSOCK(details.st_mode)
        or details.st_uid != binding["authority_uid"]
        or details.st_gid != binding["ipc_gid"]
        or details.st_mode & stat.S_IWOTH
    ):
        raise FailClosedRuntimeError(
            "Profile A authority IPC endpoint custody is invalid"
        )
    return _connect_and_request(
        endpoint=endpoint,
        expected_authority_uid=binding["authority_uid"],
        expected_mode=PROFILE_A_PRODUCTION_MODE,
        request=request,
    )


def request_profile_a_owner_state_issuance_v1(
    *, request: Any, continuation: Any, authority_act: Any, correlation: Any
) -> dict[str, Any]:
    """Request owner-state issuance through the fixed production boundary."""

    canonical = _plain(request)
    request_identity = _text(
        canonical.get("request_identity") if isinstance(canonical, dict) else None,
        "request identity",
    )
    ipc_request = _request(
        operation=PROFILE_A_ISSUE_OWNER_STATE,
        request_identity=f"PROFILE-A-ISSUE:{request_identity}",
        payload={
            "request": request,
            "continuation": continuation,
            "authority_act": authority_act,
            "correlation": correlation,
        },
    )
    response = _production_request(ipc_request)
    if response["status"] != "COMPLETED" or response["failure_code"] != "NONE":
        raise FailClosedRuntimeError(
            "Profile A owner-state issuance failed closed"
        )
    if not isinstance(response["result"], dict):
        raise FailClosedRuntimeError(
            "Profile A owner-state issuance response is invalid"
        )
    return response


def request_profile_a_bounded_evidence_reduction_decision_v1(
    *, request_identity: str, decision_inputs: Mapping[str, Any]
) -> dict[str, Any]:
    """Request one origin-bound production decision envelope."""

    from aigol.runtime.evidence_reduction_gate import BoundedEvidenceReductionGateV1

    inputs = _plain(decision_inputs)
    try:
        ipc_request = _request(
            operation=PROFILE_A_EVALUATE_DECISION,
            request_identity=request_identity,
            payload={"decision_inputs": inputs},
        )
        response = _production_request(ipc_request)
        result = response["result"]
        if (
            response["status"] != "COMPLETED"
            or response["failure_code"] != "NONE"
            or not isinstance(result, dict)
            or set(result) != {"decision", "origin_evidence"}
            or not isinstance(result["decision"], dict)
            or not isinstance(result["origin_evidence"], dict)
        ):
            raise FailClosedRuntimeError(
                "Profile A authority decision failed closed"
            )
        if result["decision"].get("decision") == PROFILE_A_TEST_ONLY_ALLOW:
            raise FailClosedRuntimeError(
                "Profile A production client rejected a test decision"
            )
        origin = _validate_decision_origin_evidence(
            result["origin_evidence"]
        )
        if (
            origin["boundary_mode"] != PROFILE_A_PRODUCTION_MODE
            or origin["authority_process_identity"]
            != PROFILE_A_AUTHORITY_PRINCIPAL_IDENTITY
            or origin["decision_hash"]
            != result["decision"].get("replay_hash")
        ):
            raise FailClosedRuntimeError(
                "Profile A production decision origin is invalid"
            )
        return result
    except (FailClosedRuntimeError, OSError, TypeError, ValueError):
        return {
            "decision": BoundedEvidenceReductionGateV1().evaluate(**inputs),
            "origin_evidence": None,
        }


def authenticate_profile_a_decision_origin_v1(
    *,
    verification_request_identity: str,
    origin_evidence: Mapping[str, Any],
    decision_hash: str,
    planned_manifest_hash: str,
    authorization_hash: str,
    consumer_kind: str,
    effect_identity: str,
) -> dict[str, Any]:
    """Reauthenticate one decision at the fixed production process."""

    ipc_request = _request(
        operation=PROFILE_A_VERIFY_DECISION_ORIGIN,
        request_identity=verification_request_identity,
        payload={
            "origin_evidence": origin_evidence,
            "decision_hash": _text(decision_hash, "decision hash"),
            "planned_manifest_hash": _text(
                planned_manifest_hash, "planned manifest hash"
            ),
            "authorization_hash": _text(
                authorization_hash, "authorization hash"
            ),
            "consumer_kind": _text(consumer_kind, "origin consumer kind"),
            "effect_identity": _text(effect_identity, "effect identity"),
        },
    )
    response = _production_request(ipc_request)
    result = response["result"]
    if (
        response["status"] != "COMPLETED"
        or response["failure_code"] != "NONE"
        or not isinstance(result, dict)
        or result.get("verification_status")
        != PROFILE_A_PRODUCTION_ORIGIN_VERIFIED
        or result.get("decision_hash") != decision_hash
        or result.get("consumer_kind") != consumer_kind
        or result.get("effect_identity") != effect_identity
    ):
        raise FailClosedRuntimeError(
            "Profile A decision origin is not production-authenticated"
        )
    return result


def request_profile_a_zero_authority_test_v1(
    *,
    socket_path: str | Path,
    operation: str,
    request_identity: str,
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    """Exercise the test protocol without acquiring production authority."""

    request = _request(
        operation=operation,
        request_identity=request_identity,
        payload=payload,
    )
    return _connect_and_request(
        endpoint=Path(socket_path),
        expected_authority_uid=os.geteuid(),
        expected_mode=PROFILE_A_ZERO_AUTHORITY_TEST_MODE,
        request=request,
    )


def main() -> int:
    serve_profile_a_authority_process_v1()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "PROFILE_A_AUTHORITY_BOUNDARY_VERSION",
    "PROFILE_A_AUTHORITY_PRINCIPAL_IDENTITY",
    "PROFILE_A_ACTUAL_MANIFEST_CONSUMER",
    "PROFILE_A_EVALUATE_DECISION",
    "PROFILE_A_ISSUE_OWNER_STATE",
    "PROFILE_A_PROCESS_INTERNAL_ALLOW_CANDIDATE",
    "PROFILE_A_PRODUCTION_BINDING_PATH",
    "PROFILE_A_PRODUCTION_ORIGIN_VERIFIED",
    "PROFILE_A_PRODUCTION_SOCKET_PATH",
    "PROFILE_A_RUNTIMELEDGER_CONSUMER",
    "PROFILE_A_TEST_ONLY_ALLOW",
    "PROFILE_A_TEST_ORIGIN_VERIFIED",
    "PROFILE_A_TEST_VERIFICATION_CONSUMER",
    "PROFILE_A_VERIFY_DECISION_ORIGIN",
    "PROFILE_A_ZERO_AUTHORITY_TEST_MODE",
    "authenticate_profile_a_decision_origin_v1",
    "create_profile_a_zero_authority_test_context_v1",
    "request_profile_a_bounded_evidence_reduction_decision_v1",
    "request_profile_a_owner_state_issuance_v1",
    "request_profile_a_zero_authority_test_v1",
    "serve_profile_a_authority_process_v1",
    "serve_profile_a_zero_authority_test_process_v1",
    "validate_profile_a_authority_process_context_v1",
]
