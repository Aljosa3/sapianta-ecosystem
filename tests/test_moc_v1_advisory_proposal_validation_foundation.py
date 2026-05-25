import json

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.moc.advisory_contract_generation import generate_advisory_contract
from aigol.moc.advisory_proposal_validation import (
    FAIL_CLOSED,
    INVALID_BOUNDARY,
    INVALID_CONTRACT_REFERENCE,
    VALID,
    inspect_advisory_proposal_validation,
    validate_advisory_proposal,
)


def _generation_input():
    return {
        "intent_summary": "Prepare bounded advisory proposal validation evidence.",
        "scope": "proposal validation only",
        "risk_level": "low",
        "mutation_classification": "parametric",
        "governance_anchors": [
            {
                "anchor_id": "MOC_V1_ADVISORY_PROPOSAL_VALIDATION_FOUNDATION",
                "anchor_type": "governance_specification",
                "source_ref": "docs/governance/cognition/MOC_V1_ADVISORY_PROPOSAL_VALIDATION_FOUNDATION.md",
            }
        ],
        "allowed_actions": ["prepare_validation_summary", "record_advisory_evidence"],
        "forbidden_actions": ["execute_task"],
        "required_approvals": ["human_review"],
        "expected_outputs": ["MOC_V1_ADVISORY_PROPOSAL_VALIDATION_RESULT"],
        "deterministic_constraints": {
            "no_hidden_inference": True,
            "no_self_dispatch": True,
            "no_runtime_mutation": True,
            "no_autonomous_continuation": True,
            "no_provider_activation": True,
        },
    }


def _validated_contract_artifact():
    return generate_advisory_contract(_generation_input())


def _valid_proposal(contract_artifact=None):
    artifact = contract_artifact or _validated_contract_artifact()
    contract = artifact["contract"]
    return {
        "proposal_id": "proposal-001",
        "proposal_summary": "Prepare replay-visible validation evidence.",
        "linked_contract_id": contract["intent_id"],
        "linked_contract_hash": artifact["contract_hash"],
        "suggested_actions": ["prepare_validation_summary"],
        "expected_outputs": ["MOC_V1_ADVISORY_PROPOSAL_VALIDATION_RESULT"],
        "bounded_scope": "proposal validation only",
        "approvals_required": ["human_review"],
        "replay_safe": True,
        "advisory_only": True,
    }


def test_valid_proposal_passes():
    contract = _validated_contract_artifact()
    proposal = _valid_proposal(contract)

    result = validate_advisory_proposal(proposal, contract)

    assert result["proposal_validation_status"] == VALID
    assert result["proposal_scope_valid"] is True
    assert result["proposal_boundary_valid"] is True
    assert result["proposal_replay_safe"] is True
    assert result["proposal_advisory_only"] is True


def test_invalid_contract_reference_fails():
    contract = _validated_contract_artifact()
    proposal = _valid_proposal(contract)
    proposal["linked_contract_hash"] = "sha256:not-the-contract"

    result = validate_advisory_proposal(proposal, contract)

    assert result["proposal_validation_status"] == INVALID_CONTRACT_REFERENCE
    assert "linked_contract_hash mismatch" in result["violations"]


def test_advisory_only_false_fails():
    contract = _validated_contract_artifact()
    proposal = _valid_proposal(contract)
    proposal["advisory_only"] = False

    result = validate_advisory_proposal(proposal, contract)

    assert result["proposal_validation_status"] == INVALID_BOUNDARY
    assert "advisory_only must be true" in result["violations"]


def test_replay_safe_false_fails():
    contract = _validated_contract_artifact()
    proposal = _valid_proposal(contract)
    proposal["replay_safe"] = False

    result = validate_advisory_proposal(proposal, contract)

    assert result["proposal_validation_status"] == INVALID_BOUNDARY
    assert "replay_safe must be true" in result["violations"]


def test_forbidden_action_fails():
    contract = _validated_contract_artifact()
    proposal = _valid_proposal(contract)
    proposal["suggested_actions"] = ["execute_task"]

    result = validate_advisory_proposal(proposal, contract)

    assert result["proposal_validation_status"] == INVALID_BOUNDARY
    assert any("forbidden_actions" in violation for violation in result["violations"])


def test_action_outside_allowed_actions_fails():
    contract = _validated_contract_artifact()
    proposal = _valid_proposal(contract)
    proposal["suggested_actions"] = ["invent_unlisted_action"]

    result = validate_advisory_proposal(proposal, contract)

    assert result["proposal_validation_status"] == INVALID_BOUNDARY
    assert any("outside contract allowed_actions" in violation for violation in result["violations"])


def test_missing_human_review_fails():
    contract = _validated_contract_artifact()
    proposal = _valid_proposal(contract)
    proposal["approvals_required"] = ["peer_review"]

    result = validate_advisory_proposal(proposal, contract)

    assert result["proposal_validation_status"] == INVALID_BOUNDARY
    assert "approvals_required must include human_review" in result["violations"]


def test_malformed_proposal_fails_closed(tmp_path):
    contract_path = tmp_path / "contract.json"
    proposal_path = tmp_path / "proposal.json"
    contract_path.write_text(json.dumps(_validated_contract_artifact(), sort_keys=True), encoding="utf-8")
    proposal_path.write_text("{not-json", encoding="utf-8")

    result = inspect_advisory_proposal_validation(proposal_path=proposal_path, contract_path=contract_path)

    validation = result["advisory_proposal_validation_result"]
    assert validation["proposal_validation_status"] == FAIL_CLOSED
    assert validation["unknowns"]


def test_deterministic_proposal_hash_stable():
    contract = _validated_contract_artifact()
    proposal = _valid_proposal(contract)

    first = validate_advisory_proposal(proposal, contract)
    second = validate_advisory_proposal(proposal, contract)

    assert first == second
    assert first["proposal_hash"].startswith("sha256:")
    assert first["validation_result_hash"].startswith("sha256:")


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

    contract = _validated_contract_artifact()
    proposal = _valid_proposal(contract)
    contract_path = tmp_path / "contract.json"
    proposal_path = tmp_path / "proposal.json"
    contract_path.write_text(json.dumps(contract, sort_keys=True), encoding="utf-8")
    proposal_path.write_text(json.dumps(proposal, sort_keys=True), encoding="utf-8")

    parser = build_parser()
    args = parser.parse_args(
        ["moc", "validate-proposal", "--proposal", str(proposal_path), "--contract", str(contract_path), "--json"]
    )
    result = run_command(args)

    assert called == {"execution": False, "provider": False}
    assert result["execution_authority_added"] is False
    assert result["worker_dispatch_added"] is False
    assert result["provider_activation_added"] is False
    assert result["semantic_reasoning_added"] is False
    assert result["advisory_proposal_validation_result"]["proposal_validation_status"] == VALID


def test_no_proposal_mutation_occurs(tmp_path):
    contract = _validated_contract_artifact()
    proposal = _valid_proposal(contract)
    before = json.dumps(proposal, sort_keys=True)
    output_path = tmp_path / "proposal_validation.json"

    validate_advisory_proposal(proposal, contract)
    assert json.dumps(proposal, sort_keys=True) == before

    contract_path = tmp_path / "contract.json"
    proposal_path = tmp_path / "proposal.json"
    contract_path.write_text(json.dumps(contract, sort_keys=True), encoding="utf-8")
    proposal_path.write_text(before, encoding="utf-8")
    inspect_advisory_proposal_validation(proposal_path=proposal_path, contract_path=contract_path, output_path=output_path)
    assert proposal_path.read_text(encoding="utf-8") == before
    assert json.loads(output_path.read_text(encoding="utf-8"))["governance_guarantees"]["worker_dispatch"] is False


def test_no_hidden_inference_occurs():
    contract = _validated_contract_artifact()
    proposal = _valid_proposal(contract)

    result = validate_advisory_proposal(proposal, contract)

    assert result["validation_constraints"]["explicit_fields_only"] is True
    assert result["validation_constraints"]["hidden_inference"] is False
    assert result["validation_constraints"]["proposal_repair"] is False
    assert result["validation_constraints"]["proposal_execution"] is False
    assert result["validation_constraints"]["worker_task_created"] is False


def test_cli_renders_validation_summary(tmp_path):
    contract = _validated_contract_artifact()
    proposal = _valid_proposal(contract)
    contract_path = tmp_path / "contract.json"
    proposal_path = tmp_path / "proposal.json"
    contract_path.write_text(json.dumps(contract, sort_keys=True), encoding="utf-8")
    proposal_path.write_text(json.dumps(proposal, sort_keys=True), encoding="utf-8")

    parser = build_parser()
    args = parser.parse_args(["moc", "validate-proposal", "--proposal", str(proposal_path), "--contract", str(contract_path)])
    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol moc validate-proposal"
    assert "AIGOL MOC VALIDATE PROPOSAL" in rendered
    assert "Proposal Validation Status" in rendered
    assert "Contract Linkage" in rendered
    assert "Governance Guarantees" in rendered
