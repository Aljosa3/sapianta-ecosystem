from copy import deepcopy

from sapianta_system.runtime.validation.operational_epoch import (
    FAILURE_INJECTION_CASES,
    create_operational_validation_record,
    validate_deterministic_recovery,
    validate_fail_closed_failure_injection,
    validate_governance_under_stress,
    validate_operational_continuity,
    validate_operational_lifecycle,
    validate_replay_identity,
    validate_replay_safe_certification,
)


def _request(index=1):
    return {
        "request_id": f"REQ-{index}",
        "operation_type": "RUN_VALIDATION",
        "target_scope": {"kind": "validation", "value": "tests/", "bounded": True},
    }


def test_normal_operational_request_validates_full_lifecycle():
    record = create_operational_validation_record(request=_request())
    assert validate_operational_lifecycle(record)["valid"] is True
    assert validate_operational_continuity(record)["valid"] is True
    assert record["ungoverned_execution_path"] is False


def test_replay_identity_is_deterministic_and_read_only():
    first = create_operational_validation_record(request=_request())
    second = create_operational_validation_record(request=_request())
    before = deepcopy(first)
    result = validate_replay_identity(first, second)
    assert result["valid"] is True
    assert result["read_only"] is True
    assert first == before


def test_bounded_recovery_is_deterministic_without_retry_or_fallback():
    result = validate_deterministic_recovery(create_operational_validation_record(request=_request()))
    assert result["valid"] is True
    assert result["retry_used"] is False
    assert result["fallback_used"] is False


def test_failure_injection_cases_fail_closed():
    result = validate_fail_closed_failure_injection(create_operational_validation_record(request=_request()))
    assert result["valid"] is True
    assert set(result["cases"]) == set(FAILURE_INJECTION_CASES)
    assert all(case["blocked"] for case in result["cases"].values())


def test_sequence_validation_has_no_hidden_state_leakage():
    records = [create_operational_validation_record(request=_request(index)) for index in range(1, 4)]
    result = validate_governance_under_stress(records)
    assert result["valid"] is True
    assert result["hidden_state_leakage_detected"] is False
    assert result["invalid_request_corrupted_valid_replay_state"] is False


def test_replay_safe_certification_requires_all_validations():
    result = validate_replay_safe_certification(create_operational_validation_record(request=_request()))
    assert result["certified"] is True
    assert result["deterministic"] is True
    assert result["fail_closed"] is True
