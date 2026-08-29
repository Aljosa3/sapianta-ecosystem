from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime.governance.governance_conformance_engine import (
    GovernanceConformanceEngine,
)
from runtime.governance.conformance_models import ConformanceStatus


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_git(repository: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repository), *args],
        capture_output=True,
        text=True,
        check=True,
    )


def initialize_repository(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "init", "--quiet", str(root)],
        capture_output=True,
        text=True,
        check=True,
    )


def active_hook_path(repository: Path) -> Path:
    result = run_git(
        repository,
        "rev-parse",
        "--path-format=absolute",
        "--git-path",
        "hooks/pre-commit",
    )
    return Path(result.stdout.strip())


def create_minimal_conformant_repo(root: Path, *, initialize_root: bool = True) -> None:
    if initialize_root:
        initialize_repository(root)
    for doc in (
        "docs/governance/CONSTITUTIONAL_ARCHITECTURE_SPEC_V1.md",
        "docs/governance/CANONICAL_LAYER_MODEL.md",
        "docs/governance/CONSTITUTIONAL_INVARIANTS.md",
        "docs/governance/GOVERNANCE_ENFORCEMENT_HIERARCHY.md",
        "docs/governance/GOVERNANCE_LINEAGE_MODEL.md",
        "docs/governance_audit/GOVERNANCE_LAYER_MAP.md",
        "docs/governance_audit/LAYER0_CONSTITUTION_ANALYSIS.md",
        "docs/governance_audit/GOVERNANCE_GAP_ANALYSIS.md",
    ):
        write(root / doc, "# evidence\n")

    write(
        root / "sapianta_system/governance/phases/LAYER_0_FREEZE.yaml",
        "layer: 0\nlocked_files:\n- a\ncore_constitutional_v1\n",
    )
    write(
        root / "sapianta_system/scripts/check_layer_freeze.py",
        "LAYER_0_FREEZE.yaml\nlocked_files\nSAPIANTA_FREEZE_OVERRIDE\n",
    )
    write(
        root / "sapianta_system/runtime/development/architecture_guardian.py",
        "protected_paths runtime/governance runtime/layer2 eval exec\n",
    )
    write(
        root / "sapianta_system/runtime/development/mutation_guard.py",
        "FORBIDDEN_PATHS runtime/governance runtime/ledger runtime/layer2\n",
    )
    write(
        root / "sapianta_system/runtime/development/mutation_validator.py",
        '"L0": "IMMUTABLE"\n"L1": "IMMUTABLE"\ncheck_mutation_permission\n',
    )
    write(
        root / "sapianta_system/runtime/governance/promotion_gate.py",
        "STRUCTURAL PARAMETRIC requires_approval\n",
    )
    write(
        root / "sapianta_system/runtime/development/dev_governance_gate.py",
        "BLOCK REVIEW Fail-closed approved_by_human\n",
    )
    write(
        root / "sapianta_system/runtime/development/ccs/certification_engine.py",
        "ArchitectureGuardian run_strict_generated_tests CERTIFIED REJECTED\n",
    )
    write(
        root / "sapianta_system/runtime/governance/chain_verifier.py",
        "previous_hash stable_hash verify\n",
    )
    write(
        root / "sapianta_system/runtime/governance/replay_engine.py",
        "ReplayMismatchError replay hash\n",
    )
    hook = "promotion_gate_v02\ncheck_layer_freeze\n"
    write(root / "scripts/hooks/pre-commit", hook)
    write(root / "sapianta_system/scripts/hooks/pre-commit", hook)
    initialize_repository(root / "sapianta_system")
    write(active_hook_path(root), hook)
    write(active_hook_path(root / "sapianta_system"), hook)


def test_conformant_repo_scores_conformant(tmp_path: Path) -> None:
    create_minimal_conformant_repo(tmp_path)

    report = GovernanceConformanceEngine(tmp_path).run()

    assert report.status is ConformanceStatus.CONFORMANT
    assert report.checks_failed == 0
    assert report.critical_violations == 0
    assert report.to_dict()["deterministic"] is True


def test_hook_mismatch_detection(tmp_path: Path) -> None:
    create_minimal_conformant_repo(tmp_path)
    root = active_hook_path(tmp_path / "sapianta_system")
    write(root, "# missing governance checks\n")

    report = GovernanceConformanceEngine(tmp_path).run()

    assert report.status is ConformanceStatus.PARTIALLY_CONFORMANT
    assert any(
        violation.violation_type == "HOOK_MISMATCH"
        and violation.surface == "git-resolved:sapianta_system:hooks/pre-commit"
        for violation in report.violations
    )
    assert root.read_text(encoding="utf-8") == "# missing governance checks\n"


def test_linked_worktree_active_root_hook_scores_conformant(tmp_path: Path) -> None:
    primary = tmp_path / "primary"
    linked = tmp_path / "linked"
    initialize_repository(primary)
    write(primary / "tracked", "stable\n")
    run_git(primary, "add", "tracked")
    run_git(
        primary,
        "-c",
        "user.name=Governance Test",
        "-c",
        "user.email=governance-test@example.invalid",
        "commit",
        "--quiet",
        "-m",
        "fixture",
    )
    run_git(primary, "worktree", "add", "--quiet", "--detach", str(linked))
    create_minimal_conformant_repo(linked, initialize_root=False)

    report = GovernanceConformanceEngine(linked).run()

    assert (linked / ".git").is_file()
    assert report.status is ConformanceStatus.CONFORMANT
    assert report.checks_passed == 20
    assert report.checks_failed == 0


def test_missing_active_hook_fails_closed(tmp_path: Path) -> None:
    create_minimal_conformant_repo(tmp_path)
    root_hook = active_hook_path(tmp_path)
    root_hook.unlink()

    report = GovernanceConformanceEngine(tmp_path).run()

    assert report.status is ConformanceStatus.PARTIALLY_CONFORMANT
    assert any(
        violation.evidence == "HOOK-ROOT-PRECOMMIT"
        and violation.actual == "missing or unreadable"
        for violation in report.violations
    )


def test_noncanonical_active_hook_bytes_fail_closed(tmp_path: Path) -> None:
    create_minimal_conformant_repo(tmp_path)
    root_hook = active_hook_path(tmp_path)
    write(root_hook, "# drift\npromotion_gate_v02\ncheck_layer_freeze\n")

    report = GovernanceConformanceEngine(tmp_path).run()

    assert report.status is ConformanceStatus.PARTIALLY_CONFORMANT
    assert any(
        violation.evidence == "HOOK-ROOT-PRECOMMIT"
        and violation.actual == "bytes differ from canonical hook"
        for violation in report.violations
    )


def test_hook_path_resolution_failure_fails_closed(tmp_path: Path) -> None:
    create_minimal_conformant_repo(tmp_path)
    shutil.rmtree(tmp_path / ".git")

    report = GovernanceConformanceEngine(tmp_path).run()

    assert report.status is ConformanceStatus.PARTIALLY_CONFORMANT
    assert any(
        violation.evidence == "HOOK-ROOT-PRECOMMIT"
        and violation.actual == "Git hook-path resolution failed"
        for violation in report.violations
    )


def test_mutation_coverage_validation_detects_missing_layer2(tmp_path: Path) -> None:
    create_minimal_conformant_repo(tmp_path)
    write(
        tmp_path / "sapianta_system/runtime/development/mutation_guard.py",
        "FORBIDDEN_PATHS runtime/governance runtime/ledger\n",
    )

    report = GovernanceConformanceEngine(tmp_path).run()

    assert any(
        violation.violation_type == "MISSING_MUTATION_BOUNDARY"
        and "runtime/layer2" in violation.actual
        for violation in report.violations
    )


def test_fail_closed_on_missing_constitution(tmp_path: Path) -> None:
    create_minimal_conformant_repo(tmp_path)
    (tmp_path / "docs/governance/CONSTITUTIONAL_INVARIANTS.md").unlink()

    report = GovernanceConformanceEngine(tmp_path).run()

    assert report.status is ConformanceStatus.CRITICAL_VIOLATION
    assert report.critical_violations == 1
    assert any(
        violation.violation_type == "MISSING_CONSTITUTIONAL_SPEC"
        for violation in report.violations
    )


def test_report_hash_is_replay_stable(tmp_path: Path) -> None:
    create_minimal_conformant_repo(tmp_path)

    first = GovernanceConformanceEngine(tmp_path).run()
    second = GovernanceConformanceEngine(tmp_path).run()

    assert first.report_hash == second.report_hash
    assert first.to_dict() == second.to_dict()
