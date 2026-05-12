from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.protocol.lineage import parent_child_lineage, validate_lineage


def test_lineage_validation_rejects_empty_ids() -> None:
    result = validate_lineage(
        {"source_task_id": "", "source_result_id": "RESULT-001"},
        required_fields=("source_task_id", "source_result_id"),
    )
    assert not result.valid
    assert result.errors[0]["field"] == "lineage.source_task_id"


def test_parent_child_lineage_is_deterministic() -> None:
    assert parent_child_lineage("TASK-001", "RESULT-001") == {
        "parent_id": "TASK-001",
        "child_id": "RESULT-001",
    }
