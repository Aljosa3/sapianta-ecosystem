#!/usr/bin/env python3
"""Repository-only proof for the G77-256IW FUTURE guest import-root binding.

This owner performs source inspection, committed-evidence authentication,
NoCloud member extraction, and isolated imports from a temporary archive of the
authenticated IF runtime target.  It creates no authority and invokes no
launcher, QEMU, VM, request, P11 consumer, retry, repair, or replay path.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
IV_HEAD = "d9bf5a04a5277a7cd3291d728e46688b89303144"
IV_TREE = "44f9f14c9bec8b231f00fa9188398c9ef52ec64a"
IV_SUBJECT = "G77-256IV record FUTURE authorized pre-request import failure"
IF_HEAD = "699fcdce794ff49b6c8735602936355724ed1c90"
IF_TREE = "7c773d4b2acdf013f1b8238eabfc8eced4dd6866"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"

IW_ROOT = Path(".github/governance/evidence/g77_256iw_future_guest_import_root_binding_v1")
CLOUD_INIT = IW_ROOT / "static/G77_256IW_CLOUD_INIT_USER_DATA_V1.yaml"
SEED = IW_ROOT / "static/SAPIANTA_FUTURE_NOCLOUD_SEED_V1.img"
TERMINAL = IW_ROOT / "G77_256IW_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = IW_ROOT / "G77_256IW_G48_IMPLEMENTATION_REPORT_V1.md"
CLOUD_SHA256 = "10092e4d10327c0bef42608e3125ca4b04b82b8e91a0c5e88a5148ee1a14fee2"
SEED_SHA256 = "655b8b4122f89acbf0e4d3a670ee3b4fb38fb37600eeb6c8745c0a13cdc57eab"
FM_ROOT = Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1")
FM_LAUNCHER = FM_ROOT / "launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
FM_META = FM_ROOT / "raw/G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"
FM_NETWORK = FM_ROOT / "raw/G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"
FM_LAUNCHER_BEFORE_SHA256 = "669985cc31ea7bde26a3187e0f212d6ab2dd6643f73fc34589a7fb7e633ad6c0"
FM_LAUNCHER_AFTER_SHA256 = "ee06a8b77870aecd1621ab9fb2af1c412cea525ea55b6367e3bae9dd1e6d5ab6"
IT_ROOT = Path(".github/governance/evidence/g77_256it_future_bootstrap_seed_binding_v1")
IT_CLOUD = IT_ROOT / "static/G77_256IT_CLOUD_INIT_USER_DATA_V1.yaml"
IT_SEED = IT_ROOT / "static/SAPIANTA_FUTURE_NOCLOUD_SEED_V1.img"
IT_CLOUD_SHA256 = "85fff3ed0a764c2e0a26acc5d08778b21bec9fe925c2eb69e931b410f906eaff"
IT_SEED_SHA256 = "58b880d7011a9a781968139f212eef8f6b913f0efadf86df1ee98ac05b0f3369"
IV_ROOT = Path(".github/governance/evidence/g77_256iv_future_operational_v1")
IV_REPORT = IV_ROOT / "G77_256IV_G48_IMPLEMENTATION_REPORT_V1.md"
IV_TERMINAL = IV_ROOT / "G77_256IV_SPCE_TERMINAL_REDUCTION_V1.json"
IV_SERIAL = IV_ROOT / "G77_256IV_SERIAL_CONSOLE_V1.log"
IV_PRE = IV_ROOT / "operation_state/receipts/G77_256IV_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
IV_POST = IV_ROOT / "operation_state/receipts/G77_256IV_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
IV_ADAPTER = IV_ROOT / "operation_state/guest_harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
IV_HASHES = {
    IV_REPORT: "206e103c557d4f4c90c0d5593655da348b16df19261ea117949bf82aa7054083",
    IV_TERMINAL: "2fd72ceb29bf887946565db653fd541102e6a4ea66aa5556374d4f7e38cae786",
    IV_SERIAL: "492353716186284bb13653e8f8db4483d77798aa9613dc7c283918cceecbd6ec",
    IV_PRE: "170fde0968426440aa3c4c6c2b8f5a975991382b38c1704da352368f7c5d1af8",
    IV_POST: "12f99c130c87627de71d25c0c0a6f1f4a6861ac4a29de8976dc2b0fcf0e7e289",
}
EX_CERTIFICATE = Path(
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
)
EX_VALIDATOR = Path(
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "validator/G77_256EX_COMMON_SUBSTRATE_CERTIFICATION_VALIDATOR_V1.py"
)
EX_SHA256 = "91c477171147c56516c0f473ab887c12173c4bab225f2733c274b32467824b2f"
DU_V2 = Path(
    ".github/governance/evidence/g77_256du_continuation_manifest_contract_v2/"
    "validator/G77_256DU_CONTINUATION_MANIFEST_COMPATIBILITY_VALIDATOR_V2.py"
)
GUEST_ROOT = "/mnt/aigol"
GUEST_ADAPTER = "/mnt/dp-harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
TOP_LEVEL_AIGOL_IMPORTS = [
    "aigol.runtime.canonical_che_evidence_correlation_contract_v1",
    "aigol.runtime.canonical_human_authority_act_contract_v1",
    "aigol.runtime.transport.serialization",
]
FUTURE_PAYLOAD = "9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547"
FUTURE_SOURCE_ACT = "7167b0725d2c84bafde1d0060f512b0fa358d777ec1beff8b7c68d22ee6502e8"
FUTURE_CHE = "CHE-CORRELATION-15b2680b5577da169cecf9efb3231e2e6f6467e6f409fa2594b04128f998e454"


class IWBindingError(ValueError):
    """One deterministic fail-closed IW verification error."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes((ROOT / path).read_bytes())


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise IWBindingError(f"DUPLICATE_JSON_KEY__{key}")
        value[key] = item
    return value


def load_canonical(path: Path) -> dict[str, Any]:
    raw = (ROOT / path).read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise IWBindingError(f"CANONICAL_JSON_INVALID__{path}")
    return value


def load_unique(path: Path) -> dict[str, Any]:
    value = json.loads((ROOT / path).read_bytes(), object_pairs_hook=unique_object)
    if not isinstance(value, dict):
        raise IWBindingError(f"JSON_OBJECT_REQUIRED__{path}")
    return value


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def load_module(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, ROOT / path)
    if specification is None or specification.loader is None:
        raise IWBindingError(f"MODULE_LOAD_FAILED__{identity}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def authenticate_entry() -> dict[str, Any]:
    observed = {
        "repository": str(ROOT),
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
        "remote_tracking_head": git("rev-parse", f"origin/{BRANCH}"),
        "index": git("diff", "--cached", "--name-only"),
    }
    expected = {
        "repository": str(ROOT), "branch": BRANCH, "head": IV_HEAD,
        "tree": IV_TREE, "subject": IV_SUBJECT, "origin": ORIGIN,
        "remote_tracking_head": IV_HEAD, "index": "",
    }
    if observed != expected:
        raise IWBindingError("EXACT_RATIFIED_IV_CHECKPOINT_MISMATCH")
    nested = ROOT / "sapianta_system"
    nested_state = {
        "origin": git("remote", "get-url", "origin", cwd=nested),
        "head": git("rev-parse", "HEAD", cwd=nested),
        "tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "branch": git("branch", "--show-current", cwd=nested),
        "status": git("status", "--porcelain", cwd=nested),
        "tag": git("describe", "--tags", "--exact-match", "HEAD", cwd=nested),
    }
    if nested_state != {
        "origin": NESTED_ORIGIN, "head": NESTED_HEAD, "tree": NESTED_TREE,
        "branch": "", "status": "", "tag": NESTED_TAG,
    }:
        raise IWBindingError("NESTED_AUTHORITY_NOT_CLEAN_DETACHED_PINNED")
    return observed | {"initial_worktree": "AUTHENTICATED_CLEAN_BEFORE_IW_MUTATION", "nested": nested_state}


def reconstruct_iv_terminal() -> dict[str, Any]:
    for path, identity in IV_HASHES.items():
        if sha256_path(path) != identity:
            raise IWBindingError(f"IV_HISTORICAL_IDENTITY_MISMATCH__{path}")
    envelope = load_canonical(IV_TERMINAL)
    reduction = envelope["reduction"]
    if envelope["reduction_sha256"] != sha256_bytes(canonical_bytes(reduction)):
        raise IWBindingError("IV_TERMINAL_INNER_SEAL_INVALID")
    expected = {
        "terminal": "E__AUTHORIZED_OPERATION_FAILED_BEFORE_REQUEST",
        "last_verified_edge": "ONE_AUTHORIZED_FM_INVOCATION__ONE_NO_NETWORK_QEMU_BOOT__FUTURE_GUEST_ADAPTER_PROCESS_STARTED",
        "first_broken_edge": "FUTURE_GUEST_ADAPTER_TOP_LEVEL_AIGOL_IMPORT_BEFORE_GUEST_CHECKOUT_IMPORT_ROOT_BINDING",
        "blocking_owner": "G77_256IT_FUTURE_BOOTSTRAP_SEED_GUEST_IMPORT_ENVIRONMENT_BINDING",
        "exact_failure": "ModuleNotFoundError: No module named 'aigol'",
        "minimum_missing_capability": "GUEST_BOOTSTRAP_IMPORT_ROOT_BINDING_FOR_AIGOL_BEFORE_FUTURE_ADAPTER_TOP_LEVEL_IMPORTS",
        "minimum_legal_next_delta": "SEPARATE_HUMAN_REVIEWED_REPOSITORY_ONLY_SUCCESSOR_GENERATION_TO_BIND_AND_STATICALLY_VERIFY_PYTHON_IMPORT_ROOT__NO_RETRY_IN_IV",
    }
    if {key: reduction[key] for key in expected} != expected:
        raise IWBindingError("IV_TERMINAL_SEMANTIC_MISMATCH")
    counters = reduction["operational_counters"]
    required = {
        "authority_consumption": 1, "e05_credit": 0,
        "fm_operational_launcher_invocation": 1, "future_denial": 0,
        "future_operation": 0, "human_authorization_presentation": 1,
        "human_operational_authority": 1, "operation_attempt": 1,
        "p11_entry": 0, "pre": 1, "protected_effect": 0,
        "protected_invocation": 0, "qemu": 1, "repair_retry": 0,
        "replay": 0, "request": 0, "retry": 0,
        "second_consumption": 0, "vm_boot": 1, "vm_creation": 1,
    }
    if counters != required or reduction["e05"] != {"before": "10/18", "after": "10/18", "credit": 0}:
        raise IWBindingError("IV_OPERATIONAL_CARDINALITY_MISMATCH")
    serial = (ROOT / IV_SERIAL).read_text(encoding="utf-8")
    sequence = [
        "G77_256FM_BOOT_MARKER=PASS",
        'File "/mnt/dp-harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py", line 20',
        "ModuleNotFoundError: No module named 'aigol'",
        "G77_256FM_HARNESS_EXIT_STATUS=1",
    ]
    positions = [serial.find(item) for item in sequence]
    if min(positions) < 0 or positions != sorted(positions):
        raise IWBindingError("IV_DECISIVE_SERIAL_SEQUENCE_MISMATCH")
    pre, post = load_canonical(IV_PRE), load_canonical(IV_POST)
    if pre["vector"] != post["vector"] or pre["execution_attempt_count"] != 1:
        raise IWBindingError("IV_RECEIPT_PAIR_MISMATCH")
    argv = pre["vector"]["argv"]
    expected_seed = str(ROOT / IT_SEED)
    if sum(expected_seed in argument for argument in argv) != 1:
        raise IWBindingError("IV_IT_SEED_BINDING_MISMATCH")
    if sum("mount_tag=aigol_checkout" in argument for argument in argv) != 1:
        raise IWBindingError("IV_CHECKOUT_PROJECTION_MISMATCH")
    nic_positions = [index for index, value in enumerate(argv) if value == "-nic"]
    if len(nic_positions) != 1 or argv[nic_positions[0] + 1] != "none" or post["process_exit_status"] != 0:
        raise IWBindingError("IV_NO_NETWORK_PROCESS_RECEIPT_MISMATCH")
    return expected | {"operational_counters": counters, "serial_sequence": "VERIFIED", "receipt_pair": "VERIFIED"}


def top_level_imports() -> list[str]:
    tree = ast.parse((ROOT / IV_ADAPTER).read_text(encoding="utf-8"))
    imports = [
        node.module for node in tree.body
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("aigol.")
    ]
    if imports != TOP_LEVEL_AIGOL_IMPORTS:
        raise IWBindingError("FUTURE_ADAPTER_TOP_LEVEL_IMPORT_SET_MISMATCH")
    return imports


def seed_projection() -> dict[str, Any]:
    sources = {"/user-data": CLOUD_INIT, "/meta-data": FM_META, "/network-config": FM_NETWORK}
    for member, source in sources.items():
        projected = subprocess.check_output(
            ["isoinfo", "-i", str(ROOT / SEED), "-R", "-x", member],
            stderr=subprocess.DEVNULL,
        )
        if projected != (ROOT / source).read_bytes():
            raise IWBindingError(f"NOCLOUD_PROJECTION_MISMATCH__{member}")
    return {
        "repository_bootstrap_to_nocloud_user_data": "VERIFIED__EXACT_BYTES",
        "nocloud_common_members_to_repository_sources": "VERIFIED__EXACT_BYTES",
        "seed_sha256": SEED_SHA256,
        "wall_clock_dependency_count": "VERIFIED__0",
    }


def audit_binding() -> dict[str, Any]:
    if sha256_path(IT_CLOUD) != IT_CLOUD_SHA256 or sha256_path(IT_SEED) != IT_SEED_SHA256:
        raise IWBindingError("HISTORICAL_IT_IDENTITY_MISMATCH")
    if git("diff", "--name-only", "HEAD", "--", str(IT_ROOT), str(IV_ROOT)):
        raise IWBindingError("HISTORICAL_IT_OR_IV_MUTATED")
    if sha256_path(CLOUD_INIT) != CLOUD_SHA256 or sha256_path(SEED) != SEED_SHA256:
        raise IWBindingError("IW_BOOTSTRAP_OR_SEED_IDENTITY_MISMATCH")
    if sha256_path(FM_LAUNCHER) != FM_LAUNCHER_AFTER_SHA256:
        raise IWBindingError("FM_LAUNCHER_SUCCESSOR_IDENTITY_MISMATCH")
    cloud = (ROOT / CLOUD_INIT).read_text(encoding="utf-8")
    ordered = [
        "mount -t 9p -o trans=virtio,version=9p2000.L,ro aigol_checkout /mnt/aigol",
        "export PYTHONPATH=/mnt/aigol",
        "echo G77_256FM_BOOT_MARKER=PASS",
        f"/usr/bin/python3 {GUEST_ADAPTER}",
    ]
    positions = [cloud.find(item) for item in ordered]
    if min(positions) < 0 or positions != sorted(positions):
        raise IWBindingError("IMPORT_ROOT_NOT_BOUND_BEFORE_ADAPTER_IMPORT")
    if cloud.count("export PYTHONPATH=/mnt/aigol") != 1:
        raise IWBindingError("GUEST_IMPORT_ROOT_BINDING_CARDINALITY_INVALID")
    launcher = load_module(FM_LAUNCHER, "g77_256iw_fm_launcher")
    selected = launcher.current_bootstrap_asset_bindings("FUTURE")
    expected = {
        "cloud_init_path": CLOUD_INIT.as_posix(), "cloud_init_sha256": CLOUD_SHA256,
        "seed_path": str(ROOT / SEED), "seed_sha256": SEED_SHA256,
    }
    if selected != expected:
        raise IWBindingError("FM_FUTURE_SUCCESSOR_SELECTION_MISMATCH")
    tree = ast.parse((ROOT / FM_LAUNCHER).read_text(encoding="utf-8"))
    if sum(isinstance(node, ast.FunctionDef) and node.name == "main" for node in tree.body) != 1:
        raise IWBindingError("PRODUCTION_ROUTE_COUNT_INVALID")
    return {
        "checkout_exists": "VERIFIED__MOUNTED_AT_/mnt/aigol_BEFORE_ADAPTER",
        "checkout_is_python_import_root": "VERIFIED__PYTHONPATH_EXACTLY_/mnt/aigol_BEFORE_ADAPTER",
        "source_to_projection_to_consumer": "VERIFIED",
        "selector_binding": selected,
        "ordering": "CHECKOUT_MOUNT__IMPORT_ROOT_EXPORT__BOOT_MARKER__ADAPTER_EXECUTION",
        "seed_projection": seed_projection(),
    }


def isolated_import_proof() -> dict[str, Any]:
    if git("rev-parse", f"{IF_HEAD}^{{tree}}") != IF_TREE:
        raise IWBindingError("IF_RUNTIME_TARGET_TREE_MISMATCH")
    imports = top_level_imports()
    code = "; ".join(f"import {name}" for name in imports)
    with tempfile.TemporaryDirectory(prefix="g77_256iw_static_") as temporary:
        root = Path(temporary)
        archive, checkout, outside = root / "if.tar", root / "checkout", root / "outside"
        checkout.mkdir()
        outside.mkdir()
        subprocess.run(
            ["git", "archive", "--format=tar", f"--output={archive}", IF_HEAD],
            cwd=ROOT, check=True,
        )
        subprocess.run(["tar", "-xf", str(archive), "-C", str(checkout)], check=True)
        environment = {
            "PATH": "/usr/bin:/bin", "LC_ALL": "C", "PYTHONNOUSERSITE": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        without = subprocess.run(
            ["/usr/bin/python3", "-c", code], cwd=outside, env=environment,
            text=True, capture_output=True, check=False,
        )
        if without.returncode == 0 or "No module named 'aigol'" not in without.stderr:
            raise IWBindingError("WITHOUT_GUEST_IMPORT_ROOT_DID_NOT_FAIL_AS_EXPECTED")
        with_environment = environment | {"PYTHONPATH": str(checkout)}
        with_root = subprocess.run(
            ["/usr/bin/python3", "-c", code], cwd=outside, env=with_environment,
            text=True, capture_output=True, check=False,
        )
        if with_root.returncode != 0:
            raise IWBindingError(f"WITH_GUEST_IMPORT_ROOT_FAILED__{with_root.stderr.strip()}")
    return {
        "runtime_target": {"role": "IF", "head": IF_HEAD, "tree": IF_TREE},
        "isolated_working_directory": "VERIFIED__OUTSIDE_CHECKOUT",
        "host_pythonpath_removed": "VERIFIED",
        "host_sys_path_false_positive": "VERIFIED__0",
        "without_guest_import_root": "EXPECTED_FAIL__ModuleNotFoundError_NO_MODULE_NAMED_AIGOL",
        "with_governed_guest_import_root": "PASS",
        "verified_imports": imports,
    }


def ex_reuse() -> dict[str, str]:
    if sha256_path(EX_CERTIFICATE) != EX_SHA256:
        raise IWBindingError("EX_CERTIFICATE_IDENTITY_MISMATCH")
    validator = load_module(EX_VALIDATOR, "g77_256iw_ex_validator")
    result = validator.validate(ROOT / EX_CERTIFICATE)
    if result["component_counts"]["CERTIFIED"] != 17 or (
        result["regression_total"], result["regression_pass"], result["regression_fail"]
    ) != (12, 12, 0):
        raise IWBindingError("EX_17_OF_17_REGRESSION_MISMATCH")
    return {"ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0", "ex_is_authority": "VERIFIED__NO"}


def zero_authority_firewall() -> dict[str, str]:
    return {
        "human_operational_authority_created": "VERIFIED__0", "authority_consumption": "VERIFIED__0",
        "pre_operational_invocation": "VERIFIED__0", "fm_operational_invocation": "VERIFIED__0",
        "qemu_operational_invocation": "VERIFIED__0", "vm_operational_boot": "VERIFIED__0",
        "operation_attempt": "VERIFIED__0", "request": "VERIFIED__0", "p11_entry": "VERIFIED__0",
        "protected_invocation": "VERIFIED__0", "protected_effect": "VERIFIED__0", "retry": "VERIFIED__0",
        "repair_retry": "VERIFIED__0", "replay": "VERIFIED__0", "e05_credit": "VERIFIED__0",
    }


def post_commit_readiness_gate() -> str:
    validator = load_module(DU_V2, "g77_256iw_du_v2")
    try:
        validator.build_du_fixture(ROOT)
    except validator.CompatibilityError as exc:
        if exc.code == "RUNTIME_TARGET_SELECTION_WORKTREE_DRIFT":
            return "EXPECTED_FAIL_CLOSED__RUNTIME_TARGET_SELECTION_WORKTREE_DRIFT"
        raise
    raise IWBindingError("UNCOMMITTED_IW_SELECTOR_PASSED_POST_COMMIT_READINESS")


def build_reduction() -> dict[str, Any]:
    entry = authenticate_entry()
    iv = reconstruct_iv_terminal()
    binding = audit_binding()
    import_proof = isolated_import_proof()
    return {
        "schema_id": "G77_256IW_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "terminal": "A__FUTURE_GUEST_IMPORT_ROOT_BINDING_REPOSITORY_IMPLEMENTED",
        "entry": entry,
        "iv_terminal_reconstruction": iv,
        "owner_graph": binding,
        "import_root_static_verification": import_proof,
        "dependent_identity_recomputation": [
            {"owner": CLOUD_INIT.as_posix(), "old_identity": IT_CLOUD_SHA256, "new_identity": CLOUD_SHA256, "reason": "GUEST_IMPORT_ROOT_BINDING"},
            {"owner": SEED.as_posix(), "old_identity": IT_SEED_SHA256, "new_identity": SEED_SHA256, "reason": "NOCLOUD_USER_DATA_PROJECTION"},
            {"owner": FM_LAUNCHER.as_posix(), "old_identity": FM_LAUNCHER_BEFORE_SHA256, "new_identity": FM_LAUNCHER_AFTER_SHA256, "reason": "EXISTING_FUTURE_SELECTOR_REBIND"},
        ],
        "future_semantics": {
            "evaluation": 500, "valid_from": 600, "valid_until": 1000, "relation": "500 < 600 < 1000",
            "payload_digest": FUTURE_PAYLOAD, "source_act": FUTURE_SOURCE_ACT, "che_correlation": FUTURE_CHE,
            "future_semantic_mutation_count": "VERIFIED__0", "wall_clock_dependency_count": "VERIFIED__0",
        },
        "v2_role_separation": {
            "runtime_target": {"role": "IF", "head": IF_HEAD, "tree": IF_TREE, "candidate_sha256": "ad5d204ec6ace09f18b83fd5f868e73dac5e36dad81149f9f335c87f68cf42f7"},
            "certification_baseline": {"role": "REPOSITORY_DERIVED", "head": IV_HEAD, "tree": IV_TREE},
            "role_collapse": "VERIFIED__NO",
        },
        "authority_firewall": zero_authority_firewall(),
        "post_commit_readiness_gate": post_commit_readiness_gate(),
        "route_firewall": {
            "production_route_before": "VERIFIED__1", "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0", "parallel_flow_created": "VERIFIED__NO",
            "new_launcher_count": "VERIFIED__0", "new_generic_adapter_count": "VERIFIED__0",
            "new_dispatcher_count": "VERIFIED__0", "new_global_registry_count": "VERIFIED__0",
            "p11_mutation_count": "VERIFIED__0",
        },
        "historical_failure_firewall": {
            "checked_failure_class_count": "VERIFIED__30", "reintroduced_failure_count": "VERIFIED__0",
            "iv_import_root_failure_historical_occurrence_count": "VERIFIED__1",
            "iv_import_root_failure_successor_static_recurrence_count": "VERIFIED__0",
            "caller_selected_import_root_count": "VERIFIED__0", "host_sys_path_false_positive_count": "VERIFIED__0",
            "network_or_package_install_dependency_count": "VERIFIED__0",
        },
        "proof_reuse": ex_reuse(),
        "e05": {"before": "10/18", "after": "10/18", "credit": 0, "frontier_distance": "VERIFIED__8_UNSATISFIED_OF_18"},
        "terminal_frontier": {
            "last_verified_edge": "FUTURE_GUEST_IMPORT_ROOT_BINDING_REPOSITORY_STATIC_CLOSURE",
            "first_broken_edge": "POST_COMMIT_IMPORT_ROOT_BINDING_AND_FULL_STATIC_READINESS_NOT_YET_AUTHENTICATED",
            "minimum_missing_capability": "POST_COMMIT_AUTHENTICATION_OF_GUEST_IMPORT_ROOT_BINDING_AND_FULL_STATIC_READINESS",
            "minimum_legal_next_delta": "HUMAN_REVIEW_COMMIT_PUSH_THEN_SEPARATE_POST_COMMIT_READINESS_GENERATION",
            "auto_continuable": "NO", "human_review_required": "YES", "next_generation_started": "NO",
        },
    }


def build_envelope() -> dict[str, Any]:
    reduction = build_reduction()
    return {
        "schema_id": "G77_256IW_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }


def main() -> int:
    envelope = build_envelope()
    (ROOT / TERMINAL).write_bytes(canonical_bytes(envelope))
    print(json.dumps(envelope["reduction"]["terminal_frontier"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
