"""Certification for cognition-to-governed-execution lineage."""

from __future__ import annotations

from copy import deepcopy
import json
import subprocess
from pathlib import Path

from aigol.runtime.conversational_cli_runtime import (
    GOVERNED_DEVELOPMENT_WORKFLOW,
    WORKFLOW_SELECTED,
    reconstruct_conversational_cli_routing_replay,
    route_conversational_cli_intent,
)
from aigol.runtime.governance_artifact_creation_runtime import reconstruct_governance_artifact_creation_replay
from aigol.runtime.governed_development_workflow_runtime import (
    APPROVED,
    FAILED_CLOSED,
    GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED,
    create_governed_development_approval,
    create_governed_development_proposal,
    execute_governed_development_workflow,
    reconstruct_governed_development_workflow_replay,
)
from aigol.runtime.governed_repository_mutation_runtime import reconstruct_governed_repository_mutation_replay
from aigol.runtime.multi_provider_cognition_runtime import create_default_cognition_provider_contract
from aigol.runtime.ocs_llm_cognition_end_to_end_runtime import (
    STATUS_COMPLETED,
    reconstruct_ocs_llm_cognition_end_to_end_replay,
    run_ocs_llm_cognition_end_to_end,
)
from aigol.runtime.transport.serialization import replay_hash
from aigol.runtime.validation_command_runner_runtime import (
    VALIDATION_COMMAND_COMPLETED,
    reconstruct_validation_command_replay,
)


CREATED_AT = "2026-06-23T00:00:00Z"
HUMAN_QUESTION = "Should we add replay validation to the governed runtime?"
DEVELOPMENT_REQUEST = "Add replay validation"


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "docs" / "governance").mkdir(parents=True)
    (repo / "aigol" / "runtime").mkdir(parents=True)
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    return repo


def _artifact_hash(payload: dict) -> dict:
    artifact = dict(payload)
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _source_context() -> dict:
    source = {
        "artifact_type": "HUMAN_QUESTION_ARTIFACT_V1",
        "artifact_id": "COGNITION-TO-EXECUTION-HUMAN-QUESTION-000001",
        "summary": HUMAN_QUESTION,
        "replay_visible": True,
        "approval_created": False,
        "execution_requested": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    source["artifact_hash"] = replay_hash(source)
    return {"conversation_context": [source]}


def _provider_payload(provider_id: str) -> str:
    return json.dumps(
        {
            "findings": [
                "Replay validation should remain governed before repository mutation.",
                f"{provider_id} recommends human review before execution.",
            ],
            "assumptions": ["Provider output is advisory and non-authoritative."],
            "alternatives": ["Do nothing", "Create a governed development proposal"],
            "risks": ["Skipping approval would violate governance boundaries."],
            "uncertainties": ["Final implementation scope requires human approval."],
            "confidence": "HIGH",
        },
        sort_keys=True,
    )


def _ocs_capture(tmp_path: Path) -> dict:
    providers = ("provider-a", "provider-b", "provider-c")

    def _transport(_payload: dict, metadata: dict) -> dict:
        provider_id = metadata["provider_id"]
        return {"output_text": _provider_payload(provider_id)}

    return run_ocs_llm_cognition_end_to_end(
        end_to_end_id="COGNITION-TO-GOVERNED-EXECUTION-OCS-000001",
        human_question=HUMAN_QUESTION,
        source_context=_source_context(),
        provider_contracts=[
            create_default_cognition_provider_contract(provider_id=provider_id, created_at=CREATED_AT)
            for provider_id in providers
        ],
        transport_registry={provider_id: _transport for provider_id in providers},
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ocs_cognition",
        source_chain_id="CHAIN-COGNITION-TO-GOVERNED-EXECUTION-000001",
        source_request_reference="COGNITION-TO-EXECUTION-HUMAN-QUESTION-000001",
        single_provider_primary_mode=False,
    )


def _human_review(ocs_capture: dict) -> dict:
    artifact = {
        "artifact_type": "COGNITION_TO_EXECUTION_HUMAN_REVIEW_ARTIFACT_V1",
        "review_id": "COGNITION-TO-GOVERNED-EXECUTION-HUMAN-REVIEW-000001",
        "review_decision": "PROCEED_TO_GOVERNED_DEVELOPMENT_WORKFLOW",
        "ocs_replay_reference": ocs_capture["replay_reference"],
        "ocs_capture_hash": ocs_capture["ocs_llm_cognition_end_to_end_hash"],
        "comparison_artifact_hash": ocs_capture["ocs_llm_cognition_end_to_end_artifact"]["comparison_artifact_hash"],
        "human_authority_preserved": True,
        "provider_authority_granted": False,
        "comparison_authority_granted": False,
        "approval_created": False,
        "execution_authorized": False,
        "worker_invoked": False,
        "created_at": CREATED_AT,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _route(tmp_path: Path, human_review: dict) -> dict:
    return route_conversational_cli_intent(
        routing_id="COGNITION-TO-GOVERNED-EXECUTION-ROUTING-000001",
        prompt_id="COGNITION-TO-GOVERNED-EXECUTION-TURN-000001",
        human_prompt=DEVELOPMENT_REQUEST,
        canonical_chain_id="CHAIN-COGNITION-TO-GOVERNED-EXECUTION-000001",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "development_routing",
    )


def _file_mutation() -> dict:
    content = "COGNITION_TO_EXECUTION_REPLAY_VALIDATION = True\n"
    return {
        "target_path": "aigol/runtime/cognition_to_execution_replay_validation.py",
        "operation": "CREATE_OR_REPLACE",
        "new_content": content,
        "new_content_hash": replay_hash(content),
        "approved": True,
    }


def _proposal(route_capture: dict, ocs_capture: dict, human_review: dict) -> dict:
    decision = route_capture["routing_decision_artifact"]
    selection = route_capture["workflow_selection_artifact"]
    return create_governed_development_proposal(
        proposal_id="COGNITION-TO-GOVERNED-EXECUTION-PROPOSAL-000001",
        original_request_reference=human_review["review_id"],
        resolved_intent_reference=selection["workflow_selection_id"],
        governance_artifact={
            "target_path": "docs/governance/COGNITION_TO_EXECUTION_REPLAY_VALIDATION_ARTIFACT_V1.md",
            "artifact_title": "COGNITION_TO_EXECUTION_REPLAY_VALIDATION_ARTIFACT_V1",
            "artifact_purpose": "Record the cognition-to-governed-execution certification fixture.",
            "proposed_content": "# COGNITION_TO_EXECUTION_REPLAY_VALIDATION_ARTIFACT_V1\n\nStatus: Defined\n",
            "expected_sections": ["Status"],
        },
        repository_file_mutations=[_file_mutation()],
        repository_validation_command=["git", "diff", "--check"],
        replay_references=[
            ocs_capture["replay_reference"],
            human_review["review_id"],
            route_capture["conversational_cli_routing_replay_reference"],
            decision["routing_decision_id"],
            selection["workflow_selection_id"],
        ],
        replay_hashes=[
            ocs_capture["ocs_llm_cognition_end_to_end_hash"],
            human_review["artifact_hash"],
            route_capture["conversational_cli_routing_hash"],
            decision["artifact_hash"],
            selection["artifact_hash"],
        ],
        created_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
    )


def _approval(proposal: dict, human_review: dict) -> dict:
    return create_governed_development_approval(
        approval_id="COGNITION-TO-GOVERNED-EXECUTION-APPROVAL-000001",
        proposal_artifact=proposal,
        decision=APPROVED,
        approved_by="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
        replay_references=[human_review["review_id"], proposal["proposal_id"]],
        replay_hashes=[human_review["artifact_hash"], proposal["artifact_hash"]],
    )


def _request_artifact(ocs_capture: dict, human_review: dict) -> dict:
    return _artifact_hash(
        {
            "artifact_type": "COGNITION_TO_GOVERNED_EXECUTION_REQUEST_ARTIFACT_V1",
            "request_id": "COGNITION-TO-GOVERNED-EXECUTION-REQUEST-000001",
            "human_question": HUMAN_QUESTION,
            "development_request": DEVELOPMENT_REQUEST,
            "ocs_replay_reference": ocs_capture["replay_reference"],
            "human_review_reference": human_review["review_id"],
            "created_at": CREATED_AT,
        }
    )


def _intent_artifact(route_capture: dict, human_review: dict) -> dict:
    intake = deepcopy(route_capture["workflow_selection_artifact"]["human_intent_intake"])
    intake["artifact_type"] = "COGNITION_TO_GOVERNED_EXECUTION_INTENT_ARTIFACT_V1"
    intake["intent_id"] = "COGNITION-TO-GOVERNED-EXECUTION-INTENT-000001"
    intake["human_review_hash"] = human_review["artifact_hash"]
    intake["artifact_hash"] = replay_hash(intake)
    return intake


def _context_artifact(proposal: dict) -> dict:
    return _artifact_hash(
        {
            "artifact_type": "COGNITION_TO_GOVERNED_EXECUTION_REPOSITORY_CONTEXT_ARTIFACT_V1",
            "context_id": "COGNITION-TO-GOVERNED-EXECUTION-CONTEXT-000001",
            "context_fresh": True,
            "target_paths": proposal["repository_mutation_proposal"]["target_paths"],
            "governance_target_path": proposal["governance_artifact_proposal"]["target_path"],
            "created_at": CREATED_AT,
        }
    )


def _execute(repo: Path, replay_dir: Path, route_capture: dict, ocs_capture: dict, human_review: dict, proposal: dict, approval: dict | None) -> dict:
    return execute_governed_development_workflow(
        execution_id="COGNITION-TO-GOVERNED-EXECUTION-EXECUTION-000001",
        request_artifact=_request_artifact(ocs_capture, human_review),
        intent_artifact=_intent_artifact(route_capture, human_review),
        workflow_artifact=route_capture["workflow_selection_artifact"],
        repository_context_artifact=_context_artifact(proposal),
        proposal_artifact=proposal,
        approval_artifact=approval,
        repository_root=repo,
        executed_by="AIGOL_COGNITION_TO_GOVERNED_EXECUTION_CERTIFICATION",
        executed_at=CREATED_AT,
        replay_dir=replay_dir,
    )


def test_cognition_to_governed_execution_certifies_single_governance_chain(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    ocs_capture = _ocs_capture(tmp_path)
    ocs_replay = reconstruct_ocs_llm_cognition_end_to_end_replay(ocs_capture["replay_reference"])
    human_review = _human_review(ocs_capture)
    route_capture = _route(tmp_path, human_review)
    routing_replay = reconstruct_conversational_cli_routing_replay(route_capture["conversational_cli_routing_replay_reference"])
    proposal = _proposal(route_capture, ocs_capture, human_review)
    approval = _approval(proposal, human_review)

    capture = _execute(repo, tmp_path / "governed_development", route_capture, ocs_capture, human_review, proposal, approval)
    governed_replay = reconstruct_governed_development_workflow_replay(capture["governed_development_replay_reference"])
    governance_replay = reconstruct_governance_artifact_creation_replay(
        capture["governance_artifact_creation_capture"]["governance_artifact_creation_replay_reference"]
    )
    mutation_replay = reconstruct_governed_repository_mutation_replay(
        capture["governed_repository_mutation_capture"]["governed_repository_mutation_replay_reference"]
    )
    repository_validation = reconstruct_validation_command_replay(
        tmp_path / "governed_development" / "governed_repository_mutation" / "validation_command"
    )

    assert ocs_capture["final_status"] == STATUS_COMPLETED
    assert ocs_capture["approval_created"] is False
    assert ocs_capture["execution_requested"] is False
    assert ocs_capture["worker_invoked"] is False
    assert all(value is False for value in ocs_capture["authority_flags"].values())
    assert ocs_replay["selected_cognition_mode"] == "MULTI_PROVIDER_COMPARISON"
    assert ocs_replay["stage_replay"]["cognition_comparison"]["source_cognition_artifact_count"] == 3
    assert ocs_replay["stage_replay"]["cognition_comparison"]["authority_flags"]
    assert all(value is False for value in ocs_replay["stage_replay"]["cognition_comparison"]["authority_flags"].values())

    assert human_review["human_authority_preserved"] is True
    assert human_review["provider_authority_granted"] is False
    assert human_review["comparison_authority_granted"] is False
    assert human_review["execution_authorized"] is False

    assert route_capture["routing_status"] == WORKFLOW_SELECTED
    assert routing_replay["workflow_id"] == GOVERNED_DEVELOPMENT_WORKFLOW
    assert approval["proposal_hash"] == proposal["artifact_hash"]
    assert human_review["artifact_hash"] in approval["replay_hashes"]

    assert capture["execution_status"] == GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED
    assert capture["approval_bypassed"] is False
    assert capture["repository_mutation_worker_protections_preserved"] is True
    assert capture["validation_allowlists_preserved"] is True
    assert governed_replay["execution_status"] == GOVERNED_DEVELOPMENT_WORKFLOW_COMPLETED
    assert governed_replay["human_authority_preserved"] is True
    assert governed_replay["replay_lineage_preserved"] is True
    assert governance_replay["replay_lineage_preserved"] is True
    assert mutation_replay["repository_mutation_worker_used"] is True
    assert repository_validation["command_status"] == VALIDATION_COMMAND_COMPLETED
    assert repository_validation["allowlist_enforced"] is True


def test_cognition_to_governed_execution_fails_closed_without_execution_approval(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    ocs_capture = _ocs_capture(tmp_path)
    human_review = _human_review(ocs_capture)
    route_capture = _route(tmp_path, human_review)
    proposal = _proposal(route_capture, ocs_capture, human_review)

    capture = _execute(repo, tmp_path / "missing_approval", route_capture, ocs_capture, human_review, proposal, None)

    assert capture["execution_status"] == FAILED_CLOSED
    assert "FAIL_CLOSED_NO_APPROVAL" in capture["failure_reason"]
    assert capture["approval_bypassed"] is False
    assert not (repo / proposal["governance_artifact_proposal"]["target_path"]).exists()
    assert not (repo / proposal["repository_mutation_proposal"]["target_paths"][0]).exists()
