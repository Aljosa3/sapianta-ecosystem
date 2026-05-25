"""Tests for MOC V1 worker dispatch authorization foundation."""

from __future__ import annotations

import json

from aigol.cli.aigol_cli import build_parser, run_command
from aigol.moc.approval_gate import evaluate_approval_gate
from aigol.moc.dispatch_authorization import (
    DISPATCH_AUTHORIZED,
    DISPATCH_AUTHORIZATION_REJECTED,
    FAIL_CLOSED,
    authorize_worker_dispatch,
    inspect_worker_dispatch_authorization,
)
from aigol.moc.dispatch_authorization_preview import build_dispatch_authorization_preview
from aigol.moc.dispatch_request import build_worker_dispatch_request
from aigol.moc.proposal_ledger import build_proposal_ledger_entry
from aigol.moc.proposal_persistence import PROPOSED, VALIDATED, create_proposal_persistence_record
from aigol.moc.worker_preparation import prepare_worker_package


def _proposal() -> dict:
    return {
        "proposal_id": "proposal-dispatch-authorization-001",
        "proposal_summary": "Authorize future dispatch eligibility without runtime execution.",
        "linked_contract_id": "contract-dispatch-authorization-001",
        "linked_contract_hash": "sha256:contract-dispatch-authorization",
        "proposal_hash": "sha256:proposal-dispatch-authorization",
        "suggested_actions": ["prepare_worker_task"],
        "allowed_actions": ["prepare_worker_task"],
        "forbidden_actions": ["execute_task", "dispatch_worker", "activate_provider"],
        "expected_outputs": ["MOC_V1_WORKER_DISPATCH_AUTHORIZATION"],
        "bounded_scope": "future runtime dispatch eligibility only",
        "approvals_required": ["human_review"],
        "replay_safe": True,
        "advisory_only": True,
        "lineage_refs": [{"ref_type": "contract", "hash": "sha256:contract-dispatch-authorization"}],
        "approval_refs": [{"ref_type": "human_review", "hash": "sha256:approval-dispatch-authorization"}],
        "validation_refs": [{"ref_type": "proposal_validation", "hash": "sha256:validation-dispatch-authorization"}],
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
        "request_statement": "Request consideration only; runtime execution remains forbidden.",
        "explicit_non_authorization": True,
        "replay_safe": True,
        "advisory_only": True,
    }


def _dispatch_request() -> dict:
    return build_worker_dispatch_request(_eligible_preview(), _request_evidence())


def _write_json(path, value: dict) -> None:
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def test_valid_dispatch_request_creates_dispatch_authorized() -> None:
    authorization = authorize_worker_dispatch(_dispatch_request())

    assert authorization["dispatch_authorization_status"] == DISPATCH_AUTHORIZED
    assert authorization["dispatch_authorized"] is True
    assert authorization["authorization_scope"] == "future_runtime_dispatch_only"


def test_missing_request_fails_closed() -> None:
    authorization = authorize_worker_dispatch(None)

    assert authorization["dispatch_authorization_status"] == FAIL_CLOSED
    assert "dispatch request evidence missing" in authorization["authorization_violations"]


def test_invalid_request_is_rejected() -> None:
    request = _dispatch_request()
    request["dispatch_request_status"] = "DISPATCH_REQUEST_REJECTED"

    authorization = authorize_worker_dispatch(request)

    assert authorization["dispatch_authorization_status"] == DISPATCH_AUTHORIZATION_REJECTED
    assert "dispatch request status is not DISPATCH_REQUEST_CREATED" in authorization["authorization_violations"]


def test_dispatch_authority_true_in_request_fails() -> None:
    request = _dispatch_request()
    request["dispatch_authority"] = True

    authorization = authorize_worker_dispatch(request)

    assert authorization["dispatch_authorization_status"] == FAIL_CLOSED
    assert "dispatch_authority must remain false" in authorization["authorization_violations"]


def test_execution_authority_true_in_request_fails() -> None:
    request = _dispatch_request()
    request["execution_authority"] = True

    authorization = authorize_worker_dispatch(request)

    assert authorization["dispatch_authorization_status"] == FAIL_CLOSED
    assert "execution_authority must remain false" in authorization["authorization_violations"]


def test_provider_activation_true_in_request_fails() -> None:
    request = _dispatch_request()
    request["provider_activation"] = True

    authorization = authorize_worker_dispatch(request)

    assert authorization["dispatch_authorization_status"] == FAIL_CLOSED
    assert "provider_activation must remain false" in authorization["authorization_violations"]


def test_worker_dispatch_true_in_request_fails() -> None:
    request = _dispatch_request()
    request["worker_dispatch"] = True

    authorization = authorize_worker_dispatch(request)

    assert authorization["dispatch_authorization_status"] == FAIL_CLOSED
    assert "worker_dispatch must remain false" in authorization["authorization_violations"]


def test_missing_lineage_approval_replay_refs_fails() -> None:
    request = _dispatch_request()
    request["lineage_refs"] = []
    request["approval_refs"] = []
    request["replay_refs"] = []

    authorization = authorize_worker_dispatch(request)

    assert authorization["dispatch_authorization_status"] == FAIL_CLOSED
    assert "lineage refs must exist" in authorization["authorization_violations"]
    assert "approval refs must exist" in authorization["authorization_violations"]
    assert "replay refs must exist" in authorization["authorization_violations"]


def test_deterministic_dispatch_authorization_hash() -> None:
    first = authorize_worker_dispatch(_dispatch_request())
    second = authorize_worker_dispatch(_dispatch_request())

    assert first["dispatch_authorization_hash"] == second["dispatch_authorization_hash"]
    assert first == second


def test_cli_never_invokes_execution_or_provider(monkeypatch, tmp_path) -> None:
    def fail_execution(*args, **kwargs):  # pragma: no cover - should never be reached
        raise AssertionError("execution path invoked")

    def fail_provider(*args, **kwargs):  # pragma: no cover - should never be reached
        raise AssertionError("provider path invoked")

    monkeypatch.setattr("aigol.cli.aigol_cli.run_execution_handoff", fail_execution)
    monkeypatch.setattr("agol_bridge.providers.codex_cli_provider.run_bounded_codex_cli_task", fail_provider)
    request_path = tmp_path / "dispatch_request.json"
    _write_json(request_path, _dispatch_request())

    parser = build_parser()
    args = parser.parse_args(
        [
            "moc",
            "dispatch-authorize",
            "--dispatch-request",
            str(request_path),
            "--json",
        ]
    )
    result = run_command(args)

    authorization = result["worker_dispatch_authorization"]
    assert authorization["dispatch_authorization_status"] == DISPATCH_AUTHORIZED
    assert result["worker_dispatch_performed"] is False
    assert result["provider_activation_added"] is False
    assert result["runtime_execution_added"] is False


def test_no_governance_mutation_occurs(tmp_path) -> None:
    request_path = tmp_path / "dispatch_request.json"
    _write_json(request_path, _dispatch_request())
    before_request = request_path.read_text(encoding="utf-8")

    result = inspect_worker_dispatch_authorization(dispatch_request_path=request_path)

    assert request_path.read_text(encoding="utf-8") == before_request
    assert result["governance_mutation_added"] is False
    assert result["worker_dispatch_authorization"]["governance_guarantees"]["governance_mutation"] is False


def test_dispatch_authorized_still_has_runtime_execution_false() -> None:
    authorization = authorize_worker_dispatch(_dispatch_request())

    assert authorization["dispatch_authorization_status"] == DISPATCH_AUTHORIZED
    assert authorization["runtime_execution"] is False
    assert authorization["governance_guarantees"]["runtime_execution"] is False


def test_dispatch_authorized_still_has_worker_dispatch_performed_false() -> None:
    authorization = authorize_worker_dispatch(_dispatch_request())

    assert authorization["dispatch_authorization_status"] == DISPATCH_AUTHORIZED
    assert authorization["worker_dispatch_performed"] is False
    assert authorization["governance_guarantees"]["worker_dispatch_performed"] is False
