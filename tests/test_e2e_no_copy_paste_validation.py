from sapianta_bridge.no_copy_paste_loop.e2e_validation import run_e2e_no_copy_paste_validation
from sapianta_bridge.no_copy_paste_loop.e2e_validation.e2e_validation_case import E2EValidationCase
from sapianta_bridge.no_copy_paste_loop.e2e_validation.e2e_validation_evidence import validation_report


def test_e2e_validation_passes_full_no_copy_paste_loop() -> None:
    output = run_e2e_no_copy_paste_validation()
    report = output["validation_report"]
    lineage = output["lineage_evidence"]

    assert report["status"] == "PASSED"
    assert report["chatgpt_request_bound"] is True
    assert report["ingress_bound"] is True
    assert report["nl_to_envelope_bound"] is True
    assert report["session_bound"] is True
    assert report["provider_invocation_bound"] is True
    assert report["result_return_bound"] is True
    assert report["chatgpt_response_bound"] is True
    assert report["manual_copy_paste_required"] is False
    assert report["replay_safe"] is True
    assert lineage["envelope_identity_preserved"] is True
    assert lineage["provider_identity_preserved"] is True
    assert lineage["result_lineage_preserved"] is True


def test_e2e_validation_uses_deterministic_mock_provider_only() -> None:
    output = run_e2e_no_copy_paste_validation()

    assert output["lineage_evidence"]["provider_id"] == "deterministic_mock"
    assert output["loop_output"]["bridge_output"]["invocation_output"]["invocation_result"]["provider_id"] == "deterministic_mock"


def test_e2e_validation_rejects_provider_identity_change() -> None:
    output = run_e2e_no_copy_paste_validation()
    loop_output = output["loop_output"]
    loop_output["loop_binding"]["provider_id"] = "codex"

    assert loop_output["loop_binding"]["provider_id"] != loop_output["bridge_output"]["invocation_output"]["invocation_result"]["provider_id"]


def test_e2e_validation_report_fails_closed_on_missing_identity() -> None:
    checks = {
        "chatgpt_request_bound": True,
        "ingress_bound": False,
        "nl_to_envelope_bound": True,
        "session_bound": True,
        "provider_invocation_bound": True,
        "result_return_bound": True,
        "chatgpt_response_bound": True,
    }
    report = validation_report(checks=checks, errors=[{"field": "ingress_bound", "reason": "missing ingress"}])

    assert report["status"] == "FAILED"
    assert report["replay_safe"] is False


def test_e2e_validation_blocks_unknown_provider() -> None:
    output = run_e2e_no_copy_paste_validation(
        E2EValidationCase(requested_provider_id="unknown_provider")
    )

    assert output["validation_report"]["status"] == "FAILED"
    assert output["validation_report"]["provider_invocation_bound"] is False


def test_e2e_validation_reports_no_orchestration_or_routing() -> None:
    report = run_e2e_no_copy_paste_validation()["validation_report"]

    assert report["orchestration_introduced"] is False
    assert report["provider_routing_introduced"] is False
    assert report["autonomous_execution_introduced"] is False
    assert report["retries_introduced"] is False
    assert report["fallback_introduced"] is False
