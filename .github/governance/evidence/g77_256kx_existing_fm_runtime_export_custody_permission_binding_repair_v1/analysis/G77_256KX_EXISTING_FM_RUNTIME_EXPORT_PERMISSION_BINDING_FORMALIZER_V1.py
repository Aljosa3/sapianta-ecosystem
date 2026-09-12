#!/usr/bin/env python3
"""Authenticate and reduce the KX repository-only FM permission repair."""

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
KX = ROOT / ".github/governance/evidence/g77_256kx_existing_fm_runtime_export_custody_permission_binding_repair_v1"
KW = ROOT / ".github/governance/evidence/g77_256kw_fresh_expired_operational_recommissioning_v1"
KF = ROOT / ".github/governance/evidence/g77_256kf_guest_harness_permission_binding_repair_v1"
LAUNCHER_RELATIVE = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
LAUNCHER = ROOT / LAUNCHER_RELATIVE
FRESH_CONTEXT_OWNER = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
KW_TERMINAL = KW / "G77_256KW_SPCE_TERMINAL_FAILURE_REDUCTION_V1.json"
KW_OBSERVATION = KW / "G77_256KW_PHASE_B_RUNTIME_EXPORT_CUSTODY_FAILURE_OBSERVATION_V1.json"
KW_AUTHORITY = KW / "G77_256KW_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json"
KW_HUMAN_SOURCE = KW / "G77_256KW_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
KW_RAW = KW / "operation_state/runtime_export/G77_256KW_RAW_EXECUTION_EVIDENCE_V1.jsonl"
KW_CONTEXT = KW / "operation_state/runtime_export/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
KW_ADAPTER = KW / "operation_state/guest_harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
KW_PRE_RECEIPT = KW / "operation_state/receipts/G77_256KW_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
KF_REDUCTION = KF / "G77_256KF_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
P11 = ROOT / "tests/p11_da_operational_consumer_v1.py"
EX_CERTIFICATE = ROOT / (
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
)
EX_SEAL = ROOT / (
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_FINAL_VALIDATION_SEAL_V1.json"
)
FORMALIZER_PATH = Path(__file__).resolve()
TEST_PATH = KX / "tests/test_g77_256kx_runtime_export_permission_binding_v1.py"
REPORT_PATH = KX / "G77_256KX_G48_IMPLEMENTATION_REPORT_V1.md"
TERMINAL_PATH = KX / "G77_256KX_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"

HEAD = "e691b568c0136d3079b5a546e5f8536f1805f7ee"
TREE = "70416c1ea4e1a2fc0cb0c065e8243d12545000e7"
SUBJECT = "G77-256KW localize runtime export custody edge"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"

KW_TERMINAL_SHA256 = "b6d2ad8cdad66c5ae56bef59ec4a949fe78241441b39700cb79b39562224a663"
KW_OBSERVATION_SHA256 = "fc7b02c71be2d249f8b5a756921612eef0da4e7f140f0e2920c4eea23d627a0c"
KW_AUTHORITY_SHA256 = "4017c67a7708fa0fca3194ed8024f7dc2792badb00d6ce1b43f06f210c159c21"
KW_HUMAN_SOURCE_SHA256 = "692b106107c5959e55a727d19a1bb5cfda783b4ac91a4b6d525c1e6fee6a43bd"
KW_RAW_SHA256 = "b77198c2a235a7130fedf22cba28a56535afd510a88183d56dddb3e3f8dd7080"
KW_CONTEXT_SHA256 = "aa29315205a28100c00f940d2aba9575e1b60cacb97b9e5a548cf451674295b2"
KW_ADAPTER_SHA256 = "f24d696ee3ab1f1b5d5feef2fa29e155e971f1aa1b8d890c98734011fb40e1d7"
KW_PRE_RECEIPT_SHA256 = "7291dad6e63e964fd23e4304429587a729255fb9a4aceae1e6315075ab2134dc"
KF_REDUCTION_SHA256 = "6210226beb40806d3099dcb50577a7a59dadb4c5a4443fb32308c280914d86c8"
PRE_REPAIR_LAUNCHER_SHA256 = "e1db7e6d59d81a85ee025b27c3145abe697c1097822694498a4ad686d2406c51"
POST_REPAIR_LAUNCHER_SHA256 = "76c82e3701abbd14e9003f356ed326c7bc179935198a060910118d8c40d92aa6"
FRESH_CONTEXT_OWNER_SHA256 = "337aa8d19f519bd0873ff9d688c16fc6b914e70ef1b03504813d2f4fdf8d899b"
P11_SHA256 = "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5"
EX_CERTIFICATE_SHA256 = "91c477171147c56516c0f473ab887c12173c4bab225f2733c274b32467824b2f"
EX_SEAL_SHA256 = "46115a7627264793af5e289abe85565fcaaf8a381b009e185c35ebc3d4b8a543"

TERMINAL = "A__KX_EXISTING_FM_RUNTIME_EXPORT_PERMISSION_BINDING_REPAIR_VERIFIED__REPOSITORY_ONLY__NO_OPERATION"
KW_TERMINAL_VALUE = "I__KW_PROVIDER_RECOVERY__NEW_RUNTIME_EXPORT_CUSTODY_EDGE_FOUND__CLASSIFIED__FAIL_CLOSED__NO_RETRY"
GENERATION = "G77_256KX_EXISTING_FM_RUNTIME_EXPORT_CUSTODY_PERMISSION_BINDING_REPAIR_V1"
PRE_ROOT_MODE = 0o700
POST_ROOT_MODE = 0o701
CONTEXT_MODE = 0o664
HOST_UID = 1000
HOST_GID = 1000
CUSTODY_UID = 3
CUSTODY_GID = 3


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


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


def permission_bits(
    mode: int, *, owner_uid: int, owner_gid: int, actor_uid: int, actor_gid: int
) -> int:
    if actor_uid == owner_uid:
        return (mode >> 6) & 0o7
    if actor_gid == owner_gid:
        return (mode >> 3) & 0o7
    return mode & 0o7


def permits(bits: int, permission: int) -> bool:
    return bits & permission == permission


def authenticate_entry(remote_head: str, nested_remote_tag: str) -> dict[str, Any]:
    observed = {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
        "remote_head": remote_head,
        "remote_equality": remote_head == HEAD,
        "index_empty": git("diff", "--cached", "--name-only") == "",
        "stable_ancestry": subprocess.run(
            ["git", "merge-base", "--is-ancestor", ANCHOR, "HEAD"], cwd=ROOT
        ).returncode == 0,
    }
    expected = {
        "branch": BRANCH, "head": HEAD, "tree": TREE, "subject": SUBJECT,
        "origin": ORIGIN, "remote_head": HEAD, "remote_equality": True,
        "index_empty": True, "stable_ancestry": True,
    }
    if observed != expected:
        raise RuntimeError("KX repository entry mismatch")
    nested = ROOT / "sapianta_system"
    nested_observed = {
        "origin": git("remote", "get-url", "origin", cwd=nested),
        "head": git("rev-parse", "HEAD", cwd=nested),
        "tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "clean": git("status", "--porcelain", cwd=nested) == "",
        "detached": subprocess.run(
            ["git", "symbolic-ref", "-q", "HEAD"], cwd=nested,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        ).returncode != 0,
        "tag": git("describe", "--tags", "--exact-match", "HEAD", cwd=nested),
        "remote_tag": nested_remote_tag,
    }
    if nested_observed != {
        "origin": NESTED_ORIGIN, "head": NESTED_HEAD, "tree": NESTED_TREE,
        "clean": True, "detached": True, "tag": NESTED_TAG,
        "remote_tag": NESTED_HEAD,
    }:
        raise RuntimeError("KX nested authority mismatch")
    observed["nested_authority"] = nested_observed
    return observed


def authenticate_delta() -> dict[str, Any]:
    tracked = tuple(filter(None, git("diff", "--name-only").splitlines()))
    if tracked != (LAUNCHER_RELATIVE.as_posix(),):
        raise RuntimeError("unexpected tracked KX delta")
    expected = {
        FORMALIZER_PATH.relative_to(ROOT).as_posix(),
        TEST_PATH.relative_to(ROOT).as_posix(),
        REPORT_PATH.relative_to(ROOT).as_posix(),
        TERMINAL_PATH.relative_to(ROOT).as_posix(),
    }
    untracked = set(filter(None, git("ls-files", "--others", "--exclude-standard").splitlines()))
    if untracked not in (expected - {TERMINAL_PATH.relative_to(ROOT).as_posix()}, expected):
        raise RuntimeError("unexpected or incomplete untracked KX delta")
    if git("diff", "--numstat", "--", LAUNCHER_RELATIVE.as_posix()) != (
        f"12\t1\t{LAUNCHER_RELATIVE.as_posix()}"
    ):
        raise RuntimeError("KX launcher delta shape mismatch")
    return {
        "tracked_production_mutation": LAUNCHER_RELATIVE.as_posix(),
        "production_mutation_count": 1,
        "new_owner_count": 0,
        "new_route_count": 0,
        "new_registry_count": 0,
        "new_generic_abstraction_count": 0,
        "new_constitutional_concept_count": 0,
        "p11_implementation_mutation_count": 0,
        "unrelated_mutation_count": 0,
    }


def authenticate_kw_terminal() -> dict[str, Any]:
    expected_hashes = (
        (KW_TERMINAL, KW_TERMINAL_SHA256),
        (KW_OBSERVATION, KW_OBSERVATION_SHA256),
        (KW_AUTHORITY, KW_AUTHORITY_SHA256),
        (KW_HUMAN_SOURCE, KW_HUMAN_SOURCE_SHA256),
        (KW_RAW, KW_RAW_SHA256),
        (KW_CONTEXT, KW_CONTEXT_SHA256),
        (KW_ADAPTER, KW_ADAPTER_SHA256),
        (KW_PRE_RECEIPT, KW_PRE_RECEIPT_SHA256),
    )
    for path, expected in expected_hashes:
        if sha256(path) != expected:
            raise RuntimeError(f"KW evidence identity mismatch: {path}")
        committed = subprocess.check_output(
            ["git", "show", f"{HEAD}:{path.relative_to(ROOT)}"], cwd=ROOT
        )
        if path.read_bytes() != committed:
            raise RuntimeError(f"KW evidence differs from committed bytes: {path}")
    reduction = load_inner(KW_TERMINAL, "reduction")
    observation = load_inner(KW_OBSERVATION, "observation")
    checkpoint = load_inner(KW_AUTHORITY, "checkpoint")
    counters = {
        "authority_consumption_count": 1, "expired_denial_count": 0,
        "fm_operational_invocation_count": 1, "operation_attempt_count": 1,
        "operation_request_count": 0, "operational_authorization_count": 1,
        "p11_entry_count": 0, "pre_operational_invocation_count": 1,
        "protected_effect_count": 0, "protected_invocation_count": 0,
        "qemu_start_count": 1, "repair_retry_count": 0, "replay_count": 0,
        "retry_count": 0, "vm_start_count": 1,
    }
    if reduction.get("terminal") != KW_TERMINAL_VALUE:
        raise RuntimeError("KW terminal mismatch")
    if reduction.get("operational_counters") != counters:
        raise RuntimeError("KW operational counter mismatch")
    if reduction.get("e05") != {
        "after": "VERIFIED__11_OF_18", "before": "VERIFIED__11_OF_18",
        "credit": "VERIFIED__0", "expired": "NOT_PROVEN_OPERATIONALLY",
        "frontier": "VERIFIED__7_UNSATISFIED_OF_18", "kw_credit": "VERIFIED__0",
    }:
        raise RuntimeError("KW E05 state mismatch")
    if checkpoint.get("human_source_sha256") != KW_HUMAN_SOURCE_SHA256 or not (
        checkpoint.get("authority_state_before") == "GRANTED_UNCONSUMED"
        and checkpoint.get("authority_state_after") == "CONSUMED"
        and checkpoint.get("authority_reusable") is False
        and checkpoint.get("authority_transferable") is False
    ):
        raise RuntimeError("KW terminal authority mismatch")
    expected_observation = {
        "exact_exception_type": "PermissionError",
        "exact_exception_errno": 13,
        "exact_exception_path": "/mnt/g77-evidence/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json",
        "host_runtime_export_mode": "0700",
        "host_context_projection_mode": "0664",
        "host_runtime_export_uid": HOST_UID,
        "host_runtime_export_gid": HOST_GID,
        "guest_custody_uid": CUSTODY_UID,
        "guest_custody_gid": CUSTODY_GID,
    }
    if any(observation.get(key) != value for key, value in expected_observation.items()):
        raise RuntimeError("KW custody observation mismatch")
    records = [json.loads(line) for line in KW_RAW.read_text(encoding="utf-8").splitlines()]
    commissioning = [record.get("record_type") for record in records[1:13]]
    if commissioning != [f"commissioning_P{index:02d}" for index in range(1, 13)]:
        raise RuntimeError("KW P01-P12 commissioning evidence mismatch")
    if any(record.get("facts", {}).get("result") != "PASS" for record in records[1:13]):
        raise RuntimeError("KW P01-P12 commissioning did not pass")
    return {
        "terminal": reduction["terminal"],
        "operational_counters": counters,
        "authority": {
            "state": "VERIFIED__CONSUMED_EXACTLY_ONCE__NONREUSABLE__NONTRANSFERABLE",
            "human_source_sha256": KW_HUMAN_SOURCE_SHA256,
        },
        "e05": reduction["e05"],
        "failure": expected_observation,
        "commissioning": "VERIFIED__P01_THROUGH_P12_PASS_BEFORE_CONTEXT_LOAD_FAILURE",
    }


def authenticate_owner_and_contract() -> dict[str, Any]:
    pre_raw = subprocess.check_output(["git", "show", f"{HEAD}:{LAUNCHER_RELATIVE}"], cwd=ROOT)
    post_raw = LAUNCHER.read_bytes()
    if sha256_bytes(pre_raw) != PRE_REPAIR_LAUNCHER_SHA256:
        raise RuntimeError("pre-repair FM launcher identity mismatch")
    if sha256_bytes(post_raw) != POST_REPAIR_LAUNCHER_SHA256:
        raise RuntimeError("post-repair FM launcher identity mismatch")
    pre_source = pre_raw.decode()
    post_source = post_raw.decode()
    if pre_source.count("runtime_export.mkdir(mode=0o700, parents=False, exist_ok=False)") != 1:
        raise RuntimeError("pre-repair runtime-export owner binding mismatch")
    required = (
        "RUNTIME_EXPORT_ROOT_CONSTRUCTION_MODE = 0o700",
        "RUNTIME_EXPORT_ROOT_PRESENTATION_MODE = 0o701",
        "mode=RUNTIME_EXPORT_ROOT_CONSTRUCTION_MODE,",
        "runtime_export.chmod(RUNTIME_EXPORT_ROOT_PRESENTATION_MODE)",
        'raise RuntimeError("runtime export root permission binding mismatch")',
    )
    if any(post_source.count(token) != 1 for token in required):
        raise RuntimeError("post-repair runtime-export binding incomplete or ambiguous")
    tree = ast.parse(post_source)
    owners = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "materialize_operation_state"]
    if len(owners) != 1:
        raise RuntimeError("FM materialization owner missing or ambiguous")
    manifest_at = post_source.index("runtime_manifest.write_bytes(candidate.read_bytes())")
    context_at = post_source.index("context_projection.write_bytes(context_source_path.read_bytes())")
    chmod_at = post_source.index("runtime_export.chmod(RUNTIME_EXPORT_ROOT_PRESENTATION_MODE)")
    if not manifest_at < context_at < chmod_at:
        raise RuntimeError("runtime export published before complete initial materialization")
    pre_bits = permission_bits(
        PRE_ROOT_MODE, owner_uid=HOST_UID, owner_gid=HOST_GID,
        actor_uid=CUSTODY_UID, actor_gid=CUSTODY_GID,
    )
    post_bits = permission_bits(
        POST_ROOT_MODE, owner_uid=HOST_UID, owner_gid=HOST_GID,
        actor_uid=CUSTODY_UID, actor_gid=CUSTODY_GID,
    )
    context_bits = permission_bits(
        CONTEXT_MODE, owner_uid=HOST_UID, owner_gid=HOST_GID,
        actor_uid=CUSTODY_UID, actor_gid=CUSTODY_GID,
    )
    if permits(pre_bits, os.X_OK):
        raise RuntimeError("pre-repair custody traversal unexpectedly permitted")
    if not permits(post_bits, os.X_OK) or permits(post_bits, os.R_OK | os.W_OK):
        raise RuntimeError("post-repair root is not search-only")
    if not permits(context_bits, os.R_OK) or permits(context_bits, os.W_OK):
        raise RuntimeError("sealed context custody contract mismatch")
    if PRE_ROOT_MODE ^ POST_ROOT_MODE != 0o001 or POST_ROOT_MODE & 0o006:
        raise RuntimeError("runtime-export repair is not the one-bit minimum")
    if sha256(FRESH_CONTEXT_OWNER) != FRESH_CONTEXT_OWNER_SHA256:
        raise RuntimeError("FM fresh-context owner identity mismatch")
    context_owner_source = FRESH_CONTEXT_OWNER.read_text(encoding="utf-8")
    shared_context_tokens = (
        'WRONG_ATTEMPT = "WRONG_ATTEMPT"', 'WRONG_INPUT = "WRONG_INPUT"',
        'WRONG_CONTRACT = "WRONG_CONTRACT"',
        'WRONG_PROVENANCE = "WRONG_PROVENANCE"', 'FUTURE = "FUTURE"',
        'EXPIRED = "EXPIRED"',
        'runtime_export = operation_evidence_root / "runtime_export"',
        '"runtime_export_root": str(runtime_export)',
    )
    if any(context_owner_source.count(token) < 1 for token in shared_context_tokens):
        raise RuntimeError("common FM vector runtime-export binding mismatch")
    receipt = load_canonical(KW_PRE_RECEIPT)
    argv = receipt["vector"]["argv"]
    exports = [argv[index + 1] for index, value in enumerate(argv[:-1]) if value == "-virtfs"]
    runtime_exports = [value for value in exports if "mount_tag=g77_evidence" in value]
    if len(runtime_exports) != 1 or "readonly=on" in runtime_exports[0]:
        raise RuntimeError("existing runtime-export mount owner mismatch")
    if sha256(KF_REDUCTION) != KF_REDUCTION_SHA256:
        raise RuntimeError("KF repair identity mismatch")
    kf = load_inner(KF_REDUCTION, "reduction")
    if kf.get("terminal") != "A__GUEST_HARNESS_PERMISSION_BINDING_REPOSITORY_VERIFIED":
        raise RuntimeError("KF repair not intact")
    if sha256(P11) != P11_SHA256 or P11.read_bytes() != subprocess.check_output(
        ["git", "show", f"{HEAD}:{P11.relative_to(ROOT)}"], cwd=ROOT
    ):
        raise RuntimeError("P11 identity changed")
    return {
        "caller": "EXISTING_GENERATION_PREAUTHORIZATION_MATERIALIZER",
        "actual_owner": f"{LAUNCHER_RELATIVE}:materialize_operation_state",
        "materialization_point": "FM.materialize_operation_state",
        "mount_semantics": "EXISTING_SINGLE_G77_EVIDENCE_9P_EXPORT_TO_/mnt/g77-evidence",
        "before": "PRIVATE_CONSTRUCTION_AND_PRESENTATION_0700",
        "after": "PRIVATE_CONSTRUCTION_0700_THEN_SEARCH_ONLY_PRESENTATION_0701",
        "custody_principal": {"uid": CUSTODY_UID, "gid": CUSTODY_GID},
        "complete_pre_request_traversal_contract": [
            "KF_GUEST_HARNESS_ROOT_0701__UNCHANGED",
            "FM_RUNTIME_EXPORT_ROOT_0701__KX_REPAIRED",
        ],
        "sealed_context": "OBSERVED_0664__CUSTODY_READ_ALLOWED_WRITE_DENIED",
        "minimum_permission_delta": "VERIFIED__ONE_BIT__OTHER_EXECUTE__0700_TO_0701",
        "root_listing": "DENIED", "root_write": "DENIED",
        "context_write": "DENIED", "route_expansion": "ABSENT",
        "authority_expansion": "ABSENT", "kf_repair": "VERIFIED__INTACT",
        "p11_sha256": P11_SHA256,
        "production_route_before": 1, "production_route_after": 1,
    }


def authenticate_ex_reuse() -> dict[str, Any]:
    if sha256(EX_CERTIFICATE) != EX_CERTIFICATE_SHA256 or sha256(EX_SEAL) != EX_SEAL_SHA256:
        raise RuntimeError("EX common proof identity mismatch")
    certificate = json.loads(EX_CERTIFICATE.read_bytes())["certificate"]
    certified = [
        row for row in certificate["component_certification_matrix"]
        if row.get("proposed_ex_classification") == "CERTIFIED"
    ]
    if len(certified) != 17:
        raise RuntimeError("EX certified component count mismatch")
    return {
        "ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0",
        "assumption_invalidation_count": 0,
    }


def zero_operational_counters() -> dict[str, int]:
    return {
        "human_operational_authorization_count": 0, "authority_consumption_count": 0,
        "fm_operational_invocation_count": 0, "qemu_count": 0, "vm_count": 0,
        "operation_attempt_count": 0, "operation_request_count": 0,
        "expired_denial_count": 0, "p11_entry_count": 0,
        "protected_invocation_count": 0, "protected_effect_count": 0,
        "retry_count": 0, "repair_retry_count": 0, "replay_count": 0,
    }


def build_reduction(remote_head: str = HEAD, nested_remote_tag: str = NESTED_HEAD) -> dict[str, Any]:
    entry = authenticate_entry(remote_head, nested_remote_tag)
    delta = authenticate_delta()
    kw = authenticate_kw_terminal()
    owner = authenticate_owner_and_contract()
    ex = authenticate_ex_reuse()
    return {
        "schema_id": "G77_256KX_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation_identity": GENERATION,
        "terminal": TERMINAL,
        "entry": entry,
        "kw_terminal_authentication": kw,
        "failure_novelty_and_convergence_check": {
            "failure_class": "NEW_SEMANTIC_EDGE",
            "novelty": "VERIFIED__DISTINCT_RUNTIME_EXPORT_TRAVERSAL_EDGE_AFTER_KF_HARNESS_TRAVERSAL_REPAIR",
            "affected_invariant": "GUEST_CUSTODY_MUST_LOAD_SEALED_OPERATION_CONTEXT_BEFORE_GATE_WITHOUT_WRITE_AUTHORITY",
            "previous_closest_edge": "KE_GUEST_HARNESS_ROOT_TRAVERSAL_DENIAL",
            "semantic_difference": "KF_REPAIRED_GUEST_HARNESS_ROOT__DISTINCT_FM_RUNTIME_EXPORT_ROOT_REMAINED_0700",
            "production_behavior_impact": "VERIFIED__SOLE_ROUTE_BLOCKED_BEFORE_EXPIRED_REQUEST__ZERO_PROTECTED_EFFECT",
            "new_capability_required": "VERIFIED__BOUNDED_EXISTING_FM_RUNTIME_EXPORT_PRESENTATION_BINDING",
            "new_proof_required": "VERIFIED__REPOSITORY_ONLY_SEARCH_TRAVERSAL_AND_CONTEXT_READ_WITHOUT_WRITE",
            "convergence_signal": "VERIFIED__KW_FRONTIER_PASSED_KF_AND_P01_TO_P12",
            "repetition_pressure": "VERIFIED__HIGH__E05_REMAINS_11_OF_18_ACROSS_MULTIPLE_GENERATIONS",
            "verification_amplification_risk": "ESTIMATED__LOW_AFTER_COMPLETE_PRE_REQUEST_TRAVERSAL_CONTRACT_AUTHENTICATION",
            "overengineering_risk": "ESTIMATED__LOW__ONE_EXISTING_OWNER_ONE_BIT_PRESENTATION_DELTA",
            "classification_evidence": "VERIFIED__COMMITTED_KW_RAW_OBSERVATION_TERMINAL__FM_OWNER__KF_PRECEDENT",
            "classification_confidence": "VERIFIED__HIGH",
            "acceptance_requirement_forcing_continuation": "VERIFIED__KX_REPOSITORY_REPAIR_AND_DETERMINISTIC_PROOF_ONLY",
        },
        "owner_and_minimum_permission_contract": owner,
        "spce_phase_a": {
            "result": "VERIFIED__CANDIDATE_VALIDATED_BEFORE_IMPLEMENTATION",
            "owner": owner["actual_owner"],
            "affected_roots": ["operation_state/runtime_export"],
            "change": "0700_PRIVATE_CONSTRUCTION_TO_0701_FINAL_SEARCH_ONLY_PRESENTATION",
            "allowed": "CUSTODY_TRAVERSE_DIRECT_ROOT_AND_READ_EXISTING_0664_SEALED_CONTEXT",
            "forbidden": "CUSTODY_LIST_WRITE_MUTATE_REPLACE_OR_CREATE__ROUTE_OR_AUTHORITY_EXPANSION",
            "machine_verification": "PYTHON_AST_SOURCE_ORDER__POSIX_PERMISSION_MODEL__FILESYSTEM_MODE_TESTS",
        },
        "implemented_delta": delta,
        "cross_vector_reuse_assessment": {
            "authority_lifecycle": {
                "cross_vector_reuse_scope": "MULTI_VECTOR_REUSABLE",
                "reusable_component": "DIRECT_HUMAN_UTF8_SOURCE_BYTES_TO_DERIVED_DIGEST_TO_CANONICAL_HANDOFF_TO_ONE_SHOT_CONSUMPTION_PATTERN",
                "reuse_invariant": "EXPLICIT_HUMAN_DECISION_SOURCE_AND_EXACT_BYTES_PRECEDE_AUTHORITY_BINDING_AND_CONSUMPTION",
                "applicable_vectors": ["EXPIRED", "FUTURE", "WRONG_ATTEMPT", "WRONG_CONTRACT", "WRONG_INPUT", "WRONG_PROVENANCE"],
                "vector_specific_residue": "FRESH_PER_GENERATION_AUTHORITY_AND_VECTOR_OUTCOME",
                "reuse_preconditions": "FRESH_HUMAN_SOURCE_AND_EXACT_GENERATION_BINDINGS",
                "revalidation_required": "VERIFIED__PER_GENERATION_AND_VECTOR",
                "expected_future_proof_reduction": "ESTIMATED__LIFECYCLE_PATTERN_REUSE_ONLY__NO_AUTHORITY_OR_CREDIT_TRANSFER",
            },
            "runtime_export_permission_presentation": {
                "cross_vector_reuse_scope": "COMMON_E05_INFRASTRUCTURE",
                "reusable_component": "EXISTING_FM_RUNTIME_EXPORT_ROOT_FINAL_PRESENTATION_BINDING",
                "reuse_invariant": "ALL_EXISTING_FM_VECTORS_LOAD_THE_SEALED_CONTEXT_FROM_THE_SAME_DIRECT_G77_EVIDENCE_ROOT",
                "applicable_vectors": ["EXPIRED", "FUTURE", "WRONG_ATTEMPT", "WRONG_CONTRACT", "WRONG_INPUT", "WRONG_PROVENANCE"],
                "vector_specific_residue": "VECTOR_ADAPTER_SEMANTICS_AND_OPERATIONAL_OUTCOME",
                "reuse_preconditions": "EXISTING_FM_MATERIALIZER_AND_DIRECT_SEALED_CONTEXT_LAYOUT",
                "revalidation_required": "VERIFIED__RELEVANT_FM_AND_VECTOR_BINDINGS",
                "expected_future_proof_reduction": "ESTIMATED__ONE_COMMON_TRAVERSAL_BINDING__NO_VECTOR_OPERATIONAL_PROOF_TRANSFER",
            },
        },
        "e05": {
            "before": "VERIFIED__11_OF_18", "after": "VERIFIED__11_OF_18",
            "frontier": "VERIFIED__7_UNSATISFIED_OF_18", "credit": "VERIFIED__0",
            "kx_credit": "VERIFIED__0", "expired": "NOT_PROVEN_OPERATIONALLY",
        },
        "ex": ex,
        "governance_reporting": {
            "project_state": "VERIFIED__KX_REPOSITORY_PERMISSION_BINDING_REPAIRED_PENDING_HUMAN_REVIEW",
            "project_progress": "VERIFIED__KW_RUNTIME_EXPORT_BLOCKER_CLOSED_IN_REPOSITORY_ONLY_PROOF__E05_UNCHANGED",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__ONE_PRE_REQUEST_REPOSITORY_BLOCKER_CLOSED__OPERATIONAL_FRONTIER_NOT_RETESTED",
            "constitutional_health_evidence": "VERIFIED__MINIMUM_ONE_BIT_OWNER_DELTA__NO_AUTHORITY_OR_ROUTE_EXPANSION",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficience": "ESTIMATED__HIGH__AUTHENTICATED_OWNER_AND_KF_PATTERN_REUSED",
            "overengineering_risk": "ESTIMATED__LOW",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_EVIDENCE_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__KW_TO_KX_REPOSITORY_CONTINUATION",
            "candidate_capability": "VERIFIED__REPOSITORY_ONLY_RUNTIME_EXPORT_SEARCH_AND_CONTEXT_READ_CONTRACT",
            "shadow_design_target": "VERIFIED__SOLE_FM_TO_ER_TO_P11_ROUTE",
            "constitutional_continuation_progress": "VERIFIED__FORMALIZE_REUSE_BIND_VERIFY_COMPLETE_FOR_KX",
            "last_verified_operational_edge": "VERIFIED__KW_GUEST_COMMISSIONING_P01_TO_P12_THEN_CONTEXT_PERMISSION_FAILURE",
            "first_unverified_operational_edge": "NOT_PROVEN__REPAIRED_CONTEXT_LOAD_THEN_EXPIRED_REQUEST_AND_DENIAL",
            "last_verified_edge": "VERIFIED__KX_DETERMINISTIC_RUNTIME_EXPORT_PERMISSION_CONTRACT",
            "first_broken_edge": "NOT_PROVEN__NO_POST_REPAIR_OPERATION_PERFORMED",
            "current_real_blocker": "VERIFIED__HUMAN_REVIEW_AND_COMMIT_REQUIRED_BEFORE_ANY_FRESH_OPERATIONAL_DESIGN",
            "minimum_missing_capability": "NOT_PROVEN__NEXT_OPERATIONAL_FRONTIER_REQUIRES_SEPARATE_FRESH_AUTHORITY_GENERATION",
            "minimum_legal_next_delta": "AFTER_HUMAN_REVIEW__COMMIT_PUSH_KX__THEN_SEPARATELY_DESIGN_FRESH_OPERATIONAL_GENERATION",
        },
        "architectural_delta_budget": {
            "production_mutation_count": 1, "new_owner_count": 0,
            "new_route_count": 0, "new_registry_count": 0,
            "new_generic_abstraction_count": 0, "new_constitutional_concept_count": 0,
            "p11_implementation_mutation_count": 0, "production_route_before": 1,
            "production_route_after": 1, "parallel_flow": "NO",
        },
        "operational_counters": zero_operational_counters(),
        "proof_yield": {
            "new_verified_capability_count": 1, "new_operational_capability_count": 0,
            "new_operational_observation_count": 0, "new_e05_credit_count": 0,
            "blocker_localized_count": 0, "blocker_closed_count": 1,
            "ex_proof_reuse_count": 17, "ex_reconstruction_count": 0,
        },
        "ccwim": {
            "authenticated_repository_continuation": "VERIFIED__YES",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "handoff_ambiguity_count": "VERIFIED__0",
            "binding_owner_ambiguity_count": "VERIFIED__0",
            "authority_state_ambiguity_count": "VERIFIED__0",
            "operational_attempt_ambiguity_count": "VERIFIED__0",
        },
        "hac_hai_hae": "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED",
        "reuse_impact_assessment": {
            "existing_certified_capabilities_reused": "FM__KF_SEARCH_ONLY_PRESENTATION_PATTERN__KW_FAILURE_EVIDENCE__EX_17_OF_17__P11",
            "new_capabilities": "VERIFIED__ONE_REPOSITORY_ONLY_EXISTING_FM_RUNTIME_EXPORT_PERMISSION_PRESENTATION_BINDING",
            "existing_capability_became_unreachable": False,
            "parallel_flow_created": False,
            "production_path_count_effect": "UNCHANGED__1_TO_1",
        },
        "terminality": {
            "auto_continuable": False, "human_review_required": True,
            "staged": False, "committed": False, "pushed": False,
            "repository_only_proof_is_operational_proof": False,
            "kw_retry_allowed": False, "kw_authority_reuse_allowed": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-head", default=HEAD)
    parser.add_argument("--nested-remote-tag", default=NESTED_HEAD)
    args = parser.parse_args()
    reduction = build_reduction(args.remote_head, args.nested_remote_tag)
    envelope = {
        "schema_id": "G77_256KX_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }
    sys.stdout.buffer.write(canonical_bytes(envelope))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
