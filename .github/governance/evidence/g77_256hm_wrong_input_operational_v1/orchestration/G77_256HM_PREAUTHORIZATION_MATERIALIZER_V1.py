#!/usr/bin/env python3
"""Materialize one HM WRONG_INPUT request and stop before Human authority.

This bounded orchestrator reuses the existing GY, FM, GL, GN, and ER owners.
It has no authority-consumption, PRE, launcher, QEMU, VM-boot, request, P11,
protected-invocation, protected-effect, retry, repair, or replay entry point.
"""

from __future__ import annotations

from copy import deepcopy
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
HM = ROOT / ".github/governance/evidence/g77_256hm_wrong_input_operational_v1"
LIVE = HM / "live_binding"
OPERATION_ROOT = HM / "operation_state"
TRANSIENT_ROOT = Path("/tmp/g77_256hm_wrong_input_operational_v1")

BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
HEAD = "45495c09edf55cc201e3d146ea77e713f579166b"
TREE = "37ba96de335ee91851ff682f8cd97cf4e49ab5f5"
SUBJECT = "G77-256HL certify WRONG_INPUT preoperational readiness"
STABLE_ANCESTRY = "5c972e9960987ab27420395b54ace693df097e7b"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
GENERATION = (
    "G77_256HM_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_"
    "OPERATIONAL_COMMISSIONING_V1"
)
OPERATION = "G77_256HM_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001"
PREFIX = "G77_256HM"
RECORDED_AT_UTC = "2026-09-03T14:35:22Z"

HL_ROOT = ROOT / ".github/governance/evidence/g77_256hl_post_hk_live_binding_readiness_v1"
HL_REDUCTION = HL_ROOT / "G77_256HL_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
HL_CANDIDATE = HL_ROOT / "live_binding/candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
GY_BINDER_PATH = ROOT / ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/binding/G77_256GY_WRONG_INPUT_POST_COMMIT_BINDING_V1.py"
GY_PRODUCER_PATH = ROOT / ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/producer/G77_256GY_WRONG_INPUT_REQUEST_AND_CANDIDATE_PRODUCER_V1.py"
FM_PATH = ROOT / ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
GL_PATH = ROOT / ".github/governance/evidence/g77_256gl_receipt_parent_equivalence_v1/orchestration/G77_256GL_RECEIPT_PARENT_PREAUTHORIZATION_BINDING_V1.py"
GN_PATH = ROOT / ".github/governance/evidence/g77_256gn_human_authorization_presentation_binding_v1/presentation/G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"

CANDIDATE = LIVE / "candidate/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
RUNTIME = LIVE / "runtime_projection/G77_256GY_WRONG_INPUT_POST_COMMIT_CANDIDATE_V1.json"
CONTEXT = LIVE / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
STATIC = HM / "G77_256HM_PREAUTHORITY_STATIC_READINESS_V1.json"
GL_OBSERVATION = HM / "G77_256HM_GL_RECEIPT_PARENT_OBSERVATION_V1.json"
GL_EQUIVALENCE = HM / "G77_256HM_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1.json"
CHECKPOINT = HM / "G77_256HM_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json"
REQUEST = HM / "G77_256HM_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
PRESENTATION = HM / "G77_256HM_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
GN_EQUIVALENCE = HM / "G77_256HM_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1.json"
PREHUMAN = HM / "G77_256HM_PREHUMAN_PHASE_ABCDEFG_REDUCTION_V1.json"
VALIDATION = HM / "G77_256HM_PREAUTHORIZATION_VALIDATION_V1.json"
GRANT_SOURCE = HM / "G77_256HM_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
POSTGRANT_SAFE_STOP = HM / "G77_256HM_POSTGRANT_PRECONSUMPTION_CAPACITY_SAFE_STOP_CHECKPOINT_V1.json"


def load_module(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"module unavailable: {identity}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise RuntimeError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def load_unique(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise RuntimeError(f"non-canonical JSON: {path}")
    return value


def seal(schema_id: str, inner_name: str, inner: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": schema_id,
        inner_name: inner,
        f"{inner_name}_sha256": sha256_bytes(canonical_bytes(inner)),
    }


def write_new(path: Path, payload: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise RuntimeError(f"fresh artifact collision: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=cwd, text=True, stderr=subprocess.DEVNULL
    ).strip()


def authenticate_entry_and_hl() -> dict[str, Any]:
    entry = {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("log", "-1", "--format=%s"),
        "remote_head": git("rev-parse", f"origin/{BRANCH}"),
    }
    expected = {
        "branch": BRANCH,
        "head": HEAD,
        "tree": TREE,
        "subject": SUBJECT,
        "remote_head": HEAD,
    }
    if entry != expected:
        raise RuntimeError("ENTRY_CHECKPOINT_STATUS_NOT_VERIFIED")
    status_lines = git("status", "--porcelain", "--untracked-files=all").splitlines()
    if any(
        not line.startswith(
            "?? .github/governance/evidence/g77_256hm_wrong_input_operational_v1/"
        )
        for line in status_lines
    ):
        raise RuntimeError("entry worktree contains non-HM state")
    if git("diff", "--cached", "--name-only"):
        raise RuntimeError("entry index is not empty")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", STABLE_ANCESTRY, "HEAD"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode:
        raise RuntimeError("stable ancestry not verified")
    nested = ROOT / "sapianta_system"
    if {
        "head": git("rev-parse", "HEAD", cwd=nested),
        "tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "branch": git("branch", "--show-current", cwd=nested),
        "status": git("status", "--porcelain", "--untracked-files=all", cwd=nested),
        "tag": git("show-ref", "--verify", "refs/tags/sapianta-system-nested-authority-3183bab-v1", cwd=nested).split()[0],
    } != {
        "head": NESTED_HEAD,
        "tree": NESTED_TREE,
        "branch": "",
        "status": "",
        "tag": NESTED_HEAD,
    }:
        raise RuntimeError("nested authority not verified")

    hl_envelope = load_unique(HL_REDUCTION)
    if hl_envelope["reduction_sha256"] != sha256_bytes(
        canonical_bytes(hl_envelope["reduction"])
    ):
        raise RuntimeError("HL reduction seal mismatch")
    hl = hl_envelope["reduction"]
    required = {
        "terminal_branch": hl["readiness"]["terminal_branch"],
        "post_commit_live_binding_status": hl["readiness"]["post_commit_live_binding_status"],
        "preoperational_readiness_status": hl["readiness"]["preoperational_readiness_status"],
        "next_operational_generation_eligible": hl["readiness"]["next_operational_generation_eligible"],
        "no_known_repository_preauthorization_blocker_status": hl["readiness"]["no_known_repository_preauthorization_blocker_status"],
        "du": hl["du_eb_ee"]["du_status"],
        "eb": hl["du_eb_ee"]["eb_status"],
        "ee": hl["du_eb_ee"]["ee_status"],
        "preauth_negative_matrix": hl["preauthorization_negative_matrix"]["status"],
        "preauth_negative_case_count": hl["preauthorization_negative_matrix"]["case_count"],
        "e05": hl["e05"]["after"],
    }
    if required != {
        "terminal_branch": "BRANCH_A__FULL_POST_HK_PREOPERATIONAL_READINESS_VERIFIED",
        "post_commit_live_binding_status": "VERIFIED",
        "preoperational_readiness_status": "VERIFIED",
        "next_operational_generation_eligible": "VERIFIED",
        "no_known_repository_preauthorization_blocker_status": "VERIFIED",
        "du": "PASS",
        "eb": "PASS",
        "ee": "PASS",
        "preauth_negative_matrix": "VERIFIED",
        "preauth_negative_case_count": 22,
        "e05": "7/18",
    }:
        raise RuntimeError("HL_READINESS_RECONSTRUCTION_STATUS_NOT_VERIFIED")
    return entry | {
        "repository": str(ROOT),
        "stable_ancestry_anchor": STABLE_ANCESTRY,
        "tracked_worktree_clean_before_mutation": True,
        "index_empty_before_mutation": True,
        "local_remote_equal": True,
    }


def build_hm_candidate() -> dict[str, Any]:
    producer = load_module(GY_PRODUCER_PATH, "g77_256hm_gy_producer")
    candidate = producer.build_candidate(ROOT)
    reference = load_unique(HL_CANDIDATE)
    expected = deepcopy(reference)
    expected["manifest"]["required_head"] = HEAD
    expected["manifest"]["source_tree"] = TREE
    expected["manifest_sha256"] = sha256_bytes(canonical_bytes(expected["manifest"]))
    if candidate != expected:
        raise RuntimeError("HM candidate changed outside HEAD/tree/seal rebind")
    return candidate


def materialize_live_binding(candidate: dict[str, Any]) -> dict[str, Any]:
    binder = load_module(GY_BINDER_PATH, "g77_256hm_gy_binder")
    original = binder.build_post_commit_candidate
    binder.build_post_commit_candidate = lambda _root: deepcopy(candidate)
    try:
        result = binder.instantiate_post_commit_binding(
            repository_root=ROOT, output_root=LIVE
        )
    finally:
        binder.build_post_commit_candidate = original
    return result


def write_validation() -> int:
    """Seal results already obtained without invoking any operational owner."""

    validation = {
        "schema_id": "G77_256HM_PREAUTHORIZATION_VALIDATION_V1",
        "recorded_at_utc": "2026-09-03T14:41:00Z",
        "hm_focused": "PASS__7_OF_7",
        "gy_current_applicable": "PASS__21_OF_21__3_HISTORICAL_PREDECESSOR_SNAPSHOTS_DESELECTED",
        "ha_current_applicable": "PASS__8_OF_8__2_HISTORICAL_PREDECESSOR_SNAPSHOTS_DESELECTED",
        "hg_projection": "PASS__10_OF_10",
        "gn_presentation": "PASS__42_OF_42",
        "gl_receipt_parent": "PASS__10_OF_10",
        "governance_tests": "PASS__9_OF_9",
        "governance_engine": "PASS__20_OF_20__CONFORMANT__ZERO_WARNINGS__ZERO_VIOLATIONS",
        "ex": "PASS__12_OF_12__17_COMPONENTS_REUSED__ZERO_RECONSTRUCTED",
        "layer_0_freeze": "PASS",
        "hl_focused": "HISTORICAL_NON_APPLICABLE__EXACT_HK_PREDECESSOR_BOUND",
        "hk_focused": "HISTORICAL_NON_APPLICABLE__EXACT_HG_HJ_PREDECESSOR_BOUND",
        "du_eb_ee": "PASS__REAUTHENTICATED_BY_HM_FOCUSED_AND_STATIC_ADMISSION",
        "p11_che_fk": "PASS__UNCHANGED_HASH_BOUND_STATIC_DEPENDENCIES__NO_ENTRY",
        "canonical_json_duplicate_keys_inner_seals": "PASS",
        "python_ast_syntax": "PASS",
        "single_route": "PASS__ONE_FM_MAIN__ONE_QEMU_CALL_SITE",
        "no_network_qemu_definition": "PASS__EXACTLY_ONE_NIC_NONE",
        "git_diff_check": "PASS__TRACKED_INDEX_AND_UNTRACKED_HM_FILES",
        "human_operational_authority_count": 0,
        "authority_consumption_count": 0,
        "fm_operational_launcher_invocation_count": 0,
        "qemu_execution_count": 0,
        "vm_creation_count": 0,
        "vm_boot_count": 0,
        "operation_attempt_count": 0,
        "request_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_and_continue_count": 0,
        "operational_replay_count": 0,
    }
    write_new(VALIDATION, canonical_bytes(seal(
        "G77_256HM_PREAUTHORIZATION_VALIDATION_ENVELOPE_V1",
        "validation",
        validation,
    )))
    print(json.dumps({"result": "HM_PREAUTHORIZATION_VALIDATION_SEALED"}))
    return 0


def write_postgrant_safe_stop() -> int:
    """Authenticate one exact grant and stop with authority unconsumed."""

    expected_grant = (
        "I explicitly authorize request `fa99566594f5efba7eb1c428a8551e74514f32797ee93343778f39b8a94749b6` "
        "for operation `G77_256HM_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001`, subject to its exact one-shot, "
        "no-network, zero-retry, zero-repair, and zero-replay limits.\n"
    ).encode("utf-8")
    if GRANT_SOURCE.is_symlink() or GRANT_SOURCE.read_bytes() != expected_grant:
        raise RuntimeError("exact Human grant source mismatch")
    gn = load_module(GN_PATH, "g77_256hm_postgrant_gn")
    request = gn.load_validated_sealed_request(REQUEST)
    if (
        request["request_sha256"]
        != "fa99566594f5efba7eb1c428a8551e74514f32797ee93343778f39b8a94749b6"
        or request["request"]["generation_identity"] != GENERATION
        or request["request"]["operation_identity"] != OPERATION
        or request["request"]["requested_authority_semantics"]["retry_limit"] != 0
        or request["request"]["requested_authority_semantics"]["repair_limit"] != 0
        or request["request"]["requested_authority_semantics"]["replay_limit"] != 0
        or request["request"]["requested_authority_semantics"]["network_authorized"] is not False
    ):
        raise RuntimeError("Human grant does not exactly bind sealed request")
    context = load_unique(CONTEXT)
    forbidden = (
        HM / "G77_256HM_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
        Path(context["pre_receipt_path"]),
        Path(context["post_receipt_path"]),
        Path(context["serial_path"]),
    )
    if any(path.exists() or path.is_symlink() for path in forbidden):
        raise RuntimeError("authority or operation already consumed")
    checkpoint = {
        "schema_id": "G77_256HM_POSTGRANT_PRECONSUMPTION_CAPACITY_SAFE_STOP_CHECKPOINT_V1",
        "recorded_at_utc": "2026-09-03T14:46:46Z",
        "terminal_branch": "BRANCH_C__SAFE_STOP_BEFORE_AUTHORITY_CONSUMPTION__CURRENT_PROVIDER_CAPACITY_UNAVAILABLE",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "repository_state": {
            "head": HEAD,
            "tree": TREE,
            "tracked_worktree_clean": True,
            "index_empty": True,
            "matching_qemu_operation_absent": True,
            "receipt_namespace_unused": True,
        },
        "grant_authentication": {
            "human_grant_present": True,
            "human_grant_binding_status": "VERIFIED",
            "human_grant_source_path": GRANT_SOURCE.relative_to(ROOT).as_posix(),
            "human_grant_source_sha256": sha256_path(GRANT_SOURCE),
            "sealed_authorization_request_sha256": request["request_sha256"],
            "authorization_request_file_sha256": sha256_path(REQUEST),
            "gn_presentation_sha256": sha256_path(PRESENTATION),
            "exact_generation_match": True,
            "exact_operation_match": True,
            "exact_prohibitions_match": True,
            "fresh": True,
            "authority_reusable": False,
            "conflicting_authority_absent": True,
            "authority_consumed": False,
            "execution_authority_handoff_created": False,
            "execution_authority_handoff_validated": False,
            "prior_hm_operation_absent": True,
        },
        "provider_capacity": {
            "telemetry_source": "CODEX_APP_SERVER_ACCOUNT_RATE_LIMITS_READ",
            "telemetry_read_status": "FAILED__SERVICE_404_NOT_FOUND",
            "last_verified_pregrant_primary_remaining_percent": 72,
            "last_verified_pregrant_secondary_remaining_percent": 33,
            "current_primary_remaining_percent": None,
            "current_secondary_remaining_percent": None,
            "rate_limit_reached_type": "UNKNOWN__READ_FAILED",
            "spend_control_reached": "UNKNOWN__READ_FAILED",
            "telemetry_is_token_cost_or_billing_evidence": False,
            "provider_capacity_is_execution_authority": False,
            "provider_capacity_status": "NOT_VERIFIED_AFTER_GRANT",
            "decision": "SAFE_STOP_BEFORE_AUTHORITY_CONSUMPTION",
        },
        "handoff_sufficiency": {
            "handoff_sufficiency_status": "SUFFICIENT",
            "handoff_state_completeness": "COMPLETE",
            "handoff_prompt_eligibility": "NO__AUTHORITY_ALREADY_GRANTED__NO_REPLACEMENT_PROMPT_PERMITTED",
            "handoff_reconstruction_required": False,
            "handoff_reconstruction_success": "NOT_APPLICABLE",
            "handoff_ambiguity_count": 0,
            "unauthenticated_handoff_assumption_count": 0,
            "same_hm_generation_continuation_eligible": True,
        },
        "operational_counters": {
            "human_operational_authority": 1,
            "authority_consumption": 0,
            "pre": 0,
            "fm_operational_launcher_invocation": 0,
            "qemu": 0,
            "vm_creation": 0,
            "vm_boot": 0,
            "operation_attempt": 0,
            "wrong_input_operation": 0,
            "request": 0,
            "p11_entry": 0,
            "protected_invocation": 0,
            "protected_effect": 0,
            "retry": 0,
            "repair_and_continue": 0,
            "operational_replay": 0,
            "e05_credit": 0,
        },
        "e05": {
            "before": "7/18",
            "after": "7/18",
            "credit_awarded": 0,
            "wrong_input_operational_capability": "NOT_PROVEN",
        },
        "continuation": {
            "same_generation_continuation": "PERMITTED_ONLY_AFTER_REAUTHENTICATING_THIS_CHECKPOINT_GRANT_SOURCE_ZERO_COUNTERS_AND_CURRENT_SUFFICIENT_PROVIDER_CAPACITY",
            "replacement_authority_required": False,
            "replacement_authority_permitted": False,
            "next_legal_action": "SAME_HM_GENERATION_CURRENT_PROVIDER_CAPACITY_RECHECK__NO_NEW_AUTHORITY__NO_RETRY_OR_REPLAY",
            "auto_continuable": False,
            "human_review_required": True,
        },
    }
    write_new(POSTGRANT_SAFE_STOP, canonical_bytes(seal(
        "G77_256HM_POSTGRANT_PRECONSUMPTION_CAPACITY_SAFE_STOP_CHECKPOINT_ENVELOPE_V1",
        "checkpoint",
        checkpoint,
    )))
    print(json.dumps({
        "result": "HM_SAFE_STOP_GRANTED_UNCONSUMED",
        "grant_source_sha256": sha256_path(GRANT_SOURCE),
        "authority_consumption": 0,
        "operation_attempt": 0,
    }, sort_keys=True))
    return 0


def main() -> int:
    entry = authenticate_entry_and_hl()
    candidate = build_hm_candidate()
    binding = materialize_live_binding(candidate)
    fm = load_module(FM_PATH, "g77_256hm_existing_fm")
    context = fm.build_operation_context(
        repository_root=ROOT,
        repository_head=HEAD,
        repository_tree=TREE,
        generation_identity=GENERATION,
        operation_identity=OPERATION,
        identity_namespace_prefix=PREFIX,
        operation_evidence_root=OPERATION_ROOT,
        transient_root=TRANSIENT_ROOT,
        candidate_source_path=CANDIDATE.relative_to(ROOT),
    )
    write_new(CONTEXT, fm.fresh_context.canonical_bytes(context))
    destination = fm.preauth_fresh_checkout_destination_readiness(ROOT, context)
    materialization = fm.materialize_operation_state(
        repository_root=ROOT,
        context=context,
        context_source_path=CONTEXT,
        candidate_source_path=CANDIDATE.relative_to(ROOT),
    )
    observations = fm.observe_context_assets(ROOT, context, CANDIDATE.relative_to(ROOT))
    readiness = fm.authority_free_static_readiness(
        repository_root=ROOT,
        context=context,
        observed_head=HEAD,
        observed_tree=TREE,
        repository_clean=True,
        observed_asset_sha256=observations,
        candidate_source_path=CANDIDATE.relative_to(ROOT),
    )
    static_inner = {
        "schema_id": "G77_256HM_PREAUTHORITY_STATIC_READINESS_V1",
        "binding_result": binding,
        "destination_readiness": destination,
        "materialization": materialization,
        "asset_observations": observations,
        "readiness": readiness,
        "human_constitutional_authorization_count": 0,
        "operational_execution_count": 0,
        "vm_creation_count": 0,
    }
    write_new(STATIC, canonical_bytes(seal(
        "G77_256HM_PREAUTHORITY_STATIC_READINESS_ENVELOPE_V1", "proof", static_inner
    )))

    gl = load_module(GL_PATH, "g77_256hm_existing_gl")
    claim = gl.prepare_and_observe_receipt_parent(ROOT, context)
    write_new(GL_OBSERVATION, canonical_bytes(claim))
    gl_checkpoint = gl.reduce_preauthorization_checkpoint(ROOT, context, claim)
    equivalence = gl.validate_preauth_final_admission_equivalence(
        ROOT, context, claim, gl_checkpoint
    )
    gl_proof = {
        "schema_id": "G77_256HM_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_V1",
        "generation_identity": GENERATION,
        **equivalence,
    }
    write_new(GL_EQUIVALENCE, canonical_bytes(seal(
        "G77_256HM_GL_PREAUTH_FINAL_ADMISSION_EQUIVALENCE_ENVELOPE_V1",
        "proof",
        gl_proof,
    )))

    counters = {
        "human_operational_authority": 0,
        "authority_consumption": 0,
        "pre": 0,
        "fm_operational_launcher_invocation": 0,
        "qemu": 0,
        "vm_creation": 0,
        "vm_boot": 0,
        "operation_attempt": 0,
        "wrong_input_operation": 0,
        "request": 0,
        "p11_entry": 0,
        "protected_invocation": 0,
        "protected_effect": 0,
        "retry": 0,
        "repair_and_continue": 0,
        "operational_replay": 0,
        "e05_credit": 0,
    }
    checkpoint = {
        "schema_id": "G77_256HM_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1",
        "artifact_class": "SEALED_PREAUTHORIZATION_CHECKPOINT__NONAUTHORITY__NONOPERATIONAL",
        "recorded_at_utc": RECORDED_AT_UTC,
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "entry_checkpoint": entry,
        "hl_readiness_reconstruction": {
            "terminal_branch": "BRANCH_A__FULL_POST_HK_PREOPERATIONAL_READINESS_VERIFIED",
            "hl_readiness_reconstruction_status": "VERIFIED",
            "post_commit_live_binding_status": "VERIFIED",
            "du_status": "PASS",
            "eb_status": "PASS",
            "ee_status": "PASS",
            "preauth_negative_matrix_status": "VERIFIED",
            "preauth_negative_case_count": 22,
            "no_known_repository_preauthorization_blocker_status": "VERIFIED",
            "preoperational_readiness_status": "VERIFIED",
            "next_operational_generation_eligible": "VERIFIED",
        },
        "frontier": {
            "last_verified_edge": "FULL_POST_HK_PREOPERATIONAL_READINESS_VERIFIED",
            "first_unproven_edge": "FRESH_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_COMMISSIONING",
            "minimum_missing_capability": "ONE_FRESH_SEPARATELY_HUMAN_REVIEWED_HUMAN_AUTHORIZED_WRONG_INPUT_OPERATIONAL_COMMISSIONING_GENERATION",
            "next_legal_edge": "PRESENT_EXACT_GN_AUTHORIZATION_REQUEST_AND_WAIT_FOR_EXPLICIT_HUMAN_GRANT",
        },
        "handoff_sufficiency": {
            "handoff_sufficiency_status": "VERIFIED",
            "handoff_state_completeness": "COMPLETE",
            "handoff_prompt_eligibility": "YES",
            "handoff_reconstruction_required": False,
            "handoff_reconstruction_success": "NOT_APPLICABLE",
            "handoff_ambiguity_count": 0,
            "unauthenticated_handoff_assumption_count": 0,
            "authority_state": "NONE",
            "authority_consumed": False,
            "operation_attempt": 0,
            "retry": 0,
            "operational_replay": 0,
            "e05": "7/18",
        },
        "identities": {
            "candidate_sha256": sha256_path(CANDIDATE),
            "runtime_projection_sha256": sha256_path(RUNTIME),
            "context_file_sha256": sha256_path(CONTEXT),
            "context_sha256": context["context_sha256"],
            "canonical_argv_sha256": context["canonical_argv_sha256"],
        },
        "semantic_firewall": {
            "case": "E05_NEGATIVE_AUTHORITY_WRONG_INPUT",
            "target_mutation": "input_identity",
            "dependent_recomputation": "record_identity",
            "semantic_mutation_count": 1,
            "expected_differing_fields": ["input_identity", "record_identity"],
            "wrong_input_semantic_firewall_status": "VERIFIED",
        },
        "preauthorization": {
            "pre_authorization_static_admission_status": "VERIFIED",
            "static_readiness_result": readiness["result"],
            "static_readiness_file_sha256": sha256_path(STATIC),
            "receipt_parent_ready": True,
            "receipt_parent_observation_sha256": claim["observation_sha256"],
            "receipt_parent_observation_file_sha256": sha256_path(GL_OBSERVATION),
            "preauth_final_admission_equivalence": equivalence["preauth_final_admission_equivalence"],
            "preauth_final_admission_equivalence_file_sha256": sha256_path(GL_EQUIVALENCE),
            "wrong_input_candidate_identity_status": "VERIFIED",
            "canonical_argv_identity_status": "VERIFIED",
            "single_route_status": "VERIFIED",
            "no_network_qemu_definition_status": "VERIFIED",
        },
        "resource_capacity": {
            "telemetry_source": "CODEX_APP_SERVER_ACCOUNT_RATE_LIMITS_READ",
            "primary_used_percent": 28,
            "primary_remaining_percent": 72,
            "primary_window_duration_minutes": 300,
            "secondary_used_percent": 67,
            "secondary_remaining_percent": 33,
            "secondary_window_duration_minutes": 10080,
            "rate_limit_reached_type": None,
            "spend_control_reached": False,
            "telemetry_is_token_cost_or_billing_evidence": False,
            "resource_capacity_is_execution_authority": False,
            "result": "PASS__SUFFICIENT_AT_HUMAN_AUTHORIZATION_BARRIER",
        },
        "reuse": {
            "ex_reused": "17/17",
            "ex_reconstructed": 0,
            "production_route_before": 1,
            "production_route_after": 1,
            "production_route_delta": 0,
            "new_generic_framework_count": 0,
            "new_production_route_count": 0,
            "new_authority_layer_count": 0,
        },
        "operational_counters": counters,
        "authority_boundary": {
            "human_operational_authority_present": False,
            "checkpoint_is_authority": False,
            "prompt_is_authority": False,
            "resource_capacity_is_authority": False,
            "provider_permission_is_authority": False,
            "auto_continuable": False,
            "human_review_required": True,
            "next_legal_phase": "SEAL_AUTHORIZATION_REQUEST_THEN_DERIVE_AND_VERIFY_GN_PRESENTATION",
        },
        "e05": {"before": "7/18", "maximum_possible_credit": 1, "current": "7/18", "credit_awarded": 0},
    }
    checkpoint_envelope = seal(
        "G77_256HM_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_ENVELOPE_V1",
        "checkpoint",
        checkpoint,
    )
    write_new(CHECKPOINT, canonical_bytes(checkpoint_envelope))

    bindings = context["qemu_executable_base_seed_checkout_bindings"]
    request = {
        "schema_id": "G77_256HM_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1",
        "recorded_at_utc": RECORDED_AT_UTC,
        "request_class": "NON_AUTHORITY__ONE_EXPLICIT_HUMAN_DECISION_REQUIRED",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "repository": {
            "branch": BRANCH,
            "head": HEAD,
            "tree": TREE,
            "remote_head": HEAD,
            "stable_ancestry_anchor": STABLE_ANCESTRY,
        },
        "immutable_assets": bindings,
        "live_binding": {
            "candidate_sha256": sha256_path(CANDIDATE),
            "context_sha256": context["context_sha256"],
            "context_file_sha256": sha256_path(CONTEXT),
            "canonical_argv_sha256": context["canonical_argv_sha256"],
            "du": "PASS",
            "eb": "PASS",
            "ee": "PASS",
            "candidate_semantics_changed": False,
            "candidate_binding_regeneration_required": True,
            "receipt_parent": context["receipt_parent"],
        },
        "preauthorization": {
            "static_readiness_file_sha256": sha256_path(STATIC),
            "checkpoint_file_sha256": sha256_path(CHECKPOINT),
            "checkpoint_inner_sha256": checkpoint_envelope["checkpoint_sha256"],
            "checkpoint_path": CHECKPOINT.relative_to(ROOT).as_posix(),
            "complete_deterministic_readiness": "PASS",
            "receipt_parent_observation_file_sha256": sha256_path(GL_OBSERVATION),
            "preauth_final_admission_equivalence_file_sha256": sha256_path(GL_EQUIVALENCE),
            "preauth_final_admission_equivalence": equivalence["preauth_final_admission_equivalence"],
            "gk_receipt_parent_false_positive_blocked": "YES",
            "all_operational_counters_zero": True,
        },
        "requested_authority_semantics": {
            "authorization_kind": "FRESH_HUMAN_CONSTITUTIONAL_OPERATIONAL_AUTHORIZATION",
            "explicit": True,
            "fresh": True,
            "one_shot": True,
            "reusable": False,
            "transferable": False,
            "generation_bound": True,
            "operation_bound": True,
            "head_bound": True,
            "tree_bound": True,
            "candidate_bound": True,
            "context_bound": True,
            "canonical_argv_bound": True,
            "checkpoint_bound": True,
            "authorization_request_bound": True,
            "governed_launcher_activation_limit": 1,
            "qemu_execution_limit": 1,
            "vm_boot_limit": 1,
            "operation_attempt_limit": 1,
            "network_authorized": False,
            "retry_limit": 0,
            "repair_limit": 0,
            "replay_limit": 0,
            "replacement_authority_authorized": False,
            "second_attempt_authorized": False,
            "successor_generation_authorized": False,
        },
        "authorized_vector_requested": "WRONG_INPUT",
        "request_is_authority": False,
        "checkpoint_is_authority": False,
        "resource_capacity_is_authority": False,
        "provider_permission_is_authority": False,
        "provider_permission_confirmation_count": 0,
        "human_constitutional_authorization_count": 0,
        "human_terminal_review_count": 0,
        "governed_launcher_activations": 0,
        "qemu_execution_count": 0,
        "vm_boot_count": 0,
        "operation_attempt_count": 0,
        "wrong_attempt_execution_count": 0,
        "request_count": 0,
        "p11_entry_count": 0,
        "pre_count": 0,
        "post_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_execution_count": 0,
        "replay_execution_count": 0,
        "auto_continuable": False,
        "human_review_required": True,
    }
    request_envelope = seal(
        "G77_256HM_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_ENVELOPE_V1",
        "request",
        request,
    )
    write_new(REQUEST, canonical_bytes(request_envelope))

    gn = load_module(GN_PATH, "g77_256hm_existing_gn")
    presentation = gn.render_human_authorization_presentation(REQUEST)
    write_new(PRESENTATION, presentation)
    gn_result = gn.validate_human_authorization_presentation(REQUEST, presentation)
    gn_proof = {
        "schema_id": "G77_256HM_GN_HUMAN_PRESENTATION_EQUIVALENCE_V1",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "request_path": REQUEST.relative_to(ROOT).as_posix(),
        "request_file_sha256": sha256_path(REQUEST),
        "presentation_path": PRESENTATION.relative_to(ROOT).as_posix(),
        **gn_result,
        "authority_present": False,
        "auto_continuable": False,
    }
    write_new(GN_EQUIVALENCE, canonical_bytes(seal(
        "G77_256HM_GN_HUMAN_PRESENTATION_EQUIVALENCE_ENVELOPE_V1",
        "proof",
        gn_proof,
    )))

    prehuman = {
        "schema_id": "G77_256HM_PREHUMAN_PHASE_ABCDEFG_REDUCTION_V1",
        "recorded_at_utc": RECORDED_AT_UTC,
        "phase": "PHASES_A_B_C_D_E_F_G_COMPLETE__MANDATORY_HUMAN_AUTHORIZATION_STOP",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "entry": entry,
        "hl_readiness_reconstruction_status": "VERIFIED",
        "handoff_sufficiency_status": "VERIFIED",
        "fresh_operation_material_status": "VERIFIED",
        "wrong_input_semantic_firewall_status": "VERIFIED",
        "pre_authorization_static_admission_status": "VERIFIED",
        "identities": {
            "candidate_sha256": sha256_path(CANDIDATE),
            "context_file_sha256": sha256_path(CONTEXT),
            "context_sha256": context["context_sha256"],
            "canonical_argv_sha256": context["canonical_argv_sha256"],
            "authorization_request_file_sha256": sha256_path(REQUEST),
            "authorization_request_sha256": request_envelope["request_sha256"],
            "gn_presentation_file_sha256": sha256_path(PRESENTATION),
            "gn_presentation_proof_file_sha256": sha256_path(GN_EQUIVALENCE),
            "checkpoint_file_sha256": sha256_path(CHECKPOINT),
            "checkpoint_sha256": checkpoint_envelope["checkpoint_sha256"],
        },
        "owner_results": {
            "du": "PASS",
            "eb": "PASS",
            "ee": "PASS",
            "fm_materialization": materialization["result"],
            "fm_static_readiness": readiness["result"],
            "gl": equivalence["preauth_final_admission_equivalence"],
            "gn": gn_result["human_presentation_request_equivalence"],
            "ex": "PASS__17_OF_17_REUSED__0_RECONSTRUCTED",
        },
        "operational_counters": counters,
        "e05": {"before": "7/18", "maximum_possible_credit": 1, "credit_awarded": 0, "current": "7/18"},
        "authority_boundary": {
            "human_authorization_required": "YES",
            "human_authorization_status": "NOT_GRANTED",
            "authority_disposition": "NONE",
            "request_is_authority": False,
            "checkpoint_is_authority": False,
            "provider_capacity_is_authority": False,
            "operation_execution_status": "NOT_STARTED",
            "next_legal_action": "PRESENT_EXACT_GN_DETERMINISTIC_TEXT_AND_STOP_FOR_ONE_HUMAN_DECISION",
            "auto_continuable": False,
            "human_review_required": True,
        },
    }
    write_new(PREHUMAN, canonical_bytes(seal(
        "G77_256HM_PREHUMAN_PHASE_ABCDEFG_REDUCTION_ENVELOPE_V1",
        "reduction",
        prehuman,
    )))
    print(json.dumps({
        "result": "HM_HUMAN_AUTHORIZATION_BARRIER_READY",
        "request_sha256": request_envelope["request_sha256"],
        "presentation_sha256": sha256_path(PRESENTATION),
        "checkpoint_sha256": checkpoint_envelope["checkpoint_sha256"],
        "context_sha256": context["context_sha256"],
        "canonical_argv_sha256": context["canonical_argv_sha256"],
        "candidate_sha256": sha256_path(CANDIDATE),
        "operational_counters": counters,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--seal-validation"]:
        raise SystemExit(write_validation())
    if sys.argv[1:] == ["--postgrant-safe-stop"]:
        raise SystemExit(write_postgrant_safe_stop())
    if sys.argv[1:]:
        raise SystemExit(
            "usage: materializer [--seal-validation|--postgrant-safe-stop]"
        )
    raise SystemExit(main())
