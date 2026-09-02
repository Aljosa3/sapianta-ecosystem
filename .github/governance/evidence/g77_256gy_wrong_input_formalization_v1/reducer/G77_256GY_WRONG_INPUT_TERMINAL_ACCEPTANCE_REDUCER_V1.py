#!/usr/bin/env python3
"""Fail-closed terminal acceptance for one WRONG_INPUT evidence packet."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


CASE_ID = "G77_256GY_E05_WRONG_INPUT_DENIAL_BEFORE_ENTRY_001"
SELECTED_VECTOR = "P11-E05/NEGATIVE_AUTHORITY/WRONG_INPUT"
FORMAL_SPECIFICATION_IDENTITY = "G77_256GY_WRONG_INPUT_FORMAL_SPECIFICATION_V1"
FORMAL_SPECIFICATION_SHA256 = (
    "434bcecf4665fb97be0095996f17927c5408e4597f77280f3c28172ee97af037"
)
CANDIDATE_IDENTITY = "G77_256GY_WRONG_INPUT_CANONICAL_CANDIDATE_TEMPLATE_V1"
EVIDENCE_PROVENANCE = "G77_256GY_BOUND_WRONG_INPUT_RAW_EVIDENCE_V1"
EXPECTED_DIFFERING_FIELDS = ["input_identity", "record_identity"]
EXPECTED_DENIAL_BOUNDARY = (
    "D2_PRECLAIM_AUTHORITY_BINDING_VALIDATION_BEFORE_PRECLAIM_LEDGER_APPEND_"
    "CLAIM_ENTRY_INVOCATION_OR_EFFECT"
)
EXPECTED_ERROR_TYPE = "FailClosedRuntimeError"
EXPECTED_ERROR_REASON = "operational Human act input_record_identity binding is invalid"
REQUIRED_RAW_RECORD_TYPES = {
    "wrong_input_request",
    "wrong_input_denial_complete",
    "request_counter",
    "p11_entry_counter",
    "protected_invocation_counter",
    "protected_effect_counter",
}
REQUIRED_FIELDS = {
    "schema_id",
    "case_id",
    "selected_vector",
    "formal_specification_identity",
    "formal_specification_sha256",
    "candidate_identity",
    "evidence_provenance",
    "request_identity",
    "authorized_input_record",
    "supplied_input_record",
    "differing_input_fields",
    "semantic_mutation_field",
    "dependent_recomputation_fields",
    "preserved_dimension_proof",
    "denial_boundary",
    "denial_error_type",
    "denial_error_reason",
    "request_count",
    "p11_entry_count",
    "protected_invocation_count",
    "protected_effect_count",
    "claim_attempted",
    "owner_state_unchanged",
    "runtime_ledger_exists",
    "output_present",
    "raw_evidence_records",
}


class WrongInputReductionError(ValueError):
    """One deterministic terminal fail-closed rejection."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise WrongInputReductionError(code)


def _record_identity(value: Mapping[str, Any]) -> str:
    preimage = dict(value)
    preimage.pop("record_identity", None)
    return "sha256:" + hashlib.sha256(canonical_bytes(preimage).rstrip(b"\n")).hexdigest()


def reduce_wrong_input_terminal_evidence(evidence: Mapping[str, Any]) -> dict[str, Any]:
    """Accept complete evidence but award no repository-only E05 credit."""

    _require(isinstance(evidence, Mapping), "EVIDENCE_NOT_OBJECT")
    _require(set(evidence) == REQUIRED_FIELDS, "EVIDENCE_FIELDS_INCOMPLETE_OR_UNKNOWN")
    _require(evidence["schema_id"] == "G77_256GY_WRONG_INPUT_OPERATIONAL_EVIDENCE_V1", "EVIDENCE_SCHEMA_MISMATCH")
    _require(evidence["case_id"] == CASE_ID, "CASE_ID_MISMATCH")
    _require(evidence["selected_vector"] == SELECTED_VECTOR, "VECTOR_IDENTITY_MISMATCH")
    _require(
        evidence["formal_specification_identity"] == FORMAL_SPECIFICATION_IDENTITY,
        "FORMAL_SPECIFICATION_IDENTITY_MISMATCH",
    )
    _require(
        evidence["formal_specification_sha256"] == FORMAL_SPECIFICATION_SHA256,
        "FORMAL_SPECIFICATION_SHA256_MISMATCH",
    )
    _require(
        evidence["candidate_identity"] == CANDIDATE_IDENTITY,
        "CANDIDATE_IDENTITY_MISMATCH",
    )
    _require(
        evidence["evidence_provenance"] == EVIDENCE_PROVENANCE,
        "EVIDENCE_PROVENANCE_MISMATCH",
    )
    _require(isinstance(evidence["request_identity"], str) and evidence["request_identity"], "REQUEST_IDENTITY_INVALID")
    authorized = evidence["authorized_input_record"]
    supplied = evidence["supplied_input_record"]
    _require(isinstance(authorized, Mapping) and isinstance(supplied, Mapping), "INPUT_RECORDS_MISSING")
    _require(set(authorized) == set(supplied), "INPUT_RECORD_FIELD_SET_MISMATCH")
    _require(
        authorized.get("record_identity") == _record_identity(authorized),
        "AUTHORIZED_RECORD_IDENTITY_INVALID",
    )
    _require(
        supplied.get("record_identity") == _record_identity(supplied),
        "SUPPLIED_RECORD_IDENTITY_INVALID",
    )
    _require(
        authorized.get("input_identity") != supplied.get("input_identity"),
        "INPUT_IDENTITY_NOT_MUTATED",
    )
    actual_differing = sorted(
        key for key in authorized if authorized.get(key) != supplied.get(key)
    )
    _require(sorted(evidence["differing_input_fields"]) == EXPECTED_DIFFERING_FIELDS, "DECLARED_MUTATION_IDENTITY_INVALID")
    _require(actual_differing == EXPECTED_DIFFERING_FIELDS, "ACTUAL_MUTATION_IDENTITY_INVALID")
    _require(evidence["semantic_mutation_field"] == "input_identity", "SEMANTIC_MUTATION_FIELD_INVALID")
    _require(evidence["dependent_recomputation_fields"] == ["record_identity"], "DEPENDENT_RECOMPUTATION_INVALID")
    proof = evidence["preserved_dimension_proof"]
    _require(isinstance(proof, Mapping) and proof and set(proof.values()) == {True}, "PRESERVED_DIMENSION_PROOF_INCOMPLETE")
    expected_preserved = set(authorized) - set(EXPECTED_DIFFERING_FIELDS)
    _require(set(proof) == expected_preserved, "PRESERVED_DIMENSION_SET_INVALID")
    _require(evidence["denial_boundary"] == EXPECTED_DENIAL_BOUNDARY, "P11_DENIAL_BOUNDARY_INVALID")
    _require(evidence["denial_error_type"] == EXPECTED_ERROR_TYPE, "DENIAL_ERROR_TYPE_INVALID")
    _require(evidence["denial_error_reason"] == EXPECTED_ERROR_REASON, "DENIAL_ERROR_REASON_INVALID")
    _require(evidence["request_count"] == 1, "REQUEST_COUNT_INVALID")
    _require(evidence["p11_entry_count"] == 0, "UNEXPECTED_P11_ENTRY")
    _require(evidence["protected_invocation_count"] == 0, "UNEXPECTED_PROTECTED_INVOCATION")
    _require(evidence["protected_effect_count"] == 0, "UNEXPECTED_PROTECTED_EFFECT")
    _require(evidence["claim_attempted"] is False, "UNEXPECTED_CLAIM")
    _require(evidence["owner_state_unchanged"] is True, "OWNER_STATE_CHANGED")
    _require(evidence["runtime_ledger_exists"] is False, "UNEXPECTED_RUNTIME_LEDGER")
    _require(evidence["output_present"] is False, "UNEXPECTED_OUTPUT")
    raw_records = evidence["raw_evidence_records"]
    _require(isinstance(raw_records, list) and raw_records, "RAW_EVIDENCE_MISSING")
    _require(
        all(
            isinstance(item, Mapping)
            and isinstance(item.get("record_type"), str)
            and isinstance(item.get("facts"), Mapping)
            for item in raw_records
        ),
        "RAW_EVIDENCE_STRUCTURE_INVALID",
    )
    raw_types = {
        item["record_type"] for item in raw_records
    }
    _require(REQUIRED_RAW_RECORD_TYPES.issubset(raw_types), "RAW_EVIDENCE_INCOMPLETE")
    identity_records = [
        item
        for item in raw_records
        if item["record_type"] in {"wrong_input_request", "wrong_input_denial_complete"}
    ]
    _require(
        identity_records
        and all(
            item["facts"].get("request_identity") == evidence["request_identity"]
            and item["facts"].get("case_id") == CASE_ID
            and item["facts"].get("selected_vector") == SELECTED_VECTOR
            and item["facts"].get("evidence_provenance") == EVIDENCE_PROVENANCE
            for item in identity_records
        ),
        "RAW_EVIDENCE_PROVENANCE_INVALID",
    )
    packet_sha256 = sha256_bytes(canonical_bytes(dict(evidence)))
    return {
        "schema_id": "G77_256GY_WRONG_INPUT_TERMINAL_ACCEPTANCE_RESULT_V1",
        "case_id": CASE_ID,
        "selected_vector": SELECTED_VECTOR,
        "evidence_packet_sha256": packet_sha256,
        "terminal_acceptance": "PASS__COMPLETE_WRONG_INPUT_D2_DENIAL_EVIDENCE",
        "request_count": 1,
        "p11_entry_count": 0,
        "protected_invocation_count": 0,
        "protected_effect_count": 0,
        "repository_only_generation": True,
        "e05_credit": 0,
        "credit_disposition": "WITHHELD__GY_HAS_NO_OPERATIONAL_AUTHORITY_AND_NO_OPERATIONAL_EVIDENCE",
        "auto_continuable": False,
        "human_review_required": True,
    }


if __name__ == "__main__":
    raise SystemExit("repository-only reducer; no CLI operational entry point")
