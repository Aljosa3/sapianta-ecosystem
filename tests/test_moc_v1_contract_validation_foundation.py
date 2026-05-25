import json

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.moc.contract_validation import (
    FAIL_CLOSED,
    INVALID_BOUNDARY,
    INVALID_SCHEMA,
    VALID,
    inspect_contract_validation,
    validate_semantic_contract,
)


def _valid_contract():
    return {
        "intent_id": "intent-001",
        "intent_summary": "Prepare a bounded semantic validation proof.",
        "scope": "documentation and validation only",
        "risk_level": "low",
        "mutation_classification": "parametric",
        "governance_anchors": [
            {
                "anchor_id": "MOC_V1_SPEC",
                "anchor_type": "governance_specification",
                "source_ref": "docs/governance/cognition/MOC_V1_SPEC.md",
            }
        ],
        "allowed_actions": ["validate semantic contract"],
        "forbidden_actions": ["execute task", "dispatch worker", "activate provider"],
        "required_approvals": ["human approval before worker task consideration"],
        "expected_outputs": ["MOC_V1_CONTRACT_VALIDATION_RESULT"],
        "advisory_only": True,
        "replay_safe": True,
        "deterministic_constraints": {
            "no_hidden_inference": True,
            "no_self_dispatch": True,
            "no_runtime_mutation": True,
            "no_autonomous_continuation": True,
            "no_provider_activation": True,
        },
    }


def test_valid_contract_passes():
    result = validate_semantic_contract(_valid_contract())

    assert result["validation_status"] == VALID
    assert result["schema_valid"] is True
    assert result["boundary_valid"] is True
    assert result["advisory_only"] is True
    assert result["replay_safe"] is True
    assert result["violations"] == []


def test_missing_required_field_fails():
    contract = _valid_contract()
    contract.pop("intent_summary")

    result = validate_semantic_contract(contract)

    assert result["validation_status"] == INVALID_SCHEMA
    assert result["schema_valid"] is False
    assert any("intent_summary" in violation for violation in result["violations"])


def test_advisory_only_false_fails_boundary():
    contract = _valid_contract()
    contract["advisory_only"] = False

    result = validate_semantic_contract(contract)

    assert result["validation_status"] == INVALID_BOUNDARY
    assert "advisory_only must be true" in result["violations"]


def test_replay_safe_false_fails_boundary():
    contract = _valid_contract()
    contract["replay_safe"] = False

    result = validate_semantic_contract(contract)

    assert result["validation_status"] == INVALID_BOUNDARY
    assert "replay_safe must be true" in result["violations"]


def test_forbidden_authority_field_fails_boundary():
    contract = _valid_contract()
    contract["execution_authority"] = True

    result = validate_semantic_contract(contract)

    assert result["validation_status"] == INVALID_BOUNDARY
    assert any("execution_authority" in violation for violation in result["violations"])


def test_invalid_enum_fails_schema():
    contract = _valid_contract()
    contract["risk_level"] = "planetary"

    result = validate_semantic_contract(contract)

    assert result["validation_status"] == INVALID_SCHEMA
    assert result["schema_valid"] is False
    assert any("risk_level" in violation for violation in result["violations"])


def test_missing_deterministic_constraints_fails():
    contract = _valid_contract()
    contract.pop("deterministic_constraints")

    result = validate_semantic_contract(contract)

    assert result["validation_status"] == INVALID_BOUNDARY
    assert "deterministic_constraints must be present" in result["violations"]


def test_malformed_json_fails_closed(tmp_path):
    contract_path = tmp_path / "contract.json"
    contract_path.write_text("{not-json", encoding="utf-8")

    result = inspect_contract_validation(input_path=contract_path)

    validation = result["contract_validation_result"]
    assert validation["validation_status"] == FAIL_CLOSED
    assert validation["schema_valid"] is False
    assert validation["boundary_valid"] is False
    assert validation["unknowns"]


def test_validation_result_hash_deterministic():
    first = validate_semantic_contract(_valid_contract())
    second = validate_semantic_contract(_valid_contract())

    assert first == second
    assert first["validation_result_hash"].startswith("sha256:")
    assert first["contract_hash"].startswith("sha256:")


def test_cli_never_invokes_provider_or_execution(monkeypatch, tmp_path):
    called = {"execution": False, "provider": False}

    def forbidden_execution(*args, **kwargs):
        called["execution"] = True
        raise AssertionError("execution must not run")

    def forbidden_provider(*args, **kwargs):
        called["provider"] = True
        raise AssertionError("provider must not run")

    import aigol.cli.aigol_cli as cli
    import agol_bridge.providers.codex_cli_provider as provider

    monkeypatch.setattr(cli, "run_execution_handoff", forbidden_execution)
    if hasattr(provider, "run_bounded_codex_cli"):
        monkeypatch.setattr(provider, "run_bounded_codex_cli", forbidden_provider)

    contract_path = tmp_path / "contract.json"
    contract_path.write_text(json.dumps(_valid_contract(), sort_keys=True), encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args(["moc", "validate-contract", "--input", str(contract_path), "--json"])
    result = run_command(args)

    assert called == {"execution": False, "provider": False}
    assert result["execution_authority_added"] is False
    assert result["worker_dispatch_added"] is False
    assert result["provider_activation_added"] is False
    assert result["semantic_reasoning_added"] is False
    assert result["contract_validation_result"]["validation_status"] == VALID


def test_no_contract_mutation_occurs(tmp_path):
    contract = _valid_contract()
    before = json.dumps(contract, sort_keys=True)
    output_path = tmp_path / "validation.json"

    result = validate_semantic_contract(contract)
    assert json.dumps(contract, sort_keys=True) == before

    contract_path = tmp_path / "contract.json"
    contract_path.write_text(before, encoding="utf-8")
    inspect_contract_validation(input_path=contract_path, output_path=output_path)
    assert contract_path.read_text(encoding="utf-8") == before
    assert json.loads(output_path.read_text(encoding="utf-8"))["validation_result_hash"] == result["validation_result_hash"]


def test_cli_renders_validation_summary(tmp_path):
    contract_path = tmp_path / "contract.json"
    contract_path.write_text(json.dumps(_valid_contract(), sort_keys=True), encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args(["moc", "validate-contract", "--input", str(contract_path)])
    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol moc validate-contract"
    assert "AIGOL MOC VALIDATE CONTRACT" in rendered
    assert "Validation Status" in rendered
    assert "Governance Guarantees" in rendered
