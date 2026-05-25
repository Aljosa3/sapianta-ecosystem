import json

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.moc.proposal_persistence import (
    APPROVAL_PENDING,
    APPROVED,
    CORRECTED,
    CORRECTION_REQUIRED,
    FAIL_CLOSED,
    PREPARED_FOR_WORKER,
    PROPOSED,
    REJECTED,
    VALIDATED,
    VALID_TRANSITIONS,
    create_proposal_persistence_record,
    inspect_proposal_persistence,
)


def _proposal():
    return {
        "proposal_id": "proposal-persistence-001",
        "proposal_summary": "Persist advisory proposal lifecycle evidence.",
        "linked_contract_id": "moc-intent-persistence",
        "linked_contract_hash": "sha256:contract",
        "suggested_actions": ["prepare_validation_summary"],
        "expected_outputs": ["MOC_V1_PROPOSAL_PERSISTENCE_RECORD"],
        "bounded_scope": "proposal persistence only",
        "approvals_required": ["human_review"],
        "replay_safe": True,
        "advisory_only": True,
        "correction_attempt": 2,
        "lineage_refs": [{"ref_type": "contract", "hash": "sha256:contract"}],
        "validation_refs": [{"ref_type": "validation", "hash": "sha256:validation"}],
        "correction_refs": [{"ref_type": "correction", "hash": "sha256:correction"}],
        "approval_refs": [{"ref_type": "approval", "hash": "sha256:approval"}],
    }


def test_valid_transitions_succeed():
    proposal = _proposal()
    for previous_state, state in sorted(VALID_TRANSITIONS):
        record = create_proposal_persistence_record(
            proposal,
            proposal_state=state,
            previous_state=previous_state,
        )
        assert record["proposal_state"] == state
        assert record["previous_state"] == previous_state
        assert record["state_transition_valid"] is True


def test_invalid_transition_fails_closed():
    record = create_proposal_persistence_record(
        _proposal(),
        proposal_state=PREPARED_FOR_WORKER,
        previous_state=PROPOSED,
    )

    assert record["proposal_state"] == FAIL_CLOSED
    assert record["requested_proposal_state"] == PREPARED_FOR_WORKER
    assert record["state_transition_valid"] is False
    assert record["transition_violations"]


def test_lineage_refs_preserved():
    record = create_proposal_persistence_record(
        _proposal(),
        proposal_state=VALIDATED,
        previous_state=PROPOSED,
    )

    assert record["lineage_refs"] == [{"ref_type": "contract", "hash": "sha256:contract"}]
    assert record["validation_refs"] == [{"ref_type": "validation", "hash": "sha256:validation"}]
    assert record["approval_refs"] == [{"ref_type": "approval", "hash": "sha256:approval"}]


def test_correction_chain_preserved():
    record = create_proposal_persistence_record(
        _proposal(),
        proposal_state=CORRECTED,
        previous_state=CORRECTION_REQUIRED,
    )

    assert record["state_transition_valid"] is True
    assert record["correction_attempt"] == 2
    assert record["correction_refs"] == [{"ref_type": "correction", "hash": "sha256:correction"}]


def test_deterministic_persistence_hash():
    first = create_proposal_persistence_record(
        _proposal(),
        proposal_state=APPROVAL_PENDING,
        previous_state=VALIDATED,
    )
    second = create_proposal_persistence_record(
        _proposal(),
        proposal_state=APPROVAL_PENDING,
        previous_state=VALIDATED,
    )

    assert first == second
    assert first["persistence_hash"].startswith("sha256:")


def test_replay_safe_always_true():
    record = create_proposal_persistence_record(
        _proposal(),
        proposal_state=REJECTED,
        previous_state=PROPOSED,
    )

    assert record["replay_safe"] is True


def test_advisory_only_always_true():
    record = create_proposal_persistence_record(
        _proposal(),
        proposal_state=APPROVED,
        previous_state=APPROVAL_PENDING,
    )

    assert record["advisory_only"] is True


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

    proposal_path = tmp_path / "proposal.json"
    proposal_path.write_text(json.dumps(_proposal(), sort_keys=True), encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args(
        [
            "moc",
            "persist-proposal",
            "--proposal",
            str(proposal_path),
            "--state",
            VALIDATED,
            "--previous-state",
            PROPOSED,
            "--json",
        ]
    )
    result = run_command(args)

    assert called == {"execution": False, "provider": False}
    assert result["execution_authority_added"] is False
    assert result["worker_dispatch_added"] is False
    assert result["provider_activation_added"] is False


def test_no_governance_mutation_occurs(tmp_path):
    proposal = _proposal()
    before = json.dumps(proposal, sort_keys=True)
    output_path = tmp_path / "record.json"

    create_proposal_persistence_record(proposal, proposal_state=VALIDATED, previous_state=PROPOSED)
    assert json.dumps(proposal, sort_keys=True) == before

    proposal_path = tmp_path / "proposal.json"
    proposal_path.write_text(before, encoding="utf-8")
    inspect_proposal_persistence(
        proposal_path=proposal_path,
        proposal_state=VALIDATED,
        previous_state=PROPOSED,
        output_path=output_path,
    )
    assert proposal_path.read_text(encoding="utf-8") == before
    assert json.loads(output_path.read_text(encoding="utf-8"))["governance_guarantees"]["governance_mutation"] is False


def test_no_hidden_continuation_occurs():
    record = create_proposal_persistence_record(
        _proposal(),
        proposal_state=PREPARED_FOR_WORKER,
        previous_state=APPROVED,
    )

    assert record["state_transition_valid"] is True
    assert record["governance_guarantees"]["hidden_continuation"] is False
    assert record["governance_guarantees"]["worker_dispatch"] is False
    assert record["governance_guarantees"]["proposal_execution"] is False


def test_cli_renders_persistence_summary(tmp_path):
    proposal_path = tmp_path / "proposal.json"
    proposal_path.write_text(json.dumps(_proposal(), sort_keys=True), encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args(
        [
            "moc",
            "persist-proposal",
            "--proposal",
            str(proposal_path),
            "--state",
            VALIDATED,
            "--previous-state",
            PROPOSED,
        ]
    )
    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol moc persist-proposal"
    assert "AIGOL MOC PERSIST PROPOSAL" in rendered
    assert "Proposal Persistence" in rendered
    assert "Transition" in rendered
    assert "Governance Guarantees" in rendered
