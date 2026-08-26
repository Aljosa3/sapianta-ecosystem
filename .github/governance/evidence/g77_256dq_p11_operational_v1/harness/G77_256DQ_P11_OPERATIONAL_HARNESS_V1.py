#!/usr/bin/env python3
"""One fresh bounded non-production P11 attempt with durable raw evidence."""

from __future__ import annotations

import errno
import hashlib
import json
import os
from pathlib import Path
import signal
import shutil
import socket
import stat
import subprocess
import sys
import time
from typing import Any


SCHEMA_ID = "G77_256DQ_RAW_EXECUTION_EVIDENCE_V1"
GENERATION_ID = "G77_256DQ_ONE_FRESH_BOUNDED_NON_PRODUCTION_G2_E05_P11_GENERATION_V1"
ATTEMPT_ID = "G77_256DQ_G2_E05_ATTEMPT_001"
ACT_ID = "G77_256DQ_EXACT_CURRENT_ONE_USE_HUMAN_OPERATIONAL_ACT_001"
CHECKOUT = Path("/mnt/aigol")
RAW_ROOT = Path("/mnt/g77-evidence")
RAW_PATH = RAW_ROOT / "G77_256DQ_RAW_EXECUTION_EVIDENCE_V1.jsonl"
DQ_HARNESS_PATH = Path("/mnt/dp-harness/G77_256DQ_P11_OPERATIONAL_HARNESS_V1.py")
DN_HARNESS_PATH = Path("/mnt/g77-harness/G77_256DN_P03_DIAGNOSTIC_HARNESS_V1.py")
DN_RAW_PATH = RAW_ROOT / "G77_256DN_P03_RAW_EVIDENCE_V1.jsonl"
DN_SEAL_PATH = RAW_ROOT / "G77_256DN_SPCE_EXECUTION_SEAL_V1.json"
PRE_ACT_SEAL_PATH = RAW_ROOT / "G77_256DQ_PRE_ACT_CHECKPOINT_V1.json"
AUTHORITY_SEAL_PATH = RAW_ROOT / "G77_256DQ_AUTHORITY_CHECKPOINT_V1.json"
GUEST_SEAL_PATH = RAW_ROOT / "G77_256DQ_GUEST_EXECUTION_SEAL_V1.json"
TEARDOWN_SEAL_PATH = RAW_ROOT / "G77_256DQ_GUEST_TEARDOWN_SEAL_V1.json"
CONTINUATION_MANIFEST_PATH = RAW_ROOT / "G77_256DQ_CONTINUATION_MANIFEST_V1.json"
FIXTURE_ROOT = Path("/run/g77-256dq-p11")
ENDPOINT = FIXTURE_ROOT / "p11_da_disposable_custody_v1.sock"
PROTECTED_PROBE = FIXTURE_ROOT / "protected-probe"
PROTECTED_TARGET = PROTECTED_PROBE / "state.json"
ROLE_BINDINGS = {
    "issuance": {"uid": 1, "gid": 1, "groups": [4]},
    "caller": {"uid": 2, "gid": 2, "groups": [4]},
    "custody": {"uid": 3, "gid": 3, "groups": []},
}
ACCEPTED_ERRNOS = {errno.EACCES, errno.EPERM, errno.EROFS}
P04_EFFECTS = ("write", "unlink", "rename", "replace", "chmod", "chown")
SEQUENCE = 0


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def append_record(record_type: str, evidence_class: str, facts: dict[str, Any]) -> str:
    global SEQUENCE
    record = {
        "schema_id": SCHEMA_ID,
        "record_sequence": SEQUENCE,
        "record_type": record_type,
        "evidence_class": evidence_class,
        "facts": facts,
    }
    payload = canonical_bytes(record)
    with RAW_PATH.open("ab", buffering=0) as handle:
        handle.write(payload)
        os.fsync(handle.fileno())
    SEQUENCE += 1
    return "sha256:" + sha256_bytes(payload)


def write_canonical(path: Path, value: dict[str, Any]) -> str:
    payload = canonical_bytes(value)
    path.write_bytes(payload)
    with path.open("rb") as handle:
        os.fsync(handle.fileno())
    return sha256_bytes(payload)


def write_canonical_atomic(path: Path, value: dict[str, Any]) -> str:
    payload = canonical_bytes(value)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        with temporary.open("xb", buffering=0) as handle:
            handle.write(payload)
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        with path.open("rb") as handle:
            os.fsync(handle.fileno())
    finally:
        temporary.unlink(missing_ok=True)
    return sha256_bytes(payload)


def update_continuation_manifest(
    *,
    current_spce_phase: str,
    execution_counters: dict[str, int],
    authority_lifecycle_state: str,
    first_failure_or_current_result: str | None,
    teardown_state: str,
    authorized_next_action: str,
    additional_completed_seals: tuple[dict[str, str], ...] = (),
) -> tuple[str, dict[str, Any]]:
    envelope = json.loads(CONTINUATION_MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest = envelope["manifest"]
    if envelope.get("manifest_sha256") != sha256_bytes(canonical_bytes(manifest)):
        raise RuntimeError("continuation manifest hash mismatch")
    completed = list(manifest["completed_phase_seals"])
    known = {item["identity"] for item in completed}
    for item in additional_completed_seals:
        if item["identity"] not in known:
            completed.append(item)
            known.add(item["identity"])
    manifest.update({
        "current_spce_phase": current_spce_phase,
        "completed_phase_seals": completed,
        "execution_counters": dict(execution_counters),
        "authority_lifecycle_state": authority_lifecycle_state,
        "first_failure_or_current_result": first_failure_or_current_result,
        "teardown_state": teardown_state,
        "authorized_next_action": authorized_next_action,
        "auto_continuable": False,
        "manifest_is_authority": False,
    })
    updated = {
        "schema_id": "G77_256DQ_CONTINUATION_MANIFEST_ENVELOPE_V1",
        "manifest": manifest,
        "manifest_sha256": sha256_bytes(canonical_bytes(manifest)),
    }
    file_sha = write_canonical_atomic(CONTINUATION_MANIFEST_PATH, updated)
    return file_sha, updated


def path_identity(path: Path, missing_ok: bool = False) -> dict[str, Any] | None:
    try:
        value = path.lstat()
    except FileNotFoundError:
        if missing_ok:
            return None
        raise
    if stat.S_ISSOCK(value.st_mode):
        kind = "socket"
    elif stat.S_ISDIR(value.st_mode):
        kind = "directory"
    elif stat.S_ISREG(value.st_mode):
        kind = "regular"
    elif stat.S_ISLNK(value.st_mode):
        kind = "symlink"
    else:
        kind = "other"
    try:
        realpath = str(path.resolve(strict=True))
    except FileNotFoundError:
        realpath = None
    return {
        "path": str(path),
        "realpath": realpath,
        "device": value.st_dev,
        "inode": value.st_ino,
        "type": kind,
        "uid": value.st_uid,
        "gid": value.st_gid,
        "mode": f"{stat.S_IMODE(value.st_mode):04o}",
    }


def run_git(*args: str) -> str:
    return subprocess.run(
        ["git", "-c", f"safe.directory={CHECKOUT}", *args],
        cwd=CHECKOUT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
    ).stdout.strip()


def checkout_context(expected_head: str, expected_tree: str) -> dict[str, Any]:
    mounts = Path("/proc/self/mounts").read_text(encoding="utf-8").splitlines()
    checkout_lines = [line for line in mounts if f" {CHECKOUT} " in line]
    interfaces = sorted(path.name for path in Path("/sys/class/net").iterdir())
    routes = Path("/proc/net/route").read_text(encoding="utf-8").splitlines()
    return {
        "expected_head": expected_head,
        "observed_head": run_git("rev-parse", "HEAD"),
        "expected_tree": expected_tree,
        "observed_tree": run_git("rev-parse", "HEAD^{tree}"),
        "checkout_status_porcelain": run_git("status", "--porcelain"),
        "checkout_mount_lines": checkout_lines,
        "checkout_mount_read_only": bool(checkout_lines)
        and all("ro" in line.split()[3].split(",") for line in checkout_lines),
        "checkout_statvfs_read_only": bool(os.statvfs(CHECKOUT).f_flag & os.ST_RDONLY),
        "guest_mount_table": mounts,
        "interfaces": interfaces,
        "route_table": routes,
        "production_route_count": sum(
            1 for line in routes[1:] if line.strip() and not line.split()[0] == "lo"
        ),
        "guest_os_release": Path("/etc/os-release").read_text(encoding="utf-8").splitlines(),
    }


def drop_role(role: str) -> None:
    binding = ROLE_BINDINGS[role]
    os.setgroups(binding["groups"])
    os.setgid(binding["gid"])
    os.setuid(binding["uid"])


def role_identity(role: str) -> dict[str, Any]:
    read_fd, write_fd = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(read_fd)
        try:
            drop_role(role)
            payload = {
                "role": role,
                "pid": os.getpid(),
                "uid": os.getuid(),
                "gid": os.getgid(),
                "groups": os.getgroups(),
            }
            os.write(write_fd, canonical_bytes(payload))
        finally:
            os.close(write_fd)
            os._exit(0)
    os.close(write_fd)
    raw = b""
    while True:
        chunk = os.read(read_fd, 65536)
        if not chunk:
            break
        raw += chunk
    os.close(read_fd)
    waited, status_value = os.waitpid(pid, 0)
    if waited != pid or status_value != 0:
        raise RuntimeError(f"role identity child failed: {role}")
    return json.loads(raw)


def p04_source(role: str, effect: str) -> Path | None:
    if effect in {"rename", "replace"}:
        return PROTECTED_PROBE / f".{role}-{effect}-source"
    return None


def p04_probe_child(role: str, effect: str, write_fd: int) -> None:
    try:
        drop_role(role)
        source = p04_source(role, effect)
        target_before = path_identity(PROTECTED_TARGET)
        source_before = path_identity(source, True) if source else None
        succeeded = False
        number = 0
        name = "NONE"
        try:
            if effect == "write":
                with PROTECTED_TARGET.open("a", encoding="utf-8") as handle:
                    handle.write("forbidden")
            elif effect == "unlink":
                PROTECTED_TARGET.unlink()
            elif effect == "rename":
                source.rename(PROTECTED_TARGET)
            elif effect == "replace":
                os.replace(source, PROTECTED_TARGET)
            elif effect == "chmod":
                os.chmod(PROTECTED_TARGET, 0o666)
            elif effect == "chown":
                os.chown(PROTECTED_TARGET, os.getuid(), os.getgid())
            succeeded = True
        except OSError as exc:
            number = int(exc.errno or 0)
            name = errno.errorcode.get(number, "UNKNOWN")
        target_after = path_identity(PROTECTED_TARGET, True)
        source_after = path_identity(source, True) if source else None
        preserved = target_after is not None and all(
            target_after[key] == target_before[key] for key in ("device", "inode", "type")
        )
        payload = {
            "role": role,
            "effect": effect,
            "actor": {
                "pid": os.getpid(),
                "uid": os.getuid(),
                "gid": os.getgid(),
                "groups": os.getgroups(),
            },
            "parent_before": path_identity(PROTECTED_PROBE),
            "target_before": target_before,
            "source_before": source_before,
            "source_same_device": (
                source_before is not None and source_before["device"] == target_before["device"]
            ) if source else None,
            "operation_succeeded": succeeded,
            "errno_number": number,
            "errno_symbolic_name": name,
            "source_after": source_after,
            "target_after": target_after,
            "target_identity_preserved": preserved,
            "accepted_denial": (not succeeded and number in ACCEPTED_ERRNOS and preserved),
        }
        os.write(write_fd, canonical_bytes(payload))
    finally:
        os.close(write_fd)
        os._exit(0)


def p04_probe(role: str, effect: str) -> dict[str, Any]:
    source = p04_source(role, effect)
    if source:
        source.write_text("same-filesystem-source", encoding="utf-8")
        os.chown(source, ROLE_BINDINGS[role]["uid"], ROLE_BINDINGS[role]["gid"])
        os.chmod(source, 0o600)
    read_fd, write_fd = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(read_fd)
        p04_probe_child(role, effect, write_fd)
    os.close(write_fd)
    raw = b""
    while True:
        chunk = os.read(read_fd, 65536)
        if not chunk:
            break
        raw += chunk
    os.close(read_fd)
    waited, status_value = os.waitpid(pid, 0)
    if waited != pid or status_value != 0:
        raise RuntimeError(f"P04 child failed: {role}/{effect}")
    return json.loads(raw)


def connect_as_role(role: str, endpoint: Path) -> tuple[int, int]:
    ready_read, ready_write = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(ready_read)
        try:
            drop_role(role)
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(str(endpoint))
            os.write(ready_write, b"1")
            try:
                client.recv(1)
            except OSError:
                pass
            client.close()
        finally:
            os.close(ready_write)
            os._exit(0)
    os.close(ready_write)
    return pid, ready_read


def accept_peer(server: socket.socket, role: str) -> tuple[dict[str, Any], socket.socket, int]:
    pid, ready_read = connect_as_role(role, ENDPOINT)
    connection, _ = server.accept()
    os.read(ready_read, 1)
    os.close(ready_read)
    raw = connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12)
    import struct
    peer_pid, peer_uid, peer_gid = struct.unpack("3i", raw)
    return {"role": role, "pid": peer_pid, "uid": peer_uid, "gid": peer_gid}, connection, pid


def finish_client(connection: socket.socket, pid: int) -> None:
    try:
        connection.sendall(b"1")
    except OSError:
        pass
    connection.close()
    os.waitpid(pid, 0)


def send_message(channel: socket.socket, value: dict[str, Any]) -> None:
    channel.sendall(canonical_bytes(value))


def receive_message(reader: Any) -> dict[str, Any]:
    line = reader.readline()
    if not line:
        raise RuntimeError("custody control channel closed")
    return json.loads(line)


def create_input_and_authority(gate: Any, bindings: Any, store: Any) -> tuple[Any, ...]:
    from aigol.runtime.canonical_che_evidence_correlation_contract_v1 import (
        CANONICAL_CHE_EVIDENCE_CORRELATION_CONTRACT_VERSION,
        NOT_APPLICABLE,
        RECORDED,
        create_canonical_che_evidence_correlation_v1,
    )
    from aigol.runtime.canonical_human_authority_act_contract_v1 import (
        AUTHORIZATION,
        CANONICAL_HUMAN_AUTHORITY_ACT_CONTRACT_VERSION,
        HUMAN_AUTHORITY_OWNER,
        CanonicalHumanAuthorityActV1,
        canonical_human_authority_payload_digest_v1,
    )
    from aigol.runtime.transport.serialization import replay_hash
    from p11_da_disposable_substrate_v1 import bind_record_identity, validate_input_record_bytes

    contract_hash = replay_hash({"contract": "G77_256DQ_G2_E05_FAIL_CLOSED_AUTHORITY_V1"})
    input_value = {
        "schema_id": "SAPIANTA_P11_BOUNDED_CONSUMER_INPUT_V1",
        "schema_version": "1.0.0",
        "record_kind": "P11_BOUNDED_CONSUMER_INPUT",
        "record_identity": "",
        "attempt_identity": ATTEMPT_ID,
        "input_identity": "G77_256DQ_G2_E05_INPUT_001",
        "provenance_identity": "G77_256DQ_AUTHENTICATED_DP_CD_MINIMUM_PROVENANCE_V1",
        "contract_identity": "G77_256DQ_G2_E05_FAIL_CLOSED_AUTHORITY_CONTRACT_V1",
        "contract_version": "1.0.0",
        "contract_content_sha256": contract_hash,
        "authorization_reference": ACT_ID,
        "caller_identity_reference": f"P11_ORCHESTRATION_CALLER_PRINCIPAL:{bindings.caller_uid}",
        "preflight_binding_identity": gate.gate_identity,
        "preflight_status": "PASSED",
        "p10_inventory_identity": "G77_256DQ_P10_ONE_ATTEMPT_ZERO_RETRY_INVENTORY_V1",
        "comparator_outcome_identity": "G77_256DQ_G2_E05_EQUAL_OUTCOME_001",
        "comparator_outcome": "EQUAL",
        "replay_context_identity": "G77_256DQ_EXISTING_RUNTIMELEDGER_REPLAY_CONTEXT_V1",
    }
    input_bytes = bind_record_identity(input_value)
    input_record = validate_input_record_bytes(input_bytes)
    now = time.time_ns()
    valid_from = now - 1_000_000_000
    valid_until = now + 300_000_000_000
    payload = {
        "decision_package_identity": gate.ch_decision_package_identity,
        "decision_package_sha256": gate.ch_artifact_sha256,
        "cg_checkpoint": gate.cg_checkpoint,
        "cg_report_identity": gate.cg_report_identity,
        "cd_plan_identity": gate.cd_plan_identity,
        "cd_plan_sha256": gate.cd_plan_sha256,
        "cf_source_tree_identity": gate.cf_source_tree_identity,
        "materialization_identity": gate.materialization_identity,
        "evidence_obligation_id": "P11-E05",
        "case_id": "G2_E05_EXACT_CURRENT_AVAILABLE_ONE_WINNING_CLAIM_001",
        "evidence_run_identity": "G77_256DQ_EVIDENCE_RUN_001",
        "caller_role": "P11_ORCHESTRATION_CALLER_PRINCIPAL",
        "caller_uid": bindings.caller_uid,
        "custody_role": "AUTHORITY_CUSTODY_PROCESS_PRINCIPAL",
        "custody_uid": bindings.custody_uid,
        "fixed_endpoint_identity": gate.endpoint_identity,
        "protected_owner_state_root_identity": gate.owner_state_root_identity,
        "protected_owner_state_revision": 0,
        "attempt_identity": ATTEMPT_ID,
        "input_record_identity": input_record["record_identity"],
        "input_payload_identity": input_record["input_identity"],
        "contract_identity": input_record["contract_identity"],
        "contract_version": input_record["contract_version"],
        "contract_content_sha256": input_record["contract_content_sha256"],
        "allowed_operation": "CLAIM_AND_INVOKE_ONCE",
        "maximum_attempts": 1,
        "automatic_retries": 0,
        "maximum_duration_ns": 10_000_000_000,
        "authority_effect_outside_bound_attempt": 0,
        "production_routing_effect": 0,
        "valid_from_unix_ns": valid_from,
        "valid_until_unix_ns": valid_until,
        "terminal_consumption_and_non_reuse": "REQUIRED",
        "required_disposal": "REQUIRED",
        "minimum_retention": "CD_AUTHORIZED_MINIMUM_TRAIL_PLUS_DQ_RAW_PREIMAGE",
    }
    payload_digest = canonical_human_authority_payload_digest_v1(payload)
    act = CanonicalHumanAuthorityActV1(
        contract_version=CANONICAL_HUMAN_AUTHORITY_ACT_CONTRACT_VERSION,
        authority_act_identity=ACT_ID,
        authority_kind=AUTHORIZATION,
        interaction_identity="G77_256DQ_INTERACTION_001",
        conversation_identity="G77_256DQ_CONVERSATION_001",
        session_identity="G77_256DQ_SESSION_001",
        actor_identity="HUMAN_CONSTITUTIONAL_AUTHORITY",
        request_identity="G77_256DQ_REQUEST_001",
        continuation_identity="G77_256DQ_CONTINUATION_001",
        target_identity=gate.owner_state_root_identity,
        target_revision=0,
        producing_owner=HUMAN_AUTHORITY_OWNER,
        expected_owner="AUTHORITY_CUSTODY_PROCESS_PRINCIPAL",
        authority_scope="P11_DA_ONE_BOUNDED_OPERATIONAL_ATTEMPT_V1",
        payload=payload,
        payload_digest=payload_digest,
        metadata={
            "generation_identity": GENERATION_ID,
            "human_authorization_source": "G77_256DQ_CURRENT_PROMPT",
            "non_transferable": True,
            "non_reusable": True,
            "machine_completed_human_semantics": 0,
        },
    )
    correlation = create_canonical_che_evidence_correlation_v1(
        contract_version=CANONICAL_CHE_EVIDENCE_CORRELATION_CONTRACT_VERSION,
        interaction_identity=act.interaction_identity,
        conversation_identity=act.conversation_identity,
        session_identity=act.session_identity,
        workspace_identity="SAPIANTA_WORKSPACE",
        runtime_scope_identity=GENERATION_ID,
        actor_identity=act.actor_identity,
        source_channel_identity="G77_256DQ_HUMAN_AUTHORIZATION_CHANNEL",
        adapter_identity="G77_256DQ_CANONICAL_BINDING_ADAPTER",
        request_identity=act.request_identity,
        che_entry_identity="G77_256DQ_CHE_ENTRY_001",
        source_act_identity=act.authority_act_identity,
        source_act_digest=replay_hash(act.to_dict()),
        order_identity="G77_256DQ_ORDER_001",
        idempotency_identity="G77_256DQ_IDEMPOTENCY_001",
        continuation_identity=act.continuation_identity,
        continuation_sequence=1,
        authority_act_identity=act.authority_act_identity,
        authority_kind=act.authority_kind,
        authority_requesting_owner_identity=act.expected_owner,
        authority_target_identity=act.target_identity,
        authority_target_revision=act.target_revision,
        authority_payload_digest=act.payload_digest,
        authority_result_identity="G77_256DQ_AUTHORITY_RESULT_001",
        opaque_reference_set_identity=NOT_APPLICABLE,
        ordered_reference_set_digest=NOT_APPLICABLE,
        opaque_reference_correlations=(),
        producing_owner_identity=HUMAN_AUTHORITY_OWNER,
        owner_state_identity=gate.owner_state_root_identity,
        owner_revision_before=0,
        owner_revision_after=1,
        owner_advancement="ADVANCED",
        owner_disposition="RECORDED",
        next_act_identity=NOT_APPLICABLE,
        refusal_identity=NOT_APPLICABLE,
        terminal_identity=NOT_APPLICABLE,
        owner_projection_identity="G77_256DQ_OWNER_PROJECTION_001",
        failure_identity=NOT_APPLICABLE,
        presentation_identity="G77_256DQ_PRESENTATION_001",
        response_identity="G77_256DQ_RESPONSE_001",
        response_digest=replay_hash({"response": "G77_256DQ_AUTHORITY_RECORDED"}),
        delivery_record_identity="G77_256DQ_DELIVERY_001",
        delivery_status=NOT_APPLICABLE,
        duplicate_resolution=NOT_APPLICABLE,
        acknowledgement_state=NOT_APPLICABLE,
        replay_references=(),
        replay_status=NOT_APPLICABLE,
        certification_references=(),
        certification_status=NOT_APPLICABLE,
        evidence_status=RECORDED,
        metadata={"generation_identity": GENERATION_ID},
    )
    return input_bytes, input_record, act, correlation


def custody_process(
    control: socket.socket,
    server: socket.socket,
    condition_evidence: tuple[tuple[str, str], ...],
) -> None:
    try:
        drop_role("custody")
        sys.path.insert(0, str(CHECKOUT))
        sys.path.insert(0, str(CHECKOUT / "tests"))
        from p11_da_custody_process_v1 import (
            CustodyOperation,
            CustodyRequest,
            FixedPrincipalBindings,
        )
        from p11_da_operational_consumer_v1 import (
            CH_PASS_CONJUNCTION,
            P11BoundedConsumerV1,
            ProtectedOwnerStateStoreV1,
            create_commissioning_gate_v1,
            fixed_endpoint_identity,
            fixed_principal_bindings_identity,
            fixture_root_identity,
            materialization_identity,
        )
        bindings = FixedPrincipalBindings(1, 2, 3)
        store = ProtectedOwnerStateStoreV1(FIXTURE_ROOT, 3)
        fixture_identity = fixture_root_identity(FIXTURE_ROOT, 3)
        principal_identity = fixed_principal_bindings_identity(bindings)
        endpoint_identity = fixed_endpoint_identity(FIXTURE_ROOT, 3)
        materialization = materialization_identity(
            fixture_identity=fixture_identity,
            principal_identity=principal_identity,
            endpoint_identity=endpoint_identity,
            owner_state_identity=store.root_identity,
        )
        gate = create_commissioning_gate_v1(
            dh_checkpoint="9f5fd37212547cf06b664c94152ae0ec50a55b79",
            ch_decision_package_identity=(
                "G77_256CH_P11_E01_E12_OPERATIONAL_EVIDENCE_GENERATION_"
                "HUMAN_AUTHORIZATION_DECISION_PACKAGE_V1"
            ),
            ch_artifact_sha256="d07f6eae99abd6f95b37553c84eb226298e40e5c61f42f5597980d784a16e2ce",
            cg_checkpoint="bccbb46a65ebc0de7a0c421e4c871b8487d3bb0c",
            cg_report_identity=(
                "G77_256CG_P11_IMPLEMENTED_DISPOSABLE_D_A_TEST_SUBSTRATE_"
                "INDEPENDENT_VALIDATION_AND_OPERATIONAL_EVIDENCE_AUTHORIZATION_"
                "READINESS_ASSESSMENT_V1"
            ),
            cd_plan_identity=(
                "G77_256CD_P11_PRE_IMPLEMENTATION_EVIDENCE_GENERATION_AND_"
                "VALIDATION_PLAN_V1"
            ),
            cd_plan_sha256="666162ed94c5b291c1694230cbdc2ea040ba2165817f3c325fe2979fe993b670",
            cf_source_tree_identity="bb5382994b266e53358acb286ef06f41ce2936e6",
            cf_source_sha256="a1b58fa8ddedb5058393aa23d815262c92c8b185c0b193764f77420313af0bab",
            materialization_identity=materialization,
            fixture_root_identity=fixture_identity,
            principal_bindings_identity=principal_identity,
            endpoint_identity=endpoint_identity,
            owner_state_root_identity=store.root_identity,
            condition_results=CH_PASS_CONJUNCTION,
            condition_evidence_identities=condition_evidence,
        )
        consumer = P11BoundedConsumerV1(
            store=store,
            principal_bindings=bindings,
            commissioning_gate=gate,
        )
        send_message(control, {
            "message_type": "GATE_READY",
            "gate": gate.identity_preimage() | {"gate_identity": gate.gate_identity},
            "store_root": str(store.root),
            "store_root_identity": store.root_identity,
            "materialization_identity": materialization,
        })
        reader = control.makefile("r", encoding="utf-8")
        if receive_message(reader)["command"] != "CREATE_ACT":
            raise RuntimeError("pre-act checkpoint acknowledgement missing")
        input_bytes, input_record, act, correlation = create_input_and_authority(
            gate, bindings, store
        )
        send_message(control, {
            "message_type": "ACT_CREATED",
            "input_record": input_record,
            "input_canonical_utf8": input_bytes.decode("utf-8"),
            "human_authority_act": act.to_dict(),
            "che_correlation": correlation.to_dict(),
        })
        if receive_message(reader)["command"] != "SUBMIT_ACT":
            raise RuntimeError("act creation acknowledgement missing")
        issuance_connection, _ = server.accept()
        available_identity = consumer.submit_human_act(
            issuance_connection,
            act=act,
            correlation=correlation,
            input_record_canonical_bytes=input_bytes,
        )
        issuance_connection.sendall(b"1")
        issuance_connection.close()
        available = store.current()
        send_message(control, {
            "message_type": "ACT_SUBMITTED",
            "available_state_identity": available_identity,
            "available_state": {
                "state": available.state.value,
                "revision": available.revision,
                "binding": {
                    field: getattr(available.binding, field)
                    for field in available.binding.__dataclass_fields__
                },
            },
            "owner_revision_files": [
                json.loads(path.read_text(encoding="utf-8"))
                for path in sorted(store.root.iterdir())
            ],
        })
        if receive_message(reader)["command"] != "INVOKE_ONCE":
            raise RuntimeError("authority checkpoint acknowledgement missing")
        caller_connection, _ = server.accept()
        request = CustodyRequest(
            protocol_identity="P11_DA_DISPOSABLE_LOCAL_IPC_V1",
            operation=CustodyOperation.CLAIM_AND_INVOKE_ONCE,
            request_identity="G77_256DQ_CUSTODY_REQUEST_001",
            canonical_payload=input_bytes,
        )
        output_bytes = consumer.claim_and_invoke_once(
            caller_connection,
            request,
            act=act,
            correlation=correlation,
            input_record_canonical_bytes=input_bytes,
        )
        caller_connection.sendall(b"1")
        caller_connection.close()
        current = store.current()
        ledger_path = (
            FIXTURE_ROOT / "runtime_replay" /
            f"runtime_{gate.materialization_identity}_ledger.jsonl"
        )
        ledger_entries = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines()]
        send_message(control, {
            "message_type": "ATTEMPT_COMPLETE",
            "output_canonical_utf8": output_bytes.decode("utf-8"),
            "output_record": json.loads(output_bytes),
            "owner_state": {
                "state": current.state.value,
                "revision": current.revision,
                "output_record_identity": current.output_record_identity,
                "outcome": current.outcome,
            },
            "owner_revision_files": [
                json.loads(path.read_text(encoding="utf-8"))
                for path in sorted(store.root.iterdir())
            ],
            "runtime_ledger_entries": ledger_entries,
            "runtime_ledger_canonical_utf8": ledger_path.read_text(encoding="utf-8"),
        })
        reader.close()
        control.close()
        server.close()
        os._exit(0)
    except BaseException as exc:
        try:
            send_message(control, {
                "message_type": "CUSTODY_FAILURE",
                "error_type": type(exc).__name__,
                "error": str(exc),
            })
        finally:
            os._exit(111)


def main() -> int:
    if len(sys.argv) != 6:
        raise SystemExit("expected DQ_HARNESS_SHA SCHEMA_SHA HEAD TREE DN_HARNESS_SHA")
    expected_harness, schema_sha, expected_head, expected_tree, dn_harness_sha = sys.argv[1:]
    RAW_ROOT.mkdir(parents=True, exist_ok=True)
    expected_absent = (
        RAW_PATH, DN_RAW_PATH, DN_SEAL_PATH, PRE_ACT_SEAL_PATH,
        AUTHORITY_SEAL_PATH, GUEST_SEAL_PATH, TEARDOWN_SEAL_PATH,
    )
    if any(path.exists() for path in expected_absent):
        raise SystemExit("DQ evidence sink is not empty")
    if not CONTINUATION_MANIFEST_PATH.is_file():
        raise SystemExit("DQ continuation manifest is absent")
    first_failure: str | None = None
    counters = {
        "vm_creation_count": 1,
        "vm_boot_count": 1,
        "automatic_retry_count": 0,
        "second_vm_count": 0,
        "human_operational_act_creation_count": 0,
        "human_operational_act_claimed_count": 0,
        "human_operational_act_invoked_count": 0,
        "human_operational_act_terminally_bound_count": 0,
        "human_operational_act_permanently_exhausted_count": 0,
        "p11_entry_count": 0,
        "p11_operational_invocation_count": 0,
        "e01_e12_execution_count": 0,
        "g2_e05_execution_count": 0,
        "p12_entry_count": 0,
        "production_route_count": 0,
    }
    server: socket.socket | None = None
    custody_pid: int | None = None
    parent_control: socket.socket | None = None
    reader: Any | None = None
    condition_evidence: list[tuple[str, str]] = []
    try:
        actual_harness = sha256_path(DQ_HARNESS_PATH)
        if actual_harness != expected_harness:
            raise RuntimeError("DQ harness hash mismatch")
        context = checkout_context(expected_head, expected_tree)
        if not all((
            context["observed_head"] == expected_head,
            context["observed_tree"] == expected_tree,
            context["checkout_status_porcelain"] == "",
            context["checkout_mount_read_only"],
            context["checkout_statvfs_read_only"],
            context["interfaces"] == ["lo"],
            context["production_route_count"] == 0,
        )):
            raise RuntimeError("checkout or no-production context gate failed")
        manifest_file_sha, manifest_envelope = update_continuation_manifest(
            current_spce_phase="PHASE_B_VM_BOOTED_FRESH_COMMISSIONING",
            execution_counters=counters,
            authority_lifecycle_state="NOT_CREATED",
            first_failure_or_current_result=None,
            teardown_state="PENDING",
            authorized_next_action="RUN_FRESH_P01_P12_THEN_STOP_ON_FIRST_FAILURE",
        )
        append_record("execution_context", "EVIDENCE", {
            "generation_identity": GENERATION_ID,
            "expected_harness_sha256": expected_harness,
            "observed_harness_sha256": actual_harness,
            "evidence_schema_sha256": schema_sha,
            "historical_dl_gap_state": "KNOWN_UNRECOVERABLE_HISTORICAL_EVIDENCE_GAP",
            "dn_current_p03_result": "PASS__PROSPECTIVE_ONLY",
            "clrec_state": "CANDIDATE_ONLY__NOT_CERTIFIED",
            "continuation_manifest_file_sha256": manifest_file_sha,
            "continuation_manifest_sha256": manifest_envelope["manifest_sha256"],
            "checkout_context": context,
        })

        # P01: exact three distinct live UIDs.
        identities = [role_identity(role) for role in ("issuance", "caller", "custody")]
        p01_pass = len({item["uid"] for item in identities}) == 3 and [
            item["uid"] for item in identities
        ] == [1, 2, 3]
        evidence_id = append_record("commissioning_P01", "EVIDENCE", {
            "requirement": "EXACT_THREE_DISTINCT_LIVE_OS_PRINCIPALS",
            "live_roles": identities,
            "result": "PASS" if p01_pass else "FAIL",
        })
        if not p01_pass:
            raise RuntimeError("P01 failed")
        condition_evidence.append(("P01", evidence_id))

        FIXTURE_ROOT.mkdir(mode=0o750)
        os.chown(FIXTURE_ROOT, 3, 4)
        os.chmod(FIXTURE_ROOT, 0o750)
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(str(ENDPOINT))
        server.listen(8)
        os.chown(ENDPOINT, 3, 4)
        os.chmod(ENDPOINT, 0o660)

        # P02: fixed custody endpoint.
        parent_id = path_identity(FIXTURE_ROOT)
        endpoint_id = path_identity(ENDPOINT)
        p02_pass = all((
            parent_id["uid"] == 3, parent_id["gid"] == 4, parent_id["mode"] == "0750",
            endpoint_id["uid"] == 3, endpoint_id["gid"] == 4,
            endpoint_id["mode"] == "0660", endpoint_id["type"] == "socket",
        ))
        evidence_id = append_record("commissioning_P02", "EVIDENCE", {
            "requirement": "FIXED_ENDPOINT_CUSTODY_OWNERSHIP",
            "endpoint_parent": parent_id,
            "endpoint": endpoint_id,
            "protocol": "P11_DA_DISPOSABLE_LOCAL_IPC_V1",
            "result": "PASS" if p02_pass else "FAIL",
        })
        if not p02_pass:
            raise RuntimeError("P02 failed")
        condition_evidence.append(("P02", evidence_id))

        # P03: reuse the exact retained DN corrected instrument prospectively.
        dn_status = subprocess.run([
            "/usr/bin/python3", str(DN_HARNESS_PATH), dn_harness_sha,
            "a812d9163f67aa37fabd281de418bf29a7b6a3fd22a0066e5de02c8107f90a84",
            expected_head, expected_tree,
        ], timeout=360).returncode
        dn_records = [json.loads(line) for line in DN_RAW_PATH.read_text(encoding="utf-8").splitlines()]
        dn_aggregate = next(item for item in dn_records if item["record_type"] == "aggregate")
        p03_pass = dn_status == 0 and dn_aggregate["result"].startswith("PASS__")
        evidence_id = append_record("commissioning_P03", "EVIDENCE", {
            "requirement": "CALLER_AND_ISSUER_ENDPOINT_REPLACEMENT_ACCESS_ABSENT",
            "dn_instrument_scope": "CURRENT_DQ_ENVIRONMENT_PROSPECTIVE_ONLY",
            "dn_raw_sha256": sha256_path(DN_RAW_PATH),
            "dn_guest_seal_sha256": sha256_path(DN_SEAL_PATH),
            "aggregate_preimage": dn_aggregate,
            "result": "PASS" if p03_pass else "FAIL",
        })
        if not p03_pass:
            raise RuntimeError("P03 failed")
        condition_evidence.append(("P03", evidence_id))

        # P04: protected custody state denial matrix.
        PROTECTED_PROBE.mkdir(mode=0o750)
        os.chown(PROTECTED_PROBE, 3, 4)
        os.chmod(PROTECTED_PROBE, 0o750)
        PROTECTED_TARGET.write_text("protected-owner-state", encoding="utf-8")
        os.chown(PROTECTED_TARGET, 3, 3)
        os.chmod(PROTECTED_TARGET, 0o600)
        probes = [
            p04_probe(role, effect)
            for role in ("issuance", "caller")
            for effect in P04_EFFECTS
        ]
        p04_pass = len(probes) == 12 and all(item["accepted_denial"] for item in probes)
        evidence_id = append_record("commissioning_P04", "EVIDENCE", {
            "requirement": "PROTECTED_OWNER_STATE_CUSTODY_AND_NON_REPLACEABILITY",
            "probe_count": len(probes),
            "raw_probes": probes,
            "result": "PASS" if p04_pass else "FAIL",
        })
        if not p04_pass:
            raise RuntimeError("P04 failed")
        condition_evidence.append(("P04", evidence_id))
        shutil.rmtree(PROTECTED_PROBE)

        # P05: live SO_PEERCRED and exact operation-role map.
        sys.path.insert(0, str(CHECKOUT / "tests"))
        sys.path.insert(0, str(CHECKOUT))
        from p11_da_custody_process_v1 import (
            CustodyOperation, CustodyPeerCredentialVerifier,
            FixedPrincipalBindings, PeerCredentials,
        )
        bindings = FixedPrincipalBindings(1, 2, 3)
        verifier = CustodyPeerCredentialVerifier(bindings)
        allowed = {
            "issuance": CustodyOperation.SUBMIT_CANONICAL_HUMAN_ACT,
            "caller": CustodyOperation.CLAIM_AND_INVOKE_ONCE,
            "custody": CustodyOperation.READ_ONLY_AUDIT,
        }
        live_peers: list[dict[str, Any]] = []
        captured: dict[str, PeerCredentials] = {}
        for role in ("issuance", "caller", "custody"):
            peer, connection, client_pid = accept_peer(server, role)
            credential = PeerCredentials(peer["pid"], peer["uid"], peer["gid"])
            authenticated_role = verifier.authenticate(allowed[role], credential).value
            peer["operation"] = allowed[role].value
            peer["authenticated_role"] = authenticated_role
            live_peers.append(peer)
            captured[role] = credential
            finish_client(connection, client_pid)
        wrong_denials: list[dict[str, Any]] = []
        for role, credential in captured.items():
            for other_role, operation in allowed.items():
                if role == other_role:
                    continue
                denied = False
                try:
                    verifier.authenticate(operation, credential)
                except Exception:
                    denied = True
                wrong_denials.append({
                    "peer_role": role,
                    "attempted_operation": operation.value,
                    "denied": denied,
                })
        p05_pass = len(live_peers) == 3 and all(item["denied"] for item in wrong_denials)
        evidence_id = append_record("commissioning_P05", "EVIDENCE", {
            "requirement": "LIVE_ROLE_BOUND_SO_PEERCRED",
            "allowed_live_reads": live_peers,
            "wrong_role_denials": wrong_denials,
            "result": "PASS" if p05_pass else "FAIL",
        })
        if not p05_pass:
            raise RuntimeError("P05 failed")
        condition_evidence.append(("P05", evidence_id))

        from p11_da_custody_process_v1 import CUSTODY_REQUEST_FIELDS, FORBIDDEN_REQUEST_SELECTION_FIELDS
        from p11_da_disposable_substrate_v1 import ConstructionOnlyConsumerStub, D3_PHASE_SEQUENCE
        from p11_da_operational_consumer_v1 import (
            AUTOMATIC_RETRY_COUNT_V1, INVOCATIONS_PER_CLAIM_V1,
            OPERATIONAL_LEDGER_EVENT_TYPES, P11BoundedConsumerV1,
            PRODUCTION_ROUTE_COUNT_V1,
        )

        p06_pass = not (CUSTODY_REQUEST_FIELDS & FORBIDDEN_REQUEST_SELECTION_FIELDS)
        evidence_id = append_record("commissioning_P06", "EVIDENCE", {
            "request_fields": sorted(CUSTODY_REQUEST_FIELDS),
            "forbidden_selection_fields": sorted(FORBIDDEN_REQUEST_SELECTION_FIELDS),
            "intersection": sorted(CUSTODY_REQUEST_FIELDS & FORBIDDEN_REQUEST_SELECTION_FIELDS),
            "result": "PASS" if p06_pass else "FAIL",
        })
        if not p06_pass:
            raise RuntimeError("P06 failed")
        condition_evidence.append(("P06", evidence_id))

        p07_pass = (
            ConstructionOnlyConsumerStub.operational_p11_entry is False
            and P11BoundedConsumerV1.operational_p11_entry is True
            and not issubclass(P11BoundedConsumerV1, ConstructionOnlyConsumerStub)
        )
        evidence_id = append_record("commissioning_P07", "EVIDENCE", {
            "construction_stub_operational_entry": ConstructionOnlyConsumerStub.operational_p11_entry,
            "operational_consumer_entry": P11BoundedConsumerV1.operational_p11_entry,
            "consumer_inherits_construction_stub": issubclass(P11BoundedConsumerV1, ConstructionOnlyConsumerStub),
            "result": "PASS" if p07_pass else "FAIL",
        })
        if not p07_pass:
            raise RuntimeError("P07 failed")
        condition_evidence.append(("P07", evidence_id))

        p08_pass = ConstructionOnlyConsumerStub.authority_effect == 0
        evidence_id = append_record("commissioning_P08", "EVIDENCE", {
            "detached_construction_authority_effect": ConstructionOnlyConsumerStub.authority_effect,
            "result": "PASS" if p08_pass else "FAIL",
        })
        if not p08_pass:
            raise RuntimeError("P08 failed")
        condition_evidence.append(("P08", evidence_id))

        p09_pass = len(OPERATIONAL_LEDGER_EVENT_TYPES) == 5
        evidence_id = append_record("commissioning_P09", "EVIDENCE", {
            "operational_event_types": sorted(OPERATIONAL_LEDGER_EVENT_TYPES),
            "construction_events_used_as_satisfying_evidence": False,
            "result": "PASS" if p09_pass else "FAIL",
        })
        if not p09_pass:
            raise RuntimeError("P09 failed")
        condition_evidence.append(("P09", evidence_id))

        p10_pass = (
            [item.value for item in D3_PHASE_SEQUENCE] == [
                "PRECLAIM", "CLAIM", "ONE_BOUNDED_INVOCATION",
                "TERMINAL_BIND", "PERMANENT_EXHAUSTION",
            ]
            and AUTOMATIC_RETRY_COUNT_V1 == 0
            and INVOCATIONS_PER_CLAIM_V1 == 1
            and PRODUCTION_ROUTE_COUNT_V1 == 0
        )
        evidence_id = append_record("commissioning_P10", "EVIDENCE", {
            "phase_sequence": [item.value for item in D3_PHASE_SEQUENCE],
            "automatic_retry_count": AUTOMATIC_RETRY_COUNT_V1,
            "invocations_per_claim": INVOCATIONS_PER_CLAIM_V1,
            "production_route_count": PRODUCTION_ROUTE_COUNT_V1,
            "result": "PASS" if p10_pass else "FAIL",
        })
        if not p10_pass:
            raise RuntimeError("P10 failed")
        condition_evidence.append(("P10", evidence_id))

        p11_pass = all(counters[key] == 0 for key in (
            "human_operational_act_creation_count", "human_operational_act_claimed_count",
            "p11_entry_count", "p11_operational_invocation_count",
        ))
        evidence_id = append_record("commissioning_P11", "HUMAN_DECISION", {
            "generation_authorization": "PRESENT__EXACT_DQ_ONLY",
            "one_use_attempt_authorization": "PRESENT__MAY_BE_CREATED_ONLY_AFTER_THIS_GATE",
            "act_created_before_gate": False,
            "result": "PASS" if p11_pass else "FAIL",
        })
        if not p11_pass:
            raise RuntimeError("P11 commissioning gate failed")
        condition_evidence.append(("P11", evidence_id))

        p12_pass = context["interfaces"] == ["lo"] and context["production_route_count"] == 0
        evidence_id = append_record("commissioning_P12", "NOT_AUTHORIZED", {
            "interfaces": context["interfaces"],
            "route_table": context["route_table"],
            "production_route_count": context["production_route_count"],
            "p12_entry_authorized": False,
            "result": "PASS" if p12_pass else "FAIL",
        })
        if not p12_pass:
            raise RuntimeError("P12 commissioning gate failed")
        condition_evidence.append(("P12", evidence_id))

        # Custody process creates the protected store and gate, then pauses.
        parent_control, child_control = socket.socketpair()
        custody_pid = os.fork()
        if custody_pid == 0:
            parent_control.close()
            custody_process(child_control, server, tuple(condition_evidence))
        child_control.close()
        server.close()
        server = None
        reader = parent_control.makefile("r", encoding="utf-8")
        gate_message = receive_message(reader)
        if gate_message["message_type"] != "GATE_READY":
            raise RuntimeError(f"custody failed before gate: {gate_message}")
        append_record("commissioning_aggregate", "EVIDENCE", {
            "condition_results": [[f"P{number:02d}", "PASS"] for number in range(1, 13)],
            "condition_evidence_identities": condition_evidence,
            "gate": gate_message["gate"],
            "materialization_identity": gate_message["materialization_identity"],
            "act_creation_count": 0,
            "p11_entry_count": 0,
            "result": "PASS__12_OF_12__ACT_NOT_CREATED",
        })
        preact = {
            "schema_id": "G77_256DQ_PRE_ACT_CHECKPOINT_V1",
            "generation_identity": GENERATION_ID,
            "source_head": expected_head,
            "source_tree": expected_tree,
            "completed_gates": [f"P{number:02d}" for number in range(1, 13)],
            "pending_gates": ["CREATE_ONE_USE_ACT", "SUBMIT", "PRECLAIM", "CLAIM", "ONE_INVOCATION", "TERMINAL_BIND", "PERMANENT_EXHAUSTION", "TEARDOWN"],
            "authority_disposition": "GENERATION_AUTHORIZED__ACT_AUTHORIZED_BUT_NOT_CREATED",
            "raw_evidence_prefix_sha256": sha256_path(RAW_PATH),
            "raw_record_count": SEQUENCE,
            "harness_sha256": expected_harness,
            "environment_identity": gate_message["materialization_identity"],
            "execution_counters": counters,
            "first_failure": None,
            "teardown_state": "PENDING",
            "checkpoint_is_authority": False,
            "continuation": "SAME_LIVE_DQ_GENERATION_ONLY__NO_REPLAY__NO_AUTHORITY_TRANSFER",
        }
        preact_sha = write_canonical(PRE_ACT_SEAL_PATH, preact)
        append_record("spce_pre_act_checkpoint", "EVIDENCE", {
            "path": str(PRE_ACT_SEAL_PATH), "sha256": preact_sha, "preimage": preact,
        })
        manifest_file_sha, manifest_envelope = update_continuation_manifest(
            current_spce_phase="PHASE_B_P01_P12_PASS_PRE_ACT",
            execution_counters=counters,
            authority_lifecycle_state="AUTHORIZED_BUT_NOT_CREATED",
            first_failure_or_current_result="PASS__P01_P12_12_OF_12__ACT_NOT_CREATED",
            teardown_state="PENDING",
            authorized_next_action="SAME_LIVE_GENERATION_ONLY__CREATE_EXACT_ONE_USE_ACT",
            additional_completed_seals=({
                "identity": "G77_256DQ_PRE_ACT_CHECKPOINT_V1",
                "sha256": preact_sha,
            },),
        )
        append_record("continuation_manifest_pre_act", "EVIDENCE", {
            "path": str(CONTINUATION_MANIFEST_PATH),
            "file_sha256": manifest_file_sha,
            "manifest_sha256": manifest_envelope["manifest_sha256"],
            "current_spce_phase": manifest_envelope["manifest"]["current_spce_phase"],
            "manifest_is_authority": False,
        })
        send_message(parent_control, {"command": "CREATE_ACT"})

        act_message = receive_message(reader)
        if act_message["message_type"] != "ACT_CREATED":
            raise RuntimeError(f"custody failed creating act: {act_message}")
        counters["human_operational_act_creation_count"] = 1
        append_record("human_operational_act_created", "HUMAN_DECISION", {
            **act_message,
            "creation_count": 1,
            "non_transferable": True,
            "non_reusable": True,
        })
        send_message(parent_control, {"command": "SUBMIT_ACT"})
        issuance_pid, issuance_ready = connect_as_role("issuance", ENDPOINT)
        os.read(issuance_ready, 1)
        os.close(issuance_ready)
        submitted = receive_message(reader)
        os.waitpid(issuance_pid, 0)
        if submitted["message_type"] != "ACT_SUBMITTED":
            raise RuntimeError(f"custody failed submitting act: {submitted}")
        append_record("human_operational_act_available", "EVIDENCE", submitted)
        authority_seal = {
            "schema_id": "G77_256DQ_AUTHORITY_CHECKPOINT_V1",
            "generation_identity": GENERATION_ID,
            "attempt_identity": ATTEMPT_ID,
            "authority_act_identity": ACT_ID,
            "authority_act_preimage": act_message["human_authority_act"],
            "che_correlation_preimage": act_message["che_correlation"],
            "input_record_preimage": act_message["input_record"],
            "owner_state_preimage": submitted["available_state"],
            "raw_evidence_prefix_sha256": sha256_path(RAW_PATH),
            "raw_record_count": SEQUENCE,
            "completed_gates": ["P01-P12", "ACT_CREATE", "ACT_SUBMIT_AVAILABLE"],
            "pending_gates": ["PRECLAIM", "CLAIM", "ONE_INVOCATION", "TERMINAL_BIND", "PERMANENT_EXHAUSTION", "TEARDOWN"],
            "execution_counters": counters,
            "first_failure": None,
            "teardown_state": "PENDING",
            "checkpoint_is_authority": False,
            "continuation": "EXACT_CURRENT_ACT_AVAILABLE_ONLY_INSIDE_SAME_LIVE_DQ_GENERATION__NO_TRANSFER_OR_REPLAY",
        }
        authority_sha = write_canonical(AUTHORITY_SEAL_PATH, authority_seal)
        append_record("spce_authority_checkpoint", "EVIDENCE", {
            "path": str(AUTHORITY_SEAL_PATH), "sha256": authority_sha, "preimage": authority_seal,
        })
        manifest_file_sha, manifest_envelope = update_continuation_manifest(
            current_spce_phase="PHASE_B_EXACT_ONE_USE_ACT_AVAILABLE_LIVE_ONLY",
            execution_counters=counters,
            authority_lifecycle_state="AVAILABLE_REVISION_0__NON_TRANSFERABLE__LIVE_GENERATION_ONLY",
            first_failure_or_current_result="ACT_CREATED_AND_SUBMITTED_AVAILABLE__ZERO_INVOCATIONS",
            teardown_state="PENDING",
            authorized_next_action="SAME_LIVE_GENERATION_ONLY__CLAIM_AND_INVOKE_ONCE__FRESH_SESSION_MUST_NOT_RESUME_ACT",
            additional_completed_seals=({
                "identity": "G77_256DQ_AUTHORITY_CHECKPOINT_V1",
                "sha256": authority_sha,
            },),
        )
        append_record("continuation_manifest_authority", "EVIDENCE", {
            "path": str(CONTINUATION_MANIFEST_PATH),
            "file_sha256": manifest_file_sha,
            "manifest_sha256": manifest_envelope["manifest_sha256"],
            "current_spce_phase": manifest_envelope["manifest"]["current_spce_phase"],
            "manifest_is_authority": False,
        })
        send_message(parent_control, {"command": "INVOKE_ONCE"})
        caller_pid, caller_ready = connect_as_role("caller", ENDPOINT)
        os.read(caller_ready, 1)
        os.close(caller_ready)
        result = receive_message(reader)
        os.waitpid(caller_pid, 0)
        if result["message_type"] != "ATTEMPT_COMPLETE":
            raise RuntimeError(f"custody failed operational attempt: {result}")
        waited, custody_status = os.waitpid(custody_pid, 0)
        custody_pid = None
        if waited <= 0 or custody_status != 0:
            raise RuntimeError("custody process did not terminate cleanly")
        parent_control.close()
        parent_control = None
        reader.close()
        reader = None
        counters.update({
            "human_operational_act_claimed_count": 1,
            "human_operational_act_invoked_count": 1,
            "human_operational_act_terminally_bound_count": 1,
            "human_operational_act_permanently_exhausted_count": 1,
            "p11_entry_count": 1,
            "p11_operational_invocation_count": 1,
            "e01_e12_execution_count": 1,
            "g2_e05_execution_count": 1,
        })
        append_record("p11_attempt_result", "FACT", {
            **result,
            "attempt_identity": ATTEMPT_ID,
            "authority_act_identity": ACT_ID,
            "evidence_obligation_id": "P11-E05",
            "case_id": "G2_E05_EXACT_CURRENT_AVAILABLE_ONE_WINNING_CLAIM_001",
            "e05_positive_baseline": {
                "initial_owner_state": "AVAILABLE",
                "initial_owner_revision": 0,
                "winning_claim_count": 1,
                "competing_claim_count": 0,
                "return_to_available": False,
                "terminal_owner_state": "CONSUMED",
                "terminal_owner_revision": 2,
            },
            "execution_counters": counters,
            "result": "PASS__ONE_EXACT_CURRENT_AVAILABLE_ACT__ONE_WINNING_G2_E05_CLAIM__EQUAL_ZERO_ROUTING_OUTPUT__ACT_CONSUMED",
        })
        guest_seal = {
            "schema_id": "G77_256DQ_GUEST_EXECUTION_SEAL_V1",
            "generation_identity": GENERATION_ID,
            "source_head": expected_head,
            "source_tree": expected_tree,
            "completed_gates": [
                "P01-P12", "ACT_CREATE", "ACT_SUBMIT", "PRECLAIM", "CLAIM",
                "ONE_BOUNDED_INVOCATION", "TERMINAL_BIND", "PERMANENT_EXHAUSTION",
            ],
            "pending_gates": ["TEARDOWN", "G48_FINALIZATION"],
            "authority_disposition": "ACT_TERMINALLY_BOUND_AND_PERMANENTLY_EXHAUSTED__NON_REUSABLE",
            "evidence_obligation_id": "P11-E05",
            "case_id": "G2_E05_EXACT_CURRENT_AVAILABLE_ONE_WINNING_CLAIM_001",
            "operational_result": "PASS__ONE_EXACT_CURRENT_AVAILABLE_ACT__ONE_WINNING_G2_E05_CLAIM__EQUAL_ZERO_ROUTING_OUTPUT__ACT_CONSUMED",
            "execution_counters": counters,
            "raw_evidence_prefix_sha256": sha256_path(RAW_PATH),
            "raw_record_count": SEQUENCE,
            "pre_act_checkpoint_sha256": preact_sha,
            "authority_checkpoint_sha256": authority_sha,
            "harness_sha256": expected_harness,
            "environment_identity": gate_message["materialization_identity"],
            "first_failure": None,
            "teardown_state": "PENDING",
            "checkpoint_is_authority": False,
            "continuation": "RESULT_RECONSTRUCTION_ONLY__NO_SECOND_ATTEMPT__NO_P12__NO_PRODUCTION",
        }
        guest_seal_sha = write_canonical(GUEST_SEAL_PATH, guest_seal)
        append_record("spce_guest_execution_seal", "EVIDENCE", {
            "path": str(GUEST_SEAL_PATH), "sha256": guest_seal_sha, "preimage": guest_seal,
        })
        manifest_file_sha, manifest_envelope = update_continuation_manifest(
            current_spce_phase="PHASE_C_EXECUTION_COMPLETE_PENDING_GUEST_TEARDOWN",
            execution_counters=counters,
            authority_lifecycle_state="CONSUMED_REVISION_2__PERMANENTLY_EXHAUSTED",
            first_failure_or_current_result="PASS__G2_E05_POSITIVE_BASELINE__ONE_WINNING_CLAIM__ACT_CONSUMED",
            teardown_state="PENDING",
            authorized_next_action="TEARDOWN_AND_FINALIZATION_ONLY__NO_EXECUTION_REPLAY",
            additional_completed_seals=({
                "identity": "G77_256DQ_GUEST_EXECUTION_SEAL_V1",
                "sha256": guest_seal_sha,
            },),
        )
        append_record("continuation_manifest_post_execution", "EVIDENCE", {
            "path": str(CONTINUATION_MANIFEST_PATH),
            "file_sha256": manifest_file_sha,
            "manifest_sha256": manifest_envelope["manifest_sha256"],
            "current_spce_phase": manifest_envelope["manifest"]["current_spce_phase"],
            "manifest_is_authority": False,
        })
        return 0
    except BaseException as exc:
        first_failure = f"{type(exc).__name__}: {exc}"
        append_record("first_failure", "FACT", {
            "first_failure": first_failure,
            "execution_counters": counters,
            "repair_count": 0,
            "automatic_retry_count": 0,
        })
        return 40
    finally:
        if server is not None:
            server.close()
        if reader is not None:
            reader.close()
        if parent_control is not None:
            parent_control.close()
        if custody_pid is not None:
            try:
                os.kill(custody_pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                os.waitpid(custody_pid, 0)
            except ChildProcessError:
                pass
        shutil.rmtree(FIXTURE_ROOT, ignore_errors=True)
        teardown_facts = {
            "fixture_root_absent": not FIXTURE_ROOT.exists(),
            "execution_counters": counters,
            "first_failure": first_failure,
            "teardown_state": "COMPLETE" if not FIXTURE_ROOT.exists() else "FAILED",
        }
        append_record("guest_teardown", "FACT", teardown_facts)
        teardown_seal = {
            "schema_id": "G77_256DQ_GUEST_TEARDOWN_SEAL_V1",
            "generation_identity": GENERATION_ID,
            "raw_evidence_sha256": sha256_path(RAW_PATH),
            "raw_record_count": SEQUENCE,
            "execution_counters": counters,
            "first_failure": first_failure,
            "teardown_state": teardown_facts["teardown_state"],
            "checkpoint_is_authority": False,
            "continuation": "FINALIZATION_ONLY__NO_EXECUTION_REPLAY__NO_ADDITIONAL_ATTEMPT",
        }
        teardown_seal_sha = write_canonical(TEARDOWN_SEAL_PATH, teardown_seal)
        if first_failure is None and counters["g2_e05_execution_count"] == 1:
            authority_state = "CONSUMED_REVISION_2__PERMANENTLY_EXHAUSTED"
            current_result = "PASS__G2_E05_POSITIVE_BASELINE__GUEST_TEARDOWN_COMPLETE"
        elif counters["human_operational_act_creation_count"] == 0:
            authority_state = "NOT_CREATED__NO_AUTHORITY_SURVIVES"
            current_result = first_failure
        else:
            authority_state = "LIVE_AUTHORITY_TERMINATED_WITH_DISPOSABLE_GUEST__NON_TRANSFERABLE__NO_AUTHORITY_SURVIVES"
            current_result = first_failure
        update_continuation_manifest(
            current_spce_phase="PHASE_D_GUEST_TEARDOWN_COMPLETE_PENDING_HOST_FINALIZATION",
            execution_counters=counters,
            authority_lifecycle_state=authority_state,
            first_failure_or_current_result=current_result,
            teardown_state=teardown_facts["teardown_state"],
            authorized_next_action="HOST_AUTHENTICATION_FINAL_SEAL_AND_TRANSIENT_TEARDOWN_ONLY__NO_EXECUTION",
            additional_completed_seals=({
                "identity": "G77_256DQ_GUEST_TEARDOWN_SEAL_V1",
                "sha256": teardown_seal_sha,
            },),
        )


if __name__ == "__main__":
    raise SystemExit(main())
