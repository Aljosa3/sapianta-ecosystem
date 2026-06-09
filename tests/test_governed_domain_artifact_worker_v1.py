from __future__ import annotations

import json
from pathlib import Path

import pytest

from aigol.authorization.authorization_runtime import (
    authorize_worker_request,
    reconstruct_authorization_replay,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import load_json
from aigol.workers.domain_artifact_worker import (
    AUTHORIZED_SCOPE,
    DOMAIN_ARTIFACT_WORKER_ID,
    DOMAIN_ARTIFACTS_AUTHORED,
    DOMAIN_DEFINITION_ARTIFACT_V1,
    DOMAIN_GOVERNANCE_EVIDENCE_ARTIFACT_V1,
    DOMAIN_METADATA_ARTIFACT_V1,
    DOMAIN_REGISTRATION_ARTIFACT_V1,
    FAILED_CLOSED,
    create_domain_artifact_request,
    execute_domain_artifact_request,
    reconstruct_domain_artifact_worker_replay,
    validate_domain_artifact_request,
)


TIMESTAMP = "2026-06-09T00:00:00Z"
DOMAIN_NAME = "FreshDomain"


def _proposal_for_authorization() -> dict:
    return {
        "proposal_id": "PROPOSAL-DOMAIN-ARTIFACT-000001",
        "proposal_hash": "sha256:domain-artifact-proposal",
        "proposal_lineage": {
            "provider_id": "OCS",
            "proposal_hash": "sha256:domain-artifact-proposal",
        },
        "governance_review": "GOVERNANCE_REVIEW_DOMAIN_ARTIFACT_WORKER_V1",
    }


def _worker_target() -> dict:
    return {
        "worker_id": DOMAIN_ARTIFACT_WORKER_ID,
        "domain": "governed_domain",
        "capability": "author_domain_artifacts",
    }


def _source_clarification_reference() -> dict:
    return {
        "clarification_id": "SESSION-FRESHDOMAIN:TURN-000001:UNKNOWN-DOMAIN-CLARIFICATION:CLARIFICATION",
        "continuity_status": "WORKFLOW_RESUME_READY",
        "originating_workflow_id": "CREATE_DOMAIN_COMPLIANCE_CLARIFICATION",
        "originating_intent": "CREATE_DOMAIN",
        "proposed_domain": DOMAIN_NAME,
        "next_governed_workflow_stage": "OCS_OR_EXECUTION_HANDOFF_REVIEW",
    }


def _authorized_request(tmp_path, **overrides) -> dict:
    authorization_capture = authorize_worker_request(
        authorization_id="AUTHORIZATION-DOMAIN-ARTIFACT-000001",
        proposal=_proposal_for_authorization(),
        worker_target=_worker_target(),
        authorization_scope=AUTHORIZED_SCOPE,
        authorization_timestamp=TIMESTAMP,
        replay_dir=tmp_path / "authorization_replay",
    )
    args = {
        "authorization_record": authorization_capture["authorization_record"],
        "request_id": "AUTHORIZED_DOMAIN_ARTIFACT_REQUEST-000001",
        "domain_name": DOMAIN_NAME,
        "primary_purpose": "Create a safe pilot governed domain for operator workflow acceptance.",
        "expected_capabilities": [
            "Clarification handling",
            "Bounded workflow resume",
            "Replay continuity inspection",
        ],
        "target_users": ["Internal AiGOL operators"],
        "source_clarification_reference": _source_clarification_reference(),
        "request_timestamp": TIMESTAMP,
        "proposal_reference": {
            "proposal_id": _proposal_for_authorization()["proposal_id"],
            "proposal_hash": _proposal_for_authorization()["proposal_hash"],
        },
        "replay_reference": authorization_capture["authorization_record"]["authorization_hash"],
    }
    args.update(overrides)
    return create_domain_artifact_request(**args)


def _run_domain_artifact_worker(tmp_path, **overrides) -> dict:
    output_dir = tmp_path / "domain_outputs"
    output_dir.mkdir()
    request = _authorized_request(tmp_path, **overrides)
    worker_capture = execute_domain_artifact_request(
        authorized_request=request,
        output_dir=output_dir,
        replay_dir=tmp_path / "domain_worker_replay",
    )
    return {
        "authorized_request": request,
        "worker_capture": worker_capture,
        "output_dir": output_dir,
    }


def test_domain_artifact_worker_creates_required_artifacts(tmp_path) -> None:
    capture = _run_domain_artifact_worker(tmp_path)
    result = capture["worker_capture"]["domain_artifact_worker_result"]

    assert result["event_type"] == DOMAIN_ARTIFACTS_AUTHORED
    assert result["execution_status"] == "SUCCEEDED"
    assert result["domain_name"] == DOMAIN_NAME
    assert result["domain_approved"] is False
    assert result["domain_activated"] is False
    assert result["live_registry_mutated"] is False
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["worker_result"]["domain_definition_created"] is True
    assert result["worker_result"]["domain_metadata_created"] is True
    assert result["worker_result"]["domain_registration_created"] is True
    assert result["worker_result"]["governance_evidence_created"] is True

    definition = load_json(Path(result["worker_result"]["domain_definition_path"]))
    metadata = load_json(Path(result["worker_result"]["domain_metadata_path"]))
    registration = load_json(Path(result["worker_result"]["domain_registration_path"]))
    evidence = load_json(Path(result["worker_result"]["governance_evidence_path"]))

    assert definition["artifact_type"] == DOMAIN_DEFINITION_ARTIFACT_V1
    assert metadata["artifact_type"] == DOMAIN_METADATA_ARTIFACT_V1
    assert registration["artifact_type"] == DOMAIN_REGISTRATION_ARTIFACT_V1
    assert evidence["artifact_type"] == DOMAIN_GOVERNANCE_EVIDENCE_ARTIFACT_V1
    assert definition["domain_name"] == DOMAIN_NAME
    assert metadata["domain_name"] == DOMAIN_NAME
    assert registration["domain_name"] == DOMAIN_NAME
    assert evidence["domain_name"] == DOMAIN_NAME
    assert registration["registration_authority_granted"] is False
    assert registration["live_registry_mutated"] is False


def test_domain_artifact_worker_replay_reconstructs_authorized_path(tmp_path) -> None:
    capture = _run_domain_artifact_worker(tmp_path)
    authorization_replay = reconstruct_authorization_replay(tmp_path / "authorization_replay")
    worker_replay = reconstruct_domain_artifact_worker_replay(tmp_path / "domain_worker_replay")

    assert authorization_replay["worker_authorized"] == DOMAIN_ARTIFACT_WORKER_ID
    assert authorization_replay["scope_authorized"] == AUTHORIZED_SCOPE
    assert worker_replay["proposal_reference"]["proposal_id"] == _proposal_for_authorization()["proposal_id"]
    assert worker_replay["authorization_id"] == "AUTHORIZATION-DOMAIN-ARTIFACT-000001"
    assert worker_replay["request_id"] == capture["authorized_request"]["request_id"]
    assert worker_replay["worker_id"] == DOMAIN_ARTIFACT_WORKER_ID
    assert worker_replay["domain_name"] == DOMAIN_NAME
    assert worker_replay["worker_action"] == "authored_governed_domain_artifacts"
    assert worker_replay["worker_result"]["domain_definition_created"] is True
    assert worker_replay["domain_approved"] is False
    assert worker_replay["live_registry_mutated"] is False


def test_scope_mismatch_fails_closed(tmp_path) -> None:
    authorization_capture = authorize_worker_request(
        authorization_id="AUTHORIZATION-DOMAIN-ARTIFACT-000001",
        proposal=_proposal_for_authorization(),
        worker_target=_worker_target(),
        authorization_scope="READ_ONLY",
        authorization_timestamp=TIMESTAMP,
        replay_dir=tmp_path,
    )

    with pytest.raises(FailClosedRuntimeError, match="scope mismatch"):
        create_domain_artifact_request(
            authorization_record=authorization_capture["authorization_record"],
            request_id="AUTHORIZED_DOMAIN_ARTIFACT_REQUEST-000001",
            domain_name=DOMAIN_NAME,
            primary_purpose="Create a safe pilot governed domain.",
            expected_capabilities=["Replay continuity inspection"],
            target_users=["Internal AiGOL operators"],
            source_clarification_reference=_source_clarification_reference(),
            request_timestamp=TIMESTAMP,
            proposal_reference={"proposal_id": "PROPOSAL-DOMAIN-ARTIFACT-000001"},
            replay_reference=authorization_capture["authorization_record"]["authorization_hash"],
        )


def test_invalid_domain_name_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="domain_name contains invalid characters"):
        _authorized_request(tmp_path, domain_name="../FreshDomain")


def test_missing_expected_capabilities_fails_closed(tmp_path) -> None:
    with pytest.raises(FailClosedRuntimeError, match="expected_capabilities"):
        _authorized_request(tmp_path, expected_capabilities=[])


def test_authority_bearing_request_rejected(tmp_path) -> None:
    request = _authorized_request(tmp_path)
    request["live_domain_registry_write"] = True

    with pytest.raises(FailClosedRuntimeError, match="forbidden authority field"):
        validate_domain_artifact_request(request)


def test_worker_unavailable_fails_closed(tmp_path) -> None:
    output_dir = tmp_path / "domain_outputs"
    output_dir.mkdir()
    request = _authorized_request(tmp_path)

    capture = execute_domain_artifact_request(
        authorized_request=request,
        output_dir=output_dir,
        replay_dir=tmp_path / "domain_worker_replay",
        worker_available=False,
    )

    result = capture["domain_artifact_worker_result"]
    assert result["execution_status"] == FAILED_CLOSED
    assert "domain artifact worker unavailable" in result["failure_reason"]
    assert result["domain_approved"] is False
    assert result["live_registry_mutated"] is False


def test_append_only_replay_violation_fails_closed(tmp_path) -> None:
    capture = _run_domain_artifact_worker(tmp_path)
    second = execute_domain_artifact_request(
        authorized_request=capture["authorized_request"],
        output_dir=capture["output_dir"],
        replay_dir=tmp_path / "domain_worker_replay",
    )

    result = second["domain_artifact_worker_result"]
    assert result["execution_status"] == FAILED_CLOSED
    assert "append-only domain artifact worker artifact already exists" in result["failure_reason"]


def test_domain_artifact_worker_replay_corruption_detection(tmp_path) -> None:
    _run_domain_artifact_worker(tmp_path)
    replay_file = tmp_path / "domain_worker_replay" / "001_domain_artifact_worker_result.json"
    wrapper = json.loads(replay_file.read_text(encoding="utf-8"))
    wrapper["artifact"]["domain_name"] = "TamperedDomain"
    replay_file.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_domain_artifact_worker_replay(tmp_path / "domain_worker_replay")

