"""Governed terminal attachment request."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TerminalAttachmentRequest:
    terminal_attachment_session_id: str
    runtime_serving_session_id: str
    stdin_binding_id: str
    stdout_binding_id: str

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def create_terminal_attachment_request(*, terminal_session: dict) -> TerminalAttachmentRequest:
    return TerminalAttachmentRequest(
        terminal_session["terminal_attachment_session_id"],
        terminal_session["runtime_serving_session_id"],
        terminal_session["stdin_binding_id"],
        terminal_session["stdout_binding_id"],
    )
