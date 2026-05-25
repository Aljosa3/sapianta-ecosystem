import json

from aigol.cli.aigol_cli import build_parser, render_command_result, run_command
from aigol.moc.proposal_ledger import (
    APPENDED,
    FAIL_CLOSED,
    append_proposal_ledger_entry,
    build_proposal_ledger_entry,
    inspect_proposal_ledger_append,
)
from aigol.moc.proposal_persistence import PROPOSED, VALIDATED, create_proposal_persistence_record


def _proposal():
    return {
        "proposal_id": "proposal-ledger-001",
        "linked_contract_id": "moc-intent-ledger",
        "linked_contract_hash": "sha256:contract",
        "replay_safe": True,
        "advisory_only": True,
        "correction_attempt": 1,
        "lineage_refs": [{"ref_type": "contract", "hash": "sha256:contract"}],
        "validation_refs": [{"ref_type": "validation", "hash": "sha256:validation"}],
        "correction_refs": [{"ref_type": "correction", "hash": "sha256:correction"}],
        "approval_refs": [{"ref_type": "approval", "hash": "sha256:approval"}],
    }


def _persistence_record():
    return create_proposal_persistence_record(
        _proposal(),
        proposal_state=VALIDATED,
        previous_state=PROPOSED,
    )


def test_append_only_behavior(tmp_path):
    ledger_path = tmp_path / "proposal_ledger.jsonl"

    first = append_proposal_ledger_entry(_persistence_record(), ledger_path=ledger_path)
    second = append_proposal_ledger_entry(_persistence_record(), ledger_path=ledger_path)
    lines = ledger_path.read_text(encoding="utf-8").splitlines()

    assert first["ledger_append_status"] == APPENDED
    assert second["ledger_append_status"] == APPENDED
    assert len(lines) == 2


def test_prior_entries_never_mutate(tmp_path):
    ledger_path = tmp_path / "proposal_ledger.jsonl"

    append_proposal_ledger_entry(_persistence_record(), ledger_path=ledger_path)
    before = ledger_path.read_text(encoding="utf-8")
    append_proposal_ledger_entry(_persistence_record(), ledger_path=ledger_path)
    after_lines = ledger_path.read_text(encoding="utf-8").splitlines()

    assert after_lines[0] + "\n" == before


def test_deterministic_ledger_hashing():
    record = _persistence_record()
    first = build_proposal_ledger_entry(record, previous_ledger_hash="sha256:previous")
    second = build_proposal_ledger_entry(record, previous_ledger_hash="sha256:previous")

    assert first == second
    assert first["ledger_entry_hash"].startswith("sha256:")
    assert first["ledger_entry_id"].startswith("sha256:")


def test_lineage_continuity_preserved():
    entry = build_proposal_ledger_entry(_persistence_record(), previous_ledger_hash="sha256:previous")

    assert entry["lineage_refs"] == [{"ref_type": "contract", "hash": "sha256:contract"}]
    assert entry["validation_refs"] == [{"ref_type": "validation", "hash": "sha256:validation"}]
    assert entry["correction_refs"] == [{"ref_type": "correction", "hash": "sha256:correction"}]
    assert entry["approval_refs"] == [{"ref_type": "approval", "hash": "sha256:approval"}]


def test_invalid_persistence_record_fails_closed(tmp_path):
    ledger_path = tmp_path / "proposal_ledger.jsonl"
    invalid_record = dict(_persistence_record())
    invalid_record["state_transition_valid"] = False

    entry = append_proposal_ledger_entry(invalid_record, ledger_path=ledger_path)

    assert entry["ledger_append_status"] == FAIL_CLOSED
    assert entry["append_performed"] is False
    assert not ledger_path.exists()


def test_missing_lineage_fails_closed(tmp_path):
    ledger_path = tmp_path / "proposal_ledger.jsonl"
    record = dict(_persistence_record())
    record["lineage_refs"] = []

    entry = append_proposal_ledger_entry(record, ledger_path=ledger_path)

    assert entry["ledger_append_status"] == FAIL_CLOSED
    assert "lineage_refs missing" in entry["violations"]
    assert not ledger_path.exists()


def test_replay_safe_always_true():
    entry = build_proposal_ledger_entry(_persistence_record(), previous_ledger_hash="sha256:previous")

    assert entry["replay_safe"] is True


def test_advisory_only_always_true():
    entry = build_proposal_ledger_entry(_persistence_record(), previous_ledger_hash="sha256:previous")

    assert entry["advisory_only"] is True


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

    record_path = tmp_path / "record.json"
    ledger_path = tmp_path / "ledger.jsonl"
    record_path.write_text(json.dumps(_persistence_record(), sort_keys=True), encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args(
        [
            "moc",
            "append-ledger",
            "--persistence-record",
            str(record_path),
            "--ledger-path",
            str(ledger_path),
            "--json",
        ]
    )
    result = run_command(args)

    assert called == {"execution": False, "provider": False}
    assert result["execution_authority_added"] is False
    assert result["worker_dispatch_added"] is False
    assert result["provider_activation_added"] is False
    assert result["proposal_ledger_entry"]["ledger_append_status"] == APPENDED


def test_no_governance_mutation_occurs(tmp_path):
    record = _persistence_record()
    before = json.dumps(record, sort_keys=True)
    record_path = tmp_path / "record.json"
    output_path = tmp_path / "entry.json"
    ledger_path = tmp_path / "ledger.jsonl"
    record_path.write_text(before, encoding="utf-8")

    inspect_proposal_ledger_append(
        persistence_record_path=record_path,
        ledger_path=ledger_path,
        output_path=output_path,
    )

    assert record_path.read_text(encoding="utf-8") == before
    assert json.loads(output_path.read_text(encoding="utf-8"))["governance_guarantees"]["governance_mutation"] is False


def test_no_hidden_continuation_occurs():
    entry = build_proposal_ledger_entry(_persistence_record(), previous_ledger_hash="sha256:previous")

    assert entry["governance_guarantees"]["hidden_continuation"] is False
    assert entry["governance_guarantees"]["worker_dispatch"] is False
    assert entry["governance_guarantees"]["automatic_approval"] is False


def test_previous_ledger_hash_chains_entries(tmp_path):
    ledger_path = tmp_path / "proposal_ledger.jsonl"

    first = append_proposal_ledger_entry(_persistence_record(), ledger_path=ledger_path)
    second = append_proposal_ledger_entry(_persistence_record(), ledger_path=ledger_path)

    assert first["previous_ledger_hash"] == "UNKNOWN"
    assert second["previous_ledger_hash"] == first["ledger_entry_hash"]


def test_cli_renders_ledger_summary(tmp_path):
    record_path = tmp_path / "record.json"
    ledger_path = tmp_path / "ledger.jsonl"
    record_path.write_text(json.dumps(_persistence_record(), sort_keys=True), encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args(
        [
            "moc",
            "append-ledger",
            "--persistence-record",
            str(record_path),
            "--ledger-path",
            str(ledger_path),
        ]
    )
    result = run_command(args)
    rendered = render_command_result(result)

    assert result["command"] == "aigol moc append-ledger"
    assert "AIGOL MOC APPEND LEDGER" in rendered
    assert "Proposal Ledger" in rendered
    assert "Chronology" in rendered
    assert "Governance Guarantees" in rendered
