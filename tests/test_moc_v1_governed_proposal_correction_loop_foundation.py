import json

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.moc.advisory_contract_generation import generate_advisory_contract
from aigol.moc.advisory_proposal_validation import validate_advisory_proposal
from aigol.moc.proposal_correction_loop import (
    CORRECTION_LIMIT_REACHED,
    CORRECTION_REQUIRED,
    PROPOSAL_VALID,
    build_proposal_correction_feedback,
    inspect_proposal_correction_feedback,
)


def _generation_input():
    return {
        "intent_summary": "Prepare bounded correction feedback evidence.",
        "scope": "proposal correction feedback only",
        "risk_level": "low",
        "mutation_classification": "parametric",
        "governance_anchors": [
            {
                "anchor_id": "MOC_V1_GOVERNED_PROPOSAL_CORRECTION_LOOP_FOUNDATION",
                "anchor_type": "governance_specification",
                "source_ref": "docs/governance/cognition/MOC_V1_GOVERNED_PROPOSAL_CORRECTION_LOOP_FOUNDATION.md",
            }
        ],
        "allowed_actions": ["prepare_validation_summary"],
        "forbidden_actions": ["execute_task"],
        "required_approvals": ["human_review"],
        "expected_outputs": ["MOC_V1_PROPOSAL_CORRECTION_FEEDBACK"],
        "deterministic_constraints": {
            "no_hidden_inference": True,
            "no_self_dispatch": True,
            "no_runtime_mutation": True,
            "no_autonomous_continuation": True,
            "no_provider_activation": True,
        },
    }


def _contract():
    return generate_advisory_contract(_generation_input())


def _proposal(contract_artifact=None, *, valid=True):
    artifact = contract_artifact or _contract()
    contract = artifact["contract"]
    return {
        "proposal_id": "proposal-correction-001",
        "proposal_summary": "Prepare correction-loop validation evidence.",
        "linked_contract_id": contract["intent_id"],
        "linked_contract_hash": artifact["contract_hash"],
        "suggested_actions": ["prepare_validation_summary" if valid else "execute_task"],
        "expected_outputs": ["MOC_V1_PROPOSAL_CORRECTION_FEEDBACK"],
        "bounded_scope": "proposal correction feedback only",
        "approvals_required": ["human_review"],
        "replay_safe": True,
        "advisory_only": True,
    }


def _validation_result(valid=False):
    contract = _contract()
    proposal = _proposal(contract, valid=valid)
    return validate_advisory_proposal(proposal, contract)


def test_invalid_proposal_validation_result_creates_correction_required():
    validation = _validation_result(valid=False)

    feedback = build_proposal_correction_feedback(validation, attempt_number=1, max_attempts=3)

    assert feedback["correction_status"] == CORRECTION_REQUIRED
    assert feedback["linked_proposal_id"] == "proposal-correction-001"
    assert feedback["required_corrections"]


def test_valid_proposal_validation_result_creates_proposal_valid():
    validation = _validation_result(valid=True)

    feedback = build_proposal_correction_feedback(validation, attempt_number=1, max_attempts=3)

    assert feedback["correction_status"] == PROPOSAL_VALID
    assert feedback["required_corrections"] == []


def test_max_attempts_reached_creates_limit_reached():
    validation = _validation_result(valid=False)

    feedback = build_proposal_correction_feedback(validation, attempt_number=3, max_attempts=3)

    assert feedback["correction_status"] == CORRECTION_LIMIT_REACHED
    assert feedback["rejection_reason"] == "correction attempt limit reached"


def test_feedback_contains_explicit_violations():
    validation = _validation_result(valid=False)

    feedback = build_proposal_correction_feedback(validation, attempt_number=1, max_attempts=3)

    assert feedback["violations"] == validation["violations"]
    assert feedback["llm_instruction_payload"]["explicit_violations"] == validation["violations"]


def test_feedback_contains_forbidden_next_steps():
    feedback = build_proposal_correction_feedback(_validation_result(valid=False), attempt_number=1, max_attempts=3)

    for forbidden in (
        "execute_proposal",
        "dispatch_worker",
        "activate_provider",
        "bypass_human_approval",
        "create_hidden_continuation",
        "repair_inside_aigol",
    ):
        assert forbidden in feedback["forbidden_next_steps"]


def test_feedback_is_safe_for_llm_correction():
    feedback = build_proposal_correction_feedback(_validation_result(valid=False), attempt_number=1, max_attempts=3)
    payload = feedback["llm_instruction_payload"]

    assert payload["safe_for_llm_correction"] is True
    assert payload["llm_called_by_aigol"] is False
    assert payload["aigol_repaired_proposal"] is False
    assert "proposal does not equal execution" in payload["required_reminders"]


def test_deterministic_feedback_hash():
    validation = _validation_result(valid=False)

    first = build_proposal_correction_feedback(validation, attempt_number=1, max_attempts=3)
    second = build_proposal_correction_feedback(validation, attempt_number=1, max_attempts=3)

    assert first == second
    assert first["correction_feedback_hash"].startswith("sha256:")


def test_cli_never_invokes_provider_execution_or_llm(monkeypatch, tmp_path):
    called = {"execution": False, "provider": False, "llm": False}

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

    validation_path = tmp_path / "validation.json"
    validation_path.write_text(json.dumps(_validation_result(valid=False), sort_keys=True), encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args(
        [
            "moc",
            "correction-feedback",
            "--validation-result",
            str(validation_path),
            "--attempt",
            "1",
            "--max-attempts",
            "3",
            "--json",
        ]
    )
    result = run_command(args)

    assert called == {"execution": False, "provider": False, "llm": False}
    assert result["execution_authority_added"] is False
    assert result["worker_dispatch_added"] is False
    assert result["provider_activation_added"] is False
    assert result["llm_call_added"] is False


def test_no_proposal_mutation_occurs(tmp_path):
    validation = _validation_result(valid=False)
    before = json.dumps(validation, sort_keys=True)
    output_path = tmp_path / "feedback.json"

    build_proposal_correction_feedback(validation, attempt_number=1, max_attempts=3)
    assert json.dumps(validation, sort_keys=True) == before

    validation_path = tmp_path / "validation.json"
    validation_path.write_text(before, encoding="utf-8")
    inspect_proposal_correction_feedback(
        validation_result_path=validation_path,
        attempt_number=1,
        max_attempts=3,
        output_path=output_path,
    )
    assert validation_path.read_text(encoding="utf-8") == before
    assert json.loads(output_path.read_text(encoding="utf-8"))["governance_guarantees"]["aigol_repaired_proposal"] is False


def test_no_hidden_inference_occurs():
    feedback = build_proposal_correction_feedback(_validation_result(valid=False), attempt_number=1, max_attempts=3)

    assert feedback["governance_guarantees"]["hidden_inference"] is False
    assert feedback["governance_guarantees"]["aigol_repaired_proposal"] is False
    assert feedback["governance_guarantees"]["hidden_continuation"] is False


def test_cli_renders_correction_summary(tmp_path):
    validation_path = tmp_path / "validation.json"
    validation_path.write_text(json.dumps(_validation_result(valid=False), sort_keys=True), encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args(
        [
            "moc",
            "correction-feedback",
            "--validation-result",
            str(validation_path),
            "--attempt",
            "1",
            "--max-attempts",
            "3",
        ]
    )
    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol moc correction-feedback"
    assert "AIGOL MOC CORRECTION FEEDBACK" in rendered
    assert "Correction Status" in rendered
    assert "Forbidden Next Steps" in rendered
    assert "Governance Guarantees" in rendered
