#!/usr/bin/env python3
"""Materialize once, then verify, the authority-free G77-256LQ Phase A.

The materialization path reuses existing FM/GL owners.  It creates no Human
authority, invokes no operational launcher, writes no execution receipt, and
starts no QEMU, VM, P11 entry, protected invocation, or protected effect.
The default path is read-only.
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
ENTRY_HEAD = "7e6b281e861ae6e7572c3eea9f8be2ceca470b8f"
ENTRY_TREE = "568b04fcb9ead818e0869dfce7ccf0d6649fb75a"
ENTRY_SUBJECT = "G77-256LP record transition capability terminal"
LP_IMPLEMENTATION = "f2674040ef305b1c4ae53f7f0be9894368cdd7a7"
LO_HEAD = "541d48dd6f859ac8dd79ae4dcae57675f6cf3a79"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
RUNTIME_HEAD = "f7acd5feb3dec686ca4e2cd359b63e232f6c5fbe"
RUNTIME_TREE = "968704d8915edf6d524a8a7705591788d8333bdd"
EXPECTED_SCOPE = "P11_DA_ONE_BOUNDED_OPERATIONAL_ATTEMPT_V1"
PRESENTED_SCOPE = "P11_DA_DIFFERENT_OPERATIONAL_SCOPE_V1"
GENERATION = "G77_256LQ_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_SCOPE_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256LQ_E05_WRONG_SCOPE_DENIAL_BEFORE_P11_ENTRY_001"
ATTEMPT = "G77_256LQ_E05_AUTHORIZED_ATTEMPT_001"
REVIEW_ID = "G77_256LQ_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_001"
PREFIX = "G77_256LQ"
TERMINAL = (
    "A__G77_256LQ_WRONG_SCOPE_FRESH_PHASE_A_REVIEW_OBJECT_SEALED__"
    "LP_TRANSITION_COMPATIBLE__ZERO_AUTHORITY__ZERO_OPERATION__"
    "READY_FOR_HUMAN_DECISION"
)

LQ_REL = Path(
    ".github/governance/evidence/"
    "g77_256lq_wrong_scope_fresh_phase_a_review_object_v1"
)
LQ = ROOT / LQ_REL
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
LP_REDUCTION_REL = Path(
    ".github/governance/evidence/g77_256lp_committed_review_transition_v1/"
    "G77_256LP_SPCE_TERMINAL_REDUCTION_V1.json"
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
    LP_REDUCTION_REL: "fee1e1bdf2bf8de547135b05be09cf8b987ba2786a34642524a291a74470918b",
    EX_REL: "91c477171147c56516c0f473ab887c12173c4bab225f2733c274b32467824b2f",
    P11_REL: "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5",
}

CONTEXT = LQ / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
READINESS = LQ / "G77_256LQ_PREAUTHORITY_STATIC_READINESS_V1.json"
REVIEW = LQ / "G77_256LQ_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_V1.json"
PRESENTATION = LQ / "G77_256LQ_HUMAN_DECISION_PRESENTATION_V1.txt"
REDUCTION = LQ / "G77_256LQ_SPCE_TERMINAL_REDUCTION_V1.json"
REPORT = LQ / "G77_256LQ_G48_IMPLEMENTATION_REPORT_V1.md"
TRANSIENT = Path("/tmp/g77_256lq_wrong_scope_fresh_phase_a_review_object_v1")


class LQVerificationError(RuntimeError):
    """One deterministic fail-closed LQ verification failure."""


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
        raise LQVerificationError(f"MODULE_LOAD_FAILED:{name}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


FM = load_module(ROOT / FM_REL, "g77_256lq_existing_fm_owner")
GL = load_module(ROOT / GL_REL, "g77_256lq_existing_gl_owner")
LG = load_module(ROOT / LG_REL, "g77_256lq_existing_wrong_scope_semantics")


def load_canonical(path: Path) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise LQVerificationError(f"DUPLICATE_JSON_KEY:{key}")
            result[key] = value
        return result

    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise LQVerificationError(f"NONCANONICAL_JSON:{path}")
    return value


def sealed(schema: str, field: str, value: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": schema,
        field: value,
        f"{field}_sha256": hashlib.sha256(canonical_bytes(value)).hexdigest(),
    }


def write_fresh(path: Path, value: dict[str, Any] | str) -> None:
    if path.exists() or path.is_symlink():
        raise LQVerificationError(f"FRESH_ARTIFACT_COLLISION:{path}")
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
        or not is_ancestor(LP_IMPLEMENTATION, ENTRY_HEAD)
        or not is_ancestor(LO_HEAD, ENTRY_HEAD)
        or not is_ancestor(ENTRY_HEAD, head)
        or not is_ancestor(ENTRY_HEAD, remote)
    ):
        raise LQVerificationError("LP_ENTRY_OR_SUCCESSOR_AUTHENTICATION_FAILED")
    dirty = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT,
        text=True,
    ).splitlines()
    unexpected = [
        line
        for line in dirty
        if not line[3:].startswith(LQ_REL.as_posix() + "/")
    ]
    if unexpected:
        raise LQVerificationError(f"UNRELATED_MUTATION:{unexpected}")
    changed = set(
        filter(None, git("diff", "--name-only", ENTRY_HEAD, "HEAD").splitlines())
    )
    if any(not path.startswith(LQ_REL.as_posix() + "/") for path in changed):
        raise LQVerificationError("PRODUCTION_OR_UNRELATED_MUTATION")
    nested = ROOT / "sapianta_system"
    if (
        git("rev-parse", "HEAD", cwd=nested) != NESTED_HEAD
        or git("rev-parse", "HEAD^{tree}", cwd=nested) != NESTED_TREE
        or git("status", "--porcelain=v1", "--untracked-files=all", cwd=nested)
        or git("branch", "--show-current", cwd=nested)
        or git("rev-parse", f"refs/tags/{NESTED_TAG}^{{}}", cwd=nested)
        != NESTED_HEAD
    ):
        raise LQVerificationError("NESTED_AUTHORITY_MISMATCH")
    return {
        "entry_head": ENTRY_HEAD,
        "entry_tree": ENTRY_TREE,
        "current_head": head,
        "current_tree": git("rev-parse", "HEAD^{tree}"),
        "remote_head": remote,
    }


def authenticate_sources() -> None:
    for relative, expected in SOURCE_HASHES.items():
        path = ROOT / relative
        if path.is_symlink() or not path.is_file() or sha256_path(path) != expected:
            raise LQVerificationError(f"SOURCE_IDENTITY_MISMATCH:{relative}")
        committed = subprocess.check_output(
            ["git", "show", f"{ENTRY_HEAD}:{relative.as_posix()}"], cwd=ROOT
        )
        if committed != path.read_bytes():
            raise LQVerificationError(f"SOURCE_NOT_LP_COMMITTED:{relative}")


def build_review(context: dict[str, Any], readiness_sha256: str) -> dict[str, Any]:
    return {
        "GENERATION": "G77-256LQ",
        "GENERATION_ID": GENERATION,
        "VECTOR": "WRONG_SCOPE",
        "PHASE": "A",
        "SEALED_PHASE": "PHASE_A__PREHUMAN__NONOPERATIONAL",
        "REVIEW_OBJECT_ID": REVIEW_ID,
        "CANONICAL_OPERATION_ID": OPERATION,
        "ATTEMPT_BINDING": {
            "attempt_identity": ATTEMPT,
            "operation_attempt_limit": 1,
        },
        "CANONICAL_CONTEXT_BINDING": {
            "path": CONTEXT.relative_to(ROOT).as_posix(),
            "context_sha256": context["context_sha256"],
            "whole_file_sha256": sha256_path(CONTEXT),
            "repository_head": context["repository_head"],
            "repository_tree": context["repository_tree"],
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
        "AUTHORIZED_SCOPE": EXPECTED_SCOPE,
        "PRESENTED_SCOPE": PRESENTED_SCOPE,
        "ISOLATED_MISMATCH": {
            "field": "authority_scope",
            "expected": EXPECTED_SCOPE,
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
        "GOVERNED_RUNTIME_CHECKOUT": {
            "head": RUNTIME_HEAD,
            "tree": RUNTIME_TREE,
            "separate_from_review_and_admission_identity": True,
        },
        "RECEIPT_PARENT_BINDING": {
            "path": context["receipt_parent"],
            "readiness": "PASS__EXISTING_FM_GL_OWNER",
            "receipt_namespace_unused": True,
        },
        "ONE_SHOT_LIMIT": 1,
        "RETRY_LIMIT": 0,
        "AUTHORITY": "NONE",
        "AUTHORITY_CREATED": "NO",
        "AUTHORITY_CONSUMED": "NO",
        "OPERATION_STATE": "NOT_STARTED",
        "P11_STATE": "NOT_ENTERED",
        "PROTECTED_EFFECT": "NONE",
        "HUMAN_DECISION_STATE": "PENDING",
        "READINESS": "READY_FOR_HUMAN_DECISION",
        "PREVIOUS_LIFECYCLE": {
            "LM_OBJECT_REUSED": False,
            "LM_OR_LN_AUTHORITY_REUSED": False,
            "OLD_APPROVAL_INHERITED": False,
            "state": "HISTORICAL_ONLY__TERMINAL__NONTRANSFERABLE",
        },
        "STATE_COUNTERS": zero_counters(),
        "NOTICES": [
            "THIS OBJECT IS NOT AUTHORIZED",
            "APPROVAL HAS NOT YET BEEN GIVEN",
            "NO OPERATION MAY START FROM THIS GENERATION",
            "LM AND LN ARE HISTORICAL AND MUST NOT BE RESURRECTED",
            "A FRESH HUMAN DECISION MUST BIND THIS EXACT OBJECT",
            "INTELLIGENCE != AUTHORITY",
        ],
        "NEXT_ALLOWED_TRANSITION": "INDEPENDENT_HUMAN_REVIEW_AND_DECISION",
    }


def render_presentation(
    context: dict[str, Any], review: dict[str, Any]
) -> str:
    return (
        "G77-256LQ WRONG_SCOPE PHASE-A HUMAN REVIEW PRESENTATION\n\n"
        "THIS OBJECT IS NOT AUTHORIZED.\n"
        "APPROVAL HAS NOT YET BEEN GIVEN.\n"
        "NO OPERATION MAY START FROM THIS GENERATION.\n"
        "LM AND LN ARE HISTORICAL AND MUST NOT BE RESURRECTED.\n"
        "A FUTURE HUMAN DECISION MUST BIND THIS EXACT LQ OBJECT.\n\n"
        f"REVIEW_OBJECT_ID = {REVIEW_ID}\n"
        f"REVIEW_OBJECT_PATH = {REVIEW.relative_to(ROOT).as_posix()}\n"
        f"REVIEW_OBJECT_WHOLE_FILE_SHA256 = {sha256_path(REVIEW)}\n"
        f"REVIEW_OBJECT_CANONICAL_INNER_SHA256 = {review['review_object_sha256']}\n"
        f"CANONICAL_CONTEXT_PATH = {CONTEXT.relative_to(ROOT).as_posix()}\n"
        f"CANONICAL_CONTEXT_WHOLE_FILE_SHA256 = {sha256_path(CONTEXT)}\n"
        f"CANONICAL_CONTEXT_INNER_SHA256 = {context['context_sha256']}\n"
        f"AUTHORIZED_SCOPE = {EXPECTED_SCOPE}\n"
        f"PRESENTED_SCOPE = {PRESENTED_SCOPE}\n"
        "ISOLATED_MISMATCH = authority_scope\n"
        "ONE_SHOT_LIMIT = 1\nRETRY_LIMIT = 0\n"
        "AUTHORITY = NONE\nAUTHORITY_CREATED = NO\nAUTHORITY_CONSUMED = NO\n"
        "OPERATION_STATE = NOT_STARTED\nP11_STATE = NOT_ENTERED\n"
        "PROTECTED_EFFECT = NONE\nHUMAN_DECISION_STATE = PENDING\n"
        "READINESS = READY_FOR_HUMAN_DECISION\n"
    )


def cross_vector() -> list[dict[str, str]]:
    return [
        {
            "vector": vector,
            "reuse": reuse,
            "authority_transfer": "NO",
            "proof_transfer": "NO",
            "e05_credit_transfer": "NO",
        }
        for vector, reuse in (
            ("WRONG_ATTEMPT", "FM_ONE_SHOT_AND_RECEIPT_BINDINGS"),
            ("WRONG_INPUT", "FM_CONTEXT_AND_EXACT_ADMISSION"),
            ("WRONG_CONTRACT", "FM_CONTEXT_AND_EXACT_ADMISSION"),
            ("WRONG_PROVENANCE", "FM_CONTEXT_AND_EXACT_ADMISSION"),
            ("WRONG_CALLER", "PRE_ENTRY_FAIL_CLOSED_PRECEDENT"),
            ("FUTURE", "FM_TEMPORAL_AND_PRESENTATION_PRECEDENT"),
            ("EXPIRED", "FM_TEMPORAL_AND_PRESENTATION_PRECEDENT"),
        )
    ]


def build_reduction(context: dict[str, Any], readiness: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "G77_256LQ_SPCE_TERMINAL_REDUCTION_V1",
        "generation": "G77-256LQ",
        "vector": "WRONG_SCOPE",
        "terminal": TERMINAL,
        "failure_novelty_and_convergence_check": {
            "FAILURE_CLASS": "PROOF_GAP",
            "NOVELTY": "FRESH_POST_LP_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT",
            "AFFECTED_INVARIANT": "EXACT_HUMAN_REVIEW_OBJECT_AND_FRESH_DECISION_MUST_PRECEDE_ANY_WRONG_SCOPE_OPERATION",
            "PREVIOUS_CLOSEST_EDGE": "G77_256LP_STATIC_COMMITTED_REVIEW_TO_CURRENT_ADMISSION_TRANSITION",
            "SEMANTIC_DIFFERENCE": "ONE_FRESH_LQ_LIFECYCLE_INSTANCE__NO_NEW_PRODUCTION_SEMANTIC",
            "PRODUCTION_BEHAVIOR_IMPACT": "NONE",
            "NEW_CAPABILITY_REQUIRED": "NO",
            "NEW_PROOF_REQUIRED": "FRESH_PHASE_A_OBJECT_NOW__OPERATIONAL_WRONG_SCOPE_DENIAL_LATER",
            "CONVERGENCE_SIGNAL": "LP_CAPABILITY_REUSED__ONE_FRESH_OBJECT__ONE_HUMAN_BOUNDARY",
            "REPETITION_PRESSURE": "LOW__LM_LN_NOT_REUSED",
            "VERIFICATION_AMPLIFICATION_RISK": "BOUNDED__NO_DUPLICATE_OWNER_ROUTE_OR_TRANSITION",
        },
        "spce": {
            "state": "LP_EXACT_TRANSITION_CAPABILITY_AUTHENTICATED",
            "problem": "NO_FRESH_POST_LP_WRONG_SCOPE_HUMAN_REVIEW_OBJECT",
            "constraints": "FRESH_AUTHORITY_FREE_SINGLE_MISMATCH_ZERO_PRODUCTION_AND_OPERATION",
            "execution": "MATERIALIZE_VALIDATE_SEAL_COMMIT_PUSH_THEN_STOP_AT_HUMAN_DECISION",
        },
        "context": {
            "path": CONTEXT.relative_to(ROOT).as_posix(),
            "context_sha256": context["context_sha256"],
            "whole_file_sha256": sha256_path(CONTEXT),
            "repository_head": ENTRY_HEAD,
            "repository_tree": ENTRY_TREE,
        },
        "review_object": {
            "count": 1,
            "id": REVIEW_ID,
            "path": REVIEW.relative_to(ROOT).as_posix(),
            "whole_file_sha256": sha256_path(REVIEW),
            "canonical_inner_sha256": load_canonical(REVIEW)["review_object_sha256"],
        },
        "readiness": {
            "file_sha256": sha256_path(READINESS),
            "checkpoint_sha256": readiness["checkpoint_sha256"],
            "receipt_parent_ready": True,
            "lp_transition_compatibility": "PENDING_IMMUTABLE_COMMIT_R__STATIC_MODEL_AUTHENTICATED",
        },
        "scope": {
            "authorized": EXPECTED_SCOPE,
            "presented": PRESENTED_SCOPE,
            "isolated_mismatch": "authority_scope",
            "independent_semantic_mutation_count": 1,
        },
        "cross_vector_reuse_assessment": cross_vector(),
        "forward_compatibility": {
            "AMBIGUOUS": "UNCHANGED",
            "STALE": "STRONGER__FRESH_IDENTITY_AND_NO_ANCESTRY_AUTHORITY",
            "REVOKED": "UNCHANGED",
            "SUPERSEDED": "UNCHANGED",
            "WRONG_SCOPE": "STRONGER_STATIC_BINDING_ONLY__OPERATIONAL_UNSAT",
            "COHERENT_COPY": "STRONGER__LP_CANONICAL_PATH_IDENTITY_BOUND",
        },
        "architecture": {
            "PRODUCTION_MUTATION": 0,
            "FM_MUTATION": 0,
            "GN_MUTATION": 0,
            "P11_MUTATION": 0,
            "ER_MUTATION": 0,
            "EX_MUTATION": 0,
            "REGISTRY_DELTA": 0,
            "OWNER_DELTA": 0,
            "ROUTE_DELTA": 0,
            "NEW_CONSTITUTIONAL_CONCEPT": 0,
            "ROUTE_COUNT_BEFORE": 1,
            "ROUTE_COUNT_AFTER": 1,
        },
        "reuse_impact_assessment": {
            "existing_certified_capabilities_reused": "FM_GL_LG_LK_LM_LP_GN_FC_ER_P11_EX",
            "new_capabilities": "NONE__ONE_FRESH_LIFECYCLE_INSTANCE",
            "existing_capability_unreachable": False,
            "parallel_flow": False,
            "production_route_effect": "UNCHANGED__1_TO_1",
        },
        "e05": {
            "BEFORE": "12/18",
            "LQ_CREDIT": 0,
            "AFTER": "12/18",
            "FRONTIER": "WRONG_SCOPE",
            "WRONG_SCOPE": "UNSAT__OPERATIONAL_DENIAL_NOT_PERFORMED",
        },
        "ex": {"REUSED": "VERIFIED__17_OF_17", "RECONSTRUCTED": "VERIFIED__0"},
        "operational_counters": zero_counters(),
        "human_boundary": {
            "authority": "NONE",
            "decision": "PENDING",
            "ready_for_human_decision": True,
            "next": "INDEPENDENT_HUMAN_REVIEW_ONLY",
        },
    }


def materialize() -> dict[str, Any]:
    repository = authenticate_repository()
    authenticate_sources()
    if repository["current_head"] != ENTRY_HEAD or repository["remote_head"] != ENTRY_HEAD:
        raise LQVerificationError("MATERIALIZATION_REQUIRES_EXACT_LP_ENTRY")
    targets = (CONTEXT, READINESS, REVIEW, PRESENTATION, REDUCTION)
    if any(path.exists() or path.is_symlink() for path in targets):
        raise LQVerificationError("LQ_ONE_SHOT_NAMESPACE_NOT_FRESH")
    if (LQ / "operation_state").exists() or TRANSIENT.exists() or TRANSIENT.is_symlink():
        raise LQVerificationError("LQ_MATERIALIZATION_NAMESPACE_NOT_FRESH")
    if subprocess.run(
        ["git", "grep", "-F", REVIEW_ID, ENTRY_HEAD],
        cwd=ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0:
        raise LQVerificationError("LQ_REVIEW_ID_NOT_FRESH")

    context = FM.build_operation_context(
        repository_root=ROOT,
        repository_head=ENTRY_HEAD,
        repository_tree=ENTRY_TREE,
        generation_identity=GENERATION,
        operation_identity=OPERATION,
        identity_namespace_prefix=PREFIX,
        operation_evidence_root=LQ / "operation_state",
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
    receipt_checkpoint = GL.reduce_preauthorization_checkpoint(
        ROOT, context, receipt_claim
    )
    readiness_inner = {
        "schema_id": "G77_256LQ_PREAUTHORITY_STATIC_READINESS_V1",
        "artifact_class": "AUTHORITY_FREE_STATIC_OBSERVATION__NONOPERATIONAL",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "context_sha256": context["context_sha256"],
        "context_file_sha256": sha256_path(CONTEXT),
        "entry_head": ENTRY_HEAD,
        "entry_tree": ENTRY_TREE,
        "materialization": materialization,
        "static_readiness": static,
        "receipt_parent_claim": receipt_claim,
        "receipt_parent_checkpoint": receipt_checkpoint,
        "authority_state": "NONE",
        "operation_state": "NOT_STARTED",
        "operational_counters": zero_counters(),
    }
    readiness = sealed(
        "G77_256LQ_PREAUTHORITY_STATIC_READINESS_ENVELOPE_V1",
        "checkpoint",
        readiness_inner,
    )
    write_fresh(READINESS, readiness)
    review_inner = build_review(context, sha256_path(READINESS))
    review = sealed(
        "G77_256LQ_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_ENVELOPE_V1",
        "review_object",
        review_inner,
    )
    write_fresh(REVIEW, review)
    write_fresh(PRESENTATION, render_presentation(context, review))
    reduction_inner = build_reduction(context, readiness)
    write_fresh(
        REDUCTION,
        sealed(
            "G77_256LQ_SPCE_TERMINAL_REDUCTION_ENVELOPE_V1",
            "reduction",
            reduction_inner,
        ),
    )
    return verify()


def authenticate_transition_compatibility(
    context: dict[str, Any], repository: dict[str, str]
) -> dict[str, Any]:
    relative_context = CONTEXT.relative_to(ROOT).as_posix()
    if FM._committed_review_context_path(ROOT, context) != relative_context:
        raise LQVerificationError("LP_CANONICAL_REVIEW_PATH_MISMATCH")
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
            raise LQVerificationError("UNCOMMITTED_REVIEW_STATE_INVALID")
        return {
            "state": "PENDING_IMMUTABLE_COMMIT_R",
            "review_identity_R": "PENDING_COMMIT",
            "current_admission_identity_C": f"{current_head}/{current_tree}",
            "transition_proof_state": "NOT_CREATED",
        }
    introductions = git(
        "log", "--format=%H", "--diff-filter=A", current_head, "--", relative_context
    ).splitlines()
    if len(introductions) != 1:
        raise LQVerificationError("LQ_REVIEW_INTRODUCTION_MISSING_OR_AMBIGUOUS")
    review_head = introductions[0]
    review_tree = git("rev-parse", f"{review_head}^{{tree}}")
    if (
        not is_ancestor(ENTRY_HEAD, review_head)
        or not is_ancestor(review_head, current_head)
        or subprocess.check_output(
            ["git", "show", f"{review_head}:{relative_context}"], cwd=ROOT
        ) != CONTEXT.read_bytes()
    ):
        raise LQVerificationError("LQ_COMMITTED_REVIEW_IDENTITY_INVALID")
    if review_head == current_head:
        return {
            "state": "IMMUTABLE_REVIEW_IDENTITY_R_COMMITTED__SUCCESSOR_C_REQUIRED",
            "review_identity_R": f"{review_head}/{review_tree}",
            "current_admission_identity_C": f"{current_head}/{current_tree}",
            "transition_proof_state": "NOT_CREATED__NO_SUCCESSOR_DELTA",
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
        raise LQVerificationError("LP_TRANSITION_AUTHENTICATION_FAILED")
    return {
        "state": "LP_EXACT_TRANSITION_COMPATIBILITY_VERIFIED",
        "review_identity_R": f"{review_head}/{review_tree}",
        "current_admission_identity_C": f"{current_head}/{current_tree}",
        "transition_proof_state": "DERIVED_IN_MEMORY__NONAUTHORITY__NONCONSUMABLE",
        "transition_sha256": proof["transition_sha256"],
    }


def verify() -> dict[str, Any]:
    repository = authenticate_repository()
    authenticate_sources()
    context = load_canonical(CONTEXT)
    FM.fresh_context.validate_context(context, repository_root=ROOT)
    if (
        context["generation_identity"] != GENERATION
        or context["operation_identity"] != OPERATION
        or context["repository_head"] != ENTRY_HEAD
        or context["repository_tree"] != ENTRY_TREE
        or context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["head"] != RUNTIME_HEAD
        or context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["tree"] != RUNTIME_TREE
    ):
        raise LQVerificationError("CANONICAL_CONTEXT_BINDING_MISMATCH")
    readiness = load_canonical(READINESS)
    checkpoint = readiness.get("checkpoint")
    if (
        not isinstance(checkpoint, dict)
        or readiness.get("checkpoint_sha256")
        != hashlib.sha256(canonical_bytes(checkpoint)).hexdigest()
        or checkpoint.get("context_sha256") != context["context_sha256"]
        or checkpoint.get("authority_state") != "NONE"
        or checkpoint.get("operation_state") != "NOT_STARTED"
        or any(checkpoint.get("operational_counters", {}).values())
    ):
        raise LQVerificationError("STATIC_READINESS_SEAL_OR_BOUNDARY_INVALID")
    GL.validate_bound_observation(
        ROOT, context, checkpoint["receipt_parent_claim"]
    )
    review_envelope = load_canonical(REVIEW)
    review = review_envelope.get("review_object")
    if (
        review_envelope.get("schema_id")
        != "G77_256LQ_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_ENVELOPE_V1"
        or not isinstance(review, dict)
        or review_envelope.get("review_object_sha256")
        != hashlib.sha256(canonical_bytes(review)).hexdigest()
        or len(list(LQ.glob("*PHASE_A_REVIEW_OBJECT*.json"))) != 1
    ):
        raise LQVerificationError("REVIEW_OBJECT_CARDINALITY_OR_SEAL_INVALID")
    required = {
        "GENERATION": "G77-256LQ",
        "GENERATION_ID": GENERATION,
        "VECTOR": "WRONG_SCOPE",
        "PHASE": "A",
        "REVIEW_OBJECT_ID": REVIEW_ID,
        "CANONICAL_OPERATION_ID": OPERATION,
        "AUTHORIZED_SCOPE": EXPECTED_SCOPE,
        "PRESENTED_SCOPE": PRESENTED_SCOPE,
        "ONE_SHOT_LIMIT": 1,
        "RETRY_LIMIT": 0,
        "AUTHORITY": "NONE",
        "AUTHORITY_CREATED": "NO",
        "AUTHORITY_CONSUMED": "NO",
        "OPERATION_STATE": "NOT_STARTED",
        "P11_STATE": "NOT_ENTERED",
        "PROTECTED_EFFECT": "NONE",
        "HUMAN_DECISION_STATE": "PENDING",
        "READINESS": "READY_FOR_HUMAN_DECISION",
    }
    if any(review.get(key) != expected for key, expected in required.items()):
        raise LQVerificationError("REVIEW_OBJECT_REQUIRED_FIELD_MISMATCH")
    binding = review.get("CANONICAL_CONTEXT_BINDING", {})
    if binding != {
        "path": CONTEXT.relative_to(ROOT).as_posix(),
        "context_sha256": context["context_sha256"],
        "whole_file_sha256": sha256_path(CONTEXT),
        "repository_head": ENTRY_HEAD,
        "repository_tree": ENTRY_TREE,
        "preauthority_static_readiness_file_sha256": sha256_path(READINESS),
    }:
        raise LQVerificationError("REVIEW_TO_CONTEXT_BINDING_MISMATCH")
    mismatch = review.get("ISOLATED_MISMATCH", {})
    model = LG.authenticate_wrong_scope_semantics(ROOT)
    if (
        mismatch.get("field") != "authority_scope"
        or mismatch.get("expected") != EXPECTED_SCOPE
        or mismatch.get("presented") != PRESENTED_SCOPE
        or mismatch.get("independent_semantic_mutation_count") != 1
        or model.get("independent_semantic_mutation_count") != 1
        or model["baseline"]["authority_scope"] != EXPECTED_SCOPE
        or model["presented"]["authority_scope"] != PRESENTED_SCOPE
    ):
        raise LQVerificationError("WRONG_SCOPE_NOT_EXACTLY_ONE_MISMATCH")
    candidate = review.get("CANDIDATE_HUMAN_ACT_MATERIAL", {})
    if (
        candidate.get("is_authority") is not False
        or candidate.get("human_actor_identity_state") != "ABSENT"
        or candidate.get("human_authority_source_bytes_state") != "ABSENT"
        or candidate.get("payload_digest_state") != "UNMATERIALIZED"
    ):
        raise LQVerificationError("HUMAN_AUTHORITY_BOUNDARY_CROSSED")
    previous = review.get("PREVIOUS_LIFECYCLE", {})
    if any(
        previous.get(field) is not False
        for field in ("LM_OBJECT_REUSED", "LM_OR_LN_AUTHORITY_REUSED", "OLD_APPROVAL_INHERITED")
    ):
        raise LQVerificationError("LM_LN_LIFECYCLE_RESURRECTION")
    if not review.get("STATE_COUNTERS") or any(review["STATE_COUNTERS"].values()):
        raise LQVerificationError("NONZERO_AUTHORITY_OR_OPERATION_COUNTER")
    if PRESENTATION.read_text(encoding="utf-8") != render_presentation(
        context, review_envelope
    ):
        raise LQVerificationError("HUMAN_PRESENTATION_BINDING_MISMATCH")
    forbidden = (
        "*HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE*",
        "*FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF*",
        "*AUTHORITY_VALIDATION_AND_CONSUMPTION*",
        "*OPERATIONAL_INVOCATION_ATTEMPT*",
        "*SERIAL_CONSOLE*",
        "*PRE_EXECUTED_QEMU_ARGV_RECEIPT*",
        "*POST_EXECUTED_QEMU_ARGV_RECEIPT*",
    )
    if any(list(LQ.rglob(pattern)) for pattern in forbidden):
        raise LQVerificationError("AUTHORITY_OR_OPERATION_ARTIFACT_PRESENT")
    reduction_envelope = load_canonical(REDUCTION)
    reduction = reduction_envelope.get("reduction")
    if (
        not isinstance(reduction, dict)
        or reduction_envelope.get("reduction_sha256")
        != hashlib.sha256(canonical_bytes(reduction)).hexdigest()
        or reduction != build_reduction(context, readiness)
    ):
        raise LQVerificationError("SPCE_REDUCTION_INVALID")
    transition = authenticate_transition_compatibility(context, repository)
    return {
        "terminal": TERMINAL,
        "repository": repository,
        "review_object_id": REVIEW_ID,
        "review_object_whole_sha256": sha256_path(REVIEW),
        "review_object_inner_sha256": review_envelope["review_object_sha256"],
        "context_sha256": context["context_sha256"],
        "transition": transition,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--materialize", action="store_true")
    arguments = parser.parse_args()
    result = materialize() if arguments.materialize else verify()
    print(result["terminal"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
