#!/usr/bin/env python3
"""Repository-only formalization for the Human-selected G77-256JF Option A."""

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
JF = ROOT / ".github/governance/evidence/g77_256jf_future_current_fm_context_owner_exact_governed_operation_namespace_binding_v1"
JE = ROOT / ".github/governance/evidence/g77_256je_future_fresh_human_authorized_operational_denial_v1"
FM_OWNER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
FM_LAUNCHER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
CONTEXT = JE / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
REQUEST = JE / "G77_256JE_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json"
PRESENTATION = JE / "G77_256JE_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"
HUMAN_SOURCE = JE / "G77_256JE_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
HANDOFF = JE / "G77_256JE_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
CONSUMPTION = JE / "G77_256JE_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json"
PRE = JE / "operation_state/receipts/G77_256JE_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
POST = JE / "operation_state/receipts/G77_256JE_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"
TERMINAL = JF / "G77_256JF_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
REPORT = JF / "G77_256JF_G48_IMPLEMENTATION_REPORT_V1.md"

ENTRY_HEAD = "02faf1a8de38869e07750095e5dce03284e51822"
ENTRY_TREE = "6cef6be2203941799adf805541095e211df556ed"
ENTRY_SUBJECT = "G77-256JE record FUTURE pre-request namespace binding failure"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
IF_HEAD = "699fcdce794ff49b6c8735602936355724ed1c90"
IF_TREE = "7c773d4b2acdf013f1b8238eabfc8eced4dd6866"
GENERATION = "G77_256JE_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256JE_E05_FUTURE_DENIAL_BEFORE_ENTRY_001"
CONTEXT_SHA256 = "1e04e1d34e77dd0605eb03e21c2c8f51dc99b3c68fbe60b01f539f9ad0b590c3"
CURRENT_FM_OWNER_HASH_BEFORE = "9a5b0c5a542b00352cfde6aef399c72f589ce1b2fffae1911983854e378fdbb1"
CURRENT_FM_OWNER_HASH_AFTER = "cef00e0fc99bc67a75648bcc65d54c90577467a3e0f12bec46097ae01b6543e5"
REQUEST_SHA256 = "e90d59c6bbe3ff401102bc50c1c55bc926b246058a94dc1f4e6a666e687b6e8c"
HUMAN_SOURCE_SHA256 = "86f6f6448950468a4e688451e7d823b7b5dfce14fde387ae40c304ee6eb21e1c"
HANDOFF_FILE_SHA256 = "b1820f620f19de2c567b900a6534733119f62098d834be0af937613c50b16ec9"
CANONICAL_ARGV_SHA256 = "92256e675832e3a43b39cf3bf7e3699d418707da2d22a0c0ff9d1a7d5a72afb3"
CANDIDATE_SHA256 = "ad5d204ec6ace09f18b83fd5f868e73dac5e36dad81149f9f335c87f68cf42f7"
EXACT_ROOT = (
    "/home/pisarna/work/sapianta-fl/.github/governance/evidence/"
    "g77_256je_future_fresh_human_authorized_operational_denial_v1/operation_state"
)
VECTOR_ONLY_ROOT = (
    "/home/pisarna/work/sapianta-fl/.github/governance/evidence/"
    "g77_256je_future_operational_v1/operation_state"
)
TERMINAL_ID = (
    "A__FUTURE_CURRENT_FM_CONTEXT_OWNER_SEALED_OPERATION_EVIDENCE_ROOT_"
    "NAMESPACE_BINDING_REPOSITORY_ONLY_VERIFIED"
)


class JFError(ValueError):
    """One deterministic fail-closed repository-only JF error."""


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
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise JFError(f"DUPLICATE_KEY:{key}")
        result[key] = value
    return result


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw, object_pairs_hook=unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise JFError(f"MALFORMED_JSON:{path}") from exc
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise JFError(f"NONCANONICAL_JSON:{path}")
    return value


def load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise JFError(f"MODULE_UNAVAILABLE:{path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def context_identity(context: dict[str, Any]) -> str:
    unsealed = {key: value for key, value in context.items() if key != "context_sha256"}
    return sha256_bytes(canonical_bytes(unsealed))


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def authenticate_selection_checkpoint() -> dict[str, Any]:
    nested = ROOT / "sapianta_system"
    observed = {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("log", "-1", "--format=%s"),
        "origin": git("remote", "get-url", "origin"),
        "index_empty": git("diff", "--cached", "--name-only") == "",
        "nested_head": git("rev-parse", "HEAD", cwd=nested),
        "nested_tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "nested_tag": git("describe", "--tags", "--exact-match", "HEAD", cwd=nested),
        "nested_detached": git("branch", "--show-current", cwd=nested) == "",
        "nested_clean": git("status", "--porcelain=v1", cwd=nested) == "",
    }
    expected = {
        "branch": BRANCH,
        "head": ENTRY_HEAD,
        "tree": ENTRY_TREE,
        "subject": ENTRY_SUBJECT,
        "origin": ORIGIN,
        "index_empty": True,
        "nested_head": NESTED_HEAD,
        "nested_tree": NESTED_TREE,
        "nested_tag": NESTED_TAG,
        "nested_detached": True,
        "nested_clean": True,
    }
    if observed != expected:
        raise JFError("SELECTION_CHECKPOINT_AUTHENTICATION_FAILED")
    return observed


def reject_root_substitution(context: dict[str, Any], substituted_root: str) -> str:
    mutated = deepcopy(context)
    mutated["operation_evidence_root"] = substituted_root
    mutated_identity = context_identity(mutated)
    if mutated_identity == CONTEXT_SHA256:
        raise JFError("OPERATION_ROOT_SUBSTITUTION_DID_NOT_CHANGE_CONTEXT_IDENTITY")
    request = load_canonical(REQUEST)["request"]
    handoff = load_canonical(HANDOFF)["authorization"]
    if (
        mutated_identity == request["live_binding"]["context_sha256"]
        or mutated_identity == handoff["authorized_context_sha256"]
    ):
        raise JFError("OPERATION_ROOT_SUBSTITUTION_RETAINED_AUTHENTICATED_IDENTITY")
    return mutated_identity


def option_a_proof_gate() -> dict[str, Any]:
    context = load_canonical(CONTEXT)
    request_envelope = load_canonical(REQUEST)
    request = request_envelope["request"]
    handoff_envelope = load_canonical(HANDOFF)
    handoff = handoff_envelope["authorization"]
    consumption = load_canonical(CONSUMPTION)["checkpoint"]
    pre = load_canonical(PRE)
    post = load_canonical(POST)
    presentation = PRESENTATION.read_text(encoding="utf-8")
    human_source = HUMAN_SOURCE.read_text(encoding="utf-8").replace("\\_", "_")

    identities = {
        context_identity(context),
        context["context_sha256"],
        request["live_binding"]["context_sha256"],
        handoff["authorized_context_sha256"],
        pre["context_sha256"],
        post["context_sha256"],
    }
    generations = {
        context["generation_identity"], request["generation_identity"],
        handoff["authorized_generation_identity"], consumption["generation_identity"],
        pre["generation_identity"], post["generation_identity"],
    }
    operations = {
        context["operation_identity"], request["operation_identity"],
        handoff["authorized_operation_identity"], consumption["operation_identity"],
        pre["operation_identity"], post["operation_identity"],
    }
    if identities != {CONTEXT_SHA256} or generations != {GENERATION} or operations != {OPERATION}:
        raise JFError("OPTION_A_AUTHENTICATED_CORRELATION_FAILED")
    if context["operation_evidence_root"] != EXACT_ROOT:
        raise JFError("OPTION_A_EXACT_ROOT_MISMATCH")
    if request_envelope["request_sha256"] != REQUEST_SHA256:
        raise JFError("OPTION_A_REQUEST_IDENTITY_MISMATCH")
    if sha256_path(HUMAN_SOURCE) != HUMAN_SOURCE_SHA256:
        raise JFError("OPTION_A_HUMAN_SOURCE_IDENTITY_MISMATCH")
    if sha256_path(HANDOFF) != HANDOFF_FILE_SHA256:
        raise JFError("OPTION_A_HANDOFF_FILE_IDENTITY_MISMATCH")
    required_presentation = {
        f'AUTHORIZATION_REQUEST_SHA256 "{REQUEST_SHA256}"',
        f'CONTEXT_SHA256 "{CONTEXT_SHA256}"',
        f'GENERATION_ID "{GENERATION}"',
        f'OPERATION_ID "{OPERATION}"',
    }
    if not all(item in presentation for item in required_presentation):
        raise JFError("OPTION_A_PRESENTATION_CORRELATION_FAILED")
    if not all(item in human_source for item in (REQUEST_SHA256, CONTEXT_SHA256, OPERATION)):
        raise JFError("OPTION_A_HUMAN_SOURCE_CORRELATION_FAILED")
    if (
        handoff["authorized_candidate_sha256"] != CANDIDATE_SHA256
        or handoff["authorized_canonical_argv_sha256"] != CANONICAL_ARGV_SHA256
        or handoff["authorized_repository_head"] != context["repository_head"]
        or handoff["authorized_repository_tree"] != context["repository_tree"]
        or handoff["authorization_reusable"] is not False
        or consumption["authority_handoff_file_sha256"] != HANDOFF_FILE_SHA256
        or consumption["authority_consumed"] != 1
        or consumption["authority_reusable"] is not False
        or pre["execution_authority_file_sha256"] != HANDOFF_FILE_SHA256
        or post["execution_authority_file_sha256"] != HANDOFF_FILE_SHA256
    ):
        raise JFError("OPTION_A_AUTHORITY_OR_RECEIPT_CORRELATION_FAILED")
    argv = context["canonical_argv"]
    if (
        context["canonical_argv_sha256"] != CANONICAL_ARGV_SHA256
        or context["candidate_manifest_sha256"] != CANDIDATE_SHA256
        or not any(EXACT_ROOT + "/runtime_export" in argument for argument in argv)
        or not any(EXACT_ROOT + "/guest_harness" in argument for argument in argv)
        or context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["head"] != IF_HEAD
        or context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["tree"] != IF_TREE
    ):
        raise JFError("OPTION_A_ARGV_CANDIDATE_OR_RUNTIME_CORRELATION_FAILED")

    vector_only_identity = reject_root_substitution(context, VECTOR_ONLY_ROOT)
    other_generation_identity = reject_root_substitution(
        context, EXACT_ROOT.replace("g77_256je_", "g77_256jd_")
    )
    other_operation_identity = reject_root_substitution(
        context, EXACT_ROOT.replace("operational_denial", "operational_request")
    )
    return {
        "result": "VERIFIED__OPTION_A_PROOF_GATE_PASS",
        "namespace_authority_owner": "SEALED_CONTEXT_OPERATION_EVIDENCE_ROOT",
        "exact_root": EXACT_ROOT,
        "context_identity": CONTEXT_SHA256,
        "generation_correlation": "VERIFIED",
        "operation_correlation": "VERIFIED",
        "candidate_correlation": "VERIFIED",
        "canonical_argv_correlation": "VERIFIED",
        "repository_baseline_correlation": "VERIFIED",
        "runtime_target_correlation": "VERIFIED",
        "human_authorization_correlation": "VERIFIED",
        "consumed_authority_correlation": "VERIFIED",
        "pre_post_receipt_correlation": "VERIFIED",
        "caller_override": "VERIFIED__REJECTED_BY_AUTHENTICATED_IDENTITY_CHANGE",
        "vector_only_substitution_identity": vector_only_identity,
        "cross_generation_substitution_identity": other_generation_identity,
        "cross_operation_substitution_identity": other_operation_identity,
    }


def terminal_reduction() -> dict[str, Any]:
    proof = option_a_proof_gate()
    return {
        "schema_id": "G77_256JF_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": "G77-256JF",
        "terminal": TERMINAL_ID,
        "mode": "REPOSITORY_ONLY__NO_OPERATIONAL_AUTHORITY__NO_OPERATION",
        "human_architectural_selection": "VERIFIED__OPTION_A",
        "recovery": {
            "type": "SAME_GENERATION_CROSS_WORKER_PROVIDER_LIMIT_RECOVERY",
            "provider_limit_is_execution_authority": False,
            "uncommitted_delta_recovery": "VERIFIED__YES",
            "preexisting_recovered_jf_delta": [
                FM_LAUNCHER.as_posix(),
                FM_OWNER.as_posix(),
                REPORT.relative_to(ROOT).as_posix(),
                TERMINAL.relative_to(ROOT).as_posix(),
                Path(__file__).resolve().relative_to(ROOT).as_posix(),
                (JF / "tests/test_g77_256jf_operation_namespace_binding_v1.py")
                .relative_to(ROOT).as_posix(),
            ],
            "recovery_worker_additional_delta": [
                REPORT.relative_to(ROOT).as_posix(),
                TERMINAL.relative_to(ROOT).as_posix(),
                Path(__file__).resolve().relative_to(ROOT).as_posix(),
                (JF / "tests/test_g77_256jf_operation_namespace_binding_v1.py")
                .relative_to(ROOT).as_posix(),
            ],
        },
        "entry": {
            "head": ENTRY_HEAD, "tree": ENTRY_TREE, "remote_head": ENTRY_HEAD,
            "branch": BRANCH, "subject": ENTRY_SUBJECT,
            "nested_head": NESTED_HEAD, "nested_tree": NESTED_TREE,
        },
        "runtime_target": {"head": IF_HEAD, "tree": IF_TREE},
        "namespace_binding": proof,
        "implementation": {
            "je_observed_namespace": (
                "g77_256je_future_fresh_human_authorized_operational_denial_v1/"
                "operation_state"
            ),
            "historical_vector_only_derived_namespace": (
                "g77_256je_future_operational_v1/operation_state"
            ),
            "current_fm_owner_binding_status": "VERIFIED__EXACT_SEALED_ROOT_REPOSITORY_ONLY",
            "current_fm_owner_hash_before": CURRENT_FM_OWNER_HASH_BEFORE,
            "current_fm_owner_hash_after": CURRENT_FM_OWNER_HASH_AFTER,
            "fm_launcher_binding_status": "VERIFIED__CURRENT_OWNER_HASH_UPDATED",
            "caller_selectable_namespace_count": 0,
            "cross_generation_namespace_rejection": "VERIFIED",
            "cross_operation_namespace_rejection": "VERIFIED",
            "namespace_escape_rejection": "VERIFIED",
            "symlink_escape_rejection": "VERIFIED",
        },
        "je_terminal": (
            "N__REQUEST_NOT_CREATED__CURRENT_FM_CONTEXT_OWNER_REJECTED_SEALED_"
            "OPERATION_PROJECTION_AS_NOT_NAMESPACE_BOUND"
        ),
        "preservation": {
            "jc_jd_projection": "VERIFIED",
            "future_semantics": "VERIFIED__UNCHANGED",
            "du_eb_ee_v2": "VERIFIED__UNCHANGED",
            "p11_mutation_count": 0,
            "historical_je_mutation_count": 0,
            "production_route_before": 1,
            "production_route_after": 1,
            "production_route_delta": 0,
            "ex_reused": "VERIFIED__17_OF_17",
            "ex_reconstructed": "VERIFIED__0",
        },
        "operational_counters": {key: 0 for key in (
            "human_authorization", "authority_consumption", "pre", "fm_operational_invocation",
            "qemu", "vm", "vm_boot", "operation_attempt", "request", "p11_entry",
            "protected_invocation", "protected_effect", "retry", "repair_retry", "replay",
        )},
        "e05": {"before": "VERIFIED__10_OF_18", "after": "VERIFIED__10_OF_18", "credit": "VERIFIED__0", "future": "NOT_PROVEN_OPERATIONALLY"},
        "metrics": {
            "project_progress": "VERIFIED__E05_10_OF_18__JF_NAMESPACE_BINDING_REPOSITORY_ONLY_VERIFIED",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "constitutional_frontier_distanc_e": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "e05_frontier_distance": "VERIFIED__8_UNSATISFIED_OF_18",
            "selected_e05_local_frontier_distance": "VERIFIED__POST_COMMIT_LIVE_BINDING_READINESS_THEN_FRESH_COMMISSIONING",
            "governance_efficience": "ESTIMATED__HIGH_REUSE_NARROW_EXISTING_OWNER_DELTA",
            "architectural_governance_efficience": "VERIFIED__ONE_ROUTE_ZERO_REGISTRIES_ZERO_P11_MUTATION",
            "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
            "overengineering_risk": "ESTIMATED__LOW",
            "proof_process_overhead_risk": "ESTIMATED__MODERATE",
            "aigol_codex_work_share": "NOT_MEASURED",
            "prompt_context_reuse_ratio": "NOT_MEASURED",
            "repository_derived_execution_context_ratio": "ESTIMATED__DOMINANT__NO_NUMERIC_INSTRUMENT",
            "constitutional_prompt_externalization_ratio": "NOT_MEASURED",
            "token_benchmark": "NOT_MEASURED",
            "llm_cost_reduction_ratio": "NOT_MEASURED",
            "lcrr": "NOT_MEASURED",
        },
        "frontier": {
            "last_verified_edge": "CURRENT_FM_CONTEXT_OWNER_ACCEPTS_AUTHENTICATED_EXACT_SEALED_JE_OPERATION_NAMESPACE_REPOSITORY_ONLY",
            "first_broken_edge": "POST_COMMIT_CURRENT_OWNER_LIVE_BINDING_NOT_YET_RATIFIED",
            "blocking_owner": "HUMAN_REVIEW_COMMIT_AND_SEPARATE_POST_COMMIT_READINESS",
            "minimum_missing_capability": "POST_COMMIT_LIVE_BINDING_READINESS_FOR_UPDATED_CURRENT_FM_CONTEXT_OWNER",
            "minimum_legal_next_delta": "HUMAN_REVIEW_THEN_COMMIT_REMOTE_RATIFICATION_THEN_SEPARATE_POST_COMMIT_READINESS__NO_OPERATION_IN_JF",
        },
        "overengineering": {
            "new_abstraction_count": 1,
            "new_generic_framework_count": 0,
            "generic_projection_framework_count": 0,
            "new_route_count": 0,
            "new_registry_count": 0,
            "new_namespace_registry_count": 0,
            "caller_selectable_identity_count": 0,
            "caller_selectable_namespace_count": 0,
            "duplicate_owner_semantics_count": 0,
            "duplicate_future_adapter_count": 0,
            "duplicate_p11_logic_count": 0,
        },
        "candidate": {
            "before": "ONE_SHOT_REACHED_CURRENT_FM_CONTEXT_OWNER_NAMESPACE_VALIDATION__FUTURE_REQUEST_AND_DENIAL_NOT_PROVEN",
            "after": "CURRENT_FM_CONTEXT_OWNER_EXACT_GOVERNED_OPERATION_NAMESPACE_BINDING_REPOSITORY_ONLY_VERIFIED",
            "shadow_design_target": "FAMILY_LOCAL_DU_EB_EE_V2_OPTION_B_WITH_COLOCATED_FAIL_CLOSED_MAJOR_VERSION_DISPATCH",
        },
        "reuse": {
            "reused_certified_capability_set": "VERIFIED__JE_JD_JC_JB_JA_IZ_IY_IX_IW_IV_IE_IF_DU_EB_EE_V2_FM_GN_GL_ER_FC_FK_CHE_P11_EX_GOVERNANCE_LAYER_0_NESTED_AUTHORITY",
            "new_capability_set": "VERIFIED__CURRENT_FM_OWNER_SEALED_OPERATION_EVIDENCE_ROOT_EXACT_NAMESPACE_VALIDATION",
            "unreachable_preexisting_capability_set": "VERIFIED__EMPTY",
            "parallel_flow_created": "VERIFIED__NO",
        },
        "continuity": {
            "constitutional_health_evidence": "VERIFIED__IV_FAIL_CLOSED__IW_BINDING__IX_READINESS__IY_IMPORT_SUCCESS_ENTRYPOINT_FAIL_CLOSED__IZ_BINDING__JA_READINESS__JB_OWNER_DRIFT_FAIL_CLOSED__JC_OWNER_PROJECTION__JD_READINESS__JE_PREAUTHORIZATION__JE_HUMAN_AUTHORIZATION__JE_AUTHORITY_CONSUMPTION__JE_ONE_SHOT_OPERATION__JE_PRE_REQUEST_NAMESPACE_FAILURE__JE_TERMINAL_RECOVERY__JE_COMMITTED_REMOTE_RATIFIED__JF_ARCHITECTURAL_SELECTION_STOP__HUMAN_OPTION_A_SELECTION__JF_OPTION_A_PROOF_GATE__JF_REPOSITORY_ONLY_BINDING__JF_PROVIDER_LIMIT_RECOVERY__JF_VALIDATION_REDUCTION",
            "constitutional_continuation_progress": "VERIFIED__IV_IMPORT_ROOT_FAILURE__IW_IMPORT_ROOT_BINDING__IX_POST_COMMIT_IMPORT_READINESS__IY_IMPORT_SUCCESS_AND_ENTRYPOINT_ABSENCE__IZ_ENTRYPOINT_STATIC_BINDING__JA_POST_COMMIT_LIVE_BINDING_READINESS__JB_PREAUTH_GUEST_CONTEXT_OWNER_DRIFT__JC_CURRENT_OWNER_PROJECTION_RECONCILIATION__JD_POST_JC_COMMIT_LIVE_BINDING_AND_OPERATIONAL_READINESS__JE_PREAUTHORIZATION__JE_FRESH_HUMAN_AUTHORIZATION__JE_SINGLE_AUTHORITY_CONSUMPTION__JE_SINGLE_FM_QEMU_VM_OPERATION__JE_PRE_REQUEST_NAMESPACE_BOUND_FAILURE__JE_SAME_GENERATION_TERMINAL_RECOVERY__JE_COMMITTED_REMOTE_RATIFIED__JF_ARCHITECTURAL_AMBIGUITY__HUMAN_OPTION_A_SELECTION__JF_OPTION_A_PROOF_GATE__JF_OPTION_A_EXISTING_IMPLEMENTATION__JF_PROVIDER_LIMIT_RECOVERY__JF_CURRENT_TERMINAL",
        },
        "cognition": {
            "cognition_assisted_handoff": "VERIFIED__SAME_GENERATION_CROSS_WORKER_PROVIDER_LIMIT_RECOVERY",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_GIT_BASELINE_EXISTING_UNCOMMITTED_JF_DELTA_COMMITTED_JE_EVIDENCE_HUMAN_OPTION_A_SELECTION_AND_DETERMINISTIC_REPOSITORY_ONLY_VERIFICATION_PRIMARY__WORKER_IDENTITY_AND_PROVIDER_NONAUTHORITATIVE",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION",
            "cross_worker_state_recovery_level": "VERIFIED__COMMITTED_JE_STATE_EXISTING_UNCOMMITTED_JF_DELTA_AND_OPTION_A_SELECTION_RECOVERED",
            "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NO_NUMERIC_INSTRUMENT",
            "human_handoff_information_required": "VERIFIED__OPTION_A_ARCHITECTURAL_SELECTION_ONLY",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_identity_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "inter_generation_cross_worker_continuation": "VERIFIED__JE_TO_JF",
            "intra_generation_cross_worker_continuation": "VERIFIED__JF_IMPLEMENTATION_TO_JF_PROVIDER_LIMIT_RECOVERY",
            "uncommitted_delta_recovery": "VERIFIED__YES",
            "authority_state_recovery": "VERIFIED__JE_CONSUMED_NONREUSABLE__JF_ZERO_AUTHORITY",
            "consumed_authority_recovery": "VERIFIED__JE_EXACTLY_ONE__JF_ZERO",
            "post_operation_state_recovery": "VERIFIED__JE_TERMINAL_EVIDENCE_RECONSTRUCTED",
            "operation_replay_prevention": "VERIFIED__NO_JF_OPERATION_OR_JE_REPLAY",
            "cross_worker_constitutional_drift": "VERIFIED__0_AT_ARTIFACT_LEVEL",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0_OUTSIDE_AUTHENTICATED_JF_BOUNDARY",
            "handoff_sufficiency_status": "VERIFIED",
            "handoff_state_completeness": "VERIFIED__COMPLETE_FOR_JF_RECOVERY_VALIDATION_AND_REDUCTION",
            "handoff_reconstruction_required": "VERIFIED__NO__EXISTING_DELTA_AND_EXPLICIT_CHECKPOINT_SUFFICIENT",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0_AFTER_HUMAN_SELECTION",
            "unauthenticated_handoff_assumption_count": "VERIFIED__0",
            "repository_state_ambiguity": "VERIFIED__0",
            "architectural_design_ambiguity": "VERIFIED__3_MODELS_BEFORE_HUMAN_SELECTION__0_AFTER_OPTION_A_SELECTION",
            "human_architectural_selection_status": "VERIFIED__OPTION_A",
        },
        "validation": {
            "jf_focused": "VERIFIED__28_PASSED",
            "fm_context_owner": "VERIFIED__17_PASSED",
            "hg_jc_jd_current_applicable": "VERIFIED__9_PLUS_16_PLUS_13_PASSED",
            "historical_checkpoint_pinned": "VERIFIED__HG_1__JC_4__JD_6__JE_1",
            "future_semantics": "VERIFIED__10_PASSED__1_HISTORICAL_ENTRY_DESELECTED",
            "gn_gl": "VERIFIED__52_PASSED",
            "du_eb_ee_v2": "VERIFIED__12_STRUCTURAL_PASSED__EXPECTED_PRECOMMIT_LIVE_BINDING_FAILURE__RUNTIME_TARGET_SELECTION_WORKTREE_DRIFT",
            "fk_che": "VERIFIED__11_PASSED",
            "ex": "VERIFIED__12_OF_12__17_OF_17_REUSED",
            "governance_pytest": "VERIFIED__9_PASSED",
            "conformance_engine": "VERIFIED__20_PASSED__CONFORMANT__0_WARNINGS__0_VIOLATIONS",
            "layer_0_freeze": "VERIFIED__PASS",
            "git_diff_check": "VERIFIED__PASS",
        },
        "shadow_automation_status": "VERIFIED__ABSENT",
        "human_review_required": True,
        "auto_continuable": False,
    }


def terminal_envelope() -> dict[str, Any]:
    reduction = terminal_reduction()
    return {
        "schema_id": "G77_256JF_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }
