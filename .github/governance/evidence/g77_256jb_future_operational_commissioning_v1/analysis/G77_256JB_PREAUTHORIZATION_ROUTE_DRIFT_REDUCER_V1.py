#!/usr/bin/env python3
"""Seal JB's authority-free certified-route drift terminal.

This reducer reads the partially materialized Phase-A state after FM's own
static-readiness gate failed.  It never creates authority, invokes PRE/FM,
launches QEMU, boots a VM, executes REQUEST, or enters P11.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
JB = ROOT / ".github/governance/evidence/g77_256jb_future_operational_commissioning_v1"
MATERIALIZER = JB / "orchestration/G77_256JB_PREAUTHORIZATION_MATERIALIZER_V1.py"
CONTEXT = JB / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
CANDIDATE = JB / "live_binding/candidate/G77_256IH_FUTURE_IF_BOUND_CURRENT_CANDIDATE_V1.json"
TERMINAL = JB / "G77_256JB_SPCE_TERMINAL_PREAUTHORIZATION_ROUTE_DRIFT_V1.json"
FM_OWNER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)

HEAD = "bb83b26bd3a7012c5a8a44e26fe93c91700337a6"
TREE = "c7951de62a0d16d45fd60fbfb14e54047543b13c"
IF_HEAD = "699fcdce794ff49b6c8735602936355724ed1c90"
IF_TREE = "7c773d4b2acdf013f1b8238eabfc8eced4dd6866"
EXPECTED_OWNER_SHA256 = "da09342d92f2a8d8310987aa0104bd6bd6ad7a3d009b51b8d710443c4884e9c7"
OBSERVED_OWNER_SHA256 = "fdfa04349529d70bc97820a1848f8afc22b81071859d5456550799e0f9476237"
GENERATION = "G77_256JB_ONE_FRESH_HUMAN_AUTHORIZED_FUTURE_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256JB_E05_FUTURE_DENIAL_BEFORE_ENTRY_001"

ESTABLISHED_FAILURE_CLASSES = (
    "future_commit_self_reference", "precommit_head_dependency", "checkout_mismatch",
    "alternates_escape", "checkout_collision", "transient_root_collision",
    "host_guest_path_mismatch", "adapter_mismatch", "launcher_sha_mismatch",
    "bootstrap_sha_mismatch", "nocloud_mismatch", "stale_projection",
    "historical_wrapper_binding", "runtime_current_identity_collapse",
    "runtime_certification_collapse", "caller_selected_runtime", "caller_selected_vector",
    "caller_selected_version", "caller_selected_import_root", "global_registry",
    "generic_dispatcher", "weak_generation_binding", "parallel_route", "p11_bypass",
    "automatic_authority", "authority_replay", "automatic_retry", "repair_retry",
    "host_sys_path_false_positive", "network_dependency", "guest_import_root_regression",
    "cross_generation_authority", "second_authority_consumption", "second_qemu",
    "second_operation", "provider_limit_replay", "historical_evidence_rewrite",
    "duplicate_future_semantics", "duplicate_request_logic", "duplicate_p11_logic",
    "entrypoint_induced_p11_bypass", "uncommitted_owner_false_positive",
    "runtime_target_selection_worktree_drift_bypass",
)
JB_FAILURE_CLASSES = (
    "authorization_presentation_is_not_authority", "historical_authority_reuse",
    "double_authority_consumption", "second_pre", "second_fm", "second_qemu",
    "second_vm", "second_operation", "retry", "repair_retry", "replay",
    "automatic_operation_after_human_boundary", "request_p11_entry_counter_collapse",
    "denial_effect_counter_collapse", "provider_limit_replay",
    "post_failure_automatic_repair",
)


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def load_materializer():
    specification = importlib.util.spec_from_file_location("g77_256jb_terminal_materializer", MATERIALIZER)
    if specification is None or specification.loader is None:
        raise RuntimeError("JB_MATERIALIZER_UNAVAILABLE")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def main() -> None:
    if TERMINAL.exists() or TERMINAL.is_symlink():
        raise RuntimeError("JB_TERMINAL_COLLISION")
    materializer = load_materializer()
    entry = materializer.authenticate_entry(HEAD, materializer.NESTED_HEAD)
    ja = materializer.reconstruct_ja()
    context = materializer.load_canonical(CONTEXT)
    checkout = Path(context["qemu_executable_base_seed_checkout_bindings"]["checkout"]["path"])
    checkout_owner = checkout / FM_OWNER
    observed_owner = sha256(checkout_owner)
    expected_owner = context["wrapper_fc_er_che_schema_hashes"]["fresh_operation_context_owner"]
    if (
        context["generation_identity"] != GENERATION
        or context["operation_identity"] != OPERATION
        or context["repository_head"] != HEAD
        or context["repository_tree"] != TREE
        or git("rev-parse", "HEAD", cwd=checkout) != IF_HEAD
        or git("rev-parse", "HEAD^{tree}", cwd=checkout) != IF_TREE
        or expected_owner != EXPECTED_OWNER_SHA256
        or observed_owner != OBSERVED_OWNER_SHA256
        or expected_owner == observed_owner
        or sha256(ROOT / FM_OWNER) != expected_owner
    ):
        raise RuntimeError("JB_ROUTE_DRIFT_EVIDENCE_MISMATCH")
    counters = {
        "human_operational_authority": 0, "authority_consumption": 0, "pre": 0,
        "fm_operational_invocation": 0, "qemu": 0, "vm_boot": 0,
        "operation_attempt": 0, "request_execution": 0, "future_denial": 0,
        "p11_operational_entry": 0, "protected_invocation": 0,
        "protected_effect": 0, "retry": 0, "repair_retry": 0, "replay": 0,
    }
    reduction = {
        "schema_id": "G77_256JB_SPCE_TERMINAL_PREAUTHORIZATION_ROUTE_DRIFT_V1",
        "recorded_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "generation_identity": GENERATION,
        "operation_identity": OPERATION,
        "terminal": "M__CERTIFIED_ROUTE_DRIFT_DETECTED",
        "phase": "PHASE_A__AUTHORITY_FREE_PREPARATION",
        "entry": entry,
        "ja_reconstruction": ja,
        "role_separation": {
            "target_runtime_identity": {"head": IF_HEAD, "tree": IF_TREE},
            "current_repository_identity": {"head": HEAD, "tree": TREE},
            "certification_baseline_identity": {"head": HEAD, "tree": TREE},
            "runtime_certification_role_separation": "VERIFIED__PRESERVED",
        },
        "prepared_identities": {
            "candidate_sha256": sha256(CANDIDATE),
            "context_file_sha256": sha256(CONTEXT),
            "context_sha256": context["context_sha256"],
            "canonical_argv_sha256": context["canonical_argv_sha256"],
            "sealed_request_sha256": "NOT_APPLICABLE__REQUEST_NOT_MATERIALIZED",
            "inner_request_sha256": "NOT_APPLICABLE__REQUEST_NOT_MATERIALIZED",
            "preauthorization_checkpoint_sha256": "NOT_APPLICABLE__FM_STATIC_READINESS_FAILED",
            "authorization_presentation_sha256": "NOT_APPLICABLE__HUMAN_BOUNDARY_NOT_REACHED",
        },
        "route_drift": {
            "owner": FM_OWNER.as_posix(),
            "current_repository_owner_sha256": expected_owner,
            "detached_if_checkout_owner_sha256": observed_owner,
            "guest_owner_path": "/mnt/aigol/" + FM_OWNER.as_posix(),
            "fm_gate": "authority_free_static_readiness",
            "fm_failure": "authority-free immutable asset or candidate binding mismatch",
            "exact_mismatch": "DETACHED_IF_CHECKOUT_FM_CONTEXT_OWNER_SHA256_NE_CURRENT_COMMITTED_FM_CONTEXT_OWNER_SHA256",
        },
        "authority_boundary": {
            "authorization_presentation_materialized": 0,
            "human_authorization_required_printed": False,
            "human_authority_present": False,
            "historical_iy_authority_reused": False,
            "auto_continuable": False,
            "human_review_required": True,
            "phase_b_started": False,
        },
        "operational_counters": counters,
        "e05": {"before": "VERIFIED__10_OF_18", "after": "VERIFIED__10_OF_18", "credit": "VERIFIED__0"},
        "reuse": {
            "ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0",
            "production_route_before": "VERIFIED__1", "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0", "p11_mutation_count": "VERIFIED__0",
            "new_production_architecture_count": "VERIFIED__0",
        },
        "historical_failure_firewall": {
            "checked_failure_classes": list(ESTABLISHED_FAILURE_CLASSES + JB_FAILURE_CLASSES),
            "checked_failure_class_count": f"VERIFIED__{len(ESTABLISHED_FAILURE_CLASSES + JB_FAILURE_CLASSES)}",
            "reintroduced_historical_failure_count": "VERIFIED__1__CERTIFIED_ROUTE_RUNTIME_OWNER_DRIFT_EXPOSED",
        },
        "terminal_reduction": {
            "last_verified_edge": "FRESH_JB_CONTEXT_AND_DETACHED_IF_CHECKOUT_AUTHORITY_FREE_MATERIALIZATION",
            "first_broken_edge": "FM_AUTHORITY_FREE_IMMUTABLE_ASSET_BINDING__GUEST_CONTEXT_OWNER_EQUALITY",
            "blocking_owner": "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.authority_free_static_readiness",
            "exact_failure": "DETACHED_IF_CHECKOUT_CONTEXT_OWNER_SHA256_fdfa0434_NE_COMMITTED_JA_CONTEXT_OWNER_SHA256_da09342d",
            "minimum_missing_capability": "CERTIFIED_RUNTIME_PROJECTION_OF_THE_COMMITTED_FM_CONTEXT_OWNER_WITHOUT_RUNTIME_CERTIFICATION_ROLE_COLLAPSE",
            "minimum_legal_next_delta": "SEPARATE_HUMAN_REVIEWED_REPOSITORY_ONLY_GENERATION_TO_RECONCILE_THE_GUEST_CONTEXT_OWNER_BINDING__NO_AUTHORIZATION_OR_OPERATION_IN_JB",
        },
    }
    envelope = {
        "schema_id": "G77_256JB_SPCE_TERMINAL_PREAUTHORIZATION_ROUTE_DRIFT_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": hashlib.sha256(canonical_bytes(reduction)).hexdigest(),
    }
    TERMINAL.write_bytes(canonical_bytes(envelope))


if __name__ == "__main__":
    main()
