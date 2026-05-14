"""Deterministic E2E validation case definition."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class E2EValidationCase:
    validation_name: str = "FIRST_END_TO_END_NO_COPY_PASTE_VALIDATION_V1"
    chatgpt_input: str = "Inspect governance evidence"
    requested_provider_id: str = "deterministic_mock"
    conversation_id: str = "E2E-NO-COPY-PASTE"
    timestamp: str = "1970-01-01T00:00:00Z"

    def to_dict(self) -> dict[str, Any]:
        return {
            "validation_name": self.validation_name,
            "chatgpt_input": self.chatgpt_input,
            "requested_provider_id": self.requested_provider_id,
            "conversation_id": self.conversation_id,
            "timestamp": self.timestamp,
            "manual_intermediate_transfer_allowed": False,
            "external_api_calls_allowed": False,
            "shell_network_execution_allowed": False,
            "replay_safe": True,
        }


def default_e2e_validation_case() -> E2EValidationCase:
    return E2EValidationCase()
