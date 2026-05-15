"""Response model for no-copy/paste validation."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NoCopyPasteValidationResponse:
    status: str
    binding: dict[str, Any]
    normalized_result: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "binding": self.binding,
            "normalized_result": self.normalized_result,
            "manual_prompt_relay_present": False,
            "continuity_fabricated": False,
            "provider_success_fabricated": False,
            "replay_safe": True,
        }
