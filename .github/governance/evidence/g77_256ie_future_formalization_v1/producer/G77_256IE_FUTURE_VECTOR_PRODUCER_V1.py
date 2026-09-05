#!/usr/bin/env python3
"""Deterministic repository-only producer for one E05 FUTURE vector.

This module transforms a nonauthority canonical payload fixture. It creates no
Human act, request, owner state, P11 entry, launcher invocation, or operation.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping

from aigol.runtime.canonical_human_authority_act_contract_v1 import (
    canonical_human_authority_payload_digest_v1,
)


sys.dont_write_bytecode = True

GENERATION_ID = "G77_256IE_REPOSITORY_ONLY_FUTURE_FORMALIZATION_V1"
CASE_ID = "G77_256IE_E05_FUTURE_REPOSITORY_VECTOR_001"
SELECTED_VECTOR = "P11-E05/NEGATIVE_AUTHORITY/FUTURE"
BASE_HEAD = "559deecb226b66d626e45e6f607b0aab6df81f1c"
BASE_TREE = "2b7617318f402f5148e9ea8dd033870946d17ef7"
SPECIFICATION_SHA256 = "368894ef96e89b032f55216b3ee8a97bd3028da8391ae0fe31398d6f52b4a438"
FIXTURE_SHA256 = "6a3aee899acef667fadbc10db1fa70a58e536269917d720e168218bc30dbf00b"
TARGET_COORDINATE = "valid_from_unix_ns"
DEPENDENT_COORDINATES = ("human_authority_act.payload_digest",)
EXPECTED_ERROR_REASON = "operational Human act is not current"
EXPECTED_DENIAL_STAGE = (
    "D2_SUBMISSION_AUTHORITY_CURRENTNESS_VALIDATION_BEFORE_PROTECTED_OWNER_STATE_"
    "INITIALIZATION_PRECLAIM_CLAIM_ENTRY_INVOCATION_OR_EFFECT"
)

ROOT_RELATIVE = Path(".github/governance/evidence/g77_256ie_future_formalization_v1")
SPECIFICATION_PATH = ROOT_RELATIVE / "G77_256IE_FUTURE_FORMAL_SPECIFICATION_V1.json"
FIXTURE_PATH = ROOT_RELATIVE / "G77_256IE_FUTURE_TIME_FIXTURE_V1.json"
OWNER_BINDINGS = {
    Path("tests/p11_da_operational_consumer_v1.py"):
        "220e41ee3ea8fa6b21ecebe62aa4436b816d9b7678d251e18979fa87b160fc4e",
    Path("tests/p11_da_disposable_substrate_v1.py"):
        "a1b58fa8ddedb5058393aa23d815262c92c8b185c0b193764f77420313af0bab",
    Path("aigol/runtime/canonical_human_authority_act_contract_v1.py"):
        "905ce577c31c2c538033455d1633470a34e9f7a94edd6190d50932e97ba8ebc8",
    Path("aigol/runtime/canonical_che_evidence_correlation_contract_v1.py"):
        "75801995214e81419aab9a02326499c771ec0039658fb49598aa54bd033e13c5",
}


class FutureVectorProducerError(ValueError):
    """One fail-closed repository formalization rejection."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def canonical_document_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise FutureVectorProducerError(f"DUPLICATE_JSON_KEY__{key}")
        result[key] = value
    return result


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise FutureVectorProducerError(code)


def _load_canonical_envelope(
    path: Path, *, schema_id: str, inner_key: str, seal_key: str, seal: str
) -> dict[str, Any]:
    raw = path.read_bytes()
    envelope = json.loads(raw, object_pairs_hook=_unique_object)
    _require(raw == canonical_document_bytes(envelope), f"{inner_key.upper()}_NOT_CANONICAL")
    _require(envelope.get("schema_id") == schema_id, f"{inner_key.upper()}_SCHEMA_INVALID")
    _require(set(envelope) == {"schema_id", inner_key, seal_key}, f"{inner_key.upper()}_ENVELOPE_INVALID")
    observed = sha256_bytes(canonical_bytes(envelope[inner_key]))
    _require(observed == envelope[seal_key] == seal, f"{inner_key.upper()}_SEAL_INVALID")
    return envelope


def authenticate_repository_owners(repository_root: Path) -> list[dict[str, str]]:
    bindings: list[dict[str, str]] = []
    for path, expected in OWNER_BINDINGS.items():
        observed = sha256_bytes((repository_root / path).read_bytes())
        _require(observed == expected, f"OWNER_HASH_MISMATCH__{path.name}")
        bindings.append({"path": path.as_posix(), "sha256": observed})
    return bindings


def produce_future_vector(repository_root: Path) -> dict[str, Any]:
    """Produce one canonical, nonauthority FUTURE payload comparison."""

    root = repository_root.resolve()
    specification = _load_canonical_envelope(
        root / SPECIFICATION_PATH,
        schema_id="G77_256IE_FUTURE_FORMAL_SPECIFICATION_ENVELOPE_V1",
        inner_key="specification",
        seal_key="specification_sha256",
        seal=SPECIFICATION_SHA256,
    )["specification"]
    fixture = _load_canonical_envelope(
        root / FIXTURE_PATH,
        schema_id="G77_256IE_FUTURE_TIME_FIXTURE_ENVELOPE_V1",
        inner_key="fixture",
        seal_key="fixture_sha256",
        seal=FIXTURE_SHA256,
    )["fixture"]
    owners = authenticate_repository_owners(root)

    baseline = deepcopy(fixture["baseline_payload"])
    evaluation = fixture["evaluation_time_unix_ns"]
    future_valid_from = fixture["future_valid_from_unix_ns"]
    valid_until = fixture["valid_until_unix_ns"]
    preserved_set = set(specification["preserved_coordinate_set"])
    _require(set(baseline) == preserved_set | {TARGET_COORDINATE}, "BASELINE_FIELD_SET_INVALID")
    _require(baseline["valid_until_unix_ns"] == valid_until, "FIXTURE_VALID_UNTIL_MISMATCH")
    _require(
        baseline[TARGET_COORDINATE] <= evaluation < valid_until,
        "BASELINE_NOT_CURRENT_AT_EVALUATION_TIME",
    )
    _require(evaluation < future_valid_from < valid_until, "FUTURE_TIME_RELATION_INVALID")

    future = deepcopy(baseline)
    future[TARGET_COORDINATE] = future_valid_from
    differing = sorted(key for key in baseline if baseline[key] != future[key])
    _require(differing == [TARGET_COORDINATE], "FUTURE_MUTATION_NOT_ISOLATED")
    preserved = {
        key: baseline[key] == future[key]
        for key in sorted(preserved_set)
    }
    _require(preserved and set(preserved.values()) == {True}, "PRESERVED_COORDINATE_CHANGED")

    baseline_digest = canonical_human_authority_payload_digest_v1(baseline)
    future_digest = canonical_human_authority_payload_digest_v1(future)
    _require(baseline_digest != future_digest, "PAYLOAD_DIGEST_NOT_RECOMPUTED")
    return {
        "schema_id": "G77_256IE_FUTURE_REPOSITORY_VECTOR_V1",
        "generation_identity": GENERATION_ID,
        "case_id": CASE_ID,
        "selected_vector": SELECTED_VECTOR,
        "base_head": BASE_HEAD,
        "base_tree": BASE_TREE,
        "formal_specification_sha256": SPECIFICATION_SHA256,
        "time_fixture_sha256": FIXTURE_SHA256,
        "repository_owner_bindings": owners,
        "evaluation_time_unix_ns": evaluation,
        "baseline_payload": baseline,
        "future_payload": future,
        "baseline_payload_digest": baseline_digest,
        "future_payload_digest": future_digest,
        "independent_mutation_count": 1,
        "independent_mutated_coordinate": TARGET_COORDINATE,
        "dependent_recomputation_count": 1,
        "dependent_recomputed_coordinates": list(DEPENDENT_COORDINATES),
        "differing_payload_fields": differing,
        "preserved_coordinate_proof": preserved,
        "time_relation": {"evaluation_time_lt_valid_from_lt_valid_until": True},
        "expected_denial_stage": EXPECTED_DENIAL_STAGE,
        "expected_error_reason": EXPECTED_ERROR_REASON,
        "fixture_is_human_authority": False,
        "fixture_is_operational_request": False,
        "fixture_uses_wall_clock": False,
    }


if __name__ == "__main__":
    raise SystemExit("repository-only producer; no operational CLI entry point")
