"""Tests for MOC V1 governed return interpretation foundation."""

from __future__ import annotations

import json

from aigol.cli.aigol_cli import build_parser, run_command
from aigol.moc.approval_gate import evaluate_approval_gate
from aigol.moc.dispatch_authorization import authorize_worker_dispatch
from aigol.moc.dispatch_authorization_preview import build_dispatch_authorization_preview
from aigol.moc.dispatch_request import build_worker_dispatch_request
from aigol.moc.governed_return_interpretation import (
    DISPATCH_RECORDED_ONLY,
    EXECUTION_NOT_PERFORMED,
    FAIL_CLOSED,
    PROVIDER_GATE_ELIGIBLE_ONLY,
    inspect_governed_return_interpretation,
    interpret_governed_return,
)
from aigol.moc.proposal_ledger import build_proposal_ledger_entry
from aigol.moc.proposal_persistence import PROPOSED, VALIDATED, create_proposal_persistence_record
from aigol.moc.provider_execution_gate import evaluate_provider_execution_gate
from aigol.moc.runtime_dispatch import create_runtime_dispatch_event
from aigol.moc.worker_preparation import prepare_worker_package


def _proposal() -> dict:
    return {
        "proposal_id": "proposal-return-interpretation-001",
        "proposal_summary": "Interpret governed return evidence without execution or repair.",
        "linked_contract_id": "contract-return-interpretation-001",
        "linked_contract_hash": "sha256:contract-return-interpretation",
        "proposal_hash": "sha256:proposal-return-interpretation",
        "suggested_actions": ["prepare_worker_task"],
        "allowed_actions": ["prepare_worker_task"],
        "forbidden_actions": ["execute_task", "retry_task", "repair_result", "generate_next_task"],
        "expected_outputs": ["MOC_V1_GOVERNED_RETURN_INTERPRETATION"],
        "bounded_scope": "governed return interpretation only",
        "approvals_required": ["human_review"],
        "replay_safe": True,
        "advisory_only": True,
        "lineage_refs": [{"ref_type": "contract", "hash": "sha256:contract-return-interpretation"}],
        "approval_refs": [{"ref_type": "human_review", "hash": "sha256:approval-return-interpretation"}],
        "validation_refs": [{"ref_type": "proposal_validation", "hash": "sha256:validation-return-interpretation"}],
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
        "request_statement": "Request governed return interpretation only.",
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


def _provider_gate() -> dict:
    return evaluate_provider_execution_gate(_runtime_dispatch())


def _return_evidence(**overrides) -> dict:
    evidence = {
        "execution_completed": False,
        "result_present": False,
        "provider_execution_performed": False,
        "automatic_retry": False,
        "automatic_next_task": False,
        "result_repaired": False,
    }
    evidence.update(overrides)
    return evidence


def _write_json(path, value: dict) -> None:
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def test_runtime_dispatch_only_creates_dispatch_recorded_only() -> None:
    interpretation = interpret_governed_return(_runtime_dispatch())

    assert interpretation["outcome_classification"] == DISPATCH_RECORDED_ONLY
    assert interpretation["required_human_review"] is True


def test_provider_gate_only_creates_provider_gate_eligible_only() -> None:
    interpretation = interpret_governed_return(_runtime_dispatch(), _provider_gate())

    assert interpretation["outcome_classification"] == PROVIDER_GATE_ELIGIBLE_ONLY
    assert interpretation["provider_gate_hash"] == _provider_gate()["provider_gate_hash"]


def test_execution_completed_false_creates_execution_not_performed() -> None:
    interpretation = interpret_governed_return(_runtime_dispatch(), _provider_gate(), _return_evidence())

    assert interpretation["outcome_classification"] == EXECUTION_NOT_PERFORMED
    assert interpretation["execution_completed"] is False
    assert interpretation["result_present"] is False


def test_missing_runtime_dispatch_fails_closed() -> None:
    interpretation = interpret_governed_return(None)

    assert interpretation["interpretation_status"] == FAIL_CLOSED
    assert "runtime dispatch evidence missing" in interpretation["interpretation_violations"]


def test_missing_lineage_replay_refs_fail_closed() -> None:
    runtime_dispatch = _runtime_dispatch()
    runtime_dispatch["lineage_refs"] = []
    runtime_dispatch["replay_refs"] = []

    interpretation = interpret_governed_return(runtime_dispatch)

    assert interpretation["interpretation_status"] == FAIL_CLOSED
    assert "lineage refs must exist" in interpretation["interpretation_violations"]
    assert "replay refs must exist" in interpretation["interpretation_violations"]


def test_required_human_review_remains_true() -> None:
    interpretation = interpret_governed_return(_runtime_dispatch(), _provider_gate(), _return_evidence())

    assert interpretation["required_human_review"] is True


def test_no_automatic_retry() -> None:
    interpretation = interpret_governed_return(_runtime_dispatch(), _provider_gate(), _return_evidence())

    assert interpretation["governance_guarantees"]["automatic_retry"] is False


def test_no_automatic_next_task() -> None:
    interpretation = interpret_governed_return(_runtime_dispatch(), _provider_gate(), _return_evidence())

    assert interpretation["governance_guarantees"]["automatic_next_task"] is False


def test_deterministic_interpretation_hash() -> None:
    first = interpret_governed_return(_runtime_dispatch(), _provider_gate(), _return_evidence())
    second = interpret_governed_return(_runtime_dispatch(), _provider_gate(), _return_evidence())

    assert first["interpretation_hash"] == second["interpretation_hash"]
    assert first == second


def test_cli_never_invokes_provider_or_execution(monkeypatch, tmp_path) -> None:
    def fail_execution(*args, **kwargs):  # pragma: no cover - should never be reached
        raise AssertionError("execution path invoked")

    def fail_provider(*args, **kwargs):  # pragma: no cover - should never be reached
        raise AssertionError("provider path invoked")

    monkeypatch.setattr("aigol.cli.aigol_cli.run_execution_handoff", fail_execution)
    monkeypatch.setattr("agol_bridge.providers.codex_cli_provider.run_bounded_codex_cli_task", fail_provider)
    runtime_dispatch_path = tmp_path / "runtime_dispatch.json"
    provider_gate_path = tmp_path / "provider_gate.json"
    return_evidence_path = tmp_path / "return_evidence.json"
    _write_json(runtime_dispatch_path, _runtime_dispatch())
    _write_json(provider_gate_path, _provider_gate())
    _write_json(return_evidence_path, _return_evidence())

    parser = build_parser()
    args = parser.parse_args(
        [
            "moc",
            "interpret-return",
            "--runtime-dispatch",
            str(runtime_dispatch_path),
            "--provider-gate",
            str(provider_gate_path),
            "--return-evidence",
            str(return_evidence_path),
            "--json",
        ]
    )
    result = run_command(args)

    interpretation = result["governed_return_interpretation"]
    assert interpretation["outcome_classification"] == EXECUTION_NOT_PERFORMED
    assert result["provider_activation_added"] is False
    assert result["automatic_retry_added"] is False
    assert result["automatic_next_task_added"] is False


def test_no_governance_mutation_occurs(tmp_path) -> None:
    runtime_dispatch_path = tmp_path / "runtime_dispatch.json"
    provider_gate_path = tmp_path / "provider_gate.json"
    _write_json(runtime_dispatch_path, _runtime_dispatch())
    _write_json(provider_gate_path, _provider_gate())
    before_runtime_dispatch = runtime_dispatch_path.read_text(encoding="utf-8")
    before_provider_gate = provider_gate_path.read_text(encoding="utf-8")

    result = inspect_governed_return_interpretation(
        runtime_dispatch_path=runtime_dispatch_path,
        provider_gate_path=provider_gate_path,
    )

    assert runtime_dispatch_path.read_text(encoding="utf-8") == before_runtime_dispatch
    assert provider_gate_path.read_text(encoding="utf-8") == before_provider_gate
    assert result["governance_mutation_added"] is False
    assert result["governed_return_interpretation"]["governance_guarantees"]["governance_mutation"] is False


def test_no_hidden_continuation_occurs() -> None:
    interpretation = interpret_governed_return(_runtime_dispatch(), _provider_gate(), _return_evidence())

    assert interpretation["governance_guarantees"]["autonomous_continuation"] is False
    assert "automatic_next_task" not in interpretation["next_step_recommendation"]
