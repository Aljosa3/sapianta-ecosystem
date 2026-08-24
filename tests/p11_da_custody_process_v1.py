"""Construction-only fixed local custody-process mechanics for P11 D-A (S2).

The module defines a disposable Unix IPC and peer-credential boundary.  It
does not provision principals, originate Human authority, or run a daemon.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
import socket
import struct
from types import MappingProxyType
from typing import Any, Mapping

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize


ROLE_COUNT = 3
LOCAL_ONLY = True
REMOTE_NETWORK_TRANSPORT = "PROHIBITED"
CALLER_SELECTED_ENDPOINT = "PROHIBITED"
CALLER_SELECTED_PRINCIPAL = "PROHIBITED"
CALLER_SELECTED_CREDENTIAL = "PROHIBITED"
CALLER_SELECTED_RESOLVER = "PROHIBITED"
CALLER_SELECTED_STORE = "PROHIBITED"
CALLER_SELECTED_OWNER_STATE = "PROHIBITED"
CALLER_SELECTED_CUSTODY_PATH = "PROHIBITED"
OS_IDENTITY_AUTHORITY_EFFECT = 0

FIXED_ENDPOINT_NAME = "p11_da_disposable_custody_v1.sock"
FIXED_PROTOCOL_IDENTITY = "P11_DA_DISPOSABLE_LOCAL_IPC_V1"
MAX_FRAME_BYTES = 1_048_576
_FRAME_HEADER = struct.Struct("!I")
_PEER_CREDENTIALS = struct.Struct("3i")


def _fail(message: str) -> None:
    raise FailClosedRuntimeError(message)


class PrincipalRole(str, Enum):
    HUMAN_AUTHORITY_ISSUANCE_PRINCIPAL = "HUMAN_AUTHORITY_ISSUANCE_PRINCIPAL"
    P11_ORCHESTRATION_CALLER_PRINCIPAL = "P11_ORCHESTRATION_CALLER_PRINCIPAL"
    AUTHORITY_CUSTODY_PROCESS_PRINCIPAL = "AUTHORITY_CUSTODY_PROCESS_PRINCIPAL"


class CustodyOperation(str, Enum):
    SUBMIT_CANONICAL_HUMAN_ACT = "SUBMIT_CANONICAL_HUMAN_ACT"
    REQUEST_REVOCATION = "REQUEST_REVOCATION"
    REQUEST_SUPERSESSION = "REQUEST_SUPERSESSION"
    CLAIM_AND_INVOKE_ONCE = "CLAIM_AND_INVOKE_ONCE"
    READ_ONLY_AUDIT = "READ_ONLY_AUDIT"


@dataclass(frozen=True, slots=True)
class RoleDescriptor:
    role: PrincipalRole
    allowed_operations: frozenset[CustodyOperation]
    authority_effect: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.role, PrincipalRole) or not self.allowed_operations:
            _fail("P11 D-A role descriptor is invalid")
        if self.authority_effect != 0:
            _fail("OS role cannot supply constitutional authority")


ROLE_DESCRIPTORS: Mapping[PrincipalRole, RoleDescriptor] = MappingProxyType(
    {
        PrincipalRole.HUMAN_AUTHORITY_ISSUANCE_PRINCIPAL: RoleDescriptor(
            PrincipalRole.HUMAN_AUTHORITY_ISSUANCE_PRINCIPAL,
            frozenset(
                {
                    CustodyOperation.SUBMIT_CANONICAL_HUMAN_ACT,
                    CustodyOperation.REQUEST_REVOCATION,
                    CustodyOperation.REQUEST_SUPERSESSION,
                }
            ),
        ),
        PrincipalRole.P11_ORCHESTRATION_CALLER_PRINCIPAL: RoleDescriptor(
            PrincipalRole.P11_ORCHESTRATION_CALLER_PRINCIPAL,
            frozenset({CustodyOperation.CLAIM_AND_INVOKE_ONCE}),
        ),
        PrincipalRole.AUTHORITY_CUSTODY_PROCESS_PRINCIPAL: RoleDescriptor(
            PrincipalRole.AUTHORITY_CUSTODY_PROCESS_PRINCIPAL,
            frozenset({CustodyOperation.READ_ONLY_AUDIT}),
        ),
    }
)


@dataclass(frozen=True, slots=True, init=False)
class FixedLocalIPCConfiguration:
    protocol_identity: str
    endpoint_name: str
    local_only: bool
    remote_fallback_allowed: bool
    caller_endpoint_parameter_allowed: bool

    def __init__(self) -> None:
        object.__setattr__(self, "protocol_identity", FIXED_PROTOCOL_IDENTITY)
        object.__setattr__(self, "endpoint_name", FIXED_ENDPOINT_NAME)
        object.__setattr__(self, "local_only", True)
        object.__setattr__(self, "remote_fallback_allowed", False)
        object.__setattr__(self, "caller_endpoint_parameter_allowed", False)

    def endpoint_under_fixture_root(self, fixture_root: Path) -> Path:
        if not isinstance(fixture_root, Path) or not fixture_root.is_absolute():
            _fail("disposable fixture root must be an absolute Path")
        return fixture_root / self.endpoint_name


@dataclass(frozen=True, slots=True)
class FixedPrincipalBindings:
    issuance_uid: int
    caller_uid: int
    custody_uid: int

    def __post_init__(self) -> None:
        values = (self.issuance_uid, self.caller_uid, self.custody_uid)
        if any(
            not isinstance(value, int) or isinstance(value, bool) or value < 0
            for value in values
        ):
            _fail("principal UID bindings must be non-negative integers")
        if len(set(values)) != ROLE_COUNT:
            _fail("all three P11 D-A principal UID bindings must be distinct")

    def uid_for(self, role: PrincipalRole) -> int:
        return {
            PrincipalRole.HUMAN_AUTHORITY_ISSUANCE_PRINCIPAL: self.issuance_uid,
            PrincipalRole.P11_ORCHESTRATION_CALLER_PRINCIPAL: self.caller_uid,
            PrincipalRole.AUTHORITY_CUSTODY_PROCESS_PRINCIPAL: self.custody_uid,
        }[role]


@dataclass(frozen=True, slots=True)
class PeerCredentials:
    pid: int
    uid: int
    gid: int

    def __post_init__(self) -> None:
        for field_name in ("pid", "uid", "gid"):
            value = getattr(self, field_name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                _fail(f"peer {field_name} is invalid")


def read_kernel_peer_credentials(connection: socket.socket) -> PeerCredentials:
    """Read Linux kernel-supplied peer credentials; never trust request data."""

    if not isinstance(connection, socket.socket) or connection.family != socket.AF_UNIX:
        _fail("P11 D-A custody requires a Unix-domain socket")
    raw = connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, _PEER_CREDENTIALS.size)
    pid, uid, gid = _PEER_CREDENTIALS.unpack(raw)
    return PeerCredentials(pid=pid, uid=uid, gid=gid)


class CustodyPeerCredentialVerifier:
    """Deployment-bound verifier owned by the custody fixture, not a request."""

    def __init__(self, bindings: FixedPrincipalBindings) -> None:
        if not isinstance(bindings, FixedPrincipalBindings):
            _fail("fixed principal bindings are required")
        self._bindings = bindings

    def authenticate(
        self, operation: CustodyOperation, peer: PeerCredentials
    ) -> PrincipalRole:
        if not isinstance(operation, CustodyOperation):
            _fail("custody operation is invalid")
        if not isinstance(peer, PeerCredentials):
            _fail("kernel peer credentials are required")
        matching = tuple(
            role
            for role in PrincipalRole
            if self._bindings.uid_for(role) == peer.uid
            and operation in ROLE_DESCRIPTORS[role].allowed_operations
        )
        if len(matching) != 1:
            _fail("peer is not authorized for the fixed custody operation")
        return matching[0]


@dataclass(frozen=True, slots=True)
class CustodyRequest:
    """Closed request shape with no custody-composition selection fields."""

    protocol_identity: str
    operation: CustodyOperation
    request_identity: str
    canonical_payload: bytes

    def __post_init__(self) -> None:
        if self.protocol_identity != FIXED_PROTOCOL_IDENTITY:
            _fail("custody request protocol identity is invalid")
        if not isinstance(self.operation, CustodyOperation):
            _fail("custody request operation is invalid")
        if not isinstance(self.request_identity, str) or not self.request_identity.strip():
            _fail("custody request identity is required")
        if not isinstance(self.canonical_payload, bytes) or not self.canonical_payload:
            _fail("custody request canonical payload is required")


FORBIDDEN_REQUEST_SELECTION_FIELDS = frozenset(
    {
        "principal",
        "endpoint",
        "credential",
        "resolver",
        "store",
        "owner_state",
        "custody_path",
    }
)
CUSTODY_REQUEST_FIELDS = frozenset(CustodyRequest.__dataclass_fields__)


def encode_local_frame(value: Mapping[str, Any]) -> bytes:
    payload = canonical_serialize(dict(value)).encode("utf-8")
    if not payload or len(payload) > MAX_FRAME_BYTES:
        _fail("local custody frame size is invalid")
    return _FRAME_HEADER.pack(len(payload)) + payload


def decode_local_frame(frame: bytes) -> dict[str, Any]:
    if not isinstance(frame, bytes) or len(frame) < _FRAME_HEADER.size:
        _fail("local custody frame is incomplete")
    (size,) = _FRAME_HEADER.unpack(frame[: _FRAME_HEADER.size])
    payload = frame[_FRAME_HEADER.size :]
    if size != len(payload) or size == 0 or size > MAX_FRAME_BYTES:
        _fail("local custody frame length is invalid")
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise FailClosedRuntimeError("local custody frame payload is invalid") from exc
    if not isinstance(value, dict) or canonical_serialize(value).encode("utf-8") != payload:
        _fail("local custody frame payload is not canonical")
    return value


assert len(ROLE_DESCRIPTORS) == ROLE_COUNT
assert not (CUSTODY_REQUEST_FIELDS & FORBIDDEN_REQUEST_SELECTION_FIELDS)


__all__ = [
    "CALLER_SELECTED_CUSTODY_PATH",
    "CALLER_SELECTED_ENDPOINT",
    "CALLER_SELECTED_OWNER_STATE",
    "CALLER_SELECTED_PRINCIPAL",
    "CALLER_SELECTED_RESOLVER",
    "CALLER_SELECTED_STORE",
    "CUSTODY_REQUEST_FIELDS",
    "CustodyOperation",
    "CustodyPeerCredentialVerifier",
    "CustodyRequest",
    "FIXED_ENDPOINT_NAME",
    "FIXED_PROTOCOL_IDENTITY",
    "FORBIDDEN_REQUEST_SELECTION_FIELDS",
    "FixedLocalIPCConfiguration",
    "FixedPrincipalBindings",
    "LOCAL_ONLY",
    "OS_IDENTITY_AUTHORITY_EFFECT",
    "PeerCredentials",
    "PrincipalRole",
    "ROLE_COUNT",
    "ROLE_DESCRIPTORS",
    "decode_local_frame",
    "encode_local_frame",
    "read_kernel_peer_credentials",
]
