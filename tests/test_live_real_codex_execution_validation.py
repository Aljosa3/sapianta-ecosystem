from sapianta_bridge.provider_connectors.live_validation.live_codex_validation_case import (
    create_live_codex_validation_case,
)
from sapianta_bridge.provider_connectors.live_validation.live_codex_validation_evidence import (
    validate_live_codex_validation_evidence,
)
from sapianta_bridge.provider_connectors.live_validation.live_codex_validation_runner import (
    run_live_codex_validation,
)


def test_live_real_codex_execution_validation_reports_passed_or_blocked(tmp_path):
    result = run_live_codex_validation(workspace_path=tmp_path, timeout_seconds=30)

    assert result["status"] in {"PASSED", "BLOCKED"}
    assert result["evidence"]["validation_name"] == "LIVE_REAL_CODEX_EXECUTION_VALIDATION_V1"
    assert result["evidence"]["execution_authorized"] is True or result["status"] == "BLOCKED"
    assert result["evidence"]["provider_id"] == "codex_cli"
    assert result["evidence"]["orchestration_introduced"] is False
    assert result["evidence"]["routing_introduced"] is False
    assert result["evidence"]["retries_introduced"] is False
    assert result["evidence"]["fallback_introduced"] is False
    assert result["evidence_validation"]["valid"] is True
    if result["status"] == "PASSED":
        assert result["evidence"]["codex_cli_executed"] is True
        assert result["evidence"]["exit_code_captured"] is True
        assert result["bounded_execution_result"]["bounded_execution_status"] == "SUCCESS"
    else:
        assert result["blocked_reason"]


def test_live_real_codex_execution_validation_blocks_without_codex(tmp_path):
    result = run_live_codex_validation(
        workspace_path=tmp_path,
        codex_executable="",
        timeout_seconds=30,
    )

    assert result["status"] == "BLOCKED"
    assert result["evidence"]["codex_cli_detected"] is False
    assert result["evidence_validation"]["valid"] is True


def test_live_real_codex_validation_case_requires_prepared_artifact(tmp_path):
    case = create_live_codex_validation_case(
        workspace_path=tmp_path,
        codex_executable="",
        timeout_seconds=30,
    )

    assert case["status"] == "BLOCKED"
    assert case["blocked_reason"] == "codex CLI not detected"


def test_live_real_codex_evidence_rejects_routing(tmp_path):
    result = run_live_codex_validation(
        workspace_path=tmp_path,
        codex_executable="",
        timeout_seconds=30,
    )
    evidence = result["evidence"]
    evidence["routing_introduced"] = True

    validation = validate_live_codex_validation_evidence(evidence)

    assert validation["valid"] is False
    assert any(error["field"] == "routing_introduced" for error in validation["errors"])
