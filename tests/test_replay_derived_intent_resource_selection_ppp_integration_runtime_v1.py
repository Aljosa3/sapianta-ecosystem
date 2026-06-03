"""Tests for AIGOL_REPLAY_DERIVED_INTENT_RESOURCE_SELECTION_PPP_INTEGRATION_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.improvement_intent_cognition_routing_runtime import route_improvement_intent_to_cognition
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.replay_derived_intent_resource_selection_ppp_integration_runtime import (
    FAILED_CLOSED,
    PPP_INTENT_ROUTED,
    PPP_ROUTED_INTENT_ARTIFACT_V1,
    PPP_ROUTING_CLASSIFICATION_V1,
    PPP_ROUTING_EVIDENCE_V1,
    reconstruct_replay_derived_intent_resource_selection_ppp_integration_replay,
    route_replay_derived_intent_to_ppp,
)
from aigol.runtime.replay_derived_intent_resource_selection_routing_runtime import (
    route_replay_derived_intent_to_resource_selection,
)
from aigol.runtime.replay_gap_detection_runtime import detect_replay_gaps
from aigol.runtime.replay_to_improvement_intent_runtime import create_improvement_intent_from_replay_gap
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash
from aigol.runtime.unified_resource_selection_runtime import PROVIDER_ROLE


CREATED_AT = "2026-06-03T19:30:00+00:00"
CHAIN_ID = "CHAIN-PPP-ROUTING-000001"


def _evidence(evidence_id: str, evidence_type: str, payload: dict, **extra) -> dict:
    return {
        "evidence_id": evidence_id,
        "evidence_type": evidence_type,
        "source_replay_reference": f"replay/{evidence_id}.json",
        "source_replay_payload": payload,
        "source_replay_hash": replay_hash(payload),
        "canonical_chain_id": CHAIN_ID,
        "observed_condition": "observed replay condition",
        "expected_condition": "expected replay condition",
        "confidence": "DETERMINISTIC",
        **extra,
    }


def _resource_selection_routing_capture(tmp_path, *, domain_id: str = "TRADING"):
    gap = detect_replay_gaps(
        detection_id=f"GAP-PPP-{domain_id}",
        domain_id=domain_id,
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"gap-{domain_id}",
        replay_artifacts=[
            _evidence("VALIDATION-FAIL", "VALIDATION_RESULT", {"status": "FAILED"}, status="FAILED")
        ],
    )
    intent = create_improvement_intent_from_replay_gap(
        improvement_intent_id=f"IMPROVEMENT-INTENT-PPP-{domain_id}",
        gap_detection_artifact=gap["gap_detection_artifact"],
        gap_classification_artifact=gap["gap_classification_artifact"],
        gap_evidence_artifact=gap["gap_evidence_artifact"],
        canonical_chain_id=CHAIN_ID,
        affected_layer="GOVERNANCE",
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"intent-{domain_id}",
    )
    cognition = route_improvement_intent_to_cognition(
        routing_id=f"COGNITION-ROUTING-PPP-{domain_id}",
        improvement_intent_artifact=intent["improvement_intent_artifact"],
        improvement_intent_evidence_artifact=intent["improvement_intent_evidence_artifact"],
        improvement_intent_classification_artifact=intent["improvement_intent_classification_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"cognition-{domain_id}",
    )
    return route_replay_derived_intent_to_resource_selection(
        routing_id=f"RESOURCE-SELECTION-ROUTING-PPP-{domain_id}",
        cognition_routed_intent_artifact=cognition["cognition_routed_intent_artifact"],
        cognition_routing_evidence_artifact=cognition["cognition_routing_evidence_artifact"],
        cognition_routing_classification_artifact=cognition["cognition_routing_classification_artifact"],
        created_at=CREATED_AT,
        replay_dir=tmp_path / f"resource-routing-{domain_id}",
    )


def test_routes_resource_selection_routed_replay_intent_to_ppp_input(tmp_path) -> None:
    resource_routing = _resource_selection_routing_capture(tmp_path)
    capture = route_replay_derived_intent_to_ppp(
        routing_id="PPP-ROUTING-000001",
        resource_selection_routed_intent_artifact=resource_routing["resource_selection_routed_intent_artifact"],
        resource_selection_routing_evidence_artifact=resource_routing[
            "resource_selection_routing_evidence_artifact"
        ],
        resource_selection_routing_classification_artifact=resource_routing[
            "resource_selection_routing_classification_artifact"
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ppp-routing",
    )
    reconstructed = reconstruct_replay_derived_intent_resource_selection_ppp_integration_replay(
        tmp_path / "ppp-routing"
    )
    routed = capture["ppp_routed_intent_artifact"]
    contract = routed["ppp_input_contract"]

    assert capture["routing_status"] == PPP_INTENT_ROUTED
    assert capture["ppp_routing_evidence_artifact"]["artifact_type"] == PPP_ROUTING_EVIDENCE_V1
    assert capture["ppp_routing_classification_artifact"]["artifact_type"] == PPP_ROUTING_CLASSIFICATION_V1
    assert routed["artifact_type"] == PPP_ROUTED_INTENT_ARTIFACT_V1
    assert routed["ppp_input_type"] == "STRUCTURED_PPP_INTENT"
    assert contract["workflow_type"] == "NATIVE_DEVELOPMENT"
    assert contract["required_capability"] == "PROPOSAL_GENERATION"
    assert contract["requested_role_type"] == PROVIDER_ROLE
    assert contract["domain_id"] == "TRADING"
    assert contract["provider_necessity_classification"] == "PROVIDER_REQUIRED"
    assert contract["ppp_stage"] == "PROPOSAL_PRODUCTION"
    assert routed["source_lineage_preserved"] is True
    assert routed["intent_source_visible_to_ppp"] is False
    assert contract["intent_source_visible_to_ppp"] is False
    assert routed["resource_references"]["domain_id"] == "TRADING"
    assert routed["ppp_proposal_production_invoked"] is False
    assert routed["ppp_invoked"] is False
    assert routed["proposal_created"] is False
    assert routed["provider_invoked"] is False
    assert routed["worker_invoked"] is False
    assert routed["authorization_created"] is False
    assert routed["execution_requested"] is False
    assert routed["dispatch_requested"] is False
    assert reconstructed["routing_status"] == PPP_INTENT_ROUTED
    assert reconstructed["replay_artifact_count"] == 4


def test_human_and_replay_intent_are_ppp_equivalent_after_routing(tmp_path) -> None:
    resource_routing = _resource_selection_routing_capture(tmp_path, domain_id="MARKETING")
    capture = route_replay_derived_intent_to_ppp(
        routing_id="PPP-ROUTING-EQUIVALENCE-000001",
        resource_selection_routed_intent_artifact=resource_routing["resource_selection_routed_intent_artifact"],
        resource_selection_routing_evidence_artifact=resource_routing[
            "resource_selection_routing_evidence_artifact"
        ],
        resource_selection_routing_classification_artifact=resource_routing[
            "resource_selection_routing_classification_artifact"
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "equivalence",
    )
    contract = capture["ppp_input_contract"]

    assert set(contract) == {
        "intent_reference",
        "workflow_type",
        "required_capability",
        "requested_role_type",
        "domain_id",
        "provider_necessity_classification",
        "confidence",
        "ppp_stage",
        "intent_source_visible_to_ppp",
    }
    assert contract["intent_source_visible_to_ppp"] is False
    assert "REPLAY_GAP_DETECTION" not in contract.values()
    assert "REPLAY_DERIVED_INTENT" not in contract.values()


def test_ppp_routing_fails_closed_when_source_visibility_leaks(tmp_path) -> None:
    resource_routing = _resource_selection_routing_capture(tmp_path)
    artifact = dict(resource_routing["resource_selection_routed_intent_artifact"])
    contract = dict(artifact["resource_selection_input_contract"])
    contract["intent_source_visible_to_resource_selection"] = True
    artifact["resource_selection_input_contract"] = contract
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)
    capture = route_replay_derived_intent_to_ppp(
        routing_id="PPP-ROUTING-LEAK-000001",
        resource_selection_routed_intent_artifact=artifact,
        resource_selection_routing_evidence_artifact=resource_routing[
            "resource_selection_routing_evidence_artifact"
        ],
        resource_selection_routing_classification_artifact=resource_routing[
            "resource_selection_routing_classification_artifact"
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "leak",
    )

    assert capture["routing_status"] == FAILED_CLOSED
    assert "source visibility leak" in capture["failure_reason"]


def test_ppp_routing_fails_closed_when_lineage_hash_mismatches(tmp_path) -> None:
    resource_routing = _resource_selection_routing_capture(tmp_path)
    artifact = dict(resource_routing["resource_selection_routed_intent_artifact"])
    artifact["routing_evidence_hash"] = "sha256:not-real"
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)
    capture = route_replay_derived_intent_to_ppp(
        routing_id="PPP-ROUTING-LINEAGE-000001",
        resource_selection_routed_intent_artifact=artifact,
        resource_selection_routing_evidence_artifact=resource_routing[
            "resource_selection_routing_evidence_artifact"
        ],
        resource_selection_routing_classification_artifact=resource_routing[
            "resource_selection_routing_classification_artifact"
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "lineage",
    )

    assert capture["routing_status"] == FAILED_CLOSED
    assert "replay lineage broken" in capture["failure_reason"]


def test_ppp_routing_fails_closed_when_chain_continuity_fails(tmp_path) -> None:
    resource_routing = _resource_selection_routing_capture(tmp_path)
    evidence = dict(resource_routing["resource_selection_routing_evidence_artifact"])
    evidence["canonical_chain_id"] = "DIFFERENT-CHAIN"
    evidence.pop("artifact_hash")
    evidence["artifact_hash"] = replay_hash(evidence)
    classification = dict(resource_routing["resource_selection_routing_classification_artifact"])
    classification["routing_evidence_hash"] = evidence["artifact_hash"]
    classification.pop("artifact_hash")
    classification["artifact_hash"] = replay_hash(classification)
    artifact = dict(resource_routing["resource_selection_routed_intent_artifact"])
    artifact["routing_evidence_hash"] = evidence["artifact_hash"]
    artifact["routing_classification_hash"] = classification["artifact_hash"]
    artifact.pop("artifact_hash")
    artifact["artifact_hash"] = replay_hash(artifact)

    capture = route_replay_derived_intent_to_ppp(
        routing_id="PPP-ROUTING-CHAIN-000001",
        resource_selection_routed_intent_artifact=artifact,
        resource_selection_routing_evidence_artifact=evidence,
        resource_selection_routing_classification_artifact=classification,
        created_at=CREATED_AT,
        replay_dir=tmp_path / "chain",
    )

    assert capture["routing_status"] == FAILED_CLOSED
    assert "chain continuity failed" in capture["failure_reason"]


def test_reconstruction_detects_corrupt_ppp_routing_replay(tmp_path) -> None:
    resource_routing = _resource_selection_routing_capture(tmp_path)
    route_replay_derived_intent_to_ppp(
        routing_id="PPP-ROUTING-CORRUPT-000001",
        resource_selection_routed_intent_artifact=resource_routing["resource_selection_routed_intent_artifact"],
        resource_selection_routing_evidence_artifact=resource_routing[
            "resource_selection_routing_evidence_artifact"
        ],
        resource_selection_routing_classification_artifact=resource_routing[
            "resource_selection_routing_classification_artifact"
        ],
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt",
    )
    path = tmp_path / "corrupt" / "002_ppp_routed_intent_recorded.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["normalized_intent"] = "corrupted"
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_replay_derived_intent_resource_selection_ppp_integration_replay(tmp_path / "corrupt")


def test_replay_derived_intent_ppp_routing_has_no_ppp_provider_worker_or_execution_invocation_imports() -> None:
    import aigol.runtime.replay_derived_intent_resource_selection_ppp_integration_runtime as runtime

    source = inspect.getsource(runtime)

    assert "integrate_resource_selection_with_ppp(" not in source
    assert "produce_provider_development_proposal(" not in source
    assert "run_provider_attachment(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
