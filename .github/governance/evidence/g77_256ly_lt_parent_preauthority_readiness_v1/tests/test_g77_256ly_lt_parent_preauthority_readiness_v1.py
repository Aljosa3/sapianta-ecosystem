from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import tempfile

import pytest


ROOT = Path(__file__).resolve().parents[5]
MODULE_PATH = ROOT / (
    ".github/governance/evidence/g77_256ly_lt_parent_preauthority_readiness_v1/"
    "orchestration/G77_256LY_LT_PARENT_PREAUTHORITY_READINESS_V1.py"
)
LX_DECISION = ROOT / (
    ".github/governance/evidence/g77_256lx_lt_state_parent_blocker_classification_v1/"
    "G77_256LX_TERMINAL_DECISION_V1.json"
)
LT_PATH = ROOT / (
    ".github/governance/evidence/g77_256lt_session_independent_one_shot_supervision_v1/"
    "harness/G77_256LT_SESSION_INDEPENDENT_ONE_SHOT_SUPERVISOR_V1.py"
)
LU_RELATION = ROOT / (
    ".github/governance/evidence/g77_256lu_lt_fm_static_integration_readiness_v1/"
    "G77_256LU_STATIC_INTEGRATION_BINDING_RELATION_V1.json"
)
REPORT = ROOT / (
    ".github/governance/evidence/g77_256ly_lt_parent_preauthority_readiness_v1/"
    "G77_256LY_G48_IMPLEMENTATION_REPORT_V1.md"
)
TERMINAL = ROOT / (
    ".github/governance/evidence/g77_256ly_lt_parent_preauthority_readiness_v1/"
    "G77_256LY_TERMINAL_DECISION_V1.json"
)


def load_module():
    specification = importlib.util.spec_from_file_location("g77_256ly_readiness", MODULE_PATH)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


LY = load_module()


def paths(base: Path) -> tuple[Path, Path]:
    root = base / "G77_256LY_SYNTHETIC_GENERATION"
    root.mkdir(mode=0o700)
    leaf = root / "operation_state" / "lt_supervision" / "LIFECYCLE_001"
    return root, leaf


def test_missing_parent_is_boundedly_materialized_and_leaf_remains_absent():
    with tempfile.TemporaryDirectory(prefix="g77_256ly_prepare_") as temporary:
        root, leaf = paths(Path(temporary))
        readiness = LY.prepare_lt_parent_readiness(root, leaf)
        observation = readiness["observation"]

        assert leaf.parent.is_dir()
        assert not leaf.exists() and not leaf.is_symlink()
        assert sorted(path.relative_to(root).as_posix() for path in root.rglob("*")) == [
            "operation_state",
            "operation_state/lt_supervision",
        ]
        assert stat.S_IMODE(leaf.parent.stat().st_mode) == 0o700
        assert observation["lt_state_parent"] == str(leaf.parent)
        assert observation["lt_lifecycle_leaf"] == str(leaf)
        assert observation["parent_identity"]["device"] == leaf.parent.stat().st_dev
        assert observation["parent_identity"]["inode"] == leaf.parent.stat().st_ino
        assert observation["parent_durability_validated"] is True
        assert observation["lifecycle_leaf_absent"] is True
        assert observation["stale_reservation_absent"] is True
        assert not (leaf.parent / LY.PROBE_NAME).exists()
        assert LY.reobserve_before_authority_consumption(root, leaf, readiness)["result"] == (
            LY.PRECONSUMPTION_RESULT
        )


def test_exact_derivation_and_path_escape_fail_closed():
    with tempfile.TemporaryDirectory(prefix="g77_256ly_paths_") as temporary:
        base = Path(temporary)
        root, leaf = paths(base)
        derived = LY.derive_lt_paths(root, leaf)
        assert derived == (root.absolute(), leaf.parent.absolute(), leaf.absolute())
        with pytest.raises(LY.ReadinessError, match="ESCAPES"):
            LY.prepare_lt_parent_readiness(root, base / "outside" / "LIFECYCLE_001")


def test_permitted_root_may_be_the_exact_parent_without_identity_drift():
    with tempfile.TemporaryDirectory(prefix="g77_256ly_root_parent_") as temporary:
        root, _ = paths(Path(temporary))
        leaf = root / "LIFECYCLE_001"
        readiness = LY.prepare_lt_parent_readiness(root, leaf)
        result = LY.reobserve_before_authority_consumption(root, leaf, readiness)
        assert result["result"] == LY.PRECONSUMPTION_RESULT
        assert not leaf.exists()


@pytest.mark.parametrize("collision", ["symlink", "file"])
def test_symlink_and_non_directory_parent_components_fail_closed(collision: str):
    with tempfile.TemporaryDirectory(prefix="g77_256ly_collision_") as temporary:
        base = Path(temporary)
        root, leaf = paths(base)
        operation_state = root / "operation_state"
        if collision == "symlink":
            target = base / "outside"
            target.mkdir()
            operation_state.symlink_to(target, target_is_directory=True)
        else:
            operation_state.write_text("collision", encoding="utf-8")
        with pytest.raises(LY.ReadinessError, match="SYMLINK_OR_NON_DIRECTORY"):
            LY.prepare_lt_parent_readiness(root, leaf)
        assert not leaf.exists()


@pytest.mark.parametrize("leaf_kind", ["directory", "file", "symlink"])
def test_existing_or_stale_lifecycle_leaf_is_rejected(leaf_kind: str):
    with tempfile.TemporaryDirectory(prefix="g77_256ly_stale_") as temporary:
        base = Path(temporary)
        root, leaf = paths(base)
        leaf.parent.mkdir(parents=True, mode=0o700)
        os.chmod(root / "operation_state", 0o700)
        if leaf_kind == "directory":
            leaf.mkdir()
        elif leaf_kind == "file":
            leaf.write_text("stale", encoding="utf-8")
        else:
            leaf.symlink_to(base / "missing-target")
        with pytest.raises(LY.ReadinessError, match="EXISTS_OR_STALE_RESERVATION"):
            LY.prepare_lt_parent_readiness(root, leaf)


def test_preconsumption_rejects_same_path_replaced_parent_object():
    with tempfile.TemporaryDirectory(prefix="g77_256ly_identity_") as temporary:
        root, leaf = paths(Path(temporary))
        readiness = LY.prepare_lt_parent_readiness(root, leaf)
        original_parent = leaf.parent.with_name("lt_supervision_original_held")
        leaf.parent.rename(original_parent)
        leaf.parent.mkdir(mode=0o700)
        assert leaf.parent.stat().st_ino != original_parent.stat().st_ino
        with pytest.raises(LY.ReadinessError, match="IDENTITY_DRIFT"):
            LY.reobserve_before_authority_consumption(root, leaf, readiness)


def test_preconsumption_rejects_leaf_binding_and_leaf_state_drift():
    with tempfile.TemporaryDirectory(prefix="g77_256ly_leaf_drift_") as temporary:
        root, leaf = paths(Path(temporary))
        readiness = LY.prepare_lt_parent_readiness(root, leaf)
        with pytest.raises(LY.ReadinessError, match="BINDING_MISMATCH"):
            LY.reobserve_before_authority_consumption(
                root, leaf.with_name("LIFECYCLE_002"), readiness
            )
        leaf.write_text("stale reservation", encoding="utf-8")
        with pytest.raises(LY.ReadinessError, match="EXISTS_OR_STALE_RESERVATION"):
            LY.reobserve_before_authority_consumption(root, leaf, readiness)


def test_preconsumption_rejects_parent_permission_and_usability_drift():
    with tempfile.TemporaryDirectory(prefix="g77_256ly_permission_drift_") as temporary:
        root, leaf = paths(Path(temporary))
        readiness = LY.prepare_lt_parent_readiness(root, leaf)
        leaf.parent.chmod(0o750)
        with pytest.raises(LY.ReadinessError, match="MODE_NOT_0700"):
            LY.reobserve_before_authority_consumption(root, leaf, readiness)


def test_ambiguous_or_forged_readiness_fails_closed():
    with tempfile.TemporaryDirectory(prefix="g77_256ly_ambiguous_") as temporary:
        root, leaf = paths(Path(temporary))
        readiness = LY.prepare_lt_parent_readiness(root, leaf)
        forged = copy.deepcopy(readiness)
        forged["observation"]["parent_identity"]["inode"] += 1
        with pytest.raises(LY.ReadinessError, match="SEAL_MISMATCH"):
            LY.reobserve_before_authority_consumption(root, leaf, forged)
        unknown = copy.deepcopy(readiness)
        unknown["free_standing_ready"] = True
        with pytest.raises(LY.ReadinessError, match="MALFORMED"):
            LY.reobserve_before_authority_consumption(root, leaf, unknown)


def test_reobservation_is_read_only_and_readiness_has_zero_operational_effects():
    with tempfile.TemporaryDirectory(prefix="g77_256ly_zero_effect_") as temporary:
        root, leaf = paths(Path(temporary))
        readiness = LY.prepare_lt_parent_readiness(root, leaf)
        before = leaf.parent.stat()
        before_entries = tuple(leaf.parent.iterdir())
        result = LY.reobserve_before_authority_consumption(root, leaf, readiness)
        after = leaf.parent.stat()
        assert before_entries == tuple(leaf.parent.iterdir()) == ()
        assert (before.st_dev, before.st_ino, before.st_mode, before.st_mtime_ns, before.st_ctime_ns) == (
            after.st_dev,
            after.st_ino,
            after.st_mode,
            after.st_mtime_ns,
            after.st_ctime_ns,
        )
        counters = {
            key: value
            for key, value in readiness["observation"].items()
            if key.endswith("_count")
        }
        assert counters and all(value == 0 for value in counters.values())
        assert result["authority_consumed_count"] == 0
        assert result["operation_attempt_count"] == 0
        assert not leaf.exists()


def test_module_has_no_authority_launch_or_operational_owner_import():
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {
        alias.name
        for node in tree.body
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert not imported.intersection({"subprocess", "qemu", "libvirt"})
    for forbidden in ("launch_detached(", "prepare_authority(", "consume_authority("):
        assert forbidden not in source
    assert source.count("os.mkdir(") == 1


def test_authenticated_lx_lt_lu_and_ex_reuse_baseline_remains_unchanged():
    lx = json.loads(LX_DECISION.read_bytes())
    decision = lx["decision"]
    evidence = lx["evidence"]
    assert decision["FAILURE_CLASS"] == "DUPLICATE_OR_EQUIVALENT_EDGE"
    assert decision["MINIMUM_MISSING_CAPABILITY"] == "NONE"
    assert evidence["ex"] == {
        "EX_RECONSTRUCTED": "VERIFIED__0",
        "EX_REUSED": "VERIFIED__17_OF_17",
    }
    assert LT_PATH.read_bytes()
    relation = json.loads(LU_RELATION.read_bytes())["relation"]
    assert relation["integration_readiness"] == "PROVEN"


def test_terminal_decision_is_sealed_and_preserves_zero_operation_boundary():
    envelope = json.loads(TERMINAL.read_bytes())
    decision = envelope["decision"]
    assert envelope["decision_sha256"] == hashlib.sha256(
        LY.canonical_bytes(decision)
    ).hexdigest()
    assert decision["MINIMUM_MISSING_CAPABILITY"] == "NONE"
    assert decision["MINIMUM_MISSING_PROOF"] == (
        "NONE_FOR_GENERATION_LOCAL_LT_PARENT_PREAUTHORITY_READINESS_COMPOSITION"
    )
    assert decision["E05_BEFORE"] == decision["E05_AFTER"] == "12/18"
    assert decision["LY_E05_CREDIT"] == 0
    assert decision["WRONG_SCOPE_STATUS"] == "UNSAT"
    assert all(value == 0 for value in envelope["evidence"]["ly_counters"].values())


def test_g48_report_has_exact_structure_questions_and_terminal_verdict():
    report = REPORT.read_text(encoding="utf-8")
    headings = [line for line in report.splitlines() if line.startswith("# ")]
    assert headings == [
        "# 1. Implementation Summary",
        "# 2. Code Evidence",
        "# 3. Constitutional Self-Assessment",
        "# 4. Validation Matrix",
        "# 5. Repository Mutation Summary",
        "# 6. Certification Verdict",
    ]
    questions = (
        "Katere obstoječe certificirane zmogljivosti se ponovno uporabijo?",
        "Katere nove zmogljivosti (če sploh) nastanejo?",
        "Ali katera obstoječa zmogljivost postane nedosegljiva?",
        "Ali implementacija ustvarja vzporedni tok?",
        "Ali zmanjšuje ali povečuje število produkcijskih poti?",
    )
    assert all(report.count(question) == 1 for question in questions)
    verdict = json.loads(TERMINAL.read_bytes())["decision"]["TERMINAL"]
    assert report.rstrip().endswith(verdict)
