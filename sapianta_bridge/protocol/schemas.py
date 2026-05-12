"""Canonical schemas and enum definitions for bridge protocol artifacts."""

from __future__ import annotations

PROTOCOL_VERSION = "0.1"
PROTOCOL_NAME = "SAPIANTA_CODEX_BRIDGE_PROTOCOL"

SUPPORTED_ARTIFACTS = (
    "task.json",
    "result.json",
    "analysis_context.json",
    "next_task_proposal.json",
)

TASK_TYPES = ("PATCH", "FEATURE", "FIX", "INVESTIGATION")
RISK_LEVELS = ("LOW", "MEDIUM", "HIGH", "CRITICAL")
RESULT_STATUSES = ("PASS", "FAIL", "BLOCKED", "ESCALATED")
PROPOSAL_TYPES = ("FOLLOW_UP", "FIX", "FINALIZE", "INVESTIGATE", "STOP")

TASK_REQUIRED_FIELDS = (
    "protocol_version",
    "task_id",
    "milestone_id",
    "task_type",
    "objective",
    "target_paths",
    "allowed_operations",
    "forbidden_operations",
    "constraints",
    "validation_required",
    "expected_outputs",
    "risk_level",
    "human_approval_required",
    "lineage",
)

RESULT_REQUIRED_FIELDS = (
    "protocol_version",
    "task_id",
    "result_id",
    "status",
    "execution_summary",
    "files_created",
    "files_modified",
    "files_deleted",
    "tests",
    "errors",
    "warnings",
    "diff_summary",
    "artifact_hashes",
    "lineage",
)

ANALYSIS_CONTEXT_REQUIRED_FIELDS = (
    "protocol_version",
    "task_id",
    "analysis_context_id",
    "interpretation_ready",
    "architectural_impact",
    "governance_impact",
    "risk_analysis",
    "opportunities",
    "recommended_next_milestone",
    "artifact_hashes",
    "lineage",
)

NEXT_TASK_PROPOSAL_REQUIRED_FIELDS = (
    "protocol_version",
    "proposal_id",
    "proposal_type",
    "recommended_action",
    "rationale",
    "approval_required",
    "allowed_to_execute_automatically",
    "lineage",
)

REQUIRED_FIELDS_BY_ARTIFACT = {
    "task.json": TASK_REQUIRED_FIELDS,
    "result.json": RESULT_REQUIRED_FIELDS,
    "analysis_context.json": ANALYSIS_CONTEXT_REQUIRED_FIELDS,
    "next_task_proposal.json": NEXT_TASK_PROPOSAL_REQUIRED_FIELDS,
}

