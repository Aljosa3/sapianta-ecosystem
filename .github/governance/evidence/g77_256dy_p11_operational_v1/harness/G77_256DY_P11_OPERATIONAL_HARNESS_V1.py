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
import struct
import subprocess
import sys
import time
from typing import Any


SCHEMA_ID = "G77_256DY_RAW_EXECUTION_EVIDENCE_V1"
GENERATION_ID = "G77_256DY_ONE_FRESH_BOUNDED_NON_PRODUCTION_E05_UNKNOWN_AUTHORITY_P11_GENERATION_V1"
ATTEMPT_ID = "G77_256DY_E05_UNKNOWN_AUTHORITY_ATTEMPT_001"
UNKNOWN_AUTHORITY_REFERENCE = "G77_256DY_UNKNOWN_AUTHORITY_REFERENCE_001"
CASE_ID = "G77_256DY_E05_UNKNOWN_AUTHORITY_DENIAL_BEFORE_ATTEMPT_001"
CHECKOUT = Path("/mnt/aigol")
RAW_ROOT = Path("/mnt/g77-evidence")
RAW_PATH = RAW_ROOT / "G77_256DY_RAW_EXECUTION_EVIDENCE_V1.jsonl"
DY_HARNESS_PATH = Path("/mnt/dp-harness/G77_256DY_P11_OPERATIONAL_HARNESS_V1.py")
DN_HARNESS_PATH = Path("/mnt/g77-harness/G77_256DN_P03_DIAGNOSTIC_HARNESS_V1.py")
DN_RAW_PATH = RAW_ROOT / "G77_256DN_P03_RAW_EVIDENCE_V1.jsonl"
DN_SEAL_PATH = RAW_ROOT / "G77_256DN_SPCE_EXECUTION_SEAL_V1.json"
PRE_ACT_SEAL_PATH = RAW_ROOT / "G77_256DY_PRE_ACT_CHECKPOINT_V1.json"
GUEST_SEAL_PATH = RAW_ROOT / "G77_256DY_GUEST_EXECUTION_SEAL_V1.json"
TEARDOWN_SEAL_PATH = RAW_ROOT / "G77_256DY_GUEST_TEARDOWN_SEAL_V1.json"
CONTINUATION_MANIFEST_PATH = RAW_ROOT / "G77_256DY_CONTINUATION_MANIFEST_V1.json"
FIXTURE_ROOT = Path("/run/g77-256dy-p11")
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
    if envelope.get("schema_id") != "SAPIANTA_SPCE_CONTINUATION_MANIFEST_ENVELOPE_V1":
        raise RuntimeError("canonical continuation manifest envelope mismatch")
    if envelope.get("manifest_sha256") != sha256_bytes(canonical_bytes(manifest)):
        raise RuntimeError("continuation manifest hash mismatch")
    if manifest.get("schema_id") != "SAPIANTA_SPCE_CONTINUATION_MANIFEST_V1":
        raise RuntimeError("canonical continuation manifest identity mismatch")
    if manifest.get("manifest_version") != "1.0.0":
        raise RuntimeError("canonical continuation manifest version mismatch")

    canonical_execution_counters = {
        "automatic_retry_count": execution_counters["automatic_retry_count"],
        "commissioning_execution_count": execution_counters["p01_p12_executed_count"],
        "commissioning_pass_count": execution_counters["p01_p12_pass_count"],
        "execution_replay_count": execution_counters["execution_replay_count"],
        "full_history_reconstruction_count": execution_counters["full_history_reconstruction_count"],
        "human_operational_act_claimed_count": execution_counters["human_operational_act_claimed_count"],
        "human_operational_act_created_count": execution_counters["human_operational_act_creation_count"],
        "human_operational_act_invoked_count": execution_counters["human_operational_act_invoked_count"],
        "human_operational_act_permanently_exhausted_count": execution_counters["human_operational_act_permanently_exhausted_count"],
        "human_operational_act_submitted_count": execution_counters["human_operational_act_submitted_count"],
        "human_operational_act_terminally_bound_count": execution_counters["human_operational_act_terminally_bound_count"],
        "p11_entry_count": execution_counters["p11_entry_count"],
        "p11_operational_invocation_count": execution_counters["p11_operational_invocation_count"],
        "p12_entry_count": execution_counters["p12_entry_count"],
        "production_route_count": execution_counters["production_route_count"],
        "repair_and_continue_count": execution_counters["repair_and_continue_count"],
        "second_vm_count": execution_counters["second_vm_count"],
        "vm_boot_count": execution_counters["vm_boot_count"],
        "vm_creation_count": execution_counters["vm_creation_count"],
    }
    case_counters = {
        "e01_e12_execution_count": execution_counters["e01_e12_execution_count"],
        "e05_case_execution_count": execution_counters["e05_case_execution_count"],
        "e05_concurrency_contender_count": execution_counters["e05_concurrency_contender_count"],
        "e05_concurrency_loser_count": execution_counters["e05_concurrency_loser_count"],
        "e05_concurrency_winner_count": execution_counters["e05_concurrency_winner_count"],
        "p01_p12_executed_count": execution_counters["p01_p12_executed_count"],
        "p01_p12_pass_count": execution_counters["p01_p12_pass_count"],
    }
    if authority_lifecycle_state == "NOT_CREATED":
        authority_state = {
            "lifecycle_state": "NOT_CREATED", "act_identity": None,
            "owner_revision": None, "authority_survives": False,
            "transferable": False, "reusable": False,
        }
    else:
        authority_state = {
            "lifecycle_state": "NO_AUTHORITY_SURVIVES", "act_identity": None,
            "owner_revision": None, "authority_survives": False,
            "transferable": False, "reusable": False,
        }

    observations = list(manifest.get("observations", []))
    for item in additional_completed_seals:
        observation = (
            f"GUEST_CHECKPOINT_RECORDED__{item['identity']}__SHA256_{item['sha256']}"
        )
        if observation not in observations:
            observations.append(observation)
    continuation_mode = (
        "FINALIZATION_ONLY"
        if authorized_next_action.startswith(("TEARDOWN", "HOST_AUTHENTICATION"))
        else "SAME_LIVE_GENERATION_ONLY"
    )
    manifest.update({
        "current_spce_phase": current_spce_phase,
        "phase_sequence": manifest["phase_sequence"] + 1,
        "execution_counters": canonical_execution_counters,
        "case_counters": case_counters,
        "authority_state": authority_state,
        "first_failure_or_current_result": first_failure_or_current_result,
        "teardown_state": teardown_state,
        "frontier_state": {
            "constitutional_frontier": "ONE_AUTHORIZED_DY_E05_UNKNOWN_AUTHORITY_GENERATION",
            "exact_next_legal_action": authorized_next_action,
            "continuation_mode": continuation_mode,
            "requires_human_review": True,
        },
        "auto_continuable": False,
        "checkpoint_is_authority": False,
        "manifest_is_authority": False,
        "observations": observations,
    })
    updated = {
        "schema_id": "SAPIANTA_SPCE_CONTINUATION_MANIFEST_ENVELOPE_V1",
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


def create_unknown_input(gate: Any, bindings: Any) -> tuple[bytes, dict[str, Any]]:
    """Create one input that references no submitted or authoritative act."""
    from aigol.runtime.transport.serialization import replay_hash
    from p11_da_disposable_substrate_v1 import bind_record_identity, validate_input_record_bytes

    contract_hash = replay_hash(
        {"contract": "G77_256DY_E05_UNKNOWN_AUTHORITY_FAIL_CLOSED_V1"}
    )
    input_value = {
        "schema_id": "SAPIANTA_P11_BOUNDED_CONSUMER_INPUT_V1",
        "schema_version": "1.0.0",
        "record_kind": "P11_BOUNDED_CONSUMER_INPUT",
        "record_identity": "",
        "attempt_identity": ATTEMPT_ID,
        "input_identity": "G77_256DY_E05_UNKNOWN_AUTHORITY_INPUT_001",
        "provenance_identity": "G77_256DY_AUTHENTICATED_CD_DX_MINIMUM_PROVENANCE_V1",
        "contract_identity": "G77_256DY_E05_UNKNOWN_AUTHORITY_FAIL_CLOSED_CONTRACT_V1",
        "contract_version": "1.0.0",
        "contract_content_sha256": contract_hash,
        "authorization_reference": UNKNOWN_AUTHORITY_REFERENCE,
        "caller_identity_reference": (
            f"P11_ORCHESTRATION_CALLER_PRINCIPAL:{bindings.caller_uid}"
        ),
        "preflight_binding_identity": gate.gate_identity,
        "preflight_status": "PASSED",
        "p10_inventory_identity": "G77_256DY_P10_ONE_DENIAL_ZERO_RETRY_INVENTORY_V1",
        "comparator_outcome_identity": "G77_256DY_E05_UNKNOWN_AUTHORITY_DENIAL_OUTCOME_001",
        "comparator_outcome": "FAILED_CLOSED",
        "replay_context_identity": "G77_256DY_EXISTING_RUNTIMELEDGER_REPLAY_CONTEXT_V1",
    }
    input_bytes = bind_record_identity(input_value)
    return input_bytes, validate_input_record_bytes(input_bytes)


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
        command = receive_message(reader)["command"]
        if command == "INVOKE_UNKNOWN_AUTHORITY":
            input_bytes, input_record = create_unknown_input(gate, bindings)
            connection, _ = server.accept()
            raw_peer = connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12)
            peer_pid, peer_uid, peer_gid = struct.unpack("3i", raw_peer)
            request = CustodyRequest(
                protocol_identity="P11_DA_DISPOSABLE_LOCAL_IPC_V1",
                operation=CustodyOperation.CLAIM_AND_INVOKE_ONCE,
                request_identity="G77_256DY_CUSTODY_REQUEST_001",
                canonical_payload=input_bytes,
            )
            allowed = False
            output_canonical_utf8 = None
            denial_error_type = None
            denial_error = None
            try:
                output_bytes = consumer.claim_and_invoke_once(
                    connection,
                    request,
                    act=None,  # type: ignore[arg-type]
                    correlation=None,  # type: ignore[arg-type]
                    input_record_canonical_bytes=input_bytes,
                )
                allowed = True
                output_canonical_utf8 = output_bytes.decode("utf-8")
                connection.sendall(b"1")
            except BaseException as exc:
                denial_error_type = type(exc).__name__
                denial_error = str(exc)
                connection.sendall(b"0")
            finally:
                connection.close()
            owner_state = store.current(allow_missing=True)
            owner_revision_files = [
                json.loads(path.read_text(encoding="utf-8"))
                for path in sorted(store.root.iterdir())
            ]
            ledger_root = FIXTURE_ROOT / "runtime_replay"
            denial_pass = all((
                not allowed,
                denial_error_type == "FailClosedRuntimeError",
                denial_error == "protected owner-state is not initialized",
                owner_state is None,
                owner_revision_files == [],
                not ledger_root.exists(),
            ))
            send_message(control, {
                "message_type": "UNKNOWN_AUTHORITY_COMPLETE",
                "case_id": CASE_ID,
                "selected_e05_vector": "UNKNOWN",
                "request_identity": request.request_identity,
                "unknown_authority_reference": UNKNOWN_AUTHORITY_REFERENCE,
                "input_record": input_record,
                "input_canonical_utf8": input_bytes.decode("utf-8"),
                "peer_credentials": {
                    "pid": peer_pid, "uid": peer_uid, "gid": peer_gid,
                },
                "denial_point": "D2_PROTECTED_AUTHORITY_RESOLUTION_BEFORE_PRECLAIM",
                "denial_error_type": denial_error_type,
                "denial_error": denial_error,
                "operational_authority_obtained": allowed,
                "output_canonical_utf8": output_canonical_utf8,
                "authoritative_owner_state_before": None,
                "authoritative_owner_state_after": None,
                "owner_revision_files": owner_revision_files,
                "runtime_ledger_root_exists": ledger_root.exists(),
                "runtime_ledger_entry_count": 0,
                "claim_attempted": False,
                "invocation_attempted": False,
                "denial_invariant_pass": denial_pass,
            })
            reader.close()
            control.close()
            server.close()
            os._exit(0 if denial_pass else 112)
        raise RuntimeError("unknown-authority execution command missing")
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
        raise SystemExit("expected DY_HARNESS_SHA SCHEMA_SHA HEAD TREE DN_HARNESS_SHA")
    expected_harness, schema_sha, expected_head, expected_tree, dn_harness_sha = sys.argv[1:]
    RAW_ROOT.mkdir(parents=True, exist_ok=True)
    expected_absent = (
        RAW_PATH, DN_RAW_PATH, DN_SEAL_PATH, PRE_ACT_SEAL_PATH,
        GUEST_SEAL_PATH, TEARDOWN_SEAL_PATH,
    )
    if any(path.exists() for path in expected_absent):
        raise SystemExit("DY evidence sink is not empty")
    if not CONTINUATION_MANIFEST_PATH.is_file():
        raise SystemExit("DY continuation manifest is absent")
    first_failure: str | None = None
    counters = {
        "vm_creation_count": 1,
        "vm_boot_count": 1,
        "automatic_retry_count": 0,
        "repair_and_continue_count": 0,
        "second_vm_count": 0,
        "human_operational_act_creation_count": 0,
        "human_operational_act_submitted_count": 0,
        "human_operational_act_claimed_count": 0,
        "human_operational_act_invoked_count": 0,
        "human_operational_act_terminally_bound_count": 0,
        "human_operational_act_permanently_exhausted_count": 0,
        "p11_entry_count": 0,
        "p11_operational_invocation_count": 0,
        "e01_e12_execution_count": 0,
        "p01_p12_executed_count": 0,
        "p01_p12_pass_count": 0,
        "e05_case_execution_count": 0,
        "e05_concurrency_contender_count": 0,
        "e05_concurrency_winner_count": 0,
        "e05_concurrency_loser_count": 0,
        "p12_entry_count": 0,
        "production_route_count": 0,
        "full_history_reconstruction_count": 0,
        "execution_replay_count": 0,
    }
    server: socket.socket | None = None
    custody_pid: int | None = None
    parent_control: socket.socket | None = None
    reader: Any | None = None
    condition_evidence: list[tuple[str, str]] = []
    try:
        actual_harness = sha256_path(DY_HARNESS_PATH)
        if actual_harness != expected_harness:
            raise RuntimeError("DY harness hash mismatch")
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
            "dn_instrument_scope": "CURRENT_DY_ENVIRONMENT_PROSPECTIVE_ONLY",
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
            "generation_authorization": "PRESENT__EXACT_DY_UNKNOWN_AUTHORITY_CASE_ONLY",
            "one_use_attempt_authorization": "NOT_REQUIRED__NO_ACT_MAY_BE_CREATED_FOR_UNKNOWN_VECTOR",
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
        counters["p01_p12_executed_count"] = 1
        counters["p01_p12_pass_count"] = 1

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
            "schema_id": "G77_256DY_PRE_ACT_CHECKPOINT_V1",
            "generation_identity": GENERATION_ID,
            "source_head": expected_head,
            "source_tree": expected_tree,
            "completed_gates": [f"P{number:02d}" for number in range(1, 13)],
            "pending_gates": ["ONE_UNKNOWN_AUTHORITY_RESOLUTION_DENIAL", "TEARDOWN"],
            "authority_disposition": "NO_ACT_AUTHORIZED_OR_CREATED__UNKNOWN_REFERENCE_IS_NOT_AUTHORITY",
            "raw_evidence_prefix_sha256": sha256_path(RAW_PATH),
            "raw_record_count": SEQUENCE,
            "harness_sha256": expected_harness,
            "environment_identity": gate_message["materialization_identity"],
            "execution_counters": counters,
            "first_failure": None,
            "teardown_state": "PENDING",
            "checkpoint_is_authority": False,
            "continuation": "SAME_LIVE_DY_GENERATION_ONLY__NO_REPLAY__NO_AUTHORITY_TRANSFER",
        }
        preact_sha = write_canonical(PRE_ACT_SEAL_PATH, preact)
        append_record("spce_pre_act_checkpoint", "EVIDENCE", {
            "path": str(PRE_ACT_SEAL_PATH), "sha256": preact_sha, "preimage": preact,
        })
        manifest_file_sha, manifest_envelope = update_continuation_manifest(
            current_spce_phase="PHASE_B_P01_P12_PASS_PRE_ACT",
            execution_counters=counters,
            authority_lifecycle_state="NOT_CREATED",
            first_failure_or_current_result="PASS__P01_P12_12_OF_12__ACT_NOT_CREATED",
            teardown_state="PENDING",
            authorized_next_action="SAME_LIVE_GENERATION_ONLY__SUBMIT_ONE_UNKNOWN_REFERENCE_FOR_FAIL_CLOSED_RESOLUTION",
            additional_completed_seals=({
                "identity": "G77_256DY_PRE_ACT_CHECKPOINT_V1",
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
        send_message(parent_control, {"command": "INVOKE_UNKNOWN_AUTHORITY"})
        caller_pid, caller_ready = connect_as_role("caller", ENDPOINT)
        os.read(caller_ready, 1)
        os.close(caller_ready)
        result = receive_message(reader)
        os.waitpid(caller_pid, 0)
        if result["message_type"] != "UNKNOWN_AUTHORITY_COMPLETE":
            raise RuntimeError(f"custody failed unknown-authority case: {result}")
        waited, custody_status = os.waitpid(custody_pid, 0)
        custody_pid = None
        if waited <= 0 or custody_status != 0:
            raise RuntimeError("custody process did not terminate cleanly")
        parent_control.close()
        parent_control = None
        reader.close()
        reader = None
        counters.update({
            "p11_entry_count": 1,
            "p11_operational_invocation_count": 0,
            "e01_e12_execution_count": 1,
            "e05_case_execution_count": 1,
        })
        if not result["denial_invariant_pass"]:
            raise RuntimeError("E05 unknown-authority denial invariant failed")
        append_record("p11_attempt_result", "FACT", {
            **result,
            "attempt_identity": ATTEMPT_ID,
            "authority_act_identity": None,
            "evidence_obligation_id": "P11-E05",
            "case_id": CASE_ID,
            "selected_e05_vector": "UNKNOWN",
            "authority_resolution": {
                "submitted_authority_act_count": 0,
                "unknown_reference_count": 1,
                "authoritative_owner_state_before": None,
                "authoritative_owner_state_after": None,
                "claim_attempted": False,
                "invocation_attempted": False,
                "unauthorized_effect_count": 0,
            },
            "execution_counters": counters,
            "result": "PASS__UNKNOWN_AUTHORITY_REJECTED_AT_D2_RESOLUTION_BEFORE_PRECLAIM__NO_ACT_CLAIM_INVOCATION_LEDGER_OR_ROUTING_EFFECT",
        })
        guest_seal = {
            "schema_id": "G77_256DY_GUEST_EXECUTION_SEAL_V1",
            "generation_identity": GENERATION_ID,
            "source_head": expected_head,
            "source_tree": expected_tree,
            "completed_gates": [
                "P01-P12", "UNKNOWN_AUTHORITY_RESOLUTION_DENIAL",
                "ZERO_UNAUTHORIZED_EFFECT",
            ],
            "pending_gates": ["TEARDOWN", "G48_FINALIZATION"],
            "authority_disposition": "NO_HUMAN_ACT_CREATED__UNKNOWN_REFERENCE_NEVER_BECAME_AUTHORITY",
            "evidence_obligation_id": "P11-E05",
            "case_id": CASE_ID,
            "selected_e05_vector": "UNKNOWN",
            "operational_result": "PASS__UNKNOWN_AUTHORITY_DENIED_BEFORE_PRECLAIM_WITH_ZERO_EFFECT",
            "execution_counters": counters,
            "raw_evidence_prefix_sha256": sha256_path(RAW_PATH),
            "raw_record_count": SEQUENCE,
            "pre_act_checkpoint_sha256": preact_sha,
            "harness_sha256": expected_harness,
            "environment_identity": gate_message["materialization_identity"],
            "first_failure": None,
            "teardown_state": "PENDING",
            "checkpoint_is_authority": False,
            "continuation": "RESULT_RECONSTRUCTION_ONLY__NO_SECOND_VECTOR__NO_RETRY__NO_P12__NO_PRODUCTION",
        }
        guest_seal_sha = write_canonical(GUEST_SEAL_PATH, guest_seal)
        append_record("spce_guest_execution_seal", "EVIDENCE", {
            "path": str(GUEST_SEAL_PATH), "sha256": guest_seal_sha,
            "preimage": guest_seal,
        })
        manifest_file_sha, manifest_envelope = update_continuation_manifest(
            current_spce_phase="PHASE_C_UNKNOWN_AUTHORITY_DENIAL_COMPLETE_PENDING_GUEST_TEARDOWN",
            execution_counters=counters,
            authority_lifecycle_state="NOT_CREATED",
            first_failure_or_current_result="PASS__E05_UNKNOWN_AUTHORITY__DENIED_BEFORE_PRECLAIM__ZERO_EFFECT",
            teardown_state="PENDING",
            authorized_next_action="TEARDOWN_AND_FINALIZATION_ONLY__NO_EXECUTION_REPLAY_OR_NEXT_VECTOR",
            additional_completed_seals=({
                "identity": "G77_256DY_GUEST_EXECUTION_SEAL_V1",
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
            "schema_id": "G77_256DY_GUEST_TEARDOWN_SEAL_V1",
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
        if first_failure is None and counters["e05_case_execution_count"] == 1:
            authority_state = "NOT_CREATED__NO_AUTHORITY_SURVIVES"
            current_result = "PASS__E05_UNKNOWN_AUTHORITY__DENIED_BEFORE_PRECLAIM__GUEST_TEARDOWN_COMPLETE"
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
                "identity": "G77_256DY_GUEST_TEARDOWN_SEAL_V1",
                "sha256": teardown_seal_sha,
            },),
        )


if __name__ == "__main__":
    raise SystemExit(main())
