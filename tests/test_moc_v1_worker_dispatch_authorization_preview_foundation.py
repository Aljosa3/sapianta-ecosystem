"""Tests for MOC V1 worker dispatch authorization preview."""

from __future__ import annotations

import json

from aigol.cli.aigol_cli import build_parser, run_command
from aigol.moc.approval_gate import evaluate_approval_gate
from aigol.moc.dispatch_authorization_preview import (
    DISPATCH_PREVIEW_ELIGIBLE,
    DISPATCH_PREVIEW_REJECTED,
    FAIL_CLOSED,
    build_dispatch_authorization_preview,
    inspect_dispatch_authorization_preview,
)
from aigol.moc.proposal_ledger import build_proposal_ledger_entry
from aigol.moc.proposal_persistence import PROPOSED, VALIDATED, create_proposal_persistence_record
from aigol.moc.worker_preparation import prepare_worker_package


def _proposal() -> dict:
    return {
        "proposal_id": "proposal-dispatch-preview-001",
        "proposal_summary": "Preview dispatch eligibility without dispatch.",
        "linked_contract_id": "contract-dispatch-preview-001",
        "linked_contract_hash": "sha256:contract-dispatch-preview",
        "proposal_hash": "sha256:proposal-dispatch-preview",
        "suggested_actions": ["prepare_worker_task"],
        "allowed_actions": ["prepare_worker_task"],
        "forbidden_actions": ["execute_task", "dispatch_worker", "activate_provider"],
        "expected_outputs": ["MOC_V1_WORKER_DISPATCH_AUTHORIZATION_PREVIEW"],
        "bounded_scope": "dispatch preview only",
        "approvals_required": ["human_review"],
        "replay_safe": True,
        "advisory_only": True,
        "lineage_refs": [{"ref_type": "contract", "hash": "sha256:contract-dispatch-preview"}],
        "approval_refs": [{"ref_type": "human_review", "hash": "sha256:approval-dispatch-preview"}],
        "validation_refs": [{"ref_type": "proposal_validation", "hash": "sha256:validation-dispatch-preview"}],
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


def _worker_package() -> dict:
    return prepare_worker_package(_proposal(), _approval_gate())


def _write_json(path, value: dict) -> None:
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def test_valid_worker_package_creates_dispatch_preview_eligible() -> None:
    preview = build_dispatch_authorization_preview(_worker_package())

    assert preview["dispatch_preview_status"] == DISPATCH_PREVIEW_ELIGIBLE
    assert preview["dispatch_eligible_preview"] is True


def test_missing_worker_package_fails_closed() -> None:
    preview = build_dispatch_authorization_preview(None)

    assert preview["dispatch_preview_status"] == FAIL_CLOSED
    assert "worker package evidence missing" in preview["dispatch_preview_violations"]


def test_non_prepared_package_is_rejected() -> None:
    worker_package = _worker_package()
    worker_package["preparation_status"] = "NOT_APPROVED"

    preview = build_dispatch_authorization_preview(worker_package)

    assert preview["dispatch_preview_status"] == DISPATCH_PREVIEW_REJECTED
    assert "worker package is not PREPARED_FOR_WORKER" in preview["dispatch_preview_violations"]


def test_ready_for_dispatch_true_fails() -> None:
    worker_package = _worker_package()
    worker_package["ready_for_dispatch"] = True

    preview = build_dispatch_authorization_preview(worker_package)

    assert preview["dispatch_preview_status"] == DISPATCH_PREVIEW_REJECTED
    assert "ready_for_dispatch must remain false" in preview["dispatch_preview_violations"]


def test_dispatch_authority_true_fails() -> None:
    worker_package = _worker_package()
    worker_package["dispatch_authority"] = True

    preview = build_dispatch_authorization_preview(worker_package)

    assert preview["dispatch_preview_status"] == DISPATCH_PREVIEW_REJECTED
    assert "dispatch_authority must remain false" in preview["dispatch_preview_violations"]


def test_execution_authority_true_fails() -> None:
    worker_package = _worker_package()
    worker_package["execution_authority"] = True

    preview = build_dispatch_authorization_preview(worker_package)

    assert preview["dispatch_preview_status"] == DISPATCH_PREVIEW_REJECTED
    assert "execution_authority must remain false" in preview["dispatch_preview_violations"]


def test_provider_activation_true_fails() -> None:
    worker_package = _worker_package()
    worker_package["provider_activation"] = True

    preview = build_dispatch_authorization_preview(worker_package)

    assert preview["dispatch_preview_status"] == DISPATCH_PREVIEW_REJECTED
    assert "provider_activation must remain false" in preview["dispatch_preview_violations"]


def test_worker_dispatch_true_fails() -> None:
    worker_package = _worker_package()
    worker_package["worker_dispatch"] = True

    preview = build_dispatch_authorization_preview(worker_package)

    assert preview["dispatch_preview_status"] == DISPATCH_PREVIEW_REJECTED
    assert "worker_dispatch must remain false" in preview["dispatch_preview_violations"]


def test_missing_lineage_approval_or_replay_refs_fails() -> None:
    worker_package = _worker_package()
    worker_package["lineage_refs"] = []
    worker_package["approval_refs"] = []
    worker_package["replay_refs"] = []

    preview = build_dispatch_authorization_preview(worker_package)

    assert preview["dispatch_preview_status"] == DISPATCH_PREVIEW_REJECTED
    assert "lineage refs must exist" in preview["dispatch_preview_violations"]
    assert "approval refs must exist" in preview["dispatch_preview_violations"]
    assert "replay refs must exist" in preview["dispatch_preview_violations"]


def test_overlapping_allowed_and_forbidden_worker_actions_fails() -> None:
    worker_package = _worker_package()
    worker_package["forbidden_worker_actions"] = ["prepare_worker_task"]

    preview = build_dispatch_authorization_preview(worker_package)

    assert preview["dispatch_preview_status"] == DISPATCH_PREVIEW_REJECTED
    assert 'allowed and forbidden worker actions overlap: ["prepare_worker_task"]' in preview["dispatch_preview_violations"]


def test_deterministic_dispatch_preview_hash() -> None:
    first = build_dispatch_authorization_preview(_worker_package())
    second = build_dispatch_authorization_preview(_worker_package())

    assert first["dispatch_preview_hash"] == second["dispatch_preview_hash"]
    assert first == second


def test_cli_never_invokes_execution_or_provider(monkeypatch, tmp_path) -> None:
    def fail_execution(*args, **kwargs):  # pragma: no cover - should never be reached
        raise AssertionError("execution path invoked")

    def fail_provider(*args, **kwargs):  # pragma: no cover - should never be reached
        raise AssertionError("provider path invoked")

    monkeypatch.setattr("aigol.cli.aigol_cli.run_execution_handoff", fail_execution)
    monkeypatch.setattr("agol_bridge.providers.codex_cli_provider.run_bounded_codex_cli_task", fail_provider)
    worker_package_path = tmp_path / "worker_package.json"
    _write_json(worker_package_path, _worker_package())

    parser = build_parser()
    args = parser.parse_args(
        [
            "moc",
            "dispatch-preview",
            "--worker-package",
            str(worker_package_path),
            "--json",
        ]
    )
    result = run_command(args)

    preview = result["dispatch_authorization_preview"]
    assert preview["dispatch_preview_status"] == DISPATCH_PREVIEW_ELIGIBLE
    assert result["worker_dispatch_added"] is False
    assert result["provider_activation_added"] is False


def test_no_governance_mutation_occurs(tmp_path) -> None:
    worker_package_path = tmp_path / "worker_package.json"
    _write_json(worker_package_path, _worker_package())
    before = worker_package_path.read_text(encoding="utf-8")

    result = inspect_dispatch_authorization_preview(worker_package_path=worker_package_path)

    assert worker_package_path.read_text(encoding="utf-8") == before
    assert result["governance_mutation_added"] is False
    assert result["dispatch_authorization_preview"]["governance_guarantees"]["governance_mutation"] is False


def test_eligible_preview_still_has_all_authority_flags_false() -> None:
    preview = build_dispatch_authorization_preview(_worker_package())

    assert preview["dispatch_preview_status"] == DISPATCH_PREVIEW_ELIGIBLE
    assert preview["dispatch_authority"] is False
    assert preview["execution_authority"] is False
    assert preview["provider_activation"] is False
    assert preview["worker_dispatch"] is False
    assert preview["ready_for_actual_dispatch"] is False
    assert preview["governance_guarantees"]["actual_dispatch_authorization"] is False
