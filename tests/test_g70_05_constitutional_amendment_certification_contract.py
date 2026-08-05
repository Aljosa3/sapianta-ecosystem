from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
import importlib.util
import json
from pathlib import Path

import pytest

from aigol.runtime.canonical_human_authority_act_contract_v1 import (
    HUMAN_AUTHORITY_OWNER,
)
from aigol.runtime.constitutional_amendment_certification_contract_v1 import (
    CERTIFICATION_RULE_SATISFIED,
    CONSTITUTIONAL_AMENDMENT_CERTIFICATION_ARTIFACT_VERSION,
    CONSTITUTIONAL_AMENDMENT_CERTIFICATION_CONTRACT_VERSION,
    CONSTITUTIONAL_AMENDMENT_CERTIFICATION_EVIDENCE_ORDER,
    CONSTITUTIONAL_AMENDMENT_CERTIFICATION_RULE_ORDER,
    CONSTITUTIONAL_AMENDMENT_CERTIFICATION_SCOPE,
    CONSTITUTIONAL_AMENDMENT_CERTIFICATION_SERIALIZATION_VERSION,
    CONSTITUTIONAL_AMENDMENT_CERTIFIED_NOT_ACTIVATED,
    CONSTITUTIONAL_GAP_CERTIFICATION_EVIDENCE,
    CONSTITUTIONAL_IMPACT_CERTIFICATION_EVIDENCE,
    CONSTITUTIONAL_PROPOSAL_CERTIFICATION_EVIDENCE,
    HUMAN_RATIFICATION_CERTIFICATION_EVIDENCE,
    ConstitutionalAmendmentCertificationEvidenceReferenceV1,
    ConstitutionalAmendmentCertificationRuleResultV1,
    certify_constitutional_amendment_v1,
    deserialize_constitutional_amendment_certification_v1,
    serialize_constitutional_amendment_certification_v1,
    validate_constitutional_amendment_certification_artifact_v1,
    validate_constitutional_amendment_certification_evidence_reference_v1,
    validate_constitutional_amendment_certification_rule_result_v1,
)
from aigol.runtime.constitutional_gap_determination_evidence_contract_v1 import (
    CONSTITUTIONAL_CERTIFICATION_OWNER,
)
from aigol.runtime.models import FailClosedRuntimeError


MODULE = Path(
    "aigol/runtime/constitutional_amendment_certification_contract_v1.py"
)
CERTIFIED_AT = "2026-08-05T16:00:00Z"


def _load_certified_ratification_fixture_module():
    path = Path(
        "tests/test_g70_04_constitutional_human_ratification_contract.py"
    )
    spec = importlib.util.spec_from_file_location("g70_04_fixture", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


G70_04 = _load_certified_ratification_fixture_module()


def _reference(role, owner, identity, digest):
    return ConstitutionalAmendmentCertificationEvidenceReferenceV1(
        evidence_role=role,
        producing_owner=owner,
        artifact_identity=identity,
        artifact_digest=digest,
    )


def _evidence(ratification):
    assessment = ratification.impact_assessment
    proposal = assessment.amendment_proposal
    gap = proposal.constitutional_gap
    return (
        _reference(
            CONSTITUTIONAL_GAP_CERTIFICATION_EVIDENCE,
            gap.responsibility_owner,
            gap.gap_identity,
            gap.artifact_digest,
        ),
        _reference(
            CONSTITUTIONAL_PROPOSAL_CERTIFICATION_EVIDENCE,
            proposal.proposing_owner,
            proposal.proposal_identity,
            proposal.artifact_digest,
        ),
        _reference(
            CONSTITUTIONAL_IMPACT_CERTIFICATION_EVIDENCE,
            assessment.assessing_owner,
            assessment.assessment_identity,
            assessment.artifact_digest,
        ),
        _reference(
            HUMAN_RATIFICATION_CERTIFICATION_EVIDENCE,
            HUMAN_AUTHORITY_OWNER,
            ratification.ratification_identity,
            ratification.artifact_digest,
        ),
    )


def _certify(ratification=None, evidence=None, **overrides):
    ratification = ratification or G70_04._create()
    return certify_constitutional_amendment_v1(
        human_ratification=ratification,
        certifying_owner=overrides.get(
            "certifying_owner", CONSTITUTIONAL_CERTIFICATION_OWNER
        ),
        evidence_references=(
            evidence if evidence is not None else _evidence(ratification)
        ),
        certified_at=overrides.get("certified_at", CERTIFIED_AT),
    )


def test_certification_is_immutable_versioned_and_not_activation():
    certification = _certify()

    assert certification.contract_version == (
        CONSTITUTIONAL_AMENDMENT_CERTIFICATION_CONTRACT_VERSION
    )
    assert certification.artifact_version == (
        CONSTITUTIONAL_AMENDMENT_CERTIFICATION_ARTIFACT_VERSION
    )
    assert certification.serialization_version == (
        CONSTITUTIONAL_AMENDMENT_CERTIFICATION_SERIALIZATION_VERSION
    )
    assert certification.certification_status == (
        CONSTITUTIONAL_AMENDMENT_CERTIFIED_NOT_ACTIVATED
    )
    assert certification.certifying_owner == CONSTITUTIONAL_CERTIFICATION_OWNER
    with pytest.raises(FrozenInstanceError):
        certification.certification_status = "ACTIVATED"


def test_certification_scope_is_closed_to_exactly_four_cap_artifacts():
    certification = _certify()
    ratification = certification.human_ratification
    assessment = ratification.impact_assessment
    proposal = assessment.amendment_proposal
    gap = proposal.constitutional_gap

    assert certification.certification_scope == (
        CONSTITUTIONAL_AMENDMENT_CERTIFICATION_SCOPE
    )
    assert tuple(
        item.evidence_role for item in certification.evidence_references
    ) == CONSTITUTIONAL_AMENDMENT_CERTIFICATION_EVIDENCE_ORDER
    assert tuple(
        item.artifact_identity for item in certification.evidence_references
    ) == (
        gap.gap_identity,
        proposal.proposal_identity,
        assessment.assessment_identity,
        ratification.ratification_identity,
    )


def test_certification_identity_and_digest_are_content_deterministic():
    ratification = G70_04._create()
    first = _certify(ratification)
    second = _certify(ratification)

    assert first == second
    assert first.certification_identity == second.certification_identity
    assert first.artifact_digest == second.artifact_digest
    later = _certify(ratification, certified_at="2026-08-05T16:00:01Z")
    assert later.certification_identity != first.certification_identity
    assert later.artifact_digest != first.artifact_digest


def test_deterministic_rules_are_complete_ordered_and_publicly_validated():
    certification = _certify()

    assert tuple(item.rule_id for item in certification.rule_results) == (
        CONSTITUTIONAL_AMENDMENT_CERTIFICATION_RULE_ORDER
    )
    assert all(
        item.rule_status == CERTIFICATION_RULE_SATISFIED
        for item in certification.rule_results
    )
    assert (
        validate_constitutional_amendment_certification_rule_result_v1(
            value=certification.rule_results[0].to_dict(),
            expected_rule_id=CONSTITUTIONAL_AMENDMENT_CERTIFICATION_RULE_ORDER[0],
        )
        == certification.rule_results[0]
    )
    with pytest.raises(FailClosedRuntimeError, match="rule identity is invalid"):
        validate_constitutional_amendment_certification_rule_result_v1(
            value=certification.rule_results[0],
            expected_rule_id=CONSTITUTIONAL_AMENDMENT_CERTIFICATION_RULE_ORDER[1],
        )
    with pytest.raises(FailClosedRuntimeError, match="not satisfied"):
        ConstitutionalAmendmentCertificationRuleResultV1(
            rule_id=CONSTITUTIONAL_AMENDMENT_CERTIFICATION_RULE_ORDER[0],
            rule_status="FAILED",
        )
    with pytest.raises(FailClosedRuntimeError, match="not recognized"):
        ConstitutionalAmendmentCertificationRuleResultV1(
            rule_id="INVENTED_CERTIFICATION_RULE",
            rule_status=CERTIFICATION_RULE_SATISFIED,
        )
    with pytest.raises(FailClosedRuntimeError, match="rules are incomplete"):
        validate_constitutional_amendment_certification_artifact_v1(
            replace(certification, rule_results=certification.rule_results[:-1])
        )


def test_exact_evidence_validator_rejects_missing_reordered_or_tampered_chain():
    ratification = G70_04._create()
    evidence = _evidence(ratification)
    first = evidence[0]

    assert (
        validate_constitutional_amendment_certification_evidence_reference_v1(
            value=first.to_dict(),
            expected_role=first.evidence_role,
            expected_owner=first.producing_owner,
            expected_artifact_identity=first.artifact_identity,
            expected_artifact_digest=first.artifact_digest,
        )
        == first
    )
    with pytest.raises(FailClosedRuntimeError, match="incomplete"):
        _certify(ratification, evidence=evidence[:-1])
    with pytest.raises(FailClosedRuntimeError, match="order is not canonical"):
        _certify(ratification, evidence=tuple(reversed(evidence)))
    with pytest.raises(FailClosedRuntimeError, match="evidence identity is invalid"):
        _certify(
            ratification,
            evidence=(
                replace(first, artifact_identity="WRONG-GAP"),
                *evidence[1:],
            ),
        )


def test_wrong_certification_owner_and_unknown_evidence_role_fail_closed():
    with pytest.raises(FailClosedRuntimeError, match="owner is invalid"):
        _certify(certifying_owner="INVENTED_CERTIFICATION_OWNER")
    with pytest.raises(FailClosedRuntimeError, match="role is not recognized"):
        ConstitutionalAmendmentCertificationEvidenceReferenceV1(
            evidence_role="CONSTITUTIONAL_SUCCESSOR_EVIDENCE",
            producing_owner=CONSTITUTIONAL_CERTIFICATION_OWNER,
            artifact_identity="successor-V2",
            artifact_digest="sha256:" + ("0" * 64),
        )


def test_public_artifact_validator_round_trips_and_rejects_tampering():
    certification = _certify()

    assert (
        validate_constitutional_amendment_certification_artifact_v1(
            certification.to_dict()
        )
        == certification
    )
    with pytest.raises(FailClosedRuntimeError, match="version is invalid"):
        validate_constitutional_amendment_certification_artifact_v1(
            replace(certification, artifact_version="CERTIFICATION_V2")
        )
    with pytest.raises(FailClosedRuntimeError, match="scope is invalid"):
        validate_constitutional_amendment_certification_artifact_v1(
            replace(
                certification,
                certification_scope=(
                    *certification.certification_scope,
                    "CONSTITUTIONAL_SUCCESSOR",
                ),
            )
        )
    with pytest.raises(FailClosedRuntimeError, match="rule order"):
        validate_constitutional_amendment_certification_artifact_v1(
            replace(
                certification,
                rule_results=tuple(reversed(certification.rule_results)),
            )
        )
    with pytest.raises(FailClosedRuntimeError, match="Human binding is invalid"):
        validate_constitutional_amendment_certification_artifact_v1(
            replace(
                certification,
                human_ratification=replace(
                    certification.human_ratification,
                    ratified_at="2026-08-05T16:00:00Z",
                ),
            )
        )


def test_serialization_is_canonical_versioned_and_round_trips():
    certification = _certify()
    serialized = serialize_constitutional_amendment_certification_v1(
        certification
    )

    assert (
        deserialize_constitutional_amendment_certification_v1(serialized)
        == certification
    )
    assert (
        deserialize_constitutional_amendment_certification_v1(
            serialized.encode("utf-8")
        )
        == certification
    )
    assert serialize_constitutional_amendment_certification_v1(
        certification
    ) == serialized


def test_noncanonical_tampered_or_expanded_serialization_fails_closed():
    certification = _certify()
    canonical = serialize_constitutional_amendment_certification_v1(
        certification
    )

    with pytest.raises(FailClosedRuntimeError, match="not canonical"):
        deserialize_constitutional_amendment_certification_v1(
            json.dumps(json.loads(canonical), indent=2, sort_keys=True)
        )
    tampered = json.loads(canonical)
    tampered["certification_status"] = "ACTIVATED"
    with pytest.raises(FailClosedRuntimeError, match="status is invalid"):
        deserialize_constitutional_amendment_certification_v1(
            json.dumps(tampered, sort_keys=True, separators=(",", ":"))
        )
    expanded = json.loads(canonical)
    expanded["constitutional_successor"] = {"version": "V2"}
    with pytest.raises(FailClosedRuntimeError, match="artifact is malformed"):
        deserialize_constitutional_amendment_certification_v1(
            json.dumps(expanded, sort_keys=True, separators=(",", ":"))
        )


def test_resolved_boundary_impact_can_be_certified_without_activation():
    assessment = G70_04._assessment(
        production_path_impact=G70_04.PRODUCTION_PATH_CHANGE_PROPOSED
    )
    ratification = G70_04._create(G70_04._transport(assessment=assessment))
    certification = _certify(ratification)

    assert certification.amendment_certification_performed is True
    assert certification.amendment_publication_performed is False
    assert certification.amendment_activation_performed is False
    assert certification.constitutional_successor_activation_performed is False


def test_certification_preserves_topology_and_all_mutation_boundaries():
    certification = _certify()

    assert (
        certification.che_definition_count,
        certification.production_hic_family_count,
        certification.production_owner_chain_count,
        certification.production_path_count,
        certification.parallel_production_path_count,
    ) == (1, 1, 1, 1, 0)
    assert certification.runtime_mutation_performed is False
    assert certification.production_mutation_performed is False
    assert certification.owner_mutation_performed is False
    assert certification.che_mutation_performed is False
    assert certification.hic_mutation_performed is False
    assert certification.replay_mutation_performed is False
    assert certification.cro_mutation_performed is False
    assert certification.hic_semantic_capability_introduced is False

    with pytest.raises(FailClosedRuntimeError, match="boundary invariants"):
        validate_constitutional_amendment_certification_artifact_v1(
            replace(certification, runtime_mutation_performed=True)
        )


def test_contract_has_no_persistence_activation_production_or_hic_calls():
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
            "activate_amendment",
            "publish_amendment",
            "activate_constitutional_successor",
            "run_human_interface_runtime_entry",
            "mutate_runtime",
            "mutate_production",
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
