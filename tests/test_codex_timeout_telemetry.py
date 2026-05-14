from sapianta_bridge.provider_connectors.codex_timeout_telemetry import (
    codex_timeout_telemetry,
    validate_codex_timeout_telemetry,
)


def test_timeout_telemetry_records_samples_and_duration():
    telemetry = codex_timeout_telemetry(
        timeout_seconds=30,
        duration_seconds=30,
        timed_out=True,
        stdout="x" * 300,
        stderr="blocked",
    )

    assert telemetry["timeout_exceeded"] is True
    assert len(telemetry["stdout_sample"]) == 240
    assert validate_codex_timeout_telemetry(telemetry)["valid"] is True


def test_timeout_telemetry_rejects_invalid_timeout():
    telemetry = codex_timeout_telemetry(
        timeout_seconds=0,
        duration_seconds=0,
        timed_out=False,
        stdout="",
        stderr="",
    )

    validation = validate_codex_timeout_telemetry(telemetry)

    assert validation["valid"] is False
    assert any(error["field"] == "timeout_seconds" for error in validation["errors"])
