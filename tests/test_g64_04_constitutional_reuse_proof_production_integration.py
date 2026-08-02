from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import subprocess

import pytest

from aigol.runtime.constitutional_development_governance_operational_integration import (
    G47_OPERATIONAL_INTEGRATION_READY,
    integrate_constitutional_development_governance,
)
from aigol.runtime.constitutional_reuse_proof_production_gate import (
    APPLICABILITY_UNRESOLVED,
    NOT_APPLICABLE,
    READY_FOR_FRESH_G47,
    REQUIRED,
    WAITING_FOR_REUSE_PROOF_EVIDENCE,
    bind_reuse_proof_admission_to_g47,
    classify_reuse_proof_applicability,
    prepare_reuse_proof_production_admission,
    validate_reuse_proof_g47_scope_binding,
)
from aigol.runtime.governed_repository_mutation_runtime import (
    APPROVED,
    FAILED_CLOSED,
    create_governed_repository_mutation_approval,
    create_governed_repository_mutation_proposal,
    execute_governed_repository_mutation,
)
from aigol.runtime.governed_development_workflow_runtime import (
    AWAITING_CONSTITUTIONAL_CERTIFICATION_AND_PROMOTION,
    create_governed_development_approval,
    create_governed_development_proposal,
    execute_governed_development_workflow,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.acli_governed_development_execution_bridge import (
    FAILED_CLOSED as ACLI_FAILED_CLOSED,
    propose_acli_governed_development_execution,
)
from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-08-02T00:00:00Z"
REQUEST = (
    "Fix the regressed human interface terminal summary and restore its exact "
    "certified presentation behavior. Include focused tests and validation."
)
BASELINE = {
    "commit": "1" * 40,
    "parent": "2" * 40,
    "tree": "3" * 40,
    "worktree_clean": True,
    "governing_sources": [
        {
            "path": "docs/governance/G64_03_CONSTITUTIONAL_REUSE_PROOF_PRODUCTION_INTEGRATION_DESIGN_REPORT_V1.md",
            "sha256": replay_hash("G64-03"),
        }
    ],
    "known_limitations": ["Focused fixture baseline for deterministic gate validation."],
}
EXEMPTION_EVIDENCE = {
    "evidence_complete": True,
    "architecture_delta": False,
    "prior_certification_hash": replay_hash("prior exact certification"),
    "diagnosed_divergence": "presentation regression",
    "exact_repair_scope": "restore certified terminal summary presentation",
}


def _workspace(tmp_path: Path, name: str) -> Path:
    workspace = tmp_path / name
    workspace.mkdir()
    subprocess.run(["git", "init"], cwd=workspace, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "g64@example.invalid"], cwd=workspace, check=True)
    subprocess.run(["git", "config", "user.name", "G64 Test"], cwd=workspace, check=True)
    (workspace / "BASELINE.txt").write_text("one\n", encoding="utf-8")
    subprocess.run(["git", "add", "BASELINE.txt"], cwd=workspace, check=True)
    subprocess.run(["git", "commit", "-m", "baseline parent"], cwd=workspace, check=True, capture_output=True)
    (workspace / "BASELINE.txt").write_text("two\n", encoding="utf-8")
    subprocess.run(["git", "add", "BASELINE.txt"], cwd=workspace, check=True)
    subprocess.run(["git", "commit", "-m", "baseline head"], cwd=workspace, check=True, capture_output=True)
    return workspace


def _baseline(workspace: Path) -> dict:
    def git_value(*args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=workspace, check=True, capture_output=True, text=True
        ).stdout.strip()

    return {
        "commit": git_value("rev-parse", "HEAD"),
        "parent": git_value("rev-parse", "HEAD^"),
        "tree": git_value("rev-parse", "HEAD^{tree}"),
        "worktree_clean": True,
        "governing_sources": deepcopy(BASELINE["governing_sources"]),
        "known_limitations": deepcopy(BASELINE["known_limitations"]),
    }


def _project_context(tmp_path: Path, name: str, *, admitted: bool) -> dict:
    workspace = _workspace(tmp_path, f"{name}-workspace")
    kwargs = {}
    if admitted:
        kwargs = {
            "reuse_proof_exemption_code": "EXACT_CERTIFIED_BEHAVIOR_REPAIR",
            "reuse_proof_exemption_evidence": deepcopy(EXEMPTION_EVIDENCE),
            "reuse_proof_authenticated_baseline": _baseline(workspace),
        }
    return prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id=name,
        message=REQUEST,
        runtime_root=tmp_path / "runtime",
        workspace=workspace,
        created_at=CREATED_AT,
        **kwargs,
    )


def _binding_for_paths(
    tmp_path: Path,
    target_paths: list[str],
    *,
    scope_additions: dict | None = None,
) -> dict:
    context = _project_context(tmp_path, "G64-04-BASE", admitted=True)
    workspace = Path(context["workspace"])
    baseline = context["reuse_proof_production_admission"]["authenticated_baseline"]
    objective = context["project_objective_inference"]
    knowledge = context["knowledge_reuse"]
    applicability = classify_reuse_proof_applicability(
        applicability_id="G64-04-MUTATION-APP",
        request_reference="G64-04-MUTATION-REQUEST",
        request_hash=replay_hash(REQUEST),
        project_objective_reference=objective["artifact_type"],
        project_objective_hash=objective["artifact_hash"],
        authenticated_baseline=deepcopy(baseline),
        proposed_scope={
            "entry_point": "GOVERNED_REPOSITORY_MUTATION",
            "target_paths": target_paths,
            **(scope_additions or {}),
        },
        change_characteristics={},
        exemption_code="EXACT_CERTIFIED_BEHAVIOR_REPAIR",
        exemption_evidence=deepcopy(EXEMPTION_EVIDENCE),
        created_at=CREATED_AT,
    )
    admission = prepare_reuse_proof_production_admission(
        admission_id="G64-04-MUTATION-ADMISSION",
        applicability_artifact=applicability,
        repository_root=workspace,
        created_at=CREATED_AT,
    )
    g47 = integrate_constitutional_development_governance(
        request=REQUEST,
        project_objective_artifact=objective,
        knowledge_reuse_artifact=knowledge,
        workspace_state=None,
        workspace=workspace,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "direct-g47",
        reuse_proof_admission=admission,
    )
    return bind_reuse_proof_admission_to_g47(
        admission_artifact=admission,
        g47_operational_record=g47,
    )


def test_architecture_affecting_work_waits_without_proof_deterministically(
    tmp_path: Path,
) -> None:
    applicability = classify_reuse_proof_applicability(
        applicability_id="G64-04-REQUIRED",
        request_reference="REQUEST",
        request_hash=replay_hash(REQUEST),
        project_objective_reference=None,
        project_objective_hash=None,
        authenticated_baseline=deepcopy(BASELINE),
        proposed_scope={"target_paths": ["aigol/runtime/new_owner.py"]},
        change_characteristics={"creates_component": True},
        created_at=CREATED_AT,
    )
    repeated = classify_reuse_proof_applicability(
        applicability_id="G64-04-REQUIRED",
        request_reference="REQUEST",
        request_hash=replay_hash(REQUEST),
        project_objective_reference=None,
        project_objective_hash=None,
        authenticated_baseline=deepcopy(BASELINE),
        proposed_scope={"target_paths": ["aigol/runtime/new_owner.py"]},
        change_characteristics={"creates_component": True},
        created_at=CREATED_AT,
    )
    admission = prepare_reuse_proof_production_admission(
        admission_id="G64-04-WAITING",
        applicability_artifact=applicability,
        repository_root=tmp_path,
        created_at=CREATED_AT,
    )

    assert applicability["applicability_disposition"] == REQUIRED
    assert repeated == applicability
    assert admission["admission_status"] == WAITING_FOR_REUSE_PROOF_EVIDENCE
    assert admission["planning_authorized"] is False
    assert admission["worker_invoked"] is False


def test_unknown_non_architectural_claim_is_not_silently_exempted() -> None:
    applicability = classify_reuse_proof_applicability(
        applicability_id="G64-04-UNRESOLVED",
        request_reference="REQUEST",
        request_hash=replay_hash(REQUEST),
        project_objective_reference=None,
        project_objective_hash=None,
        authenticated_baseline=deepcopy(BASELINE),
        proposed_scope={"target_paths": []},
        change_characteristics={},
        created_at=CREATED_AT,
    )
    admission = prepare_reuse_proof_production_admission(
        admission_id="G64-04-UNRESOLVED-ADMISSION",
        applicability_artifact=applicability,
        repository_root=".",
        created_at=CREATED_AT,
    )

    assert applicability["applicability_disposition"] == "UNRESOLVED"
    assert admission["admission_status"] == APPLICABILITY_UNRESOLVED


def test_project_services_invokes_gate_and_blocks_g47_without_proof(
    tmp_path: Path,
) -> None:
    context = _project_context(tmp_path, "G64-04-BLOCKED", admitted=False)

    assert context["reuse_proof_production_admission"]["admission_status"] == (
        WAITING_FOR_REUSE_PROOF_EVIDENCE
    )
    assert context["constitutional_development_governance"] is None
    assert context["canonical_implementation_turn_binding"] is None
    assert context["development_intent_resolution"]["summary_admissible"] is False


def test_proven_exemption_still_runs_fresh_g47_and_binds_scope(
    tmp_path: Path,
) -> None:
    context = _project_context(tmp_path, "G64-04-EXEMPT", admitted=True)
    admission = context["reuse_proof_production_admission"]
    binding = context["reuse_proof_g47_scope_binding"]

    assert admission["applicability_artifact"]["applicability_disposition"] == NOT_APPLICABLE
    assert admission["admission_status"] == READY_FOR_FRESH_G47
    assert admission["proof_requirement"] == "NOT_APPLICABLE_PROVEN"
    assert context["constitutional_development_governance"]["integration_status"] == (
        G47_OPERATIONAL_INTEGRATION_READY
    )
    assert binding["admission_hash"] == admission["artifact_hash"]
    assert validate_reuse_proof_g47_scope_binding(binding) == binding


def test_direct_g47_without_mandatory_admission_cannot_start(tmp_path: Path) -> None:
    context = _project_context(tmp_path, "G64-04-DIRECT", admitted=True)
    with pytest.raises(TypeError, match="reuse_proof_admission"):
        integrate_constitutional_development_governance(
            request=REQUEST,
            project_objective_artifact=context["project_objective_inference"],
            knowledge_reuse_artifact=context["knowledge_reuse"],
            workspace_state=None,
            workspace=tmp_path,
            created_at=CREATED_AT,
            replay_dir=tmp_path / "missing-admission",
        )


def test_acli_proposal_cannot_become_approval_ready_without_scope_binding(
    tmp_path: Path,
) -> None:
    workspace = _workspace(tmp_path, "G64-04-ACLI-workspace")
    routing_decision = {
        "routing_decision_id": "ROUTING",
        "artifact_hash": replay_hash("routing"),
    }
    workflow_selection = {
        "workflow_selection_id": "WORKFLOW",
        "workflow_id": "GOVERNED_DEVELOPMENT_WORKFLOW",
        "human_intent_intake": {},
        "artifact_hash": replay_hash("workflow"),
    }
    capture = propose_acli_governed_development_execution(
        bridge_id="G64-04-ACLI",
        prompt_id="PROMPT",
        human_prompt="Create a new runtime adapter.",
        conversational_routing_capture={
            "routing_decision_artifact": routing_decision,
            "workflow_selection_artifact": workflow_selection,
            "conversational_cli_routing_replay_reference": "REPLAY",
            "conversational_cli_routing_hash": replay_hash("routing replay"),
        },
        universal_intake_artifact={
            "universal_intake_id": "INTAKE",
            "artifact_hash": replay_hash("intake"),
        },
        workspace_root=workspace,
        proposed_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "acli-replay",
    )

    assert capture["bridge_status"] == ACLI_FAILED_CLOSED
    assert capture["approval_required"] is False
    assert capture["mutation_performed"] is False
    assert capture["worker_invoked"] is False
    assert "scope binding" in capture["failure_reason"]


def test_mutation_proposal_requires_current_scope_bound_lineage(tmp_path: Path) -> None:
    target = "aigol/runtime/exact_repair.py"
    binding = _binding_for_paths(tmp_path, [target])
    mutation = {
        "target_path": target,
        "operation": "CREATE_OR_REPLACE",
        "new_content": "VALUE = 1\n",
        "new_content_hash": replay_hash("VALUE = 1\n"),
        "approved": True,
    }
    proposal = create_governed_repository_mutation_proposal(
        proposal_id="G64-04-MUTATION",
        original_request_reference="REQUEST",
        resolved_intent_reference="INTENT",
        file_mutations=[mutation],
        validation_command=["git", "diff", "--check"],
        replay_references=["REPLAY"],
        replay_hashes=[replay_hash("replay")],
        created_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        reuse_proof_g47_scope_binding=binding,
    )

    assert proposal["reuse_proof_g47_scope_binding_hash"] == binding["artifact_hash"]
    approval = create_governed_repository_mutation_approval(
        approval_id="G64-04-MUTATION-APPROVAL",
        proposal_artifact=proposal,
        decision=APPROVED,
        approved_by="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
        replay_references=["REPLAY"],
        replay_hashes=[proposal["artifact_hash"]],
    )
    capture = execute_governed_repository_mutation(
        execution_id="G64-04-MUTATION-EXECUTION",
        request_artifact={"request_id": "REQUEST", "artifact_hash": replay_hash({"request_id": "REQUEST"})},
        intent_artifact={"intent_id": "INTENT", "artifact_hash": replay_hash({"intent_id": "INTENT"})},
        workflow_artifact={"workflow_id": "GOVERNED_REPOSITORY_MUTATION"},
        repository_context_artifact={"target_paths": [target], "context_fresh": True},
        proposal_artifact=proposal,
        approval_artifact=approval,
        repository_root=tmp_path / "G64-04-BASE-workspace",
        executed_by="AIGOL_GOVERNED_REPOSITORY_MUTATION_RUNTIME",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "mutation-replay",
    )
    assert capture["execution_status"] == "GOVERNED_REPOSITORY_MUTATION_COMPLETED"
    assert capture["worker_invoked"] is True
    tampered = deepcopy(binding)
    tampered["scope_digest"] = replay_hash("different")
    with pytest.raises(FailClosedRuntimeError):
        create_governed_repository_mutation_proposal(
            proposal_id="G64-04-TAMPERED",
            original_request_reference="REQUEST",
            resolved_intent_reference="INTENT",
            file_mutations=[mutation],
            validation_command=["git", "diff", "--check"],
            replay_references=["REPLAY"],
            replay_hashes=[replay_hash("replay")],
            created_by="HUMAN_OPERATOR",
            created_at=CREATED_AT,
            reuse_proof_g47_scope_binding=tampered,
        )


def test_stale_baseline_refuses_before_worker_invocation(tmp_path: Path) -> None:
    target = "aigol/runtime/exact_repair.py"
    binding = _binding_for_paths(tmp_path, [target])
    mutation = {
        "target_path": target,
        "operation": "CREATE_OR_REPLACE",
        "new_content": "VALUE = 1\n",
        "new_content_hash": replay_hash("VALUE = 1\n"),
        "approved": True,
    }
    proposal = create_governed_repository_mutation_proposal(
        proposal_id="G64-04-STALE",
        original_request_reference="REQUEST",
        resolved_intent_reference="INTENT",
        file_mutations=[mutation],
        validation_command=["git", "diff", "--check"],
        replay_references=["REPLAY"],
        replay_hashes=[replay_hash("replay")],
        created_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        reuse_proof_g47_scope_binding=binding,
    )
    approval = create_governed_repository_mutation_approval(
        approval_id="G64-04-STALE-APPROVAL",
        proposal_artifact=proposal,
        decision=APPROVED,
        approved_by="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
        replay_references=["REPLAY"],
        replay_hashes=[proposal["artifact_hash"]],
    )
    workspace = tmp_path / "G64-04-BASE-workspace"
    (workspace / "UNAUTHENTICATED.txt").write_text("drift\n", encoding="utf-8")
    capture = execute_governed_repository_mutation(
        execution_id="G64-04-STALE-EXECUTION",
        request_artifact={"request_id": "REQUEST", "artifact_hash": replay_hash({"request_id": "REQUEST"})},
        intent_artifact={"intent_id": "INTENT", "artifact_hash": replay_hash({"intent_id": "INTENT"})},
        workflow_artifact={"workflow_id": "GOVERNED_REPOSITORY_MUTATION"},
        repository_context_artifact={"target_paths": [target], "context_fresh": True},
        proposal_artifact=proposal,
        approval_artifact=approval,
        repository_root=workspace,
        executed_by="AIGOL_GOVERNED_REPOSITORY_MUTATION_RUNTIME",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "stale-replay",
    )

    assert capture["execution_status"] == FAILED_CLOSED
    assert capture["worker_invoked"] is False
    assert capture["repository_mutation_performed"] is False
    assert "UNAUTHENTICATED_DRIFT" in capture["failure_reason"]


def test_governed_development_revalidates_before_each_component(tmp_path: Path) -> None:
    target = "aigol/runtime/exact_development_repair.py"
    governance_target = "docs/governance/G64_04_EXACT_REPAIR_EVIDENCE.md"
    governance_content = "# G64-04 Exact Repair Evidence\n\nStatus: Validated\n"
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
        proposal_id="G64-04-DEVELOPMENT",
        original_request_reference="REQUEST",
        resolved_intent_reference="INTENT",
        governance_artifact={
            "target_path": governance_target,
            "artifact_title": "G64_04_EXACT_REPAIR_EVIDENCE",
            "artifact_purpose": "Record exact certified behavior repair evidence.",
            "proposed_content": governance_content,
            "expected_sections": ["Status"],
        },
        repository_file_mutations=[
            {
                "target_path": target,
                "operation": "CREATE_OR_REPLACE",
                "new_content": "VALUE = 1\n",
                "new_content_hash": replay_hash("VALUE = 1\n"),
                "approved": True,
            }
        ],
        repository_validation_command=["git", "diff", "--check"],
        replay_references=["REPLAY"],
        replay_hashes=[replay_hash("replay")],
        created_by="HUMAN_OPERATOR",
        created_at=CREATED_AT,
        reuse_proof_g47_scope_binding=binding,
    )
    approval = create_governed_development_approval(
        approval_id="G64-04-DEVELOPMENT-APPROVAL",
        proposal_artifact=proposal,
        decision=APPROVED,
        approved_by="HUMAN_OPERATOR",
        approved_at=CREATED_AT,
        replay_references=["REPLAY"],
        replay_hashes=[proposal["artifact_hash"]],
    )
    workspace = tmp_path / "G64-04-BASE-workspace"
    capture = execute_governed_development_workflow(
        execution_id="G64-04-DEVELOPMENT-EXECUTION",
        request_artifact={"request_id": "REQUEST", "artifact_hash": replay_hash({"request_id": "REQUEST"})},
        intent_artifact={"intent_id": "INTENT", "artifact_hash": replay_hash({"intent_id": "INTENT"})},
        workflow_artifact={"workflow_id": "GOVERNED_DEVELOPMENT_WORKFLOW"},
        repository_context_artifact={"context_fresh": True},
        proposal_artifact=proposal,
        approval_artifact=approval,
        repository_root=workspace,
        executed_by="AIGOL_GOVERNED_DEVELOPMENT_WORKFLOW_RUNTIME",
        executed_at=CREATED_AT,
        replay_dir=tmp_path / "development-replay",
    )

    assert (
        capture["execution_status"]
        == AWAITING_CONSTITUTIONAL_CERTIFICATION_AND_PROMOTION
    ), capture["failure_reason"]
    assert (workspace / governance_target).is_file()
    assert (workspace / target).is_file()
