"""MOC V1 validation command helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.moc.advisory_contract_generation import inspect_advisory_contract_generation
from aigol.moc.advisory_proposal_validation import inspect_advisory_proposal_validation
from aigol.moc.contract_validation import inspect_contract_validation
from aigol.moc.proposal_correction_loop import inspect_proposal_correction_feedback
from aigol.moc.proposal_ledger import inspect_proposal_ledger_append
from aigol.moc.proposal_persistence import inspect_proposal_persistence


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


__all__ = [
    "append_ledger_command",
    "correction_feedback_command",
    "generate_contract_command",
    "persist_proposal_command",
    "validate_contract_command",
    "validate_proposal_command",
]
