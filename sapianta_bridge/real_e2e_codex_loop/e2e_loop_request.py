"""Real bounded Codex E2E loop request."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sapianta_bridge.nl_envelope.nl_request import semantic_hash

from .e2e_loop_identity import create_e2e_loop_identity


REQUIRED_PROVIDER_ID = "codex_cli"


@dataclass(frozen=True)
class RealE2ELoopRequest:
    loop_identity: dict[str, Any]
    chatgpt_request: str
    provider_id: str
    workspace_path: str
    timeout_seconds: int
    execution_authorized: bool
    approved_by: str
    codex_executable: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "loop_identity": self.loop_identity,
            "loop_id": self.loop_identity["loop_id"],
            "chatgpt_request": self.chatgpt_request,
            "provider_id": self.provider_id,
            "workspace_path": self.workspace_path,
            "timeout_seconds": self.timeout_seconds,
            "execution_authorized": self.execution_authorized,
            "approved_by": self.approved_by,
            "codex_executable": self.codex_executable,
            "replay_identity": self.loop_identity["replay_identity"],
            "manual_copy_paste_required": False,
            "hidden_prompt_rewriting_present": False,
            "provider_routing_present": False,
            "retry_present": False,
            "fallback_present": False,
            "orchestration_present": False,
            "autonomous_continuation_present": False,
            "replay_safe": True,
        }


def create_e2e_loop_request(
    *,
    chatgpt_request: str,
    workspace_path: str,
    timeout_seconds: int,
    execution_authorized: bool,
    approved_by: str,
    codex_executable: str = "codex",
    provider_id: str = REQUIRED_PROVIDER_ID,
) -> RealE2ELoopRequest:
    replay_identity = f"REPLAY-REAL-E2E-{semantic_hash(chatgpt_request.strip())[:16]}"
    identity = create_e2e_loop_identity(
        chatgpt_request=chatgpt_request,
        provider_id=provider_id,
        replay_identity=replay_identity,
    ).to_dict()
    return RealE2ELoopRequest(
        loop_identity=identity,
        chatgpt_request=chatgpt_request,
        provider_id=provider_id,
        workspace_path=workspace_path,
        timeout_seconds=timeout_seconds,
        execution_authorized=execution_authorized,
        approved_by=approved_by,
        codex_executable=codex_executable,
    )
