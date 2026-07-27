"""Fail-closed input errors for the constitutional validator kernel."""

from __future__ import annotations


class ConstitutionalValidationInputError(ValueError):
    """A deterministic input failure carrying a stable reason code."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


__all__ = ["ConstitutionalValidationInputError"]
