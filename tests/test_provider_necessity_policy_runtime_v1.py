"""Tests for AIGOL_PROVIDER_NECESSITY_POLICY_RUNTIME_V1."""

from __future__ import annotations

import inspect
import json

import pytest

from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.provider_necessity_policy_runtime import (
    AIGOL_PROVIDER_NECESSITY_POLICY_RUNTIME_VERSION,
    PROVIDER_NECESSITY_CLASSIFIED,
    PROVIDER_NECESSITY_POLICY_ARTIFACT_V1,
    PROVIDER_OPTIONAL,
    PROVIDER_PROHIBITED,
    PROVIDER_REQUIRED,
    classify_provider_necessity,
    default_provider_necessity_policy,
    reconstruct_provider_necessity_policy_replay,
)
from aigol.runtime.transport.serialization import canonical_serialize


CREATED_AT = "2026-06-02T18:00:00+00:00"


def test_show_chain_provider_is_prohibited_and_reconstructable(tmp_path) -> None:
    capture = classify_provider_necessity(
        policy_decision_id="PROVIDER-POLICY-SHOW-CHAIN-000001",
        workflow_type="OPERATOR_INSPECTION",
        command="SHOW_CHAIN",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "show_chain",
    )
    reconstructed = reconstruct_provider_necessity_policy_replay(tmp_path / "show_chain")
    artifact = capture["provider_necessity_policy_artifact"]

    assert artifact["artifact_type"] == PROVIDER_NECESSITY_POLICY_ARTIFACT_V1
    assert capture["policy_status"] == PROVIDER_NECESSITY_CLASSIFIED
    assert capture["necessity_classification"] == PROVIDER_PROHIBITED
    assert capture["policy_version"] == AIGOL_PROVIDER_NECESSITY_POLICY_RUNTIME_VERSION
    assert capture["policy_hash"].startswith("sha256:")
    assert "Chain inspection" in capture["reason"]
    assert capture["provider_invoked"] is False
    assert capture["proposal_generated"] is False
    assert reconstructed["necessity_classification"] == PROVIDER_PROHIBITED
    assert reconstructed["replay_artifact_count"] == 2


def test_dashboard_and_replay_inspection_provider_are_prohibited(tmp_path) -> None:
    dashboard = classify_provider_necessity(
        policy_decision_id="PROVIDER-POLICY-DASHBOARD-000001",
        workflow_type="OPERATOR_INSPECTION",
        command="DASHBOARD",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "dashboard",
    )
    replay = classify_provider_necessity(
        policy_decision_id="PROVIDER-POLICY-REPLAY-000001",
        workflow_type="REPLAY_INSPECTION",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "replay",
    )

    assert dashboard["necessity_classification"] == PROVIDER_PROHIBITED
    assert replay["necessity_classification"] == PROVIDER_PROHIBITED


def test_worker_foundation_and_domain_architecture_provider_are_required(tmp_path) -> None:
    worker = classify_provider_necessity(
        policy_decision_id="PROVIDER-POLICY-WORKER-000001",
        workflow_type="NATIVE_DEVELOPMENT",
        task_kind="WORKER_FOUNDATION",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "worker_foundation",
    )
    domain = classify_provider_necessity(
        policy_decision_id="PROVIDER-POLICY-DOMAIN-000001",
        workflow_type="NATIVE_DEVELOPMENT",
        task_kind="DOMAIN_ARCHITECTURE_PROPOSAL",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "domain_architecture",
    )

    assert worker["necessity_classification"] == PROVIDER_REQUIRED
    assert domain["necessity_classification"] == PROVIDER_REQUIRED
    assert worker["provider_invoked"] is False
    assert domain["proposal_generated"] is False


def test_governance_review_provider_is_optional(tmp_path) -> None:
    capture = classify_provider_necessity(
        policy_decision_id="PROVIDER-POLICY-GOVERNANCE-000001",
        workflow_type="GOVERNANCE_REVIEW",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "governance_review",
    )

    assert capture["necessity_classification"] == PROVIDER_OPTIONAL
    assert "optional" in capture["reason"].lower()


def test_unknown_workflow_fails_closed(tmp_path) -> None:
    capture = classify_provider_necessity(
        policy_decision_id="PROVIDER-POLICY-UNKNOWN-000001",
        workflow_type="UNMAPPED_WORKFLOW",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "unknown",
    )

    assert capture["fail_closed"] is True
    assert capture["necessity_classification"] is None
    assert "necessity cannot be determined" in capture["failure_reason"]
    assert capture["provider_invoked"] is False


def test_ambiguous_policy_fails_closed(tmp_path) -> None:
    policy = default_provider_necessity_policy()
    policy["rules"].append(dict(policy["rules"][0], rule_id="DUPLICATE_SHOW_CHAIN_RULE"))
    policy.pop("policy_hash", None)

    capture = classify_provider_necessity(
        policy_decision_id="PROVIDER-POLICY-AMBIGUOUS-000001",
        workflow_type="OPERATOR_INSPECTION",
        command="SHOW_CHAIN",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "ambiguous",
        policy=policy,
    )

    assert capture["fail_closed"] is True
    assert "ambiguous necessity classification" in capture["failure_reason"]


def test_reconstruction_detects_corrupt_provider_necessity_replay(tmp_path) -> None:
    classify_provider_necessity(
        policy_decision_id="PROVIDER-POLICY-CORRUPT-000001",
        workflow_type="GOVERNANCE_REVIEW",
        created_at=CREATED_AT,
        replay_dir=tmp_path / "corrupt",
    )
    path = tmp_path / "corrupt" / "000_provider_necessity_policy_classified.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    wrapper["artifact"]["necessity_classification"] = PROVIDER_REQUIRED
    path.write_text(canonical_serialize(wrapper) + "\n", encoding="utf-8")

    with pytest.raises(FailClosedRuntimeError, match="hash mismatch"):
        reconstruct_provider_necessity_policy_replay(tmp_path / "corrupt")


def test_provider_necessity_policy_has_no_provider_worker_or_execution_imports() -> None:
    import aigol.runtime.provider_necessity_policy_runtime as runtime

    source = inspect.getsource(runtime)

    assert "OpenAIProviderAdapter" not in source
    assert "run_provider_attachment(" not in source
    assert "dispatch_worker(" not in source
    assert "invoke_worker(" not in source
    assert "create_execution_request(" not in source
    assert "start_execution(" not in source
