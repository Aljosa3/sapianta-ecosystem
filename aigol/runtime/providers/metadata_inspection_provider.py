"""Bounded read-only runtime metadata inspection provider."""

from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
import platform
import resource
import sys
from typing import Any, Callable

from aigol.runtime.transport.serialization import replay_hash


class MetadataInspectionProvider:
    """Exposes bounded runtime metadata without mutation authority."""

    _UNSAFE_FIELDS = (
        "environment_variables",
        "secrets",
        "tokens",
        "api_keys",
        "credentials",
        "filesystem_crawling",
        "process_control",
        "shell_access",
        "subprocess_execution",
        "network_scanning",
        "telemetry_streaming",
        "persistent_monitoring",
        "metrics_aggregation",
    )
    _SECRET_MARKERS = ("secret", "token", "key", "password", "credential", "authorization")

    def __init__(
        self,
        repository_root: str | Path | None = None,
        timestamp_provider: Callable[[], str] | None = None,
    ) -> None:
        self._repository_root = Path(repository_root) if repository_root is not None else Path.cwd()
        self._timestamp_provider = timestamp_provider or self._utc_timestamp

    def inspect_runtime(self) -> dict[str, Any]:
        fields = {
            "runtime_version": self._runtime_version(),
            "provider_availability": {
                "metadata_inspection_provider": True,
                "inspect_runtime": True,
                "inspect_environment": True,
                "inspect_process": True,
            },
            "governance_artifact_visibility": self._governance_artifact_visibility(),
            "replay_capability_indicators": {
                "structured_evidence": True,
                "evidence_hash": True,
                "read_only": True,
                "deterministic_structure": True,
            },
        }
        return self._evidence("inspect_runtime", "RUNTIME_METADATA_INSPECTED", "runtime metadata inspected", fields)

    def inspect_environment(self) -> dict[str, Any]:
        fields = {
            "os_name": platform.system() or "UNAVAILABLE",
            "python_version": platform.python_version(),
            "working_directory": str(Path.cwd()),
            "timezone": self._timezone_name(),
        }
        return self._evidence("inspect_environment", "ENVIRONMENT_METADATA_INSPECTED", "environment metadata inspected", fields)

    def inspect_process(self) -> dict[str, Any]:
        fields = {
            "process_id": os.getpid(),
            "process_start_timestamp": self._process_start_timestamp(),
            "process_metadata": self._process_metadata(),
        }
        return self._evidence("inspect_process", "PROCESS_METADATA_INSPECTED", "process metadata inspected", fields)

    def _evidence(self, operation: str, status: str, reason: str, fields: dict[str, Any]) -> dict[str, Any]:
        safe_fields, blocked_fields = self._filter_safe_fields(fields)
        evidence = {
            "operation": operation,
            "timestamp": self._timestamp_provider(),
            "status": status,
            "inspected_fields": sorted(safe_fields),
            "blocked_fields": sorted(set(blocked_fields).union(self._UNSAFE_FIELDS)),
            "reason": reason,
            "metadata": safe_fields,
        }
        evidence["evidence_hash"] = replay_hash(evidence)
        return evidence

    def _filter_safe_fields(self, fields: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        safe_fields: dict[str, Any] = {}
        blocked_fields: list[str] = []
        for name, value in fields.items():
            if self._is_secret_field(name):
                blocked_fields.append(name)
                continue
            safe_fields[name] = value
        return safe_fields, blocked_fields

    def _is_secret_field(self, field_name: str) -> bool:
        normalized = field_name.lower()
        return any(marker in normalized for marker in self._SECRET_MARKERS)

    def _runtime_version(self) -> dict[str, str]:
        return {
            "provider_name": "REAL_METADATA_INSPECTION_PROVIDER_V1",
            "schema_version": "1.0",
            "python_runtime": platform.python_implementation(),
        }

    def _governance_artifact_visibility(self) -> dict[str, bool]:
        artifacts = {
            "constitutional_architecture_spec": "docs/governance/CONSTITUTIONAL_ARCHITECTURE_SPEC_V1.md",
            "canonical_layer_model": "docs/governance/CANONICAL_LAYER_MODEL.md",
            "constitutional_invariants": "docs/governance/CONSTITUTIONAL_INVARIANTS.md",
            "governance_enforcement_hierarchy": "docs/governance/GOVERNANCE_ENFORCEMENT_HIERARCHY.md",
            "governance_lineage_model": "docs/governance/GOVERNANCE_LINEAGE_MODEL.md",
        }
        return {name: (self._repository_root / relative_path).is_file() for name, relative_path in artifacts.items()}

    def _timezone_name(self) -> str:
        try:
            current_timezone = datetime.now().astimezone().tzinfo
            if current_timezone is None:
                return "UNAVAILABLE"
            return current_timezone.tzname(None) or "UNAVAILABLE"
        except (OSError, ValueError):
            return "UNAVAILABLE"

    def _process_start_timestamp(self) -> str:
        proc_start = self._linux_process_start_timestamp()
        if proc_start != "UNAVAILABLE":
            return proc_start
        return "UNAVAILABLE"

    def _linux_process_start_timestamp(self) -> str:
        try:
            stat_parts = Path("/proc/self/stat").read_text(encoding="utf-8").split()
            boot_time = self._linux_boot_time()
            if boot_time <= 0:
                return "UNAVAILABLE"
            ticks_per_second = os.sysconf(os.sysconf_names["SC_CLK_TCK"])
            start_ticks = int(stat_parts[21])
            start_seconds = boot_time + (start_ticks / ticks_per_second)
            return datetime.fromtimestamp(start_seconds, tz=timezone.utc).isoformat()
        except (IndexError, KeyError, OSError, ValueError):
            return "UNAVAILABLE"

    def _linux_boot_time(self) -> int:
        try:
            for line in Path("/proc/stat").read_text(encoding="utf-8").splitlines():
                if line.startswith("btime "):
                    return int(line.split()[1])
        except (OSError, ValueError):
            return 0
        return 0

    def _process_metadata(self) -> dict[str, Any]:
        metadata = {
            "memory_max_rss": "UNAVAILABLE",
        }
        try:
            metadata["memory_max_rss"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        except (OSError, ValueError):
            metadata["memory_max_rss"] = "UNAVAILABLE"
        return metadata

    def _utc_timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat()
