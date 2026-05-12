from __future__ import annotations

from sapianta_bridge.protocol.hashing import compute_hash


def valid_task() -> dict:
    return {
        "protocol_version": "0.1",
        "task_id": "TASK-001",
        "milestone_id": "BRIDGE-PROTOCOL-V0.1",
        "task_type": "PATCH",
        "objective": "Create deterministic protocol schemas.",
        "target_paths": ["sapianta_bridge/protocol"],
        "allowed_operations": ["create files"],
        "forbidden_operations": ["subprocess execution"],
        "constraints": ["fail closed"],
        "validation_required": {
            "pytest": True,
            "py_compile": True,
            "git_diff_check": True,
        },
        "expected_outputs": ["result.json", "analysis_context.json"],
        "risk_level": "LOW",
        "human_approval_required": True,
        "lineage": {
            "parent_task_id": None,
            "source_result_id": None,
            "source_reflection_id": None,
        },
    }


def valid_result() -> dict:
    task = valid_task()
    result = {
        "protocol_version": "0.1",
        "task_id": task["task_id"],
        "result_id": "RESULT-001",
        "status": "PASS",
        "execution_summary": "Schema files created.",
        "files_created": ["sapianta_bridge/protocol/schemas.py"],
        "files_modified": [],
        "files_deleted": [],
        "tests": {
            "pytest": {"passed": True},
            "py_compile": {"passed": True},
            "git_diff_check": {"passed": True},
        },
        "errors": [],
        "warnings": [],
        "diff_summary": "Added protocol substrate.",
        "artifact_hashes": {
            "result_sha256": "0" * 64,
            "task_sha256": compute_hash(task),
        },
        "lineage": {
            "source_task_id": task["task_id"],
            "parent_result_id": None,
        },
    }
    result["artifact_hashes"]["result_sha256"] = compute_hash(
        result,
        omit_hash_fields={"result_sha256"},
    )
    return result

