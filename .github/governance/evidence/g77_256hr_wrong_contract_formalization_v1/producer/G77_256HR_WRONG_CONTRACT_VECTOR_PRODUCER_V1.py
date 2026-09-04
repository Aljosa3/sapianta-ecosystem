#!/usr/bin/env python3
"""Deterministic repository-only producer for one E05 WRONG_CONTRACT vector.

This module reads authenticated committed evidence and emits canonical candidate
bytes.  It owns no authority, PRE, launcher, P11 entry, VM, or operation path.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType
from typing import Any


GENERATION_ID = "G77_256HR_REPOSITORY_ONLY_WRONG_CONTRACT_FORMALIZATION_V1"
CASE_ID = "G77_256HR_E05_WRONG_CONTRACT_REPOSITORY_VECTOR_001"
SELECTED_VECTOR = "P11-E05/NEGATIVE_AUTHORITY/WRONG_CONTRACT"
TARGET_COORDINATE = "contract_identity"
DEPENDENT_COORDINATES = ("record_identity",)
EXPECTED_DIFFERING_FIELDS = ("contract_identity", "record_identity")
EXPECTED_DENIAL_BOUNDARY = (
    "D2_PRECLAIM_AUTHORITY_BINDING_VALIDATION_BEFORE_PRECLAIM_LEDGER_APPEND_"
    "CLAIM_ENTRY_INVOCATION_OR_EFFECT"
)
EXPECTED_ERROR_TYPE = "FailClosedRuntimeError"
EXPECTED_ERROR_REASON = "operational Human act input_record_identity binding is invalid"
SPECIFICATION_INNER_SHA256 = "f376752ee8c77879a96a5e05a25e6dee3a064477da051c2fa67d456627396228"

SPECIFICATION_PATH = Path(
    ".github/governance/evidence/g77_256hr_wrong_contract_formalization_v1/"
    "G77_256HR_WRONG_CONTRACT_FORMAL_SPECIFICATION_V1.json"
)
SUBSTRATE_PATH = Path("tests/p11_da_disposable_substrate_v1.py")
SUBSTRATE_SHA256 = "a1b58fa8ddedb5058393aa23d815262c92c8b185c0b193764f77420313af0bab"
SOURCE_RAW_PATH = Path(
    ".github/governance/evidence/g77_256hp_wrong_input_operational_v1/"
    "operation_state/runtime_export/G77_256HP_RAW_EXECUTION_EVIDENCE_V1.jsonl"
)
SOURCE_RAW_SHA256 = "116f694f80e95d88104df7d8b01ed0458212ae0b5d0222cd86419443c8d0f189"
SOURCE_RAW_GIT_BLOB = "289cc783b6a7fa4c4407e8ec1842ac8b2346ac37"
SOURCE_RECORD_SEQUENCE = 16
SOURCE_RECORD_TYPE = "human_operational_act_created"


class WrongContractProducerError(ValueError):
    """One deterministic fail-closed producer rejection."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def canonical_document_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode(
        "utf-8"
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise WrongContractProducerError(f"DUPLICATE_JSON_KEY__{key}")
        value[key] = item
    return value


def _load_module(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise WrongContractProducerError(f"MODULE_LOAD_FAILED__{identity}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def _authenticate_specification(root: Path) -> dict[str, Any]:
    raw = (root / SPECIFICATION_PATH).read_bytes()
    envelope = json.loads(raw, object_pairs_hook=_unique_object)
    if raw != canonical_document_bytes(envelope):
        raise WrongContractProducerError("FORMAL_SPECIFICATION_NOT_CANONICAL")
    if set(envelope) != {"schema_id", "specification", "specification_sha256"}:
        raise WrongContractProducerError("FORMAL_SPECIFICATION_ENVELOPE_INVALID")
    if envelope["schema_id"] != "G77_256HR_WRONG_CONTRACT_FORMAL_SPECIFICATION_ENVELOPE_V1":
        raise WrongContractProducerError("FORMAL_SPECIFICATION_SCHEMA_INVALID")
    inner = sha256_bytes(canonical_bytes(envelope["specification"]))
    if inner != envelope["specification_sha256"] or inner != SPECIFICATION_INNER_SHA256:
        raise WrongContractProducerError("FORMAL_SPECIFICATION_SEAL_INVALID")
    return envelope


def _load_substrate(root: Path) -> ModuleType:
    path = root / SUBSTRATE_PATH
    if sha256_bytes(path.read_bytes()) != SUBSTRATE_SHA256:
        raise WrongContractProducerError("P11_SUBSTRATE_HASH_MISMATCH")
    return _load_module(path, "g77_256hr_p11_input_owner")


def _authenticated_source(root: Path, substrate: ModuleType) -> dict[str, Any]:
    path = root / SOURCE_RAW_PATH
    raw_bytes = path.read_bytes()
    if sha256_bytes(raw_bytes) != SOURCE_RAW_SHA256:
        raise WrongContractProducerError("SOURCE_PROVENANCE_HASH_MISMATCH")
    records = [
        json.loads(line, object_pairs_hook=_unique_object)
        for line in raw_bytes.decode("utf-8").splitlines()
        if line
    ]
    matches = [
        record
        for record in records
        if record.get("record_sequence") == SOURCE_RECORD_SEQUENCE
        and record.get("record_type") == SOURCE_RECORD_TYPE
    ]
    if len(matches) != 1:
        raise WrongContractProducerError("SOURCE_PROVENANCE_RECORD_AMBIGUOUS_OR_ABSENT")
    facts = matches[0].get("facts")
    if not isinstance(facts, dict):
        raise WrongContractProducerError("SOURCE_FACTS_INVALID")
    source_text = facts.get("input_canonical_utf8")
    source_record = facts.get("input_record")
    act = facts.get("human_authority_act")
    if not isinstance(source_text, str) or not isinstance(source_record, dict) or not isinstance(act, dict):
        raise WrongContractProducerError("SOURCE_ACT_INPUT_PAIR_INCOMPLETE")
    source_bytes = source_text.encode("utf-8")
    validated = substrate.validate_input_record_bytes(source_bytes)
    if validated != source_record:
        raise WrongContractProducerError("SOURCE_INPUT_PREIMAGE_MISMATCH")
    payload = act.get("payload")
    if not isinstance(payload, dict):
        raise WrongContractProducerError("SOURCE_ACT_PAYLOAD_INVALID")
    contract_fields = (
        "contract_identity",
        "contract_version",
        "contract_content_sha256",
    )
    if any(payload.get(field) != validated.get(field) for field in contract_fields):
        raise WrongContractProducerError("SOURCE_CONTRACT_TRIPLE_NOT_AUTHORIZED")
    return {
        "act_identity": act.get("authority_act_identity"),
        "authorized_contract_binding": {
            field: payload[field] for field in contract_fields
        },
        "input_canonical_bytes": source_bytes,
        "input_record": validated,
    }


def produce_wrong_contract_vector(
    *, repository_root: Path, wrong_contract_identity: str
) -> dict[str, Any]:
    """Replace only contract_identity and recompute only record_identity."""

    root = repository_root.resolve()
    _authenticate_specification(root)
    substrate = _load_substrate(root)
    source = _authenticated_source(root, substrate)
    if not isinstance(wrong_contract_identity, str) or not wrong_contract_identity.strip():
        raise WrongContractProducerError("WRONG_CONTRACT_IDENTITY_MALFORMED")
    authorized = source["input_record"]
    if wrong_contract_identity == authorized[TARGET_COORDINATE]:
        raise WrongContractProducerError("CONTRACT_IDENTITY_NOT_MUTATED")

    candidate_value = dict(authorized)
    candidate_value["record_identity"] = ""
    candidate_value[TARGET_COORDINATE] = wrong_contract_identity
    candidate_bytes = substrate.bind_record_identity(candidate_value)
    candidate = substrate.validate_input_record_bytes(candidate_bytes)
    differing = tuple(
        sorted(key for key in authorized if authorized[key] != candidate[key])
    )
    if differing != EXPECTED_DIFFERING_FIELDS:
        raise WrongContractProducerError(
            "WRONG_CONTRACT_MUTATION_NOT_ISOLATED__" + ",".join(differing)
        )
    preserved = {
        key: authorized[key] == candidate[key]
        for key in sorted(authorized)
        if key not in EXPECTED_DIFFERING_FIELDS
    }
    if not preserved or set(preserved.values()) != {True}:
        raise WrongContractProducerError("NON_TARGET_DIMENSION_CHANGED")

    return {
        "schema_id": "G77_256HR_WRONG_CONTRACT_REPOSITORY_VECTOR_V1",
        "generation_identity": GENERATION_ID,
        "case_id": CASE_ID,
        "selected_vector": SELECTED_VECTOR,
        "formal_specification_sha256": SPECIFICATION_INNER_SHA256,
        "source_provenance": {
            "authority_status": "HISTORICAL_EVIDENCE_ONLY__NOT_CURRENT_AUTHORITY",
            "path": SOURCE_RAW_PATH.as_posix(),
            "sha256": SOURCE_RAW_SHA256,
            "git_blob": SOURCE_RAW_GIT_BLOB,
            "record_sequence": SOURCE_RECORD_SEQUENCE,
            "record_type": SOURCE_RECORD_TYPE,
            "source_act_identity": source["act_identity"],
        },
        "authorized_contract_binding": source["authorized_contract_binding"],
        "source_input_record": authorized,
        "candidate_input_record": candidate,
        "source_input_canonical_utf8": source["input_canonical_bytes"].decode("utf-8"),
        "candidate_input_canonical_utf8": candidate_bytes.decode("utf-8"),
        "target_mutated_coordinate": TARGET_COORDINATE,
        "dependent_recomputation_fields": list(DEPENDENT_COORDINATES),
        "semantic_mutation_count": 1,
        "differing_input_fields": list(differing),
        "preserved_dimension_proof": preserved,
        "expected_denial_boundary": EXPECTED_DENIAL_BOUNDARY,
        "expected_error_type": EXPECTED_ERROR_TYPE,
        "expected_error_reason": EXPECTED_ERROR_REASON,
        "contract_specific_comparison_reached": False,
        "repository_vector_only": True,
        "authority_created": False,
        "request_created": False,
        "operation_attempted": False,
        "e05_credit": 0,
    }


def produce_wrong_contract_vector_bytes(
    *, repository_root: Path, wrong_contract_identity: str
) -> bytes:
    """Emit deterministic canonical JSON bytes for the bounded vector."""

    return canonical_bytes(
        produce_wrong_contract_vector(
            repository_root=repository_root,
            wrong_contract_identity=wrong_contract_identity,
        )
    )


if __name__ == "__main__":
    raise SystemExit("repository-only module; no operational entry point")
