"""Continuity preview command helpers for the deterministic AiGOL CLI."""

from __future__ import annotations

from agol_bridge.chatgpt_ingress.controlled_execution_continuity_preview import create_controlled_execution_continuity_preview
from agol_bridge.chatgpt_ingress.explicit_dispatch_authorization import create_explicit_dispatch_authorization
from agol_bridge.chatgpt_ingress.governed_handoff_package_preview import create_governed_handoff_package_preview
from agol_bridge.chatgpt_ingress.governed_task_package_preview import create_governed_task_package_preview
from agol_bridge.chatgpt_ingress.human_approval_gate import create_human_approval_gate


def build_governed_chain(*, ingress_artifact: dict) -> dict:
    task_preview = create_governed_task_package_preview(ingress_artifact)
    approval = create_human_approval_gate(
        preview=task_preview,
        human_decision="APPROVE",
        approval_reason="AiGOL CLI deterministic continuity approval evidence.",
        operator_label="AIGOL_CLI_OPERATOR",
        created_at="1970-01-01T00:00:00Z",
    )
    handoff_preview = create_governed_handoff_package_preview(
        task_package_preview=task_preview,
        human_approval=approval,
    )
    dispatch_authorization = create_explicit_dispatch_authorization(
        handoff_preview=handoff_preview,
        dispatch_decision="AUTHORIZE",
        dispatch_authorization_reason="AiGOL CLI deterministic dispatch authorization evidence.",
    )
    continuity_preview = create_controlled_execution_continuity_preview(dispatch_authorization=dispatch_authorization)
    return {
        "command": "aigol continuity preview",
        "task_package_preview": task_preview,
        "human_approval": approval,
        "handoff_preview": handoff_preview,
        "dispatch_authorization": dispatch_authorization,
        "continuity_preview": continuity_preview,
        "replay_identity": continuity_preview.get("replay_identity", task_preview.get("replay_identity", "UNKNOWN")),
        "hash_continuity": {
            "ingress_artifact_hash": task_preview.get("source_ingress_artifact_hash", ""),
            "proposal_candidate_hash": task_preview.get("semantic_proposal_candidate_hash", "UNKNOWN"),
            "contract_candidate_hash": task_preview.get("semantic_contract_candidate_hash", "UNKNOWN"),
            "acceptance_gate_hash": task_preview.get("admissibility_gate_hash", "UNKNOWN"),
            "task_preview_hash": task_preview.get("preview_hash", ""),
            "human_approval_hash": approval.get("approval_hash", ""),
            "handoff_preview_hash": handoff_preview.get("handoff_preview_hash", ""),
            "dispatch_authorization_hash": dispatch_authorization.get("dispatch_authorization_hash", ""),
            "continuity_preview_hash": continuity_preview.get("continuity_preview_hash", ""),
        },
    }


def continuity_preview_summary(*, ingress_artifact: dict) -> dict:
    chain = build_governed_chain(ingress_artifact=ingress_artifact)
    preview = chain["continuity_preview"]
    return {
        "command": "aigol continuity preview",
        "continuity_status": preview.get("execution_continuity_status", "UNKNOWN"),
        "replay_identity": chain["replay_identity"],
        "hash_continuity": chain["hash_continuity"],
        "execution_path_candidate": preview.get("execution_path_candidate", {}),
        "provider_invoked": preview.get("provider_invoked", False),
        "native_messaging_called": preview.get("native_messaging_called", False),
    }


__all__ = ["build_governed_chain", "continuity_preview_summary"]
