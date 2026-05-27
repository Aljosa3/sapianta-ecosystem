from pathlib import Path

import aigol.runtime.operator.runtime_execution_cli as runtime_cli


EXPECTED_OUTPUT = """[RUNTIME CONTRACT]
runtime_surface: operational
governance: active
readonly_runtime: true
fail_closed: true

[SCHEMA]
governed_return_schema: 1.0
replay_contract_version: 1.0

[VERIFICATION]
verification_contract: active
continuity_validation: enabled
evidence_validation: enabled

[COMMANDS]
inspect-runtime
inspect-replay
verify-replay
list-replays
latest-replay
show-runtime-session
runtime-summary
inspect-runtime-contract

[GUARANTEES]
readonly_operations_only: true
runtime_mutation_allowed: false
replay_execution_allowed: false
orchestration_enabled: false"""


def test_successful_runtime_contract_inspection_is_deterministic() -> None:
    result = runtime_cli.inspect_runtime_contract()

    assert result["fail_closed"] is False
    assert result["fail_closed_enforced"] is True
    assert runtime_cli.render_runtime_contract(result) == EXPECTED_OUTPUT
    assert runtime_cli.render_runtime_contract(runtime_cli.inspect_runtime_contract()) == EXPECTED_OUTPUT


def test_runtime_contract_shows_readonly_guarantees_and_stable_commands() -> None:
    result = runtime_cli.inspect_runtime_contract()

    assert result["readonly_runtime"] is True
    assert result["readonly_operations_only"] is True
    assert result["runtime_mutation_allowed"] is False
    assert result["replay_execution_allowed"] is False
    assert result["orchestration_enabled"] is False
    assert result["commands"] == [
        "inspect-runtime",
        "inspect-replay",
        "verify-replay",
        "list-replays",
        "latest-replay",
        "show-runtime-session",
        "runtime-summary",
        "inspect-runtime-contract",
    ]


def test_malformed_runtime_contract_state_fails_closed() -> None:
    malformed_state = runtime_cli._runtime_contract_state()
    malformed_state["readonly_runtime"] = False

    result = runtime_cli._validate_runtime_contract_state(malformed_state)

    assert result["governance"] == "blocked"
    assert result["fail_closed"] is True
    assert result["commands"] == []


def test_invalid_runtime_contract_schema_fails_closed() -> None:
    invalid_state = runtime_cli._runtime_contract_state()
    invalid_state["governed_return_schema"] = "2.0"

    result = runtime_cli._validate_runtime_contract_state(invalid_state)

    assert result["governed_return_schema"] == "invalid"
    assert result["fail_closed"] is True


def test_invalid_replay_contract_version_fails_closed() -> None:
    invalid_state = runtime_cli._runtime_contract_state()
    invalid_state["replay_contract_version"] = "unknown"

    result = runtime_cli._validate_runtime_contract_state(invalid_state)

    assert result["replay_contract_version"] == "invalid"
    assert result["fail_closed"] is True


def test_corrupted_runtime_command_contract_fails_closed() -> None:
    invalid_state = runtime_cli._runtime_contract_state()
    invalid_state["commands"].remove("verify-replay")

    result = runtime_cli._validate_runtime_contract_state(invalid_state)

    assert result["verification_contract"] == "missing"
    assert result["fail_closed"] is True


def test_missing_verification_contract_fails_closed(monkeypatch) -> None:
    monkeypatch.setattr(runtime_cli, "verify_governed_return", None)

    result = runtime_cli.inspect_runtime_contract()

    assert result["verification_contract"] == "missing"
    assert result["fail_closed"] is True


def test_runtime_contract_command_does_not_create_runtime_storage(tmp_path: Path, capsys) -> None:
    runtime_root = tmp_path / "runtime"

    assert runtime_cli.main(["--runtime-root", str(runtime_root), "inspect-runtime-contract"]) == 0

    assert capsys.readouterr().out.rstrip("\n") == EXPECTED_OUTPUT
    assert runtime_root.exists() is False
