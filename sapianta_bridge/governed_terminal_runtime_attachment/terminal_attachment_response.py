"""Governed terminal attachment response."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TerminalAttachmentResponse:
    terminal_attachment_session_id: str
    response_return_id: str

    def to_dict(self) -> dict:
        return {
            "terminal_attachment_session_id": self.terminal_attachment_session_id,
            "response_return_id": self.response_return_id,
            "terminal_status": "TERMINAL_RESPONSE_EMITTED",
        }


def create_terminal_attachment_response(*, binding: dict) -> TerminalAttachmentResponse:
    return TerminalAttachmentResponse(binding["terminal_attachment_session_id"], binding["response_return_id"])
