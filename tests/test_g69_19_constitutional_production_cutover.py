from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import runpy

import pytest

from aigol.cli.clia import session as clia_session
from aigol.cli.clia import transport as clia_transport
from aigol.cli.clia.transport import submit_clia_human_act_v1
from aigol.runtime.canonical_hic_conformance_runtime_v1 import (
    CLIA_PRODUCTION_PROFILE_V1,
    PRODUCTION_HIC,
)
from aigol.runtime.constitutional_full_branch_replay_cro_coverage_v1 import (
    observe_constitutional_full_branch_coverage_for_cro_v1,
    persist_constitutional_full_branch_replay_correlation_v1,
)
from aigol.runtime.constitutional_production_cutover_v1 import (
    CANONICAL,
    CLIA_PRODUCTION_HIC_FAMILY,
    CONSTITUTIONAL_PRODUCTION_CUTOVER_ESTABLISHED,
    CONSTITUTIONAL_PRODUCTION_CUTOVER_ROLLED_BACK,
    activate_constitutional_production_cutover_v1,
    create_constitutional_production_cutover_certification_v1,
    read_constitutional_production_cutover_state_v1,
    rollback_constitutional_production_cutover_v1,
    run_production_g64_completion_branch_v1,
    run_production_natural_conversation_branch_v1,
    validate_active_constitutional_production_cutover_v1,
    validate_constitutional_production_cutover_certification_v1,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.transport.serialization import canonical_serialize, replay_hash


g69_18 = runpy.run_path(
    "tests/test_g69_18_constitutional_full_branch_replay_cro_coverage.py"
)
g69_13 = runpy.run_path("tests/test_g69_13_complete_hic_conformance.py")


def _certification(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    correlation = g69_18["_correlation"](tmp_path / "coverage", monkeypatch)
    replay_path = persist_constitutional_full_branch_replay_correlation_v1(
        replay_root=tmp_path / "replay",
        correlation=correlation,
    )
    observation = observe_constitutional_full_branch_coverage_for_cro_v1(
        replay_path
    )
    return create_constitutional_production_cutover_certification_v1(
        full_branch_correlation=correlation,
        full_branch_cro_observation=observation,
        release_decision_identity="G69-19-RELEASE-DECISION",
        hic_certification_reference="G69-13-COMPLETE-HIC-CERTIFICATION",
        consumer_audit_reference="G68-04-CONSUMER-AUDIT-PLUS-G69-19-CLOSURE",
        rollback_proof_reference="G69-19-ATOMIC-ROLLBACK-PROOF",
        fail_closed_proof_reference="G69-19-FAIL-CLOSED-CUTOVER-PROOF",
        full_branch_replay_reference=str(replay_path),
        activated_at="2026-08-05T20:00:00Z",
    )


def test_terminal_certification_requires_complete_b6_through_b9_lineage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    certification = _certification(tmp_path, monkeypatch)

    assert certification["certification_status"] == (
        CONSTITUTIONAL_PRODUCTION_CUTOVER_ESTABLISHED
    )
    assert certification["canonical_hic_family"] == CLIA_PRODUCTION_HIC_FAMILY
    assert certification["che_definition_count"] == 1
    assert certification["production_hic_family_count"] == 1
    assert certification["production_owner_chain_count"] == 1
    assert certification["production_path_count"] == 1
    assert certification["parallel_production_path_count"] == 0
    assert certification["hic_responsibility"] == "TRANSPORT_ONLY"
    assert certification["hic_semantic_capability"] == "NO_SEMANTIC_CAPABILITY"
    assert certification["compatibility_forwarding_created"] is False
    assert certification["new_constitutional_capability_created"] is False


def test_atomic_cutover_activates_one_family_and_deprecates_old_defaults(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    certification = _certification(tmp_path, monkeypatch)
    runtime_root = tmp_path / "production"
    path = activate_constitutional_production_cutover_v1(
        runtime_root=runtime_root,
        certification=certification,
    )
    state = validate_active_constitutional_production_cutover_v1(runtime_root)
    statuses = {
        item["surface_identity"]: item["current_status"]
        for item in state["surface_dispositions"]
    }

    assert state["state_status"] == CONSTITUTIONAL_PRODUCTION_CUTOVER_ESTABLISHED
    assert statuses["clia"] == CANONICAL
    assert statuses["aicli-default"] == "DEPRECATED"
    assert statuses["aicli-submit"] == "DEPRECATED"
    assert statuses["aigol-next-default"] == "DEPRECATED"
    assert statuses["aicli-conversation-v2"] == "COMPATIBILITY"
    assert all(not item["forwarding_alias"] for item in state["surface_dispositions"])
    assert read_constitutional_production_cutover_state_v1(path) == state


def test_cutover_is_idempotent_but_rejects_competing_release(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    certification = _certification(tmp_path, monkeypatch)
    runtime_root = tmp_path / "production"
    first = activate_constitutional_production_cutover_v1(
        runtime_root=runtime_root, certification=certification
    )
    before = first.read_bytes()
    second = activate_constitutional_production_cutover_v1(
        runtime_root=runtime_root, certification=certification
    )
    assert second == first
    assert second.read_bytes() == before

    competing = deepcopy(certification)
    competing["release_decision_identity"] = "COMPETING-RELEASE"
    competing["certification_identity"] = "production-cutover-sha256:" + replay_hash(
        {key: item for key, item in competing.items() if key != "certification_identity"}
    ).split(":", 1)[1]
    with pytest.raises(FailClosedRuntimeError):
        activate_constitutional_production_cutover_v1(
            runtime_root=runtime_root, certification=competing
        )


def test_certification_and_active_state_tampering_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    certification = _certification(tmp_path, monkeypatch)
    candidate = deepcopy(certification)
    candidate["production_path_count"] = 2
    with pytest.raises(FailClosedRuntimeError):
        validate_constitutional_production_cutover_certification_v1(candidate)

    runtime_root = tmp_path / "production"
    path = activate_constitutional_production_cutover_v1(
        runtime_root=runtime_root, certification=certification
    )
    state = json.loads(path.read_text(encoding="utf-8"))
    state["surface_dispositions"][0]["current_status"] = "DEVELOPMENT"
    state["state_hash"] = replay_hash(
        {key: item for key, item in state.items() if key != "state_hash"}
    )
    path.write_text(canonical_serialize(state) + "\n", encoding="utf-8")
    with pytest.raises(FailClosedRuntimeError):
        validate_active_constitutional_production_cutover_v1(runtime_root)


def test_atomic_rollback_restores_one_legacy_family_and_disables_clia(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    certification = _certification(tmp_path, monkeypatch)
    runtime_root = tmp_path / "production"
    path = activate_constitutional_production_cutover_v1(
        runtime_root=runtime_root, certification=certification
    )
    rollback_constitutional_production_cutover_v1(
        runtime_root=runtime_root,
        rollback_decision_identity="G69-19-ROLLBACK-DECISION",
    )
    state = read_constitutional_production_cutover_state_v1(path)
    statuses = {
        item["surface_identity"]: item["current_status"]
        for item in state["surface_dispositions"]
    }
    assert state["state_status"] == CONSTITUTIONAL_PRODUCTION_CUTOVER_ROLLED_BACK
    assert state["rollback_decision_identity"] == "G69-19-ROLLBACK-DECISION"
    assert statuses["clia"] == "DEVELOPMENT"
    assert statuses["aicli-default"] == CANONICAL
    with pytest.raises(FailClosedRuntimeError):
        validate_active_constitutional_production_cutover_v1(runtime_root)


def test_production_owner_callers_are_cutover_gated(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = "aigol.runtime.constitutional_production_cutover_v1"
    called = []
    monkeypatch.setattr(
        f"{module}.compose_constitutional_natural_conversation_branch_v1",
        lambda **kwargs: called.append(("natural", kwargs)) or {"owner": "G16"},
    )
    monkeypatch.setattr(
        f"{module}.compose_constitutional_g64_completion_branch_v1",
        lambda **kwargs: called.append(("completion", kwargs)) or {"owner": "G17"},
    )
    with pytest.raises(FailClosedRuntimeError):
        run_production_natural_conversation_branch_v1(
            cutover_runtime_root=tmp_path / "production", evidence="x"
        )

    certification = _certification(tmp_path, monkeypatch)
    activate_constitutional_production_cutover_v1(
        runtime_root=tmp_path / "production", certification=certification
    )
    assert run_production_natural_conversation_branch_v1(
        cutover_runtime_root=tmp_path / "production", evidence="natural"
    ) == {"owner": "G16"}
    assert run_production_g64_completion_branch_v1(
        cutover_runtime_root=tmp_path / "production", evidence="completion"
    ) == {"owner": "G17"}
    assert called == [
        ("natural", {"evidence": "natural"}),
        ("completion", {"evidence": "completion"}),
    ]


def test_active_production_clia_calls_only_the_sole_che(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runtime_root = tmp_path / "production"
    activate_constitutional_production_cutover_v1(
        runtime_root=runtime_root,
        certification=_certification(tmp_path, monkeypatch),
    )
    value = clia_session.create_clia_transport_session_v1(
        transport_session_identity="G69-19-ACTIVE-CLIA",
        human_actor_reference="HUMAN_OPERATOR",
        workspace_reference=str(tmp_path / "workspace"),
        runtime_root_reference=str(runtime_root),
        created_at="2026-08-05T20:00:00Z",
        production=True,
    )
    clia_session.open_clia_transport_session_v1(value)
    captured = {}

    def sole_che(**kwargs):
        captured["request"] = kwargs["request_envelope"]
        captured["runner"] = kwargs["governed_runtime_runner"]
        return g69_13["_refusal_response"](kwargs["request_envelope"])

    monkeypatch.setattr(clia_transport, "run_human_interface_runtime_entry", sole_che)
    result = clia_transport.submit_clia_human_act_v1(
        session=value,
        human_act="Exact production Human act.",
    )

    assert captured["request"].adapter_identity == CLIA_PRODUCTION_PROFILE_V1.adapter_identity
    assert captured["runner"] is clia_transport.reject_hic_owned_workflow_v1
    assert result.production_status == clia_session.CLIA_PRODUCTION_STATUS
    assert value.active_submission_identity is None


def test_clia_is_the_distinct_production_hic_profile_and_stays_transport_only() -> None:
    assert CLIA_PRODUCTION_PROFILE_V1.certification_scope == PRODUCTION_HIC
    assert CLIA_PRODUCTION_PROFILE_V1.interface_identity == "CLIA"
    assert clia_session.CLIA_PRODUCTION_ADAPTER_IDENTITY == (
        CLIA_PRODUCTION_PROFILE_V1.adapter_identity
    )
    assert clia_session.CLIA_PRODUCTION_STATUS == "CLIA_CANONICAL_PRODUCTION_HIC_G69_19"
    production_session = clia_session.create_clia_transport_session_v1(
        transport_session_identity="G69-19-PRODUCTION-SESSION",
        human_actor_reference="HUMAN_OPERATOR",
        workspace_reference=".",
        runtime_root_reference=".runtime/g69-19-test",
        created_at="2026-08-05T20:00:00Z",
        production=True,
    )
    assert production_session.adapter_identity == CLIA_PRODUCTION_PROFILE_V1.adapter_identity
    clia_session.open_clia_transport_session_v1(production_session)
    with pytest.raises(FailClosedRuntimeError, match="cutover is not active"):
        submit_clia_human_act_v1(
            session=production_session,
            human_act="Exact production Human act.",
        )
    assert production_session.active_submission_identity is None
    assert production_session.status is clia_session.CliaTransportStatus.TRANSPORT_FAILED_CLOSED
    transport_source = Path("aigol/cli/clia/transport.py").read_text(encoding="utf-8")
    assert "run_human_interface_runtime_entry(" in transport_source
    assert "reject_hic_owned_workflow_v1" in transport_source
    assert "compose_constitutional_natural_conversation" not in transport_source
    assert "compose_constitutional_g64_completion" not in transport_source
    for old_launcher in ("aicli", "aigol/cli/aicli.py", "aigol/cli/aigol_cli.py"):
        source = Path(old_launcher).read_text(encoding="utf-8")
        assert "aigol.cli.clia" not in source
        assert "from .clia" not in source
