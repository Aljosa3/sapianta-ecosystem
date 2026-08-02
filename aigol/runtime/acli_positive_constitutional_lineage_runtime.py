"""Positive AiCLI transport for existing G63 and G47 constitutional lineage."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from aigol.runtime.acli_governed_development_execution_bridge import (
    derive_acli_governed_development_scope,
)
from aigol.runtime.constitutional_reuse_proof_production_gate import (
    validate_reuse_proof_g47_scope_binding,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
)
from aigol.runtime.transport.serialization import replay_hash, write_json_immutable


ACLI_POSITIVE_CONSTITUTIONAL_LINEAGE_VERSION = (
    "G64_06_ACLI_POSITIVE_CONSTITUTIONAL_LINEAGE_INTEGRATION_V1"
)
ACLI_POSITIVE_CONSTITUTIONAL_LINEAGE_ARTIFACT_V1 = (
    "ACLI_POSITIVE_CONSTITUTIONAL_LINEAGE_ARTIFACT_V1"
)
LINEAGE_READY_FOR_BRIDGE = "LINEAGE_READY_FOR_BRIDGE"


def prepare_acli_positive_constitutional_lineage(
    *,
    lineage_id: str,
    prompt_id: str,
    human_prompt: str,
    conversational_routing_capture: dict[str, Any],
    workspace_root: str | Path,
    created_at: str,
    replay_dir: str | Path,
    reuse_proof_input: dict[str, Any] | None = None,
    reuse_proof_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run existing Platform Core, G63, and G47 owners and bind their result."""

    if (reuse_proof_input is None) == (reuse_proof_result is None):
        raise FailClosedRuntimeError(
            "AiCLI positive constitutional lineage requires exactly one reuse proof artifact"
        )
    replay_path = Path(replay_dir)
    if replay_path.exists():
        raise FailClosedRuntimeError(
            "AiCLI positive constitutional lineage replay already exists"
        )
    scope_projection = derive_acli_governed_development_scope(
        prompt_id=prompt_id,
        human_prompt=human_prompt,
        conversational_routing_capture=conversational_routing_capture,
        workspace_root=workspace_root,
    )
    project_context = prepare_unified_human_interface_project_context(
        interface_name="AiCLI positive constitutional lineage",
        session_id=f"{lineage_id}:PROJECT-SERVICES",
        message=human_prompt,
        runtime_root=replay_path / "platform_core_project_services",
        workspace=workspace_root,
        created_at=created_at,
        reuse_proof_input=reuse_proof_input,
        reuse_proof_result=reuse_proof_result,
        reuse_proof_proposed_scope=scope_projection["proposed_scope"],
    )
    binding = validate_reuse_proof_g47_scope_binding(
        project_context.get("reuse_proof_g47_scope_binding")
    )
    bound_scope = binding["proposed_scope"]
    for field in (
        "entry_point",
        "work_type",
        "target_paths",
        "governance_target_paths",
        "allowed_intermediate_deltas",
    ):
        if bound_scope.get(field) != scope_projection["proposed_scope"].get(field):
            raise FailClosedRuntimeError(
                "FAIL_CLOSED_REUSE_DECISION_SCOPE_CONFLICT"
            )
    governance = project_context.get("constitutional_development_governance")
    if not isinstance(governance, dict):
        raise FailClosedRuntimeError(
            "AiCLI positive constitutional lineage requires fresh G47 evidence"
        )
    artifact = {
        "artifact_type": ACLI_POSITIVE_CONSTITUTIONAL_LINEAGE_ARTIFACT_V1,
        "runtime_version": ACLI_POSITIVE_CONSTITUTIONAL_LINEAGE_VERSION,
        "lineage_id": _require_string(lineage_id, "lineage_id"),
        "prompt_id": _require_string(prompt_id, "prompt_id"),
        "human_prompt_hash": replay_hash(_require_string(human_prompt, "human_prompt")),
        "source_routing_hash": _require_string(
            conversational_routing_capture.get("conversational_cli_routing_hash"),
            "conversational_cli_routing_hash",
        ),
        "scope_projection": scope_projection,
        "scope_projection_hash": scope_projection["artifact_hash"],
        "reuse_proof_production_admission": deepcopy(
            project_context["reuse_proof_production_admission"]
        ),
        "reuse_proof_production_admission_hash": project_context[
            "reuse_proof_production_admission_hash"
        ],
        "g47_operational_record": deepcopy(governance),
        "g47_operational_record_hash": governance["artifact_hash"],
        "reuse_proof_g47_scope_binding": binding,
        "reuse_proof_g47_scope_binding_hash": binding["artifact_hash"],
        "lineage_status": LINEAGE_READY_FOR_BRIDGE,
        "created_at": _require_string(created_at, "created_at"),
        "platform_core_owner_preserved": True,
        "reuse_proof_owner_preserved": True,
        "development_governance_owner_preserved": True,
        "bridge_validation_modified": False,
        "approval_created": False,
        "authorization_created": False,
        "repository_mutated": False,
        "worker_invoked": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    transported_routing = deepcopy(conversational_routing_capture)
    transported_routing.update(
        {
            "reuse_proof_g47_scope_binding": binding,
            "reuse_proof_g47_scope_binding_hash": binding["artifact_hash"],
            "acli_positive_constitutional_lineage_id": artifact["lineage_id"],
            "acli_positive_constitutional_lineage_hash": artifact["artifact_hash"],
            "acli_positive_constitutional_lineage_replay_reference": str(
                replay_path
            ),
        }
    )
    transported_routing["constitutional_lineage_transport_hash"] = replay_hash(
        {
            "source_routing_hash": artifact["source_routing_hash"],
            "scope_projection_hash": artifact["scope_projection_hash"],
            "reuse_proof_g47_scope_binding_hash": binding["artifact_hash"],
            "lineage_hash": artifact["artifact_hash"],
        }
    )
    write_json_immutable(
        replay_path / "000_acli_positive_constitutional_lineage_recorded.json",
        {"artifact": artifact},
    )
    return {
        "lineage_artifact": artifact,
        "routing_capture": transported_routing,
        "reuse_proof_g47_scope_binding": binding,
        "replay_reference": str(replay_path),
        "lineage_status": LINEAGE_READY_FOR_BRIDGE,
        "fail_closed": False,
    }


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FailClosedRuntimeError(f"{field} is required")
    return value.strip()

