from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from hashlib import sha256
import json
from pathlib import Path

import pytest

from aigol.runtime.constitutional_gap_determination_evidence_contract_v1 import (
    ABSENT,
    CONSTITUTION_ALREADY_SUFFICIENT,
    CONSTITUTIONAL_GAP,
    CONSTITUTIONAL_GAP_ARTIFACT_VERSION,
    CONSTITUTIONAL_GAP_CONTRACT_VERSION,
    CONSTITUTIONAL_GAP_PREDICATE_DEFINITIONS,
    CONSTITUTIONAL_GAP_PREDICATE_ORDER,
    CONSTITUTIONAL_GAP_SERIALIZATION_VERSION,
    RESPONSIBILITY_OWNER,
    SATISFIED,
    UNSATISFIED,
    ConstitutionalGapEvidenceReferenceV1,
    deserialize_constitutional_gap_artifact_v1,
    determine_constitutional_gap_v1,
    serialize_constitutional_gap_artifact_v1,
    validate_constitutional_gap_artifact_v1,
    validate_constitutional_gap_determination_result_v1,
    validate_constitutional_gap_evidence_reference_v1,
)
from aigol.runtime.models import FailClosedRuntimeError


MODULE = Path(
    "aigol/runtime/constitutional_gap_determination_evidence_contract_v1.py"
)
RESPONSIBILITY = "DEFINE_BOUNDED_CONSTITUTIONAL_CAPABILITY"
RESPONSIBILITY_OWNER_ID = "DECLARED_CONSTITUTIONAL_CAPABILITY_OWNER"
BASELINE = "constitutional-baseline-G70-00"
DETERMINED_AT = "2026-08-05T12:00:00Z"


def _owner_for(predicate_id: str) -> str:
    definition = next(
        item
        for item in CONSTITUTIONAL_GAP_PREDICATE_DEFINITIONS
        if item.predicate_id == predicate_id
    )
    if definition.evidence_owner_rule == RESPONSIBILITY_OWNER:
        return RESPONSIBILITY_OWNER_ID
    return definition.evidence_owner_rule


def _reference(
    predicate_id: str,
    status: str = SATISFIED,
) -> ConstitutionalGapEvidenceReferenceV1:
    if status == ABSENT:
        identity = None
        digest = None
    else:
        identity = f"evidence-{predicate_id}"
        digest = "sha256:" + sha256(identity.encode("utf-8")).hexdigest()
    return ConstitutionalGapEvidenceReferenceV1(
        predicate_id=predicate_id,
        evidence_status=status,
        producing_owner=_owner_for(predicate_id),
        artifact_identity=identity,
        artifact_digest=digest,
    )


def _all_satisfied():
    return tuple(_reference(item) for item in CONSTITUTIONAL_GAP_PREDICATE_ORDER)


def _determine(evidence_references):
    return determine_constitutional_gap_v1(
        implementation_request_identity="implementation-request-G70-01",
        implementation_responsibility=RESPONSIBILITY,
        responsibility_owner=RESPONSIBILITY_OWNER_ID,
        constitutional_baseline_identity=BASELINE,
        evidence_references=evidence_references,
        determined_at=DETERMINED_AT,
    )


def test_complete_owner_evidence_has_only_sufficient_disposition():
    result = _determine(tuple(reversed(_all_satisfied())))

    assert result.disposition == CONSTITUTION_ALREADY_SUFFICIENT
    assert result.gap_artifact is None
    assert tuple(item.predicate_id for item in result.ordered_evidence) == (
        CONSTITUTIONAL_GAP_PREDICATE_ORDER
    )
    assert validate_constitutional_gap_determination_result_v1(result) == result


def test_unsatisfied_predicate_creates_immutable_owner_bound_gap():
    evidence = list(_all_satisfied())
    target = CONSTITUTIONAL_GAP_PREDICATE_ORDER[4]
    evidence[4] = _reference(target, UNSATISFIED)

    result = _determine(tuple(evidence))
    artifact = result.gap_artifact

    assert result.disposition == CONSTITUTIONAL_GAP
    assert artifact is not None
    assert artifact.contract_version == CONSTITUTIONAL_GAP_CONTRACT_VERSION
    assert artifact.artifact_version == CONSTITUTIONAL_GAP_ARTIFACT_VERSION
    assert (
        artifact.serialization_version
        == CONSTITUTIONAL_GAP_SERIALIZATION_VERSION
    )
    assert artifact.ordered_gap_predicates == (target,)
    assert artifact.first_gap_predicate == target
    assert artifact.determination_identity == result.determination_identity
    with pytest.raises(FrozenInstanceError):
        artifact.gap_status = "CLOSED"


def test_missing_evidence_is_deterministically_materialized_as_absent_gap():
    evidence = _all_satisfied()[:-2]

    first = _determine(evidence)
    second = _determine(evidence)

    assert first == second
    assert first.disposition == CONSTITUTIONAL_GAP
    assert first.gap_artifact is not None
    assert first.gap_artifact.ordered_gap_predicates == (
        CONSTITUTIONAL_GAP_PREDICATE_ORDER[-2:]
    )
    assert [item.evidence_status for item in first.ordered_evidence[-2:]] == [
        ABSENT,
        ABSENT,
    ]
    assert all(item.artifact_identity is None for item in first.ordered_evidence[-2:])


def test_gap_order_is_constitutional_not_caller_order():
    target_a = CONSTITUTIONAL_GAP_PREDICATE_ORDER[2]
    target_b = CONSTITUTIONAL_GAP_PREDICATE_ORDER[9]
    evidence = [
        _reference(
            predicate_id,
            UNSATISFIED if predicate_id in {target_a, target_b} else SATISFIED,
        )
        for predicate_id in reversed(CONSTITUTIONAL_GAP_PREDICATE_ORDER)
    ]

    artifact = _determine(evidence).gap_artifact

    assert artifact is not None
    assert artifact.ordered_gap_predicates == (target_a, target_b)
    assert artifact.first_gap_predicate == target_a


def test_owner_validation_is_exact_and_public():
    reference = _reference(CONSTITUTIONAL_GAP_PREDICATE_ORDER[0])
    assert (
        validate_constitutional_gap_evidence_reference_v1(
            value=reference.to_dict(),
            responsibility_owner=RESPONSIBILITY_OWNER_ID,
        )
        == reference
    )

    with pytest.raises(FailClosedRuntimeError, match="required owner"):
        validate_constitutional_gap_evidence_reference_v1(
            value=replace(reference, producing_owner="WRONG_OWNER"),
            responsibility_owner=RESPONSIBILITY_OWNER_ID,
        )


@pytest.mark.parametrize(
    "candidate,match",
    (
        (
            {
                "predicate_id": "UNKNOWN_PREDICATE",
                "evidence_status": SATISFIED,
                "producing_owner": "OWNER",
                "artifact_identity": "artifact",
                "artifact_digest": "sha256:" + ("0" * 64),
            },
            "not recognized",
        ),
        (
            {
                "predicate_id": CONSTITUTIONAL_GAP_PREDICATE_ORDER[0],
                "evidence_status": "UNKNOWN_STATUS",
                "producing_owner": RESPONSIBILITY_OWNER_ID,
                "artifact_identity": "artifact",
                "artifact_digest": "sha256:" + ("0" * 64),
            },
            "status is not recognized",
        ),
        (
            {
                "predicate_id": CONSTITUTIONAL_GAP_PREDICATE_ORDER[0],
                "evidence_status": SATISFIED,
                "producing_owner": RESPONSIBILITY_OWNER_ID,
                "artifact_identity": "artifact",
                "artifact_digest": "not-a-digest",
            },
            "SHA-256",
        ),
        (
            {
                "predicate_id": CONSTITUTIONAL_GAP_PREDICATE_ORDER[0],
                "evidence_status": ABSENT,
                "producing_owner": RESPONSIBILITY_OWNER_ID,
                "artifact_identity": "invented-artifact",
                "artifact_digest": "sha256:" + ("0" * 64),
            },
            "cannot claim",
        ),
    ),
)
def test_malformed_evidence_fails_closed(candidate, match):
    with pytest.raises(FailClosedRuntimeError, match=match):
        _determine((candidate,))


def test_duplicate_predicate_evidence_fails_closed():
    duplicate = _reference(CONSTITUTIONAL_GAP_PREDICATE_ORDER[0])

    with pytest.raises(FailClosedRuntimeError, match="duplicated"):
        _determine((duplicate, duplicate))


def test_gap_artifact_serialization_is_canonical_versioned_and_round_trips():
    artifact = _determine(()).gap_artifact
    assert artifact is not None

    serialized = serialize_constitutional_gap_artifact_v1(artifact)
    restored = deserialize_constitutional_gap_artifact_v1(serialized)

    assert restored == artifact
    assert serialize_constitutional_gap_artifact_v1(restored) == serialized
    assert deserialize_constitutional_gap_artifact_v1(serialized.encode()) == artifact


def test_noncanonical_or_tampered_serialization_fails_closed():
    artifact = _determine(()).gap_artifact
    assert artifact is not None
    canonical = serialize_constitutional_gap_artifact_v1(artifact)
    expanded = json.dumps(json.loads(canonical), indent=2, sort_keys=True)

    with pytest.raises(FailClosedRuntimeError, match="not canonical"):
        deserialize_constitutional_gap_artifact_v1(expanded)

    tampered = json.loads(canonical)
    tampered["implementation_responsibility"] = "TAMPERED"
    with pytest.raises(FailClosedRuntimeError, match="identity is invalid"):
        deserialize_constitutional_gap_artifact_v1(
            json.dumps(tampered, sort_keys=True, separators=(",", ":"))
        )


def test_public_artifact_validator_rejects_version_and_predicate_tampering():
    artifact = _determine(()).gap_artifact
    assert artifact is not None
    assert validate_constitutional_gap_artifact_v1(artifact.to_dict()) == artifact

    with pytest.raises(FailClosedRuntimeError, match="version is invalid"):
        validate_constitutional_gap_artifact_v1(
            replace(artifact, artifact_version="CONSTITUTIONAL_GAP_ARTIFACT_V2")
        )
    with pytest.raises(FailClosedRuntimeError, match="reduction is invalid"):
        validate_constitutional_gap_artifact_v1(
            replace(
                artifact,
                ordered_gap_predicates=artifact.ordered_gap_predicates[1:],
                first_gap_predicate=artifact.ordered_gap_predicates[1],
            )
        )


def test_result_preserves_one_production_topology_and_creates_no_authority():
    result = _determine(())

    assert result.che_definition_count == 1
    assert result.production_hic_family_count == 1
    assert result.production_owner_chain_count == 1
    assert result.production_path_count == 1
    assert result.parallel_production_path_count == 0
    assert result.amendment_authority_created is False
    assert result.runtime_mutation_performed is False
    assert result.production_behavior_changed is False
    assert result.replay_path_created is False
    assert result.cro_authority_created is False

    with pytest.raises(FailClosedRuntimeError, match="boundary invariants"):
        validate_constitutional_gap_determination_result_v1(
            replace(result, production_path_count=2)
        )
    with pytest.raises(FailClosedRuntimeError, match="topology is malformed"):
        replace(result, production_path_count=True)


def test_contract_has_no_persistence_production_or_amendment_orchestration():
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }

    assert imported_modules == {
        "__future__",
        "dataclasses",
        "hashlib",
        "typing",
        "aigol.runtime.models",
        "aigol.runtime.transport.serialization",
    }
    assert called_names.isdisjoint(
        {
            "open",
            "write_json_immutable",
            "run_human_interface_runtime_entry",
            "activate_amendment",
            "approve_amendment",
            "certify_amendment",
            "propose_amendment",
        }
    )
    source = MODULE.read_text(encoding="utf-8").lower()
    assert "historical implementations" not in source
