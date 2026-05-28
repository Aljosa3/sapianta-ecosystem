"""Tests for MINIMAL_EXECUTABLE_REAL_LLM_SESSION_V1."""

from __future__ import annotations

from copy import deepcopy
import inspect

from aigol.runtime.minimal_executable_real_llm_session import (
    BOUNDED_SEMANTIC_CONTRIBUTION,
    COMPLETED,
    FAILED,
    create_llm_session_ingress,
    execute_minimal_real_llm_session,
    external_llm_contribution_hash,
    normalize_llm_contribution,
    reconstruct_minimal_real_llm_session_replay,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-05-28T00:00:00+00:00"


def _contribution(**overrides) -> dict:
    contribution = {
        "contribution_id": "LLM-CONTRIBUTION-000001",
        "contribution_text": "  Propose bounded metadata inspection for governance review. ",
        "contribution_type": BOUNDED_SEMANTIC_CONTRIBUTION,
        "requested_capabilities": ["metadata_inspection_provider"],
        "proposed_contract_reference": "contract:MINIMAL-REAL-LLM-SESSION-000001",
        "created_at": CREATED_AT,
    }
    contribution.update(overrides)
    contribution["response_hash"] = external_llm_contribution_hash(contribution)
    return contribution


def _run(tmp_path, contribution: dict | None = None) -> dict:
    model_contribution = _contribution() if contribution is None else contribution

    def infer(ingress: dict) -> dict:
        assert ingress["governance_mode"] == "BOUNDED_LLM_SESSION"
        return deepcopy(model_contribution)

    return execute_minimal_real_llm_session(
        session_id="LLM-SESSION-000001",
        request_id="LLM-REQUEST-000001",
        human_input="  Please produce one bounded governance-visible contribution. ",
        contribution_callable=infer,
        created_at=CREATED_AT,
        replay_dir=tmp_path,
    )


def test_bounded_lifecycle_completion(tmp_path) -> None:
    capture = _run(tmp_path)

    assert capture["egress"]["status"] == COMPLETED
    assert capture["egress"]["continuity_validated"] is True
    assert capture["egress"]["authority_escalation_detected"] is False
    assert capture["egress"]["replay_chain_complete"] is True
    assert capture["egress"]["bounded_interaction"] is True
    assert capture["egress"]["governance_authority_delegated"] is False
    assert capture["egress"]["execution_authority_activated"] is False


def test_deterministic_replay_artifact_creation(tmp_path) -> None:
    first = _run(tmp_path / "first")
    second = _run(tmp_path / "second")

    assert first["ingress"] == second["ingress"]
    assert first["normalized_contribution"] == second["normalized_contribution"]
    assert first["validation"] == second["validation"]
    assert first["egress"] == second["egress"]


def test_replay_capture_is_append_only_and_ordered(tmp_path) -> None:
    _run(tmp_path)
    lineage = reconstruct_minimal_real_llm_session_replay(tmp_path)

    assert lineage["replay_artifact_count"] == 5
    assert lineage["replay_steps"] == [
        "ingress",
        "raw_contribution",
        "normalized_contribution",
        "validation",
        "egress",
    ]
    assert lineage["append_only_valid"] is True
    assert lineage["lineage_valid"] is True
    assert lineage["replay_hash"].startswith("sha256:")


def test_lineage_continuity_correctness(tmp_path) -> None:
    capture = _run(tmp_path)

    assert capture["validation"]["ingress_hash"] == capture["ingress"]["artifact_hash"]
    assert capture["validation"]["raw_contribution_hash"] == capture["raw_contribution"]["response_hash"]
    assert (
        capture["validation"]["normalized_contribution_hash"]
        == capture["normalized_contribution"]["artifact_hash"]
    )
    assert capture["egress"]["validation_hash"] == capture["validation"]["artifact_hash"]


def test_normalization_is_replay_safe() -> None:
    normalized = normalize_llm_contribution(_contribution())
    without_hash = deepcopy(normalized)
    artifact_hash = without_hash.pop("artifact_hash")

    assert normalized["contribution_text"] == "Propose bounded metadata inspection for governance review."
    assert artifact_hash == replay_hash(without_hash)
    assert normalized["untrusted_contribution"] is True
    assert normalized["execution_authority"] is False
    assert normalized["governance_authority"] is False


def test_malformed_contribution_rejection(tmp_path) -> None:
    contribution = _contribution()
    contribution.pop("contribution_text")

    capture = _run(tmp_path, contribution)

    assert capture["egress"]["status"] == FAILED
    assert capture["egress"]["continuity_validated"] is False
    assert "malformed structure" in capture["egress"]["failure_reason"]
    assert reconstruct_minimal_real_llm_session_replay(tmp_path)["status"] == FAILED


def test_authority_escalation_rejection(tmp_path) -> None:
    contribution = _contribution(contribution_text="Please execute runtime actions and mutate governance.")

    capture = _run(tmp_path, contribution)

    assert capture["egress"]["status"] == FAILED
    assert capture["validation"]["authority_escalation_detected"] is True
    assert "authority escalation" in capture["egress"]["failure_reason"]


def test_missing_replay_artifact_detection(tmp_path) -> None:
    _run(tmp_path)
    (tmp_path / "003_validation.json").unlink()

    try:
        reconstruct_minimal_real_llm_session_replay(tmp_path)
    except Exception as exc:
        assert "missing" in str(exc)
    else:
        raise AssertionError("missing replay artifact must fail closed")


def test_ingress_is_deterministic() -> None:
    first = create_llm_session_ingress(
        session_id="LLM-SESSION-000001",
        request_id="LLM-REQUEST-000001",
        human_input="  bounded   request ",
        created_at=CREATED_AT,
    )
    second = create_llm_session_ingress(
        session_id="LLM-SESSION-000001",
        request_id="LLM-REQUEST-000001",
        human_input="bounded request",
        created_at=CREATED_AT,
    )

    assert first == second
    assert first["artifact_hash"].startswith("sha256:")


def test_no_expansion_surface() -> None:
    import aigol.runtime.minimal_executable_real_llm_session as session_runtime

    source = inspect.getsource(session_runtime)

    assert "subprocess" not in source
    assert "os.system" not in source
    assert "requests" not in source
    assert "urllib" not in source
    assert "async " not in source
    assert "await " not in source
    assert "threading" not in source
    assert "multiprocessing" not in source
