"""Passive G65 topology seed and the bounded G67-02 current overlay."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aigol.runtime.transport.serialization import load_json, replay_hash


TOPOLOGY_OVERLAY_VERSION = "G67_02_CONSTITUTIONAL_RUNTIME_TOPOLOGY_OVERLAY_V1"
G65_MAP_VERSION = "G65_10_CONSTITUTIONAL_NERVOUS_SYSTEM_STATIC_MAP_V1"
G65_MAP_PATH = (
    Path(__file__).resolve().parents[3]
    / "docs/governance/maps/AIGOL_CONSTITUTIONAL_NERVOUS_SYSTEM_MAP_V1.json"
)

CURRENT_STAGES = (
    "CANONICAL_HUMAN_ENTRY",
    "HUMAN_INTENT_PRECEDENCE",
    "CONVERSATION",
    "SEMANTIC_SLOTS_CWM",
    "INTERPRETER_PROPOSAL",
    "PROPOSAL_VALIDATION",
    "PROPOSAL_COMMIT",
    "REQUEST_CLASSIFICATION",
    "OWNER_BOUND_CLARIFICATION_CONTINUATION",
    "CANDIDATE_REVIEW",
    "HUMAN_CONFIRMATION",
    "OBJECTIVE_READINESS",
    "OBJECTIVE_COMMITMENT",
    "FLOW_BINDING",
    "COMMITMENT_HANDOFF",
    "PLATFORM_OBJECTIVE",
    "PLATFORM_ADMISSION",
    "PRODUCTION_REUSE_PROOF",
    "DEVELOPMENT_GOVERNANCE",
    "CAPABILITY_ROUTE",
    "EXECUTION_PREPARATION",
    "EXECUTION_SUMMARY",
    "HUMAN_EXECUTION_DECISION",
    "EXECUTION_AUTHORIZATION",
    "RESOURCE_SELECTION",
    "WORKER_INVOCATION_REQUEST",
    "WORKER_ASSIGNMENT",
    "WORKER_DISPATCH",
    "WORKER_INVOCATION",
    "EXECUTION",
    "RESULT_CAPTURE",
    "RESULT_VALIDATION",
    "CAPABILITY_COMPLETION",
    "POST_EXECUTION_REPLAY_REVIEW",
    "GOVERNED_TERMINATION",
    "FINAL_EXECUTION_CERTIFICATION",
)


def load_topology_overlay(version: str) -> dict[str, Any]:
    """Load the immutable G65 seed and compose an in-memory passive overlay."""

    source = load_json(G65_MAP_PATH)
    semantics = source.get("map_semantics")
    required = {
        "descriptive_only": True,
        "runtime_registry": False,
        "grants_authority": False,
        "authorizes_execution": False,
        "authorizes_mutation": False,
        "static_reconstruction_only": True,
        "exhaustive_dynamic_reachability_claimed": False,
    }
    if source.get("map_version") != G65_MAP_VERSION or semantics != required:
        raise ValueError("G65 topology seed semantics differ")
    selected_is_current = version == TOPOLOGY_OVERLAY_VERSION
    selected_is_seed_only = version == G65_MAP_VERSION
    return {
        "topology_overlay_version": version,
        "supported": selected_is_current or selected_is_seed_only,
        "current_overlay_selected": selected_is_current,
        "g65_map_version": source["map_version"],
        "g65_map_hash": replay_hash(source),
        "map_semantics": dict(required),
        "current_stages": list(CURRENT_STAGES) if selected_is_current else [],
        "known_uncomposed_edges": [
            {
                "from": "FINAL_EXECUTION_CERTIFICATION",
                "to": "G64_CONSTITUTIONAL_COMPLETION",
                "gap_classification": "UNCOMPOSED",
                "correlated": False,
            }
        ],
    }
