"""Deterministic Constitutional Reuse Proof Runtime for G63-05.

The runtime composes existing authenticated evidence owners and implements only
the G63-specific proof semantics identified by G63-04.  It does not discover
provider capabilities, authorize planning or execution, mutate repositories,
or replace Development Governance.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
from pathlib import Path
import re
import subprocess
from typing import Any

from aigol.runtime.capability_audit_runtime import (
    AIGOL_CAPABILITY_AUDIT_RUNTIME_VERSION,
    build_capability_matrix,
    detect_capabilities,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION,
    list_platform_capability_certifications,
    lookup_platform_capability_certification,
)
from aigol.runtime.platform_capability_composition_coverage import (
    COVERAGE_COMPLETE,
    NO_GAP_EXISTING_CAPABILITY_SUFFICIENT,
    PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_VERSION,
    discover_platform_capability_composition_coverage,
    validate_platform_capability_composition_coverage,
)
from aigol.runtime.platform_development_composition_plan import (
    DEVELOPMENT_COMPOSITION_PLAN_NO_IMPLEMENTATION_REQUIRED,
    compose_platform_development_plan,
    validate_platform_development_composition_plan,
)
from aigol.runtime.platform_core_project_services import (
    PLATFORM_CORE_HUMAN_INTENT_CAPABILITY_RESOLUTION_VERSION,
    PLATFORM_CORE_PROJECT_KNOWLEDGE_REUSE_VERSION,
    PLATFORM_CORE_PROJECT_SERVICES_VERSION,
    discover_candidate_capabilities,
    project_knowledge_context_from_workspace,
)
from aigol.runtime.platform_knowledge_runtime import (
    PLATFORM_KNOWLEDGE_RUNTIME_VERSION,
    query_platform_knowledge,
    validate_platform_knowledge_response,
)
from aigol.runtime.transport.serialization import replay_hash
from runtime.governance.governance_conformance_engine import run_conformance_check


CONSTITUTIONAL_REUSE_PROOF_RUNTIME_VERSION = (
    "G63_05_CONSTITUTIONAL_REUSE_PROOF_RUNTIME_V1"
)
RESPONSIBILITY_SIGNATURE_ARTIFACT_V1 = (
    "CONSTITUTIONAL_REUSE_PROOF_RESPONSIBILITY_SIGNATURE_V1"
)
REUSE_PROOF_INPUT_ARTIFACT_V1 = "CONSTITUTIONAL_REUSE_PROOF_INPUT_V1"
REUSE_PROOF_RESULT_ARTIFACT_V1 = "CONSTITUTIONAL_REUSE_PROOF_RESULT_V1"
REUSE_PROOF_G47_HANDOFF_ARTIFACT_V1 = (
    "CONSTITUTIONAL_REUSE_PROOF_G47_HANDOFF_V1"
)

PROOF_COMPLETE_FOR_EVOLUTION_PLANNING = "PROOF_COMPLETE_FOR_EVOLUTION_PLANNING"

REUSE = "REUSE"
EXTEND = "EXTEND"
CONSOLIDATE = "CONSOLIDATE"
CREATE_NEW = "CREATE_NEW"
DECISIONS = (REUSE, EXTEND, CONSOLIDATE, CREATE_NEW)

RESPONSIBILITY_FIELDS = (
    "semantic_responsibility",
    "inputs",
    "outputs",
    "state_and_persistence",
    "authority",
    "non_authorities",
    "boundary",
    "determinism",
    "evidence_and_replay",
    "activation_and_lifecycle",
)

SEARCH_EVIDENCE_CLASSES = (
    "CONSTITUTIONAL_GOVERNANCE",
    "PCBV31",
    "RUNTIME_API",
    "REGISTRY_ROUTING",
    "CALLERS_DYNAMIC_PATHS",
    "TEST_REPLAY_MIGRATION",
    "LEGACY_ALTERNATE",
    "GIT_HISTORY",
    "EXTERNAL_EFFECTS",
    "EXTERNAL_DYNAMIC_SOURCES",
)
SEARCH_STATUSES = frozenset({"SEARCHED", "NOT_APPLICABLE", "UNKNOWN_BLOCKED"})

MATURITY_STATES = frozenset(
    {
        "DECLARED",
        "CERTIFIED_METADATA",
        "RUNTIME_BOUND",
        "INVOKABLE",
        "EXECUTABLE",
        "EVIDENCE_PRODUCING",
        "TEST_ONLY",
        "EXPERIMENTAL",
        "DEPRECATED",
        "HISTORICAL_ONLY",
        "UNVERIFIED",
    }
)

EQUIVALENCE_DISPOSITIONS = frozenset(
    {
        "EXACT_EQUIVALENT",
        "SEMANTIC_EQUIVALENT_DIFFERENT_INTERFACE",
        "PARTIAL_OVERLAP",
        "COMPLEMENTARY_FRAGMENT",
        "AUTHORITY_INCOMPATIBLE",
        "DEPRECATED_ONLY",
        "UNAVAILABLE",
        "UNRELATED",
        "UNKNOWN_BLOCKED",
    }
)

COMPATIBILITY_DIMENSIONS = (
    "API",
    "SCHEMA",
    "BEHAVIOR",
    "AUTHORITY",
    "OWNERSHIP",
    "DEPENDENCY_DIRECTION",
    "REGISTRY_SELECTION",
    "PERSISTENCE",
    "REPLAY_EVIDENCE",
    "PROVIDER_NETWORK_PRIVACY",
    "WORKER_EXECUTION",
    "HUMAN_INTERACTION",
    "MIGRATION",
    "RELEASE",
    "CERTIFICATION_SCOPE",
)
COMPATIBILITY_RESULTS = frozenset(
    {
        "DIRECTLY_COMPATIBLE",
        "ADAPTER_COMPATIBLE",
        "VERSIONED_EXTENSION_REQUIRED",
        "INCOMPATIBLE",
        "UNKNOWN_BLOCKED",
    }
)

EXTENSION_RUNGS = (
    "CONFIGURATION_PROFILE_SELECTION",
    "DIRECT_PUBLIC_API_INTEGRATION",
    "REPRESENTATION_ADAPTER",
    "ADDITIVE_OWNER_SURFACE",
    "VERSIONED_OWNER_CONTRACT",
    "OWNER_SCOPED_COMPOSITION_CONSOLIDATION",
)
EXTENSION_RESULTS = frozenset({"FEASIBLE", "INFEASIBLE", "UNKNOWN_BLOCKED"})

DUPLICATE_TYPES = frozenset(
    {
        "EXACT_DUPLICATE",
        "FUNCTIONAL_DUPLICATE",
        "AUTHORITY_DUPLICATE",
        "REGISTRY_DUPLICATE",
        "ROUTING_DUPLICATE",
        "EVIDENCE_DUPLICATE",
        "COMPLEMENTARY_FRAGMENTATION",
        "SCOPED_NON_DUPLICATE",
        "HISTORICAL_OVERLAP",
    }
)
CONSOLIDATION_RESULTS = frozenset(
    {"FEASIBLE", "INFEASIBLE", "NOT_APPLICABLE", "UNKNOWN_BLOCKED"}
)

OWNERSHIP_ROLES = (
    "architectural_owner",
    "authority_owner",
    "implementation_owner",
    "state_owner",
    "registry_owner",
    "evidence_replay_owner",
    "lifecycle_owner",
    "human_owner",
)

EVOLUTION_FIELDS = (
    "existing_consumers_compatible",
    "defaults_unchanged",
    "schema_api_compatible",
    "authority_unchanged",
    "owner_unchanged",
    "state_replay_compatible",
    "registry_selection_unchanged",
    "rollback_without_migration",
)

BOUNDARY_FLAGS = {
    "development_governance_authority": True,
    "proof_evidence_only": True,
    "platform_core_authority_inherited": False,
    "capability_discovery_replaced": False,
    "repository_reconstruction_replaced": False,
    "registry_ownership_replaced": False,
    "project_services_replaced": False,
    "conversation_layer_modified": False,
    "replay_modified": False,
    "authorization_modified": False,
    "worker_modified": False,
    "provider_invoked": False,
    "worker_invoked": False,
    "execution_authorized": False,
    "planning_authorized": False,
    "repository_mutated": False,
    "new_registry_created": False,
}

_SHA1_PATTERN = re.compile(r"^[0-9a-f]{40}$")
_SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")

_OWNER_COMPOSITION_GOVERNING_SOURCES = (
    "docs/governance/G63_02_CONSTITUTIONAL_REUSE_PROOF_FRAMEWORK_REPORT_V1.md",
    "docs/governance/G63_04_CONSTITUTIONAL_REUSE_PROOF_RUNTIME_COMPOSITION_AUDIT_REPORT_V1.md",
    "docs/governance/G64_03_CONSTITUTIONAL_REUSE_PROOF_PRODUCTION_INTEGRATION_DESIGN_REPORT_V1.md",
)


def create_responsibility_signature(
    *,
    semantic_responsibility: str,
    inputs: list[str] | tuple[str, ...],
    outputs: list[str] | tuple[str, ...],
    state_and_persistence: str,
    authority: str,
    non_authorities: list[str] | tuple[str, ...],
    boundary: str,
    determinism: str,
    evidence_and_replay: str,
    activation_and_lifecycle: str,
) -> dict[str, Any]:
    """Create one canonical responsibility signature without proposing a component."""

    artifact = {
        "artifact_type": RESPONSIBILITY_SIGNATURE_ARTIFACT_V1,
        "runtime_version": CONSTITUTIONAL_REUSE_PROOF_RUNTIME_VERSION,
        "semantic_responsibility": _require_string(
            semantic_responsibility, "semantic_responsibility"
        ),
        "inputs": _canonical_strings(inputs, "inputs", require_nonempty=True),
        "outputs": _canonical_strings(outputs, "outputs", require_nonempty=True),
        "state_and_persistence": _require_string(
            state_and_persistence, "state_and_persistence"
        ),
        "authority": _require_string(authority, "authority"),
        "non_authorities": _canonical_strings(
            non_authorities, "non_authorities", require_nonempty=True
        ),
        "boundary": _require_string(boundary, "boundary"),
        "determinism": _require_string(determinism, "determinism"),
        "evidence_and_replay": _require_string(
            evidence_and_replay, "evidence_and_replay"
        ),
        "activation_and_lifecycle": _require_string(
            activation_and_lifecycle, "activation_and_lifecycle"
        ),
    }
    artifact["signature_hash"] = replay_hash(artifact)
    return validate_responsibility_signature(artifact)


def validate_responsibility_signature(artifact: dict[str, Any]) -> dict[str, Any]:
    """Validate the complete G63 responsibility signature and its identity."""

    candidate = _require_dict(artifact, "responsibility_signature")
    if candidate.get("artifact_type") != RESPONSIBILITY_SIGNATURE_ARTIFACT_V1:
        raise FailClosedRuntimeError("responsibility signature artifact type is invalid")
    if candidate.get("runtime_version") != CONSTITUTIONAL_REUSE_PROOF_RUNTIME_VERSION:
        raise FailClosedRuntimeError("responsibility signature runtime version is invalid")
    for field in RESPONSIBILITY_FIELDS:
        if field in {"inputs", "outputs", "non_authorities"}:
            expected = _canonical_strings(candidate.get(field), field, require_nonempty=True)
            if candidate.get(field) != expected:
                raise FailClosedRuntimeError(f"responsibility signature {field} is not canonical")
        else:
            _require_string(candidate.get(field), field)
    _verify_named_hash(candidate, "signature_hash", "responsibility signature")
    return deepcopy(candidate)


def compose_constitutional_reuse_proof_input(
    *,
    proof_id: str,
    request: str,
    proposed_scope: dict[str, Any],
    repository_root: str | Path,
    created_at: str,
    workspace_state: dict[str, Any] | None = None,
    expected_baseline: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compose one existing G63 input from authenticated read-only owners.

    This bounded owner path intentionally supports only the strongest existing
    G20 disposition: one unchanged certified capability is sufficient. Every
    other disposition remains incomplete and fails closed for caller or Human
    evidence instead of being promoted into a synthetic proof.
    """

    query = _require_string(request, "request")
    scope = _require_dict(proposed_scope, "proposed_scope")
    root = Path(repository_root).resolve()
    if not root.is_dir():
        raise FailClosedRuntimeError("reuse proof repository root is unavailable")

    baseline = _acquire_authenticated_owner_baseline(
        root=root,
        expected_baseline=expected_baseline,
    )
    coverage = validate_platform_capability_composition_coverage(
        discover_platform_capability_composition_coverage(
            query=query,
            workspace_state=workspace_state,
            governance_root=root,
            created_at=created_at,
        )
    )
    if coverage.get("coverage_status") != COVERAGE_COMPLETE:
        raise FailClosedRuntimeError(
            "material capability coverage evidence is unavailable or incomplete"
        )
    if coverage.get("uncovered_residual_gap_count") != 0:
        raise FailClosedRuntimeError("material capability coverage contains a residual gap")
    minimal = _require_dict(
        coverage.get("minimal_required_platform_extension"),
        "minimal_required_platform_extension",
    )
    if minimal.get("classification") != NO_GAP_EXISTING_CAPABILITY_SUFFICIENT:
        raise FailClosedRuntimeError(
            "owner evidence does not prove one unchanged certified reuse target"
        )
    recommended = _canonical_strings(
        minimal.get("recommended_components"),
        "recommended_components",
        require_nonempty=True,
    )
    if len(recommended) != 1:
        raise FailClosedRuntimeError("owner evidence has no unique reuse target")
    candidate_id = recommended[0]

    discovered = coverage.get("discovered_reusable_capabilities")
    if not isinstance(discovered, list) or len(discovered) != 1:
        raise FailClosedRuntimeError("owner evidence has contradictory candidate cardinality")
    discovered_candidate = _require_dict(discovered[0], "discovered capability")
    if (
        discovered_candidate.get("capability_identifier") != candidate_id
        or discovered_candidate.get("certified") is not True
    ):
        raise FailClosedRuntimeError("owner evidence contradicts the selected reuse target")

    record = lookup_platform_capability_certification(candidate_id)
    if record is None or record.get("superseded_by") is not None:
        raise FailClosedRuntimeError("selected reuse target is not currently certified")
    if (
        discovered_candidate.get("certification_record_hash")
        != record["certification_record_hash"]
        or discovered_candidate.get("implementation_owner")
        != record["implementation_owner"]
    ):
        raise FailClosedRuntimeError("certification owner evidence is contradictory")

    discovery = coverage.get("candidate_capability_discovery")
    goal_target = (
        str(discovery.get("selected_goal_target") or "general_project_goal")
        if isinstance(discovery, dict)
        else "general_project_goal"
    )
    knowledge = validate_platform_knowledge_response(
        query_platform_knowledge(
            query=query,
            capability_identifier=candidate_id,
            goal_target=goal_target,
            workspace_state=workspace_state,
        )
    )
    if (
        knowledge.get("canonical_capability_identifier") != candidate_id
        or knowledge.get("certification_record_hash")
        != record["certification_record_hash"]
        or knowledge.get("capability_owner") != record["capability_owner"]
        or knowledge.get("architectural_owner") != record["architectural_owner"]
        or knowledge.get("implementation_owner") != record["implementation_owner"]
        or knowledge.get("is_certified") is not True
    ):
        raise FailClosedRuntimeError("Platform Knowledge contradicts certification evidence")

    plan = validate_platform_development_composition_plan(
        compose_platform_development_plan(
            capability_coverage_artifact=coverage,
            created_at=created_at,
        )
    )
    if (
        plan.get("plan_status")
        != DEVELOPMENT_COMPOSITION_PLAN_NO_IMPLEMENTATION_REQUIRED
        or plan.get("implementation_required") is not False
        or plan.get("residual_capability_gaps")
    ):
        raise FailClosedRuntimeError("G20 planning evidence contradicts unchanged reuse")

    implementation_path = _implementation_owner_path(
        root,
        _require_string(record.get("implementation_owner"), "implementation_owner"),
    )
    if implementation_path is None:
        raise FailClosedRuntimeError("certified implementation owner is unavailable")

    matrix = build_capability_matrix(detect_capabilities(root))
    conformance = run_conformance_check(root)
    if conformance.get("critical_violations"):
        raise FailClosedRuntimeError("critical governance conformance violation blocks proof")

    evidence_refs = _owner_evidence_references(
        coverage=coverage,
        knowledge=knowledge,
        plan=plan,
        record=record,
        capability_matrix=matrix,
        conformance=conformance,
    )
    route_descriptor = next(
        (
            deepcopy(item)
            for item in coverage.get("platform_query_route_descriptors", [])
            if isinstance(item, dict)
            and item.get("service_identifier") == candidate_id
        ),
        None,
    )
    if route_descriptor is not None and (
        route_descriptor.get("implementation_owner") != record["implementation_owner"]
    ):
        raise FailClosedRuntimeError("route ownership contradicts certification evidence")

    signature = create_responsibility_signature(
        semantic_responsibility=query,
        inputs=["authenticated project objective", "authenticated owner evidence"],
        outputs=["existing certified capability reuse disposition"],
        state_and_persistence="No new state or persistence; reuse is read-only evidence composition.",
        authority="Development Governance owns reuse-proof completeness and semantics.",
        non_authorities=[
            "does not authorize implementation",
            "does not authorize execution",
            "does not replace source fact owners",
        ],
        boundary="Consumes owner facts without transferring source-owner authority.",
        determinism="Canonical owner normalization, fail-closed validation, and replay hashing.",
        evidence_and_replay="Preserves owner artifact hashes, references, limitations, and uncertainty.",
        activation_and_lifecycle="Runs at the existing Project Services pre-G64 seam only when proof is required.",
    )
    search_manifest = _owner_search_manifest(
        baseline=baseline,
        coverage=coverage,
        record=record,
        route_descriptor=route_descriptor,
    )
    ownership_roles = {
        "architectural_owner": record["architectural_owner"],
        "authority_owner": record["capability_owner"],
        "implementation_owner": record["implementation_owner"],
        "state_owner": record["capability_owner"],
        "registry_owner": "PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY",
        "evidence_replay_owner": "GOVERNANCE_REPORT_EVIDENCE",
        "lifecycle_owner": "DEVELOPMENT_GOVERNANCE",
        "human_owner": "HUMAN_AUTHORITY",
        "consumers": ["CONSTITUTIONAL_REUSE_PROOF_RUNTIME"],
    }
    compatibility = {
        dimension: "DIRECTLY_COMPATIBLE" for dimension in COMPATIBILITY_DIMENSIONS
    }
    target_layers = scope.get("target_layers") or ["L3_GOVERNANCE_SYSTEM"]
    return create_constitutional_reuse_proof_input(
        proof_id=proof_id,
        responsibility_signature=signature,
        authenticated_baseline=baseline,
        target_layers=target_layers,
        search_manifest=search_manifest,
        capability_inventory=[
            {
                "candidate_id": candidate_id,
                "candidate_type": "CERTIFIED_RUNTIME",
                "source_reference": record["certification_evidence"][0],
                "source_hash": record["certification_record_hash"],
                "maturity": [
                    "CERTIFIED_METADATA",
                    "EVIDENCE_PRODUCING",
                    "RUNTIME_BOUND",
                ],
                "active": True,
                "public_contract": True,
            }
        ],
        ownership_matrix=[{"candidate_id": candidate_id, "roles": ownership_roles}],
        registry_matrix=[
            {
                "candidate_id": candidate_id,
                "registry_id": "PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY",
                "registry_version": PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION,
                "record_hash": record["certification_record_hash"],
                "status": record["certification_status"],
                "runtime_bound": True,
                "invocable": route_descriptor is not None,
                "authority": "GOVERNANCE_METADATA_ONLY",
                "consumers": ["PLATFORM_KNOWLEDGE_RUNTIME"],
            }
        ],
        implementation_usage_graph=[
            {
                "candidate_id": candidate_id,
                "module": record["implementation_owner"],
                "api": (
                    route_descriptor.get("adapter_name")
                    if route_descriptor is not None
                    else "CERTIFIED_MODULE_PUBLIC_SURFACE"
                ),
                "status": "ACTIVE_CERTIFIED",
                "reachable": True,
                "default_route": False,
                "effects": ["CERTIFIED_BEHAVIOR_UNCHANGED"],
                "consumers": ["CONSTITUTIONAL_REUSE_PROOF_RUNTIME"],
                "assurance_refs": evidence_refs,
                "history_disposition": "CURRENT_NOT_SUPERSEDED",
            }
        ],
        equivalence_matrix=[
            {
                "candidate_id": candidate_id,
                "disposition": "EXACT_EQUIVALENT",
                "matched_fields": list(RESPONSIBILITY_FIELDS),
                "mismatched_fields": [],
                "evidence_refs": evidence_refs,
            }
        ],
        compatibility_matrix=[
            {
                "candidate_id": candidate_id,
                "dimensions": compatibility,
                "evidence_refs": evidence_refs,
            }
        ],
        extension_ladder=[],
        duplicate_matrix=[],
        negative_evidence={
            "reuse_rejected": [],
            "extend_rejected": [],
            "consolidate_rejected": [],
            "absence_scope": [],
            "proposed_ownership": {},
        },
        evolution_evidence={
            **{field: True for field in EVOLUTION_FIELDS},
            "evidence_refs": evidence_refs,
        },
        authority_and_dependency_delta={
            "authority_delta": "NONE",
            "ownership_delta": "NONE",
            "dependency_delta": "NONE",
            "evidence_refs": evidence_refs,
        },
        migration_rollback_deprecation={
            "migration": "NOT_REQUIRED__EXISTING_CERTIFIED_CAPABILITY_REUSED_UNCHANGED",
            "rollback": "STOP_REUSE_WITHOUT_MUTATING_THE_EXISTING_OWNER",
            "deprecation": "NO_EXISTING_SURFACE_DEPRECATED",
            "evidence_refs": evidence_refs,
        },
        next_checkpoints=["G47_FRESH_DEVELOPMENT_GOVERNANCE_ASSESSMENT"],
        known_limitations=[
            "General keyword knowledge may identify additional related capabilities; only the G20 unique certified target and its explicit registry lookup are authoritative here.",
            "External dynamic evidence is not inferred from local repository evidence.",
            "Repository-only evidence is not operational proof.",
        ],
        created_at=created_at,
    )


def _acquire_authenticated_owner_baseline(
    *,
    root: Path,
    expected_baseline: dict[str, Any] | None,
) -> dict[str, Any]:
    def git_value(*args: str) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            raise FailClosedRuntimeError("authenticated Git evidence is unavailable")
        return completed.stdout.strip()

    observed_identity = {
        "commit": git_value("rev-parse", "HEAD"),
        "parent": git_value("rev-parse", "HEAD^"),
        "tree": git_value("rev-parse", "HEAD^{tree}"),
        "worktree_clean": not bool(git_value("status", "--porcelain")),
    }
    if observed_identity["worktree_clean"] is not True:
        raise FailClosedRuntimeError("reuse proof baseline must be clean")

    if expected_baseline is not None:
        baseline = _normalize_baseline(expected_baseline)
        for field in ("commit", "parent", "tree", "worktree_clean"):
            if baseline[field] != observed_identity[field]:
                raise FailClosedRuntimeError("authenticated baseline evidence is contradictory")
        _verify_governing_source_bytes(root, baseline["governing_sources"])
        return baseline

    sources = []
    for relative in _OWNER_COMPOSITION_GOVERNING_SOURCES:
        path = root / relative
        if not path.is_file():
            raise FailClosedRuntimeError("material governing source is unavailable")
        sources.append(
            {
                "path": relative,
                "sha256": "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    return _normalize_baseline(
        {
            **observed_identity,
            "governing_sources": sources,
            "known_limitations": [
                "The baseline authenticates local Git objects and governing source bytes only.",
                "No remote or operational state is inferred by the composition runtime.",
            ],
        }
    )


def _verify_governing_source_bytes(
    root: Path,
    sources: list[dict[str, str]],
) -> None:
    for source in sources:
        path = root / source["path"]
        if not path.is_file():
            raise FailClosedRuntimeError("authenticated governing source is unavailable")
        observed = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        if observed != source["sha256"]:
            raise FailClosedRuntimeError("authenticated governing source hash mismatch")


def _implementation_owner_path(root: Path, owner: str) -> Path | None:
    relative = Path(*owner.split("."))
    module_path = root / relative.with_suffix(".py")
    package_path = root / relative / "__init__.py"
    if module_path.is_file():
        return module_path
    if package_path.is_file():
        return package_path
    return None


def _owner_evidence_references(
    *,
    coverage: dict[str, Any],
    knowledge: dict[str, Any],
    plan: dict[str, Any],
    record: dict[str, Any],
    capability_matrix: dict[str, Any],
    conformance: dict[str, Any],
) -> list[str]:
    references = [
        coverage["artifact_hash"],
        knowledge["artifact_hash"],
        plan["artifact_hash"],
        record["certification_record_hash"],
        capability_matrix["matrix_hash"],
        replay_hash(conformance),
        *record["certification_evidence"],
    ]
    return sorted({str(item) for item in references if str(item).strip()})


def _owner_search_manifest(
    *,
    baseline: dict[str, Any],
    coverage: dict[str, Any],
    record: dict[str, Any],
    route_descriptor: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    searched = {
        "CONSTITUTIONAL_GOVERNANCE": (
            "authenticated governing source bytes and governance conformance",
            "owner source hashing and existing conformance engine",
        ),
        "PCBV31": (
            "authenticated Git commit, parent, tree, and clean status",
            "read-only Git object and status inspection",
        ),
        "RUNTIME_API": (
            "certified implementation owner and public module surface",
            "certification registry and implementation-owner path validation",
        ),
        "REGISTRY_ROUTING": (
            "certification registry and Platform route descriptors",
            "existing G15 registry and Platform router metadata",
        ),
        "TEST_REPLAY_MIGRATION": (
            "certification, capability-audit, and no-migration owner evidence",
            "existing certification references and pure capability audit",
        ),
        "GIT_HISTORY": (
            "current immutable Git identity and direct parent",
            "read-only Git object inspection",
        ),
    }
    manifest = []
    for evidence_class in SEARCH_EVIDENCE_CLASSES:
        if evidence_class in searched:
            scope, method = searched[evidence_class]
            observation = (
                f"owner evidence authenticated for {record['capability_identifier']} "
                f"at {baseline['commit']} with coverage {coverage['artifact_hash']}"
            )
            if evidence_class == "REGISTRY_ROUTING" and route_descriptor is None:
                observation += "; no route descriptor exists and registry-only reuse is preserved"
            manifest.append(
                {
                    "evidence_class": evidence_class,
                    "scope": scope,
                    "method": method,
                    "observation": observation,
                    "status": "SEARCHED",
                    "material": True,
                    "limitation": None,
                }
            )
            continue
        manifest.append(
            {
                "evidence_class": evidence_class,
                "scope": "unchanged certified local capability reuse",
                "method": "bounded G63 applicability reduction",
                "observation": "no new caller, external effect, dynamic source, or legacy alternate is asserted",
                "status": "NOT_APPLICABLE",
                "material": False,
                "limitation": "A scope change would require new owner evidence and recomposition.",
            }
        )
    return manifest


def create_constitutional_reuse_proof_input(
    *,
    proof_id: str,
    responsibility_signature: dict[str, Any],
    authenticated_baseline: dict[str, Any],
    target_layers: list[str] | tuple[str, ...],
    search_manifest: list[dict[str, Any]],
    capability_inventory: list[dict[str, Any]],
    ownership_matrix: list[dict[str, Any]],
    registry_matrix: list[dict[str, Any]],
    implementation_usage_graph: list[dict[str, Any]],
    equivalence_matrix: list[dict[str, Any]],
    compatibility_matrix: list[dict[str, Any]],
    extension_ladder: list[dict[str, Any]],
    duplicate_matrix: list[dict[str, Any]],
    negative_evidence: dict[str, Any],
    evolution_evidence: dict[str, Any],
    authority_and_dependency_delta: dict[str, Any],
    migration_rollback_deprecation: dict[str, Any],
    next_checkpoints: list[str] | tuple[str, ...],
    known_limitations: list[str] | tuple[str, ...],
    created_at: str,
) -> dict[str, Any]:
    """Create a hash-bound proof input from owner-supplied evidence."""

    signature = validate_responsibility_signature(responsibility_signature)
    artifact = {
        "artifact_type": REUSE_PROOF_INPUT_ARTIFACT_V1,
        "runtime_version": CONSTITUTIONAL_REUSE_PROOF_RUNTIME_VERSION,
        "proof_id": _require_string(proof_id, "proof_id"),
        "responsibility_signature": signature,
        "responsibility_signature_hash": signature["signature_hash"],
        "authenticated_baseline": _normalize_baseline(authenticated_baseline),
        "target_layers": _canonical_strings(
            target_layers, "target_layers", require_nonempty=True
        ),
        "search_manifest": _sort_records(search_manifest, "evidence_class"),
        "capability_inventory": _sort_records(capability_inventory, "candidate_id"),
        "ownership_matrix": _sort_records(ownership_matrix, "candidate_id"),
        "registry_matrix": _sort_records(registry_matrix, "candidate_id"),
        "implementation_usage_graph": _sort_records(
            implementation_usage_graph, "candidate_id"
        ),
        "equivalence_matrix": _sort_records(equivalence_matrix, "candidate_id"),
        "compatibility_matrix": _sort_records(
            compatibility_matrix, "candidate_id"
        ),
        "extension_ladder": deepcopy(extension_ladder),
        "duplicate_matrix": _sort_duplicate_records(duplicate_matrix),
        "negative_evidence": deepcopy(negative_evidence),
        "evolution_evidence": deepcopy(evolution_evidence),
        "authority_and_dependency_delta": deepcopy(authority_and_dependency_delta),
        "migration_rollback_deprecation": deepcopy(
            migration_rollback_deprecation
        ),
        "next_checkpoints": _canonical_strings(
            next_checkpoints, "next_checkpoints", require_nonempty=True
        ),
        "known_limitations": _canonical_strings(
            known_limitations, "known_limitations", require_nonempty=False
        ),
        "created_at": _require_string(created_at, "created_at"),
    }
    artifact["input_hash"] = replay_hash(artifact)
    return validate_constitutional_reuse_proof_input(artifact)


def validate_constitutional_reuse_proof_input(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate structure and integrity before consulting existing owners."""

    candidate = _require_dict(artifact, "reuse proof input")
    if candidate.get("artifact_type") != REUSE_PROOF_INPUT_ARTIFACT_V1:
        raise FailClosedRuntimeError("reuse proof input artifact type is invalid")
    if candidate.get("runtime_version") != CONSTITUTIONAL_REUSE_PROOF_RUNTIME_VERSION:
        raise FailClosedRuntimeError("reuse proof input runtime version is invalid")
    _require_string(candidate.get("proof_id"), "proof_id")
    signature = validate_responsibility_signature(
        _require_dict(candidate.get("responsibility_signature"), "responsibility_signature")
    )
    if candidate.get("responsibility_signature_hash") != signature["signature_hash"]:
        raise FailClosedRuntimeError("reuse proof signature binding mismatch")
    normalized_baseline = _normalize_baseline(candidate.get("authenticated_baseline"))
    if candidate.get("authenticated_baseline") != normalized_baseline:
        raise FailClosedRuntimeError("authenticated baseline is not canonical")
    for field in ("target_layers", "next_checkpoints", "known_limitations"):
        expected = _canonical_strings(
            candidate.get(field),
            field,
            require_nonempty=field != "known_limitations",
        )
        if candidate.get(field) != expected:
            raise FailClosedRuntimeError(f"reuse proof input {field} is not canonical")
    for field, key in (
        ("search_manifest", "evidence_class"),
        ("capability_inventory", "candidate_id"),
        ("ownership_matrix", "candidate_id"),
        ("registry_matrix", "candidate_id"),
        ("implementation_usage_graph", "candidate_id"),
        ("equivalence_matrix", "candidate_id"),
        ("compatibility_matrix", "candidate_id"),
    ):
        value = candidate.get(field)
        if not isinstance(value, list):
            raise FailClosedRuntimeError(f"{field} must be a list")
        if value != _sort_records(value, key):
            raise FailClosedRuntimeError(f"{field} is not canonical")
    duplicates = candidate.get("duplicate_matrix")
    if not isinstance(duplicates, list) or duplicates != _sort_duplicate_records(duplicates):
        raise FailClosedRuntimeError("duplicate_matrix is not canonical")
    if not isinstance(candidate.get("extension_ladder"), list):
        raise FailClosedRuntimeError("extension_ladder must be a list")
    for field in (
        "negative_evidence",
        "evolution_evidence",
        "authority_and_dependency_delta",
        "migration_rollback_deprecation",
    ):
        _require_dict(candidate.get(field), field)
    _require_string(candidate.get("created_at"), "created_at")
    _verify_named_hash(candidate, "input_hash", "reuse proof input")
    return deepcopy(candidate)


def evaluate_constitutional_reuse_proof(
    *,
    proof_input: dict[str, Any],
    repository_root: str | Path,
    workspace_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate one complete proof and return exactly one G63 decision."""

    source = validate_constitutional_reuse_proof_input(proof_input)
    root = Path(repository_root).resolve()
    if not root.is_dir():
        raise FailClosedRuntimeError("reuse proof repository root is unavailable")

    search_manifest = _validate_search_manifest(source["search_manifest"])
    inventory = _validate_capability_inventory(source["capability_inventory"])
    candidate_ids = tuple(item["candidate_id"] for item in inventory)
    ownership = _validate_ownership_matrix(source["ownership_matrix"], candidate_ids)
    registries = _validate_registry_matrix(source["registry_matrix"], candidate_ids)
    usage = _validate_implementation_usage_graph(
        source["implementation_usage_graph"], candidate_ids
    )
    equivalence = _validate_equivalence_matrix(
        source["equivalence_matrix"], candidate_ids
    )
    compatibility = _validate_compatibility_matrix(
        source["compatibility_matrix"], candidate_ids
    )
    ladder = _validate_extension_ladder(source["extension_ladder"])
    duplicates = _validate_duplicate_matrix(source["duplicate_matrix"], candidate_ids)
    negative_evidence = _validate_negative_evidence(source["negative_evidence"])
    evolution_evidence = _validate_evolution_evidence(source["evolution_evidence"])
    authority_delta = _validate_named_evidence_map(
        source["authority_and_dependency_delta"],
        "authority_and_dependency_delta",
    )
    lifecycle = _validate_lifecycle_evidence(
        source["migration_rollback_deprecation"]
    )

    registry_by_id = {
        record["capability_identifier"]: record
        for record in list_platform_capability_certifications()
    }
    _validate_registered_candidate_bindings(
        inventory=inventory,
        ownership=ownership,
        registries=registries,
        usage=usage,
        registry_by_id=registry_by_id,
    )

    composition_evidence = _compose_existing_owner_evidence(
        signature=source["responsibility_signature"],
        root=root,
        workspace_state=workspace_state,
        created_at=source["created_at"],
        registry_records=list(registry_by_id.values()),
    )
    if composition_evidence["governance_conformance"]["critical_violations"]:
        raise FailClosedRuntimeError("critical governance conformance violation blocks proof")

    decision, selected_target = _reduce_decision(
        inventory=inventory,
        equivalence=equivalence,
        compatibility=compatibility,
        ladder=ladder,
        duplicates=duplicates,
        negative_evidence=negative_evidence,
    )
    additive_or_versioned = _classify_evolution(
        decision=decision,
        evidence=evolution_evidence,
    )
    _validate_decision_lifecycle(
        decision=decision,
        authority_delta=authority_delta,
        lifecycle=lifecycle,
    )

    artifact = {
        "artifact_type": REUSE_PROOF_RESULT_ARTIFACT_V1,
        "runtime_version": CONSTITUTIONAL_REUSE_PROOF_RUNTIME_VERSION,
        "proof_id": source["proof_id"],
        "source_input_hash": source["input_hash"],
        "authenticated_baseline": deepcopy(source["authenticated_baseline"]),
        "responsibility_signature": deepcopy(source["responsibility_signature"]),
        "target_layers_and_class": {
            "target_layers": deepcopy(source["target_layers"]),
            "evolution_classification": additive_or_versioned,
        },
        "search_manifest": search_manifest,
        "capability_inventory": inventory,
        "ownership_matrix": ownership,
        "registry_matrix": registries,
        "implementation_usage_graph": usage,
        "equivalence_matrix": equivalence,
        "compatibility_matrix": compatibility,
        "extension_ladder": ladder,
        "duplicate_matrix": duplicates,
        "negative_evidence": negative_evidence,
        "evolution_evidence": evolution_evidence,
        "decision": decision,
        "selected_target": selected_target,
        "additive_or_versioned": additive_or_versioned,
        "authority_and_dependency_delta": authority_delta,
        "migration_rollback_deprecation": lifecycle,
        "next_checkpoints": deepcopy(source["next_checkpoints"]),
        "known_limitations": deepcopy(source["known_limitations"]),
        "proof_disposition": PROOF_COMPLETE_FOR_EVOLUTION_PLANNING,
        "composition_evidence": composition_evidence,
        "created_at": source["created_at"],
        **BOUNDARY_FLAGS,
    }
    artifact["evidence_identity"] = replay_hash(artifact)
    return validate_constitutional_reuse_proof_result(artifact)


def validate_constitutional_reuse_proof_result(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    """Validate a complete proof result without consulting mutable state."""

    candidate = _require_dict(artifact, "reuse proof result")
    if candidate.get("artifact_type") != REUSE_PROOF_RESULT_ARTIFACT_V1:
        raise FailClosedRuntimeError("reuse proof result artifact type is invalid")
    if candidate.get("runtime_version") != CONSTITUTIONAL_REUSE_PROOF_RUNTIME_VERSION:
        raise FailClosedRuntimeError("reuse proof result runtime version is invalid")
    _require_string(candidate.get("proof_id"), "proof_id")
    _require_hash(candidate.get("source_input_hash"), "source_input_hash")
    signature = validate_responsibility_signature(
        _require_dict(candidate.get("responsibility_signature"), "responsibility_signature")
    )
    baseline = _normalize_baseline(candidate.get("authenticated_baseline"))
    if candidate.get("authenticated_baseline") != baseline:
        raise FailClosedRuntimeError("reuse proof result baseline is not canonical")

    target = _require_dict(candidate.get("target_layers_and_class"), "target_layers_and_class")
    layers = _canonical_strings(
        target.get("target_layers"), "target_layers", require_nonempty=True
    )
    if target.get("target_layers") != layers:
        raise FailClosedRuntimeError("reuse proof result target layers are not canonical")

    search_manifest = _validate_search_manifest(candidate.get("search_manifest"))
    inventory = _validate_capability_inventory(candidate.get("capability_inventory"))
    candidate_ids = tuple(item["candidate_id"] for item in inventory)
    ownership = _validate_ownership_matrix(candidate.get("ownership_matrix"), candidate_ids)
    registries = _validate_registry_matrix(candidate.get("registry_matrix"), candidate_ids)
    usage = _validate_implementation_usage_graph(
        candidate.get("implementation_usage_graph"), candidate_ids
    )
    equivalence = _validate_equivalence_matrix(
        candidate.get("equivalence_matrix"), candidate_ids
    )
    compatibility = _validate_compatibility_matrix(
        candidate.get("compatibility_matrix"), candidate_ids
    )
    ladder = _validate_extension_ladder(candidate.get("extension_ladder"))
    duplicates = _validate_duplicate_matrix(candidate.get("duplicate_matrix"), candidate_ids)
    negative_evidence = _validate_negative_evidence(candidate.get("negative_evidence"))
    evolution_evidence = _validate_evolution_evidence(candidate.get("evolution_evidence"))
    authority_delta = _validate_named_evidence_map(
        candidate.get("authority_and_dependency_delta"),
        "authority_and_dependency_delta",
    )
    lifecycle = _validate_lifecycle_evidence(
        candidate.get("migration_rollback_deprecation")
    )
    expected_decision, expected_target = _reduce_decision(
        inventory=inventory,
        equivalence=equivalence,
        compatibility=compatibility,
        ladder=ladder,
        duplicates=duplicates,
        negative_evidence=negative_evidence,
    )
    if candidate.get("decision") != expected_decision:
        raise FailClosedRuntimeError("reuse proof result decision does not follow the reducer")
    if candidate.get("selected_target") != expected_target:
        raise FailClosedRuntimeError("reuse proof result target does not follow the reducer")
    expected_evolution = _classify_evolution(
        decision=expected_decision,
        evidence=evolution_evidence,
    )
    if candidate.get("additive_or_versioned") != expected_evolution:
        raise FailClosedRuntimeError("reuse proof evolution classification mismatch")
    if target.get("evolution_classification") != expected_evolution:
        raise FailClosedRuntimeError("reuse proof target evolution class mismatch")
    _validate_decision_lifecycle(
        decision=expected_decision,
        authority_delta=authority_delta,
        lifecycle=lifecycle,
    )
    if candidate.get("proof_disposition") != PROOF_COMPLETE_FOR_EVOLUTION_PLANNING:
        raise FailClosedRuntimeError("reuse proof result disposition is invalid")
    for field, expected in BOUNDARY_FLAGS.items():
        if candidate.get(field) is not expected:
            raise FailClosedRuntimeError("reuse proof authority boundary mismatch")
    composition = _require_dict(candidate.get("composition_evidence"), "composition_evidence")
    _verify_named_hash(
        composition, "composition_evidence_hash", "reuse proof composition evidence"
    )
    for field in ("provider_invoked", "worker_invoked", "repository_mutated"):
        if composition.get(field) is not False:
            raise FailClosedRuntimeError("reuse proof composition crossed an authority boundary")
    _canonical_strings(
        candidate.get("next_checkpoints"), "next_checkpoints", require_nonempty=True
    )
    _canonical_strings(
        candidate.get("known_limitations"), "known_limitations", require_nonempty=False
    )
    _require_string(candidate.get("created_at"), "created_at")
    _verify_named_hash(candidate, "evidence_identity", "reuse proof result")
    return deepcopy(candidate)


def project_reuse_proof_to_development_governance(
    proof_result: dict[str, Any],
) -> dict[str, Any]:
    """Project a complete proof reference toward G47 without granting eligibility."""

    proof = validate_constitutional_reuse_proof_result(proof_result)
    artifact = {
        "artifact_type": REUSE_PROOF_G47_HANDOFF_ARTIFACT_V1,
        "runtime_version": CONSTITUTIONAL_REUSE_PROOF_RUNTIME_VERSION,
        "source_proof_id": proof["proof_id"],
        "source_proof_hash": proof["evidence_identity"],
        "source_proof_disposition": proof["proof_disposition"],
        "source_reuse_decision": proof["decision"],
        "source_selected_target": deepcopy(proof["selected_target"]),
        "source_evolution_classification": proof["additive_or_versioned"],
        "g47_action": "RUN_FRESH_DEVELOPMENT_GOVERNANCE_ASSESSMENT",
        "requires_g47_task_intake": True,
        "requires_g47_cdd_classification": True,
        "requires_g47_authoritative_evidence_snapshot": True,
        "requires_g47_need_assessment": True,
        "requires_g47_governance_disposition": True,
        "requires_g47_planning_eligibility": True,
        "g47_need_assessment_precomputed": False,
        "g47_planning_eligible": False,
        "authorizes_planning": False,
        "authorizes_implementation": False,
        "authorizes_execution": False,
        "authorization_modified": False,
        "worker_modified": False,
        "replay_modified": False,
        "repository_mutated": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return validate_reuse_proof_g47_handoff(artifact)


def validate_reuse_proof_g47_handoff(artifact: dict[str, Any]) -> dict[str, Any]:
    """Validate the non-authorizing G63-to-G47 projection."""

    candidate = _require_dict(artifact, "reuse proof G47 handoff")
    if candidate.get("artifact_type") != REUSE_PROOF_G47_HANDOFF_ARTIFACT_V1:
        raise FailClosedRuntimeError("reuse proof G47 handoff type is invalid")
    if candidate.get("runtime_version") != CONSTITUTIONAL_REUSE_PROOF_RUNTIME_VERSION:
        raise FailClosedRuntimeError("reuse proof G47 handoff version is invalid")
    _require_string(candidate.get("source_proof_id"), "source_proof_id")
    _require_hash(candidate.get("source_proof_hash"), "source_proof_hash")
    if candidate.get("source_proof_disposition") != PROOF_COMPLETE_FOR_EVOLUTION_PLANNING:
        raise FailClosedRuntimeError("reuse proof G47 handoff source is incomplete")
    if candidate.get("source_reuse_decision") not in DECISIONS:
        raise FailClosedRuntimeError("reuse proof G47 handoff decision is invalid")
    if candidate.get("g47_action") != "RUN_FRESH_DEVELOPMENT_GOVERNANCE_ASSESSMENT":
        raise FailClosedRuntimeError("reuse proof G47 handoff action is invalid")
    for field in (
        "requires_g47_task_intake",
        "requires_g47_cdd_classification",
        "requires_g47_authoritative_evidence_snapshot",
        "requires_g47_need_assessment",
        "requires_g47_governance_disposition",
        "requires_g47_planning_eligibility",
    ):
        if candidate.get(field) is not True:
            raise FailClosedRuntimeError("reuse proof G47 handoff omitted a G47 stage")
    for field in (
        "g47_need_assessment_precomputed",
        "g47_planning_eligible",
        "authorizes_planning",
        "authorizes_implementation",
        "authorizes_execution",
        "authorization_modified",
        "worker_modified",
        "replay_modified",
        "repository_mutated",
    ):
        if candidate.get(field) is not False:
            raise FailClosedRuntimeError("reuse proof G47 handoff authority mismatch")
    _verify_named_hash(candidate, "artifact_hash", "reuse proof G47 handoff")
    return deepcopy(candidate)


def _compose_existing_owner_evidence(
    *,
    signature: dict[str, Any],
    root: Path,
    workspace_state: dict[str, Any] | None,
    created_at: str,
    registry_records: list[dict[str, Any]],
) -> dict[str, Any]:
    query = signature["semantic_responsibility"]
    discovery = discover_candidate_capabilities(
        message=query,
        workspace_state=workspace_state,
    )
    goal_target = str(discovery.get("selected_goal_target") or "general_project_goal")
    knowledge_reuse = project_knowledge_context_from_workspace(
        message=query,
        workspace_state=workspace_state,
        goal_target=goal_target,
        governed_request=query,
        candidate_capability_discovery=discovery,
    )
    knowledge = validate_platform_knowledge_response(
        query_platform_knowledge(
            query=query,
            goal_target=goal_target,
            workspace_state=workspace_state,
        )
    )
    coverage = validate_platform_capability_composition_coverage(
        discover_platform_capability_composition_coverage(
            query=query,
            workspace_state=workspace_state,
            governance_root=root,
            created_at=created_at,
        )
    )
    capability_matrix = build_capability_matrix(detect_capabilities(root))
    conformance = run_conformance_check(root)
    evidence = {
        "platform_core_project_services_version": PLATFORM_CORE_PROJECT_SERVICES_VERSION,
        "human_intent_capability_resolution_version": (
            PLATFORM_CORE_HUMAN_INTENT_CAPABILITY_RESOLUTION_VERSION
        ),
        "project_knowledge_reuse_version": PLATFORM_CORE_PROJECT_KNOWLEDGE_REUSE_VERSION,
        "platform_knowledge_runtime_version": PLATFORM_KNOWLEDGE_RUNTIME_VERSION,
        "capability_certification_registry_version": (
            PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION
        ),
        "capability_composition_coverage_version": (
            PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_VERSION
        ),
        "capability_audit_runtime_version": AIGOL_CAPABILITY_AUDIT_RUNTIME_VERSION,
        "candidate_capability_discovery": discovery,
        "candidate_capability_discovery_hash": discovery["artifact_hash"],
        "project_knowledge_reuse": knowledge_reuse,
        "project_knowledge_reuse_hash": replay_hash(knowledge_reuse),
        "platform_knowledge_response": knowledge,
        "platform_knowledge_response_hash": knowledge["artifact_hash"],
        "capability_composition_coverage": coverage,
        "capability_composition_coverage_hash": coverage["artifact_hash"],
        "capability_audit_summary": {
            "scope": deepcopy(capability_matrix["scope"]),
            "capability_counts": deepcopy(capability_matrix["capability_counts"]),
            "normalized_capability_counts": deepcopy(
                capability_matrix["normalized_capability_counts"]
            ),
            "matrix_hash": capability_matrix["matrix_hash"],
        },
        "certification_registry_record_count": len(registry_records),
        "certification_registry_fingerprint": replay_hash(registry_records),
        "governance_conformance": conformance,
        "existing_owners_reused": [
            "PLATFORM_CORE_PROJECT_SERVICES",
            "PLATFORM_CORE_KNOWLEDGE",
            "PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY",
            "PLATFORM_CORE_CAPABILITY_DISCOVERY",
            "AIGOL_CAPABILITY_AUDIT_RUNTIME",
            "GOVERNANCE_CONFORMANCE_ENGINE",
        ],
        "provider_invoked": False,
        "worker_invoked": False,
        "repository_mutated": False,
    }
    evidence["composition_evidence_hash"] = replay_hash(evidence)
    return evidence


def _validate_search_manifest(value: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_class = _unique_by(value, "evidence_class", "search_manifest")
    if tuple(sorted(by_class)) != tuple(sorted(SEARCH_EVIDENCE_CLASSES)):
        raise FailClosedRuntimeError("search manifest does not cover every evidence class")
    normalized = []
    for evidence_class in SEARCH_EVIDENCE_CLASSES:
        item = by_class[evidence_class]
        status = item.get("status")
        if status not in SEARCH_STATUSES:
            raise FailClosedRuntimeError("search manifest status is invalid")
        material = item.get("material")
        if not isinstance(material, bool):
            raise FailClosedRuntimeError("search manifest material flag is required")
        if status == "UNKNOWN_BLOCKED" and material:
            raise FailClosedRuntimeError("material repository search scope is unknown")
        normalized.append(
            {
                "evidence_class": evidence_class,
                "scope": _require_string(item.get("scope"), "search scope"),
                "method": _require_string(item.get("method"), "search method"),
                "observation": _require_string(
                    item.get("observation"), "search observation"
                ),
                "status": status,
                "material": material,
                "limitation": _optional_string(item.get("limitation")),
            }
        )
    return normalized


def _validate_capability_inventory(value: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = _unique_by(value, "candidate_id", "capability_inventory")
    normalized = []
    for candidate_id in sorted(by_id):
        item = by_id[candidate_id]
        maturity = _canonical_strings(
            item.get("maturity"), "candidate maturity", require_nonempty=True
        )
        if not set(maturity) <= MATURITY_STATES:
            raise FailClosedRuntimeError("candidate maturity state is invalid")
        for field in ("active", "public_contract"):
            if not isinstance(item.get(field), bool):
                raise FailClosedRuntimeError(f"candidate {field} flag is required")
        normalized.append(
            {
                "candidate_id": candidate_id,
                "candidate_type": _require_string(
                    item.get("candidate_type"), "candidate_type"
                ),
                "source_reference": _require_string(
                    item.get("source_reference"), "candidate source_reference"
                ),
                "source_hash": _require_hash(
                    item.get("source_hash"), "candidate source_hash"
                ),
                "maturity": maturity,
                "active": item["active"],
                "public_contract": item["public_contract"],
            }
        )
    return normalized


def _validate_ownership_matrix(
    value: list[dict[str, Any]], candidate_ids: tuple[str, ...]
) -> list[dict[str, Any]]:
    by_id = _unique_by(value, "candidate_id", "ownership_matrix")
    _require_same_candidate_set(by_id, candidate_ids, "ownership_matrix")
    normalized = []
    for candidate_id in sorted(by_id):
        item = by_id[candidate_id]
        roles = _require_dict(item.get("roles"), "ownership roles")
        normalized_roles = {
            role: _require_string(roles.get(role), role) for role in OWNERSHIP_ROLES
        }
        normalized_roles["consumers"] = _canonical_strings(
            roles.get("consumers"), "ownership consumers", require_nonempty=True
        )
        normalized.append({"candidate_id": candidate_id, "roles": normalized_roles})
    return normalized


def _validate_registry_matrix(
    value: list[dict[str, Any]], candidate_ids: tuple[str, ...]
) -> list[dict[str, Any]]:
    by_id = _unique_by(value, "candidate_id", "registry_matrix")
    _require_same_candidate_set(by_id, candidate_ids, "registry_matrix")
    normalized = []
    for candidate_id in sorted(by_id):
        item = by_id[candidate_id]
        for field in ("runtime_bound", "invocable"):
            if not isinstance(item.get(field), bool):
                raise FailClosedRuntimeError(f"registry {field} flag is required")
        normalized.append(
            {
                "candidate_id": candidate_id,
                "registry_id": _require_string(item.get("registry_id"), "registry_id"),
                "registry_version": _require_string(
                    item.get("registry_version"), "registry_version"
                ),
                "record_hash": _require_hash(item.get("record_hash"), "record_hash"),
                "status": _require_string(item.get("status"), "registry status"),
                "runtime_bound": item["runtime_bound"],
                "invocable": item["invocable"],
                "authority": _require_string(
                    item.get("authority"), "registry authority"
                ),
                "consumers": _canonical_strings(
                    item.get("consumers"), "registry consumers", require_nonempty=True
                ),
            }
        )
    return normalized


def _validate_implementation_usage_graph(
    value: list[dict[str, Any]], candidate_ids: tuple[str, ...]
) -> list[dict[str, Any]]:
    by_id = _unique_by(value, "candidate_id", "implementation_usage_graph")
    _require_same_candidate_set(by_id, candidate_ids, "implementation_usage_graph")
    normalized = []
    for candidate_id in sorted(by_id):
        item = by_id[candidate_id]
        for field in ("reachable", "default_route"):
            if not isinstance(item.get(field), bool):
                raise FailClosedRuntimeError(f"implementation {field} flag is required")
        normalized.append(
            {
                "candidate_id": candidate_id,
                "module": _require_string(item.get("module"), "implementation module"),
                "api": _require_string(item.get("api"), "implementation api"),
                "status": _require_string(item.get("status"), "implementation status"),
                "reachable": item["reachable"],
                "default_route": item["default_route"],
                "effects": _canonical_strings(
                    item.get("effects"), "implementation effects", require_nonempty=True
                ),
                "consumers": _canonical_strings(
                    item.get("consumers"), "implementation consumers", require_nonempty=True
                ),
                "assurance_refs": _canonical_strings(
                    item.get("assurance_refs"),
                    "implementation assurance_refs",
                    require_nonempty=True,
                ),
                "history_disposition": _require_string(
                    item.get("history_disposition"), "history_disposition"
                ),
            }
        )
    return normalized


def _validate_equivalence_matrix(
    value: list[dict[str, Any]], candidate_ids: tuple[str, ...]
) -> list[dict[str, Any]]:
    by_id = _unique_by(value, "candidate_id", "equivalence_matrix")
    _require_same_candidate_set(by_id, candidate_ids, "equivalence_matrix")
    normalized = []
    for candidate_id in sorted(by_id):
        item = by_id[candidate_id]
        disposition = item.get("disposition")
        if disposition not in EQUIVALENCE_DISPOSITIONS:
            raise FailClosedRuntimeError("equivalence disposition is invalid")
        if disposition == "UNKNOWN_BLOCKED":
            raise FailClosedRuntimeError("semantic equivalence is unknown")
        matched = _canonical_strings(
            item.get("matched_fields"), "matched_fields", require_nonempty=False
        )
        mismatched = _canonical_strings(
            item.get("mismatched_fields"), "mismatched_fields", require_nonempty=False
        )
        if not set(matched).union(mismatched) <= set(RESPONSIBILITY_FIELDS):
            raise FailClosedRuntimeError("equivalence field is not part of the signature")
        if disposition == "EXACT_EQUIVALENT":
            if tuple(matched) != tuple(sorted(RESPONSIBILITY_FIELDS)) or mismatched:
                raise FailClosedRuntimeError("exact equivalence must cover every signature field")
        normalized.append(
            {
                "candidate_id": candidate_id,
                "disposition": disposition,
                "matched_fields": matched,
                "mismatched_fields": mismatched,
                "evidence_refs": _canonical_strings(
                    item.get("evidence_refs"), "equivalence evidence", require_nonempty=True
                ),
            }
        )
    return normalized


def _validate_compatibility_matrix(
    value: list[dict[str, Any]], candidate_ids: tuple[str, ...]
) -> list[dict[str, Any]]:
    by_id = _unique_by(value, "candidate_id", "compatibility_matrix")
    _require_same_candidate_set(by_id, candidate_ids, "compatibility_matrix")
    normalized = []
    for candidate_id in sorted(by_id):
        item = by_id[candidate_id]
        dimensions = _require_dict(item.get("dimensions"), "compatibility dimensions")
        if set(dimensions) != set(COMPATIBILITY_DIMENSIONS):
            raise FailClosedRuntimeError("compatibility dimensions are incomplete")
        normalized_dimensions = {}
        for dimension in COMPATIBILITY_DIMENSIONS:
            result = dimensions.get(dimension)
            if result not in COMPATIBILITY_RESULTS:
                raise FailClosedRuntimeError("compatibility result is invalid")
            if result == "UNKNOWN_BLOCKED":
                raise FailClosedRuntimeError("compatibility is unknown")
            normalized_dimensions[dimension] = result
        normalized.append(
            {
                "candidate_id": candidate_id,
                "dimensions": normalized_dimensions,
                "evidence_refs": _canonical_strings(
                    item.get("evidence_refs"), "compatibility evidence", require_nonempty=True
                ),
            }
        )
    return normalized


def _validate_extension_ladder(value: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(value) > len(EXTENSION_RUNGS):
        raise FailClosedRuntimeError("extension ladder has too many rungs")
    normalized = []
    for index, item in enumerate(value):
        if not isinstance(item, dict) or item.get("rung") != EXTENSION_RUNGS[index]:
            raise FailClosedRuntimeError("extension ladder ordering is invalid")
        result = item.get("result")
        if result not in EXTENSION_RESULTS:
            raise FailClosedRuntimeError("extension ladder result is invalid")
        if result == "UNKNOWN_BLOCKED":
            raise FailClosedRuntimeError("extension feasibility is unknown")
        normalized.append(
            {
                "rung": EXTENSION_RUNGS[index],
                "result": result,
                "candidate_id": _optional_string(item.get("candidate_id")),
                "owner": _optional_string(item.get("owner")),
                "reason": _require_string(item.get("reason"), "extension reason"),
                "evidence_refs": _canonical_strings(
                    item.get("evidence_refs"), "extension evidence", require_nonempty=True
                ),
            }
        )
        if result == "FEASIBLE" and index != len(value) - 1:
            raise FailClosedRuntimeError("extension ladder continued after a feasible rung")
    return normalized


def _validate_duplicate_matrix(
    value: list[dict[str, Any]], candidate_ids: tuple[str, ...]
) -> list[dict[str, Any]]:
    normalized = []
    known = set(candidate_ids)
    for item in _sort_duplicate_records(value):
        overlap_type = item.get("overlap_type")
        feasibility = item.get("consolidation_feasibility")
        if overlap_type not in DUPLICATE_TYPES:
            raise FailClosedRuntimeError("duplicate overlap type is invalid")
        if feasibility not in CONSOLIDATION_RESULTS:
            raise FailClosedRuntimeError("duplicate consolidation result is invalid")
        if feasibility == "UNKNOWN_BLOCKED":
            raise FailClosedRuntimeError("duplicate consolidation is unknown")
        ids = _canonical_strings(
            item.get("candidate_ids"), "duplicate candidate_ids", require_nonempty=True
        )
        if not set(ids) <= known:
            raise FailClosedRuntimeError("duplicate matrix references an unknown candidate")
        resolved = item.get("owner_conflict_resolved")
        if not isinstance(resolved, bool):
            raise FailClosedRuntimeError("duplicate owner conflict disposition is required")
        if overlap_type in {"AUTHORITY_DUPLICATE", "REGISTRY_DUPLICATE", "ROUTING_DUPLICATE", "EVIDENCE_DUPLICATE"} and not resolved:
            raise FailClosedRuntimeError("duplicate authority remains unresolved")
        normalized.append(
            {
                "candidate_ids": ids,
                "overlap_type": overlap_type,
                "consolidation_feasibility": feasibility,
                "owner_conflict_resolved": resolved,
                "evidence_refs": _canonical_strings(
                    item.get("evidence_refs"), "duplicate evidence", require_nonempty=True
                ),
            }
        )
    return normalized


def _validate_negative_evidence(value: dict[str, Any]) -> dict[str, Any]:
    item = _require_dict(value, "negative_evidence")
    return {
        "reuse_rejected": _canonical_strings(
            item.get("reuse_rejected"), "reuse_rejected", require_nonempty=False
        ),
        "extend_rejected": _canonical_strings(
            item.get("extend_rejected"), "extend_rejected", require_nonempty=False
        ),
        "consolidate_rejected": _canonical_strings(
            item.get("consolidate_rejected"),
            "consolidate_rejected",
            require_nonempty=False,
        ),
        "absence_scope": _canonical_strings(
            item.get("absence_scope"), "absence_scope", require_nonempty=False
        ),
        "proposed_ownership": deepcopy(
            _require_dict(item.get("proposed_ownership"), "proposed_ownership")
        ),
    }


def _validate_evolution_evidence(value: dict[str, Any]) -> dict[str, Any]:
    item = _require_dict(value, "evolution_evidence")
    normalized = {}
    for field in EVOLUTION_FIELDS:
        if not isinstance(item.get(field), bool):
            raise FailClosedRuntimeError(f"evolution evidence {field} must be boolean")
        normalized[field] = item[field]
    normalized["evidence_refs"] = _canonical_strings(
        item.get("evidence_refs"), "evolution evidence refs", require_nonempty=True
    )
    return normalized


def _validate_named_evidence_map(value: dict[str, Any], label: str) -> dict[str, Any]:
    item = _require_dict(value, label)
    for field in ("authority_delta", "ownership_delta", "dependency_delta"):
        _require_string(item.get(field), f"{label}.{field}")
    evidence_refs = _canonical_strings(
        item.get("evidence_refs"), f"{label}.evidence_refs", require_nonempty=True
    )
    return {
        "authority_delta": item["authority_delta"],
        "ownership_delta": item["ownership_delta"],
        "dependency_delta": item["dependency_delta"],
        "evidence_refs": evidence_refs,
    }


def _validate_lifecycle_evidence(value: dict[str, Any]) -> dict[str, Any]:
    item = _require_dict(value, "migration_rollback_deprecation")
    normalized = {
        field: _require_string(item.get(field), field)
        for field in ("migration", "rollback", "deprecation")
    }
    normalized["evidence_refs"] = _canonical_strings(
        item.get("evidence_refs"), "lifecycle evidence refs", require_nonempty=True
    )
    return normalized


def _validate_registered_candidate_bindings(
    *,
    inventory: list[dict[str, Any]],
    ownership: list[dict[str, Any]],
    registries: list[dict[str, Any]],
    usage: list[dict[str, Any]],
    registry_by_id: dict[str, dict[str, Any]],
) -> None:
    owner_by_id = {item["candidate_id"]: item["roles"] for item in ownership}
    registry_item_by_id = {item["candidate_id"]: item for item in registries}
    usage_by_id = {item["candidate_id"]: item for item in usage}
    for candidate in inventory:
        candidate_id = candidate["candidate_id"]
        registry_item = registry_item_by_id[candidate_id]
        if registry_item["registry_id"] != "PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY":
            continue
        record = registry_by_id.get(candidate_id)
        if record is None:
            raise FailClosedRuntimeError("registered candidate is absent from G15")
        if registry_item["registry_version"] != PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION:
            raise FailClosedRuntimeError("candidate registry version mismatch")
        if registry_item["record_hash"] != record["certification_record_hash"]:
            raise FailClosedRuntimeError("candidate certification record hash mismatch")
        if registry_item["status"] != record["certification_status"]:
            raise FailClosedRuntimeError("candidate certification status mismatch")
        roles = owner_by_id[candidate_id]
        if roles["architectural_owner"] != record["architectural_owner"]:
            raise FailClosedRuntimeError("candidate architectural owner mismatch")
        if roles["authority_owner"] != record["capability_owner"]:
            raise FailClosedRuntimeError("candidate authority owner mismatch")
        if roles["implementation_owner"] != record["implementation_owner"]:
            raise FailClosedRuntimeError("candidate implementation owner mismatch")
        if usage_by_id[candidate_id]["module"] != record["implementation_owner"]:
            raise FailClosedRuntimeError("candidate implementation module mismatch")


def _reduce_decision(
    *,
    inventory: list[dict[str, Any]],
    equivalence: list[dict[str, Any]],
    compatibility: list[dict[str, Any]],
    ladder: list[dict[str, Any]],
    duplicates: list[dict[str, Any]],
    negative_evidence: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    inventory_by_id = {item["candidate_id"]: item for item in inventory}
    equivalence_by_id = {item["candidate_id"]: item for item in equivalence}
    compatibility_by_id = {item["candidate_id"]: item for item in compatibility}
    active_ids = {
        candidate_id
        for candidate_id, item in inventory_by_id.items()
        if item["active"]
        and item["public_contract"]
        and not set(item["maturity"]).intersection(
            {"DEPRECATED", "HISTORICAL_ONLY", "UNVERIFIED", "TEST_ONLY"}
        )
    }
    blocking_duplicates = [
        item
        for item in duplicates
        if item["overlap_type"]
        in {
            "EXACT_DUPLICATE",
            "FUNCTIONAL_DUPLICATE",
            "AUTHORITY_DUPLICATE",
            "REGISTRY_DUPLICATE",
            "ROUTING_DUPLICATE",
            "EVIDENCE_DUPLICATE",
        }
        and item["consolidation_feasibility"] != "NOT_APPLICABLE"
    ]
    direct = []
    for candidate_id in sorted(active_ids):
        eq = equivalence_by_id[candidate_id]
        comp = compatibility_by_id[candidate_id]
        if eq["disposition"] == "EXACT_EQUIVALENT" and all(
            result == "DIRECTLY_COMPATIBLE"
            for result in comp["dimensions"].values()
        ):
            direct.append(candidate_id)
    if len(direct) == 1 and not blocking_duplicates:
        if ladder:
            raise FailClosedRuntimeError("direct reuse must not require extension analysis")
        return REUSE, {"candidate_ids": direct, "owner_preserved": True}
    if len(direct) > 1:
        raise FailClosedRuntimeError("multiple direct equivalents require duplicate disposition")

    feasible = [item for item in ladder if item["result"] == "FEASIBLE"]
    if feasible:
        selected = feasible[0]
        rung_index = EXTENSION_RUNGS.index(selected["rung"])
        if rung_index < 5:
            candidate_id = selected["candidate_id"]
            if candidate_id not in active_ids:
                raise FailClosedRuntimeError("extension target is not an active existing owner")
            comp_results = set(compatibility_by_id[candidate_id]["dimensions"].values())
            if "INCOMPATIBLE" in comp_results:
                raise FailClosedRuntimeError("incompatible candidate cannot be extended")
            return EXTEND, {
                "candidate_ids": [candidate_id],
                "extension_rung": selected["rung"],
                "owner": selected["owner"],
                "owner_preserved": True,
            }
        feasible_duplicates = [
            item for item in duplicates if item["consolidation_feasibility"] == "FEASIBLE"
        ]
        if not feasible_duplicates:
            raise FailClosedRuntimeError("consolidation lacks feasible duplicate evidence")
        selected_ids = sorted(
            {
                candidate_id
                for item in feasible_duplicates
                for candidate_id in item["candidate_ids"]
            }
        )
        if not selected_ids:
            raise FailClosedRuntimeError("consolidation target is absent")
        return CONSOLIDATE, {
            "candidate_ids": selected_ids,
            "extension_rung": selected["rung"],
            "owner": selected["owner"],
            "owner_preserved": True,
        }

    if len(ladder) != len(EXTENSION_RUNGS) or any(
        item["result"] != "INFEASIBLE" for item in ladder
    ):
        raise FailClosedRuntimeError("proof has no supported reuse outcome")
    for field in ("reuse_rejected", "extend_rejected", "consolidate_rejected", "absence_scope"):
        if not negative_evidence[field]:
            raise FailClosedRuntimeError("CREATE_NEW rejection package is incomplete")
    proposed = negative_evidence["proposed_ownership"]
    for role in OWNERSHIP_ROLES:
        _require_string(proposed.get(role), f"proposed_ownership.{role}")
    proposed_consumers = _canonical_strings(
        proposed.get("consumers"), "proposed_ownership.consumers", require_nonempty=True
    )
    return CREATE_NEW, {
        "candidate_ids": [],
        "proposed_ownership": {**deepcopy(proposed), "consumers": proposed_consumers},
        "owner_preserved": False,
    }


def _classify_evolution(*, decision: str, evidence: dict[str, Any]) -> str:
    if decision == REUSE:
        return "NO_CHANGE_REQUIRED"
    if all(evidence[field] for field in EVOLUTION_FIELDS):
        return "ADDITIVE_EXTENSION"
    if not evidence["authority_unchanged"] or not evidence["owner_unchanged"] or not evidence["defaults_unchanged"]:
        return "CONSTITUTIONAL_MODIFICATION"
    return "VERSIONED_EXTENSION"


def _validate_decision_lifecycle(
    *,
    decision: str,
    authority_delta: dict[str, Any],
    lifecycle: dict[str, Any],
) -> None:
    if decision == REUSE:
        if authority_delta["authority_delta"] != "NONE" or authority_delta["ownership_delta"] != "NONE" or authority_delta["dependency_delta"] != "NONE":
            raise FailClosedRuntimeError("REUSE cannot contain authority or dependency deltas")
    for field in ("migration", "rollback", "deprecation"):
        if not lifecycle[field]:
            raise FailClosedRuntimeError("lifecycle evidence is incomplete")


def _normalize_baseline(value: Any) -> dict[str, Any]:
    baseline = _require_dict(value, "authenticated_baseline")
    normalized = {
        "commit": _require_sha1(baseline.get("commit"), "baseline commit"),
        "parent": _require_sha1(baseline.get("parent"), "baseline parent"),
        "tree": _require_sha1(baseline.get("tree"), "baseline tree"),
        "worktree_clean": baseline.get("worktree_clean"),
        "governing_sources": _normalize_governing_sources(
            baseline.get("governing_sources")
        ),
        "known_limitations": _canonical_strings(
            baseline.get("known_limitations"),
            "baseline known_limitations",
            require_nonempty=False,
        ),
    }
    if normalized["worktree_clean"] is not True:
        raise FailClosedRuntimeError("reuse proof baseline must be clean")
    return normalized


def _normalize_governing_sources(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, (list, tuple)) or not value:
        raise FailClosedRuntimeError("governing_sources must be non-empty")
    normalized = []
    seen = set()
    for item in value:
        record = _require_dict(item, "governing source")
        path = _require_string(record.get("path"), "governing source path")
        if path in seen:
            raise FailClosedRuntimeError("governing source is duplicated")
        seen.add(path)
        normalized.append(
            {"path": path, "sha256": _require_hash(record.get("sha256"), "sha256")}
        )
    return sorted(normalized, key=lambda item: item["path"])


def _sort_records(value: Any, key: str) -> list[dict[str, Any]]:
    if not isinstance(value, (list, tuple)):
        raise FailClosedRuntimeError(f"records for {key} must be a list")
    records = []
    for item in value:
        record = _require_dict(item, key)
        _require_string(record.get(key), key)
        records.append(deepcopy(record))
    if len({item[key] for item in records}) != len(records):
        raise FailClosedRuntimeError(f"duplicate {key}")
    return sorted(records, key=lambda item: item[key])


def _sort_duplicate_records(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, (list, tuple)):
        raise FailClosedRuntimeError("duplicate_matrix must be a list")
    records = []
    for item in value:
        record = _require_dict(item, "duplicate matrix item")
        records.append(deepcopy(record))
    return sorted(
        records,
        key=lambda item: (
            str(item.get("overlap_type") or ""),
            tuple(sorted(str(value) for value in item.get("candidate_ids") or [])),
        ),
    )


def _unique_by(
    value: list[dict[str, Any]], key: str, label: str
) -> dict[str, dict[str, Any]]:
    if not isinstance(value, list):
        raise FailClosedRuntimeError(f"{label} must be a list")
    result = {}
    for item in value:
        record = _require_dict(item, label)
        identity = _require_string(record.get(key), key)
        if identity in result:
            raise FailClosedRuntimeError(f"{label} contains duplicate {key}")
        result[identity] = record
    return result


def _require_same_candidate_set(
    by_id: dict[str, Any], candidate_ids: tuple[str, ...], label: str
) -> None:
    if set(by_id) != set(candidate_ids):
        raise FailClosedRuntimeError(f"{label} candidate coverage mismatch")


def _canonical_strings(
    value: Any,
    field: str,
    *,
    require_nonempty: bool,
) -> list[str]:
    if not isinstance(value, (list, tuple)):
        raise FailClosedRuntimeError(f"{field} must be a list")
    normalized = sorted({_require_string(item, field) for item in value})
    if require_nonempty and not normalized:
        raise FailClosedRuntimeError(f"{field} must be non-empty")
    return normalized


def _require_dict(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FailClosedRuntimeError(f"{field} must be a dict")
    return deepcopy(value)


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field} is required")
    return value.strip()


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    return _require_string(value, "optional string")


def _require_hash(value: Any, field: str) -> str:
    text = _require_string(value, field)
    if not _SHA256_PATTERN.fullmatch(text):
        raise FailClosedRuntimeError(f"{field} must be a sha256 hash")
    return text


def _require_sha1(value: Any, field: str) -> str:
    text = _require_string(value, field)
    if not _SHA1_PATTERN.fullmatch(text):
        raise FailClosedRuntimeError(f"{field} must be a 40-character Git identity")
    return text


def _verify_named_hash(artifact: dict[str, Any], field: str, label: str) -> None:
    _require_hash(artifact.get(field), field)
    body = deepcopy(artifact)
    actual = body.pop(field)
    if replay_hash(body) != actual:
        raise FailClosedRuntimeError(f"{label} hash mismatch")


__all__ = [
    "COMPATIBILITY_DIMENSIONS",
    "CONSOLIDATE",
    "CONSTITUTIONAL_REUSE_PROOF_RUNTIME_VERSION",
    "CREATE_NEW",
    "DECISIONS",
    "EXTEND",
    "EXTENSION_RUNGS",
    "PROOF_COMPLETE_FOR_EVOLUTION_PLANNING",
    "REUSE",
    "compose_constitutional_reuse_proof_input",
    "create_constitutional_reuse_proof_input",
    "create_responsibility_signature",
    "evaluate_constitutional_reuse_proof",
    "project_reuse_proof_to_development_governance",
    "validate_constitutional_reuse_proof_input",
    "validate_constitutional_reuse_proof_result",
    "validate_responsibility_signature",
    "validate_reuse_proof_g47_handoff",
]
