from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

import aigol.runtime.constitutional_reuse_proof_runtime as reuse_runtime
from aigol.runtime.constitutional_reuse_proof_runtime import (
    COMPATIBILITY_DIMENSIONS,
    CONSOLIDATE,
    CREATE_NEW,
    EXTEND,
    EXTENSION_RUNGS,
    REUSE,
    RESPONSIBILITY_FIELDS,
    SEARCH_EVIDENCE_CLASSES,
    create_constitutional_reuse_proof_input,
    create_responsibility_signature,
    evaluate_constitutional_reuse_proof,
    project_reuse_proof_to_development_governance,
    validate_constitutional_reuse_proof_result,
    validate_reuse_proof_g47_handoff,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_certification_registry import (
    PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION,
    lookup_platform_capability_certification,
)
from aigol.runtime.transport.serialization import replay_hash


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
BASELINE = {
    "commit": "61fdd92849f7878b2fde1744c7459c2e0d009461",
    "parent": "760804c542fa8220f8d176443171a30c351711b0",
    "tree": "d6b1ab0ab392165be1dcc74e881fedb392eff14b",
    "worktree_clean": True,
    "governing_sources": [
        {
            "path": "docs/governance/G63_04_CONSTITUTIONAL_REUSE_PROOF_RUNTIME_COMPOSITION_AUDIT_REPORT_V1.md",
            "sha256": "sha256:36391ade93412bdd48ed9e139285b5bec815d2afdf930ed01ecedbd2c185d9bb",
        }
    ],
    "known_limitations": [
        "The runtime composes authenticated local owners and does not claim unavailable external evidence."
    ],
}


def _signature() -> dict:
    return create_responsibility_signature(
        semantic_responsibility=(
            "deterministically reconstruct registered platform capability knowledge"
        ),
        inputs=["authenticated repository", "bounded capability query"],
        outputs=["immutable reuse proof", "one four-token decision"],
        state_and_persistence="No state mutation; caller owns governed persistence.",
        authority="Development Governance owns reuse-proof evaluation only.",
        non_authorities=[
            "does not authorize implementation",
            "does not authorize execution",
            "does not replace Platform Core",
        ],
        boundary="Consumes authenticated owner evidence without inheriting owner authority.",
        determinism="Canonical ordering, fail-closed validation, and replay hashing.",
        evidence_and_replay="Carries source identities and an immutable evidence identity.",
        activation_and_lifecycle="Explicit governed invocation before evolution planning.",
    )


def _search_manifest() -> list[dict]:
    return [
        {
            "evidence_class": evidence_class,
            "scope": f"authenticated {evidence_class.lower()} scope",
            "method": "existing owner API or immutable repository observation",
            "observation": "scope searched and evidence disposition recorded",
            "status": "SEARCHED",
            "material": True,
            "limitation": None,
        }
        for evidence_class in SEARCH_EVIDENCE_CLASSES
    ]


def _registered_candidate(candidate_id: str) -> tuple[dict, dict, dict, dict]:
    record = lookup_platform_capability_certification(candidate_id)
    assert record is not None
    inventory = {
        "candidate_id": candidate_id,
        "candidate_type": "CERTIFIED_RUNTIME",
        "source_reference": record["certification_evidence"][0],
        "source_hash": record["certification_record_hash"],
        "maturity": ["CERTIFIED_METADATA", "EVIDENCE_PRODUCING", "RUNTIME_BOUND"],
        "active": True,
        "public_contract": True,
    }
    ownership = {
        "candidate_id": candidate_id,
        "roles": {
            "architectural_owner": record["architectural_owner"],
            "authority_owner": record["capability_owner"],
            "implementation_owner": record["implementation_owner"],
            "state_owner": record["capability_owner"],
            "registry_owner": "PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY",
            "evidence_replay_owner": "GOVERNANCE_REPORT_EVIDENCE",
            "lifecycle_owner": "DEVELOPMENT_GOVERNANCE",
            "human_owner": "HUMAN_AUTHORITY",
            "consumers": ["CONSTITUTIONAL_REUSE_PROOF_RUNTIME"],
        },
    }
    registry = {
        "candidate_id": candidate_id,
        "registry_id": "PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY",
        "registry_version": PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY_VERSION,
        "record_hash": record["certification_record_hash"],
        "status": record["certification_status"],
        "runtime_bound": True,
        "invocable": False,
        "authority": "GOVERNANCE_METADATA_ONLY",
        "consumers": ["PLATFORM_KNOWLEDGE_RUNTIME"],
    }
    usage = {
        "candidate_id": candidate_id,
        "module": record["implementation_owner"],
        "api": (
            "query_platform_knowledge"
            if candidate_id == "PLATFORM_KNOWLEDGE_RUNTIME"
            else "discover_platform_capability_composition_coverage"
        ),
        "status": "ACTIVE_CERTIFIED",
        "reachable": True,
        "default_route": False,
        "effects": ["READ_ONLY_GOVERNANCE_EVIDENCE"],
        "consumers": ["CONSTITUTIONAL_REUSE_PROOF_RUNTIME"],
        "assurance_refs": list(record["certification_evidence"]),
        "history_disposition": "CURRENT_NOT_SUPERSEDED",
    }
    return inventory, ownership, registry, usage


def _equivalence(candidate_id: str, disposition: str) -> dict:
    if disposition == "EXACT_EQUIVALENT":
        matched = list(RESPONSIBILITY_FIELDS)
        mismatched: list[str] = []
    elif disposition == "COMPLEMENTARY_FRAGMENT":
        matched = ["inputs", "outputs", "evidence_and_replay"]
        mismatched = ["semantic_responsibility", "boundary"]
    else:
        matched = ["semantic_responsibility", "authority", "boundary"]
        mismatched = ["inputs", "outputs"]
    return {
        "candidate_id": candidate_id,
        "disposition": disposition,
        "matched_fields": matched,
        "mismatched_fields": mismatched,
        "evidence_refs": [f"authenticated equivalence evidence for {candidate_id}"],
    }


def _compatibility(candidate_id: str, default: str) -> dict:
    return {
        "candidate_id": candidate_id,
        "dimensions": {dimension: default for dimension in COMPATIBILITY_DIMENSIONS},
        "evidence_refs": [f"authenticated compatibility evidence for {candidate_id}"],
    }


def _ladder(
    *,
    feasible_index: int | None,
    candidate_id: str | None,
    owner: str | None,
) -> list[dict]:
    limit = len(EXTENSION_RUNGS) if feasible_index is None else feasible_index + 1
    return [
        {
            "rung": rung,
            "result": "FEASIBLE" if index == feasible_index else "INFEASIBLE",
            "candidate_id": candidate_id if index == feasible_index else None,
            "owner": owner if index == feasible_index else None,
            "reason": f"authenticated feasibility disposition for rung {index + 1}",
            "evidence_refs": [f"extension-rung-{index + 1}-evidence"],
        }
        for index, rung in enumerate(EXTENSION_RUNGS[:limit])
    ]


def _negative(create_new: bool = False) -> dict:
    if not create_new:
        return {
            "reuse_rejected": [],
            "extend_rejected": [],
            "consolidate_rejected": [],
            "absence_scope": [],
            "proposed_ownership": {},
        }
    return {
        "reuse_rejected": ["all candidates rejected by signature field and owner evidence"],
        "extend_rejected": ["all six ordered extension rungs are infeasible"],
        "consolidate_rejected": ["no existing combination covers the responsibility"],
        "absence_scope": ["current historical dynamic external registry test deprecated"],
        "proposed_ownership": {
            "architectural_owner": "DEVELOPMENT_GOVERNANCE",
            "authority_owner": "DEVELOPMENT_GOVERNANCE",
            "implementation_owner": "BOUNDED_FUTURE_COMPONENT",
            "state_owner": "CALLER_OWNED_GOVERNED_EVIDENCE",
            "registry_owner": "NO_NEW_REGISTRY",
            "evidence_replay_owner": "GOVERNANCE_REPORT_EVIDENCE",
            "lifecycle_owner": "DEVELOPMENT_GOVERNANCE",
            "human_owner": "HUMAN_AUTHORITY",
            "consumers": ["FUTURE_G47_ASSESSMENT"],
        },
    }


def _proof_input(
    *,
    candidate_ids: tuple[str, ...] = ("PLATFORM_KNOWLEDGE_RUNTIME",),
    equivalence_disposition: str = "EXACT_EQUIVALENT",
    compatibility_result: str = "DIRECTLY_COMPATIBLE",
    extension_ladder: list[dict] | None = None,
    duplicate_matrix: list[dict] | None = None,
    create_new: bool = False,
) -> dict:
    inventories: list[dict] = []
    ownership: list[dict] = []
    registries: list[dict] = []
    usages: list[dict] = []
    for candidate_id in candidate_ids:
        inventory, owner, registry, usage = _registered_candidate(candidate_id)
        inventories.append(inventory)
        ownership.append(owner)
        registries.append(registry)
        usages.append(usage)
    owner_unchanged = not create_new
    return create_constitutional_reuse_proof_input(
        proof_id=f"G63-05-{equivalence_disposition}-{len(candidate_ids)}",
        responsibility_signature=_signature(),
        authenticated_baseline=deepcopy(BASELINE),
        target_layers=["L3_GOVERNANCE_SYSTEM"],
        search_manifest=_search_manifest(),
        capability_inventory=inventories,
        ownership_matrix=ownership,
        registry_matrix=registries,
        implementation_usage_graph=usages,
        equivalence_matrix=[
            _equivalence(candidate_id, equivalence_disposition)
            for candidate_id in candidate_ids
        ],
        compatibility_matrix=[
            _compatibility(candidate_id, compatibility_result)
            for candidate_id in candidate_ids
        ],
        extension_ladder=extension_ladder or [],
        duplicate_matrix=duplicate_matrix or [],
        negative_evidence=_negative(create_new=create_new),
        evolution_evidence={
            "existing_consumers_compatible": True,
            "defaults_unchanged": True,
            "schema_api_compatible": True,
            "authority_unchanged": True,
            "owner_unchanged": owner_unchanged,
            "state_replay_compatible": True,
            "registry_selection_unchanged": True,
            "rollback_without_migration": True,
            "evidence_refs": ["authenticated evolution classification evidence"],
        },
        authority_and_dependency_delta={
            "authority_delta": "NONE" if not create_new else "BOUNDED_NEW_OWNER_PROPOSED",
            "ownership_delta": "NONE" if not create_new else "BOUNDED_NEW_OWNER_PROPOSED",
            "dependency_delta": "NONE" if not create_new else "ONE_WAY_CONSUMER_DEPENDENCY",
            "evidence_refs": ["authority and dependency evidence"],
        },
        migration_rollback_deprecation={
            "migration": "NOT_REQUIRED",
            "rollback": "DISABLE_FUTURE_OPT_IN_SURFACE",
            "deprecation": "NO_EXISTING_SURFACE_DEPRECATED",
            "evidence_refs": ["lifecycle evidence"],
        },
        next_checkpoints=["G47_FRESH_DEVELOPMENT_GOVERNANCE_ASSESSMENT"],
        known_limitations=["No unavailable external source is inferred as absent."],
        created_at="2026-08-01T00:00:00Z",
    )


@pytest.fixture(scope="module")
def reuse_result() -> dict:
    return evaluate_constitutional_reuse_proof(
        proof_input=_proof_input(),
        repository_root=REPOSITORY_ROOT,
    )


@pytest.fixture
def frozen_existing_owner_evidence(monkeypatch: pytest.MonkeyPatch, reuse_result: dict) -> None:
    evidence = deepcopy(reuse_result["composition_evidence"])
    monkeypatch.setattr(
        reuse_runtime,
        "_compose_existing_owner_evidence",
        lambda **_: deepcopy(evidence),
    )


def test_reuse_composes_existing_owners_and_is_deterministic(reuse_result: dict) -> None:
    repeated = evaluate_constitutional_reuse_proof(
        proof_input=_proof_input(),
        repository_root=REPOSITORY_ROOT,
    )

    assert reuse_result == repeated
    assert reuse_result["decision"] == REUSE
    assert reuse_result["additive_or_versioned"] == "NO_CHANGE_REQUIRED"
    assert reuse_result["selected_target"]["candidate_ids"] == [
        "PLATFORM_KNOWLEDGE_RUNTIME"
    ]
    assert reuse_result["composition_evidence"]["existing_owners_reused"] == [
        "PLATFORM_CORE_PROJECT_SERVICES",
        "PLATFORM_CORE_KNOWLEDGE",
        "PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY",
        "PLATFORM_CORE_CAPABILITY_DISCOVERY",
        "AIGOL_CAPABILITY_AUDIT_RUNTIME",
        "GOVERNANCE_CONFORMANCE_ENGINE",
    ]
    assert reuse_result["provider_invoked"] is False
    assert reuse_result["worker_invoked"] is False
    assert reuse_result["repository_mutated"] is False


def test_first_feasible_owner_rung_returns_extend(
    frozen_existing_owner_evidence: None,
) -> None:
    proof_input = _proof_input(
        equivalence_disposition="SEMANTIC_EQUIVALENT_DIFFERENT_INTERFACE",
        compatibility_result="ADAPTER_COMPATIBLE",
        extension_ladder=_ladder(
            feasible_index=2,
            candidate_id="PLATFORM_KNOWLEDGE_RUNTIME",
            owner="PLATFORM_CORE_KNOWLEDGE",
        ),
    )

    result = evaluate_constitutional_reuse_proof(
        proof_input=proof_input,
        repository_root=REPOSITORY_ROOT,
    )

    assert result["decision"] == EXTEND
    assert result["selected_target"]["extension_rung"] == "REPRESENTATION_ADAPTER"
    assert result["selected_target"]["owner_preserved"] is True
    assert result["additive_or_versioned"] == "ADDITIVE_EXTENSION"


def test_owner_scoped_complementary_surfaces_return_consolidate(
    frozen_existing_owner_evidence: None,
) -> None:
    candidate_ids = (
        "PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_RUNTIME",
        "PLATFORM_KNOWLEDGE_RUNTIME",
    )
    proof_input = _proof_input(
        candidate_ids=candidate_ids,
        equivalence_disposition="COMPLEMENTARY_FRAGMENT",
        compatibility_result="ADAPTER_COMPATIBLE",
        extension_ladder=_ladder(
            feasible_index=5,
            candidate_id="PLATFORM_KNOWLEDGE_RUNTIME",
            owner="PLATFORM_CORE",
        ),
        duplicate_matrix=[
            {
                "candidate_ids": list(candidate_ids),
                "overlap_type": "COMPLEMENTARY_FRAGMENTATION",
                "consolidation_feasibility": "FEASIBLE",
                "owner_conflict_resolved": True,
                "evidence_refs": ["authenticated complementary coverage evidence"],
            }
        ],
    )

    result = evaluate_constitutional_reuse_proof(
        proof_input=proof_input,
        repository_root=REPOSITORY_ROOT,
    )

    assert result["decision"] == CONSOLIDATE
    assert result["selected_target"]["candidate_ids"] == sorted(candidate_ids)
    assert result["selected_target"]["owner_preserved"] is True


def test_complete_rejection_package_returns_create_new(
    frozen_existing_owner_evidence: None,
) -> None:
    proof_input = _proof_input(
        candidate_ids=(),
        extension_ladder=_ladder(
            feasible_index=None,
            candidate_id=None,
            owner=None,
        ),
        create_new=True,
    )

    result = evaluate_constitutional_reuse_proof(
        proof_input=proof_input,
        repository_root=REPOSITORY_ROOT,
    )

    assert result["decision"] == CREATE_NEW
    assert result["selected_target"]["candidate_ids"] == []
    assert result["selected_target"]["owner_preserved"] is False
    assert result["additive_or_versioned"] == "CONSTITUTIONAL_MODIFICATION"


def test_material_unknown_search_scope_fails_closed(
    frozen_existing_owner_evidence: None,
) -> None:
    proof_input = _proof_input()
    proof_input["search_manifest"][0]["status"] = "UNKNOWN_BLOCKED"
    proof_input["input_hash"] = replay_hash(
        {key: value for key, value in proof_input.items() if key != "input_hash"}
    )

    with pytest.raises(FailClosedRuntimeError, match="material repository search scope"):
        evaluate_constitutional_reuse_proof(
            proof_input=proof_input,
            repository_root=REPOSITORY_ROOT,
        )


def test_unknown_compatibility_fails_closed(
    frozen_existing_owner_evidence: None,
) -> None:
    proof_input = _proof_input()
    proof_input["compatibility_matrix"][0]["dimensions"]["AUTHORITY"] = "UNKNOWN_BLOCKED"
    proof_input["input_hash"] = replay_hash(
        {key: value for key, value in proof_input.items() if key != "input_hash"}
    )

    with pytest.raises(FailClosedRuntimeError, match="compatibility is unknown"):
        evaluate_constitutional_reuse_proof(
            proof_input=proof_input,
            repository_root=REPOSITORY_ROOT,
        )


def test_create_new_without_all_rejections_fails_closed(
    frozen_existing_owner_evidence: None,
) -> None:
    proof_input = _proof_input(
        candidate_ids=(),
        extension_ladder=_ladder(
            feasible_index=None,
            candidate_id=None,
            owner=None,
        ),
        create_new=True,
    )
    proof_input["negative_evidence"]["consolidate_rejected"] = []
    proof_input["input_hash"] = replay_hash(
        {key: value for key, value in proof_input.items() if key != "input_hash"}
    )

    with pytest.raises(FailClosedRuntimeError, match="rejection package is incomplete"):
        evaluate_constitutional_reuse_proof(
            proof_input=proof_input,
            repository_root=REPOSITORY_ROOT,
        )


def test_registered_owner_claim_must_match_g15(
    frozen_existing_owner_evidence: None,
) -> None:
    proof_input = _proof_input()
    proof_input["ownership_matrix"][0]["roles"]["authority_owner"] = "WRONG_OWNER"
    proof_input["input_hash"] = replay_hash(
        {key: value for key, value in proof_input.items() if key != "input_hash"}
    )

    with pytest.raises(FailClosedRuntimeError, match="authority owner mismatch"):
        evaluate_constitutional_reuse_proof(
            proof_input=proof_input,
            repository_root=REPOSITORY_ROOT,
        )


def test_result_validator_recomputes_decision_and_integrity(reuse_result: dict) -> None:
    tampered = deepcopy(reuse_result)
    tampered["decision"] = CREATE_NEW
    tampered["evidence_identity"] = replay_hash(
        {key: value for key, value in tampered.items() if key != "evidence_identity"}
    )

    with pytest.raises(FailClosedRuntimeError, match="does not follow the reducer"):
        validate_constitutional_reuse_proof_result(tampered)


def test_g47_projection_is_hash_bound_and_never_grants_authority(
    reuse_result: dict,
) -> None:
    handoff = project_reuse_proof_to_development_governance(reuse_result)

    assert handoff["g47_action"] == "RUN_FRESH_DEVELOPMENT_GOVERNANCE_ASSESSMENT"
    assert handoff["g47_need_assessment_precomputed"] is False
    assert handoff["g47_planning_eligible"] is False
    assert handoff["authorizes_planning"] is False
    assert handoff["authorizes_implementation"] is False
    assert handoff["authorizes_execution"] is False

    tampered = deepcopy(handoff)
    tampered["authorizes_implementation"] = True
    tampered["artifact_hash"] = replay_hash(
        {key: value for key, value in tampered.items() if key != "artifact_hash"}
    )
    with pytest.raises(FailClosedRuntimeError, match="authority mismatch"):
        validate_reuse_proof_g47_handoff(tampered)
