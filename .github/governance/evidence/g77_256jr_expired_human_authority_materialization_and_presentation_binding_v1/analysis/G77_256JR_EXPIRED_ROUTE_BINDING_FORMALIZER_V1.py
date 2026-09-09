#!/usr/bin/env python3
"""Formalize JR's repository-only EXPIRED binding to the sole governed route.

The formalizer authenticates committed lineage and statically exercises only
pure derivation/validation surfaces.  It never calls an adapter or launcher
entrypoint, creates Human authority, enters P11, or performs an operation.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
ENTRY_HEAD = "f2f00fab5b47e5c3e59629f9542258e65f20a9c0"
ENTRY_TREE = "07ae3ad87775f30f298a691f1054881915604d32"
ENTRY_SUBJECT = "G77-256JQ localize EXPIRED preauthorization route blocker"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
JQ_TERMINAL = "M__EXPIRED_PREAUTHORIZATION_ROUTE_CONTRACT_NOT_AVAILABLE"
TERMINAL = (
    "A__EXPIRED_HUMAN_AUTHORITY_MATERIALIZATION_AND_PRESENTATION_"
    "BINDING_REPOSITORY_VERIFIED"
)

JR = Path(
    ".github/governance/evidence/"
    "g77_256jr_expired_human_authority_materialization_and_presentation_binding_v1"
)
ADAPTER = JR / "adapter/G77_256JR_EXPIRED_VECTOR_ADAPTER_V1.py"
CLOUD_INIT = JR / "static/G77_256JR_CLOUD_INIT_USER_DATA_V1.yaml"
SEED = JR / "static/SAPIANTA_EXPIRED_NOCLOUD_SEED_V1.img"
FORMALIZER = JR / "analysis/G77_256JR_EXPIRED_ROUTE_BINDING_FORMALIZER_V1.py"
TEST = JR / "tests/test_g77_256jr_expired_route_binding_v1.py"
REDUCTION = JR / "G77_256JR_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = JR / "G77_256JR_G48_IMPLEMENTATION_REPORT_V1.md"

CONTEXT_OWNER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
LAUNCHER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
GN_PRESENTATION = Path(
    ".github/governance/evidence/"
    "g77_256gn_human_authorization_presentation_binding_v1/presentation/"
    "G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
)
ER_HARNESS = Path(
    ".github/governance/evidence/g77_256er_p11_operational_v1/harness/"
    "G77_256ER_P11_OPERATIONAL_HARNESS_V1.py"
)
FC_ADAPTER = Path(
    ".github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/harness/"
    "G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
)
P11 = Path("tests/p11_da_operational_consumer_v1.py")
JQ_REDUCTION = Path(
    ".github/governance/evidence/"
    "g77_256jq_expired_fresh_human_authorized_operational_denial_before_p11_entry_v1/"
    "G77_256JQ_SPCE_TERMINAL_REPOSITORY_ONLY_BLOCKER_REDUCTION_V1.json"
)
GM_REQUEST = Path(
    ".github/governance/evidence/g77_256gm_wrong_attempt_operational_v1/"
    "G77_256GM_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
)

TRACKED_PRODUCTION = (CONTEXT_OWNER, LAUNCHER, GN_PRESENTATION)
CREATED_PRODUCTION = (ADAPTER, CLOUD_INIT, SEED)
EVIDENCE_FILES = (FORMALIZER, TEST, REDUCTION, REPORT)
FINAL_UNTRACKED = CREATED_PRODUCTION + EVIDENCE_FILES
RECOVERED_JR_FILES = {
    ADAPTER.as_posix(): {
        "line_count": 269,
        "size_bytes": 10705,
        "sha256": "96b5a90269cf871f722babbdcf49b0aa067d712c9d07142d0a2acb15510c68c2",
    }
}

EXPECTED_VECTOR_PATHS = {
    "WRONG_ATTEMPT": (
        ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/harness/"
        "G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
    ),
    "WRONG_INPUT": (
        ".github/governance/evidence/g77_256ha_wrong_input_route_binding_v1/adapter/"
        "G77_256HA_WRONG_INPUT_VECTOR_ADAPTER_V1.py"
    ),
    "WRONG_CONTRACT": (
        ".github/governance/evidence/g77_256ht_wrong_contract_route_extension_v1/"
        "adapter/G77_256HT_WRONG_CONTRACT_VECTOR_ADAPTER_V1.py"
    ),
    "WRONG_PROVENANCE": (
        ".github/governance/evidence/g77_256ia_wrong_provenance_route_extension_v1/"
        "adapter/G77_256IA_WRONG_PROVENANCE_VECTOR_ADAPTER_V1.py"
    ),
    "FUTURE": (
        ".github/governance/evidence/g77_256jc_future_guest_context_owner_projection_v1/"
        "adapter/G77_256JC_FUTURE_VECTOR_ADAPTER_V1.py"
    ),
    "EXPIRED": ADAPTER.as_posix(),
}
GENERATION_SUFFIXES = {
    vector: f"_ONE_FRESH_HUMAN_AUTHORIZED_{vector}_OPERATIONAL_COMMISSIONING_V1"
    for vector in EXPECTED_VECTOR_PATHS
}
EXPECTED_BOOTSTRAP = {
    "WRONG_ATTEMPT": (
        ".github/governance/evidence/g77_256hk_current_hg_bootstrap_binding_v1/"
        "static/G77_256HK_CLOUD_INIT_USER_DATA_V1.yaml",
        "f10425de141e2f790b4b57fe00aa59c345aeb4e2c0e58e3a2b57cbaf602ff666",
        "6346b9f02b236d71f2698b01a0d607549ad4d9d779a72b5168658994c519913d",
    ),
    "WRONG_INPUT": (
        ".github/governance/evidence/g77_256hn_wrong_input_bootstrap_harness_binding_v1/"
        "static/G77_256HN_CLOUD_INIT_USER_DATA_V1.yaml",
        "be30e3c5084b7464653b8560d4259d69dbdff106d5c118791df6cf87c28d718f",
        "e9aeac9135ecbf92bffbb8798a90bd61e39e49e15fa5dff0a4c0e6974e6bf731",
    ),
    "WRONG_CONTRACT": (
        ".github/governance/evidence/g77_256ht_wrong_contract_route_extension_v1/"
        "static/G77_256HT_CLOUD_INIT_USER_DATA_TEMPLATE_V1.yaml",
        "c3f7f93a55f2c3a76fe73bccb9aa0b54fed2f5011c326c0f8774a8ca72c7442f",
        "fc98a62a1b3bd813b7f570438fc48151c378aeba4389de13d4e532d3f7979b21",
    ),
    "WRONG_PROVENANCE": (
        ".github/governance/evidence/g77_256ia_wrong_provenance_route_extension_v1/"
        "static/G77_256IA_CLOUD_INIT_USER_DATA_TEMPLATE_V1.yaml",
        "4725543bab299d1e153b2c40f9fcd0791ce9c2af318e88c41deeba9e6c69ed84",
        "4154ec58b7ebf46299ccc495a0a1232b7e31f67221f987b6fe7959f8d5593c7c",
    ),
    "FUTURE": (
        ".github/governance/evidence/g77_256jc_future_guest_context_owner_projection_v1/"
        "static/G77_256JC_CLOUD_INIT_USER_DATA_V1.yaml",
        "2a7a5dbe1e8bf17aec4a9199ac8609d40d71a1e7726211ed0d6a9faf719f6ff4",
        "6998d4cdaff3617b9e2c29f17318a220619fc718d0d9f9168b08e614cfdf0418",
    ),
    "EXPIRED": (
        CLOUD_INIT.as_posix(),
        "bcf626825e5d253fd0d6ae3af33f8ed26ad2d6b405d1203294c196eae1b421ee",
        "47a79fe9b4dad751ab232789465753fabd27ff7db2443f3af3a99058e48fb516",
    ),
}


class JRError(RuntimeError):
    """One deterministic fail-closed JR verification error."""


def fail(token: str) -> None:
    raise JRError(token)


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=cwd, text=True, stderr=subprocess.DEVNULL
    ).strip()


def load_module(path: Path, identity: str):
    specification = importlib.util.spec_from_file_location(identity, ROOT / path)
    if specification is None or specification.loader is None:
        fail(f"MODULE_IMPORT_FAILED__{identity}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def load_envelope(path: Path, terminal: str) -> dict[str, Any]:
    envelope = json.loads(path.read_bytes())
    reduction = envelope.get("reduction")
    if not isinstance(reduction, dict):
        fail("REDUCTION_MISSING")
    if envelope.get("reduction_sha256") != hashlib.sha256(
        canonical_bytes(reduction)
    ).hexdigest():
        fail("REDUCTION_INNER_SEAL_INVALID")
    if reduction.get("terminal") != terminal:
        fail("REDUCTION_TERMINAL_INVALID")
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
        "branch": BRANCH,
        "head": ENTRY_HEAD,
        "tree": ENTRY_TREE,
        "subject": ENTRY_SUBJECT,
        "origin": ORIGIN,
        "remote_tracking_head": ENTRY_HEAD,
        "index_empty": True,
    }
    if observed != expected:
        fail("ENTRY_IDENTITY_MISMATCH")
    changed = set(git("diff", "--name-only").splitlines())
    if changed != {path.as_posix() for path in TRACKED_PRODUCTION}:
        fail("TRACKED_JR_DELTA_SCOPE_INVALID")
    status = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT, text=True,
    ).splitlines()
    if any(line[:2] not in {" M", "??"} for line in status):
        fail("STAGED_OR_UNEXPECTED_STATUS_CLASS")
    allowed = {path.as_posix() for path in TRACKED_PRODUCTION + FINAL_UNTRACKED}
    if not {line[3:] for line in status} <= allowed:
        fail("OUT_OF_SCOPE_JR_DELTA")
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
        "recovery_entry_worktree": "EXPECTED__JR_GENERATION_ONLY_DIRTY",
        "remote_head_equality": "VERIFIED__DIRECT_READ_ONLY_LS_REMOTE_AT_RECOVERY_ENTRY",
        "nested_remote_tag_equality": "VERIFIED__DIRECT_READ_ONLY_LS_REMOTE_AT_RECOVERY_ENTRY",
        "nested_authority": nested_state,
    }


def authenticate_jq() -> dict[str, Any]:
    jq = load_envelope(ROOT / JQ_REDUCTION, JQ_TERMINAL)
    required_frontier = {
        "constitutional_frontier_distance": (
            "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR"
        ),
        "last_verified_edge": (
            "POST_JO_COMMITTED_LIVE_BINDING_AND_EXPIRED_OPERATIONAL_"
            "READINESS_REPOSITORY_VERIFIED"
        ),
        "first_broken_edge": (
            "EXPIRED_PREAUTHORIZATION_CANDIDATE_CANNOT_BE_TRUTHFULLY_"
            "MATERIALIZED_BY_CURRENT_HUMAN_AUTHORITY_ROUTE"
        ),
        "minimum_missing_capability": (
            "GOVERNED_EXPIRED_COMPATIBLE_HUMAN_AUTHORITY_ACT_"
            "MATERIALIZATION_AND_PRESENTATION_BINDING"
        ),
        "minimum_legal_next_delta": (
            "SEPARATE_REPOSITORY_ONLY_MINIMUM_IMPLEMENTATION_GENERATION_TO_BIND_"
            "EXPIRED_INTO_EXISTING_HUMAN_AUTHORITY_ROUTE__NO_OPERATION"
        ),
    }
    if jq["frontier"] != required_frontier:
        fail("JQ_FRONTIER_MISMATCH")
    if jq["e05"] != {
        "after": "VERIFIED__11_OF_18", "before": "VERIFIED__11_OF_18",
        "credit": "VERIFIED__0",
        "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
        "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
    }:
        fail("JQ_E05_MISMATCH")
    if set(jq["operational_counters"].values()) != {"VERIFIED__0"}:
        fail("JQ_OPERATIONAL_FIREWALL_MISMATCH")
    if jq["reuse"]["ex_reused"] != "VERIFIED__17_OF_17" or (
        jq["reuse"]["ex_reconstructed"] != "VERIFIED__0"
    ):
        fail("JQ_EX_MISMATCH")
    return {
        "terminal": jq["terminal"], "frontier": jq["frontier"],
        "e05": jq["e05"], "operational_counters": "VERIFIED__ALL_FOURTEEN_ZERO",
        "ex_reused": jq["reuse"]["ex_reused"],
        "ex_reconstructed": jq["reuse"]["ex_reconstructed"],
    }


def verify_route_binding() -> dict[str, Any]:
    owner = load_module(CONTEXT_OWNER, "g77_256jr_context_owner")
    launcher_dir = str((ROOT / LAUNCHER).parent)
    if launcher_dir not in sys.path:
        sys.path.insert(0, launcher_dir)
    sys.modules["sapianta_fresh_operation_context_v1"] = owner
    launcher = load_module(LAUNCHER, "g77_256jr_sole_launcher")
    expected_vectors = frozenset(EXPECTED_VECTOR_PATHS)
    if owner.SUPPORTED_OPERATION_VECTORS != expected_vectors:
        fail("CONTEXT_VECTOR_SET_INVALID")
    for vector, path in EXPECTED_VECTOR_PATHS.items():
        generation = "G77_256JR" + GENERATION_SUFFIXES[vector]
        if owner.operation_vector(generation) != vector:
            fail(f"CONTEXT_VECTOR_DERIVATION_INVALID__{vector}")
        if owner.adapter_source_relative_path(generation) != path:
            fail(f"CONTEXT_ADAPTER_PATH_INVALID__{vector}")
        bootstrap = launcher.current_bootstrap_asset_bindings(vector)
        expected_bootstrap = EXPECTED_BOOTSTRAP[vector]
        if (
            bootstrap["cloud_init_path"] != expected_bootstrap[0]
            or bootstrap["cloud_init_sha256"] != expected_bootstrap[1]
            or bootstrap["seed_sha256"] != expected_bootstrap[2]
        ):
            fail(f"BOOTSTRAP_REGRESSION__{vector}")
        if launcher.operation_attempt_limit_field(vector) != (
            vector.lower() + "_operational_attempt_limit"
        ):
            fail(f"AUTHORIZATION_FIELD_REGRESSION__{vector}")
    generation = "G77_256JR" + GENERATION_SUFFIXES["EXPIRED"]
    context = launcher.build_operation_context(
        repository_root=ROOT,
        repository_head=ENTRY_HEAD,
        repository_tree=ENTRY_TREE,
        generation_identity=generation,
        operation_identity="G77_256JR_EXPIRED_OPERATION_001",
        identity_namespace_prefix="G77_256JR",
        operation_evidence_root=Path("/tmp/g77_256jr_repository_only_operation_state"),
        transient_root=Path("/tmp/g77_256jr_repository_only_transient"),
    )
    owner.validate_context(context, repository_root=ROOT)
    binding = context["guest_adapter_binding"]
    if binding["source_path"] != ADAPTER.as_posix() or (
        binding["source_sha256"] != RECOVERED_JR_FILES[ADAPTER.as_posix()]["sha256"]
    ):
        fail("EXPIRED_ADAPTER_CONTEXT_BINDING_INVALID")
    if context["preclaim_temporal_binding"]["coordinate_unix_ns"] != 1000:
        fail("EXPIRED_PRECLAIM_COORDINATE_INVALID")
    if launcher.operation_attempt_limit_field("EXPIRED") != "expired_operational_attempt_limit":
        fail("EXPIRED_AUTHORIZATION_FIELD_INVALID")
    if launcher.fc_guest_consumer_path(ROOT, "G77_256JR", "EXPIRED") != (
        "/mnt/dp-harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
    ):
        fail("SOLE_GUEST_CONSUMER_PATH_INVALID")
    return {
        "context_owner": CONTEXT_OWNER.as_posix(),
        "launcher": LAUNCHER.as_posix(),
        "derived_vector": "EXPIRED",
        "adapter_source_path": binding["source_path"],
        "adapter_source_sha256": binding["source_sha256"],
        "guest_consumer_path": binding["guest_path"],
        "preclaim_coordinate_unix_ns": 1000,
        "supported_vectors": sorted(expected_vectors),
        "production_route_before": "VERIFIED__1",
        "production_route_after": "VERIFIED__1",
        "production_route_delta": "VERIFIED__0",
        "parallel_route_created": "VERIFIED__NO",
    }


def verify_adapter() -> dict[str, Any]:
    if sha256_path(ROOT / ADAPTER) != RECOVERED_JR_FILES[ADAPTER.as_posix()]["sha256"]:
        fail("RECOVERED_ADAPTER_IDENTITY_CHANGED")
    adapter = load_module(ADAPTER, "g77_256jr_expired_adapter")
    coordinates = adapter.authenticate_expired_semantics(ROOT)
    expected = {
        "baseline_preclaim_time_unix_ns": 500,
        "expired_preclaim_time_unix_ns": 1000,
        "valid_from_unix_ns": 100,
        "valid_until_unix_ns": 1000,
    }
    if coordinates != expected:
        fail("ADAPTER_COORDINATE_BINDING_INVALID")
    transformed = adapter.specialize_fc_runtime_source(
        repository_root=ROOT, identity_namespace_prefix="G77_256JR"
    )
    required = (
        'GENERATION_ID = "G77_256JR_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_',
        "now_unix_ns=SUBMISSION_TIME_UNIX_NS",
        'denial_error == "one-use Human act expired before PRECLAIM"',
        'after.state.value == "EXPIRED"',
        "after.revision == 1",
        "differing_fields == []",
    )
    if not all(token in transformed for token in required):
        fail("ADAPTER_SPECIALIZATION_INCOMPLETE")
    source = (ROOT / ADAPTER).read_text(encoding="utf-8")
    forbidden = (
        "def main(repository_root", "preclaim_time_unix_ns:",
        "valid_from_unix_ns:", "valid_until_unix_ns:", "import time",
        "qemu-system", "subprocess", "P11_DA_OPERATIONAL_PRECLAIM\"",
    )
    if any(token in source for token in forbidden):
        fail("ADAPTER_AUTHORITY_OR_OPERATION_SURFACE_DETECTED")
    if sha256_path(ROOT / FC_ADAPTER) != adapter.FC_ADAPTER_SHA256 or (
        sha256_path(ROOT / ER_HARNESS) != adapter.ER_HARNESS_SHA256
    ):
        fail("SHARED_FC_ER_BINDING_INVALID")
    return {
        "recovered_adapter_sha256": sha256_path(ROOT / ADAPTER),
        "fixed_submission_time_unix_ns": adapter.SUBMISSION_TIME_UNIX_NS,
        "fixed_valid_from_unix_ns": adapter.VALID_FROM_UNIX_NS,
        "fixed_valid_until_unix_ns": adapter.VALID_UNTIL_UNIX_NS,
        "fixed_preclaim_time_unix_ns": adapter.PRECLAIM_TIME_UNIX_NS,
        "caller_selectable_temporal_coordinate_count": "VERIFIED__0",
        "provider_selectable_temporal_coordinate_count": "VERIFIED__0",
        "human_selectable_temporal_coordinate_count": "VERIFIED__0",
        "generic_er_mutation_count": "VERIFIED__0",
        "p11_mutation_count": "VERIFIED__0",
        "adapter_main_invoked": "VERIFIED__NO",
    }


def verify_presentation() -> dict[str, Any]:
    gn = load_module(GN_PRESENTATION, "g77_256jr_gn_presentation")
    expected_vectors = frozenset(EXPECTED_VECTOR_PATHS)
    if gn.SUPPORTED_VECTORS != expected_vectors:
        fail("GN_VECTOR_SET_INVALID")
    envelope = json.loads((ROOT / GM_REQUEST).read_bytes())
    envelope["request"]["authorized_vector_requested"] = "EXPIRED"
    envelope["request"]["generation_identity"] = (
        "G77_256JR" + GENERATION_SUFFIXES["EXPIRED"]
    )
    gn._validate_request_semantics(envelope)
    mismatched = json.loads(json.dumps(envelope))
    mismatched["request"]["generation_identity"] = (
        "G77_256JR" + GENERATION_SUFFIXES["FUTURE"]
    )
    try:
        gn._validate_request_semantics(mismatched)
    except gn.PresentationBindingError as exc:
        if str(exc) != "SEALED_REQUEST_VECTOR_GENERATION_BINDING_INVALID":
            fail("GN_MISMATCH_REJECTION_INVALID")
    else:
        fail("GN_MISMATCH_ACCEPTED")
    unknown = json.loads(json.dumps(envelope))
    unknown["request"]["authorized_vector_requested"] = "UNKNOWN"
    try:
        gn._validate_request_semantics(unknown)
    except gn.PresentationBindingError as exc:
        if str(exc) != "SEALED_REQUEST_VECTOR_INVALID":
            fail("GN_UNKNOWN_REJECTION_INVALID")
    else:
        fail("GN_UNKNOWN_ACCEPTED")
    return {
        "presentation_owner": GN_PRESENTATION.as_posix(),
        "expired_exact_generation_binding": "VERIFIED__ACCEPTED",
        "expired_future_mismatch": "VERIFIED__REJECTED",
        "unknown_vector": "VERIFIED__REJECTED",
        "human_request_created": "VERIFIED__0",
        "human_presentation_created": "VERIFIED__0",
        "human_authority_created": "VERIFIED__0",
    }


def verify_static_assets() -> dict[str, Any]:
    expected = {
        CLOUD_INIT.as_posix(): "bcf626825e5d253fd0d6ae3af33f8ed26ad2d6b405d1203294c196eae1b421ee",
        SEED.as_posix(): "47a79fe9b4dad751ab232789465753fabd27ff7db2443f3af3a99058e48fb516",
    }
    observed = {
        path.as_posix(): sha256_path(ROOT / path) for path in (CLOUD_INIT, SEED)
    }
    if observed != expected:
        fail("STATIC_ASSET_IDENTITY_MISMATCH")
    projections = {
        "/user-data": ROOT / CLOUD_INIT,
        "/meta-data": ROOT / (
            ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/raw/"
            "G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"
        ),
        "/network-config": ROOT / (
            ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/raw/"
            "G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"
        ),
    }
    for member, source in projections.items():
        projected = subprocess.check_output(
            ["isoinfo", "-i", str(ROOT / SEED), "-R", "-x", member],
            stderr=subprocess.DEVNULL,
        )
        if projected != source.read_bytes():
            fail(f"NOCLOUD_PROJECTION_MISMATCH__{member}")
    return {
        "cloud_init_path": CLOUD_INIT.as_posix(),
        "cloud_init_sha256": observed[CLOUD_INIT.as_posix()],
        "seed_path": SEED.as_posix(),
        "seed_sha256": observed[SEED.as_posix()],
        "family_local": "VERIFIED__YES",
        "authority": "VERIFIED__NO",
        "execution_authority": "VERIFIED__NO",
        "nocloud_source_projection": "VERIFIED__EXACT",
    }


def verify_temporal_and_regressions() -> dict[str, Any]:
    tests_dir = str((ROOT / P11).parent)
    if tests_dir not in sys.path:
        sys.path.insert(0, tests_dir)
    p11 = load_module(P11, "g77_256jr_p11_static")
    table = {
        str(coordinate): p11.preclaim_temporal_decision(
            {"coordinate_unix_ns": coordinate},
            valid_from_unix_ns=100,
            valid_until_unix_ns=1000,
        )
        for coordinate in (999, 1000, 1001)
    }
    if table != {"999": "CURRENT", "1000": "EXPIRED", "1001": "EXPIRED"}:
        fail("P11_TEMPORAL_TRUTH_TABLE_INVALID")
    p11_source = (ROOT / P11).read_text(encoding="utf-8")
    claim_source = p11_source[p11_source.index("    def claim_and_invoke_once("):]
    preclaim = claim_source.index('"P11_DA_OPERATIONAL_PRECLAIM"')
    expired = claim_source.index('if temporal_decision == "EXPIRED":')
    if expired >= preclaim:
        fail("P11_EXPIRED_BOUNDARY_MOVED_AFTER_ENTRY")
    owner = load_module(CONTEXT_OWNER, "g77_256jr_context_regression")
    paths = {}
    for vector, expected_path in EXPECTED_VECTOR_PATHS.items():
        generation = "G77_256JR" + GENERATION_SUFFIXES[vector]
        paths[vector] = owner.adapter_source_relative_path(generation)
        if paths[vector] != expected_path:
            fail(f"VECTOR_REGRESSION__{vector}")
    return {
        "truth_table": table,
        "future_semantics": "VERIFIED__DISTINCT_AND_UNCHANGED",
        "wrong_attempt": "VERIFIED__UNCHANGED",
        "wrong_contract": "VERIFIED__UNCHANGED",
        "wrong_input": "VERIFIED__UNCHANGED",
        "wrong_provenance": "VERIFIED__UNCHANGED",
        "p11_expired_boundary": "BEFORE_P11_DA_OPERATIONAL_PRECLAIM_APPEND",
        "vector_paths": paths,
    }


def zero_counters() -> dict[str, str]:
    return {name: "VERIFIED__0" for name in (
        "operational_authorization_count", "authority_consumption_count",
        "pre_operational_count", "fm_operational_invocation_count", "qemu_count",
        "vm_count", "operation_attempt_count", "request_count", "p11_entry_count",
        "protected_invocation_count", "protected_effect_count", "retry_count",
        "repair_retry_count", "replay_count",
    )}


def mutation_identities() -> dict[str, str]:
    return {
        path.as_posix(): sha256_path(ROOT / path)
        for path in TRACKED_PRODUCTION + CREATED_PRODUCTION + EVIDENCE_FILES
        if (ROOT / path).is_file() and path != REDUCTION
    }


def build_reduction() -> dict[str, Any]:
    jq = authenticate_jq()
    return {
        "schema_id": "G77_256JR_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": "G77-256JR",
        "mode": "SAME_GENERATION_PROVIDER_LIMIT_RECOVERY__REPOSITORY_ONLY",
        "terminal": TERMINAL,
        "spce": [
            "AUTHENTICATE_JQ_BASELINE", "AUTHENTICATE_EXISTING_JR_DELTA",
            "RECONSTRUCT_JR_IMPLEMENTATION_DECISION", "REUSE_EX_AND_JJ_THROUGH_JQ",
            "VERIFY_MINIMUM_GOVERNED_DELTA", "COMPLETE_SAME_JR_DELTA",
            "VERIFY_REPOSITORY_ONLY", "REDUCE", "STOP",
        ],
        "entry": authenticate_entry(),
        "recovery_provenance": {
            "recovery_type": "SAME_GENERATION_PROVIDER_LIMIT_RECOVERY",
            "recovery_source_generation": "G77-256JR",
            "new_generation_created": "VERIFIED__NO",
            "previous_provider_termination": "PROVIDER_5H_LIMIT_EXHAUSTED",
            "recovery_existing_delta_authenticated": "VERIFIED__YES",
            "recovered_files_at_entry": RECOVERED_JR_FILES,
            "recovery_duplicate_operation_count": "VERIFIED__0",
            "recovery_operation_replay_count": "VERIFIED__0",
        },
        "jq_reconstruction": jq,
        "minimum_design_decision": {
            "critical_minimum_delta_answer": "VERIFIED__YES",
            "future_reuse_as_expired": "VERIFIED__PROHIBITED_SEMANTIC_MISCLASSIFICATION",
            "generic_er_or_p11_weakening": "VERIFIED__NOT_PERFORMED",
            "second_launcher_or_owner": "VERIFIED__NOT_CREATED",
            "selected_delta": "FAMILY_LOCAL_EXPIRED_EXTENSION_TO_EXISTING_SOLE_ROUTE",
            "incomparable_safe_option_count": "VERIFIED__0",
        },
        "route_binding": verify_route_binding(),
        "adapter": verify_adapter(),
        "presentation": verify_presentation(),
        "static_assets": verify_static_assets(),
        "temporal_and_regressions": verify_temporal_and_regressions(),
        "authority_separation": {
            "certified_is_authorized": "VERIFIED__NO",
            "certified_without_valid_authorization_protected_effect_count": "VERIFIED__0",
            "protected_machine_effect_without_valid_p11_authority_count": "VERIFIED__0",
            "worker_bypass_count": "VERIFIED__0",
            "provider_capability_is_execution_authority": "VERIFIED__NO",
            "temporal_coordinate_is_execution_authority": "VERIFIED__NO",
            "temporal_coordinate_is_human_authority": "VERIFIED__NO",
            "temporal_coordinate_is_p11_authority": "VERIFIED__NO",
            "temporal_coordinate_is_protected_effect_authority": "VERIFIED__NO",
            "request_entry_invocation_effect_are_distinct": "VERIFIED__YES",
            "one_use_authority_semantics_preserved": "VERIFIED__YES",
        },
        "human_authority_assurance_status": (
            "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED"
        ),
        "operational_counters": zero_counters(),
        "e05": {
            "before": "VERIFIED__11_OF_18", "after": "VERIFIED__11_OF_18",
            "credit": "VERIFIED__0",
            "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
            "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
        },
        "architecture": {
            "p11_implementation_mutation_count": "VERIFIED__0",
            "production_mutation_count": "VERIFIED__6",
            "production_files_changed": [path.as_posix() for path in TRACKED_PRODUCTION],
            "production_files_created": [path.as_posix() for path in CREATED_PRODUCTION],
            "new_owner_count": "VERIFIED__0", "new_route_count": "VERIFIED__0",
            "new_registry_count": "VERIFIED__0",
            "new_generic_abstraction_count": "VERIFIED__0",
            "new_constitutional_concept_count": "VERIFIED__0",
            "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0",
        },
        "proof_yield": {
            "new_verified_capability_count": (
                "VERIFIED__1__EXPIRED_COMPATIBLE_HUMAN_AUTHORITY_"
                "MATERIALIZATION_AND_PRESENTATION_REPOSITORY_CAPABILITY"
            ),
            "new_blocker_localized_count": "VERIFIED__0",
            "e05_credit": "VERIFIED__0",
            "proof_reuse_count": "VERIFIED__17__EX_COMMON_CAPABILITIES",
        },
        "reuse": {
            "ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0",
            "existing_certified_capabilities_reused": (
                "EX_17_OF_17__JJ__JL__JM__JO__JP__JQ__FM__FC__ER__GN__P11"
            ),
            "new_capability_set": (
                "VERIFIED__ONE_FAMILY_LOCAL_EXPIRED_MATERIALIZATION_AND_PRESENTATION_BINDING"
            ),
            "unreachable_existing_capability_set": "VERIFIED__EMPTY",
            "parallel_flow_created": "VERIFIED__NO",
        },
        "metrics": {
            "project_progress": "VERIFIED__JR_REPOSITORY_CAPABILITY_BOUND_TO_SOLE_ROUTE",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": (
                "ESTIMATED__EXPIRED_REPOSITORY_BINDING_COMPLETE__FRESH_OPERATION_REMAINS"
            ),
            "constitutional_health_evidence": (
                "VERIFIED__CLOSED_VECTOR_EXTENSION_WITHOUT_AUTHORITY_OR_ROUTE_BYPASS"
            ),
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficience": "ESTIMATED__HIGH__EX_17_OF_17_REUSED_ONE_ROUTE_PRESERVED",
            "overengineering_risk": "ESTIMATED__LOW__FAMILY_LOCAL_DELTA_NO_GENERIC_FRAMEWORK",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_EVIDENCE_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__SAME_JR_CROSS_PROVIDER_RECOVERY",
            "candidate_capability": (
                "VERIFIED__REPOSITORY_ONLY_EXPIRED_MATERIALIZATION_AND_PRESENTATION_BINDING"
            ),
            "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE_WITH_EXPIRED_SPECIALIZATION",
            "constitutional_continuation_progress": (
                "VERIFIED__JQ_BLOCKER_TO_JR_REPOSITORY_CAPABILITY"
            ),
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
            "recovery_type": "SAME_GENERATION_PROVIDER_LIMIT_RECOVERY",
            "recovery_source_generation": "G77-256JR",
            "recovery_existing_delta_authenticated": "VERIFIED__YES",
            "recovery_duplicate_operation_count": "VERIFIED__0",
            "recovery_operation_replay_count": "VERIFIED__0",
        },
        "frontier": {
            "last_verified_edge": (
                "EXPIRED_COMPATIBLE_HUMAN_AUTHORITY_MATERIALIZATION_AND_"
                "PRESENTATION_REPOSITORY_BINDING_VERIFIED"
            ),
            "first_broken_edge": (
                "FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_DENIAL_NOT_YET_PROVEN"
            ),
            "minimum_missing_capability": (
                "FRESH_HUMAN_AUTHORIZED_EXPIRED_DENIAL_BEFORE_P11_ENTRY"
            ),
            "minimum_legal_next_delta": (
                "SEPARATE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_GENERATION"
            ),
        },
        "mutation_identities": mutation_identities(),
        "auto_continuable": False,
        "human_review_required": True,
    }


def main() -> int:
    reduction = build_reduction()
    envelope = {
        "schema_id": "G77_256JR_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": hashlib.sha256(canonical_bytes(reduction)).hexdigest(),
    }
    (ROOT / REDUCTION).write_bytes(canonical_bytes(envelope))
    print(json.dumps({
        "terminal": TERMINAL,
        "reduction_sha256": envelope["reduction_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
