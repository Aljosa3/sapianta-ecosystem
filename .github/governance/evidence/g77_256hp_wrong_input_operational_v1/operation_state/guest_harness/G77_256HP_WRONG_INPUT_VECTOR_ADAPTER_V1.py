#!/usr/bin/env python3
"""Bounded WRONG_INPUT adapter for the existing FM guest/P11 boundary.

This module owns no launcher, authority, P11 behavior, or terminal reducer.  It
authenticates and invokes the committed GY mutation owner, then packages those
exact canonical bytes in the existing custody request type.  HA validates this
construction statically and never calls ``claim_and_invoke_once``.
HA grants no authority and performs no operation.
"""

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys
from types import ModuleType
from typing import Any


GY_PRODUCER_RELATIVE_PATH = Path(
    ".github/governance/evidence/g77_256gy_wrong_input_formalization_v1/producer/"
    "G77_256GY_WRONG_INPUT_REQUEST_AND_CANDIDATE_PRODUCER_V1.py"
)
GY_PRODUCER_SHA256 = (
    "643de4aa38264410c445107dfdd71b02334871021dd0b7d5ef8886a62e80cd22"
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
SELECTED_VECTOR = "P11-E05/NEGATIVE_AUTHORITY/WRONG_INPUT"
TARGET_MUTATION = "input_identity"
DEPENDENT_RECOMPUTATION = "record_identity"
SEMANTIC_MUTATION_COUNT = 1
EXPECTED_DIFFERING_FIELDS = ["input_identity", "record_identity"]
EXPECTED_DENIAL_REASON = (
    "operational Human act input_record_identity binding is invalid"
)
EXPECTED_DENIAL_BOUNDARY = (
    "D2_PRECLAIM_AUTHORITY_BINDING_VALIDATION_BEFORE_PRECLAIM_LEDGER_APPEND_"
    "CLAIM_ENTRY_INVOCATION_OR_EFFECT"
)


class WrongInputAdapterError(RuntimeError):
    """Fail-closed static adapter construction error."""


def _sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_module(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise WrongInputAdapterError("WRONG_INPUT_OWNER_IMPORT_FAILED")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def load_wrong_input_owner(repository_root: Path) -> ModuleType:
    """Authenticate the committed GY producer before reuse."""

    root = repository_root.resolve()
    path = root / GY_PRODUCER_RELATIVE_PATH
    if path.is_symlink() or not path.is_file():
        raise WrongInputAdapterError("WRONG_INPUT_OWNER_PATH_INVALID")
    if _sha256_path(path) != GY_PRODUCER_SHA256:
        raise WrongInputAdapterError("WRONG_INPUT_OWNER_HASH_MISMATCH")
    return _load_module(path, "g77_256ha_committed_gy_wrong_input_owner")


def construct_wrong_input_payload(
    *,
    repository_root: Path,
    authorized_input_canonical_bytes: bytes,
    wrong_input_identity: str,
    request_identity: str,
) -> dict[str, Any]:
    """Return only the committed GY mutation and its canonical P11 payload."""

    owner = load_wrong_input_owner(repository_root)
    request = owner.produce_wrong_input_request(
        repository_root=repository_root,
        authorized_input_canonical_bytes=authorized_input_canonical_bytes,
        wrong_input_identity=wrong_input_identity,
        request_identity=request_identity,
    )
    required = {
        "selected_vector": SELECTED_VECTOR,
        "target_mutated_coordinate": TARGET_MUTATION,
        "dependent_recomputation_fields": [DEPENDENT_RECOMPUTATION],
        "semantic_mutation_count": SEMANTIC_MUTATION_COUNT,
        "differing_input_fields": EXPECTED_DIFFERING_FIELDS,
        "expected_denial_boundary": EXPECTED_DENIAL_BOUNDARY,
        "expected_error_reason": EXPECTED_DENIAL_REASON,
        "request_is_authority": False,
        "request_is_operational_execution": False,
    }
    for field, expected in required.items():
        if request.get(field) != expected:
            raise WrongInputAdapterError(f"GY_SEMANTIC_BINDING_DRIFT__{field}")
    canonical_payload = request.get("supplied_input_canonical_utf8")
    if not isinstance(canonical_payload, str):
        raise WrongInputAdapterError("GY_CANONICAL_PAYLOAD_ABSENT")
    return {
        "schema_id": "G77_256HA_WRONG_INPUT_GUEST_ADAPTER_PROJECTION_V1",
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
    *,
    repository_root: Path,
    authorized_input_canonical_bytes: bytes,
    wrong_input_identity: str,
    request_identity: str,
) -> Any:
    """Construct the existing request type without entering the P11 consumer."""

    root = repository_root.resolve()
    tests_root = root / "tests"
    sys.path.insert(0, str(tests_root))
    try:
        from p11_da_custody_process_v1 import CustodyOperation, CustodyRequest
    finally:
        sys.path.pop(0)
    projection = construct_wrong_input_payload(
        repository_root=root,
        authorized_input_canonical_bytes=authorized_input_canonical_bytes,
        wrong_input_identity=wrong_input_identity,
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
    """Derive the WRONG_INPUT runtime adapter from the hash-bound FC/FK owner.

    The transformation is closed and count-checked. It changes the case/vector
    vocabulary and the single request mutation coordinate; it does not alter
    P11, authority, CHE, counter, checkout, or launcher implementations.
    """

    source_path = repository_root.resolve() / FC_ADAPTER_RELATIVE_PATH
    if source_path.is_symlink() or not source_path.is_file():
        raise WrongInputAdapterError("FC_FK_ADAPTER_PATH_INVALID")
    if _sha256_path(source_path) != FC_ADAPTER_SHA256:
        raise WrongInputAdapterError("FC_FK_ADAPTER_HASH_MISMATCH")
    if not identity_namespace_prefix.startswith("G77_256"):
        raise WrongInputAdapterError("IDENTITY_NAMESPACE_PREFIX_INVALID")
    source = source_path.read_text(encoding="utf-8")
    transformed = source.replace("G77_256FC", identity_namespace_prefix)
    transformed = transformed.replace("WRONG_ATTEMPT", "WRONG_INPUT")
    transformed = transformed.replace("wrong_attempt", "wrong_input")
    exact_replacements = {
        'wrong_value["attempt_identity"] = WRONG_INPUT_ID': (
            'wrong_value["input_identity"] = WRONG_INPUT_ID'
        ),
        'denial_error == "operational Human act attempt_identity binding is invalid"': (
            'denial_error == "operational Human act input_record_identity binding is invalid"'
        ),
        'differing_fields == ["attempt_identity", "record_identity"]': (
            'differing_fields == ["input_identity", "record_identity"]'
        ),
        '"semantic_mutation_field": "attempt_identity"': (
            '"semantic_mutation_field": "input_identity"'
        ),
        '"isolated_mutation_fields": ["attempt_identity", "record_identity"]': (
            '"isolated_mutation_fields": ["input_identity", "record_identity"]'
        ),
    }
    for old, new in exact_replacements.items():
        if transformed.count(old) != 1:
            raise WrongInputAdapterError(
                "FC_FK_SPECIALIZATION_PRECONDITION_INVALID__" + old
            )
        transformed = transformed.replace(old, new)
    forbidden = (
        'wrong_value["attempt_identity"] = WRONG_INPUT_ID',
        '"semantic_mutation_field": "attempt_identity"',
        "WRONG_ATTEMPT",
    )
    if any(token in transformed for token in forbidden):
        raise WrongInputAdapterError("WRONG_ATTEMPT_SEMANTIC_LEAK_IN_SPECIALIZATION")
    if transformed.count('wrong_value["input_identity"] = WRONG_INPUT_ID') != 1:
        raise WrongInputAdapterError("WRONG_INPUT_MUTATION_NOT_EXACTLY_ONCE")
    compile(transformed, str(source_path), "exec")
    return transformed


def load_guest_runtime_namespace(
    repository_root: Path = GUEST_REPOSITORY_ROOT,
    context_path: Path = GUEST_CONTEXT_PATH,
) -> dict[str, Any]:
    """Load the sealed context and instantiate the exact runtime specialization."""

    root = repository_root.resolve()
    context_owner_path = root / (
        ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
        "sapianta_fresh_operation_context_v1.py"
    )
    context_owner = _load_module(context_owner_path, "g77_256ha_guest_context_owner")
    context = context_owner.load_context(context_path, repository_root=root)
    if context_owner.operation_vector(context["generation_identity"]) != "WRONG_INPUT":
        raise WrongInputAdapterError("SEALED_CONTEXT_VECTOR_IS_NOT_WRONG_INPUT")
    source = specialize_fc_runtime_source(
        repository_root=root,
        identity_namespace_prefix=context["identity_namespace_prefix"],
    )
    namespace: dict[str, Any] = {
        "__name__": "sapianta_context_bound_wrong_input_specialization_v1",
        "__file__": str(root / FC_ADAPTER_RELATIVE_PATH),
        "__package__": None,
    }
    exec(compile(source, namespace["__file__"], "exec"), namespace)
    if namespace.get("GENERATION_ID") != context["generation_identity"]:
        raise WrongInputAdapterError("WRONG_INPUT_GENERATION_SPECIALIZATION_FAILED")
    return namespace


def main() -> int:
    """Use the existing FC/FK/ER runtime with the sealed WRONG_INPUT strategy."""

    namespace = load_guest_runtime_namespace()
    return int(namespace["main"]())


if __name__ == "__main__":
    raise SystemExit(main())
