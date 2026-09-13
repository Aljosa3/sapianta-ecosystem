#!/usr/bin/env python3
"""Verify the fail-closed G77-256LH pre-Human binding terminal.

The verifier is read-only. It authenticates the committed LG authority-free
capability proof, reconstructs the exact FM bootstrap mismatch, and proves
that no Human-authority or operational artifact exists.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
LH_REL = Path(
    ".github/governance/evidence/"
    "g77_256lh_fresh_wrong_scope_operational_acceptance_v1"
)
LH = ROOT / LH_REL
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
HEAD = "332ca67e20e8f330bc9182d1aa9cc99ef3f02363"
TREE = "8ac8b003bae4727c40ec20aaefd7ff41eb3d3c71"
SUBJECT = "G77-256LG align shadow lifecycle reporting"
IMPLEMENTATION_PARENT = "06bc0c36a58d89b78a7e5ad1378231744f5d3fea"
IMPLEMENTATION_TREE = "9d141fb4ca106853921f3d2dfaa48b2c486d3aa2"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
GENERATION = (
    "G77_256LH_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_SCOPE_"
    "OPERATIONAL_COMMISSIONING_V1"
)
OPERATION = "G77_256LH_E05_WRONG_SCOPE_DENIAL_BEFORE_P11_ENTRY_001"
TERMINAL = "A__G77_256LH_PHASE_A_BINDING_FAILURE__STOP"

FM_PATH = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
LG_ADAPTER_PATH = Path(
    ".github/governance/evidence/"
    "g77_256lg_wrong_scope_existing_route_admission_v1/adapter/"
    "G77_256LG_WRONG_SCOPE_VECTOR_ADAPTER_V1.py"
)
LG_REDUCTION_PATH = Path(
    ".github/governance/evidence/"
    "g77_256lg_wrong_scope_existing_route_admission_v1/"
    "G77_256LG_SPCE_TERMINAL_PHASE_A_REDUCTION_V1.json"
)
CONTEXT_PATH = LH_REL / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
REDUCTION_PATH = LH_REL / "G77_256LH_SPCE_PHASE_A_BINDING_FAILURE_REDUCTION_V1.json"
REPORT_PATH = LH_REL / "G77_256LH_G48_IMPLEMENTATION_REPORT_V1.md"
COMMITTED_HASHES = {
    FM_PATH: "c600cd2e723494558d6916460c7f358cd264f3ec72b96655afc23d8e3fb97bd5",
    LG_ADAPTER_PATH: "67847030651e8add82dd16bc8741ad0d81f44c7ba873689a521aea85f2ec4949",
    LG_REDUCTION_PATH: "c5610c246459af6c15387f031debd5ef7cb00461b16adbde3815ddfd6db415bf",
    Path("tests/p11_da_operational_consumer_v1.py"):
        "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5",
}
LG_INNER_SHA256 = "90cf9000bade0cebd63776b88d637156eb859b2ab934408745b0efb0d92de16e"
LG_TERMINAL = (
    "A__WRONG_SCOPE_EXISTING_ROUTE_ADMISSION_COMPLETE__"
    "PHASE_A_LIVE_BINDING_READY__READY_FOR_HUMAN_DECISION"
)


class LHVerificationError(RuntimeError):
    """One fail-closed verification error."""


def load_module(relative: Path, name: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, ROOT / relative)
    if specification is None or specification.loader is None:
        raise LHVerificationError(f"MODULE_UNAVAILABLE:{relative}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


FM = load_module(FM_PATH, "g77_256lh_failure_fm")
LG = load_module(LG_ADAPTER_PATH, "g77_256lh_failure_lg")


def canonical_bytes(value: Any, *, utf8: bool = False) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=not utf8,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def load_canonical(path: Path, *, utf8: bool = False) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value, utf8=utf8):
        raise LHVerificationError(f"NONCANONICAL_JSON:{path}")
    return value


def verify_seal(
    path: Path, inner_name: str, *, utf8: bool = False
) -> tuple[dict[str, Any], dict[str, Any]]:
    envelope = load_canonical(path, utf8=utf8)
    value = envelope.get(inner_name)
    if (
        not isinstance(value, dict)
        or envelope.get(f"{inner_name}_sha256")
        != sha256_bytes(canonical_bytes(value, utf8=utf8))
    ):
        raise LHVerificationError(f"INNER_SEAL_MISMATCH:{path}")
    return envelope, value


def authenticate_repository() -> None:
    if (
        ROOT != Path("/home/pisarna/work/sapianta-fl")
        or git("rev-parse", "--show-toplevel") != str(ROOT)
        or git("branch", "--show-current") != BRANCH
        or git("rev-parse", "HEAD") != HEAD
        or git("rev-parse", "HEAD^{tree}") != TREE
        or git("log", "-1", "--format=%s") != SUBJECT
        or git("rev-parse", "HEAD^") != IMPLEMENTATION_PARENT
        or git("show", "-s", "--format=%T", IMPLEMENTATION_PARENT)
        != IMPLEMENTATION_TREE
    ):
        raise LHVerificationError("OUTER_REPOSITORY_CHECKPOINT_MISMATCH")
    dirty = git("status", "--porcelain=v1", "--untracked-files=all").splitlines()
    if any(LH_REL.as_posix() not in line for line in dirty):
        raise LHVerificationError("MUTATION_OUTSIDE_LH_SCOPE")
    nested = ROOT / "sapianta_system"
    if (
        git("rev-parse", "HEAD", cwd=nested) != NESTED_HEAD
        or git("rev-parse", "HEAD^{tree}", cwd=nested) != NESTED_TREE
        or git("status", "--short", cwd=nested)
        or git("branch", "--show-current", cwd=nested)
        or git("rev-parse", f"refs/tags/{NESTED_TAG}^{{}}", cwd=nested)
        != NESTED_HEAD
    ):
        raise LHVerificationError("NESTED_AUTHORITY_CHECKPOINT_MISMATCH")
    for path, expected in COMMITTED_HASHES.items():
        raw = (ROOT / path).read_bytes()
        committed = subprocess.check_output(
            ["git", "show", f"{HEAD}:{path.as_posix()}"], cwd=ROOT
        )
        if raw != committed or sha256_bytes(raw) != expected:
            raise LHVerificationError(f"COMMITTED_DEPENDENCY_MISMATCH:{path}")


def authenticate_lg() -> None:
    envelope, reduction = verify_seal(
        ROOT / LG_REDUCTION_PATH, "reduction", utf8=True
    )
    if (
        envelope["reduction_sha256"] != LG_INNER_SHA256
        or reduction.get("terminal") != LG_TERMINAL
        or any(reduction.get("operational_counters", {}).values())
        or reduction.get("e05", {}).get("after") != "12/18"
        or reduction.get("e05", {}).get("credit") != 0
    ):
        raise LHVerificationError("LG_TERMINAL_CONTRACT_MISMATCH")
    model = LG.authenticate_wrong_scope_semantics(ROOT)
    if (
        model.get("independent_semantic_mutation_count") != 1
        or model.get("independent_semantic_mutation_set")
        != [
            "authority_scope:P11_DA_ONE_BOUNDED_OPERATIONAL_ATTEMPT_V1"
            "->P11_DA_DIFFERENT_OPERATIONAL_SCOPE_V1"
        ]
    ):
        raise LHVerificationError("LG_WRONG_SCOPE_MODEL_MISMATCH")


def derive_binding_failure(context: dict[str, Any]) -> dict[str, Any]:
    binding = context["guest_adapter_binding"]
    bootstrap = FM.bootstrap_asset_bindings(context)
    cloud_path = ROOT / bootstrap["cloud_init_path"]
    observed = list(
        FM.bootstrap_guest_command_arguments(
            cloud_path.read_text(encoding="utf-8"),
            binding["bootstrap_guest_path"],
        )
    )
    expected = [
        binding["source_sha256"],
        context["wrapper_fc_er_che_schema_hashes"]["raw_evidence_schema"],
        context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["head"],
        context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["tree"],
        FM.sha256_path(ROOT / FM.DN_HARNESS),
    ]
    differences = [
        index
        for index, pair in enumerate(zip(observed, expected, strict=True))
        if pair[0] != pair[1]
    ]
    return {
        "validator": "FM_PROVE_GUEST_ADAPTER_BINDING",
        "error": "cloud-init pre-request argument binding mismatch",
        "expected_arguments": expected,
        "observed_arguments": observed,
        "differing_argument_indexes": differences,
        "differing_coordinates": ["checkout_head", "checkout_tree"],
        "matched_coordinates": [
            "adapter_sha256",
            "raw_evidence_schema_sha256",
            "dn_harness_sha256",
        ],
        "cloud_init_path": bootstrap["cloud_init_path"],
        "cloud_init_sha256": sha256_path(cloud_path),
        "seed_path": bootstrap["seed_path"],
        "seed_sha256": sha256_path(Path(bootstrap["seed_path"])),
    }


def verify() -> dict[str, Any]:
    authenticate_repository()
    authenticate_lg()
    context = load_canonical(ROOT / CONTEXT_PATH)
    FM.fresh_context.validate_context(context, repository_root=ROOT)
    envelope, reduction = verify_seal(ROOT / REDUCTION_PATH, "reduction")
    failure = derive_binding_failure(context)
    if (
        context.get("generation_identity") != GENERATION
        or context.get("operation_identity") != OPERATION
        or FM.context_vector(context) != "WRONG_SCOPE"
        or failure["differing_argument_indexes"] != [2, 3]
        or reduction.get("binding_failure") != failure
        or reduction.get("terminal") != TERMINAL
        or reduction.get("ready_for_human_decision") is not False
        or reduction.get("human_authority_present") is not False
        or reduction.get("phase_b_started") is not False
        or any(reduction.get("operational_counters", {}).values())
        or reduction.get("e05", {}).get("after") != "12/18"
        or reduction.get("e05", {}).get("credit") != 0
        or reduction.get("architecture", {}).get("production_mutation") != 0
    ):
        raise LHVerificationError("FAILURE_TERMINAL_CONTRACT_MISMATCH")
    forbidden_names = (
        "HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST",
        "HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION",
        "HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE",
        "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF",
        "PRE_EXECUTED_QEMU_ARGV_RECEIPT",
        "POST_EXECUTED_QEMU_ARGV_RECEIPT",
        "RAW_EXECUTION_EVIDENCE",
        "GUEST_EXECUTION_SEAL",
    )
    forbidden = [
        path.relative_to(ROOT).as_posix()
        for path in LH.rglob("*")
        if path.is_file() and any(token in path.name for token in forbidden_names)
    ]
    if forbidden or Path(context["serial_path"]).exists():
        raise LHVerificationError(f"FORBIDDEN_OPERATIONAL_ARTIFACT:{forbidden}")
    for relative in context["guest_output_relative_paths"]:
        if (Path(context["runtime_export_root"]) / relative).exists():
            raise LHVerificationError(f"OPERATIONAL_GUEST_OUTPUT:{relative}")
    receipt_parent = Path(context["receipt_parent"])
    if receipt_parent.exists() and any(receipt_parent.iterdir()):
        raise LHVerificationError("OPERATIONAL_RECEIPT_PRESENT")
    report = (ROOT / REPORT_PATH).read_text(encoding="utf-8")
    headings = [line for line in report.splitlines() if line.startswith("# ")]
    if headings != [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ] or not report.rstrip().endswith(TERMINAL):
        raise LHVerificationError("G48_REPORT_STRUCTURE_MISMATCH")
    if set(envelope) != {"schema_id", "reduction", "reduction_sha256"}:
        raise LHVerificationError("REDUCTION_ENVELOPE_SHAPE_MISMATCH")
    return {
        "terminal": TERMINAL,
        "failure_class": "IMPLEMENTATION_REGRESSION",
        "differing_argument_indexes": [2, 3],
        "ready_for_human_decision": False,
        "operational_counters": reduction["operational_counters"],
        "e05": reduction["e05"],
        "ex": reduction["ex"],
    }


if __name__ == "__main__":
    print(verify()["terminal"])
