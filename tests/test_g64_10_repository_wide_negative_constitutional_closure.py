"""G64-10 repository-wide negative constitutional closure matrix.

The matrix calls authenticated public owner seams only. It introduces no
runtime behavior, fixtures, or alternate governance path.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from aigol.cli.aigol_cli import run_interactive_conversation
from aigol.runtime.acli_governed_development_execution_bridge import (
    FAILED_CLOSED as BRIDGE_FAILED_CLOSED,
    propose_acli_governed_development_execution,
)
from aigol.runtime.authenticated_provider_selection_runtime import (
    SELECTION_REPLAY_DIRECTORY,
    reconstruct_authenticated_provider_selection,
    select_authenticated_provider,
    validate_authenticated_provider_selection,
)
from aigol.runtime.constitutional_certification_completion_gate import (
    CONSTITUTIONAL_COMPLETION_FAILED_CLOSED,
    finalize_governed_development_completion,
)
from aigol.runtime.constitutional_governance_certification import (
    certify_constitutional_governance,
)
from aigol.runtime.constitutional_reuse_proof_production_gate import (
    validate_reuse_proof_g47_scope_binding,
)
from aigol.runtime.governed_development_workflow_runtime import (
    APPROVED,
    FAILED_CLOSED as WORKFLOW_FAILED_CLOSED,
    create_governed_development_approval,
    create_governed_development_proposal,
    execute_governed_development_workflow,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import replay_hash
from test_g59_04_conversation_interpreter_proposal_runtime_v2 import (
    OBSERVED,
    PARSER,
    _operation,
    _proposal,
    _registry,
    _state,
    proposal_v2,
)
from test_g64_04_constitutional_reuse_proof_production_integration import (
    CREATED_AT,
    REQUEST,
    _binding_for_paths,
    _project_context,
)
from test_g64_06_acli_positive_constitutional_lineage import (
    REQUEST as ACLI_REQUEST,
    _args,
    _input_sequence,
    _workspace,
)
from test_g64_07_constitutional_certification_completion_gate import (
    _assessment,
    _evidence,
    _pending_capture,
    _promotion,
)


def _development_inputs(tmp_path: Path) -> tuple[dict, dict, Path]:
    target = "aigol/runtime/g64_10_worker_boundary.py"
    governance_target = "docs/governance/G64_10_WORKER_BOUNDARY.md"
    governance_content = "# G64-10 Worker Boundary\n\nStatus: Test fixture\n"
    binding = _binding_for_paths(
        tmp_path,
        [target],
        scope_additions={
            "entry_point": "GOVERNED_DEVELOPMENT_WORKFLOW",
            "governance_target_paths": [governance_target],
            "allowed_intermediate_deltas": [
                {
                    "target_path": governance_target,
                    "content_hash": replay_hash(governance_content.strip()),
                }
            ],
        },
    )
    proposal = create_governed_development_proposal(
        proposal_id="G64-10-DEVELOPMENT",
        original_request_reference="G64-10-REQUEST",
        resolved_intent_reference="G64-10-INTENT",
        governance_artifact={
            "target_path": governance_target,
            "artifact_title": "G64_10_WORKER_BOUNDARY",
            "artifact_purpose": "Exercise the authenticated Worker boundary.",
            "proposed_content": governance_content,
            "expected_sections": ["Status"],
        },
        repository_file_mutations=[
            {
                "target_path": target,
                "operation": "CREATE_OR_REPLACE",
                "new_content": "VALUE = 10\n",
                "new_content_hash": replay_hash("VALUE = 10\n"),
                "approved": True,
            }
        ],
        repository_validation_command=["git", "diff", "--check"],
        replay_references=["G64-10-REPLAY"],
        replay_hashes=[replay_hash("G64-10-REPLAY")],
        created_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        reuse_proof_g47_scope_binding=binding,
    )
    approval = create_governed_development_approval(
        approval_id="G64-10-APPROVAL",
        proposal_artifact=proposal,
        decision=APPROVED,
        approved_by="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
        replay_references=["G64-10-REPLAY"],
        replay_hashes=[proposal["artifact_hash"]],
    )
    return proposal, approval, tmp_path / "G64-04-BASE-workspace"


def _execute_development(
    tmp_path: Path,
    proposal: dict,
    approval: dict | None,
    workspace: Path,
    replay_name: str,
) -> dict:
    return execute_governed_development_workflow(
        execution_id=f"G64-10-{replay_name}",
        request_artifact={
            "request_id": "G64-10-REQUEST",
            "artifact_hash": replay_hash({"request_id": "G64-10-REQUEST"}),
        },
        intent_artifact={
            "intent_id": "G64-10-INTENT",
            "artifact_hash": replay_hash({"intent_id": "G64-10-INTENT"}),
        },
        workflow_artifact={"workflow_id": "GOVERNED_DEVELOPMENT_WORKFLOW"},
        repository_context_artifact={"context_fresh": True},
        proposal_artifact=proposal,
        approval_artifact=approval,
        repository_root=workspace,
        executed_by="AIGOL_G64_10_NEGATIVE_VALIDATION",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / replay_name,
    )


def _bridge_inputs() -> tuple[dict, dict]:
    routing_decision = {
        "routing_decision_id": "G64-10-ROUTING",
        "artifact_hash": replay_hash("G64-10-routing"),
    }
    workflow_selection = {
        "workflow_selection_id": "G64-10-WORKFLOW",
        "workflow_id": "GOVERNED_DEVELOPMENT_WORKFLOW",
        "human_intent_intake": {},
        "artifact_hash": replay_hash("G64-10-workflow"),
    }
    return (
        {
            "routing_decision_artifact": routing_decision,
            "workflow_selection_artifact": workflow_selection,
            "conversational_cli_routing_replay_reference": "G64-10-ROUTING-REPLAY",
            "conversational_cli_routing_hash": replay_hash("G64-10-routing-replay"),
        },
        {
            "universal_intake_id": "G64-10-INTAKE",
            "artifact_hash": replay_hash("G64-10-intake"),
        },
    )


def test_missing_reuse_proof_fails_closed_at_production_admission(tmp_path: Path) -> None:
    context = _project_context(tmp_path, "G64-10-MISSING-REUSE", admitted=False)

    assert context["reuse_proof_production_admission"]["planning_authorized"] is False
    assert context["constitutional_development_governance"] is None
    assert context["canonical_implementation_turn_binding"] is None


def test_missing_g47_governance_fails_closed_at_scope_binding(tmp_path: Path) -> None:
    binding = _binding_for_paths(tmp_path, ["aigol/runtime/g64_10_g47.py"])
    missing_g47 = deepcopy(binding)
    missing_g47.pop("g47_operational_record")

    with pytest.raises(FailClosedRuntimeError, match="g47_operational_record"):
        validate_reuse_proof_g47_scope_binding(missing_g47)


def test_missing_lineage_fails_closed_before_proposal_creation() -> None:
    with pytest.raises(FailClosedRuntimeError, match="scope binding type is invalid"):
        create_governed_development_proposal(
            proposal_id="G64-10-MISSING-LINEAGE",
            original_request_reference="G64-10-REQUEST",
            resolved_intent_reference="G64-10-INTENT",
            governance_artifact={},
            repository_file_mutations=[],
            repository_validation_command=["git", "diff", "--check"],
            replay_references=["G64-10-REPLAY"],
            replay_hashes=[replay_hash("G64-10-REPLAY")],
            created_by="HUMAN_OPERATOR",
            created_at=CREATED_AT,
            reuse_proof_g47_scope_binding={},
        )


def test_missing_certification_fails_closed_at_completion_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pending = _pending_capture(tmp_path, monkeypatch)
    assessment = _assessment()
    certification = certify_constitutional_governance(assessment)
    promotion = _promotion(pending["execution_id"])
    report_evidence = _evidence(
        tmp_path / "G64_10_REPORT.md",
        pending,
        assessment,
        certification,
        promotion,
    )
    capture = finalize_governed_development_completion(
        finalization_id="G64-10-MISSING-CERTIFICATION",
        governed_development_capture=pending,
        g48_report_evidence=report_evidence,
        governance_assessment=assessment,
        constitutional_certification=None,
        promotion_evidence=promotion,
        finalized_by="CONSTITUTIONAL_CERTIFICATION_OWNER",
        finalized_at=CREATED_AT,
        replay_dir=tmp_path / "missing-certification",
    )

    assert capture["completion_status"] == CONSTITUTIONAL_COMPLETION_FAILED_CLOSED
    assert capture["constitutional_completion_reached"] is False
    assert capture["promotion_eligible"] is False


def test_missing_provider_owner_fails_closed() -> None:
    with pytest.raises(FailClosedRuntimeError, match="selection binding is required"):
        validate_authenticated_provider_selection(
            binding=None,
            provider_id="openai",
            required_capability="PROPOSAL_GENERATION",
        )


def test_invalid_provider_owner_fails_closed(tmp_path: Path) -> None:
    binding = select_authenticated_provider(
        selection_id="G64-10-INVALID-PROVIDER-OWNER",
        provider_id="openai",
        workflow_type="G64_10_NEGATIVE_VALIDATION",
        required_capability="PROPOSAL_GENERATION",
        domain_id="GOVERNANCE",
        created_at=CREATED_AT,
        replay_dir=tmp_path,
    )
    invalid = deepcopy(binding)
    invalid["selection_owner"] = "UNAUTHENTICATED_PROVIDER_OWNER"
    invalid.pop("artifact_hash")
    invalid["artifact_hash"] = replay_hash(invalid)

    with pytest.raises(FailClosedRuntimeError, match="provider selection owner is not authenticated"):
        validate_authenticated_provider_selection(
            binding=invalid,
            provider_id="openai",
            required_capability="PROPOSAL_GENERATION",
        )


def test_replay_mismatch_fails_closed_at_provider_owner_reconstruction(tmp_path: Path) -> None:
    binding = select_authenticated_provider(
        selection_id="G64-10-REPLAY-MISMATCH",
        provider_id="openai",
        workflow_type="G64_10_NEGATIVE_VALIDATION",
        required_capability="PROPOSAL_GENERATION",
        domain_id="GOVERNANCE",
        created_at=CREATED_AT,
        replay_dir=tmp_path,
    )
    replay_path = tmp_path / SELECTION_REPLAY_DIRECTORY / "000_resource_selection_recorded.json"
    wrapper = json.loads(replay_path.read_text(encoding="utf-8"))
    wrapper["artifact"]["selected_resource_id"] = "TAMPERED"
    replay_path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="resource selection.*hash mismatch"):
        reconstruct_authenticated_provider_selection(
            replay_dir=tmp_path,
            binding=binding,
            provider_id="openai",
            required_capability="PROPOSAL_GENERATION",
        )


def test_authorization_mismatch_fails_closed_before_worker(tmp_path: Path) -> None:
    proposal, approval, workspace = _development_inputs(tmp_path)
    mismatched = deepcopy(approval)
    mismatched["proposal_hash"] = replay_hash("different proposal")
    mismatched.pop("artifact_hash")
    mismatched["artifact_hash"] = replay_hash(mismatched)

    capture = _execute_development(tmp_path, proposal, mismatched, workspace, "authorization-mismatch")

    assert capture["execution_status"] == WORKFLOW_FAILED_CLOSED
    assert capture["governed_repository_mutation_capture"] is None
    assert "APPROVAL_SCOPE_MISMATCH" in capture["failure_reason"]


def test_bridge_bypass_fails_closed_without_scope_binding(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    routing_capture, universal_intake = _bridge_inputs()
    capture = propose_acli_governed_development_execution(
        bridge_id="G64-10-BRIDGE-BYPASS",
        prompt_id="G64-10-PROMPT",
        human_prompt="Create G64_10_BRIDGE_BYPASS_V1.",
        conversational_routing_capture=routing_capture,
        universal_intake_artifact=universal_intake,
        workspace_root=workspace,
        proposed_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "bridge-bypass",
    )

    assert capture["bridge_status"] == BRIDGE_FAILED_CLOSED
    assert capture["approval_required"] is False
    assert capture["worker_invoked"] is False


def test_aicli_bypass_fails_closed_without_reuse_proof(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    result = run_interactive_conversation(
        _args(tmp_path, workspace, None),
        input_func=_input_sequence([ACLI_REQUEST, "exit"]),
        output_func=lambda _line: None,
    )

    assert result["failed_turns"] == 1
    assert result["worker_invoked"] is False
    assert result["turns"][0]["response_status"] == "FAILED_CLOSED"


def test_project_services_bypass_fails_closed_without_admission(tmp_path: Path) -> None:
    context = _project_context(tmp_path, "G64-10-PROJECT-SERVICES", admitted=False)

    assert context["development_intent_resolution"]["summary_admissible"] is False
    assert context["constitutional_development_governance"] is None


def test_worker_bypass_fails_closed_without_human_approval(tmp_path: Path) -> None:
    proposal, _approval, workspace = _development_inputs(tmp_path)
    capture = _execute_development(tmp_path, proposal, None, workspace, "worker-bypass")

    assert capture["execution_status"] == WORKFLOW_FAILED_CLOSED
    assert capture["governed_repository_mutation_capture"] is None
    assert "NO_APPROVAL" in capture["failure_reason"]


def test_conversation_layer_bypass_rejects_direct_execution_request(tmp_path: Path) -> None:
    state = _state(tmp_path)
    text = "implement"
    proposal = _proposal(state, text, [_operation(state, text)])
    proposal["execution_request"] = {"run": True}
    proposal = proposal_v2._with_proposal_identity_and_integrity(proposal)

    result = proposal_v2.assess_conversation_interpreter_proposal_v2(
        proposal,
        current_state=state,
        source_turn_text=text,
        observed_at=OBSERVED,
        interpreter_registry=_registry((PARSER, proposal_v2.DETERMINISTIC_PARSER)),
    )

    assert result["validation_disposition"] == proposal_v2.REJECTED
    assert result["candidate_operation_set"] is None
    assert result["semantic_cwm_mutated"] is False
    assert result["rejection_reasons"] == ["FORBIDDEN_AUTHORITY_FIELD"]
