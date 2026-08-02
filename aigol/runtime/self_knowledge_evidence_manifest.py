"""Authenticated, fixed-input evidence manifest for Self Knowledge Runtime.

This module defines no query, Conversation, provider, Worker, replay-write, or
repository-discovery behavior.  It builds and verifies one explicit inventory
of repository-relative evidence paths introduced by G65-02.
"""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from aigol.runtime.models import FailClosedRuntimeError


SELF_KNOWLEDGE_EVIDENCE_MANIFEST_V1 = "SELF_KNOWLEDGE_EVIDENCE_MANIFEST_V1"
SELF_KNOWLEDGE_EVIDENCE_MANIFEST_VERSION = "G65_02_SELF_KNOWLEDGE_EVIDENCE_MANIFEST_V1"
SELF_KNOWLEDGE_EVIDENCE_MANIFEST_CONTRACT = "G65_01_SELF_KNOWLEDGE_ARCHITECTURE_CERTIFIED"
SELF_KNOWLEDGE_EVIDENCE_MANIFEST_PATH = (
    ".github/governance/manifests/SELF_KNOWLEDGE_EVIDENCE_MANIFEST_V1.json"
)
SOURCE_DIGEST_ALGORITHM = "SHA-256"

REQUIRED_SOURCE_CLASSES = (
    "CAPABILITY_REGISTRY",
    "CERTIFIED_HISTORY",
    "CONSTITUTION",
    "ENFORCEMENT_AND_LINEAGE",
    "GOVERNANCE_STATE",
    "KNOWN_LIMITATION",
    "OWNER_AND_BOUNDARY",
)

_MANIFEST_FIELDS = frozenset(
    {
        "artifact_type",
        "manifest_version",
        "manifest_contract",
        "constitutional_baseline",
        "self_knowledge_architecture_verdict",
        "source_digest_algorithm",
        "required_source_classes",
        "sources",
        "manifest_hash",
    }
)
_SOURCE_FIELDS = frozenset(
    {
        "source_id",
        "source_class",
        "path",
        "sha256",
        "schema_or_section_identifier",
        "authority_class",
        "required",
    }
)

# This is an allowlist, not a discovery pattern.  It is deliberately sorted
# by (source_class, source_id, path) and must change only through a governed
# manifest version update.
_SOURCE_DEFINITIONS = (
    (
        "CAPABILITY_REGISTRY",
        "PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_RUNTIME",
        "aigol/runtime/platform_capability_certification_registry.py",
        "CapabilityCertificationRecord",
        "GOVERNED_METADATA",
    ),
    (
        "CAPABILITY_REGISTRY",
        "PLATFORM_CORE_CAPABILITY_REGISTRY_MANIFEST",
        ".github/governance/manifests/PLATFORM_CORE_CAPABILITY_REGISTRY_V1.json",
        "PLATFORM_CORE_CAPABILITY_REGISTRY_V1",
        "CANONICAL_MANIFEST",
    ),
    (
        "CERTIFIED_HISTORY",
        "G64_01_CLOSURE_AUDIT",
        "docs/governance/G64_01_CONSTITUTIONAL_GOVERNANCE_CLOSURE_AUDIT_REPORT_V1.md",
        "G64_01_CONSTITUTIONAL_GOVERNANCE_CLOSURE_AUDIT_REPORT_V1",
        "CERTIFIED_G48_EVIDENCE",
    ),
    (
        "CERTIFIED_HISTORY",
        "G64_02_REPAIR_SEQUENCE",
        "docs/governance/G64_02_CONSTITUTIONAL_GOVERNANCE_CLOSURE_REPAIR_SEQUENCING_REPORT_V1.md",
        "G64_02_CONSTITUTIONAL_GOVERNANCE_CLOSURE_REPAIR_SEQUENCING_REPORT_V1",
        "CERTIFIED_G48_EVIDENCE",
    ),
    (
        "CERTIFIED_HISTORY",
        "G64_03_REUSE_PROOF_DESIGN",
        "docs/governance/G64_03_CONSTITUTIONAL_REUSE_PROOF_PRODUCTION_INTEGRATION_DESIGN_REPORT_V1.md",
        "G64_03_CONSTITUTIONAL_REUSE_PROOF_PRODUCTION_INTEGRATION_DESIGN_REPORT_V1",
        "CERTIFIED_G48_EVIDENCE",
    ),
    (
        "CERTIFIED_HISTORY",
        "G64_04_REUSE_PROOF_IMPLEMENTATION",
        "docs/governance/G64_04_CONSTITUTIONAL_REUSE_PROOF_PRODUCTION_INTEGRATION_IMPLEMENTATION_REPORT_V1.md",
        "G64_04_CONSTITUTIONAL_REUSE_PROOF_PRODUCTION_INTEGRATION_IMPLEMENTATION_REPORT_V1",
        "CERTIFIED_G48_EVIDENCE",
    ),
    (
        "CERTIFIED_HISTORY",
        "G64_05_REVALIDATION",
        "docs/governance/G64_05_CONSTITUTIONAL_GOVERNANCE_REVALIDATION_REPORT_V1.md",
        "G64_05_CONSTITUTIONAL_GOVERNANCE_REVALIDATION_REPORT_V1",
        "CERTIFIED_G48_EVIDENCE",
    ),
    (
        "CERTIFIED_HISTORY",
        "G64_06_AICLI_LINEAGE",
        "docs/governance/G64_06_AICLI_POSITIVE_CONSTITUTIONAL_LINEAGE_INTEGRATION_IMPLEMENTATION_REPORT_V1.md",
        "G64_06_AICLI_POSITIVE_CONSTITUTIONAL_LINEAGE_INTEGRATION_IMPLEMENTATION_REPORT_V1",
        "CERTIFIED_G48_EVIDENCE",
    ),
    (
        "CERTIFIED_HISTORY",
        "G64_07_COMPLETION_GATE",
        "docs/governance/G64_07_CONSTITUTIONAL_CERTIFICATION_COMPLETION_GATE_IMPLEMENTATION_REPORT_V1.md",
        "G64_07_CONSTITUTIONAL_CERTIFICATION_COMPLETION_GATE_IMPLEMENTATION_REPORT_V1",
        "CERTIFIED_G48_EVIDENCE",
    ),
    (
        "CERTIFIED_HISTORY",
        "G64_08_HOOK_REPAIR",
        "docs/governance/G64_08_GOVERNANCE_HOOK_DRIFT_REPAIR_IMPLEMENTATION_REPORT_V1.md",
        "G64_08_GOVERNANCE_HOOK_DRIFT_REPAIR_IMPLEMENTATION_REPORT_V1",
        "CERTIFIED_G48_EVIDENCE",
    ),
    (
        "CERTIFIED_HISTORY",
        "G64_09_PROVIDER_OWNERSHIP",
        "docs/governance/G64_09_CONSTITUTIONAL_PROVIDER_OWNERSHIP_CONSOLIDATION_IMPLEMENTATION_REPORT_V1.md",
        "G64_09_CONSTITUTIONAL_PROVIDER_OWNERSHIP_CONSOLIDATION_IMPLEMENTATION_REPORT_V1",
        "CERTIFIED_G48_EVIDENCE",
    ),
    (
        "CERTIFIED_HISTORY",
        "G64_10_NEGATIVE_VALIDATION",
        "docs/governance/G64_10_REPOSITORY_WIDE_NEGATIVE_CONSTITUTIONAL_CLOSURE_VALIDATION_REPORT_V1.md",
        "G64_10_REPOSITORY_WIDE_NEGATIVE_CONSTITUTIONAL_CLOSURE_VALIDATION_REPORT_V1",
        "CERTIFIED_G48_EVIDENCE",
    ),
    (
        "CERTIFIED_HISTORY",
        "G64_11_FINAL_CLOSURE",
        "docs/governance/G64_11_FINAL_CONSTITUTIONAL_GOVERNANCE_CLOSURE_AUDIT_REPORT_V1.md",
        "G64_11_FINAL_CONSTITUTIONAL_GOVERNANCE_CLOSURE_AUDIT_REPORT_V1",
        "CERTIFIED_G48_EVIDENCE",
    ),
    (
        "CERTIFIED_HISTORY",
        "G65_01_SELF_KNOWLEDGE_ARCHITECTURE",
        "docs/governance/G65_01_SELF_KNOWLEDGE_ARCHITECTURE_REPORT_V1.md",
        "G65_01_SELF_KNOWLEDGE_ARCHITECTURE_REPORT_V1",
        "CERTIFIED_G48_EVIDENCE",
    ),
    (
        "CONSTITUTION",
        "CANONICAL_LAYER_MODEL",
        "docs/governance/CANONICAL_LAYER_MODEL.md",
        "CANONICAL_LAYER_MODEL",
        "CANONICAL_CONSTITUTION",
    ),
    (
        "CONSTITUTION",
        "CONSTITUTIONAL_ARCHITECTURE_SPEC",
        "docs/governance/CONSTITUTIONAL_ARCHITECTURE_SPEC_V1.md",
        "CONSTITUTIONAL_ARCHITECTURE_SPEC_V1",
        "CANONICAL_CONSTITUTION",
    ),
    (
        "CONSTITUTION",
        "CONSTITUTIONAL_INVARIANTS",
        "docs/governance/CONSTITUTIONAL_INVARIANTS.md",
        "CONSTITUTIONAL_INVARIANTS",
        "CANONICAL_CONSTITUTION",
    ),
    (
        "CONSTITUTION",
        "STABLE_SUBSTRATE_DECLARATION",
        "docs/governance/STABLE_SUBSTRATE_DECLARATION_V1.md",
        "STABLE_SUBSTRATE_DECLARATION_V1",
        "CANONICAL_CONSTITUTION",
    ),
    (
        "ENFORCEMENT_AND_LINEAGE",
        "GOVERNANCE_ENFORCEMENT_HIERARCHY",
        "docs/governance/GOVERNANCE_ENFORCEMENT_HIERARCHY.md",
        "GOVERNANCE_ENFORCEMENT_HIERARCHY",
        "CANONICAL_CONSTITUTION",
    ),
    (
        "ENFORCEMENT_AND_LINEAGE",
        "GOVERNANCE_LINEAGE_MODEL",
        "docs/governance/GOVERNANCE_LINEAGE_MODEL.md",
        "GOVERNANCE_LINEAGE_MODEL",
        "CANONICAL_CONSTITUTION",
    ),
    (
        "GOVERNANCE_STATE",
        "G64_08_CONFORMANCE_EVIDENCE",
        "docs/governance/G64_08_GOVERNANCE_HOOK_DRIFT_REPAIR_IMPLEMENTATION_REPORT_V1.md",
        "G64_08_GOVERNANCE_HOOK_DRIFT_REPAIR_IMPLEMENTATION_REPORT_V1",
        "CERTIFIED_G48_EVIDENCE",
    ),
    (
        "GOVERNANCE_STATE",
        "SYSTEM_STATE",
        "runtime/governance/master/SYSTEM_STATE.md",
        "SYSTEM_STATE",
        "DOCUMENTATION_ONLY",
    ),
    (
        "KNOWN_LIMITATION",
        "G64_11_RESIDUAL_RISKS",
        "docs/governance/G64_11_FINAL_CONSTITUTIONAL_GOVERNANCE_CLOSURE_AUDIT_REPORT_V1.md",
        "G64_11_REMAINING_RISKS",
        "CERTIFIED_G48_EVIDENCE",
    ),
    (
        "KNOWN_LIMITATION",
        "GOVERNANCE_LINEAGE_LIMITATIONS",
        "docs/governance/GOVERNANCE_LINEAGE_MODEL.md",
        "GOVERNANCE_LINEAGE_MODEL_LIMITATIONS",
        "CANONICAL_CONSTITUTION",
    ),
    (
        "OWNER_AND_BOUNDARY",
        "CONVERSATION_NON_AUTHORITY_VALIDATOR",
        "aigol/runtime/platform_core_conversation_interpreter_proposal_runtime_v2.py",
        "PLATFORM_CORE_CONVERSATION_INTERPRETER_PROPOSAL_RUNTIME_V2",
        "RUNTIME_ENFORCED",
    ),
    (
        "OWNER_AND_BOUNDARY",
        "G64_11_OWNER_BOUNDARIES",
        "docs/governance/G64_11_FINAL_CONSTITUTIONAL_GOVERNANCE_CLOSURE_AUDIT_REPORT_V1.md",
        "G64_11_RESPONSIBILITY_BOUNDARIES",
        "CERTIFIED_G48_EVIDENCE",
    ),
)


def build_self_knowledge_evidence_manifest(repository_root: str | Path) -> dict[str, Any]:
    """Build the one deterministic V1 manifest from the fixed allowlist."""

    root = _repository_root(repository_root)
    sources = [
        {
            "source_id": source_id,
            "source_class": source_class,
            "path": path,
            "sha256": _source_digest(root, path),
            "schema_or_section_identifier": schema_or_section_identifier,
            "authority_class": authority_class,
            "required": True,
        }
        for (
            source_class,
            source_id,
            path,
            schema_or_section_identifier,
            authority_class,
        ) in _canonical_source_definitions()
    ]
    manifest = {
        "artifact_type": SELF_KNOWLEDGE_EVIDENCE_MANIFEST_V1,
        "manifest_version": SELF_KNOWLEDGE_EVIDENCE_MANIFEST_VERSION,
        "manifest_contract": SELF_KNOWLEDGE_EVIDENCE_MANIFEST_CONTRACT,
        "constitutional_baseline": "CONSTITUTIONAL_GOVERNANCE_CLOSED",
        "self_knowledge_architecture_verdict": "SELF_KNOWLEDGE_ARCHITECTURE_CERTIFIED",
        "source_digest_algorithm": SOURCE_DIGEST_ALGORITHM,
        "required_source_classes": list(REQUIRED_SOURCE_CLASSES),
        "sources": sources,
    }
    manifest["manifest_hash"] = _canonical_digest(manifest)
    return manifest


def validate_self_knowledge_evidence_manifest(
    manifest: dict[str, Any],
    repository_root: str | Path,
) -> dict[str, Any]:
    """Validate a V1 manifest and all fixed-source SHA-256 bindings."""

    root = _repository_root(repository_root)
    if not isinstance(manifest, dict) or set(manifest) != _MANIFEST_FIELDS:
        _fail("manifest schema is invalid")
    _require_exact_header(manifest)
    sources = manifest["sources"]
    if not isinstance(sources, list):
        _fail("manifest sources must be a list")
    expected = build_self_knowledge_evidence_manifest(root)
    if sources != expected["sources"]:
        _fail("manifest source inventory or digest binding is invalid")
    expected_hash = _canonical_digest({key: value for key, value in manifest.items() if key != "manifest_hash"})
    if manifest["manifest_hash"] != expected_hash:
        _fail("manifest hash mismatch")
    if manifest["manifest_hash"] != expected["manifest_hash"]:
        _fail("manifest version binding is stale")
    return deepcopy(manifest)


def self_knowledge_evidence_manifest_source_paths() -> tuple[str, ...]:
    """Return the explicit V1 allowlist in canonical source-record order."""

    return tuple(definition[2] for definition in _canonical_source_definitions())


def _canonical_source_definitions() -> tuple[tuple[str, str, str, str, str], ...]:
    """Return the static inventory in its required canonical order."""

    return tuple(sorted(_SOURCE_DEFINITIONS, key=lambda item: (item[0], item[1], item[2])))


def _require_exact_header(manifest: dict[str, Any]) -> None:
    expected_header = {
        "artifact_type": SELF_KNOWLEDGE_EVIDENCE_MANIFEST_V1,
        "manifest_version": SELF_KNOWLEDGE_EVIDENCE_MANIFEST_VERSION,
        "manifest_contract": SELF_KNOWLEDGE_EVIDENCE_MANIFEST_CONTRACT,
        "constitutional_baseline": "CONSTITUTIONAL_GOVERNANCE_CLOSED",
        "self_knowledge_architecture_verdict": "SELF_KNOWLEDGE_ARCHITECTURE_CERTIFIED",
        "source_digest_algorithm": SOURCE_DIGEST_ALGORITHM,
        "required_source_classes": list(REQUIRED_SOURCE_CLASSES),
    }
    for field, expected_value in expected_header.items():
        if manifest.get(field) != expected_value:
            _fail(f"manifest {field} is invalid")


def _repository_root(repository_root: str | Path) -> Path:
    root = Path(repository_root)
    if not root.is_dir():
        _fail("repository root is invalid")
    return root.resolve()


def _source_digest(root: Path, relative_path: str) -> str:
    path = _resolve_allowlisted_path(root, relative_path)
    if not path.is_file():
        _fail("manifest source is missing")
    return f"sha256:{sha256(path.read_bytes()).hexdigest()}"


def _resolve_allowlisted_path(root: Path, relative_path: str) -> Path:
    if relative_path not in self_knowledge_evidence_manifest_source_paths():
        _fail("manifest source path is not allowlisted")
    candidate = (root / relative_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        _fail("manifest source path escapes repository root")
    return candidate


def _canonical_digest(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return f"sha256:{sha256(encoded).hexdigest()}"


def _fail(message: str) -> None:
    raise FailClosedRuntimeError(f"SELF_KNOWLEDGE_EVIDENCE_MANIFEST_INVALID: {message}")


__all__ = [
    "REQUIRED_SOURCE_CLASSES",
    "SELF_KNOWLEDGE_EVIDENCE_MANIFEST_CONTRACT",
    "SELF_KNOWLEDGE_EVIDENCE_MANIFEST_PATH",
    "SELF_KNOWLEDGE_EVIDENCE_MANIFEST_V1",
    "SELF_KNOWLEDGE_EVIDENCE_MANIFEST_VERSION",
    "SOURCE_DIGEST_ALGORITHM",
    "build_self_knowledge_evidence_manifest",
    "self_knowledge_evidence_manifest_source_paths",
    "validate_self_knowledge_evidence_manifest",
]
