from __future__ import annotations

from pathlib import Path

from aigol.cli import aicli
from aigol.runtime.human_interface_runtime_entry_service import (
    CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_NOT_REQUIRED,
    run_human_interface_runtime_entry,
)
from aigol.runtime.platform_core_project_services import (
    GOVERNED_READ_ONLY_WORK_BOUND,
    PLATFORM_CORE_READ_ONLY_WORK_BINDING_VERSION,
    prepare_unified_human_interface_project_context,
    resolve_development_intent,
)
from aigol.runtime.platform_presentation_layer import (
    CANONICAL_PLATFORM_PRESENTATION_ARTIFACT_V1,
)


CREATED_AT = "2026-07-11T00:00:00Z"


def _reader(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str = "") -> str:
        return next(iterator)

    return read


def test_audit_only_produces_governed_read_only_result(tmp_path: Path) -> None:
    context = prepare_unified_human_interface_project_context(
        interface_name="test",
        session_id="G19-HI-10-AUDIT-ONLY",
        message=(
            "Perform an AUDIT_ONLY source-level architecture audit of replay certification. "
            "Do not modify code."
        ),
        runtime_root=tmp_path,
        workspace=".",
        created_at=CREATED_AT,
    )

    resolution = context["development_intent_resolution"]
    conversation = context["human_conversation_experience"]
    result = context["governed_read_only_work_result"]

    assert resolution["requested_work_type"] == "AUDIT_ONLY"
    assert resolution["prepared_work_type"] == "AUDIT_ONLY"
    assert resolution["summary_admissible"] is False
    assert resolution["runtime_binding_admissible"] is False
    assert resolution["read_only_work_binding_version"] == PLATFORM_CORE_READ_ONLY_WORK_BINDING_VERSION
    assert resolution["read_only_work_binding_admissible"] is True
    assert resolution["read_only_work_result_status"] == "GOVERNED_READ_ONLY_RESULT_READY"
    assert result["binding_status"] == GOVERNED_READ_ONLY_WORK_BOUND
    assert result["runtime_version"] == PLATFORM_CORE_READ_ONLY_WORK_BINDING_VERSION
    assert result["read_only"] is True
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["repository_mutated"] is False
    assert result["runtime_implementation_invoked"] is False
    assert result["canonical_presentation"]["artifact_type"] == CANONICAL_PLATFORM_PRESENTATION_ARTIFACT_V1
    assert result["canonical_presentation_hash"].startswith("sha256:")
    assert result["artifact_hash"].startswith("sha256:")
    assert conversation["response_mode"] == "READ_ONLY_RESULT"
    assert conversation["governed_read_only_work_result_hash"] == result["artifact_hash"]


def test_implementation_runtime_binding_remains_approval_gated() -> None:
    result = resolve_development_intent(
        message="Implement governance validation utility.\n\nwork_type: IMPLEMENTATION"
    )

    assert result["requested_work_type"] == "IMPLEMENTATION"
    assert result["summary_admissible"] is True
    assert result["runtime_binding_admissible"] is True
    assert result["read_only_work_binding_admissible"] is False
    assert result["requires_human_approval"] is True


def test_non_mutating_work_types_bind_to_read_only_services(tmp_path: Path) -> None:
    for work_type in ("REVIEW", "ANALYSIS", "CERTIFICATION", "DOCUMENTATION"):
        context = prepare_unified_human_interface_project_context(
            interface_name="test",
            session_id=f"G19-HI-10-{work_type}",
            message=(
                f"work_type: {work_type}\n"
                "Review where the platform presentation layer is implemented."
            ),
            runtime_root=tmp_path,
            workspace=".",
            created_at=CREATED_AT,
        )
        resolution = context["development_intent_resolution"]
        result = context["governed_read_only_work_result"]

        assert resolution["requested_work_type"] == work_type
        assert resolution["prepared_work_type"] == work_type
        assert resolution["summary_admissible"] is False
        assert resolution["runtime_binding_admissible"] is False
        assert resolution["read_only_work_binding_admissible"] is True
        assert result["binding_status"] == GOVERNED_READ_ONLY_WORK_BOUND
        assert result["read_only"] is True
        assert result["provider_invoked"] is False
        assert result["worker_invoked"] is False
        assert result["repository_mutated"] is False
        assert result["canonical_presentation"]["artifact_type"] == CANONICAL_PLATFORM_PRESENTATION_ARTIFACT_V1


def test_aicli_renders_platform_core_read_only_result_without_runtime(tmp_path: Path) -> None:
    calls: list[dict] = []
    output: list[str] = []

    result = aicli.run_reference_uhi_session(
        session_id="G19-HI-10-AICLI",
        runtime_root=tmp_path,
        workspace=".",
        input_reader=_reader(
            [
                "work_type: AUDIT_ONLY\nWhere is replay certification runtime implemented?",
                "/send",
                "/exit",
            ]
        ),
        output_writer=output.append,
        runtime_runner=lambda **kwargs: calls.append(kwargs) or {},
    )

    assert result["runtime_entered"] is False
    assert calls == []
    assert any("Governed read-only result" in line for line in output)
    assert any("provider_invoked: False" in line for line in output)
    assert any("worker_invoked: False" in line for line in output)


def test_runtime_entry_surfaces_read_only_result_without_implementation_runner(
    tmp_path: Path,
) -> None:
    calls: list[dict] = []

    result = run_human_interface_runtime_entry(
        interface_name="test",
        session_id="G19-HI-10-RUNTIME-ENTRY",
        human_requests=[
            "work_type: AUDIT_ONLY\nWhere is replay certification runtime implemented?"
        ],
        created_at=CREATED_AT,
        runtime_root=tmp_path,
        workspace=".",
        governed_runtime_runner=lambda *_args, **_kwargs: calls.append({}) or {},
    )

    assert result["canonical_runtime_entry_status"] == CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY_NOT_REQUIRED
    assert result["runtime_entered"] is False
    assert result["read_only_runtime_entered"] is True
    assert result["governed_read_only_work_result"]["binding_status"] == GOVERNED_READ_ONLY_WORK_BOUND
    assert result["governed_read_only_work_result"]["provider_invoked"] is False
    assert result["governed_read_only_work_result"]["worker_invoked"] is False
    assert calls == []
