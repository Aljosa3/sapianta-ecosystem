from sapianta_bridge.provider_connectors.live_validation.live_codex_validation_evidence import (
    validate_live_codex_validation_evidence,
)
from sapianta_bridge.provider_connectors.live_validation.live_codex_validation_runner import (
    run_live_codex_validation_v2,
)


def test_live_real_codex_execution_validation_v2_reports_passed_or_blocked(tmp_path):
    result = run_live_codex_validation_v2(workspace_path=tmp_path, timeout_seconds=30)

    assert result["status"] in {"PASSED", "BLOCKED"}
    evidence = result["evidence"]
    assert evidence["validation_name"] == "LIVE_REAL_CODEX_EXECUTION_VALIDATION_V2"
    assert evidence["contract_used"] == "codex exec <bounded_prompt>"
    assert evidence["previous_blocked_contract"] == "codex run <prepared_task_artifact>"
    assert evidence["shell_used"] is False
    assert evidence["provider_id"] == "codex_cli"
    assert evidence["orchestration_introduced"] is False
    assert evidence["routing_introduced"] is False
    assert evidence["retries_introduced"] is False
    assert evidence["fallback_introduced"] is False
    assert result["evidence_validation"]["valid"] is True
    if result["status"] == "PASSED":
        assert evidence["codex_cli_executed"] is True
        assert evidence["exit_code_captured"] is True
    else:
        assert result["blocked_reason"]


def test_live_real_codex_execution_validation_v2_blocks_without_codex(tmp_path):
    result = run_live_codex_validation_v2(
        workspace_path=tmp_path,
        codex_executable="",
        timeout_seconds=30,
    )

    assert result["status"] == "BLOCKED"
    assert result["evidence"]["codex_cli_detected"] is False
    assert result["evidence"]["contract_used"] == "codex exec <bounded_prompt>"
    assert result["evidence_validation"]["valid"] is True


def test_live_real_codex_execution_validation_v2_evidence_rejects_run_contract(tmp_path):
    result = run_live_codex_validation_v2(
        workspace_path=tmp_path,
        codex_executable="",
        timeout_seconds=30,
    )
    evidence = result["evidence"]
    evidence["contract_used"] = "codex run <prepared_task_artifact>"

    validation = validate_live_codex_validation_evidence(evidence)

    assert validation["valid"] is False
    assert any(error["field"] == "contract_used" for error in validation["errors"])
