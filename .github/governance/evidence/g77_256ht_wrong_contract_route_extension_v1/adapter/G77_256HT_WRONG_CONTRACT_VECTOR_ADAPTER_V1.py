#!/usr/bin/env python3
"""Bounded WRONG_CONTRACT adapter for the existing FM guest/P11 boundary.

The adapter owns no launcher, authority, P11 semantics, or production route.
It authenticates and reuses the committed HR mutation owner and derives the
existing FC/FK runtime specialization with one semantic mutation:
``contract_identity``. ``record_identity`` is recomputed only as its dependent
canonical identity. No Human act or unrelated input coordinate is changed.
"""

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys
from types import ModuleType
from typing import Any


HR_PRODUCER_RELATIVE_PATH = Path(
    ".github/governance/evidence/g77_256hr_wrong_contract_formalization_v1/"
    "producer/G77_256HR_WRONG_CONTRACT_VECTOR_PRODUCER_V1.py"
)
HR_PRODUCER_SHA256 = (
    "3a8e6a0bed06d748b9df50bec7aaeb93c059ec36214c997c8675a488c46d27c5"
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
SELECTED_VECTOR = "P11-E05/NEGATIVE_AUTHORITY/WRONG_CONTRACT"
TARGET_MUTATION = "contract_identity"
DEPENDENT_RECOMPUTATION = "record_identity"
SEMANTIC_MUTATION_COUNT = 1
EXPECTED_DIFFERING_FIELDS = ["contract_identity", "record_identity"]
EXPECTED_DENIAL_REASON = (
    "operational Human act input_record_identity binding is invalid"
)
EXPECTED_DENIAL_BOUNDARY = (
    "D2_PRECLAIM_AUTHORITY_BINDING_VALIDATION_BEFORE_PRECLAIM_LEDGER_APPEND_"
    "CLAIM_ENTRY_INVOCATION_OR_EFFECT"
)


class WrongContractAdapterError(RuntimeError):
    """Fail-closed adapter construction or specialization error."""


def _sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_module(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise WrongContractAdapterError("WRONG_CONTRACT_OWNER_IMPORT_FAILED")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def load_wrong_contract_owner(repository_root: Path) -> ModuleType:
    """Authenticate the committed HR producer before reuse."""

    path = repository_root.resolve() / HR_PRODUCER_RELATIVE_PATH
    if path.is_symlink() or not path.is_file():
        raise WrongContractAdapterError("WRONG_CONTRACT_OWNER_PATH_INVALID")
    if _sha256_path(path) != HR_PRODUCER_SHA256:
        raise WrongContractAdapterError("WRONG_CONTRACT_OWNER_HASH_MISMATCH")
    return _load_module(path, "g77_256ht_committed_hr_wrong_contract_owner")


def construct_wrong_contract_payload(
    *, repository_root: Path, wrong_contract_identity: str, request_identity: str
) -> dict[str, Any]:
    """Return the committed HR mutation as an existing P11 payload projection."""

    owner = load_wrong_contract_owner(repository_root)
    candidate = owner.produce_wrong_contract_vector(
        repository_root=repository_root,
        wrong_contract_identity=wrong_contract_identity,
    )
    required = {
        "selected_vector": SELECTED_VECTOR,
        "target_mutated_coordinate": TARGET_MUTATION,
        "dependent_recomputation_fields": [DEPENDENT_RECOMPUTATION],
        "semantic_mutation_count": SEMANTIC_MUTATION_COUNT,
        "differing_input_fields": EXPECTED_DIFFERING_FIELDS,
        "expected_denial_boundary": EXPECTED_DENIAL_BOUNDARY,
        "expected_error_reason": EXPECTED_DENIAL_REASON,
        "contract_specific_comparison_reached": False,
        "authority_created": False,
        "request_created": False,
        "operation_attempted": False,
    }
    for field, expected in required.items():
        if candidate.get(field) != expected:
            raise WrongContractAdapterError(f"HR_SEMANTIC_BINDING_DRIFT__{field}")
    canonical_payload = candidate.get("candidate_input_canonical_utf8")
    if not isinstance(canonical_payload, str):
        raise WrongContractAdapterError("HR_CANONICAL_PAYLOAD_ABSENT")
    return {
        "schema_id": "G77_256HT_WRONG_CONTRACT_GUEST_ADAPTER_PROJECTION_V1",
        "protocol_identity": "P11_DA_DISPOSABLE_LOCAL_IPC_V1",
        "operation": "CLAIM_AND_INVOKE_ONCE",
        "request_identity": request_identity,
        "canonical_payload_utf8": canonical_payload,
        "semantic_binding": required,
        "request_is_authority": False,
        "adapter_invoked_p11": False,
        "operational_execution_count": 0,
    }


def construct_existing_custody_request(
    *, repository_root: Path, wrong_contract_identity: str, request_identity: str
) -> Any:
    """Construct the existing request type without entering the P11 consumer."""

    root = repository_root.resolve()
    sys.path.insert(0, str(root / "tests"))
    try:
        from p11_da_custody_process_v1 import CustodyOperation, CustodyRequest
    finally:
        sys.path.pop(0)
    projection = construct_wrong_contract_payload(
        repository_root=root,
        wrong_contract_identity=wrong_contract_identity,
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
    """Derive the closed WRONG_CONTRACT strategy from the FC/FK runtime."""

    source_path = repository_root.resolve() / FC_ADAPTER_RELATIVE_PATH
    if source_path.is_symlink() or not source_path.is_file():
        raise WrongContractAdapterError("FC_FK_ADAPTER_PATH_INVALID")
    if _sha256_path(source_path) != FC_ADAPTER_SHA256:
        raise WrongContractAdapterError("FC_FK_ADAPTER_HASH_MISMATCH")
    if not identity_namespace_prefix.startswith("G77_256"):
        raise WrongContractAdapterError("IDENTITY_NAMESPACE_PREFIX_INVALID")
    source = source_path.read_text(encoding="utf-8")
    transformed = source.replace("G77_256FC", identity_namespace_prefix)
    transformed = transformed.replace("WRONG_ATTEMPT", "WRONG_CONTRACT")
    transformed = transformed.replace("wrong_attempt", "wrong_contract")
    exact_replacements = {
        'wrong_value["attempt_identity"] = WRONG_CONTRACT_ID': (
            'wrong_value["contract_identity"] = WRONG_CONTRACT_ID'
        ),
        'denial_error == "operational Human act attempt_identity binding is invalid"': (
            'denial_error == "operational Human act input_record_identity binding is invalid"'
        ),
        'differing_fields == ["attempt_identity", "record_identity"]': (
            'differing_fields == ["contract_identity", "record_identity"]'
        ),
        '"semantic_mutation_field": "attempt_identity"': (
            '"semantic_mutation_field": "contract_identity"'
        ),
        '"isolated_mutation_fields": ["attempt_identity", "record_identity"]': (
            '"isolated_mutation_fields": ["contract_identity", "record_identity"]'
        ),
    }
    for old, new in exact_replacements.items():
        if transformed.count(old) != 1:
            raise WrongContractAdapterError(
                "FC_FK_SPECIALIZATION_PRECONDITION_INVALID__" + old
            )
        transformed = transformed.replace(old, new)
    act_marker = f'ACT_ID = "{identity_namespace_prefix}_EXACT_CURRENT_ONE_USE_HUMAN_OPERATIONAL_ACT_001"'
    if transformed.count(act_marker) != 1:
        raise WrongContractAdapterError("AUTHORIZED_CONTRACT_ID_INSERTION_FAILED")
    transformed = transformed.replace(
        act_marker,
        (
            f'AUTHORIZED_CONTRACT_ID = "{identity_namespace_prefix}_E05_'
            'WRONG_CONTRACT_FAIL_CLOSED_CONTRACT_V1"\n' + act_marker
        ),
    )
    semantic_evidence_replacements = {
        '"authorized_attempt_identity": AUTHORIZED_ATTEMPT_ID,': (
            '"authorized_contract_identity": AUTHORIZED_CONTRACT_ID,'
        ),
        '"supplied_attempt_identity": WRONG_CONTRACT_ID,': (
            '"supplied_contract_identity": WRONG_CONTRACT_ID,'
        ),
    }
    for old, new in semantic_evidence_replacements.items():
        if transformed.count(old) != 2:
            raise WrongContractAdapterError(
                "FC_FK_SEMANTIC_EVIDENCE_PRECONDITION_INVALID__" + old
            )
        transformed = transformed.replace(old, new)
    forbidden = (
        'wrong_value["attempt_identity"] = WRONG_CONTRACT_ID',
        '"semantic_mutation_field": "attempt_identity"',
        "WRONG_ATTEMPT",
    )
    if any(token in transformed for token in forbidden):
        raise WrongContractAdapterError(
            "WRONG_ATTEMPT_SEMANTIC_LEAK_IN_SPECIALIZATION"
        )
    if transformed.count('wrong_value["contract_identity"] = WRONG_CONTRACT_ID') != 1:
        raise WrongContractAdapterError("WRONG_CONTRACT_MUTATION_NOT_EXACTLY_ONCE")
    if '"supplied_attempt_identity": WRONG_CONTRACT_ID' in transformed:
        raise WrongContractAdapterError("WRONG_CONTRACT_EVIDENCE_MISLABELED_AS_ATTEMPT")
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
        context_owner_path, "g77_256ht_guest_context_owner"
    )
    context = context_owner.load_context(context_path, repository_root=root)
    if context_owner.operation_vector(context["generation_identity"]) != "WRONG_CONTRACT":
        raise WrongContractAdapterError("SEALED_CONTEXT_VECTOR_IS_NOT_WRONG_CONTRACT")
    source = specialize_fc_runtime_source(
        repository_root=root,
        identity_namespace_prefix=context["identity_namespace_prefix"],
    )
    namespace: dict[str, Any] = {
        "__name__": "sapianta_context_bound_wrong_contract_specialization_v1",
        "__file__": str(root / FC_ADAPTER_RELATIVE_PATH),
        "__package__": None,
    }
    exec(compile(source, namespace["__file__"], "exec"), namespace)
    if namespace.get("GENERATION_ID") != context["generation_identity"]:
        raise WrongContractAdapterError(
            "WRONG_CONTRACT_GENERATION_SPECIALIZATION_FAILED"
        )
    return namespace


def main() -> int:
    """Use the existing FC/FK/ER runtime with the sealed strategy."""

    namespace = load_guest_runtime_namespace()
    return int(namespace["main"]())


if __name__ == "__main__":
    raise SystemExit(main())
