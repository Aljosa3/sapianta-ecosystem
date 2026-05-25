"""MOC V1 validation command helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.moc.approval_gate import inspect_approval_gate
from aigol.moc.advisory_contract_generation import inspect_advisory_contract_generation
from aigol.moc.advisory_proposal_validation import inspect_advisory_proposal_validation
from aigol.moc.contract_validation import inspect_contract_validation
from aigol.moc.proposal_correction_loop import inspect_proposal_correction_feedback
from aigol.moc.proposal_ledger import inspect_proposal_ledger_append
from aigol.moc.proposal_persistence import inspect_proposal_persistence
from aigol.moc.dispatch_authorization import inspect_worker_dispatch_authorization
from aigol.moc.dispatch_authorization_preview import inspect_dispatch_authorization_preview
from aigol.moc.dispatch_request import inspect_worker_dispatch_request
from aigol.moc.worker_preparation import inspect_worker_preparation


def validate_contract_command(
    *,
    input_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    return inspect_contract_validation(input_path=input_path, output_path=output_path)


def generate_contract_command(
    *,
    input_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    return inspect_advisory_contract_generation(input_path=input_path, output_path=output_path)


def validate_proposal_command(
    *,
    proposal_path: str | Path | None = None,
    contract_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    return inspect_advisory_proposal_validation(
        proposal_path=proposal_path,
        contract_path=contract_path,
        output_path=output_path,
    )


def correction_feedback_command(
    *,
    validation_result_path: str | Path | None = None,
    attempt_number: int | str = 1,
    max_attempts: int | str = 3,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    return inspect_proposal_correction_feedback(
        validation_result_path=validation_result_path,
        attempt_number=attempt_number,
        max_attempts=max_attempts,
        output_path=output_path,
    )


def persist_proposal_command(
    *,
    proposal_path: str | Path | None = None,
    proposal_state: str,
    previous_state: str,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    return inspect_proposal_persistence(
        proposal_path=proposal_path,
        proposal_state=proposal_state,
        previous_state=previous_state,
        output_path=output_path,
    )


def append_ledger_command(
    *,
    persistence_record_path: str | Path | None = None,
    ledger_path: str | Path,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    return inspect_proposal_ledger_append(
        persistence_record_path=persistence_record_path,
        ledger_path=ledger_path,
        output_path=output_path,
    )


def approval_gate_command(
    *,
    proposal_path: str | Path | None = None,
    ledger_entry_path: str | Path | None = None,
    approval_evidence_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    return inspect_approval_gate(
        proposal_path=proposal_path,
        ledger_entry_path=ledger_entry_path,
        approval_evidence_path=approval_evidence_path,
        output_path=output_path,
    )


def prepare_worker_command(
    *,
    proposal_path: str | Path | None = None,
    approval_gate_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    return inspect_worker_preparation(
        proposal_path=proposal_path,
        approval_gate_path=approval_gate_path,
        output_path=output_path,
    )


def dispatch_preview_command(
    *,
    worker_package_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    return inspect_dispatch_authorization_preview(
        worker_package_path=worker_package_path,
        output_path=output_path,
    )


def dispatch_request_command(
    *,
    dispatch_preview_path: str | Path | None = None,
    request_evidence_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    return inspect_worker_dispatch_request(
        dispatch_preview_path=dispatch_preview_path,
        request_evidence_path=request_evidence_path,
        output_path=output_path,
    )


def dispatch_authorize_command(
    *,
    dispatch_request_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    return inspect_worker_dispatch_authorization(
        dispatch_request_path=dispatch_request_path,
        output_path=output_path,
    )


__all__ = [
    "append_ledger_command",
    "approval_gate_command",
    "correction_feedback_command",
    "dispatch_authorize_command",
    "dispatch_preview_command",
    "dispatch_request_command",
    "generate_contract_command",
    "persist_proposal_command",
    "prepare_worker_command",
    "validate_contract_command",
    "validate_proposal_command",
]
