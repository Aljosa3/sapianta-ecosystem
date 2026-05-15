"""Runtime-bound attachment response."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RuntimeAttachmentResponse:
    runtime_attachment_session_id: str
    response_return_id: str

    def to_dict(self) -> dict[str, Any]:
        return {"runtime_attachment_session_id": self.runtime_attachment_session_id, "response_return_id": self.response_return_id, "attachment_status": "ATTACHMENT_RUNTIME_EMITTED", "continuity_fabricated": False, "replay_safe": True}


def create_runtime_attachment_response(*, binding: dict[str, Any]) -> RuntimeAttachmentResponse:
    return RuntimeAttachmentResponse(binding["runtime_attachment_session_id"], binding["response_return_id"])
