#!/usr/bin/env python3
"""Deterministic repository-only producer for one E05 WRONG_PROVENANCE vector.

The existing protected P11 custody owner-state is the provenance authority.
This module only authenticates committed evidence and emits canonical bytes. It
contains no authority, request, PRE, launcher, VM, P11-entry, or operation path.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType
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
TARGET_COORDINATE = "provenance_identity"
DEPENDENT_COORDINATES = ("record_identity",)
EXPECTED_DIFFERING_FIELDS = ("provenance_identity", "record_identity")
EXPECTED_DENIAL_BOUNDARY = (
    "D2_PRECLAIM_AUTHORITY_BINDING_VALIDATION_BEFORE_PRECLAIM_LEDGER_APPEND_"
    "CLAIM_ENTRY_INVOCATION_OR_EFFECT"
)
EXPECTED_ERROR_TYPE = "FailClosedRuntimeError"
EXPECTED_ERROR_REASON = "operational Human act input_record_identity binding is invalid"
SPECIFICATION_INNER_SHA256 = "f3dd54dafd6e3c390c456d3fdc1408c2f57c887352f26e7d122d59b292136bd0"

SPECIFICATION_PATH = Path(
    ".github/governance/evidence/g77_256hz_wrong_provenance_formalization_v1/"
    "G77_256HZ_WRONG_PROVENANCE_FORMAL_SPECIFICATION_V1.json"
)
SUBSTRATE_PATH = Path("tests/p11_da_disposable_substrate_v1.py")
SUBSTRATE_SHA256 = "a1b58fa8ddedb5058393aa23d815262c92c8b185c0b193764f77420313af0bab"
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


class WrongProvenanceProducerError(ValueError):
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


def git_blob_identity(value: bytes) -> str:
    header = f"blob {len(value)}\0".encode("ascii")
    return hashlib.sha1(header + value).hexdigest()


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise WrongProvenanceProducerError(f"DUPLICATE_JSON_KEY__{key}")
        value[key] = item
    return value


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise WrongProvenanceProducerError(code)


def _load_module(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise WrongProvenanceProducerError(f"MODULE_LOAD_FAILED__{identity}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def _authenticate_specification(root: Path) -> dict[str, Any]:
    raw = (root / SPECIFICATION_PATH).read_bytes()
    envelope = json.loads(raw, object_pairs_hook=_unique_object)
    _require(raw == canonical_document_bytes(envelope), "FORMAL_SPECIFICATION_NOT_CANONICAL")
    _require(
        set(envelope) == {"schema_id", "specification", "specification_sha256"},
        "FORMAL_SPECIFICATION_ENVELOPE_INVALID",
    )
    _require(
        envelope["schema_id"]
        == "G77_256HZ_WRONG_PROVENANCE_FORMAL_SPECIFICATION_ENVELOPE_V1",
        "FORMAL_SPECIFICATION_SCHEMA_INVALID",
    )
    inner = sha256_bytes(canonical_bytes(envelope["specification"]))
    _require(
        inner == envelope["specification_sha256"] == SPECIFICATION_INNER_SHA256,
        "FORMAL_SPECIFICATION_SEAL_INVALID",
    )
    return envelope


def _load_substrate(root: Path) -> ModuleType:
    path = root / SUBSTRATE_PATH
    _require(sha256_bytes(path.read_bytes()) == SUBSTRATE_SHA256, "P11_SUBSTRATE_HASH_MISMATCH")
    return _load_module(path, "g77_256hz_p11_input_owner")


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


def _resolution_observation(
    *, sequence: int, owner_state_identity: str, authority_act_identity: str, provenance_identity: str
) -> dict[str, Any]:
    return {
        "authority_act_identity": authority_act_identity,
        "authoritative_owner_identity": AUTHORITATIVE_OWNER,
        "owner_state_identity": owner_state_identity,
        "provenance_identity": provenance_identity,
        "record_sequence": sequence,
        "source_role": "PROTECTED_CUSTODY_OWNER_STATE",
    }


def resolve_authoritative_provenance(
    observations: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Resolve one material identity from existing protected-owner observations."""

    if not observations:
        raise WrongProvenanceProducerError("AUTHORITATIVE_PROVENANCE_SOURCE_MISSING")
    expected_fields = {
        "authority_act_identity",
        "authoritative_owner_identity",
        "owner_state_identity",
        "provenance_identity",
        "record_sequence",
        "source_role",
    }
    material: set[tuple[str, str, str, str]] = set()
    for observation in observations:
        _require(
            isinstance(observation, Mapping) and set(observation) == expected_fields,
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
                isinstance(observation[field], str) and bool(observation[field].strip()),
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
    if len(material) != 1:
        raise WrongProvenanceProducerError("AUTHORITATIVE_PROVENANCE_RESOLUTION_AMBIGUOUS")
    owner, owner_state, act_identity, provenance = next(iter(material))
    return {
        "authority_act_identity": act_identity,
        "authoritative_owner_identity": owner,
        "authoritative_provenance_identity": provenance,
        "owner_state_identity": owner_state,
        "resolution_status": "UNIQUE_AUTHENTICATED_EXISTING_PROTECTED_OWNER",
        "source_observation_count": len(observations),
    }


def _authenticated_source(root: Path, substrate: ModuleType) -> dict[str, Any]:
    raw = (root / SOURCE_RAW_PATH).read_bytes()
    _require(sha256_bytes(raw) == SOURCE_RAW_SHA256, "SOURCE_EVIDENCE_HASH_MISMATCH")
    _require(git_blob_identity(raw) == SOURCE_RAW_GIT_BLOB, "SOURCE_EVIDENCE_GIT_BLOB_MISMATCH")
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
    source_record = act_facts.get("input_record")
    act_value = act_facts.get("human_authority_act")
    correlation_value = act_facts.get("che_correlation")
    _require(
        isinstance(source_text, str)
        and isinstance(source_record, Mapping)
        and isinstance(act_value, dict)
        and isinstance(correlation_value, dict),
        "SOURCE_ACT_INPUT_CHE_TUPLE_INCOMPLETE",
    )
    validated_record = substrate.validate_input_record_bytes(source_text.encode("utf-8"))
    _require(validated_record == source_record, "SOURCE_INPUT_PREIMAGE_MISMATCH")
    act = CanonicalHumanAuthorityActV1.from_dict(act_value)
    correlation = CanonicalCHEEvidenceCorrelationV1.from_dict(correlation_value)
    substrate.P11CaptureReplayAdapter.validate_existing_authority_sources(act, correlation)
    _require(act.metadata.get("generation_identity") == SOURCE_GENERATION, "SOURCE_GENERATION_MISMATCH")
    _require(correlation.metadata.get("generation_identity") == SOURCE_GENERATION, "CHE_GENERATION_MISMATCH")
    _require(act.expected_owner == AUTHORITATIVE_OWNER, "SOURCE_ACT_EXPECTED_OWNER_INVALID")
    _require(correlation.authority_requesting_owner_identity == AUTHORITATIVE_OWNER, "CHE_OWNER_INVALID")
    _require(correlation.producing_owner_identity == "HUMAN_AUTHORITY", "CHE_PRODUCING_OWNER_INVALID")
    _require(correlation.owner_state_identity == act.target_identity, "CHE_OWNER_STATE_BINDING_INVALID")
    _require(correlation.source_act_digest == replay_hash(act.to_dict()), "CHE_SOURCE_ACT_DIGEST_INVALID")
    _require(correlation.authority_payload_digest == act.payload_digest, "CHE_AUTHORITY_PAYLOAD_DIGEST_INVALID")

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
        "attempt_identity": validated_record["attempt_identity"],
        "authority_act_identity": act.authority_act_identity,
        "authority_act_content_identity": replay_hash(act.to_dict()),
        "authorization_identity": act.authority_act_identity,
        "contract_content_sha256": validated_record["contract_content_sha256"],
        "contract_identity": validated_record["contract_identity"],
        "contract_version": validated_record["contract_version"],
        "input_identity": validated_record["input_identity"],
        "input_record_identity": validated_record["record_identity"],
    }
    for field, expected in expected_binding.items():
        _require(binding.get(field) == expected, f"SOURCE_OWNER_BINDING_INVALID__{field}")

    checkpoint_facts = checkpoint_record.get("facts")
    preimage = checkpoint_facts.get("preimage") if isinstance(checkpoint_facts, Mapping) else None
    _require(isinstance(preimage, Mapping), "SOURCE_CHECKPOINT_PREIMAGE_INVALID")
    checkpoint_owner = preimage.get("owner_state_preimage")
    _require(
        isinstance(checkpoint_owner, Mapping)
        and checkpoint_owner.get("binding") == binding
        and preimage.get("input_record_preimage") == validated_record
        and preimage.get("authority_act_preimage") == act.to_dict()
        and preimage.get("che_correlation_preimage") == correlation.to_dict(),
        "SOURCE_CHECKPOINT_BINDING_INVALID",
    )

    provenance = binding.get("provenance_identity")
    _require(isinstance(provenance, str) and bool(provenance.strip()), "SOURCE_PROVENANCE_INVALID")
    observations = [
        _resolution_observation(
            sequence=SOURCE_OWNER_SEQUENCE,
            owner_state_identity=act.target_identity,
            authority_act_identity=act.authority_act_identity,
            provenance_identity=provenance,
        ),
        _resolution_observation(
            sequence=SOURCE_CHECKPOINT_SEQUENCE,
            owner_state_identity=act.target_identity,
            authority_act_identity=act.authority_act_identity,
            provenance_identity=checkpoint_owner["binding"]["provenance_identity"],
        ),
    ]
    resolution = resolve_authoritative_provenance(observations)
    _require(validated_record["provenance_identity"] == resolution["authoritative_provenance_identity"], "BASELINE_PROVENANCE_NOT_AUTHORITATIVE")
    return {
        "act_identity": act.authority_act_identity,
        "input_canonical_bytes": source_text.encode("utf-8"),
        "input_record": validated_record,
        "observations": observations,
        "resolution": resolution,
    }


def produce_wrong_provenance_vector(
    *, repository_root: Path, wrong_provenance_identity: str
) -> dict[str, Any]:
    """Replace provenance_identity once and recompute only record_identity."""

    root = repository_root.resolve()
    _authenticate_specification(root)
    substrate = _load_substrate(root)
    source = _authenticated_source(root, substrate)
    _require(
        isinstance(wrong_provenance_identity, str)
        and bool(wrong_provenance_identity.strip())
        and wrong_provenance_identity == wrong_provenance_identity.strip(),
        "WRONG_PROVENANCE_IDENTITY_MALFORMED",
    )
    authorized = source["input_record"]
    authoritative = source["resolution"]["authoritative_provenance_identity"]
    _require(wrong_provenance_identity != authoritative, "PROVENANCE_IDENTITY_NOT_MUTATED")

    supplied_value = dict(authorized)
    supplied_value["record_identity"] = ""
    supplied_value[TARGET_COORDINATE] = wrong_provenance_identity
    supplied_bytes = substrate.bind_record_identity(supplied_value)
    supplied = substrate.validate_input_record_bytes(supplied_bytes)
    differing = tuple(sorted(key for key in authorized if authorized[key] != supplied[key]))
    _require(differing == EXPECTED_DIFFERING_FIELDS, "WRONG_PROVENANCE_MUTATION_NOT_ISOLATED")
    preserved = {
        key: authorized[key] == supplied[key]
        for key in sorted(authorized)
        if key not in EXPECTED_DIFFERING_FIELDS
    }
    _require(bool(preserved) and set(preserved.values()) == {True}, "NON_TARGET_DIMENSION_CHANGED")

    return {
        "authority_created": False,
        "authoritative_provenance_resolution": {
            **source["resolution"],
            "observations": source["observations"],
            "source_is_current_operational_authority": False,
        },
        "base_head": BASE_HEAD,
        "base_tree": BASE_TREE,
        "baseline_input_canonical_utf8": source["input_canonical_bytes"].decode("utf-8"),
        "baseline_input_record": authorized,
        "case_id": CASE_ID,
        "dependent_recomputation_count": 1,
        "dependent_recomputed_coordinate": "record_identity",
        "differing_input_fields": list(differing),
        "e05_credit": 0,
        "expected_denial_boundary": EXPECTED_DENIAL_BOUNDARY,
        "expected_error_reason": EXPECTED_ERROR_REASON,
        "expected_error_type": EXPECTED_ERROR_TYPE,
        "formal_specification_sha256": SPECIFICATION_INNER_SHA256,
        "generation_identity": GENERATION_ID,
        "independent_mutated_coordinate": TARGET_COORDINATE,
        "independent_mutation_count": 1,
        "operation_attempted": False,
        "preserved_independent_coordinate_proof": preserved,
        "provenance_specific_comparison_reached": False,
        "repository_vector_only": True,
        "request_created": False,
        "schema_id": "G77_256HZ_WRONG_PROVENANCE_REPOSITORY_VECTOR_V1",
        "selected_vector": SELECTED_VECTOR,
        "source_evidence": {
            "authority_status": "HISTORICAL_CERTIFIED_EVIDENCE_ONLY__NOT_CURRENT_AUTHORITY",
            "git_blob": SOURCE_RAW_GIT_BLOB,
            "path": SOURCE_RAW_PATH.as_posix(),
            "sha256": SOURCE_RAW_SHA256,
        },
        "supplied_input_canonical_utf8": supplied_bytes.decode("utf-8"),
        "supplied_input_record": supplied,
    }


def produce_wrong_provenance_vector_bytes(
    *, repository_root: Path, wrong_provenance_identity: str
) -> bytes:
    return canonical_bytes(
        produce_wrong_provenance_vector(
            repository_root=repository_root,
            wrong_provenance_identity=wrong_provenance_identity,
        )
    )


if __name__ == "__main__":
    raise SystemExit("repository-only module; no operational entry point")
