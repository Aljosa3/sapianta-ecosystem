from __future__ import annotations

from copy import deepcopy
import subprocess
from pathlib import Path

import pytest

import aigol.runtime.constitutional_reuse_proof_runtime as reuse_runtime
from aigol.runtime.constitutional_reuse_proof_production_gate import (
    READY_FOR_FRESH_G47,
)
from aigol.runtime.constitutional_reuse_proof_runtime import (
    REUSE,
    compose_constitutional_reuse_proof_input,
    evaluate_constitutional_reuse_proof,
    validate_constitutional_reuse_proof_input,
)
from aigol.runtime.models import FailClosedRuntimeError
from aigol.runtime.platform_capability_composition_coverage import (
    discover_platform_capability_composition_coverage,
)
from aigol.runtime.platform_core_project_services import (
    prepare_unified_human_interface_project_context,
)
from aigol.runtime.transport.serialization import replay_hash


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CREATED_AT = "2026-09-16T00:00:00Z"
REQUEST = "Improve replay certification with focused tests and validation."
GOVERNING_SOURCES = (
    "docs/governance/G63_02_CONSTITUTIONAL_REUSE_PROOF_FRAMEWORK_REPORT_V1.md",
    "docs/governance/G63_04_CONSTITUTIONAL_REUSE_PROOF_RUNTIME_COMPOSITION_AUDIT_REPORT_V1.md",
    "docs/governance/G64_03_CONSTITUTIONAL_REUSE_PROOF_PRODUCTION_INTEGRATION_DESIGN_REPORT_V1.md",
)
IMPLEMENTATION_PATH = "aigol/runtime/replay_certification_runtime.py"


def _run_git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _owner_workspace(tmp_path: Path) -> Path:
    root = tmp_path / "owner-workspace"
    root.mkdir()
    _run_git(root, "init")
    _run_git(root, "config", "user.email", "g63-owner@example.invalid")
    _run_git(root, "config", "user.name", "G63 Owner Evidence")
    (root / "BASELINE.txt").write_text("parent\n", encoding="utf-8")
    _run_git(root, "add", "BASELINE.txt")
    _run_git(root, "commit", "-m", "baseline parent")
    for relative in (*GOVERNING_SOURCES, IMPLEMENTATION_PATH):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((REPOSITORY_ROOT / relative).read_bytes())
    _run_git(root, "add", *GOVERNING_SOURCES, IMPLEMENTATION_PATH)
    _run_git(root, "commit", "-m", "authenticated owner evidence")
    return root


def _coverage() -> dict:
    return discover_platform_capability_composition_coverage(
        query=REQUEST,
        governance_root=REPOSITORY_ROOT,
        created_at=CREATED_AT,
    )


def _freeze_read_only_owners(
    monkeypatch: pytest.MonkeyPatch,
    coverage: dict,
) -> None:
    monkeypatch.setattr(
        reuse_runtime,
        "discover_platform_capability_composition_coverage",
        lambda **_: deepcopy(coverage),
    )
    monkeypatch.setattr(
        reuse_runtime,
        "run_conformance_check",
        lambda _: {"status": "CONFORMANT", "critical_violations": []},
    )


def _freeze_evaluation_composition(monkeypatch: pytest.MonkeyPatch) -> None:
    evidence = {
        "source": "FOCUSED_OWNER_EVIDENCE_FIXTURE",
        "governance_conformance": {
            "status": "CONFORMANT",
            "critical_violations": [],
        },
        "existing_owners_reused": [
            "PLATFORM_CORE_PROJECT_SERVICES",
            "PLATFORM_CORE_KNOWLEDGE",
            "PLATFORM_CAPABILITY_CERTIFICATION_REGISTRY",
            "PLATFORM_CORE_CAPABILITY_DISCOVERY",
            "AIGOL_CAPABILITY_AUDIT_RUNTIME",
            "GOVERNANCE_CONFORMANCE_ENGINE",
        ],
        "provider_invoked": False,
        "worker_invoked": False,
        "repository_mutated": False,
    }
    evidence["composition_evidence_hash"] = replay_hash(evidence)
    monkeypatch.setattr(
        reuse_runtime,
        "_compose_existing_owner_evidence",
        lambda **_: deepcopy(evidence),
    )


def _compose(
    root: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    coverage: dict | None = None,
) -> dict:
    _freeze_read_only_owners(monkeypatch, coverage or _coverage())
    return compose_constitutional_reuse_proof_input(
        proof_id="G63-OWNER-BOUND-001",
        request=REQUEST,
        proposed_scope={
            "entry_point": "PLATFORM_CORE_PROJECT_SERVICES",
            "work_type": "IMPLEMENTATION",
            "target_paths": [],
            "governance_target_paths": [],
        },
        repository_root=root,
        created_at=CREATED_AT,
    )


def test_owner_composition_normalizes_existing_g63_input_and_reducer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _owner_workspace(tmp_path)
    proof_input = _compose(root, monkeypatch)

    assert validate_constitutional_reuse_proof_input(proof_input) == proof_input
    assert proof_input["capability_inventory"][0]["candidate_id"] == (
        "REPLAY_CERTIFICATION_RUNTIME"
    )
    assert proof_input["ownership_matrix"][0]["roles"]["authority_owner"] == (
        "PLATFORM_CORE_REPLAY"
    )
    assert proof_input["known_limitations"]
    assert proof_input["authenticated_baseline"]["commit"] == _run_git(
        root, "rev-parse", "HEAD"
    )

    _freeze_evaluation_composition(monkeypatch)
    result = evaluate_constitutional_reuse_proof(
        proof_input=proof_input,
        repository_root=root,
    )
    assert result["decision"] == REUSE
    assert result["planning_authorized"] is False
    assert result["execution_authorized"] is False
    assert result["provider_invoked"] is False
    assert result["worker_invoked"] is False
    assert result["repository_mutated"] is False


def test_owner_composition_calls_existing_source_owners(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _owner_workspace(tmp_path)
    coverage = _coverage()
    calls = {"coverage": 0, "knowledge": 0, "audit": 0, "conformance": 0}
    original_knowledge = reuse_runtime.query_platform_knowledge
    original_audit = reuse_runtime.detect_capabilities

    def coverage_owner(**_: object) -> dict:
        calls["coverage"] += 1
        return deepcopy(coverage)

    def knowledge_owner(**kwargs: object) -> dict:
        calls["knowledge"] += 1
        return original_knowledge(**kwargs)

    def audit_owner(repository_root: Path) -> dict:
        calls["audit"] += 1
        return original_audit(repository_root)

    def conformance_owner(_: Path) -> dict:
        calls["conformance"] += 1
        return {"status": "CONFORMANT", "critical_violations": []}

    monkeypatch.setattr(
        reuse_runtime, "discover_platform_capability_composition_coverage", coverage_owner
    )
    monkeypatch.setattr(reuse_runtime, "query_platform_knowledge", knowledge_owner)
    monkeypatch.setattr(reuse_runtime, "detect_capabilities", audit_owner)
    monkeypatch.setattr(reuse_runtime, "run_conformance_check", conformance_owner)

    proof_input = compose_constitutional_reuse_proof_input(
        proof_id="G63-OWNER-CALLS-001",
        request=REQUEST,
        proposed_scope={"entry_point": "PLATFORM_CORE_PROJECT_SERVICES"},
        repository_root=root,
        created_at=CREATED_AT,
    )

    assert calls == {"coverage": 1, "knowledge": 1, "audit": 1, "conformance": 1}
    assert proof_input["capability_inventory"][0]["source_hash"].startswith("sha256:")


def test_unavailable_material_owner_evidence_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _owner_workspace(tmp_path)
    (root / IMPLEMENTATION_PATH).unlink()
    _run_git(root, "add", IMPLEMENTATION_PATH)
    _run_git(root, "commit", "-m", "remove material implementation evidence")
    _freeze_read_only_owners(monkeypatch, _coverage())

    with pytest.raises(
        FailClosedRuntimeError,
        match="certified implementation owner is unavailable",
    ):
        compose_constitutional_reuse_proof_input(
            proof_id="G63-MISSING-001",
            request=REQUEST,
            proposed_scope={"entry_point": "PLATFORM_CORE_PROJECT_SERVICES"},
            repository_root=root,
            created_at=CREATED_AT,
        )


def test_contradictory_material_owner_evidence_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _owner_workspace(tmp_path)
    coverage = _coverage()
    coverage["discovered_reusable_capabilities"][0]["certification_record_hash"] = (
        replay_hash("contradictory owner")
    )
    body = deepcopy(coverage)
    body.pop("artifact_hash")
    coverage["artifact_hash"] = replay_hash(body)
    _freeze_read_only_owners(monkeypatch, coverage)

    with pytest.raises(
        FailClosedRuntimeError,
        match="certification owner evidence is contradictory",
    ):
        compose_constitutional_reuse_proof_input(
            proof_id="G63-CONTRADICTORY-001",
            request=REQUEST,
            proposed_scope={"entry_point": "PLATFORM_CORE_PROJECT_SERVICES"},
            repository_root=root,
            created_at=CREATED_AT,
        )


def test_dirty_repository_baseline_fails_closed_before_owner_reduction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _owner_workspace(tmp_path)
    (root / "UNTRACKED.txt").write_text("uncertain Human work\n", encoding="utf-8")
    _freeze_read_only_owners(monkeypatch, _coverage())

    with pytest.raises(FailClosedRuntimeError, match="baseline must be clean"):
        compose_constitutional_reuse_proof_input(
            proof_id="G63-DIRTY-001",
            request=REQUEST,
            proposed_scope={"entry_point": "PLATFORM_CORE_PROJECT_SERVICES"},
            repository_root=root,
            created_at=CREATED_AT,
        )


def test_project_services_automatic_composition_uses_existing_g64_g47_route(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _owner_workspace(tmp_path)
    _freeze_read_only_owners(monkeypatch, _coverage())
    _freeze_evaluation_composition(monkeypatch)

    context = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id="G63-AUTO-SEAM",
        message=REQUEST,
        runtime_root=tmp_path / "runtime",
        workspace=root,
        created_at=CREATED_AT,
    )

    admission = context["reuse_proof_production_admission"]
    assert admission["admission_status"] == READY_FOR_FRESH_G47
    assert admission["reuse_proof_result"]["decision"] == REUSE
    assert context["constitutional_development_governance"] is not None
    assert context["reuse_proof_g47_scope_binding"] is not None
    assert context["workspace"] == str(root.resolve())


def test_explicit_valid_proof_result_takes_precedence_over_automatic_composition(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _owner_workspace(tmp_path)
    proof_input = _compose(root, monkeypatch)
    _freeze_evaluation_composition(monkeypatch)
    proof_result = evaluate_constitutional_reuse_proof(
        proof_input=proof_input,
        repository_root=root,
    )

    def automatic_composition_must_not_run(**_: object) -> dict:
        raise AssertionError("automatic composition overrode caller-supplied proof")

    monkeypatch.setattr(
        reuse_runtime,
        "compose_constitutional_reuse_proof_input",
        automatic_composition_must_not_run,
    )
    context = prepare_unified_human_interface_project_context(
        interface_name="aicli",
        session_id="G63-EXPLICIT-PRECEDENCE",
        message=REQUEST,
        runtime_root=tmp_path / "explicit-runtime",
        workspace=root,
        created_at=CREATED_AT,
        reuse_proof_result=proof_result,
    )

    admission = context["reuse_proof_production_admission"]
    assert admission["admission_status"] == READY_FOR_FRESH_G47
    assert admission["reuse_proof_hash"] == proof_result["evidence_identity"]


def test_composition_has_no_cognition_human_authority_or_operational_surface(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _owner_workspace(tmp_path)
    proof_input = _compose(root, monkeypatch)
    serialized = repr(proof_input)

    assert "COGNITION" not in serialized
    assert "QEMU" not in serialized
    assert "E05" not in serialized
    assert "Human authority" not in serialized
    assert proof_input["ownership_matrix"][0]["roles"]["human_owner"] == (
        "HUMAN_AUTHORITY"
    )
