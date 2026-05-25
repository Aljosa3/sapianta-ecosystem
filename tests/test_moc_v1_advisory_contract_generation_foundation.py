import json

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.moc.advisory_contract_generation import (
    DEFAULT_FORBIDDEN_ACTIONS,
    FAIL_CLOSED,
    GENERATED_INVALID,
    GENERATED_VALID,
    generate_advisory_contract,
    inspect_advisory_contract_generation,
)
from aigol.moc.contract_validation import VALID


def _generation_input():
    return {
        "intent_summary": "Prepare a bounded MOC semantic contract draft.",
        "scope": "advisory contract generation only",
        "risk_level": "low",
        "mutation_classification": "parametric",
        "governance_anchors": [
            {
                "anchor_id": "MOC_V1_SPEC",
                "anchor_type": "governance_specification",
                "source_ref": "docs/governance/cognition/MOC_V1_SPEC.md",
            }
        ],
        "allowed_actions": ["generate advisory semantic contract draft"],
        "forbidden_actions": ["execute_task"],
        "required_approvals": [],
        "expected_outputs": ["MOC_V1_ADVISORY_CONTRACT_GENERATION_RESULT"],
        "deterministic_constraints": {
            "no_hidden_inference": True,
            "no_self_dispatch": True,
            "no_runtime_mutation": True,
            "no_autonomous_continuation": True,
            "no_provider_activation": True,
        },
    }


def test_valid_explicit_input_generates_valid_contract():
    result = generate_advisory_contract(_generation_input())

    assert result["generation_status"] == GENERATED_VALID
    assert result["validation_result"]["validation_status"] == VALID
    assert result["contract"]["intent_id"].startswith("moc-intent-")
    assert result["contract_hash"].startswith("sha256:")


def test_missing_required_input_fails_closed():
    generation_input = _generation_input()
    generation_input.pop("scope")

    result = generate_advisory_contract(generation_input)

    assert result["generation_status"] == FAIL_CLOSED
    assert result["contract"] == {}
    assert any("scope" in violation for violation in result["violations"])


def test_generated_contract_always_has_advisory_only_true():
    result = generate_advisory_contract(_generation_input())

    assert result["contract"]["advisory_only"] is True
    assert result["governance_guarantees"]["advisory_only"] is True


def test_generated_contract_always_has_replay_safe_true():
    result = generate_advisory_contract(_generation_input())

    assert result["contract"]["replay_safe"] is True
    assert result["governance_guarantees"]["replay_safe"] is True


def test_default_forbidden_actions_include_blockers():
    result = generate_advisory_contract(_generation_input())

    for action in DEFAULT_FORBIDDEN_ACTIONS:
        assert action in result["contract"]["forbidden_actions"]


def test_generated_contract_is_validated_after_generation():
    result = generate_advisory_contract(_generation_input())

    assert result["validation_result"]["artifact_type"] == "MOC_V1_CONTRACT_VALIDATION_RESULT"
    assert result["validation_result"]["contract_hash"] == result["contract_hash"]
    assert result["validation_result"]["validation_status"] == VALID


def test_invalid_generated_contract_cannot_be_marked_valid():
    generation_input = _generation_input()
    generation_input["risk_level"] = "unbounded"

    result = generate_advisory_contract(generation_input)

    assert result["generation_status"] == GENERATED_INVALID
    assert result["validation_result"]["validation_status"] != VALID
    assert result["validation_result"]["schema_valid"] is False


def test_deterministic_contract_hash_and_result_hash():
    first = generate_advisory_contract(_generation_input())
    second = generate_advisory_contract(_generation_input())

    assert first == second
    assert first["contract_hash"].startswith("sha256:")
    assert first["generation_result_hash"].startswith("sha256:")


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

    input_path = tmp_path / "generation_input.json"
    input_path.write_text(json.dumps(_generation_input(), sort_keys=True), encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args(["moc", "generate-contract", "--input", str(input_path), "--json"])
    result = run_command(args)

    assert called == {"execution": False, "provider": False}
    assert result["execution_authority_added"] is False
    assert result["worker_dispatch_added"] is False
    assert result["provider_activation_added"] is False
    assert result["semantic_reasoning_added"] is False
    assert result["advisory_contract_generation_result"]["generation_status"] == GENERATED_VALID


def test_no_governance_mutation_occurs(tmp_path):
    generation_input = _generation_input()
    before = json.dumps(generation_input, sort_keys=True)
    output_path = tmp_path / "generation_result.json"

    generate_advisory_contract(generation_input)
    assert json.dumps(generation_input, sort_keys=True) == before

    input_path = tmp_path / "generation_input.json"
    input_path.write_text(before, encoding="utf-8")
    inspect_advisory_contract_generation(input_path=input_path, output_path=output_path)
    assert input_path.read_text(encoding="utf-8") == before
    assert json.loads(output_path.read_text(encoding="utf-8"))["governance_guarantees"]["governance_mutation"] is False


def test_no_hidden_inference_occurs():
    result = generate_advisory_contract(_generation_input())

    assert result["generation_constraints"]["explicit_input_only"] is True
    assert result["generation_constraints"]["hidden_inference"] is False
    assert result["generation_constraints"]["contract_repair"] is False
    assert result["generation_constraints"]["worker_task_created"] is False
    assert result["generation_constraints"]["execution_triggered"] is False


def test_cli_renders_generation_summary(tmp_path):
    input_path = tmp_path / "generation_input.json"
    input_path.write_text(json.dumps(_generation_input(), sort_keys=True), encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args(["moc", "generate-contract", "--input", str(input_path)])
    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol moc generate-contract"
    assert "AIGOL MOC GENERATE CONTRACT" in rendered
    assert "Generation Status" in rendered
    assert "Validation" in rendered
    assert "Governance Guarantees" in rendered
