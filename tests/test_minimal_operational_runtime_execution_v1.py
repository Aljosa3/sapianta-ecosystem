"""Tests for MINIMAL_OPERATIONAL_RUNTIME_EXECUTION_V1."""

from __future__ import annotations

import inspect

from aigol.runtime.operator.runtime_execution_cli import (
    DEFAULT_TIMESTAMP,
    main,
    render_runtime_inspection,
    run_runtime_inspection,
)


def _invalid_proposal() -> dict:
    return {
        "proposal_id": "INVALID-MUTATING-PROPOSAL",
        "natural_language_input": "Attempt a non-readonly operation.",
        "proposal_type": "CONTRACT_PROPOSAL",
        "requested_capabilities": ["readonly_http_get_provider"],
        "proposed_contract_reference": "contract:INVALID-MUTATING-CONTRACT",
        "created_at": DEFAULT_TIMESTAMP,
    }


def test_inspect_runtime_executes_existing_readonly_governed_path_and_persists_replay(tmp_path) -> None:
    result = run_runtime_inspection(runtime_root=tmp_path / "runtime")

    operation = result["operation"]
    assert operation == {
        "operation_id": "RUNTIME-INSPECTION-001",
        "operation_type": "inspect-runtime",
        "timestamp": DEFAULT_TIMESTAMP,
        "provider": "metadata_inspection_provider",
        "readonly": True,
        "status": "success",
        "replay_reference": "RUNTIME-INSPECTION-001",
    }
    assert result["execution"]["execution_result"].execution_status == "EXECUTED"
    assert result["governed_return"].return_status == "ACCEPTED"
    assert result["persistence"]["status"] == "PERSISTED"
    assert result["verification"]["status"] == "VERIFY_PASSED"
    assert result["runtime_summary"]["replay_entries"] == 1
    assert (tmp_path / "runtime" / "ledger" / "governed_returns.jsonl").is_file()
    assert (tmp_path / "runtime" / "evidence" / operation["replay_reference"] / "governed_return.json").is_file()


def test_runtime_inspection_enforces_readonly_isolation(tmp_path) -> None:
    result = run_runtime_inspection(runtime_root=tmp_path / "runtime")
    metadata = result["isolation"].to_dict()["isolation_metadata"]

    assert metadata["provider_state_mutation_allowed"] is False
    assert metadata["runtime_state_mutation_allowed"] is False
    assert metadata["network_mutation_allowed"] is False
    assert result["governed_return_artifact"]["diagnostic_evidence"]["readonly_enforced"] is True


def test_runtime_inspection_fails_closed_and_persists_blocked_evidence(tmp_path) -> None:
    result = run_runtime_inspection(
        operation_id="RUNTIME-INSPECTION-BLOCKED",
        runtime_root=tmp_path / "runtime",
        proposal_input=_invalid_proposal(),
    )

    assert result["operation"]["status"] == "blocked"
    assert result["execution"]["execution_result"].execution_status == "REJECTED"
    assert result["execution"]["provider_evidence"] is None
    assert result["governed_return"].return_status == "REJECTED"
    assert result["governed_return_artifact"]["execution_status"] == "EXECUTION_BLOCKED"
    assert result["governed_return_artifact"]["fail_closed"] is True
    assert result["persistence"]["status"] == "PERSISTED"
    assert result["verification"]["status"] == "VERIFY_PASSED"
    assert result["fail_closed"] is True


def test_operator_visible_output_is_deterministic_for_identical_empty_state(tmp_path) -> None:
    first = render_runtime_inspection(run_runtime_inspection(runtime_root=tmp_path / "first"))
    second = render_runtime_inspection(run_runtime_inspection(runtime_root=tmp_path / "second"))

    assert first == second
    assert "[OPERATION]\nstatus: success\noperation: inspect-runtime" in first
    assert "readonly: true" in first
    assert "replay_entries: 1" in first
    assert "verification: verify_passed" in first


def test_cli_exposes_inspect_runtime_command(tmp_path, capsys) -> None:
    assert main(["--runtime-root", str(tmp_path / "runtime"), "inspect-runtime"]) == 0

    output = capsys.readouterr().out
    assert "governance: active" in output
    assert "persistence: persisted" in output


def test_malformed_existing_replay_ledger_fails_closed(tmp_path) -> None:
    runtime_root = tmp_path / "runtime"
    ledger = runtime_root / "ledger" / "governed_returns.jsonl"
    ledger.parent.mkdir(parents=True)
    ledger.write_text("not-json\n", encoding="utf-8")

    result = run_runtime_inspection(runtime_root=runtime_root)

    assert result["operation"]["status"] == "failed_closed"
    assert result["verification"]["status"] == "VERIFY_FAILED"
    assert result["runtime_summary"]["replay_available"] is False
    assert result["fail_closed"] is True


def test_operator_path_introduces_no_mutating_or_orchestration_surface() -> None:
    import aigol.runtime.operator.runtime_execution_cli as execution_cli

    source = inspect.getsource(execution_cli).lower()
    assert "subprocess" not in source
    assert "async " not in source
    assert "await " not in source
    assert "threading" not in source
    assert "autonomous" not in source
    assert '"orchestration_enabled": true' not in source
