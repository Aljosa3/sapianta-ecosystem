"""Tests for MOC V1 worker dispatch request foundation."""

from __future__ import annotations

import json

from aigol.cli.aigol_cli import build_parser, run_command
from aigol.moc.approval_gate import evaluate_approval_gate
from aigol.moc.dispatch_authorization_preview import build_dispatch_authorization_preview
from aigol.moc.dispatch_request import (
    DISPATCH_REQUEST_CREATED,
    DISPATCH_REQUEST_REJECTED,
    FAIL_CLOSED,
    build_worker_dispatch_request,
    inspect_worker_dispatch_request,
)
from aigol.moc.proposal_ledger import build_proposal_ledger_entry
from aigol.moc.proposal_persistence import PROPOSED, VALIDATED, create_proposal_persistence_record
from aigol.moc.worker_preparation import prepare_worker_package


def _proposal() -> dict:
    return {
        "proposal_id": "proposal-dispatch-request-001",
        "proposal_summary": "Request consideration of future dispatch authorization without dispatch.",
        "linked_contract_id": "contract-dispatch-request-001",
        "linked_contract_hash": "sha256:contract-dispatch-request",
        "proposal_hash": "sha256:proposal-dispatch-request",
        "suggested_actions": ["prepare_worker_task"],
        "allowed_actions": ["prepare_worker_task"],
        "forbidden_actions": ["execute_task", "dispatch_worker", "activate_provider"],
        "expected_outputs": ["MOC_V1_WORKER_DISPATCH_REQUEST"],
        "bounded_scope": "dispatch request evidence only",
        "approvals_required": ["human_review"],
        "replay_safe": True,
        "advisory_only": True,
        "lineage_refs": [{"ref_type": "contract", "hash": "sha256:contract-dispatch-request"}],
        "approval_refs": [{"ref_type": "human_review", "hash": "sha256:approval-dispatch-request"}],
        "validation_refs": [{"ref_type": "proposal_validation", "hash": "sha256:validation-dispatch-request"}],
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


def _eligible_preview() -> dict:
    return build_dispatch_authorization_preview(_worker_package())


def _request_evidence() -> dict:
    return {
        "requester_type": "human_or_governance",
        "request_scope": "dispatch may be considered by a future authorization layer",
        "request_statement": "Request consideration only; do not dispatch or authorize dispatch.",
        "explicit_non_authorization": True,
    }


def _write_json(path, value: dict) -> None:
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def test_eligible_preview_creates_dispatch_request_created() -> None:
    request = build_worker_dispatch_request(_eligible_preview(), _request_evidence())

    assert request["dispatch_request_status"] == DISPATCH_REQUEST_CREATED
    assert request["artifact_type"] == "MOC_V1_WORKER_DISPATCH_REQUEST"
    assert request["requester_type"] == "human_or_governance"


def test_missing_preview_fails_closed() -> None:
    request = build_worker_dispatch_request(None, _request_evidence())

    assert request["dispatch_request_status"] == FAIL_CLOSED
    assert "dispatch preview evidence missing" in request["request_violations"]


def test_non_eligible_preview_is_rejected() -> None:
    preview = _eligible_preview()
    preview["dispatch_preview_status"] = "DISPATCH_PREVIEW_REJECTED"

    request = build_worker_dispatch_request(preview, _request_evidence())

    assert request["dispatch_request_status"] == DISPATCH_REQUEST_REJECTED
    assert "dispatch preview is not DISPATCH_PREVIEW_ELIGIBLE" in request["request_violations"]


def test_missing_request_evidence_fails_closed() -> None:
    request = build_worker_dispatch_request(_eligible_preview(), None)

    assert request["dispatch_request_status"] == FAIL_CLOSED
    assert "request evidence missing" in request["request_violations"]


def test_missing_lineage_approval_replay_refs_fails_closed() -> None:
    preview = _eligible_preview()
    preview["lineage_refs"] = []
    preview["approval_refs"] = []
    preview["replay_refs"] = []

    request = build_worker_dispatch_request(preview, _request_evidence())

    assert request["dispatch_request_status"] == FAIL_CLOSED
    assert "lineage refs must exist" in request["request_violations"]
    assert "approval refs must exist" in request["request_violations"]
    assert "replay refs must exist" in request["request_violations"]


def test_dispatch_authority_remains_false() -> None:
    request = build_worker_dispatch_request(_eligible_preview(), _request_evidence())

    assert request["dispatch_authority"] is False
    assert request["governance_guarantees"]["dispatch_authority"] is False


def test_execution_authority_remains_false() -> None:
    request = build_worker_dispatch_request(_eligible_preview(), _request_evidence())

    assert request["execution_authority"] is False
    assert request["governance_guarantees"]["execution_authority"] is False


def test_provider_activation_remains_false() -> None:
    request = build_worker_dispatch_request(_eligible_preview(), _request_evidence())

    assert request["provider_activation"] is False
    assert request["governance_guarantees"]["provider_activation"] is False


def test_worker_dispatch_remains_false() -> None:
    request = build_worker_dispatch_request(_eligible_preview(), _request_evidence())

    assert request["worker_dispatch"] is False
    assert request["governance_guarantees"]["worker_dispatch"] is False


def test_deterministic_dispatch_request_hash() -> None:
    first = build_worker_dispatch_request(_eligible_preview(), _request_evidence())
    second = build_worker_dispatch_request(_eligible_preview(), _request_evidence())

    assert first["dispatch_request_hash"] == second["dispatch_request_hash"]
    assert first == second


def test_cli_never_invokes_execution_or_provider(monkeypatch, tmp_path) -> None:
    def fail_execution(*args, **kwargs):  # pragma: no cover - should never be reached
        raise AssertionError("execution path invoked")

    def fail_provider(*args, **kwargs):  # pragma: no cover - should never be reached
        raise AssertionError("provider path invoked")

    monkeypatch.setattr("aigol.cli.aigol_cli.run_execution_handoff", fail_execution)
    monkeypatch.setattr("agol_bridge.providers.codex_cli_provider.run_bounded_codex_cli_task", fail_provider)
    preview_path = tmp_path / "dispatch_preview.json"
    request_evidence_path = tmp_path / "request_evidence.json"
    _write_json(preview_path, _eligible_preview())
    _write_json(request_evidence_path, _request_evidence())

    parser = build_parser()
    args = parser.parse_args(
        [
            "moc",
            "dispatch-request",
            "--dispatch-preview",
            str(preview_path),
            "--request-evidence",
            str(request_evidence_path),
            "--json",
        ]
    )
    result = run_command(args)

    request = result["worker_dispatch_request"]
    assert request["dispatch_request_status"] == DISPATCH_REQUEST_CREATED
    assert result["worker_dispatch_added"] is False
    assert result["provider_activation_added"] is False
    assert result["execution_authority_added"] is False


def test_no_governance_mutation_occurs(tmp_path) -> None:
    preview_path = tmp_path / "dispatch_preview.json"
    request_evidence_path = tmp_path / "request_evidence.json"
    _write_json(preview_path, _eligible_preview())
    _write_json(request_evidence_path, _request_evidence())
    before_preview = preview_path.read_text(encoding="utf-8")
    before_evidence = request_evidence_path.read_text(encoding="utf-8")

    result = inspect_worker_dispatch_request(
        dispatch_preview_path=preview_path,
        request_evidence_path=request_evidence_path,
    )

    assert preview_path.read_text(encoding="utf-8") == before_preview
    assert request_evidence_path.read_text(encoding="utf-8") == before_evidence
    assert result["governance_mutation_added"] is False
    assert result["worker_dispatch_request"]["governance_guarantees"]["governance_mutation"] is False


def test_request_does_not_imply_authorization() -> None:
    request = build_worker_dispatch_request(_eligible_preview(), _request_evidence())

    assert request["dispatch_request_status"] == DISPATCH_REQUEST_CREATED
    assert request["ready_for_actual_dispatch"] is False
    assert request["dispatch_authority"] is False
    assert request["execution_authority"] is False
    assert request["provider_activation"] is False
    assert request["worker_dispatch"] is False
