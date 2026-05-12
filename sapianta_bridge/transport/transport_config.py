"""Transport configuration for bounded Codex bridge execution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TransportConfig:
    runtime_root: Path = Path("sapianta_bridge/runtime")
    workspace: Path = Path(".")
    quarantine_root: Path = Path("sapianta_bridge/protocol/quarantine")
    command: tuple[str, ...] = ("codex", "exec")
    timeout_seconds: int = 300

    @property
    def tasks_dir(self) -> Path:
        return self.runtime_root / "tasks"

    @property
    def processing_dir(self) -> Path:
        return self.runtime_root / "processing"

    @property
    def completed_dir(self) -> Path:
        return self.runtime_root / "completed"

    @property
    def failed_dir(self) -> Path:
        return self.runtime_root / "failed"

    @property
    def logs_dir(self) -> Path:
        return self.runtime_root / "logs"

    @property
    def replay_log_path(self) -> Path:
        return self.logs_dir / "replay_log.jsonl"

    @property
    def lock_path(self) -> Path:
        return self.processing_dir / ".bridge.lock"

    def ensure_directories(self) -> None:
        for directory in (
            self.tasks_dir,
            self.processing_dir,
            self.completed_dir,
            self.failed_dir,
            self.logs_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)
