#!/usr/bin/env python3
"""Verify the G77-256LN pre-authority current-admission conflict.

This verifier is read-only.  It does not construct a Human authority object,
call final admission with synthetic authority, consume authority, or invoke the
FM operational route.  It proves that the first authority-free conjunct of
final admission rejects the exact sealed LM context at the LN entry commit.
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
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ENTRY_HEAD = "027b76b3031acd2214add3e447e0197e884833ec"
ENTRY_TREE = "e4c5c567887bfbfa16ae98a5034cabbad29d4346"
ENTRY_SUBJECT = "G77-256LM record fresh Human decision readiness"
LM_IMPLEMENTATION = "7368af35f707f75f4d0951133995013211699126"
LM_IMPLEMENTATION_TREE = "43d9ea08d098b751ed738d050e9d73b4eff3261b"
LL_HEAD = "ea3781b64cd8780021e8cbb5e65f6b057b1bf649"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
DECISION_ID = "G77_256LM_WRONG_SCOPE_PHASE_A_DECISION_OBJECT_001"
OPERATION_ID = "G77_256LM_E05_WRONG_SCOPE_DENIAL_BEFORE_P11_ENTRY_001"
DECISION_FILE_SHA256 = "a0dd34a573e4dc43482d6d7054f55ba8c3792f573c92606c119b6f31f82ceadc"
DECISION_INNER_SHA256 = "a50c9d17f9b69667fd3074bce8c713e67347700ba6ddcc5c7f2e399dfcfdddb7"
RECEIPT_FILE_SHA256 = "9d95056790eefdca89afaf5a46112e5b37b356b2ae3d137b929144e5e915a725"
RECEIPT_INNER_SHA256 = "88c2e05a4d667c4cb418b14d9b0de5a2bb62fc73c9cbb15ca5e97ffea33a8a8e"
HUMAN_DECISION_PROMPT_SHA256 = "ebc0da0131702480c046eb9792f76ed502027037ff0a858f203bba9e79a06bf1"
HUMAN_DECISION_PROMPT_BYTE_COUNT = 21939
EXPECTED_SCOPE = "P11_DA_ONE_BOUNDED_OPERATIONAL_ATTEMPT_V1"
PRESENTED_SCOPE = "P11_DA_DIFFERENT_OPERATIONAL_SCOPE_V1"
FAILURE = "sealed route target is not the current repository identity"
TERMINAL = "A__G77_256LN_AUTHORITY_BINDING_CONFLICT__STOP"

LN_REL = Path(
    ".github/governance/evidence/"
    "g77_256ln_wrong_scope_operational_acceptance_v1"
)
LN = ROOT / LN_REL
LM_REL = Path(
    ".github/governance/evidence/"
    "g77_256lm_wrong_scope_receipt_parent_phase_a_v1"
)
LM = ROOT / LM_REL
DECISION = LM / "G77_256LM_WRONG_SCOPE_PHASE_A_DECISION_OBJECT_V1.json"
RECEIPT = LM / "G77_256LM_GL_RECEIPT_PARENT_OBSERVATION_V1.json"
CONTEXT = LM / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
LM_REDUCTION = LM / "G77_256LM_SPCE_TERMINAL_REDUCTION_V1.json"
FM_REL = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
GL_REL = Path(
    ".github/governance/evidence/g77_256gl_receipt_parent_equivalence_v1/"
    "orchestration/G77_256GL_RECEIPT_PARENT_PREAUTHORIZATION_BINDING_V1.py"
)
LJ_TEST_REL = Path(
    ".github/governance/evidence/g77_256lj_wrong_scope_stable_checkout_reuse_v1/"
    "tests/test_g77_256lj_stable_checkout_reuse_v1.py"
)
SOURCE_HASHES = {
    FM_REL: "4bb8151e68aca89dd09e85178e177834a2811211870a37124d3991d757c7c247",
    GL_REL: "e98451a19daeeab752334e93564c29bc71c13e660d172076c940ab66516b30bc",
    LJ_TEST_REL: "f70c3c867cf2a3dd271a59dab70856baba542f6a09587a395b41f48ce4e9a8fa",
    LM_REL / "analysis/G77_256LM_PHASE_A_LIFECYCLE_V1.py": "873ec7ee664b19d7e6fc1ae31e8abb7d14b5e4ee7f1f4e452a26753419bec423",
    LM_REL / "G77_256LM_G48_IMPLEMENTATION_REPORT_V1.md": "3a4ef266a257ce9be9fb3e8b9fe496400f73d5a2c703970c376e8f1fd1890af2",
}
AUTHORITY_PATTERNS = (
    "*HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE*",
    "*FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF*",
    "*AUTHORITY_VALIDATION_AND_CONSUMPTION*",
    "*OPERATIONAL_INVOCATION_ATTEMPT*",
)


class LNConflict(RuntimeError):
    """One fail-closed LN verification error."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                   allow_nan=False) + "\n"
    ).encode("utf-8")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=cwd, text=True, stderr=subprocess.DEVNULL
    ).strip()


def is_ancestor(ancestor: str, descendant: str) -> bool:
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant], cwd=ROOT,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
    ).returncode == 0


def load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise LNConflict(f"MODULE_UNAVAILABLE:{name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


FM = load_module(ROOT / FM_REL, "g77_256ln_existing_fm_owner")
GL = load_module(ROOT / GL_REL, "g77_256ln_existing_gl_owner")


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise LNConflict(f"NONCANONICAL_JSON:{path}")
    return value


def authenticate_repository() -> dict[str, str]:
    head = git("rev-parse", "HEAD")
    remote = git("rev-parse", f"refs/remotes/origin/{BRANCH}")
    if (
        ROOT != Path("/home/pisarna/work/sapianta-fl")
        or git("branch", "--show-current") != BRANCH
        or git("rev-parse", f"{ENTRY_HEAD}^{{tree}}") != ENTRY_TREE
        or git("show", "-s", "--format=%s", ENTRY_HEAD) != ENTRY_SUBJECT
        or git("rev-parse", f"{LM_IMPLEMENTATION}^{{tree}}")
        != LM_IMPLEMENTATION_TREE
        or not is_ancestor(LL_HEAD, ENTRY_HEAD)
        or not is_ancestor(LM_IMPLEMENTATION, ENTRY_HEAD)
        or not is_ancestor(ENTRY_HEAD, head)
        or not is_ancestor(ENTRY_HEAD, remote)
    ):
        raise LNConflict("LM_ENTRY_OR_SUCCESSOR_AUTHENTICATION_FAILED")
    dirty = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT, text=True,
    ).splitlines()
    unexpected = [
        line for line in dirty if not line[3:].startswith(LN_REL.as_posix() + "/")
    ]
    if unexpected:
        raise LNConflict(f"UNRELATED_MUTATION:{unexpected}")
    nested = ROOT / "sapianta_system"
    if (
        git("rev-parse", "HEAD", cwd=nested) != NESTED_HEAD
        or git("rev-parse", "HEAD^{tree}", cwd=nested) != NESTED_TREE
        or git("status", "--porcelain", cwd=nested)
        or git("branch", "--show-current", cwd=nested)
        or git("rev-parse", f"refs/tags/{NESTED_TAG}^{{}}", cwd=nested)
        != NESTED_HEAD
    ):
        raise LNConflict("NESTED_AUTHORITY_MISMATCH")
    return {"entry_head": ENTRY_HEAD, "entry_tree": ENTRY_TREE,
            "current_head": head, "remote_head": remote}


def authenticate_sources() -> None:
    for relative, expected in SOURCE_HASHES.items():
        path = ROOT / relative
        if path.is_symlink() or not path.is_file() or sha256_path(path) != expected:
            raise LNConflict(f"SOURCE_IDENTITY_MISMATCH:{relative}")
        if subprocess.check_output(
            ["git", "show", f"{ENTRY_HEAD}:{relative.as_posix()}"], cwd=ROOT
        ) != path.read_bytes():
            raise LNConflict(f"SOURCE_NOT_LM_COMMITTED:{relative}")


def authenticate_phase_a() -> tuple[dict[str, Any], dict[str, Any]]:
    if sha256_path(DECISION) != DECISION_FILE_SHA256:
        raise LNConflict("DECISION_WHOLE_FILE_SHA_MISMATCH")
    decision_envelope = load_canonical(DECISION)
    decision = decision_envelope.get("decision_object")
    if (
        not isinstance(decision, dict)
        or decision_envelope.get("decision_object_sha256") != DECISION_INNER_SHA256
        or hashlib.sha256(canonical_bytes(decision)).hexdigest() != DECISION_INNER_SHA256
        or decision.get("DECISION_OBJECT_ID") != DECISION_ID
        or decision.get("CANONICAL_OPERATION_ID") != OPERATION_ID
        or decision.get("VECTOR") != "WRONG_SCOPE"
        or decision.get("EXPECTED_SCOPE") != EXPECTED_SCOPE
        or decision.get("PRESENTED_SCOPE") != PRESENTED_SCOPE
        or decision.get("ISOLATED_SCOPE_MISMATCH", {}).get(
            "independent_semantic_mutation_count"
        ) != 1
        or decision.get("ISOLATED_SCOPE_MISMATCH", {}).get(
            "independent_semantic_mutation_field"
        ) != "authority_scope"
        or decision.get("AUTHORITY_STATE") != "NONE"
        or decision.get("OPERATION_STATE") != "NOT_STARTED"
        or decision.get("P11_ENTRY_STATE") != "NOT_ENTERED"
        or decision.get("PROTECTED_EFFECT_STATE") != "NONE"
        or decision.get("HUMAN_DECISION_STATE") != "PENDING"
        or any(decision.get("STATE_COUNTERS", {}).values())
    ):
        raise LNConflict("DECISION_OBJECT_CONFLICT")
    if sha256_path(RECEIPT) != RECEIPT_FILE_SHA256:
        raise LNConflict("RECEIPT_WHOLE_FILE_SHA_MISMATCH")
    receipt_envelope = load_canonical(RECEIPT)
    receipt = receipt_envelope.get("observation")
    if (
        not isinstance(receipt, dict)
        or receipt_envelope.get("observation_sha256") != RECEIPT_INNER_SHA256
        or hashlib.sha256(canonical_bytes(receipt)).hexdigest() != RECEIPT_INNER_SHA256
    ):
        raise LNConflict("RECEIPT_INNER_SHA_MISMATCH")
    context = load_canonical(CONTEXT)
    GL.validate_bound_observation(ROOT, context, receipt_envelope)
    checkpoint = GL.reduce_preauthorization_checkpoint(ROOT, context, receipt_envelope)
    proof = GL.validate_preauth_final_admission_equivalence(
        ROOT, context, receipt_envelope, checkpoint
    )
    if proof.get("preauth_final_admission_equivalence") != GL.EQUIVALENCE_RESULT:
        raise LNConflict("RECEIPT_FINAL_ADMISSION_EQUIVALENCE_CONFLICT")
    return decision, context


def prove_preauthority_final_admission_conflict(
    context: dict[str, Any]
) -> dict[str, str]:
    current_head = git("rev-parse", "HEAD")
    current_tree = git("rev-parse", "HEAD^{tree}")
    if (
        context.get("repository_head") != LL_HEAD
        or context.get("repository_tree") != "607e9dae3a562d823d64b17888c11d3e4b881e2f"
        or current_head == context["repository_head"]
        or current_tree == context["repository_tree"]
    ):
        raise LNConflict("EXPECTED_SEALED_BASE_CURRENT_ADMISSION_DIFFERENCE_ABSENT")
    try:
        FM.authenticate_current_committed_jm_route(
            ROOT, context["repository_head"], context["repository_tree"]
        )
    except RuntimeError as error:
        if str(error) != FAILURE:
            raise LNConflict(f"UNEXPECTED_CURRENT_ADMISSION_FAILURE:{error}") from error
    else:
        raise LNConflict("STALE_SEALED_ROUTE_UNEXPECTEDLY_ADMITTED")
    source = (ROOT / FM_REL).read_text(encoding="utf-8")
    static_at = source.index("def authority_free_static_readiness(")
    final_at = source.index("def validate_final_admission(")
    if (
        source.find("authenticate_current_committed_jm_route(", static_at)
        > source.find("def constitutional_anchor_is_ancestor(", static_at)
        or source.find("static_readiness = authority_free_static_readiness(", final_at) < 0
    ):
        raise LNConflict("FINAL_ADMISSION_CURRENT_ROUTE_ORDER_UNPROVEN")
    lj_test = (ROOT / LJ_TEST_REL).read_text(encoding="utf-8")
    if (
        "test_current_admission_equality_was_not_weakened" not in lj_test
        or "sealed route target is not the current" not in lj_test
    ):
        raise LNConflict("LJ_CURRENT_ADMISSION_INVARIANT_UNPROVEN")
    return {
        "sealed_materialization_head": context["repository_head"],
        "sealed_materialization_tree": context["repository_tree"],
        "current_admission_head": current_head,
        "current_admission_tree": current_tree,
        "first_failed_conjunct": "FM_AUTHORITY_FREE_STATIC_READINESS_CURRENT_COMMITTED_JM_ROUTE",
        "error": FAILURE,
    }


def authenticate_zero_authority_operation() -> None:
    for pattern in AUTHORITY_PATTERNS:
        if list(LN.rglob(pattern)):
            raise LNConflict(f"LN_AUTHORITY_OR_OPERATION_ARTIFACT_PRESENT:{pattern}")
    context = load_canonical(CONTEXT)
    if any(path.exists() for path in FM.receipt_consumable_paths(ROOT, context)):
        raise LNConflict("LM_RECEIPT_NAMESPACE_CONSUMED")


def verify() -> dict[str, Any]:
    repository = authenticate_repository()
    authenticate_sources()
    decision, context = authenticate_phase_a()
    conflict = prove_preauthority_final_admission_conflict(context)
    authenticate_zero_authority_operation()
    return {
        "terminal": TERMINAL,
        "entry": repository,
        "human_decision_present": True,
        "human_decision_prompt_sha256": HUMAN_DECISION_PROMPT_SHA256,
        "human_decision_prompt_byte_count": HUMAN_DECISION_PROMPT_BYTE_COUNT,
        "decision_object_id": decision["DECISION_OBJECT_ID"],
        "operation_identity": decision["CANONICAL_OPERATION_ID"],
        "failure_class": "DUPLICATE_OR_EQUIVALENT_EDGE",
        "conflict": conflict,
        "human_authority_source_count": 0,
        "authority_creation_count": 0,
        "authority_consumption_count": 0,
        "operation_attempt_count": 0,
        "qemu_start_count": 0,
        "vm_start_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "e05_before": "12/18",
        "ln_e05_credit": 0,
        "e05_after": "12/18",
    }


if __name__ == "__main__":
    print(verify()["terminal"])
