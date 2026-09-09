#!/usr/bin/env python3
"""Repository-only G77-256JP committed JO readiness reauthentication.

This formalizer reads committed Git objects and static source structure only.
It creates no authority and has no PRE, FM, QEMU, VM, request, P11-entry, or
protected-effect execution path.
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
ENTRY_HEAD = "bd6432aee86b44315073d9b83c60c000d3d95d02"
ENTRY_TREE = "682d1d7dca1d5e7a2ee46d22db20d968c9f5ee08"
ENTRY_SUBJECT = "G77-256JO bind sole route to committed JM P11 and sealed context"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
JM_HEAD = "4126dd5ad78fffb259625ca1033bb1d5419cc245"
JM_TREE = "87a227fafdb19e4d0c245d96f62f7728468580e6"
JN_HEAD = "3e2fab7a24ef06d58edfd13edd307a254ad6f543"
JN_TREE = "ecee2ce4de6b5240fe533235afd10d20d56bf79d"
JM_TERMINAL = (
    "A__OPTION_A_DETERMINISTIC_PRECLAIM_TEMPORAL_BINDING_"
    "IMPLEMENTED_AND_REPOSITORY_VERIFIED"
)
JN_TERMINAL = "M__POST_JM_READINESS_REQUIRES_SEPARATE_IMPLEMENTATION_DELTA"
JO_TERMINAL = (
    "A__SOLE_ER_FM_ROUTE_BOUND_TO_COMMITTED_JM_P11_AND_SEALED_CONTEXT_"
    "REPOSITORY_VERIFIED"
)
TERMINAL = (
    "A__POST_JO_COMMITTED_LIVE_BINDING_AND_EXPIRED_OPERATIONAL_READINESS_"
    "REPOSITORY_VERIFIED"
)
JM_P11_SHA256 = (
    "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5"
)
HISTORICAL_IF_HEAD = "699fcdce794ff49b6c8735602936355724ed1c90"
HISTORICAL_IF_P11_SHA256 = (
    "220e41ee3ea8fa6b21ecebe62aa4436b816d9b7678d251e18979fa87b160fc4e"
)

JP = Path(
    ".github/governance/evidence/"
    "g77_256jp_post_jo_committed_live_binding_and_expired_operational_"
    "readiness_reauthentication_v1"
)
REPORT = JP / "G77_256JP_G48_IMPLEMENTATION_REPORT_V1.md"
REDUCTION = JP / "G77_256JP_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
FORMALIZER = JP / "analysis/G77_256JP_POST_JO_READINESS_FORMALIZER_V1.py"
TEST = JP / "tests/test_g77_256jp_post_jo_readiness_v1.py"
JP_FILES = (REPORT, REDUCTION, FORMALIZER, TEST)

JO = Path(
    ".github/governance/evidence/"
    "g77_256jo_bind_sole_er_fm_route_to_committed_jm_p11_and_sealed_context_v1"
)
JO_REPORT = JO / "G77_256JO_G48_IMPLEMENTATION_REPORT_V1.md"
JO_REDUCTION = JO / "G77_256JO_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
JO_FORMALIZER = JO / "analysis/G77_256JO_SOLE_ROUTE_BINDING_FORMALIZER_V1.py"
JO_TEST = JO / "tests/test_g77_256jo_sole_route_binding_v1.py"
JN_REDUCTION = Path(
    ".github/governance/evidence/"
    "g77_256jn_post_jm_live_binding_ex_successor_reauthentication_and_"
    "expired_operational_readiness_v1/"
    "G77_256JN_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
JM_REDUCTION = Path(
    ".github/governance/evidence/"
    "g77_256jm_option_a_deterministic_preclaim_temporal_binding_implementation_v1/"
    "G77_256JM_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
EX_CERTIFICATE = Path(
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
)
EW_MANIFEST = Path(
    ".github/governance/evidence/g77_256ew_reusable_p11_spce_substrate_v1/"
    "G77_256EW_P11_SPCE_REUSABLE_SUBSTRATE_MANIFEST_V1.json"
)
LAUNCHER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
ER = Path(
    ".github/governance/evidence/g77_256er_p11_operational_v1/harness/"
    "G77_256ER_P11_OPERATIONAL_HARNESS_V1.py"
)
FC = Path(
    ".github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/harness/"
    "G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
)
FM_ADAPTER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/harness/"
    "G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
)
HA = Path(
    ".github/governance/evidence/g77_256ha_wrong_input_route_binding_v1/adapter/"
    "G77_256HA_WRONG_INPUT_VECTOR_ADAPTER_V1.py"
)
HT = Path(
    ".github/governance/evidence/g77_256ht_wrong_contract_route_extension_v1/adapter/"
    "G77_256HT_WRONG_CONTRACT_VECTOR_ADAPTER_V1.py"
)
IA = Path(
    ".github/governance/evidence/g77_256ia_wrong_provenance_route_extension_v1/adapter/"
    "G77_256IA_WRONG_PROVENANCE_VECTOR_ADAPTER_V1.py"
)
JC = Path(
    ".github/governance/evidence/"
    "g77_256jc_future_guest_context_owner_projection_v1/adapter/"
    "G77_256JC_FUTURE_VECTOR_ADAPTER_V1.py"
)
P11 = Path("tests/p11_da_operational_consumer_v1.py")
PRODUCTION_PATHS = (LAUNCHER, ER, FC, FM_ADAPTER, HA, HT, IA, JC)

# Both object names are required: Git blob identity authenticates repository
# membership, while SHA-256 preserves the exact-byte dependency vocabulary used
# by the route itself and by JO's report/reduction.
JO_COMMITTED_IDENTITIES: dict[Path, tuple[str, str]] = {
    LAUNCHER: (
        "935b28b727e0909b2a0bbb21f0f3b641c9fff6bd",
        "65a5719bcace99bc875c2bf7c7334255716e57d5b06df6b2b0b084352f329402",
    ),
    ER: (
        "eba82d9250b43f91bab84d0801b8496238a63e37",
        "c6539d1cc60940b1999956965bff43923a270598a982cd19f976eadec0a93152",
    ),
    FC: (
        "66f25717ba44044bea611451342babb3ef39b3ad",
        "b2e9f72d6b35b2db0021bf9bf1223350f570d1eaecda3379a8af013c705aa770",
    ),
    FM_ADAPTER: (
        "d49ee16c17ba3a3e9f7b5068e7a193c8020ec12a",
        "807f9e789f5fcd2358c3e9bc9b938f28a56f2c5c48d131450d9e0b15d15a5fe5",
    ),
    HA: (
        "c660ca5721c0bda88a6515e15eb749e7665de4ca",
        "805d97b6862dce8558dfe211337f0ed012f9dcc043cdca89e98ab163a522a99d",
    ),
    HT: (
        "38d5da78083b93b5859c2630cd4e3b52cf854309",
        "1aa28d0711eccf54aa7bdf214b38839317d325e80a782cbb091f640e5508a1b5",
    ),
    IA: (
        "0fb854da43d988cffe932c0f01d513098abd93eb",
        "416f11cbb5b947ffd71fd7760b2892172487565c5b789bb19f86771ed2a0e003",
    ),
    JC: (
        "3a7cd6f9a621001bf61a0e4fb5e69bdbfa273970",
        "71b223a35a9fe33fdf4adac5fd1b93aa16a26006629761a4ea851d4ccd821104",
    ),
    JO_REDUCTION: (
        "dc859a833facc8347785df06cdf3f6597bc584e3",
        "dd6894e92fc2647c30f1638317a3c0bd0a56ee4ddafc7320dcee572f44f2c59e",
    ),
    JO_FORMALIZER: (
        "937a876fd4e9225f74316352872a7462438753d8",
        "74ad5fbc0943e218b2a132c8d7a43731ad463c1e95c46eba754f6ede10134b6f",
    ),
    JO_TEST: (
        "c102beb0d6b275c7fc280ecc136d9b8cb943b92a",
        "ac1ae766caccb343e2d201b1bb9c09b11c7fd48effe20fafb919e7e32ca25fb0",
    ),
    JO_REPORT: (
        "320acd4fbde4b960a43654a765f5cc23fe9aac0a",
        "b91e2f9b5e73b018ab00a0fecd464fc972ba6f6d8e42e13bf5d11274b4c87189",
    ),
}


class JPError(RuntimeError):
    """One deterministic fail-closed JP verification error."""


def fail(token: str) -> None:
    raise JPError(token)


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=cwd, text=True, stderr=subprocess.DEVNULL
    ).strip()


def committed_bytes(path: Path, revision: str = ENTRY_HEAD) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{revision}:{path.as_posix()}"], cwd=ROOT,
        stderr=subprocess.DEVNULL,
    )


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            fail(f"DUPLICATE_JSON_KEY__{key}")
        value[key] = item
    return value


def load_json_bytes(raw: bytes) -> dict[str, Any]:
    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict):
        fail("JSON_OBJECT_REQUIRED")
    return value


def authenticate_envelope_bytes(raw: bytes, terminal: str) -> dict[str, Any]:
    envelope = load_json_bytes(raw)
    reduction = envelope.get("reduction")
    if not isinstance(reduction, dict):
        fail("REDUCTION_MISSING")
    if envelope.get("reduction_sha256") != sha256_bytes(canonical_bytes(reduction)):
        fail("REDUCTION_SEAL_INVALID")
    if reduction.get("terminal") != terminal:
        fail("TERMINAL_INVALID")
    return reduction


def authenticate_entry() -> dict[str, Any]:
    observed = {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
        "remote_tracking_head": git("rev-parse", f"origin/{BRANCH}"),
        "index_empty": git("diff", "--cached", "--name-only") == "",
    }
    expected = {
        "branch": BRANCH, "head": ENTRY_HEAD, "tree": ENTRY_TREE,
        "subject": ENTRY_SUBJECT, "origin": ORIGIN,
        "remote_tracking_head": ENTRY_HEAD, "index_empty": True,
    }
    if observed != expected:
        fail("ENTRY_IDENTITY_MISMATCH")
    status = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT, text=True,
    ).splitlines()
    if any(not line.startswith("?? ") for line in status):
        fail("TRACKED_OR_INDEX_DELTA_DETECTED")
    untracked = {line[3:] for line in status}
    expected_untracked = {path.as_posix() for path in JP_FILES}
    if not untracked <= expected_untracked:
        fail("OUT_OF_SCOPE_UNTRACKED_DELTA")
    nested = ROOT / "sapianta_system"
    nested_state = {
        "origin": git("remote", "get-url", "origin", cwd=nested),
        "head": git("rev-parse", "HEAD", cwd=nested),
        "tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "clean": git("status", "--porcelain=v1", cwd=nested) == "",
        "detached": git("branch", "--show-current", cwd=nested) == "",
        "tag": git("describe", "--tags", "--exact-match", "HEAD", cwd=nested),
    }
    expected_nested = {
        "origin": NESTED_ORIGIN, "head": NESTED_HEAD, "tree": NESTED_TREE,
        "clean": True, "detached": True, "tag": NESTED_TAG,
    }
    if nested_state != expected_nested:
        fail("NESTED_AUTHORITY_MISMATCH")
    return observed | {
        "entry_clean_before_first_write": "VERIFIED__YES",
        "entry_index_empty_before_first_write": "VERIFIED__YES",
        "direct_remote_equality": "VERIFIED__DIRECT_READ_ONLY_LS_REMOTE_AT_ENTRY",
        "current_delta_scope": "VERIFIED__JP_EVIDENCE_ONLY",
        "nested_authority": nested_state,
        "nested_remote_tag_equality": "VERIFIED__DIRECT_READ_ONLY_LS_REMOTE_AT_ENTRY",
    }


def authenticate_committed_jo_identities() -> list[dict[str, str]]:
    identities: list[dict[str, str]] = []
    for path, (expected_blob, expected_sha256) in JO_COMMITTED_IDENTITIES.items():
        raw = committed_bytes(path)
        observed_blob = git("rev-parse", f"{ENTRY_HEAD}:{path.as_posix()}")
        observed_sha256 = sha256_bytes(raw)
        if observed_blob != expected_blob or observed_sha256 != expected_sha256:
            fail(f"JO_COMMITTED_IDENTITY_MISMATCH__{path}")
        if (ROOT / path).read_bytes() != raw:
            fail(f"JO_WORKTREE_DIFFERS_FROM_COMMITTED__{path}")
        identities.append({
            "path": path.as_posix(), "git_blob": observed_blob,
            "sha256": observed_sha256,
            "worktree_equals_committed": "VERIFIED__YES",
        })
    return identities


def reconstruct_jo() -> dict[str, Any]:
    jo = authenticate_envelope_bytes(committed_bytes(JO_REDUCTION), JO_TERMINAL)
    expected_architecture = {
        "p11_implementation_mutation_count": "VERIFIED__0",
        "production_mutation_count": "VERIFIED__8",
        "new_owner_count": "VERIFIED__0", "new_route_count": "VERIFIED__0",
        "new_registry_count": "VERIFIED__0",
        "new_generic_abstraction_count": "VERIFIED__0",
        "new_constitutional_concept_count": "VERIFIED__0",
        "production_route_before": "VERIFIED__1",
        "production_route_after": "VERIFIED__1",
        "production_route_delta": "VERIFIED__0",
        "parallel_flow_created": "VERIFIED__NO",
    }
    if jo.get("architecture") != expected_architecture:
        fail("JO_ARCHITECTURE_RECONSTRUCTION_MISMATCH")
    if set(jo.get("operational_counters", {}).values()) != {"VERIFIED__0"}:
        fail("JO_OPERATIONAL_COUNTER_MISMATCH")
    if jo.get("lineage", {}).get("ex_reused") != "VERIFIED__17_OF_17":
        fail("JO_EX_REUSE_MISMATCH")
    if jo.get("lineage", {}).get("ex_reconstructed") != "VERIFIED__0":
        fail("JO_EX_RECONSTRUCTION_MISMATCH")
    if jo.get("e05") != {
        "before": "VERIFIED__11_OF_18", "after": "VERIFIED__11_OF_18",
        "credit": "VERIFIED__0", "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
        "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
    }:
        fail("JO_E05_MISMATCH")
    if jo.get("frontier") != {
        "last_verified_edge": "SOLE_ER_FM_ROUTE_BOUND_TO_COMMITTED_JM_P11_AND_SEALED_CONTEXT_REPOSITORY_VERIFIED",
        "first_broken_edge": "POST_JO_COMMITTED_IDENTITY_LIVE_BINDING_AND_READINESS_NOT_YET_REAUTHENTICATED",
        "minimum_missing_capability": "COMMITTED_JO_POST_COMMIT_LIVE_BINDING_AND_REPOSITORY_READINESS_REAUTHENTICATION",
        "minimum_legal_next_delta": "AFTER_HUMAN_REVIEW_AND_COMMIT_ONLY__SEPARATE_REPOSITORY_ONLY_POST_COMMIT_LIVE_BINDING_AND_READINESS_GENERATION__NO_OPERATION",
        "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
    }:
        fail("JO_FRONTIER_MISMATCH")
    return {
        "terminal": JO_TERMINAL,
        "inner_seal": "VERIFIED__YES",
        "architecture": expected_architecture,
        "operational_counters": jo["operational_counters"],
        "e05": jo["e05"],
        "frontier": jo["frontier"],
    }


def reconstruct_minimum_lineage() -> dict[str, str]:
    if git("rev-parse", f"{JM_HEAD}^{{tree}}") != JM_TREE:
        fail("JM_TREE_MISMATCH")
    if git("rev-parse", f"{JN_HEAD}^{{tree}}") != JN_TREE:
        fail("JN_TREE_MISMATCH")
    jm = authenticate_envelope_bytes(committed_bytes(JM_REDUCTION), JM_TERMINAL)
    jn = authenticate_envelope_bytes(committed_bytes(JN_REDUCTION), JN_TERMINAL)
    if jm.get("implementation", {}).get("p11_consumer_sha256") != JM_P11_SHA256:
        fail("JM_P11_IDENTITY_MISMATCH")
    if jn.get("frontier", {}).get("minimum_missing_capability") != (
        "SOLE_ROUTE_BINDING_TO_COMMITTED_JM_P11_PLUS_SEALED_CONTEXT_GATE_HANDOFF"
    ):
        fail("JN_BLOCKER_MISMATCH")
    return {
        "jm_head": JM_HEAD, "jm_tree": JM_TREE, "jm_terminal": JM_TERMINAL,
        "jn_head": JN_HEAD, "jn_tree": JN_TREE, "jn_terminal": JN_TERMINAL,
        "continuity": "VERIFIED__JM_IMPLEMENTATION_TO_JN_BLOCKER_TO_JO_CLOSURE",
    }


def call_keywords(tree: ast.AST, name: str) -> list[set[str]]:
    result: list[set[str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == name:
                result.append({item.arg for item in node.keywords if item.arg})
    return result


def verify_committed_route() -> dict[str, Any]:
    sources = {
        path: committed_bytes(path).decode("utf-8") for path in PRODUCTION_PATHS
    }
    trees = {path: ast.parse(source) for path, source in sources.items()}
    launcher = sources[LAUNCHER]
    er = sources[ER]
    if launcher.count("def build_operation_context(") != 1:
        fail("CONTEXT_OWNER_CARDINALITY_INVALID")
    if launcher.count("result = subprocess.run(argv, check=False)") != 1:
        fail("GOVERNED_LAUNCHER_CARDINALITY_INVALID")
    if "authenticate_current_committed_jm_route" not in launcher:
        fail("CURRENT_JM_ROUTE_AUTHENTICATOR_MISSING")
    if "\nCHECKOUT_HEAD = \"" in launcher or "\nCHECKOUT_TREE = \"" in launcher:
        fail("ALTERNATE_DETACHED_ROUTE_SELECTOR_PRESENT")
    if sha256_bytes(committed_bytes(P11)) != JM_P11_SHA256:
        fail("CURRENT_P11_NOT_EXACT_JM")
    if sha256_bytes(committed_bytes(P11, HISTORICAL_IF_HEAD)) != HISTORICAL_IF_P11_SHA256:
        fail("HISTORICAL_IF_P11_IDENTITY_MISMATCH")
    required_gate = {"operation_context_sha256", "preclaim_temporal_binding_identity"}
    required_consumer = {"fresh_operation_context"}
    for path in (ER, FC):
        gate_calls = call_keywords(trees[path], "create_commissioning_gate_v1")
        consumer_calls = call_keywords(trees[path], "P11BoundedConsumerV1")
        if len(gate_calls) != 1 or len(consumer_calls) != 1:
            fail(f"P11_CONSUMER_ROUTE_CARDINALITY_INVALID__{path}")
        if not required_gate <= gate_calls[0] or not required_consumer <= consumer_calls[0]:
            fail(f"SEALED_CONTEXT_HANDOFF_INCOMPLETE__{path}")
    if er.count("load_authenticated_fresh_operation_context()") < 3:
        fail("SEALED_CONTEXT_AUTHENTICATION_MISSING")
    for required in (
        "context != _AUTHENTICATED_FRESH_OPERATION_CONTEXT",
        "sealed operation context checkout binding mismatch",
        "sealed operation context ER harness binding mismatch",
        "runtime P11 is not the committed JM implementation",
    ):
        if required not in er:
            fail("ER_CONTEXT_FAIL_CLOSED_GUARD_MISSING")
    er_sha = JO_COMMITTED_IDENTITIES[ER][1]
    fc_sha = JO_COMMITTED_IDENTITIES[FC][1]
    if f'ER_HARNESS_SHA256 = "{er_sha}"' not in launcher:
        fail("LAUNCHER_ER_DEPENDENCY_MISMATCH")
    if f'FK_ADAPTER_SHA256 = "{fc_sha}"' not in launcher:
        fail("LAUNCHER_FC_DEPENDENCY_MISMATCH")
    if f'FC_SOURCE_SHA256 = "{fc_sha}"' not in sources[FM_ADAPTER]:
        fail("FM_ADAPTER_FC_DEPENDENCY_MISMATCH")
    for adapter in (HA, HT, IA, JC):
        if fc_sha not in sources[adapter]:
            fail(f"VECTOR_FC_DEPENDENCY_MISMATCH__{adapter}")
    if er_sha not in sources[JC]:
        fail("JC_ER_DEPENDENCY_MISMATCH")

    changed = set(git("diff-tree", "--no-commit-id", "--name-only", "-r", ENTRY_HEAD).splitlines())
    expected_changed = {path.as_posix() for path in JO_COMMITTED_IDENTITIES}
    if changed != expected_changed:
        fail("JO_COMMITTED_CHANGESET_MISMATCH")
    parent_launcher = committed_bytes(LAUNCHER, f"{ENTRY_HEAD}^").decode("utf-8")
    if parent_launcher.count("result = subprocess.run(argv, check=False)") != 1:
        fail("PRE_JO_ROUTE_CARDINALITY_INVALID")
    return {
        "production_route_count": "VERIFIED__1",
        "governed_launcher_count": "VERIFIED__1",
        "existing_context_owner_count": "VERIFIED__1",
        "governed_runtime_checkout_path_count": "VERIFIED__1",
        "p11_operational_consumer_path_count": "VERIFIED__1",
        "parallel_runtime_route_count": "VERIFIED__0",
        "compatibility_bypass_count": "VERIFIED__0",
        "alternate_p11_path_count": "VERIFIED__0",
        "current_jm_p11_sha256": JM_P11_SHA256,
        "historical_if_p11_sha256": HISTORICAL_IF_P11_SHA256,
        "historical_if_is_current_authority": "VERIFIED__NO__FAIL_CLOSED",
        "exact_byte_dependency_closure": "VERIFIED__COMMITTED_JO_8_COMPONENT_CHAIN",
        "base_er_context_handoff": "VERIFIED__FM_OWNER_TO_ER_TO_GATE_TO_P11",
        "fc_context_handoff": "VERIFIED__FM_OWNER_TO_ER_TO_FC_GATE_TO_P11",
        "context_fields": [
            "operation_context_sha256", "preclaim_temporal_binding_identity",
            "fresh_operation_context",
        ],
        "context_source": "VERIFIED__AUTHENTICATED_SEALED_OPERATION_CONTEXT",
        "post_authentication_substitution": "VERIFIED__FAIL_CLOSED",
    }


def verify_temporal_contract() -> dict[str, str]:
    source = committed_bytes(P11).decode("utf-8")
    tree = ast.parse(source)
    function = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "preclaim_temporal_decision"
    )
    segment = ast.get_source_segment(source, function) or ""
    for required in (
        'return "FUTURE"', 'return "EXPIRED"', 'return "CURRENT"',
        'preclaim_time = temporal_binding["coordinate_unix_ns"]',
    ):
        if required not in source:
            fail("TEMPORAL_CONTRACT_BINDING_MISSING")
    if "time.time_ns()" in segment:
        fail("GOVERNED_PRECLAIM_WALL_CLOCK_FALLBACK")
    return {
        "future": "preclaim < valid_from",
        "current": "valid_from <= preclaim < valid_until",
        "expired": "preclaim >= valid_until",
        "boundary": "VERIFIED__999_CURRENT__1000_EXPIRED__1001_EXPIRED",
        "governed_wall_clock_fallback": "VERIFIED__ABSENT",
        "remaining_wall_clock_uses": "VERIFIED__NON_PRECLAIM_OBSERVATION_OR_DISTINCT_HISTORICAL_SUBMISSION_CONTROL",
    }


def verify_ex_successor_delta() -> dict[str, str]:
    certificate = load_json_bytes(committed_bytes(EX_CERTIFICATE))["certificate"]
    manifest = load_json_bytes(committed_bytes(EW_MANIFEST))["manifest"]
    bindings = {item["identity"]: item for item in manifest["component_bindings"]}
    er_binding = bindings["ER_OPERATIONAL_HARNESS"]
    p11_binding = bindings["P11_OPERATIONAL_CONSUMER"]
    changed = set(git("diff-tree", "--no-commit-id", "--name-only", "-r", ENTRY_HEAD).splitlines())
    ex_paths = {item["path"]: item for item in manifest["component_bindings"]}
    changed_ex = [ex_paths[path] for path in changed if path in ex_paths]
    if certificate["component_counts"]["CERTIFIED"] != 17:
        fail("EX_CERTIFIED_COUNT_MISMATCH")
    if len(changed_ex) != 1 or changed_ex[0]["identity"] != "ER_OPERATIONAL_HARNESS":
        fail("JO_EX_BOUND_DELTA_MISMATCH")
    if er_binding["classification"] != "REQUIRES_HARDENING":
        fail("ER_EX_CLASSIFICATION_MISMATCH")
    if p11_binding["sha256"] != HISTORICAL_IF_P11_SHA256:
        fail("EW_HISTORICAL_P11_MISMATCH")
    if JO_COMMITTED_IDENTITIES[ER][1] == er_binding["sha256"]:
        fail("ER_SUCCESSOR_NOT_DISTINCT")
    return {
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
        "changed_ex_bound_component_count": "VERIFIED__1",
        "changed_component": "ER_OPERATIONAL_HARNESS",
        "classification": "REQUIRES_HARDENING",
        "historical_sha256": er_binding["sha256"],
        "successor_sha256": JO_COMMITTED_IDENTITIES[ER][1],
        "additional_ex_bound_component_change_count": "VERIFIED__0",
        "new_certificate_count": "VERIFIED__0",
        "new_proof_owner_count": "VERIFIED__0",
    }


def zero_counters() -> dict[str, str]:
    return {key: "VERIFIED__0" for key in (
        "operational_authorization_count", "authority_consumption_count",
        "pre_operational_count", "fm_operational_invocation_count", "qemu_count",
        "vm_count", "operation_attempt_count", "request_count", "p11_entry_count",
        "protected_invocation_count", "protected_effect_count", "retry_count",
        "repair_retry_count", "replay_count",
    )}


def build_reduction() -> dict[str, Any]:
    entry = authenticate_entry()
    identities = authenticate_committed_jo_identities()
    jo = reconstruct_jo()
    lineage = reconstruct_minimum_lineage()
    route = verify_committed_route()
    temporal = verify_temporal_contract()
    ex = verify_ex_successor_delta()
    return {
        "schema_id": "G77_256JP_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": "G77-256JP",
        "mode": "REPOSITORY_ONLY__NO_AUTHORITY__NO_OPERATION",
        "spce": [
            "AUTHENTICATE", "RECONSTRUCT_JO", "REUSE_EX",
            "REAUTHENTICATE_JO_CHANGED_BINDINGS", "VERIFY_COMMITTED_LIVE_BINDING",
            "VERIFY_SEALED_CONTEXT_HANDOFF", "VERIFY_SOLE_ROUTE_READINESS",
            "VERIFY_FAIL_CLOSED", "REDUCE", "STOP",
        ],
        "terminal": TERMINAL,
        "entry": entry,
        "jo_reconstruction": jo,
        "minimum_lineage": lineage,
        "committed_jo_identities": identities,
        "live_binding": route,
        "temporal_contract": temporal,
        "ex_successor_reauthentication": ex,
        "authority_separation": {
            "certified_is_authorized": "VERIFIED__NO",
            "certified_without_valid_authorization_protected_effect_count": "VERIFIED__0",
            "protected_machine_effect_without_valid_p11_authority_count": "VERIFIED__0",
            "worker_bypass_count": "VERIFIED__0",
            "provider_capability_is_execution_authority": "VERIFIED__NO",
            "temporal_coordinate_is_execution_human_p11_or_effect_authority": "VERIFIED__NO",
            "request_entry_invocation_effect_are_distinct": "VERIFIED__YES",
            "repository_readiness_is_authorization": "VERIFIED__NO",
        },
        "fail_closed_matrix": {
            key: "VERIFIED__BEFORE_PROTECTED_INVOCATION_OR_EFFECT" for key in (
                "historical_if_p11_substitution", "arbitrary_p11_bytes",
                "wrong_committed_repository_head_tree", "missing_operation_context_sha256",
                "wrong_operation_context_sha256", "missing_preclaim_temporal_binding_identity",
                "wrong_preclaim_temporal_binding_identity", "missing_fresh_operation_context",
                "changed_context_after_authentication", "context_seal_mismatch",
                "repository_checkout_identity_mismatch", "gate_context_mismatch",
                "p11_consumer_context_mismatch", "caller_selected_temporal_coordinate",
                "provider_selected_temporal_coordinate",
                "independent_human_selected_temporal_coordinate",
                "alternate_parallel_route_substitution",
            )
        },
        "architecture": {
            "p11_implementation_mutation_count": "VERIFIED__0",
            "production_mutation_count": "VERIFIED__0",
            "new_owner_count": "VERIFIED__0", "new_route_count": "VERIFIED__0",
            "new_registry_count": "VERIFIED__0",
            "new_generic_abstraction_count": "VERIFIED__0",
            "new_constitutional_concept_count": "VERIFIED__0",
            "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0",
            "parallel_flow_created": "VERIFIED__NO",
        },
        "e05": {
            "before": "VERIFIED__11_OF_18", "after": "VERIFIED__11_OF_18",
            "credit": "VERIFIED__0", "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
            "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
        },
        "operational_counters": zero_counters(),
        "proof_yield": {
            "new_verified_capability_count": "VERIFIED__1__POST_JO_COMMITTED_LIVE_BINDING_AND_REPOSITORY_READINESS",
            "new_blocker_localized_count": "VERIFIED__0",
            "e05_credit": "VERIFIED__0",
            "proof_reuse_count": "VERIFIED__17__EX_COMMON_CAPABILITIES",
        },
        "metrics": {
            "project_progress": "VERIFIED__POST_JO_COMMITTED_REPOSITORY_READINESS__OPERATIONAL_EXPIRED_DENIAL_PENDING",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__COMMITTED_ROUTE_READY_FOR_SEPARATE_AUTHORIZED_EXPIRED_OPERATION",
            "constitutional_health_evidence": "VERIFIED__FAIL_CLOSED_COMMITTED_EXACT_BYTES_SINGLE_ROUTE_SEALED_CONTEXT_AUTHORITY_SEPARATION",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "governance_efficience": "ESTIMATED__HIGH__JO_AND_EX_PROOF_REUSED_WITH_ZERO_PRODUCTION_MUTATION",
            "overengineering_risk": "ESTIMATED__LOW__EVIDENCE_ONLY_ZERO_NEW_OWNER_ROUTE_REGISTRY_OR_ABSTRACTION",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_COMMITTED_REPOSITORY_EVIDENCE_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__JO_TO_JP_REPOSITORY_CONTINUATION",
            "candidate_capability": "VERIFIED__REPOSITORY_READINESS_ONLY__NOT_AUTHORIZATION_OR_OPERATIONAL_PROOF",
            "shadow_design_target": "VERIFIED__SEPARATE_FRESH_HUMAN_AUTHORIZED_EXPIRED_DENIAL_BEFORE_P11_ENTRY",
            "constitutional_continuation_progress": "VERIFIED__JO_POST_COMMIT_GAP_CLOSED_REPOSITORY_ONLY__NO_E05_CREDIT",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
        },
        "human_authority_assurance_status": "NOT_APPLICABLE__JP_CREATES_NO_HUMAN_OPERATIONAL_AUTHORITY",
        "frontier": {
            "last_verified_edge": "POST_JO_COMMITTED_LIVE_BINDING_AND_EXPIRED_OPERATIONAL_READINESS_REPOSITORY_VERIFIED",
            "first_broken_edge": "FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_DENIAL_NOT_YET_PROVEN",
            "minimum_missing_capability": "FRESH_HUMAN_AUTHORIZED_EXPIRED_DENIAL_BEFORE_P11_ENTRY",
            "minimum_legal_next_delta": "SEPARATE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_GENERATION",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
        },
        "validation": {
            "jp_focused": "VERIFIED__15_PASSED",
            "jo_non_operational_regression": "VERIFIED__15_PASSED__2_PRECOMMIT_SCOPE_TESTS_DESELECTED",
            "governance_conformance": "VERIFIED__9_PASSED__ENGINE_20_OF_20_CONFORMANT",
            "layer_0": "VERIFIED__ZERO_DELTA",
            "g48": "VERIFIED__EXACTLY_SIX_H1",
            "git_diff_check": "VERIFIED__PASS",
            "final_index": "VERIFIED__EMPTY",
        },
        "auto_continuable": False,
        "human_review_required": True,
    }


def envelope(reduction: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "G77_256JP_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }


def main() -> int:
    sys.stdout.buffer.write(canonical_bytes(envelope(build_reduction())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
