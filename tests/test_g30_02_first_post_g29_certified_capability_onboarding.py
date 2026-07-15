"""Focused G30-02 first post-G29 capability onboarding tests."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from aigol.runtime.certified_capability_invocation_binding_runtime import (
    CERTIFIED_CAPABILITY_INVOCATION_COMPLETED,
    PLATFORM_CAPABILITY_COMPOSITION_COVERAGE,
    invoke_certified_capability,
    reconstruct_certified_capability_invocation_replay,
)
from aigol.runtime.explicit_canonical_artifact_ingress_runtime import (
    reconstruct_explicit_canonical_artifact_ingress,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_composition_coverage import (
    PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_ARTIFACT_V1,
    PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_REQUEST_ARTIFACT_V1,
    create_platform_capability_composition_coverage_request,
    validate_platform_capability_composition_coverage_request,
)
from aigol.runtime.platform_capability_certification_registry import (
    lookup_platform_capability_certification,
)
from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
)
from aigol.runtime.platform_knowledge_runtime import query_platform_knowledge
from aigol.runtime.project_context_semantic_capability_route import (
    reconstruct_project_context_semantic_capability_route,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-07-15T00:00:00Z"
SESSION_ID = "SESSION-G30-02"
REQUEST = (
    "work_type: analysis. Analyze Platform capability composition coverage "
    "for reusable certified capabilities."
)


def _request() -> dict:
    return create_platform_capability_composition_coverage_request(
        request_id="G30-02-COMPOSITION-COVERAGE-REQUEST",
        query="Assess reusable Platform capability coverage and residual gaps.",
        created_at=CREATED_AT,
    )


def _wrapper(tmp_path: Path, artifact: dict | None = None) -> Path:
    wrapper = {
        "replay_index": 0,
        "replay_step": "composition_coverage_request_recorded",
        "artifact": deepcopy(artifact or _request()),
    }
    wrapper["wrapper_hash"] = replay_hash(wrapper)
    path = tmp_path / "canonical-input" / "000_composition_coverage_request_recorded.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(wrapper, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def test_canonical_request_is_immutable_and_tamper_evident() -> None:
    artifact = _request()

    assert artifact["artifact_type"] == (
        PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_REQUEST_ARTIFACT_V1
    )
    assert artifact["read_only"] is True
    assert artifact["provider_invoked"] is False
    assert artifact["worker_invoked"] is False
    assert artifact["repository_mutated"] is False
    assert validate_platform_capability_composition_coverage_request(artifact) == artifact

    tampered = deepcopy(artifact)
    tampered["query"] = "tampered"
    with pytest.raises(FailClosedRuntimeError, match="query hash mismatch"):
        validate_platform_capability_composition_coverage_request(tampered)


def test_g28_invokes_existing_read_only_capability_and_reconstructs(tmp_path: Path) -> None:
    request = _request()
    knowledge = query_platform_knowledge(
        query=REQUEST,
        capability_identifier=PLATFORM_CAPABILITY_COMPOSITION_COVERAGE,
    )
    capture = invoke_certified_capability(
        invocation_id="G30-02-DIRECT-G28",
        session_id=SESSION_ID,
        platform_knowledge_response=knowledge,
        platform_knowledge_response_reference="G30-02-KNOWLEDGE",
        discovered_capability_identifier=PLATFORM_CAPABILITY_COMPOSITION_COVERAGE,
        capability_inputs={
            "composition_coverage_request_artifact": request,
            "composition_coverage_request_reference": request["request_id"],
            "composition_coverage_request_hash": request["artifact_hash"],
        },
        invoked_by="PLATFORM_CORE",
        invoked_at=CREATED_AT,
        replay_dir=tmp_path / "g28",
    )
    reconstructed = reconstruct_certified_capability_invocation_replay(tmp_path / "g28")

    assert capture["invocation_status"] == CERTIFIED_CAPABILITY_INVOCATION_COMPLETED
    assert capture["capability_output_artifact"]["artifact_type"] == (
        PLATFORM_CAPABILITY_COMPOSITION_COVERAGE_ARTIFACT_V1
    )
    assert reconstructed["capability_identifier"] == (
        PLATFORM_CAPABILITY_COMPOSITION_COVERAGE
    )
    assert capture["provider_invoked"] is False
    assert capture["worker_invoked"] is False
    assert capture["repository_mutated"] is False

    native_replay = (
        tmp_path
        / "g28"
        / "capability_runtime"
        / "000_platform_capability_composition_coverage_recorded.json"
    )
    wrapper = json.loads(native_replay.read_text(encoding="utf-8"))
    wrapper["artifact"]["query"] = "tampered"
    native_replay.write_text(json.dumps(wrapper), encoding="utf-8")
    with pytest.raises(FailClosedRuntimeError, match="wrapper hash mismatch"):
        reconstruct_certified_capability_invocation_replay(tmp_path / "g28")


def test_natural_language_traverses_g29_ingress_g28_presentation_and_replay(
    tmp_path: Path,
) -> None:
    reference = _wrapper(tmp_path)
    context = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id=SESSION_ID,
        message=REQUEST,
        runtime_root=tmp_path / "runtime",
        workspace=tmp_path,
        created_at=CREATED_AT,
        explicit_canonical_artifact_references=[str(reference)],
    )
    route = context["semantic_capability_runtime_route"]
    result = context["governed_read_only_work_result"]

    assert route["route_status"] == "SEMANTIC_CAPABILITY_ROUTE_COMPLETED"
    assert route["selected_capability_identifier"] == (
        PLATFORM_CAPABILITY_COMPOSITION_COVERAGE
    )
    assert route["canonical_platform_presentation"]["presentation_status"] in {
        "PRESENTATION_READY",
        "PRESENTATION_MISSING_EVIDENCE",
    }
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["repository_mutated"] is False

    ingress = reconstruct_explicit_canonical_artifact_ingress(
        context["explicit_canonical_artifact_ingress_reference"]
    )
    reconstructed_route = reconstruct_project_context_semantic_capability_route(
        route["replay_reference"]
    )
    assert ingress["downstream_route_hash"] == route["artifact_hash"]
    assert reconstructed_route["artifact_hash"] == route["artifact_hash"]


def test_certification_record_includes_g30_onboarding_evidence() -> None:
    record = lookup_platform_capability_certification(
        PLATFORM_CAPABILITY_COMPOSITION_COVERAGE
    )

    assert record["certification_status"] == "CERTIFIED"
    assert (
        "docs/governance/G30_02_FIRST_POST_G29_CERTIFIED_CAPABILITY_ONBOARDING.md"
        in record["certification_evidence"]
    )
