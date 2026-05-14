from sapianta_bridge.envelopes.execution_envelope import create_execution_envelope
from sapianta_bridge.providers.normalized_result import NormalizedExecutionResult
from sapianta_bridge.runtime.runtime_result import (
    create_runtime_result,
    validate_runtime_result,
)


def _envelope() -> dict:
    return create_execution_envelope(
        envelope_id="ENV-RESULT",
        provider_id="deterministic_mock",
        allowed_roots=["sapianta_bridge"],
        authority_scope=["READ_ONLY", "NO_NETWORK", "NO_PRIVILEGE_ESCALATION"],
        allowed_actions=["inspect"],
        forbidden_actions=["mutate"],
        replay_identity="REPLAY-RESULT",
        validation_requirements=["pytest"],
    ).to_dict()


def test_runtime_result_wraps_normalized_result() -> None:
    result = create_runtime_result(
        envelope=_envelope(),
        normalized_result=NormalizedExecutionResult(
            provider_id="deterministic_mock",
            execution_status="SUCCESS",
            artifacts_created=("artifact.txt",),
        ),
        guard_status={"runtime_allowed": True},
    )

    assert result.runtime_status == "SUCCESS"
    assert result.artifacts == ("artifact.txt",)
    assert validate_runtime_result(result)["valid"] is True


def test_runtime_result_maps_not_executed_to_needs_review() -> None:
    result = create_runtime_result(
        envelope=_envelope(),
        normalized_result=NormalizedExecutionResult(
            provider_id="deterministic_mock",
            execution_status="NOT_EXECUTED",
        ),
        guard_status={"runtime_allowed": True},
    )

    assert result.runtime_status == "NEEDS_REVIEW"


def test_runtime_result_rejects_invalid_normalized_payload() -> None:
    result = create_runtime_result(
        envelope=_envelope(),
        normalized_result=NormalizedExecutionResult(
            provider_id="deterministic_mock",
            execution_status="SUCCESS",
            governance_modified=True,
        ),
        guard_status={"runtime_allowed": True},
    ).to_dict()

    validation = validate_runtime_result(result)

    assert validation["valid"] is False
    assert {"field": "governance_modified", "reason": "providers cannot modify governance"} in validation["errors"]
