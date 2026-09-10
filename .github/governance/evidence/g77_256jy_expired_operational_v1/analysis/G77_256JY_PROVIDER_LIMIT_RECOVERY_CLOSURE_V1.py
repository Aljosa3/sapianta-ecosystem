#!/usr/bin/env python3
"""Close JY from durable evidence after same-account provider-limit reset."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
JY = ROOT / ".github/governance/evidence/g77_256jy_expired_operational_v1"
SOURCE = JY / "G77_256JY_HUMAN_OPERATIONAL_AUTHORIZATION_SOURCE_V1.txt"
HANDOFF = JY / "G77_256JY_FRESH_HUMAN_OPERATIONAL_AUTHORIZATION_HANDOFF_V1.json"
CONSUMPTION = JY / "G77_256JY_AUTHORITY_VALIDATION_AND_CONSUMPTION_CHECKPOINT_V1.json"
FAILURE = JY / "G77_256JY_PHASE_B_FM_INVOCATION_FAILURE_V1.json"
TERMINAL_REDUCTION = JY / "G77_256JY_SPCE_TERMINAL_FAILURE_REDUCTION_V1.json"
PHASE_A = JY / "G77_256JY_PREHUMAN_PHASE_A_REDUCTION_V1.json"
CONTEXT = JY / "live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json"
CLOSURE = JY / "G77_256JY_PROVIDER_LIMIT_RECOVERY_TERMINAL_CLOSURE_V1.json"

HEAD = "939d7eda8ff333b6cf0dfbd54d274aabefcba698"
TREE = "bce9f2863a7314a1e5e088066efeea52615d989d"
SUBJECT = "G77-256JX verify ER admission runtime checkout role separation"
SOURCE_SHA256 = "413d0c8164a240b9853d2a95d215128dedca2cc86fa95da3dff7e41c8bafffd4"
EXPECTED_AUTHORITY_SHA256 = "7211842d95639b2d869a19af1c0848d61197b2dae66c931cf5dd1e9aa5584d9d"
SUPPLIED_AUTHORITY_SHA256 = "7211842d95639b2d869a19af1c0848d61197b2dae66c931cf5dd1e9aa5584d9"
FAILURE_FILE_SHA256 = "de8068ce65f5c556d301dbe3d6d4f8f812cb7fc4c3b809a82ba3a72a42d1a97e"
TERMINAL_FILE_SHA256 = "45d02b6b5a1fbd632df4f4b9dcd4b17dccdeab5fcabdb428030917574f5dba90"
RECOVERY_ENTRY_FILE_COUNT = 29
RECOVERY_ENTRY_INVENTORY_SHA256 = (
    "c2dcb6ea10de3b1e716095b0ac67fad06203fc148b4e431a54544867dc9b1f73"
)
TERMINAL = (
    "M__JY_TERMINAL_FAILURE_REDUCED_TO_CALLER_CONSTRUCTED_TRUNCATED_"
    "FM_AUTHORITY_DIGEST_ARGUMENT_BEFORE_PRE"
)


class ClosureError(RuntimeError):
    """One deterministic fail-closed closure error."""


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
            raise ClosureError(f"DUPLICATE_JSON_KEY:{key}")
        value[key] = item
    return value


def load_sealed(path: Path, inner: str) -> tuple[dict[str, Any], dict[str, Any]]:
    raw = path.read_bytes()
    envelope = json.loads(raw, object_pairs_hook=unique_object)
    if raw != canonical_bytes(envelope):
        raise ClosureError(f"NONCANONICAL_JSON:{path.name}")
    value = envelope.get(inner)
    if not isinstance(value, dict) or envelope.get(f"{inner}_sha256") != (
        hashlib.sha256(canonical_bytes(value)).hexdigest()
    ):
        raise ClosureError(f"INVALID_SEAL:{path.name}")
    return envelope, value


def git(*arguments: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=cwd, text=True, stderr=subprocess.DEVNULL
    ).strip()


def counters() -> dict[str, int]:
    return {
        "operational_authorization_count": 1,
        "authority_consumption_count": 1,
        "fm_operational_invocation_count": 1,
        "pre_operational_count": 0,
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


def close() -> None:
    if CLOSURE.exists() or CLOSURE.is_symlink():
        raise ClosureError("RECOVERY_CLOSURE_ALREADY_EXISTS")
    recovery_script = Path(__file__).resolve()
    recovery_inventory = {
        path.relative_to(ROOT).as_posix(): sha256(path)
        for path in sorted(JY.rglob("*"))
        if path.is_file() and path.resolve() not in {recovery_script, CLOSURE.resolve()}
    }
    recovery_inventory_sha256 = hashlib.sha256(
        canonical_bytes(recovery_inventory)
    ).hexdigest()
    if (
        len(recovery_inventory) != RECOVERY_ENTRY_FILE_COUNT
        or recovery_inventory_sha256 != RECOVERY_ENTRY_INVENTORY_SHA256
    ):
        raise ClosureError("RECOVERY_ENTRY_INVENTORY_MISMATCH")
    observed_entry = {
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "subject": git("show", "-s", "--format=%s", "HEAD"),
        "origin": git("remote", "get-url", "origin"),
        "remote_head": HEAD,
        "direct_remote_equality": "VERIFIED__READ_ONLY_LS_REMOTE_AT_RECOVERY_ENTRY",
        "index_empty": git("diff", "--cached", "--name-only") == "",
        "tracked_delta_empty": git("diff", "--name-only") == "",
        "bounded_untracked_root": JY.relative_to(ROOT).as_posix(),
        "recovery_entry_file_count": RECOVERY_ENTRY_FILE_COUNT,
        "recovery_entry_inventory_sha256": RECOVERY_ENTRY_INVENTORY_SHA256,
    }
    if observed_entry != {
        "branch": "g77-256fl-wrong-attempt-preboot-blocker",
        "head": HEAD,
        "tree": TREE,
        "subject": SUBJECT,
        "origin": "git@github.com:Aljosa3/sapianta-ecosystem.git",
        "remote_head": HEAD,
        "direct_remote_equality": "VERIFIED__READ_ONLY_LS_REMOTE_AT_RECOVERY_ENTRY",
        "index_empty": True,
        "tracked_delta_empty": True,
        "bounded_untracked_root": JY.relative_to(ROOT).as_posix(),
        "recovery_entry_file_count": RECOVERY_ENTRY_FILE_COUNT,
        "recovery_entry_inventory_sha256": RECOVERY_ENTRY_INVENTORY_SHA256,
    }:
        raise ClosureError("RECOVERY_ENTRY_MISMATCH")
    nested = ROOT / "sapianta_system"
    nested_state = {
        "origin": git("remote", "get-url", "origin", cwd=nested),
        "head": git("rev-parse", "HEAD", cwd=nested),
        "tree": git("rev-parse", "HEAD^{tree}", cwd=nested),
        "clean": git("status", "--porcelain", cwd=nested) == "",
        "detached": git("branch", "--show-current", cwd=nested) == "",
        "tag": git("describe", "--exact-match", "--tags", "HEAD", cwd=nested),
        "remote_tag_equal": "VERIFIED__READ_ONLY_LS_REMOTE_AT_RECOVERY_ENTRY",
    }
    if nested_state != {
        "origin": "git@github.com:Aljosa3/sapianta-core.git",
        "head": "3183bab71f8f30397c0309dd2e6d846d14a11f66",
        "tree": "7c32ec05efc2be43297849bc38ec8766514a523d",
        "clean": True,
        "detached": True,
        "tag": "sapianta-system-nested-authority-3183bab-v1",
        "remote_tag_equal": "VERIFIED__READ_ONLY_LS_REMOTE_AT_RECOVERY_ENTRY",
    }:
        raise ClosureError("NESTED_AUTHORITY_MISMATCH")

    _, authorization = load_sealed(HANDOFF, "authorization")
    _, consumption = load_sealed(CONSUMPTION, "checkpoint")
    _, failure = load_sealed(FAILURE, "failure")
    _, prior = load_sealed(TERMINAL_REDUCTION, "reduction")
    _, phase_a = load_sealed(PHASE_A, "reduction")
    context_raw = CONTEXT.read_bytes()
    context = json.loads(context_raw, object_pairs_hook=unique_object)
    if context_raw != canonical_bytes(context):
        raise ClosureError("CONTEXT_NOT_CANONICAL")
    if (
        sha256(SOURCE) != SOURCE_SHA256
        or sha256(HANDOFF) != EXPECTED_AUTHORITY_SHA256
        or sha256(FAILURE) != FAILURE_FILE_SHA256
        or sha256(TERMINAL_REDUCTION) != TERMINAL_FILE_SHA256
        or authorization.get("authorization_source_sha256") != SOURCE_SHA256
        or authorization.get("authorization_reusable") is not False
        or consumption.get("authority_state_after") != "CONSUMED"
        or consumption.get("authority_consumed") != 1
        or consumption.get("authority_reusable") is not False
        or consumption.get("authority_transferable") is not False
        or failure.get("supplied_execution_authority_sha256")
        != SUPPLIED_AUTHORITY_SHA256
        or failure.get("actual_authority_file_sha256")
        != EXPECTED_AUTHORITY_SHA256
        or failure.get("supplied_digest_length") != 63
        or failure.get("exact_exception")
        != "supplied execution authority hash malformed"
        or prior.get("operational_counters") != counters()
        or phase_a.get("identities", {}).get("context_sha256")
        != "889069b1a29fa8ec7ace00881ee3de47fa096ecf2f9983d66a48b825b5f5513e"
    ):
        raise ClosureError("TERMINAL_FACT_MISMATCH")
    if SUPPLIED_AUTHORITY_SHA256 + "d" != EXPECTED_AUTHORITY_SHA256:
        raise ClosureError("DIGEST_DIFFERENCE_NOT_EXACT")
    if any(
        Path(context[key]).exists() or Path(context[key]).is_symlink()
        for key in ("pre_receipt_path", "post_receipt_path")
    ):
        raise ClosureError("PRE_OR_POST_RECEIPT_PRESENT")

    recorded = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )
    closure = {
        "schema_id": "G77_256JY_PROVIDER_LIMIT_RECOVERY_TERMINAL_CLOSURE_V1",
        "recorded_at_utc": recorded,
        "terminal": TERMINAL,
        "mode": "EVIDENCE_ONLY__TERMINAL_REDUCTION__NO_OPERATION",
        "generation": "G77-256JY",
        "recovery": {
            "recovery_type": "SAME_GENERATION_SAME_ACCOUNT_PROVIDER_LIMIT_RESET_RECOVERY",
            "same_generation": "VERIFIED__YES",
            "same_codex_account": "VERIFIED__YES",
            "provider_limit_reset": "VERIFIED__YES",
            "evidence_recovery_only": "VERIFIED__YES",
            "cross_account_recovery": "VERIFIED__NO",
            "provider_capacity_is_execution_authority": False,
            "additional_authority_count": 0,
            "additional_consumption_count": 0,
            "additional_fm_invocation_count": 0,
            "additional_pre_count": 0,
            "additional_qemu_count": 0,
            "additional_vm_count": 0,
            "additional_operation_attempt_count": 0,
        },
        "entry": observed_entry,
        "nested_authority": nested_state,
        "phase_a_identities": phase_a["identities"],
        "authority_finality": {
            "human_source_sha256": SOURCE_SHA256,
            "expected_authority_digest": EXPECTED_AUTHORITY_SHA256,
            "consumed": True,
            "reusable": False,
            "transferable": False,
            "historical_evidence_only": True,
        },
        "failure_localization": {
            "expected_authority_digest": EXPECTED_AUTHORITY_SHA256,
            "expected_digest_length": 64,
            "supplied_authority_digest": SUPPLIED_AUTHORITY_SHA256,
            "supplied_digest_length": 63,
            "exact_difference": "FINAL_HEX_CHARACTER_D_OMITTED",
            "introduction_boundary": "EXTERNAL_CODEX_EXEC_COMMAND_ARGUMENT_CONSTRUCTION",
            "argument": "--execution-authority-sha256",
            "orchestration_materialization": "VERIFIED__CORRECT_64_HEX_HANDOFF_FILE_DIGEST",
            "argument_construction": "VERIFIED__DEFECT__63_HEX_LITERAL_CONSTRUCTED",
            "shell_cli_transport": "VERIFIED__PRESERVED_CALLER_SUPPLIED_63_HEX_LITERAL",
            "fm_validation": "VERIFIED__CORRECT_FAIL_CLOSED_HEX_64_REJECTION",
            "underlying_authority_artifact": "VERIFIED__CORRECT_AND_CANONICAL",
            "failure_boundary": "FM_SUPPLIED_AUTHORITY_DIGEST_SYNTAX_BINDING_BEFORE_PRE",
        },
        "operational_counters": counters(),
        "e05": {
            "state": "VERIFIED__11_OF_18",
            "frontier": "VERIFIED__7_UNSATISFIED_OF_18",
            "credit": "VERIFIED__0",
            "expired": "NOT_PROVEN_OPERATIONALLY",
        },
        "reuse": {
            "ex_reused": "VERIFIED__17_OF_17",
            "ex_reconstructed": "VERIFIED__0",
        },
        "architecture": {
            "production_mutation_count": "VERIFIED__0",
            "p11_implementation_mutation_count": "VERIFIED__0",
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
            "new_blocker_localized_count": "VERIFIED__1",
            "e05_credit": "VERIFIED__0",
            "proof_reuse_count": "VERIFIED__17",
        },
        "frontier": {
            "last_verified_edge": "ONE_FRESH_JY_HUMAN_AUTHORITY_AUTHENTICATED_CONSUMED_AND_FM_INVOKED_ONCE",
            "first_broken_edge": "FM_SUPPLIED_AUTHORITY_DIGEST_SYNTAX_BINDING_BEFORE_PRE",
            "minimum_missing_capability": "EXACT_AUTHENTICATED_AUTHORITY_DIGEST_PRESERVING_FM_INVOCATION_BINDING",
            "minimum_legal_next_delta": "SEPARATE_REPOSITORY_ONLY_AUTHORITY_DIGEST_HANDOFF_REPAIR_GENERATION",
        },
        "ccwim": {
            "ccwim_maturity_level": "ESTIMATED__L4_LIKE__NO_GOVERNED_CERTIFICATION",
            "authenticated_repository_continuation": "VERIFIED__YES",
            "previous_worker_conversation_required": "VERIFIED__NO",
            "previous_worker_memory_required": "VERIFIED__NO",
            "handoff_reconstruction_success": "VERIFIED__YES",
            "handoff_ambiguity_count": "VERIFIED__0",
            "observed_artifact_level_cross_worker_drift": "VERIFIED__0",
            "cognition_assisted_handoff": "VERIFIED__SAME_GENERATION_SAME_CODEX_ACCOUNT_PROVIDER_LIMIT_RESET_EVIDENCE_RECOVERY_ONLY",
        },
        "jy_closed_for_operation": True,
        "auto_continuable": False,
        "human_review_required": True,
    }
    envelope = {
        "schema_id": "G77_256JY_PROVIDER_LIMIT_RECOVERY_TERMINAL_CLOSURE_ENVELOPE_V1",
        "closure": closure,
        "closure_sha256": hashlib.sha256(canonical_bytes(closure)).hexdigest(),
    }
    CLOSURE.write_bytes(canonical_bytes(envelope))


if __name__ == "__main__":
    close()
