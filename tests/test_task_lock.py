from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sapianta_bridge.transport.task_lock import TaskLock, lock_available


def test_lock_prevents_concurrent_processing(tmp_path: Path) -> None:
    lock_path = tmp_path / ".bridge.lock"
    first = TaskLock(lock_path, "TASK-001")
    second = TaskLock(lock_path, "TASK-002")

    assert first.acquire() is True
    assert lock_available(lock_path) is False
    assert second.acquire() is False
    first.release()
    assert lock_available(lock_path) is True

