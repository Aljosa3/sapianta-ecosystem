from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess

import pytest

from aigol.cli.aigol_cli import build_parser, run_interactive_conversation
import aigol.runtime.constitutional_reuse_proof_runtime as reuse_runtime
from aigol.runtime.constitutional_reuse_proof_runtime import (
    EXTENSION_RUNGS,
    SEARCH_EVIDENCE_CLASSES,
    create_constitutional_reuse_proof_input,
    create_responsibility_signature,
)
from aigol.runtime.transport.serialization import replay_hash


CREATED_AT = "2026-08-02T00:00:00Z"
SESSION_ID = "G64-06-ACLI-POSITIVE-LINEAGE"
REQUEST = (
    "Create governance artifact G64_06_POSITIVE_PATH_V1 documenting a bounded "
    "positive constitutional lineage integration."
)


def _input_sequence(values: list[str]):
    iterator = iter(values)

    def read(_prompt: str) -> str:
        return next(iterator)

    return read


def _workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    subprocess.run(["git", "init"], cwd=workspace, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "g64-06@example.invalid"],
        cwd=workspace,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "G64-06 Test"],
        cwd=workspace,
        check=True,
    )
    (workspace / "BASELINE.txt").write_text("one\n", encoding="utf-8")
    subprocess.run(["git", "add", "BASELINE.txt"], cwd=workspace, check=True)
    subprocess.run(
        ["git", "commit", "-m", "baseline parent"],
        cwd=workspace,
        check=True,
        capture_output=True,
    )
    (workspace / "BASELINE.txt").write_text("two\n", encoding="utf-8")
    subprocess.run(["git", "add", "BASELINE.txt"], cwd=workspace, check=True)
    subprocess.run(
        ["git", "commit", "-m", "baseline head"],
        cwd=workspace,
        check=True,
        capture_output=True,
    )
    return workspace


def _git_value(workspace: Path, revision: str) -> str:
    return subprocess.run(
        ["git", "rev-parse", revision],
        cwd=workspace,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _proof_input(workspace: Path) -> dict:
    baseline = {
        "commit": _git_value(workspace, "HEAD"),
        "parent": _git_value(workspace, "HEAD^"),
        "tree": _git_value(workspace, "HEAD^{tree}"),
        "worktree_clean": True,
        "governing_sources": [
            {
                "path": "docs/governance/G64_05_CONSTITUTIONAL_GOVERNANCE_REVALIDATION_REPORT_V1.md",
                "sha256": replay_hash("G64-05 focused test authority"),
            }
        ],
        "known_limitations": [
            "Focused positive-path fixture uses an isolated Git repository."
        ],
    }
    signature = create_responsibility_signature(
        semantic_responsibility=(
            "add one bounded AiCLI constitutional lineage integration artifact"
        ),
        inputs=["authenticated reuse proof", "exact governed development scope"],
        outputs=["scope-bound proposal", "fresh G47 evidence"],
        state_and_persistence="Caller-owned replay evidence only.",
        authority="Development Governance retains all planning authority.",
        non_authorities=[
            "does not authorize mutation",
            "does not authorize Worker execution",
        ],
        boundary="AiCLI transports but does not interpret owner decisions.",
        determinism="Exact Git baseline, scope digest, and replay hashes.",
        evidence_and_replay="G63 and G47 identities remain independently visible.",
        activation_and_lifecycle="Explicit invocation before proposal approval.",
    )
    return create_constitutional_reuse_proof_input(
        proof_id="G64-06-FOCUSED-CREATE-NEW",
        responsibility_signature=signature,
        authenticated_baseline=baseline,
        target_layers=["L3_GOVERNANCE_SYSTEM"],
        search_manifest=[
            {
                "evidence_class": evidence_class,
                "scope": f"authenticated {evidence_class.lower()} scope",
                "method": "existing owner API or immutable Git observation",
                "observation": "no reusable candidate satisfies the exact scope",
                "status": "SEARCHED",
                "material": True,
                "limitation": None,
            }
            for evidence_class in SEARCH_EVIDENCE_CLASSES
        ],
        capability_inventory=[],
        ownership_matrix=[],
        registry_matrix=[],
        implementation_usage_graph=[],
        equivalence_matrix=[],
        compatibility_matrix=[],
        extension_ladder=[
            {
                "rung": rung,
                "result": "INFEASIBLE",
                "candidate_id": None,
                "owner": None,
                "reason": f"authenticated infeasibility for {rung}",
                "evidence_refs": [f"G64-06-{index:02d}"],
            }
            for index, rung in enumerate(EXTENSION_RUNGS, start=1)
        ],
        duplicate_matrix=[],
        negative_evidence={
            "reuse_rejected": ["no exact equivalent candidate"],
            "extend_rejected": ["all ordered extension rungs are infeasible"],
            "consolidate_rejected": ["no complementary candidate composition"],
            "absence_scope": ["authenticated isolated repository and registries"],
            "proposed_ownership": {
                "architectural_owner": "DEVELOPMENT_GOVERNANCE",
                "authority_owner": "DEVELOPMENT_GOVERNANCE",
                "implementation_owner": "ACLI_GOVERNED_DEVELOPMENT_WORKFLOW",
                "state_owner": "CALLER_OWNED_REPLAY",
                "registry_owner": "NO_NEW_REGISTRY",
                "evidence_replay_owner": "GOVERNANCE_REPLAY",
                "lifecycle_owner": "DEVELOPMENT_GOVERNANCE",
                "human_owner": "HUMAN_AUTHORITY",
                "consumers": ["ACLI_GOVERNED_DEVELOPMENT_EXECUTION_BRIDGE"],
            },
        },
        evolution_evidence={
            "existing_consumers_compatible": True,
            "defaults_unchanged": False,
            "schema_api_compatible": True,
            "authority_unchanged": False,
            "owner_unchanged": False,
            "state_replay_compatible": True,
            "registry_selection_unchanged": True,
            "rollback_without_migration": True,
            "evidence_refs": ["G64-06 evolution classification evidence"],
        },
        authority_and_dependency_delta={
            "authority_delta": "BOUNDED_NEW_OWNER_PROPOSED",
            "ownership_delta": "BOUNDED_NEW_OWNER_PROPOSED",
            "dependency_delta": "ONE_WAY_CONSUMER_DEPENDENCY",
            "evidence_refs": ["G64-06 authority delta evidence"],
        },
        migration_rollback_deprecation={
            "migration": "NOT_REQUIRED",
            "rollback": "REMOVE_UNAPPROVED_ADDITIVE_ARTIFACT",
            "deprecation": "NONE",
            "evidence_refs": ["G64-06 lifecycle evidence"],
        },
        next_checkpoints=["G47_FRESH_DEVELOPMENT_GOVERNANCE_ASSESSMENT"],
        known_limitations=["Focused isolated repository fixture."],
        created_at=CREATED_AT,
    )


def _args(tmp_path: Path, workspace: Path, proof_input: dict | None):
    parser = build_parser()
    values = [
        "conversation",
        "--session-id",
        SESSION_ID,
        "--created-at",
        CREATED_AT,
        "--runtime-root",
        str(tmp_path / "runtime"),
        "--workspace",
        str(workspace),
    ]
    if proof_input is not None:
        proof_path = tmp_path / "reuse-proof-input.json"
        proof_path.write_text(json.dumps({"artifact": proof_input}), encoding="utf-8")
        values.extend(["--reuse-proof-input-json", str(proof_path)])
    return parser.parse_args(values)


def test_positive_acli_path_runs_g63_and_fresh_g47_before_bridge_and_worker(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = _workspace(tmp_path)
    proof_input = _proof_input(workspace)
    composed_evidence = {
        "governance_conformance": {"critical_violations": 0},
        "existing_owners_reused": [
            "PLATFORM_CORE_PROJECT_SERVICES",
            "GOVERNANCE_CONFORMANCE_ENGINE",
        ],
        "provider_invoked": False,
        "worker_invoked": False,
        "repository_mutated": False,
    }
    composed_evidence["composition_evidence_hash"] = replay_hash(
        composed_evidence
    )
    monkeypatch.setattr(
        reuse_runtime,
        "_compose_existing_owner_evidence",
        lambda **_: deepcopy(composed_evidence),
    )

    result = run_interactive_conversation(
        _args(tmp_path, workspace, proof_input),
        input_func=_input_sequence([REQUEST, "APPROVE", "exit"]),
        output_func=lambda _line: None,
    )

    proposal_turn = result["turns"][0]
    execution_turn = result["turns"][1]
    assert result["failed_turns"] == 0
    assert proposal_turn["response_status"] == "APPROVAL_REQUIRED"
    assert proposal_turn["acli_positive_constitutional_lineage_id"]
    assert proposal_turn["acli_positive_constitutional_lineage_hash"].startswith(
        "sha256:"
    )
    assert proposal_turn["reuse_proof_g47_scope_binding_hash"].startswith("sha256:")
    assert execution_turn["response_status"] == (
        "AWAITING_CONSTITUTIONAL_CERTIFICATION_AND_PROMOTION"
    )
    assert execution_turn["worker_invoked"] is True
    assert execution_turn["repository_mutation_performed"] is True
    lineage_replay = (
        tmp_path
        / "runtime"
        / SESSION_ID
        / "TURN-000001"
        / "acli_positive_constitutional_lineage"
        / "000_acli_positive_constitutional_lineage_recorded.json"
    )
    lineage = json.loads(lineage_replay.read_text(encoding="utf-8"))["artifact"]
    assert lineage["lineage_status"] == "LINEAGE_READY_FOR_BRIDGE"
    assert lineage["reuse_proof_production_admission"]["proof_requirement"] == (
        "REQUIRED_SATISFIED"
    )
    assert lineage["g47_operational_record"]["planning_eligible"] is True
    assert lineage["worker_invoked"] is False


def test_missing_proof_keeps_existing_bridge_fail_closed_without_mutation(
    tmp_path: Path,
) -> None:
    workspace = _workspace(tmp_path)
    result = run_interactive_conversation(
        _args(tmp_path, workspace, None),
        input_func=_input_sequence([REQUEST, "exit"]),
        output_func=lambda _line: None,
    )

    turn = result["turns"][0]
    assert result["failed_turns"] == 1
    assert turn["response_status"] == "FAILED_CLOSED"
    assert turn["worker_invoked"] is False
    assert turn["repository_mutation_performed"] is False
    assert not (workspace / "docs/governance/G64_06_POSITIVE_PATH_V1.md").exists()


def test_tampered_proof_fails_before_bridge_and_worker(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    tampered = deepcopy(_proof_input(workspace))
    tampered["input_hash"] = replay_hash("tampered")

    result = run_interactive_conversation(
        _args(tmp_path, workspace, tampered),
        input_func=_input_sequence([REQUEST, "exit"]),
        output_func=lambda _line: None,
    )

    assert result["failed_turns"] == 1
    assert result["worker_invoked"] is False
    assert not any(workspace.glob("aigol/runtime/acli_governed_development_*.py"))
