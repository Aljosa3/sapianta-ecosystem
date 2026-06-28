"""Tests for G2-14 compatibility retirement certification."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.compatibility_retirement_certification_runtime import (
    COMPATIBILITY_RETIREMENT_CERTIFICATION_ARTIFACT_V1,
    COMPATIBILITY_RETIREMENT_CERTIFIED,
    RETAINED_ACTIVE_PARITY_NOT_PROVEN,
    RETAINED_OBSERVATIONAL_REPLAY_EVIDENCE,
    RETAINED_PERMANENT_STRUCTURED_AUTHORITY,
    RETIRED_PERMANENTLY,
    certify_compatibility_retirement,
    reconstruct_compatibility_retirement_certification_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


CERTIFIED_AT = "2026-06-28T00:00:00Z"


def _layer(
    layer_id: str,
    *,
    parity_status: str = "PARITY_CERTIFIED",
    retirement_candidate: bool = False,
    observational_replay_required: bool = True,
    permanent_structured_authority: bool = False,
) -> dict:
    return {
        "layer_id": layer_id,
        "compatibility_layer": f"{layer_id}_COMPATIBILITY_LAYER",
        "semantic_source": "CANONICAL_SEMANTIC_ARTIFACT",
        "parity_status": parity_status,
        "parity_evidence_hash": replay_hash({"layer_id": layer_id, "parity_status": parity_status}),
        "retirement_candidate": retirement_candidate,
        "observational_replay_required": observational_replay_required,
        "permanent_structured_authority": permanent_structured_authority,
        "fallback_status": "COMPATIBILITY_FALLBACK_VISIBLE",
        "migration_batches": ["G2-14"],
        "retirement_rationale": f"{layer_id} has explicit retirement disposition evidence.",
        "replay_integrity_verified": True,
        "rollback_capability_verified": True,
        "governance_authority_preserved": True,
        "ocs_authority_preserved": True,
        "ppp_authority_preserved": True,
        "provider_authority_preserved": True,
        "worker_authority_preserved": True,
        "approval_authority_preserved": True,
    }


def test_certifies_retired_observational_active_and_structured_dispositions(tmp_path) -> None:
    capture = certify_compatibility_retirement(
        certification_id="G2-14-CERTIFICATION-000001",
        compatibility_layers=[
            _layer(
                "CERTIFIED_AUTHORITY_RETIREMENT",
                retirement_candidate=True,
                observational_replay_required=False,
            ),
            _layer("CERTIFIED_REPLAY_EVIDENCE"),
            _layer("UNCERTIFIED_ACTIVE_FALLBACK", parity_status="PARITY_NOT_PROVEN"),
            _layer(
                "COMMAND_BOUNDARY_STRUCTURED_AUTHORITY",
                permanent_structured_authority=True,
            ),
        ],
        certified_by="HUMAN_OPERATOR",
        certified_at=CERTIFIED_AT,
        replay_dir=tmp_path / "g2_14",
    )
    artifact = capture["compatibility_retirement_certification_artifact"]
    reconstructed = reconstruct_compatibility_retirement_certification_replay(tmp_path / "g2_14")

    assert capture["certification_status"] == COMPATIBILITY_RETIREMENT_CERTIFIED
    assert capture["compatibility_retirement_certified"] is True
    assert artifact["artifact_type"] == COMPATIBILITY_RETIREMENT_CERTIFICATION_ARTIFACT_V1
    assert artifact["compatibility_code_deleted"] is False
    assert artifact["runtime_behavior_changed"] is False
    assert artifact["historical_replay_reinterpreted"] is False
    assert artifact["replay_integrity_preserved"] is True
    assert artifact["rollback_capability_preserved"] is True
    assert artifact["authority_boundaries_preserved"] is True
    assert artifact["generation2_completion_assessment"] == (
        "GENERATION_2_COMPATIBILITY_RETIREMENT_CERTIFIED_WITH_ACTIVE_EXCEPTIONS"
    )
    assert artifact["retired_layers"][0]["disposition"] == RETIRED_PERMANENTLY
    assert artifact["observational_replay_layers"][0]["disposition"] == (
        RETAINED_OBSERVATIONAL_REPLAY_EVIDENCE
    )
    assert artifact["active_compatibility_layers"][0]["disposition"] == RETAINED_ACTIVE_PARITY_NOT_PROVEN
    assert artifact["permanent_structured_authority_layers"][0]["disposition"] == (
        RETAINED_PERMANENT_STRUCTURED_AUTHORITY
    )
    assert reconstructed["retired_layers"] == artifact["retired_layers"]
    assert reconstructed["observational_replay_layers"] == artifact["observational_replay_layers"]
    assert reconstructed["active_compatibility_layers"] == artifact["active_compatibility_layers"]
    assert reconstructed["permanent_structured_authority_layers"] == (
        artifact["permanent_structured_authority_layers"]
    )
    assert reconstructed["runtime_behavior_changed"] is False
    assert reconstructed["governance_modified"] is False
    assert reconstructed["provider_invoked"] is False
    assert reconstructed["worker_invoked"] is False


def test_certification_without_active_exceptions_marks_completion_ready(tmp_path) -> None:
    capture = certify_compatibility_retirement(
        certification_id="G2-14-CERTIFICATION-NO-ACTIVE",
        compatibility_layers=[
            _layer("CERTIFIED_RETIRED", retirement_candidate=True, observational_replay_required=False),
            _layer("CERTIFIED_OBSERVATIONAL"),
        ],
        certified_by="HUMAN_OPERATOR",
        certified_at=CERTIFIED_AT,
        replay_dir=tmp_path / "no_active",
    )

    assert capture["certification_status"] == COMPATIBILITY_RETIREMENT_CERTIFIED
    assert capture["generation2_completion_assessment"] == "GENERATION_2_COMPATIBILITY_RETIREMENT_CERTIFIED"
    assert capture["active_compatibility_layers"] == []


def test_missing_replay_integrity_fails_closed(tmp_path) -> None:
    layer = _layer("BROKEN_REPLAY_INTEGRITY")
    layer["replay_integrity_verified"] = False

    capture = certify_compatibility_retirement(
        certification_id="G2-14-CERTIFICATION-BROKEN-REPLAY",
        compatibility_layers=[layer],
        certified_by="HUMAN_OPERATOR",
        certified_at=CERTIFIED_AT,
        replay_dir=tmp_path / "broken_replay",
    )

    assert capture["certification_status"] == "FAILED_CLOSED"
    assert "replay integrity not verified" in capture["failure_reason"]
    assert capture["compatibility_retirement_certified"] is False
    assert capture["replay_integrity_preserved"] is False
    assert capture["compatibility_retirement_certification_artifact"]["compatibility_code_deleted"] is False


def test_missing_authority_boundary_fails_closed(tmp_path) -> None:
    layer = _layer("BROKEN_AUTHORITY_BOUNDARY")
    layer["provider_authority_preserved"] = False

    capture = certify_compatibility_retirement(
        certification_id="G2-14-CERTIFICATION-BROKEN-AUTHORITY",
        compatibility_layers=[layer],
        certified_by="HUMAN_OPERATOR",
        certified_at=CERTIFIED_AT,
        replay_dir=tmp_path / "broken_authority",
    )

    assert capture["certification_status"] == "FAILED_CLOSED"
    assert "provider_authority_preserved missing" in capture["failure_reason"]
    assert capture["authority_boundaries_preserved"] is False


def test_reconstruction_detects_tampered_retirement_replay(tmp_path) -> None:
    certify_compatibility_retirement(
        certification_id="G2-14-CERTIFICATION-TAMPERED",
        compatibility_layers=[_layer("CERTIFIED_REPLAY_EVIDENCE")],
        certified_by="HUMAN_OPERATOR",
        certified_at=CERTIFIED_AT,
        replay_dir=tmp_path / "tampered",
    )
    path = tmp_path / "tampered" / "000_compatibility_retirement_certification_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["runtime_behavior_changed"] = True
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_compatibility_retirement_certification_replay(tmp_path / "tampered")


def test_runtime_has_no_provider_worker_or_governance_mutation_surfaces() -> None:
    import aigol.runtime.compatibility_retirement_certification_runtime as runtime

    source = inspect.getsource(runtime)

    assert "invoke_worker(" not in source
    assert "execute_worker(" not in source
    assert "invoke_live_external_llm_provider(" not in source
    assert "modify_governance(" not in source
    assert "modify_code(" not in source
    assert "write_text(" not in source
    assert "subprocess." not in source
    assert "os.system" not in source
