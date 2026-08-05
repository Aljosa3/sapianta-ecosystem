from __future__ import annotations

import ast
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import runpy

import pytest

from aigol.runtime.constitutional_full_branch_replay_cro_coverage_v1 import (
    CERTIFIED_COMPLETE_BRANCH_JOURNEYS,
    FULL_BRANCH_REPLAY_AND_CRO_COVERAGE_ESTABLISHED,
    create_constitutional_full_branch_replay_correlation_v1,
    observe_constitutional_full_branch_coverage_for_cro_v1,
    persist_constitutional_full_branch_replay_correlation_v1,
    read_constitutional_full_branch_replay_correlation_v1,
    reconstruct_constitutional_full_branch_replay_v1,
    validate_constitutional_full_branch_cro_observation_v1,
    validate_constitutional_full_branch_replay_correlation_v1,
)
from aigol.runtime.constitutional_production_workflow_branch_contract_v1 import (
    GOVERNED_ACTION,
    CanonicalWorkflowBranchProvenanceV1,
    CanonicalWorkflowEvidenceReferenceV1,
    bind_canonical_workflow_branch_provenance_v1,
    create_canonical_production_workflow_branch_model_v1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash
MODULE = Path(
    "aigol/runtime/constitutional_full_branch_replay_cro_coverage_v1.py"
)
OBSERVED_AT = "2026-08-05T18:00:00Z"
compose_natural_conversation = runpy.run_path(
    "tests/test_g69_16_constitutional_natural_conversation_branch_composition.py"
)["_compose"]
compose_g64_completion = runpy.run_path(
    "tests/test_g69_17_constitutional_g64_completion_branch_composition.py"
)["_compose"]


def _definition(model, branch_kind):
    return next(
        item for item in model.branch_definitions if item.branch_kind == branch_kind
    )


def _evidence(model, branch_kind, *, natural_result=None):
    definition = _definition(model, branch_kind)
    references = []
    for requirement in definition.required_evidence:
        identity = f"{branch_kind}-{requirement.evidence_role}-G69-18"
        digest = "sha256:" + sha256(identity.encode("utf-8")).hexdigest()
        if (
            natural_result is not None
            and branch_kind == GOVERNED_ACTION
            and requirement.evidence_role == "PROPOSAL_COMMIT"
        ):
            identity = natural_result["commit_identity"]
            digest = natural_result["commit_receipt_checksum"]
        references.append(
            CanonicalWorkflowEvidenceReferenceV1(
                evidence_role=requirement.evidence_role,
                producing_owner=requirement.producing_owner,
                artifact_identity=identity,
                artifact_digest=digest,
            )
        )
    return tuple(references)


def _journey(model, kinds, index, *, natural_result=None):
    result = []
    for sequence, branch_kind in enumerate(kinds, start=1):
        definition = _definition(model, branch_kind)
        previous = result[-1] if result else None
        result.append(
            bind_canonical_workflow_branch_provenance_v1(
                model=model,
                source_request_identity=f"request-G69-18-{index}",
                source_interaction_identity=f"interaction-G69-18-{index}",
                branch_sequence=sequence,
                branch_kind=branch_kind,
                predecessor_branch_kind=(
                    None if previous is None else previous.branch_kind
                ),
                previous_provenance_identity=(
                    None if previous is None else previous.provenance_identity
                ),
                predicate_facts={
                    definition.predicate.fact_name:
                    definition.predicate.expected_value
                },
                evidence_references=_evidence(
                    model,
                    branch_kind,
                    natural_result=natural_result,
                ),
                observed_at=OBSERVED_AT,
            )
        )
    return tuple(result)


def _inputs(tmp_path, monkeypatch):
    natural = compose_natural_conversation(tmp_path / "natural")
    completion_root = tmp_path / "completion"
    completion_root.mkdir()
    completion, _ = compose_g64_completion(completion_root, monkeypatch)
    model = create_canonical_production_workflow_branch_model_v1()
    journeys = [
        _journey(model, kinds, index, natural_result=natural if index == 2 else None)
        for index, kinds in enumerate(CERTIFIED_COMPLETE_BRANCH_JOURNEYS[:-1], start=1)
    ]
    journeys.append(
        tuple(
            CanonicalWorkflowBranchProvenanceV1.from_dict(item)
            for item in completion["branch_journey"]
        )
    )
    return model, tuple(journeys), natural, completion


def _correlation(tmp_path, monkeypatch):
    model, journeys, natural, completion = _inputs(tmp_path, monkeypatch)
    return create_constitutional_full_branch_replay_correlation_v1(
        workflow_model=model,
        certified_journeys=journeys,
        natural_conversation_result=natural,
        g64_completion_result=completion,
        correlated_at=OBSERVED_AT,
    )


def test_full_correlation_covers_every_certified_branch_and_edge(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    correlation = _correlation(tmp_path, monkeypatch)

    assert correlation["coverage_status"] == (
        FULL_BRANCH_REPLAY_AND_CRO_COVERAGE_ESTABLISHED
    )
    assert len(correlation["branch_coverage"]) == 8
    assert len(correlation["edge_coverage"]) == 11
    assert len(correlation["certified_journeys"]) == 5
    assert correlation["che_definition_count"] == 1
    assert correlation["production_hic_family_count"] == 1
    assert correlation["production_owner_chain_count"] == 1
    assert correlation["production_path_count"] == 1
    assert correlation["parallel_production_path_count"] == 0
    assert correlation["hic_responsibility"] == "TRANSPORT_ONLY"
    assert correlation["hic_semantic_capability"] == "NO_SEMANTIC_CAPABILITY"
    assert correlation["production_cutover_performed"] is False


def test_replay_persists_immutably_and_reconstructs_exact_owner_provenance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    correlation = _correlation(tmp_path, monkeypatch)
    path = persist_constitutional_full_branch_replay_correlation_v1(
        replay_root=tmp_path / "replay",
        correlation=correlation,
    )
    first_bytes = path.read_bytes()

    assert read_constitutional_full_branch_replay_correlation_v1(path) == correlation
    reconstruction = reconstruct_constitutional_full_branch_replay_v1(path)
    assert reconstruction["explicit_gaps"] == []
    assert len(reconstruction["events"]) == sum(
        len(item) for item in CERTIFIED_COMPLETE_BRANCH_JOURNEYS
    )
    assert all(event["decision_owner"] for event in reconstruction["events"])
    assert path.read_bytes() == first_bytes


def test_cro_observes_every_branch_and_edge_without_mutating_replay(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    correlation = _correlation(tmp_path, monkeypatch)
    path = persist_constitutional_full_branch_replay_correlation_v1(
        replay_root=tmp_path / "replay",
        correlation=correlation,
    )
    before = path.read_bytes()

    observation = observe_constitutional_full_branch_coverage_for_cro_v1(path)

    assert observation["observed_branch_kinds"] == correlation["branch_coverage"]
    assert observation["observed_edges"] == correlation["edge_coverage"]
    assert observation["observation_gaps"] == []
    assert observation["read_only"] is True
    assert observation["post_hoc"] is True
    assert observation["out_of_band"] is True
    assert observation["authoritative"] is False
    assert observation["runtime_predecessor"] is False
    assert observation["production_cutover_performed"] is False
    assert path.read_bytes() == before


@pytest.mark.parametrize(
    "field,value",
    (
        ("branch_coverage", ["READ_ONLY"]),
        ("edge_coverage", ["READ_ONLY->HUMAN_RETURN"]),
        ("production_path_count", 2),
        ("hic_responsibility", "SEMANTIC_OWNER"),
        ("production_cutover_performed", True),
    ),
)
def test_correlation_fails_closed_on_incomplete_coverage_or_boundary_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value,
) -> None:
    candidate = deepcopy(_correlation(tmp_path, monkeypatch))
    candidate[field] = value
    candidate["correlation_identity"] = "tampered"

    with pytest.raises(FailClosedRuntimeError):
        validate_constitutional_full_branch_replay_correlation_v1(candidate)


def test_correlation_fails_closed_on_missing_journey_or_composition_mismatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model, journeys, natural, completion = _inputs(tmp_path, monkeypatch)
    with pytest.raises(FailClosedRuntimeError):
        create_constitutional_full_branch_replay_correlation_v1(
            workflow_model=model,
            certified_journeys=journeys[:-1],
            natural_conversation_result=natural,
            g64_completion_result=completion,
            correlated_at=OBSERVED_AT,
        )

    natural = deepcopy(natural)
    natural["commit_identity"] = "wrong-owner-commit"
    natural_body = deepcopy(natural)
    natural_body.pop("result_hash")
    natural["result_hash"] = replay_hash(natural_body)
    with pytest.raises(FailClosedRuntimeError):
        create_constitutional_full_branch_replay_correlation_v1(
            workflow_model=model,
            certified_journeys=journeys,
            natural_conversation_result=natural,
            g64_completion_result=completion,
            correlated_at=OBSERVED_AT,
        )


def test_corrupted_replay_and_cro_observation_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    correlation = _correlation(tmp_path, monkeypatch)
    path = persist_constitutional_full_branch_replay_correlation_v1(
        replay_root=tmp_path / "replay",
        correlation=correlation,
    )
    record = json.loads(path.read_text(encoding="utf-8"))
    record["correlation"]["branch_coverage"] = ["READ_ONLY"]
    path.write_text(canonical_serialize(record) + "\n", encoding="utf-8")
    with pytest.raises(FailClosedRuntimeError):
        observe_constitutional_full_branch_coverage_for_cro_v1(path)

    path = persist_constitutional_full_branch_replay_correlation_v1(
        replay_root=tmp_path / "fresh-replay",
        correlation=correlation,
    )
    observation = observe_constitutional_full_branch_coverage_for_cro_v1(path)
    observation["authoritative"] = True
    body = deepcopy(observation)
    body.pop("observation_hash")
    observation["observation_hash"] = replay_hash(body)
    with pytest.raises(FailClosedRuntimeError):
        validate_constitutional_full_branch_cro_observation_v1(observation)


def test_b9_module_has_no_che_hic_branch_execution_or_cutover_imports() -> None:
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert not any(
        token in name
        for name in imports
        for token in (
            "run_human_interface_runtime_entry",
            "human_interface_contract",
            "production_conversation_flow_binding",
            "worker_invocation",
            "production_cutover",
        )
    )
    source = MODULE.read_text(encoding="utf-8")
    assert "compose_constitutional_natural_conversation_branch_v1" not in source
    assert "compose_constitutional_g64_completion_branch_v1" not in source
