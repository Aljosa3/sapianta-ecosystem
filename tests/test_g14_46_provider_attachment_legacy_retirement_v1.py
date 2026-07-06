"""Regression coverage for G14_46_PROVIDER_ATTACHMENT_LEGACY_RETIREMENT_V1."""

from __future__ import annotations

from pathlib import Path

import aigol.runtime.openai_provider_adapter as legacy_openai_adapter
import aigol.runtime.provider_attachment as legacy_provider_attachment


REPO_ROOT = Path(__file__).resolve().parents[1]
PRODUCTION_ROOT = REPO_ROOT / "aigol"
CERTIFIED_ATTACHMENT = REPO_ROOT / "aigol/provider/certified_provider_attachment.py"
PROVIDER_RUNTIME = REPO_ROOT / "aigol/provider/provider_runtime.py"
LEGACY_COMPATIBILITY_MODULES = {
    REPO_ROOT / "aigol/runtime/provider_attachment.py",
    REPO_ROOT / "aigol/runtime/openai_provider_adapter.py",
}
PROVIDER_RUNTIME_ONLY = {
    PROVIDER_RUNTIME,
    CERTIFIED_ATTACHMENT,
}


def _production_sources() -> list[Path]:
    return sorted(path for path in PRODUCTION_ROOT.rglob("*.py") if "__pycache__" not in path.parts)


def test_legacy_provider_attachment_modules_are_explicitly_compatibility_only() -> None:
    assert legacy_provider_attachment.LEGACY_PROVIDER_ATTACHMENT_CLASSIFICATION == "LEGACY_COMPATIBILITY"
    assert legacy_provider_attachment.PRODUCTION_PROVIDER_ROUTING_ALLOWED is False
    assert legacy_provider_attachment.CERTIFIED_RUNTIME_REACHABLE is False

    assert legacy_openai_adapter.LEGACY_PROVIDER_ATTACHMENT_CLASSIFICATION == "LEGACY_COMPATIBILITY"
    assert legacy_openai_adapter.PRODUCTION_PROVIDER_ROUTING_ALLOWED is False
    assert legacy_openai_adapter.CERTIFIED_RUNTIME_REACHABLE is False


def test_production_code_cannot_import_legacy_provider_attachment_paths() -> None:
    forbidden_tokens = (
        "from aigol.runtime.provider_attachment import",
        "import aigol.runtime.provider_attachment",
        "from aigol.runtime.openai_provider_adapter import",
        "import aigol.runtime.openai_provider_adapter",
        "attach_real_provider_response(",
        "invoke_openai_provider_adapter(",
    )
    offenders: list[str] = []
    for path in _production_sources():
        if path in LEGACY_COMPATIBILITY_MODULES:
            continue
        source = path.read_text(encoding="utf-8")
        if any(token in source for token in forbidden_tokens):
            offenders.append(str(path.relative_to(REPO_ROOT)))

    assert offenders == []


def test_production_provider_invocation_uses_certified_attachment_only() -> None:
    direct_runtime_callers: list[str] = []
    certified_callers: list[str] = []
    for path in _production_sources():
        if path in PROVIDER_RUNTIME_ONLY:
            continue
        source = path.read_text(encoding="utf-8")
        if "run_provider_attachment(" in source:
            direct_runtime_callers.append(str(path.relative_to(REPO_ROOT)))
        if "run_certified_provider_attachment(" in source:
            certified_callers.append(str(path.relative_to(REPO_ROOT)))

    assert direct_runtime_callers == []
    assert "aigol/runtime/openai_external_worker_provider_adapter.py" in certified_callers
    assert "aigol/runtime/provider_assisted_intent_classification.py" in certified_callers
    assert "aigol/runtime/provider_assisted_conversation_runtime.py" in certified_callers


def test_repository_has_one_production_provider_attachment_boundary() -> None:
    boundary_definitions = []
    for path in _production_sources():
        if path in LEGACY_COMPATIBILITY_MODULES or path == PROVIDER_RUNTIME:
            continue
        source = path.read_text(encoding="utf-8")
        if "def run_certified_provider_attachment(" in source:
            boundary_definitions.append(str(path.relative_to(REPO_ROOT)))
        assert "def attach_real_provider_response(" not in source
        assert "def invoke_openai_provider_adapter(" not in source

    assert boundary_definitions == ["aigol/provider/certified_provider_attachment.py"]


def test_external_worker_adapter_is_routed_through_certified_attachment() -> None:
    source = (REPO_ROOT / "aigol/runtime/openai_external_worker_provider_adapter.py").read_text(
        encoding="utf-8"
    )

    assert "run_certified_provider_attachment(" in source
    assert "invoke_openai_provider_adapter(" not in source
    assert "attach_real_provider_response(" not in source
    assert 'PROVIDER_ATTACHMENT_BOUNDARY = "CERTIFIED_PROVIDER_ATTACHMENT"' in source
