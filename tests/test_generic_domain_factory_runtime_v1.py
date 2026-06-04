"""Tests for AIGOL_GENERIC_DOMAIN_FACTORY_RUNTIME_V1."""

from __future__ import annotations

import inspect

import pytest

from aigol.cli.aigol_cli import run_interactive_conversation
from aigol.runtime.domain_bundle_registry_runtime import (
    default_domain_bundle_registry,
    domain_bundle_contents,
    resolve_domain_bundle_entry,
)
from aigol.runtime.executable_domain_bundle_runtime import (
    EXECUTABLE_BUNDLE_VERIFIED,
    reconstruct_executable_domain_bundle_replay,
)
from aigol.runtime.generic_domain_factory_runtime import create_generic_executable_domain_bundle
from test_worker_result_validation_runtime_v1 import CREATED_AT, _args, _input_sequence, _validate


def _entry(domain_id: str) -> dict:
    return resolve_domain_bundle_entry(domain_id=domain_id, require_executable=True)


def _workspace(tmp_path) -> None:
    (tmp_path / "governance").mkdir(exist_ok=True)
    (tmp_path / "aigol" / "runtime").mkdir(parents=True, exist_ok=True)
    (tmp_path / "tests").mkdir(exist_ok=True)


@pytest.mark.parametrize(
    ("prompt", "domain_id"),
    [
        ("Create a marketing domain.", "MARKETING"),
        ("Create a server management domain.", "SERVER_MANAGEMENT"),
        ("Create a trading domain.", "TRADING"),
        ("Create a healthcare domain.", "HEALTHCARE"),
    ],
)
def test_generic_domain_factory_creates_registry_defined_bundle(tmp_path, prompt: str, domain_id: str) -> None:
    validation = _validate(tmp_path, prompt=prompt, suffix=domain_id.lower())
    _workspace(tmp_path)
    entry = _entry(domain_id)
    replay_dir = tmp_path / f"generic_factory_{domain_id.lower()}"

    result = create_generic_executable_domain_bundle(
        generic_domain_factory_runtime_id=f"GENERIC-DOMAIN-FACTORY-{domain_id}",
        domain_id=domain_id,
        worker_result_validation_artifact=validation["worker_result_validation_artifact"],
        worker_result_validation_replay_reference=validation["worker_result_validation_replay_reference"],
        workspace_root=tmp_path,
        created_by="AIGOL_GOVERNANCE",
        created_at=CREATED_AT,
        replay_dir=replay_dir,
    )
    reconstructed = reconstruct_executable_domain_bundle_replay(replay_dir)
    contents = domain_bundle_contents(entry)

    assert result["domain_id"] == domain_id
    assert result["executable_bundle_verification_status"] == EXECUTABLE_BUNDLE_VERIFIED
    assert result["artifact_paths"] == entry["artifact_paths"]
    assert reconstructed["executable_bundle_verification_status"] == EXECUTABLE_BUNDLE_VERIFIED
    for path, content in contents.items():
        assert (tmp_path / path).read_text(encoding="utf-8") == content


@pytest.mark.parametrize(
    ("prompt", "domain_id"),
    [
        ("Create a marketing domain.", "MARKETING"),
        ("Create a server management domain.", "SERVER_MANAGEMENT"),
        ("Create a trading domain.", "TRADING"),
        ("Create a healthcare domain.", "HEALTHCARE"),
    ],
)
def test_interactive_cli_reaches_governed_executable_bundle_generation_for_domains(
    tmp_path,
    prompt: str,
    domain_id: str,
) -> None:
    output: list[str] = []
    result = run_interactive_conversation(
        _args(tmp_path, session_id=f"SESSION-CLI-GENERIC-DOMAIN-FACTORY-{domain_id}-000001"),
        input_func=_input_sequence([prompt, "exit"]),
        output_func=output.append,
    )
    entry = _entry(domain_id)

    assert result["executable_bundle_authorized"] is True
    assert result["artifacts_created"] is True
    assert result["executable_bundle_verified"] is True
    assert result["post_execution_replay_reviewed"] is True
    assert result["terminated"] is True
    assert all((tmp_path / path).exists() for path in entry["artifact_paths"])
    assert any("Executable Bundle Authorization Status: EXECUTABLE_BUNDLE_AUTHORIZED" in chunk for chunk in output)


def test_generic_domain_factory_fails_closed_on_existing_target(tmp_path) -> None:
    validation = _validate(tmp_path, prompt="Create a healthcare domain.", suffix="healthcare-existing")
    _workspace(tmp_path)
    existing = tmp_path / "governance" / "HEALTHCARE_DOMAIN_FOUNDATION_V1.md"
    existing.write_text("existing\n", encoding="utf-8")

    result = create_generic_executable_domain_bundle(
        generic_domain_factory_runtime_id="GENERIC-DOMAIN-FACTORY-HEALTHCARE-EXISTING",
        domain_id="HEALTHCARE",
        worker_result_validation_artifact=validation["worker_result_validation_artifact"],
        worker_result_validation_replay_reference=validation["worker_result_validation_replay_reference"],
        workspace_root=tmp_path,
        created_by="AIGOL_GOVERNANCE",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "generic_factory_healthcare_existing",
    )

    assert result["fail_closed"] is True
    assert "target already exists" in result["failure_reason"]


def test_generic_domain_factory_uses_registry_and_has_no_ocs_or_semantic_cognition_changes() -> None:
    import aigol.runtime.generic_domain_factory_runtime as runtime

    source = inspect.getsource(runtime)

    assert "default_domain_bundle_registry" not in source
    assert "resolve_domain_bundle(" in source
    assert "ocs_functionality_enabled" in source
    assert "semantic_cognition_changed" in source
    assert "OpenAIProviderAdapter" not in source
    assert "cognition_runtime" not in source
    assert "semantic_context" not in source
    assert {entry["domain_id"] for entry in default_domain_bundle_registry()["entries"]} == {
        "MARKETING",
        "SERVER_MANAGEMENT",
        "TRADING",
        "HEALTHCARE",
    }
