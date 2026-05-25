"""Tests for MOC V1 approval-gated worker preparation."""

from __future__ import annotations

import json

from aigol.cli.aigol_cli import build_parser, run_command
from aigol.moc.approval_gate import evaluate_approval_gate
from aigol.moc.proposal_ledger import build_proposal_ledger_entry
from aigol.moc.proposal_persistence import PROPOSED, VALIDATED, create_proposal_persistence_record
from aigol.moc.worker_preparation import (
    FAIL_CLOSED,
    NOT_APPROVED,
    PREPARED_FOR_WORKER,
    inspect_worker_preparation,
    prepare_worker_package,
)


def _proposal() -> dict:
    return {
        "proposal_id": "proposal-worker-001",
        "proposal_summary": "Prepare a bounded worker package without dispatch.",
        "linked_contract_id": "contract-worker-001",
        "linked_contract_hash": "sha256:contract-worker",
        "proposal_hash": "sha256:proposal-worker",
        "suggested_actions": ["prepare_worker_task"],
        "allowed_actions": ["prepare_worker_task"],
        "forbidden_actions": ["execute_task", "dispatch_worker", "activate_provider"],
        "expected_outputs": ["MOC_V1_WORKER_PREPARATION_PACKAGE"],
        "bounded_scope": "worker preparation only",
        "approvals_required": ["human_review"],
        "replay_safe": True,
        "advisory_only": True,
        "lineage_refs": [{"ref_type": "contract", "hash": "sha256:contract-worker"}],
        "approval_refs": [{"ref_type": "human_review", "hash": "sha256:approval-worker"}],
        "validation_refs": [{"ref_type": "proposal_validation", "hash": "sha256:validation-worker"}],
    }


def _approval_gate(proposal: dict | None = None) -> dict:
    proposal_artifact = proposal or _proposal()
    persistence = create_proposal_persistence_record(
        proposal_artifact,
        proposal_state=VALIDATED,
        previous_state=PROPOSED,
    )
    ledger_entry = build_proposal_ledger_entry(
        persistence,
        previous_ledger_hash="sha256:previous-ledger",
    )
    approval_evidence = {
        "human_review": True,
        "approval_decision": "APPROVED_FOR_WORKER_PREPARATION",
    }
    return evaluate_approval_gate(proposal_artifact, ledger_entry, approval_evidence)


def _write_json(path, value: dict) -> None:
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def test_approved_proposal_creates_prepared_for_worker() -> None:
    package = prepare_worker_package(_proposal(), _approval_gate())

    assert package["preparation_status"] == PREPARED_FOR_WORKER
    assert package["allowed_worker_actions"] == ["prepare_worker_task"]


def test_missing_approval_gate_fails_closed() -> None:
    package = prepare_worker_package(_proposal(), None)

    assert package["preparation_status"] == FAIL_CLOSED
    assert "approval gate evidence missing" in package["preparation_violations"]


def test_non_approved_gate_creates_not_approved() -> None:
    approval_gate = _approval_gate()
    approval_gate["approval_status"] = "APPROVAL_REJECTED"

    package = prepare_worker_package(_proposal(), approval_gate)

    assert package["preparation_status"] == NOT_APPROVED
    assert package["allowed_worker_actions"] == []


def test_advisory_only_false_fails() -> None:
    proposal = _proposal()
    proposal["advisory_only"] = False

    package = prepare_worker_package(proposal, _approval_gate(_proposal()))

    assert package["preparation_status"] != PREPARED_FOR_WORKER
    assert "advisory_only must be true" in package["preparation_violations"]


def test_replay_safe_false_fails() -> None:
    proposal = _proposal()
    proposal["replay_safe"] = False

    package = prepare_worker_package(proposal, _approval_gate(_proposal()))

    assert package["preparation_status"] != PREPARED_FOR_WORKER
    assert "replay_safe must be true" in package["preparation_violations"]


def test_forbidden_worker_action_fails() -> None:
    proposal = _proposal()
    proposal["suggested_actions"] = ["execute_task"]

    package = prepare_worker_package(proposal, _approval_gate(_proposal()))

    assert package["preparation_status"] != PREPARED_FOR_WORKER
    assert "worker action appears in explicit forbidden actions: execute_task" in package["preparation_violations"]


def test_generated_package_has_ready_for_dispatch_false() -> None:
    package = prepare_worker_package(_proposal(), _approval_gate())

    assert package["ready_for_dispatch"] is False


def test_generated_package_has_execution_authority_false() -> None:
    package = prepare_worker_package(_proposal(), _approval_gate())

    assert package["execution_authority"] is False
    assert package["governance_guarantees"]["execution_authority"] is False


def test_deterministic_worker_preparation_hash() -> None:
    first = prepare_worker_package(_proposal(), _approval_gate())
    second = prepare_worker_package(_proposal(), _approval_gate())

    assert first["worker_preparation_hash"] == second["worker_preparation_hash"]
    assert first == second


def test_cli_never_invokes_execution_or_provider(monkeypatch, tmp_path) -> None:
    def fail_execution(*args, **kwargs):  # pragma: no cover - should never be reached
        raise AssertionError("execution path invoked")

    def fail_provider(*args, **kwargs):  # pragma: no cover - should never be reached
        raise AssertionError("provider path invoked")

    monkeypatch.setattr("aigol.cli.aigol_cli.run_execution_handoff", fail_execution)
    monkeypatch.setattr("agol_bridge.providers.codex_cli_provider.run_bounded_codex_cli_task", fail_provider)
    proposal_path = tmp_path / "proposal.json"
    approval_gate_path = tmp_path / "approval_gate.json"
    _write_json(proposal_path, _proposal())
    _write_json(approval_gate_path, _approval_gate())

    parser = build_parser()
    args = parser.parse_args(
        [
            "moc",
            "prepare-worker",
            "--proposal",
            str(proposal_path),
            "--approval-gate",
            str(approval_gate_path),
            "--json",
        ]
    )
    result = run_command(args)

    package = result["worker_preparation_package"]
    assert package["preparation_status"] == PREPARED_FOR_WORKER
    assert result["provider_activation_added"] is False
    assert result["worker_dispatch_added"] is False


def test_no_governance_mutation_occurs(tmp_path) -> None:
    proposal_path = tmp_path / "proposal.json"
    approval_gate_path = tmp_path / "approval_gate.json"
    proposal = _proposal()
    approval_gate = _approval_gate()
    _write_json(proposal_path, proposal)
    _write_json(approval_gate_path, approval_gate)
    before_proposal = proposal_path.read_text(encoding="utf-8")
    before_gate = approval_gate_path.read_text(encoding="utf-8")

    result = inspect_worker_preparation(
        proposal_path=proposal_path,
        approval_gate_path=approval_gate_path,
    )

    assert proposal_path.read_text(encoding="utf-8") == before_proposal
    assert approval_gate_path.read_text(encoding="utf-8") == before_gate
    assert result["governance_mutation_added"] is False
    assert result["worker_preparation_package"]["governance_guarantees"]["governance_mutation"] is False


def test_no_hidden_continuation_occurs() -> None:
    package = prepare_worker_package(_proposal(), _approval_gate())

    assert package["worker_dispatch"] is False
    assert package["provider_activation"] is False
    assert package["governance_guarantees"]["hidden_continuation"] is False
    assert package["governance_guarantees"]["autonomous_continuation"] is False
