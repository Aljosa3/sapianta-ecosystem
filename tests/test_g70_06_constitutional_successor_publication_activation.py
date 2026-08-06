from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

import pytest

from aigol.runtime.constitutional_amendment_certification_contract_v1 import (
    CONSTITUTIONAL_AMENDMENT_CERTIFIED_NOT_ACTIVATED,
    validate_constitutional_amendment_certification_artifact_v1,
)
from aigol.runtime.constitutional_human_ratification_contract_v1 import (
    CONSTITUTIONAL_GOVERNANCE_OWNER,
)
from aigol.runtime.constitutional_impact_assessment_contract_v1 import (
    OWNER_LOCAL_REPLAY_CUSTODIAN,
)
from aigol.runtime.constitutional_successor_publication_activation_contract_v1 import (
    COMPATIBILITY_EVIDENCE,
    CONSTITUTIONAL_SUCCESSOR_ARTIFACT_VERSION,
    CONSTITUTIONAL_SUCCESSOR_COMPATIBILITY_OBLIGATIONS,
    CONSTITUTIONAL_SUCCESSOR_MIGRATION_OBLIGATIONS,
    CONSTITUTIONAL_SUCCESSOR_NORMATIVELY_ACTIVE_RUNTIME_NOT_IMPLEMENTED,
    CONSTITUTIONAL_SUCCESSOR_PUBLICATION_ACTIVATION_CONTRACT_VERSION,
    CONSTITUTIONAL_SUCCESSOR_PUBLISHED,
    CONSTITUTIONAL_SUCCESSOR_PUBLISHED_AND_NORMATIVELY_ACTIVE,
    CONSTITUTIONAL_SUCCESSOR_SERIALIZATION_VERSION,
    MIGRATION_PLAN_EVIDENCE,
    PREDECESSOR_RETENTION_EVIDENCE,
    PREDECESSOR_SUPERSEDED_RETAINED_IMMUTABLE,
    ROLLBACK_ELIGIBILITY_EVIDENCE,
    ROLLBACK_ELIGIBLE,
    ROLLBACK_INELIGIBILITY_EVIDENCE,
    ROLLBACK_NOT_ELIGIBLE,
    ConstitutionalSuccessorMigrationEvidenceReferenceV1,
    create_constitutional_pre_activation_lineage_state_v1,
    deserialize_constitutional_successor_publication_activation_v1,
    publish_and_activate_constitutional_successor_v1,
    serialize_constitutional_successor_publication_activation_v1,
    validate_constitutional_activation_scope_v1,
    validate_constitutional_pre_activation_lineage_state_v1,
    validate_constitutional_successor_activation_record_v1,
    validate_constitutional_successor_migration_evidence_reference_v1,
    validate_constitutional_successor_publication_activation_v1,
    validate_constitutional_successor_publication_record_v1,
)
from aigol.runtime.models import FailClosedRuntimeError


MODULE = Path(
    "aigol/runtime/constitutional_successor_publication_activation_contract_v1.py"
)
OBSERVED_AT = "2026-08-05T16:05:00Z"
PUBLISHED_AT = "2026-08-05T16:10:00Z"
EFFECTIVE_AT = "2026-08-05T16:15:00Z"


def _load_g70_05_fixture_module():
    path = Path(
        "tests/test_g70_05_constitutional_amendment_certification_contract.py"
    )
    spec = importlib.util.spec_from_file_location("g70_05_fixture", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


G70_05 = _load_g70_05_fixture_module()


def _digest(value: str) -> str:
    return "sha256:" + sha256(value.encode("utf-8")).hexdigest()


def _certification():
    certification = G70_05._certify()
    assert certification.certification_status == (
        CONSTITUTIONAL_AMENDMENT_CERTIFIED_NOT_ACTIVATED
    )
    return validate_constitutional_amendment_certification_artifact_v1(
        certification
    )


def _proposal(certification):
    return certification.human_ratification.impact_assessment.amendment_proposal


def _lineage(
    certification=None,
    *,
    claims=(),
    identity=None,
    version=None,
    digest=None,
):
    certification = certification or _certification()
    proposal = _proposal(certification)
    return create_constitutional_pre_activation_lineage_state_v1(
        governing_owner=CONSTITUTIONAL_GOVERNANCE_OWNER,
        active_constitution_identity=(
            identity or proposal.target_constitutional_artifact_identity
        ),
        active_constitution_version=(
            version or proposal.target_constitutional_artifact_version
        ),
        active_constitution_digest=(
            digest or proposal.target_constitutional_artifact_digest
        ),
        claimed_active_successor_identities=claims,
        observed_at=OBSERVED_AT,
    )


def _reference(role, owner, identity):
    return ConstitutionalSuccessorMigrationEvidenceReferenceV1(
        evidence_role=role,
        producing_owner=owner,
        artifact_identity=identity,
        artifact_digest=_digest(identity),
    )


def _evidence(certification, rollback_eligibility=ROLLBACK_ELIGIBLE):
    proposal = _proposal(certification)
    rollback_role = (
        ROLLBACK_ELIGIBILITY_EVIDENCE
        if rollback_eligibility == ROLLBACK_ELIGIBLE
        else ROLLBACK_INELIGIBILITY_EVIDENCE
    )
    return (
        _reference(
            MIGRATION_PLAN_EVIDENCE,
            proposal.target_constitutional_owner,
            "G70-06-MIGRATION-PLAN",
        ),
        _reference(
            COMPATIBILITY_EVIDENCE,
            proposal.target_constitutional_owner,
            "G70-06-COMPATIBILITY",
        ),
        _reference(
            PREDECESSOR_RETENTION_EVIDENCE,
            OWNER_LOCAL_REPLAY_CUSTODIAN,
            "G70-06-PREDECESSOR-RETENTION",
        ),
        _reference(
            rollback_role,
            proposal.target_constitutional_owner,
            "G70-06-ROLLBACK-ELIGIBILITY",
        ),
    )


def _activate(
    certification=None,
    lineage=None,
    evidence=None,
    rollback_eligibility=ROLLBACK_ELIGIBLE,
    **overrides,
):
    certification = certification or _certification()
    lineage = lineage or _lineage(certification)
    evidence = (
        evidence
        if evidence is not None
        else _evidence(certification, rollback_eligibility)
    )
    return publish_and_activate_constitutional_successor_v1(
        certified_amendment=certification,
        pre_activation_lineage_state=lineage,
        publishing_owner=overrides.get(
            "publishing_owner", CONSTITUTIONAL_GOVERNANCE_OWNER
        ),
        activating_owner=overrides.get(
            "activating_owner", CONSTITUTIONAL_GOVERNANCE_OWNER
        ),
        migration_evidence_references=evidence,
        rollback_eligibility=rollback_eligibility,
        published_at=overrides.get("published_at", PUBLISHED_AT),
        effective_at=overrides.get("effective_at", EFFECTIVE_AT),
    )


def test_successor_is_immutable_versioned_published_and_normatively_active():
    successor = _activate()

    assert successor.contract_version == (
        CONSTITUTIONAL_SUCCESSOR_PUBLICATION_ACTIVATION_CONTRACT_VERSION
    )
    assert successor.artifact_version == CONSTITUTIONAL_SUCCESSOR_ARTIFACT_VERSION
    assert successor.serialization_version == (
        CONSTITUTIONAL_SUCCESSOR_SERIALIZATION_VERSION
    )
    assert successor.successor_status == (
        CONSTITUTIONAL_SUCCESSOR_PUBLISHED_AND_NORMATIVELY_ACTIVE
    )
    assert successor.publication_record.publication_status == (
        CONSTITUTIONAL_SUCCESSOR_PUBLISHED
    )
    assert successor.activation_record.activation_status == (
        CONSTITUTIONAL_SUCCESSOR_NORMATIVELY_ACTIVE_RUNTIME_NOT_IMPLEMENTED
    )
    with pytest.raises(FrozenInstanceError):
        successor.successor_status = "MUTATED"


def test_exact_g70_01_through_g70_05_chain_and_predecessor_are_bound():
    certification = _certification()
    successor = _activate(certification)
    proposal = _proposal(certification)

    assert successor.certified_amendment == certification
    assert successor.predecessor_constitution_identity == (
        proposal.target_constitutional_artifact_identity
    )
    assert successor.predecessor_constitution_version == (
        proposal.target_constitutional_artifact_version
    )
    assert successor.predecessor_constitution_digest == (
        proposal.target_constitutional_artifact_digest
    )
    assert successor.successor_constitution_version == (
        proposal.proposed_successor_version
    )
    assert successor.successor_normative_change_statement == (
        proposal.normative_change_statement
    )
    assert successor.activation_scope.target_constitutional_artifact_identity == (
        proposal.target_constitutional_artifact_identity
    )


def test_successor_publication_activation_and_serialization_are_deterministic():
    certification = _certification()
    lineage = _lineage(certification)
    evidence = _evidence(certification)
    first = _activate(certification, lineage, evidence)
    second = _activate(certification, lineage, evidence)

    assert first == second
    assert first.successor_constitution_identity == (
        second.successor_constitution_identity
    )
    assert first.publication_record == second.publication_record
    assert first.activation_record == second.activation_record
    assert first.successor_artifact_identity == second.successor_artifact_identity
    assert first.artifact_digest == second.artifact_digest


@pytest.mark.parametrize(
    ("identity", "version", "digest"),
    (
        ("STALE-CONSTITUTION", None, None),
        (None, "STALE-VERSION", None),
        (None, None, "sha256:" + ("0" * 64)),
    ),
)
def test_stale_predecessor_identity_version_or_digest_fails_closed(
    identity,
    version,
    digest,
):
    certification = _certification()
    stale = _lineage(
        certification,
        identity=identity,
        version=version,
        digest=digest,
    )

    with pytest.raises(FailClosedRuntimeError, match="identity or version is stale"):
        _activate(certification, stale)


@pytest.mark.parametrize(
    "claims",
    (
        ("CONFLICTING-SUCCESSOR",),
        ("CONFLICTING-SUCCESSOR-A", "CONFLICTING-SUCCESSOR-B"),
    ),
)
def test_any_existing_active_successor_claim_fails_closed(claims):
    certification = _certification()
    conflicting = _lineage(certification, claims=claims)

    with pytest.raises(FailClosedRuntimeError, match="already claims"):
        _activate(certification, conflicting)


def test_successor_identity_conflict_and_scope_expansion_fail_closed():
    successor = _activate()

    with pytest.raises(FailClosedRuntimeError, match="successor identity is invalid"):
        validate_constitutional_successor_publication_activation_v1(
            replace(
                successor,
                successor_constitution_identity="CONFLICTING-SUCCESSOR",
            )
        )
    with pytest.raises(FailClosedRuntimeError, match="scope exceeds"):
        validate_constitutional_successor_publication_activation_v1(
            replace(
                successor,
                activation_scope=replace(
                    successor.activation_scope,
                    target_constitutional_owner="EXPANDED-OWNER",
                ),
            )
        )


def test_existing_governance_owner_is_required_for_publication_and_activation():
    with pytest.raises(FailClosedRuntimeError, match="owner is invalid"):
        _activate(publishing_owner="INVENTED-PUBLICATION-OWNER")
    with pytest.raises(FailClosedRuntimeError, match="owner is invalid"):
        _activate(activating_owner="INVENTED-ACTIVATION-OWNER")
    certification = _certification()
    proposal = _proposal(certification)
    with pytest.raises(FailClosedRuntimeError, match="state owner is invalid"):
        create_constitutional_pre_activation_lineage_state_v1(
            governing_owner="INVENTED-LINEAGE-OWNER",
            active_constitution_identity=(
                proposal.target_constitutional_artifact_identity
            ),
            active_constitution_version=(
                proposal.target_constitutional_artifact_version
            ),
            active_constitution_digest=(
                proposal.target_constitutional_artifact_digest
            ),
            claimed_active_successor_identities=(),
            observed_at=OBSERVED_AT,
        )


def test_migration_evidence_is_complete_ordered_owner_bound_and_public():
    certification = _certification()
    evidence = _evidence(certification)
    first = evidence[0]

    assert (
        validate_constitutional_successor_migration_evidence_reference_v1(
            value=first.to_dict(),
            expected_role=first.evidence_role,
            expected_owner=first.producing_owner,
            expected_artifact_identity=first.artifact_identity,
            expected_artifact_digest=first.artifact_digest,
        )
        == first
    )
    with pytest.raises(FailClosedRuntimeError, match="incomplete"):
        _activate(certification, evidence=evidence[:-1])
    with pytest.raises(FailClosedRuntimeError, match="order is not canonical"):
        _activate(certification, evidence=tuple(reversed(evidence)))
    with pytest.raises(FailClosedRuntimeError, match="role or owner is invalid"):
        _activate(
            certification,
            evidence=(
                replace(first, producing_owner="WRONG-OWNER"),
                *evidence[1:],
            ),
        )


def test_rollback_eligibility_is_explicit_evidenced_and_targets_predecessor():
    certification = _certification()
    eligible = _activate(certification, rollback_eligibility=ROLLBACK_ELIGIBLE)
    ineligible = _activate(
        certification,
        rollback_eligibility=ROLLBACK_NOT_ELIGIBLE,
    )

    assert eligible.rollback_eligibility == ROLLBACK_ELIGIBLE
    assert eligible.migration_evidence_references[-1].evidence_role == (
        ROLLBACK_ELIGIBILITY_EVIDENCE
    )
    assert ineligible.rollback_eligibility == ROLLBACK_NOT_ELIGIBLE
    assert ineligible.migration_evidence_references[-1].evidence_role == (
        ROLLBACK_INELIGIBILITY_EVIDENCE
    )
    for successor in (eligible, ineligible):
        assert successor.rollback_target_identity == (
            successor.predecessor_constitution_identity
        )
        assert successor.rollback_target_version == (
            successor.predecessor_constitution_version
        )
        assert successor.rollback_target_digest == (
            successor.predecessor_constitution_digest
        )

    with pytest.raises(FailClosedRuntimeError, match="order is not canonical"):
        _activate(
            certification,
            evidence=_evidence(certification, ROLLBACK_NOT_ELIGIBLE),
            rollback_eligibility=ROLLBACK_ELIGIBLE,
        )


def test_supersession_is_explicit_non_destructive_and_obligations_are_exact():
    successor = _activate()

    assert successor.predecessor_lifecycle_status == (
        PREDECESSOR_SUPERSEDED_RETAINED_IMMUTABLE
    )
    assert successor.predecessor_evidence_immutable is True
    assert successor.predecessor_history_rewritten is False
    assert successor.migration_obligations == (
        CONSTITUTIONAL_SUCCESSOR_MIGRATION_OBLIGATIONS
    )
    assert successor.compatibility_obligations == (
        CONSTITUTIONAL_SUCCESSOR_COMPATIBILITY_OBLIGATIONS
    )
    with pytest.raises(FailClosedRuntimeError, match="boundary invariants"):
        validate_constitutional_successor_publication_activation_v1(
            replace(successor, predecessor_history_rewritten=True)
        )


@pytest.mark.parametrize(
    ("published_at", "effective_at"),
    (
        ("2026-08-05T15:59:59Z", EFFECTIVE_AT),
        (PUBLISHED_AT, "2026-08-05T16:09:59Z"),
        ("not-a-time", EFFECTIVE_AT),
    ),
)
def test_certification_publication_activation_time_order_fails_closed(
    published_at,
    effective_at,
):
    with pytest.raises(FailClosedRuntimeError, match="temporal order|canonical UTC"):
        _activate(published_at=published_at, effective_at=effective_at)


def test_public_validators_round_trip_every_governed_record():
    successor = _activate()

    assert (
        validate_constitutional_pre_activation_lineage_state_v1(
            successor.pre_activation_lineage_state.to_dict()
        )
        == successor.pre_activation_lineage_state
    )
    assert (
        validate_constitutional_activation_scope_v1(
            value=successor.activation_scope.to_dict(),
            certification=successor.certified_amendment,
        )
        == successor.activation_scope
    )
    assert (
        validate_constitutional_successor_publication_record_v1(
            successor.publication_record.to_dict()
        )
        == successor.publication_record
    )
    assert (
        validate_constitutional_successor_activation_record_v1(
            successor.activation_record.to_dict()
        )
        == successor.activation_record
    )
    assert (
        validate_constitutional_successor_publication_activation_v1(
            successor.to_dict()
        )
        == successor
    )


def test_tampered_certification_publication_or_activation_fails_closed():
    successor = _activate()

    with pytest.raises(FailClosedRuntimeError, match="certification status"):
        _activate(
            certification=replace(
                successor.certified_amendment,
                certification_status="CERTIFICATION-TAMPERED",
            )
        )
    with pytest.raises(FailClosedRuntimeError, match="publication identity"):
        validate_constitutional_successor_publication_activation_v1(
            replace(
                successor,
                publication_record=replace(
                    successor.publication_record,
                    published_at="2026-08-05T16:11:00Z",
                ),
            )
        )
    with pytest.raises(FailClosedRuntimeError, match="activation record"):
        validate_constitutional_successor_publication_activation_v1(
            replace(
                successor,
                activation_record=replace(
                    successor.activation_record,
                    active_successor_count=2,
                ),
            )
        )


def test_serialization_is_canonical_versioned_and_tamper_evident():
    successor = _activate()
    serialized = serialize_constitutional_successor_publication_activation_v1(
        successor
    )

    assert (
        deserialize_constitutional_successor_publication_activation_v1(
            serialized
        )
        == successor
    )
    assert (
        deserialize_constitutional_successor_publication_activation_v1(
            serialized.encode("utf-8")
        )
        == successor
    )
    with pytest.raises(FailClosedRuntimeError, match="not canonical"):
        deserialize_constitutional_successor_publication_activation_v1(
            json.dumps(json.loads(serialized), indent=2, sort_keys=True)
        )
    expanded = json.loads(serialized)
    expanded["runtime_implementation"] = {"status": "ACTIVE"}
    with pytest.raises(FailClosedRuntimeError, match="successor artifact is malformed"):
        deserialize_constitutional_successor_publication_activation_v1(
            json.dumps(expanded, sort_keys=True, separators=(",", ":"))
        )


def test_normative_activation_preserves_runtime_and_production_topology():
    successor = _activate()

    assert successor.active_constitution_count == 1
    assert (
        successor.che_definition_count,
        successor.production_hic_family_count,
        successor.production_owner_chain_count,
        successor.production_path_count,
        successor.parallel_production_path_count,
    ) == (1, 1, 1, 1, 0)
    assert successor.constitutional_publication_performed is True
    assert successor.constitutional_activation_performed is True
    assert successor.runtime_implementation_performed is False
    assert successor.runtime_feature_activation_performed is False
    assert successor.runtime_mutation_performed is False
    assert successor.production_mutation_performed is False
    assert successor.owner_mutation_performed is False
    assert successor.che_mutation_performed is False
    assert successor.hic_mutation_performed is False
    assert successor.replay_authority_changed is False
    assert successor.cro_authority_changed is False
    assert successor.hic_semantic_capability_introduced is False
    assert successor.cap_exclusivity_certified is False


def test_contract_has_no_persistence_runtime_production_hic_or_closure_calls():
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert called_names.isdisjoint(
        {
            "open",
            "write_json_immutable",
            "run_human_interface_runtime_entry",
            "activate_runtime_feature",
            "mutate_runtime",
            "mutate_production",
            "certify_cap_exclusivity",
        }
    )
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert all(
        fragment not in module_name
        for module_name in imported_modules
        for fragment in (
            "production_runtime",
            "human_interface_runtime",
            "replay_runtime",
            "observatory",
        )
    )
    source = MODULE.read_text(encoding="utf-8").lower()
    assert "historical implementations" not in source
