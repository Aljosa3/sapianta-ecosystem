"""Task package schema for AGOL Bridge v0.1."""

TASK_REQUIRED_FIELDS = {
    "task_id": str,
    "governance_mode": str,
    "risk_class": str,
    "approval_required": bool,
    "codex_prompt": str,
    "constraints": list,
    "expected_outputs": list,
    "metadata": dict,
}

TASK_SCHEMA_VERSION = "agol_bridge_task_v0_1"
