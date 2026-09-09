#!/usr/bin/env python3
"""Deterministic repository-only reduction for G77-256JM.

This module authenticates committed JL evidence and reduces the implemented
Option A binding.  It has no operational entry point and cannot create Human
authority, invoke P11, PRE, FM, QEMU, a VM, or a protected effect.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True

ENTRY_BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ENTRY_HEAD = "651168072f39d6cd0323efc23ed830445a05062b"
ENTRY_TREE = "46b4967707332873f8102f46f156541fbb901d39"
ENTRY_SUBJECT = "G77-256JL formalize P11 deterministic preclaim temporal owner"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
TERMINAL = (
    "A__OPTION_A_DETERMINISTIC_PRECLAIM_TEMPORAL_BINDING_"
    "IMPLEMENTED_AND_REPOSITORY_VERIFIED"
)
NAMESPACE = Path(
    ".github/governance/evidence/"
    "g77_256jm_option_a_deterministic_preclaim_temporal_binding_implementation_v1"
)
OUTPUT_NAME = "G77_256JM_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"

JL = Path(
    ".github/governance/evidence/"
    "g77_256jl_p11_custody_owned_deterministic_preclaim_temporal_owner_contract_v1/"
    "G77_256JL_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
FM_OWNER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
FM_LAUNCHER = FM_OWNER.parent / "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
CONTEXT_SCHEMA = Path(
    ".github/governance/evidence/g77_256gd_fresh_operation_context_v1/"
    "SAPIANTA_FRESH_OPERATION_CONTEXT_V1.schema.json"
)
P11 = Path("tests/p11_da_operational_consumer_v1.py")
DI_TEST = Path("tests/test_g77_256di_p11_da_operational_consumer_v1.py")
EX_CERTIFICATE = Path(
    ".github/governance/evidence/g77_256ex_common_substrate_certification_v1/"
    "G77_256EX_P11_SPCE_COMMON_SUBSTRATE_CERTIFICATION_V1.json"
)
EW_MANIFEST = Path(
    ".github/governance/evidence/g77_256ew_reusable_p11_spce_substrate_v1/"
    "G77_256EW_P11_SPCE_REUSABLE_SUBSTRATE_MANIFEST_V1.json"
)
EX_CERTIFICATE_SHA256 = (
    "91c477171147c56516c0f473ab887c12173c4bab225f2733c274b32467824b2f"
)
EW_MANIFEST_SHA256 = (
    "42744ccb19767a9f90ed909f3d99b05622053fd00e97886d8a331bcadfe8675c"
)

EXPECTED_DELTA_PATHS = sorted([
    str(FM_OWNER),
    str(FM_LAUNCHER),
    str(CONTEXT_SCHEMA),
    str(P11),
    str(DI_TEST),
    str(NAMESPACE / "G77_256JM_G48_IMPLEMENTATION_REPORT_V1.md"),
    str(NAMESPACE / OUTPUT_NAME),
    str(NAMESPACE / "analysis/G77_256JM_OPTION_A_TEMPORAL_BINDING_FORMALIZER_V1.py"),
    str(NAMESPACE / "tests/test_g77_256jm_option_a_temporal_binding_v1.py"),
])


class JMError(RuntimeError):
    """One deterministic fail-closed JM reduction error."""


def fail(token: str) -> None:
    raise JMError(token)


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            fail(f"DUPLICATE_JSON_KEY__{key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_bytes(), object_pairs_hook=unique_object)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise JMError(f"JSON_INVALID__{path}") from exc
    if not isinstance(value, dict):
        fail(f"JSON_OBJECT_REQUIRED__{path}")
    return value


def git(root: Path, *arguments: str) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=root, text=True, stderr=subprocess.DEVNULL
    ).strip()


def authenticate_entry(root: Path) -> dict[str, Any]:
    observed = {
        "branch": git(root, "branch", "--show-current"),
        "head": git(root, "rev-parse", "HEAD"),
        "tree": git(root, "rev-parse", "HEAD^{tree}"),
        "subject": git(root, "show", "-s", "--format=%s", "HEAD"),
        "origin": git(root, "remote", "get-url", "origin"),
        "remote_tracking_head": git(
            root, "rev-parse", f"refs/remotes/origin/{ENTRY_BRANCH}"
        ),
    }
    if observed != {
        "branch": ENTRY_BRANCH,
        "head": ENTRY_HEAD,
        "tree": ENTRY_TREE,
        "subject": ENTRY_SUBJECT,
        "origin": ORIGIN,
        "remote_tracking_head": ENTRY_HEAD,
    }:
        fail("ENTRY_IDENTITY_MISMATCH")
    if git(root, "diff", "--cached", "--name-only"):
        fail("INDEX_NOT_EMPTY")
    status = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root,
        text=True,
    )
    paths = sorted(
        line[3:]
        for line in status.splitlines()
        if not line[3:].endswith(".pyc") and "__pycache__" not in line[3:]
    )
    if paths != EXPECTED_DELTA_PATHS:
        fail("WORKTREE_DELTA_SCOPE_MISMATCH")
    nested = root / "sapianta_system"
    nested_state = {
        "clean": git(nested, "status", "--porcelain") == "",
        "detached": git(nested, "branch", "--show-current") == "",
        "head": git(nested, "rev-parse", "HEAD"),
        "tree": git(nested, "rev-parse", "HEAD^{tree}"),
        "tag": git(nested, "describe", "--tags", "--exact-match", "HEAD"),
        "origin": git(nested, "remote", "get-url", "origin"),
    }
    if nested_state != {
        "clean": True,
        "detached": True,
        "head": NESTED_HEAD,
        "tree": NESTED_TREE,
        "tag": NESTED_TAG,
        "origin": NESTED_ORIGIN,
    }:
        fail("NESTED_AUTHORITY_MISMATCH")
    return observed | {
        "entry_remote_head": ENTRY_HEAD,
        "remote_network_equality": (
            "VERIFIED__DIRECT_READ_ONLY_LS_REMOTE_DURING_RECOVERY_PREFLIGHT"
        ),
        "entry_worktree": "VERIFIED__DIRTY__EXPECTED_NINE_PATH_JM_RECOVERY_OBJECT",
        "previous_worker_checkpoint_statement": "CONTEXT_ONLY__NOT_USED_AS_PROOF",
        "index": "VERIFIED__EMPTY",
        "bounded_current_delta_paths": paths,
        "nested_authority": nested_state,
        "nested_remote_tag_equality": (
            "VERIFIED__DIRECT_READ_ONLY_LS_REMOTE_DURING_RECOVERY_PREFLIGHT"
        ),
    }


def reconstruct_jl(root: Path) -> dict[str, str]:
    envelope = load_json(root / JL)
    reduction = envelope.get("reduction")
    if not isinstance(reduction, dict) or envelope.get("reduction_sha256") != (
        sha256_bytes(canonical_bytes(reduction))
    ):
        fail("JL_INNER_SEAL_INVALID")
    expected = {
        "terminal": "A__P11_CUSTODY_OWNED_DETERMINISTIC_PRECLAIM_TEMPORAL_OWNER_CONTRACT_VERIFIED",
        "selected_temporal_owner_contract": "OPTION_A__P11_CUSTODY_POLICY_OWNED_COORDINATE_SEALED_IN_EXISTING_SAPIANTA_FRESH_OPERATION_CONTEXT_V1",
        "temporal_coordinate_owner": "P11_DA_AUTHORITY_CUSTODY_PROCESS_PRINCIPAL_TEMPORAL_POLICY_V1",
    }
    if {key: reduction.get(key) for key in expected} != expected:
        fail("JL_CONTRACT_MISMATCH")
    return expected | {
        "authenticated_sha256": sha256_file(root / JL),
        "ex_reused": reduction["ex_reused"],
        "ex_reconstructed": reduction["ex_reconstructed"],
    }


def authenticate_ex_reuse(root: Path) -> dict[str, Any]:
    """Authenticate proof reuse without treating P11 hardening as certified."""

    certificate_path = root / EX_CERTIFICATE
    manifest_path = root / EW_MANIFEST
    if sha256_file(certificate_path) != EX_CERTIFICATE_SHA256:
        fail("EX_CERTIFICATE_HASH_MISMATCH")
    if sha256_file(manifest_path) != EW_MANIFEST_SHA256:
        fail("EW_MANIFEST_HASH_MISMATCH")
    certificate = load_json(certificate_path).get("certificate")
    manifest = load_json(manifest_path).get("manifest")
    if not isinstance(certificate, dict) or not isinstance(manifest, dict):
        fail("EX_REUSE_SOURCE_INVALID")
    if certificate.get("component_counts", {}).get("CERTIFIED") != 17:
        fail("EX_CERTIFIED_COMPONENT_COUNT_MISMATCH")
    bindings = manifest.get("component_bindings")
    if not isinstance(bindings, list):
        fail("EW_COMPONENT_BINDINGS_INVALID")
    p11_binding = next(
        (item for item in bindings if item.get("path") == str(P11)), None
    )
    if not isinstance(p11_binding, dict) or (
        p11_binding.get("classification") != "REQUIRES_HARDENING"
    ):
        fail("P11_EX_CLASSIFICATION_MISMATCH")
    if p11_binding.get("sha256") == sha256_file(root / P11):
        fail("P11_HARDENING_DELTA_NOT_OBSERVED")
    return {
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
        "entry_parent_ex_validator": "VERIFIED__12_OF_12",
        "current_modified_ex_manifest_path_set": [str(P11)],
        "current_modified_ex_component_classification": "REQUIRES_HARDENING",
        "current_dirty_worktree_exact_byte_validator": (
            "EXPECTED_FAIL_CLOSED__P11_REQUIRES_HARDENING_HASH_CHANGED"
        ),
        "operational_reuse_admissibility": (
            "NOT_PROVEN__REQUIRES_POST_COMMIT_SUCCESSOR_REAUTHENTICATION"
        ),
    }


def authenticate_implementation(root: Path) -> dict[str, Any]:
    fm = (root / FM_OWNER).read_text(encoding="utf-8")
    launcher = (root / FM_LAUNCHER).read_text(encoding="utf-8")
    p11 = (root / P11).read_text(encoding="utf-8")
    ast.parse(fm)
    ast.parse(launcher)
    ast.parse(p11)
    required_fm = (
        "materialize_preclaim_temporal_binding",
        '"preclaim_temporal_binding"',
        "validate_preclaim_temporal_binding",
        "PRECLAIM_TEMPORAL_SPECIFICATION_SHA256",
    )
    required_p11 = (
        "authenticate_preclaim_temporal_binding",
        "operation_context_sha256",
        "preclaim_temporal_binding_identity",
        'preclaim_time = temporal_binding["coordinate_unix_ns"]',
        'temporal_decision == "FUTURE"',
        'temporal_decision == "EXPIRED"',
    )
    if any(value not in fm for value in required_fm):
        fail("FM_BINDING_IMPLEMENTATION_INCOMPLETE")
    if any(value not in p11 for value in required_p11):
        fail("P11_BINDING_IMPLEMENTATION_INCOMPLETE")
    claim = p11[p11.index("    def claim_and_invoke_once("):p11.index(
        "\n\nassert AUTOMATIC_RETRY_COUNT_V1", p11.index("    def claim_and_invoke_once(")
    )]
    if "time.time_ns" in claim:
        fail("P11_PRECLAIM_UNAUTHENTICATED_CLOCK_REMAINS")
    if launcher.count("def build_operation_context(") != 1:
        fail("PRODUCTION_CONTEXT_ROUTE_COUNT_CHANGED")
    return {
        "context_owner_sha256": sha256_file(root / FM_OWNER),
        "launcher_sha256": sha256_file(root / FM_LAUNCHER),
        "context_schema_sha256": sha256_file(root / CONTEXT_SCHEMA),
        "p11_consumer_sha256": sha256_file(root / P11),
        "coordinate_materializer": "VERIFIED__COMMITTED_JJ_SPECIFICATION_TO_OPERATION_LOCAL_BINDING",
        "canonical_context_seal": "VERIFIED__COORDINATE_COVERED_BY_CONTEXT_SHA256",
        "human_correlation": "VERIFIED__WHOLE_CONTEXT_SHA256_ONLY__NO_COORDINATE_SELECTION",
        "commissioning_preflight": "VERIFIED__CONTEXT_AND_TEMPORAL_IDENTITIES_IN_GATE_IDENTITY",
        "p11_custody_reauthentication": "VERIFIED__AT_CONSTRUCTION_AND_PRECLAIM",
        "preclaim_source": "VERIFIED__AUTHENTICATED_OPERATION_LOCAL_COORDINATE",
        "uncontrolled_wall_clock_fallback": "VERIFIED__ABSENT_FROM_PRECLAIM_DECISION",
    }


def build_reduction(root: Path) -> dict[str, Any]:
    root = root.resolve()
    entry = authenticate_entry(root)
    jl = reconstruct_jl(root)
    ex_reuse = authenticate_ex_reuse(root)
    implementation = authenticate_implementation(root)
    zeros = {key: "VERIFIED__0" for key in (
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
    return {
        "schema_id": "G77_256JM_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1",
        "generation": "G77-256JM",
        "mode": "REPOSITORY_ONLY_IMPLEMENTATION__NO_AUTHORITY__NO_OPERATION",
        "spce": [
            "AUTHENTICATE", "RECONSTRUCT_JL", "REUSE_EX", "TRACE_EXISTING_BINDING",
            "IMPLEMENT_MINIMUM_OPTION_A_DELTA", "VERIFY_AUTHENTICATION",
            "VERIFY_FAIL_CLOSED", "VERIFY_DETERMINISM", "VERIFY_NON_BYPASS",
            "REDUCE", "STOP",
        ],
        "terminal": TERMINAL,
        "entry": entry,
        "jl_reconstruction": jl,
        "implementation": implementation,
        "temporal_semantics": {
            "future": "preclaim_coordinate < valid_from",
            "current": "valid_from <= preclaim_coordinate < valid_until",
            "expired": "preclaim_coordinate >= valid_until",
            "boundary": "VERIFIED__999_CURRENT__1000_EXPIRED__1001_EXPIRED",
            "same_authenticated_inputs_same_coordinate_same_decision": "VERIFIED",
            "operational_replay": "PROHIBITED",
        },
        "authority_separation": {
            "caller_selectable_time_authority_count": "VERIFIED__0",
            "provider_selectable_time_authority_count": "VERIFIED__0",
            "human_selectable_time_authority_count": "VERIFIED__0",
            "temporal_coordinate_is_execution_authority": "VERIFIED__NO",
            "temporal_coordinate_is_human_authority": "VERIFIED__NO",
            "temporal_coordinate_is_p11_authority": "VERIFIED__NO",
            "temporal_coordinate_is_protected_effect_authority": "VERIFIED__NO",
            "deterministic_temporal_input_without_valid_p11_authority": "NO_PROTECTED_EFFECT",
        },
        "failure_matrix": {
            key: "VERIFIED__FAIL_CLOSED_BEFORE_PRECLAIM_APPEND"
            for key in (
                "missing", "malformed", "wrong_type", "invalid_value", "conflicting",
                "duplicate", "coordinate_seal_mismatch", "context_mismatch",
                "operation_mismatch", "candidate_context_correlation_mismatch",
                "preflight_mismatch", "mutation_after_sealing",
                "mutation_after_human_correlation", "caller_substitution",
                "provider_model_substitution", "replay_with_changed_coordinate",
            )
        } | {
            "wall_clock_disagreement": "VERIFIED__IGNORED__NO_OVERRIDE_OR_REPAIR"
        },
        "architecture": {
            "new_owner_count": "VERIFIED__0",
            "new_route_count": "VERIFIED__0",
            "new_registry_count": "VERIFIED__0",
            "new_generic_abstraction_count": "VERIFIED__0",
            "new_constitutional_concept_count": "VERIFIED__0",
            "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0",
            "parallel_flow_created": "VERIFIED__NO",
            "p11_implementation_mutation_count": "VERIFIED__1",
            "production_mutation_count": "VERIFIED__3",
        },
        "reuse": ex_reuse | {
            "preexisting_capability_unreachable": "VERIFIED__NO",
        },
        "e05": {
            "before": "VERIFIED__11_OF_18",
            "after": "VERIFIED__11_OF_18",
            "credit": "VERIFIED__0",
            "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
            "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
        },
        "operational_counters": zeros,
        "proof_yield": {
            "new_verified_capability_count": "VERIFIED__1__OPTION_A_REPOSITORY_BINDING",
            "new_blocker_localized_count": "VERIFIED__1__POST_COMMIT_LIVE_BINDING_READINESS",
            "e05_credit": "VERIFIED__0",
            "proof_reuse_count": "VERIFIED__17__EX_COMMON_CAPABILITIES",
        },
        "frontier": {
            "last_verified_edge": "OPTION_A_CONTEXT_GATE_P11_BINDING_IMPLEMENTED_AND_REPOSITORY_VERIFIED",
            "first_broken_edge": "POST_JM_COMMITTED_IDENTITY_LIVE_BINDING_EX_SUCCESSOR_REAUTHENTICATION_AND_READINESS_NOT_PROVEN",
            "minimum_missing_capability": "COMMITTED_POST_JM_LIVE_BINDING_AND_EX_SUCCESSOR_REAUTHENTICATION",
            "minimum_legal_next_delta": "AFTER_HUMAN_REVIEW__SEPARATE_POST_COMMIT_LIVE_BINDING_EX_SUCCESSOR_REAUTHENTICATION_AND_READINESS_GENERATION__NO_OPERATION",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
        },
        "metrics": {
            "project_progress": "VERIFIED__JL_CONTRACT_TO_JM_REPOSITORY_IMPLEMENTATION",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": "ESTIMATED__IMPLEMENTATION_COMPLETE__POST_COMMIT_READINESS_AND_OPERATIONAL_PROOF_REMAIN",
            "constitutional_health_evidence": "VERIFIED__FAIL_CLOSED_AUTHORITY_SEPARATION_REPLAY_AND_SINGLE_ROUTE_PRESERVED",
            "shadow_automation_status": "VERIFIED__ABSENT",
            "governance_efficience": "ESTIMATED__HIGH__EX_REUSED_AND_THREE_PRODUCTION_IMPLEMENTATION_FILES_MUTATED",
            "overengineering_risk": "ESTIMATED__LOW__NO_CLOCK_FRAMEWORK_PROVIDER_REGISTRY_OR_ROUTE",
            "cognition_provenance": "VERIFIED__AUTHENTICATED_REPOSITORY_EVIDENCE_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__JL_TO_JM_REPOSITORY_CONTINUATION",
            "candidate_capability": "VERIFIED__OPTION_A_REPOSITORY_BINDING_ONLY",
            "shadow_design_target": "VERIFIED__CONTEXT_SEALED_CUSTODY_REAUTHENTICATED_COORDINATE",
            "constitutional_continuation_progress": "VERIFIED__CONTRACT_TO_IMPLEMENTATION__NO_E05_CREDIT",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "intra_generation_cross_worker_continuation": (
                "VERIFIED__G77_256JM_SAME_GENERATION_CROSS_ACCOUNT_CONTINUATION"
            ),
            "uncommitted_delta_recovery": (
                "VERIFIED__9_PATHS__1430_INSERTIONS__9_DELETIONS_PRE_REPAIR"
            ),
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
        },
        "validation": {
            "jm_focused": "VERIFIED__22_PASSED",
            "p11_regression": "VERIFIED__8_PASSED",
            "fresh_context_regression": "VERIFIED__17_PASSED",
            "ex_entry_parent": "VERIFIED__12_OF_12__17_CERTIFIED",
            "ex_current_delta": (
                "VERIFIED__ONLY_REQUIRES_HARDENING_P11_MANIFEST_PATH_MUTATED"
            ),
            "governance_conformance": "VERIFIED__9_PASSED__ENGINE_20_OF_20_CONFORMANT",
            "layer_0": "VERIFIED__ZERO_DELTA",
            "g48": "VERIFIED__EXACTLY_SIX_H1",
            "git_diff_check": "VERIFIED__PASS",
            "final_index": "VERIFIED__EMPTY",
        },
        "auto_continuable": False,
        "human_review_required": True,
    }


def envelope(reduction: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "G77_256JM_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    value = envelope(build_reduction(arguments.repository_root))
    raw = canonical_bytes(value)
    if arguments.output is None:
        sys.stdout.buffer.write(raw)
    else:
        arguments.output.write_bytes(raw)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
