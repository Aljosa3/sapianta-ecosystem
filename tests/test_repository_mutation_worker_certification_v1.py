"""Checks for AIGOL_REPOSITORY_MUTATION_WORKER_RUNTIME_CERTIFICATION_V1."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CERTIFICATION = ROOT / ".github/governance/finalize/AIGOL_REPOSITORY_MUTATION_WORKER_RUNTIME_CERTIFICATION_V1.json"


def _load() -> dict:
    return json.loads(CERTIFICATION.read_text(encoding="utf-8"))


def test_repository_mutation_worker_certification_records_runtime_scope() -> None:
    certification = _load()
    scope = certification["certification_scope"]

    assert certification["artifact_type"] == "REPOSITORY_MUTATION_WORKER_RUNTIME_CERTIFICATION_V1"
    assert certification["certified_runtime"] == "AIGOL_REPOSITORY_MUTATION_WORKER_RUNTIME_V1"
    assert certification["certification_status"] == "CERTIFIED"
    assert scope["input_artifacts"] == [
        "PATCH_PROPOSAL_ARTIFACT_V1",
        "CERTIFIED_WORKER_EXECUTION_RESULT_ARTIFACT_V1",
    ]
    assert scope["output_artifact"] == "REPOSITORY_MUTATION_ARTIFACT_V1"
    assert scope["allowed_operations"] == ["CREATE_OR_REPLACE", "REPLACE_CONTENT"]
    assert scope["approved_file_mutations_only"] is True
    assert scope["governance_artifact_mutation_allowed"] is False
    assert scope["replay_artifact_mutation_allowed"] is False
    assert scope["arbitrary_shell_allowed"] is False
    assert scope["provider_invocation_allowed"] is False


def test_repository_mutation_worker_certification_preserves_governance_guarantees() -> None:
    certification = _load()
    guarantees = certification["governance_guarantees"]

    assert guarantees["repository_mutation_worker_implemented"] is True
    assert guarantees["repository_mutation_artifact_generated"] is True
    assert guarantees["before_after_hashes_recorded"] is True
    assert guarantees["original_snapshots_preserved"] is True
    assert guarantees["replay_lineage_preserved"] is True
    assert guarantees["human_authority_preserved"] is True
    assert guarantees["authorization_boundaries_preserved"] is True
    assert guarantees["unauthorized_mutation_prevented"] is True
    assert guarantees["fail_closed_preserved"] is True
    assert guarantees["ready_for_governed_repository_changes"] is True


def test_repository_mutation_worker_certification_final_outputs() -> None:
    certification = _load()
    outputs = certification["final_outputs"]

    assert outputs["REPOSITORY_MUTATION_WORKER_IMPLEMENTED"] == "YES"
    assert outputs["REPOSITORY_MUTATION_ARTIFACT_GENERATED"] == "YES"
    assert outputs["REPLAY_LINEAGE_PRESERVED"] == "YES"
    assert outputs["UNAUTHORIZED_MUTATION_PREVENTED"] == "YES"
    assert outputs["FAIL_CLOSED_PRESERVED"] == "YES"
    assert outputs["READY_FOR_GOVERNED_REPOSITORY_CHANGES"] == "YES"
