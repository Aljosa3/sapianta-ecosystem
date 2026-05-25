import json

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.moc.approval_gate import (
    APPROVAL_PENDING,
    APPROVAL_REJECTED,
    APPROVED_FOR_WORKER_PREPARATION,
    FAIL_CLOSED,
    evaluate_approval_gate,
    inspect_approval_gate,
)
from aigol.moc.proposal_ledger import build_proposal_ledger_entry
from aigol.moc.proposal_persistence import PROPOSED, VALIDATED, create_proposal_persistence_record


def _proposal():
    proposal = {
        "proposal_id": "proposal-approval-001",
        "proposal_summary": "Approve worker preparation eligibility.",
        "linked_contract_id": "moc-intent-approval",
        "linked_contract_hash": "sha256:contract",
        "suggested_actions": ["prepare_worker_task"],
        "expected_outputs": ["MOC_V1_APPROVAL_GATE_RESULT"],
        "bounded_scope": "approval gate only",
        "approvals_required": ["human_review"],
        "replay_safe": True,
        "advisory_only": True,
        "lineage_refs": [{"ref_type": "contract", "hash": "sha256:contract"}],
        "validation_refs": [{"ref_type": "validation", "hash": "sha256:validation"}],
        "correction_refs": [],
        "approval_refs": [],
    }
    proposal["proposal_hash"] = "sha256:proposal"
    return proposal


def _ledger_entry(proposal=None):
    proposal = proposal or _proposal()
    persistence = create_proposal_persistence_record(
        proposal,
        proposal_state=VALIDATED,
        previous_state=PROPOSED,
    )
    return build_proposal_ledger_entry(persistence, previous_ledger_hash="sha256:previous")


def _approval():
    return {
        "approval_id": "approval-001",
        "human_review": True,
        "approval_decision": "APPROVED_FOR_WORKER_PREPARATION",
        "reviewer": "human",
        "approval_notes": "Approved for worker preparation eligibility only.",
    }


def test_valid_proposal_becomes_approved_for_worker_preparation():
    proposal = _proposal()
    ledger = _ledger_entry(proposal)

    result = evaluate_approval_gate(proposal, ledger, _approval())

    assert result["approval_status"] == APPROVED_FOR_WORKER_PREPARATION
    assert result["approval_eligible"] is True
    assert result["approval_requirements_satisfied"] is True


def test_missing_ledger_evidence_fails_closed():
    result = evaluate_approval_gate(_proposal(), None, _approval())

    assert result["approval_status"] == FAIL_CLOSED
    assert "ledger evidence missing" in result["approval_violations"]


def test_missing_human_approval_fails():
    proposal = _proposal()
    ledger = _ledger_entry(proposal)
    approval = dict(_approval())
    approval["human_review"] = False

    result = evaluate_approval_gate(proposal, ledger, approval)

    assert result["approval_status"] == APPROVAL_PENDING
    assert "human_review approval must exist" in result["approval_violations"]


def test_unresolved_correction_loop_fails():
    proposal = _proposal()
    proposal["correction_status"] = "CORRECTION_REQUIRED"
    ledger = _ledger_entry(proposal)

    result = evaluate_approval_gate(proposal, ledger, _approval())

    assert result["approval_status"] == APPROVAL_REJECTED
    assert "correction loop unresolved" in result["approval_violations"]


def test_advisory_only_false_fails():
    proposal = _proposal()
    proposal["advisory_only"] = False
    ledger = _ledger_entry(proposal)

    result = evaluate_approval_gate(proposal, ledger, _approval())

    assert result["approval_status"] == APPROVAL_REJECTED
    assert "advisory_only must be true" in result["approval_violations"]


def test_replay_safe_false_fails():
    proposal = _proposal()
    proposal["replay_safe"] = False
    ledger = _ledger_entry(proposal)

    result = evaluate_approval_gate(proposal, ledger, _approval())

    assert result["approval_status"] == APPROVAL_REJECTED
    assert "replay_safe must be true" in result["approval_violations"]


def test_forbidden_authority_field_fails():
    proposal = _proposal()
    proposal["execution_authority"] = True
    ledger = _ledger_entry(proposal)

    result = evaluate_approval_gate(proposal, ledger, _approval())

    assert result["approval_status"] == APPROVAL_REJECTED
    assert any("execution_authority" in violation for violation in result["approval_violations"])


def test_deterministic_approval_gate_hash():
    proposal = _proposal()
    ledger = _ledger_entry(proposal)

    first = evaluate_approval_gate(proposal, ledger, _approval())
    second = evaluate_approval_gate(proposal, ledger, _approval())

    assert first == second
    assert first["approval_gate_hash"].startswith("sha256:")


def test_cli_never_invokes_execution_or_provider(monkeypatch, tmp_path):
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

    proposal = _proposal()
    ledger = _ledger_entry(proposal)
    proposal_path = tmp_path / "proposal.json"
    ledger_path = tmp_path / "ledger.json"
    approval_path = tmp_path / "approval.json"
    proposal_path.write_text(json.dumps(proposal, sort_keys=True), encoding="utf-8")
    ledger_path.write_text(json.dumps(ledger, sort_keys=True), encoding="utf-8")
    approval_path.write_text(json.dumps(_approval(), sort_keys=True), encoding="utf-8")

    parser = build_parser()
    args = parser.parse_args(
        [
            "moc",
            "approval-gate",
            "--proposal",
            str(proposal_path),
            "--ledger-entry",
            str(ledger_path),
            "--approval-evidence",
            str(approval_path),
            "--json",
        ]
    )
    result = run_command(args)

    assert called == {"execution": False, "provider": False}
    assert result["execution_authority_added"] is False
    assert result["worker_dispatch_added"] is False
    assert result["provider_activation_added"] is False
    assert result["approval_gate_result"]["approval_status"] == APPROVED_FOR_WORKER_PREPARATION


def test_no_governance_mutation_occurs(tmp_path):
    proposal = _proposal()
    ledger = _ledger_entry(proposal)
    approval = _approval()
    proposal_before = json.dumps(proposal, sort_keys=True)
    ledger_before = json.dumps(ledger, sort_keys=True)
    approval_before = json.dumps(approval, sort_keys=True)

    evaluate_approval_gate(proposal, ledger, approval)

    assert json.dumps(proposal, sort_keys=True) == proposal_before
    assert json.dumps(ledger, sort_keys=True) == ledger_before
    assert json.dumps(approval, sort_keys=True) == approval_before


def test_no_hidden_continuation_occurs():
    proposal = _proposal()
    ledger = _ledger_entry(proposal)

    result = evaluate_approval_gate(proposal, ledger, _approval())

    assert result["governance_guarantees"]["autonomous_continuation"] is False
    assert result["governance_guarantees"]["automatic_execution"] is False
    assert result["governance_guarantees"]["worker_dispatch"] is False


def test_approval_does_not_imply_execution():
    proposal = _proposal()
    ledger = _ledger_entry(proposal)

    result = evaluate_approval_gate(proposal, ledger, _approval())

    assert result["approval_status"] == APPROVED_FOR_WORKER_PREPARATION
    assert result["governance_guarantees"]["execution_authority"] is False
    assert result["governance_guarantees"]["provider_activation"] is False
    assert result["governance_guarantees"]["proposal_execution"] is False


def test_cli_renders_approval_summary(tmp_path):
    proposal = _proposal()
    ledger = _ledger_entry(proposal)
    proposal_path = tmp_path / "proposal.json"
    ledger_path = tmp_path / "ledger.json"
    approval_path = tmp_path / "approval.json"
    proposal_path.write_text(json.dumps(proposal, sort_keys=True), encoding="utf-8")
    ledger_path.write_text(json.dumps(ledger, sort_keys=True), encoding="utf-8")
    approval_path.write_text(json.dumps(_approval(), sort_keys=True), encoding="utf-8")

    parser = build_parser()
    args = parser.parse_args(
        [
            "moc",
            "approval-gate",
            "--proposal",
            str(proposal_path),
            "--ledger-entry",
            str(ledger_path),
            "--approval-evidence",
            str(approval_path),
        ]
    )
    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol moc approval-gate"
    assert "AIGOL MOC APPROVAL GATE" in rendered
    assert "Approval Gate" in rendered
    assert "Governance Guarantees" in rendered


def test_output_write_preserves_inputs(tmp_path):
    proposal = _proposal()
    ledger = _ledger_entry(proposal)
    proposal_path = tmp_path / "proposal.json"
    ledger_path = tmp_path / "ledger.json"
    approval_path = tmp_path / "approval.json"
    output_path = tmp_path / "approval_result.json"
    proposal_text = json.dumps(proposal, sort_keys=True)
    ledger_text = json.dumps(ledger, sort_keys=True)
    approval_text = json.dumps(_approval(), sort_keys=True)
    proposal_path.write_text(proposal_text, encoding="utf-8")
    ledger_path.write_text(ledger_text, encoding="utf-8")
    approval_path.write_text(approval_text, encoding="utf-8")

    inspect_approval_gate(
        proposal_path=proposal_path,
        ledger_entry_path=ledger_path,
        approval_evidence_path=approval_path,
        output_path=output_path,
    )

    assert proposal_path.read_text(encoding="utf-8") == proposal_text
    assert ledger_path.read_text(encoding="utf-8") == ledger_text
    assert approval_path.read_text(encoding="utf-8") == approval_text
