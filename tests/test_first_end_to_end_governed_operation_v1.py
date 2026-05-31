from __future__ import annotations

import json

import pytest

from aigol.authorization.authorization_runtime import (
    authorize_worker_request,
    reconstruct_authorization_replay,
)
from aigol.provider.provider_adapter import ProviderAdapter
from aigol.provider.provider_proposal_envelope import (
    ProviderProposalEnvelope,
    create_provider_proposal_envelope,
)
from aigol.provider.provider_registry import AVAILABLE, ProviderMetadata, ProviderRegistry
from aigol.provider.provider_runtime import run_provider_attachment, reconstruct_provider_attachment_replay
from aigol.runtime.models import FailClosedRuntimeError
from aigol.workers.filesystem_worker import (
    AUTHORIZED_SCOPE,
    FAILED_CLOSED,
    FILESYSTEM_WORKER_EXECUTED,
    FILESYSTEM_WORKER_ID,
    create_authorized_worker_request,
    execute_filesystem_create_request,
    reconstruct_filesystem_worker_replay,
    validate_authorized_worker_request,
)


TIMESTAMP = "2026-05-31T12:00:00Z"
CONTENT = "FIRST_END_TO_END_GOVERNED_OPERATION_V1"


class StaticProviderAdapter(ProviderAdapter):
    provider_id = "openai"
    provider_version = "FIRST_REAL_PROVIDER_ATTACHMENT_V1"

    def generate_proposal(self, request, *, proposal_id: str, timestamp: str) -> ProviderProposalEnvelope:
        return create_provider_proposal_envelope(
            proposal_id=proposal_id,
            provider_id=self.provider_id,
            provider_version=self.provider_version,
            request=request,
            response={
                "proposal_kind": "FILESYSTEM_CREATE_FILE",
                "reason": "Create one governed proof file.",
                "target_worker": FILESYSTEM_WORKER_ID,
                "file_path": "test.txt",
                "content": CONTENT,
            },
            timestamp=timestamp,
        )


def _provider_registry() -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register_provider(
        ProviderMetadata(
            provider_id="openai",
            provider_type="openai",
            provider_version="FIRST_REAL_PROVIDER_ATTACHMENT_V1",
            provider_status=AVAILABLE,
            domain="cognition",
            capability="proposal_generation",
            resource_type="text",
        )
    )
    return registry


def _proposal_for_authorization(provider_capture):
    envelope = provider_capture["provider_proposal_envelope"]
    return {
        "proposal_id": envelope["proposal_id"],
        "proposal_hash": envelope["proposal_hash"],
        "proposal_lineage": {
            "provider_id": envelope["provider_id"],
            "provider_version": envelope["provider_version"],
            "proposal_hash": envelope["proposal_hash"],
        },
        "governance_review": "GOVERNANCE_REVIEW_FIRST_END_TO_END_GOVERNED_OPERATION_V1",
    }


def _worker_target():
    return {
        "worker_id": FILESYSTEM_WORKER_ID,
        "domain": "filesystem",
        "capability": "filesystem_create_file",
    }


def _run_end_to_end(tmp_path):
    human_request = {
        "prompt_id": "HUMAN_REQUEST-000001",
        "prompt": "Create test.txt with FIRST_END_TO_END_GOVERNED_OPERATION_V1",
    }
    provider_capture = run_provider_attachment(
        provider_id="openai",
        request=human_request,
        proposal_id="PROPOSAL-000001",
        timestamp=TIMESTAMP,
        registry=_provider_registry(),
        adapter=StaticProviderAdapter(),
        replay_dir=tmp_path / "provider_replay",
    )
    authorization_capture = authorize_worker_request(
        authorization_id="AUTHORIZATION-000001",
        proposal=_proposal_for_authorization(provider_capture),
        worker_target=_worker_target(),
        authorization_scope=AUTHORIZED_SCOPE,
        authorization_timestamp=TIMESTAMP,
        replay_dir=tmp_path / "authorization_replay",
    )
    authorized_request = create_authorized_worker_request(
        authorization_record=authorization_capture["authorization_record"],
        request_id="AUTHORIZED_WORKER_REQUEST-000001",
        file_path="test.txt",
        content=CONTENT,
        request_timestamp=TIMESTAMP,
        proposal_reference={
            "proposal_id": provider_capture["provider_proposal_envelope"]["proposal_id"],
            "proposal_hash": provider_capture["provider_proposal_envelope"]["proposal_hash"],
        },
        replay_reference=authorization_capture["authorization_record"]["authorization_hash"],
    )
    workspace = tmp_path / "governed_workspace"
    workspace.mkdir()
    worker_capture = execute_filesystem_create_request(
        authorized_request=authorized_request,
        base_dir=workspace,
        replay_dir=tmp_path / "worker_replay",
    )
    return {
        "human_request": human_request,
        "provider_capture": provider_capture,
        "authorization_capture": authorization_capture,
        "authorized_request": authorized_request,
        "worker_capture": worker_capture,
        "workspace": workspace,
    }


def test_first_end_to_end_governed_operation_succeeds(tmp_path):
    capture = _run_end_to_end(tmp_path)
    target = capture["workspace"] / "test.txt"

    assert target.read_text(encoding="utf-8") == CONTENT
    assert capture["provider_capture"]["provider_proposal_envelope"]["provider_id"] == "openai"
    assert capture["authorization_capture"]["authorization_record"]["authorization_scope"] == AUTHORIZED_SCOPE
    assert capture["authorized_request"]["worker_id"] == FILESYSTEM_WORKER_ID
    assert capture["worker_capture"]["filesystem_worker_execution"]["event_type"] == FILESYSTEM_WORKER_EXECUTED
    assert capture["worker_capture"]["filesystem_worker_execution"]["execution_result"]["created"] is True


def test_full_replay_reconstructs_human_provider_proposal_authorization_request_worker_and_result(tmp_path):
    capture = _run_end_to_end(tmp_path)
    provider_replay = reconstruct_provider_attachment_replay(tmp_path / "provider_replay")
    authorization_replay = reconstruct_authorization_replay(tmp_path / "authorization_replay")
    worker_replay = reconstruct_filesystem_worker_replay(tmp_path / "worker_replay")

    assert provider_replay["request"] == capture["human_request"]
    assert provider_replay["provider_id"] == "openai"
    assert provider_replay["proposal_hash"] == capture["provider_capture"]["provider_proposal_envelope"]["proposal_hash"]

    assert authorization_replay["who_proposed"] == "PROPOSAL-000001"
    assert authorization_replay["worker_authorized"] == FILESYSTEM_WORKER_ID
    assert authorization_replay["scope_authorized"] == AUTHORIZED_SCOPE

    assert worker_replay["proposal_reference"]["proposal_id"] == "PROPOSAL-000001"
    assert worker_replay["authorization_id"] == "AUTHORIZATION-000001"
    assert worker_replay["request_id"] == "AUTHORIZED_WORKER_REQUEST-000001"
    assert worker_replay["worker_id"] == FILESYSTEM_WORKER_ID
    assert worker_replay["execution_result"]["created"] is True
    assert worker_replay["file_path"] == "test.txt"


def test_missing_proposal_fails_closed(tmp_path):
    capture = authorize_worker_request(
        authorization_id="AUTHORIZATION-000001",
        proposal={},
        worker_target=_worker_target(),
        authorization_scope=AUTHORIZED_SCOPE,
        authorization_timestamp=TIMESTAMP,
        replay_dir=tmp_path,
    )

    assert capture["authorization_created"]["event_type"] == FAILED_CLOSED
    assert "proposal_id is required" in capture["authorization_created"]["failure_reason"]


def test_missing_authorization_fails_closed():
    with pytest.raises(FailClosedRuntimeError, match="authorization record"):
        create_authorized_worker_request(
            authorization_record={},
            request_id="AUTHORIZED_WORKER_REQUEST-000001",
            file_path="test.txt",
            content=CONTENT,
            request_timestamp=TIMESTAMP,
            proposal_reference={"proposal_id": "PROPOSAL-000001"},
            replay_reference="sha256:missing",
        )


def test_invalid_authorized_request_fails_closed(tmp_path):
    capture = _run_end_to_end(tmp_path)
    request = dict(capture["authorized_request"])
    request["file_path"] = "../test.txt"

    worker_capture = execute_filesystem_create_request(
        authorized_request=request,
        base_dir=capture["workspace"],
        replay_dir=tmp_path / "invalid_worker_replay",
    )

    assert worker_capture["filesystem_worker_execution"]["execution_status"] == FAILED_CLOSED
    assert "file_path must be a single relative filename" in worker_capture["filesystem_worker_execution"]["failure_reason"]


def test_unknown_worker_fails_closed(tmp_path):
    auth_capture = authorize_worker_request(
        authorization_id="AUTHORIZATION-000001",
        proposal={
            "proposal_id": "PROPOSAL-000001",
            "proposal_lineage": {"provider_id": "openai", "proposal_hash": "sha256:proposal"},
            "governance_review": "GOVERNANCE_REVIEW-000001",
        },
        worker_target={
            "worker_id": "UNKNOWN_WORKER",
            "domain": "filesystem",
            "capability": "filesystem_create_file",
        },
        authorization_scope=AUTHORIZED_SCOPE,
        authorization_timestamp=TIMESTAMP,
        replay_dir=tmp_path,
    )

    with pytest.raises(FailClosedRuntimeError, match="worker mismatch"):
        create_authorized_worker_request(
            authorization_record=auth_capture["authorization_record"],
            request_id="AUTHORIZED_WORKER_REQUEST-000001",
            file_path="test.txt",
            content=CONTENT,
            request_timestamp=TIMESTAMP,
            proposal_reference={"proposal_id": "PROPOSAL-000001"},
            replay_reference=auth_capture["authorization_record"]["authorization_hash"],
        )


def test_scope_mismatch_fails_closed(tmp_path):
    auth_capture = authorize_worker_request(
        authorization_id="AUTHORIZATION-000001",
        proposal={
            "proposal_id": "PROPOSAL-000001",
            "proposal_lineage": {"provider_id": "openai", "proposal_hash": "sha256:proposal"},
            "governance_review": "GOVERNANCE_REVIEW-000001",
        },
        worker_target=_worker_target(),
        authorization_scope="READ_ONLY",
        authorization_timestamp=TIMESTAMP,
        replay_dir=tmp_path,
    )

    with pytest.raises(FailClosedRuntimeError, match="scope mismatch"):
        create_authorized_worker_request(
            authorization_record=auth_capture["authorization_record"],
            request_id="AUTHORIZED_WORKER_REQUEST-000001",
            file_path="test.txt",
            content=CONTENT,
            request_timestamp=TIMESTAMP,
            proposal_reference={"proposal_id": "PROPOSAL-000001"},
            replay_reference=auth_capture["authorization_record"]["authorization_hash"],
        )


def test_authorized_worker_request_cannot_exceed_authorization_scope(tmp_path):
    capture = _run_end_to_end(tmp_path)
    request = dict(capture["authorized_request"])
    request["authorized_scope"] = "FILESYSTEM_DELETE_FILE"

    with pytest.raises(FailClosedRuntimeError, match="scope mismatch|hash mismatch"):
        validate_authorized_worker_request(request)


def test_worker_append_only_replay_violation_fails_closed(tmp_path):
    capture = _run_end_to_end(tmp_path)
    second = execute_filesystem_create_request(
        authorized_request=capture["authorized_request"],
        base_dir=capture["workspace"],
        replay_dir=tmp_path / "worker_replay",
    )

    assert second["filesystem_worker_execution"]["execution_status"] == FAILED_CLOSED
    assert "append-only worker artifact already exists" in second["filesystem_worker_execution"]["failure_reason"]


def test_worker_replay_corruption_detection(tmp_path):
    _run_end_to_end(tmp_path)
    replay_file = tmp_path / "worker_replay" / "001_filesystem_worker_execution.json"
    wrapper = json.loads(replay_file.read_text(encoding="utf-8"))
    wrapper["artifact"]["worker_id"] = "TAMPERED_WORKER"
    replay_file.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_filesystem_worker_replay(tmp_path / "worker_replay")
