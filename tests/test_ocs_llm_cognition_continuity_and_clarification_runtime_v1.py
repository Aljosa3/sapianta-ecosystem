"""Tests for AIGOL_OCS_LLM_COGNITION_CONTINUITY_AND_CLARIFICATION_V1."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aigol.runtime.cognition_comparison_runtime import run_cognition_comparison_runtime
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.multi_provider_cognition_runtime import (
    create_default_cognition_provider_contract,
    run_multi_provider_cognition_runtime,
)
from aigol.runtime.ocs_context_assembly_runtime import assemble_ocs_context
from aigol.runtime.ocs_llm_cognition_continuity_and_clarification_runtime import (
    CERTIFIED_CLASSIFICATION,
    COGNITION_CLARIFICATION_ARTIFACT_V1,
    COGNITION_CONTINUITY_ARTIFACT_V1,
    COGNITION_HISTORY_REFERENCE_V1,
    FINAL_CLASSIFICATION,
    STATUS_COMPLETED,
    STATUS_FAILED_CLOSED,
    reconstruct_ocs_llm_cognition_continuity_and_clarification_replay,
    run_ocs_llm_cognition_continuity_and_clarification,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-06-05T00:00:00Z"


def _conversation_source(source_id: str) -> dict:
    artifact = {
        "artifact_type": "HUMAN_REQUEST_ARTIFACT_V1",
        "artifact_id": source_id,
        "status": "REPLAY_VISIBLE",
        "summary": "Human asks for OCS LLM cognition continuity and clarification.",
        "replay_visible": True,
        "authority": False,
        "execution_requested": False,
        "worker_invoked": False,
        "governance_modified": False,
        "replay_modified": False,
    }
    artifact["artifact_hash"] = replay_hash(artifact)
    return artifact


def _context(tmp_path: Path, suffix: str) -> dict:
    capture = assemble_ocs_context(
        context_assembly_id=f"OCS-CONTEXT-CONTINUITY-{suffix}",
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"ocs_context_{suffix}",
        source_context={"conversation_context": [_conversation_source(f"HUMAN-REQUEST-CONTINUITY-{suffix}")]},
        source_chain_id=f"CHAIN-CONTINUITY-{suffix}",
        source_request_reference=f"HUMAN-REQUEST-CONTINUITY-{suffix}",
    )
    assert capture["fail_closed"] is False
    return capture["ocs_context_assembly_artifact"]


def _contracts() -> list[dict]:
    return [
        create_default_cognition_provider_contract(provider_id="provider-a", created_at=CREATED_AT),
        create_default_cognition_provider_contract(provider_id="provider-b", created_at=CREATED_AT),
        create_default_cognition_provider_contract(provider_id="provider-c", created_at=CREATED_AT),
    ]


def _provider_text(provider_id: str) -> str:
    return json.dumps(
        {
            "findings": [
                "Shared finding: provider cognition requires human review.",
                f"{provider_id} disagreement persists.",
            ],
            "assumptions": [f"{provider_id} assumption differs."],
            "alternatives": [f"{provider_id} alternative differs."],
            "risks": [f"{provider_id} risk differs."],
            "uncertainties": ["Shared uncertainty: target scope remains underspecified."],
            "confidence": "MEDIUM",
        },
        sort_keys=True,
    )


def _transports():
    transports = {}
    for provider_id in ("provider-a", "provider-b", "provider-c"):
        def call(_payload: dict, metadata: dict, provider_id: str = provider_id) -> dict:
            assert metadata["provider_role"] == "COGNITION_PROVIDER"
            return {"output_text": _provider_text(provider_id)}

        transports[provider_id] = call
    return transports


def _comparison(tmp_path: Path, suffix: str = "CURRENT") -> tuple[dict, dict]:
    multi = run_multi_provider_cognition_runtime(
        multi_provider_cognition_bundle_id=f"MULTI-PROVIDER-CONTINUITY-{suffix}",
        human_request="Assess continuity and clarification needs.",
        ocs_context_artifact=_context(tmp_path, suffix),
        provider_contracts=_contracts(),
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"multi_provider_{suffix}",
        transport_registry=_transports(),
    )
    assert multi["fail_closed"] is False
    comparison = run_cognition_comparison_runtime(
        cognition_comparison_id=f"COGNITION-COMPARISON-CONTINUITY-{suffix}",
        multi_provider_result_bundle=multi["result_bundle"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"comparison_{suffix}",
    )
    assert comparison["fail_closed"] is False
    return comparison["cognition_comparison_artifact"], multi["provider_results"][0]["llm_cognition_artifact"]


def _run(tmp_path: Path, **overrides):
    current_comparison, _prior_cognition = _comparison(tmp_path / "current", "CURRENT")
    args = {
        "continuity_id": "COGNITION-CONTINUITY-001",
        "clarification_id": "COGNITION-CLARIFICATION-001",
        "current_comparison_artifact": current_comparison,
        "created_at": CREATED_AT,
        "replay_dir": tmp_path / "continuity",
    }
    args.update(overrides)
    return run_ocs_llm_cognition_continuity_and_clarification(**args)


def test_continuity_and_clarification_generates_candidates_from_current_comparison(tmp_path):
    result = _run(tmp_path)
    history = result["history_reference"]
    continuity = result["cognition_continuity_artifact"]
    clarification = result["cognition_clarification_artifact"]
    replay = reconstruct_ocs_llm_cognition_continuity_and_clarification_replay(tmp_path / "continuity")

    assert result["final_classification"] == FINAL_CLASSIFICATION
    assert result["classification"] == CERTIFIED_CLASSIFICATION
    assert result["final_status"] == STATUS_COMPLETED
    assert history["artifact_type"] == COGNITION_HISTORY_REFERENCE_V1
    assert continuity["artifact_type"] == COGNITION_CONTINUITY_ARTIFACT_V1
    assert clarification["artifact_type"] == COGNITION_CLARIFICATION_ARTIFACT_V1
    assert clarification["clarification_required"] is True
    assert {item["trigger"] for item in clarification["clarification_candidates"]} >= {
        "DISAGREEMENT_THRESHOLD_EXCEEDED",
        "UNCERTAINTY_THRESHOLD_EXCEEDED",
        "LOW_COMPARISON_CONFIDENCE",
    }
    assert replay["clarification_required"] is True
    assert replay["clarification_candidate_count"] >= 3


def test_prior_cognition_and_comparison_are_reused_for_continuity_detection(tmp_path):
    current_comparison, _ = _comparison(tmp_path / "current", "CURRENT")
    prior_comparison, prior_cognition = _comparison(tmp_path / "prior", "PRIOR")

    result = run_ocs_llm_cognition_continuity_and_clarification(
        continuity_id="COGNITION-CONTINUITY-002",
        clarification_id="COGNITION-CLARIFICATION-002",
        current_comparison_artifact=current_comparison,
        prior_cognition_artifacts=[prior_cognition],
        prior_comparison_artifacts=[prior_comparison],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "continuity",
    )

    continuity = result["cognition_continuity_artifact"]
    clarification = result["cognition_clarification_artifact"]
    assert continuity["continuity_summary"]["prior_cognition_reused"] == 1
    assert continuity["continuity_summary"]["prior_comparisons_reused"] == 1
    assert continuity["stale_cognition"]
    assert continuity["repeated_uncertainty"]
    assert continuity["recurring_disagreement"]
    assert {item["trigger"] for item in clarification["clarification_candidates"]} >= {
        "REPEATED_UNCERTAINTY",
        "RECURRING_DISAGREEMENT",
    }


def test_prior_clarification_artifacts_are_history_reusable(tmp_path):
    first = _run(tmp_path / "first")
    current_comparison, _ = _comparison(tmp_path / "second", "SECOND")

    result = run_ocs_llm_cognition_continuity_and_clarification(
        continuity_id="COGNITION-CONTINUITY-003",
        clarification_id="COGNITION-CLARIFICATION-003",
        current_comparison_artifact=current_comparison,
        prior_clarification_artifacts=[first["cognition_clarification_artifact"]],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "continuity",
    )

    history = result["history_reference"]
    continuity = result["cognition_continuity_artifact"]
    assert history["history_counts"]["prior_clarification_artifact_count"] == 1
    assert continuity["continuity_summary"]["prior_clarifications_reused"] == 1


def test_boundary_preservation_no_execution_or_approval_created(tmp_path):
    result = _run(tmp_path)
    for artifact in (
        result["history_reference"],
        result["cognition_continuity_artifact"],
        result["cognition_clarification_artifact"],
        result,
    ):
        assert artifact["approval_created"] is False
        assert artifact["worker_invoked"] is False
        assert artifact["execution_requested"] is False
        assert artifact["governance_modified"] is False
        assert artifact["replay_modified"] is False
        assert all(value is False for value in artifact["authority_flags"].values())


def test_invalid_prior_clarification_fails_closed(tmp_path):
    current_comparison, _ = _comparison(tmp_path / "current", "CURRENT")
    result = run_ocs_llm_cognition_continuity_and_clarification(
        continuity_id="COGNITION-CONTINUITY-004",
        clarification_id="COGNITION-CLARIFICATION-004",
        current_comparison_artifact=current_comparison,
        prior_clarification_artifacts=[{"artifact_type": "BAD", "replay_visible": True}],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "continuity",
    )

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "invalid prior cognition clarification artifact" in result["failure_reason"]


def test_replay_tampering_is_detected(tmp_path):
    _run(tmp_path)
    path = tmp_path / "continuity" / "002_cognition_clarification_artifact.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["clarification_required"] = False
    path.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="replay hash mismatch"):
        reconstruct_ocs_llm_cognition_continuity_and_clarification_replay(tmp_path / "continuity")


def test_append_only_replay_collision_fails_closed(tmp_path):
    _run(tmp_path)
    result = _run(tmp_path / "second", replay_dir=tmp_path / "continuity")

    assert result["final_status"] == STATUS_FAILED_CLOSED
    assert "already exists" in result["failure_reason"]
