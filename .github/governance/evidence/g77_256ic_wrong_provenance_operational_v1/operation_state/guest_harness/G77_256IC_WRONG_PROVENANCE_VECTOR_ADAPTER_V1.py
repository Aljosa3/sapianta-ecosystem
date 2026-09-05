#!/usr/bin/env python3
"""Bounded WRONG_PROVENANCE adapter for the existing FM guest/P11 boundary.

This adapter owns no launcher, authority, P11 semantics, or production route.
It authenticates and reuses the committed HZ producer and independent reducer,
then derives the existing FC/FK runtime specialization for exactly one
independent ``provenance_identity`` mutation and its dependent
``record_identity`` recomputation.
"""

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys
from types import ModuleType
from typing import Any


HZ_PRODUCER_RELATIVE_PATH = Path(
    ".github/governance/evidence/g77_256hz_wrong_provenance_formalization_v1/"
    "producer/G77_256HZ_WRONG_PROVENANCE_VECTOR_PRODUCER_V1.py"
)
HZ_PRODUCER_SHA256 = (
    "d8b6933b024248f6650ec74295dbe1ce1c864377648e8e2804a34e15b6c01b12"
)
HZ_REDUCER_RELATIVE_PATH = Path(
    ".github/governance/evidence/g77_256hz_wrong_provenance_formalization_v1/"
    "reducer/G77_256HZ_WRONG_PROVENANCE_REPOSITORY_CAPABILITY_REDUCER_V1.py"
)
HZ_REDUCER_SHA256 = (
    "b30c082185ebe185a0be0504a44ebc97d8f20a201b143a93b8d53e2e356a6585"
)
FC_ADAPTER_RELATIVE_PATH = Path(
    ".github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/harness/"
    "G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
)
FC_ADAPTER_SHA256 = (
    "7ae104802f49613ca60836913d2c68269b59728bc35bb677fdb3637aaf4b84c6"
)
GUEST_REPOSITORY_ROOT = Path("/mnt/aigol")
GUEST_CONTEXT_PATH = Path("/mnt/g77-evidence/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json")
SELECTED_VECTOR = "P11-E05/NEGATIVE_AUTHORITY/WRONG_PROVENANCE"
TARGET_MUTATION = "provenance_identity"
DEPENDENT_RECOMPUTATION = "record_identity"
EXPECTED_DIFFERING_FIELDS = ["provenance_identity", "record_identity"]
EXPECTED_DENIAL_REASON = (
    "operational Human act input_record_identity binding is invalid"
)
EXPECTED_DENIAL_BOUNDARY = (
    "D2_PRECLAIM_AUTHORITY_BINDING_VALIDATION_BEFORE_PRECLAIM_LEDGER_APPEND_"
    "CLAIM_ENTRY_INVOCATION_OR_EFFECT"
)


class WrongProvenanceAdapterError(RuntimeError):
    """Fail-closed adapter construction or specialization error."""


def _sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_module(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise WrongProvenanceAdapterError("WRONG_PROVENANCE_OWNER_IMPORT_FAILED")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def _load_hz_owners(repository_root: Path) -> tuple[ModuleType, ModuleType]:
    """Authenticate both committed HZ semantic owners before reuse."""

    root = repository_root.resolve()
    producer_path = root / HZ_PRODUCER_RELATIVE_PATH
    reducer_path = root / HZ_REDUCER_RELATIVE_PATH
    for path, expected_hash, code in (
        (producer_path, HZ_PRODUCER_SHA256, "HZ_PRODUCER"),
        (reducer_path, HZ_REDUCER_SHA256, "HZ_REDUCER"),
    ):
        if path.is_symlink() or not path.is_file():
            raise WrongProvenanceAdapterError(f"{code}_PATH_INVALID")
        if _sha256_path(path) != expected_hash:
            raise WrongProvenanceAdapterError(f"{code}_HASH_MISMATCH")
    return (
        _load_module(producer_path, "g77_256ia_committed_hz_producer"),
        _load_module(reducer_path, "g77_256ia_committed_hz_reducer"),
    )


def construct_wrong_provenance_payload(
    *, repository_root: Path, wrong_provenance_identity: str, request_identity: str
) -> dict[str, Any]:
    """Project the exact producer bytes only after independent HZ reduction."""

    producer, reducer = _load_hz_owners(repository_root)
    candidate_bytes = producer.produce_wrong_provenance_vector_bytes(
        repository_root=repository_root,
        wrong_provenance_identity=wrong_provenance_identity,
    )
    reduction = reducer.reduce_wrong_provenance_candidate(
        candidate_bytes,
        repository_root=repository_root,
    )
    required_reduction = {
        "authoritative_provenance_resolution": (
            "VERIFIED__UNIQUE_EXISTING_PROTECTED_OWNER"
        ),
        "binding_status": "NOT_PROVEN",
        "dependent_recomputation_count": 1,
        "dependent_recomputed_coordinate": DEPENDENT_RECOMPUTATION,
        "e05_credit": 0,
        "expected_denial_reachability": (
            "VERIFIED__EARLIER_RECORD_IDENTITY_BINDING_DENIAL__"
            "PROVENANCE_SPECIFIC_COMPARISON_NOT_REACHED"
        ),
        "independent_mutated_coordinate": TARGET_MUTATION,
        "independent_mutation_count": 1,
        "operational_capability": "NOT_PROVEN",
        "preoperational_readiness": "NOT_PROVEN",
        "repository_capability": "VERIFIED",
        "route_support": "NOT_PROVEN",
    }
    for field, expected in required_reduction.items():
        if reduction.get(field) != expected:
            raise WrongProvenanceAdapterError(f"HZ_REDUCTION_DRIFT__{field}")
    candidate = producer.produce_wrong_provenance_vector(
        repository_root=repository_root,
        wrong_provenance_identity=wrong_provenance_identity,
    )
    required_candidate = {
        "selected_vector": SELECTED_VECTOR,
        "independent_mutated_coordinate": TARGET_MUTATION,
        "independent_mutation_count": 1,
        "dependent_recomputed_coordinate": DEPENDENT_RECOMPUTATION,
        "dependent_recomputation_count": 1,
        "differing_input_fields": EXPECTED_DIFFERING_FIELDS,
        "expected_denial_boundary": EXPECTED_DENIAL_BOUNDARY,
        "expected_error_reason": EXPECTED_DENIAL_REASON,
        "provenance_specific_comparison_reached": False,
        "authority_created": False,
        "request_created": False,
        "operation_attempted": False,
        "e05_credit": 0,
    }
    for field, expected in required_candidate.items():
        if candidate.get(field) != expected:
            raise WrongProvenanceAdapterError(f"HZ_SEMANTIC_BINDING_DRIFT__{field}")
    resolution = candidate.get("authoritative_provenance_resolution")
    if not isinstance(resolution, dict) or resolution.get("resolution_status") != (
        "UNIQUE_AUTHENTICATED_EXISTING_PROTECTED_OWNER"
    ):
        raise WrongProvenanceAdapterError("HZ_AUTHORITATIVE_PROVENANCE_DRIFT")
    return {
        "schema_id": "G77_256IA_WRONG_PROVENANCE_GUEST_ADAPTER_PROJECTION_V1",
        "protocol_identity": "P11_DA_DISPOSABLE_LOCAL_IPC_V1",
        "operation": "CLAIM_AND_INVOKE_ONCE",
        "request_identity": request_identity,
        "canonical_payload_utf8": candidate["supplied_input_canonical_utf8"],
        "semantic_binding": required_candidate,
        "authoritative_provenance_resolution": required_reduction[
            "authoritative_provenance_resolution"
        ],
        "request_is_authority": False,
        "adapter_invoked_p11": False,
        "operational_execution_count": 0,
    }


def construct_existing_custody_request(
    *, repository_root: Path, wrong_provenance_identity: str, request_identity: str
) -> Any:
    """Construct the existing request type without entering the P11 consumer."""

    root = repository_root.resolve()
    sys.path.insert(0, str(root / "tests"))
    try:
        from p11_da_custody_process_v1 import CustodyOperation, CustodyRequest
    finally:
        sys.path.pop(0)
    projection = construct_wrong_provenance_payload(
        repository_root=root,
        wrong_provenance_identity=wrong_provenance_identity,
        request_identity=request_identity,
    )
    return CustodyRequest(
        protocol_identity=projection["protocol_identity"],
        operation=CustodyOperation.CLAIM_AND_INVOKE_ONCE,
        request_identity=projection["request_identity"],
        canonical_payload=projection["canonical_payload_utf8"].encode("utf-8"),
    )


def specialize_fc_runtime_source(
    *, repository_root: Path, identity_namespace_prefix: str
) -> str:
    """Derive the closed WRONG_PROVENANCE strategy from the FC/FK runtime."""

    source_path = repository_root.resolve() / FC_ADAPTER_RELATIVE_PATH
    if source_path.is_symlink() or not source_path.is_file():
        raise WrongProvenanceAdapterError("FC_FK_ADAPTER_PATH_INVALID")
    if _sha256_path(source_path) != FC_ADAPTER_SHA256:
        raise WrongProvenanceAdapterError("FC_FK_ADAPTER_HASH_MISMATCH")
    if not identity_namespace_prefix.startswith("G77_256"):
        raise WrongProvenanceAdapterError("IDENTITY_NAMESPACE_PREFIX_INVALID")
    source = source_path.read_text(encoding="utf-8")
    transformed = source.replace("G77_256FC", identity_namespace_prefix)
    transformed = transformed.replace("WRONG_ATTEMPT", "WRONG_PROVENANCE")
    transformed = transformed.replace("wrong_attempt", "wrong_provenance")
    exact_replacements = {
        'wrong_value["attempt_identity"] = WRONG_PROVENANCE_ID': (
            'wrong_value["provenance_identity"] = WRONG_PROVENANCE_ID'
        ),
        'denial_error == "operational Human act attempt_identity binding is invalid"': (
            'denial_error == "operational Human act input_record_identity binding is invalid"'
        ),
        'differing_fields == ["attempt_identity", "record_identity"]': (
            'differing_fields == ["provenance_identity", "record_identity"]'
        ),
        '"semantic_mutation_field": "attempt_identity"': (
            '"semantic_mutation_field": "provenance_identity"'
        ),
        '"isolated_mutation_fields": ["attempt_identity", "record_identity"]': (
            '"isolated_mutation_fields": ["provenance_identity", "record_identity"]'
        ),
    }
    for old, new in exact_replacements.items():
        if transformed.count(old) != 1:
            raise WrongProvenanceAdapterError(
                "FC_FK_SPECIALIZATION_PRECONDITION_INVALID__" + old
            )
        transformed = transformed.replace(old, new)
    act_marker = (
        f'ACT_ID = "{identity_namespace_prefix}_EXACT_CURRENT_ONE_USE_'
        'HUMAN_OPERATIONAL_ACT_001"'
    )
    if transformed.count(act_marker) != 1:
        raise WrongProvenanceAdapterError("AUTHORIZED_PROVENANCE_ID_INSERTION_FAILED")
    transformed = transformed.replace(
        act_marker,
        (
            f'AUTHORIZED_PROVENANCE_ID = "{identity_namespace_prefix}_'
            'AUTHENTICATED_FA_EM_CD_PROVENANCE_V1"\n' + act_marker
        ),
    )
    semantic_evidence_replacements = {
        '"authorized_attempt_identity": AUTHORIZED_ATTEMPT_ID,': (
            '"authorized_provenance_identity": AUTHORIZED_PROVENANCE_ID,'
        ),
        '"supplied_attempt_identity": WRONG_PROVENANCE_ID,': (
            '"supplied_provenance_identity": WRONG_PROVENANCE_ID,'
        ),
    }
    for old, new in semantic_evidence_replacements.items():
        if transformed.count(old) != 2:
            raise WrongProvenanceAdapterError(
                "FC_FK_SEMANTIC_EVIDENCE_PRECONDITION_INVALID__" + old
            )
        transformed = transformed.replace(old, new)
    forbidden = (
        'wrong_value["attempt_identity"] = WRONG_PROVENANCE_ID',
        '"semantic_mutation_field": "attempt_identity"',
        "WRONG_ATTEMPT",
    )
    if any(token in transformed for token in forbidden):
        raise WrongProvenanceAdapterError(
            "WRONG_ATTEMPT_SEMANTIC_LEAK_IN_SPECIALIZATION"
        )
    if transformed.count(
        'wrong_value["provenance_identity"] = WRONG_PROVENANCE_ID'
    ) != 1:
        raise WrongProvenanceAdapterError("WRONG_PROVENANCE_MUTATION_NOT_EXACTLY_ONCE")
    if '"supplied_attempt_identity": WRONG_PROVENANCE_ID' in transformed:
        raise WrongProvenanceAdapterError(
            "WRONG_PROVENANCE_EVIDENCE_MISLABELED_AS_ATTEMPT"
        )
    compile(transformed, str(source_path), "exec")
    return transformed


def load_guest_runtime_namespace(
    repository_root: Path = GUEST_REPOSITORY_ROOT,
    context_path: Path = GUEST_CONTEXT_PATH,
) -> dict[str, Any]:
    """Load the sealed context and instantiate the exact specialization."""

    root = repository_root.resolve()
    context_owner_path = root / (
        ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
        "sapianta_fresh_operation_context_v1.py"
    )
    context_owner = _load_module(
        context_owner_path, "g77_256ia_guest_context_owner"
    )
    context = context_owner.load_context(context_path, repository_root=root)
    if context_owner.operation_vector(context["generation_identity"]) != (
        "WRONG_PROVENANCE"
    ):
        raise WrongProvenanceAdapterError(
            "SEALED_CONTEXT_VECTOR_IS_NOT_WRONG_PROVENANCE"
        )
    source = specialize_fc_runtime_source(
        repository_root=root,
        identity_namespace_prefix=context["identity_namespace_prefix"],
    )
    namespace: dict[str, Any] = {
        "__name__": "sapianta_context_bound_wrong_provenance_specialization_v1",
        "__file__": str(root / FC_ADAPTER_RELATIVE_PATH),
        "__package__": None,
    }
    exec(compile(source, namespace["__file__"], "exec"), namespace)
    if namespace.get("GENERATION_ID") != context["generation_identity"]:
        raise WrongProvenanceAdapterError(
            "WRONG_PROVENANCE_GENERATION_SPECIALIZATION_FAILED"
        )
    return namespace


def main() -> int:
    """Use the existing FC/FK/ER runtime with the sealed strategy."""

    namespace = load_guest_runtime_namespace()
    return int(namespace["main"]())


if __name__ == "__main__":
    raise SystemExit(main())
