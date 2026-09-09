#!/usr/bin/env python3
"""Reduce the first JS preauthorization failure without retry or operation."""

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
JS = ROOT / ".github/governance/evidence/g77_256js_expired_operational_v1"
CONTEXT_PATH = JS / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
REDUCTION_PATH = JS / "G77_256JS_SPCE_PREAUTHORIZATION_BLOCKER_REDUCTION_V1.json"
MATERIALIZER = JS / "orchestration/G77_256JS_PREAUTHORIZATION_MATERIALIZER_V1.py"
FM_PATH = ROOT / (
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
JR_REDUCTION = ROOT / (
    ".github/governance/evidence/"
    "g77_256jr_expired_human_authority_materialization_and_presentation_binding_v1/"
    "G77_256JR_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
HEAD = "304b342e26e92f226afa01db4b4203acfa51f532"
TREE = "fc0c50e4dd79e900d85d48c5c0aeb53fe9d0c937"
SUBJECT = "G77-256JR bind EXPIRED Human-authority materialization and presentation"
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
GENERATION = "G77_256JS_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256JS_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"


def load_module(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"module unavailable: {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


FM = load_module(FM_PATH, "g77_256js_blocker_fm")


def canonical_bytes(value: Any) -> bytes:
    return FM.canonical_bytes(value)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *arguments], cwd=cwd, text=True).strip()


def main() -> None:
    if REDUCTION_PATH.exists() or REDUCTION_PATH.is_symlink():
        raise RuntimeError("blocker reduction already exists")
    if (
        git("branch", "--show-current") != BRANCH
        or git("rev-parse", "HEAD") != HEAD
        or git("rev-parse", "HEAD^{tree}") != TREE
        or git("show", "-s", "--format=%s", "HEAD") != SUBJECT
        or git("diff", "--cached", "--name-only") != ""
        or git("status", "--porcelain", "--untracked-files=no") != ""
    ):
        raise RuntimeError("repository identity drift during fail-closed reduction")
    context = json.loads(CONTEXT_PATH.read_bytes())
    FM.fresh_context.validate_context(context, repository_root=ROOT)
    if (
        context["generation_identity"] != GENERATION
        or context["operation_identity"] != OPERATION
        or context["repository_head"] != HEAD
        or context["repository_tree"] != TREE
        or context["preclaim_temporal_binding"]["coordinate_unix_ns"] != 1000
    ):
        raise RuntimeError("partial JS context identity mismatch")

    binding = context["guest_adapter_binding"]
    cloud_path = ROOT / FM.EXPIRED_CLOUD_INIT
    actual = FM.bootstrap_guest_command_arguments(
        cloud_path.read_text(encoding="utf-8"), binding["bootstrap_guest_path"]
    )
    expected = (
        binding["source_sha256"],
        context["wrapper_fc_er_che_schema_hashes"]["raw_evidence_schema"],
        HEAD,
        TREE,
        sha256_path(ROOT / FM.DN_HARNESS),
    )
    if actual[:2] != expected[:2] or actual[4] != expected[4]:
        raise RuntimeError("blocker is broader than the checkout coordinate pair")
    if actual[2:] == expected[2:]:
        raise RuntimeError("expected cloud-init blocker is absent")
    if actual[2:4] != (
        "f2f00fab5b47e5c3e59629f9542258e65f20a9c0",
        "07ae3ad87775f30f298a691f1054881915604d32",
    ):
        raise RuntimeError("unexpected cloud-init pre-request identity")

    candidate = JS / "live_binding/candidate/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
    runtime = JS / "live_binding/runtime_projection/G77_256GD_CANONICAL_CONTINUATION_MANIFEST_BINDING_REISSUE_V1.json"
    runtime_export = Path(context["runtime_export_root"])
    required_partial = (
        candidate,
        runtime,
        runtime_export / "G77_256JS_CONTINUATION_MANIFEST_V1.json",
        runtime_export / "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json",
        Path(binding["projected_path"]),
        Path(binding["bootstrap_projected_path"]),
    )
    if any(not path.is_file() or path.is_symlink() for path in required_partial):
        raise RuntimeError("expected preauthorization partial materialization absent")
    if len({sha256_path(path) for path in required_partial[:3]}) != 1:
        raise RuntimeError("candidate projection identity mismatch")

    forbidden = (
        JS / "G77_256JS_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt",
        JS / "G77_256JS_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json",
        JS / "G77_256JS_HUMAN_OPERATIONAL_AUTHORIZATION_REQUEST_V1.json",
        JS / "G77_256JS_HUMAN_OPERATIONAL_AUTHORIZATION_PRESENTATION_V1.txt",
        JS / "G77_256JS_PREAUTHORIZATION_SAFE_STOP_CHECKPOINT_V1.json",
        Path(context["pre_receipt_path"]),
        Path(context["post_receipt_path"]),
        Path(context["serial_path"]),
        *(runtime_export / relative for relative in context["guest_output_relative_paths"]),
    )
    if any(path.exists() or path.is_symlink() for path in forbidden):
        raise RuntimeError("authority, request, checkpoint, or operation artifact exists")

    jr_envelope = json.loads(JR_REDUCTION.read_bytes())
    jr = jr_envelope["reduction"]
    if (
        jr_envelope["reduction_sha256"]
        != hashlib.sha256(canonical_bytes(jr)).hexdigest()
        or jr["terminal"]
        != "A__EXPIRED_HUMAN_AUTHORITY_MATERIALIZATION_AND_PRESENTATION_BINDING_REPOSITORY_VERIFIED"
    ):
        raise RuntimeError("JR reduction drift")

    zero = {key: "VERIFIED__0" for key in (
        "operational_authorization_count",
        "authority_consumption_count",
        "pre_operational_count",
        "fm_operational_invocation_count",
        "qemu_count",
        "vm_count",
        "operation_attempt_count",
        "request_count",
        "p11_entry_count",
        "protected_invocation_count",
        "protected_effect_count",
        "retry_count",
        "repair_retry_count",
        "replay_count",
    )}
    reduction = {
        "schema_id": "G77_256JS_SPCE_PREAUTHORIZATION_BLOCKER_REDUCTION_V1",
        "recorded_at_utc": datetime.now(timezone.utc).replace(
            microsecond=0
        ).isoformat().replace("+00:00", "Z"),
        "generation": "G77-256JS",
        "phase": "FAIL_CLOSED_BEFORE_HUMAN_AUTHORIZATION_PRESENTATION",
        "terminal": "M__EXPIRED_FRESH_PREAUTHORIZATION_BOOTSTRAP_HEAD_TREE_BINDING_MISMATCH",
        "entry": {
            "branch": BRANCH,
            "head": HEAD,
            "tree": TREE,
            "subject": SUBJECT,
            "remote_head": HEAD,
            "entry_worktree_clean": True,
            "entry_index_empty": True,
        },
        "nested_authority": {
            "origin": "git@github.com:Aljosa3/sapianta-core.git",
            "head": "3183bab71f8f30397c0309dd2e6d846d14a11f66",
            "tree": "7c32ec05efc2be43297849bc38ec8766514a523d",
            "tag": "sapianta-system-nested-authority-3183bab-v1",
            "clean": True,
            "detached": True,
            "pinned": True,
            "remote_tag_equal": True,
        },
        "jr": {
            "terminal": jr["terminal"],
            "repository_capability": "VERIFIED__EXPIRED_COMPATIBLE_HUMAN_AUTHORITY_MATERIALIZATION_AND_PRESENTATION_REPOSITORY_CAPABILITY",
            "ex_reused": "VERIFIED__17_OF_17",
            "ex_reconstructed": "VERIFIED__0",
            "operational_counters": "VERIFIED__ALL_FOURTEEN_ZERO",
        },
        "candidate": {
            "generation_identity": GENERATION,
            "operation_identity": OPERATION,
            "candidate_path": candidate.relative_to(ROOT).as_posix(),
            "candidate_sha256": sha256_path(candidate),
            "runtime_projection_sha256": sha256_path(runtime),
            "context_path": CONTEXT_PATH.relative_to(ROOT).as_posix(),
            "context_file_sha256": sha256_path(CONTEXT_PATH),
            "context_sha256": context["context_sha256"],
            "canonical_argv_sha256": context["canonical_argv_sha256"],
            "expired_adapter_sha256": binding["source_sha256"],
            "temporal_binding_sha256": hashlib.sha256(
                canonical_bytes(context["preclaim_temporal_binding"])
            ).hexdigest(),
            "valid_from_unix_ns": 100,
            "valid_until_unix_ns": 1000,
            "governed_preclaim_coordinate_unix_ns": 1000,
            "request_identity": "NOT_MATERIALIZED",
            "presentation_identity": "NOT_MATERIALIZED",
            "preauthorization_checkpoint_digest": "NOT_MATERIALIZED",
        },
        "blocker": {
            "failure_owner": "FM_PREAUTHORITY_GUEST_ADAPTER_BINDING",
            "failure_reason": "cloud-init pre-request argument binding mismatch",
            "expected_argument_tuple": list(expected),
            "observed_argument_tuple": list(actual),
            "differing_tuple_positions": [2, 3],
            "last_verified_edge": "EXACT_JS_EXPIRED_CONTEXT_AND_AUTHORITY_FREE_OPERATION_STATE_MATERIALIZED_WITHOUT_QEMU",
            "first_broken_edge": "JR_EXPIRED_CLOUD_INIT_PRE_REQUEST_HEAD_TREE_DO_NOT_BIND_RATIFIED_JR_CHECKOUT",
            "minimum_missing_capability": "EXPIRED_BOOTSTRAP_PRE_REQUEST_ARGUMENTS_BOUND_TO_RATIFIED_JR_HEAD_TREE",
            "minimum_legal_next_delta": "SEPARATE_REPOSITORY_ONLY_FAMILY_LOCAL_BOOTSTRAP_BINDING_FIX_GENERATION__NO_AUTHORITY__NO_OPERATION",
        },
        "operational_counters": zero,
        "materialization_counters": {
            "preauthorization_materialization_attempt_count": "VERIFIED__1",
            "operation_state_materialization_count": "VERIFIED__1__WITHOUT_QEMU",
            "human_authorization_request_materialization_count": "VERIFIED__0",
            "human_presentation_materialization_count": "VERIFIED__0",
            "preauthorization_checkpoint_materialization_count": "VERIFIED__0",
        },
        "e05": {
            "before": "VERIFIED__11_OF_18",
            "after": "VERIFIED__11_OF_18",
            "credit": "VERIFIED__0",
            "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
            "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
        },
        "architecture": {
            "p11_implementation_mutation_count": "VERIFIED__0",
            "production_mutation_count": "VERIFIED__0",
            "new_owner_count": "VERIFIED__0",
            "new_route_count": "VERIFIED__0",
            "new_registry_count": "VERIFIED__0",
            "new_generic_abstraction_count": "VERIFIED__0",
            "new_constitutional_concept_count": "VERIFIED__0",
            "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0",
        },
        "proof_yield": {
            "new_verified_capability_count": "VERIFIED__0",
            "new_blocker_localized_count": "VERIFIED__1__EXPIRED_BOOTSTRAP_HEAD_TREE_BINDING",
            "e05_credit": "VERIFIED__0",
            "proof_reuse_count": "VERIFIED__17__EX_COMMON_CAPABILITIES",
        },
        "reuse_impact_assessment": {
            "existing_certified_capabilities_reused": "EX_17_OF_17__JJ__JL__JM__JO__JP__JQ__JR__FM__FC__ER__GN__P11",
            "new_capabilities": "NONE",
            "existing_capability_became_unreachable": False,
            "parallel_flow_created": False,
            "production_path_count_effect": "UNCHANGED__1_TO_1",
        },
        "governance_dashboard": {
            "project_progress": "VERIFIED__JS_PREAUTHORIZATION_BLOCKER_LOCALIZED",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__EXPIRED_OPERATION_BLOCKED_BEFORE_HUMAN_PRESENTATION",
            "constitutional_health_evidence": "VERIFIED__FAIL_CLOSED_BEFORE_AUTHORITY_AND_OPERATION",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficience": "ESTIMATED__HIGH__ONE_ATTEMPT_LOCALIZED_EXACT_TWO_FIELD_DRIFT",
            "overengineering_risk": "ESTIMATED__LOW__NO_PRODUCTION_FIX_IN_JS",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_AND_RUNTIME_EXCEPTION_EVIDENCE_PRIMARY",
            "cognition_assisted_handoff": "NOT_APPLICABLE__NO_PROVIDER_RECOVERY",
            "candidate_capability": "NOT_PROVEN__CHECKPOINT_AND_PRESENTATION_NOT_MATERIALIZED",
            "shadow_design_target": "VERIFIED__SOLE_FM_ER_P11_ROUTE_WITH_EXPIRED_SPECIALIZATION",
            "constitutional_continuation_progress": "VERIFIED__JR_TO_JS_BLOCKER_LOCALIZATION",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
        },
        "human_authority_assurance_status": "NOT_PROVEN__AUTHENTICATED_HAC_HAI_HAE_DEFINITIONS_NOT_LOCATED",
        "auto_continuable": False,
        "human_review_required": True,
    }
    envelope = {
        "schema_id": "G77_256JS_SPCE_PREAUTHORIZATION_BLOCKER_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": hashlib.sha256(canonical_bytes(reduction)).hexdigest(),
    }
    REDUCTION_PATH.write_bytes(canonical_bytes(envelope))


if __name__ == "__main__":
    main()
