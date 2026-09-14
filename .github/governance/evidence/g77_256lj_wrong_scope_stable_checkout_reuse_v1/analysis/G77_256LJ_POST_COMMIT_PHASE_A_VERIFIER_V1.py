#!/usr/bin/env python3
"""Authority-free G77-256LJ stable-checkout and post-commit Phase-A proof."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
LJ_REL = Path(
    ".github/governance/evidence/"
    "g77_256lj_wrong_scope_stable_checkout_reuse_v1"
)
LJ = ROOT / LJ_REL
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ENTRY_HEAD = "0604669f956c328538dc87eb55e72112f78a420a"
ENTRY_TREE = "e72c72359bf369795b1c6b5c3120c1af9a647ffc"
ENTRY_SUBJECT = "G77-256LI record post-commit Phase-A binding failure"
LI_IMPLEMENTATION = "c725df9545518e867ad31a39d83ae71522be1c05"
LH_HEAD = "f7acd5feb3dec686ca4e2cd359b63e232f6c5fbe"
LH_TREE = "968704d8915edf6d524a8a7705591788d8333bdd"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
TERMINAL = (
    "A__G77_256LJ_WRONG_SCOPE_STABLE_GOVERNED_CHECKOUT_REUSE_PROVEN__"
    "POST_COMMIT_PHASE_A_STATIC_READINESS_VERIFIED__ZERO_AUTHORITY__"
    "ZERO_OPERATION__READY_FOR_HUMAN_DECISION"
)

FM_REL = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
ADAPTER_REL = Path(
    ".github/governance/evidence/"
    "g77_256lg_wrong_scope_existing_route_admission_v1/adapter/"
    "G77_256LG_WRONG_SCOPE_VECTOR_ADAPTER_V1.py"
)
LE_REL = Path(
    ".github/governance/evidence/"
    "g77_256le_wrong_scope_minimum_governed_delta_v1/"
    "G77_256LE_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
FC_REL = Path(
    ".github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/harness/"
    "G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
)
ER_REL = Path(
    ".github/governance/evidence/g77_256er_p11_operational_v1/harness/"
    "G77_256ER_P11_OPERATIONAL_HARNESS_V1.py"
)
P11_REL = Path("tests/p11_da_operational_consumer_v1.py")
LI_REDUCTION_REL = Path(
    ".github/governance/evidence/g77_256li_wrong_scope_current_checkout_binding_v1/"
    "G77_256LI_SPCE_TERMINAL_PHASE_A_READINESS_REDUCTION_V1.json"
)
CLOUD_REL = LJ_REL / "static/G77_256LJ_CLOUD_INIT_USER_DATA_V1.yaml"
SEED_REL = LJ_REL / "static/SAPIANTA_WRONG_SCOPE_NOCLOUD_SEED_V3.img"
REDUCTION = LJ / "G77_256LJ_SPCE_TERMINAL_REDUCTION_V1.json"
REPORT = LJ / "G77_256LJ_G48_IMPLEMENTATION_REPORT_V1.md"

FM_SHA256 = "4bb8151e68aca89dd09e85178e177834a2811211870a37124d3991d757c7c247"
ADAPTER_BASE_SHA256 = "67847030651e8add82dd16bc8741ad0d81f44c7ba873689a521aea85f2ec4949"
ADAPTER_SHA256 = "035c3c02cfb4cee26c6af2501b85a547d0376c80c4df376b7a40a8671277136f"
LE_SHA256 = "7710f40b8f2bb57229167c37fff527cf2e18c81769f82db096e029a3895c45dc"
FC_SHA256 = "b2e9f72d6b35b2db0021bf9bf1223350f570d1eaecda3379a8af013c705aa770"
ER_SHA256 = "c6539d1cc60940b1999956965bff43923a270598a982cd19f976eadec0a93152"
P11_SHA256 = "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5"
LI_REDUCTION_SHA256 = "8d33b16514da651a6aa49c37a6d564ace194ea72c0bf2a415da448a038bc0f34"
CLOUD_SHA256 = "17957eee3b80526632c0384c552f1e11979b0411995a131950c207a9086feaea"
SEED_SHA256 = "29d46bad5bb2243dc4120ca39c62bf45363335b8e215a9f3e32e04957e70964e"


class LJVerificationError(RuntimeError):
    """One fail-closed LJ verification error."""


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


def committed(relative: Path, revision: str) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{revision}:{relative.as_posix()}"], cwd=ROOT
    )


def load_module(path: Path, name: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise LJVerificationError(f"MODULE_SPECIFICATION_UNAVAILABLE:{name}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def is_ancestor(ancestor: str, descendant: str) -> bool:
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def authenticate_entry() -> dict[str, Any]:
    current_head = git("rev-parse", "HEAD")
    if (
        ROOT != Path("/home/pisarna/work/sapianta-fl")
        or git("rev-parse", "--show-toplevel") != str(ROOT)
        or git("branch", "--show-current") != BRANCH
        or git("rev-parse", f"{ENTRY_HEAD}^{{tree}}") != ENTRY_TREE
        or git("show", "-s", "--format=%s", ENTRY_HEAD) != ENTRY_SUBJECT
        or not is_ancestor(LI_IMPLEMENTATION, current_head)
        or not is_ancestor(ENTRY_HEAD, current_head)
        or not is_ancestor(LH_HEAD, current_head)
    ):
        raise LJVerificationError("ENTRY_CHECKPOINT_MISMATCH")
    nested = ROOT / "sapianta_system"
    if (
        git("rev-parse", "HEAD", cwd=nested) != NESTED_HEAD
        or git("rev-parse", "HEAD^{tree}", cwd=nested) != NESTED_TREE
        or git("status", "--short", cwd=nested)
        or git("branch", "--show-current", cwd=nested)
        or git("rev-parse", f"refs/tags/{NESTED_TAG}^{{}}", cwd=nested) != NESTED_HEAD
    ):
        raise LJVerificationError("NESTED_AUTHORITY_CHECKPOINT_MISMATCH")
    allowed = {FM_REL.as_posix(), ADAPTER_REL.as_posix()}
    prefix = LJ_REL.as_posix() + "/"
    dirty = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT,
        text=True,
    ).splitlines()
    unexpected = [
        line for line in dirty
        if line[3:] not in allowed and not line[3:].startswith(prefix)
    ]
    if unexpected:
        raise LJVerificationError(f"UNRELATED_MUTATION:{unexpected}")
    return {
        "entry_head": ENTRY_HEAD,
        "entry_tree": ENTRY_TREE,
        "current_head": current_head,
        "current_tree": git("rev-parse", "HEAD^{tree}"),
        "nested_head": NESTED_HEAD,
        "nested_tree": NESTED_TREE,
    }


def authenticate_predecessor() -> dict[str, Any]:
    raw = (ROOT / LI_REDUCTION_REL).read_bytes()
    if raw != committed(LI_REDUCTION_REL, ENTRY_HEAD) or sha256_bytes(raw) != LI_REDUCTION_SHA256:
        raise LJVerificationError("LI_DURABLE_EVIDENCE_DRIFT")
    envelope = json.loads(raw)
    reduction = envelope.get("reduction")
    if (
        not isinstance(reduction, dict)
        or envelope.get("reduction_sha256") != sha256_bytes(canonical_bytes(reduction))
        or reduction.get("terminal")
        != "A__G77_256LI_ARCHITECTURAL_SCOPE_EXPANSION_REQUIRED__STOP_FOR_HUMAN_REVIEW"
        or reduction.get("failure_novelty_and_convergence_check", {}).get("failure_class")
        != "DUPLICATE_OR_EQUIVALENT_EDGE"
        or {
            key: reduction.get("e05", {}).get(key)
            for key in ("after", "before", "credit")
        } != {"after": "12/18", "before": "12/18", "credit": 0}
    ):
        raise LJVerificationError("LI_PREDECESSOR_CONTRACT_MISMATCH")
    return reduction["failure_novelty_and_convergence_check"]


def authenticate_stable_reuse() -> dict[str, Any]:
    fm = load_module(ROOT / FM_REL, "g77_256lj_fm")
    adapter = load_module(ROOT / ADAPTER_REL, "g77_256lj_adapter")
    current_head = git("rev-parse", "HEAD")
    current_tree = git("rev-parse", "HEAD^{tree}")
    expected = {
        FM_REL: FM_SHA256,
        ADAPTER_REL: ADAPTER_SHA256,
        LE_REL: LE_SHA256,
        FC_REL: FC_SHA256,
        ER_REL: ER_SHA256,
        P11_REL: P11_SHA256,
        CLOUD_REL: CLOUD_SHA256,
        SEED_REL: SEED_SHA256,
    }
    if any(sha256(ROOT / path) != digest for path, digest in expected.items()):
        raise LJVerificationError("DEPENDENCY_IDENTITY_MISMATCH")
    if (
        git("rev-parse", f"{LH_HEAD}^{{tree}}") != LH_TREE
        or not is_ancestor(LH_HEAD, current_head)
        or sha256_bytes(committed(ADAPTER_REL, LH_HEAD)) != ADAPTER_BASE_SHA256
        or sha256_bytes(committed(LE_REL, LH_HEAD)) != LE_SHA256
        or sha256_bytes(committed(FC_REL, LH_HEAD)) != FC_SHA256
        or sha256_bytes(committed(ER_REL, LH_HEAD)) != ER_SHA256
        or sha256_bytes(committed(P11_REL, LH_HEAD)) != P11_SHA256
    ):
        raise LJVerificationError("STABLE_LH_RUNTIME_DEPENDENCY_MISMATCH")
    if fm.governed_checkout_identity(
        ROOT, fm.fresh_context.WRONG_SCOPE, current_head, current_tree
    ) != (LH_HEAD, LH_TREE):
        raise LJVerificationError("WRONG_SCOPE_STABLE_OWNER_RESULT_MISMATCH")
    if fm.governed_checkout_identity(
        ROOT, fm.fresh_context.EXPIRED, current_head, current_tree
    ) != (fm.EXPIRED_CHECKOUT_HEAD, fm.EXPIRED_CHECKOUT_TREE):
        raise LJVerificationError("EXPIRED_STABLE_OWNER_RESULT_CHANGED")
    for vector in (
        fm.fresh_context.WRONG_ATTEMPT,
        fm.fresh_context.WRONG_INPUT,
        fm.fresh_context.WRONG_CONTRACT,
        fm.fresh_context.WRONG_PROVENANCE,
        fm.fresh_context.FUTURE,
    ):
        if fm.governed_checkout_identity(ROOT, vector, current_head, current_tree) != (
            current_head,
            current_tree,
        ):
            raise LJVerificationError(f"NON_TARGET_CHECKOUT_SEMANTICS_CHANGED:{vector}")
    er = adapter.specialize_er_harness(ROOT)
    role_function = er.load_authenticated_fresh_operation_context
    if "repository_head" in role_function.__code__.co_consts:
        raise LJVerificationError("ER_ADMISSION_RUNTIME_ROLE_COLLAPSE_REMAINS")
    base_er = (ROOT / ER_REL).read_text(encoding="utf-8")
    if base_er.count('context["repository_head"] != observed_head') != 1:
        raise LJVerificationError("ER_BASE_FAIL_CLOSED_ADMISSION_ANCHOR_DRIFT")
    tree = ast.parse((ROOT / FM_REL).read_text(encoding="utf-8"))
    if sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "main"
        for node in tree.body
    ) != 1:
        raise LJVerificationError("PRODUCTION_ROUTE_COUNT_CHANGED")
    return {
        "source_owner": "EXISTING_FM_SEALED_RUNTIME_CHECKOUT_IDENTITY_OWNER",
        "stable_head": LH_HEAD,
        "stable_tree": LH_TREE,
        "current_admission_head": current_head,
        "current_admission_tree": current_tree,
        "runtime_role_separated": True,
        "route": "FM->ER->P11",
        "route_count": 1,
    }


def authenticate_seed_projection() -> dict[str, Any]:
    seed = ROOT / SEED_REL
    descriptor = subprocess.check_output(
        ["isoinfo", "-i", str(seed), "-d"], stderr=subprocess.DEVNULL, text=True
    )
    inventory = subprocess.check_output(
        ["isoinfo", "-i", str(seed), "-R", "-f"],
        stderr=subprocess.DEVNULL,
        text=True,
    ).splitlines()
    if "Volume id: cidata" not in descriptor or sorted(inventory) != [
        "/meta-data", "/network-config", "/user-data"
    ]:
        raise LJVerificationError("NOCLOUD_STRUCTURE_MISMATCH")
    members = {
        "/user-data": ROOT / CLOUD_REL,
        "/meta-data": ROOT / fm_meta_relative(),
        "/network-config": ROOT / fm_network_relative(),
    }
    for member, source in members.items():
        projected = subprocess.check_output(
            ["isoinfo", "-i", str(seed), "-R", "-x", member],
            stderr=subprocess.DEVNULL,
        )
        if projected != source.read_bytes():
            raise LJVerificationError(f"NOCLOUD_PROJECTION_MISMATCH:{member}")
    return {"seed_sha256": SEED_SHA256, "projection": "VERIFIED__EXACT_THREE_MEMBERS"}


def fm_meta_relative() -> Path:
    return Path(
        ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/raw/"
        "G77_256FM_CLOUD_INIT_META_DATA_V1.yaml"
    )


def fm_network_relative() -> Path:
    return Path(
        ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/raw/"
        "G77_256FM_CLOUD_INIT_NETWORK_CONFIG_V1.yaml"
    )


def authenticate_postcommit_phase_a(work_root: Path) -> dict[str, Any]:
    fm = load_module(ROOT / FM_REL, "g77_256lj_phase_a_fm")
    current_head = git("rev-parse", "HEAD")
    current_tree = git("rev-parse", "HEAD^{tree}")
    transient = work_root / "transient"
    operation_state = work_root / "operation_state"
    context = fm.build_operation_context(
        repository_root=ROOT,
        repository_head=current_head,
        repository_tree=current_tree,
        generation_identity=(
            "G77_256LJ_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_SCOPE_"
            "OPERATIONAL_COMMISSIONING_V1"
        ),
        operation_identity="G77_256LJ_STATIC_FIXTURE_ONLY_NO_OPERATION_001",
        identity_namespace_prefix="G77_256LJ",
        operation_evidence_root=operation_state,
        transient_root=transient,
        candidate_source_path=LI_REDUCTION_REL,
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
        ["git", "checkout", "--quiet", "--detach", LH_HEAD], cwd=checkout, check=True
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
    shutil.copyfile(ROOT / LI_REDUCTION_REL, Path(context["runtime_manifest_path"]))
    (export / fm.fresh_context.GUEST_CONTEXT_FILENAME).write_bytes(
        fm.canonical_bytes(context)
    )
    overlay = Path(context["overlay_path"])
    overlay.parent.mkdir(parents=True, exist_ok=True)
    overlay.touch()
    observations = fm.observe_context_assets(ROOT, context, LI_REDUCTION_REL)
    readiness = fm.authority_free_static_readiness(
        repository_root=ROOT,
        context=context,
        observed_head=current_head,
        observed_tree=current_tree,
        repository_clean=True,
        observed_asset_sha256=observations,
        candidate_source_path=LI_REDUCTION_REL,
    )
    checkout_binding = context["qemu_executable_base_seed_checkout_bindings"]["checkout"]
    if (
        readiness.get("result") != "STATIC_READINESS_PASS"
        or context["repository_head"] != current_head
        or context["repository_tree"] != current_tree
        or checkout_binding["head"] != LH_HEAD
        or checkout_binding["tree"] != LH_TREE
        or current_head == LH_HEAD
        or fm.context_vector(context) != fm.fresh_context.WRONG_SCOPE
    ):
        raise LJVerificationError("POST_COMMIT_PHASE_A_RESULT_MISMATCH")
    return {
        "result": "PASS__POST_COMMIT_PHASE_A_STATIC_READINESS",
        "repository_head": current_head,
        "repository_tree": current_tree,
        "governed_runtime_checkout_head": LH_HEAD,
        "governed_runtime_checkout_tree": LH_TREE,
        "vector": "WRONG_SCOPE",
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
    raw = REDUCTION.read_bytes()
    envelope = json.loads(raw)
    reduction = envelope.get("reduction")
    if (
        raw != canonical_bytes(envelope)
        or not isinstance(reduction, dict)
        or envelope.get("reduction_sha256") != sha256_bytes(canonical_bytes(reduction))
        or reduction.get("terminal") != TERMINAL
        or {
            key: reduction.get("e05", {}).get(key)
            for key in ("after", "before", "credit")
        } != {"after": "12/18", "before": "12/18", "credit": 0}
        or any(reduction.get("operational_counters", {}).values())
    ):
        raise LJVerificationError("LJ_REDUCTION_CONTRACT_MISMATCH")
    headings = [
        line for line in REPORT.read_text(encoding="utf-8").splitlines()
        if line.startswith("# ")
    ]
    expected = [f"# {index}. {title}" for index, title in enumerate((
        "Implementation Summary",
        "Code Evidence",
        "Constitutional Self-Assessment",
        "Validation Matrix",
        "Repository Mutation Summary",
        "Certification Verdict",
    ), 1)]
    if headings != expected or not REPORT.read_text(encoding="utf-8").rstrip().endswith(TERMINAL):
        raise LJVerificationError("G48_REPORT_STRUCTURE_MISMATCH")
    return reduction


def verify(work_root: Path, require_evidence: bool = True) -> dict[str, Any]:
    entry = authenticate_entry()
    failure = authenticate_predecessor()
    reuse = authenticate_stable_reuse()
    seed = authenticate_seed_projection()
    phase_a = authenticate_postcommit_phase_a(work_root)
    evidence = authenticate_evidence() if require_evidence else None
    return {
        "terminal": TERMINAL,
        "entry": entry,
        "predecessor_failure": failure,
        "stable_reuse": reuse,
        "seed": seed,
        "phase_a": phase_a,
        "evidence": evidence,
    }


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="g77_256lj_verify.", dir="/tmp") as temporary:
        print(verify(Path(temporary))["terminal"])
