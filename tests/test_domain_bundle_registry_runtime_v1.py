"""Tests for AIGOL_DOMAIN_BUNDLE_REGISTRY_RUNTIME_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect
import json

import pytest

from aigol.runtime.domain_bundle_registry_runtime import (
    AIGOL_DOMAIN_BUNDLE_REGISTRY_RUNTIME_VERSION,
    DOMAIN_BUNDLE_REGISTRY_VERSION,
    DOMAIN_BUNDLE_RESOLVED,
    DOMAIN_BUNDLE_RESOLUTION_ARTIFACT_V1,
    FAILED_CLOSED,
    RESOLVABLE_EXECUTABLE,
    RESOLVABLE_NOT_EXECUTABLE,
    default_domain_bundle_registry,
    reconstruct_domain_bundle_resolution_replay,
    resolve_domain_bundle,
    resolve_domain_bundle_entry,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CREATED_AT = "2026-06-04T00:00:00+00:00"


def test_default_registry_resolves_required_domains_without_prompt_derived_filenames() -> None:
    registry = default_domain_bundle_registry()
    entries = {entry["domain_id"]: entry for entry in registry["entries"]}

    assert registry["runtime_version"] == AIGOL_DOMAIN_BUNDLE_REGISTRY_RUNTIME_VERSION
    assert registry["registry_version"] == DOMAIN_BUNDLE_REGISTRY_VERSION
    assert set(entries) == {"MARKETING", "SERVER_MANAGEMENT", "TRADING", "HEALTHCARE"}
    assert entries["MARKETING"]["factory_resolution_status"] == RESOLVABLE_EXECUTABLE
    assert entries["SERVER_MANAGEMENT"]["factory_resolution_status"] == RESOLVABLE_NOT_EXECUTABLE
    assert entries["TRADING"]["factory_resolution_status"] == RESOLVABLE_NOT_EXECUTABLE
    assert entries["HEALTHCARE"]["factory_resolution_status"] == RESOLVABLE_NOT_EXECUTABLE
    assert entries["MARKETING"]["artifact_paths"] == [
        "governance/MARKETING_DOMAIN_FOUNDATION_V1.md",
        "governance/MARKETING_DOMAIN_MODEL_V1.md",
        "governance/MARKETING_DOMAIN_CERTIFICATION.json",
        "aigol/runtime/marketing_domain_runtime.py",
        "tests/test_marketing_domain_runtime_v1.py",
    ]
    assert registry["registry_hash"].startswith("sha256:")
    assert registry["artifact_hash"].startswith("sha256:")


@pytest.mark.parametrize(
    ("domain_id", "expected_status"),
    [
        ("MARKETING", RESOLVABLE_EXECUTABLE),
        ("SERVER_MANAGEMENT", RESOLVABLE_NOT_EXECUTABLE),
        ("TRADING", RESOLVABLE_NOT_EXECUTABLE),
        ("HEALTHCARE", RESOLVABLE_NOT_EXECUTABLE),
    ],
)
def test_resolves_domain_bundle_with_replay(tmp_path, domain_id: str, expected_status: str) -> None:
    capture = resolve_domain_bundle(
        resolution_id=f"DOMAIN-BUNDLE-RESOLUTION-{domain_id}",
        domain_id=domain_id,
        created_at=CREATED_AT,
        replay_dir=tmp_path / domain_id.lower(),
    )
    reconstructed = reconstruct_domain_bundle_resolution_replay(tmp_path / domain_id.lower())

    assert capture["resolution_status"] == DOMAIN_BUNDLE_RESOLVED
    assert capture["artifact_type"] == DOMAIN_BUNDLE_RESOLUTION_ARTIFACT_V1
    assert capture["domain_id"] == domain_id
    assert capture["factory_resolution_status"] == expected_status
    assert capture["registry_hash"].startswith("sha256:")
    assert capture["registry_entry_hash"].startswith("sha256:")
    assert reconstructed["resolution_status"] == DOMAIN_BUNDLE_RESOLVED
    assert reconstructed["domain_id"] == domain_id
    assert reconstructed["registry_hash"] == capture["registry_hash"]
    assert reconstructed["registry_entry_hash"] == capture["registry_entry_hash"]
    assert reconstructed["replay_artifact_count"] == 2
    assert reconstructed["provider_invoked"] is False
    assert reconstructed["worker_invoked"] is False
    assert reconstructed["execution_requested"] is False
    assert reconstructed["dispatch_requested"] is False


def test_marketing_entry_resolves_as_current_executable_bundle_identity() -> None:
    entry = resolve_domain_bundle_entry(
        domain_id="MARKETING",
        bundle_id="MARKETING_EXECUTABLE_DOMAIN_BUNDLE_V1",
        require_executable=True,
    )

    assert entry["domain_id"] == "MARKETING"
    assert entry["bundle_id"] == "MARKETING_EXECUTABLE_DOMAIN_BUNDLE_V1"
    assert entry["factory_resolution_status"] == RESOLVABLE_EXECUTABLE
    assert "governance/MARKETING_DOMAIN_FOUNDATION_V1.md" in entry["artifact_paths"]


def test_non_executable_domain_fails_closed_when_executable_required(tmp_path) -> None:
    capture = resolve_domain_bundle(
        resolution_id="DOMAIN-BUNDLE-RESOLUTION-SERVER-MANAGEMENT-EXECUTABLE",
        domain_id="SERVER_MANAGEMENT",
        require_executable=True,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "server_management_executable",
    )
    reconstructed = reconstruct_domain_bundle_resolution_replay(tmp_path / "server_management_executable")

    assert capture["resolution_status"] == FAILED_CLOSED
    assert capture["fail_closed"] is True
    assert "not executable" in capture["failure_reason"]
    assert reconstructed["resolution_status"] == FAILED_CLOSED
    assert reconstructed["failure_reason"] == capture["failure_reason"]


def test_unknown_domain_fails_closed_with_replay(tmp_path) -> None:
    capture = resolve_domain_bundle(
        resolution_id="DOMAIN-BUNDLE-RESOLUTION-LEGAL",
        domain_id="LEGAL",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "legal",
    )

    assert capture["fail_closed"] is True
    assert "unknown domain bundle" in capture["failure_reason"]


def test_registry_hash_mismatch_fails_closed(tmp_path) -> None:
    registry = default_domain_bundle_registry()
    registry["registry_hash"] = "sha256:bad"

    capture = resolve_domain_bundle(
        resolution_id="DOMAIN-BUNDLE-RESOLUTION-HASH-MISMATCH",
        domain_id="MARKETING",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "hash_mismatch",
        registry=registry,
    )

    assert capture["fail_closed"] is True
    assert "registry hash mismatch" in capture["failure_reason"]


def test_duplicate_domain_registration_fails_closed(tmp_path) -> None:
    registry = default_domain_bundle_registry()
    duplicate = deepcopy(registry["entries"][0])
    duplicate["bundle_id"] = "MARKETING_DUPLICATE_EXECUTABLE_DOMAIN_BUNDLE_V1"
    duplicate.pop("entry_hash")
    duplicate["entry_hash"] = replay_hash({key: value for key, value in duplicate.items() if key != "entry_hash"})
    registry["entries"].append(duplicate)
    registry.pop("registry_hash")
    registry.pop("artifact_hash")

    capture = resolve_domain_bundle(
        resolution_id="DOMAIN-BUNDLE-RESOLUTION-DUPLICATE",
        domain_id="MARKETING",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "duplicate",
        registry=registry,
    )

    assert capture["fail_closed"] is True
    assert "duplicate domain registration" in capture["failure_reason"]


def test_reconstruction_detects_corrupt_domain_bundle_resolution_replay(tmp_path) -> None:
    resolve_domain_bundle(
        resolution_id="DOMAIN-BUNDLE-RESOLUTION-CORRUPT",
        domain_id="MARKETING",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt",
    )
    path = tmp_path / "corrupt" / "000_domain_bundle_resolution_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["domain_id"] = "CORRUPTED"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_domain_bundle_resolution_replay(tmp_path / "corrupt")


def test_domain_bundle_registry_runtime_has_no_provider_worker_execution_or_filesystem_creation() -> None:
    import aigol.runtime.domain_bundle_registry_runtime as registry_runtime

    source = inspect.getsource(registry_runtime)

    assert "OpenAIProviderAdapter" not in source
    assert "run_provider_attachment(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
    assert ".open(\"x\"" not in source
