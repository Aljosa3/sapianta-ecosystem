from __future__ import annotations

import json
from pathlib import Path

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
from aigol.runtime.transport.serialization import load_json
from aigol.workers.github_worker import (
    AUTHORIZED_SCOPE,
    FAILED_CLOSED,
    GITHUB_ISSUE_DRAFT_CREATED,
    GITHUB_WORKER_ID,
    create_github_issue_draft_request,
    execute_github_issue_draft_request,
    reconstruct_github_worker_replay,
    validate_github_issue_draft_request,
)


TIMESTAMP = "2026-05-31T12:00:00Z"
REPOSITORY = "sapianta/aigol"


class StaticGitHubProposalProvider(ProviderAdapter):
    provider_id = "openai"
    provider_version = "FIRST_REAL_PROVIDER_ATTACHMENT_V1"

    def generate_proposal(self, request, *, proposal_id: str, timestamp: str) -> ProviderProposalEnvelope:
        return create_provider_proposal_envelope(
            proposal_id=proposal_id,
            provider_id=self.provider_id,
            provider_version=self.provider_version,
            request=request,
            response={
                "proposal_kind": "GITHUB_CREATE_ISSUE_DRAFT",
                "reason": "Create a governed GitHub issue draft for human review.",
                "target_worker": GITHUB_WORKER_ID,
                "repository": REPOSITORY,
                "issue_title": "Governed issue draft from AiGOL",
                "issue_body": "This issue draft was created through governed authorization and replay.",
                "labels": ["governed", "audit"],
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
        "governance_review": "GOVERNANCE_REVIEW_FIRST_REAL_DOMAIN_WORKER_V1",
    }


def _worker_target():
    return {
        "worker_id": GITHUB_WORKER_ID,
        "domain": "github",
        "capability": "create_issue_draft",
    }


def _run_github_domain_operation(tmp_path):
    human_request = {
        "prompt_id": "HUMAN_REQUEST-GITHUB-000001",
        "prompt": "Create a governed GitHub issue draft for sapianta/aigol.",
    }
    provider_capture = run_provider_attachment(
        provider_id="openai",
        request=human_request,
        proposal_id="PROPOSAL-GITHUB-000001",
        timestamp=TIMESTAMP,
        registry=_provider_registry(),
        adapter=StaticGitHubProposalProvider(),
        replay_dir=tmp_path / "provider_replay",
    )
    proposal = provider_capture["provider_proposal_envelope"]["response"]
    authorization_capture = authorize_worker_request(
        authorization_id="AUTHORIZATION-GITHUB-000001",
        proposal=_proposal_for_authorization(provider_capture),
        worker_target=_worker_target(),
        authorization_scope=AUTHORIZED_SCOPE,
        authorization_timestamp=TIMESTAMP,
        replay_dir=tmp_path / "authorization_replay",
    )
    authorized_request = create_github_issue_draft_request(
        authorization_record=authorization_capture["authorization_record"],
        request_id="AUTHORIZED_GITHUB_REQUEST-000001",
        repository=proposal["repository"],
        issue_title=proposal["issue_title"],
        issue_body=proposal["issue_body"],
        labels=proposal["labels"],
        request_timestamp=TIMESTAMP,
        proposal_reference={
            "proposal_id": provider_capture["provider_proposal_envelope"]["proposal_id"],
            "proposal_hash": provider_capture["provider_proposal_envelope"]["proposal_hash"],
        },
        replay_reference=authorization_capture["authorization_record"]["authorization_hash"],
    )
    output_dir = tmp_path / "github_outputs"
    output_dir.mkdir()
    worker_capture = execute_github_issue_draft_request(
        authorized_request=authorized_request,
        known_repositories=[REPOSITORY],
        output_dir=output_dir,
        replay_dir=tmp_path / "github_worker_replay",
    )
    return {
        "human_request": human_request,
        "provider_capture": provider_capture,
        "authorization_capture": authorization_capture,
        "authorized_request": authorized_request,
        "worker_capture": worker_capture,
        "output_dir": output_dir,
    }


def test_github_domain_worker_creates_issue_draft(tmp_path):
    capture = _run_github_domain_operation(tmp_path)
    result = capture["worker_capture"]["github_worker_result"]
    issue_draft_path = result["worker_result"]["issue_draft_path"]
    issue_draft = load_json(Path(issue_draft_path))

    assert result["event_type"] == GITHUB_ISSUE_DRAFT_CREATED
    assert result["execution_status"] == "SUCCEEDED"
    assert result["github_api_invoked"] is False
    assert result["repository_mutated"] is False
    assert issue_draft["repository"] == REPOSITORY
    assert issue_draft["title"] == "Governed issue draft from AiGOL"
    assert issue_draft["github_api_invoked"] is False
    assert issue_draft["repository_mutated"] is False


def test_github_domain_worker_replay_reconstructs_full_path(tmp_path):
    capture = _run_github_domain_operation(tmp_path)
    provider_replay = reconstruct_provider_attachment_replay(tmp_path / "provider_replay")
    authorization_replay = reconstruct_authorization_replay(tmp_path / "authorization_replay")
    worker_replay = reconstruct_github_worker_replay(tmp_path / "github_worker_replay")

    assert provider_replay["request"] == capture["human_request"]
    assert provider_replay["provider_id"] == "openai"
    assert authorization_replay["who_proposed"] == "PROPOSAL-GITHUB-000001"
    assert authorization_replay["worker_authorized"] == GITHUB_WORKER_ID
    assert authorization_replay["scope_authorized"] == AUTHORIZED_SCOPE
    assert worker_replay["proposal_reference"]["proposal_id"] == "PROPOSAL-GITHUB-000001"
    assert worker_replay["authorization_id"] == "AUTHORIZATION-GITHUB-000001"
    assert worker_replay["request_id"] == "AUTHORIZED_GITHUB_REQUEST-000001"
    assert worker_replay["worker_action"] == "created_github_issue_draft_artifact"
    assert worker_replay["worker_result"]["issue_draft_created"] is True
    assert worker_replay["github_api_invoked"] is False
    assert worker_replay["repository_mutated"] is False


def test_missing_authorization_fails_closed():
    with pytest.raises(FailClosedRuntimeError, match="authorization record"):
        create_github_issue_draft_request(
            authorization_record={},
            request_id="AUTHORIZED_GITHUB_REQUEST-000001",
            repository=REPOSITORY,
            issue_title="Governed issue draft from AiGOL",
            issue_body="This issue draft was created through governed authorization and replay.",
            labels=["governed"],
            request_timestamp=TIMESTAMP,
            proposal_reference={"proposal_id": "PROPOSAL-GITHUB-000001"},
            replay_reference="sha256:missing",
        )


def test_scope_mismatch_fails_closed(tmp_path):
    auth_capture = authorize_worker_request(
        authorization_id="AUTHORIZATION-GITHUB-000001",
        proposal={
            "proposal_id": "PROPOSAL-GITHUB-000001",
            "proposal_lineage": {"provider_id": "openai", "proposal_hash": "sha256:proposal"},
            "governance_review": "GOVERNANCE_REVIEW-000001",
        },
        worker_target=_worker_target(),
        authorization_scope="READ_ONLY",
        authorization_timestamp=TIMESTAMP,
        replay_dir=tmp_path,
    )

    with pytest.raises(FailClosedRuntimeError, match="scope mismatch"):
        create_github_issue_draft_request(
            authorization_record=auth_capture["authorization_record"],
            request_id="AUTHORIZED_GITHUB_REQUEST-000001",
            repository=REPOSITORY,
            issue_title="Governed issue draft from AiGOL",
            issue_body="This issue draft was created through governed authorization and replay.",
            labels=["governed"],
            request_timestamp=TIMESTAMP,
            proposal_reference={"proposal_id": "PROPOSAL-GITHUB-000001"},
            replay_reference=auth_capture["authorization_record"]["authorization_hash"],
        )


def test_unknown_repository_fails_closed(tmp_path):
    capture = _run_github_domain_operation(tmp_path)
    output_dir = tmp_path / "unknown_repository_outputs"
    output_dir.mkdir()

    worker_capture = execute_github_issue_draft_request(
        authorized_request=capture["authorized_request"],
        known_repositories=["other/repository"],
        output_dir=output_dir,
        replay_dir=tmp_path / "unknown_repository_replay",
    )

    assert worker_capture["github_worker_result"]["execution_status"] == FAILED_CLOSED
    assert "unknown repository" in worker_capture["github_worker_result"]["failure_reason"]
    assert worker_capture["github_worker_result"]["github_api_invoked"] is False


def test_worker_unavailable_fails_closed(tmp_path):
    capture = _run_github_domain_operation(tmp_path)
    output_dir = tmp_path / "unavailable_outputs"
    output_dir.mkdir()

    worker_capture = execute_github_issue_draft_request(
        authorized_request=capture["authorized_request"],
        known_repositories=[REPOSITORY],
        output_dir=output_dir,
        replay_dir=tmp_path / "unavailable_replay",
        worker_available=False,
    )

    assert worker_capture["github_worker_result"]["execution_status"] == FAILED_CLOSED
    assert "github worker unavailable" in worker_capture["github_worker_result"]["failure_reason"]
    assert worker_capture["github_worker_result"]["github_api_invoked"] is False


def test_invalid_request_fails_closed(tmp_path):
    capture = _run_github_domain_operation(tmp_path)
    request = dict(capture["authorized_request"])
    request["repository"] = "not-a-repository"
    output_dir = tmp_path / "invalid_outputs"
    output_dir.mkdir()

    worker_capture = execute_github_issue_draft_request(
        authorized_request=request,
        known_repositories=[REPOSITORY],
        output_dir=output_dir,
        replay_dir=tmp_path / "invalid_replay",
    )

    assert worker_capture["github_worker_result"]["execution_status"] == FAILED_CLOSED
    assert "repository must be owner/name" in worker_capture["github_worker_result"]["failure_reason"]


def test_authority_bearing_request_rejected(tmp_path):
    capture = _run_github_domain_operation(tmp_path)
    request = dict(capture["authorized_request"])
    request["github_api_token"] = "secret"

    with pytest.raises(FailClosedRuntimeError, match="forbidden authority field"):
        validate_github_issue_draft_request(request)


def test_github_worker_append_only_replay_violation_fails_closed(tmp_path):
    capture = _run_github_domain_operation(tmp_path)
    second = execute_github_issue_draft_request(
        authorized_request=capture["authorized_request"],
        known_repositories=[REPOSITORY],
        output_dir=capture["output_dir"],
        replay_dir=tmp_path / "github_worker_replay",
    )

    assert second["github_worker_result"]["execution_status"] == FAILED_CLOSED
    assert "append-only github worker artifact already exists" in second["github_worker_result"]["failure_reason"]


def test_github_worker_replay_corruption_detection(tmp_path):
    _run_github_domain_operation(tmp_path)
    replay_file = tmp_path / "github_worker_replay" / "001_github_worker_result.json"
    wrapper = json.loads(replay_file.read_text(encoding="utf-8"))
    wrapper["artifact"]["repository"] = "tampered/repo"
    replay_file.write_text(json.dumps(wrapper, sort_keys=True), encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_github_worker_replay(tmp_path / "github_worker_replay")
