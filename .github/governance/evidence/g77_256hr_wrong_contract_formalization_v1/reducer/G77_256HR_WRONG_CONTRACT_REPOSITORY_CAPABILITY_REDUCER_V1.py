#!/usr/bin/env python3
"""Independent fail-closed reducer for one repository-only WRONG_CONTRACT vector."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping


GENERATION_ID = "G77_256HR_REPOSITORY_ONLY_WRONG_CONTRACT_FORMALIZATION_V1"
CASE_ID = "G77_256HR_E05_WRONG_CONTRACT_REPOSITORY_VECTOR_001"
SELECTED_VECTOR = "P11-E05/NEGATIVE_AUTHORITY/WRONG_CONTRACT"
FORMAL_SPECIFICATION_SHA256 = "f376752ee8c77879a96a5e05a25e6dee3a064477da051c2fa67d456627396228"
EXPECTED_DIFFERING_FIELDS = ["contract_identity", "record_identity"]
EXPECTED_DENIAL_BOUNDARY = (
    "D2_PRECLAIM_AUTHORITY_BINDING_VALIDATION_BEFORE_PRECLAIM_LEDGER_APPEND_"
    "CLAIM_ENTRY_INVOCATION_OR_EFFECT"
)
EXPECTED_ERROR_TYPE = "FailClosedRuntimeError"
EXPECTED_ERROR_REASON = "operational Human act input_record_identity binding is invalid"
SOURCE_RAW_PATH = Path(
    ".github/governance/evidence/g77_256hp_wrong_input_operational_v1/"
    "operation_state/runtime_export/G77_256HP_RAW_EXECUTION_EVIDENCE_V1.jsonl"
)
SOURCE_RAW_SHA256 = "116f694f80e95d88104df7d8b01ed0458212ae0b5d0222cd86419443c8d0f189"
SOURCE_RAW_GIT_BLOB = "289cc783b6a7fa4c4407e8ec1842ac8b2346ac37"
SOURCE_RECORD_SEQUENCE = 16
SOURCE_RECORD_TYPE = "human_operational_act_created"

INPUT_FIELDS = {
    "schema_id",
    "schema_version",
    "record_kind",
    "record_identity",
    "attempt_identity",
    "input_identity",
    "provenance_identity",
    "contract_identity",
    "contract_version",
    "contract_content_sha256",
    "authorization_reference",
    "caller_identity_reference",
    "preflight_binding_identity",
    "preflight_status",
    "p10_inventory_identity",
    "comparator_outcome_identity",
    "comparator_outcome",
    "replay_context_identity",
}
HASH_PATTERN = re.compile(r"sha256:[0-9a-f]{64}\Z")
REQUIRED_FIELDS = {
    "schema_id",
    "generation_identity",
    "case_id",
    "selected_vector",
    "formal_specification_sha256",
    "source_provenance",
    "authorized_contract_binding",
    "source_input_record",
    "candidate_input_record",
    "source_input_canonical_utf8",
    "candidate_input_canonical_utf8",
    "target_mutated_coordinate",
    "dependent_recomputation_fields",
    "semantic_mutation_count",
    "differing_input_fields",
    "preserved_dimension_proof",
    "expected_denial_boundary",
    "expected_error_type",
    "expected_error_reason",
    "contract_specific_comparison_reached",
    "repository_vector_only",
    "authority_created",
    "request_created",
    "operation_attempted",
    "e05_credit",
}


class WrongContractReductionError(ValueError):
    """One deterministic semantic-firewall rejection."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _canonical_record_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise WrongContractReductionError(code)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise WrongContractReductionError(f"DUPLICATE_JSON_KEY__{key}")
        value[key] = item
    return value


def _record_identity(value: Mapping[str, Any]) -> str:
    preimage = dict(value)
    preimage.pop("record_identity", None)
    return "sha256:" + _sha256(_canonical_record_bytes(preimage))


def _validate_input_record(value: Any, *, prefix: str) -> Mapping[str, Any]:
    _require(isinstance(value, Mapping), f"{prefix}_INPUT_NOT_OBJECT")
    _require(set(value) == INPUT_FIELDS, f"{prefix}_INPUT_FIELD_SET_INVALID")
    _require(value["schema_id"] == "SAPIANTA_P11_BOUNDED_CONSUMER_INPUT_V1", f"{prefix}_SCHEMA_ID_INVALID")
    _require(value["schema_version"] == "1.0.0", f"{prefix}_SCHEMA_VERSION_INVALID")
    _require(value["record_kind"] == "P11_BOUNDED_CONSUMER_INPUT", f"{prefix}_RECORD_KIND_INVALID")
    for field in INPUT_FIELDS - {"record_identity", "contract_content_sha256"}:
        _require(isinstance(value[field], str) and bool(value[field].strip()), f"{prefix}_{field.upper()}_MALFORMED")
    _require(isinstance(value["record_identity"], str) and HASH_PATTERN.fullmatch(value["record_identity"]) is not None, f"{prefix}_RECORD_IDENTITY_MALFORMED")
    _require(isinstance(value["contract_content_sha256"], str) and HASH_PATTERN.fullmatch(value["contract_content_sha256"]) is not None, f"{prefix}_CONTRACT_CONTENT_SHA256_MALFORMED")
    _require(value["preflight_status"] == "PASSED", f"{prefix}_PREFLIGHT_STATUS_INVALID")
    _require(value["comparator_outcome"] in {"EQUAL", "MISMATCH", "FAILED_CLOSED"}, f"{prefix}_COMPARATOR_OUTCOME_INVALID")
    _require(value["record_identity"] == _record_identity(value), f"{prefix}_RECORD_IDENTITY_STALE")
    return value


def _authenticate_source(root: Path) -> tuple[Mapping[str, Any], Mapping[str, Any], str]:
    raw = (root / SOURCE_RAW_PATH).read_bytes()
    _require(_sha256(raw) == SOURCE_RAW_SHA256, "SOURCE_PROVENANCE_HASH_MISMATCH")
    records = [
        json.loads(line, object_pairs_hook=_unique_object)
        for line in raw.decode("utf-8").splitlines()
        if line
    ]
    matches = [
        record
        for record in records
        if record.get("record_sequence") == SOURCE_RECORD_SEQUENCE
        and record.get("record_type") == SOURCE_RECORD_TYPE
    ]
    _require(len(matches) == 1, "SOURCE_PROVENANCE_RECORD_AMBIGUOUS_OR_ABSENT")
    facts = matches[0].get("facts")
    _require(isinstance(facts, Mapping), "SOURCE_FACTS_INVALID")
    source_record = _validate_input_record(facts.get("input_record"), prefix="SOURCE")
    source_text = facts.get("input_canonical_utf8")
    _require(isinstance(source_text, str), "SOURCE_CANONICAL_UTF8_MISSING")
    _require(source_text.encode("utf-8") == _canonical_record_bytes(source_record), "SOURCE_CANONICAL_UTF8_INVALID")
    act = facts.get("human_authority_act")
    _require(isinstance(act, Mapping) and isinstance(act.get("payload"), Mapping), "SOURCE_ACT_PAYLOAD_INVALID")
    payload = act["payload"]
    binding = {
        field: payload.get(field)
        for field in ("contract_identity", "contract_version", "contract_content_sha256")
    }
    _require(all(binding[field] == source_record[field] for field in binding), "SOURCE_CONTRACT_TRIPLE_NOT_AUTHORIZED")
    return source_record, binding, str(act.get("authority_act_identity"))


def reduce_wrong_contract_candidate(
    candidate_canonical_bytes: bytes, *, repository_root: Path
) -> dict[str, Any]:
    """Accept exact repository capability while withholding operational credit."""

    _require(isinstance(candidate_canonical_bytes, bytes) and bool(candidate_canonical_bytes), "CANDIDATE_BYTES_MISSING")
    try:
        candidate = json.loads(candidate_canonical_bytes, object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WrongContractReductionError("CANDIDATE_NOT_CANONICAL_JSON") from exc
    _require(isinstance(candidate, Mapping), "CANDIDATE_NOT_OBJECT")
    _require(candidate_canonical_bytes == canonical_bytes(candidate), "CANDIDATE_NOT_CANONICAL_JSON")
    _require(set(candidate) == REQUIRED_FIELDS, "CANDIDATE_FIELDS_INCOMPLETE_OR_UNKNOWN")
    _require(candidate["schema_id"] == "G77_256HR_WRONG_CONTRACT_REPOSITORY_VECTOR_V1", "CANDIDATE_SCHEMA_MISMATCH")
    _require(candidate["generation_identity"] == GENERATION_ID, "GENERATION_IDENTITY_MISMATCH")
    _require(candidate["case_id"] == CASE_ID, "CASE_ID_MISMATCH")
    _require(candidate["selected_vector"] == SELECTED_VECTOR, "MUTATION_CLASS_NOT_WRONG_CONTRACT")
    _require(candidate["formal_specification_sha256"] == FORMAL_SPECIFICATION_SHA256, "FORMAL_SPECIFICATION_SHA256_MISMATCH")

    root = repository_root.resolve()
    authenticated_source, authorized_binding, source_act_identity = _authenticate_source(root)
    provenance = candidate["source_provenance"]
    expected_provenance = {
        "authority_status": "HISTORICAL_EVIDENCE_ONLY__NOT_CURRENT_AUTHORITY",
        "path": SOURCE_RAW_PATH.as_posix(),
        "sha256": SOURCE_RAW_SHA256,
        "git_blob": SOURCE_RAW_GIT_BLOB,
        "record_sequence": SOURCE_RECORD_SEQUENCE,
        "record_type": SOURCE_RECORD_TYPE,
        "source_act_identity": source_act_identity,
    }
    _require(provenance == expected_provenance, "SOURCE_PROVENANCE_BINDING_INVALID")
    _require(candidate["authorized_contract_binding"] == authorized_binding, "AUTHORIZED_CONTRACT_BINDING_INVALID")

    source = _validate_input_record(candidate["source_input_record"], prefix="SOURCE")
    supplied = _validate_input_record(candidate["candidate_input_record"], prefix="CANDIDATE")
    _require(source == authenticated_source, "SOURCE_INPUT_NOT_AUTHENTICATED")
    _require(candidate["source_input_canonical_utf8"].encode("utf-8") == _canonical_record_bytes(source), "SOURCE_CANONICAL_BYTES_INVALID")
    _require(candidate["candidate_input_canonical_utf8"].encode("utf-8") == _canonical_record_bytes(supplied), "CANDIDATE_CANONICAL_BYTES_INVALID")
    _require(source["contract_identity"] != supplied["contract_identity"], "CONTRACT_IDENTITY_NOT_MUTATED")

    actual_differing = sorted(key for key in source if source[key] != supplied[key])
    _require(candidate["differing_input_fields"] == EXPECTED_DIFFERING_FIELDS, "DECLARED_MUTATION_SET_INVALID")
    _require(actual_differing == EXPECTED_DIFFERING_FIELDS, "MULTIPLE_OR_UNRELATED_SEMANTIC_MUTATION")
    _require(candidate["target_mutated_coordinate"] == "contract_identity", "MUTATION_CLASS_NOT_WRONG_CONTRACT")
    _require(candidate["dependent_recomputation_fields"] == ["record_identity"], "DEPENDENT_RECOMPUTATION_INVALID")
    _require(candidate["semantic_mutation_count"] == 1, "SEMANTIC_MUTATION_COUNT_INVALID")
    proof = candidate["preserved_dimension_proof"]
    expected_preserved = INPUT_FIELDS - set(EXPECTED_DIFFERING_FIELDS)
    _require(isinstance(proof, Mapping) and set(proof) == expected_preserved, "PRESERVED_DIMENSION_SET_INVALID")
    _require(set(proof.values()) == {True}, "PRESERVED_DIMENSION_PROOF_INVALID")
    _require(all(source[field] == supplied[field] for field in expected_preserved), "UNRELATED_IDENTITY_RECOMPUTED")

    _require(candidate["expected_denial_boundary"] == EXPECTED_DENIAL_BOUNDARY, "EXPECTED_DENIAL_BOUNDARY_INVALID")
    _require(candidate["expected_error_type"] == EXPECTED_ERROR_TYPE, "EXPECTED_ERROR_TYPE_INVALID")
    _require(candidate["expected_error_reason"] == EXPECTED_ERROR_REASON, "EXPECTED_ERROR_REASON_INVALID")
    _require(candidate["contract_specific_comparison_reached"] is False, "CONTRACT_COMPARISON_ORDER_OVERCLAIM")
    _require(candidate["repository_vector_only"] is True, "REPOSITORY_ONLY_BOUNDARY_INVALID")
    _require(candidate["authority_created"] is False, "UNEXPECTED_AUTHORITY")
    _require(candidate["request_created"] is False, "UNEXPECTED_REQUEST")
    _require(candidate["operation_attempted"] is False, "UNEXPECTED_OPERATION")
    _require(candidate["e05_credit"] == 0, "UNEXPECTED_E05_CREDIT")

    return {
        "schema_id": "G77_256HR_WRONG_CONTRACT_REPOSITORY_CAPABILITY_RESULT_V1",
        "case_id": CASE_ID,
        "selected_vector": SELECTED_VECTOR,
        "candidate_sha256": _sha256(candidate_canonical_bytes),
        "formal_spec_status": "VERIFIED",
        "producer_status": "VERIFIED",
        "reducer_status": "VERIFIED",
        "semantic_firewall_status": "VERIFIED",
        "repository_capability": "VERIFIED",
        "binding_status": "NOT_PROVEN",
        "preoperational_readiness": "NOT_PROVEN",
        "operational_capability": "NOT_PROVEN",
        "e05_credit": 0,
        "e05_before": "8/18",
        "e05_after": "8/18",
        "auto_continuable": False,
        "human_review_required": True,
    }


if __name__ == "__main__":
    raise SystemExit("repository-only reducer; no operational entry point")
