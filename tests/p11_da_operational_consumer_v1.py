"""Minimum disposable operational P11 consumer implementation.

The module is an implementation surface for a later separately authorized
non-production generation.  Importing, constructing, or certifying it does not
enter P11.  Only ``submit_human_act`` and ``claim_and_invoke_once`` are
operational entry methods, and this generation does not call either method.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
import os
from pathlib import Path
import socket
import stat
import time
from types import MappingProxyType
from typing import Any, Mapping

from aigol.runtime.canonical_human_authority_act_contract_v1 import (
    AUTHORIZATION,
    HUMAN_AUTHORITY_OWNER,
    CanonicalHumanAuthorityActV1,
)
from aigol.runtime.canonical_che_evidence_correlation_contract_v1 import (
    CanonicalCHEEvidenceCorrelationV1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.ledger import RuntimeLedger
from aigol.runtime.transport.serialization import (
    canonical_serialize,
    replay_hash,
    verify_replay_hash,
)
from p11_da_custody_process_v1 import (
    FIXED_ENDPOINT_NAME,
    FIXED_PROTOCOL_IDENTITY,
    CustodyOperation,
    CustodyPeerCredentialVerifier,
    CustodyRequest,
    FixedPrincipalBindings,
    PrincipalRole,
    read_kernel_peer_credentials,
)
from p11_da_disposable_substrate_v1 import (
    AUTOMATIC_RETRY_COUNT,
    D3_PHASE_SEQUENCE,
    MAXIMUM_DURATION_NS,
    OUTPUT_RECORD_COUNT,
    OUTPUT_RECORD_KIND,
    OUTPUT_SCHEMA_ID,
    PRODUCTION_ROUTE_COUNT,
    SCHEMA_VERSION,
    AuthorityBinding,
    DisposableOwnerState,
    OwnerStateName,
    P11CaptureReplayAdapter,
    atomically_claim_construction_state,
    bind_record_identity,
    terminal_bind_and_consume,
    transition_owner_state,
    validate_input_record_bytes,
    validate_output_record_bytes,
)


OPERATIONAL_CONSUMER_IDENTITY = "P11_DA_MINIMUM_BOUNDED_OPERATIONAL_CONSUMER_V1"
OPERATIONAL_AUTHORITY_SCOPE = "P11_DA_ONE_BOUNDED_OPERATIONAL_ATTEMPT_V1"
FIXED_OWNER_STATE_DIRECTORY_NAME = "p11_da_protected_owner_state_v1"
OWNER_STATE_SCHEMA_ID = "P11_DA_PROTECTED_OWNER_STATE_REVISION_V1"
COMMISSIONING_GATE_SCHEMA_ID = "P11_DA_CH_P01_P12_COMMISSIONING_GATE_V1"
DH_CHECKPOINT = "9f5fd37212547cf06b664c94152ae0ec50a55b79"
CH_DECISION_PACKAGE_IDENTITY = (
    "G77_256CH_P11_E01_E12_OPERATIONAL_EVIDENCE_GENERATION_"
    "HUMAN_AUTHORIZATION_DECISION_PACKAGE_V1"
)
CH_ARTIFACT_SHA256 = (
    "d07f6eae99abd6f95b37553c84eb226298e40e5c61f42f5597980d784a16e2ce"
)
CF_SOURCE_GIT_BLOB = "bb5382994b266e53358acb286ef06f41ce2936e6"
CF_SOURCE_SHA256 = (
    "a1b58fa8ddedb5058393aa23d815262c92c8b185c0b193764f77420313af0bab"
)

OPERATIONAL_P11_ENTRY_AUTHORIZED_IN_G77_256DI = False
OPERATIONAL_INVOCATION_AUTHORIZED_IN_G77_256DI = False
E01_E12_EXECUTION_AUTHORIZED_IN_G77_256DI = False
P12_ENTRY_AUTHORIZED_IN_G77_256DI = False
PRODUCTION_ROUTING_AUTHORIZED_IN_G77_256DI = False

AUTHORITY_EFFECT_OUTSIDE_BOUND_ATTEMPT = 0
SATISFYING_EVIDENCE_EFFECT_OF_COMMISSIONING = 0
AUTOMATIC_RETRY_COUNT_V1 = AUTOMATIC_RETRY_COUNT
INVOCATIONS_PER_CLAIM_V1 = 1
OUTPUT_RECORD_COUNT_V1 = OUTPUT_RECORD_COUNT
PRODUCTION_ROUTE_COUNT_V1 = PRODUCTION_ROUTE_COUNT

CH_PRECONDITION_IDS = tuple(f"P{number:02d}" for number in range(1, 13))
CH_PASS_CONJUNCTION = tuple((condition, "PASS") for condition in CH_PRECONDITION_IDS)

OPERATIONAL_ACT_PAYLOAD_FIELDS = frozenset(
    {
        "decision_package_identity",
        "decision_package_sha256",
        "cg_checkpoint",
        "cg_report_identity",
        "cd_plan_identity",
        "cd_plan_sha256",
        "cf_source_tree_identity",
        "materialization_identity",
        "evidence_obligation_id",
        "case_id",
        "evidence_run_identity",
        "caller_role",
        "caller_uid",
        "custody_role",
        "custody_uid",
        "fixed_endpoint_identity",
        "protected_owner_state_root_identity",
        "protected_owner_state_revision",
        "attempt_identity",
        "input_record_identity",
        "input_payload_identity",
        "contract_identity",
        "contract_version",
        "contract_content_sha256",
        "allowed_operation",
        "maximum_attempts",
        "automatic_retries",
        "maximum_duration_ns",
        "authority_effect_outside_bound_attempt",
        "production_routing_effect",
        "valid_from_unix_ns",
        "valid_until_unix_ns",
        "terminal_consumption_and_non_reuse",
        "required_disposal",
        "minimum_retention",
    }
)

OPERATIONAL_LEDGER_EVENT_TYPES = frozenset(
    {
        "P11_DA_OPERATIONAL_PRECLAIM",
        "P11_DA_OPERATIONAL_CLAIM",
        "P11_DA_OPERATIONAL_INVOCATION",
        "P11_DA_OPERATIONAL_TERMINAL_BIND",
        "P11_DA_OPERATIONAL_PERMANENT_EXHAUSTION",
    }
)


def _fail(message: str) -> None:
    raise FailClosedRuntimeError(message)


def _identity(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        _fail(f"{field_name} must be an exact non-empty identity")
    return value


def _sha256_identity(value: Any, field_name: str) -> str:
    text = _identity(value, field_name)
    raw = text.removeprefix("sha256:")
    if len(raw) != 64 or any(character not in "0123456789abcdef" for character in raw):
        _fail(f"{field_name} must be a SHA-256 identity")
    return text


def _nonnegative_integer(value: Any, field_name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        _fail(f"{field_name} must be a non-negative integer")
    return value


def _binding_to_dict(binding: AuthorityBinding) -> dict[str, Any]:
    return {
        field_name: deepcopy(getattr(binding, field_name))
        for field_name in binding.__dataclass_fields__
    }


def _state_to_record(state: DisposableOwnerState) -> dict[str, Any]:
    value = {
        "schema_id": OWNER_STATE_SCHEMA_ID,
        "binding": _binding_to_dict(state.binding),
        "state": state.state.value,
        "revision": state.revision,
        "output_record_identity": state.output_record_identity,
        "outcome": state.outcome,
        "disposal_completion_proof_identity": (
            state.disposal_completion_proof_identity
        ),
        "state_hash": "",
    }
    value["state_hash"] = replay_hash(
        {key: item for key, item in value.items() if key != "state_hash"}
    )
    return value


def _state_from_record(value: Any) -> DisposableOwnerState:
    expected_fields = {
        "schema_id",
        "binding",
        "state",
        "revision",
        "output_record_identity",
        "outcome",
        "disposal_completion_proof_identity",
        "state_hash",
    }
    if not isinstance(value, dict) or set(value) != expected_fields:
        _fail("protected owner-state revision structure is invalid")
    if value["schema_id"] != OWNER_STATE_SCHEMA_ID:
        _fail("protected owner-state revision schema is invalid")
    verify_replay_hash(value, hash_field="state_hash")
    binding_value = value["binding"]
    if not isinstance(binding_value, dict) or set(binding_value) != set(
        AuthorityBinding.__dataclass_fields__
    ):
        _fail("protected owner-state authority binding is invalid")
    try:
        state_name = OwnerStateName(value["state"])
    except (TypeError, ValueError) as exc:
        raise FailClosedRuntimeError("protected owner-state value is invalid") from exc
    return DisposableOwnerState(
        binding=AuthorityBinding(**binding_value),
        state=state_name,
        revision=value["revision"],
        output_record_identity=value["output_record_identity"],
        outcome=value["outcome"],
        disposal_completion_proof_identity=(
            value["disposal_completion_proof_identity"]
        ),
    )


def fixed_principal_bindings_identity(bindings: FixedPrincipalBindings) -> str:
    if not isinstance(bindings, FixedPrincipalBindings):
        _fail("fixed principal bindings are required")
    return replay_hash(
        {
            "schema_id": "P11_DA_FIXED_PRINCIPAL_BINDINGS_V1",
            "issuance_uid": bindings.issuance_uid,
            "caller_uid": bindings.caller_uid,
            "custody_uid": bindings.custody_uid,
        }
    )


class ProtectedOwnerStateStoreV1:
    """One custody-owned append-only revision store; no caller path selection."""

    def __init__(self, fixture_root: Path, custody_uid: int) -> None:
        if not isinstance(fixture_root, Path) or not fixture_root.is_absolute():
            _fail("protected owner-state fixture root must be an absolute Path")
        self._fixture_root = fixture_root
        self._custody_uid = _nonnegative_integer(custody_uid, "custody UID")
        self._validate_directory(self._fixture_root, create=False)
        self._root = self._fixture_root / FIXED_OWNER_STATE_DIRECTORY_NAME
        if not self._root.exists():
            self._root.mkdir(mode=0o700)
        self._validate_directory(self._root, create=False)

    @property
    def fixture_root(self) -> Path:
        return self._fixture_root

    @property
    def root(self) -> Path:
        return self._root

    @property
    def root_identity(self) -> str:
        self._validate_directory(self._root, create=False)
        metadata = self._root.stat()
        return replay_hash(
            {
                "schema_id": "P11_DA_PROTECTED_OWNER_STATE_ROOT_IDENTITY_V1",
                "path": str(self._root),
                "device": metadata.st_dev,
                "inode": metadata.st_ino,
                "uid": metadata.st_uid,
                "mode": stat.S_IMODE(metadata.st_mode),
            }
        )

    def _validate_directory(self, path: Path, *, create: bool) -> None:
        if create and not path.exists():
            path.mkdir(mode=0o700)
        try:
            metadata = path.lstat()
        except FileNotFoundError as exc:
            raise FailClosedRuntimeError("protected custody directory is absent") from exc
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            _fail("protected custody path must be a real directory")
        if path.resolve(strict=True) != path:
            _fail("protected custody path cannot use aliases or symlinks")
        if metadata.st_uid != self._custody_uid:
            _fail("protected custody directory owner is invalid")
        if stat.S_IMODE(metadata.st_mode) & 0o022:
            _fail("protected custody directory cannot be group/other writable")

    def _revision_path(self, revision: int) -> Path:
        _nonnegative_integer(revision, "owner-state revision")
        return self._root / f"revision-{revision:020d}.json"

    def _revision_paths(self) -> tuple[Path, ...]:
        self._validate_directory(self._root, create=False)
        paths = tuple(sorted(self._root.iterdir()))
        if any(
            path.name != f"revision-{index:020d}.json"
            for index, path in enumerate(paths)
        ):
            _fail("protected owner-state revision set is not contiguous")
        return paths

    def current(self, *, allow_missing: bool = False) -> DisposableOwnerState | None:
        paths = self._revision_paths()
        if not paths:
            if allow_missing:
                return None
            _fail("protected owner-state is not initialized")
        states: list[DisposableOwnerState] = []
        for index, path in enumerate(paths):
            metadata = path.lstat()
            if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
                _fail("protected owner-state revision must be a regular file")
            if metadata.st_uid != self._custody_uid:
                _fail("protected owner-state revision owner is invalid")
            if stat.S_IMODE(metadata.st_mode) & 0o077:
                _fail("protected owner-state revision permissions are invalid")
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise FailClosedRuntimeError(
                    "protected owner-state revision is not valid JSON"
                ) from exc
            state_value = _state_from_record(value)
            if state_value.revision != index:
                _fail("protected owner-state revision identity is invalid")
            if index == 0:
                if state_value.state is not OwnerStateName.AVAILABLE:
                    _fail("protected owner-state must begin AVAILABLE")
            else:
                previous = states[-1]
                if state_value.binding != previous.binding:
                    _fail("protected owner-state authority binding changed")
                transition = (previous.state, state_value.state)
                if transition not in {
                    (OwnerStateName.AVAILABLE, OwnerStateName.CLAIMED),
                    (OwnerStateName.AVAILABLE, OwnerStateName.REVOKED),
                    (OwnerStateName.AVAILABLE, OwnerStateName.SUPERSEDED),
                    (OwnerStateName.AVAILABLE, OwnerStateName.EXPIRED),
                    (OwnerStateName.CLAIMED, OwnerStateName.CONSUMED),
                    (
                        OwnerStateName.CLAIMED,
                        OwnerStateName.RECONCILIATION_REQUIRED,
                    ),
                    (
                        OwnerStateName.RECONCILIATION_REQUIRED,
                        OwnerStateName.CONSUMED,
                    ),
                }:
                    _fail("protected owner-state transition lineage is invalid")
            states.append(state_value)
        return states[-1]

    def _append(self, expected: DisposableOwnerState | None, target: DisposableOwnerState) -> None:
        current = self.current(allow_missing=True)
        if current != expected:
            _fail("protected owner-state compare-and-append conflict")
        expected_revision = 0 if current is None else current.revision + 1
        if target.revision != expected_revision:
            _fail("protected owner-state target revision is invalid")
        path = self._revision_path(target.revision)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        try:
            descriptor = os.open(path, flags, 0o600)
        except FileExistsError as exc:
            raise FailClosedRuntimeError(
                "protected owner-state concurrent transition denied"
            ) from exc
        payload = canonical_serialize(_state_to_record(target)) + "\n"
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
        except BaseException:
            # A partial exclusive revision is intentionally retained.  Future
            # reads fail closed and cannot reinterpret the prior act as reusable.
            raise
        directory_descriptor = os.open(self._root, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)

    def initialize_available(self, binding: AuthorityBinding) -> DisposableOwnerState:
        if not isinstance(binding, AuthorityBinding):
            _fail("canonical authority binding is required")
        state_value = DisposableOwnerState(binding=binding)
        self._append(None, state_value)
        return state_value

    def claim(
        self,
        expected: DisposableOwnerState,
        *,
        claim_time_unix_ns: int,
        authenticated_caller_principal_identity: str,
    ) -> DisposableOwnerState:
        claimed = atomically_claim_construction_state(
            expected,
            claim_time_unix_ns=claim_time_unix_ns,
            authenticated_caller_principal_identity=(
                authenticated_caller_principal_identity
            ),
        )
        self._append(expected, claimed)
        return claimed

    def mark_reconciliation_required(
        self, expected: DisposableOwnerState
    ) -> DisposableOwnerState:
        target = transition_owner_state(
            expected, OwnerStateName.RECONCILIATION_REQUIRED
        )
        self._append(expected, target)
        return target

    def terminal_bind_and_permanently_exhaust(
        self,
        expected: DisposableOwnerState,
        output_record: Mapping[str, Any],
        *,
        reconciliation_establishes_terminal_exhaustion: bool = False,
    ) -> DisposableOwnerState:
        target = terminal_bind_and_consume(
            expected,
            output_record,
            reconciliation_establishes_terminal_exhaustion=(
                reconciliation_establishes_terminal_exhaustion
            ),
        )
        self._append(expected, target)
        return target

    def terminate_unclaimed(
        self, expected: DisposableOwnerState, target: OwnerStateName
    ) -> DisposableOwnerState:
        if target not in {
            OwnerStateName.REVOKED,
            OwnerStateName.SUPERSEDED,
            OwnerStateName.EXPIRED,
        }:
            _fail("unclaimed terminal target is invalid")
        terminated = transition_owner_state(expected, target)
        self._append(expected, terminated)
        return terminated


@dataclass(frozen=True, slots=True)
class CommissioningGateV1:
    gate_identity: str
    dh_checkpoint: str
    ch_decision_package_identity: str
    ch_artifact_sha256: str
    cg_checkpoint: str
    cg_report_identity: str
    cd_plan_identity: str
    cd_plan_sha256: str
    cf_source_tree_identity: str
    cf_source_sha256: str
    materialization_identity: str
    fixture_root_identity: str
    principal_bindings_identity: str
    endpoint_identity: str
    owner_state_root_identity: str
    condition_results: tuple[tuple[str, str], ...]
    condition_evidence_identities: tuple[tuple[str, str], ...]
    satisfying_evidence_effect: int = SATISFYING_EVIDENCE_EFFECT_OF_COMMISSIONING
    p11_invocation_effect: int = 0

    def __post_init__(self) -> None:
        for field_name in (
            "gate_identity",
            "dh_checkpoint",
            "ch_decision_package_identity",
            "cg_checkpoint",
            "cg_report_identity",
            "cd_plan_identity",
            "cf_source_tree_identity",
            "materialization_identity",
            "fixture_root_identity",
            "principal_bindings_identity",
            "endpoint_identity",
            "owner_state_root_identity",
        ):
            _identity(getattr(self, field_name), field_name)
        _sha256_identity(self.ch_artifact_sha256, "CH artifact SHA-256")
        _sha256_identity(self.cd_plan_sha256, "CD plan SHA-256")
        _sha256_identity(self.cf_source_sha256, "CF source SHA-256")
        if self.dh_checkpoint != DH_CHECKPOINT:
            _fail("commissioning gate DH checkpoint is invalid")
        if self.ch_decision_package_identity != CH_DECISION_PACKAGE_IDENTITY:
            _fail("commissioning gate CH decision package identity is invalid")
        if self.ch_artifact_sha256 != CH_ARTIFACT_SHA256:
            _fail("commissioning gate CH artifact identity is invalid")
        if self.cf_source_tree_identity != CF_SOURCE_GIT_BLOB:
            _fail("commissioning gate CF source Git identity is invalid")
        if self.cf_source_sha256 != CF_SOURCE_SHA256:
            _fail("commissioning gate CF source content identity is invalid")
        if self.condition_results != CH_PASS_CONJUNCTION:
            _fail("all twelve CH commissioning conditions must pass exactly")
        if tuple(item[0] for item in self.condition_evidence_identities) != (
            CH_PRECONDITION_IDS
        ) or any(
            not isinstance(identity, str) or not identity.strip()
            for _, identity in self.condition_evidence_identities
        ):
            _fail("all twelve CH conditions require bound evidence identities")
        if self.satisfying_evidence_effect != 0 or self.p11_invocation_effect != 0:
            _fail("commissioning gate cannot create evidence or invoke P11")
        if self.gate_identity != replay_hash(self.identity_preimage()):
            _fail("commissioning gate identity is invalid")

    def identity_preimage(self) -> dict[str, Any]:
        return {
            "schema_id": COMMISSIONING_GATE_SCHEMA_ID,
            "dh_checkpoint": self.dh_checkpoint,
            "ch_decision_package_identity": self.ch_decision_package_identity,
            "ch_artifact_sha256": self.ch_artifact_sha256,
            "cg_checkpoint": self.cg_checkpoint,
            "cg_report_identity": self.cg_report_identity,
            "cd_plan_identity": self.cd_plan_identity,
            "cd_plan_sha256": self.cd_plan_sha256,
            "cf_source_tree_identity": self.cf_source_tree_identity,
            "cf_source_sha256": self.cf_source_sha256,
            "materialization_identity": self.materialization_identity,
            "fixture_root_identity": self.fixture_root_identity,
            "principal_bindings_identity": self.principal_bindings_identity,
            "endpoint_identity": self.endpoint_identity,
            "owner_state_root_identity": self.owner_state_root_identity,
            "condition_results": [list(item) for item in self.condition_results],
            "condition_evidence_identities": [
                list(item) for item in self.condition_evidence_identities
            ],
            "satisfying_evidence_effect": self.satisfying_evidence_effect,
            "p11_invocation_effect": self.p11_invocation_effect,
        }


def create_commissioning_gate_v1(**facts: Any) -> CommissioningGateV1:
    value = dict(facts)
    value.setdefault("satisfying_evidence_effect", 0)
    value.setdefault("p11_invocation_effect", 0)
    provisional = CommissioningGateV1.__new__(CommissioningGateV1)
    for field_name in CommissioningGateV1.__dataclass_fields__:
        if field_name == "gate_identity":
            object.__setattr__(provisional, field_name, "pending")
        else:
            object.__setattr__(provisional, field_name, value[field_name])
    value["gate_identity"] = replay_hash(provisional.identity_preimage())
    return CommissioningGateV1(**value)


def fixture_root_identity(fixture_root: Path, custody_uid: int) -> str:
    if not isinstance(fixture_root, Path) or not fixture_root.is_absolute():
        _fail("fixture root must be an absolute Path")
    metadata = fixture_root.stat()
    if metadata.st_uid != custody_uid:
        _fail("fixture root custody owner is invalid")
    return replay_hash(
        {
            "schema_id": "P11_DA_DISPOSABLE_FIXTURE_ROOT_IDENTITY_V1",
            "path": str(fixture_root),
            "device": metadata.st_dev,
            "inode": metadata.st_ino,
            "uid": metadata.st_uid,
            "mode": stat.S_IMODE(metadata.st_mode),
        }
    )


def fixed_endpoint_identity(fixture_root: Path, custody_uid: int) -> str:
    return replay_hash(
        {
            "schema_id": "P11_DA_FIXED_ENDPOINT_IDENTITY_V1",
            "path": str(fixture_root / FIXED_ENDPOINT_NAME),
            "protocol_identity": FIXED_PROTOCOL_IDENTITY,
            "custody_uid": custody_uid,
            "local_only": True,
            "remote_fallback": False,
        }
    )


def materialization_identity(
    *,
    fixture_identity: str,
    principal_identity: str,
    endpoint_identity: str,
    owner_state_identity: str,
) -> str:
    return replay_hash(
        {
            "schema_id": "P11_DA_OPERATIONAL_MATERIALIZATION_IDENTITY_V1",
            "fixture_root_identity": fixture_identity,
            "principal_bindings_identity": principal_identity,
            "fixed_endpoint_identity": endpoint_identity,
            "protected_owner_state_root_identity": owner_state_identity,
        }
    )


def validate_operational_act_payload(
    payload: Any,
    *,
    input_record: Mapping[str, Any],
    gate: CommissioningGateV1,
    bindings: FixedPrincipalBindings,
    owner_revision: int,
    now_unix_ns: int,
) -> Mapping[str, Any]:
    if not isinstance(payload, Mapping) or set(payload) != OPERATIONAL_ACT_PAYLOAD_FIELDS:
        _fail("operational Human act payload structure is invalid")
    value = dict(payload)
    for field_name in OPERATIONAL_ACT_PAYLOAD_FIELDS - {
        "caller_uid",
        "custody_uid",
        "protected_owner_state_revision",
        "maximum_attempts",
        "automatic_retries",
        "maximum_duration_ns",
        "authority_effect_outside_bound_attempt",
        "production_routing_effect",
        "valid_from_unix_ns",
        "valid_until_unix_ns",
    }:
        _identity(value[field_name], field_name)
    for field_name in ("decision_package_sha256", "cd_plan_sha256"):
        _sha256_identity(value[field_name], field_name)
    _sha256_identity(value["contract_content_sha256"], "contract content SHA-256")
    expected_equalities = {
        "decision_package_identity": gate.ch_decision_package_identity,
        "decision_package_sha256": gate.ch_artifact_sha256,
        "cg_checkpoint": gate.cg_checkpoint,
        "cg_report_identity": gate.cg_report_identity,
        "cd_plan_identity": gate.cd_plan_identity,
        "cd_plan_sha256": gate.cd_plan_sha256,
        "cf_source_tree_identity": gate.cf_source_tree_identity,
        "materialization_identity": gate.materialization_identity,
        "caller_role": PrincipalRole.P11_ORCHESTRATION_CALLER_PRINCIPAL.value,
        "caller_uid": bindings.caller_uid,
        "custody_role": PrincipalRole.AUTHORITY_CUSTODY_PROCESS_PRINCIPAL.value,
        "custody_uid": bindings.custody_uid,
        "fixed_endpoint_identity": gate.endpoint_identity,
        "protected_owner_state_root_identity": gate.owner_state_root_identity,
        "protected_owner_state_revision": owner_revision,
        "attempt_identity": input_record["attempt_identity"],
        "input_record_identity": input_record["record_identity"],
        "input_payload_identity": input_record["input_identity"],
        "contract_identity": input_record["contract_identity"],
        "contract_version": input_record["contract_version"],
        "contract_content_sha256": input_record["contract_content_sha256"],
        "allowed_operation": CustodyOperation.CLAIM_AND_INVOKE_ONCE.value,
        "maximum_attempts": 1,
        "automatic_retries": 0,
        "maximum_duration_ns": MAXIMUM_DURATION_NS,
        "authority_effect_outside_bound_attempt": 0,
        "production_routing_effect": 0,
        "terminal_consumption_and_non_reuse": "REQUIRED",
    }
    for field_name, expected in expected_equalities.items():
        if value[field_name] != expected:
            _fail(f"operational Human act {field_name} binding is invalid")
    valid_from = _nonnegative_integer(value["valid_from_unix_ns"], "valid from")
    valid_until = _nonnegative_integer(value["valid_until_unix_ns"], "valid until")
    current = _nonnegative_integer(now_unix_ns, "current time")
    if not valid_from <= current < valid_until:
        _fail("operational Human act is not current")
    return MappingProxyType(value)


class P11BoundedConsumerV1:
    """One fixed-custody, one-act, one-invocation, zero-production consumer."""

    operational_p11_entry = True
    authority_origin = HUMAN_AUTHORITY_OWNER
    authority_effect_outside_bound_attempt = 0
    automatic_retry_count = AUTOMATIC_RETRY_COUNT_V1
    invocations_per_claim = INVOCATIONS_PER_CLAIM_V1
    output_record_count = OUTPUT_RECORD_COUNT_V1
    production_route_count = PRODUCTION_ROUTE_COUNT_V1
    phase_sequence = D3_PHASE_SEQUENCE

    def __init__(
        self,
        *,
        store: ProtectedOwnerStateStoreV1,
        principal_bindings: FixedPrincipalBindings,
        commissioning_gate: CommissioningGateV1,
    ) -> None:
        if not isinstance(store, ProtectedOwnerStateStoreV1):
            _fail("protected owner-state store is required")
        if not isinstance(principal_bindings, FixedPrincipalBindings):
            _fail("fixed principal bindings are required")
        if not isinstance(commissioning_gate, CommissioningGateV1):
            _fail("authenticated commissioning gate is required")
        fixture_identity = fixture_root_identity(
            store.fixture_root, principal_bindings.custody_uid
        )
        principal_identity = fixed_principal_bindings_identity(principal_bindings)
        endpoint = fixed_endpoint_identity(
            store.fixture_root, principal_bindings.custody_uid
        )
        materialization = materialization_identity(
            fixture_identity=fixture_identity,
            principal_identity=principal_identity,
            endpoint_identity=endpoint,
            owner_state_identity=store.root_identity,
        )
        expected = {
            "fixture_root_identity": fixture_identity,
            "principal_bindings_identity": principal_identity,
            "endpoint_identity": endpoint,
            "owner_state_root_identity": store.root_identity,
            "materialization_identity": materialization,
        }
        for field_name, expected_value in expected.items():
            if getattr(commissioning_gate, field_name) != expected_value:
                _fail(f"commissioning gate {field_name} is stale or mismatched")
        self._store = store
        self._bindings = principal_bindings
        self._gate = commissioning_gate
        self._peer_verifier = CustodyPeerCredentialVerifier(principal_bindings)
        self._ledger = RuntimeLedger(store.fixture_root)

    @property
    def ledger_implementation(self) -> type[RuntimeLedger]:
        return type(self._ledger)

    @property
    def construction_adapter_reused_as_operational_consumer(self) -> bool:
        return isinstance(self, P11CaptureReplayAdapter)

    def _authenticate_peer(
        self, connection: socket.socket, operation: CustodyOperation
    ) -> PrincipalRole:
        peer = read_kernel_peer_credentials(connection)
        return self._peer_verifier.authenticate(operation, peer)

    def _validate_authority_sources(
        self,
        act: CanonicalHumanAuthorityActV1,
        correlation: CanonicalCHEEvidenceCorrelationV1,
        input_record: Mapping[str, Any],
        *,
        owner_revision: int,
        now_unix_ns: int,
    ) -> AuthorityBinding:
        validated_act, validated_correlation = (
            P11CaptureReplayAdapter.validate_existing_authority_sources(
                act, correlation
            )
        )
        if validated_act.authority_kind != AUTHORIZATION:
            _fail("operational Human act kind must be AUTHORIZATION")
        if validated_act.authority_scope != OPERATIONAL_AUTHORITY_SCOPE:
            _fail("operational Human act scope is invalid")
        if validated_act.expected_owner != (
            PrincipalRole.AUTHORITY_CUSTODY_PROCESS_PRINCIPAL.value
        ):
            _fail("operational Human act expected owner is invalid")
        if validated_act.target_identity != self._gate.owner_state_root_identity:
            _fail("operational Human act target identity is invalid")
        if validated_act.target_revision != owner_revision:
            _fail("operational Human act target revision is stale")
        payload = validate_operational_act_payload(
            validated_act.payload,
            input_record=input_record,
            gate=self._gate,
            bindings=self._bindings,
            owner_revision=owner_revision,
            now_unix_ns=now_unix_ns,
        )
        correlation_equalities = {
            "interaction_identity": validated_act.interaction_identity,
            "conversation_identity": validated_act.conversation_identity,
            "session_identity": validated_act.session_identity,
            "actor_identity": validated_act.actor_identity,
            "request_identity": validated_act.request_identity,
            "continuation_identity": validated_act.continuation_identity,
            "authority_act_identity": validated_act.authority_act_identity,
            "authority_kind": validated_act.authority_kind,
            "authority_target_identity": validated_act.target_identity,
            "authority_target_revision": validated_act.target_revision,
            "authority_payload_digest": validated_act.payload_digest,
            "owner_state_identity": self._gate.owner_state_root_identity,
            "owner_revision_before": owner_revision,
        }
        for field_name, expected_value in correlation_equalities.items():
            if getattr(validated_correlation, field_name) != expected_value:
                _fail(f"CHE operational {field_name} binding is invalid")
        if input_record["authorization_reference"] != (
            validated_act.authority_act_identity
        ):
            _fail("P11 input authorization reference is invalid")
        expected_caller = (
            f"{PrincipalRole.P11_ORCHESTRATION_CALLER_PRINCIPAL.value}:"
            f"{self._bindings.caller_uid}"
        )
        if input_record["caller_identity_reference"] != expected_caller:
            _fail("P11 input caller identity reference is invalid")
        if input_record["preflight_binding_identity"] != self._gate.gate_identity:
            _fail("P11 input commissioning gate binding is invalid")
        return AuthorityBinding(
            authenticated_caller_principal_identity=expected_caller,
            authority_act_identity=validated_act.authority_act_identity,
            authority_act_content_identity=replay_hash(validated_act.to_dict()),
            authorization_identity=validated_act.authority_act_identity,
            attempt_identity=input_record["attempt_identity"],
            input_record_identity=input_record["record_identity"],
            input_identity=input_record["input_identity"],
            provenance_identity=input_record["provenance_identity"],
            contract_identity=input_record["contract_identity"],
            contract_version=input_record["contract_version"],
            contract_content_sha256=input_record["contract_content_sha256"],
            authorized_scope=OPERATIONAL_AUTHORITY_SCOPE,
            valid_from_unix_ns=payload["valid_from_unix_ns"],
            valid_until_unix_ns=payload["valid_until_unix_ns"],
        )

    def submit_human_act(
        self,
        connection: socket.socket,
        *,
        act: CanonicalHumanAuthorityActV1,
        correlation: CanonicalCHEEvidenceCorrelationV1,
        input_record_canonical_bytes: bytes,
        now_unix_ns: int | None = None,
    ) -> str:
        role = self._authenticate_peer(
            connection, CustodyOperation.SUBMIT_CANONICAL_HUMAN_ACT
        )
        if role is not PrincipalRole.HUMAN_AUTHORITY_ISSUANCE_PRINCIPAL:
            _fail("only the fixed Human issuance principal may submit an act")
        if self._store.current(allow_missing=True) is not None:
            _fail("protected owner-state already contains an authority act")
        input_record = validate_input_record_bytes(input_record_canonical_bytes)
        current_time = time.time_ns() if now_unix_ns is None else now_unix_ns
        binding = self._validate_authority_sources(
            act,
            correlation,
            input_record,
            owner_revision=0,
            now_unix_ns=current_time,
        )
        available = self._store.initialize_available(binding)
        return replay_hash(_state_to_record(available))

    def terminate_human_act(
        self,
        connection: socket.socket,
        *,
        operation: CustodyOperation,
        authority_act_identity: str,
    ) -> str:
        if operation not in {
            CustodyOperation.REQUEST_REVOCATION,
            CustodyOperation.REQUEST_SUPERSESSION,
        }:
            _fail("Human act termination operation is invalid")
        role = self._authenticate_peer(connection, operation)
        if role is not PrincipalRole.HUMAN_AUTHORITY_ISSUANCE_PRINCIPAL:
            _fail("only the fixed Human issuance principal may terminate an act")
        current = self._store.current()
        if current is None or current.state is not OwnerStateName.AVAILABLE:
            _fail("only an AVAILABLE one-use Human act may be terminated")
        if current.binding.authority_act_identity != _identity(
            authority_act_identity, "authority act identity"
        ):
            _fail("Human act termination identity mismatch")
        target = (
            OwnerStateName.REVOKED
            if operation is CustodyOperation.REQUEST_REVOCATION
            else OwnerStateName.SUPERSEDED
        )
        terminated = self._store.terminate_unclaimed(current, target)
        return replay_hash(_state_to_record(terminated))

    def _append_operational_event(
        self, event_type: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        if event_type not in OPERATIONAL_LEDGER_EVENT_TYPES:
            _fail("operational RuntimeLedger event type is invalid")
        return self._ledger.append(
            self._gate.materialization_identity, event_type, payload
        )

    @staticmethod
    def _build_one_output(
        input_record: Mapping[str, Any],
        *,
        authorization_identity: str,
        started_at_unix_ns: int,
        terminal_at_unix_ns: int,
    ) -> bytes:
        outcome = input_record["comparator_outcome"]
        failed_closed = outcome == "FAILED_CLOSED"
        output = {
            "schema_id": OUTPUT_SCHEMA_ID,
            "schema_version": SCHEMA_VERSION,
            "record_kind": OUTPUT_RECORD_KIND,
            "record_identity": "",
            "attempt_identity": input_record["attempt_identity"],
            "input_identity": input_record["input_identity"],
            "input_record_identity": input_record["record_identity"],
            "authorization_identity": authorization_identity,
            "contract_identity": input_record["contract_identity"],
            "contract_version": input_record["contract_version"],
            "contract_content_sha256": input_record["contract_content_sha256"],
            "provenance_identity": input_record["provenance_identity"],
            "outcome": outcome,
            "failure_class_or_reason": (
                "COMPARATOR_FAILED_CLOSED" if failed_closed else None
            ),
            "started_at_unix_ns": started_at_unix_ns,
            "terminal_at_unix_ns": terminal_at_unix_ns,
            "duration_ns": terminal_at_unix_ns - started_at_unix_ns,
            "disposal_completion_proof_identity": (
                replay_hash(
                    {
                        "schema_id": "P11_DA_FAIL_CLOSED_DISPOSAL_PROOF_V1",
                        "attempt_identity": input_record["attempt_identity"],
                        "input_record_identity": input_record["record_identity"],
                    }
                )
                if failed_closed
                else None
            ),
        }
        return bind_record_identity(output)

    def claim_and_invoke_once(
        self,
        connection: socket.socket,
        request: CustodyRequest,
        *,
        act: CanonicalHumanAuthorityActV1,
        correlation: CanonicalCHEEvidenceCorrelationV1,
        input_record_canonical_bytes: bytes,
    ) -> bytes:
        if not isinstance(request, CustodyRequest):
            _fail("closed custody request is required")
        if request.operation is not CustodyOperation.CLAIM_AND_INVOKE_ONCE:
            _fail("custody request operation is not the one bounded invocation")
        if request.canonical_payload != input_record_canonical_bytes:
            _fail("custody request payload is not the exact P11 input")
        role = self._authenticate_peer(
            connection, CustodyOperation.CLAIM_AND_INVOKE_ONCE
        )
        if role is not PrincipalRole.P11_ORCHESTRATION_CALLER_PRINCIPAL:
            _fail("only the fixed P11 caller principal may claim")
        preclaim_time = time.time_ns()
        input_record = validate_input_record_bytes(input_record_canonical_bytes)
        available = self._store.current()
        if available is None or available.state is not OwnerStateName.AVAILABLE:
            _fail("one-use Human act is absent or no longer available")
        if preclaim_time >= available.binding.valid_until_unix_ns:
            self._store.terminate_unclaimed(available, OwnerStateName.EXPIRED)
            _fail("one-use Human act expired before PRECLAIM")
        binding = self._validate_authority_sources(
            act,
            correlation,
            input_record,
            owner_revision=available.revision,
            now_unix_ns=preclaim_time,
        )
        if binding != available.binding:
            _fail("PRECLAIM authority binding differs from protected custody")
        self._append_operational_event(
            "P11_DA_OPERATIONAL_PRECLAIM",
            {
                "attempt_identity": binding.attempt_identity,
                "authority_act_identity": binding.authority_act_identity,
                "commissioning_gate_identity": self._gate.gate_identity,
                "authority_effect": 0,
                "production_routing_effect": 0,
            },
        )
        caller_identity = (
            f"{PrincipalRole.P11_ORCHESTRATION_CALLER_PRINCIPAL.value}:"
            f"{self._bindings.caller_uid}"
        )
        claimed = self._store.claim(
            available,
            claim_time_unix_ns=preclaim_time,
            authenticated_caller_principal_identity=caller_identity,
        )
        try:
            self._append_operational_event(
                "P11_DA_OPERATIONAL_CLAIM",
                {
                    "attempt_identity": binding.attempt_identity,
                    "owner_state_revision": claimed.revision,
                },
            )
            started = time.time_ns()
            serialized_output = self._build_one_output(
                input_record,
                authorization_identity=binding.authorization_identity,
                started_at_unix_ns=started,
                terminal_at_unix_ns=time.time_ns(),
            )
            output = validate_output_record_bytes(
                serialized_output,
                input_record,
                validated_authorization_identity=binding.authorization_identity,
            )
            self._append_operational_event(
                "P11_DA_OPERATIONAL_INVOCATION",
                {
                    "attempt_identity": binding.attempt_identity,
                    "input_record_identity": input_record["record_identity"],
                    "output_record_identity": output["record_identity"],
                    "invocation_count": 1,
                    "automatic_retry_count": 0,
                    "production_route_count": 0,
                },
            )
            consumed = self._store.terminal_bind_and_permanently_exhaust(
                claimed, output
            )
        except BaseException:
            current = self._store.current()
            if current is not None and current.state is OwnerStateName.CLAIMED:
                self._store.mark_reconciliation_required(current)
            raise
        self._append_operational_event(
            "P11_DA_OPERATIONAL_TERMINAL_BIND",
            {
                "attempt_identity": binding.attempt_identity,
                "output_record_identity": consumed.output_record_identity,
                "owner_state_revision": consumed.revision,
            },
        )
        self._append_operational_event(
            "P11_DA_OPERATIONAL_PERMANENT_EXHAUSTION",
            {
                "attempt_identity": binding.attempt_identity,
                "authority_act_identity": binding.authority_act_identity,
                "owner_state": consumed.state.value,
                "reusable": False,
            },
        )
        return serialized_output


assert AUTOMATIC_RETRY_COUNT_V1 == 0
assert INVOCATIONS_PER_CLAIM_V1 == 1
assert OUTPUT_RECORD_COUNT_V1 == 1
assert PRODUCTION_ROUTE_COUNT_V1 == 0
assert len(CH_PRECONDITION_IDS) == 12


__all__ = [
    "AUTHORITY_EFFECT_OUTSIDE_BOUND_ATTEMPT",
    "AUTOMATIC_RETRY_COUNT_V1",
    "CH_PASS_CONJUNCTION",
    "CH_PRECONDITION_IDS",
    "CH_ARTIFACT_SHA256",
    "CH_DECISION_PACKAGE_IDENTITY",
    "COMMISSIONING_GATE_SCHEMA_ID",
    "CommissioningGateV1",
    "CF_SOURCE_GIT_BLOB",
    "CF_SOURCE_SHA256",
    "DH_CHECKPOINT",
    "E01_E12_EXECUTION_AUTHORIZED_IN_G77_256DI",
    "FIXED_OWNER_STATE_DIRECTORY_NAME",
    "INVOCATIONS_PER_CLAIM_V1",
    "OPERATIONAL_ACT_PAYLOAD_FIELDS",
    "OPERATIONAL_AUTHORITY_SCOPE",
    "OPERATIONAL_CONSUMER_IDENTITY",
    "OPERATIONAL_INVOCATION_AUTHORIZED_IN_G77_256DI",
    "OPERATIONAL_LEDGER_EVENT_TYPES",
    "OPERATIONAL_P11_ENTRY_AUTHORIZED_IN_G77_256DI",
    "OUTPUT_RECORD_COUNT_V1",
    "P11BoundedConsumerV1",
    "P12_ENTRY_AUTHORIZED_IN_G77_256DI",
    "PRODUCTION_ROUTE_COUNT_V1",
    "PRODUCTION_ROUTING_AUTHORIZED_IN_G77_256DI",
    "ProtectedOwnerStateStoreV1",
    "create_commissioning_gate_v1",
    "fixed_endpoint_identity",
    "fixed_principal_bindings_identity",
    "fixture_root_identity",
    "materialization_identity",
    "validate_operational_act_payload",
]
