"""Tests for MOC V1 worker provider execution gate foundation."""

from __future__ import annotations

import json
import subprocess

from aigol.cli.aigol_cli import build_parser, run_command
from aigol.moc.approval_gate import evaluate_approval_gate
from aigol.moc.dispatch_authorization import authorize_worker_dispatch
from aigol.moc.dispatch_authorization_preview import build_dispatch_authorization_preview
from aigol.moc.dispatch_request import build_worker_dispatch_request
from aigol.moc.proposal_ledger import build_proposal_ledger_entry
from aigol.moc.proposal_persistence import PROPOSED, VALIDATED, create_proposal_persistence_record
from aigol.moc.provider_execution_gate import (
    FAIL_CLOSED,
    PROVIDER_EXECUTION_ELIGIBLE,
    PROVIDER_EXECUTION_REJECTED,
    evaluate_provider_execution_gate,
    inspect_provider_execution_gate,
)
from aigol.moc.runtime_dispatch import create_runtime_dispatch_event
from aigol.moc.worker_preparation import prepare_worker_package


def _proposal() -> dict:
    return {
        "proposal_id": "proposal-provider-gate-001",
        "proposal_summary": "Evaluate future provider execution eligibility without provider execution.",
        "linked_contract_id": "contract-provider-gate-001",
        "linked_contract_hash": "sha256:contract-provider-gate",
        "proposal_hash": "sha256:proposal-provider-gate",
        "suggested_actions": ["prepare_worker_task"],
        "allowed_actions": ["prepare_worker_task"],
        "forbidden_actions": ["execute_task", "activate_provider", "call_external_api", "run_shell_command"],
        "expected_outputs": ["MOC_V1_WORKER_PROVIDER_EXECUTION_GATE"],
        "bounded_scope": "provider execution eligibility gate only",
        "approvals_required": ["human_review"],
        "replay_safe": True,
        "advisory_only": True,
        "lineage_refs": [{"ref_type": "contract", "hash": "sha256:contract-provider-gate"}],
        "approval_refs": [{"ref_type": "human_review", "hash": "sha256:approval-provider-gate"}],
        "validation_refs": [{"ref_type": "proposal_validation", "hash": "sha256:validation-provider-gate"}],
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
        "request_statement": "Request provider execution eligibility gating only.",
        "explicit_non_authorization": True,
        "replay_safe": True,
        "advisory_only": True,
    }


def _dispatch_request() -> dict:
    return build_worker_dispatch_request(_eligible_preview(), _request_evidence())


def _dispatch_authorization() -> dict:
    return authorize_worker_dispatch(_dispatch_request())


def _runtime_dispatch() -> dict:
    return create_runtime_dispatch_event(_dispatch_authorization())


def _write_json(path, value: dict) -> None:
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def test_valid_runtime_dispatch_creates_provider_execution_eligible() -> None:
    gate = evaluate_provider_execution_gate(_runtime_dispatch())

    assert gate["provider_gate_status"] == PROVIDER_EXECUTION_ELIGIBLE
    assert gate["provider_execution_eligible"] is True


def test_missing_runtime_dispatch_fails_closed() -> None:
    gate = evaluate_provider_execution_gate(None)

    assert gate["provider_gate_status"] == FAIL_CLOSED
    assert "runtime dispatch evidence missing" in gate["provider_gate_violations"]


def test_invalid_runtime_dispatch_is_rejected() -> None:
    runtime_dispatch = _runtime_dispatch()
    runtime_dispatch["runtime_dispatch_status"] = "RUNTIME_DISPATCH_REJECTED"

    gate = evaluate_provider_execution_gate(runtime_dispatch)

    assert gate["provider_gate_status"] == PROVIDER_EXECUTION_REJECTED
    assert "runtime dispatch status is not RUNTIME_DISPATCH_PERFORMED" in gate["provider_gate_violations"]


def test_provider_activation_performed_true_fails() -> None:
    runtime_dispatch = _runtime_dispatch()
    runtime_dispatch["provider_activation_performed"] = True

    gate = evaluate_provider_execution_gate(runtime_dispatch)

    assert gate["provider_gate_status"] == FAIL_CLOSED
    assert "provider_activation_performed must remain false" in gate["provider_gate_violations"]


def test_execution_completed_true_fails() -> None:
    runtime_dispatch = _runtime_dispatch()
    runtime_dispatch["execution_completed"] = True

    gate = evaluate_provider_execution_gate(runtime_dispatch)

    assert gate["provider_gate_status"] == FAIL_CLOSED
    assert "execution_completed must remain false" in gate["provider_gate_violations"]


def test_execution_result_present_true_fails() -> None:
    runtime_dispatch = _runtime_dispatch()
    runtime_dispatch["execution_result_present"] = True

    gate = evaluate_provider_execution_gate(runtime_dispatch)

    assert gate["provider_gate_status"] == FAIL_CLOSED
    assert "execution_result_present must remain false" in gate["provider_gate_violations"]


def test_automatic_retry_true_fails() -> None:
    runtime_dispatch = _runtime_dispatch()
    runtime_dispatch["dispatch_events"][0]["automatic_retry"] = True

    gate = evaluate_provider_execution_gate(runtime_dispatch)

    assert gate["provider_gate_status"] == FAIL_CLOSED
    assert "automatic_retry must remain false" in gate["provider_gate_violations"]


def test_recursive_dispatch_true_fails() -> None:
    runtime_dispatch = _runtime_dispatch()
    runtime_dispatch["dispatch_events"][0]["recursive_dispatch"] = True

    gate = evaluate_provider_execution_gate(runtime_dispatch)

    assert gate["provider_gate_status"] == FAIL_CLOSED
    assert "recursive_dispatch must remain false" in gate["provider_gate_violations"]


def test_missing_lineage_approval_replay_refs_fails() -> None:
    runtime_dispatch = _runtime_dispatch()
    runtime_dispatch["lineage_refs"] = []
    runtime_dispatch["approval_refs"] = []
    runtime_dispatch["replay_refs"] = []

    gate = evaluate_provider_execution_gate(runtime_dispatch)

    assert gate["provider_gate_status"] == FAIL_CLOSED
    assert "lineage refs must exist" in gate["provider_gate_violations"]
    assert "approval refs must exist" in gate["provider_gate_violations"]
    assert "replay refs must exist" in gate["provider_gate_violations"]


def test_deterministic_provider_gate_hash() -> None:
    first = evaluate_provider_execution_gate(_runtime_dispatch())
    second = evaluate_provider_execution_gate(_runtime_dispatch())

    assert first["provider_gate_hash"] == second["provider_gate_hash"]
    assert first == second


def test_cli_never_invokes_external_provider_api_or_shell(monkeypatch, tmp_path) -> None:
    def fail_execution(*args, **kwargs):  # pragma: no cover - should never be reached
        raise AssertionError("execution path invoked")

    def fail_provider(*args, **kwargs):  # pragma: no cover - should never be reached
        raise AssertionError("provider path invoked")

    def fail_shell(*args, **kwargs):  # pragma: no cover - should never be reached
        raise AssertionError("shell path invoked")

    monkeypatch.setattr("aigol.cli.aigol_cli.run_execution_handoff", fail_execution)
    monkeypatch.setattr("agol_bridge.providers.codex_cli_provider.run_bounded_codex_cli_task", fail_provider)
    monkeypatch.setattr(subprocess, "run", fail_shell)
    runtime_dispatch_path = tmp_path / "runtime_dispatch.json"
    _write_json(runtime_dispatch_path, _runtime_dispatch())

    parser = build_parser()
    args = parser.parse_args(
        [
            "moc",
            "provider-execution-gate",
            "--runtime-dispatch",
            str(runtime_dispatch_path),
            "--json",
        ]
    )
    result = run_command(args)

    gate = result["provider_execution_gate"]
    assert gate["provider_gate_status"] == PROVIDER_EXECUTION_ELIGIBLE
    assert result["external_api_called"] is False
    assert result["shell_command_executed"] is False
    assert result["provider_execution_performed"] is False


def test_no_governance_mutation_occurs(tmp_path) -> None:
    runtime_dispatch_path = tmp_path / "runtime_dispatch.json"
    _write_json(runtime_dispatch_path, _runtime_dispatch())
    before_runtime_dispatch = runtime_dispatch_path.read_text(encoding="utf-8")

    result = inspect_provider_execution_gate(runtime_dispatch_path=runtime_dispatch_path)

    assert runtime_dispatch_path.read_text(encoding="utf-8") == before_runtime_dispatch
    assert result["governance_mutation_added"] is False
    assert result["provider_execution_gate"]["governance_guarantees"]["governance_mutation"] is False


def test_eligible_gate_still_has_provider_activation_false() -> None:
    gate = evaluate_provider_execution_gate(_runtime_dispatch())

    assert gate["provider_gate_status"] == PROVIDER_EXECUTION_ELIGIBLE
    assert gate["provider_activation"] is False
    assert gate["governance_guarantees"]["provider_activation"] is False


def test_eligible_gate_still_has_provider_execution_performed_false() -> None:
    gate = evaluate_provider_execution_gate(_runtime_dispatch())

    assert gate["provider_gate_status"] == PROVIDER_EXECUTION_ELIGIBLE
    assert gate["provider_execution_performed"] is False
    assert gate["governance_guarantees"]["provider_execution_performed"] is False
