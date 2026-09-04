#!/usr/bin/env python3
"""Independent fail-closed reducer for the repository-only WRONG_PROVENANCE vector."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence

from aigol.runtime.canonical_che_evidence_correlation_contract_v1 import (
    CanonicalCHEEvidenceCorrelationV1,
)
from aigol.runtime.canonical_human_authority_act_contract_v1 import (
    CanonicalHumanAuthorityActV1,
)
from aigol.runtime.transport.serialization import replay_hash


GENERATION_ID = "G77_256HZ_REPOSITORY_ONLY_WRONG_PROVENANCE_FORMALIZATION_V1"
BASE_HEAD = "451fafdeafc935c352a27f75fbddb473423ce7b3"
BASE_TREE = "98a5f94880cae12e91ab3173fad36de8c90d0d23"
CASE_ID = "G77_256HZ_E05_WRONG_PROVENANCE_REPOSITORY_VECTOR_001"
SELECTED_VECTOR = "P11-E05/NEGATIVE_AUTHORITY/WRONG_PROVENANCE"
FORMAL_SPECIFICATION_SHA256 = "f3dd54dafd6e3c390c456d3fdc1408c2f57c887352f26e7d122d59b292136bd0"
EXPECTED_DIFFERING_FIELDS = ["provenance_identity", "record_identity"]
EXPECTED_DENIAL_BOUNDARY = (
    "D2_PRECLAIM_AUTHORITY_BINDING_VALIDATION_BEFORE_PRECLAIM_LEDGER_APPEND_"
    "CLAIM_ENTRY_INVOCATION_OR_EFFECT"
)
EXPECTED_ERROR_TYPE = "FailClosedRuntimeError"
EXPECTED_ERROR_REASON = "operational Human act input_record_identity binding is invalid"
SOURCE_RAW_PATH = Path(
    ".github/governance/evidence/g77_256hx_wrong_contract_operational_v1/"
    "operation_state/runtime_export/G77_256HX_RAW_EXECUTION_EVIDENCE_V1.jsonl"
)
SOURCE_RAW_SHA256 = "ef68294aac53051396c5eac20c786bf914f42de9a4e628f07580591a797187f5"
SOURCE_RAW_GIT_BLOB = "4947ad5f128d8734cddb10b70cd7a3bfd72bd373"
SOURCE_ACT_SEQUENCE = 16
SOURCE_OWNER_SEQUENCE = 17
SOURCE_CHECKPOINT_SEQUENCE = 18
AUTHORITATIVE_OWNER = "AUTHORITY_CUSTODY_PROCESS_PRINCIPAL"
SOURCE_GENERATION = (
    "G77_256HX_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_CONTRACT_OPERATIONAL_COMMISSIONING_V1"
)

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
REQUIRED_FIELDS = {
    "authority_created",
    "authoritative_provenance_resolution",
    "base_head",
    "base_tree",
    "baseline_input_canonical_utf8",
    "baseline_input_record",
    "case_id",
    "dependent_recomputation_count",
    "dependent_recomputed_coordinate",
    "differing_input_fields",
    "e05_credit",
    "expected_denial_boundary",
    "expected_error_reason",
    "expected_error_type",
    "formal_specification_sha256",
    "generation_identity",
    "independent_mutated_coordinate",
    "independent_mutation_count",
    "operation_attempted",
    "preserved_independent_coordinate_proof",
    "provenance_specific_comparison_reached",
    "repository_vector_only",
    "request_created",
    "schema_id",
    "selected_vector",
    "source_evidence",
    "supplied_input_canonical_utf8",
    "supplied_input_record",
}
RESOLUTION_OBSERVATION_FIELDS = {
    "authority_act_identity",
    "authoritative_owner_identity",
    "owner_state_identity",
    "provenance_identity",
    "record_sequence",
    "source_role",
}
HASH_PATTERN = re.compile(r"sha256:[0-9a-f]{64}\Z")


class WrongProvenanceReductionError(ValueError):
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


def _git_blob_identity(value: bytes) -> str:
    return hashlib.sha1(f"blob {len(value)}\0".encode("ascii") + value).hexdigest()


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise WrongProvenanceReductionError(code)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise WrongProvenanceReductionError(f"DUPLICATE_JSON_KEY__{key}")
        value[key] = item
    return value


def _record_identity(value: Mapping[str, Any]) -> str:
    preimage = dict(value)
    preimage.pop("record_identity", None)
    return "sha256:" + _sha256(_canonical_record_bytes(preimage))


def _validate_input_record(value: Any, *, prefix: str) -> Mapping[str, Any]:
    _require(isinstance(value, Mapping), f"{prefix}_INPUT_NOT_OBJECT")
    _require(set(value) == INPUT_FIELDS, f"{prefix}_INPUT_FIELD_SET_INVALID")
    _require(
        value["schema_id"] == "SAPIANTA_P11_BOUNDED_CONSUMER_INPUT_V1",
        f"{prefix}_SCHEMA_ID_INVALID",
    )
    _require(value["schema_version"] == "1.0.0", f"{prefix}_SCHEMA_VERSION_INVALID")
    _require(
        value["record_kind"] == "P11_BOUNDED_CONSUMER_INPUT",
        f"{prefix}_RECORD_KIND_INVALID",
    )
    for field in INPUT_FIELDS - {"record_identity", "contract_content_sha256"}:
        _require(
            isinstance(value[field], str)
            and bool(value[field].strip())
            and value[field] == value[field].strip(),
            f"{prefix}_{field.upper()}_MALFORMED",
        )
    _require(
        isinstance(value["record_identity"], str)
        and HASH_PATTERN.fullmatch(value["record_identity"]) is not None,
        f"{prefix}_RECORD_IDENTITY_MALFORMED",
    )
    _require(
        isinstance(value["contract_content_sha256"], str)
        and HASH_PATTERN.fullmatch(value["contract_content_sha256"]) is not None,
        f"{prefix}_CONTRACT_CONTENT_SHA256_MALFORMED",
    )
    _require(value["preflight_status"] == "PASSED", f"{prefix}_PREFLIGHT_STATUS_INVALID")
    _require(
        value["comparator_outcome"] in {"EQUAL", "MISMATCH", "FAILED_CLOSED"},
        f"{prefix}_COMPARATOR_OUTCOME_INVALID",
    )
    _require(
        value["record_identity"] == _record_identity(value),
        f"{prefix}_RECORD_IDENTITY_STALE",
    )
    return value


def _one_record(
    records: Sequence[Mapping[str, Any]], sequence: int, record_type: str
) -> Mapping[str, Any]:
    matches = [
        record
        for record in records
        if record.get("record_sequence") == sequence
        and record.get("record_type") == record_type
    ]
    _require(len(matches) == 1, f"SOURCE_RECORD_AMBIGUOUS_OR_ABSENT__{sequence}")
    return matches[0]


def resolve_authoritative_provenance(
    observations: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Resolve independently from protected custody, never from supplied input."""

    if not observations:
        raise WrongProvenanceReductionError("AUTHORITATIVE_PROVENANCE_SOURCE_MISSING")
    material: set[tuple[str, str, str, str]] = set()
    for observation in observations:
        _require(
            isinstance(observation, Mapping)
            and set(observation) == RESOLUTION_OBSERVATION_FIELDS,
            "AUTHORITATIVE_PROVENANCE_OBSERVATION_INVALID",
        )
        _require(
            observation["source_role"] == "PROTECTED_CUSTODY_OWNER_STATE",
            "SUPPLIED_PROVENANCE_CANNOT_BE_AUTHORITATIVE",
        )
        _require(
            observation["authoritative_owner_identity"] == AUTHORITATIVE_OWNER,
            "AUTHORITATIVE_PROVENANCE_OWNER_INVALID",
        )
        for field in ("authority_act_identity", "owner_state_identity", "provenance_identity"):
            _require(
                isinstance(observation[field], str)
                and bool(observation[field].strip()),
                "AUTHORITATIVE_PROVENANCE_OBSERVATION_INVALID",
            )
        material.add(
            (
                observation["authoritative_owner_identity"],
                observation["owner_state_identity"],
                observation["authority_act_identity"],
                observation["provenance_identity"],
            )
        )
    _require(len(material) == 1, "AUTHORITATIVE_PROVENANCE_RESOLUTION_AMBIGUOUS")
    owner, owner_state, act_identity, provenance = next(iter(material))
    return {
        "authority_act_identity": act_identity,
        "authoritative_owner_identity": owner,
        "authoritative_provenance_identity": provenance,
        "owner_state_identity": owner_state,
        "resolution_status": "UNIQUE_AUTHENTICATED_EXISTING_PROTECTED_OWNER",
        "source_observation_count": len(observations),
    }


def _authenticated_source(root: Path) -> dict[str, Any]:
    raw = (root / SOURCE_RAW_PATH).read_bytes()
    _require(_sha256(raw) == SOURCE_RAW_SHA256, "SOURCE_EVIDENCE_HASH_MISMATCH")
    _require(_git_blob_identity(raw) == SOURCE_RAW_GIT_BLOB, "SOURCE_EVIDENCE_GIT_BLOB_MISMATCH")
    records = [
        json.loads(line, object_pairs_hook=_unique_object)
        for line in raw.decode("utf-8").splitlines()
        if line
    ]
    act_record = _one_record(records, SOURCE_ACT_SEQUENCE, "human_operational_act_created")
    owner_record = _one_record(records, SOURCE_OWNER_SEQUENCE, "human_operational_act_available")
    checkpoint_record = _one_record(records, SOURCE_CHECKPOINT_SEQUENCE, "spce_authority_checkpoint")

    act_facts = act_record.get("facts")
    _require(isinstance(act_facts, Mapping), "SOURCE_ACT_FACTS_INVALID")
    source_text = act_facts.get("input_canonical_utf8")
    source_record = _validate_input_record(act_facts.get("input_record"), prefix="BASELINE")
    _require(
        isinstance(source_text, str)
        and source_text.encode("utf-8") == _canonical_record_bytes(source_record),
        "SOURCE_INPUT_CANONICAL_BYTES_INVALID",
    )
    act_value = act_facts.get("human_authority_act")
    correlation_value = act_facts.get("che_correlation")
    _require(
        isinstance(act_value, dict) and isinstance(correlation_value, dict),
        "SOURCE_ACT_CHE_TUPLE_INCOMPLETE",
    )
    act = CanonicalHumanAuthorityActV1.from_dict(act_value)
    correlation = CanonicalCHEEvidenceCorrelationV1.from_dict(correlation_value)
    _require(correlation.authority_act_identity == act.authority_act_identity, "CHE_ACT_IDENTITY_BINDING_INVALID")
    _require(correlation.source_act_digest == replay_hash(act.to_dict()), "CHE_SOURCE_ACT_DIGEST_INVALID")
    _require(correlation.authority_payload_digest == act.payload_digest, "CHE_AUTHORITY_PAYLOAD_DIGEST_INVALID")
    _require(act.expected_owner == AUTHORITATIVE_OWNER, "SOURCE_ACT_EXPECTED_OWNER_INVALID")
    _require(correlation.authority_requesting_owner_identity == AUTHORITATIVE_OWNER, "CHE_OWNER_INVALID")
    _require(correlation.producing_owner_identity == "HUMAN_AUTHORITY", "CHE_PRODUCING_OWNER_INVALID")
    _require(correlation.owner_state_identity == act.target_identity, "CHE_OWNER_STATE_BINDING_INVALID")
    _require(act.metadata.get("generation_identity") == SOURCE_GENERATION, "SOURCE_GENERATION_MISMATCH")
    _require(correlation.metadata.get("generation_identity") == SOURCE_GENERATION, "CHE_GENERATION_MISMATCH")

    owner_facts = owner_record.get("facts")
    _require(isinstance(owner_facts, Mapping), "SOURCE_OWNER_FACTS_INVALID")
    available = owner_facts.get("available_state")
    revisions = owner_facts.get("owner_revision_files")
    _require(
        isinstance(available, Mapping)
        and available.get("state") == "AVAILABLE"
        and available.get("revision") == 0
        and isinstance(revisions, list)
        and len(revisions) == 1
        and isinstance(revisions[0], Mapping),
        "SOURCE_PROTECTED_OWNER_STATE_INVALID",
    )
    binding = available.get("binding")
    revision = dict(revisions[0])
    _require(isinstance(binding, Mapping) and revision.get("binding") == binding, "SOURCE_OWNER_BINDING_AMBIGUOUS")
    state_hash = revision.pop("state_hash", None)
    _require(state_hash == replay_hash(revision), "SOURCE_OWNER_STATE_HASH_INVALID")
    expected_binding = {
        "attempt_identity": source_record["attempt_identity"],
        "authority_act_identity": act.authority_act_identity,
        "authority_act_content_identity": replay_hash(act.to_dict()),
        "authorization_identity": act.authority_act_identity,
        "contract_content_sha256": source_record["contract_content_sha256"],
        "contract_identity": source_record["contract_identity"],
        "contract_version": source_record["contract_version"],
        "input_identity": source_record["input_identity"],
        "input_record_identity": source_record["record_identity"],
    }
    for field, expected in expected_binding.items():
        _require(binding.get(field) == expected, f"SOURCE_OWNER_BINDING_INVALID__{field}")

    checkpoint_facts = checkpoint_record.get("facts")
    preimage = checkpoint_facts.get("preimage") if isinstance(checkpoint_facts, Mapping) else None
    checkpoint_owner = preimage.get("owner_state_preimage") if isinstance(preimage, Mapping) else None
    _require(
        isinstance(checkpoint_owner, Mapping)
        and checkpoint_owner.get("binding") == binding
        and preimage.get("input_record_preimage") == source_record
        and preimage.get("authority_act_preimage") == act.to_dict()
        and preimage.get("che_correlation_preimage") == correlation.to_dict(),
        "SOURCE_CHECKPOINT_BINDING_INVALID",
    )
    provenance = binding.get("provenance_identity")
    _require(isinstance(provenance, str) and bool(provenance.strip()), "SOURCE_PROVENANCE_INVALID")
    observations = [
        {
            "authority_act_identity": act.authority_act_identity,
            "authoritative_owner_identity": AUTHORITATIVE_OWNER,
            "owner_state_identity": act.target_identity,
            "provenance_identity": provenance,
            "record_sequence": SOURCE_OWNER_SEQUENCE,
            "source_role": "PROTECTED_CUSTODY_OWNER_STATE",
        },
        {
            "authority_act_identity": act.authority_act_identity,
            "authoritative_owner_identity": AUTHORITATIVE_OWNER,
            "owner_state_identity": act.target_identity,
            "provenance_identity": checkpoint_owner["binding"]["provenance_identity"],
            "record_sequence": SOURCE_CHECKPOINT_SEQUENCE,
            "source_role": "PROTECTED_CUSTODY_OWNER_STATE",
        },
    ]
    resolution = resolve_authoritative_provenance(observations)
    _require(source_record["provenance_identity"] == resolution["authoritative_provenance_identity"], "BASELINE_PROVENANCE_NOT_AUTHORITATIVE")
    return {
        "input_record": source_record,
        "input_canonical_utf8": source_text,
        "observations": observations,
        "resolution": resolution,
    }


def reduce_wrong_provenance_candidate(
    candidate_canonical_bytes: bytes, *, repository_root: Path
) -> dict[str, Any]:
    """Accept repository capability while withholding route, operation, and credit."""

    _require(
        isinstance(candidate_canonical_bytes, bytes) and bool(candidate_canonical_bytes),
        "CANDIDATE_BYTES_MISSING",
    )
    try:
        candidate = json.loads(
            candidate_canonical_bytes, object_pairs_hook=_unique_object
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WrongProvenanceReductionError("CANDIDATE_NOT_CANONICAL_JSON") from exc
    _require(isinstance(candidate, Mapping), "CANDIDATE_NOT_OBJECT")
    _require(candidate_canonical_bytes == canonical_bytes(candidate), "CANDIDATE_NOT_CANONICAL_JSON")
    _require(set(candidate) == REQUIRED_FIELDS, "CANDIDATE_FIELDS_INCOMPLETE_OR_UNKNOWN")
    _require(candidate["schema_id"] == "G77_256HZ_WRONG_PROVENANCE_REPOSITORY_VECTOR_V1", "CANDIDATE_SCHEMA_MISMATCH")
    _require(candidate["generation_identity"] == GENERATION_ID, "GENERATION_IDENTITY_MISMATCH")
    _require(candidate["base_head"] == BASE_HEAD, "BASE_HEAD_MISMATCH")
    _require(candidate["base_tree"] == BASE_TREE, "BASE_TREE_MISMATCH")
    _require(candidate["case_id"] == CASE_ID, "CASE_ID_MISMATCH")
    _require(candidate["selected_vector"] == SELECTED_VECTOR, "MUTATION_CLASS_NOT_WRONG_PROVENANCE")
    _require(candidate["formal_specification_sha256"] == FORMAL_SPECIFICATION_SHA256, "FORMAL_SPECIFICATION_SHA256_MISMATCH")

    authenticated = _authenticated_source(repository_root.resolve())
    expected_source_evidence = {
        "authority_status": "HISTORICAL_CERTIFIED_EVIDENCE_ONLY__NOT_CURRENT_AUTHORITY",
        "git_blob": SOURCE_RAW_GIT_BLOB,
        "path": SOURCE_RAW_PATH.as_posix(),
        "sha256": SOURCE_RAW_SHA256,
    }
    _require(candidate["source_evidence"] == expected_source_evidence, "SOURCE_EVIDENCE_BINDING_INVALID")
    expected_resolution = {
        **authenticated["resolution"],
        "observations": authenticated["observations"],
        "source_is_current_operational_authority": False,
    }
    _require(candidate["authoritative_provenance_resolution"] == expected_resolution, "AUTHORITATIVE_PROVENANCE_PROOF_INVALID")
    resolved = resolve_authoritative_provenance(
        candidate["authoritative_provenance_resolution"].get("observations", [])
        if isinstance(candidate["authoritative_provenance_resolution"], Mapping)
        else []
    )

    baseline = _validate_input_record(candidate["baseline_input_record"], prefix="BASELINE")
    supplied = _validate_input_record(candidate["supplied_input_record"], prefix="SUPPLIED")
    _require(baseline == authenticated["input_record"], "BASELINE_INPUT_NOT_AUTHENTICATED")
    _require(
        candidate["baseline_input_canonical_utf8"].encode("utf-8")
        == _canonical_record_bytes(baseline)
        == authenticated["input_canonical_utf8"].encode("utf-8"),
        "BASELINE_CANONICAL_BYTES_INVALID",
    )
    _require(
        candidate["supplied_input_canonical_utf8"].encode("utf-8")
        == _canonical_record_bytes(supplied),
        "SUPPLIED_CANONICAL_BYTES_INVALID",
    )
    authoritative_identity = resolved["authoritative_provenance_identity"]
    _require(baseline["provenance_identity"] == authoritative_identity, "BASELINE_PROVENANCE_NOT_AUTHORITATIVE")
    _require(supplied["provenance_identity"] != authoritative_identity, "PROVENANCE_IDENTITY_NOT_MUTATED")

    actual_differing = sorted(key for key in baseline if baseline[key] != supplied[key])
    _require(candidate["differing_input_fields"] == EXPECTED_DIFFERING_FIELDS, "DECLARED_MUTATION_SET_INVALID")
    _require(actual_differing == EXPECTED_DIFFERING_FIELDS, "MULTIPLE_OR_UNRELATED_INDEPENDENT_MUTATION")
    _require(candidate["independent_mutation_count"] == 1, "INDEPENDENT_MUTATION_COUNT_INVALID")
    _require(candidate["independent_mutated_coordinate"] == "provenance_identity", "INDEPENDENT_MUTATED_COORDINATE_INVALID")
    _require(candidate["dependent_recomputation_count"] == 1, "DEPENDENT_RECOMPUTATION_COUNT_INVALID")
    _require(candidate["dependent_recomputed_coordinate"] == "record_identity", "DEPENDENT_RECOMPUTED_COORDINATE_INVALID")
    expected_preserved = {
        key: True for key in sorted(baseline) if key not in EXPECTED_DIFFERING_FIELDS
    }
    _require(candidate["preserved_independent_coordinate_proof"] == expected_preserved, "PRESERVED_COORDINATE_PROOF_INVALID")

    _require(candidate["expected_denial_boundary"] == EXPECTED_DENIAL_BOUNDARY, "EXPECTED_DENIAL_BOUNDARY_INVALID")
    _require(candidate["expected_error_type"] == EXPECTED_ERROR_TYPE, "EXPECTED_ERROR_TYPE_INVALID")
    _require(candidate["expected_error_reason"] == EXPECTED_ERROR_REASON, "EXPECTED_ERROR_REASON_INVALID")
    _require(candidate["provenance_specific_comparison_reached"] is False, "DENIAL_REACHABILITY_OVERCLAIM")
    _require(candidate["repository_vector_only"] is True, "REPOSITORY_ONLY_BOUNDARY_INVALID")
    _require(candidate["authority_created"] is False, "AUTHORITY_CREATION_OVERCLAIM")
    _require(candidate["request_created"] is False, "REQUEST_CREATION_OVERCLAIM")
    _require(candidate["operation_attempted"] is False, "OPERATION_OVERCLAIM")
    _require(candidate["e05_credit"] == 0, "E05_CREDIT_OVERCLAIM")

    return {
        "authoritative_provenance_identity": authoritative_identity,
        "authoritative_provenance_resolution": "VERIFIED__UNIQUE_EXISTING_PROTECTED_OWNER",
        "auto_continuable": False,
        "binding_status": "NOT_PROVEN",
        "dependent_recomputation_count": 1,
        "dependent_recomputed_coordinate": "record_identity",
        "e05_after": "9/18",
        "e05_before": "9/18",
        "e05_credit": 0,
        "expected_denial_reachability": "VERIFIED__EARLIER_RECORD_IDENTITY_BINDING_DENIAL__PROVENANCE_SPECIFIC_COMPARISON_NOT_REACHED",
        "human_review_required": True,
        "independent_mutated_coordinate": "provenance_identity",
        "independent_mutation_count": 1,
        "operational_capability": "NOT_PROVEN",
        "preoperational_readiness": "NOT_PROVEN",
        "repository_capability": "VERIFIED",
        "route_support": "NOT_PROVEN",
        "terminal_acceptance": "PASS__BOUNDED_WRONG_PROVENANCE_REPOSITORY_CAPABILITY_ONLY",
    }


if __name__ == "__main__":
    raise SystemExit("repository-only module; no operational entry point")
