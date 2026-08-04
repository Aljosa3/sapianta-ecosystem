from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

import pytest

from aigol.cli.aigol_cli import run_interactive_conversation
from aigol.runtime.constitutional_runtime_observatory import (
    ADAPTER_CATALOG_VERSION,
    GAP_PRECEDENCE,
    build_constitutional_human_intent_journey_v1,
    classify_constitutional_runtime_gap_v1,
    evidence_adapter_catalog_v1,
)
from aigol.runtime.human_interface_runtime_entry_service import (
    run_human_interface_runtime_entry,
)
from aigol.runtime.implementation_manifest_runtime import (
    CREATE_ONLY,
    create_implementation_manifest,
)
from aigol.runtime.transport.serialization import load_json, replay_hash


SESSION = "G67-02-OBSERVATORY-CORE"
CREATED = "2026-08-04T12:00:00Z"


def _time(second: int) -> str:
    return f"2026-08-04T12:00:{second:02d}Z"


def _manifest(root: Path) -> dict:
    return create_implementation_manifest(
        manifest_id="MANIFEST-G67-02-000001",
        canonical_chain_id="CHAIN-G67-02-000001",
        implementation_bundle_id="G67_02_OBSERVATORY_CORE",
        source_candidate_reference="CANDIDATE-G67-02-000001",
        source_candidate_hash=replay_hash({"source": "G67-02"}),
        implementation_handoff_reference="HANDOFF-G67-02-000001",
        implementation_handoff_hash=replay_hash({"handoff": "G67-02"}),
        provider_generation_authorization_reference="AUTH-G67-02-000001",
        provider_generation_authorization_hash=replay_hash({"auth": "G67-02"}),
        provider_response_reference="RESPONSE-G67-02-000001",
        provider_response_hash=replay_hash({"response": "G67-02"}),
        target_domain="PLATFORM_CORE",
        target_resource="G67_02_OBSERVATORY_CORE",
        target_worker=None,
        generated_files=[
            {
                "file_entry_id": "FILE-G67-02-000001",
                "target_path": "bounded/g67_02_target.py",
                "artifact_type": "PYTHON_RUNTIME_MODULE",
                "operation": CREATE_ONLY,
                "content": "VALUE = 1\n",
                "validation_requirements": [],
            }
        ],
        generated_tests=[],
        validation_requirements=["git diff --check"],
        known_gaps=[],
        created_at=CREATED,
        replay_dir=root / "manifest",
    )["implementation_manifest_artifact"]


def _entry(
    root: Path,
    workspace: Path,
    request: str,
    *,
    second: int,
    artifacts: list[dict] | None = None,
) -> dict:
    return run_human_interface_runtime_entry(
        interface_name="aicli",
        session_id=SESSION,
        human_requests=[request],
        created_at=_time(second),
        runtime_root=root,
        workspace=workspace,
        governed_runtime_runner=run_interactive_conversation,
        explicit_canonical_artifacts=artifacts or [],
    )


def _build_source(root: Path, workspace: Path, artifact_root: Path) -> dict:
    _entry(root, workspace, "Implement a validator.", second=1)
    captures = [
        _entry(root, workspace, text, second=index)
        for index, text in enumerate(
            (
                "action: Implement and normalize",
                "subject: a repository implementation change",
                "outcome: canonical change evidence",
                "work-type: ANALYSIS",
            ),
            start=2,
        )
    ]
    confirmed = _entry(
        root,
        workspace,
        captures[-1]["canonical_typed_semantic_composition"][
            "expected_confirmation_action"
        ],
        second=6,
    )
    committed = _entry(
        root,
        workspace,
        confirmed["canonical_typed_semantic_composition"]["expected_commit_action"],
        second=7,
        artifacts=[_manifest(artifact_root)],
    )
    prepared = committed["committed_objective_execution_preparation"]
    completed = _entry(
        root,
        workspace,
        prepared["expected_authorization_action"],
        second=8,
    )["constitutional_execution_spine_completion"]
    flow = committed["production_conversation_flow_binding"]
    flow_root = Path(flow["ordered_predecessor_references"][0]["replay_reference"]).parent
    integration_root = Path(prepared["integration_root"])
    roots = [
        ("G66_FLOW_BINDING", flow_root),
        ("G60_EXECUTION_PREPARATION", integration_root / "001_execution_prepared.json"),
        ("EXECUTION_AUTHORIZATION", integration_root / "authorization"),
        ("WORKER_INVOCATION_REQUEST", integration_root / "worker_request"),
        ("WORKER_ASSIGNMENT", integration_root / "worker_assignment"),
        ("WORKER_DISPATCH", integration_root / "worker_dispatch"),
        ("WORKER_INVOCATION", integration_root / "worker_invocation"),
        ("EXECUTION", integration_root / "execution"),
        ("RESULT_CAPTURE", integration_root / "result_capture"),
        ("RESULT_VALIDATION", integration_root / "result_validation"),
        ("CAPABILITY_COMPLETION", integration_root / "completion"),
        ("POST_EXECUTION_REPLAY_REVIEW", integration_root / "post_execution_replay_review"),
        ("GOVERNED_TERMINATION", integration_root / "governed_termination"),
        ("FINAL_EXECUTION_CERTIFICATION", integration_root / "final_execution_certification"),
    ]
    assert completed["final_execution_certification"]["execution_certified"] is True
    return {
        "scope": root,
        "roots": [{"adapter_id": key, "path": str(path)} for key, path in roots],
        "selector": {
            "session_id": SESSION,
            "commitment_identity": prepared["prepared_artifact"]["commitment_identity"],
            "human_actor": "HUMAN_OPERATOR",
        },
    }


@pytest.fixture(scope="module")
def evidence(tmp_path_factory: pytest.TempPathFactory) -> dict:
    base = tmp_path_factory.mktemp("g67_02_observatory")
    return _build_source(base / "runtime", base / "workspace", base / "artifact")


def _build(evidence: dict, **overrides: object) -> dict:
    arguments = {
        "evidence_scope_root": evidence["scope"],
        "evidence_roots": evidence["roots"],
        "selector": evidence["selector"],
    }
    arguments.update(overrides)
    return build_constitutional_human_intent_journey_v1(**arguments)


def _byte_snapshot(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_successful_non_mutating_journey_reaches_final_certification(evidence: dict) -> None:
    journey = _build(evidence)
    assert journey["journey_status"] == "OBSERVED_THROUGH_FINAL_EXECUTION_CERTIFICATION"
    assert journey["terminal_classification"] == "FINAL_EXECUTION_CERTIFIED"
    assert journey["runtime_events"][0]["stage"] == "HUMAN_INTENT_PRECEDENCE"
    assert journey["runtime_events"][-1]["stage"] == "FINAL_EXECUTION_CERTIFICATION"
    stages = {event["stage"] for event in journey["runtime_events"]}
    assert {"CONVERSATION", "SEMANTIC_SLOTS_CWM", "CANDIDATE_REVIEW", "FLOW_BINDING"} <= stages
    assert journey["branches"][0] == {"branch": "NON_MUTATING_CAPABILITY", "selected": True}
    with pytest.raises(TypeError):
        journey["journey_status"] = "CHANGED"


def test_projection_is_deterministic(evidence: dict) -> None:
    first = _build(evidence)
    second = _build(evidence)
    assert first == second
    assert first["projection_hash"] == second["projection_hash"]
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_owner_identity_is_preserved(evidence: dict) -> None:
    journey = _build(evidence)
    owners = {event["stage"]: event["owner"] for event in journey["runtime_events"]}
    assert owners["HUMAN_CONFIRMATION"] == "HUMAN_AUTHORITY"
    assert owners["EXECUTION_AUTHORIZATION"] == "EXECUTION_AUTHORIZATION"
    assert owners["FINAL_EXECUTION_CERTIFICATION"] == "FINAL_EXECUTION_CERTIFICATION"
    assert all(decision["observatory_authority"] == "NONE" for decision in journey["decisions"])


def test_evidence_is_byte_identical_after_observation(evidence: dict) -> None:
    before = _byte_snapshot(evidence["scope"])
    _build(evidence)
    assert _byte_snapshot(evidence["scope"]) == before


def test_observatory_invokes_no_writer_or_action_api(evidence: dict, monkeypatch: pytest.MonkeyPatch) -> None:
    import aigol.runtime.transport.serialization as serialization

    def forbidden(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("forbidden mutating API invoked")

    monkeypatch.setattr(serialization, "write_json_immutable", forbidden)
    journey = _build(evidence)
    assert journey["read_only"] is True
    assert journey["persisted"] is False
    assert journey["provider_invoked"] is False
    assert journey["observatory_worker_invoked"] is False


def test_corrupted_owner_evidence_fails_closed(evidence: dict, tmp_path: Path) -> None:
    copied = tmp_path / "runtime"
    shutil.copytree(evidence["scope"], copied)
    roots = []
    for item in evidence["roots"]:
        relative = Path(item["path"]).relative_to(evidence["scope"])
        roots.append({"adapter_id": item["adapter_id"], "path": str(copied / relative)})
    auth = next(Path(item["path"]) for item in roots if item["adapter_id"] == "EXECUTION_AUTHORIZATION")
    record = load_json(auth / "002_authorization_artifact_recorded.json")
    record["artifact"]["authorized_scope"] = "TAMPERED"
    (auth / "002_authorization_artifact_recorded.json").write_text(json.dumps(record), encoding="utf-8")
    journey = _build(evidence, evidence_scope_root=copied, evidence_roots=roots)
    assert journey["journey_status"] == "OBSERVATION_FAILED_CLOSED"
    assert journey["gaps"][0]["classification"] == "CORRUPTED"
    assert journey["runtime_events"] == ()


def test_duplicate_owner_roots_are_ambiguous(evidence: dict) -> None:
    roots = list(evidence["roots"]) + [dict(evidence["roots"][0])]
    journey = _build(evidence, evidence_roots=roots)
    assert journey["gaps"][0]["classification"] == "AMBIGUOUS"


def test_unknown_adapter_is_unsupported_evidence(evidence: dict) -> None:
    journey = _build(
        evidence,
        evidence_roots=[
            {"adapter_id": "UNKNOWN_STRUCTURAL_MATCH", "path": evidence["roots"][0]["path"]}
        ],
    )
    assert journey["gaps"][0]["classification"] == "UNSUPPORTED_EVIDENCE"


def test_not_reached_gap_and_precedence_are_exact() -> None:
    gap = classify_constitutional_runtime_gap_v1(
        subject="WORKER_ASSIGNMENT",
        not_reached=True,
        not_observed=True,
    )
    assert GAP_PRECEDENCE == tuple(gap["precedence"])
    assert gap["classification"] == "NOT_REACHED"


def test_non_mutating_branch_marks_mutation_not_applicable(evidence: dict) -> None:
    journey = _build(evidence)
    gaps = {gap["subject"]: gap["classification"] for gap in journey["gaps"]}
    assert gaps["MUTATION_BRANCH"] == "NOT_APPLICABLE"


def test_provider_content_is_intentionally_excluded(evidence: dict) -> None:
    journey = _build(evidence)
    gaps = {gap["subject"]: gap["classification"] for gap in journey["gaps"]}
    assert gaps["RAW_PROVIDER_CONTENT"] == "INTENTIONALLY_EXCLUDED"
    assert all("provider_content" not in event for event in journey["runtime_events"])


def test_g64_completion_is_uncomposed_not_correlated(evidence: dict) -> None:
    journey = _build(evidence)
    gaps = {gap["subject"]: gap["classification"] for gap in journey["gaps"]}
    assert gaps["G64_CONSTITUTIONAL_COMPLETION"] == "UNCOMPOSED"
    assert journey["topology"]["known_uncomposed_edges"][0]["correlated"] is False


def test_stale_topology_fails_closed(evidence: dict) -> None:
    journey = _build(
        evidence,
        topology_version="G65_10_CONSTITUTIONAL_NERVOUS_SYSTEM_STATIC_MAP_V1",
    )
    assert journey["gaps"][0]["classification"] == "STALE_TOPOLOGY"
    assert journey["runtime_events"] == ()


def test_catalog_is_passive_and_production_path_count_is_unchanged(evidence: dict) -> None:
    catalog = evidence_adapter_catalog_v1()
    journey = _build(evidence)
    assert catalog["catalog_version"] == ADAPTER_CATALOG_VERSION
    assert catalog["grants_authority"] is False
    assert all(item["read_only"] is True for item in catalog["adapters"])
    assert journey["grants_authority"] is False
    assert journey["authorizes_execution"] is False
    assert journey["authorizes_mutation"] is False
    assert journey["admissible_as_predecessor"] is False
