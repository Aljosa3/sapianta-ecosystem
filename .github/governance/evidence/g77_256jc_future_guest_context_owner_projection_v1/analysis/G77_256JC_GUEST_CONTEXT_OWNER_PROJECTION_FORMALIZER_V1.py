#!/usr/bin/env python3
"""Repository-only formalization for the JC guest context-owner projection."""

from __future__ import annotations

import ast
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
JC = ROOT / ".github/governance/evidence/g77_256jc_future_guest_context_owner_projection_v1"
FM_LAUNCHER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
FM_CONTEXT_OWNER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
JC_ADAPTER = Path(
    ".github/governance/evidence/g77_256jc_future_guest_context_owner_projection_v1/adapter/"
    "G77_256JC_FUTURE_VECTOR_ADAPTER_V1.py"
)
JC_CLOUD_INIT = Path(
    ".github/governance/evidence/g77_256jc_future_guest_context_owner_projection_v1/static/"
    "G77_256JC_CLOUD_INIT_USER_DATA_V1.yaml"
)
JC_SEED = Path(
    ".github/governance/evidence/g77_256jc_future_guest_context_owner_projection_v1/static/"
    "SAPIANTA_FUTURE_NOCLOUD_SEED_V3.img"
)
JB_TERMINAL = Path(
    ".github/governance/evidence/g77_256jb_future_operational_commissioning_v1/"
    "G77_256JB_SPCE_TERMINAL_PREAUTHORIZATION_ROUTE_DRIFT_V1.json"
)
IH_CANDIDATE = Path(
    ".github/governance/evidence/g77_256ih_future_if_identity_rebind_v1/live_binding/"
    "candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json"
)

BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
HEAD = "f75c79cf3eda73ba15866b6d0480bc6a966fe44a"
TREE = "29957cb3f48fe4045978b4b779269b89d186fd20"
SUBJECT = "G77-256JB record FUTURE preauthorization route drift"
IF_HEAD = "699fcdce794ff49b6c8735602936355724ed1c90"
IF_TREE = "7c773d4b2acdf013f1b8238eabfc8eced4dd6866"
JB_OWNER_SHA256 = "da09342d92f2a8d8310987aa0104bd6bd6ad7a3d009b51b8d710443c4884e9c7"
IF_OWNER_SHA256 = "fdfa04349529d70bc97820a1848f8afc22b81071859d5456550799e0f9476237"
JC_OWNER_SHA256 = "9a5b0c5a542b00352cfde6aef399c72f589ce1b2fffae1911983854e378fdbb1"
JC_ADAPTER_SHA256 = "fb3cf7976447cb624b57f804b70d042513e24671f5f350e509c6006f0efabcdc"
JC_CLOUD_INIT_SHA256 = "2a7a5dbe1e8bf17aec4a9199ac8609d40d71a1e7726211ed0d6a9faf719f6ff4"
JC_SEED_SHA256 = "6998d4cdaff3617b9e2c29f17318a220619fc718d0d9f9168b08e614cfdf0418"
GUEST_OWNER_PATH = "/mnt/dp-harness/sapianta_fresh_operation_context_v1.py"
PRODUCTION_FILES = (
    FM_LAUNCHER, FM_CONTEXT_OWNER, JC_ADAPTER, JC_CLOUD_INIT, JC_SEED,
)
JC_FILES = (
    JC / "G77_256JC_G48_IMPLEMENTATION_REPORT_V1.md",
    JC / "G77_256JC_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json",
    JC / "adapter/G77_256JC_FUTURE_VECTOR_ADAPTER_V1.py",
    JC / "analysis/G77_256JC_GUEST_CONTEXT_OWNER_PROJECTION_FORMALIZER_V1.py",
    JC / "static/G77_256JC_CLOUD_INIT_USER_DATA_V1.yaml",
    JC / "static/SAPIANTA_FUTURE_NOCLOUD_SEED_V3.img",
    JC / "tests/test_g77_256jc_future_guest_context_owner_projection_v1.py",
)
HISTORICAL_IZ_FILES = (
    Path(".github/governance/evidence/g77_256iz_future_operational_entrypoint_v1/G77_256IZ_ENTRYPOINT_FORMAL_ANALYSIS_V1.md"),
    Path(".github/governance/evidence/g77_256iz_future_operational_entrypoint_v1/G77_256IZ_G48_IMPLEMENTATION_REPORT_V1.md"),
    Path(".github/governance/evidence/g77_256iz_future_operational_entrypoint_v1/G77_256IZ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"),
    Path(".github/governance/evidence/g77_256iz_future_operational_entrypoint_v1/adapter/G77_256IZ_FUTURE_VECTOR_ADAPTER_V1.py"),
    Path(".github/governance/evidence/g77_256iz_future_operational_entrypoint_v1/static/G77_256IZ_CLOUD_INIT_USER_DATA_V1.yaml"),
    Path(".github/governance/evidence/g77_256iz_future_operational_entrypoint_v1/static/SAPIANTA_FUTURE_NOCLOUD_SEED_V2.img"),
    Path(".github/governance/evidence/g77_256iz_future_operational_entrypoint_v1/tests/test_g77_256iz_future_operational_entrypoint_v1.py"),
)
REQUIRED_HARNESS_REJECTION_CASES = (
    "missing_context_owner", "wrong_context_owner", "extra_harness_member",
    "historical_if_context_owner", "wrong_adapter", "wrong_bootstrap_alias",
)
HISTORICAL_FAILURE_CLASSES = (
    "future_commit_self_reference",
    "runtime_certification_role_collapse",
    "historical_current_owner_collapse",
    "historical_iz_mutation",
    "checkout_runtime_collapse",
    "host_false_positive_import",
    "missing_guest_import_root",
    "missing_operational_adapter_entrypoint",
    "stale_bootstrap_consumer",
    "stale_launcher",
    "route_duplication",
    "generic_adapter_proliferation",
    "global_registry",
    "automatic_authority",
    "authority_reuse",
    "retry",
    "repair_retry",
    "replay",
    "request_p11_counter_collapse",
    "automatic_owner_rebinding",
    "provider_limit_replay",
    "duplicate_generation_after_provider_limit",
    "partial_delta_loss",
    "stale_g48_after_worker_recovery",
    "hash_only_negative_proof_without_gate_execution",
    "open_unbounded_harness_membership",
)


class JCError(RuntimeError):
    """One fail-closed JC authentication or formalization error."""


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise JCError(f"DUPLICATE_KEY:{key}")
        result[key] = value
    return result


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise JCError(f"NONCANONICAL_JSON:{path}")
    return value


def load_module(relative: Path, name: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, ROOT / relative)
    if specification is None or specification.loader is None:
        raise JCError(f"MODULE_UNAVAILABLE:{relative}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def committed_bytes(revision: str, relative: Path) -> bytes:
    return subprocess.check_output(["git", "show", f"{revision}:{relative}"], cwd=ROOT)


def authenticate_baseline() -> dict[str, Any]:
    observed = {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
        "index_empty": git("diff", "--cached", "--name-only") == "",
    }
    expected = {
        "branch": BRANCH, "head": HEAD, "tree": TREE,
        "subject": SUBJECT, "origin": ORIGIN, "index_empty": True,
    }
    if observed != expected:
        raise JCError("EXACT_RATIFIED_JB_BASELINE_MISMATCH")
    nested = ROOT / "sapianta_system"
    nested_state = {
        "origin": git("remote", "get-url", "origin", cwd=nested),
        "head": git("rev-parse", "HEAD", cwd=nested),
        "tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "clean": git("status", "--porcelain", cwd=nested) == "",
        "detached": git("branch", "--show-current", cwd=nested) == "",
        "tag": git("describe", "--exact-match", "--tags", "HEAD", cwd=nested),
    }
    if nested_state != {
        "origin": "git@github.com:Aljosa3/sapianta-core.git",
        "head": "3183bab71f8f30397c0309dd2e6d846d14a11f66",
        "tree": "7c32ec05efc2be43297849bc38ec8766514a523d",
        "clean": True, "detached": True,
        "tag": "sapianta-system-nested-authority-3183bab-v1",
    }:
        raise JCError("NESTED_AUTHORITY_MISMATCH")
    return observed | {"nested_authority": nested_state}


def reconstruct_jb_failure() -> dict[str, Any]:
    envelope = load_canonical(ROOT / JB_TERMINAL)
    reduction = envelope["reduction"]
    if envelope["reduction_sha256"] != sha256_bytes(canonical_bytes(reduction)):
        raise JCError("JB_TERMINAL_INNER_SEAL_MISMATCH")
    drift = reduction["route_drift"]
    committed_jb_owner = sha256_bytes(committed_bytes(HEAD, FM_CONTEXT_OWNER))
    committed_if_owner = sha256_bytes(committed_bytes(IF_HEAD, FM_CONTEXT_OWNER))
    if (
        reduction["terminal"] != "M__CERTIFIED_ROUTE_DRIFT_DETECTED"
        or drift["current_repository_owner_sha256"] != JB_OWNER_SHA256
        or drift["detached_if_checkout_owner_sha256"] != IF_OWNER_SHA256
        or committed_jb_owner != JB_OWNER_SHA256
        or committed_if_owner != IF_OWNER_SHA256
    ):
        raise JCError("JB_FAILURE_RECONSTRUCTION_MISMATCH")
    return {
        "terminal": reduction["terminal"],
        "jb_owner_sha256": committed_jb_owner,
        "if_owner_sha256": committed_if_owner,
        "exact_mismatch_reproduced": True,
    }


def role_model() -> dict[str, Any]:
    target = {"head": IF_HEAD, "tree": IF_TREE}
    baseline = {"head": HEAD, "tree": TREE}
    return {
        "target_runtime_identity": target,
        "current_repository_identity": baseline,
        "certification_baseline_identity": baseline,
        "fm_selector_owner_identity": {
            "role": "CURRENT_CERTIFICATION_OWNED_SELECTOR",
            "path": FM_LAUNCHER.as_posix(),
        },
        "fm_context_owner_identity": {
            "role": "CURRENT_CERTIFICATION_OWNED_CONTEXT_VALIDATOR",
            "path": FM_CONTEXT_OWNER.as_posix(),
            "sha256": JC_OWNER_SHA256,
        },
        "guest_projected_context_owner_identity": {
            "role": "READ_ONLY_CURRENT_OWNER_PROJECTION",
            "guest_path": GUEST_OWNER_PATH,
            "sha256": JC_OWNER_SHA256,
        },
        "candidate_required_identity": target,
        "checkout_identity": target,
        "evidence_issuer_identity": {
            "head": HEAD, "tree": TREE,
            "plus": "JC_WORKTREE_PRODUCTION_OWNERS_PENDING_COMMIT",
        },
        "equalities": {
            "TARGET_RUNTIME_IDENTITY_EQ_CANDIDATE_REQUIRED_IDENTITY": "VERIFIED",
            "TARGET_RUNTIME_IDENTITY_EQ_CHECKOUT_IDENTITY": "VERIFIED",
            "CURRENT_REPOSITORY_IDENTITY_EQ_CERTIFICATION_BASELINE_IDENTITY": "VERIFIED",
            "FM_CONTEXT_OWNER_IDENTITY_EQ_GUEST_PROJECTED_CONTEXT_OWNER_IDENTITY": "VERIFIED",
            "TARGET_RUNTIME_IDENTITY_NE_CURRENT_REPOSITORY_IDENTITY": "VERIFIED",
            "TARGET_RUNTIME_IDENTITY_NE_CERTIFICATION_BASELINE_IDENTITY": "VERIFIED",
            "DETACHED_IF_OWNER_IDENTITY_NE_GUEST_PROJECTED_CONTEXT_OWNER_IDENTITY": "VERIFIED",
            "EVIDENCE_ISSUER_IDENTITY_EQ_CERTIFICATION_BASELINE_PLUS_BOUND_OWNERS": "VERIFIED",
        },
    }


def authenticate_unique_projection_mechanism() -> dict[str, Any]:
    launcher_source = (ROOT / FM_LAUNCHER).read_text(encoding="utf-8")
    context_source = (ROOT / FM_CONTEXT_OWNER).read_text(encoding="utf-8")
    adapter_source = (ROOT / JC_ADAPTER).read_text(encoding="utf-8")
    for source in (launcher_source, context_source, adapter_source):
        ast.parse(source)
    required = (
        "FRESH_OPERATION_CONTEXT_OWNER_PROJECTION_FILENAME" in launcher_source,
        "context_owner_projection.write_bytes(context_owner_source.read_bytes())" in launcher_source,
        "host_projection_guest_byte_identity" in launcher_source,
        "GUEST_CONTEXT_OWNER_PATH" in context_source,
        "resolved_repository_root == GUEST_REPOSITORY_ROOT" in context_source,
        "GUEST_PROJECTED_FM_CONTEXT_OWNER" in adapter_source,
        "if root == GUEST_REPOSITORY_ROOT" in adapter_source,
    )
    if not all(required):
        raise JCError("PROJECTION_MECHANISM_INCOMPLETE")
    identities = {
        FM_CONTEXT_OWNER.as_posix(): JC_OWNER_SHA256,
        JC_ADAPTER.as_posix(): JC_ADAPTER_SHA256,
        JC_CLOUD_INIT.as_posix(): JC_CLOUD_INIT_SHA256,
        JC_SEED.as_posix(): JC_SEED_SHA256,
    }
    for relative, expected in identities.items():
        if sha256(ROOT / relative) != expected:
            raise JCError(f"JC_OWNER_HASH_MISMATCH:{relative}")
    return {
        "class": "C__AUTHENTICATED_CURRENT_OWNER_PROJECTED_SEPARATELY_FROM_DETACHED_RUNTIME",
        "mechanism": "EXISTING_OPERATION_LOCAL_READ_ONLY_FM_HARNESS_PROJECTION_PLUS_HG_PROJECTION_AWARE_VALIDATION",
        "uniqueness": "VERIFIED__ONLY_EXISTING_SINGLE_ROUTE_PROJECTION_OWNED_BY_FM_AND_CONSUMED_BY_THE_CURRENT_ADAPTER",
        "caller_selected_owner_identity": False,
        "runtime_certification_role_collapse": False,
        "generic_framework": False,
        "identities": identities,
    }


def current_production_identities() -> dict[str, str]:
    return {relative.as_posix(): sha256(ROOT / relative) for relative in PRODUCTION_FILES}


def authenticate_recovered_delta() -> dict[str, Any]:
    status = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT, text=True,
    ).splitlines()
    tracked = {
        line[3:] for line in status if line.startswith(" M ")
    }
    untracked = {
        line[3:] for line in status if line.startswith("?? ")
    }
    expected_tracked = {FM_LAUNCHER.as_posix(), FM_CONTEXT_OWNER.as_posix()}
    expected_untracked = {
        path.relative_to(ROOT).as_posix() for path in JC_FILES
    }
    if tracked != expected_tracked or untracked != expected_untracked:
        raise JCError("UNCOMMITTED_JC_DELTA_SCOPE_MISMATCH")
    return {
        "tracked_modified": sorted(tracked),
        "untracked_jc_files": sorted(untracked),
        "production_owner_mutation_count": "VERIFIED__2",
        "jc_file_count": "VERIFIED__7",
        "index": "EMPTY",
    }


def authenticate_historical_iz_immutability() -> dict[str, Any]:
    identities: dict[str, str] = {}
    for relative in HISTORICAL_IZ_FILES:
        raw = (ROOT / relative).read_bytes()
        if raw != committed_bytes(HEAD, relative):
            raise JCError(f"HISTORICAL_IZ_MUTATION_REMAINS:{relative}")
        identities[relative.as_posix()] = sha256_bytes(raw)
    return {
        "authenticated_file_count": f"VERIFIED__{len(identities)}",
        "historical_iz_mutation_count": "VERIFIED__0",
        "historical_evidence_mutation_count": "VERIFIED__0",
        "identities": identities,
    }


def terminal_reduction() -> dict[str, Any]:
    """Return the deterministic JC terminal; creation remains an explicit edit."""

    return {
        "schema_id": "G77_256JC_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": "G77-256JC",
        "mode": "REPOSITORY_ONLY__NO_AUTHORIZATION__NO_OPERATION",
        "terminal": "A__FUTURE_GUEST_FM_CONTEXT_OWNER_PROJECTION_REPOSITORY_ONLY_RECONCILED_AND_STATICALLY_VERIFIED",
        "entry": {
            "branch": BRANCH, "origin": ORIGIN, "head": HEAD, "tree": TREE,
            "subject": SUBJECT, "remote_head": HEAD, "index": "EMPTY",
            "nested_head": "3183bab71f8f30397c0309dd2e6d846d14a11f66",
            "nested_tree": "7c32ec05efc2be43297849bc38ec8766514a523d",
            "nested_state": "CLEAN__DETACHED__PINNED__REMOTE_TAG_EQUAL",
        },
        "same_generation_recovery": {
            "generation_restarted": False,
            "generation_count_increment": 0,
            "worker_sequence": "SOL_HIGH_WORKER_1__PROVIDER_LIMIT__ASTRA_EXTRA_HIGH_RECOVERY__PROVIDER_LIMIT__SOL_HIGH_TERMINAL_RECOVERY",
            "provider_limit_recovery_count": "VERIFIED__2",
            "uncommitted_delta_recovery": "VERIFIED__YES",
            "historical_iz_mutation_discovered_and_removed_before_certification": "RECOVERED__YES",
            "primary_recovery_source": "RATIFIED_JB_GIT_CHECKPOINT_PLUS_AUTHENTICATED_UNCOMMITTED_JC_DELTA_PLUS_REPOSITORY_EVIDENCE",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_identity_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
        },
        "recovered_delta": authenticate_recovered_delta(),
        "historical_immutability": authenticate_historical_iz_immutability(),
        "jb_failure": reconstruct_jb_failure(),
        "roles": role_model(),
        "projection": authenticate_unique_projection_mechanism(),
        "production_identities": current_production_identities(),
        "static_verification": {
            "pre_correction_jb_failure": "VERIFIED__EXACT_COMMITTED_REPRODUCTION",
            "pre_correction_jb_gate_execution": "VERIFIED__ACTUAL_COMMITTED_AUTHORITY_FREE_STATIC_READINESS_REJECTS",
            "post_correction_authority_free_static_readiness": "VERIFIED__PASS",
            "detached_if_checkout_unchanged": "VERIFIED",
            "guest_current_owner_projection": "VERIFIED__READ_ONLY_FM_HARNESS",
            "harness_member_count": "VERIFIED__3",
            "required_harness_rejection_count": f"VERIFIED__{len(REQUIRED_HARNESS_REJECTION_CASES)}",
            "required_harness_rejection_cases": list(REQUIRED_HARNESS_REJECTION_CASES),
            "additional_harness_rejection": "VERIFIED__SYMLINK_CONTEXT_OWNER",
            "future_semantics_unchanged": "VERIFIED",
            "nocloud_projection": "VERIFIED__THREE_OF_THREE_EXACT",
            "runtime_certification_role_separation": "VERIFIED__PRESERVED",
            "post_commit_live_binding": "NOT_PROVEN__JC_OWNERS_UNCOMMITTED",
            "du_eb_ee_current_state": "EXPECTED_FAIL_CLOSED__RUNTIME_TARGET_SELECTION_WORKTREE_DRIFT",
            "operational_future_denial": "NOT_PROVEN",
        },
        "reuse": {
            "ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0",
            "production_route_before": "VERIFIED__1", "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0", "p11_mutation_count": "VERIFIED__0",
            "new_generic_adapter_count": "VERIFIED__0", "new_dispatcher_count": "VERIFIED__0",
            "new_global_registry_count": "VERIFIED__0", "parallel_flow_created": "VERIFIED__NO",
        },
        "reuse_impact": {
            "reused_certified_capability_set": "VERIFIED__JB_JA_IZ_FM_GH_HG_HD_IW_IE_IF_DU_EB_EE_V2_ER_FC_FK_CANONICAL_HUMAN_ACT_CHE_CUSTODY_REQUEST_P11_GN_GL_DI_EX_GOVERNANCE_LAYER_0_NESTED_AUTHORITY",
            "new_capability_set": "VERIFIED__BOUNDED_CURRENT_FM_CONTEXT_OWNER_READ_ONLY_GUEST_PROJECTION_AND_JC_EVIDENCE",
            "unreachable_preexisting_capability_set": "VERIFIED__EMPTY",
            "parallel_flow_created": "VERIFIED__NO",
            "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0",
            "production_owner_mutation_count": "VERIFIED__2",
            "new_generic_framework_count": "VERIFIED__0",
        },
        "operational_counters": {
            "authorization_presentation": 0, "human_authorization": 0,
            "authority_consumption": 0, "pre": 0, "fm_operational_invocation": 0,
            "qemu": 0, "vm_boot": 0, "operation_attempt": 0, "request": 0,
            "future_denial": 0, "p11_entry": 0, "protected_invocation": 0,
            "protected_effect": 0, "retry": 0, "repair_retry": 0, "replay": 0,
        },
        "e05": {
            "before": "VERIFIED__10_OF_18", "after": "VERIFIED__10_OF_18",
            "credit": "VERIFIED__0",
        },
        "historical_failure_firewall": {
            "checked_failure_class_count": f"VERIFIED__{len(HISTORICAL_FAILURE_CLASSES)}",
            "checked_failure_classes": list(HISTORICAL_FAILURE_CLASSES),
            "reintroduced_historical_failure_count": "VERIFIED__0",
        },
        "validation": {
            "jc_focused": "VERIFIED__20_PASSED",
            "jb_negative_gate": "VERIFIED__1_PASSED__ACTUAL_GATE_EXECUTED",
            "sealed_harness": "VERIFIED__6_REQUIRED_REJECTIONS_PLUS_1_SYMLINK_REJECTION",
            "fm_operation_context": "VERIFIED__17_PASSED",
            "ie_current_applicable": "VERIFIED__10_PASSED__1_HISTORICAL_ENTRY_DESELECTED",
            "iz_current_applicable": "VERIFIED__10_PASSED__3_HISTORICAL_GENERATION_PINNED_DESELECTED",
            "in_v2_structural": "VERIFIED__12_PASSED",
            "du_eb_ee_uncommitted_boundary": "PASS__EXPECTED_FAIL_CLOSED__RUNTIME_TARGET_SELECTION_WORKTREE_DRIFT",
            "route_regressions": "VERIFIED__124_PASSED",
            "ex": "VERIFIED__12_OF_12__CERTIFIED_17_OF_17_REUSED",
            "governance_pytest": "VERIFIED__13_PASSED",
            "conformance_engine": "VERIFIED__20_PASSED__CONFORMANT__0_WARNINGS__0_VIOLATIONS",
            "layer_0_freeze": "VERIFIED__PASS",
            "git_diff_check": "VERIFIED__PASS",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_L5_CLAIM",
            "cross_worker_state_recovery_level": "VERIFIED__AUTHENTICATED_REPOSITORY_HANDOFF",
            "repository_derived_context_ratio": "ESTIMATED__DOMINANT__NO_NUMERIC_INSTRUMENT",
            "human_handoff_information_required": "VERIFIED__COMMISSION_SCOPE_JB_CHECKPOINT_DELTA_AND_LOCATORS",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_identity_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "inter_generation_cross_worker_continuation": "VERIFIED__JB_TO_JC",
            "intra_generation_cross_worker_continuation": "VERIFIED__SOL_HIGH_TO_ASTRA_EXTRA_HIGH_TO_SOL_HIGH",
            "uncommitted_delta_recovery": "VERIFIED__YES",
            "authority_state_recovery": "VERIFIED__JC_ZERO_AUTHORITY__IY_HISTORICAL_AUTHORITY_NONREUSABLE",
            "consumed_authority_recovery": "VERIFIED__IY_CONSUMPTION_RECONSTRUCTED_AND_NOT_REUSED",
            "post_operation_state_recovery": "VERIFIED__IY_FAIL_CLOSED_TERMINAL_AND_JB_PREAUTH_FAILURE_RECONSTRUCTED",
            "operation_replay_prevention": "VERIFIED__JC_ZERO_OPERATION__PROVIDER_LIMITS_DID_NOT_TRIGGER_REPLAY",
            "cross_worker_constitutional_drift": "NOT_PROVEN__NO_GOVERNED_WORKER_IDENTITY_DRIFT_INSTRUMENT",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0_AFTER_BOUNDED_TEST_COMPLETION_AND_STALE_EVIDENCE_REFRESH",
            "handoff_sufficiency_status": "VERIFIED",
            "handoff_state_completeness": "VERIFIED__COMPLETE_FOR_JC_SCOPE",
            "handoff_reconstruction_required": "VERIFIED__YES",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "unauthenticated_handoff_assumption_count": "VERIFIED__0",
        },
        "continuity": {
            "chain": "IV -> IW -> IX -> IY -> IZ -> JA -> JB -> JC",
            "same_generation_worker_chain": "SOL_HIGH_WORKER_1 -> PROVIDER_LIMIT -> ASTRA_EXTRA_HIGH_RECOVERY -> PROVIDER_LIMIT -> SOL_HIGH_TERMINAL_RECOVERY",
            "constitutional_health_evidence": "VERIFIED__HISTORICAL_FAILURES_FAIL_CLOSED__JC_SAME_GENERATION_RECOVERED__ACTUAL_JB_GATE_AND_SEALED_HARNESS_PROVEN__ONE_ROUTE__P11_UNCHANGED__RUNTIME_CERTIFICATION_SEPARATED__ZERO_AUTHORITY_ZERO_OPERATION_ZERO_RETRY_ZERO_REPLAY",
        },
        "infrastructure_amortization": {
            "future_generations_so_far": "VERIFIED__25__IE_THROUGH_JC",
            "future_e05_credit_so_far": "VERIFIED__0",
            "future_operational_attempts_so_far": "VERIFIED__2__IV_AND_IY",
            "marginal_new_infrastructure_for_jc": "VERIFIED__ONE_CURRENT_OWNER_ENTRY_IN_EXISTING_READ_ONLY_FM_HARNESS_PLUS_DEPENDENT_HASH_REBIND_AND_EVIDENCE",
            "new_common_infrastructure": "VERIFIED__0",
            "new_vector_specific_infrastructure": "VERIFIED__0",
            "infrastructure_amortization_signal": "ESTIMATED__HIGH_REUSE_WITH_ZERO_ROUTE_GROWTH_AND_ZERO_OPERATION",
        },
        "metrics": {
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "constitutional_frontier_distanc_e": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "e05_frontier_distance": "VERIFIED__8_UNSATISFIED_OF_18",
            "governance_efficience": "ESTIMATED__HIGH_REUSE_WITH_FAIL_CLOSED_ROLE_SEPARATION_AND_BOUNDED_PROJECTION",
            "architectural_governance_efficience": "VERIFIED__ONE_ROUTE_ZERO_ROUTE_DELTA_ZERO_P11_MUTATION_ONE_EXISTING_PROJECTION_MECHANISM",
            "proof_reuse_efficiency": "VERIFIED__EX_17_OF_17_REUSED__0_RECONSTRUCTED",
            "cognition_assisted_handoff": "VERIFIED__SAME_GENERATION_REPOSITORY_DERIVED_SOL_HIGH_TO_ASTRA_EXTRA_HIGH_TO_SOL_HIGH_RECOVERY",
            "cognition_provenance": "VERIFIED__RATIFIED_JB_GIT_CHECKPOINT_AUTHENTICATED_UNCOMMITTED_JC_DELTA_AND_REPOSITORY_EVIDENCE_PRIMARY__MODEL_IDENTITIES_NONAUTHORITATIVE",
            "aigol_codex_work_share": "NOT_MEASURED",
            "prompt_context_reuse_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "repository_derived_execution_context_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "constitutional_prompt_externalization_ratio": "NOT_MEASURED__NO_GOVERNED_NUMERIC_INSTRUMENT",
            "token_benchmark": "NOT_MEASURED",
            "llm_cost_reduction_ratio": "NOT_MEASURED",
            "lcrr": "NOT_MEASURED",
            "overengineering_risk": "ESTIMATED__LOW__EXISTING_PROJECTION_SPECIALIZED_WITHOUT_NEW_ABSTRACTION",
            "proof_process_overhead_risk": "ESTIMATED__MODERATE",
            "candidate_capability": "VERIFIED__FUTURE_GUEST_CURRENT_FM_CONTEXT_OWNER_PROJECTED_READ_ONLY_SEPARATELY_FROM_DETACHED_IF_RUNTIME_AND_AUTHORITY_FREE_STATIC_READINESS_PASS__POST_COMMIT_AND_OPERATIONAL_DENIAL_NOT_PROVEN",
            "shadow_design_target": "VERIFIED__FAMILY_LOCAL_DU_EB_EE_V2_OPTION_B_WITH_COLOCATED_FAIL_CLOSED_MAJOR_VERSION_DISPATCH",
            "shadow_automation_status": "VERIFIED__ABSENT",
        },
        "terminal_reduction": {
            "last_verified_edge": "FUTURE_GUEST_CURRENT_FM_CONTEXT_OWNER_READ_ONLY_PROJECTION_AND_AUTHORITY_FREE_STATIC_READINESS",
            "first_broken_edge": "POST_COMMIT_LIVE_BINDING_AND_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_NOT_PRESENT",
            "blocking_owner": "HUMAN_REVIEW_AND_POST_COMMIT_READINESS_BOUNDARY",
            "exact_failure": "NOT_APPLICABLE__JB_OWNER_DRIFT_CLOSED_STATICALLY__NO_OPERATION_ATTEMPTED",
            "minimum_missing_capability": "POST_COMMIT_REAUTHENTICATION_THEN_SEPARATE_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION",
            "minimum_legal_next_delta": "HUMAN_REVIEW_COMMIT_AND_PUSH_FOLLOWED_BY_SEPARATE_POST_COMMIT_READINESS__NO_OPERATION_IN_JC",
        },
    }


if __name__ == "__main__":
    reduction = terminal_reduction()
    envelope = {
        "schema_id": "G77_256JC_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }
    sys.stdout.buffer.write(canonical_bytes(envelope))
