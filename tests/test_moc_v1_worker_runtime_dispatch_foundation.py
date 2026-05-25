"""Tests for MOC V1 worker runtime dispatch foundation."""

from __future__ import annotations

import json

from aigol.cli.aigol_cli import build_parser, run_command
from aigol.moc.approval_gate import evaluate_approval_gate
from aigol.moc.dispatch_authorization import authorize_worker_dispatch
from aigol.moc.dispatch_authorization_preview import build_dispatch_authorization_preview
from aigol.moc.dispatch_request import build_worker_dispatch_request
from aigol.moc.proposal_ledger import build_proposal_ledger_entry
from aigol.moc.proposal_persistence import PROPOSED, VALIDATED, create_proposal_persistence_record
from aigol.moc.runtime_dispatch import (
    FAIL_CLOSED,
    RUNTIME_DISPATCH_PERFORMED,
    RUNTIME_DISPATCH_REJECTED,
    create_runtime_dispatch_event,
    inspect_runtime_dispatch,
)
from aigol.moc.worker_preparation import prepare_worker_package


def _proposal() -> dict:
    return {
        "proposal_id": "proposal-runtime-dispatch-001",
        "proposal_summary": "Record bounded runtime dispatch without provider execution.",
        "linked_contract_id": "contract-runtime-dispatch-001",
        "linked_contract_hash": "sha256:contract-runtime-dispatch",
        "proposal_hash": "sha256:proposal-runtime-dispatch",
        "suggested_actions": ["prepare_worker_task"],
        "allowed_actions": ["prepare_worker_task"],
        "forbidden_actions": ["execute_task", "activate_provider", "recursive_dispatch"],
        "expected_outputs": ["MOC_V1_RUNTIME_DISPATCH_EVENT"],
        "bounded_scope": "bounded single runtime dispatch event only",
        "approvals_required": ["human_review"],
        "replay_safe": True,
        "advisory_only": True,
        "lineage_refs": [{"ref_type": "contract", "hash": "sha256:contract-runtime-dispatch"}],
        "approval_refs": [{"ref_type": "human_review", "hash": "sha256:approval-runtime-dispatch"}],
        "validation_refs": [{"ref_type": "proposal_validation", "hash": "sha256:validation-runtime-dispatch"}],
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
        "request_statement": "Request bounded runtime dispatch recording only.",
        "explicit_non_authorization": True,
        "replay_safe": True,
        "advisory_only": True,
    }


def _dispatch_request() -> dict:
    return build_worker_dispatch_request(_eligible_preview(), _request_evidence())


def _dispatch_authorization() -> dict:
    return authorize_worker_dispatch(_dispatch_request())


def _write_json(path, value: dict) -> None:
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def test_valid_dispatch_authorization_creates_runtime_dispatch_performed() -> None:
    dispatch_event = create_runtime_dispatch_event(_dispatch_authorization())

    assert dispatch_event["runtime_dispatch_status"] == RUNTIME_DISPATCH_PERFORMED
    assert dispatch_event["runtime_dispatch_performed"] is True
    assert dispatch_event["runtime_execution_scope"] == "bounded_single_dispatch"


def test_missing_authorization_fails_closed() -> None:
    dispatch_event = create_runtime_dispatch_event(None)

    assert dispatch_event["runtime_dispatch_status"] == FAIL_CLOSED
    assert "dispatch authorization evidence missing" in dispatch_event["runtime_violations"]


def test_invalid_authorization_rejected() -> None:
    authorization = _dispatch_authorization()
    authorization["dispatch_authorization_status"] = "DISPATCH_AUTHORIZATION_REJECTED"

    dispatch_event = create_runtime_dispatch_event(authorization)

    assert dispatch_event["runtime_dispatch_status"] == RUNTIME_DISPATCH_REJECTED
    assert "dispatch authorization status is not DISPATCH_AUTHORIZED" in dispatch_event["runtime_violations"]


def test_provider_activation_remains_false() -> None:
    dispatch_event = create_runtime_dispatch_event(_dispatch_authorization())

    assert dispatch_event["provider_activation_performed"] is False
    assert dispatch_event["governance_guarantees"]["provider_activation_performed"] is False


def test_execution_completed_remains_false() -> None:
    dispatch_event = create_runtime_dispatch_event(_dispatch_authorization())

    assert dispatch_event["execution_completed"] is False
    assert dispatch_event["execution_result_present"] is False
    assert dispatch_event["governance_guarantees"]["execution_completed"] is False


def test_no_recursive_dispatch() -> None:
    dispatch_event = create_runtime_dispatch_event(_dispatch_authorization())

    assert dispatch_event["dispatch_events"][0]["recursive_dispatch"] is False
    assert dispatch_event["governance_guarantees"]["single_dispatch_only"] is True


def test_no_automatic_retry() -> None:
    dispatch_event = create_runtime_dispatch_event(_dispatch_authorization())

    assert dispatch_event["dispatch_events"][0]["automatic_retry"] is False
    assert dispatch_event["governance_guarantees"]["automatic_retry"] is False


def test_lineage_replay_approval_refs_required() -> None:
    authorization = _dispatch_authorization()
    authorization["lineage_refs"] = []
    authorization["approval_refs"] = []
    authorization["replay_refs"] = []

    dispatch_event = create_runtime_dispatch_event(authorization)

    assert dispatch_event["runtime_dispatch_status"] == FAIL_CLOSED
    assert "lineage refs must exist" in dispatch_event["runtime_violations"]
    assert "approval refs must exist" in dispatch_event["runtime_violations"]
    assert "replay refs must exist" in dispatch_event["runtime_violations"]


def test_deterministic_runtime_dispatch_hash() -> None:
    first = create_runtime_dispatch_event(_dispatch_authorization())
    second = create_runtime_dispatch_event(_dispatch_authorization())

    assert first["runtime_dispatch_hash"] == second["runtime_dispatch_hash"]
    assert first == second


def test_cli_never_activates_external_providers(monkeypatch, tmp_path) -> None:
    def fail_execution(*args, **kwargs):  # pragma: no cover - should never be reached
        raise AssertionError("execution path invoked")

    def fail_provider(*args, **kwargs):  # pragma: no cover - should never be reached
        raise AssertionError("provider path invoked")

    monkeypatch.setattr("aigol.cli.aigol_cli.run_execution_handoff", fail_execution)
    monkeypatch.setattr("agol_bridge.providers.codex_cli_provider.run_bounded_codex_cli_task", fail_provider)
    authorization_path = tmp_path / "dispatch_authorization.json"
    _write_json(authorization_path, _dispatch_authorization())

    parser = build_parser()
    args = parser.parse_args(
        [
            "moc",
            "runtime-dispatch",
            "--dispatch-authorization",
            str(authorization_path),
            "--json",
        ]
    )
    result = run_command(args)

    dispatch_event = result["runtime_dispatch_event"]
    assert dispatch_event["runtime_dispatch_status"] == RUNTIME_DISPATCH_PERFORMED
    assert result["external_provider_activation_added"] is False
    assert result["execution_completed"] is False
    assert result["automatic_retry_added"] is False


def test_no_governance_mutation_occurs(tmp_path) -> None:
    authorization_path = tmp_path / "dispatch_authorization.json"
    _write_json(authorization_path, _dispatch_authorization())
    before_authorization = authorization_path.read_text(encoding="utf-8")

    result = inspect_runtime_dispatch(dispatch_authorization_path=authorization_path)

    assert authorization_path.read_text(encoding="utf-8") == before_authorization
    assert result["governance_mutation_added"] is False
    assert result["runtime_dispatch_event"]["governance_guarantees"]["governance_mutation"] is False


def test_runtime_dispatch_remains_bounded() -> None:
    dispatch_event = create_runtime_dispatch_event(_dispatch_authorization())

    assert dispatch_event["runtime_execution_scope"] == "bounded_single_dispatch"
    assert dispatch_event["governance_guarantees"]["bounded_runtime_dispatch"] is True
    assert dispatch_event["governance_guarantees"]["single_dispatch_only"] is True
    assert len(dispatch_event["dispatch_events"]) == 1
