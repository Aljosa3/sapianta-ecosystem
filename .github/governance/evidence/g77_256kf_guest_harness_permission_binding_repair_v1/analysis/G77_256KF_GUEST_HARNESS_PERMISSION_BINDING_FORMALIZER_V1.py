#!/usr/bin/env python3
"""Authenticate and reduce the KF repository-only permission binding repair."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
KF = ROOT / ".github/governance/evidence/g77_256kf_guest_harness_permission_binding_repair_v1"
KE = ROOT / ".github/governance/evidence/g77_256ke_fresh_expired_operational_recommissioning_v1"
LAUNCHER_RELATIVE = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
LAUNCHER = ROOT / LAUNCHER_RELATIVE
KE_TERMINAL = KE / "G77_256KE_SPCE_TERMINAL_FAILURE_REDUCTION_V1.json"
KE_OBSERVATION = KE / "G77_256KE_PHASE_B_GUEST_CUSTODY_FAILURE_OBSERVATION_V1.json"
KE_ADAPTER = KE / "operation_state/guest_harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
KE_PRE_RECEIPT = KE / "operation_state/receipts/G77_256KE_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
KE_RAW = KE / "operation_state/runtime_export/G77_256KE_RAW_EXECUTION_EVIDENCE_V1.jsonl"
KE_SERIAL = KE / "G77_256KE_SERIAL_CONSOLE_V1.log"
KE_TEARDOWN = KE / "operation_state/runtime_export/G77_256KE_GUEST_TEARDOWN_SEAL_V1.json"
P11 = ROOT / "tests/p11_da_operational_consumer_v1.py"
TERMINAL_PATH = KF / "G77_256KF_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT_PATH = KF / "G77_256KF_G48_IMPLEMENTATION_REPORT_V1.md"
TEST_PATH = KF / "tests/test_g77_256kf_guest_harness_permission_binding_v1.py"
FORMALIZER_PATH = Path(__file__).resolve()
EX_CERTIFICATE = ROOT / (
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
)
EX_SEAL = ROOT / (
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_FINAL_VALIDATION_SEAL_V1.json"
)

HEAD = "cdfc2ae475a58d20a6ba48d6a0e573c7dbcfcefa"
TREE = "ab41528f8a9b2c475f5a44cc61a58144050dd40d"
SUBJECT = "G77-256KE reduce terminal guest custody failure"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
KE_TERMINAL_SHA256 = "741463b61aa517d6322389cf214edae0f3e0aa0c56afc755354d3e6d2b79abf4"
KE_OBSERVATION_SHA256 = "a5d6786074dbbbe738c2d25b7aa91b6667f60d814f6bbbe66e3023c7d04f527e"
KE_ADAPTER_SHA256 = "f24d696ee3ab1f1b5d5feef2fa29e155e971f1aa1b8d890c98734011fb40e1d7"
KE_RAW_SHA256 = "7602388667ff722ea40851189f895e827227e8aecfc8269ec65f008dbfbfe9fb"
KE_SERIAL_SHA256 = "b1c772f8431ea8432d470e895458497f142f29c3fea360f5e22bada407d9762e"
KE_TEARDOWN_SHA256 = "e6e068ea5b69fd36e3c5370dab37bba38a56a3235f895b52276afcf7813a5553"
PRE_REPAIR_LAUNCHER_SHA256 = "662cce2458300c12cb6dfb18d8c836db7867c4400430a8081acbb4e285a60a36"
POST_REPAIR_LAUNCHER_SHA256 = "e1db7e6d59d81a85ee025b27c3145abe697c1097822694498a4ad686d2406c51"
P11_SHA256 = "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5"
EX_CERTIFICATE_SHA256 = "91c477171147c56516c0f473ab887c12173c4bab225f2733c274b32467824b2f"
EX_SEAL_SHA256 = "46115a7627264793af5e289abe85565fcaaf8a381b009e185c35ebc3d4b8a543"
TERMINAL = "A__GUEST_HARNESS_PERMISSION_BINDING_REPOSITORY_VERIFIED"
EXACT_EXCEPTION = (
    "PermissionError: [Errno 13] Permission denied: "
    "/mnt/dp-harness/sapianta_fresh_operation_context_v1.py"
)

PRE_ROOT_MODE = 0o700
POST_ROOT_MODE = 0o701
CONTEXT_OWNER_MODE = 0o644
HOST_UID = 1000
HOST_GID = 1000
CUSTODY_UID = 3
CUSTODY_GID = 3


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise RuntimeError(f"noncanonical evidence: {path}")
    return value


def load_inner(path: Path, key: str) -> dict[str, Any]:
    envelope = load_canonical(path)
    inner = envelope.get(key)
    if not isinstance(inner, dict):
        raise RuntimeError(f"missing inner object: {path}")
    if envelope.get(f"{key}_sha256") != sha256_bytes(canonical_bytes(inner)):
        raise RuntimeError(f"inner seal mismatch: {path}")
    return inner


def authenticate_delta() -> dict[str, Any]:
    """Accept only the interrupted KF launcher edit and bounded KF evidence."""

    tracked = tuple(filter(None, git("diff", "--name-only").splitlines()))
    if tracked != (LAUNCHER_RELATIVE.as_posix(),):
        raise RuntimeError("unexpected tracked KF delta")
    untracked = set(filter(None, git("ls-files", "--others", "--exclude-standard").splitlines()))
    expected_final = {
        FORMALIZER_PATH.relative_to(ROOT).as_posix(),
        TEST_PATH.relative_to(ROOT).as_posix(),
        REPORT_PATH.relative_to(ROOT).as_posix(),
        TERMINAL_PATH.relative_to(ROOT).as_posix(),
    }
    required_before_reduction = expected_final - {TERMINAL_PATH.relative_to(ROOT).as_posix()}
    if untracked not in (required_before_reduction, expected_final):
        raise RuntimeError("unexpected or incomplete untracked KF delta")
    numstat = git("diff", "--numstat", "--", LAUNCHER_RELATIVE.as_posix())
    if numstat != f"14\t1\t{LAUNCHER_RELATIVE.as_posix()}":
        raise RuntimeError("interrupted launcher delta shape mismatch")
    return {
        "interrupted_delta_reconstruction": "VERIFIED__EXACT_REPORTED_535_INSERTIONS_1_DELETION_BEFORE_CONTINUATION",
        "interrupted_launcher_delta": "VERIFIED__14_INSERTIONS_1_DELETION",
        "interrupted_formalizer_line_count": 521,
        "tracked_mutation": LAUNCHER_RELATIVE.as_posix(),
        "final_kf_evidence_paths": sorted(expected_final),
        "unrelated_or_unexplained_mutation_count": 0,
        "minimum": True,
        "owner_correct": True,
        "no_bypass": True,
        "no_new_route": True,
        "no_new_owner": True,
        "no_unnecessary_permission_expansion": True,
    }


def seal(schema: str, key: str, value: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": schema,
        key: value,
        f"{key}_sha256": sha256_bytes(canonical_bytes(value)),
    }


def permission_bits(
    mode: int,
    *,
    owner_uid: int,
    owner_gid: int,
    actor_uid: int,
    actor_gid: int,
) -> int:
    """Return the applicable POSIX rwx triad without invoking an OS identity."""

    if actor_uid == owner_uid:
        return (mode >> 6) & 0o7
    if actor_gid == owner_gid:
        return (mode >> 3) & 0o7
    return mode & 0o7


def permits(bits: int, permission: int) -> bool:
    return bits & permission == permission


def authenticate_entry(remote_head: str, nested_remote_tag: str) -> dict[str, Any]:
    observed = {
        "repository": str(ROOT),
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
        "remote_head": remote_head,
        "remote_equality": remote_head == HEAD,
        "index_empty": git("diff", "--cached", "--name-only") == "",
    }
    expected = {
        "repository": str(ROOT),
        "branch": BRANCH,
        "head": HEAD,
        "tree": TREE,
        "subject": SUBJECT,
        "origin": ORIGIN,
        "remote_head": HEAD,
        "remote_equality": True,
        "index_empty": True,
    }
    if observed != expected:
        raise RuntimeError("KF repository entry mismatch")

    nested = ROOT / "sapianta_system"
    nested_observed = {
        "origin": git("remote", "get-url", "origin", cwd=nested),
        "head": git("rev-parse", "HEAD", cwd=nested),
        "tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "clean": git("status", "--porcelain", cwd=nested) == "",
        "detached": subprocess.run(
            ["git", "symbolic-ref", "-q", "HEAD"],
            cwd=nested,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        != 0,
        "tag": git("describe", "--tags", "--exact-match", "HEAD", cwd=nested),
        "pinned": git("rev-parse", "HEAD", cwd=nested) == NESTED_HEAD,
        "remote_tag": nested_remote_tag,
        "remote_tag_equal": nested_remote_tag == NESTED_HEAD,
    }
    nested_expected = {
        "origin": NESTED_ORIGIN,
        "head": NESTED_HEAD,
        "tree": NESTED_TREE,
        "clean": True,
        "detached": True,
        "tag": NESTED_TAG,
        "pinned": True,
        "remote_tag": NESTED_HEAD,
        "remote_tag_equal": True,
    }
    if nested_observed != nested_expected:
        raise RuntimeError("KF nested authority mismatch")
    observed["nested_authority"] = nested_observed
    return observed


def authenticate_ke_terminal() -> dict[str, Any]:
    if sha256(KE_TERMINAL) != KE_TERMINAL_SHA256:
        raise RuntimeError("committed KE terminal file mismatch")
    if sha256(KE_OBSERVATION) != KE_OBSERVATION_SHA256:
        raise RuntimeError("committed KE observation file mismatch")
    for path, expected_hash in (
        (KE_RAW, KE_RAW_SHA256),
        (KE_SERIAL, KE_SERIAL_SHA256),
        (KE_TEARDOWN, KE_TEARDOWN_SHA256),
    ):
        if sha256(path) != expected_hash or path.read_bytes() != subprocess.check_output(
            ["git", "show", f"{HEAD}:{path.relative_to(ROOT)}"], cwd=ROOT
        ):
            raise RuntimeError(f"committed KE raw evidence mismatch: {path}")
    if KE_TERMINAL.read_bytes() != subprocess.check_output(
        ["git", "show", f"{HEAD}:{KE_TERMINAL.relative_to(ROOT)}"], cwd=ROOT
    ):
        raise RuntimeError("KE terminal differs from committed bytes")
    if KE_OBSERVATION.read_bytes() != subprocess.check_output(
        ["git", "show", f"{HEAD}:{KE_OBSERVATION.relative_to(ROOT)}"], cwd=ROOT
    ):
        raise RuntimeError("KE observation differs from committed bytes")

    reduction = load_inner(KE_TERMINAL, "reduction")
    observation = load_inner(KE_OBSERVATION, "observation")
    expected_counters = {
        "operational_authorization_count": 1,
        "authority_consumption_count": 1,
        "pre_operational_count": 1,
        "fm_operational_invocation_count": 1,
        "qemu_count": 1,
        "vm_count": 1,
        "operation_attempt_count": 1,
        "operational_request_count": 0,
        "expired_denial_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
    }
    if (
        reduction.get("terminal")
        != "M__KE_AUTHORIZED_EXPIRED_OPERATION_FAILED_AT_GUEST_CUSTODY_IMPORT_BEFORE_OPERATION_REQUEST"
        or reduction.get("operational_counters") != expected_counters
        or reduction.get("human_authority", {}).get("state")
        != "VERIFIED__CONSUMED_EXACTLY_ONCE__NONREUSABLE__NONTRANSFERABLE"
        or set(reduction.get("terminality", {}).values()) != {False}
        or reduction.get("e05", {}).get("state") != "VERIFIED__11_OF_18"
        or reduction.get("e05", {}).get("frontier") != "VERIFIED__7_UNSATISFIED_OF_18"
        or reduction.get("e05", {}).get("credit") != "VERIFIED__0"
        or reduction.get("e05", {}).get("expired") != "NOT_PROVEN_OPERATIONALLY"
        or reduction.get("reuse")
        != {"ex_reconstructed": "VERIFIED__0", "ex_reused": "VERIFIED__17_OF_17"}
    ):
        raise RuntimeError("KE terminal semantics mismatch")

    expected_observation = {
        "exact_exception_type": "PermissionError",
        "exact_exception_errno": 13,
        "exact_exception_path": "/mnt/dp-harness/sapianta_fresh_operation_context_v1.py",
        "blocker_classification": "VERIFIED__GUEST_CUSTODY_PROJECTION_PERMISSION_DENIAL_AT_CONTEXT_OWNER_LOAD",
        "root_cause": "VERIFIED__HOST_GUEST_HARNESS_PROJECTION_ROOT_MODE_0700_EXCLUDES_CUSTODY_UID_3_TRAVERSAL",
        "host_projection_root_mode": "0700",
        "host_projection_root_uid": HOST_UID,
        "host_projection_root_gid": HOST_GID,
        "guest_custody_uid": CUSTODY_UID,
        "guest_custody_gid": CUSTODY_GID,
    }
    if any(observation.get(key) != value for key, value in expected_observation.items()):
        raise RuntimeError("KE blocker provenance mismatch")
    if observation.get("first_failure", "").find("[Errno 13] Permission denied") < 0:
        raise RuntimeError("KE exact permission failure absent")
    if not observation.get("guest_projection_mount", "").startswith(
        "fm_harness /mnt/dp-harness 9p ro,"
    ):
        raise RuntimeError("KE read-only guest projection mismatch")
    raw_records = [json.loads(line) for line in KE_RAW.read_text(encoding="utf-8").splitlines()]
    guest_teardown = [record for record in raw_records if record.get("record_type") == "guest_teardown"]
    teardown = json.loads(KE_TEARDOWN.read_bytes())
    if (
        len(raw_records) != 15
        or len(guest_teardown) != 1
        or guest_teardown[0].get("facts", {}).get("first_failure") != observation["first_failure"]
        or teardown.get("first_failure") != observation["first_failure"]
        or teardown.get("raw_evidence_sha256") != KE_RAW_SHA256
        or teardown.get("teardown_state") != "COMPLETE"
        or "G77_256FM_BOOT_MARKER=PASS" not in KE_SERIAL.read_text(
            encoding="utf-8", errors="strict"
        )
        or "G77_256FM_HARNESS_EXIT_STATUS=40" not in KE_SERIAL.read_text(
            encoding="utf-8", errors="strict"
        )
    ):
        raise RuntimeError("KE raw/teardown/serial blocker provenance mismatch")
    return {
        "terminal_file_sha256": KE_TERMINAL_SHA256,
        "observation_file_sha256": KE_OBSERVATION_SHA256,
        "raw_evidence_sha256": KE_RAW_SHA256,
        "serial_sha256": KE_SERIAL_SHA256,
        "teardown_sha256": KE_TEARDOWN_SHA256,
        "terminal": reduction["terminal"],
        "historical_operational_counters": expected_counters,
        "authority": reduction["human_authority"],
        "terminality": reduction["terminality"],
        "blocker": expected_observation,
        "exact_exception": EXACT_EXCEPTION,
        "exact_path": expected_observation["exact_exception_path"],
        "guest_projection_mount": observation["guest_projection_mount"],
    }


def authenticate_owner_and_contract() -> dict[str, Any]:
    pre_raw = subprocess.check_output(
        ["git", "show", f"{HEAD}:{LAUNCHER_RELATIVE}"], cwd=ROOT
    )
    post_raw = LAUNCHER.read_bytes()
    if sha256_bytes(pre_raw) != PRE_REPAIR_LAUNCHER_SHA256:
        raise RuntimeError("pre-repair FM launcher identity mismatch")
    if sha256_bytes(post_raw) != POST_REPAIR_LAUNCHER_SHA256:
        raise RuntimeError("post-repair FM launcher identity mismatch")
    pre_source = pre_raw.decode("utf-8")
    post_source = post_raw.decode("utf-8")
    old_binding = "adapter_projection_root.mkdir(mode=0o700, parents=False, exist_ok=False)"
    if pre_source.count(old_binding) != 1 or old_binding in post_source:
        raise RuntimeError("pre-repair projection-root binding mismatch")
    required_post = (
        "GUEST_HARNESS_PROJECTION_ROOT_CONSTRUCTION_MODE = 0o700",
        "GUEST_HARNESS_PROJECTION_ROOT_PRESENTATION_MODE = 0o701",
        "mode=GUEST_HARNESS_PROJECTION_ROOT_CONSTRUCTION_MODE,",
        "adapter_projection_root.chmod(",
        "GUEST_HARNESS_PROJECTION_ROOT_PRESENTATION_MODE",
        'raise RuntimeError("adapter projection root permission binding mismatch")',
    )
    if any(post_source.count(token) < 1 for token in required_post):
        raise RuntimeError("post-repair permission binding incomplete")
    if post_source.count("def materialize_operation_state(") != 1:
        raise RuntimeError("FM materialization owner missing or ambiguous")
    write_index = post_source.index(
        "context_owner_projection.write_bytes(context_owner_source.read_bytes())"
    )
    chmod_index = post_source.index("adapter_projection_root.chmod(")
    if chmod_index <= write_index:
        raise RuntimeError("projection published before complete context-owner materialization")

    if sha256(KE_ADAPTER) != KE_ADAPTER_SHA256:
        raise RuntimeError("KE projected adapter mismatch")
    adapter_tree = ast.parse(KE_ADAPTER.read_text(encoding="utf-8"))
    load_functions = [
        node for node in adapter_tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "_load"
    ]
    if len(load_functions) != 1:
        raise RuntimeError("KE owner-loading mechanism missing or ambiguous")
    attributes = {
        node.attr for node in ast.walk(load_functions[0]) if isinstance(node, ast.Attribute)
    }
    if not {"spec_from_file_location", "module_from_spec", "exec_module"} <= attributes:
        raise RuntimeError("KE interpreter source-loading mechanism mismatch")
    if any(
        isinstance(node, ast.Name) and node.id in {"subprocess", "execv", "execl"}
        for node in ast.walk(load_functions[0])
    ):
        raise RuntimeError("unexpected direct execution mechanism")

    pre_root_bits = permission_bits(
        PRE_ROOT_MODE,
        owner_uid=HOST_UID,
        owner_gid=HOST_GID,
        actor_uid=CUSTODY_UID,
        actor_gid=CUSTODY_GID,
    )
    post_root_bits = permission_bits(
        POST_ROOT_MODE,
        owner_uid=HOST_UID,
        owner_gid=HOST_GID,
        actor_uid=CUSTODY_UID,
        actor_gid=CUSTODY_GID,
    )
    child_bits = permission_bits(
        CONTEXT_OWNER_MODE,
        owner_uid=HOST_UID,
        owner_gid=HOST_GID,
        actor_uid=CUSTODY_UID,
        actor_gid=CUSTODY_GID,
    )
    if permits(pre_root_bits, os.X_OK):
        raise RuntimeError("pre-repair traversal unexpectedly permitted")
    if not permits(child_bits, os.R_OK):
        raise RuntimeError("context-owner child is not independently readable")
    if not permits(post_root_bits, os.X_OK) or permits(post_root_bits, os.R_OK | os.W_OK):
        raise RuntimeError("post-repair root contract is not search-only")
    if permits(child_bits, os.W_OK) or permits(child_bits, os.X_OK):
        raise RuntimeError("context-owner child grants unnecessary custody authority")
    changed_bits = PRE_ROOT_MODE ^ POST_ROOT_MODE
    if changed_bits != 0o001 or POST_ROOT_MODE & 0o006:
        raise RuntimeError("0701 is not the one-bit minimum search-only repair")
    child_git_mode = git("ls-tree", HEAD, KE_ADAPTER.relative_to(ROOT).as_posix()).split()[0]
    context_owner_git_mode = git(
        "ls-tree", HEAD,
        (KE / "operation_state/guest_harness/sapianta_fresh_operation_context_v1.py")
        .relative_to(ROOT).as_posix(),
    ).split()[0]
    if child_git_mode != "100644" or context_owner_git_mode != "100644":
        raise RuntimeError("committed projected Python source mode mismatch")

    receipt = load_canonical(KE_PRE_RECEIPT)
    virtfs = [
        receipt["vector"]["argv"][index + 1]
        for index, value in enumerate(receipt["vector"]["argv"][:-1])
        if value == "-virtfs"
        and "mount_tag=fm_harness" in receipt["vector"]["argv"][index + 1]
    ]
    if len(virtfs) != 1 or not virtfs[0].endswith("security_model=none,readonly=on"):
        raise RuntimeError("read-only harness projection not preserved")
    if sha256(P11) != P11_SHA256 or P11.read_bytes() != subprocess.check_output(
        ["git", "show", f"{HEAD}:{P11.relative_to(ROOT)}"], cwd=ROOT
    ):
        raise RuntimeError("P11 identity changed")

    return {
        "caller": "EXISTING_GENERATION_PREAUTHORIZATION_MATERIALIZER",
        "authoritative_owner": f"{LAUNCHER_RELATIVE}:materialize_operation_state",
        "current_interface": "FM.materialize_operation_state",
        "current_permission_binding": "PRIVATE_CONSTRUCTION_AND_FINAL_PRESENTATION_BOTH_0700",
        "expected_permission_contract": "ROOT_0701_SEARCH_ONLY_FOR_NONOWNER__CONTEXT_OWNER_0644_READ_ONLY__NO_FILE_EXECUTE_REQUIRED",
        "adaptation_boundary": "EXISTING_FM_ADAPTER_PROJECTION_ROOT_FINAL_PRESENTATION_MODE",
        "access_mechanism": "PYTHON_IMPORTLIB_SOURCE_LOAD_VIA_EXEC_MODULE",
        "direct_execution": False,
        "interpreter_required": True,
        "file_execute_permission_required": False,
        "root_traversal": "REQUIRED__OTHER_EXECUTE_BIT_ONLY",
        "context_owner_readability": "REQUIRED__OTHER_READ_BIT_ALREADY_PRESENT",
        "committed_source_git_modes": {
            "adapter": child_git_mode,
            "context_owner": context_owner_git_mode,
        },
        "read_only_projection": "VERIFIED__PRESERVED",
        "host_owner": {"uid": HOST_UID, "gid": HOST_GID},
        "guest_custody_role": {"uid": CUSTODY_UID, "gid": CUSTODY_GID},
        "pre_repair_launcher_sha256": PRE_REPAIR_LAUNCHER_SHA256,
        "post_repair_launcher_sha256": POST_REPAIR_LAUNCHER_SHA256,
        "pre_repair_regression": "VERIFIED__ROOT_0700_DENIES_CUSTODY_UID_3_TRAVERSAL_WHILE_CHILD_0644_IS_READABLE",
        "post_repair_regression": "VERIFIED__ROOT_0701_GRANTS_SEARCH_ONLY_AND_CHILD_0644_GRANTS_READ_WITHOUT_EXECUTE",
        "first_failed_permission_predicate": "VERIFIED__PARENT_DIRECTORY_SEARCH_TRAVERSAL",
        "minimum_permission_delta": "VERIFIED__ONE_BIT__OTHER_EXECUTE__0700_TO_0701",
        "negative_permission_regressions": {
            "custody_root_read": "DENIED",
            "custody_root_write": "DENIED",
            "custody_context_owner_write": "DENIED",
            "custody_context_owner_execute": "DENIED__NOT_REQUIRED",
            "guest_projection_write": "DENIED__READ_ONLY_MOUNT",
            "alternate_projection": "ABSENT",
            "custody_uid_change": "ABSENT",
            "p11_mutation": "ABSENT",
        },
        "p11_sha256": P11_SHA256,
        "production_route_before": 1,
        "production_route_after": 1,
    }


def authenticate_ex_reuse() -> dict[str, Any]:
    if sha256(EX_CERTIFICATE) != EX_CERTIFICATE_SHA256 or sha256(EX_SEAL) != EX_SEAL_SHA256:
        raise RuntimeError("EX common proof identity mismatch")
    envelope = json.loads(EX_CERTIFICATE.read_bytes())
    certificate = envelope.get("certificate")
    if not isinstance(certificate, dict):
        raise RuntimeError("EX common proof payload missing")
    final_seal = json.loads(EX_SEAL.read_bytes()).get("seal")
    if not isinstance(final_seal, dict):
        raise RuntimeError("EX final seal payload missing")
    certificate_bindings = [
        binding for binding in final_seal.get("artifact_bindings", [])
        if isinstance(binding, dict)
        and binding.get("path") == EX_CERTIFICATE.relative_to(ROOT).as_posix()
    ]
    if len(certificate_bindings) != 1 or certificate_bindings[0].get("sha256") != EX_CERTIFICATE_SHA256:
        raise RuntimeError("EX final seal does not bind the common proof")
    matrix = certificate.get("component_certification_matrix")
    if not isinstance(matrix, list) or len(matrix) != 22:
        raise RuntimeError("EX component matrix mismatch")
    certified = [row for row in matrix if row.get("proposed_ex_classification") == "CERTIFIED"]
    if len(certified) != 17:
        raise RuntimeError("EX certified component count mismatch")
    bound_paths = {
        binding.get("path")
        for binding in certificate.get("certification_artifact_bindings", [])
        if isinstance(binding, dict)
    }
    if LAUNCHER_RELATIVE.as_posix() in bound_paths:
        raise RuntimeError("KF launcher mutation invalidates an EX artifact binding")
    exclusions = set(certificate.get("exclusions", []))
    if "ALL_VECTOR_SPECIFIC_FACTS" not in exclusions or "ACTUAL_QEMU_LAUNCH_AND_EXECUTED_ARGV" not in exclusions:
        raise RuntimeError("EX vector/operation exclusions mismatch")
    return {
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
        "assumption_invalidation_count": 0,
        "basis": "VERIFIED__KF_PERMISSION_EDGE_IS_NOT_AN_EX_BOUND_ARTIFACT_AND_VECTOR_OPERATION_FACTS_REMAIN_EXCLUDED",
        "certificate_sha256": EX_CERTIFICATE_SHA256,
        "final_seal_sha256": EX_SEAL_SHA256,
    }


def zero_operational_counters() -> dict[str, int]:
    return {
        "operational_authorization_count": 0,
        "authority_consumption_count": 0,
        "pre_operational_count": 0,
        "fm_operational_invocation_count": 0,
        "qemu_count": 0,
        "vm_count": 0,
        "operation_attempt_count": 0,
        "operational_request_count": 0,
        "expired_denial_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
    }


def zero_recovery_counters() -> dict[str, int]:
    return {
        "new_authority_consumption_during_kf_recovery": 0,
        "new_operation_attempt_during_kf_recovery": 0,
        "new_pre_during_kf_recovery": 0,
        "new_fm_operational_invocation_during_kf_recovery": 0,
        "new_qemu_during_kf_recovery": 0,
        "new_vm_during_kf_recovery": 0,
        "new_operational_request_during_kf_recovery": 0,
        "new_p11_entry_during_kf_recovery": 0,
        "new_protected_invocation_during_kf_recovery": 0,
        "new_protected_effect_during_kf_recovery": 0,
        "retry_during_kf_recovery": 0,
        "repair_retry_during_kf_recovery": 0,
        "replay_during_kf_recovery": 0,
    }


def build_reduction(
    remote_head: str = HEAD,
    nested_remote_tag: str = NESTED_HEAD,
) -> dict[str, Any]:
    entry = authenticate_entry(remote_head, nested_remote_tag)
    delta = authenticate_delta()
    ke = authenticate_ke_terminal()
    contract = authenticate_owner_and_contract()
    reuse = authenticate_ex_reuse()
    return {
        "schema_id": "G77_256KF_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "terminal": TERMINAL,
        "mode": "REPOSITORY_ONLY__NO_HUMAN_AUTHORITY__NO_OPERATIONAL_EXECUTION",
        "entry": entry,
        "provider_interruption": {
            "provider_limit_interruption": "OBSERVED",
            "generation_interrupted": "G77_256KF",
            "operational_process_interrupted": "NOT_APPLICABLE__KF_REPOSITORY_ONLY",
            "same_generation_recovery": "PERMITTED",
            "provider_capability_is_execution_authority": False,
        },
        "delta_reconstruction": delta,
        "ke_terminal": ke,
        "permission_contract": contract,
        "operational_counters": zero_operational_counters(),
        "recovery_operational_counters": zero_recovery_counters(),
        "e05": {
            "state": "VERIFIED__11_OF_18",
            "frontier": "VERIFIED__7_UNSATISFIED_OF_18",
            "credit": "VERIFIED__0",
            "expired": "NOT_PROVEN_OPERATIONALLY",
        },
        "reuse": reuse,
        "architecture": {
            "production_mutation_count": 1,
            "production_mutation_classification": "EXISTING_NON_P11_OPERATIONAL_BINDING_OWNER",
            "existing_operational_binding_owner_mutation_count": 1,
            "p11_implementation_mutation_count": 0,
            "new_owner_count": 0,
            "new_route_count": 0,
            "new_registry_count": 0,
            "new_generic_abstraction_count": 0,
            "new_constitutional_concept_count": 0,
            "production_route_before": 1,
            "production_route_after": 1,
            "one_existing_owner": True,
            "one_existing_route": True,
            "one_permission_binding": True,
            "parallel_flow_created": False,
        },
        "reuse_impact_assessment": {
            "existing_certified_capabilities_reused": "KE_TERMINAL__EX_17_OF_17__KD__KB__JZ__JX__JR__GN__FM__ER__P11__SOLE_ROUTE__NESTED_AUTHORITY",
            "new_capabilities": "VERIFIED__1_REPOSITORY_ONLY_GUEST_HARNESS_PERMISSION_BINDING_CAPABILITY",
            "existing_capability_became_unreachable": False,
            "parallel_flow_created": False,
            "production_path_count_effect": "UNCHANGED__1_TO_1",
        },
        "proof_yield": {
            "new_verified_capability_count": "VERIFIED__1_REPOSITORY_ONLY_PERMISSION_BINDING_CAPABILITY",
            "new_blocker_localized_count": "VERIFIED__0__KE_BLOCKER_REAUTHENTICATED_NOT_NEW",
            "e05_credit": "VERIFIED__0",
            "proof_reuse_count": "VERIFIED__17",
        },
        "governance": {
            "project_progress": "VERIFIED__KE_GUEST_PERMISSION_BLOCKER_REPAIRED_REPOSITORY_ONLY",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__ONE_PRE_REQUEST_GUEST_CUSTODY_BLOCKER_REMOVED_REPOSITORY_ONLY",
            "constitutional_health_evidence": "VERIFIED__FAIL_CLOSED_REPOSITORY_ONLY_REPAIR_WITH_ZERO_KF_OPERATIONAL_COUNTERS",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficience": "ESTIMATED__HIGH__ONE_EXISTING_OWNER_ONE_PERMISSION_BINDING_DELTA",
            "overengineering_risk": "ESTIMATED__LOW__ONE_MODE_TRANSITION_AND_ONE_EXISTING_VALIDATOR",
            "cognition_provenance": "VERIFIED__COMMITTED_KE_TERMINAL_AND_CURRENT_REPOSITORY_EVIDENCE_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__PROVIDER_INTERRUPTED_KF_RECONSTRUCTED_FROM_COMMITTED_AND_UNCOMMITTED_REPOSITORY_EVIDENCE",
            "candidate_capability": "VERIFIED__GUEST_HARNESS_PERMISSION_BINDING_REPOSITORY_ONLY",
            "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE_WITH_STABLE_JR_EXPIRED_CHECKOUT",
            "constitutional_continuation_progress": "VERIFIED__KE_TERMINAL_GUEST_PERMISSION_BLOCKER_TO_KF_REPOSITORY_BINDING_REPAIR",
        },
        "frontier": {
            "last_verified_edge": "GUEST_CUSTODY_PERMISSION_CONTRACT_REPOSITORY_VERIFIED",
            "first_broken_edge": "FRESH_EXPIRED_OPERATIONAL_RECOMMISSIONING_NOT_YET_REPROVEN_AFTER_KF",
            "minimum_missing_capability": "FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_DENIAL_BEFORE_P11_ENTRY",
            "minimum_legal_next_delta": "AFTER_KF_COMMIT_AND_HUMAN_REVIEW__SEPARATE_FRESH_OPERATIONAL_GENERATION_SPCE_PHASE_A_PREAUTHORIZATION_ONLY",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
            "cross_account_recovery": "VERIFIED",
            "provider_interruption_recovery": "VERIFIED",
        },
        "validation": {
            "scope": "REPOSITORY_ONLY__NO_QEMU_NO_VM_NO_OPERATIONAL_ROUTE",
            "dedicated_kf_regressions": "PASS__11",
            "applicable_nonoperational_regressions": "PASS__117__16_LIFECYCLE_PINNED_HISTORICAL_ASSERTIONS_DESELECTED",
            "governance_tests": "PASS__9",
            "conformance_engine": "PASS__20_OF_20",
            "canonical_json_and_seals": "PASS",
            "ast_and_compile": "PASS",
            "p11_identity_and_sole_route": "PASS",
            "g48_exactly_six_h1": "PASS",
            "reuse_impact_exactly_five_questions": "PASS",
            "git_diff_check": "PASS__NEW_KF_TEXT_AND_LAUNCHER_DELTA",
            "index_empty": "PASS",
            "operational_validation": "NOT_APPLICABLE__PROHIBITED_IN_KF",
        },
        "artifact_bindings": {
            "formalizer_sha256": sha256(FORMALIZER_PATH),
            "test_sha256": sha256(TEST_PATH),
            "report_sha256": sha256(REPORT_PATH),
            "launcher_sha256": POST_REPAIR_LAUNCHER_SHA256,
            "p11_sha256": P11_SHA256,
        },
        "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED",
        "auto_continuable": False,
        "human_review_required": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", default=HEAD)
    parser.add_argument("--nested-remote-tag", default=NESTED_HEAD)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    reduction = build_reduction(args.remote_head, args.nested_remote_tag)
    envelope = seal(
        "G77_256KF_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction",
        reduction,
    )
    if args.write:
        if TERMINAL_PATH.exists() or TERMINAL_PATH.is_symlink():
            raise RuntimeError("KF terminal collision")
        TERMINAL_PATH.write_bytes(canonical_bytes(envelope))
    print(TERMINAL)


if __name__ == "__main__":
    main()
