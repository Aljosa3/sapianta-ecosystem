#!/usr/bin/env python3
"""Authenticate, authorize, consume, and invoke the exact LR attempt once.

This generation-local controller delegates context validation, canonical
authority serialization, final admission, receipt ownership, and the sole
QEMU route to FM.  It adds no production owner or execution path.  Its three
explicit phases make the pre-authority and pre-consumption boundaries durable.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
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
LR_REL = Path(
    ".github/governance/evidence/"
    "g77_256lr_operational_wrong_scope_denial_v1"
)
LR = ROOT / LR_REL
LQ_REL = Path(
    ".github/governance/evidence/"
    "g77_256lq_wrong_scope_fresh_phase_a_review_object_v1"
)
LQ = ROOT / LQ_REL
CONTEXT = LQ / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
REVIEW = LQ / "G77_256LQ_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_V1.json"
PRESENTATION = LQ / "G77_256LQ_HUMAN_DECISION_PRESENTATION_V1.txt"
SOURCE = LR / "G77_256LR_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
TRANSITION = LR / "G77_256LR_LP_COMMITTED_REVIEW_TRANSITION_V1.json"
PREAUTH = LR / "G77_256LR_PREAUTHORITY_ENTRY_AND_DECISION_BINDING_V1.json"
HANDOFF = LR / "G77_256LR_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
BINDING = LR / "G77_256LR_PRECONSUMPTION_INVOCATION_BINDING_V1.json"
PRECONSUMPTION = LR / "G77_256LR_PRECONSUMPTION_READINESS_CHECKPOINT_V1.json"
CONSUMPTION = LR / "G77_256LR_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json"
ATTEMPT = LR / "G77_256LR_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1.json"
RESULT = LR / "G77_256LR_FM_OPERATIONAL_INVOCATION_RESULT_V1.json"
CANDIDATE_REL = Path(
    ".github/governance/evidence/g77_256gd_fresh_operation_context_v1/"
    "candidate/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
)
CANDIDATE = ROOT / CANDIDATE_REL
FM_PATH = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
LG_PATH = ROOT / (
    ".github/governance/evidence/g77_256lg_wrong_scope_existing_route_admission_v1/"
    "adapter/G77_256LG_WRONG_SCOPE_VECTOR_ADAPTER_V1.py"
)

BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
LP_HEAD = "7e6b281e861ae6e7572c3eea9f8be2ceca470b8f"
R_HEAD = "010aaf1b4f8ae14141d8f65ea9109dfcf5ffac83"
R_TREE = "892f0c35419dc6fd90f1fbd9d753b0aa0778730e"
R_SUBJECT = "G77-256LQ seal fresh WRONG_SCOPE Phase-A review object"
C_HEAD = "ef944daef992055583c2b18c6d7696e472efd09d"
C_TREE = "f14a9312f89ea7accdf24fa8a35a87754802fb17"
C_SUBJECT = "G77-256LQ record fresh Human decision readiness"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
ANCHOR = "5c972e9960987ab27420395b54ace693df097e7b"
OBJECT_ID = "G77_256LQ_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_001"
OBJECT_WHOLE_SHA256 = "035e406848463173bd68b6cf1ec810cdfa7ab846ce02b26cf376c7d81a77eecb"
OBJECT_INNER_SHA256 = "e4e06906cf641c2b40c3af7bf8d153ae5f7b02f2b438cab1a5659450fd3942d4"
CONTEXT_SHA256 = "361a87b513c28834e1c58aae503c37b138aca8765f96844e766c419946e467f5"
CONTEXT_WHOLE_SHA256 = "8f6e284d3ad40737b093ba2829a03315e8466dce82680429cdd138cf5a3f2a3d"
PRESENTATION_SHA256 = "3469232ca22e49cc33e9b4c84af7029ba53977459c9c39a86b7be08990a60eef"
TRANSITION_SHA256 = "3ad7d1edcb568693d6510804f03686221d1ce2a1c04be9cc722184a6c7e69911"
AUTHORIZED_SCOPE = "P11_DA_ONE_BOUNDED_OPERATIONAL_ATTEMPT_V1"
PRESENTED_SCOPE = "P11_DA_DIFFERENT_OPERATIONAL_SCOPE_V1"
GENERATION = "G77_256LQ_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_SCOPE_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256LQ_E05_WRONG_SCOPE_DENIAL_BEFORE_P11_ENTRY_001"
AUTHORITY_ID = "G77_256LR_FRESH_HUMAN_OPERATIONAL_AUTHORITY_001"
FM_SHA256 = "5a0a597434bd89752828afd85ecb5a98669f41ae66fa0480ea27be6d611597e8"
LG_SHA256 = "035c3c02cfb4cee26c6af2501b85a547d0376c80c4df376b7a40a8671277136f"

HUMAN_SOURCE_TEXT = """\"Odobrim exact sealed LQ objekt
`G77_256LQ_WRONG_SCOPE_PHASE_A_REVIEW_OBJECT_001`,
whole-object SHA256
`035e406848463173bd68b6cf1ec810cdfa7ab846ce02b26cf376c7d81a77eecb`,
za natanko en enkratni WRONG_SCOPE operational attempt v okviru
`P11_DA_ONE_BOUNDED_OPERATIONAL_ATTEMPT_V1`,
pri katerem je presented scope
`P11_DA_DIFFERENT_OPERATIONAL_SCOPE_V1`.
Odobritev velja samo za ta exact objekt in se ne prenaša na drug objekt,
scope, retry ali successor lifecycle.\"
"""


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def load_module(path: Path, name: str, expected_sha256: str) -> ModuleType:
    if path.is_symlink() or not path.is_file() or sha256_path(path) != expected_sha256:
        raise RuntimeError(f"AUTHENTICATED_OWNER_MISMATCH:{name}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"OWNER_IMPORT_FAILED:{name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


FM = load_module(FM_PATH, "g77_256lr_existing_fm_owner", FM_SHA256)
LG = load_module(LG_PATH, "g77_256lr_existing_lg_semantics", LG_SHA256)


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


def now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def seal(schema: str, field: str, value: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": schema,
        field: value,
        f"{field}_sha256": hashlib.sha256(canonical_bytes(value)).hexdigest(),
    }


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise RuntimeError(f"NONCANONICAL_JSON:{path.name}")
    return value


def inner(path: Path, field: str) -> dict[str, Any]:
    envelope = load_canonical(path)
    value = envelope.get(field)
    if (
        not isinstance(value, dict)
        or envelope.get(f"{field}_sha256")
        != hashlib.sha256(canonical_bytes(value)).hexdigest()
    ):
        raise RuntimeError(f"SEAL_MISMATCH:{path.name}")
    return value


def persist(path: Path, value: dict[str, Any]) -> str:
    if path.exists() or path.is_symlink():
        raise RuntimeError(f"ONE_SHOT_ARTIFACT_COLLISION:{path.name}")
    return FM.write_atomic(path, value)


def allowed_untracked() -> None:
    allowed_lq = {
        str(Path("operation_state/receipts/G77_256LQ_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")),
        str(Path("operation_state/receipts/G77_256LQ_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")),
        *{
            str(Path("operation_state/runtime_export") / name)
            for name in (
                "G77_256LQ_RAW_EXECUTION_EVIDENCE_V1.jsonl",
                "G77_256DN_P03_RAW_EVIDENCE_V1.jsonl",
                "G77_256DN_SPCE_EXECUTION_SEAL_V1.json",
                "G77_256LQ_PRE_ACT_CHECKPOINT_V1.json",
                "G77_256LQ_AUTHORITY_CHECKPOINT_V1.json",
                "G77_256LQ_GUEST_EXECUTION_SEAL_V1.json",
                "G77_256LQ_GUEST_TEARDOWN_SEAL_V1.json",
                "G77_256LQ_CONTINUATION_MANIFEST_TERMINAL_V1.json",
            )
        },
    }
    for line in git("status", "--porcelain=v1", "--untracked-files=all").splitlines():
        if line[:2] != "??":
            raise RuntimeError(f"TRACKED_OR_STAGED_MUTATION:{line}")
        path = line[3:]
        if path.startswith(LR_REL.as_posix() + "/"):
            continue
        if path.startswith(LQ_REL.as_posix() + "/"):
            relative = path[len(LQ_REL.as_posix()) + 1 :]
            if relative in allowed_lq:
                continue
        raise RuntimeError(f"UNRELATED_UNTRACKED_MUTATION:{line}")


def authenticate_entry(remote_head: str, nested_remote_tag: str) -> None:
    if (
        ROOT != Path("/home/pisarna/work/sapianta-fl")
        or git("branch", "--show-current") != BRANCH
        or git("rev-parse", "HEAD") != C_HEAD
        or git("rev-parse", "HEAD^{tree}") != C_TREE
        or git("show", "-s", "--format=%s", "HEAD") != C_SUBJECT
        or remote_head != C_HEAD
        or git("rev-parse", f"{R_HEAD}^{{tree}}") != R_TREE
        or git("show", "-s", "--format=%s", R_HEAD) != R_SUBJECT
        or not is_ancestor(LP_HEAD, R_HEAD)
        or not is_ancestor(R_HEAD, C_HEAD)
        or not is_ancestor(R_HEAD, remote_head)
        or git("status", "--porcelain=v1", "--untracked-files=no")
    ):
        raise RuntimeError("LQ_ENTRY_AUTHENTICATION_CONFLICT")
    allowed_untracked()
    nested = ROOT / "sapianta_system"
    if (
        git("rev-parse", "HEAD", cwd=nested) != NESTED_HEAD
        or git("rev-parse", "HEAD^{tree}", cwd=nested) != NESTED_TREE
        or git("status", "--porcelain=v1", "--untracked-files=all", cwd=nested)
        or git("branch", "--show-current", cwd=nested)
        or git("rev-parse", f"refs/tags/{NESTED_TAG}^{{}}", cwd=nested)
        != NESTED_HEAD
        or nested_remote_tag != NESTED_HEAD
    ):
        raise RuntimeError("NESTED_AUTHORITY_CONFLICT")


def authenticate_lq() -> tuple[dict[str, Any], dict[str, Any]]:
    if (
        sha256_path(REVIEW) != OBJECT_WHOLE_SHA256
        or sha256_path(CONTEXT) != CONTEXT_WHOLE_SHA256
        or sha256_path(PRESENTATION) != PRESENTATION_SHA256
    ):
        raise RuntimeError("LQ_OBJECT_CONTEXT_OR_PRESENTATION_HASH_CONFLICT")
    envelope = load_canonical(REVIEW)
    review = envelope.get("review_object")
    if (
        not isinstance(review, dict)
        or envelope.get("review_object_sha256") != OBJECT_INNER_SHA256
        or OBJECT_INNER_SHA256
        != hashlib.sha256(canonical_bytes(review)).hexdigest()
        or review.get("REVIEW_OBJECT_ID") != OBJECT_ID
        or review.get("GENERATION") != "G77-256LQ"
        or review.get("VECTOR") != "WRONG_SCOPE"
        or review.get("PHASE") != "A"
        or review.get("AUTHORIZED_SCOPE") != AUTHORIZED_SCOPE
        or review.get("PRESENTED_SCOPE") != PRESENTED_SCOPE
        or review.get("ONE_SHOT_LIMIT") != 1
        or review.get("RETRY_LIMIT") != 0
        or review.get("AUTHORITY") != "NONE"
        or review.get("AUTHORITY_CREATED") != "NO"
        or review.get("AUTHORITY_CONSUMED") != "NO"
        or review.get("OPERATION_STATE") != "NOT_STARTED"
        or review.get("P11_STATE") != "NOT_ENTERED"
        or review.get("PROTECTED_EFFECT") != "NONE"
    ):
        raise RuntimeError("LQ_REVIEW_OBJECT_BINDING_CONFLICT")
    mismatch = review.get("ISOLATED_MISMATCH", {})
    if (
        mismatch.get("field") != "authority_scope"
        or mismatch.get("expected") != AUTHORIZED_SCOPE
        or mismatch.get("presented") != PRESENTED_SCOPE
        or mismatch.get("independent_semantic_mutation_count") != 1
    ):
        raise RuntimeError("LQ_ISOLATED_MISMATCH_CONFLICT")
    binding = review.get("CANONICAL_CONTEXT_BINDING", {})
    if (
        binding.get("context_sha256") != CONTEXT_SHA256
        or binding.get("whole_file_sha256") != CONTEXT_WHOLE_SHA256
        or binding.get("path") != CONTEXT.relative_to(ROOT).as_posix()
    ):
        raise RuntimeError("LQ_CONTEXT_BINDING_CONFLICT")
    if any(review.get("STATE_COUNTERS", {}).values()):
        raise RuntimeError("LQ_PREEXISTING_AUTHORITY_OR_OPERATION_STATE")
    context = FM.fresh_context.load_context(CONTEXT, repository_root=ROOT)
    if (
        context.get("context_sha256") != CONTEXT_SHA256
        or context.get("generation_identity") != GENERATION
        or context.get("operation_identity") != OPERATION
        or context.get("repository_head") != LP_HEAD
        or FM.context_vector(context) != "WRONG_SCOPE"
    ):
        raise RuntimeError("LQ_CANONICAL_CONTEXT_CONFLICT")
    model = LG.authenticate_wrong_scope_semantics(ROOT)
    if (
        model.get("independent_semantic_mutation_count") != 1
        or model.get("independent_semantic_mutation_set")
        != [f"authority_scope:{AUTHORIZED_SCOPE}->{PRESENTED_SCOPE}"]
    ):
        raise RuntimeError("WRONG_SCOPE_SEMANTICS_CONFLICT")
    return review, context


def authenticate_human_source() -> str:
    if SOURCE.is_symlink() or not SOURCE.is_file():
        raise RuntimeError("HUMAN_DECISION_SOURCE_ABSENT_OR_UNSAFE")
    if SOURCE.read_text(encoding="utf-8") != HUMAN_SOURCE_TEXT:
        raise RuntimeError("HUMAN_DECISION_SOURCE_BYTES_CONFLICT")
    return sha256_path(SOURCE)


def derive_transition(context: dict[str, Any]) -> dict[str, Any]:
    proof = FM.build_committed_review_transition(
        repository_root=ROOT,
        context=context,
        current_admission_head=C_HEAD,
        current_admission_tree=C_TREE,
    )
    if (
        proof.get("transition_sha256") != TRANSITION_SHA256
        or proof.get("review_object_head") != R_HEAD
        or proof.get("review_object_tree") != R_TREE
        or proof.get("current_admission_head") != C_HEAD
        or proof.get("current_admission_tree") != C_TREE
        or proof.get("transition_is_authority") is not False
        or proof.get("transition_consumable") is not False
    ):
        raise RuntimeError("LP_TRANSITION_BINDING_CONFLICT")
    relation = FM.authenticate_review_to_current_admission(
        repository_root=ROOT,
        context=context,
        observed_head=C_HEAD,
        observed_tree=C_TREE,
        committed_review_transitions=[proof],
    )
    if (
        relation.get("repository_identity_relation")
        != "EXACT_COMMITTED_REVIEW_TO_CURRENT_ADMISSION_TRANSITION"
        or relation.get("committed_review_transition_sha256") != TRANSITION_SHA256
    ):
        raise RuntimeError("LP_TRANSITION_AUTHENTICATION_FAILED")
    return proof


def authority(context: dict[str, Any], source_sha256: str) -> dict[str, Any]:
    return {
        "schema_id": FM.AUTHORIZATION_SCHEMA,
        "authorization_present": True,
        "authorization_kind": "FRESH_HUMAN_OPERATIONAL_AUTHORIZATION",
        "authorization_source_sha256": source_sha256,
        "authorized_context_sha256": CONTEXT_SHA256,
        "authorized_operation_identity": OPERATION,
        "authorized_generation_identity": GENERATION,
        "authorized_vector": "WRONG_SCOPE",
        "authorized_repository_head": C_HEAD,
        "authorized_repository_tree": C_TREE,
        "authorized_constitutional_anchor_head": ANCHOR,
        "authorized_candidate_sha256": context["candidate_manifest_sha256"],
        "authorized_canonical_argv_sha256": context["canonical_argv_sha256"],
        "authorized_wrapper_sha256": context["wrapper_fc_er_che_schema_hashes"]["wrapper"],
        "authorized_fk_adapter_sha256": FM.FK_ADAPTER_SHA256,
        "vm_boot_limit": 1,
        "qemu_system_execution_limit": 1,
        "wrong_scope_operational_attempt_limit": 1,
        "retry_limit": 0,
        "repair_limit": 0,
        "replay_limit": 0,
        "receipt_namespace_must_be_unconsumed": True,
        "network_authorized": False,
        "provider_authorized": False,
        "trusted_access_authorized": False,
        "authorization_reusable": False,
        "auto_continuable": False,
    }


def counters(*, created: int, consumed: int, invoked: int) -> dict[str, int]:
    return {
        "human_authority_source_count": 1,
        "authority_creation_count": created,
        "authority_consumption_count": consumed,
        "fm_operational_invocation_count": invoked,
        "qemu_start_count": invoked,
        "vm_start_count": invoked,
        "operation_attempt_count": invoked,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "operational_replay_count": 0,
        "repair_retry_count": 0,
    }


def validate_admission(
    context: dict[str, Any],
    handoff: dict[str, Any],
    digest: str,
    proof: dict[str, Any],
) -> dict[str, str]:
    observed = FM.observe_context_assets(ROOT, context, CANDIDATE_REL)
    argv = context["canonical_argv"]
    argv_sha256 = FM.load_canonicalizer(ROOT).argv_sha256(argv)
    return FM.validate_final_admission(
        repository_root=ROOT,
        context=context,
        authority=handoff,
        authority_file_sha256=digest,
        supplied_authority_sha256=digest,
        observed_head=C_HEAD,
        observed_tree=C_TREE,
        anchor_is_ancestor=FM.constitutional_anchor_is_ancestor(ROOT),
        repository_clean=git("status", "--porcelain=v1", "--untracked-files=no") == "",
        observed_asset_sha256=observed,
        argv=argv,
        canonical_argv_sha256=argv_sha256,
        receipt_namespace_consumed=any(
            path.exists() for path in FM.receipt_consumable_paths(ROOT, context)
        ),
        candidate_source_path=CANDIDATE_REL,
        committed_review_transitions=[proof],
    )


def build_combined_binding(
    transition_file_sha256: str,
) -> tuple[dict[str, Any], list[str]]:
    fm_envelope = FM.build_preconsumption_invocation_binding(
        repository_root=ROOT,
        operation_context=CONTEXT,
        live_candidate_binding=CANDIDATE,
        execution_authority=HANDOFF,
    )
    fm_binding = FM.validate_preconsumption_invocation_binding(
        repository_root=ROOT,
        operation_context=CONTEXT,
        live_candidate_binding=CANDIDATE,
        execution_authority=HANDOFF,
        envelope=fm_envelope,
    )
    final_argv = [
        *fm_binding["final_fm_argv"],
        "--committed-review-transition",
        TRANSITION.relative_to(ROOT).as_posix(),
        "--committed-review-transition-sha256",
        transition_file_sha256,
    ]
    value = {
        "schema_id": "G77_256LR_PRECONSUMPTION_INVOCATION_BINDING_V1",
        "binding_phase": "BEFORE_AUTHORITY_CONSUMPTION_AND_FM_INVOCATION",
        "fm_owned_base_binding": fm_envelope,
        "lp_transition_path": TRANSITION.relative_to(ROOT).as_posix(),
        "lp_transition_file_sha256": transition_file_sha256,
        "lp_transition_inner_sha256": TRANSITION_SHA256,
        "lp_transition_is_authority": False,
        "lp_transition_consumable": False,
        "final_fm_argv": final_argv,
        "final_fm_argv_sha256": hashlib.sha256(canonical_bytes(final_argv)).hexdigest(),
        "caller_digest_input_count": 0,
        "process_started": False,
        "authority_consumption_count": 0,
        "fm_operational_invocation_count": 0,
    }
    return seal(
        "G77_256LR_PRECONSUMPTION_INVOCATION_BINDING_ENVELOPE_V1",
        "binding",
        value,
    ), final_argv


def preflight(args: argparse.Namespace) -> None:
    authenticate_entry(args.remote_head, args.nested_remote_tag)
    review, context = authenticate_lq()
    source_sha256 = authenticate_human_source()
    if any(
        path.exists() or path.is_symlink()
        for path in (
            TRANSITION,
            PREAUTH,
            HANDOFF,
            BINDING,
            PRECONSUMPTION,
            CONSUMPTION,
            ATTEMPT,
            RESULT,
        )
    ):
        raise RuntimeError("LR_PREAUTHORITY_NAMESPACE_NOT_FRESH")
    proof = derive_transition(context)
    observations = FM.observe_context_assets(ROOT, context, CANDIDATE_REL)
    static = FM.authority_free_static_readiness(
        repository_root=ROOT,
        context=context,
        observed_head=C_HEAD,
        observed_tree=C_TREE,
        repository_clean=True,
        observed_asset_sha256=observations,
        candidate_source_path=CANDIDATE_REL,
        committed_review_transitions=[proof],
    )
    transition_file_sha256 = persist(TRANSITION, proof)
    checkpoint = {
        "schema_id": "G77_256LR_PREAUTHORITY_ENTRY_AND_DECISION_BINDING_V1",
        "recorded_at_utc": now(),
        "generation": "G77-256LR",
        "phase": "PREAUTHORITY",
        "repository": {
            "review_head": R_HEAD,
            "review_tree": R_TREE,
            "current_head": C_HEAD,
            "current_tree": C_TREE,
            "remote_head": args.remote_head,
        },
        "human_decision": {
            "source_sha256": source_sha256,
            "object_id": OBJECT_ID,
            "object_whole_sha256": OBJECT_WHOLE_SHA256,
            "object_inner_sha256": OBJECT_INNER_SHA256,
            "context_sha256": CONTEXT_SHA256,
            "context_whole_sha256": CONTEXT_WHOLE_SHA256,
            "presentation_sha256": PRESENTATION_SHA256,
            "authorized_scope": AUTHORIZED_SCOPE,
            "presented_scope": PRESENTED_SCOPE,
            "one_shot_limit": 1,
            "retry_limit": 0,
            "exact_binding": True,
        },
        "lp_transition": {
            "file_sha256": transition_file_sha256,
            "transition_sha256": TRANSITION_SHA256,
            "is_authority": False,
            "consumable": False,
            "authentication": "EXACT_COMMITTED_REVIEW_TO_CURRENT_ADMISSION_TRANSITION",
        },
        "runtime_checkout": context["qemu_executable_base_seed_checkout_bindings"]["checkout"],
        "receipt_namespace_unused": not any(
            path.exists() for path in FM.receipt_consumable_paths(ROOT, context)
        ),
        "isolated_mismatch": "authority_scope",
        "isolated_mismatch_count": 1,
        "failure_novelty_and_convergence_check": {
            "failure_class": "PROOF_GAP",
            "novelty": "STATIC_LIFECYCLE_AND_REVIEW_BINDING_NOW_COMPLETE__OPERATIONAL_WRONG_SCOPE_ACCEPTANCE_REMAINS_UNPROVEN",
            "affected_invariant": "VALID_HUMAN_AUTHORITY_FOR_SCOPE_A_MUST_NOT_AUTHORIZE_PRESENTED_SCOPE_B",
            "previous_closest_edge": "G77_256LN_PREAUTHORITY_CURRENT_ADMISSION_CONFLICT",
            "semantic_difference": "LP_AND_LQ_NOW_PROVIDE_EXACT_COMMITTED_REVIEW_IDENTITY_AND_SUCCESSOR_ADMISSION_BINDING",
            "production_behavior_impact": "NONE_UNLESS_ONE_AUTHORIZED_OPERATIONAL_ATTEMPT_REACHES_EXISTING_DENIAL_PATH",
            "new_capability_required": "NO",
            "new_proof_required": "YES__ONE_OPERATIONAL_WRONG_SCOPE_DENIAL_BEFORE_P11",
            "convergence_signal": "STATIC_BLOCKERS_CLOSED__FRESH_HUMAN_DECISION_AVAILABLE__ONE_OPERATIONAL_EDGE_REMAINS",
            "repetition_pressure": "LOW_IF_THIS_ATTEMPT_REACHES_SCOPE_ADMISSION",
            "verification_amplification_risk": "BOUNDED__ONE_ATTEMPT_ONLY__NO_RETRY",
        },
        "cross_vector_reuse_assessment": {
            "vectors": [
                "WRONG_ATTEMPT",
                "WRONG_INPUT",
                "WRONG_CONTRACT",
                "WRONG_PROVENANCE",
                "WRONG_CALLER",
                "FUTURE",
                "EXPIRED",
            ],
            "generations": ["LI", "LJ", "LK", "LL", "LM", "LN", "LO", "LP", "LQ"],
            "mechanisms": "FM_EXACT_ADMISSION__LP_TRANSITION__STABLE_CHECKOUT__GN_PRESENTATION__ONE_SHOT_AUTHORITY__GL_RECEIPT_PARENT__ER_P11_ROUTE__LG_SCOPE__EX_17_OF_17",
            "authority_transfer": False,
            "proof_transfer": False,
            "e05_credit_transfer": False,
        },
        "static_readiness_sha256": static["readiness_sha256"],
        "authority_created_count": 0,
        "authority_consumed_count": 0,
        "operation_attempt_count": 0,
        "ready_for_authority_creation": True,
    }
    persist(
        PREAUTH,
        seal(
            "G77_256LR_PREAUTHORITY_ENTRY_AND_DECISION_BINDING_ENVELOPE_V1",
            "checkpoint",
            checkpoint,
        ),
    )
    print("A__G77_256LR_PREAUTHORITY_BINDING_VERIFIED__ZERO_AUTHORITY__ZERO_OPERATION")


def prepare_authority(args: argparse.Namespace) -> None:
    authenticate_entry(args.remote_head, args.nested_remote_tag)
    _, context = authenticate_lq()
    source_sha256 = authenticate_human_source()
    proof = derive_transition(context)
    loaded_proof = FM.load_committed_review_transition(
        TRANSITION, sha256_path(TRANSITION)
    )
    if loaded_proof != proof:
        raise RuntimeError("DURABLE_LP_TRANSITION_DRIFT")
    preauth = inner(PREAUTH, "checkpoint")
    if (
        not preauth.get("ready_for_authority_creation")
        or preauth.get("authority_created_count") != 0
        or preauth.get("authority_consumed_count") != 0
        or preauth.get("operation_attempt_count") != 0
        or preauth.get("human_decision", {}).get("source_sha256") != source_sha256
    ):
        raise RuntimeError("PREAUTHORITY_CHECKPOINT_CONFLICT")
    if any(
        path.exists() or path.is_symlink()
        for path in (HANDOFF, BINDING, PRECONSUMPTION, CONSUMPTION, ATTEMPT, RESULT)
    ):
        raise RuntimeError("LR_AUTHORITY_NAMESPACE_NOT_FRESH")
    handoff_result = FM.write_authority_handoff(
        HANDOFF, authority(context, source_sha256)
    )
    handoff, authority_file_sha256 = FM.load_authority(HANDOFF)
    if handoff_result["authority_file_sha256"] != authority_file_sha256:
        raise RuntimeError("AUTHORITY_PERSISTENCE_MISMATCH")
    admission = validate_admission(context, handoff, authority_file_sha256, proof)
    binding_envelope, final_argv = build_combined_binding(sha256_path(TRANSITION))
    binding_file_sha256 = persist(BINDING, binding_envelope)
    checkpoint = {
        "schema_id": "G77_256LR_PRECONSUMPTION_READINESS_CHECKPOINT_V1",
        "recorded_at_utc": now(),
        "generation": "G77-256LR",
        "authority_id": AUTHORITY_ID,
        "authority_file_sha256": authority_file_sha256,
        "authority_inner_sha256": handoff["authorization_sha256"],
        "authority_source_sha256": source_sha256,
        "authority_fresh": True,
        "authority_unconsumed": True,
        "authority_nonrevoked": True,
        "authority_nonsuperseded": True,
        "authority_nonexpired": True,
        "authority_not_future": True,
        "object_id": OBJECT_ID,
        "object_whole_sha256": OBJECT_WHOLE_SHA256,
        "context_sha256": CONTEXT_SHA256,
        "presentation_sha256": PRESENTATION_SHA256,
        "review_identity_r": f"{R_HEAD}/{R_TREE}",
        "current_admission_identity_c": f"{C_HEAD}/{C_TREE}",
        "transition_sha256": TRANSITION_SHA256,
        "transition_is_authority": False,
        "transition_consumable": False,
        "authorized_scope": AUTHORIZED_SCOPE,
        "presented_scope": PRESENTED_SCOPE,
        "isolated_mismatch": "authority_scope",
        "isolated_mismatch_count": 1,
        "caller_exact": True,
        "provenance_exact": True,
        "contract_exact": True,
        "input_exact": True,
        "one_shot_limit": 1,
        "retry_limit": 0,
        "receipt_namespace_unused": True,
        "runtime_checkout_exact": True,
        "final_admission_validation": "PASS",
        "admission_result": admission["result"],
        "repository_identity_relation": admission["repository_identity_relation"],
        "binding_file_sha256": binding_file_sha256,
        "final_fm_argv_sha256": hashlib.sha256(canonical_bytes(final_argv)).hexdigest(),
        "authority_state": "GRANTED_UNCONSUMED",
        "operational_counters": counters(created=1, consumed=0, invoked=0),
    }
    persist(
        PRECONSUMPTION,
        seal(
            "G77_256LR_PRECONSUMPTION_READINESS_CHECKPOINT_ENVELOPE_V1",
            "checkpoint",
            checkpoint,
        ),
    )
    print("A__G77_256LR_PRECONSUMPTION_READY__ONE_AUTHORITY_UNCONSUMED__ZERO_OPERATION")


def consume_and_operate(args: argparse.Namespace) -> int:
    authenticate_entry(args.remote_head, args.nested_remote_tag)
    _, context = authenticate_lq()
    source_sha256 = authenticate_human_source()
    if any(path.exists() or path.is_symlink() for path in (CONSUMPTION, ATTEMPT, RESULT)):
        raise RuntimeError("LR_AUTHORITY_OR_OPERATION_ALREADY_CONSUMED")
    proof = derive_transition(context)
    if FM.load_committed_review_transition(TRANSITION, sha256_path(TRANSITION)) != proof:
        raise RuntimeError("DURABLE_LP_TRANSITION_DRIFT")
    handoff, authority_file_sha256 = FM.load_authority(HANDOFF)
    if handoff["authorization"].get("authorization_source_sha256") != source_sha256:
        raise RuntimeError("AUTHORITY_SOURCE_DRIFT")
    expected_binding, final_argv = build_combined_binding(sha256_path(TRANSITION))
    if load_canonical(BINDING) != expected_binding:
        raise RuntimeError("PRECONSUMPTION_INVOCATION_BINDING_DRIFT")
    checkpoint = inner(PRECONSUMPTION, "checkpoint")
    if (
        checkpoint.get("authority_state") != "GRANTED_UNCONSUMED"
        or checkpoint.get("authority_file_sha256") != authority_file_sha256
        or checkpoint.get("transition_sha256") != TRANSITION_SHA256
        or checkpoint.get("isolated_mismatch") != "authority_scope"
        or checkpoint.get("operational_counters")
        != counters(created=1, consumed=0, invoked=0)
    ):
        raise RuntimeError("PRECONSUMPTION_CHECKPOINT_DRIFT")
    admission = validate_admission(context, handoff, authority_file_sha256, proof)
    consumption = {
        "schema_id": "G77_256LR_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1",
        "recorded_at_utc": now(),
        "generation": "G77-256LR",
        "authority_id": AUTHORITY_ID,
        "authority_source_sha256": source_sha256,
        "authority_file_sha256": authority_file_sha256,
        "authority_inner_sha256": handoff["authorization_sha256"],
        "preconsumption_checkpoint_file_sha256": sha256_path(PRECONSUMPTION),
        "final_admission_validation": "PASS",
        "admission_result": admission["result"],
        "authority_state_before": "GRANTED_UNCONSUMED",
        "authority_state_after": "CONSUMED",
        "authority_reusable": False,
        "authority_transferable": False,
        "authority_survives": False,
        "operational_counters": counters(created=1, consumed=1, invoked=0),
    }
    persist(
        CONSUMPTION,
        seal(
            "G77_256LR_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_ENVELOPE_V1",
            "checkpoint",
            consumption,
        ),
    )
    attempt = {
        "schema_id": "G77_256LR_FM_OPERATIONAL_INVOCATION_ATTEMPT_V1",
        "recorded_at_utc": now(),
        "generation": "G77-256LR",
        "authority_id": AUTHORITY_ID,
        "authority_state": "CONSUMED",
        "authority_file_sha256": authority_file_sha256,
        "invocation_binding_file_sha256": sha256_path(BINDING),
        "final_fm_argv_sha256": hashlib.sha256(canonical_bytes(final_argv)).hexdigest(),
        "transition_sha256": TRANSITION_SHA256,
        "invocation_count": 1,
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
        "operational_counters": counters(created=1, consumed=1, invoked=1),
    }
    persist(
        ATTEMPT,
        seal(
            "G77_256LR_FM_OPERATIONAL_INVOCATION_ATTEMPT_ENVELOPE_V1",
            "attempt",
            attempt,
        ),
    )
    status = 255
    process_exception: str | None = None
    try:
        status = subprocess.run(final_argv, cwd=ROOT, check=False).returncode
    except BaseException as exc:
        process_exception = f"{type(exc).__name__}:{exc}"
    result = {
        "schema_id": "G77_256LR_FM_OPERATIONAL_INVOCATION_RESULT_V1",
        "recorded_at_utc": now(),
        "generation": "G77-256LR",
        "authority_id": AUTHORITY_ID,
        "authority_state": "CONSUMED__TERMINAL_NONREUSABLE",
        "invocation_count": 1,
        "process_exit_status": status,
        "process_exception": process_exception,
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
    }
    persist(
        RESULT,
        seal(
            "G77_256LR_FM_OPERATIONAL_INVOCATION_RESULT_ENVELOPE_V1",
            "result",
            result,
        ),
    )
    return status


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "phase", choices=("preflight", "prepare-authority", "consume-and-operate")
    )
    parser.add_argument("--remote-head", required=True)
    parser.add_argument("--nested-remote-tag", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    if arguments.phase == "preflight":
        preflight(arguments)
    elif arguments.phase == "prepare-authority":
        prepare_authority(arguments)
    else:
        raise SystemExit(consume_and_operate(arguments))
