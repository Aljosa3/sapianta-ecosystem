from copy import deepcopy

from agol_bridge.providers.codex_cli_provider import build_bounded_codex_prompt
from agol_bridge.runtime.minimal_end_to_end_bridge import run_minimal_end_to_end_bridge
import agol_bridge.runtime.minimal_end_to_end_bridge as bridge_runtime
from agol_bridge.semantic_contract import (
    SEMANTIC_CONTRACT_AUTHORITY_BOUNDARY,
    synthesize_semantic_contract,
    validate_semantic_contract,
)


def test_semantic_contract_generation_is_deterministic():
    first = synthesize_semantic_contract(human_request="Implement deterministic replay compaction.")
    second = synthesize_semantic_contract(human_request="Implement deterministic replay compaction.")

    assert first == second
    assert first["contract_id"].startswith("SEMANTIC-CONTRACT-")
    assert first["artifact_hash"].startswith("sha256:")


def test_semantic_contract_schema_validation_and_hashing():
    contract = synthesize_semantic_contract(human_request="Review governed execution observability.")
    validation = validate_semantic_contract(contract)

    assert validation["valid"] is True
    assert validation["computed_hash"] == contract["artifact_hash"]

    mutated = deepcopy(contract)
    mutated["human_request"] = "mutated"
    assert validate_semantic_contract(mutated)["valid"] is False


def test_semantic_contract_preserves_non_execution_authority():
    contract = synthesize_semantic_contract(human_request="Add bounded observability.")

    assert contract["authority_boundary"] == SEMANTIC_CONTRACT_AUTHORITY_BOUNDARY
    assert contract["provenance"]["execution_authority"] is False
    assert contract["provenance"]["governance_mediated"] is True
    assert "autonomous continuation" in contract["forbidden_operations"]
    assert "semantic auto-dispatch" in contract["forbidden_operations"]


def test_bridge_task_package_includes_semantic_contract(monkeypatch, tmp_path):
    captured = {}

    def fake_provider(*, task_package, workspace_path, timeout_seconds=600):
        captured["task_package"] = deepcopy(task_package)
        return {
            "provider": "CODEX_CLI",
            "status": "COMPLETED",
            "stdout": "AIGOL_CODEX_TASK_COMPLETE",
            "stderr": "",
            "returncode": 0,
            "workspace_path": str(tmp_path),
            "task_package_id": task_package["task_id"],
            "non_authority_guarantees": ["NO_AUTO_APPROVAL", "NO_AUTO_CONTINUATION"],
            "execution_boundary": {"provider": "CODEX_CLI", "auto_approval": False, "auto_continue": False},
            "errors": [],
            "command": ["codex", "exec", "<bounded_prompt>"],
            "bounded_prompt_hash": "sha256:bounded",
            "retry_count": 0,
        }

    monkeypatch.setattr(bridge_runtime, "run_bounded_codex_cli_task", fake_provider)
    result = run_minimal_end_to_end_bridge(
        human_request="Implement deterministic replay compaction for replay event visibility.",
        session_id="SEMANTIC-CONTRACT-SESSION",
        workspace_path=str(tmp_path),
    )

    task = captured["task_package"]
    contract = task["semantic_contract"]
    assert result["status"] == "BRIDGE_ACCEPTED"
    assert task["human_request"] == "Implement deterministic replay compaction for replay event visibility."
    assert contract["human_request"] == task["human_request"]
    assert task["metadata"]["semantic_contract_id"] == contract["contract_id"]
    assert task["metadata"]["semantic_contract_hash"] == contract["artifact_hash"]
    assert task["execution_scope"] == contract["allowed_scope"]
    assert task["expected_tests"] == contract["expected_tests"]
    assert task["forbidden_operations"] == contract["forbidden_operations"]


def test_codex_prompt_includes_bounded_semantic_contract():
    contract = synthesize_semantic_contract(human_request="Implement bounded semantic contract visibility.")
    task = {
        "task_id": "TASK-SEMANTIC-1",
        "governance_mode": "governed_execution_bridge_codex_cli",
        "risk_class": "LOW",
        "approval_required": False,
        "codex_prompt": "Execute the governed semantic contract.",
        "constraints": ["no dispatch", "no approval"],
        "expected_outputs": ["summary"],
        "semantic_contract": contract,
        "metadata": {"approved": False, "lifecycle_state": "TASK_PACKAGED"},
    }

    prompt = build_bounded_codex_prompt(task_package=task)

    assert "Semantic contract JSON:" in prompt
    assert contract["contract_id"] in prompt
    assert "Use the semantic contract as structured intent, not as execution authority." in prompt
    assert "Task package JSON:" in prompt


def test_semantic_contract_contains_no_authority_leakage():
    contract = synthesize_semantic_contract(human_request="Execute? No, review bounded runtime only.")

    assert validate_semantic_contract(contract)["valid"] is True
    assert contract["authority_boundary"] == "SEMANTIC_ONLY_NON_EXECUTION_AUTHORITY"
    assert contract["provenance"]["execution_authority"] is False
    assert contract["provenance"]["chatgpt_api_invoked"] is False
