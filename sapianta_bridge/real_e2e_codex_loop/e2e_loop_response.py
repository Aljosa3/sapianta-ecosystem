"""ChatGPT-facing response for the real bounded Codex E2E loop."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RealE2ELoopResponse:
    loop_id: str
    provider_id: str
    envelope_id: str
    invocation_id: str
    result_return_id: str
    replay_identity: str
    execution_status: str
    chatgpt_response_payload: dict[str, Any]
    loop_binding: dict[str, Any]
    evidence_references: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "loop_id": self.loop_id,
            "provider_id": self.provider_id,
            "envelope_id": self.envelope_id,
            "invocation_id": self.invocation_id,
            "result_return_id": self.result_return_id,
            "replay_identity": self.replay_identity,
            "execution_status": self.execution_status,
            "chatgpt_response_payload": self.chatgpt_response_payload,
            "loop_binding": self.loop_binding,
            "evidence_references": self.evidence_references,
            "manual_copy_paste_required": False,
            "hidden_prompt_rewriting_present": False,
            "provider_routing_present": False,
            "retry_present": False,
            "fallback_present": False,
            "orchestration_present": False,
            "autonomous_continuation_present": False,
            "replay_safe": True,
        }


def create_e2e_loop_response(
    *,
    request: dict[str, Any],
    result_payload: dict[str, Any],
    loop_binding: dict[str, Any],
    evidence_references: dict[str, Any],
) -> RealE2ELoopResponse:
    return RealE2ELoopResponse(
        loop_id=request["loop_id"],
        provider_id=result_payload["provider_id"],
        envelope_id=result_payload["envelope_id"],
        invocation_id=result_payload["invocation_id"],
        result_return_id=result_payload["result_return_id"],
        replay_identity=result_payload["replay_identity"],
        execution_status=result_payload["execution_status"],
        chatgpt_response_payload={
            "interpretation_ready": result_payload["interpretation_ready"],
            "execution_status": result_payload["execution_status"],
            "normalized_provider_result": result_payload["normalized_provider_result"],
            "result_return_id": result_payload["result_return_id"],
        },
        loop_binding=loop_binding,
        evidence_references=evidence_references,
    )
