"""Tests for MOC V1 operational lineage foundation."""

from __future__ import annotations

import json

from aigol.cli.aigol_cli import build_parser, run_command
from aigol.moc.approval_gate import evaluate_approval_gate
from aigol.moc.dispatch_authorization import authorize_worker_dispatch
from aigol.moc.dispatch_authorization_preview import build_dispatch_authorization_preview
from aigol.moc.dispatch_request import build_worker_dispatch_request
from aigol.moc.governed_return_interpretation import interpret_governed_return
from aigol.moc.operational_lineage import (
    FAIL_CLOSED,
    LINEAGE_COMPLETE,
    LINEAGE_INCOMPLETE,
    build_operational_lineage,
    inspect_operational_lineage,
)
from aigol.moc.proposal_ledger import build_proposal_ledger_entry
from aigol.moc.proposal_persistence import PROPOSED, VALIDATED, create_proposal_persistence_record
from aigol.moc.provider_execution_gate import evaluate_provider_execution_gate
from aigol.moc.runtime_dispatch import create_runtime_dispatch_event
from aigol.moc.worker_preparation import prepare_worker_package


def _contract() -> dict:
    return {
        "intent_id": "contract-operational-lineage-001",
        "intent_summary": "Close explicit MOC V1 operational lineage.",
        "scope": "operational lineage only",
        "risk_level": "low",
        "mutation_classification": "cosmetic",
        "governance_anchors": [
            {
                "anchor_id": "MOC_V1_OPERATIONAL_LINEAGE_FOUNDATION",
                "anchor_type": "governance",
                "source_ref": "docs/governance/cognition/MOC_V1_OPERATIONAL_LINEAGE_FOUNDATION.md",
            }
        ],
        "allowed_actions": ["record_lineage"],
        "forbidden_actions": ["execute_task", "activate_provider", "retry_operation", "repair_lineage"],
        "required_approvals": ["human_review"],
        "expected_outputs": ["MOC_V1_OPERATIONAL_LINEAGE"],
        "advisory_only": True,
        "replay_safe": True,
        "deterministic_constraints": {
            "no_hidden_inference": True,
            "no_self_dispatch": True,
            "no_runtime_mutation": True,
            "no_autonomous_continuation": True,
            "no_provider_activation": True,
        },
        "contract_hash": "sha256:contract-operational-lineage",
    }


def _proposal() -> dict:
    return {
        "proposal_id": "proposal-operational-lineage-001",
        "proposal_summary": "Link MOC V1 operational lifecycle evidence.",
        "linked_contract_id": "contract-operational-lineage-001",
        "linked_contract_hash": "sha256:contract-operational-lineage",
        "proposal_hash": "sha256:proposal-operational-lineage",
        "suggested_actions": ["record_lineage"],
        "allowed_actions": ["record_lineage"],
        "forbidden_actions": ["execute_task", "activate_provider", "retry_operation", "repair_lineage"],
        "expected_outputs": ["MOC_V1_OPERATIONAL_LINEAGE"],
        "bounded_scope": "operational lineage only",
        "approvals_required": ["human_review"],
        "replay_safe": True,
        "advisory_only": True,
        "lineage_refs": [{"ref_type": "contract", "hash": "sha256:contract-operational-lineage"}],
        "approval_refs": [{"ref_type": "human_review", "hash": "sha256:approval-operational-lineage"}],
        "validation_refs": [{"ref_type": "proposal_validation", "hash": "sha256:validation-operational-lineage"}],
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
    approval = evaluate_approval_gate(proposal_artifact, ledger_entry, approval_evidence)
    approval["linked_validation_hash"] = "sha256:validation-operational-lineage"
    approval["linked_correction_hash"] = "sha256:correction-operational-lineage"
    approval["linked_persistence_hash"] = persistence["persistence_hash"]
    approval["lineage_refs"] = [
        {"ref_type": "validation", "hash": "sha256:validation-operational-lineage"},
        {"ref_type": "correction", "hash": "sha256:correction-operational-lineage"},
        {"ref_type": "persistence", "hash": persistence["persistence_hash"]},
    ]
    return approval


def _runtime_dispatch() -> dict:
    proposal = _proposal()
    approval = _approval_gate(proposal)
    worker = prepare_worker_package(proposal, approval)
    preview = build_dispatch_authorization_preview(worker)
    request = build_worker_dispatch_request(
        preview,
        {
            "requester_type": "human_or_governance",
            "request_scope": "dispatch may be considered by a future authorization layer",
            "replay_safe": True,
            "advisory_only": True,
        },
    )
    authorization = authorize_worker_dispatch(request)
    runtime = create_runtime_dispatch_event(authorization)
    runtime["worker_preparation_hash"] = worker["worker_preparation_hash"]
    runtime["dispatch_preview_hash"] = preview["dispatch_preview_hash"]
    runtime["dispatch_request_hash"] = request["dispatch_request_hash"]
    runtime["approval_gate_hash"] = approval["approval_gate_hash"]
    return runtime


def _provider_gate(runtime_dispatch: dict | None = None) -> dict:
    return evaluate_provider_execution_gate(runtime_dispatch or _runtime_dispatch())


def _governed_return(runtime_dispatch: dict | None = None, provider_gate: dict | None = None) -> dict:
    runtime = runtime_dispatch or _runtime_dispatch()
    gate = provider_gate if provider_gate is not None else _provider_gate(runtime)
    return interpret_governed_return(runtime, gate)


def _complete_lineage() -> dict:
    runtime = _runtime_dispatch()
    gate = _provider_gate(runtime)
    governed_return = _governed_return(runtime, gate)
    return build_operational_lineage(
        contract=_contract(),
        proposal=_proposal(),
        approval=_approval_gate(),
        runtime_dispatch=runtime,
        governed_return=governed_return,
        provider_gate=gate,
    )


def _write_json(path, value: dict) -> None:
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def test_complete_chain_creates_lineage_complete() -> None:
    lineage = _complete_lineage()

    assert lineage["lineage_status"] == LINEAGE_COMPLETE
    assert lineage["lineage_complete"] is True
    assert lineage["replay_reconstructable"] is True


def test_missing_refs_create_lineage_incomplete() -> None:
    runtime = _runtime_dispatch()
    governed_return = _governed_return(runtime, None)
    lineage = build_operational_lineage(
        contract=_contract(),
        proposal=_proposal(),
        approval=_approval_gate(),
        runtime_dispatch=runtime,
        governed_return=governed_return,
        provider_gate=None,
    )

    assert lineage["lineage_status"] == LINEAGE_INCOMPLETE
    assert "provider_gate_ref" in lineage["missing_refs"]


def test_invalid_refs_fail_closed() -> None:
    runtime = _runtime_dispatch()
    governed_return = _governed_return(runtime, _provider_gate(runtime))
    governed_return["runtime_dispatch_hash"] = "sha256:wrong-runtime"

    lineage = build_operational_lineage(
        contract=_contract(),
        proposal=_proposal(),
        approval=_approval_gate(),
        runtime_dispatch=runtime,
        governed_return=governed_return,
        provider_gate=_provider_gate(runtime),
    )

    assert lineage["lineage_status"] == FAIL_CLOSED
    assert "runtime dispatch hash does not match governed return" in lineage["lineage_violations"]


def test_replay_reconstructable_only_true_for_complete_chain() -> None:
    complete = _complete_lineage()
    incomplete = build_operational_lineage(
        contract=_contract(),
        proposal=_proposal(),
        approval=_approval_gate(),
        runtime_dispatch=_runtime_dispatch(),
        governed_return=_governed_return(_runtime_dispatch(), None),
        provider_gate=None,
    )

    assert complete["replay_reconstructable"] is True
    assert incomplete["replay_reconstructable"] is False


def test_lineage_complete_only_true_for_fully_connected_chain() -> None:
    complete = _complete_lineage()
    incomplete = build_operational_lineage(
        contract=_contract(),
        proposal=_proposal(),
        approval=_approval_gate(),
        runtime_dispatch=_runtime_dispatch(),
        governed_return=_governed_return(_runtime_dispatch(), None),
        provider_gate=None,
    )

    assert complete["lineage_complete"] is True
    assert incomplete["lineage_complete"] is False


def test_deterministic_lineage_hash() -> None:
    first = _complete_lineage()
    second = _complete_lineage()

    assert first["lineage_hash"] == second["lineage_hash"]
    assert first == second


def test_no_automatic_repair() -> None:
    lineage = build_operational_lineage(
        contract=_contract(),
        proposal=_proposal(),
        approval=_approval_gate(),
        runtime_dispatch=_runtime_dispatch(),
        governed_return=_governed_return(_runtime_dispatch(), None),
        provider_gate=None,
    )

    assert "provider_gate_ref" in lineage["missing_refs"]
    assert lineage["lineage_chain"]["provider_gate_ref"] == "UNKNOWN"


def test_no_hidden_inference() -> None:
    lineage = build_operational_lineage(
        contract=_contract(),
        proposal=_proposal(),
        approval=_approval_gate(),
        runtime_dispatch=_runtime_dispatch(),
        governed_return=_governed_return(_runtime_dispatch(), None),
        provider_gate=None,
    )

    assert lineage["lineage_chain"]["provider_gate_ref"] == "UNKNOWN"
    assert lineage["governance_guarantees"]["lineage_only"] is True


def test_cli_never_invokes_provider_or_execution(monkeypatch, tmp_path) -> None:
    def fail_execution(*args, **kwargs):  # pragma: no cover - should never be reached
        raise AssertionError("execution path invoked")

    def fail_provider(*args, **kwargs):  # pragma: no cover - should never be reached
        raise AssertionError("provider path invoked")

    monkeypatch.setattr("aigol.cli.aigol_cli.run_execution_handoff", fail_execution)
    monkeypatch.setattr("agol_bridge.providers.codex_cli_provider.run_bounded_codex_cli_task", fail_provider)
    runtime = _runtime_dispatch()
    gate = _provider_gate(runtime)
    governed_return = _governed_return(runtime, gate)
    contract_path = tmp_path / "contract.json"
    proposal_path = tmp_path / "proposal.json"
    approval_path = tmp_path / "approval.json"
    runtime_path = tmp_path / "runtime.json"
    gate_path = tmp_path / "gate.json"
    return_path = tmp_path / "return.json"
    _write_json(contract_path, _contract())
    _write_json(proposal_path, _proposal())
    _write_json(approval_path, _approval_gate())
    _write_json(runtime_path, runtime)
    _write_json(gate_path, gate)
    _write_json(return_path, governed_return)

    parser = build_parser()
    args = parser.parse_args(
        [
            "moc",
            "operational-lineage",
            "--contract",
            str(contract_path),
            "--proposal",
            str(proposal_path),
            "--approval",
            str(approval_path),
            "--runtime-dispatch",
            str(runtime_path),
            "--governed-return",
            str(return_path),
            "--provider-gate",
            str(gate_path),
            "--json",
        ]
    )
    result = run_command(args)

    assert result["operational_lineage"]["lineage_status"] == LINEAGE_COMPLETE
    assert result["execution_authority_added"] is False
    assert result["provider_activation_added"] is False


def test_no_governance_mutation_occurs(tmp_path) -> None:
    runtime = _runtime_dispatch()
    gate = _provider_gate(runtime)
    governed_return = _governed_return(runtime, gate)
    contract_path = tmp_path / "contract.json"
    proposal_path = tmp_path / "proposal.json"
    approval_path = tmp_path / "approval.json"
    runtime_path = tmp_path / "runtime.json"
    gate_path = tmp_path / "gate.json"
    return_path = tmp_path / "return.json"
    for path, artifact in (
        (contract_path, _contract()),
        (proposal_path, _proposal()),
        (approval_path, _approval_gate()),
        (runtime_path, runtime),
        (gate_path, gate),
        (return_path, governed_return),
    ):
        _write_json(path, artifact)
    before = {path: path.read_text(encoding="utf-8") for path in (contract_path, proposal_path, approval_path, runtime_path, gate_path, return_path)}

    result = inspect_operational_lineage(
        contract_path=contract_path,
        proposal_path=proposal_path,
        approval_path=approval_path,
        runtime_dispatch_path=runtime_path,
        governed_return_path=return_path,
        provider_gate_path=gate_path,
    )

    assert {path: path.read_text(encoding="utf-8") for path in before} == before
    assert result["governance_mutation_added"] is False


def test_no_orchestration_occurs() -> None:
    lineage = _complete_lineage()

    assert lineage["governance_guarantees"]["orchestration_authority"] is False


def test_lineage_continuity_flags_are_deterministic() -> None:
    first = _complete_lineage()["lineage_continuity"]
    second = _complete_lineage()["lineage_continuity"]

    assert first == second
    assert all(first.values())
