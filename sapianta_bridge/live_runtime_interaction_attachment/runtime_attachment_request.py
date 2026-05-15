"""Runtime attachment request."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RuntimeAttachmentRequest:
    runtime_attachment_session_id: str
    live_runtime_session_id: str

    def to_dict(self) -> dict[str, Any]:
        return {"runtime_attachment_session_id": self.runtime_attachment_session_id, "live_runtime_session_id": self.live_runtime_session_id, "continuity_fabrication_requested": False}


def create_runtime_attachment_request(*, session: dict[str, Any]) -> RuntimeAttachmentRequest:
    return RuntimeAttachmentRequest(session["runtime_attachment_session_id"], session["live_runtime_session_id"])
