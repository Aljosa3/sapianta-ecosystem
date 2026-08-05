from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from hashlib import sha256
import json
from pathlib import Path

import pytest

from aigol.runtime.constitutional_amendment_proposal_contract_v1 import (
    CONSTITUTIONAL_AMENDMENT_PROPOSAL_ARTIFACT_VERSION,
    CONSTITUTIONAL_AMENDMENT_PROPOSAL_CONTRACT_VERSION,
    CONSTITUTIONAL_AMENDMENT_PROPOSAL_SERIALIZATION_VERSION,
    CONSTITUTIONAL_BASELINE_EVIDENCE,
    CONSTITUTIONAL_GOVERNANCE_OWNER,
    GAP_DETERMINATION_EVIDENCE,
    PREVIOUS_PROPOSAL_EVIDENCE,
    PROPOSAL_ONLY_UNASSESSED,
    PROPOSER_AUTHORITY_EVIDENCE,
    TARGET_CONSTITUTIONAL_ARTIFACT_EVIDENCE,
    ConstitutionalAmendmentProposalEvidenceReferenceV1,
    create_constitutional_amendment_proposal_v1,
    deserialize_constitutional_amendment_proposal_v1,
    serialize_constitutional_amendment_proposal_v1,
    validate_constitutional_amendment_proposal_artifact_v1,
    validate_constitutional_amendment_proposal_evidence_reference_v1,
)
from aigol.runtime.constitutional_gap_determination_evidence_contract_v1 import (
    determine_constitutional_gap_v1,
)
from aigol.runtime.models import FailClosedRuntimeError


MODULE = Path("aigol/runtime/constitutional_amendment_proposal_contract_v1.py")
PROPOSER = "DECLARED_CONSTITUTIONAL_PROPOSER"
TARGET_OWNER = "CONSTITUTIONAL_FLOW_OWNER"
TARGET_IDENTITY = "CONSTITUTIONAL_FLOW_ARCHITECTURE_SPEC_V1"
TARGET_VERSION = "V1"
SUCCESSOR_VERSION = "V2-PROPOSED"
BASELINE = "constitutional-baseline-G70-01"
PROPOSED_AT = "2026-08-05T13:00:00Z"


def _digest(value: str) -> str:
    return "sha256:" + sha256(value.encode("utf-8")).hexdigest()


def _gap():
    result = determine_constitutional_gap_v1(
        implementation_request_identity="request-G70-02",
        implementation_responsibility="DEFINE_CONSTITUTIONAL_AMENDMENT",
        responsibility_owner="CONSTITUTIONAL_AMENDMENT_RESPONSIBILITY_OWNER",
        constitutional_baseline_identity=BASELINE,
        evidence_references=(),
        determined_at=PROPOSED_AT,
    )
    assert result.gap_artifact is not None
    return result.gap_artifact


def _reference(role: str, owner: str, identity: str, digest: str | None = None):
    return ConstitutionalAmendmentProposalEvidenceReferenceV1(
        evidence_role=role,
        producing_owner=owner,
        artifact_identity=identity,
        artifact_digest=digest or _digest(identity),
    )


def _evidence(gap=None, *, revision=1, previous_identity=None, previous_digest=None):
    gap = gap or _gap()
    values = [
        _reference(
            GAP_DETERMINATION_EVIDENCE,
            gap.responsibility_owner,
            gap.gap_identity,
            gap.artifact_digest,
        ),
        _reference(
            PROPOSER_AUTHORITY_EVIDENCE,
            PROPOSER,
            "proposal-authority-G70-02",
        ),
        _reference(
            TARGET_CONSTITUTIONAL_ARTIFACT_EVIDENCE,
            TARGET_OWNER,
            TARGET_IDENTITY,
            _digest(TARGET_IDENTITY),
        ),
        _reference(
            CONSTITUTIONAL_BASELINE_EVIDENCE,
            CONSTITUTIONAL_GOVERNANCE_OWNER,
            BASELINE,
            _digest(BASELINE),
        ),
    ]
    if revision > 1:
        values.append(
            _reference(
                PREVIOUS_PROPOSAL_EVIDENCE,
                PROPOSER,
                previous_identity,
                previous_digest,
            )
        )
    return tuple(values)


def _create(*, gap=None, evidence=None, **overrides):
    gap = gap or _gap()
    values = {
        "constitutional_gap": gap,
        "constitutional_baseline_digest": _digest(BASELINE),
        "proposing_owner": PROPOSER,
        "target_constitutional_owner": TARGET_OWNER,
        "target_constitutional_layer": "L1",
        "target_constitutional_artifact_identity": TARGET_IDENTITY,
        "target_constitutional_artifact_version": TARGET_VERSION,
        "target_constitutional_artifact_digest": _digest(TARGET_IDENTITY),
        "proposed_successor_version": SUCCESSOR_VERSION,
        "proposal_title": "Formalize the bounded amendment proposal contract",
        "normative_change_statement": (
            "Add a proposal-only Constitutional artifact without amendment authority."
        ),
        "proposal_rationale": (
            "The certified open Gap requires a bounded proposal representation."
        ),
        "evidence_references": evidence or _evidence(gap),
        "proposed_at": PROPOSED_AT,
    }
    values.update(overrides)
    return create_constitutional_amendment_proposal_v1(**values)


def test_create_proposal_is_immutable_versioned_and_proposal_only():
    proposal = _create()

    assert proposal.contract_version == (
        CONSTITUTIONAL_AMENDMENT_PROPOSAL_CONTRACT_VERSION
    )
    assert proposal.artifact_version == (
        CONSTITUTIONAL_AMENDMENT_PROPOSAL_ARTIFACT_VERSION
    )
    assert proposal.serialization_version == (
        CONSTITUTIONAL_AMENDMENT_PROPOSAL_SERIALIZATION_VERSION
    )
    assert proposal.proposal_status == PROPOSAL_ONLY_UNASSESSED
    assert proposal.proposal_revision == 1
    assert proposal.previous_proposal_identity is None
    with pytest.raises(FrozenInstanceError):
        proposal.proposal_status = "RATIFIED"


def test_proposal_identity_and_digest_are_content_deterministic():
    first = _create()
    second = _create()

    assert first == second
    assert first.proposal_identity == second.proposal_identity
    assert first.artifact_digest == second.artifact_digest
    assert first.proposal_identity.startswith("CONSTITUTIONAL-AMENDMENT-PROPOSAL-")
    assert first.artifact_digest.startswith("sha256:")


def test_proposal_embeds_and_revalidates_exact_open_gap():
    proposal = _create()
    assert proposal.constitutional_gap.gap_status == "OPEN"
    assert proposal.constitutional_baseline_identity == BASELINE

    tampered_gap = replace(
        proposal.constitutional_gap,
        implementation_responsibility="TAMPERED",
    )
    with pytest.raises(FailClosedRuntimeError, match="gap artifact identity"):
        _create(gap=tampered_gap, evidence=_evidence(proposal.constitutional_gap))


def test_public_evidence_validator_enforces_role_owner_and_binding():
    evidence = _evidence()[2]
    assert (
        validate_constitutional_amendment_proposal_evidence_reference_v1(
            value=evidence.to_dict(),
            expected_role=TARGET_CONSTITUTIONAL_ARTIFACT_EVIDENCE,
            expected_owner=TARGET_OWNER,
            expected_artifact_identity=TARGET_IDENTITY,
            expected_artifact_digest=_digest(TARGET_IDENTITY),
        )
        == evidence
    )

    with pytest.raises(FailClosedRuntimeError, match="role or owner"):
        validate_constitutional_amendment_proposal_evidence_reference_v1(
            value=replace(evidence, producing_owner="WRONG_OWNER"),
            expected_role=TARGET_CONSTITUTIONAL_ARTIFACT_EVIDENCE,
            expected_owner=TARGET_OWNER,
        )


@pytest.mark.parametrize(
    "mutation,match",
    (
        (lambda items: items[:-1], "incomplete"),
        (lambda items: tuple(reversed(items)), "order is not canonical"),
        (
            lambda items: (
                *items[:2],
                replace(items[2], artifact_identity="WRONG_TARGET"),
                *items[3:],
            ),
            "identity is invalid",
        ),
        (
            lambda items: (
                items[0],
                replace(items[1], producing_owner="WRONG_PROPOSER"),
                *items[2:],
            ),
            "role or owner is invalid",
        ),
    ),
)
def test_missing_reordered_or_wrong_owner_evidence_fails_closed(mutation, match):
    gap = _gap()
    with pytest.raises(FailClosedRuntimeError, match=match):
        _create(gap=gap, evidence=mutation(_evidence(gap)))


def test_unknown_evidence_role_and_malformed_digest_fail_closed():
    with pytest.raises(FailClosedRuntimeError, match="role is not recognized"):
        ConstitutionalAmendmentProposalEvidenceReferenceV1(
            evidence_role="UNKNOWN_ROLE",
            producing_owner=PROPOSER,
            artifact_identity="artifact",
            artifact_digest=_digest("artifact"),
        )
    with pytest.raises(FailClosedRuntimeError, match="SHA-256"):
        ConstitutionalAmendmentProposalEvidenceReferenceV1(
            evidence_role=PROPOSER_AUTHORITY_EVIDENCE,
            producing_owner=PROPOSER,
            artifact_identity="artifact",
            artifact_digest="invalid",
        )


def test_successor_version_must_be_explicit_and_distinct():
    with pytest.raises(FailClosedRuntimeError, match="must be distinct"):
        _create(proposed_successor_version=TARGET_VERSION)
    with pytest.raises(FailClosedRuntimeError, match="absent or malformed"):
        _create(proposed_successor_version="")


def test_revision_lineage_is_exact_and_owner_bound():
    first = _create()
    second = _create(
        evidence=_evidence(
            revision=2,
            previous_identity=first.proposal_identity,
            previous_digest=first.artifact_digest,
        ),
        proposal_revision=2,
        previous_proposal_identity=first.proposal_identity,
        previous_proposal_digest=first.artifact_digest,
        proposed_successor_version="V2-PROPOSED-REVISION-2",
    )

    assert second.proposal_revision == 2
    assert second.previous_proposal_identity == first.proposal_identity
    assert second.evidence_references[-1].evidence_role == PREVIOUS_PROPOSAL_EVIDENCE

    with pytest.raises(FailClosedRuntimeError, match="requires a predecessor"):
        _create(proposal_revision=2)
    with pytest.raises(FailClosedRuntimeError, match="cannot claim a predecessor"):
        _create(
            previous_proposal_identity=first.proposal_identity,
            previous_proposal_digest=first.artifact_digest,
        )


def test_public_artifact_validator_round_trips_exact_mapping():
    proposal = _create()

    assert (
        validate_constitutional_amendment_proposal_artifact_v1(proposal.to_dict())
        == proposal
    )

    with pytest.raises(FailClosedRuntimeError, match="version is invalid"):
        validate_constitutional_amendment_proposal_artifact_v1(
            replace(proposal, artifact_version="PROPOSAL_ARTIFACT_V2")
        )
    with pytest.raises(FailClosedRuntimeError, match="identity is invalid"):
        validate_constitutional_amendment_proposal_artifact_v1(
            replace(proposal, proposal_title="Tampered title")
        )


def test_serialization_is_canonical_versioned_and_round_trips():
    proposal = _create()

    serialized = serialize_constitutional_amendment_proposal_v1(proposal)
    restored = deserialize_constitutional_amendment_proposal_v1(serialized)

    assert restored == proposal
    assert deserialize_constitutional_amendment_proposal_v1(
        serialized.encode("utf-8")
    ) == proposal
    assert serialize_constitutional_amendment_proposal_v1(restored) == serialized


def test_noncanonical_and_tampered_serialization_fail_closed():
    proposal = _create()
    canonical = serialize_constitutional_amendment_proposal_v1(proposal)

    with pytest.raises(FailClosedRuntimeError, match="not canonical"):
        deserialize_constitutional_amendment_proposal_v1(
            json.dumps(json.loads(canonical), indent=2, sort_keys=True)
        )

    tampered = json.loads(canonical)
    tampered["proposal_rationale"] = "Tampered"
    with pytest.raises(FailClosedRuntimeError, match="identity is invalid"):
        deserialize_constitutional_amendment_proposal_v1(
            json.dumps(tampered, sort_keys=True, separators=(",", ":"))
        )


def test_proposal_preserves_topology_and_has_no_later_stage_authority():
    proposal = _create()

    assert (
        proposal.che_definition_count,
        proposal.production_hic_family_count,
        proposal.production_owner_chain_count,
        proposal.production_path_count,
        proposal.parallel_production_path_count,
    ) == (1, 1, 1, 1, 0)
    assert proposal.impact_assessment_performed is False
    assert proposal.human_ratification_performed is False
    assert proposal.amendment_certification_performed is False
    assert proposal.amendment_activation_performed is False
    assert proposal.runtime_mutation_performed is False
    assert proposal.production_behavior_changed is False
    assert proposal.replay_path_created is False
    assert proposal.cro_authority_created is False

    with pytest.raises(FailClosedRuntimeError, match="boundary invariants"):
        validate_constitutional_amendment_proposal_artifact_v1(
            replace(proposal, impact_assessment_performed=True)
        )


def test_contract_has_no_persistence_production_or_later_amendment_calls():
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }

    assert imported_modules == {
        "__future__",
        "dataclasses",
        "hashlib",
        "typing",
        "aigol.runtime.constitutional_gap_determination_evidence_contract_v1",
        "aigol.runtime.models",
        "aigol.runtime.transport.serialization",
    }
    assert called_names.isdisjoint(
        {
            "open",
            "write_json_immutable",
            "assess_amendment_impact",
            "ratify_amendment",
            "certify_amendment",
            "activate_amendment",
            "run_human_interface_runtime_entry",
        }
    )
    source = MODULE.read_text(encoding="utf-8").lower()
    assert "historical implementations" not in source
