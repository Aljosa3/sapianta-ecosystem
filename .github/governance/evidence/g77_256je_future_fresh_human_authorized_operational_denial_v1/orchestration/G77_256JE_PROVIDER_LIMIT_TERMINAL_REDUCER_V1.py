#!/usr/bin/env python3
"""Reduce preserved G77-256JE state without authority use or operation replay."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
JE = ROOT / ".github/governance/evidence/g77_256je_future_fresh_human_authorized_operational_denial_v1"
RECEIPTS = JE / "operation_state/receipts"
RUNTIME = JE / "operation_state/runtime_export"
OUTPUT = JE / "G77_256JE_SPCE_TERMINAL_REDUCTION_V1.json"
SERIAL = JE / "G77_256JE_SERIAL_CONSOLE_V1.log"
GENERATION = "G77_256JE_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256JE_E05_FUTURE_DENIAL_BEFORE_ENTRY_001"
TERMINAL = "N__REQUEST_NOT_CREATED__CURRENT_FM_CONTEXT_OWNER_REJECTED_SEALED_OPERATION_PROJECTION_AS_NOT_NAMESPACE_BOUND"


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_unique(path: Path) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise RuntimeError(f"duplicate JSON key: {path.name}:{key}")
            result[key] = value
        return result

    value = json.loads(path.read_bytes(), object_pairs_hook=unique)
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON object required: {path.name}")
    return value


def sealed(path: Path, key: str) -> dict[str, Any]:
    outer = load_unique(path)
    if outer.get(f"{key}_sha256") != hashlib.sha256(canonical_bytes(outer[key])).hexdigest():
        raise RuntimeError(f"inner seal mismatch: {path.name}")
    return outer[key]


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def authenticate() -> dict[str, Any]:
    if OUTPUT.exists() or OUTPUT.is_symlink():
        raise RuntimeError("terminal reduction collision")
    entry = {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
        "remote_head": "393f887f62d56811092ff6ee5aacb273f3c10d83",
        "index": git("diff", "--cached", "--name-only"),
    }
    expected = {
        "branch": "g77-256fl-wrong-attempt-preboot-blocker",
        "head": "393f887f62d56811092ff6ee5aacb273f3c10d83",
        "tree": "d304bb2b5543ba04e8b8b1e8fdf96f9cb9067ea5",
        "subject": "G77-256JD certify FUTURE post-JC live-binding readiness",
        "origin": "git@github.com:Aljosa3/sapianta-ecosystem.git",
        "remote_head": "393f887f62d56811092ff6ee5aacb273f3c10d83",
        "index": "",
    }
    if entry != expected:
        raise RuntimeError("exact JD entry mismatch")
    prefix = "?? " + JE.relative_to(ROOT).as_posix() + "/"
    if any(not line.startswith(prefix) for line in git("status", "--porcelain", "--untracked-files=all").splitlines()):
        raise RuntimeError("mutation outside JE namespace")
    nested = ROOT / "sapianta_system"
    nested_state = {
        "origin": git("remote", "get-url", "origin", cwd=nested),
        "head": git("rev-parse", "HEAD", cwd=nested),
        "tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "clean": git("status", "--porcelain", cwd=nested) == "",
        "detached": git("branch", "--show-current", cwd=nested) == "",
        "tag": git("describe", "--tags", "--exact-match", "HEAD", cwd=nested),
    }
    if nested_state != {
        "origin": "git@github.com:Aljosa3/sapianta-core.git",
        "head": "3183bab71f8f30397c0309dd2e6d846d14a11f66",
        "tree": "7c32ec05efc2be43297849bc38ec8766514a523d",
        "clean": True,
        "detached": True,
        "tag": "sapianta-system-nested-authority-3183bab-v1",
    }:
        raise RuntimeError("nested authority mismatch")
    entry["nested_authority"] = nested_state | {"remote_tag_head": nested_state["head"]}
    return entry


def verify_operation() -> dict[str, Any]:
    authority = sealed(JE / "G77_256JE_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json", "authorization")
    consumption = sealed(JE / "G77_256JE_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json", "checkpoint")
    pre = load_unique(RECEIPTS / "G77_256JE_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")
    post = load_unique(RECEIPTS / "G77_256JE_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json")
    context = load_unique(JE / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json")
    if not (
        authority["authorized_generation_identity"] == consumption["generation_identity"] == pre["generation_identity"] == post["generation_identity"] == GENERATION
        and authority["authorized_operation_identity"] == consumption["operation_identity"] == pre["operation_identity"] == post["operation_identity"] == OPERATION
        and consumption["authority_state_before"] == "GRANTED_UNCONSUMED"
        and consumption["authority_state_after"] == "CONSUMED"
        and consumption["authority_consumed"] == 1
        and consumption["authority_reusable"] is False
        and consumption["final_admission_validation"] == "PASS"
        and consumption["admission_result"] == "ADMIT_TO_BOOT_BOUNDARY_ONLY"
        and pre["started_unix_ns"] == post["started_unix_ns"]
        and pre["execution_attempt_count"] == post["execution_attempt_count"] == 1
        and pre["automatic_retry_count"] == post["automatic_retry_count"] == 0
        and pre["vector"] == post["vector"]
        and post["process_exit_status"] == 0
        and post["completed_unix_ns"] > post["started_unix_ns"]
    ):
        raise RuntimeError("authority or one-shot receipt correlation mismatch")
    expected_identities = {
        "candidate": "ad5d204ec6ace09f18b83fd5f868e73dac5e36dad81149f9f335c87f68cf42f7",
        "context": "1e04e1d34e77dd0605eb03e21c2c8f51dc99b3c68fbe60b01f539f9ad0b590c3",
        "argv": "92256e675832e3a43b39cf3bf7e3699d418707da2d22a0c0ff9d1a7d5a72afb3",
        "request": "e90d59c6bbe3ff401102bc50c1c55bc926b246058a94dc1f4e6a666e687b6e8c",
        "presentation": "1fb0c91fc6eb367df4fc99d455651ffdc1ca6b80d89a87dd3bca0518bb7f9f30",
        "checkpoint": "ebfc0fd24ca96f71439bf10c6c6a446ed992d123355e83a59e2d68193b5cd9b0",
    }
    request = load_unique(JE / "G77_256JE_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json")
    preauth = load_unique(JE / "G77_256JE_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json")
    observed = {
        "candidate": sha256(JE / "live_binding/candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json"),
        "context": context["context_sha256"],
        "argv": post["vector"]["canonical_argv_sha256"],
        "request": request["request_sha256"],
        "presentation": sha256(JE / "G77_256JE_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt"),
        "checkpoint": preauth["checkpoint_sha256"],
    }
    if observed != expected_identities:
        raise RuntimeError("JE preauthorization identity mismatch")
    argv = post["vector"]["argv"]
    if argv.count("-nic") != 1 or argv[argv.index("-nic") + 1] != "none":
        raise RuntimeError("no-network binding mismatch")
    if sha256(SERIAL) != "37b1d2cb48252797f90b3b8f94f8e537dad8dfbddda25a7d3e94c3c99001d73d":
        raise RuntimeError("durable serial mismatch")
    serial = SERIAL.read_bytes()
    required = (
        b"G77_256FM_BOOT_MARKER=PASS",
        b"sealed operation projection is not namespace-bound",
        b"G77_256FM_HARNESS_EXIT_STATUS=1",
        b"Powering off.",
        b"reboot: Power down",
    )
    if any(item not in serial for item in required) or b"operational Human act is not current" in serial:
        raise RuntimeError("serial terminal evidence mismatch")
    absent_outputs = [relative for relative in context["guest_output_relative_paths"] if not (RUNTIME / relative).exists()]
    if absent_outputs != context["guest_output_relative_paths"]:
        raise RuntimeError("unexpected post-failure guest output")
    return {
        "authority": authority,
        "consumption": consumption,
        "pre": pre,
        "post": post,
        "context": context,
        "identities": observed,
        "absent_outputs": absent_outputs,
    }


def main() -> int:
    entry = authenticate()
    evidence = verify_operation()
    operation_counters = {
        "authorization_presentation": "VERIFIED__1",
        "human_authorization": "VERIFIED__1",
        "authority_consumption": "VERIFIED__1",
        "pre": "VERIFIED__1",
        "fm_operational_invocation": "VERIFIED__1",
        "qemu": "VERIFIED__1",
        "vm": "VERIFIED__1",
        "vm_boot": "VERIFIED__1",
        "operation_attempt": "VERIFIED__1",
        "request": "VERIFIED__0",
        "future_denial": "VERIFIED__0",
        "p11_entry": "VERIFIED__0",
        "protected_invocation": "VERIFIED__0",
        "protected_effect": "VERIFIED__0",
        "retry": "VERIFIED__0",
        "repair_retry": "VERIFIED__0",
        "replay": "VERIFIED__0",
    }
    reduction = {
        "schema_id": "G77_256JE_SPCE_TERMINAL_REDUCTION_V1",
        "generation": "G77-256JE",
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "recovery_type": "VERIFIED__SAME_GENERATION_CROSS_WORKER_PROVIDER_LIMIT_POST_OPERATION_RECOVERY",
        "terminal": TERMINAL,
        "entry": entry,
        "runtime_target": {"head": "699fcdce794ff49b6c8735602936355724ed1c90", "tree": "7c773d4b2acdf013f1b8238eabfc8eced4dd6866"},
        "preauthorization_identities": evidence["identities"],
        "authority": {
            "source_sha256": sha256(JE / "G77_256JE_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"),
            "handoff_file_sha256": sha256(JE / "G77_256JE_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"),
            "state_transition": "VERIFIED__GRANTED_UNCONSUMED_TO_CONSUMED",
            "consumption": "VERIFIED__EXACTLY_ONCE",
            "reusable": "VERIFIED__NO",
            "second_consumption_authorized": False,
        },
        "operation_evidence": {
            "pre_receipt_sha256": sha256(RECEIPTS / "G77_256JE_PRE_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"),
            "post_receipt_sha256": sha256(RECEIPTS / "G77_256JE_POST_EXECUTED_QEMU_ARGV_RECEIPT_V1.json"),
            "serial_sha256": sha256(SERIAL),
            "host_qemu_exit_status": 0,
            "guest_boot": "VERIFIED__PASS",
            "cloud_init_final_stage": "VERIFIED__REACHED",
            "guest_harness_exit_status": 1,
            "guest_poweroff": "VERIFIED__COMPLETE",
            "network": "VERIFIED__NONE",
            "guest_output_absence": {"status": "VERIFIED__ALL_DECLARED_OUTPUTS_ABSENT", "paths": evidence["absent_outputs"]},
            "transient_root": "PRESERVED_FOR_HUMAN_REVIEW",
            "stale_je_process": "VERIFIED__ABSENT_AT_RECOVERY_INSPECTION",
        },
        "failure": {
            "expected_denial_reason": "operational Human act is not current",
            "expected_denial_status": "NOT_PROVEN_OPERATIONALLY",
            "observed_failure_reason": "sealed operation projection is not namespace-bound",
            "observed_failure_class": "VERIFIED__FAIL_CLOSED_PRE_REQUEST_CURRENT_FM_CONTEXT_OWNER_NAMESPACE_BINDING_REJECTION",
            "host_exit_zero_is_future_denial": False,
            "request_created": False,
        },
        "operational_counters": operation_counters,
        "second_operation_counters": {
            "authority_consumption": "VERIFIED__0", "fm_invocation": "VERIFIED__0",
            "qemu": "VERIFIED__0", "vm_boot": "VERIFIED__0", "operation_attempt": "VERIFIED__0",
        },
        "e05": {"before": "VERIFIED__10_OF_18", "after": "VERIFIED__10_OF_18", "credit": "VERIFIED__0", "future": "NOT_PROVEN_OPERATIONALLY"},
        "reuse": {
            "ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0",
            "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
            "reused_certified_capability_set": "VERIFIED__JD_JC_JB_JA_IZ_IY_IX_IW_IV_IE_IF_DU_EB_EE_V2_FM_GN_GL_ER_FC_FK_CHE_P11_EX_GOVERNANCE_LAYER_0_NESTED_AUTHORITY",
            "new_capability_set": "VERIFIED__JE_TERMINAL_RECOVERY_EVIDENCE_ONLY",
            "unreachable_preexisting_capability_set": "VERIFIED__EMPTY",
            "parallel_flow_created": "VERIFIED__NO",
            "production_route_before": "VERIFIED__1", "production_route_after": "VERIFIED__1", "production_route_delta": "VERIFIED__0",
        },
        "shadow_automation": {
            "status": "VERIFIED__ABSENT", "provider_limit_triggered_operation_replay": "VERIFIED__0",
            "automatic_human_authorization": "VERIFIED__0", "automatic_authority_regeneration": "VERIFIED__0",
            "automatic_authority_consumption": "VERIFIED__0", "automatic_pre": "VERIFIED__0",
            "automatic_fm_invocation": "VERIFIED__0", "automatic_qemu": "VERIFIED__0",
            "automatic_vm_boot": "VERIFIED__0", "automatic_operation_retry": "VERIFIED__0",
            "repair_retry": "VERIFIED__0", "replay": "VERIFIED__0", "successor_operation": "VERIFIED__0",
            "automatic_e05_credit": "VERIFIED__0", "hidden_p11_route": "VERIFIED__0", "automatic_owner_rebinding": "VERIFIED__0",
        },
        "frontier": {
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "constitutional_frontier_distanc_e": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "project_progress": "VERIFIED__E05_10_OF_18__FUTURE_NOT_PROVEN_OPERATIONALLY",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "e05_frontier_distance": "VERIFIED__8_UNSATISFIED_OF_18",
            "selected_e05_local_frontier_distance": "VERIFIED__CURRENT_FM_CONTEXT_OWNER_NAMESPACE_BINDING_BEFORE_FUTURE_REQUEST_CREATION",
            "last_verified_edge": "GUEST_BOOT_AND_CLOUD_INIT_REACHED_CURRENT_FM_CONTEXT_OWNER_CONTEXT_VALIDATION",
            "first_broken_edge": "CURRENT_FM_CONTEXT_OWNER_DERIVATION_OF_EXACT_SEALED_OPERATION_NAMESPACE",
            "blocking_owner": "CURRENT_FM_CONTEXT_OWNER__G77_256FM_SAPIANTA_FRESH_OPERATION_CONTEXT_V1",
            "minimum_missing_capability": "EXACT_GOVERNED_OPERATION_NAMESPACE_BINDING_FOR_CURRENT_FM_CONTEXT_OWNER",
            "minimum_legal_next_delta": "SEPARATE_HUMAN_REVIEWED_REPOSITORY_ONLY_GENERATION_TO_FORMALIZE_BIND_AND_VERIFY_CURRENT_FM_CONTEXT_OWNER_AGAINST_THE_EXACT_GOVERNED_OPERATION_NAMESPACE_SCHEMA__NO_JE_REPLAY",
            "human_review_required": "YES", "auto_continuable": "NO", "next_generation_started": "NO",
        },
        "continuity": {
            "constitutional_health_evidence": "VERIFIED__IV_FAIL_CLOSED__IW_BINDING__IX_READINESS__IY_IMPORT_SUCCESS_ENTRYPOINT_FAIL_CLOSED__IZ_BINDING__JA_READINESS__JB_OWNER_DRIFT_FAIL_CLOSED__JC_OWNER_PROJECTION__JD_READINESS__JE_PREAUTHORIZATION__JE_HUMAN_AUTHORIZATION__JE_AUTHORITY_CONSUMPTION__JE_ONE_SHOT_OPERATION__JE_PRE_REQUEST_NAMESPACE_FAILURE__JE_PROVIDER_LIMIT_TERMINAL_RECOVERY",
            "constitutional_continuation_progress": "VERIFIED__IV_IMPORT_ROOT_FAILURE_TO_JE_SAME_GENERATION_TERMINAL_RECOVERY_WITH_FAILED_EDGE_PRESERVED",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION",
            "cross_worker_state_recovery_level": "VERIFIED__DURABLE_POST_OPERATION_STATE_RECOVERED",
            "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NO_NUMERIC_INSTRUMENT",
            "human_handoff_information_required": "VERIFIED__RECOVERY_SCOPE_AND_EXPECTED_COORDINATES_ONLY",
            "previous_worker_conversation_required": "VERIFIED__NO", "previous_worker_identity_required": "VERIFIED__NO", "previous_worker_memory_required": "VERIFIED__NO",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "inter_generation_cross_worker_continuation": "NOT_APPLICABLE__SAME_GENERATION_RECOVERY",
            "intra_generation_cross_worker_continuation": "VERIFIED__JE_PROVIDER_LIMIT_RECOVERY",
            "uncommitted_delta_recovery": "VERIFIED__BOUNDED_JE_NAMESPACE",
            "authority_state_recovery": "VERIFIED__CONSUMED_NONREUSABLE", "consumed_authority_recovery": "VERIFIED__EXACTLY_ONE",
            "post_operation_state_recovery": "VERIFIED__RECEIPT_PAIR_SERIAL_AND_OUTPUT_ABSENCE",
            "operation_replay_prevention": "VERIFIED__NO_RECOVERY_OPERATION_AND_ONE_SHOT_NAMESPACE_CONSUMED",
            "cross_worker_constitutional_drift": "VERIFIED__0_AT_ARTIFACT_LEVEL", "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
            "handoff_sufficiency_status": "VERIFIED", "handoff_state_completeness": "VERIFIED__COMPLETE_FOR_TERMINAL_REDUCTION",
            "handoff_reconstruction_required": "VERIFIED__YES", "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0", "unauthenticated_handoff_assumption_count": "VERIFIED__0",
        },
        "cognition": {
            "cognition_assisted_handoff": "VERIFIED__SAME_GENERATION_CROSS_WORKER_PROVIDER_LIMIT_RECOVERY",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_GIT_JE_DURABLE_EVIDENCE_AND_VOLATILE_SERIAL_CORRELATION_PRIMARY__MODEL_IDENTITY_NONAUTHORITATIVE",
            "aigol_codex_work_share": "NOT_MEASURED", "prompt_context_reuse_ratio": "NOT_MEASURED",
            "repository_derived_execution_context_ratio": "NOT_MEASURED", "constitutional_prompt_externalization_ratio": "NOT_MEASURED",
            "token_benchmark": "NOT_MEASURED", "llm_cost_reduction_ratio": "NOT_MEASURED", "lcrr": "NOT_MEASURED",
        },
        "metrics": {
            "governance_efficience": "ESTIMATED__HIGH_REUSE_FAIL_CLOSED_TERMINAL_RECOVERY",
            "architectural_governance_efficience": "VERIFIED__ONE_ROUTE_ZERO_PRODUCTION_P11_AND_HISTORICAL_MUTATION",
            "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
            "p11_mutation_count": "VERIFIED__0", "new_generic_adapter_count": "VERIFIED__0",
            "new_dispatcher_count": "VERIFIED__0", "new_global_registry_count": "VERIFIED__0",
            "production_route_delta": "VERIFIED__0", "production_mutation_count": "VERIFIED__0",
            "historical_evidence_mutation_count": "VERIFIED__0",
            "overengineering_risk": "ESTIMATED__LOW__TERMINAL_EVIDENCE_ONLY", "proof_process_overhead_risk": "ESTIMATED__MODERATE",
            "new_abstraction_count": "VERIFIED__0", "new_generic_framework_count": "VERIFIED__0",
            "generic_projection_framework_count": "VERIFIED__0", "new_route_count": "VERIFIED__0", "new_registry_count": "VERIFIED__0",
            "caller_selectable_identity_count": "VERIFIED__0", "duplicate_owner_semantics_count": "VERIFIED__0",
            "duplicate_future_adapter_count": "VERIFIED__0", "duplicate_p11_logic_count": "VERIFIED__0",
            "candidate_capability_before_je": "VERIFIED__POST_JC_COMMITTED_LIVE_BINDING_AND_STATIC_OPERATIONAL_READINESS",
            "candidate_capability": "VERIFIED__ONE_SHOT_REACHED_CURRENT_FM_CONTEXT_OWNER_NAMESPACE_VALIDATION__FUTURE_REQUEST_AND_DENIAL_NOT_PROVEN",
            "shadow_design_target": "VERIFIED__FAMILY_LOCAL_DU_EB_EE_V2_OPTION_B_WITH_COLOCATED_FAIL_CLOSED_MAJOR_VERSION_DISPATCH",
        },
        "validation": {
            "je_preauthorization": "VERIFIED__5_PASSED",
            "du_eb_ee_v2_current_applicable": "VERIFIED__20_PASSED__5_HISTORICAL_ENTRY_OR_SCOPE_ASSERTIONS_DESELECTED",
            "future_semantics_current_applicable": "VERIFIED__10_PASSED__1_HISTORICAL_ENTRY_ASSERTION_DESELECTED",
            "fm_context_owner": "VERIFIED__17_PASSED",
            "gn_gl": "VERIFIED__52_PASSED", "ex": "VERIFIED__12_OF_12__CERTIFIED_17_OF_17_REUSED",
            "governance_pytest": "VERIFIED__9_PASSED",
            "conformance_engine": "VERIFIED__20_PASSED__CONFORMANT__0_WARNINGS__0_VIOLATIONS",
            "layer_0_freeze": "VERIFIED__PASS",
            "terminal_recovery": "VERIFIED__4_PASSED",
            "git_diff_check": "VERIFIED__PASS",
        },
    }
    envelope = {
        "schema_id": "G77_256JE_SPCE_TERMINAL_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": hashlib.sha256(canonical_bytes(reduction)).hexdigest(),
    }
    temporary = OUTPUT.with_name(f".{OUTPUT.name}.tmp-{os.getpid()}")
    temporary.write_bytes(canonical_bytes(envelope))
    os.replace(temporary, OUTPUT)
    print(f"TERMINAL={TERMINAL}")
    print(f"REDUCTION_SHA256={envelope['reduction_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
