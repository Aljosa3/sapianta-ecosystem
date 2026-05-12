"""Atomic single-task processing lock for bridge transport."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class TaskLock:
    lock_path: Path
    owner: str
    acquired: bool = False

    def acquire(self) -> bool:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            self.acquired = False
            return False
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(self.owner)
            handle.write("\n")
        self.acquired = True
        return True

    def release(self) -> None:
        if self.acquired and self.lock_path.exists():
            self.lock_path.unlink()
        self.acquired = False

    def __enter__(self) -> "TaskLock":
        if not self.acquire():
            raise RuntimeError("bridge task lock is already held or uncertain")
        return self

    def __exit__(self, _exc_type: Any, _exc: Any, _tb: Any) -> None:
        self.release()


def lock_available(lock_path: Path) -> bool:
    return not lock_path.exists()

