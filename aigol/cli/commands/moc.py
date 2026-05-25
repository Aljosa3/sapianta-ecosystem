"""MOC V1 validation command helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.moc.advisory_contract_generation import inspect_advisory_contract_generation
from aigol.moc.advisory_proposal_validation import inspect_advisory_proposal_validation
from aigol.moc.contract_validation import inspect_contract_validation


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


__all__ = ["generate_contract_command", "validate_contract_command", "validate_proposal_command"]
