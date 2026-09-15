#!/usr/bin/env python3
"""Materialize once, then verify, the authority-free G77-256LV Phase A.

The materialization path reuses the authenticated FM/GL/LG/LP mechanisms.
It never creates or consumes authority and never invokes FM, QEMU, a VM, P11,
or a protected effect.  The default invocation is read-only verification.
"""

from __future__ import annotations

import argparse
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
ENTRY_HEAD = "3f6055f85c8bff0a3de89eda27421c92e0742904"
ENTRY_TREE = "2e99987b75cfdc891338870281a12fe21e018ec6"
ENTRY_SUBJECT = "G77-256LU prove LT to FM static integration readiness"
LT_HEAD = "f22fae2529de35eaf8093776c04a6a8e05a097f6"
LR_HEAD = "b738b0795b9d50b60819bbbf31e49fab6b47ed5d"
LQ_REVIEW_HEAD = "010aaf1b4f8ae14141d8f65ea9109dfcf5ffac83"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
RUNTIME_HEAD = "f7acd5feb3dec686ca4e2cd359b63e232f6c5fbe"
RUNTIME_TREE = "968704d8915edf6d524a8a7705591788d8333bdd"

AUTHORIZED_SCOPE = "P11_DA_ONE_BOUNDED_OPERATIONAL_ATTEMPT_V1"
PRESENTED_SCOPE = "P11_DA_DIFFERENT_OPERATIONAL_SCOPE_V1"
LIFECYCLE_ID = "G77_256LV_WRONG_SCOPE_PHASE_A_LIFECYCLE_001"
OBJECT_ID = "G77_256LV_WRONG_SCOPE_PHASE_A_OBJECT_001"
REVIEW_ID = "G77_256LV_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_001"
CONTEXT_ID = "G77_256LV_WRONG_SCOPE_CANONICAL_CONTEXT_001"
PRESENTATION_ID = "G77_256LV_WRONG_SCOPE_HUMAN_REVIEW_PRESENTATION_001"
GENERATION_ID = "G77_256LV_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_SCOPE_OPERATIONAL_COMMISSIONING_V1"
OPERATION_ID = "G77_256LV_E05_WRONG_SCOPE_DENIAL_BEFORE_P11_ENTRY_001"
ATTEMPT_ID = "G77_256LV_E05_FUTURE_AUTHORIZED_ATTEMPT_001"
PREFIX = "G77_256LV"
TERMINAL = (
    "A__G77_256LV_WRONG_SCOPE_FRESH_PHASE_A_REVIEW_OBJECT_SEALED__"
    "CURRENT_ADMISSION_BOUND__ZERO_AUTHORITY__ZERO_OPERATION__"
    "READY_FOR_HUMAN_DECISION"
)

LV_REL = Path(
    ".github/governance/evidence/"
    "g77_256lv_fresh_wrong_scope_phase_a_review_object_v1"
)
LV = ROOT / LV_REL
FM_REL = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
GL_REL = Path(
    ".github/governance/evidence/g77_256gl_receipt_parent_equivalence_v1/"
    "orchestration/G77_256GL_RECEIPT_PARENT_PREAUTHORIZATION_BINDING_V1.py"
)
LG_REL = Path(
    ".github/governance/evidence/g77_256lg_wrong_scope_existing_route_admission_v1/"
    "adapter/G77_256LG_WRONG_SCOPE_VECTOR_ADAPTER_V1.py"
)
CANDIDATE_REL = Path(
    ".github/governance/evidence/g77_256gd_fresh_operation_context_v1/"
    "candidate/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
)
LP_REL = Path(
    ".github/governance/evidence/g77_256lp_committed_review_transition_v1/"
    "G77_256LP_SPCE_TERMINAL_REDUCTION_V1.json"
)
LQ_REVIEW_REL = Path(
    ".github/governance/evidence/g77_256lq_wrong_scope_fresh_phase_a_review_object_v1/"
    "G77_256LQ_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_V1.json"
)
LR_REL = Path(
    ".github/governance/evidence/g77_256lr_operational_wrong_scope_denial_v1/"
    "G77_256LR_INTERRUPTED_STATE_RECONSTRUCTION_V1.json"
)
LT_REL = Path(
    ".github/governance/evidence/g77_256lt_session_independent_one_shot_supervision_v1/"
    "G77_256LT_TERMINAL_DECISION_V1.json"
)
LU_DECISION_REL = Path(
    ".github/governance/evidence/g77_256lu_lt_fm_static_integration_readiness_v1/"
    "G77_256LU_TERMINAL_DECISION_V1.json"
)
LU_RELATION_REL = Path(
    ".github/governance/evidence/g77_256lu_lt_fm_static_integration_readiness_v1/"
    "G77_256LU_STATIC_INTEGRATION_BINDING_RELATION_V1.json"
)
EX_REL = Path(
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
)
P11_REL = Path("tests/p11_da_operational_consumer_v1.py")
SOURCE_HASHES = {
    FM_REL: "5a0a597434bd89752828afd85ecb5a98669f41ae66fa0480ea27be6d611597e8",
    GL_REL: "e98451a19daeeab752334e93564c29bc71c13e660d172076c940ab66516b30bc",
    LG_REL: "035c3c02cfb4cee26c6af2501b85a547d0376c80c4df376b7a40a8671277136f",
    LP_REL: "fee1e1bdf2bf8de547135b05be09cf8b987ba2786a34642524a291a74470918b",
    LQ_REVIEW_REL: "035e406848463173bd68b6cf1ec810cdfa7ab846ce02b26cf376c7d81a77eecb",
    LR_REL: "429123ec1ddef737060de182e712cb1a6091318a69345ca720764f91977b126b",
    LT_REL: "f0a6acfc31c72b1b1e890cf2e3c587b4f5ccf179ecf2da9c6e2ad724a27aae9f",
    LU_DECISION_REL: "77cf5cd0c71875bca1d57f17a06605c79101dab9217f3f1782be7a1767141cf7",
    LU_RELATION_REL: "b17bcf19cc11142b0a4a603138c0311dcce0cfb34510c76dff156fbfcce9e80c",
    EX_REL: "91c477171147c56516c0f473ab887c12173c4bab225f2733c274b32467824b2f",
    P11_REL: "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5",
}

CONTEXT = LV / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
READINESS = LV / "G77_256LV_PREAUTHORITY_STATIC_READINESS_V1.json"
REVIEW = LV / "G77_256LV_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_V1.json"
PRESENTATION = LV / "G77_256LV_HUMAN_DECISION_PRESENTATION_V1.txt"
REDUCTION = LV / "G77_256LV_SPCE_TERMINAL_REDUCTION_V1.json"
DECISION = LV / "G77_256LV_TERMINAL_DECISION_V1.json"
REPORT = LV / "G77_256LV_G48_IMPLEMENTATION_REPORT_V1.md"
TRANSIENT = Path("/tmp/g77_256lv_fresh_wrong_scope_phase_a_review_object_v1")


class LVVerificationError(RuntimeError):
    """One deterministic fail-closed LV verification failure."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=cwd, text=True, stderr=subprocess.DEVNULL
    ).strip()


def is_ancestor(ancestor: str, descendant: str) -> bool:
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def load_module(path: Path, name: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise LVVerificationError(f"MODULE_LOAD_FAILED:{name}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


FM = load_module(ROOT / FM_REL, "g77_256lv_existing_fm_owner")
GL = load_module(ROOT / GL_REL, "g77_256lv_existing_gl_owner")
LG = load_module(ROOT / LG_REL, "g77_256lv_existing_wrong_scope_semantics")


def load_canonical(path: Path) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise LVVerificationError(f"DUPLICATE_JSON_KEY:{key}")
            result[key] = value
        return result

    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise LVVerificationError(f"NONCANONICAL_JSON:{path}")
    return value


def sealed(schema: str, field: str, value: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": schema,
        field: value,
        f"{field}_sha256": hashlib.sha256(canonical_bytes(value)).hexdigest(),
    }


def write_fresh(path: Path, value: dict[str, Any] | str) -> None:
    if path.exists() or path.is_symlink():
        raise LVVerificationError(f"FRESH_ARTIFACT_COLLISION:{path}")
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if isinstance(value, str):
        path.write_text(value, encoding="utf-8")
    else:
        path.write_bytes(canonical_bytes(value))


def zero_counters() -> dict[str, int]:
    return {
        "HUMAN_AUTHORITY_SOURCE_COUNT": 0,
        "AUTHORITY_CREATION_COUNT": 0,
        "AUTHORITY_CONSUMPTION_COUNT": 0,
        "OPERATION_ATTEMPT_COUNT": 0,
        "QEMU_START_COUNT": 0,
        "VM_START_COUNT": 0,
        "P11_ENTRY_COUNT": 0,
        "PROTECTED_INVOCATION_COUNT": 0,
        "PROTECTED_EFFECT_COUNT": 0,
        "RETRY_COUNT": 0,
        "OPERATIONAL_REPLAY_COUNT": 0,
        "REPAIR_RETRY_COUNT": 0,
    }


def authenticate_repository() -> dict[str, str]:
    head = git("rev-parse", "HEAD")
    remote = git("rev-parse", f"refs/remotes/origin/{BRANCH}")
    if (
        ROOT != Path("/home/pisarna/work/sapianta-fl")
        or git("branch", "--show-current") != BRANCH
        or git("rev-parse", f"{ENTRY_HEAD}^{{tree}}") != ENTRY_TREE
        or git("show", "-s", "--format=%s", ENTRY_HEAD) != ENTRY_SUBJECT
        or not is_ancestor(LT_HEAD, ENTRY_HEAD)
        or not is_ancestor(LR_HEAD, ENTRY_HEAD)
        or not is_ancestor(ENTRY_HEAD, head)
        or not is_ancestor(ENTRY_HEAD, remote)
    ):
        raise LVVerificationError("LU_ENTRY_OR_ANCESTRY_AUTHENTICATION_FAILED")
    dirty = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT,
        text=True,
    ).splitlines()
    unexpected = [
        line for line in dirty if not line[3:].startswith(LV_REL.as_posix() + "/")
    ]
    if unexpected:
        raise LVVerificationError(f"UNRELATED_MUTATION:{unexpected}")
    changed = set(filter(None, git("diff", "--name-only", ENTRY_HEAD, "HEAD").splitlines()))
    if any(not path.startswith(LV_REL.as_posix() + "/") for path in changed):
        raise LVVerificationError("PRODUCTION_OR_UNRELATED_MUTATION")
    nested = ROOT / "sapianta_system"
    if (
        git("rev-parse", "HEAD", cwd=nested) != NESTED_HEAD
        or git("rev-parse", "HEAD^{tree}", cwd=nested) != NESTED_TREE
        or git("status", "--porcelain=v1", "--untracked-files=all", cwd=nested)
        or git("branch", "--show-current", cwd=nested)
        or git("rev-parse", f"refs/tags/{NESTED_TAG}^{{}}", cwd=nested) != NESTED_HEAD
    ):
        raise LVVerificationError("NESTED_AUTHORITY_MISMATCH")
    return {
        "entry_head": ENTRY_HEAD,
        "entry_tree": ENTRY_TREE,
        "current_head": head,
        "current_tree": git("rev-parse", "HEAD^{tree}"),
        "remote_head": remote,
    }


def authenticate_sources_and_predecessors() -> None:
    for relative, expected in SOURCE_HASHES.items():
        path = ROOT / relative
        if path.is_symlink() or not path.is_file() or sha256_path(path) != expected:
            raise LVVerificationError(f"SOURCE_IDENTITY_MISMATCH:{relative}")
        committed = subprocess.check_output(
            ["git", "show", f"{ENTRY_HEAD}:{relative.as_posix()}"], cwd=ROOT
        )
        if committed != path.read_bytes():
            raise LVVerificationError(f"SOURCE_NOT_LU_COMMITTED:{relative}")

    lr = load_canonical(ROOT / LR_REL)["reconstruction"]
    if (
        lr["cardinality"] != {
            "authority_consumed_count": 1,
            "authority_created_count": 1,
            "constitutional_cardinality_conflict": False,
            "human_decision_count": 1,
            "operation_attempt_count": 1,
            "retry_count": 0,
        }
        or lr["authority"]["reusable"] is not False
        or lr["operation"]["result"]
        != "INCOMPLETE__NO_POST_RECEIPT_NO_CONTROLLER_RESULT_NO_GUEST_TERMINAL"
        or lr["operation"]["denial_class"] != "UNKNOWN"
        or lr["human_decision"]["object_id"]
        != "G77_256LQ_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_001"
    ):
        raise LVVerificationError("LR_TERMINAL_NONREUSE_FACTS_INVALID")

    # LT/LU terminal evidence predates the compact canonical-envelope pattern.
    # Exact file hashes and LU commit-byte equality above authenticate the source;
    # JSON parsing here reads its deliberately human-oriented presentation form.
    lt = json.loads((ROOT / LT_REL).read_text(encoding="utf-8"))["decision"]
    lu = json.loads((ROOT / LU_DECISION_REL).read_text(encoding="utf-8"))["decision"]
    relation = json.loads((ROOT / LU_RELATION_REL).read_text(encoding="utf-8"))["relation"]
    if (
        lt["CAPABILITY_IMPLEMENTED"] != "YES__GENERATION_LOCAL_HARNESS_ONLY"
        or lt["AUTHORITY_EFFECT"] != "NONE"
        or lt["CONSUMABILITY"] != "NONAUTHORITY"
        or not lt["DUPLICATE_LAUNCH_PREVENTION"].startswith("PROVEN__")
        or not lt["SESSION_INDEPENDENCE_PROVEN"].startswith("YES__")
        or not lt["UNKNOWN_FAIL_CLOSED_PROVEN"].startswith("YES__")
        or lu["INTEGRATION_READINESS"] != "PROVEN"
        or lu["NEW_CAPABILITY_REQUIRED"] != "NO"
        or lu["PRODUCTION_BEHAVIOR_IMPACT"] != "NONE"
        or lu["MINIMUM_LEGAL_NEXT_DELTA"] != "FRESH_PHASE_A_WRONG_SCOPE_REVIEW_OBJECT"
        or relation["new_capability_required"] != "NO"
        or relation["production_route_count"] != "1 -> 1"
    ):
        raise LVVerificationError("LT_LU_READINESS_FACTS_INVALID")

    changed_after_lr = git("diff", "--name-only", LR_HEAD, ENTRY_HEAD).splitlines()
    if any("PHASE_A_REVIEW_OBJECT" in path for path in changed_after_lr):
        raise LVVerificationError("POST_LR_PENDING_REVIEW_OBJECT_ALREADY_EXISTS")
    for identity in (LIFECYCLE_ID, OBJECT_ID, REVIEW_ID, CONTEXT_ID, PRESENTATION_ID):
        found = subprocess.run(
            ["git", "grep", "-F", identity, ENTRY_HEAD],
            cwd=ROOT,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode == 0
        if found:
            raise LVVerificationError(f"FRESH_IDENTITY_COLLISION:{identity}")


def build_review(context: dict[str, Any], readiness_sha256: str) -> dict[str, Any]:
    return {
        "GENERATION": "G77-256LV",
        "GENERATION_ID": GENERATION_ID,
        "LIFECYCLE_ID": LIFECYCLE_ID,
        "OBJECT_ID": OBJECT_ID,
        "REVIEW_OBJECT_ID": REVIEW_ID,
        "CONTEXT_ID": CONTEXT_ID,
        "PRESENTATION_ID": PRESENTATION_ID,
        "VECTOR": "WRONG_SCOPE",
        "PHASE": "A",
        "SEALED_PHASE": "PHASE_A__PREHUMAN__NONOPERATIONAL",
        "ARTIFACT_CLASS": "HUMAN_REVIEW_OBJECT__NONAUTHORITY__NONCONSUMABLE__NONOPERATIONAL",
        "CANONICAL_OPERATION_ID": OPERATION_ID,
        "ATTEMPT_BINDING": {
            "attempt_identity": ATTEMPT_ID,
            "operation_attempt_limit_if_later_authorized": 1,
        },
        "CANONICAL_CONTEXT_BINDING": {
            "context_id": CONTEXT_ID,
            "path": CONTEXT.relative_to(ROOT).as_posix(),
            "context_sha256": context["context_sha256"],
            "whole_file_sha256": sha256_path(CONTEXT),
            "repository_head": ENTRY_HEAD,
            "repository_tree": ENTRY_TREE,
            "preauthority_static_readiness_file_sha256": readiness_sha256,
        },
        "LP_TRANSITION_BINDING": {
            "schema_id": FM.COMMITTED_REVIEW_TRANSITION_SCHEMA,
            "review_identity_R": "DERIVE_FROM_UNIQUE_COMMIT_INTRODUCING_CANONICAL_CONTEXT",
            "current_admission_identity_C": "MUST_EQUAL_FUTURE_OBSERVED_HEAD_TREE",
            "transition_relation_T": "MUST_EQUAL_FM_DETERMINISTIC_EXACT_PAIR_AND_FULL_DELTA",
            "ancestry_sufficient": False,
            "branch_name_sufficient": False,
            "coherent_copy_sufficient": False,
            "transition_is_authority": False,
            "transition_consumable": False,
            "fresh_human_decision_required": True,
        },
        "AUTHORIZED_SCOPE": AUTHORIZED_SCOPE,
        "PRESENTED_SCOPE": PRESENTED_SCOPE,
        "ISOLATED_MISMATCH": {
            "field": "authority_scope",
            "expected": AUTHORIZED_SCOPE,
            "presented": PRESENTED_SCOPE,
            "independent_semantic_mutation_count": 1,
            "preserved_dimensions": [
                "authority_kind",
                "authority_lifecycle_state",
                "attempt_identity",
                "input_identity",
                "contract_identity",
                "provenance_identity",
                "validity_interval_and_currentness",
                "target_owner_and_revision",
                "caller_identity",
            ],
        },
        "CANDIDATE_HUMAN_ACT_MATERIAL": {
            "artifact_class": "HUMAN_REVIEW_MATERIAL__NONAUTHORITY",
            "is_authority": False,
            "human_actor_identity_state": "ABSENT",
            "human_authority_source_bytes_state": "ABSENT",
            "authority_act_identity_state": "UNMATERIALIZED",
            "payload_digest_state": "UNMATERIALIZED",
            "proposed_authority_scope": PRESENTED_SCOPE,
            "proposed_operation_attempt_limit": 1,
            "proposed_retry_limit": 0,
        },
        "PREDECESSOR_READINESS": {
            "LT_CAPABILITY": "IMPLEMENTED__READINESS_ONLY__NONAUTHORITY",
            "LU_INTEGRATION": "PROVEN__STATIC_ONLY__NONOPERATIONAL",
            "authority_or_permission_transferred": False,
            "acceptance_credit_transferred": False,
        },
        "PREVIOUS_LIFECYCLE": {
            "LQ_OBJECT_ID": "G77_256LQ_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_001",
            "LQ_APPROVAL_REUSED": False,
            "LR_AUTHORITY_ID": "G77_256LR_FRESH_HUMAN_OPERATIONAL_AUTHORITY_001",
            "LR_AUTHORITY_REUSED": False,
            "LR_INVOCATION_REUSED": False,
            "LR_RECEIPT_NAMESPACE_REUSED": False,
            "LR_OPERATION_IDENTITY_REUSED": False,
            "LR_OUTCOME": "UNKNOWN__PRESERVED_WITHOUT_ZERO_ENCODING",
            "state": "HISTORICAL_ONLY__TERMINAL__NONTRANSFERABLE",
        },
        "GOVERNED_RUNTIME_CHECKOUT": {
            "head": RUNTIME_HEAD,
            "tree": RUNTIME_TREE,
            "separate_from_review_and_admission_identity": True,
        },
        "RECEIPT_PARENT_BINDING": {
            "path": context["receipt_parent"],
            "readiness": "PASS__EXISTING_FM_GL_OWNER",
            "receipt_namespace_unused": True,
            "lr_namespace_reused": False,
        },
        "ONE_SHOT_LIMIT": 1,
        "RETRY_LIMIT": 0,
        "AUTHORITY_STATE": "NONE",
        "AUTHORITY_CREATED": "NO",
        "AUTHORITY_CONSUMED": "NO",
        "HUMAN_DECISION_STATE": "PENDING",
        "OPERATION_STATE": "NOT_STARTED",
        "P11_STATE": "NOT_ENTERED",
        "PROTECTED_EFFECT_STATE": "NONE_IN_LV",
        "STATE_COUNTERS": zero_counters(),
        "NOTICES": [
            "THIS OBJECT IS NOT AUTHORIZED",
            "APPROVAL HAS NOT YET BEEN GIVEN",
            "NO OPERATION MAY START FROM THIS GENERATION",
            "LQ APPROVAL AND LR AUTHORITY ARE TERMINAL AND MUST NOT BE REUSED",
            "A FUTURE HUMAN DECISION MUST BIND THIS EXACT LV OBJECT",
            "LT AND LU ARE READINESS EVIDENCE ONLY",
            "INTELLIGENCE != AUTHORITY",
        ],
        "NEXT_ALLOWED_TRANSITION": "INDEPENDENT_HUMAN_REVIEW_AND_DECISION",
        "READINESS": "READY_FOR_HUMAN_DECISION",
    }


def render_presentation(context: dict[str, Any], review: dict[str, Any]) -> str:
    return (
        "G77-256LV WRONG_SCOPE PHASE-A HUMAN REVIEW PRESENTATION\n\n"
        f"PRESENTATION_ID = {PRESENTATION_ID}\n"
        f"LIFECYCLE_ID = {LIFECYCLE_ID}\n"
        f"OBJECT_ID = {OBJECT_ID}\n"
        f"REVIEW_OBJECT_ID = {REVIEW_ID}\n"
        "THIS OBJECT IS NOT AUTHORIZED.\n"
        "APPROVAL HAS NOT YET BEEN GIVEN.\n"
        "NO OPERATION MAY START FROM THIS GENERATION.\n"
        "LQ APPROVAL AND LR AUTHORITY ARE TERMINAL AND NONREUSABLE.\n"
        "LT/LU READINESS IS NOT AUTHORITY OR OPERATIONAL PROOF.\n"
        "A FUTURE HUMAN DECISION MUST BIND THIS EXACT LV OBJECT.\n\n"
        f"REVIEW_OBJECT_PATH = {REVIEW.relative_to(ROOT).as_posix()}\n"
        f"REVIEW_OBJECT_WHOLE_FILE_SHA256 = {sha256_path(REVIEW)}\n"
        f"REVIEW_OBJECT_CANONICAL_INNER_SHA256 = {review['review_object_sha256']}\n"
        f"CANONICAL_CONTEXT_ID = {CONTEXT_ID}\n"
        f"CANONICAL_CONTEXT_PATH = {CONTEXT.relative_to(ROOT).as_posix()}\n"
        f"CANONICAL_CONTEXT_WHOLE_FILE_SHA256 = {sha256_path(CONTEXT)}\n"
        f"CANONICAL_CONTEXT_INNER_SHA256 = {context['context_sha256']}\n"
        f"CURRENT_ADMISSION_HEAD = {ENTRY_HEAD}\n"
        f"CURRENT_ADMISSION_TREE = {ENTRY_TREE}\n"
        f"AUTHORIZED_SCOPE = {AUTHORIZED_SCOPE}\n"
        f"PRESENTED_SCOPE = {PRESENTED_SCOPE}\n"
        "ISOLATED_MISMATCH = authority_scope\n"
        "AUTHORITY_STATE = NONE\n"
        "HUMAN_DECISION_STATE = PENDING\n"
        "OPERATION_STATE = NOT_STARTED\n"
        "RETRY_STATE = 0\n"
        "P11_STATE = NOT_ENTERED\n"
        "PROTECTED_EFFECT_STATE = NONE_IN_LV\n"
        "READINESS = READY_FOR_HUMAN_DECISION\n"
    )


def cross_vector() -> dict[str, str]:
    return {
        "WRONG_ATTEMPT": "EXACT_REUSE_POSSIBLE__PHASE_A_CONTEXT_AND_ONE_SHOT_STRUCTURE",
        "WRONG_INPUT": "SEMANTICALLY_EQUIVALENT__EXACT_BINDING_STRUCTURE",
        "WRONG_CONTRACT": "SEMANTICALLY_EQUIVALENT__EXACT_BINDING_STRUCTURE",
        "WRONG_PROVENANCE": "SEMANTICALLY_EQUIVALENT__EXACT_BINDING_STRUCTURE",
        "WRONG_CALLER": "PARTIAL_REUSE__PRE_ENTRY_FAIL_CLOSED_STRUCTURE",
        "FUTURE": "EXACT_REUSE_POSSIBLE__PRESENTATION_AND_FRESHNESS_STRUCTURE",
        "EXPIRED": "EXACT_REUSE_POSSIBLE__FRESH_LIFECYCLE_STRUCTURE",
        "WRONG_SCOPE": "VECTOR_SPECIFIC__EXACT_SCOPE_PAIR_AND_ISOLATED_MISMATCH",
        "REMAINING_E05_VECTORS": "PARTIAL_REUSE__NO_ACCEPTANCE_AUTHORITY_OR_DECISION_TRANSFER",
    }


def build_reduction(context: dict[str, Any], readiness: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "G77_256LV_SPCE_TERMINAL_REDUCTION_V1",
        "generation": "G77-256LV",
        "terminal": TERMINAL,
        "failure_novelty_and_convergence": {
            "FAILURE_CLASS": "PROOF_GAP",
            "NOVELTY": "FRESH_POST_CONSUMPTION_WRONG_SCOPE_PHASE_A_LIFECYCLE",
            "AFFECTED_INVARIANT": "FRESH_HUMAN_DECISION_MUST_PRECEDE_ANY_NEW_OPERATION_AFTER_CONSUMED_AUTHORITY",
            "PREVIOUS_CLOSEST_EDGE": "LQ_REVIEW_TO_LR_CONSUMED_ONE_SHOT_LIFECYCLE__LT_LU_STATIC_READINESS",
            "SEMANTIC_DIFFERENCE": "FRESH_LV_IDENTITY_BOUND_TO_LU__NO_NEW_PRODUCTION_SEMANTIC",
            "PRODUCTION_BEHAVIOR_IMPACT": "NONE",
            "NEW_CAPABILITY_REQUIRED": "NO",
            "NEW_PROOF_REQUIRED": "AUTHENTICATED_TERMINAL_OPERATIONAL_WRONG_SCOPE_DENIAL_BEFORE_P11",
            "CONVERGENCE_SIGNAL": "FRESH_PHASE_A_LIFECYCLE_CREATED_USING_EXISTING_CERTIFIED_MECHANISMS",
            "REPETITION_PRESSURE": "BOUNDED__FRESHNESS_REQUIRED_BY_CONSUMED_PRIOR_AUTHORITY",
            "VERIFICATION_AMPLIFICATION_RISK": "LOW_TO_BOUNDED",
        },
        "duplicate_assessment": {
            "valid_fresh_pending_post_lr_object_exists": False,
            "basis": "NO_PHASE_A_REVIEW_OBJECT_ADDED_FROM_LR_TERMINAL_THROUGH_LU__LV_IDENTITIES_ABSENT_AT_LU",
            "historical_lq": "TERMINAL__DECISION_USED__AUTHORITY_CONSUMED__NONREUSABLE",
        },
        "spce": {
            "state": "LT_CAPABILITY_AND_LU_STATIC_INTEGRATION_READINESS_PROVEN",
            "problem": "PRIOR_LQ_LR_LIFECYCLE_TERMINAL_AND_CONSUMED__FRESH_REVIEW_REQUIRED",
            "constraints": "PHASE_A_ONLY__ZERO_AUTHORITY_OPERATION_QEMU_VM_P11_RETRY",
            "execution": "ONE_FRESH_SEALED_REVIEW_OBJECT__STOP_AT_HUMAN_DECISION",
        },
        "context": {
            "id": CONTEXT_ID,
            "path": CONTEXT.relative_to(ROOT).as_posix(),
            "context_sha256": context["context_sha256"],
            "whole_file_sha256": sha256_path(CONTEXT),
            "repository_head": ENTRY_HEAD,
            "repository_tree": ENTRY_TREE,
        },
        "review_object": {
            "count": 1,
            "lifecycle_id": LIFECYCLE_ID,
            "object_id": OBJECT_ID,
            "review_object_id": REVIEW_ID,
            "presentation_id": PRESENTATION_ID,
            "path": REVIEW.relative_to(ROOT).as_posix(),
            "whole_file_sha256": sha256_path(REVIEW),
            "canonical_inner_sha256": load_canonical(REVIEW)["review_object_sha256"],
        },
        "readiness": {
            "file_sha256": sha256_path(READINESS),
            "checkpoint_sha256": readiness["checkpoint_sha256"],
            "receipt_parent_ready": True,
            "lp_transition": "NONAUTHORITY__NONCONSUMABLE__DETERMINISTIC_CURRENT_ADMISSION_RECONSTRUCTION",
            "lt": "REFERENCED_AS_READINESS_ONLY",
            "lu": "REFERENCED_AS_STATIC_INTEGRATION_ONLY",
        },
        "scope": {
            "authorized": AUTHORIZED_SCOPE,
            "presented": PRESENTED_SCOPE,
            "isolated_mismatch": "authority_scope",
            "independent_semantic_mutation_count": 1,
        },
        "cross_vector_reuse_assessment": cross_vector(),
        "forward_compatibility": {
            "AMBIGUOUS": "STRONGER",
            "STALE": "STRONGER",
            "REVOKED": "UNCHANGED",
            "SUPERSEDED": "UNCHANGED",
            "WRONG_SCOPE": "STRONGER__FRESH_EXACT_PHASE_A_BINDING__OPERATIONAL_UNSAT",
            "COHERENT_COPY": "STRONGER__LP_CANONICAL_COMMIT_IDENTITY_REQUIRED",
        },
        "architecture": {
            "PRODUCTION_FILES_CHANGED": 0,
            "FM_PRODUCTION_FILES_CHANGED": 0,
            "GN_PRODUCTION_FILES_CHANGED": 0,
            "ER_PRODUCTION_FILES_CHANGED": 0,
            "P11_PRODUCTION_FILES_CHANGED": 0,
            "EX_PRODUCTION_FILES_CHANGED": 0,
            "OWNER_DELTA": 0,
            "ROUTE_COUNT_BEFORE": 1,
            "ROUTE_COUNT_AFTER": 1,
            "REGISTRY_DELTA": 0,
            "CONSTITUTIONAL_CONCEPT_DELTA": 0,
        },
        "e05": {
            "E05_BEFORE": "12/18",
            "LV_E05_CREDIT": 0,
            "E05_AFTER": "12/18",
            "WRONG_SCOPE_STATUS": "UNSAT",
        },
        "ex": {"EX_REUSED": "VERIFIED__17_OF_17", "EX_RECONSTRUCTED": "VERIFIED__0"},
        "operational_counters": zero_counters(),
        "human_boundary": {
            "authority": "NONE",
            "decision": "PENDING",
            "operation": "NOT_STARTED",
            "next": "INDEPENDENT_HUMAN_REVIEW_AND_DECISION_OVER_EXACT_LV_OBJECT",
        },
    }


def build_decision(context: dict[str, Any]) -> dict[str, Any]:
    review = load_canonical(REVIEW)
    return {
        "FAILURE_CLASS": "PROOF_GAP",
        "NOVELTY": "FRESH_POST_CONSUMPTION_WRONG_SCOPE_PHASE_A_LIFECYCLE",
        "FRESH_LIFECYCLE_CREATED": "YES",
        "LIFECYCLE_ID": LIFECYCLE_ID,
        "FRESH_OBJECT_ID": OBJECT_ID,
        "FRESH_REVIEW_OBJECT_ID": REVIEW_ID,
        "FRESH_OBJECT_WHOLE_SHA256": sha256_path(REVIEW),
        "CANONICAL_INNER_SHA256": review["review_object_sha256"],
        "CONTEXT_SHA256": context["context_sha256"],
        "CONTEXT_WHOLE_SHA256": sha256_path(CONTEXT),
        "PRESENTATION_ID": PRESENTATION_ID,
        "PRESENTATION_SHA256": sha256_path(PRESENTATION),
        "CURRENT_ADMISSION_BINDING": f"{ENTRY_HEAD}/{ENTRY_TREE}",
        "AUTHORIZED_SCOPE": AUTHORIZED_SCOPE,
        "PRESENTED_SCOPE": PRESENTED_SCOPE,
        "ISOLATED_MISMATCH": "authority_scope",
        "HUMAN_DECISION_STATE": "PENDING",
        "AUTHORITY_STATE": "NONE",
        "LQ_APPROVAL_REUSED": "NO",
        "LR_AUTHORITY_REUSED": "NO",
        "OPERATION_STATE": "NOT_STARTED",
        "P11_STATE": "NOT_ENTERED",
        "PROTECTED_EFFECT_STATE": "NONE_IN_LV",
        "NEW_CAPABILITY_REQUIRED": "NO",
        "PRODUCTION_BEHAVIOR_IMPACT": "NONE",
        "LAST_VERIFIED_PHASE_A_EDGE": "FRESH_EXACT_WRONG_SCOPE_REVIEW_OBJECT_SEALED_AND_BOUND_TO_CURRENT_ADMISSION",
        "FIRST_BROKEN_PHASE_A_EDGE": "NONE__READY_FOR_HUMAN_DECISION",
        "LAST_VERIFIED_OPERATIONAL_EDGE": "LR_VM_BOOT_DURABLY_EVIDENCED",
        "FIRST_UNVERIFIED_OPERATIONAL_EDGE": "VM_BOOT_TO_GOVERNED_GUEST_EXECUTION",
        "MINIMUM_MISSING_CAPABILITY": "NONE",
        "MINIMUM_MISSING_PROOF": "AUTHENTICATED_TERMINAL_OPERATIONAL_WRONG_SCOPE_DENIAL_BEFORE_P11",
        "MINIMUM_LEGAL_NEXT_DELTA": "INDEPENDENT_HUMAN_REVIEW_AND_DECISION_OVER_EXACT_LV_OBJECT",
        "OPERATIONAL_RETRY_AUTHORIZED": "NO",
        "TERMINAL": TERMINAL,
    }


def materialize() -> dict[str, Any]:
    repository = authenticate_repository()
    authenticate_sources_and_predecessors()
    if repository["current_head"] != ENTRY_HEAD or repository["remote_head"] != ENTRY_HEAD:
        raise LVVerificationError("MATERIALIZATION_REQUIRES_EXACT_LU_ENTRY")
    targets = (CONTEXT, READINESS, REVIEW, PRESENTATION, REDUCTION, DECISION)
    if any(path.exists() or path.is_symlink() for path in targets):
        raise LVVerificationError("LV_ONE_SHOT_NAMESPACE_NOT_FRESH")
    if (LV / "operation_state").exists() or TRANSIENT.exists() or TRANSIENT.is_symlink():
        raise LVVerificationError("LV_MATERIALIZATION_NAMESPACE_NOT_FRESH")

    context = FM.build_operation_context(
        repository_root=ROOT,
        repository_head=ENTRY_HEAD,
        repository_tree=ENTRY_TREE,
        generation_identity=GENERATION_ID,
        operation_identity=OPERATION_ID,
        identity_namespace_prefix=PREFIX,
        operation_evidence_root=LV / "operation_state",
        transient_root=TRANSIENT,
        candidate_source_path=CANDIDATE_REL,
    )
    write_fresh(CONTEXT, context)
    materialization = FM.materialize_operation_state(
        repository_root=ROOT,
        context=context,
        context_source_path=CONTEXT,
        candidate_source_path=CANDIDATE_REL,
    )
    observations = FM.observe_context_assets(ROOT, context, CANDIDATE_REL)
    static = FM.authority_free_static_readiness(
        repository_root=ROOT,
        context=context,
        observed_head=ENTRY_HEAD,
        observed_tree=ENTRY_TREE,
        repository_clean=True,
        observed_asset_sha256=observations,
        candidate_source_path=CANDIDATE_REL,
    )
    receipt_claim = GL.prepare_and_observe_receipt_parent(ROOT, context)
    receipt_checkpoint = GL.reduce_preauthorization_checkpoint(ROOT, context, receipt_claim)
    readiness_inner = {
        "schema_id": "G77_256LV_PREAUTHORITY_STATIC_READINESS_V1",
        "artifact_class": "AUTHORITY_FREE_STATIC_OBSERVATION__NONOPERATIONAL",
        "lifecycle_id": LIFECYCLE_ID,
        "generation_identity": GENERATION_ID,
        "operation_identity": OPERATION_ID,
        "context_id": CONTEXT_ID,
        "context_sha256": context["context_sha256"],
        "context_file_sha256": sha256_path(CONTEXT),
        "entry_head": ENTRY_HEAD,
        "entry_tree": ENTRY_TREE,
        "materialization": materialization,
        "static_readiness": static,
        "receipt_parent_claim": receipt_claim,
        "receipt_parent_checkpoint": receipt_checkpoint,
        "lt_readiness": "REFERENCED__NONAUTHORITY__NONOPERATIONAL",
        "lu_readiness": "REFERENCED__STATIC_PROOF_ONLY__NO_PERMISSION",
        "authority_state": "NONE",
        "human_decision_state": "PENDING",
        "operation_state": "NOT_STARTED",
        "operational_counters": zero_counters(),
    }
    readiness = sealed(
        "G77_256LV_PREAUTHORITY_STATIC_READINESS_ENVELOPE_V1",
        "checkpoint",
        readiness_inner,
    )
    write_fresh(READINESS, readiness)
    review = sealed(
        "G77_256LV_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_ENVELOPE_V1",
        "review_object",
        build_review(context, sha256_path(READINESS)),
    )
    write_fresh(REVIEW, review)
    write_fresh(PRESENTATION, render_presentation(context, review))
    write_fresh(
        REDUCTION,
        sealed(
            "G77_256LV_SPCE_TERMINAL_REDUCTION_ENVELOPE_V1",
            "reduction",
            build_reduction(context, readiness),
        ),
    )
    write_fresh(
        DECISION,
        sealed(
            "G77_256LV_TERMINAL_DECISION_ENVELOPE_V1",
            "decision",
            build_decision(context),
        ),
    )
    return verify()


def authenticate_transition(context: dict[str, Any], repository: dict[str, str]) -> dict[str, Any]:
    relative_context = CONTEXT.relative_to(ROOT).as_posix()
    if FM._committed_review_context_path(ROOT, context) != relative_context:
        raise LVVerificationError("LP_CANONICAL_REVIEW_PATH_MISMATCH")
    current_head = repository["current_head"]
    current_tree = repository["current_tree"]
    committed = subprocess.run(
        ["git", "cat-file", "-e", f"{current_head}:{relative_context}"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0
    if not committed:
        relation = FM.authenticate_review_to_current_admission(
            repository_root=ROOT,
            context=context,
            observed_head=current_head,
            observed_tree=current_tree,
        )
        if current_head != ENTRY_HEAD or relation["repository_identity_relation"] != "EXACT_SAME_HEAD_TREE":
            raise LVVerificationError("UNCOMMITTED_REVIEW_STATE_INVALID")
        return {
            "state": "PENDING_IMMUTABLE_COMMIT_R",
            "review_identity_R": "PENDING_COMMIT",
            "current_admission_identity_C": f"{current_head}/{current_tree}",
            "transition_proof_state": "NOT_CREATED",
            "transition_is_authority": False,
            "transition_consumable": False,
        }
    introductions = git(
        "log", "--format=%H", "--diff-filter=A", current_head, "--", relative_context
    ).splitlines()
    if len(introductions) != 1:
        raise LVVerificationError("LV_REVIEW_INTRODUCTION_MISSING_OR_AMBIGUOUS")
    review_head = introductions[0]
    review_tree = git("rev-parse", f"{review_head}^{{tree}}")
    if (
        not is_ancestor(ENTRY_HEAD, review_head)
        or not is_ancestor(review_head, current_head)
        or subprocess.check_output(
            ["git", "show", f"{review_head}:{relative_context}"], cwd=ROOT
        ) != CONTEXT.read_bytes()
    ):
        raise LVVerificationError("LV_COMMITTED_REVIEW_IDENTITY_INVALID")
    if review_head == current_head:
        return {
            "state": "IMMUTABLE_REVIEW_IDENTITY_R_COMMITTED__SUCCESSOR_C_REQUIRED",
            "review_identity_R": f"{review_head}/{review_tree}",
            "current_admission_identity_C": f"{current_head}/{current_tree}",
            "transition_proof_state": "NOT_CREATED__NO_SUCCESSOR_DELTA",
            "transition_is_authority": False,
            "transition_consumable": False,
        }
    proof = FM.build_committed_review_transition(
        repository_root=ROOT,
        context=context,
        current_admission_head=current_head,
        current_admission_tree=current_tree,
    )
    relation = FM.authenticate_review_to_current_admission(
        repository_root=ROOT,
        context=context,
        observed_head=current_head,
        observed_tree=current_tree,
        committed_review_transitions=[proof],
    )
    if (
        proof["review_object_head"] != review_head
        or proof["transition_is_authority"] is not False
        or proof["transition_consumable"] is not False
        or relation["repository_identity_relation"]
        != "EXACT_COMMITTED_REVIEW_TO_CURRENT_ADMISSION_TRANSITION"
    ):
        raise LVVerificationError("LP_TRANSITION_AUTHENTICATION_FAILED")
    return {
        "state": "LP_EXACT_TRANSITION_VERIFIED",
        "review_identity_R": f"{review_head}/{review_tree}",
        "current_admission_identity_C": f"{current_head}/{current_tree}",
        "transition_proof_state": "DERIVED_IN_MEMORY__NONAUTHORITY__NONCONSUMABLE",
        "transition_sha256": proof["transition_sha256"],
        "transition_is_authority": False,
        "transition_consumable": False,
    }


def verify() -> dict[str, Any]:
    repository = authenticate_repository()
    authenticate_sources_and_predecessors()
    context = load_canonical(CONTEXT)
    FM.fresh_context.validate_context(context, repository_root=ROOT)
    if (
        context["generation_identity"] != GENERATION_ID
        or context["operation_identity"] != OPERATION_ID
        or context["repository_head"] != ENTRY_HEAD
        or context["repository_tree"] != ENTRY_TREE
        or context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["head"] != RUNTIME_HEAD
        or context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["tree"] != RUNTIME_TREE
    ):
        raise LVVerificationError("CANONICAL_CONTEXT_BINDING_MISMATCH")
    readiness = load_canonical(READINESS)
    checkpoint = readiness.get("checkpoint")
    if (
        not isinstance(checkpoint, dict)
        or readiness.get("checkpoint_sha256") != hashlib.sha256(canonical_bytes(checkpoint)).hexdigest()
        or checkpoint.get("authority_state") != "NONE"
        or checkpoint.get("human_decision_state") != "PENDING"
        or checkpoint.get("operation_state") != "NOT_STARTED"
        or any(checkpoint.get("operational_counters", {}).values())
    ):
        raise LVVerificationError("STATIC_READINESS_SEAL_OR_BOUNDARY_INVALID")
    GL.validate_bound_observation(ROOT, context, checkpoint["receipt_parent_claim"])

    review_envelope = load_canonical(REVIEW)
    review = review_envelope.get("review_object")
    if (
        review_envelope.get("schema_id")
        != "G77_256LV_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_ENVELOPE_V1"
        or not isinstance(review, dict)
        or review_envelope.get("review_object_sha256")
        != hashlib.sha256(canonical_bytes(review)).hexdigest()
        or len(list(LV.glob("*PHASE_A_REVIEW_OBJECT*.json"))) != 1
    ):
        raise LVVerificationError("REVIEW_OBJECT_CARDINALITY_OR_SEAL_INVALID")
    required = {
        "GENERATION": "G77-256LV",
        "GENERATION_ID": GENERATION_ID,
        "LIFECYCLE_ID": LIFECYCLE_ID,
        "OBJECT_ID": OBJECT_ID,
        "REVIEW_OBJECT_ID": REVIEW_ID,
        "CONTEXT_ID": CONTEXT_ID,
        "PRESENTATION_ID": PRESENTATION_ID,
        "AUTHORIZED_SCOPE": AUTHORIZED_SCOPE,
        "PRESENTED_SCOPE": PRESENTED_SCOPE,
        "AUTHORITY_STATE": "NONE",
        "HUMAN_DECISION_STATE": "PENDING",
        "OPERATION_STATE": "NOT_STARTED",
        "P11_STATE": "NOT_ENTERED",
        "PROTECTED_EFFECT_STATE": "NONE_IN_LV",
        "RETRY_LIMIT": 0,
        "READINESS": "READY_FOR_HUMAN_DECISION",
    }
    if any(review.get(key) != expected for key, expected in required.items()):
        raise LVVerificationError("REVIEW_OBJECT_REQUIRED_FIELD_MISMATCH")
    binding = review.get("CANONICAL_CONTEXT_BINDING", {})
    if binding != {
        "context_id": CONTEXT_ID,
        "path": CONTEXT.relative_to(ROOT).as_posix(),
        "context_sha256": context["context_sha256"],
        "whole_file_sha256": sha256_path(CONTEXT),
        "repository_head": ENTRY_HEAD,
        "repository_tree": ENTRY_TREE,
        "preauthority_static_readiness_file_sha256": sha256_path(READINESS),
    }:
        raise LVVerificationError("REVIEW_TO_CONTEXT_BINDING_MISMATCH")
    mismatch = review.get("ISOLATED_MISMATCH", {})
    model = LG.authenticate_wrong_scope_semantics(ROOT)
    if (
        mismatch.get("field") != "authority_scope"
        or mismatch.get("expected") != AUTHORIZED_SCOPE
        or mismatch.get("presented") != PRESENTED_SCOPE
        or mismatch.get("independent_semantic_mutation_count") != 1
        or model.get("independent_semantic_mutation_count") != 1
        or model["baseline"]["authority_scope"] != AUTHORIZED_SCOPE
        or model["presented"]["authority_scope"] != PRESENTED_SCOPE
    ):
        raise LVVerificationError("WRONG_SCOPE_NOT_EXACTLY_ONE_MISMATCH")
    candidate = review.get("CANDIDATE_HUMAN_ACT_MATERIAL", {})
    previous = review.get("PREVIOUS_LIFECYCLE", {})
    if (
        candidate.get("is_authority") is not False
        or candidate.get("human_actor_identity_state") != "ABSENT"
        or candidate.get("human_authority_source_bytes_state") != "ABSENT"
        or previous.get("LQ_APPROVAL_REUSED") is not False
        or previous.get("LR_AUTHORITY_REUSED") is not False
        or previous.get("LR_INVOCATION_REUSED") is not False
        or previous.get("LR_RECEIPT_NAMESPACE_REUSED") is not False
        or previous.get("LR_OPERATION_IDENTITY_REUSED") is not False
        or not review.get("STATE_COUNTERS")
        or any(review["STATE_COUNTERS"].values())
    ):
        raise LVVerificationError("AUTHORITY_OPERATION_OR_PREDECESSOR_BOUNDARY_INVALID")
    if PRESENTATION.read_text(encoding="utf-8") != render_presentation(context, review_envelope):
        raise LVVerificationError("HUMAN_PRESENTATION_BINDING_MISMATCH")

    forbidden = (
        "*HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE*",
        "*FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF*",
        "*AUTHORITY_VALIDATION_AND_CONSUMPTION*",
        "*OPERATIONAL_INVOCATION_ATTEMPT*",
        "*SERIAL_CONSOLE*",
        "*POST_EXECUTED_QEMU_ARGV_RECEIPT*",
    )
    if any(list(LV.rglob(pattern)) for pattern in forbidden):
        raise LVVerificationError("AUTHORITY_OR_OPERATION_ARTIFACT_PRESENT")
    reduction = load_canonical(REDUCTION)
    if (
        reduction.get("reduction_sha256")
        != hashlib.sha256(canonical_bytes(reduction.get("reduction"))).hexdigest()
        or reduction.get("reduction") != build_reduction(context, readiness)
    ):
        raise LVVerificationError("SPCE_REDUCTION_INVALID")
    decision = load_canonical(DECISION)
    if (
        decision.get("decision_sha256")
        != hashlib.sha256(canonical_bytes(decision.get("decision"))).hexdigest()
        or decision.get("decision") != build_decision(context)
    ):
        raise LVVerificationError("TERMINAL_DECISION_INVALID")
    transition = authenticate_transition(context, repository)
    return {
        "terminal": TERMINAL,
        "repository": repository,
        "lifecycle_id": LIFECYCLE_ID,
        "object_id": OBJECT_ID,
        "review_object_id": REVIEW_ID,
        "review_object_whole_sha256": sha256_path(REVIEW),
        "canonical_inner_sha256": review_envelope["review_object_sha256"],
        "context_sha256": context["context_sha256"],
        "context_whole_sha256": sha256_path(CONTEXT),
        "presentation_sha256": sha256_path(PRESENTATION),
        "transition": transition,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--materialize", action="store_true")
    arguments = parser.parse_args()
    result = materialize() if arguments.materialize else verify()
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
