#!/usr/bin/env python3
"""Bind EXPIRED to the existing FM/FC/ER/P11 route without owning authority.

The adapter authenticates JJ's fixed interval and P11 preclaim coordinate,
then derives one family-local specialization of the existing FC/ER route.
Importing or specializing this module creates no act and performs no operation.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType
from typing import Any


GUEST_REPOSITORY_ROOT = Path("/mnt/aigol")
GUEST_CONTEXT_PATH = Path("/mnt/g77-evidence/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json")
FM_CONTEXT_OWNER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
GUEST_PROJECTED_FM_CONTEXT_OWNER = Path(
    "/mnt/dp-harness/sapianta_fresh_operation_context_v1.py"
)
FC_ADAPTER = Path(
    ".github/governance/evidence/g77_256fc_wrong_attempt_operational_v1/harness/"
    "G77_256FC_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py"
)
FC_ADAPTER_SHA256 = "b2e9f72d6b35b2db0021bf9bf1223350f570d1eaecda3379a8af013c705aa770"
ER_HARNESS = Path(
    ".github/governance/evidence/g77_256er_p11_operational_v1/harness/"
    "G77_256ER_P11_OPERATIONAL_HARNESS_V1.py"
)
ER_HARNESS_SHA256 = "c6539d1cc60940b1999956965bff43923a270598a982cd19f976eadec0a93152"
JJ_REDUCTION = Path(
    ".github/governance/evidence/"
    "g77_256jj_expired_vector_deterministic_repository_formalization_v1/"
    "G77_256JJ_SPCE_TERMINAL_REPOSITORY_ONLY_REDUCTION_V1.json"
)
JJ_REDUCTION_SHA256 = "35af335dba0b3e2e2aa7b5ec244ddbc08ff9c8bbc6e7a2e49296a93daecec8d7"
JJ_TERMINAL = "A__EXPIRED_VECTOR_DETERMINISTIC_REPOSITORY_FORMALIZATION_VERIFIED"
VECTOR = "EXPIRED"
SELECTED_VECTOR = "P11-E05/NEGATIVE_AUTHORITY/EXPIRED"
SUBMISSION_TIME_UNIX_NS = 500
VALID_FROM_UNIX_NS = 100
VALID_UNTIL_UNIX_NS = 1000
PRECLAIM_TIME_UNIX_NS = 1000
EXPECTED_DENIAL = "one-use Human act expired before PRECLAIM"
EXPECTED_DENIAL_BOUNDARY = "BEFORE_P11_DA_OPERATIONAL_PRECLAIM_APPEND"


class ExpiredAdapterError(RuntimeError):
    """One fail-closed EXPIRED specialization error."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _load(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise ExpiredAdapterError(f"OWNER_IMPORT_FAILED__{identity}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def authenticate_expired_semantics(repository_root: Path) -> dict[str, Any]:
    """Authenticate JJ's sealed coordinates without accepting caller values."""

    path = repository_root.resolve() / JJ_REDUCTION
    if path.is_symlink() or not path.is_file() or _sha256(path) != JJ_REDUCTION_SHA256:
        raise ExpiredAdapterError("JJ_REDUCTION_BINDING_INVALID")
    envelope = json.loads(path.read_bytes())
    reduction = envelope.get("reduction")
    if not isinstance(reduction, dict):
        raise ExpiredAdapterError("JJ_REDUCTION_MISSING")
    if envelope.get("reduction_sha256") != hashlib.sha256(
        _canonical_bytes(reduction)
    ).hexdigest():
        raise ExpiredAdapterError("JJ_REDUCTION_SEAL_INVALID")
    if reduction.get("terminal") != JJ_TERMINAL:
        raise ExpiredAdapterError("JJ_TERMINAL_INVALID")
    coordinates = reduction.get("expired_semantic_model", {}).get(
        "temporal_coordinates"
    )
    expected = {
        "baseline_preclaim_time_unix_ns": SUBMISSION_TIME_UNIX_NS,
        "expired_preclaim_time_unix_ns": PRECLAIM_TIME_UNIX_NS,
        "valid_from_unix_ns": VALID_FROM_UNIX_NS,
        "valid_until_unix_ns": VALID_UNTIL_UNIX_NS,
    }
    if coordinates != expected:
        raise ExpiredAdapterError("JJ_COORDINATE_DRIFT")
    return expected


def specialize_er_harness(repository_root: Path) -> ModuleType:
    """Derive the fixed act interval while leaving observation clocks unchanged."""

    root = repository_root.resolve()
    authenticate_expired_semantics(root)
    path = root / ER_HARNESS
    if path.is_symlink() or not path.is_file() or _sha256(path) != ER_HARNESS_SHA256:
        raise ExpiredAdapterError("ER_HARNESS_BINDING_INVALID")
    source = path.read_text(encoding="utf-8")
    clock = (
        "    now = time.time_ns()\n"
        "    valid_from = now - 1_000_000_000\n"
        "    valid_until = now + 300_000_000_000\n"
    )
    fixed = (
        "    now = 500\n"
        "    valid_from = 100\n"
        "    valid_until = 1000\n"
    )
    if source.count(clock) != 1:
        raise ExpiredAdapterError("ER_VALIDITY_SPECIALIZATION_ANCHOR_INVALID")
    source = source.replace(clock, fixed)
    module = ModuleType("g77_256jr_expired_er_specialization")
    module.__file__ = str(path)
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


def specialize_fc_runtime_source(
    *, repository_root: Path, identity_namespace_prefix: str
) -> str:
    """Derive one EXPIRED strategy from the established FC family-local shell."""

    root = repository_root.resolve()
    authenticate_expired_semantics(root)
    source_path = root / FC_ADAPTER
    if source_path.is_symlink() or not source_path.is_file():
        raise ExpiredAdapterError("FC_ADAPTER_PATH_INVALID")
    if _sha256(source_path) != FC_ADAPTER_SHA256:
        raise ExpiredAdapterError("FC_ADAPTER_HASH_MISMATCH")
    if not identity_namespace_prefix.startswith("G77_256"):
        raise ExpiredAdapterError("IDENTITY_NAMESPACE_PREFIX_INVALID")
    source = source_path.read_text(encoding="utf-8")
    transformed = source.replace("G77_256FC", identity_namespace_prefix)
    transformed = transformed.replace("WRONG_ATTEMPT", "EXPIRED")
    transformed = transformed.replace("wrong_attempt", "expired")

    mutation = (
        "        wrong_value = dict(authorized_record)\n"
        "        wrong_value[\"record_identity\"] = \"\"\n"
        "        wrong_value[\"attempt_identity\"] = EXPIRED_ID\n"
        "        wrong_bytes = bind_record_identity(wrong_value)\n"
        "        wrong_record = validate_input_record_bytes(wrong_bytes)\n"
        "        differing_fields = sorted(\n"
        "            key for key in authorized_record\n"
        "            if authorized_record[key] != wrong_record[key]\n"
        "        )\n"
    )
    unchanged = (
        "        wrong_bytes = authorized_bytes\n"
        "        wrong_record = authorized_record\n"
        "        differing_fields = []\n"
    )
    if transformed.count(mutation) != 1:
        raise ExpiredAdapterError("FC_INPUT_IDENTITY_ANCHOR_INVALID")
    transformed = transformed.replace(mutation, unchanged)

    submission = (
        "            input_record_canonical_bytes=authorized_bytes,\n"
        "        )\n"
    )
    if transformed.count(submission) != 1:
        raise ExpiredAdapterError("FC_SUBMISSION_TIME_ANCHOR_INVALID")
    transformed = transformed.replace(
        submission,
        "            input_record_canonical_bytes=authorized_bytes,\n"
        "            now_unix_ns=SUBMISSION_TIME_UNIX_NS,\n"
        "        )\n",
    )

    checks = {
        'denial_error == "operational Human act attempt_identity binding is invalid",': (
            'denial_error == "one-use Human act expired before PRECLAIM",'
        ),
        'differing_fields == ["attempt_identity", "record_identity"],': (
            "differing_fields == [],"
        ),
        'after.state.value == "AVAILABLE",': 'after.state.value == "EXPIRED",',
        "after.revision == 0,": "after.revision == 1,",
        "owner_after == owner_before,": (
            "len(owner_after) == len(owner_before) + 1,"
        ),
        '"claim_attempted": False,': '"claim_attempted": True,',
        '"owner_revision_files_unchanged": owner_after == owner_before,': (
            '"owner_revision_files_unchanged": False,'
        ),
    }
    for old, new in checks.items():
        if transformed.count(old) < 1:
            raise ExpiredAdapterError("FC_EXPIRED_REDUCTION_ANCHOR_INVALID")
        transformed = transformed.replace(old, new, 1)

    required = (
        "now_unix_ns=SUBMISSION_TIME_UNIX_NS",
        'denial_error == "one-use Human act expired before PRECLAIM"',
        'after.state.value == "EXPIRED"',
        "after.revision == 1",
        "differing_fields == []",
    )
    if not all(token in transformed for token in required):
        raise ExpiredAdapterError("FC_EXPIRED_SPECIALIZATION_INCOMPLETE")
    compile(transformed, str(source_path), "exec")
    return transformed


def load_guest_runtime_namespace(
    repository_root: Path = GUEST_REPOSITORY_ROOT,
    context_path: Path = GUEST_CONTEXT_PATH,
) -> dict[str, Any]:
    """Authenticate the sealed EXPIRED context and assemble the existing route."""

    root = repository_root.resolve()
    owner_path = (
        GUEST_PROJECTED_FM_CONTEXT_OWNER
        if root == GUEST_REPOSITORY_ROOT
        else root / FM_CONTEXT_OWNER
    )
    owner = _load(owner_path, "g77_256jr_guest_context_owner")
    context = owner.load_context(context_path, repository_root=root)
    if owner.operation_vector(context["generation_identity"]) != VECTOR:
        raise ExpiredAdapterError("SEALED_CONTEXT_VECTOR_IS_NOT_EXPIRED")
    if context["preclaim_temporal_binding"]["coordinate_unix_ns"] != PRECLAIM_TIME_UNIX_NS:
        raise ExpiredAdapterError("SEALED_PRECLAIM_COORDINATE_INVALID")
    source = specialize_fc_runtime_source(
        repository_root=root,
        identity_namespace_prefix=context["identity_namespace_prefix"],
    )
    namespace: dict[str, Any] = {
        "__name__": "sapianta_context_bound_expired_specialization_v1",
        "__file__": str(root / FC_ADAPTER),
        "__package__": None,
        "SUBMISSION_TIME_UNIX_NS": SUBMISSION_TIME_UNIX_NS,
    }
    exec(compile(source, namespace["__file__"], "exec"), namespace)
    if namespace.get("GENERATION_ID") != context["generation_identity"]:
        raise ExpiredAdapterError("EXPIRED_GENERATION_SPECIALIZATION_FAILED")
    namespace["load_er"] = lambda: specialize_er_harness(root)
    return namespace


def main() -> int:
    """Operational entry remains dormant until a later authorized generation."""

    namespace = load_guest_runtime_namespace()
    return int(namespace["main"]())


if __name__ == "__main__":
    raise SystemExit(main())
