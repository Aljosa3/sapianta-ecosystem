#!/usr/bin/env python3
"""Thin, repository-only WRONG_PROVENANCE future-chain coherence validator.

It creates no request, presentation, authority, operation state, live binding,
or operational entry point. HZ remains the semantic owner; this module only
checks the existing FM/GN chain shape needed by a later post-commit generation.
"""

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import re
import sys
from types import ModuleType
from typing import Any


FM_CONTEXT_OWNER = Path(
    ".github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/"
    "sapianta_fresh_operation_context_v1.py"
)
VECTOR = "WRONG_PROVENANCE"
SELECTED_VECTOR = "P11-E05/NEGATIVE_AUTHORITY/WRONG_PROVENANCE"
TARGET_MUTATION = "provenance_identity"
DEPENDENT_RECOMPUTATION = "record_identity"
HEX_64 = re.compile(r"^[0-9a-f]{64}$")


class WrongProvenanceMaterializationError(ValueError):
    """Fail-closed future-chain coherence rejection."""


def _load_module(path: Path, identity: str) -> ModuleType:
    specification = importlib.util.spec_from_file_location(identity, path)
    if specification is None or specification.loader is None:
        raise WrongProvenanceMaterializationError("FM_CONTEXT_OWNER_IMPORT_FAILED")
    module = importlib.util.module_from_spec(specification)
    sys.modules[identity] = module
    specification.loader.exec_module(module)
    return module


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise WrongProvenanceMaterializationError(code)


def validate_future_materialization_chain(
    *,
    repository_root: Path,
    candidate_bytes: bytes,
    candidate_semantics: dict[str, Any],
    context: dict[str, Any],
    request_binding: dict[str, Any],
    presentation_binding: dict[str, Any],
) -> dict[str, Any]:
    """Validate one synthetic future chain without materializing an artifact."""

    root = repository_root.resolve()
    owner = _load_module(root / FM_CONTEXT_OWNER, "g77_256ia_fm_context_owner")
    owner.validate_context(context, repository_root=root)
    _require(
        owner.operation_vector(context["generation_identity"]) == VECTOR,
        "CONTEXT_VECTOR_MISMATCH",
    )
    candidate_sha256 = hashlib.sha256(candidate_bytes).hexdigest()
    _require(bool(candidate_bytes), "CANDIDATE_BYTES_MISSING")
    _require(
        context["candidate_manifest_sha256"] == candidate_sha256,
        "CANDIDATE_CONTEXT_HASH_MISMATCH",
    )
    expected_semantics = {
        "selected_vector": SELECTED_VECTOR,
        "target_mutation": TARGET_MUTATION,
        "dependent_recomputation": DEPENDENT_RECOMPUTATION,
        "semantic_mutation_count": 1,
        "unrelated_mutation_count": 0,
        "authoritative_provenance_resolution": (
            "VERIFIED__UNIQUE_EXISTING_PROTECTED_OWNER"
        ),
        "provenance_specific_comparison_reached": False,
    }
    _require(
        candidate_semantics == expected_semantics,
        "WRONG_PROVENANCE_CANDIDATE_SEMANTICS_INVALID",
    )
    expected_request = {
        "authorized_vector_requested": VECTOR,
        "generation_identity": context["generation_identity"],
        "candidate_sha256": candidate_sha256,
        "context_sha256": context["context_sha256"],
        "canonical_argv_sha256": context["canonical_argv_sha256"],
        "request_is_authority": False,
    }
    _require(request_binding == expected_request, "REQUEST_CONTEXT_CHAIN_INVALID")
    expected_presentation = {
        "AUTHORIZED_VECTOR_REQUESTED": VECTOR,
        "GENERATION_ID": context["generation_identity"],
        "CANDIDATE_SHA256": candidate_sha256,
        "CONTEXT_SHA256": context["context_sha256"],
        "CANONICAL_ARGV_SHA256": context["canonical_argv_sha256"],
    }
    _require(
        presentation_binding == expected_presentation,
        "PRESENTATION_REQUEST_CHAIN_INVALID",
    )
    for digest in (
        candidate_sha256,
        context["context_sha256"],
        context["canonical_argv_sha256"],
    ):
        _require(
            isinstance(digest, str) and HEX_64.fullmatch(digest) is not None,
            "CHAIN_HASH_MALFORMED",
        )
    return {
        "schema_id": (
            "G77_256IA_WRONG_PROVENANCE_PREAUTHORIZATION_BINDING_DESIGN_V1"
        ),
        "vector": VECTOR,
        "candidate_context_argv_presentation_chain": "VERIFIED",
        "request_created": False,
        "presentation_created": False,
        "human_operational_authority": 0,
        "operation_attempt": 0,
        "post_commit_rebind_required": True,
        "preoperational_readiness": "NOT_PROVEN",
    }


if __name__ == "__main__":
    raise SystemExit("repository-only binding validator; no materialization entry point")
