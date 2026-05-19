"""Result package schema for AGOL Bridge v0.1."""

RESULT_REQUIRED_FIELDS = {
    "status": str,
    "tests": list,
    "files_changed": list,
    "artifacts": list,
    "summary": str,
    "requires_human_review": bool,
}

RESULT_SCHEMA_VERSION = "agol_bridge_result_v0_1"
