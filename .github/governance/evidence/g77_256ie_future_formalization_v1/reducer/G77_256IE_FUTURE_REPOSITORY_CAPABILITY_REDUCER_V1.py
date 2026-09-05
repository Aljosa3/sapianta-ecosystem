#!/usr/bin/env python3
"""Independent fail-closed reducer for the IE repository FUTURE vector."""

from __future__ import annotations

import hashlib
import json
import sys
from typing import Any, Mapping


sys.dont_write_bytecode = True

CASE_ID = "G77_256IE_E05_FUTURE_REPOSITORY_VECTOR_001"
SELECTED_VECTOR = "P11-E05/NEGATIVE_AUTHORITY/FUTURE"
BASE_HEAD = "559deecb226b66d626e45e6f607b0aab6df81f1c"
BASE_TREE = "2b7617318f402f5148e9ea8dd033870946d17ef7"
SPECIFICATION_SHA256 = "368894ef96e89b032f55216b3ee8a97bd3028da8391ae0fe31398d6f52b4a438"
FIXTURE_SHA256 = "6a3aee899acef667fadbc10db1fa70a58e536269917d720e168218bc30dbf00b"
TARGET_COORDINATE = "valid_from_unix_ns"
DEPENDENT_COORDINATES = ["human_authority_act.payload_digest"]
EXPECTED_DENIAL_STAGE = (
    "D2_SUBMISSION_AUTHORITY_CURRENTNESS_VALIDATION_BEFORE_PROTECTED_OWNER_STATE_"
    "INITIALIZATION_PRECLAIM_CLAIM_ENTRY_INVOCATION_OR_EFFECT"
)
EXPECTED_ERROR_REASON = "operational Human act is not current"
REQUIRED_FIELDS = {
    "schema_id", "generation_identity", "case_id", "selected_vector",
    "base_head", "base_tree", "formal_specification_sha256",
    "time_fixture_sha256", "repository_owner_bindings",
    "evaluation_time_unix_ns", "baseline_payload", "future_payload",
    "baseline_payload_digest", "future_payload_digest",
    "independent_mutation_count", "independent_mutated_coordinate",
    "dependent_recomputation_count", "dependent_recomputed_coordinates",
    "differing_payload_fields", "preserved_coordinate_proof", "time_relation",
    "expected_denial_stage", "expected_error_reason",
    "fixture_is_human_authority", "fixture_is_operational_request",
    "fixture_uses_wall_clock",
}


class FutureRepositoryReductionError(ValueError):
    """One deterministic repository capability rejection."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise FutureRepositoryReductionError(code)


def _payload_digest(payload: Mapping[str, Any]) -> str:
    return "sha256:" + sha256_bytes(canonical_bytes({"payload": dict(payload)}))


def reduce_future_repository_vector(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Accept only the isolated deterministic FUTURE formalization."""

    _require(isinstance(packet, Mapping), "PACKET_NOT_OBJECT")
    _require(set(packet) == REQUIRED_FIELDS, "PACKET_FIELDS_INCOMPLETE_OR_UNKNOWN")
    _require(packet["schema_id"] == "G77_256IE_FUTURE_REPOSITORY_VECTOR_V1", "SCHEMA_INVALID")
    _require(packet["case_id"] == CASE_ID, "CASE_ID_INVALID")
    _require(packet["selected_vector"] == SELECTED_VECTOR, "VECTOR_INVALID")
    _require(packet["base_head"] == BASE_HEAD and packet["base_tree"] == BASE_TREE, "BASE_BINDING_INVALID")
    _require(packet["formal_specification_sha256"] == SPECIFICATION_SHA256, "SPECIFICATION_BINDING_INVALID")
    _require(packet["time_fixture_sha256"] == FIXTURE_SHA256, "FIXTURE_BINDING_INVALID")
    owners = packet["repository_owner_bindings"]
    _require(isinstance(owners, list) and len(owners) == 4, "OWNER_BINDINGS_INVALID")
    _require(
        all(isinstance(item, Mapping) and set(item) == {"path", "sha256"} for item in owners),
        "OWNER_BINDING_STRUCTURE_INVALID",
    )

    baseline = packet["baseline_payload"]
    future = packet["future_payload"]
    _require(isinstance(baseline, Mapping) and isinstance(future, Mapping), "PAYLOADS_INVALID")
    _require(set(baseline) == set(future), "PAYLOAD_FIELD_SET_MISMATCH")
    actual_differing = sorted(key for key in baseline if baseline[key] != future[key])
    _require(actual_differing == [TARGET_COORDINATE], "INDEPENDENT_MUTATION_NOT_ISOLATED")
    _require(packet["differing_payload_fields"] == [TARGET_COORDINATE], "DECLARED_MUTATION_INVALID")
    _require(packet["independent_mutation_count"] == 1, "INDEPENDENT_MUTATION_COUNT_INVALID")
    _require(packet["independent_mutated_coordinate"] == TARGET_COORDINATE, "MUTATED_COORDINATE_INVALID")
    _require(packet["dependent_recomputation_count"] == 1, "DEPENDENT_RECOMPUTATION_COUNT_INVALID")
    _require(packet["dependent_recomputed_coordinates"] == DEPENDENT_COORDINATES, "DEPENDENT_COORDINATES_INVALID")
    proof = packet["preserved_coordinate_proof"]
    _require(isinstance(proof, Mapping) and proof and set(proof.values()) == {True}, "PRESERVATION_PROOF_INVALID")
    _require(set(proof) == set(baseline) - {TARGET_COORDINATE}, "PRESERVED_COORDINATE_SET_INVALID")

    evaluation = packet["evaluation_time_unix_ns"]
    baseline_from = baseline[TARGET_COORDINATE]
    future_from = future[TARGET_COORDINATE]
    valid_until = future["valid_until_unix_ns"]
    _require(
        all(isinstance(value, int) and not isinstance(value, bool) for value in (
            baseline_from, evaluation, future_from, valid_until
        )),
        "TIME_VALUES_INVALID",
    )
    _require(baseline_from <= evaluation < valid_until, "BASELINE_CURRENTNESS_INVALID")
    _require(evaluation < future_from < valid_until, "FUTURE_RELATION_INVALID")
    _require(
        packet["time_relation"] == {"evaluation_time_lt_valid_from_lt_valid_until": True},
        "DECLARED_TIME_RELATION_INVALID",
    )
    _require(packet["baseline_payload_digest"] == _payload_digest(baseline), "BASELINE_DIGEST_INVALID")
    _require(packet["future_payload_digest"] == _payload_digest(future), "FUTURE_DIGEST_INVALID")
    _require(packet["baseline_payload_digest"] != packet["future_payload_digest"], "DIGEST_NOT_RECOMPUTED")
    _require(packet["expected_denial_stage"] == EXPECTED_DENIAL_STAGE, "DENIAL_STAGE_INVALID")
    _require(packet["expected_error_reason"] == EXPECTED_ERROR_REASON, "DENIAL_REASON_INVALID")
    _require(packet["fixture_is_human_authority"] is False, "AUTHORITY_CREATED")
    _require(packet["fixture_is_operational_request"] is False, "OPERATIONAL_REQUEST_CREATED")
    _require(packet["fixture_uses_wall_clock"] is False, "WALL_CLOCK_USED")

    packet_sha256 = sha256_bytes(canonical_bytes(dict(packet)))
    return {
        "schema_id": "G77_256IE_FUTURE_REPOSITORY_CAPABILITY_RESULT_V1",
        "case_id": CASE_ID,
        "selected_vector": SELECTED_VECTOR,
        "repository_vector_sha256": packet_sha256,
        "terminal_acceptance": "PASS__FUTURE_SEMANTICS_TIME_FIXTURE_AND_PRESERVATION_FORMALIZED",
        "future_repository_formalization": "VERIFIED",
        "future_route_binding": "NOT_PROVEN",
        "future_preoperational_readiness": "NOT_PROVEN",
        "future_operational_capability": "NOT_PROVEN",
        "request_count": 0,
        "operation_attempt_count": 0,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "e05_credit": 0,
        "e05_status": "10/18",
        "auto_continuable": False,
        "human_review_required": True,
    }


if __name__ == "__main__":
    raise SystemExit("repository-only reducer; no operational CLI entry point")
