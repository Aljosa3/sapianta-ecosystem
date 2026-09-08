#!/usr/bin/env python3
"""Project the current FUTURE owner onto the existing FM/ER/FC/P11 route.

JC retains IZ semantics while separating the current FM context owner from the
detached IF runtime checkout. Runtime use still requires a later committed
target, fresh Human authorization, and a separately governed one-shot operation.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
from types import ModuleType
from typing import Any, Mapping


GUEST_REPOSITORY_ROOT = Path("/mnt/aigol")
GUEST_CONTEXT_PATH = Path("/mnt/g77-evidence/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json")
FC_ADAPTER = Path(
    ".github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/harness/"
    "G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
)
FC_ADAPTER_SHA256 = "7ae104802f49613ca60836913d2c68269b59728bc35bb677fdb3637aaf4b84c6"
ER_HARNESS = Path(
    ".github/governance/evidence/g77_256er_p11_operational_v1/harness/"
    "G77_256ER_P11_OPERATIONAL_HARNESS_V1.py"
)
ER_HARNESS_SHA256 = "4a2a84ff83c61bfec013b4bcd20eb16905eeb240869182edd6c0d948444bae89"
IE_PRODUCER = Path(
    ".github/governance/evidence/g77_256ie_future_formalization_v1/producer/"
    "G77_256IE_FUTURE_VECTOR_PRODUCER_V1.py"
)
IE_PRODUCER_SHA256 = "a683e65b8f2a84f67851e2516bf50d5d7fc3d0fe25a5b0fecc82bf1c244f9fbc"
IE_REDUCER = Path(
    ".github/governance/evidence/g77_256ie_future_formalization_v1/reducer/"
    "G77_256IE_FUTURE_REPOSITORY_CAPABILITY_REDUCER_V1.py"
)
IE_REDUCER_SHA256 = "5816e62bca2017672415fd98f5627d23d7481486c0f479a084298a4fa8a16142"
FM_CONTEXT_OWNER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
GUEST_PROJECTED_FM_CONTEXT_OWNER = Path(
    "/mnt/dp-harness/sapianta_fresh_operation_context_v1.py"
)
SELECTED_VECTOR = "P11-E05/NEGATIVE_AUTHORITY/FUTURE"
EVALUATION_TIME_UNIX_NS = 500
BASELINE_VALID_FROM_UNIX_NS = 100
FUTURE_VALID_FROM_UNIX_NS = 600
VALID_UNTIL_UNIX_NS = 1000
EXPECTED_FUTURE_PAYLOAD_DIGEST = (
    "sha256:9568e0c248ad488cabcf6bde6b490c544077862d10e3fda13bcdc8ed9953f547"
)
EXPECTED_DENIAL = "operational Human act is not current"
EXPECTED_DENIAL_TYPE = "FailClosedRuntimeError"


class FutureEntrypointError(RuntimeError):
    """One closed IZ binding or runtime-specialization rejection."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path, name: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise FutureEntrypointError(f"OWNER_IMPORT_FAILED__{name}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def authenticate_future_semantics(repository_root: Path) -> dict[str, Any]:
    """Authenticate IE's one-coordinate FUTURE packet and reduction."""

    root = repository_root.resolve()
    producer_path = root / IE_PRODUCER
    reducer_path = root / IE_REDUCER
    for path, expected, identity in (
        (producer_path, IE_PRODUCER_SHA256, "IE_PRODUCER"),
        (reducer_path, IE_REDUCER_SHA256, "IE_REDUCER"),
    ):
        if path.is_symlink() or not path.is_file() or _sha256(path) != expected:
            raise FutureEntrypointError(f"{identity}_BINDING_INVALID")
    producer = _load(producer_path, "g77_256iz_ie_producer")
    reducer = _load(reducer_path, "g77_256iz_ie_reducer")
    packet = producer.produce_future_vector(root)
    result = reducer.reduce_future_repository_vector(packet)
    expected = (
        packet["selected_vector"] == SELECTED_VECTOR,
        packet["independent_mutation_count"] == 1,
        packet["independent_mutated_coordinate"] == "valid_from_unix_ns",
        packet["differing_payload_fields"] == ["valid_from_unix_ns"],
        packet["evaluation_time_unix_ns"] == EVALUATION_TIME_UNIX_NS,
        packet["baseline_payload"]["valid_from_unix_ns"]
        == BASELINE_VALID_FROM_UNIX_NS,
        packet["future_payload"]["valid_from_unix_ns"]
        == FUTURE_VALID_FROM_UNIX_NS,
        packet["future_payload"]["valid_until_unix_ns"] == VALID_UNTIL_UNIX_NS,
        packet["future_payload_digest"] == EXPECTED_FUTURE_PAYLOAD_DIGEST,
        packet["fixture_uses_wall_clock"] is False,
        result["future_repository_formalization"] == "VERIFIED",
    )
    if not all(expected):
        raise FutureEntrypointError("IE_FUTURE_SEMANTIC_REDUCTION_DRIFT")
    return packet


def specialize_fc_runtime_source(
    *, repository_root: Path, identity_namespace_prefix: str
) -> str:
    """Derive the family-local FUTURE runtime from the exact FC/FK source."""

    root = repository_root.resolve()
    authenticate_future_semantics(root)
    source_path = root / FC_ADAPTER
    if source_path.is_symlink() or not source_path.is_file():
        raise FutureEntrypointError("FC_FK_ADAPTER_PATH_INVALID")
    if _sha256(source_path) != FC_ADAPTER_SHA256:
        raise FutureEntrypointError("FC_FK_ADAPTER_HASH_MISMATCH")
    if not identity_namespace_prefix.startswith("G77_256"):
        raise FutureEntrypointError("IDENTITY_NAMESPACE_PREFIX_INVALID")
    source = source_path.read_text(encoding="utf-8")
    transformed = source.replace("G77_256FC", identity_namespace_prefix)
    transformed = transformed.replace("WRONG_ATTEMPT", "FUTURE")
    transformed = transformed.replace("wrong_attempt", "future")
    time_anchor = (
        '        "minimum_retention": "CD_AUTHORIZED_MINIMUM_TRAIL_PLUS_FC_RAW_PREIMAGE",\n'
    )
    if transformed.count(time_anchor) != 1:
        raise FutureEntrypointError("FC_FUTURE_TIME_INSERTION_ANCHOR_INVALID")
    transformed = transformed.replace(
        time_anchor,
        '        "valid_from_unix_ns": FUTURE_VALID_FROM_UNIX_NS,\n'
        '        "valid_until_unix_ns": VALID_UNTIL_UNIX_NS,\n'
        + time_anchor,
    )
    submission_anchor = (
        "            input_record_canonical_bytes=authorized_bytes,\n"
        "        )\n"
    )
    if transformed.count(submission_anchor) != 1:
        raise FutureEntrypointError("FC_FUTURE_SUBMISSION_ANCHOR_INVALID")
    transformed = transformed.replace(
        submission_anchor,
        "            input_record_canonical_bytes=authorized_bytes,\n"
        "            now_unix_ns=EVALUATION_TIME_UNIX_NS,\n"
        "        )\n",
    )
    compile(transformed, str(source_path), "exec")
    return transformed


def future_terminal_reduction(
    *,
    phase: str,
    counters: Mapping[str, int],
    first_failure_or_current_result: str | None,
    first_failure: str | None,
    authority_checkpoint: Mapping[str, Any] | None,
    execution_seal: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Credit only the exact future-submission denial evidence shape."""

    checkpoint = authority_checkpoint or {}
    seal = execution_seal or {}
    verified = all((
        phase.startswith(("PHASE_C", "PHASE_D")),
        first_failure is None,
        isinstance(first_failure_or_current_result, str),
        first_failure_or_current_result.startswith("PASS__FUTURE_SUBMISSION_DENIED"),
        checkpoint.get("owner_state_initialization_count") == 0,
        checkpoint.get("denial_error_type") == EXPECTED_DENIAL_TYPE,
        checkpoint.get("denial_error") == EXPECTED_DENIAL,
        seal.get("operational_result")
        == "PASS__FUTURE_DENIED_AT_D2_SUBMISSION_BEFORE_OWNER_STATE_AND_ENTRY",
        seal.get("first_failure") is None,
        counters.get("human_operational_act_creation_count") == 1,
        counters.get("human_operational_act_submitted_count") == 0,
        counters.get("p11_entry_count") == 0,
        counters.get("p11_operational_invocation_count") == 0,
        counters.get("e05_case_execution_count") == 1,
    ))
    return {
        "execution_counters": dict(counters),
        "authority_lifecycle_state": (
            "NOT_CREATED__FUTURE_DENIED_AT_SUBMISSION__NO_AUTHORITY_SURVIVES"
            if verified else "UNPROVEN__NO_E05_CREDIT"
        ),
        "first_failure_or_current_result": (
            "PASS__FUTURE_SUBMISSION_DENIED_BEFORE_OWNER_STATE_AND_ENTRY"
            if verified else "FAIL_CLOSED__FUTURE_REQUIRED_EVIDENCE_MISSING"
        ),
        "success_evidence_complete": verified,
        "e05_credit": 1 if verified else 0,
    }


def _finalize_expected_future_denial(module: ModuleType, **state: Any) -> int:
    submitted = state["submitted"]
    if not (
        submitted.get("message_type") == "CUSTODY_FAILURE"
        and submitted.get("error_type") == EXPECTED_DENIAL_TYPE
        and submitted.get("error") == EXPECTED_DENIAL
    ):
        raise FutureEntrypointError("FUTURE_SUBMISSION_DENIAL_MISMATCH")
    waited, status = os.waitpid(state["custody_pid"], 0)
    if waited <= 0 or not os.WIFEXITED(status) or os.WEXITSTATUS(status) != 111:
        raise FutureEntrypointError("FUTURE_CUSTODY_TERMINAL_STATUS_INVALID")
    counters = state["counters"]
    counters.update({
        "human_operational_act_submitted_count": 0,
        "human_operational_act_claimed_count": 0,
        "human_operational_act_invoked_count": 0,
        "human_operational_act_terminally_bound_count": 0,
        "human_operational_act_permanently_exhausted_count": 0,
        "p11_entry_count": 0,
        "p11_operational_invocation_count": 0,
        "e01_e12_execution_count": 0,
        "e05_case_execution_count": 1,
    })
    checkpoint = {
        "schema_id": "SAPIANTA_FUTURE_SUBMISSION_DENIAL_CHECKPOINT_V1",
        "generation_identity": module.GENERATION_ID,
        "case_id": module.CASE_ID,
        "denial_error_type": EXPECTED_DENIAL_TYPE,
        "denial_error": EXPECTED_DENIAL,
        "evaluation_time_unix_ns": EVALUATION_TIME_UNIX_NS,
        "future_valid_from_unix_ns": FUTURE_VALID_FROM_UNIX_NS,
        "valid_until_unix_ns": VALID_UNTIL_UNIX_NS,
        "owner_state_initialization_count": 0,
        "p11_entry_count": 0,
        "protected_effect_count": 0,
        "checkpoint_is_authority": False,
        "execution_counters": counters,
    }
    checkpoint_sha = module.write_canonical(module.AUTHORITY_SEAL_PATH, checkpoint)
    module.append_record("future_submission_denial", "FACT", checkpoint)
    guest_seal = {
        "schema_id": "SAPIANTA_FUTURE_GUEST_EXECUTION_SEAL_V1",
        "generation_identity": module.GENERATION_ID,
        "source_head": state["expected_head"],
        "source_tree": state["expected_tree"],
        "case_id": module.CASE_ID,
        "completed_gates": ["P01-P12", "ACT_CREATE", "FUTURE_D2_SUBMISSION_DENIAL"],
        "pending_gates": ["TEARDOWN", "G48_FINALIZATION"],
        "authority_disposition": "NOT_CREATED__FUTURE_DENIED_AT_SUBMISSION",
        "operational_result": (
            "PASS__FUTURE_DENIED_AT_D2_SUBMISSION_BEFORE_OWNER_STATE_AND_ENTRY"
        ),
        "execution_counters": counters,
        "pre_act_checkpoint_sha256": state["preact_sha"],
        "authority_checkpoint_sha256": checkpoint_sha,
        "first_failure": None,
        "teardown_state": "PENDING",
        "checkpoint_is_authority": False,
    }
    seal_sha = module.write_canonical(module.GUEST_SEAL_PATH, guest_seal)
    module.update_continuation_manifest(
        current_spce_phase="PHASE_C_EXECUTION_COMPLETE_PENDING_GUEST_TEARDOWN",
        execution_counters=counters,
        authority_lifecycle_state=(
            "NOT_CREATED__FUTURE_DENIED_AT_SUBMISSION__NO_AUTHORITY_SURVIVES"
        ),
        first_failure_or_current_result=(
            "PASS__FUTURE_SUBMISSION_DENIED_BEFORE_OWNER_STATE_AND_ENTRY"
        ),
        teardown_state="PENDING",
        authorized_next_action="TEARDOWN_AND_FINALIZATION_ONLY__NO_REPLAY",
        additional_completed_seals=({
            "identity": guest_seal["schema_id"], "sha256": seal_sha,
        },),
    )
    return 0


def load_future_er(repository_root: Path) -> ModuleType:
    """Load the exact ER owner with the one FUTURE early-denial branch."""

    root = repository_root.resolve()
    path = root / ER_HARNESS
    if path.is_symlink() or not path.is_file() or _sha256(path) != ER_HARNESS_SHA256:
        raise FutureEntrypointError("ER_HARNESS_BINDING_INVALID")
    source = path.read_text(encoding="utf-8")
    clock = (
        "    now = time.time_ns()\n"
        "    valid_from = now - 1_000_000_000\n"
        "    valid_until = now + 300_000_000_000\n"
    )
    if source.count(clock) != 1:
        raise FutureEntrypointError("ER_TIME_SPECIALIZATION_ANCHOR_INVALID")
    source = source.replace(
        clock,
        "    now = 500\n    valid_from = 100\n    valid_until = 1000\n",
    )
    branch = (
        "        os.waitpid(issuance_pid, 0)\n"
        "        if submitted[\"message_type\"] != \"ACT_SUBMITTED\":\n"
    )
    if source.count(branch) != 1:
        raise FutureEntrypointError("ER_SUBMISSION_BRANCH_ANCHOR_INVALID")
    source = source.replace(
        branch,
        "        os.waitpid(issuance_pid, 0)\n"
        "        if submitted.get(\"message_type\") == \"CUSTODY_FAILURE\":\n"
        "            return _accept_future_submission_denial(\n"
        "                submitted=submitted, custody_pid=custody_pid,\n"
        "                counters=counters, act_message=act_message,\n"
        "                expected_head=expected_head, expected_tree=expected_tree,\n"
        "                preact_sha=preact_sha,\n"
        "            )\n"
        "        if submitted[\"message_type\"] != \"ACT_SUBMITTED\":\n",
    )
    module = ModuleType("g77_256iz_future_er_specialization")
    module.__file__ = str(path)
    module.__dict__["_accept_future_submission_denial"] = (
        lambda **state: _finalize_expected_future_denial(module, **state)
    )
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


def load_guest_runtime_namespace(
    repository_root: Path = GUEST_REPOSITORY_ROOT,
    context_path: Path = GUEST_CONTEXT_PATH,
) -> dict[str, Any]:
    """Authenticate the sealed FUTURE context and instantiate one specialization."""

    root = repository_root.resolve()
    owner_path = (
        GUEST_PROJECTED_FM_CONTEXT_OWNER
        if root == GUEST_REPOSITORY_ROOT
        else root / FM_CONTEXT_OWNER
    )
    context_owner = _load(owner_path, "g77_256iz_guest_context_owner")
    context = context_owner.load_context(context_path, repository_root=root)
    if context_owner.operation_vector(context["generation_identity"]) != "FUTURE":
        raise FutureEntrypointError("SEALED_CONTEXT_VECTOR_IS_NOT_FUTURE")
    source = specialize_fc_runtime_source(
        repository_root=root,
        identity_namespace_prefix=context["identity_namespace_prefix"],
    )
    namespace: dict[str, Any] = {
        "__name__": "sapianta_context_bound_future_specialization_v1",
        "__file__": str(root / FC_ADAPTER),
        "__package__": None,
        "EVALUATION_TIME_UNIX_NS": EVALUATION_TIME_UNIX_NS,
        "FUTURE_VALID_FROM_UNIX_NS": FUTURE_VALID_FROM_UNIX_NS,
        "VALID_UNTIL_UNIX_NS": VALID_UNTIL_UNIX_NS,
    }
    exec(compile(source, namespace["__file__"], "exec"), namespace)
    if namespace.get("GENERATION_ID") != context["generation_identity"]:
        raise FutureEntrypointError("FUTURE_GENERATION_SPECIALIZATION_FAILED")
    namespace["load_er"] = lambda: load_future_er(root)
    namespace["reduce_future_terminal_state"] = future_terminal_reduction
    return namespace


def main() -> int:
    """Run the exact existing route with the sealed FUTURE specialization."""

    namespace = load_guest_runtime_namespace()
    return int(namespace["main"]())


if __name__ == "__main__":
    raise SystemExit(main())
