#!/usr/bin/env python3
"""Verify the sealed, authority-free G77-256LK WRONG_SCOPE decision object.

This module has no operational entry point.  It authenticates committed owners,
checks one review-only decision object, and stops before Human authority creation.
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
BASE_HEAD = "e3d046cd6ad2f9e4b5e808395d88f56cc03c5a52"
BASE_TREE = "a49057d831079259daa65f52fc188b7a5c8f0b1e"
BASE_SUBJECT = "G77-256LJ record terminal post-commit readiness"
LJ_IMPLEMENTATION = "921c9a8781a22c21e259d5136c9911073d0305b3"
LI_ANCESTOR = "0604669f956c328538dc87eb55e72112f78a420a"
RUNTIME_HEAD = "f7acd5feb3dec686ca4e2cd359b63e232f6c5fbe"
RUNTIME_TREE = "968704d8915edf6d524a8a7705591788d8333bdd"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
EXPECTED_SCOPE = "P11_DA_ONE_BOUNDED_OPERATIONAL_ATTEMPT_V1"
PRESENTED_SCOPE = "P11_DA_DIFFERENT_OPERATIONAL_SCOPE_V1"
DECISION_ID = "G77_256LK_WRONG_SCOPE_PHASE_A_DECISION_OBJECT_001"
TERMINAL = (
    "A__G77_256LK_WRONG_SCOPE_FRESH_PHASE_A_DECISION_OBJECT_SEALED__"
    "ZERO_AUTHORITY__ZERO_OPERATION__READY_FOR_HUMAN_DECISION"
)
LK_REL = Path(
    ".github/governance/evidence/"
    "g77_256lk_wrong_scope_fresh_phase_a_decision_v1"
)
LK = ROOT / LK_REL
DECISION = LK / "G77_256LK_WRONG_SCOPE_PHASE_A_DECISION_OBJECT_V1.json"
PRESENTATION = LK / "G77_256LK_HUMAN_DECISION_PRESENTATION_V1.txt"
REDUCTION = LK / "G77_256LK_SPCE_TERMINAL_REDUCTION_V1.json"
REPORT = LK / "G77_256LK_G48_IMPLEMENTATION_REPORT_V1.md"

SOURCES = {
    Path(".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"):
        "4bb8151e68aca89dd09e85178e177834a2811211870a37124d3991d757c7c247",
    Path(".github/governance/evidence/g77_256lg_wrong_scope_existing_route_admission_v1/adapter/G77_256LG_WRONG_SCOPE_VECTOR_ADAPTER_V1.py"):
        "035c3c02cfb4cee26c6af2501b85a547d0376c80c4df376b7a40a8671277136f",
    Path(".github/governance/evidence/g77_256le_wrong_scope_minimum_governed_delta_v1/G77_256LE_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"):
        "7710f40b8f2bb57229167c37fff527cf2e18c81769f82db096e029a3895c45dc",
    Path(".github/governance/evidence/g77_256lj_wrong_scope_stable_checkout_reuse_v1/G77_256LJ_SPCE_TERMINAL_REDUCTION_V1.json"):
        "2cc59e4e1f20007640de360f998441dd7db5bd99e2fa942fc131d22176635b36",
    Path("aigol/runtime/canonical_human_authority_act_contract_v1.py"):
        "905ce577c31c2c538033455d1633470a34e9f7a94edd6190d50932e97ba8ebc8",
    Path(".github/governance/evidence/g77_256er_p11_operational_v1/harness/G77_256ER_P11_OPERATIONAL_HARNESS_V1.py"):
        "c6539d1cc60940b1999956965bff43923a270598a982cd19f976eadec0a93152",
    Path("tests/p11_da_operational_consumer_v1.py"):
        "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5",
    Path(".github/governance/evidence/g77_256ex_common_substrate_certification_v1/G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"):
        "91c477171147c56516c0f473ab887c12173c4bab225f2733c274b32467824b2f",
}


class LKVerificationError(RuntimeError):
    """One deterministic, fail-closed LK verification failure."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value, sort_keys=True, separators=(",", ":"),
            ensure_ascii=False, allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=cwd, text=True, stderr=subprocess.DEVNULL
    ).strip()


def is_ancestor(ancestor: str, descendant: str) -> bool:
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        check=False,
    ).returncode == 0


def load_module(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise LKVerificationError(f"MODULE_LOAD_FAILED:{identity}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def load_canonical(path: Path) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise LKVerificationError(f"DUPLICATE_JSON_KEY:{key}")
            result[key] = value
        return result

    value = json.loads(path.read_bytes(), object_pairs_hook=unique)
    if not isinstance(value, dict) or path.read_bytes() != canonical_bytes(value):
        raise LKVerificationError(f"NONCANONICAL_JSON:{path}")
    return value


def authenticate_repository() -> dict[str, str]:
    head = git("rev-parse", "HEAD")
    remote = git("rev-parse", f"refs/remotes/origin/{BRANCH}")
    if (
        ROOT != Path("/home/pisarna/work/sapianta-fl")
        or git("rev-parse", "--show-toplevel") != str(ROOT)
        or git("branch", "--show-current") != BRANCH
        or git("rev-parse", f"{BASE_HEAD}^{{tree}}") != BASE_TREE
        or git("show", "-s", "--format=%s", BASE_HEAD) != BASE_SUBJECT
        or not is_ancestor(LI_ANCESTOR, BASE_HEAD)
        or not is_ancestor(LJ_IMPLEMENTATION, BASE_HEAD)
        or not is_ancestor(BASE_HEAD, head)
        or not is_ancestor(BASE_HEAD, remote)
    ):
        raise LKVerificationError("LJ_ENTRY_OR_SUCCESSOR_AUTHENTICATION_FAILED")
    dirty = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT, text=True,
    ).splitlines()
    unexpected = [
        line for line in dirty
        if not line[3:].startswith(LK_REL.as_posix() + "/")
    ]
    if unexpected:
        raise LKVerificationError(f"UNRELATED_MUTATION:{unexpected}")
    nested = ROOT / "sapianta_system"
    if (
        git("rev-parse", "HEAD", cwd=nested) != NESTED_HEAD
        or git("rev-parse", "HEAD^{tree}", cwd=nested) != NESTED_TREE
        or git("status", "--porcelain", cwd=nested)
        or git("branch", "--show-current", cwd=nested)
        or git("rev-parse", f"refs/tags/{NESTED_TAG}^{{}}", cwd=nested)
        != NESTED_HEAD
    ):
        raise LKVerificationError("NESTED_AUTHORITY_CHECKPOINT_MISMATCH")
    return {"base_head": BASE_HEAD, "base_tree": BASE_TREE, "head": head, "remote": remote}


def authenticate_sources() -> None:
    for relative, digest in SOURCES.items():
        path = ROOT / relative
        if path.is_symlink() or not path.is_file() or sha256_path(path) != digest:
            raise LKVerificationError(f"SOURCE_IDENTITY_MISMATCH:{relative}")
        committed = subprocess.check_output(
            ["git", "show", f"{BASE_HEAD}:{relative.as_posix()}"], cwd=ROOT
        )
        if committed != path.read_bytes():
            raise LKVerificationError(f"SOURCE_NOT_BASE_COMMITTED:{relative}")


def authenticate_wrong_scope_static_semantics() -> dict[str, Any]:
    adapter_path = next(path for path in SOURCES if "G77_256LG_" in path.name)
    fm_path = next(path for path in SOURCES if "G77_256FM_ONE" in path.name)
    adapter = load_module(ROOT / adapter_path, "g77_256lk_static_adapter")
    model = adapter.authenticate_wrong_scope_semantics(ROOT)
    source = adapter.specialize_fc_runtime_source(
        repository_root=ROOT, identity_namespace_prefix="G77_256LK"
    )
    required = (
        'AUTHORIZED_ATTEMPT_ID = "G77_256LK_E05_AUTHORIZED_ATTEMPT_001"',
        'ACT_ID = "G77_256LK_EXACT_CURRENT_ONE_USE_HUMAN_OPERATIONAL_ACT_001"',
        '"input_identity": "G77_256LK_E05_WRONG_SCOPE_BASELINE_INPUT_001"',
        '"provenance_identity": "G77_256LK_AUTHENTICATED_FA_EM_CD_PROVENANCE_V1"',
        '"contract_identity": "G77_256LK_E05_WRONG_SCOPE_FAIL_CLOSED_CONTRACT_V1"',
        'wrong_act_value["authority_scope"] = WRONG_SCOPE_ID',
        'authority_differing_fields == ["authority_scope"]',
        'denial_error == "operational Human act scope is invalid"',
    )
    if not all(fragment in source for fragment in required):
        raise LKVerificationError("LK_STATIC_SPECIALIZATION_BINDING_MISMATCH")
    fm = load_module(ROOT / fm_path, "g77_256lk_fm_owner")
    if fm.governed_checkout_identity(
        ROOT, fm.fresh_context.WRONG_SCOPE, BASE_HEAD, BASE_TREE
    ) != (RUNTIME_HEAD, RUNTIME_TREE):
        raise LKVerificationError("STABLE_RUNTIME_CHECKOUT_BINDING_MISMATCH")
    return model


def authenticate_decision_object() -> dict[str, Any]:
    envelope = load_canonical(DECISION)
    decision = envelope.get("decision_object")
    if (
        envelope.get("schema_id")
        != "G77_256LK_WRONG_SCOPE_PHASE_A_DECISION_OBJECT_ENVELOPE_V1"
        or not isinstance(decision, dict)
        or envelope.get("decision_object_sha256")
        != sha256_bytes(canonical_bytes(decision))
    ):
        raise LKVerificationError("DECISION_OBJECT_SEAL_INVALID")
    required = {
        "GENERATION_ID": "G77_256LK_WRONG_SCOPE_FRESH_PHASE_A_DECISION_OBJECT_V1",
        "VECTOR": "WRONG_SCOPE",
        "DECISION_OBJECT_ID": DECISION_ID,
        "CANONICAL_OPERATION_ID": "G77_256LK_E05_WRONG_SCOPE_DENIAL_BEFORE_P11_ENTRY_001",
        "CURRENT_REPOSITORY_HEAD": BASE_HEAD,
        "CURRENT_REPOSITORY_TREE": BASE_TREE,
        "GOVERNED_RUNTIME_CHECKOUT_HEAD": RUNTIME_HEAD,
        "GOVERNED_RUNTIME_CHECKOUT_TREE": RUNTIME_TREE,
        "EXPECTED_SCOPE": EXPECTED_SCOPE,
        "PRESENTED_SCOPE": PRESENTED_SCOPE,
        "RETRY_LIMIT": 0,
        "AUTHORITY_STATE": "NONE",
        "OPERATION_STATE": "NOT_STARTED",
        "P11_ENTRY_STATE": "NOT_ENTERED",
        "PROTECTED_EFFECT_STATE": "NONE",
        "HUMAN_DECISION_STATE": "PENDING",
        "NEXT_ALLOWED_TRANSITION": "EXPLICIT_HUMAN_DECISION",
    }
    if any(decision.get(key) != value for key, value in required.items()):
        raise LKVerificationError("DECISION_OBJECT_REQUIRED_BINDING_MISMATCH")
    mismatch = decision.get("ISOLATED_SCOPE_MISMATCH", {})
    if mismatch != {
        "dependent_recomputation_fields": [
            "canonical_Human_act_content_identity",
            "CHE_source_act_digest",
            "CHE_correlation_identity",
        ],
        "expected": EXPECTED_SCOPE,
        "independent_semantic_mutation_count": 1,
        "independent_semantic_mutation_field": "authority_scope",
        "presented": PRESENTED_SCOPE,
    }:
        raise LKVerificationError("SCOPE_MISMATCH_NOT_EXACTLY_ONE")
    candidate = decision.get("CANDIDATE_HUMAN_ACT_MATERIAL", {})
    if (
        candidate.get("is_authority") is not False
        or candidate.get("human_authority_source_bytes_state") != "ABSENT"
        or candidate.get("human_actor_identity_state") != "ABSENT"
        or candidate.get("payload_digest_state") != "UNMATERIALIZED"
        or candidate.get("proposed_authority_scope") != PRESENTED_SCOPE
    ):
        raise LKVerificationError("CANDIDATE_MATERIAL_CROSSES_HUMAN_BOUNDARY")
    notices = set(decision.get("NOTICES", []))
    if not {
        "THIS OBJECT IS NOT AUTHORIZED",
        "APPROVAL HAS NOT YET BEEN GIVEN",
        "NO OPERATION MAY START FROM THIS GENERATION",
        "INTELLIGENCE != AUTHORITY",
    }.issubset(notices):
        raise LKVerificationError("MANDATORY_NONAUTHORITY_NOTICE_MISSING")
    counters = decision.get("STATE_COUNTERS", {})
    if not counters or any(counters.values()):
        raise LKVerificationError("AUTHORITY_OR_OPERATION_COUNTER_NONZERO")
    if len(list(LK.glob("*DECISION_OBJECT*.json"))) != 1:
        raise LKVerificationError("DECISION_OBJECT_COUNT_NOT_ONE")
    historical = subprocess.run(
        ["git", "grep", "-F", DECISION_ID, BASE_HEAD], cwd=ROOT,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
    )
    if historical.returncode == 0:
        raise LKVerificationError("DECISION_FRESHNESS_NOT_PROVEN")
    return decision


def authenticate_presentation(decision: dict[str, Any]) -> None:
    text = PRESENTATION.read_text(encoding="utf-8")
    required = (
        "THIS OBJECT IS NOT AUTHORIZED",
        "APPROVAL HAS NOT YET BEEN GIVEN",
        "NO OPERATION MAY START FROM THIS GENERATION",
        DECISION_ID,
        EXPECTED_SCOPE,
        PRESENTED_SCOPE,
        sha256_bytes(canonical_bytes(decision)),
        "READY_FOR_HUMAN_DECISION = YES",
    )
    if not all(fragment in text for fragment in required):
        raise LKVerificationError("HUMAN_PRESENTATION_INCOMPLETE")


def verify() -> dict[str, Any]:
    repository = authenticate_repository()
    authenticate_sources()
    semantics = authenticate_wrong_scope_static_semantics()
    decision = authenticate_decision_object()
    authenticate_presentation(decision)
    return {
        "terminal": TERMINAL,
        "repository": repository,
        "decision_object_sha256": sha256_bytes(canonical_bytes(decision)),
        "independent_semantic_mutation_count": semantics[
            "independent_semantic_mutation_count"
        ],
        "authority_creation_count": 0,
        "operation_attempt_count": 0,
        "ready_for_human_decision": True,
    }


if __name__ == "__main__":
    print(verify()["terminal"])
