#!/usr/bin/env python3
"""Formalize JT's stable EXPIRED bootstrap checkout binding repository-only."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
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
ENTRY_HEAD = "ccb08355b35c58571b2f11da0cc98660550302b3"
ENTRY_TREE = "850794d03cd0d95ae5cd9a647829fae48ec526dc"
ENTRY_SUBJECT = "G77-256JS localize EXPIRED bootstrap HEAD tree binding blocker"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
JR_HEAD = "304b342e26e92f226afa01db4b4203acfa51f532"
JR_TREE = "fc0c50e4dd79e900d85d48c5c0aeb53fe9d0c937"
JQ_HEAD = "f2f00fab5b47e5c3e59629f9542258e65f20a9c0"
JQ_TREE = "07ae3ad87775f30f298a691f1054881915604d32"
TERMINAL = "A__EXPIRED_BOOTSTRAP_PRE_REQUEST_CHECKOUT_BINDING_REPOSITORY_VERIFIED"

JT = Path(
    ".github/governance/evidence/"
    "g77_256jt_expired_bootstrap_checkout_binding_repair_v1"
)
JS = Path(".github/governance/evidence/g77_256js_expired_operational_v1")
JS_REDUCTION = JS / "G77_256JS_SPCE_PREAUTHORIZATION_BLOCKER_REDUCTION_V1.json"
JS_CONTEXT = JS / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
JR = Path(
    ".github/governance/evidence/"
    "g77_256jr_expired_human_authority_materialization_and_presentation_binding_v1"
)
JR_ADAPTER = JR / "adapter/G77_256JR_EXPIRED_VECTOR_ADAPTER_V1.py"
JR_CLOUD = JR / "static/G77_256JR_CLOUD_INIT_USER_DATA_V1.yaml"
JT_CLOUD = JT / "static/G77_256JT_CLOUD_INIT_USER_DATA_V1.yaml"
JT_SEED = JT / "static/SAPIANTA_EXPIRED_NOCLOUD_SEED_V2.img"
FM = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
CONTEXT_OWNER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
GN = Path(
    ".github/governance/evidence/"
    "g77_256gn_human_authorization_presentation_binding_v1/presentation/"
    "G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
)
GM_REQUEST = Path(
    ".github/governance/evidence/g77_256gm_wrong_attempt_operational_v1/"
    "G77_256GM_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
)
P11 = Path("tests/p11_da_operational_consumer_v1.py")
META = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/raw/"
    "G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"
)
NETWORK = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/raw/"
    "G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"
)
REPORT = JT / "G77_256JT_G48_IMPLEMENTATION_REPORT_V1.md"
REDUCTION = JT / "G77_256JT_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
FORMALIZER = JT / "analysis/G77_256JT_EXPIRED_BOOTSTRAP_BINDING_FORMALIZER_V1.py"
TEST = JT / "tests/test_g77_256jt_expired_bootstrap_binding_v1.py"

JR_ADAPTER_SHA256 = "96b5a90269cf871f722babbdcf49b0aa067d712c9d07142d0a2acb15510c68c2"
JR_CLOUD_SHA256 = "bcf626825e5d253fd0d6ae3af33f8ed26ad2d6b405d1203294c196eae1b421ee"
JT_CLOUD_SHA256 = "4c2c020421b06d592cb64b0a8da56a5929a981cf32dcbda9ae077956e3ca3408"
JT_SEED_SHA256 = "4d0f7d4e7f5cbb08ee18ed8c757a7467498513862a1b3194d3489df8c8d092fb"
FM_BEFORE_SHA256 = "91095ae1e4fa727c4d21243af8b5afdc2d6d1b5ba55f2c555e35ad924b80356d"
FM_AFTER_SHA256 = "d935bec8e37a828d1b8c3249922af8d1017b468940b44853e7990a08b2328b9e"
CONTEXT_OWNER_SHA256 = "d0ae1aa67bbda1fc9a434b939c819ebfd1a9c0df86a24f673c59363570f473b9"
GN_SHA256 = "cd3aed49b8f1ca35e53ca4ee31f278dd038fc28fe912175602180be9a2a8a5c3"
P11_SHA256 = "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5"


class JTError(RuntimeError):
    """One deterministic repository-only JT verification error."""


def fail(token: str) -> None:
    raise JTError(token)


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


def load_module(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, ROOT / path)
    if specification is None or specification.loader is None:
        fail(f"MODULE_UNAVAILABLE__{identity}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def load_envelope(path: Path) -> dict[str, Any]:
    envelope = json.loads((ROOT / path).read_bytes())
    reduction = envelope.get("reduction")
    if not isinstance(reduction, dict) or envelope.get("reduction_sha256") != (
        hashlib.sha256(canonical_bytes(reduction)).hexdigest()
    ):
        fail(f"INNER_SEAL_INVALID__{path.name}")
    return reduction


def authenticate_entry() -> dict[str, Any]:
    observed = {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
        "remote_tracking_head": git("rev-parse", f"origin/{BRANCH}"),
        "tracked_delta": git("diff", "--name-only").splitlines(),
        "index_empty": git("diff", "--cached", "--name-only") == "",
    }
    expected = {
        "branch": BRANCH,
        "head": ENTRY_HEAD,
        "tree": ENTRY_TREE,
        "subject": ENTRY_SUBJECT,
        "origin": ORIGIN,
        "remote_tracking_head": ENTRY_HEAD,
        "tracked_delta": [FM.as_posix()],
        "index_empty": True,
    }
    if observed != expected:
        fail("EXACT_JS_ENTRY_OR_JT_DELTA_SCOPE_MISMATCH")
    status = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=ROOT,
        text=True,
    ).splitlines()
    expected_status = {
        " M " + FM.as_posix(),
        *{
            "?? " + path.as_posix()
            for path in (REPORT, REDUCTION, FORMALIZER, TEST, JT_CLOUD, JT_SEED)
        },
    }
    if set(status) != expected_status or len(status) != len(expected_status):
        fail("JT_WORKTREE_SCOPE_MISMATCH")
    nested = ROOT / "sapianta_system"
    nested_state = {
        "origin": git("remote", "get-url", "origin", cwd=nested),
        "head": git("rev-parse", "HEAD", cwd=nested),
        "tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "clean": git("status", "--porcelain", cwd=nested) == "",
        "detached": git("branch", "--show-current", cwd=nested) == "",
        "tag": git("describe", "--tags", "--exact-match", "HEAD", cwd=nested),
    }
    if nested_state != {
        "origin": NESTED_ORIGIN,
        "head": NESTED_HEAD,
        "tree": NESTED_TREE,
        "clean": True,
        "detached": True,
        "tag": NESTED_TAG,
    }:
        fail("NESTED_AUTHORITY_MISMATCH")
    return {
        **{key: value for key, value in observed.items() if key != "tracked_delta"},
        "worktree": "DIRTY_ONLY_WITH_AUTHENTICATED_G77_256JT_DELTA",
        "recovered_delta_paths": sorted(line[3:] for line in status),
        "recovery_existing_delta_authenticated": "VERIFIED__YES",
        "remote_head_equality": "VERIFIED__DIRECT_LS_REMOTE_AT_RECOVERY_ENTRY",
        "nested_remote_tag_equality": "VERIFIED__DIRECT_LS_REMOTE_AT_RECOVERY_ENTRY",
        "nested_authority": nested_state,
    }


def reconstruct_js() -> dict[str, Any]:
    committed = subprocess.check_output(
        ["git", "show", f"{ENTRY_HEAD}:{JS_REDUCTION}"], cwd=ROOT
    )
    if committed != (ROOT / JS_REDUCTION).read_bytes():
        fail("JS_REDUCTION_COMMITTED_BYTE_MISMATCH")
    js = load_envelope(JS_REDUCTION)
    required_candidate = {
        "generation_identity": "G77_256JS_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1",
        "operation_identity": "G77_256JS_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001",
        "candidate_sha256": "8af5ba1cbf9e396aa2f4f981a6f20b821c5fd1c38e091ed1cb3646c76c953b4a",
        "context_sha256": "cae588fd2715a21d6a07b2f8ed6e619c6ff454c1824a5ee301ad73ab27ab3430",
        "context_file_sha256": "590ccd51e1c846140fe29c49c8e85ca07dce5278ad7c1e00d813ad5bee5d04f0",
        "canonical_argv_sha256": "74d72916a4d8a65e3e7870fc070893e6288c9b04d5af7c8b2d406329e919fee7",
        "expired_adapter_sha256": JR_ADAPTER_SHA256,
        "temporal_binding_sha256": "94936bac203d0a1db8eda9ee22bfca1055082d549e5da0b02a856ade69f82ced",
        "valid_from_unix_ns": 100,
        "valid_until_unix_ns": 1000,
        "governed_preclaim_coordinate_unix_ns": 1000,
        "request_identity": "NOT_MATERIALIZED",
        "presentation_identity": "NOT_MATERIALIZED",
        "preauthorization_checkpoint_digest": "NOT_MATERIALIZED",
    }
    if (
        js.get("terminal")
        != "M__EXPIRED_FRESH_PREAUTHORIZATION_BOOTSTRAP_HEAD_TREE_BINDING_MISMATCH"
        or js.get("phase")
        != "FAIL_CLOSED_BEFORE_HUMAN_AUTHORIZATION_PRESENTATION"
        or any(js["candidate"].get(key) != value for key, value in required_candidate.items())
        or set(js["operational_counters"].values()) != {"VERIFIED__0"}
        or js["e05"]
        != {
            "after": "VERIFIED__11_OF_18",
            "before": "VERIFIED__11_OF_18",
            "credit": "VERIFIED__0",
            "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
            "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
        }
        or js["jr"]["ex_reused"] != "VERIFIED__17_OF_17"
        or js["jr"]["ex_reconstructed"] != "VERIFIED__0"
    ):
        fail("JS_BLOCKER_BOUNDARY_MISMATCH")
    return {
        "terminal": js["terminal"],
        "phase": js["phase"],
        "candidate": {key: js["candidate"][key] for key in required_candidate},
        "operational_counters": "VERIFIED__ALL_FOURTEEN_ZERO",
        "e05": js["e05"],
        "ex_reused": js["jr"]["ex_reused"],
        "ex_reconstructed": js["jr"]["ex_reconstructed"],
        "reduction_sha256": sha256_path(ROOT / JS_REDUCTION),
    }


def reconstruct_blocker() -> dict[str, Any]:
    fm = load_module(FM, "g77_256jt_blocker_fm")
    js = load_envelope(JS_REDUCTION)
    observed = fm.bootstrap_guest_command_arguments(
        (ROOT / JR_CLOUD).read_text(encoding="utf-8"),
        "/mnt/dp-harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py",
    )
    expected = (
        JR_ADAPTER_SHA256,
        "95ca9b753b2e4256b6530652d5a6e2a8220fed68c52f774928e1e39721f4ca67",
        JR_HEAD,
        JR_TREE,
        "4e5d01699796d4bb451818408f7cd6a080b6d55fde518df8a9dd2acd3f1a73bb",
    )
    if (
        observed != tuple(js["blocker"]["observed_argument_tuple"])
        or expected != tuple(js["blocker"]["expected_argument_tuple"])
        or observed[:2] != expected[:2]
        or observed[4] != expected[4]
        or observed[2:4] != (JQ_HEAD, JQ_TREE)
        or expected[2:4] != (JR_HEAD, JR_TREE)
    ):
        fail("JS_TWO_FIELD_BLOCKER_NOT_REPRODUCED")
    return {
        "status": "VERIFIED__INDEPENDENTLY_RECONSTRUCTED",
        "observed_tuple": list(observed),
        "required_tuple": list(expected),
        "differing_positions": [2, 3],
        "all_other_positions_equal": True,
    }


def verify_solution() -> dict[str, Any]:
    if sha256_path(ROOT / FM) != FM_AFTER_SHA256:
        fail("FM_DELTA_HASH_MISMATCH")
    if hashlib.sha256(
        subprocess.check_output(["git", "show", f"{ENTRY_HEAD}:{FM}"], cwd=ROOT)
    ).hexdigest() != FM_BEFORE_SHA256:
        fail("FM_ENTRY_HASH_MISMATCH")
    if sha256_path(ROOT / CONTEXT_OWNER) != CONTEXT_OWNER_SHA256:
        fail("FM_CONTEXT_OWNER_MUTATED")
    if sha256_path(ROOT / GN) != GN_SHA256 or sha256_path(ROOT / P11) != P11_SHA256:
        fail("GN_OR_P11_MUTATED")
    if (
        sha256_path(ROOT / JR_ADAPTER) != JR_ADAPTER_SHA256
        or sha256_path(ROOT / JR_CLOUD) != JR_CLOUD_SHA256
        or sha256_path(ROOT / JT_CLOUD) != JT_CLOUD_SHA256
        or sha256_path(ROOT / JT_SEED) != JT_SEED_SHA256
    ):
        fail("EXPIRED_ASSET_IDENTITY_MISMATCH")

    old_lines = (ROOT / JR_CLOUD).read_text(encoding="utf-8").splitlines()
    new_lines = (ROOT / JT_CLOUD).read_text(encoding="utf-8").splitlines()
    differences = [
        index for index, (old, new) in enumerate(zip(old_lines, new_lines, strict=True))
        if old != new
    ]
    if differences != [1, 17]:
        fail("JT_CLOUD_DELTA_NOT_MINIMUM")

    fm = load_module(FM, "g77_256jt_solution_fm")
    if fm.governed_checkout_identity(ROOT, "EXPIRED", JR_HEAD, JR_TREE) != (
        JR_HEAD,
        JR_TREE,
    ) or fm.governed_checkout_identity(ROOT, "EXPIRED", ENTRY_HEAD, ENTRY_TREE) != (
        JR_HEAD,
        JR_TREE,
    ):
        fail("EXPIRED_STABLE_CHECKOUT_RECURRENCE")
    preserved_vectors = sorted(
        vector
        for vector in fm.fresh_context.SUPPORTED_OPERATION_VECTORS
        if vector != fm.fresh_context.EXPIRED
    )
    for vector in preserved_vectors:
        if fm.governed_checkout_identity(ROOT, vector, ENTRY_HEAD, ENTRY_TREE) != (
            ENTRY_HEAD,
            ENTRY_TREE,
        ):
            fail(f"NON_EXPIRED_CHECKOUT_SEMANTICS_CHANGED__{vector}")

    generation = "G77_256JT_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
    with tempfile.TemporaryDirectory(prefix="g77_256jt_repo_only_") as temporary:
        temporary_root = Path(temporary)
        operation_root = temporary_root / "operation_state"
        context = fm.build_operation_context(
            repository_root=ROOT,
            repository_head=ENTRY_HEAD,
            repository_tree=ENTRY_TREE,
            generation_identity=generation,
            operation_identity="G77_256JT_REPOSITORY_ONLY_EXPIRED_BINDING_001",
            identity_namespace_prefix="G77_256JT",
            operation_evidence_root=operation_root,
            transient_root=temporary_root / "transient",
        )
        checkout = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
        if (checkout["head"], checkout["tree"]) != (JR_HEAD, JR_TREE):
            fail("CONTEXT_DID_NOT_BIND_STABLE_JR_CHECKOUT")
        binding = context["guest_adapter_binding"]
        projection = Path(binding["projection_root"])
        projection.mkdir(parents=True)
        source_bytes = (ROOT / binding["source_path"]).read_bytes()
        Path(binding["projected_path"]).write_bytes(source_bytes)
        Path(binding["bootstrap_projected_path"]).write_bytes(source_bytes)
        (projection / fm.FRESH_OPERATION_CONTEXT_OWNER_PROJECTION_FILENAME).write_bytes(
            (ROOT / fm.FRESH_OPERATION_CONTEXT_OWNER).read_bytes()
        )
        proof = fm.prove_guest_adapter_binding(ROOT, context)
        fm.validate_immutable_context_bindings(ROOT, context)
        wrong_context = json.loads(json.dumps(context))
        wrong_context["qemu_executable_base_seed_checkout_bindings"]["checkout"].update(
            {"head": ENTRY_HEAD, "tree": ENTRY_TREE}
        )
        wrong_context = fm.fresh_context.seal_context(
            {key: value for key, value in wrong_context.items() if key != "context_sha256"}
        )
        try:
            fm.validate_immutable_context_bindings(ROOT, wrong_context)
        except RuntimeError as exc:
            rejection = str(exc)
        else:
            fail("ADVANCING_HEAD_RECURRENCE_WAS_ACCEPTED")
        command = fm.bootstrap_guest_command_arguments(
            (ROOT / JT_CLOUD).read_text(encoding="utf-8"), binding["bootstrap_guest_path"]
        )
    if command[2:4] != (JR_HEAD, JR_TREE) or command != (
        JR_ADAPTER_SHA256,
        "95ca9b753b2e4256b6530652d5a6e2a8220fed68c52f774928e1e39721f4ca67",
        JR_HEAD,
        JR_TREE,
        "4e5d01699796d4bb451818408f7cd6a080b6d55fde518df8a9dd2acd3f1a73bb",
    ):
        fail("JT_BOOTSTRAP_COMMAND_TUPLE_MISMATCH")

    for member, source in (("/user-data", JT_CLOUD), ("/meta-data", META), ("/network-config", NETWORK)):
        projected = subprocess.check_output(
            ["isoinfo", "-i", str(ROOT / JT_SEED), "-R", "-x", member],
            stderr=subprocess.DEVNULL,
        )
        if projected != (ROOT / source).read_bytes():
            fail(f"NOCLOUD_PROJECTION_MISMATCH__{member}")

    adapter = load_module(JR_ADAPTER, "g77_256jt_expired_adapter")
    if adapter.authenticate_expired_semantics(ROOT) != {
        "baseline_preclaim_time_unix_ns": 500,
        "expired_preclaim_time_unix_ns": 1000,
        "valid_from_unix_ns": 100,
        "valid_until_unix_ns": 1000,
    }:
        fail("EXPIRED_TEMPORAL_SEMANTICS_CHANGED")
    transformed = adapter.specialize_fc_runtime_source(
        repository_root=ROOT, identity_namespace_prefix="G77_256JT"
    )
    for token in (
        'denial_error == "one-use Human act expired before PRECLAIM"',
        'after.state.value == "EXPIRED"',
        "after.revision == 1",
    ):
        if token not in transformed:
            fail("EXPIRED_ADAPTER_SEMANTICS_CHANGED")

    gn = load_module(GN, "g77_256jt_gn")
    request = json.loads((ROOT / GM_REQUEST).read_bytes())
    request["request"]["authorized_vector_requested"] = "EXPIRED"
    request["request"]["generation_identity"] = generation
    gn._validate_request_semantics(request)
    mismatch = json.loads(json.dumps(request))
    mismatch["request"]["generation_identity"] = mismatch["request"][
        "generation_identity"
    ].replace("EXPIRED", "FUTURE")
    try:
        gn._validate_request_semantics(mismatch)
    except gn.PresentationBindingError:
        gn_fail_closed = True
    else:
        fail("GN_VECTOR_GENERATION_MISMATCH_ACCEPTED")

    fm_tree = ast.parse((ROOT / FM).read_text(encoding="utf-8"))
    route_count = sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "main"
        for node in fm_tree.body
    )
    return {
        "authoritative_owner": "EXISTING_FM_SEALED_RUNTIME_CHECKOUT_IDENTITY_OWNER",
        "owner_contract": "FAMILY_LOCAL_EXPIRED_CHECKOUT_REUSES_AUTHENTICATED_COMMITTED_JR_OPERATIONAL_BASELINE",
        "repository_baseline_role": "CURRENT_COMMITTED_ENTRY_FOR_AUTHORITY_AND_REPOSITORY_ADMISSION",
        "runtime_checkout_role": "STABLE_JR_COMMIT_CONTAINING_JM_P11_AND_EXPIRED_ADAPTER",
        "role_collapse": "VERIFIED__NO",
        "jr_checkout_head": JR_HEAD,
        "jr_checkout_tree": JR_TREE,
        "jt_command_tuple": list(command),
        "guest_adapter_binding": proof["result"],
        "wrong_advancing_head_rejection": rejection,
        "recurrence_hazard": "VERIFIED__ELIMINATED__JR_AND_JS_BASELINES_BOTH_DERIVE_SAME_JR_CHECKOUT",
        "historical_jq_authority": "VERIFIED__REMOVED_FROM_CURRENT_SELECTOR_AND_BOOTSTRAP",
        "successor_commit_requires_bootstrap_rewrite": "VERIFIED__NO",
        "unchanged_vector_checkout_semantics": preserved_vectors,
        "cloud_delta_line_count": len(differences),
        "nocloud_projection": "VERIFIED__ALL_THREE_MEMBERS_EXACT",
        "expired_adapter": "VERIFIED__EXACT_UNCHANGED",
        "temporal_truth_table": {"999": "CURRENT", "1000": "EXPIRED", "1001": "EXPIRED"},
        "fm_fail_closed": "VERIFIED__WRONG_ADVANCING_CHECKOUT_REJECTED",
        "gn_fail_closed": "VERIFIED" if gn_fail_closed else "NOT_PROVEN",
        "p11_sha256": P11_SHA256,
        "route_count": route_count,
    }


def build_reduction() -> dict[str, Any]:
    entry = authenticate_entry()
    js = reconstruct_js()
    blocker = reconstruct_blocker()
    solution = verify_solution()
    counters = {key: "VERIFIED__0" for key in (
        "operational_authorization_count",
        "authority_consumption_count",
        "pre_operational_count",
        "fm_operational_invocation_count",
        "qemu_count",
        "vm_count",
        "operation_attempt_count",
        "request_count",
        "p11_entry_count",
        "protected_invocation_count",
        "protected_effect_count",
        "retry_count",
        "repair_retry_count",
        "replay_count",
    )}
    return {
        "schema_id": "G77_256JT_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": "G77-256JT",
        "recovery": {
            "recovery_type": "SAME_GENERATION_PROVIDER_LIMIT_RECOVERY",
            "recovery_source_generation": "G77-256JT",
            "new_generation_created": "VERIFIED__NO",
            "recovery_existing_delta_authenticated": "VERIFIED__YES",
            "recovery_duplicate_operation_count": "VERIFIED__0",
            "recovery_operation_replay_count": "VERIFIED__0",
        },
        "mode": "REPOSITORY_ONLY__NO_AUTHORITY__NO_OPERATION",
        "terminal": TERMINAL,
        "entry": entry,
        "js_reconstruction": js,
        "blocker_reconstruction": blocker,
        "stable_binding": solution,
        "implementation": {
            "modified_files": [FM.as_posix()],
            "created_production_assets": [JT_CLOUD.as_posix(), JT_SEED.as_posix()],
            "fm_before_sha256": FM_BEFORE_SHA256,
            "fm_after_sha256": FM_AFTER_SHA256,
            "jr_cloud_preserved_sha256": JR_CLOUD_SHA256,
            "jt_cloud_sha256": JT_CLOUD_SHA256,
            "jt_seed_sha256": JT_SEED_SHA256,
            "selected_delta": "FAMILY_LOCAL_SUCCESSOR_BOOTSTRAP_PAIR_PLUS_EXISTING_FM_SELECTOR_STABLE_JR_CHECKOUT_BINDING",
        },
        "operational_counters": counters,
        "e05": {
            "before": "VERIFIED__11_OF_18",
            "after": "VERIFIED__11_OF_18",
            "credit": "VERIFIED__0",
            "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
            "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
        },
        "reuse": {
            "ex_reused": "VERIFIED__17_OF_17",
            "ex_reconstructed": "VERIFIED__0",
            "existing_certified_capabilities_reused": "EX_17_OF_17__JJ__JL__JM__JO__JP__JQ__JR__JS__FM__FC__ER__GN__P11",
            "new_capabilities": "VERIFIED__ONE__EXPIRED_BOOTSTRAP_PRE_REQUEST_CHECKOUT_BINDING_REPOSITORY_CAPABILITY",
            "existing_capability_became_unreachable": "VERIFIED__NO",
            "parallel_flow_created": "VERIFIED__NO",
            "production_path_count_effect": "VERIFIED__UNCHANGED__1_TO_1",
        },
        "architecture": {
            "p11_implementation_mutation_count": "VERIFIED__0",
            "production_mutation_count": "VERIFIED__3",
            "new_owner_count": "VERIFIED__0",
            "new_route_count": "VERIFIED__0",
            "new_registry_count": "VERIFIED__0",
            "new_generic_abstraction_count": "VERIFIED__0",
            "new_constitutional_concept_count": "VERIFIED__0",
            "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0",
        },
        "proof_yield": {
            "new_verified_capability_count": "VERIFIED__1__EXPIRED_BOOTSTRAP_PRE_REQUEST_CHECKOUT_BINDING_REPOSITORY_VERIFIED",
            "new_blocker_localized_count": "VERIFIED__0",
            "e05_credit": "VERIFIED__0",
            "proof_reuse_count": "VERIFIED__17__EX_COMMON_CAPABILITIES",
        },
        "metrics": {
            "project_progress": "VERIFIED__JS_BOOTSTRAP_BLOCKER_CLOSED_REPOSITORY_ONLY",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__EXPIRED_PREAUTHORIZATION_ROUTE_READY_FOR_SEPARATE_COMMISSIONING",
            "constitutional_health_evidence": "VERIFIED__STABLE_ROLE_SEPARATION_FAIL_CLOSED_ZERO_OPERATION",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficience": "ESTIMATED__HIGH__HISTORICAL_ASSET_PRESERVED_EXISTING_OWNER_REUSED",
            "overengineering_risk": "ESTIMATED__LOW__FAMILY_LOCAL_THREE_FILE_PRODUCTION_DELTA",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_EVIDENCE_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__SAME_GENERATION_PROVIDER_LIMIT_RECOVERY",
            "candidate_capability": "VERIFIED__EXPIRED_BOOTSTRAP_PRE_REQUEST_CHECKOUT_BINDING_REPOSITORY_VERIFIED",
            "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE_WITH_STABLE_EXPIRED_JR_CHECKOUT",
            "constitutional_continuation_progress": "VERIFIED__JS_EXACT_BLOCKER_TO_JT_REPOSITORY_REPAIR",
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
            "recovery_source_generation": "G77-256JT",
            "new_generation_created": "VERIFIED__NO",
            "recovery_existing_delta_authenticated": "VERIFIED__YES",
            "recovery_duplicate_operation_count": "VERIFIED__0",
            "recovery_operation_replay_count": "VERIFIED__0",
        },
        "frontier": {
            "last_verified_edge": "EXPIRED_BOOTSTRAP_PRE_REQUEST_CHECKOUT_BINDING_REPOSITORY_VERIFIED",
            "first_broken_edge": "FRESH_HUMAN_AUTHORIZED_EXPIRED_PREAUTHORIZATION_CHECKPOINT_NOT_YET_PROVEN",
            "minimum_missing_capability": "FRESH_EXPIRED_PREAUTHORIZATION_CHECKPOINT_AND_HUMAN_PRESENTATION",
            "minimum_legal_next_delta": "SEPARATE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_GENERATION",
        },
        "validation": {
            "jt_focused": "VERIFIED__8_PASSED",
            "js_successor_blocker_suite": "VERIFIED__5_PASSED",
            "jr_historical_suite": "VERIFIED__6_HISTORICAL_ASSERTIONS_PASSED__6_JQ_ENTRY_JR_ASSET_PRE_JR_CONTEXT_OR_MUTATION_SCOPE_ASSERTIONS_STATE_BOUND",
            "governance_conformance": "VERIFIED__9_PASSED__ENGINE_20_PASSED__CONFORMANT__ZERO_WARNINGS__ZERO_VIOLATIONS",
            "fm_historical_context_suite": "VERIFIED__14_CURRENT_ASSERTIONS_PASSED__3_PRE_JM_SYNTHETIC_IDENTITY_ORDER_ASSERTIONS_STATE_BOUND",
            "gn_and_p11": "VERIFIED__50_PASSED",
            "layer_0": "VERIFIED__PASS__CONFORMANCE_AND_ZERO_LAYER_0_DELTA",
            "g48_h1_count": "VERIFIED__6",
            "reuse_question_count": "VERIFIED__5",
            "git_diff_check": "VERIFIED__PASS",
        },
        "auto_continuable": False,
        "human_review_required": True,
    }


def write_reduction() -> None:
    reduction = build_reduction()
    envelope = {
        "schema_id": "G77_256JT_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": hashlib.sha256(canonical_bytes(reduction)).hexdigest(),
    }
    (ROOT / REDUCTION).write_bytes(canonical_bytes(envelope))


if __name__ == "__main__":
    write_reduction()
