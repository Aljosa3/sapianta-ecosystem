from copy import deepcopy
from pathlib import Path

from agol_bridge.continuity.validator_composition import (
    AUTHORITY_BOUNDARY_VIOLATION,
    DUPLICATE_VALIDATOR,
    NON_DETERMINISTIC_REPORT,
    UNKNOWN_VALIDATOR,
    VALID,
    VALIDATOR_FAILED,
    compose_validators,
)


def _envelope():
    return {"loop_id": "LOOP-1", "payload": {"request": "validate continuity"}}


def _artifact_map():
    return {"task_packages": {"TASK-1": {"task_id": "TASK-1"}}}


def _valid_report(name):
    return {
        "validation_id": f"VALIDATION-{name}",
        "status": VALID,
        "checks": [{"name": name, "status": VALID}],
        "authority_findings": [],
    }


def _failed_report(name, status=VALIDATOR_FAILED):
    return {
        "validation_id": f"VALIDATION-{name}",
        "status": status,
        "checks": [{"name": name, "status": status}],
        "authority_findings": [{"name": name}] if status == AUTHORITY_BOUNDARY_VIOLATION else [],
    }


def test_valid_ordered_validators_return_valid():
    calls = []

    def first(envelope, artifact_map):
        calls.append(("first", envelope["loop_id"], "TASK-1" in artifact_map["task_packages"]))
        return _valid_report("first")

    def second(envelope, artifact_map):
        calls.append(("second", envelope["loop_id"], "TASK-1" in artifact_map["task_packages"]))
        return _valid_report("second")

    report = compose_validators(
        envelope=_envelope(),
        artifact_map=_artifact_map(),
        validator_registry={"first": first, "second": second},
        validator_ids=["first", "second"],
    )

    assert report["aggregate_status"] == VALID
    assert report["validator_order"] == ["first", "second"]
    assert [item["validator_id"] for item in report["ordered_validator_reports"]] == ["first", "second"]
    assert calls == [
        ("first", "LOOP-1", True),
        ("first", "LOOP-1", True),
        ("second", "LOOP-1", True),
        ("second", "LOOP-1", True),
    ]


def test_declared_validator_order_is_preserved():
    def first(envelope, artifact_map):
        return _valid_report("first")

    def second(envelope, artifact_map):
        return _valid_report("second")

    report = compose_validators(
        envelope=_envelope(),
        artifact_map=_artifact_map(),
        validator_registry={"first": first, "second": second},
        validator_ids=["second", "first"],
    )

    assert report["validator_order"] == ["second", "first"]
    assert [item["validator_id"] for item in report["ordered_validator_reports"]] == ["second", "first"]


def test_duplicate_validator_ids_fail():
    report = compose_validators(
        envelope=_envelope(),
        artifact_map=_artifact_map(),
        validator_registry={"first": lambda envelope, artifact_map: _valid_report("first")},
        validator_ids=["first", "first"],
    )

    assert report["aggregate_status"] == DUPLICATE_VALIDATOR
    assert report["failures"] == [{"status": DUPLICATE_VALIDATOR, "validator_ids": ["first"]}]


def test_unknown_validator_ids_fail():
    report = compose_validators(
        envelope=_envelope(),
        artifact_map=_artifact_map(),
        validator_registry={"first": lambda envelope, artifact_map: _valid_report("first")},
        validator_ids=["first", "missing"],
    )

    assert report["aggregate_status"] == UNKNOWN_VALIDATOR
    assert report["failures"] == [{"status": UNKNOWN_VALIDATOR, "validator_ids": ["missing"]}]


def test_validator_failure_aggregates_deterministically():
    def first(envelope, artifact_map):
        return _valid_report("first")

    def second(envelope, artifact_map):
        return _failed_report("second")

    report = compose_validators(
        envelope=_envelope(),
        artifact_map=_artifact_map(),
        validator_registry={"first": first, "second": second},
        validator_ids=["first", "second"],
    )

    assert report["aggregate_status"] == VALIDATOR_FAILED
    assert report["failures"] == [
        {"status": VALIDATOR_FAILED, "validator_id": "second", "validator_status": VALIDATOR_FAILED}
    ]


def test_deterministic_failure_precedence():
    def authority_failure(envelope, artifact_map):
        return _failed_report("authority", AUTHORITY_BOUNDARY_VIOLATION)

    def generic_failure(envelope, artifact_map):
        return _failed_report("generic")

    report = compose_validators(
        envelope=_envelope(),
        artifact_map=_artifact_map(),
        validator_registry={"generic": generic_failure, "authority": authority_failure},
        validator_ids=["generic", "authority"],
    )

    assert report["aggregate_status"] == AUTHORITY_BOUNDARY_VIOLATION
    assert report["authority_findings"] == [
        {"validator_id": "authority", "status": AUTHORITY_BOUNDARY_VIOLATION}
    ]


def test_non_deterministic_validator_report_is_detected():
    reports = [_valid_report("first"), _failed_report("first")]

    def unstable(envelope, artifact_map):
        return reports.pop(0)

    report = compose_validators(
        envelope=_envelope(),
        artifact_map=_artifact_map(),
        validator_registry={"unstable": unstable},
        validator_ids=["unstable"],
    )

    assert report["aggregate_status"] == NON_DETERMINISTIC_REPORT
    assert report["determinism_findings"] == [
        {"validator_id": "unstable", "error": "validator returned non-deterministic reports"}
    ]


def test_same_input_produces_same_aggregate_report():
    def first(envelope, artifact_map):
        return _valid_report("first")

    envelope = _envelope()
    artifacts = _artifact_map()
    registry = {"first": first}
    validator_ids = ["first"]

    assert compose_validators(
        envelope=envelope,
        artifact_map=artifacts,
        validator_registry=registry,
        validator_ids=validator_ids,
    ) == compose_validators(
        envelope=envelope,
        artifact_map=artifacts,
        validator_registry=registry,
        validator_ids=validator_ids,
    )


def test_inputs_and_validator_outputs_are_not_mutated():
    validator_output = _valid_report("first")

    def first(envelope, artifact_map):
        envelope["payload"]["request"] = "validator-local mutation"
        artifact_map["task_packages"]["TASK-1"]["task_id"] = "validator-local mutation"
        return validator_output

    envelope = _envelope()
    artifacts = _artifact_map()
    before_envelope = deepcopy(envelope)
    before_artifacts = deepcopy(artifacts)
    before_output = deepcopy(validator_output)

    compose_validators(
        envelope=envelope,
        artifact_map=artifacts,
        validator_registry={"first": first},
        validator_ids=["first"],
    )

    assert envelope == before_envelope
    assert artifacts == before_artifacts
    assert validator_output == before_output


def test_only_supplied_validators_are_called():
    calls = []

    def supplied(envelope, artifact_map):
        calls.append("supplied")
        return _valid_report("supplied")

    def not_requested(envelope, artifact_map):
        calls.append("not_requested")
        return _valid_report("not_requested")

    compose_validators(
        envelope=_envelope(),
        artifact_map=_artifact_map(),
        validator_registry={"supplied": supplied, "not_requested": not_requested},
        validator_ids=["supplied"],
    )

    assert calls == ["supplied", "supplied"]


def test_no_filesystem_network_subprocess_provider_sidepanel_runtime_calls_are_introduced():
    source = (Path(__file__).resolve().parents[1] / "continuity/validator_composition.py").read_text()
    forbidden = (
        "open(",
        "Path(",
        "read_text",
        "write_text",
        "requests",
        "urllib",
        "socket",
        "subprocess",
        "threading",
        "Timer",
        "fetch",
        "chrome.",
        "provider.call",
        "dispatch_task",
        "approve_task",
        "__import__",
        "importlib",
        "globals(",
        "locals(",
    )
    for token in forbidden:
        assert token not in source


def test_no_approval_dispatch_execution_authority_is_introduced():
    source = (Path(__file__).resolve().parents[1] / "continuity/validator_composition.py").read_text()
    forbidden_authority_terms = (
        "approve(",
        "dispatch(",
        "execute(",
        "transition_lifecycle",
        "append_replay_event",
    )
    for token in forbidden_authority_terms:
        assert token not in source
