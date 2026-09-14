#!/usr/bin/env python3
"""Read-only G77-256LI WRONG_SCOPE bootstrap and Phase-A verifier.

This verifier creates only ephemeral, non-authority, non-operational fixtures.
It never invokes the FM launcher entrypoint, QEMU, a VM, P11, or a protected
operation.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
LI_REL = Path(
    ".github/governance/evidence/"
    "g77_256li_wrong_scope_current_checkout_binding_v1"
)
LI = ROOT / LI_REL
ENTRY_HEAD = "f7acd5feb3dec686ca4e2cd359b63e232f6c5fbe"
ENTRY_TREE = "968704d8915edf6d524a8a7705591788d8333bdd"
ENTRY_SUBJECT = "G77-256LH bind failure verifier to committed terminal"
ATTEMPTED_COMMIT = "c725df9545518e867ad31a39d83ae71522be1c05"
ATTEMPTED_TREE = "58feeebe35d4e68ed6acae86584382c6ac358d41"
ATTEMPTED_SUBJECT = "G77-256LI repair WRONG_SCOPE current-checkout binding"
LH_PARENT = "fbc3eba8d4c31f192d6127975cb5ad1f4019952a"
LG_HEAD = "332ca67e20e8f330bc9182d1aa9cc99ef3f02363"
LG_TREE = "8ac8b003bae4727c40ec20aaefd7ff41eb3d3c71"
STALE_HEAD = "5cdc56046b79b577842f1dedff1faedf6aaedfa0"
STALE_TREE = "687db58ac7e87ac9f03f445299e52de4480a8ed6"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
TERMINAL = (
    "A__G77_256LI_ARCHITECTURAL_SCOPE_EXPANSION_REQUIRED__"
    "STOP_FOR_HUMAN_REVIEW"
)

FM_REL = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
FM = ROOT / FM_REL
FM_BEFORE_SHA256 = "c600cd2e723494558d6916460c7f358cd264f3ec72b96655afc23d8e3fb97bd5"
FM_AFTER_SHA256 = "03d84b6a1f3eaf2a095b3a875769801df2d619636a266176636eb7b7953ebda2"
LG_REL = Path(
    ".github/governance/evidence/"
    "g77_256lg_wrong_scope_existing_route_admission_v1"
)
LG_CLOUD = ROOT / LG_REL / "static/G77_256LG_CLOUD_INIT_USER_DATA_V1.yaml"
LG_SEED = ROOT / LG_REL / "static/SAPIANTA_WRONG_SCOPE_NOCLOUD_SEED_V1.img"
LG_CLOUD_SHA256 = "da8ccacd41c5796c76d8fb0405d9dc715fe12676286e7adf883b4bbe6a02f69f"
LG_SEED_SHA256 = "f274348c88d001c8dbc80684026185a2c3fef638cbedf1698f1ca4bb301b2b16"
LI_CLOUD = LI / "static/G77_256LI_CLOUD_INIT_USER_DATA_V1.yaml"
LI_SEED = LI / "static/SAPIANTA_WRONG_SCOPE_NOCLOUD_SEED_V2.img"
LI_CLOUD_SHA256 = "8013bbb1b59ee082c1d820639463baa53acba9cbac84658813ca23bb65f54d0c"
LI_SEED_SHA256 = "975f38f4965038e2631341490369c6d0f8f5c36554f2f90041d66f9101fb5fdd"
LH_REDUCTION_REL = Path(
    ".github/governance/evidence/"
    "g77_256lh_fresh_wrong_scope_operational_acceptance_v1/"
    "G77_256LH_SPCE_PHASE_A_BINDING_FAILURE_REDUCTION_V1.json"
)
LH_REDUCTION = ROOT / LH_REDUCTION_REL
LH_REDUCTION_SHA256 = "7425b6ada513e1c08f709b5f28a5cd049205180a39979b696126c74dbecdaa4b"
LI_REDUCTION = LI / "G77_256LI_SPCE_TERMINAL_PHASE_A_READINESS_REDUCTION_V1.json"
LI_REPORT = LI / "G77_256LI_G48_IMPLEMENTATION_REPORT_V1.md"
META = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/raw/"
    "G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"
)
NETWORK = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/raw/"
    "G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"
)
P11 = ROOT / "tests/p11_da_operational_consumer_v1.py"
ER = ROOT / (
    ".github/governance/evidence/g77_256er_p11_operational_v1/harness/"
    "G77_256ER_P11_OPERATIONAL_HARNESS_V1.py"
)
P11_SHA256 = "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5"
ER_SHA256 = "c6539d1cc60940b1999956965bff43923a270598a982cd19f976eadec0a93152"


class LIVerificationError(RuntimeError):
    """One fail-closed G77-256LI verification error."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def committed(relative: Path, revision: str = ENTRY_HEAD) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{revision}:{relative.as_posix()}"], cwd=ROOT
    )


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise LIVerificationError(f"NONCANONICAL_JSON:{path}")
    return value


def load_fm():
    specification = importlib.util.spec_from_file_location("g77_256li_fm", FM)
    if specification is None or specification.loader is None:
        raise LIVerificationError("FM_IMPORT_SPECIFICATION_UNAVAILABLE")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def authenticate_entry() -> dict[str, Any]:
    current_head = git("rev-parse", "HEAD")
    if (
        ROOT != Path("/home/pisarna/work/sapianta-fl")
        or git("rev-parse", "--show-toplevel") != str(ROOT)
        or git("branch", "--show-current") != BRANCH
        or git("show", "-s", "--format=%T", ENTRY_HEAD) != ENTRY_TREE
        or git("show", "-s", "--format=%s", ENTRY_HEAD) != ENTRY_SUBJECT
        or git("rev-parse", f"{ENTRY_HEAD}^") != LH_PARENT
        or git("rev-parse", f"{LG_HEAD}^{{tree}}") != LG_TREE
        or git("rev-parse", f"{ATTEMPTED_COMMIT}^{{tree}}") != ATTEMPTED_TREE
        or git("show", "-s", "--format=%s", ATTEMPTED_COMMIT)
        != ATTEMPTED_SUBJECT
    ):
        raise LIVerificationError("ENTRY_CHECKPOINT_MISMATCH")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", ENTRY_HEAD, current_head],
        cwd=ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode:
        raise LIVerificationError("LH_ENTRY_NOT_ANCESTRAL_TO_CURRENT_HEAD")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", ATTEMPTED_COMMIT, current_head],
        cwd=ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode:
        raise LIVerificationError("LI_ATTEMPT_COMMIT_NOT_ANCESTRAL_TO_CURRENT_HEAD")
    nested = ROOT / "sapianta_system"
    if (
        git("rev-parse", "HEAD", cwd=nested) != NESTED_HEAD
        or git("rev-parse", "HEAD^{tree}", cwd=nested) != NESTED_TREE
        or git("status", "--short", cwd=nested)
        or git("branch", "--show-current", cwd=nested)
        or git("rev-parse", f"refs/tags/{NESTED_TAG}^{{}}", cwd=nested)
        != NESTED_HEAD
    ):
        raise LIVerificationError("NESTED_AUTHORITY_CHECKPOINT_MISMATCH")
    allowed = {FM_REL.as_posix()}
    allowed_prefix = LI_REL.as_posix() + "/"
    dirty = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT,
        text=True,
    ).splitlines()
    unexpected = [
        line for line in dirty
        if line[3:] not in allowed and not line[3:].startswith(allowed_prefix)
    ]
    if unexpected:
        raise LIVerificationError(f"UNRELATED_MUTATION:{unexpected}")
    return {
        "entry_head": ENTRY_HEAD,
        "entry_tree": ENTRY_TREE,
        "attempted_commit": ATTEMPTED_COMMIT,
        "attempted_tree": ATTEMPTED_TREE,
        "current_head": current_head,
        "branch": BRANCH,
        "nested_head": NESTED_HEAD,
        "nested_tree": NESTED_TREE,
    }


def authenticate_lh_failure() -> dict[str, Any]:
    historical = committed(LH_REDUCTION_REL)
    if LH_REDUCTION.read_bytes() != historical or sha256_bytes(historical) != LH_REDUCTION_SHA256:
        raise LIVerificationError("LH_HISTORICAL_EVIDENCE_DRIFT")
    envelope = json.loads(historical)
    reduction = envelope.get("reduction")
    if (
        not isinstance(reduction, dict)
        or envelope.get("reduction_sha256") != sha256_bytes(canonical_bytes(reduction))
        or reduction.get("terminal") != "A__G77_256LH_PHASE_A_BINDING_FAILURE__STOP"
        or reduction.get("failure_novelty_and_convergence_check", {}).get("failure_class")
        != "IMPLEMENTATION_REGRESSION"
        or reduction.get("binding_failure", {}).get("differing_argument_indexes") != [2, 3]
        or reduction.get("binding_failure", {}).get("observed_arguments", [None] * 5)[2:4]
        != [STALE_HEAD, STALE_TREE]
        or reduction.get("binding_failure", {}).get("expected_arguments", [None] * 5)[2:4]
        != [LG_HEAD, LG_TREE]
        or any(reduction.get("operational_counters", {}).values())
    ):
        raise LIVerificationError("LH_HISTORICAL_FAILURE_CONTRACT_MISMATCH")
    return {
        "failure_class": "IMPLEMENTATION_REGRESSION",
        "novelty": (
            "LG_PHASE_A_TEST_USED_LE_ENTRY_COORDINATES__FRESH_LH_CURRENT_HEAD_"
            "BINDING_NOT_PREVIOUSLY_PROVEN"
        ),
        "affected_invariant": "EXACT_REPOSITORY_AND_RUNTIME_CHECKOUT_IDENTITY_BINDING",
        "differing_argument_indexes": [2, 3],
        "new_capability_required": "NO",
        "new_proof_required": "YES__CURRENT_HEAD_BOOTSTRAP_BINDING",
    }


def authenticate_minimum_delta() -> dict[str, Any]:
    fm = load_fm()
    before = committed(FM_REL)
    expected = (
        before.replace(
            b"g77_256lg_wrong_scope_existing_route_admission_v1/",
            b"g77_256li_wrong_scope_current_checkout_binding_v1/",
            2,
        )
        .replace(
            b"static/G77_256LG_CLOUD_INIT_USER_DATA_V1.yaml",
            b"static/G77_256LI_CLOUD_INIT_USER_DATA_V1.yaml",
            1,
        )
        .replace(
            b"static/SAPIANTA_WRONG_SCOPE_NOCLOUD_SEED_V1.img",
            b"static/SAPIANTA_WRONG_SCOPE_NOCLOUD_SEED_V2.img",
            1,
        )
        .replace(LG_CLOUD_SHA256.encode(), LI_CLOUD_SHA256.encode(), 1)
        .replace(LG_SEED_SHA256.encode(), LI_SEED_SHA256.encode(), 1)
    )
    if (
        sha256_bytes(before) != FM_BEFORE_SHA256
        or FM.read_bytes() != expected
        or sha256(FM) != FM_AFTER_SHA256
        or sha256(LG_CLOUD) != LG_CLOUD_SHA256
        or sha256(LG_SEED) != LG_SEED_SHA256
        or LG_CLOUD.read_bytes() != committed(LG_REL / LG_CLOUD.relative_to(ROOT / LG_REL))
        or LG_SEED.read_bytes() != committed(LG_REL / LG_SEED.relative_to(ROOT / LG_REL))
        or sha256(LI_CLOUD) != LI_CLOUD_SHA256
        or sha256(LI_SEED) != LI_SEED_SHA256
        or sha256(P11) != P11_SHA256
        or sha256(ER) != ER_SHA256
    ):
        raise LIVerificationError("MINIMUM_DELTA_OR_IMMUTABILITY_MISMATCH")
    bootstrap = fm.current_bootstrap_asset_bindings("WRONG_SCOPE")
    observed = fm.bootstrap_guest_command_arguments(
        LI_CLOUD.read_text(encoding="utf-8"),
        "/mnt/dp-harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py",
    )
    expected_tuple = (
        "67847030651e8add82dd16bc8741ad0d81f44c7ba873689a521aea85f2ec4949",
        "95ca9b753b2e4256b6530652d5a6e2a8220fed68c52f774928e1e39721f4ca67",
        ENTRY_HEAD,
        ENTRY_TREE,
        "4e5d01699796d4bb451818408f7cd6a080b6d55fde518df8a9dd2acd3f1a73bb",
    )
    if (
        tuple(observed) != expected_tuple
        or bootstrap["cloud_init_path"] != LI_CLOUD.relative_to(ROOT).as_posix()
        or bootstrap["cloud_init_sha256"] != LI_CLOUD_SHA256
        or bootstrap["seed_path"] != str(LI_SEED)
        or bootstrap["seed_sha256"] != LI_SEED_SHA256
    ):
        raise LIVerificationError("CURRENT_BOOTSTRAP_TUPLE_MISMATCH")
    tree = ast.parse(FM.read_text(encoding="utf-8"))
    if sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "main"
        for node in tree.body
    ) != 1:
        raise LIVerificationError("PRODUCTION_ROUTE_COUNT_CHANGED")
    return {
        "source_owner": "FM_CURRENT_BOOTSTRAP_ASSET_BINDINGS",
        "direct_consumers": ["FM_PROVE_GUEST_ADAPTER_BINDING"],
        "derived_artifacts": ["LI_NOCLOUD_SEED_USER_DATA_PROJECTION"],
        "hash_dependencies": ["FM_WRONG_SCOPE_CLOUD_INIT_SHA256", "FM_WRONG_SCOPE_SEED_SHA256"],
        "seal_dependencies": [],
        "seed_image_dependencies": ["LI_CLOUD_INIT", "FM_META_DATA", "FM_NETWORK_CONFIG"],
        "test_dependencies": ["LI_FOCUSED_PHASE_A_TESTS"],
        "bootstrap_tuple": list(expected_tuple),
    }


def authenticate_seed_projection() -> dict[str, Any]:
    descriptor = subprocess.check_output(
        ["isoinfo", "-i", str(LI_SEED), "-d"],
        stderr=subprocess.DEVNULL,
        text=True,
    )
    inventory = subprocess.check_output(
        ["isoinfo", "-i", str(LI_SEED), "-R", "-f"],
        stderr=subprocess.DEVNULL,
        text=True,
    ).splitlines()
    if "Volume id: cidata" not in descriptor or sorted(inventory) != [
        "/meta-data", "/network-config", "/user-data"
    ]:
        raise LIVerificationError("NOCLOUD_STRUCTURE_MISMATCH")
    for member, source in {
        "/user-data": LI_CLOUD,
        "/meta-data": META,
        "/network-config": NETWORK,
    }.items():
        projected = subprocess.check_output(
            ["isoinfo", "-i", str(LI_SEED), "-R", "-x", member],
            stderr=subprocess.DEVNULL,
        )
        if projected != source.read_bytes():
            raise LIVerificationError(f"NOCLOUD_PROJECTION_MISMATCH:{member}")
    return {
        "generator": "genisoimage -volid cidata -joliet -rock",
        "seed_sha256": LI_SEED_SHA256,
        "projection": "VERIFIED__EXACT_THREE_MEMBERS",
    }


def authenticate_phase_a(work_root: Path) -> dict[str, Any]:
    fm = load_fm()
    candidate = LH_REDUCTION_REL
    transient = work_root / "transient"
    operation_state = work_root / "operation_state"
    context = fm.build_operation_context(
        repository_root=ROOT,
        repository_head=ENTRY_HEAD,
        repository_tree=ENTRY_TREE,
        generation_identity=(
            "G77_256LI_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_SCOPE_"
            "OPERATIONAL_COMMISSIONING_V1"
        ),
        operation_identity="G77_256LI_STATIC_FIXTURE_ONLY_NO_OPERATION_001",
        identity_namespace_prefix="G77_256LI",
        operation_evidence_root=operation_state,
        transient_root=transient,
        candidate_source_path=candidate,
    )
    checkout = Path(
        context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["path"]
    )
    checkout.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", "--quiet", "--no-checkout", "--", str(ROOT), str(checkout)],
        check=True,
    )
    subprocess.run(
        ["git", "checkout", "--quiet", "--detach", ENTRY_HEAD],
        cwd=checkout,
        check=True,
    )
    binding = context["guest_adapter_binding"]
    projection = Path(binding["projection_root"])
    projection.mkdir(parents=True)
    source = (ROOT / binding["source_path"]).read_bytes()
    Path(binding["projected_path"]).write_bytes(source)
    Path(binding["bootstrap_projected_path"]).write_bytes(source)
    shutil.copyfile(
        ROOT / fm.FRESH_OPERATION_CONTEXT_OWNER,
        projection / fm.FRESH_OPERATION_CONTEXT_OWNER_PROJECTION_FILENAME,
    )
    projection.chmod(fm.GUEST_HARNESS_PROJECTION_ROOT_PRESENTATION_MODE)
    export = Path(context["runtime_export_root"])
    export.mkdir(parents=True)
    shutil.copyfile(ROOT / candidate, Path(context["runtime_manifest_path"]))
    (export / fm.fresh_context.GUEST_CONTEXT_FILENAME).write_bytes(
        fm.canonical_bytes(context)
    )
    overlay = Path(context["overlay_path"])
    overlay.parent.mkdir(parents=True, exist_ok=True)
    overlay.touch()
    observations = fm.observe_context_assets(ROOT, context, candidate)
    try:
        fm.authority_free_static_readiness(
            repository_root=ROOT,
            context=context,
            observed_head=ENTRY_HEAD,
            observed_tree=ENTRY_TREE,
            repository_clean=True,
            observed_asset_sha256=observations,
            candidate_source_path=candidate,
        )
    except RuntimeError as error:
        if str(error) != "sealed route target is not the current repository identity":
            raise
    else:
        raise LIVerificationError("EXPECTED_POST_COMMIT_PHASE_A_FAILURE_NOT_OBSERVED")
    if (
        git("rev-parse", "HEAD") == ENTRY_HEAD
        or context.get("repository_head") != ENTRY_HEAD
        or context.get("repository_tree") != ENTRY_TREE
        or fm.context_vector(context) != "WRONG_SCOPE"
    ):
        raise LIVerificationError("POST_COMMIT_FAILURE_CONTEXT_MISMATCH")
    return {
        "result": "FAIL_CLOSED__POST_COMMIT_CURRENT_REPOSITORY_IDENTITY_MISMATCH",
        "failure_class": "DUPLICATE_OR_EQUIVALENT_EDGE",
        "error": "sealed route target is not the current repository identity",
        "ready_for_human_decision": False,
        "repository_head": ENTRY_HEAD,
        "repository_tree": ENTRY_TREE,
        "vector": "WRONG_SCOPE",
        "bootstrap_tuple": "VERIFIED__IMMUTABLE_LH_PREDECESSOR",
        "caller": "VERIFIED",
        "attempt": "VERIFIED",
        "input": "VERIFIED",
        "contract": "VERIFIED",
        "provenance": "VERIFIED",
        "scope_specialization": "VERIFIED",
        "one_attempt_limit": "VERIFIED",
        "human_authority_source_count": 0,
        "authority_consumption_count": 0,
        "operation_attempt_count": 0,
        "qemu_start_count": 0,
        "vm_start_count": 0,
        "operation_request_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "replay_count": 0,
        "repair_retry_count": 0,
    }


def authenticate_evidence() -> dict[str, Any]:
    envelope = load_canonical(LI_REDUCTION)
    reduction = envelope.get("reduction")
    if (
        not isinstance(reduction, dict)
        or envelope.get("reduction_sha256") != sha256_bytes(canonical_bytes(reduction))
        or reduction.get("terminal") != TERMINAL
        or reduction.get("e05") != {"after": "12/18", "before": "12/18", "credit": 0}
        or any(reduction.get("operational_counters", {}).values())
    ):
        raise LIVerificationError("LI_REDUCTION_CONTRACT_MISMATCH")
    report = LI_REPORT.read_text(encoding="utf-8")
    headings = [line for line in report.splitlines() if line.startswith("# ")]
    if headings != [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ] or not report.rstrip().endswith(TERMINAL):
        raise LIVerificationError("G48_REPORT_STRUCTURE_MISMATCH")
    return reduction


def verify(work_root: Path) -> dict[str, Any]:
    authenticate_entry()
    failure = authenticate_lh_failure()
    closure = authenticate_minimum_delta()
    seed = authenticate_seed_projection()
    phase_a = authenticate_phase_a(work_root)
    reduction = authenticate_evidence()
    return {
        "terminal": TERMINAL,
        "failure": failure,
        "dependency_closure": closure,
        "seed": seed,
        "phase_a_failure": phase_a,
        "e05": reduction["e05"],
        "ex": reduction["ex"],
    }


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory(prefix="g77_256li_verify.", dir="/tmp") as temporary:
        print(verify(Path(temporary))["terminal"])
