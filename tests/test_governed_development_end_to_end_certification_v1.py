"""End-to-end certification for natural-language governed development."""

from __future__ import annotations

from copy import deepcopy
import subprocess

import pytest

from aigol.runtime.conversational_cli_runtime import (
    GOVERNED_DEVELOPMENT_WORKFLOW,
    WORKFLOW_SELECTED,
    reconstruct_conversational_cli_routing_replay,
    route_conversational_cli_intent,
)
from aigol.runtime.governance_artifact_creation_runtime import (
    GOVERNANCE_ARTIFACT_CREATION_COMPLETED,
    reconstruct_governance_artifact_creation_replay,
)
from aigol.runtime.governed_development_workflow_runtime import (
    APPROVED,
    FAILED_CLOSED,
    GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED,
    create_governed_development_approval,
    create_governed_development_proposal,
    execute_governed_development_workflow,
    reconstruct_governed_development_workflow_replay,
)
from aigol.runtime.governed_repository_mutation_runtime import (
    GOVERNED_REPOSITORY_MUTATION_COMPLETED,
    reconstruct_governed_repository_mutation_replay,
)
from aigol.runtime.human_intent_clarification_intake_runtime import DEVELOPMENT_INTENT
from aigol.runtime.transport.serialization import replay_hash
from aigol.runtime.validation_command_runner_runtime import (
    VALIDATION_COMMAND_COMPLETED,
    reconstruct_validation_command_replay,
)


CREATED_AT = "2026-06-23T00:00:00Z"
SESSION_ID = "SESSION-GOVERNED-DEVELOPMENT-E2E-CERTIFICATION-000001"
NATURAL_DEVELOPMENT_PROMPT = "Add replay validation"


def _repo(tmp_path):
    repo = tmp_path / "repo"
    (repo / "docs" / "governance").mkdir(parents=True)
    (repo / "aigol" / "runtime").mkdir(parents=True)
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    return repo


def _artifact_hash(payload: dict):
    artifact = dict(payload)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _route(tmp_path):
    return route_conversational_cli_intent(
        routing_id="GOVERNED-DEVELOPMENT-E2E-CERTIFICATION-ROUTING-000001",
        prompt_id=f"{SESSION_ID}:TURN-000001",
        human_prompt=NATURAL_DEVELOPMENT_PROMPT,
        canonical_chain_id=f"{SESSION_ID}:TURN-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "routing",
    )


def _file_mutation():
    content = "CERTIFIED_REPLAY_VALIDATION = True\n"
    return {
        "target_path": "aigol/runtime/certified_replay_validation_marker.py",
        "operation": "CREATE_OR_REPLACE",
        "new_content": content,
        "new_content_hash": replay_hash(content),
        "approved": True,
    }


def _governance_artifact():
    return {
        "target_path": "docs/governance/CERTIFIED_REPLAY_VALIDATION_ARTIFACT_V1.md",
        "artifact_title": "CERTIFIED_REPLAY_VALIDATION_ARTIFACT_V1",
        "artifact_purpose": "Record the governed development certification fixture.",
        "proposed_content": "\n".join(
            [
                "# CERTIFIED_REPLAY_VALIDATION_ARTIFACT_V1",
                "",
                "Status: Defined",
                "",
                "Purpose: Certification fixture for governed development replay validation.",
                "",
            ]
        ),
        "expected_sections": ["Status", "Purpose"],
    }


def _proposal(route_capture):
    decision = route_capture["routing_decision_artifact"]
    selection = route_capture["workflow_selection_artifact"]
    return create_governed_development_proposal(
        proposal_id="GOVERNED-DEVELOPMENT-E2E-CERTIFICATION-PROPOSAL-000001",
        original_request_reference=decision["routing_decision_id"],
        resolved_intent_reference=selection["workflow_selection_id"],
        governance_artifact=_governance_artifact(),
        repository_file_mutations=[_file_mutation()],
        repository_validation_command=["git", "diff", "--check"],
        replay_references=[
            route_capture["conversational_cli_routing_replay_reference"],
            decision["routing_decision_id"],
            selection["workflow_selection_id"],
        ],
        replay_hashes=[
            route_capture["conversational_cli_routing_hash"],
            decision["artifact_hash"],
            selection["artifact_hash"],
        ],
        created_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
    )


def _approval(proposal):
    return create_governed_development_approval(
        approval_id="GOVERNED-DEVELOPMENT-E2E-CERTIFICATION-APPROVAL-000001",
        proposal_artifact=proposal,
        decision=APPROVED,
        approved_by="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
        replay_references=[proposal["proposal_id"]],
        replay_hashes=[proposal["artifact_hash"]],
    )


def _request_artifact(route_capture):
    decision = route_capture["routing_decision_artifact"]
    return _artifact_hash(
        {
            "artifact_type": "GOVERNED_DEVELOPMENT_E2E_REQUEST_ARTIFACT_V1",
            "request_id": "GOVERNED-DEVELOPMENT-E2E-CERTIFICATION-REQUEST-000001",
            "natural_language_prompt": NATURAL_DEVELOPMENT_PROMPT,
            "routing_decision_reference": decision["routing_decision_id"],
            "routing_decision_hash": decision["artifact_hash"],
            "created_at": CREATED_AT,
        }
    )


def _intent_artifact(route_capture):
    intake = deepcopy(route_capture["workflow_selection_artifact"]["human_intent_intake"])
    intake["artifact_type"] = "GOVERNED_DEVELOPMENT_E2E_HIRR_INTENT_ARTIFACT_V1"
    intake["intent_id"] = "GOVERNED-DEVELOPMENT-E2E-CERTIFICATION-INTENT-000001"
    intake["source_workflow_selection_hash"] = route_capture["workflow_selection_artifact"]["artifact_hash"]
    intake["artifact_hash"] = replay_hash(intake)
    return intake


def _context_artifact(proposal):
    return _artifact_hash(
        {
            "artifact_type": "GOVERNED_DEVELOPMENT_E2E_REPOSITORY_CONTEXT_ARTIFACT_V1",
            "context_id": "GOVERNED-DEVELOPMENT-E2E-CERTIFICATION-CONTEXT-000001",
            "context_fresh": True,
            "governance_target_path": proposal["governance_artifact_proposal"]["target_path"],
            "target_paths": proposal["repository_mutation_proposal"]["target_paths"],
            "created_at": CREATED_AT,
        }
    )


def _execute(repo, replay_dir, route_capture, proposal, approval):
    return execute_governed_development_workflow(
        execution_id="GOVERNED-DEVELOPMENT-E2E-CERTIFICATION-EXECUTION-000001",
        request_artifact=_request_artifact(route_capture),
        intent_artifact=_intent_artifact(route_capture),
        workflow_artifact=route_capture["workflow_selection_artifact"],
        repository_context_artifact=_context_artifact(proposal),
        proposal_artifact=proposal,
        approval_artifact=approval,
        repository_root=repo,
        executed_by="AIGOL_GOVERNED_DEVELOPMENT_E2E_CERTIFICATION",
        executed_at=CREATED_AT,
        replay_dir=replay_dir,
    )


def test_governed_development_end_to_end_certification_from_natural_language(tmp_path) -> None:
    repo = _repo(tmp_path)
    route_capture = _route(tmp_path)
    routing_replay = reconstruct_conversational_cli_routing_replay(
        route_capture["conversational_cli_routing_replay_reference"]
    )
    proposal = _proposal(route_capture)
    approval = _approval(proposal)

    capture = _execute(repo, tmp_path / "governed_development_replay", route_capture, proposal, approval)
    workflow_replay = reconstruct_governed_development_workflow_replay(
        capture["governed_development_replay_reference"]
    )
    governance_replay = reconstruct_governance_artifact_creation_replay(
        capture["governance_artifact_creation_capture"]["governance_artifact_creation_replay_reference"]
    )
    repository_replay = reconstruct_governed_repository_mutation_replay(
        capture["governed_repository_mutation_capture"]["governed_repository_mutation_replay_reference"]
    )
    governance_validation = reconstruct_validation_command_replay(
        tmp_path
        / "governed_development_replay"
        / "governance_artifact_creation"
        / "validation_command"
    )
    repository_validation = reconstruct_validation_command_replay(
        tmp_path
        / "governed_development_replay"
        / "governed_repository_mutation"
        / "validation_command"
    )

    assert route_capture["routing_status"] == WORKFLOW_SELECTED
    assert route_capture["workflow_id"] == GOVERNED_DEVELOPMENT_WORKFLOW
    assert route_capture["workflow_selection_artifact"]["intent_family"] == DEVELOPMENT_INTENT
    assert route_capture["workflow_selection_artifact"]["human_intent_intake"]["intent_family"] == DEVELOPMENT_INTENT
    assert routing_replay["workflow_id"] == GOVERNED_DEVELOPMENT_WORKFLOW
    assert routing_replay["worker_invoked"] is False
    assert routing_replay["approval_bypassed"] is False

    assert approval["proposal_hash"] == proposal["artifact_hash"]
    assert approval["approved_governance_artifact_proposal_hash"] == proposal["governance_artifact_proposal"][
        "artifact_hash"
    ]
    assert approval["approved_repository_mutation_proposal_hash"] == proposal["repository_mutation_proposal"][
        "artifact_hash"
    ]
    assert approval["approval_bypassed"] is False

    assert capture["execution_status"] == GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED
    assert capture["approval_bypassed"] is False
    assert capture["repository_mutation_worker_protections_preserved"] is True
    assert capture["validation_allowlists_preserved"] is True
    assert workflow_replay["execution_status"] == GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED
    assert workflow_replay["component_order"] == ["GOVERNANCE_ARTIFACT_CREATION", "GOVERNED_REPOSITORY_MUTATION"]
    assert workflow_replay["human_authority_preserved"] is True
    assert workflow_replay["replay_lineage_preserved"] is True

    assert governance_replay["creation_status"] == GOVERNANCE_ARTIFACT_CREATION_COMPLETED
    assert repository_replay["execution_status"] == GOVERNED_REPOSITORY_MUTATION_COMPLETED
    assert repository_replay["repository_mutation_worker_used"] is True
    assert governance_validation["command_status"] == VALIDATION_COMMAND_COMPLETED
    assert repository_validation["command_status"] == VALIDATION_COMMAND_COMPLETED
    assert governance_validation["allowlist_enforced"] is True
    assert repository_validation["allowlist_enforced"] is True

    assert (repo / proposal["governance_artifact_proposal"]["target_path"]).exists()
    assert (repo / proposal["repository_mutation_proposal"]["target_paths"][0]).exists()


def test_governed_development_end_to_end_certification_fails_closed_without_approval(tmp_path) -> None:
    repo = _repo(tmp_path)
    route_capture = _route(tmp_path)
    proposal = _proposal(route_capture)

    capture = _execute(repo, tmp_path / "missing_approval_replay", route_capture, proposal, None)

    assert capture["execution_status"] == FAILED_CLOSED
    assert "FAIL_CLOSED_NO_APPROVAL" in capture["failure_reason"]
    assert capture["approval_bypassed"] is False
    assert not (repo / proposal["governance_artifact_proposal"]["target_path"]).exists()
    assert not (repo / proposal["repository_mutation_proposal"]["target_paths"][0]).exists()


def test_governed_development_end_to_end_certification_fails_closed_on_proposal_hash_mismatch(tmp_path) -> None:
    repo = _repo(tmp_path)
    route_capture = _route(tmp_path)
    proposal = _proposal(route_capture)
    approval = _approval(proposal)
    tampered_proposal = deepcopy(proposal)
    tampered_content = "CERTIFIED_REPLAY_VALIDATION = 'tampered-after-approval'\n"
    tampered_proposal["repository_mutation_proposal"]["file_mutations"][0]["new_content"] = tampered_content
    tampered_proposal["repository_mutation_proposal"]["file_mutations"][0]["new_content_hash"] = replay_hash(
        tampered_content
    )
    tampered_proposal["repository_mutation_proposal"]["artifact_hash"] = replay_hash(
        {
            key: value
            for key, value in tampered_proposal["repository_mutation_proposal"].items()
            if key != "artifact_hash"
        }
    )
    tampered_proposal["artifact_hash"] = replay_hash(
        {key: value for key, value in tampered_proposal.items() if key != "artifact_hash"}
    )

    capture = _execute(repo, tmp_path / "tampered_proposal_replay", route_capture, tampered_proposal, approval)

    assert capture["execution_status"] == FAILED_CLOSED
    assert "FAIL_CLOSED_APPROVAL_SCOPE_MISMATCH" in capture["failure_reason"]
    assert capture["approval_bypassed"] is False
    assert not (repo / proposal["governance_artifact_proposal"]["target_path"]).exists()
    assert not (repo / proposal["repository_mutation_proposal"]["target_paths"][0]).exists()
