from sapianta_bridge.providers.normalized_result import (
    NormalizedExecutionResult,
    validate_normalized_result,
)


def test_normalized_result_schema_passes() -> None:
    result = NormalizedExecutionResult(provider_id="codex", execution_status="SUCCESS")
    validation = validate_normalized_result(result)

    assert validation["valid"] is True
    assert validation["normalized_result_valid"] is True


def test_normalized_result_rejects_governance_mutation() -> None:
    result = NormalizedExecutionResult(
        provider_id="codex",
        execution_status="SUCCESS",
        governance_modified=True,
    )
    validation = validate_normalized_result(result)

    assert validation["valid"] is False
    assert {"field": "governance_modified", "reason": "providers cannot modify governance"} in validation["errors"]


def test_normalized_result_rejects_hidden_tasks() -> None:
    result = NormalizedExecutionResult(
        provider_id="codex",
        execution_status="SUCCESS",
        hidden_tasks_generated=True,
    )
    validation = validate_normalized_result(result)

    assert validation["valid"] is False
    assert {"field": "hidden_tasks_generated", "reason": "providers cannot generate hidden tasks"} in validation["errors"]


def test_normalized_result_rejects_unknown_status() -> None:
    validation = validate_normalized_result(
        {
            "provider_id": "codex",
            "execution_status": "ROUTED",
            "artifacts_created": [],
            "tests_executed": False,
            "governance_modified": False,
            "execution_time_ms": 0,
            "replay_safe": True,
            "hidden_tasks_generated": False,
            "validation_bypassed": False,
        }
    )

    assert validation["valid"] is False
    assert {"field": "execution_status", "reason": "unsupported execution status"} in validation["errors"]
