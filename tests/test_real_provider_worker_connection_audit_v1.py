"""Checks for REAL_PROVIDER_WORKER_CONNECTION_AUDIT_REPORT_V1."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / ".github/governance/review/REAL_PROVIDER_WORKER_CONNECTION_AUDIT_REPORT_V1.json"


def _load() -> dict:
    return json.loads(REPORT.read_text(encoding="utf-8"))


def test_real_provider_worker_connection_audit_final_outputs() -> None:
    report = _load()
    outputs = report["final_outputs"]

    assert report["artifact_type"] == "REAL_PROVIDER_WORKER_CONNECTION_AUDIT_REPORT_V1"
    assert outputs["OPENAI_CONNECTION_READINESS"].startswith("72_HIGH")
    assert outputs["CLAUDE_CONNECTION_READINESS"].startswith("46_ARCHITECTURE_READY")
    assert outputs["MISTRAL_CONNECTION_READINESS"].startswith("34_GENERIC_ARCHITECTURE")
    assert "REAL_PROVIDER_WORKER_ADAPTER" in outputs["MISSING_COMPONENTS"]
    assert outputs["DUPLICATE_IMPLEMENTATION_RISK"] == (
        "HIGH_IF_WORKER_LIFECYCLE_OR_PACKAGE_SCHEMA_IS_REIMPLEMENTED"
    )
    assert outputs["SHORTEST_PATH_TO_REAL_PROVIDER"].startswith("OPENAI_EXTERNAL_WORKER_PROVIDER_ADAPTER_V1")


def test_real_provider_worker_connection_audit_marks_existing_components_do_not_rebuild() -> None:
    report = _load()
    matrix = report["component_existence_matrix"]
    duplicates = set(report["duplicate_components_already_implemented"])

    assert matrix["task_package_generation"]["exists"] is True
    assert matrix["task_package_generation"]["do_not_implement_again"] is True
    assert matrix["result_package_generation"]["exists"] is True
    assert matrix["result_package_generation"]["do_not_implement_again"] is True
    assert matrix["worker_invocation_lifecycle"]["exists"] is True
    assert matrix["worker_execution_lifecycle"]["exists"] is True
    assert "EXTERNAL_WORKER_TASK_PACKAGE_V1 generation" in duplicates
    assert "EXTERNAL_WORKER_RESULT_PACKAGE_V1 generation" in duplicates
    assert "OpenAI API invocation and OpenAI proposal-source adapter surfaces" in duplicates


def test_real_provider_worker_connection_audit_provider_classifications() -> None:
    report = _load()
    providers = report["provider_readiness"]

    assert providers["openai"]["adapter_already_exists"] is True
    assert providers["openai"]["api_integration_missing"] is False
    assert providers["openai"]["worker_package_integration_missing"] is True
    assert providers["claude"]["adapter_already_exists"] is False
    assert providers["claude"]["api_integration_missing"] is True
    assert providers["mistral"]["adapter_already_exists"] is False
    assert providers["mistral"]["api_integration_missing"] is True
