#!/usr/bin/env python3
"""Formalize JQ's authority-free EXPIRED preauthorization blocker.

This module reads committed repository evidence and static source only. It has
no authority creation/consumption, PRE, FM, QEMU, VM, request, P11-entry, or
protected-effect execution path.
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
BRANCH = "g77-256fl-wrong-attempt-preboot-blocker"
ORIGIN = "git@github.com:Aljosa3/sapianta-ecosystem.git"
ENTRY_HEAD = "8b4e47c296b313e437e695590589a818e977da9e"
ENTRY_TREE = "a97883ecd115106da22017255486326001e6d165"
ENTRY_SUBJECT = "G77-256JP verify post-JO EXPIRED operational readiness"
NESTED_ORIGIN = "git@github.com:Aljosa3/sapianta-core.git"
NESTED_HEAD = "3183bab71f8f30397c0309dd2e6d846d14a11f66"
NESTED_TREE = "7c32ec05efc2be43297849bc38ec8766514a523d"
NESTED_TAG = "sapianta-system-nested-authority-3183bab-v1"
JP_TERMINAL = (
    "A__POST_JO_COMMITTED_LIVE_BINDING_AND_EXPIRED_OPERATIONAL_READINESS_"
    "REPOSITORY_VERIFIED"
)
JJ_TERMINAL = "A__EXPIRED_VECTOR_DETERMINISTIC_REPOSITORY_FORMALIZATION_VERIFIED"
TERMINAL = "M__EXPIRED_PREAUTHORIZATION_ROUTE_CONTRACT_NOT_AVAILABLE"

JQ = Path(
    ".github/governance/evidence/"
    "g77_256jq_expired_fresh_human_authorized_operational_denial_before_"
    "p11_entry_v1"
)
REPORT = JQ / "G77_256JQ_G48_IMPLEMENTATION_REPORT_V1.md"
REDUCTION = JQ / "G77_256JQ_SPCE_TERMINAL_REPOSITORY_ONLY_BLOCKER_REDUCTION_V1.json"
FORMALIZER = JQ / "analysis/G77_256JQ_EXPIRED_PREAUTHORIZATION_BLOCKER_FORMALIZER_V1.py"
TEST = JQ / "tests/test_g77_256jq_expired_preauthorization_blocker_v1.py"
JQ_FILES = (REPORT, REDUCTION, FORMALIZER, TEST)
RECOVERED_JQ_FILES = {
    FORMALIZER.as_posix(): {
        "line_count": 469,
        "sha256": "7a3de5fea96c7be0378b16347d5d4cbe028aed1ee53609e1040aef5b3b3e41ca",
    },
    TEST.as_posix(): {
        "line_count": 155,
        "sha256": "74218756476f910280d41deb3cb32420ab77c08961aebfb52c34efb3ba796e01",
    },
}

JP_REDUCTION = Path(
    ".github/governance/evidence/"
    "g77_256jp_post_jo_committed_live_binding_and_expired_operational_"
    "readiness_reauthentication_v1/"
    "G77_256JP_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
JJ_REDUCTION = Path(
    ".github/governance/evidence/"
    "g77_256jj_expired_vector_deterministic_repository_formalization_v1/"
    "G77_256JJ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
CONTEXT_OWNER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
LAUNCHER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py"
)
GN_PRESENTATION = Path(
    ".github/governance/evidence/"
    "g77_256gn_human_authorization_presentation_binding_v1/presentation/"
    "G77_256GN_SEALED_REQUEST_HUMAN_AUTHORIZATION_PRESENTATION_V1.py"
)
ER_HARNESS = Path(
    ".github/governance/evidence/g77_256er_p11_operational_v1/harness/"
    "G77_256ER_P11_OPERATIONAL_HARNESS_V1.py"
)
FUTURE_ADAPTER = Path(
    ".github/governance/evidence/"
    "g77_256jc_future_guest_context_owner_projection_v1/adapter/"
    "G77_256JC_FUTURE_VECTOR_ADAPTER_V1.py"
)
P11 = Path("tests/p11_da_operational_consumer_v1.py")

SUPPORTED = (
    "FUTURE", "WRONG_ATTEMPT", "WRONG_CONTRACT", "WRONG_INPUT",
    "WRONG_PROVENANCE",
)
SOURCE_SHA256 = {
    CONTEXT_OWNER: "0c85aa41f87fb2e3e744a68b8b71778977a988c5ded0a30101d7f2313d719cd7",
    LAUNCHER: "65a5719bcace99bc875c2bf7c7334255716e57d5b06df6b2b0b084352f329402",
    GN_PRESENTATION: "be26ef5d5f54947f415df9b7539c144d9f3300997df71664b80c5f38ee1770dc",
    ER_HARNESS: "c6539d1cc60940b1999956965bff43923a270598a982cd19f976eadec0a93152",
    FUTURE_ADAPTER: "71b223a35a9fe33fdf4adac5fd1b93aa16a26006629761a4ea851d4ccd821104",
    P11: "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5",
}


class JQError(RuntimeError):
    """One deterministic fail-closed JQ formalization error."""


def fail(token: str) -> None:
    raise JQError(token)


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=cwd, text=True, stderr=subprocess.DEVNULL
    ).strip()


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            fail(f"DUPLICATE_JSON_KEY__{key}")
        value[key] = item
    return value


def load_envelope(path: Path, terminal: str) -> dict[str, Any]:
    envelope = json.loads(path.read_bytes(), object_pairs_hook=unique_object)
    reduction = envelope.get("reduction")
    if not isinstance(reduction, dict):
        fail("REDUCTION_MISSING")
    if envelope.get("reduction_sha256") != sha256_bytes(canonical_bytes(reduction)):
        fail("REDUCTION_SEAL_INVALID")
    if reduction.get("terminal") != terminal:
        fail("TERMINAL_INVALID")
    return reduction


def authenticate_entry() -> dict[str, Any]:
    observed = {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
        "remote_tracking_head": git("rev-parse", f"origin/{BRANCH}"),
        "index_empty": git("diff", "--cached", "--name-only") == "",
    }
    expected = {
        "branch": BRANCH, "head": ENTRY_HEAD, "tree": ENTRY_TREE,
        "subject": ENTRY_SUBJECT, "origin": ORIGIN,
        "remote_tracking_head": ENTRY_HEAD, "index_empty": True,
    }
    if observed != expected:
        fail("ENTRY_IDENTITY_MISMATCH")
    status = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=ROOT, text=True,
    ).splitlines()
    if any(not line.startswith("?? ") for line in status):
        fail("TRACKED_OR_INDEX_DELTA_DETECTED")
    allowed = {path.as_posix() for path in JQ_FILES}
    if not {line[3:] for line in status} <= allowed:
        fail("OUT_OF_SCOPE_UNTRACKED_DELTA")
    nested = ROOT / "sapianta_system"
    nested_state = {
        "origin": git("remote", "get-url", "origin", cwd=nested),
        "head": git("rev-parse", "HEAD", cwd=nested),
        "tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "clean": git("status", "--porcelain=v1", cwd=nested) == "",
        "detached": git("branch", "--show-current", cwd=nested) == "",
        "tag": git("describe", "--tags", "--exact-match", "HEAD", cwd=nested),
    }
    expected_nested = {
        "origin": NESTED_ORIGIN, "head": NESTED_HEAD, "tree": NESTED_TREE,
        "clean": True, "detached": True, "tag": NESTED_TAG,
    }
    if nested_state != expected_nested:
        fail("NESTED_AUTHORITY_MISMATCH")
    return observed | {
        "recovery_entry_worktree": "VERIFIED__EXPECTED_JQ_EVIDENCE_ONLY_DIRTY",
        "recovery_entry_index_empty": "VERIFIED__YES",
        "direct_remote_equality": "VERIFIED__DIRECT_READ_ONLY_LS_REMOTE_AT_ENTRY",
        "nested_remote_tag_equality": "VERIFIED__DIRECT_READ_ONLY_LS_REMOTE_AT_ENTRY",
        "current_delta_scope": "VERIFIED__JQ_EVIDENCE_ONLY",
        "nested_authority": nested_state,
    }


def _string_assignments(tree: ast.Module) -> dict[str, str]:
    values: dict[str, str] = {}
    for node in tree.body:
        if (
            isinstance(node, ast.Assign) and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            values[node.targets[0].id] = node.value.value
    return values


def assigned_string_set(path: Path, assignment: str) -> tuple[str, ...]:
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8"), filename=str(path))
    names = _string_assignments(tree)
    for node in tree.body:
        if not (
            isinstance(node, ast.Assign) and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == assignment
        ):
            continue
        value = node.value.args[0] if isinstance(node.value, ast.Call) else node.value
        if not isinstance(value, (ast.Set, ast.Tuple, ast.List)):
            fail(f"{assignment}_COLLECTION_INVALID")
        result = []
        for item in value.elts:
            if isinstance(item, ast.Constant) and isinstance(item.value, str):
                result.append(item.value)
            elif isinstance(item, ast.Name) and item.id in names:
                result.append(names[item.id])
            else:
                fail(f"{assignment}_ELEMENT_INVALID")
        return tuple(sorted(result))
    fail(f"{assignment}_MISSING")


def authenticate_sources() -> dict[str, str]:
    observed = {
        path.as_posix(): sha256_bytes((ROOT / path).read_bytes())
        for path in SOURCE_SHA256
    }
    expected = {path.as_posix(): digest for path, digest in SOURCE_SHA256.items()}
    if observed != expected:
        fail("COMMITTED_SOURCE_IDENTITY_MISMATCH")
    return observed


def reconstruct_jp() -> dict[str, Any]:
    jp = load_envelope(ROOT / JP_REDUCTION, JP_TERMINAL)
    required = {
        "terminal": JP_TERMINAL,
        "production_route_count": "VERIFIED__1",
        "ex_reused": "VERIFIED__17_OF_17",
        "ex_reconstructed": "VERIFIED__0",
        "e05": "VERIFIED__11_OF_18",
        "e05_credit": "VERIFIED__0",
        "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
    }
    observed = {
        "terminal": jp["terminal"],
        "production_route_count": jp["live_binding"]["production_route_count"],
        "ex_reused": jp["ex_successor_reauthentication"]["ex_reused"],
        "ex_reconstructed": jp["ex_successor_reauthentication"]["ex_reconstructed"],
        "e05": jp["e05"]["after"],
        "e05_credit": jp["e05"]["credit"],
        "expired_operational_status": jp["e05"]["expired_operational_status"],
    }
    if observed != required or set(jp["operational_counters"].values()) != {"VERIFIED__0"}:
        fail("JP_RECONSTRUCTION_MISMATCH")
    return observed | {
        "operational_counters": "VERIFIED__ALL_ZERO",
        "frontier": jp["frontier"],
    }


def formalize_blocker() -> dict[str, Any]:
    context_vectors = assigned_string_set(CONTEXT_OWNER, "SUPPORTED_OPERATION_VECTORS")
    presentation_vectors = assigned_string_set(GN_PRESENTATION, "SUPPORTED_VECTORS")
    if context_vectors != SUPPORTED or presentation_vectors != SUPPORTED:
        fail("CLOSED_VECTOR_SET_DRIFT")
    if "EXPIRED" in context_vectors or "EXPIRED" in presentation_vectors:
        fail("EXPIRED_UNEXPECTEDLY_SUPPORTED")

    jj = load_envelope(ROOT / JJ_REDUCTION, JJ_TERMINAL)
    coordinates = jj["expired_semantic_model"]["temporal_coordinates"]
    if coordinates != {
        "baseline_preclaim_time_unix_ns": 500,
        "expired_preclaim_time_unix_ns": 1000,
        "valid_from_unix_ns": 100,
        "valid_until_unix_ns": 1000,
    }:
        fail("JJ_TEMPORAL_COORDINATE_DRIFT")

    er = (ROOT / ER_HARNESS).read_text(encoding="utf-8")
    p11 = (ROOT / P11).read_text(encoding="utf-8")
    future = (ROOT / FUTURE_ADAPTER).read_text(encoding="utf-8")
    clock = (
        "    now = time.time_ns()\n"
        "    valid_from = now - 1_000_000_000\n"
        "    valid_until = now + 300_000_000_000\n"
    )
    if er.count(clock) != 1:
        fail("ER_ACT_VALIDITY_PRODUCER_DRIFT")
    required_p11 = (
        'preclaim_time = temporal_binding["coordinate_unix_ns"]',
        'if temporal_decision == "FUTURE":',
        '_fail("one-use Human act is future at PRECLAIM")',
        'if temporal_decision == "EXPIRED":',
        'self._store.terminate_unclaimed(available, OwnerStateName.EXPIRED)',
        '_fail("one-use Human act expired before PRECLAIM")',
        '"P11_DA_OPERATIONAL_PRECLAIM"',
    )
    if not all(token in p11 for token in required_p11):
        fail("P11_TEMPORAL_DECISION_DRIFT")
    future_specialization_tokens = (
        '"    now = 500\\n    valid_from = 100\\n    valid_until = 1000\\n"',
        '"valid_from_unix_ns": FUTURE_VALID_FROM_UNIX_NS',
        '"valid_until_unix_ns": VALID_UNTIL_UNIX_NS',
        '"            now_unix_ns=EVALUATION_TIME_UNIX_NS,\\n"',
        "FUTURE_SUBMISSION_DENIAL_CHECKPOINT_V1",
    )
    if not all(token in future for token in future_specialization_tokens):
        fail("ONLY_TEMPORAL_SPECIALIZATION_DRIFT")

    truth_table = {"999": "CURRENT", "1000": "EXPIRED", "1001": "EXPIRED"}
    if any(
        ("FUTURE" if coordinate < 100 else
         "EXPIRED" if coordinate >= 1000 else "CURRENT") != decision
        for coordinate, decision in (
            (999, "CURRENT"), (1000, "EXPIRED"), (1001, "EXPIRED")
        )
    ):
        fail("TEMPORAL_BOUNDARY_MODEL_INVALID")

    return {
        "critical_semantic_answer": "VERIFIED__NO",
        "route_owner": CONTEXT_OWNER.as_posix(),
        "route_vector_derivation": "GENERATION_IDENTITY_SUFFIX__CLOSED_SET",
        "context_supported_vectors": list(context_vectors),
        "human_presentation_supported_vectors": list(presentation_vectors),
        "expired_context_vector_supported": "VERIFIED__NO",
        "expired_human_presentation_vector_supported": "VERIFIED__NO",
        "human_presentation_rejection": "SEALED_REQUEST_VECTOR_INVALID",
        "sealed_preclaim_coordinate_unix_ns": 1000,
        "required_act_interval": {
            "valid_from_unix_ns": 100, "valid_until_unix_ns": 1000,
        },
        "current_er_act_interval_producer": {
            "valid_from_unix_ns": "time.time_ns() - 1_000_000_000",
            "valid_until_unix_ns": "time.time_ns() + 300_000_000_000",
        },
        "current_er_result_at_sealed_coordinate": (
            "FUTURE_WHEN_NOW_UNIX_NS_GT_1000001000__CURRENT_RUNTIME_DOMAIN"
        ),
        "fixed_required_interval_at_wall_clock_submission": (
            "REJECTED_AS_NOT_CURRENT__SUBMISSION_DOMAIN"
        ),
        "only_fixed_interval_specialization": (
            "JC_FUTURE__DENIES_AT_SUBMISSION__NOT_AN_EXPIRED_OPERATION_ROUTE"
        ),
        "temporal_domain_predicates": {
            "future": "preclaim < valid_from",
            "current": "valid_from <= preclaim < valid_until",
            "expired": "preclaim >= valid_until",
        },
        "valid_until_1000_truth_table": truth_table,
        "wall_clock_is_governed_preclaim_authority": "VERIFIED__NO",
        "submission_time_is_governed_preclaim_coordinate": "VERIFIED__NO",
        "p11_expired_denial_reason": "one-use Human act expired before PRECLAIM",
        "p11_expired_denial_boundary": "BEFORE_P11_DA_OPERATIONAL_PRECLAIM_APPEND",
        "exact_expired_candidate_materializable_without_implementation": "VERIFIED__NO",
        "exact_expired_preauthorization_checkpoint_materializable": "VERIFIED__NO",
        "minimum_missing_capability": (
            "GOVERNED_EXPIRED_COMPATIBLE_HUMAN_AUTHORITY_ACT_"
            "MATERIALIZATION_AND_PRESENTATION_BINDING"
        ),
    }


def zero_counters() -> dict[str, str]:
    return {name: "VERIFIED__0" for name in (
        "operational_authorization_count", "authority_consumption_count",
        "pre_operational_count", "fm_operational_invocation_count", "qemu_count",
        "vm_count", "operation_attempt_count", "request_count",
        "p11_entry_count", "protected_invocation_count",
        "protected_effect_count", "retry_count", "repair_retry_count", "replay_count",
    )}


def build_reduction() -> dict[str, Any]:
    blocker = formalize_blocker()
    return {
        "schema_id": "G77_256JQ_SPCE_TERMINAL_REPOSITORY_ONLY_BLOCKER_REDUCTION_V1",
        "generation": "G77-256JQ",
        "mode": "SAME_GENERATION_PROVIDER_LIMIT_RECOVERY__EVIDENCE_ONLY",
        "terminal": TERMINAL,
        "spce": [
            "AUTHENTICATE", "RECOVER_EXISTING_JQ_DELTA", "RECONSTRUCT_BLOCKER",
            "VERIFY_BLOCKER", "REUSE_EX", "COMPLETE_FAIL_CLOSED_REDUCTION", "STOP",
        ],
        "entry": authenticate_entry(),
        "recovery_provenance": {
            "recovery_type": "SAME_GENERATION_PROVIDER_LIMIT_RECOVERY",
            "original_generation": "G77-256JQ",
            "new_generation_created": "VERIFIED__NO",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "recovery_existing_delta_authenticated": "VERIFIED__YES",
            "recovered_file_count": "VERIFIED__2",
            "recovered_addition_count": "VERIFIED__624",
            "recovered_files_at_entry": RECOVERED_JQ_FILES,
            "recovery_duplicate_operation_count": "VERIFIED__0",
            "recovery_operation_replay_count": "VERIFIED__0",
        },
        "jp_reconstruction": reconstruct_jp(),
        "source_identities": authenticate_sources(),
        "blocker": blocker,
        "authority_boundary": {
            "candidate_materialized": "VERIFIED__0",
            "preauthorization_checkpoint_materialized": "VERIFIED__0",
            "human_authorization_request_materialized": "VERIFIED__0",
            "human_authorization_presentation_materialized": "VERIFIED__0",
            "human_authority_created_or_present": "VERIFIED__0",
            "human_authority_required": "NOT_APPLICABLE__PREAUTHORIZATION_BLOCKED",
            "human_authority_assurance_status": (
                "NOT_APPLICABLE__NO_HUMAN_REQUEST_PRESENTATION_OR_ACT_CREATED"
            ),
            "human_review_required": True,
            "auto_continuable": False,
        },
        "authority_separation": {
            "certified_is_authorized": "VERIFIED__NO",
            "certified_without_valid_authorization_protected_effect_count": "VERIFIED__0",
            "protected_machine_effect_without_valid_p11_authority_count": "VERIFIED__0",
            "worker_bypass_count": "VERIFIED__0",
            "provider_capability_is_execution_authority": "VERIFIED__NO",
            "temporal_coordinate_is_execution_human_p11_or_effect_authority": "VERIFIED__NO",
            "request_entry_invocation_effect_are_distinct": "VERIFIED__YES",
        },
        "operational_counters": zero_counters(),
        "e05": {
            "before": "VERIFIED__11_OF_18", "after": "VERIFIED__11_OF_18",
            "credit": "VERIFIED__0", "frontier_distance": "VERIFIED__7_UNSATISFIED_OF_18",
            "expired_operational_status": "NOT_PROVEN_OPERATIONALLY",
        },
        "architecture": {
            "p11_implementation_mutation_count": "VERIFIED__0",
            "production_mutation_count": "VERIFIED__0",
            "new_owner_count": "VERIFIED__0", "new_route_count": "VERIFIED__0",
            "new_registry_count": "VERIFIED__0",
            "new_generic_abstraction_count": "VERIFIED__0",
            "new_constitutional_concept_count": "VERIFIED__0",
            "production_route_before": "VERIFIED__1",
            "production_route_after": "VERIFIED__1",
            "production_route_delta": "VERIFIED__0",
            "parallel_flow_created": "VERIFIED__NO",
        },
        "proof_yield": {
            "new_verified_capability_count": "VERIFIED__0",
            "new_blocker_localized_count": "VERIFIED__1",
            "e05_credit": "VERIFIED__0",
            "proof_reuse_count": "VERIFIED__17__EX_COMMON_CAPABILITIES",
        },
        "reuse": {
            "ex_reused": "VERIFIED__17_OF_17", "ex_reconstructed": "VERIFIED__0",
            "existing_certified_capabilities_reused": (
                "EX_17_OF_17__JP__JM__JL__JJ__JO__FM__ER__P11__GN_STATIC_CONTRACTS"
            ),
            "new_capability_set": (
                "VERIFIED__EMPTY__BLOCKER_LOCALIZATION_IS_EVIDENCE_NOT_CAPABILITY"
            ),
            "unreachable_existing_capability_set": "VERIFIED__EMPTY",
        },
        "metrics": {
            "project_progress": "VERIFIED__JQ_PREAUTHORIZATION_BLOCKER_LOCALIZED",
            "project_progress_estimate": "NOT_MEASURED__NO_CERTIFIED_TOTAL_PROJECT_DENOMINATOR",
            "informal_project_progress_estimate": (
                "ESTIMATED__EXPIRED_OPERATION_REQUIRES_ONE_SEPARATE_GOVERNED_"
                "AUTHORITY_MATERIALIZATION_AND_PRESENTATION_BINDING_DELTA"
            ),
            "constitutional_health_evidence": (
                "VERIFIED__FAIL_CLOSED_BEFORE_AUTHORITY_OR_OPERATION_ON_EXACT_CONTRACT_GAP"
            ),
            "shadow_automation_status": "VERIFIED__ABSENT",
            "constitutional_frontier_distance": "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR",
            "governance_efficience": "ESTIMATED__HIGH_REUSE_AND_EARLY_FAIL_CLOSED_LOCALIZATION",
            "overengineering_risk": "ESTIMATED__LOW__FOUR_EVIDENCE_FILES_ZERO_PRODUCTION_MUTATION",
            "cognition_provenance": "VERIFIED__COMMITTED_REPOSITORY_EVIDENCE_PRIMARY",
            "cognition_assisted_handoff": "VERIFIED__JP_TO_JQ_REPOSITORY_CONTINUATION",
            "candidate_capability": "NOT_PROVEN__EXPIRED_OPERATION_CANDIDATE_NOT_MATERIALIZED",
            "shadow_design_target": (
                "NOT_PROVEN__GOVERNED_EXPIRED_COMPATIBLE_HUMAN_AUTHORITY_ACT_"
                "MATERIALIZATION_AND_PRESENTATION_BINDING"
            ),
            "constitutional_continuation_progress": (
                "VERIFIED__JP_READINESS_REINTERPRETATION_PREVENTED_AND_JQ_BLOCKER_LOCALIZED"
            ),
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
            "recovery_type": "SAME_GENERATION_PROVIDER_LIMIT_RECOVERY",
            "recovery_source_generation": "G77-256JQ",
            "recovery_existing_delta_authenticated": "VERIFIED__YES",
            "recovery_duplicate_operation_count": "VERIFIED__0",
            "recovery_operation_replay_count": "VERIFIED__0",
        },
        "periodic_metrics": {
            "aigol_codex_work_share": "NOT_MEASURED",
            "prompt_context_reuse_ratio": "NOT_MEASURED",
            "token_benchmark": "NOT_MEASURED",
            "lcrr": "NOT_MEASURED",
        },
        "frontier": {
            "last_verified_edge": (
                "POST_JO_COMMITTED_LIVE_BINDING_AND_EXPIRED_OPERATIONAL_"
                "READINESS_REPOSITORY_VERIFIED"
            ),
            "first_broken_edge": (
                "EXPIRED_PREAUTHORIZATION_CANDIDATE_CANNOT_BE_TRUTHFULLY_"
                "MATERIALIZED_BY_CURRENT_HUMAN_AUTHORITY_ROUTE"
            ),
            "minimum_missing_capability": (
                "GOVERNED_EXPIRED_COMPATIBLE_HUMAN_AUTHORITY_ACT_"
                "MATERIALIZATION_AND_PRESENTATION_BINDING"
            ),
            "minimum_legal_next_delta": (
                "SEPARATE_REPOSITORY_ONLY_MINIMUM_IMPLEMENTATION_GENERATION_TO_BIND_"
                "EXPIRED_INTO_EXISTING_HUMAN_AUTHORITY_ROUTE__NO_OPERATION"
            ),
            "constitutional_frontier_distance": (
                "NOT_MEASURED__NO_GOVERNED_UNIVERSAL_SCALAR"
            ),
        },
        "auto_continuable": False,
        "human_review_required": True,
    }


def build_envelope() -> dict[str, Any]:
    reduction = build_reduction()
    return {
        "schema_id": "G77_256JQ_SPCE_TERMINAL_REPOSITORY_ONLY_BLOCKER_ENVELOPE_V1",
        "reduction": reduction,
        "reduction_sha256": sha256_bytes(canonical_bytes(reduction)),
    }


if __name__ == "__main__":
    print(canonical_bytes(build_envelope()).decode("utf-8"), end="")
