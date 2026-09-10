#!/usr/bin/env python3
"""Reduce the sole JY Phase-B FM invocation failure without replay."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
JY = ROOT / ".github/governance/evidence/g77_256jy_expired_operational_v1"
HEAD = "939d7eda8ff333b6cf0dfbd54d274aabefcba698"
TREE = "bce9f2863a7314a1e5e088066efeea52615d989d"
SUBJECT = "G77-256JX verify ER admission runtime checkout role separation"
GENERATION = "G77_256JY_ONE_FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATIONAL_COMMISSIONING_V1"
OPERATION = "G77_256JY_E05_EXPIRED_DENIAL_BEFORE_ENTRY_001"
SOURCE = JY / "G77_256JY_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
HANDOFF = JY / "G77_256JY_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
CONSUMPTION = JY / "G77_256JY_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json"
CONTEXT = JY / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
PHASE_A = JY / "G77_256JY_PREHUMAN_PHASE_A_REDUCTION_V1.json"
FAILURE = JY / "G77_256JY_PHASE_B_FM_INVOCATION_FAILURE_V1.json"
REDUCTION = JY / "G77_256JY_SPCE_TERMINAL_FAILURE_REDUCTION_V1.json"
P11 = ROOT / "tests/p11_da_operational_consumer_v1.py"

SOURCE_SHA256 = "413d0c8164a240b9853d2a95d215128dedca2cc86fa95da3dff7e41c8bafffd4"
HANDOFF_SHA256 = "7211842d95639b2d869a19af1c0848d61197b2dae66c931cf5dd1e9aa5584d9d"
HANDOFF_INNER_SHA256 = "e6664f7a0b333fca6d8d8886f691cb140f9cf9103f2b3e62b95992b4fce2210d"
SUPPLIED_SHA256 = "7211842d95639b2d869a19af1c0848d61197b2dae66c931cf5dd1e9aa5584d9"
P11_SHA256 = "38399ab9d1eb74dc2a231eb3a363064ba8b90077d6cdbf1d3494ca937b2127f5"
TERMINAL = (
    "M__FRESH_HUMAN_AUTHORIZED_EXPIRED_OPERATION_BLOCKED_AT_FM_"
    "SUPPLIED_AUTHORITY_HASH_SYNTAX_BEFORE_PRE"
)


class JYReductionError(RuntimeError):
    """One fail-closed terminal reduction error."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise JYReductionError(f"DUPLICATE_JSON_KEY:{key}")
        value[key] = item
    return value


def load_canonical(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(value, dict) or raw != canonical_bytes(value):
        raise JYReductionError(f"NONCANONICAL_JSON:{path.name}")
    return value


def validate_seal(envelope: dict[str, Any], inner: str) -> dict[str, Any]:
    value = envelope.get(inner)
    if not isinstance(value, dict) or envelope.get(f"{inner}_sha256") != (
        hashlib.sha256(canonical_bytes(value)).hexdigest()
    ):
        raise JYReductionError(f"INVALID_SEAL:{inner}")
    return value


def sealed(schema: str, inner: str, value: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": schema,
        inner: value,
        f"{inner}_sha256": hashlib.sha256(canonical_bytes(value)).hexdigest(),
    }


def write_once(path: Path, value: dict[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise JYReductionError(f"TERMINAL_ARTIFACT_COLLISION:{path.name}")
    path.write_bytes(canonical_bytes(value))


def git(*arguments: str) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
    ).strip()


def counters() -> dict[str, int]:
    return {
        "operational_authorization_count": 1,
        "authority_consumption_count": 1,
        "pre_operational_count": 0,
        "fm_operational_invocation_count": 1,
        "qemu_count": 0,
        "vm_count": 0,
        "operation_attempt_count": 0,
        "operational_request_count": 0,
        "expired_denial_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "retry_count": 0,
        "repair_retry_count": 0,
        "replay_count": 0,
    }


def reduce() -> None:
    if (
        git("branch", "--show-current") != "g77-256fl-wrong-attempt-preboot-blocker"
        or git("rev-parse", "HEAD") != HEAD
        or git("rev-parse", "HEAD^{tree}") != TREE
        or git("show", "-s", "--format=%s", "HEAD") != SUBJECT
        or git("diff", "--cached", "--name-only")
        or git("diff", "--name-only")
    ):
        raise JYReductionError("COMMITTED_BASELINE_OR_INDEX_DRIFT")
    if sha256(SOURCE) != SOURCE_SHA256 or sha256(HANDOFF) != HANDOFF_SHA256:
        raise JYReductionError("HUMAN_AUTHORITY_IDENTITY_DRIFT")

    handoff = validate_seal(load_canonical(HANDOFF), "authorization")
    if (
        handoff.get("authorization_source_sha256") != SOURCE_SHA256
        or hashlib.sha256(canonical_bytes(handoff)).hexdigest()
        != HANDOFF_INNER_SHA256
        or handoff.get("authorization_reusable") is not False
    ):
        raise JYReductionError("HUMAN_AUTHORITY_BINDING_DRIFT")
    consumed = validate_seal(load_canonical(CONSUMPTION), "checkpoint")
    if (
        consumed.get("authority_state_after") != "CONSUMED"
        or consumed.get("authority_consumed") != 1
        or consumed.get("grant_source_sha256") != SOURCE_SHA256
        or consumed.get("authority_handoff_file_sha256") != HANDOFF_SHA256
        or consumed.get("authority_handoff_inner_sha256") != HANDOFF_INNER_SHA256
    ):
        raise JYReductionError("AUTHORITY_CONSUMPTION_NOT_EXACT")
    phase_a = validate_seal(load_canonical(PHASE_A), "reduction")
    context = load_canonical(CONTEXT)
    if (
        phase_a.get("terminal")
        != "A__FRESH_JY_EXPIRED_PREAUTHORIZATION_PRESENTATION_READY_FOR_HUMAN_DECISION"
        or context.get("generation_identity") != GENERATION
        or context.get("operation_identity") != OPERATION
        or sha256(P11) != P11_SHA256
    ):
        raise JYReductionError("PHASE_A_OR_P11_DRIFT")
    receipt_paths = [Path(context["pre_receipt_path"]), Path(context["post_receipt_path"])]
    if any(path.exists() or path.is_symlink() for path in receipt_paths):
        raise JYReductionError("UNEXPECTED_PRE_OR_POST_RECEIPT")
    if len(SUPPLIED_SHA256) != 63 or SUPPLIED_SHA256 + "d" != HANDOFF_SHA256:
        raise JYReductionError("OBSERVED_MALFORMED_ARGUMENT_NOT_EXACT")

    recorded = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )
    invocation = sealed(
        "G77_256JY_PHASE_B_FM_INVOCATION_FAILURE_ENVELOPE_V1",
        "failure",
        {
            "schema_id": "G77_256JY_PHASE_B_FM_INVOCATION_FAILURE_V1",
            "recorded_at_utc": recorded,
            "generation_identity": GENERATION,
            "operation_identity": OPERATION,
            "invocation_count": 1,
            "process_exit_status": 1,
            "supplied_execution_authority_sha256": SUPPLIED_SHA256,
            "supplied_digest_length": len(SUPPLIED_SHA256),
            "actual_authority_file_sha256": HANDOFF_SHA256,
            "exact_exception_type": "RuntimeError",
            "exact_exception": "supplied execution authority hash malformed",
            "failure_function": "validate_execution_admission",
            "failure_boundary": "FM_FINAL_ADMISSION_BEFORE_PRE_RECEIPT",
            "pre_receipt_exists": False,
            "post_receipt_exists": False,
            "qemu_started": False,
            "vm_started": False,
            "operation_started": False,
            "retry_performed": False,
            "repair_retry_performed": False,
            "replay_performed": False,
            "observation_source": "DIRECT_SINGLE_EXEC_COMMAND_RESULT",
        },
    )
    write_once(FAILURE, invocation)

    reduction = sealed(
        "G77_256JY_SPCE_TERMINAL_FAILURE_REDUCTION_ENVELOPE_V1",
        "reduction",
        {
            "schema_id": "G77_256JY_SPCE_TERMINAL_FAILURE_REDUCTION_V1",
            "recorded_at_utc": recorded,
            "generation_identity": GENERATION,
            "operation_identity": OPERATION,
            "terminal": TERMINAL,
            "continuation_type": "SAME_GENERATION_SAME_ACCOUNT_PHASE_B_CONTINUATION",
            "human_authority": {
                "source_sha256": SOURCE_SHA256,
                "authentication": "VERIFIED__EXACT_HUMAN_SUPPLIED_ACT",
                "handoff_file_sha256": HANDOFF_SHA256,
                "handoff_inner_sha256": HANDOFF_INNER_SHA256,
                "consumption": "VERIFIED__EXACTLY_ONCE__NONREUSABLE",
            },
            "failure": {
                "artifact_path": FAILURE.relative_to(ROOT).as_posix(),
                "artifact_file_sha256": sha256(FAILURE),
                "artifact_inner_sha256": invocation["failure_sha256"],
                "exact_exception": "supplied execution authority hash malformed",
                "supplied_sha256": SUPPLIED_SHA256,
                "actual_sha256": HANDOFF_SHA256,
                "localized_cause": "FM_CLI_AUTHORITY_FILE_SHA256_ARGUMENT_TRUNCATED_BY_ONE_HEX_CHARACTER",
                "failure_boundary": "FM_FINAL_ADMISSION_BEFORE_PRE_RECEIPT",
            },
            "operational_counters": counters(),
            "expired": {
                "expected_reason": "one-use Human act expired before PRECLAIM",
                "check_reached": False,
                "denial_observed": False,
                "operational_status": "NOT_PROVEN_OPERATIONALLY",
            },
            "e05": {
                "before": "VERIFIED__11_OF_18",
                "after": "VERIFIED__11_OF_18",
                "credit": "VERIFIED__0",
                "frontier_before": "VERIFIED__7_UNSATISFIED_OF_18",
                "frontier_after": "VERIFIED__7_UNSATISFIED_OF_18",
            },
            "architecture": {
                "production_mutation_count": 0,
                "p11_implementation_mutation_count": 0,
                "new_owner_count": 0,
                "new_route_count": 0,
                "new_registry_count": 0,
                "new_generic_abstraction_count": 0,
                "new_constitutional_concept_count": 0,
                "production_route_before": 1,
                "production_route_after": 1,
                "production_route_delta": 0,
            },
            "reuse": {
                "ex_reused": "VERIFIED__17_OF_17",
                "ex_reconstructed": "VERIFIED__0",
            },
            "proof_yield": {
                "new_verified_capability_count": "VERIFIED__0__PHASE_B_OPERATIONAL",
                "new_blocker_localized_count": "VERIFIED__1",
                "e05_credit": "VERIFIED__0",
                "proof_reuse_count": "VERIFIED__17",
            },
            "frontier": {
                "last_verified_edge": "FRESH_HUMAN_AUTHORITY_AUTHENTICATED_AND_CONSUMED_EXACTLY_ONCE",
                "first_broken_edge": "FM_FINAL_ADMISSION_SUPPLIED_AUTHORITY_HASH_SYNTAX_GATE",
                "minimum_missing_capability": "EXACT_64_HEX_AUTHORITY_FILE_DIGEST_DELIVERY_TO_FM",
                "minimum_legal_next_delta": "SEPARATE_REPOSITORY_ONLY_POSTMORTEM_GENERATION__NO_JY_RETRY_AUTHORIZED",
            },
            "ccwim": {
                "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION",
                "authenticated_repository_continuation": "VERIFIED__YES",
                "previous_worker_conversation_required": "VERIFIED__NO",
                "previous_worker_memory_required": "VERIFIED__NO",
                "handoff_reconstruction_success": "VERIFIED__YES",
                "handoff_ambiguity_count": "VERIFIED__0",
                "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
                "continuation_type": "SAME_GENERATION_SAME_ACCOUNT_PHASE_B_CONTINUATION",
            },
            "auto_continuable": False,
            "human_review_required": True,
        },
    )
    write_once(REDUCTION, reduction)


if __name__ == "__main__":
    reduce()
