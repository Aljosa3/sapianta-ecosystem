"""Tests for REAL_METADATA_INSPECTION_PROVIDER_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

from aigol.runtime.providers import MetadataInspectionProvider
from aigol.runtime.transport.serialization import replay_hash


FIXED_TIMESTAMP = "2026-05-26T00:00:00+00:00"


def _provider(tmp_path) -> MetadataInspectionProvider:
    return MetadataInspectionProvider(repository_root=tmp_path, timestamp_provider=lambda: FIXED_TIMESTAMP)


def test_runtime_inspection_success(tmp_path) -> None:
    governance = tmp_path / "docs" / "governance"
    governance.mkdir(parents=True)
    (governance / "CONSTITUTIONAL_ARCHITECTURE_SPEC_V1.md").write_text("spec", encoding="utf-8")
    (governance / "CANONICAL_LAYER_MODEL.md").write_text("layers", encoding="utf-8")

    evidence = _provider(tmp_path).inspect_runtime()

    assert evidence["operation"] == "inspect_runtime"
    assert evidence["timestamp"] == FIXED_TIMESTAMP
    assert evidence["status"] == "RUNTIME_METADATA_INSPECTED"
    assert evidence["metadata"]["runtime_version"]["provider_name"] == "REAL_METADATA_INSPECTION_PROVIDER_V1"
    assert evidence["metadata"]["provider_availability"]["inspect_process"] is True
    assert evidence["metadata"]["governance_artifact_visibility"]["constitutional_architecture_spec"] is True
    assert evidence["metadata"]["governance_artifact_visibility"]["governance_lineage_model"] is False
    assert evidence["metadata"]["replay_capability_indicators"]["evidence_hash"] is True


def test_environment_inspection_success(tmp_path) -> None:
    evidence = _provider(tmp_path).inspect_environment()

    assert evidence["operation"] == "inspect_environment"
    assert evidence["status"] == "ENVIRONMENT_METADATA_INSPECTED"
    assert set(evidence["metadata"]) == {"os_name", "python_version", "working_directory", "timezone"}
    assert evidence["metadata"]["os_name"]
    assert evidence["metadata"]["python_version"]
    assert "environment_variables" in evidence["blocked_fields"]


def test_process_inspection_success(tmp_path) -> None:
    evidence = _provider(tmp_path).inspect_process()

    assert evidence["operation"] == "inspect_process"
    assert evidence["status"] == "PROCESS_METADATA_INSPECTED"
    assert set(evidence["metadata"]) == {"process_id", "process_start_timestamp", "process_metadata"}
    assert isinstance(evidence["metadata"]["process_id"], int)
    assert "memory_max_rss" in evidence["metadata"]["process_metadata"]


def test_secret_filtering_enforcement(tmp_path) -> None:
    provider = _provider(tmp_path)

    evidence = provider._evidence(
        "inspect_runtime",
        "RUNTIME_METADATA_INSPECTED",
        "runtime metadata inspected",
        {
            "runtime_version": {"schema_version": "1.0"},
            "api_key": "must-not-appear",
            "password": "must-not-appear",
            "credential_hint": "must-not-appear",
        },
    )

    assert "api_key" not in evidence["metadata"]
    assert "password" not in evidence["metadata"]
    assert "credential_hint" not in evidence["metadata"]
    assert {"api_key", "password", "credential_hint"} <= set(evidence["blocked_fields"])
    assert "must-not-appear" not in repr(evidence)


def test_fail_closed_unavailable_metadata(tmp_path, monkeypatch) -> None:
    provider = _provider(tmp_path)

    monkeypatch.setattr(provider, "_linux_process_start_timestamp", lambda: "UNAVAILABLE")
    monkeypatch.setattr(provider, "_process_metadata", lambda: {"memory_max_rss": "UNAVAILABLE"})

    evidence = provider.inspect_process()

    assert evidence["metadata"]["process_start_timestamp"] == "UNAVAILABLE"
    assert evidence["metadata"]["process_metadata"]["memory_max_rss"] == "UNAVAILABLE"
    assert evidence["status"] == "PROCESS_METADATA_INSPECTED"


def test_deterministic_evidence_structure(tmp_path) -> None:
    first = _provider(tmp_path).inspect_environment()
    second = _provider(tmp_path).inspect_environment()

    assert first == second
    assert set(first) == {
        "operation",
        "timestamp",
        "status",
        "inspected_fields",
        "blocked_fields",
        "reason",
        "metadata",
        "evidence_hash",
    }
    without_hash = deepcopy(first)
    evidence_hash = without_hash.pop("evidence_hash")
    assert evidence_hash == replay_hash(without_hash)


def test_blocked_unsafe_fields(tmp_path) -> None:
    evidence = _provider(tmp_path).inspect_runtime()

    assert {
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
    } <= set(evidence["blocked_fields"])


def test_no_mutation_monitoring_or_orchestration_surface() -> None:
    public_methods = {
        name
        for name, value in inspect.getmembers(MetadataInspectionProvider, predicate=inspect.isfunction)
        if not name.startswith("_")
    }
    source = inspect.getsource(MetadataInspectionProvider)

    assert public_methods == {"inspect_runtime", "inspect_environment", "inspect_process"}
    assert "import subprocess" not in source
    assert "from subprocess" not in source
    assert "Popen" not in source
    assert "os.system" not in source
    assert "kill" not in source
    assert "async " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source
    assert "socket" not in source
    assert "walk(" not in source
    assert "rglob" not in source
    assert ".write" not in source
